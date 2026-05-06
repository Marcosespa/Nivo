"""Nivo — Payment Gateway Service (Wompi PSE/ACH integration)."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import uuid
import asyncio
from datetime import datetime, timezone

import httpx
from opentelemetry import trace
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import telemetry
from app.core.config import settings
from app.crypto.service import CryptoService
from app.models.orm.kyc_funnel_event import KYCFunnelResultEnum, KYCFunnelStepEnum
from app.models.orm.pqc_key import PQCKey as PQCKeyORM
from app.models.orm.transaction import (
    SettlementRailEnum,
    SettlementStatusEnum,
    Transaction as TransactionORM,
    TransactionStatusEnum,
)
from app.models.orm.user import User as UserORM
from app.models.orm.wallet import Wallet as WalletORM
from app.models.orm.webhook_event_log import WebhookEventLog, WebhookEventStatusEnum
from app.services.kyc_funnel_service import kyc_funnel_service

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class PaymentGatewayError(Exception):
    """Base de errores de pasarela de pagos."""


class PaymentGatewayUnavailableError(PaymentGatewayError):
    """Pasarela de pagos no disponible."""


class InvalidWebhookSignatureError(PaymentGatewayError):
    """Firma de webhook inválida."""


class TransactionNotFoundError(PaymentGatewayError):
    """Transacción no encontrada."""


class PaymentGatewayService:
    """
    Servicio de pasarela de pagos — integración con Wompi para PSE/ACH.

    Conserva el flujo de top-up firmado localmente y agrega soporte dev para
    WOMPI_MOCK_MODE/WOMPI_BASE_URL, validación HMAC e idempotencia vía event log.
    """

    WOMPI_SANDBOX_URL: str = "https://sandbox.wompi.co/v1"
    WOMPI_PRODUCTION_URL: str = "https://production.wompi.co/v1"
    REQUEST_TIMEOUT_SECONDS: int = 10
    MINIMUM_TOPUP_COP: int = 5_000_00

    def __init__(self):
        if settings.WOMPI_BASE_URL:
            self.base_url = settings.WOMPI_BASE_URL
        else:
            self.base_url = (
                self.WOMPI_SANDBOX_URL
                if settings.ENVIRONMENT != "production"
                else self.WOMPI_PRODUCTION_URL
            )
        self.mock_mode = settings.WOMPI_MOCK_MODE and settings.ENVIRONMENT != "production"
        self.crypto = CryptoService()
        self._webhook_locks: dict[str, asyncio.Lock] = {}

    async def initiate_topup(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        amount_cop: int,
        bank_code: str,
    ) -> dict:
        """Inicia un top-up PSE y deja una Transaction local PENDING firmada."""
        with tracer.start_as_current_span("payment_gateway.initiate_topup") as span:
            span.set_attribute("nivo.user_id", str(user_id))
            span.set_attribute("nivo.amount_cop", amount_cop)
            span.set_attribute("nivo.mock_mode", self.mock_mode)

            if amount_cop < self.MINIMUM_TOPUP_COP:
                raise ValueError(
                    f"Monto mínimo para top-up: ${self.MINIMUM_TOPUP_COP / 100:,.0f} COP"
                )

            user = await db.scalar(select(UserORM).where(UserORM.id == user_id))
            if not user:
                raise ValueError(f"Usuario {user_id} no existe")

            plan_limits = {
                "free": 500_000_00,
                "plus": 2_000_000_00,
                "pro": 10_000_000_00,
            }
            max_amount = plan_limits.get(user.plan.value, 500_000_00)
            if amount_cop > max_amount:
                raise ValueError(
                    f"Límite máximo para tu plan: ${max_amount / 100:,.0f} COP"
                )

            pqc_key = await db.scalar(
                select(PQCKeyORM).where(
                    (PQCKeyORM.user_id == user_id) & (PQCKeyORM.is_active == True)
                )
            )

            reference = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            signature = None
            signature_key_id = None
            if pqc_key is not None:
                signing_kp = self.crypto.generate_signing_keypair()
                tx_payload = (
                    f"topup:{reference}|user:{user_id}|amount:{amount_cop}|ts:{now.isoformat()}"
                ).encode()
                signed = self.crypto.sign_transaction(
                    tx_id=reference,
                    payload=tx_payload,
                    signing_secret_key=signing_kp.secret_key,
                    public_key_fingerprint=pqc_key.key_fingerprint,
                )
                signature = signed.signature
                signature_key_id = pqc_key.id

            transaction = TransactionORM(
                id=uuid.uuid4(),
                sender_id=user_id,
                receiver_id=user_id,
                amount_cop=amount_cop,
                status=TransactionStatusEnum.PENDING,
                rail=SettlementRailEnum.PSE,
                provider_reference=reference,
                settlement_status=SettlementStatusEnum.PENDING,
                ml_dsa_signature=signature,
                signature_key_id=signature_key_id,
                message=f"Top-up {bank_code}",
                created_at=now,
            )
            db.add(transaction)
            await db.flush()

            if self.mock_mode:
                wompi_tx_id = f"mock_{reference[:8]}"
                payment_link = f"{self.base_url or 'http://localhost:8001/mock'}/pay/{reference}"
                logger.info("[MOCK] Wompi top-up initiated for %s — ref=%s", user_id, reference)
                return {
                    "wompi_transaction_id": wompi_tx_id,
                    "local_transaction_id": str(transaction.id),
                    "payment_link_url": payment_link,
                    "reference": reference,
                }

            payload = {
                "amount_in_cents": amount_cop,
                "currency": "COP",
                "customer_email": None,
                "payment_method": {
                    "type": "PSE",
                    "user_type": 0,
                    "user_legal_id_type": "CC",
                    "user_legal_id": user.phone_number,
                    "financial_institution_code": bank_code,
                    "payment_description": "Recarga Nivo",
                },
                "redirect_url": "https://app.nivo.co/topup/result",
                "reference": reference,
                "customer_data": {"phone_number": user.phone_number},
            }

            async with httpx.AsyncClient(timeout=self.REQUEST_TIMEOUT_SECONDS) as client:
                try:
                    response = await client.post(
                        f"{self.base_url}/transactions",
                        json=payload,
                        headers={
                            "Authorization": f"Bearer {settings.PAYMENT_GATEWAY_API_KEY}",
                            "Content-Type": "application/json",
                        },
                    )
                    if response.status_code != 201:
                        logger.error("Wompi API error: %s — %s", response.status_code, response.text)
                        raise PaymentGatewayUnavailableError(
                            "No pudimos procesar tu solicitud. Intenta más tarde."
                        )

                    data = response.json()
                    wompi_tx_id = data.get("data", {}).get("id")
                    payment_link = data.get("data", {}).get("payment_link_url")
                    if not wompi_tx_id or not payment_link:
                        logger.error("Wompi response missing fields: %s", data)
                        raise PaymentGatewayUnavailableError("Respuesta inválida de pasarela")

                    transaction.provider_reference = wompi_tx_id
                    await db.flush()

                    return {
                        "wompi_transaction_id": wompi_tx_id,
                        "local_transaction_id": str(transaction.id),
                        "payment_link_url": payment_link,
                        "reference": reference,
                    }
                except httpx.TimeoutException:
                    logger.error("Wompi API timeout")
                    raise PaymentGatewayUnavailableError(
                        "La pasarela está tardando. Intenta más tarde."
                    )
                except httpx.HTTPError as e:
                    logger.error("HTTP error calling Wompi API: %s", e)
                    raise PaymentGatewayUnavailableError(
                        "Error de conexión con la pasarela de pagos"
                    )

    async def process_webhook(
        self,
        db: AsyncSession,
        payload: dict,
        signature: str,
        ip_address: str,
    ) -> None:
        """Procesa webhook de Wompi con firma, idempotencia y acreditación."""
        with tracer.start_as_current_span("payment_gateway.process_webhook") as span:
            span.set_attribute("nivo.webhook_ip", ip_address)
            span.set_attribute("nivo.mock_mode", self.mock_mode)

            timestamp = payload.get("timestamp") or payload.get("signature", {}).get("timestamp", "")
            event_data = payload.get("data", {})
            if isinstance(event_data, dict) and isinstance(event_data.get("transaction"), dict):
                event_data = event_data["transaction"]

            reference = event_data.get("reference")
            wompi_status = event_data.get("status")
            wompi_tx_id = event_data.get("id") or reference

            if not reference or not wompi_status:
                logger.error("Webhook payload missing required fields: %s", payload)
                return

            span.set_attribute("nivo.wompi_status", wompi_status)
            span.set_attribute("nivo.reference", reference)

            await self._validate_webhook_signature(
                event_data=event_data,
                timestamp=timestamp,
                signature=signature,
                ip_address=ip_address,
                wompi_tx_id=wompi_tx_id,
                wompi_status=wompi_status,
            )

            if wompi_status == "PENDING":
                logger.info("Wompi webhook PENDING for %s: awaiting final status", wompi_tx_id)
                return

            lock = self._webhook_locks.setdefault(wompi_tx_id, asyncio.Lock())
            async with lock:
                event_log = await self._claim_webhook_event(db, payload, wompi_tx_id, ip_address)
                if event_log is None:
                    return

                try:
                    local_tx = await db.scalar(
                        select(TransactionORM)
                        .where(
                            (TransactionORM.provider_reference == wompi_tx_id)
                            | (TransactionORM.provider_reference == reference)
                        )
                        .with_for_update()
                    )
                    if local_tx is None:
                        logger.warning(
                            "Webhook: transacción no encontrada para wompi_tx_id=%s reference=%s",
                            wompi_tx_id,
                            reference,
                        )
                        event_log.status = WebhookEventStatusEnum.IGNORED
                        event_log.error_message = "No local transaction found"
                        event_log.processed_at = datetime.now(timezone.utc)
                        await db.commit()
                        return

                    if local_tx.settlement_status == SettlementStatusEnum.SETTLED:
                        logger.info("Webhook idempotente — ya procesado: %s", wompi_tx_id)
                        event_log.status = WebhookEventStatusEnum.PROCESSED
                        event_log.related_transaction_id = local_tx.id
                        event_log.processed_at = datetime.now(timezone.utc)
                        await db.commit()
                        return

                    if wompi_status == "APPROVED":
                        await self._process_topup_approved(db, local_tx, wompi_tx_id, event_data)
                    elif wompi_status in {"DECLINED", "REJECTED"}:
                        await self._process_topup_declined(db, local_tx, wompi_status)
                    elif wompi_status == "VOIDED":
                        local_tx.status = TransactionStatusEnum.REVERSED
                        local_tx.settlement_status = SettlementStatusEnum.REVERSED
                        local_tx.confirmed_at = datetime.now(timezone.utc)
                    else:
                        logger.warning("Unknown Wompi status: %s for %s", wompi_status, wompi_tx_id)
                        local_tx.settlement_status = SettlementStatusEnum.FAILED

                    event_log.status = WebhookEventStatusEnum.PROCESSED
                    event_log.processed_at = datetime.now(timezone.utc)
                    event_log.related_transaction_id = local_tx.id
                    await db.commit()
                    logger.info("Webhook processed successfully: %s status=%s", wompi_tx_id, wompi_status)
                except Exception as e:
                    await db.rollback()
                    logger.error("Error processing Wompi webhook %s: %s", wompi_tx_id, e, exc_info=True)
                    await self._mark_webhook_failed(db, wompi_tx_id, e)

    async def _validate_webhook_signature(
        self,
        *,
        event_data: dict,
        timestamp: str,
        signature: str,
        ip_address: str,
        wompi_tx_id: str,
        wompi_status: str,
    ) -> None:
        with telemetry.span("webhook.wompi.signature_verify") as sig_span:
            sig_span.set_attribute("webhook.provider", "wompi")
            sig_span.set_attribute("webhook.status", wompi_status)
            sig_span.set_attribute("webhook.ip", ip_address)
            sig_span.set_attribute("webhook.tx_id_prefix", wompi_tx_id[:8])

            if self.mock_mode:
                sig_span.set_attribute("webhook.signature_result", "mock_skipped")
                return

            if not signature or not settings.WOMPI_EVENTS_SECRET:
                sig_span.set_attribute("webhook.signature_result", "missing")
                if settings.ENVIRONMENT == "production":
                    raise InvalidWebhookSignatureError("Firma de webhook requerida en producción")
                logger.warning(
                    "Wompi webhook signature validation skipped: signature_present=%s secret_configured=%s",
                    bool(signature),
                    bool(settings.WOMPI_EVENTS_SECRET),
                )
                return

            event_json = json.dumps(event_data, separators=(",", ":"), sort_keys=True)
            to_sign = f"{event_json}.{timestamp}.{settings.WOMPI_EVENTS_SECRET}"
            expected_signature = hashlib.sha256(to_sign.encode()).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                logger.warning(
                    "Invalid Wompi webhook signature from %s for tx %s — expected %s... got %s...",
                    ip_address,
                    wompi_tx_id,
                    expected_signature[:8],
                    signature[:8],
                )
                sig_span.set_attribute("webhook.signature_result", "invalid")
                raise InvalidWebhookSignatureError("Firma inválida de Wompi")

            sig_span.set_attribute("webhook.signature_result", "valid")

    async def _claim_webhook_event(
        self,
        db: AsyncSession,
        payload: dict,
        wompi_tx_id: str,
        ip_address: str,
    ) -> WebhookEventLog | None:
        try:
            existing_event = await db.scalar(
                select(WebhookEventLog).where(
                    (WebhookEventLog.provider == "wompi")
                    & (WebhookEventLog.provider_event_id == wompi_tx_id)
                )
            )
            if existing_event and existing_event.status in {
                WebhookEventStatusEnum.PROCESSED,
                WebhookEventStatusEnum.IGNORED,
            }:
                logger.info("Webhook already processed: %s", wompi_tx_id)
                return None

            if existing_event:
                existing_event.status = WebhookEventStatusEnum.PROCESSING
                existing_event.retry_count += 1
                return existing_event

            event_log = WebhookEventLog(
                provider="wompi",
                provider_event_id=wompi_tx_id,
                event_type=payload.get("event", "transaction.updated"),
                raw_payload=json.dumps(payload),
                status=WebhookEventStatusEnum.PROCESSING,
                ip_address=ip_address,
            )
            db.add(event_log)
            await db.flush()
            return event_log
        except IntegrityError:
            await db.rollback()
            logger.info("Webhook race condition for %s, retrying read", wompi_tx_id)
            existing_event = await db.scalar(
                select(WebhookEventLog).where(
                    (WebhookEventLog.provider == "wompi")
                    & (WebhookEventLog.provider_event_id == wompi_tx_id)
                )
            )
            if existing_event and existing_event.status in {
                WebhookEventStatusEnum.PROCESSED,
                WebhookEventStatusEnum.IGNORED,
                WebhookEventStatusEnum.PROCESSING,
            }:
                logger.info("Another process owns or finished webhook %s", wompi_tx_id)
                return None
            return existing_event

    async def _mark_webhook_failed(
        self,
        db: AsyncSession,
        wompi_tx_id: str,
        error: Exception,
    ) -> None:
        try:
            await db.execute(
                update(WebhookEventLog)
                .where(
                    WebhookEventLog.provider == "wompi",
                    WebhookEventLog.provider_event_id == wompi_tx_id,
                )
                .values(
                    status=WebhookEventStatusEnum.FAILED,
                    error_message=str(error)[:1024],
                    processed_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()
        except Exception as inner_e:
            logger.error("Failed to mark event as failed: %s", inner_e)

    async def _process_topup_approved(
        self,
        db: AsyncSession,
        local_tx: TransactionORM,
        wompi_tx_id: str,
        event_data: dict,
    ) -> None:
        """Acredita el top-up aprobado en la wallet del usuario."""
        if local_tx.settlement_status == SettlementStatusEnum.SETTLED:
            logger.info("Top-up already settled: %s", wompi_tx_id)
            return

        wallet = await db.scalar(
            select(WalletORM)
            .where(WalletORM.user_id == local_tx.receiver_id)
            .with_for_update()
        )
        if not wallet:
            logger.error("Wallet not found for user %s", local_tx.receiver_id)
            local_tx.settlement_status = SettlementStatusEnum.FAILED
            return

        with telemetry.span("wallet.credit") as credit_span:
            credit_span.set_attribute("wallet.user_id_hash", telemetry.hash_user_id(local_tx.receiver_id))
            credit_span.set_attribute("wallet.amount_range", telemetry.amount_range(local_tx.amount_cop))
            credit_span.set_attribute("wallet.rail", "pse")

            old_balance = wallet.display_balance_cop
            logger.info(
                "Crediting wallet: user=%s amount=$%s COP wompi_tx_id=%s",
                local_tx.receiver_id,
                f"{local_tx.amount_cop / 100:,.0f}",
                wompi_tx_id,
            )
            wallet.display_balance_cop += local_tx.amount_cop
            wallet.last_updated = datetime.now(timezone.utc)
            local_tx.settlement_status = SettlementStatusEnum.SETTLED
            local_tx.status = TransactionStatusEnum.COMPLETED
            local_tx.confirmed_at = datetime.now(timezone.utc)
            if event_data.get("id"):
                local_tx.message = (local_tx.message or "") + f"|wompi:{event_data['id']}"
            credit_span.set_attribute("wallet.result", "credited")

        if old_balance == 0:
            await kyc_funnel_service.track(
                db,
                local_tx.receiver_id,
                KYCFunnelStepEnum.FIRST_DEPOSIT,
                result=KYCFunnelResultEnum.COMPLETED,
            )

        logger.info(
            "Top-up APPROVED and credited: %s user=%s new_balance=$%s COP",
            wompi_tx_id,
            local_tx.receiver_id,
            f"{wallet.display_balance_cop / 100:,.0f}",
        )

    async def _process_topup_declined(
        self,
        db: AsyncSession,
        local_tx: TransactionORM,
        wompi_status: str,
    ) -> None:
        """Marca un top-up rechazado como fallido."""
        logger.warning(
            "Top-up %s: tx=%s user=%s amount=$%s COP",
            wompi_status,
            local_tx.id,
            local_tx.receiver_id,
            f"{local_tx.amount_cop / 100:,.0f}",
        )
        local_tx.settlement_status = SettlementStatusEnum.FAILED
        local_tx.status = TransactionStatusEnum.FAILED
        local_tx.confirmed_at = datetime.now(timezone.utc)

    async def get_topup_history(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 20,
    ) -> list[dict]:
        """Obtiene historial de top-ups del usuario."""
        stmt = (
            select(TransactionORM)
            .where(
                (TransactionORM.sender_id == user_id)
                & (TransactionORM.rail == SettlementRailEnum.PSE)
            )
            .order_by(TransactionORM.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        transactions = result.scalars().all()

        return [
            {
                "id": str(tx.id),
                "amount_cop": tx.amount_cop,
                "amount_display": f"${tx.amount_cop / 100:,.0f} COP",
                "status": tx.status.value,
                "settlement_status": tx.settlement_status.value,
                "created_at": tx.created_at.isoformat(),
            }
            for tx in transactions
        ]
