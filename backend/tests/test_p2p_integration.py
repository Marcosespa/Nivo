from __future__ import annotations

import pytest

from app.core.security import create_access_token


async def _patch_payment_side_effects(monkeypatch) -> list[str]:
    sent_otps: list[str] = []

    async def fake_send_otp(self, phone_number: str, otp_code: str) -> bool:
        sent_otps.append(otp_code)
        return True

    async def fake_send_payment_notification(
        self,
        receiver_phone: str,
        amount_display: str,
        sender_name: str,
    ) -> bool:
        return True

    async def fake_notify_payment_received(
        self,
        receiver_id,
        amount_display: str,
        sender_phone: str,
    ) -> bool:
        return True

    monkeypatch.setattr("app.services.sms_service.SMSService.send_otp", fake_send_otp)
    monkeypatch.setattr(
        "app.services.sms_service.SMSService.send_payment_notification",
        fake_send_payment_notification,
    )
    monkeypatch.setattr(
        "app.services.notification_service.NotificationService.notify_payment_received",
        fake_notify_payment_received,
    )
    return sent_otps


def _auth_headers(user) -> dict[str, str]:
    access_token = create_access_token(user.id, user.phone_number, user.plan.value)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_p2p_happy_path_confirms_and_updates_balances(client, created_user, monkeypatch):
    sent_otps = await _patch_payment_side_effects(monkeypatch)
    sender = await created_user("+573200000101", balance_cop=500_000)
    receiver = await created_user("+573200000102", balance_cop=100_000)
    sender_headers = _auth_headers(sender)
    receiver_headers = _auth_headers(receiver)

    initiate_response = await client.post(
        "/api/v1/payments/initiate",
        headers=sender_headers,
        json={
            "receiver_phone": receiver.phone_number,
            "amount_cop": 125_000,
            "message": "Pago P2P feliz",
        },
    )
    assert initiate_response.status_code == 202
    assert sent_otps

    confirm_response = await client.post(
        "/api/v1/payments/confirm",
        headers=sender_headers,
        json={"tx_id": initiate_response.json()["tx_id"], "otp_code": sent_otps[-1]},
    )
    assert confirm_response.status_code == 200
    confirm_payload = confirm_response.json()
    assert confirm_payload["status"] == "completed"
    assert confirm_payload["provider_reference"].startswith("NIVO-")
    assert confirm_payload["receipt_url"].endswith(".pdf")

    sender_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers=sender_headers,
    )
    receiver_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers=receiver_headers,
    )
    assert sender_wallet_response.json()["balance_cop"] == 375_000
    assert receiver_wallet_response.json()["balance_cop"] == 225_000


@pytest.mark.asyncio
async def test_p2p_confirm_rejects_invalid_otp_without_moving_balance(
    client,
    created_user,
    monkeypatch,
):
    await _patch_payment_side_effects(monkeypatch)
    sender = await created_user("+573200000103", balance_cop=300_000)
    receiver = await created_user("+573200000104", balance_cop=40_000)
    sender_headers = _auth_headers(sender)
    receiver_headers = _auth_headers(receiver)

    initiate_response = await client.post(
        "/api/v1/payments/initiate",
        headers=sender_headers,
        json={
            "receiver_phone": receiver.phone_number,
            "amount_cop": 50_000,
            "message": "OTP malo",
        },
    )
    assert initiate_response.status_code == 202

    confirm_response = await client.post(
        "/api/v1/payments/confirm",
        headers=sender_headers,
        json={"tx_id": initiate_response.json()["tx_id"], "otp_code": "000000"},
    )
    assert confirm_response.status_code == 401

    sender_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers=sender_headers,
    )
    receiver_wallet_response = await client.get(
        "/api/v1/users/me/wallet",
        headers=receiver_headers,
    )
    assert sender_wallet_response.json()["balance_cop"] == 300_000
    assert receiver_wallet_response.json()["balance_cop"] == 40_000


@pytest.mark.asyncio
async def test_p2p_initiate_rejects_unknown_receiver(client, created_user, monkeypatch):
    await _patch_payment_side_effects(monkeypatch)
    sender = await created_user("+573200000105", balance_cop=300_000)
    sender_headers = _auth_headers(sender)

    response = await client.post(
        "/api/v1/payments/initiate",
        headers=sender_headers,
        json={
            "receiver_phone": "+573200009999",
            "amount_cop": 50_000,
            "message": "No existe",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Receptor no encontrado en Nivo"


@pytest.mark.asyncio
async def test_p2p_initiate_rejects_insufficient_funds(client, created_user, monkeypatch):
    await _patch_payment_side_effects(monkeypatch)
    sender = await created_user("+573200000106", balance_cop=10_000)
    receiver = await created_user("+573200000107", balance_cop=0)
    sender_headers = _auth_headers(sender)

    response = await client.post(
        "/api/v1/payments/initiate",
        headers=sender_headers,
        json={
            "receiver_phone": receiver.phone_number,
            "amount_cop": 20_000,
            "message": "Sin saldo",
        },
    )

    assert response.status_code == 402
    assert response.json()["detail"] == "Saldo insuficiente en tu billetera"


@pytest.mark.asyncio
async def test_p2p_history_marks_sent_and_received_directions(client, created_user, monkeypatch):
    sent_otps = await _patch_payment_side_effects(monkeypatch)
    sender = await created_user("+573200000108", balance_cop=500_000)
    receiver = await created_user("+573200000109", balance_cop=0)
    sender_headers = _auth_headers(sender)
    receiver_headers = _auth_headers(receiver)

    initiate_response = await client.post(
        "/api/v1/payments/initiate",
        headers=sender_headers,
        json={
            "receiver_phone": receiver.phone_number,
            "amount_cop": 75_000,
            "message": "Historial",
        },
    )
    assert initiate_response.status_code == 202

    confirm_response = await client.post(
        "/api/v1/payments/confirm",
        headers=sender_headers,
        json={"tx_id": initiate_response.json()["tx_id"], "otp_code": sent_otps[-1]},
    )
    assert confirm_response.status_code == 200
    tx_id = confirm_response.json()["tx_id"]

    sender_history = await client.get(
        "/api/v1/payments/history?direction=sent",
        headers=sender_headers,
    )
    receiver_history = await client.get(
        "/api/v1/payments/history?direction=received",
        headers=receiver_headers,
    )
    sender_detail = await client.get(
        f"/api/v1/payments/{tx_id}",
        headers=sender_headers,
    )
    receiver_detail = await client.get(
        f"/api/v1/payments/{tx_id}",
        headers=receiver_headers,
    )

    assert sender_history.status_code == 200
    assert receiver_history.status_code == 200
    assert sender_history.json()["transactions"][0]["direction"] == "sent"
    assert receiver_history.json()["transactions"][0]["direction"] == "received"
    assert sender_detail.status_code == 200
    assert receiver_detail.status_code == 200
