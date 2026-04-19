from __future__ import annotations

import pytest

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_payment_initiate_confirm_history_and_detail(client, db_session, created_user, monkeypatch):
    sent_otps: list[str] = []

    async def fake_send_otp(self, phone_number: str, otp_code: str) -> bool:
        sent_otps.append(otp_code)
        return True

    async def fake_notify(self, receiver_id, amount_display, sender_phone) -> bool:
        return True

    monkeypatch.setattr("app.services.sms_service.SMSService.send_otp", fake_send_otp)
    monkeypatch.setattr("app.services.sms_service.SMSService.send_payment_notification", fake_notify)
    monkeypatch.setattr("app.services.notification_service.NotificationService.notify_payment_received", fake_notify)

    sender = await created_user("+573200000010", balance_cop=500_000)
    receiver = await created_user("+573200000011", balance_cop=100_000)

    access_token = create_access_token(sender.id, sender.phone_number, sender.plan.value)
    headers = {"Authorization": f"Bearer {access_token}"}

    initiate_response = await client.post(
        "/api/v1/payments/initiate",
        headers=headers,
        json={
            "receiver_phone": receiver.phone_number,
            "amount_cop": 125_000,
            "message": "Pago sprint 1",
        },
    )
    assert initiate_response.status_code == 202
    initiate_payload = initiate_response.json()
    assert initiate_payload["status"] == "pending_confirmation"
    assert sent_otps

    confirm_response = await client.post(
        "/api/v1/payments/confirm",
        headers=headers,
        json={"tx_id": initiate_payload["tx_id"], "otp_code": sent_otps[-1]},
    )
    assert confirm_response.status_code == 200
    confirm_payload = confirm_response.json()
    assert confirm_payload["status"] == "completed"
    assert confirm_payload["provider_reference"].startswith("NIVO-")
    assert confirm_payload["settlement_status"] == "settled"

    history_response = await client.get("/api/v1/payments/history", headers=headers)
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["total"] == 1
    assert history_payload["transactions"][0]["tx_id"] == confirm_payload["tx_id"]

    detail_response = await client.get(
        f"/api/v1/payments/{confirm_payload['tx_id']}",
        headers=headers,
    )
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["message"] == "Pago sprint 1"
    assert detail_payload["settlement_status"] == "settled"

    sender_wallet_response = await client.get("/api/v1/users/me/wallet", headers=headers)
    assert sender_wallet_response.status_code == 200
    assert sender_wallet_response.json()["balance_cop"] == 375_000

    receiver_token = create_access_token(receiver.id, receiver.phone_number, receiver.plan.value)
    receiver_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers={"Authorization": f"Bearer {receiver_token}"},
    )
    assert receiver_wallet_response.status_code == 200
    assert receiver_wallet_response.json()["balance_cop"] == 225_000


@pytest.mark.asyncio
async def test_payment_rejects_when_balance_is_insufficient(client, created_user, monkeypatch):
    async def fake_send_otp(self, phone_number: str, otp_code: str) -> bool:
        return True

    monkeypatch.setattr("app.services.sms_service.SMSService.send_otp", fake_send_otp)

    sender = await created_user("+573200000020", balance_cop=10_000)
    receiver = await created_user("+573200000021", balance_cop=0)

    access_token = create_access_token(sender.id, sender.phone_number, sender.plan.value)
    response = await client.post(
        "/api/v1/payments/initiate",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "receiver_phone": receiver.phone_number,
            "amount_cop": 20_000,
            "message": "Sin saldo",
        },
    )
    assert response.status_code == 402
