"""
Nivo — Tests del gate de dev_otp y endpoints /dev

Criterios de T-08:
  1. En producción el endpoint retorna 404 desde cualquier IP.
  2. En desarrollo desde localhost dev_otp está presente en la respuesta.
  3. En desarrollo desde IP externa dev_otp está ausente de la respuesta.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from app.main import app
from app.core.database import get_db
from app.core.config import settings


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_client(db_session: AsyncSession, fake_redis, host: str) -> AsyncClient:
    """AsyncClient que simula peticiones desde una IP específica."""
    from app.api.v1.auth import get_redis as auth_get_redis

    async def override_db():
        yield db_session

    async def override_redis():
        return fake_redis

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[auth_get_redis] = override_redis

    transport = ASGITransport(app=app, client=(host, 12345))
    return AsyncClient(transport=transport, base_url="http://testserver")


async def _request_otp(client: AsyncClient, monkeypatch) -> dict:
    """Llama a /request-otp con SMS mockeado y retorna el body JSON."""
    monkeypatch.setattr(
        "app.services.sms_service.SMSService.send_otp",
        AsyncMock(return_value=True),
    )
    resp = await client.post(
        "/api/v1/auth/request-otp",
        json={"phone_number": "3101234567"},
    )
    assert resp.status_code == 200
    return resp.json()


# ─── Tests ───────────────────────────────────────────────────────────────────

class TestDevOtpGate:

    async def test_dev_otp_present_from_localhost(
        self, db_session: AsyncSession, fake_redis, monkeypatch
    ):
        """ENVIRONMENT=development + 127.0.0.1 → dev_otp incluido en la respuesta."""
        monkeypatch.setattr(settings, "ENVIRONMENT", "development")

        async with _make_client(db_session, fake_redis, "127.0.0.1") as client:
            body = await _request_otp(client, monkeypatch)

        assert "dev_otp" in body, "dev_otp debe estar presente desde localhost en development"
        assert len(body["dev_otp"]) == 6, "dev_otp debe ser un código de 6 dígitos"
        print(f"✓ dev_otp presente desde 127.0.0.1: {body['dev_otp']}")

        app.dependency_overrides.clear()

    async def test_dev_otp_absent_from_external_ip(
        self, db_session: AsyncSession, fake_redis, monkeypatch
    ):
        """ENVIRONMENT=development + IP externa → dev_otp ausente (None / no incluido)."""
        monkeypatch.setattr(settings, "ENVIRONMENT", "development")

        async with _make_client(db_session, fake_redis, "203.0.113.42") as client:
            body = await _request_otp(client, monkeypatch)

        assert body.get("dev_otp") is None, (
            "dev_otp NO debe estar presente desde una IP externa aunque sea development"
        )
        print("✓ dev_otp ausente desde 203.0.113.42 en development")

        app.dependency_overrides.clear()

    async def test_dev_otp_absent_in_production(
        self, db_session: AsyncSession, fake_redis, monkeypatch
    ):
        """ENVIRONMENT=production → dev_otp nunca presente, sin importar la IP."""
        monkeypatch.setattr(settings, "ENVIRONMENT", "production")

        async with _make_client(db_session, fake_redis, "127.0.0.1") as client:
            body = await _request_otp(client, monkeypatch)

        assert body.get("dev_otp") is None, (
            "dev_otp NUNCA debe estar presente en producción"
        )
        print("✓ dev_otp ausente en producción incluso desde 127.0.0.1")

        app.dependency_overrides.clear()

    async def test_dev_seed_returns_404_from_external_ip(
        self, db_session: AsyncSession, fake_redis, monkeypatch
    ):
        """El endpoint /dev/seed retorna 404 desde cualquier IP que no sea localhost."""
        monkeypatch.setattr(settings, "ENVIRONMENT", "development")

        async with _make_client(db_session, fake_redis, "203.0.113.42") as client:
            resp = await client.post(
                "/api/v1/dev/seed",
                json={"sender_phone": "+573001234567", "receiver_phone": "+573009876543"},
            )

        assert resp.status_code == 404, (
            f"dev/seed debe retornar 404 desde IP externa, got {resp.status_code}"
        )
        print("✓ /dev/seed retorna 404 desde IP externa")

        app.dependency_overrides.clear()

    async def test_ipv6_localhost_also_works(
        self, db_session: AsyncSession, fake_redis, monkeypatch
    ):
        """::1 (IPv6 localhost) también debe recibir dev_otp."""
        monkeypatch.setattr(settings, "ENVIRONMENT", "development")

        async with _make_client(db_session, fake_redis, "::1") as client:
            body = await _request_otp(client, monkeypatch)

        assert "dev_otp" in body, "dev_otp debe estar presente desde ::1 (IPv6 localhost)"
        print(f"✓ dev_otp presente desde ::1")

        app.dependency_overrides.clear()
