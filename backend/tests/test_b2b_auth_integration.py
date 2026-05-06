from __future__ import annotations

import hashlib

import pytest

from app.models.orm.b2b_client import B2BClient


@pytest.mark.asyncio
async def test_crypto_rejects_invalid_b2b_api_key(client):
    response = await client.get(
        "/api/v1/crypto/algorithms",
        headers={"X-Nivo-Key": "wrong-key"},
    )

    assert response.status_code == 401
    assert "API key inválida" in response.json()["detail"]


@pytest.mark.asyncio
async def test_crypto_accepts_active_b2b_client_from_database(client, db_session):
    api_key = "db-backed-b2b-api-key-minimum-32-chars"
    db_session.add(
        B2BClient(
            name="Banco Demo",
            api_key_hash=hashlib.sha256(api_key.encode()).hexdigest(),
            is_active=True,
        )
    )
    await db_session.commit()

    response = await client.get(
        "/api/v1/crypto/algorithms",
        headers={"X-Nivo-Key": api_key},
    )

    assert response.status_code == 200
    assert "kem" in response.json()


@pytest.mark.asyncio
async def test_crypto_rejects_inactive_b2b_client_from_database(client, db_session):
    api_key = "inactive-b2b-api-key-minimum-32-chars"
    db_session.add(
        B2BClient(
            name="Cliente Inactivo",
            api_key_hash=hashlib.sha256(api_key.encode()).hexdigest(),
            is_active=False,
        )
    )
    await db_session.commit()

    response = await client.get(
        "/api/v1/crypto/algorithms",
        headers={"X-Nivo-Key": api_key},
    )

    assert response.status_code == 401
