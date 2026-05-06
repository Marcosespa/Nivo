from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_refresh_token
from app.models.orm.pqc_key import PQCKey as PQCKeyORM
from app.models.orm.wallet import Wallet as WalletORM


@pytest.mark.asyncio
async def test_request_verify_otp_and_profile_flow(client, db_session, monkeypatch):
    sent_otps: list[str] = []

    async def fake_send_otp(self, phone_number: str, otp_code: str) -> bool:
        sent_otps.append(otp_code)
        return True

    monkeypatch.setattr("app.services.sms_service.SMSService.send_otp", fake_send_otp)

    request_response = await client.post(
        "/api/v1/auth/request-otp",
        json={"phone_number": "3101234567"},
    )
    assert request_response.status_code == 200
    assert request_response.json()["expires_in_seconds"] == 300
    assert sent_otps

    verify_response = await client.post(
        "/api/v1/auth/verify-otp",
        json={
            "phone_number": "3101234567",
            "otp_code": sent_otps[-1],
            "device_id": "iphone-test",
        },
    )
    assert verify_response.status_code == 200
    auth_payload = verify_response.json()
    assert auth_payload["access_token"]
    assert auth_payload["refresh_token"]
    assert auth_payload["is_new_user"] is True

    me_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_payload['access_token']}"},
    )
    assert me_response.status_code == 200
    me_payload = me_response.json()
    assert me_payload["phone_number"] == "+573101234567"
    assert me_payload["pqc_key_fingerprint"]

    wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers={"Authorization": f"Bearer {auth_payload['access_token']}"},
    )
    assert wallet_response.status_code == 200
    assert wallet_response.json()["balance_cop"] == 0

    pqc_keys = (await db_session.execute(PQCKeyORM.__table__.select())).all()
    wallets = (await db_session.execute(WalletORM.__table__.select())).all()
    assert len(pqc_keys) == 1
    assert len(wallets) == 1


@pytest.mark.asyncio
async def test_fourth_otp_request_is_rate_limited(client, monkeypatch):
    async def fake_send_otp(self, phone_number: str, otp_code: str) -> bool:
        return True

    monkeypatch.setattr("app.services.sms_service.SMSService.send_otp", fake_send_otp)

    for _ in range(3):
        response = await client.post(
            "/api/v1/auth/request-otp",
            json={"phone_number": "3200000000"},
        )
        assert response.status_code == 200

    limited = await client.post(
        "/api/v1/auth/request-otp",
        json={"phone_number": "3200000000"},
    )
    assert limited.status_code == 429


@pytest.mark.asyncio
async def test_refresh_rotation_and_logout_blacklist(client, created_user):
    user = await created_user("+573200000001")
    refresh_token = create_refresh_token(user.id, user.phone_number, user.plan.value)

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()
    assert refresh_payload["access_token"]
    assert refresh_payload["refresh_token"]
    assert refresh_payload["refresh_token"] != refresh_token

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_payload["refresh_token"]},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Sesión cerrada correctamente"

    reused = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_payload["refresh_token"]},
    )
    assert reused.status_code == 401


@pytest.mark.asyncio
async def test_request_otp_hides_dev_otp_when_host_is_not_local(db_session, fake_redis, monkeypatch):
    from app.main import app
    from app.api.v1.auth import get_redis as auth_get_redis
    from app.api.v1.payments import get_redis as payments_get_redis

    async def override_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    async def override_redis():
        return fake_redis

    async def fake_send_otp(self, phone_number: str, otp_code: str) -> bool:
        return True

    monkeypatch.setattr("app.services.sms_service.SMSService.send_otp", fake_send_otp)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[auth_get_redis] = override_redis
    app.dependency_overrides[payments_get_redis] = override_redis

    original_api_keys = settings.B2B_API_KEYS
    settings.B2B_API_KEYS = ["test-b2b-api-key-minimum-32-chars"]

    transport = ASGITransport(app=app, client=("203.0.113.10", 54321))
    async with AsyncClient(transport=transport, base_url="http://api.nivo.internal") as http_client:
        response = await http_client.post(
            "/api/v1/auth/request-otp",
            json={"phone_number": "3101234567"},
        )

    app.dependency_overrides.clear()
    settings.B2B_API_KEYS = original_api_keys

    assert response.status_code == 200
    assert "dev_otp" not in response.json()
