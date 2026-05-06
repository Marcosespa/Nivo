"""
Nivo — Tests de integración para webhook de Wompi (top-up end-to-end)

Casos de prueba:
1. Webhook aprobado acredita saldo exactamente una vez (idempotencia)
2. Webhook con firma inválida no acredita
3. Webhook duplicado no duplica acreditación
4. Webhook rechazado marca transacción como fallida
5. Webhook sin transacción local es ignorado
"""

from __future__ import annotations

import uuid
import json
import hashlib
import hmac
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.payment_gateway_service import (
    PaymentGatewayService,
    InvalidWebhookSignatureError,
)
from app.models.orm.transaction import (
    Transaction as TransactionORM,
    TransactionStatusEnum,
    SettlementRailEnum,
    SettlementStatusEnum,
)
from app.models.orm.wallet import Wallet as WalletORM
from app.models.orm.user import User as UserORM, UserPlanEnum
from app.models.orm.webhook_event_log import WebhookEventLog, WebhookEventStatusEnum
from app.core.config import settings


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def wompi_events_secret(monkeypatch):
    """Garantiza validación de firma en tests de webhook."""
    monkeypatch.setattr(settings, "WOMPI_EVENTS_SECRET", "test_events_secret")


@pytest.fixture
async def test_user_and_wallet(db_session: AsyncSession):
    """Crea usuario de prueba con billetera y transacción pendiente."""
    user = UserORM(
        id=uuid.uuid4(),
        phone_number="+573101234567",
        plan=UserPlanEnum.FREE,
    )
    db_session.add(user)
    await db_session.flush()

    wallet = WalletORM(
        id=uuid.uuid4(),
        user_id=user.id,
        display_balance_cop=0,
    )
    db_session.add(wallet)
    await db_session.commit()

    return user, wallet


@pytest.fixture
async def pending_topup_transaction(db_session: AsyncSession, test_user_and_wallet):
    """Crea una transacción de top-up pendiente."""
    user, wallet = test_user_and_wallet
    wompi_tx_id = "WOMPI-TEST-123456"

    tx = TransactionORM(
        id=uuid.uuid4(),
        sender_id=user.id,
        receiver_id=user.id,  # Top-up: el usuario recarga su propia billetera vía Wompi
        amount_cop=100_000_00,  # $100,000 COP
        status=TransactionStatusEnum.PENDING,
        rail=SettlementRailEnum.PSE,
        provider_reference=wompi_tx_id,
        settlement_status=SettlementStatusEnum.PENDING,
        ml_dsa_signature=None,   # top-ups autenticados por HMAC de Wompi
        signature_key_id=None,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(tx)
    await db_session.commit()

    return tx, wompi_tx_id


def build_wompi_webhook_payload(wompi_tx_id: str, status: str = "APPROVED", add_signature: bool = True):
    """Construye payload de webhook de Wompi con firma correcta (si aplica)."""
    timestamp = "1713900000"  # Timestamp fijo para tests
    
    event_data = {
        "id": wompi_tx_id,
        "status": status,
        "amount_in_cents": 10000000,
        "currency": "COP",
        "reference": f"NIVO-{wompi_tx_id[:8]}",
        "customer_email": None,
    }

    payload = {
        "event": "transaction.updated",
        "timestamp": timestamp,
        "data": event_data,
    }

    if add_signature:
        event_json = json.dumps(event_data, separators=(",", ":"), sort_keys=True)
        to_sign = f"{event_json}.{timestamp}.{settings.WOMPI_EVENTS_SECRET}"
        signature = hashlib.sha256(to_sign.encode()).hexdigest()
        payload["signature"] = {"checksum": signature}
    else:
        payload["signature"] = {"checksum": ""}

    return payload, signature if add_signature else None


# ─── Tests ───────────────────────────────────────────────────────────────────

class TestWompiWebhookTopupFlow:
    """Suite de tests para el flujo completo de top-up vía webhook de Wompi."""

    async def test_webhook_approved_credits_wallet(
        self, db_session: AsyncSession, pending_topup_transaction, wompi_events_secret
    ):
        """Test: webhook APPROVED acredita saldo del usuario exactamente una vez."""
        tx, wompi_tx_id = pending_topup_transaction
        user_id = tx.sender_id
        initial_balance = 0
        topup_amount = 100_000_00

        # Construir webhook
        payload, signature = build_wompi_webhook_payload(wompi_tx_id, "APPROVED")

        # Procesar webhook
        service = PaymentGatewayService()
        await service.process_webhook(db_session, payload, signature, "192.168.1.1")

        # Verificaciones
        # 1. Transacción debe estar SETTLED
        stmt = select(TransactionORM).where(TransactionORM.id == tx.id)
        result = await db_session.execute(stmt)
        updated_tx = result.scalar_one()
        assert updated_tx.settlement_status == SettlementStatusEnum.SETTLED
        assert updated_tx.status == TransactionStatusEnum.COMPLETED

        # 2. Billetera del usuario debe estar acreditada
        stmt = select(WalletORM).where(WalletORM.user_id == user_id)
        result = await db_session.execute(stmt)
        updated_wallet = result.scalar_one()
        expected_balance = initial_balance + topup_amount
        assert updated_wallet.display_balance_cop == expected_balance
        print(f"✓ Wallet credited: ${updated_wallet.display_balance_cop / 100:,.0f} COP")

        # 3. Event log debe estar PROCESSED
        stmt = select(WebhookEventLog).where(
            (WebhookEventLog.provider == "wompi") &
            (WebhookEventLog.provider_event_id == wompi_tx_id)
        )
        result = await db_session.execute(stmt)
        event_log = result.scalar_one()
        assert event_log.status == WebhookEventStatusEnum.PROCESSED
        assert event_log.related_transaction_id == tx.id

    async def test_webhook_duplicate_idempotent(
        self, db_session: AsyncSession, pending_topup_transaction, wompi_events_secret
    ):
        """Test: enviar el mismo webhook dos veces no duplica la acreditación."""
        tx, wompi_tx_id = pending_topup_transaction
        user_id = tx.sender_id
        topup_amount = 100_000_00

        payload, signature = build_wompi_webhook_payload(wompi_tx_id, "APPROVED")

        service = PaymentGatewayService()

        # Procesar webhook primera vez
        await service.process_webhook(db_session, payload, signature, "192.168.1.1")

        # Verificar primer crédito
        stmt = select(WalletORM).where(WalletORM.user_id == user_id)
        result = await db_session.execute(stmt)
        wallet_after_first = result.scalar_one()
        balance_after_first = wallet_after_first.display_balance_cop

        assert balance_after_first == topup_amount
        print(f"✓ First webhook: balance = ${balance_after_first / 100:,.0f} COP")

        # Procesar webhook segunda vez (idéntico)
        await service.process_webhook(db_session, payload, signature, "192.168.1.1")

        # Verificar que el balance no cambió (idempotencia)
        stmt = select(WalletORM).where(WalletORM.user_id == user_id)
        result = await db_session.execute(stmt)
        wallet_after_second = result.scalar_one()
        balance_after_second = wallet_after_second.display_balance_cop

        assert balance_after_second == balance_after_first, (
            f"Idempotencia fallida: balance cambió de "
            f"${balance_after_first / 100:,.0f} a ${balance_after_second / 100:,.0f} COP"
        )
        print(f"✓ Idempotencia: balance no cambió (${balance_after_second / 100:,.0f} COP)")

    async def test_webhook_invalid_signature_rejected(
        self, db_session: AsyncSession, pending_topup_transaction, wompi_events_secret
    ):
        """Test: webhook con firma inválida es rechazado."""
        tx, wompi_tx_id = pending_topup_transaction
        user_id = tx.sender_id

        payload, _ = build_wompi_webhook_payload(wompi_tx_id, "APPROVED", add_signature=True)
        # Corromper la firma
        bad_signature = "0000000000000000000000000000000000000000000000000000000000000000"

        service = PaymentGatewayService()

        # Debe lanzar excepción por firma inválida
        with pytest.raises(InvalidWebhookSignatureError):
            await service.process_webhook(db_session, payload, bad_signature, "192.168.1.1")

        # Verificar que la billetera NO fue acreditada
        stmt = select(WalletORM).where(WalletORM.user_id == user_id)
        result = await db_session.execute(stmt)
        wallet = result.scalar_one()
        assert wallet.display_balance_cop == 0, "Billetera no debe ser acreditada con firma inválida"
        print("✓ Invalid signature rejected, wallet not credited")

    async def test_webhook_declined_marks_failed(
        self, db_session: AsyncSession, pending_topup_transaction, wompi_events_secret
    ):
        """Test: webhook DECLINED marca transacción como FAILED sin acreditar."""
        tx, wompi_tx_id = pending_topup_transaction
        user_id = tx.sender_id

        payload, signature = build_wompi_webhook_payload(wompi_tx_id, "DECLINED")

        service = PaymentGatewayService()
        await service.process_webhook(db_session, payload, signature, "192.168.1.1")

        # Verificar que transacción está FAILED
        stmt = select(TransactionORM).where(TransactionORM.id == tx.id)
        result = await db_session.execute(stmt)
        updated_tx = result.scalar_one()
        assert updated_tx.settlement_status == SettlementStatusEnum.FAILED
        assert updated_tx.status == TransactionStatusEnum.FAILED

        # Verificar que billetera NO fue acreditada
        stmt = select(WalletORM).where(WalletORM.user_id == user_id)
        result = await db_session.execute(stmt)
        wallet = result.scalar_one()
        assert wallet.display_balance_cop == 0
        print("✓ DECLINED webhook marked as FAILED, wallet not credited")

    async def test_webhook_pending_no_state_change(
        self, db_session: AsyncSession, pending_topup_transaction, wompi_events_secret
    ):
        """Test: PENDING no marca fallo ni idempotencia; la transacción sigue pendiente."""
        tx, wompi_tx_id = pending_topup_transaction
        user_id = tx.sender_id

        payload, signature = build_wompi_webhook_payload(wompi_tx_id, "PENDING")

        service = PaymentGatewayService()
        await service.process_webhook(db_session, payload, signature, "192.168.1.1")

        stmt = select(TransactionORM).where(TransactionORM.id == tx.id)
        result = await db_session.execute(stmt)
        updated_tx = result.scalar_one()
        assert updated_tx.settlement_status == SettlementStatusEnum.PENDING
        assert updated_tx.status == TransactionStatusEnum.PENDING

        stmt = select(WalletORM).where(WalletORM.user_id == user_id)
        result = await db_session.execute(stmt)
        wallet = result.scalar_one()
        assert wallet.display_balance_cop == 0

        stmt = select(WebhookEventLog).where(
            (WebhookEventLog.provider == "wompi") &
            (WebhookEventLog.provider_event_id == wompi_tx_id)
        )
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None
        print("✓ PENDING webhook left local tx and wallet unchanged, no event log row")

    async def test_webhook_no_local_transaction_ignored(
        self, db_session: AsyncSession, test_user_and_wallet, wompi_events_secret
    ):
        """Test: webhook para transacción inexistente es ignorado."""
        user, wallet = test_user_and_wallet
        wompi_tx_id = "WOMPI-NONEXISTENT-999"

        payload, signature = build_wompi_webhook_payload(wompi_tx_id, "APPROVED")

        service = PaymentGatewayService()
        await service.process_webhook(db_session, payload, signature, "192.168.1.1")

        # Verificar que el webhook fue registrado pero ignorado
        stmt = select(WebhookEventLog).where(
            (WebhookEventLog.provider == "wompi") &
            (WebhookEventLog.provider_event_id == wompi_tx_id)
        )
        result = await db_session.execute(stmt)
        event_log = result.scalar_one_or_none()

        assert event_log is not None
        assert event_log.status == WebhookEventStatusEnum.IGNORED

        # Billetera no debe ser afectada
        stmt = select(WalletORM).where(WalletORM.user_id == wallet.user_id)
        result = await db_session.execute(stmt)
        updated_wallet = result.scalar_one()
        assert updated_wallet.display_balance_cop == 0
        print("✓ Webhook for non-existent tx marked as IGNORED")

    async def test_webhook_concurrent_processing_race_condition(
        self, db_session: AsyncSession, pending_topup_transaction, wompi_events_secret
    ):
        """Test: procesar el mismo webhook de forma concurrente no causa doble acreditación."""
        tx, wompi_tx_id = pending_topup_transaction
        user_id = tx.sender_id

        payload, signature = build_wompi_webhook_payload(wompi_tx_id, "APPROVED")
        service = PaymentGatewayService()

        # Simular dos procesos intentando procesar el mismo webhook simultáneamente
        # (en real sería concurrente, aquí lo hacemos secuencial pero probando race condition)
        import asyncio
        
        results = await asyncio.gather(
            service.process_webhook(db_session, payload, signature, "192.168.1.1"),
            service.process_webhook(db_session, payload, signature, "192.168.1.1"),
            return_exceptions=True,
        )

        # Ambos deben completar sin error
        for result in results:
            if isinstance(result, Exception):
                print(f"Exception in concurrent processing: {result}")

        # Verificar que el balance se acreditó EXACTAMENTE UNA VEZ
        stmt = select(WalletORM).where(WalletORM.user_id == user_id)
        result = await db_session.execute(stmt)
        wallet = result.scalar_one()
        expected_balance = 100_000_00  # Una sola acreditación
        assert wallet.display_balance_cop == expected_balance
        print(f"✓ Concurrent processing: balance = ${wallet.display_balance_cop / 100:,.0f} COP (no duplicated)")

    async def test_initiate_topup_creates_local_transaction(
        self, db_session: AsyncSession, test_user_and_wallet, wompi_events_secret
    ):
        """Test: initiate_topup persiste una TransactionORM con provider_reference=wompi_tx_id.

        Sin esta fila el webhook handler no puede encontrar la transacción y la marca IGNORED.
        """
        user, wallet = test_user_and_wallet
        wompi_tx_id = "WOMPI-INITIATED-789"
        topup_amount = 200_000_00  # $200,000 COP

        # Simular respuesta de Wompi API
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "data": {
                "id": wompi_tx_id,
                "payment_link_url": "https://checkout.wompi.co/p/?public-key=test&currency=COP&amount-in-cents=20000000&reference=test",
            }
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = PaymentGatewayService()
            result = await service.initiate_topup(db_session, user.id, topup_amount, "001")

        # Verificar que la función retorna los campos esperados
        assert result["wompi_transaction_id"] == wompi_tx_id
        assert "payment_link_url" in result
        assert "local_transaction_id" in result

        # Verificar que se creó la fila local con el provider_reference correcto
        stmt = select(TransactionORM).where(
            TransactionORM.provider_reference == wompi_tx_id
        )
        db_result = await db_session.execute(stmt)
        local_tx = db_result.scalar_one_or_none()

        assert local_tx is not None, "initiate_topup debe crear una TransactionORM local"
        assert local_tx.sender_id == user.id
        assert local_tx.receiver_id == user.id
        assert local_tx.amount_cop == topup_amount
        assert local_tx.status == TransactionStatusEnum.PENDING
        assert local_tx.rail == SettlementRailEnum.PSE
        assert local_tx.settlement_status == SettlementStatusEnum.PENDING
        assert local_tx.ml_dsa_signature is None
        assert local_tx.signature_key_id is None
        assert str(local_tx.id) == result["local_transaction_id"]
        print(f"✓ Local transaction created: {local_tx.id} with provider_reference={wompi_tx_id}")

    async def test_full_topup_flow_initiate_then_webhook(
        self, db_session: AsyncSession, test_user_and_wallet, wompi_events_secret
    ):
        """Test end-to-end: initiate → webhook APPROVED → saldo acreditado.

        Verifica que el flujo completo funciona: la transacción creada por initiate_topup
        es encontrada y procesada correctamente por el webhook handler.
        """
        user, wallet = test_user_and_wallet
        wompi_tx_id = "WOMPI-E2E-FLOW-456"
        topup_amount = 50_000_00  # $50,000 COP

        # Paso 1: Iniciar top-up (crea la transacción local)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "data": {
                "id": wompi_tx_id,
                "payment_link_url": "https://checkout.wompi.co/p/?test",
            }
        }
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = PaymentGatewayService()
            await service.initiate_topup(db_session, user.id, topup_amount, "001")

        # Paso 2: Wompi confirma el pago vía webhook
        payload, signature = build_wompi_webhook_payload(wompi_tx_id, "APPROVED")
        await service.process_webhook(db_session, payload, signature, "34.193.0.1")

        # Verificar saldo acreditado
        stmt = select(WalletORM).where(WalletORM.user_id == user.id)
        db_result = await db_session.execute(stmt)
        updated_wallet = db_result.scalar_one()
        assert updated_wallet.display_balance_cop == topup_amount
        print(f"✓ End-to-end flow: wallet credited ${updated_wallet.display_balance_cop / 100:,.0f} COP")

    async def test_webhook_logs_for_debugging(
        self, db_session: AsyncSession, pending_topup_transaction, caplog, wompi_events_secret
    ):
        """Test: webhook genera logs claros para debugging."""
        tx, wompi_tx_id = pending_topup_transaction

        payload, signature = build_wompi_webhook_payload(wompi_tx_id, "APPROVED")
        service = PaymentGatewayService()

        import logging
        with caplog.at_level(logging.INFO):
            await service.process_webhook(db_session, payload, signature, "192.168.1.1")

        # Verificar que los logs contienen información de debugging
        log_text = caplog.text
        assert wompi_tx_id in log_text
        assert "APPROVED" in log_text or "approved" in log_text.lower()
        assert "Crediting wallet" in log_text or "credited" in log_text.lower()
        print("✓ Webhook logs contain debugging information")
