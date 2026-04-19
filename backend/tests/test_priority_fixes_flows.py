from __future__ import annotations

import hashlib

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import create_access_token
from app.models.orm.transaction import (
    Transaction as TransactionORM,
    TransactionStatusEnum,
    SettlementStatusEnum,
)


def _build_wompi_checksum(payload: dict, secret: str) -> str:
    parts: list[str] = []
    for path in payload["signature"]["properties"]:
        current = payload
        for segment in path.split("."):
            current = current[segment]
        parts.append(str(current))
    raw = f"{''.join(parts)}.{payload['signature']['timestamp']}.{secret}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@pytest.mark.asyncio
async def test_topup_webhook_flow(client, db_session, created_user):
    from app.api.v1.topup import gateway_service

    original_mock_mode = settings.WOMPI_MOCK_MODE
    original_secret = settings.WOMPI_EVENTS_SECRET
    original_service_mock_mode = gateway_service.mock_mode

    settings.WOMPI_MOCK_MODE = True
    settings.WOMPI_EVENTS_SECRET = "test-wompi-secret"
    gateway_service.mock_mode = True

    try:
        user = await created_user("+573200001000", balance_cop=100_000)
        access_token = create_access_token(user.id, user.phone_number, user.plan.value)

        initiate_response = await client.post(
            "/api/v1/topup/initiate",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"amount_cop": 750_000, "bank_code": "001"},
        )
        assert initiate_response.status_code == 201
        reference = initiate_response.json()["reference"]

        payload = {
            "event": "transaction.updated",
            "data": {
                "reference": reference,
                "status": "APPROVED",
                "id": f"wompi-{reference[:8]}",
                "amount_in_cents": 750_000,
            },
            "signature": {
                "properties": ["data.id", "data.reference", "data.status", "data.amount_in_cents"],
                "timestamp": "1713571200",
            },
            "timestamp": "1713571200",
        }
        checksum = _build_wompi_checksum(payload, settings.WOMPI_EVENTS_SECRET)

        webhook_response = await client.post(
            "/api/v1/topup/webhook",
            headers={"X-Event-Checksum": checksum},
            json=payload,
        )
        assert webhook_response.status_code == 200

        wallet_response = await client.get(
            "/api/v1/users/me/wallet",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert wallet_response.status_code == 200
        assert wallet_response.json()["balance_cop"] == 850_000

        tx_result = await db_session.execute(
            select(TransactionORM).where(TransactionORM.provider_reference == reference)
        )
        transaction = tx_result.scalar_one()
        assert transaction.status == TransactionStatusEnum.COMPLETED
        assert transaction.settlement_status == SettlementStatusEnum.SETTLED
    finally:
        settings.WOMPI_MOCK_MODE = original_mock_mode
        settings.WOMPI_EVENTS_SECRET = original_secret
        gateway_service.mock_mode = original_service_mock_mode


@pytest.mark.asyncio
async def test_p2p_payment_full_flow(client, created_user, monkeypatch):
    sent_otps: list[str] = []

    async def fake_send_otp(self, phone_number: str, otp_code: str) -> bool:
        sent_otps.append(otp_code)
        return True

    async def fake_notify(*args, **kwargs) -> bool:
        return True

    monkeypatch.setattr("app.services.sms_service.SMSService.send_otp", fake_send_otp)
    monkeypatch.setattr("app.services.notification_service.NotificationService.notify_payment_received", fake_notify)

    sender = await created_user("+573200001001", balance_cop=500_000)
    receiver = await created_user("+573200001002", balance_cop=100_000)

    sender_token = create_access_token(sender.id, sender.phone_number, sender.plan.value)
    receiver_token = create_access_token(receiver.id, receiver.phone_number, receiver.plan.value)

    initiate_response = await client.post(
        "/api/v1/payments/initiate",
        headers={"Authorization": f"Bearer {sender_token}"},
        json={
            "receiver_phone": receiver.phone_number,
            "amount_cop": 125_000,
            "message": "Pago completo",
        },
    )
    assert initiate_response.status_code == 202
    tx_id = initiate_response.json()["tx_id"]
    assert sent_otps

    execute_response = await client.post(
        "/api/v1/payments/execute",
        headers={"Authorization": f"Bearer {sender_token}"},
        json={"tx_id": tx_id, "otp_code": sent_otps[-1]},
    )
    assert execute_response.status_code == 200
    assert execute_response.json()["status"] == "completed"

    sender_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers={"Authorization": f"Bearer {sender_token}"},
    )
    receiver_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers={"Authorization": f"Bearer {receiver_token}"},
    )
    assert sender_wallet_response.json()["balance_cop"] == 375_000
    assert receiver_wallet_response.json()["balance_cop"] == 225_000


@pytest.mark.asyncio
async def test_payment_insufficient_funds(client, db_session, created_user, monkeypatch):
    async def fake_send_otp(self, phone_number: str, otp_code: str) -> bool:
        return True

    monkeypatch.setattr("app.services.sms_service.SMSService.send_otp", fake_send_otp)

    sender = await created_user("+573200001003", balance_cop=10_000)
    receiver = await created_user("+573200001004", balance_cop=30_000)

    sender_token = create_access_token(sender.id, sender.phone_number, sender.plan.value)
    receiver_token = create_access_token(receiver.id, receiver.phone_number, receiver.plan.value)

    response = await client.post(
        "/api/v1/payments/initiate",
        headers={"Authorization": f"Bearer {sender_token}"},
        json={
            "receiver_phone": receiver.phone_number,
            "amount_cop": 20_000,
            "message": "Debe fallar",
        },
    )
    assert response.status_code == 402

    sender_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers={"Authorization": f"Bearer {sender_token}"},
    )
    receiver_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers={"Authorization": f"Bearer {receiver_token}"},
    )
    assert sender_wallet_response.json()["balance_cop"] == 10_000
    assert receiver_wallet_response.json()["balance_cop"] == 30_000

    tx_count = await db_session.execute(select(func.count(TransactionORM.id)))
    assert tx_count.scalar_one() == 0
