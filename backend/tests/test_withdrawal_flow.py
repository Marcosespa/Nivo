"""Tests del flujo de retiros ACH (TASK-008)."""

from __future__ import annotations

import hashlib
import uuid

import pytest
from sqlalchemy import select

from app.core.security import create_access_token
from app.models.orm.bank_account import BankAccount, AccountTypeEnum
from app.models.orm.transaction import (
    SettlementRailEnum,
    SettlementStatusEnum,
    Transaction as TransactionORM,
    TransactionStatusEnum,
)


def _auth_headers(user) -> dict:
    token = create_access_token(user.id, user.phone_number, user.plan.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_register_bank_account_returns_micro_deposit_amount(
    client, created_user
):
    user = await created_user("+573101234567", balance_cop=100_000_00)

    response = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": "1234567890",
            "account_holder_name": "Sebastian Test",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert "bank_account_id" in body
    # 501–999 COP en centavos
    assert 501_00 <= body["verification_amount_cop"] <= 999_00
    assert body["verification_amount_display"].endswith("COP")


@pytest.mark.asyncio
async def test_verify_bank_account_with_correct_amount_succeeds(
    client, created_user, db_session
):
    user = await created_user("+573109876543", balance_cop=50_000_00)

    register = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "051",
            "account_type": "checking",
            "account_number": "9988776655",
            "account_holder_name": "Marco Test",
        },
    )
    account_id = register.json()["bank_account_id"]
    micro = register.json()["verification_amount_cop"]

    verify = await client.post(
        f"/api/v1/withdrawal/accounts/{account_id}/verify",
        headers=_auth_headers(user),
        json={"verification_amount_cop": micro},
    )

    assert verify.status_code == 200
    assert verify.json()["status"] == "verified"

    # En BD el monto y el hash quedan limpios
    refreshed = await db_session.scalar(
        select(BankAccount).where(BankAccount.id == uuid.UUID(account_id))
    )
    assert refreshed.is_verified is True
    assert refreshed.verification_amount_cop is None
    assert refreshed.verification_amount_hash is None


@pytest.mark.asyncio
async def test_verify_bank_account_with_wrong_amount_fails(
    client, created_user
):
    user = await created_user("+573104445566", balance_cop=10_000_00)

    register = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": "5566778899",
            "account_holder_name": "Mismatch Test",
        },
    )
    account_id = register.json()["bank_account_id"]
    micro = register.json()["verification_amount_cop"]
    wrong_amount = micro + 1_00 if micro < 999_00 else micro - 1_00

    verify = await client.post(
        f"/api/v1/withdrawal/accounts/{account_id}/verify",
        headers=_auth_headers(user),
        json={"verification_amount_cop": wrong_amount},
    )

    assert verify.status_code == 400
    assert "no coincide" in verify.json()["detail"]


@pytest.mark.asyncio
async def test_initiate_withdrawal_debits_wallet_and_creates_pending_tx(
    client, created_user, db_session
):
    user = await created_user("+573102223344", balance_cop=200_000_00)

    register = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": "1112223334",
            "account_holder_name": "Withdraw Test",
        },
    )
    account_id = register.json()["bank_account_id"]
    micro = register.json()["verification_amount_cop"]

    await client.post(
        f"/api/v1/withdrawal/accounts/{account_id}/verify",
        headers=_auth_headers(user),
        json={"verification_amount_cop": micro},
    )

    response = await client.post(
        "/api/v1/withdrawal/initiate",
        headers=_auth_headers(user),
        json={"bank_account_id": account_id, "amount_cop": 50_000_00},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    # Free user: comisión $2,000 COP
    assert body["amount_cop"] == 50_000_00
    assert body["commission_cop"] == 2_000_00
    assert body["total_debit"] == 52_000_00
    assert body["status"] == "pending"

    # Tx persistida con rail=ACH y status=PENDING; no firma PQC
    tx = await db_session.scalar(
        select(TransactionORM).where(TransactionORM.id == uuid.UUID(body["transaction_id"]))
    )
    assert tx is not None
    assert tx.rail == SettlementRailEnum.ACH
    assert tx.status == TransactionStatusEnum.PENDING
    assert tx.settlement_status == SettlementStatusEnum.PENDING
    # Retiros no firmados en MVP (ml_dsa_signature, signature_key_id nullable)
    assert tx.ml_dsa_signature is None
    assert tx.signature_key_id is None


@pytest.mark.asyncio
async def test_initiate_withdrawal_to_unverified_account_fails(
    client, created_user
):
    user = await created_user("+573105556677", balance_cop=100_000_00)

    register = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": "9999888877",
            "account_holder_name": "Unverified Test",
        },
    )
    account_id = register.json()["bank_account_id"]

    response = await client.post(
        "/api/v1/withdrawal/initiate",
        headers=_auth_headers(user),
        json={"bank_account_id": account_id, "amount_cop": 10_000_00},
    )

    assert response.status_code == 400
    assert "verificada" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_initiate_withdrawal_with_insufficient_balance_fails(
    client, created_user
):
    user = await created_user("+573108889990", balance_cop=5_000_00)

    register = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": "1010101010",
            "account_holder_name": "Broke User",
        },
    )
    account_id = register.json()["bank_account_id"]
    micro = register.json()["verification_amount_cop"]
    await client.post(
        f"/api/v1/withdrawal/accounts/{account_id}/verify",
        headers=_auth_headers(user),
        json={"verification_amount_cop": micro},
    )

    response = await client.post(
        "/api/v1/withdrawal/initiate",
        headers=_auth_headers(user),
        json={"bank_account_id": account_id, "amount_cop": 10_000_00},
    )

    # 10,000 + 2,000 comisión > 5,000 disponibles
    assert response.status_code == 400
    assert "saldo" in response.json()["detail"].lower() or "insuficiente" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_unverified_bank_account_succeeds(client, created_user, db_session):
    user = await created_user("+573101111222", balance_cop=10_000_00)

    register = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": "5555444433",
            "account_holder_name": "Mistake Account",
        },
    )
    account_id = register.json()["bank_account_id"]

    response = await client.delete(
        f"/api/v1/withdrawal/accounts/{account_id}",
        headers=_auth_headers(user),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    refreshed = await db_session.scalar(
        select(BankAccount).where(BankAccount.id == uuid.UUID(account_id))
    )
    assert refreshed is None


@pytest.mark.asyncio
async def test_delete_verified_bank_account_is_blocked(client, created_user):
    user = await created_user("+573103333222", balance_cop=10_000_00)

    register = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": "7777666655",
            "account_holder_name": "Locked Account",
        },
    )
    account_id = register.json()["bank_account_id"]
    micro = register.json()["verification_amount_cop"]
    await client.post(
        f"/api/v1/withdrawal/accounts/{account_id}/verify",
        headers=_auth_headers(user),
        json={"verification_amount_cop": micro},
    )

    response = await client.delete(
        f"/api/v1/withdrawal/accounts/{account_id}",
        headers=_auth_headers(user),
    )

    assert response.status_code == 400
    assert "verificada" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_second_unverified_account_is_rejected(client, created_user):
    user = await created_user("+573104444555", balance_cop=10_000_00)

    first = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": "1234509876",
            "account_holder_name": "First",
        },
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "002",
            "account_type": "savings",
            "account_number": "9876054321",
            "account_holder_name": "Second",
        },
    )

    assert second.status_code == 400
    assert "verificar" in second.json()["detail"].lower()


@pytest.mark.asyncio
async def test_account_number_is_never_returned_in_listing(
    client, created_user, db_session
):
    user = await created_user("+573109999888", balance_cop=10_000_00)
    raw_account_number = "1357902468"

    await client.post(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
        json={
            "bank_code": "001",
            "account_type": "savings",
            "account_number": raw_account_number,
            "account_holder_name": "Privacy Test",
        },
    )

    listing = await client.get(
        "/api/v1/withdrawal/accounts",
        headers=_auth_headers(user),
    )

    assert listing.status_code == 200
    body = listing.json()
    assert body["total_count"] == 1
    # No se filtra el número en plano por la API
    assert raw_account_number not in listing.text
    # Pero sí quedó cifrado en BD (ni siquiera el ciphertext contiene el plaintext)
    stored = await db_session.scalar(
        select(BankAccount).where(BankAccount.user_id == user.id)
    )
    assert raw_account_number.encode() not in stored.account_number_encrypted
