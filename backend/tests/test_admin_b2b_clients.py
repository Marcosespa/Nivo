"""Tests del endpoint admin para emitir API keys B2B."""

from __future__ import annotations

import hashlib

import pytest
from sqlalchemy import select

from app.models.orm.b2b_client import B2BClient


@pytest.mark.asyncio
async def test_admin_can_issue_b2b_api_key_and_use_it(client, db_session):
    create = await client.post(
        "/api/v1/admin/b2b-clients",
        json={"name": "Banco Demo"},
    )

    assert create.status_code == 201, create.text
    body = create.json()
    issued_key = body["api_key"]
    assert len(issued_key) >= 48
    assert body["name"] == "Banco Demo"
    assert body["is_active"] is True
    # Sólo se retorna el prefijo del hash (nunca el hash completo)
    assert len(body["api_key_hash_prefix"]) == 8

    # En BD sólo quedó el SHA-256 del key
    stored = await db_session.scalar(
        select(B2BClient).where(B2BClient.name == "Banco Demo")
    )
    assert stored is not None
    assert stored.api_key_hash == hashlib.sha256(issued_key.encode()).hexdigest()
    assert stored.api_key_hash != issued_key  # nunca se persiste el plaintext

    # La key emitida funciona contra el endpoint B2B
    used = await client.get(
        "/api/v1/crypto/algorithms",
        headers={"X-Nivo-Key": issued_key},
    )
    assert used.status_code == 200
    assert "kem" in used.json()


@pytest.mark.asyncio
async def test_admin_lists_active_b2b_clients(client, db_session):
    db_session.add_all([
        B2BClient(
            name="Activo",
            api_key_hash=hashlib.sha256(b"key-active-xxxxxxxxxxxxxxxxxxxx").hexdigest(),
            is_active=True,
        ),
        B2BClient(
            name="Inactivo",
            api_key_hash=hashlib.sha256(b"key-inactive-xxxxxxxxxxxxxxxxxx").hexdigest(),
            is_active=False,
        ),
    ])
    await db_session.commit()

    only_active = await client.get("/api/v1/admin/b2b-clients?only_active=true")
    assert only_active.status_code == 200
    names = [c["name"] for c in only_active.json()["clients"]]
    assert "Activo" in names
    assert "Inactivo" not in names

    all_clients = await client.get("/api/v1/admin/b2b-clients?only_active=false")
    assert all_clients.status_code == 200
    all_names = [c["name"] for c in all_clients.json()["clients"]]
    assert "Activo" in all_names
    assert "Inactivo" in all_names


@pytest.mark.asyncio
async def test_admin_can_deactivate_b2b_client(client, db_session):
    create = await client.post(
        "/api/v1/admin/b2b-clients",
        json={"name": "To Disable"},
    )
    assert create.status_code == 201
    issued_key = create.json()["api_key"]
    client_id = create.json()["id"]

    # Funciona antes de desactivar
    before = await client.get(
        "/api/v1/crypto/algorithms",
        headers={"X-Nivo-Key": issued_key},
    )
    assert before.status_code == 200

    deactivate = await client.post(f"/api/v1/admin/b2b-clients/{client_id}/deactivate")
    assert deactivate.status_code == 200
    assert deactivate.json()["status"] == "deactivated"

    # Tras desactivar, la key deja de validar contra la BD
    # (peor caso, todavía pasa por el fallback de settings.B2B_API_KEYS — pero
    # el key emitido es aleatorio y no está en esa lista)
    after = await client.get(
        "/api/v1/crypto/algorithms",
        headers={"X-Nivo-Key": issued_key},
    )
    assert after.status_code == 401
