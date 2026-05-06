"""Nivo — Payment Gateway Service (Wompi PSE/ACH integration)."""

from __future__ import annotations
import uuid
import hashlib
import hmac
import logging
import json
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core import telemetry
from app.models.orm.user import User as UserORM
from app.models.orm.kyc_funnel_event import KYCFunnelStepEnum, KYCFunnelResultEnum
from app.services.kyc_funnel_service import kyc_funnel_service
from app.models.orm.wallet import Wallet as WalletORM
from app.models.orm.transaction import (
    Transaction as TransactionORM,
    TransactionStatusEnum,
    SettlementRailEnum,
    SettlementStatusEnum,
)
from app.models.orm.webhook_event_log import WebhookEventLog, WebhookEventStatusEnum

logger = logging.getLogger(__name__)


# ─── Errores de dominio ───────────────────────────────────────────────────────

class PaymentGatewayError(Exception):
    """Base de errores de pasarela de pagos."""
    pass


class PaymentGatewayUnavailableError(PaymentGatewayError):
    """Pasarela de pagos no disponible."""
    pass


class InvalidWebhookSignatureError(PaymentGatewayError):
    """Firma de webhook inválida."""
    pass


class TransactionNotFoundError(PaymentGatewayError):
    """Transacción no encontrada."""
    pass


# ─── Payment Gateway Service ──────────────────────────────────────────────────

class PaymentGatewayService:
    """
    Servicio de pasarela de pagos — integración con Wompi para PSE/ACH.

    Flujo de top-up (PSE):
    1. Usuario llama POST /api/v1/topup/initiate
    2. Backend crea transacción en Wompi
    3. Wompi retorna payment_link_url
    4. Usuario completa pago en Wompi (5-10 minutos)
    5. Wompi llama webhook POST /api/v1/topup/webhook
    6. Backend crea/actualiza transacción local
    7. Backend acredita balance visual al usuario

    Límites por plan:
    - FREE: $500,000 COP máximo por transacción
    - PLUS: $2,000,000 COP máximo por transacción
    - PRO: $10,000,000 COP máximo por transacción
    """

    WOMPI_SANDBOX_URL: str = "https://sandbox.wompi.co/v1"
    WOMPI_PRODUCTION_URL: str = "https://production.wompi.co/v1"
    REQUEST_TIMEOUT_SECONDS: int = 10
    MINIMUM_TOPUP_COP: int = 5_000_00  # $5,000 COP en centavos

    def __init__(self):
        self.base_url = (
            self.WOMPI_SANDBOX_URL
            if settings.ENVIRONMENT != "production"
            else self.WOMPI_PRODUCTION_URL
        )

    async def initiate_topup(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        amount_cop: int,
        bank_code: str,
    ) -> dict:
        """
        Inicia un top-up (recarga) a través de PSE.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
            amount_cop: Monto en centavos de COP
            bank_code: Código del banco (ej: "001" para Bancolombia)

        Returns:
            Dict con transaction_id y payment_link_url

        Raises:
            ValueError: Si el monto es inválido o usuario no existe
            PaymentGatewayUnavailableError: Si Wompi API no responde
        """
        # Validar monto mínimo
        if amount_cop < self.MINIMUM_TOPUP_COP:
            raise ValueError(
                f"Monto mínimo para top-up: ${self.MINIMUM_TOPUP_COP / 100:,.0f} COP"
            )

        # Buscar usuario
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"Usuario {user_id} no existe")

        # Validar límite máximo por plan
        plan_limits = {
            "free": 500_000_00,    # $500,000
            "plus": 2_000_000_00,  # $2,000,000
            "pro": 10_000_000_00,  # $10,000,000
        }
        max_amount = plan_limits.get(user.plan.value, 500_000_00)

        if amount_cop > max_amount:
            raise ValueError(
                f"Límite máximo para tu plan: ${max_amount / 100:,.0f} COP"
            )

        # Generar referencia única (idempotency key)
        reference = str(uuid.uuid4())

        # Preparar payload para Wompi
        payload = {
            "amount_in_cents": amount_cop,
            "currency": "COP",
            "customer_email": None,
            "payment_method": {
                "type": "PSE",
                "user_type": 0,  # natural person
                "user_legal_id_type": "CC",
                "user_legal_id": user.phone_number,  # Usar teléfono como ID en MVP
                "financial_institution_code": bank_code,
                "payment_description": "Recarga Nivo",
            },
            "redirect_url": "https://app.nivo.co/topup/result",
            "reference": reference,
            "customer_data": {
                "phone_number": user.phone_number,
            },
        }

        # Llamar Wompi API
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
                    logger.error(
                        f"Wompi API error: {response.status_code} — {response.text}"
                    )
                    raise PaymentGatewayUnavailableError(
                        "No pudimos procesar tu solicitud. Intenta más tarde."
                    )

                data = response.json()
                wompi_tx_id = data.get("data", {}).get("id")
                payment_link = data.get("data", {}).get("payment_link_url")

                if not wompi_tx_id or not payment_link:
                    logger.error(f"Wompi response missing fields: {data}")
                    raise PaymentGatewayUnavailableError("Respuesta inválida de pasarela")

                # Persistir transacción local ANTES de retornar la URL.
                # El webhook handler busca por provider_reference == wompi_tx_id;
                # sin esta fila el pago aprobado siempre quedaría como IGNORED.
                local_tx = TransactionORM(
                    sender_id=user_id,
                    receiver_id=user_id,  # top-up: el usuario recarga su propia billetera
                    amount_cop=amount_cop,
                    status=TransactionStatusEnum.PENDING,
                    rail=SettlementRailEnum.PSE,
                    provider_reference=wompi_tx_id,
                    settlement_status=SettlementStatusEnum.PENDING,
                    ml_dsa_signature=None,   # autenticado por HMAC de Wompi
                    signature_key_id=None,
                )
                db.add(local_tx)
                await db.commit()
                await db.refresh(local_tx)

                logger.info(
                    f"Top-up initiated: local_tx={local_tx.id} "
                    f"wompi_tx={wompi_tx_id} amount=${amount_cop / 100:,.0f} COP"
                )

                return {
                    "wompi_transaction_id": wompi_tx_id,
                    "local_transaction_id": str(local_tx.id),
                    "payment_link_url": payment_link,
                    "reference": reference,
                }

            except httpx.TimeoutException:
                logger.error("Wompi API timeout")
                raise PaymentGatewayUnavailableError(
                    "La pasarela está tardando. Intenta más tarde."
                )
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling Wompi API: {e}")
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
        """
        Procesa webhook de Wompi — validación de firma, idempotencia y acreditación.

        FLUJO:
        1. Validar firma SHA-256 del webhook
        2. Verificar idempotencia via event log (provider_event_id único)
        3. Mapear evento a transacción local
        4. Si APPROVED: acreditar wallet de usuario
        5. Si DECLINED/VOIDED/REJECTED: marcar transacción como fallida (PENDING se ignora hasta estado final)
        6. Registrar en webhook_event_log para auditoría

        Wompi signature validation:
        - Construir string: JSON(event_data ordenado) + "." + timestamp + "." + WOMPI_EVENTS_SECRET
        - SHA-256 hexdigest debe coincidir con X-Event-Checksum

        Args:
            db: Sesión de BD
            payload: Dict con data, timestamp, signature
            signature: Checksum SHA-256 del header X-Event-Checksum
            ip_address: IP de origen (para auditoría)

        Raises:
            InvalidWebhookSignatureError: Si firma inválida
        """
        # ─── Paso 1: Extracción de datos base ────────────────────────────────────
        timestamp = payload.get("timestamp", "")
        event_data = payload.get("data", {})
        wompi_tx_id = event_data.get("id", "")  # ID único de Wompi
        wompi_status = event_data.get("status", "")  # APPROVED, DECLINED, PENDING, etc

        if not wompi_tx_id:
            logger.error(f"Wompi webhook missing transaction ID: {payload}")
            return

        # ─── Paso 2: Validar firma ────────────────────────────────────────────────
        with telemetry.span("webhook.wompi.signature_verify") as sig_span:
            sig_span.set_attribute("webhook.provider", "wompi")
            sig_span.set_attribute("webhook.status", wompi_status)
            sig_span.set_attribute("webhook.ip", ip_address)
            sig_span.set_attribute("webhook.tx_id_prefix", wompi_tx_id[:8])

            if not signature or not settings.WOMPI_EVENTS_SECRET:
                logger.error(
                    f"Wompi webhook signature validation skipped: "
                    f"signature_present={bool(signature)} secret_configured={bool(settings.WOMPI_EVENTS_SECRET)}"
                )
                sig_span.set_attribute("webhook.signature_result", "missing")
                if settings.ENVIRONMENT == "production":
                    raise InvalidWebhookSignatureError("Firma de webhook requerida en producción")
            elif signature and settings.WOMPI_EVENTS_SECRET:
                event_json = json.dumps(event_data, separators=(",", ":"), sort_keys=True)
                to_sign = f"{event_json}.{timestamp}.{settings.WOMPI_EVENTS_SECRET}"
                expected_signature = hashlib.sha256(to_sign.encode()).hexdigest()

                if not hmac.compare_digest(signature, expected_signature):
                    logger.warning(
                        f"Invalid Wompi webhook signature from {ip_address} "
                        f"for tx {wompi_tx_id} — "
                        f"expected {expected_signature[:8]}... got {signature[:8]}..."
                    )
                    sig_span.set_attribute("webhook.signature_result", "invalid")
                    raise InvalidWebhookSignatureError("Firma inválida de Wompi")

                sig_span.set_attribute("webhook.signature_result", "valid")
                logger.info(f"✓ Wompi webhook signature valid for tx {wompi_tx_id}")

        # PENDING: el pago sigue en Wompi; no tomar fila de idempotencia ni marcar la transacción local
        if wompi_status == "PENDING":
            logger.info(
                f"Wompi webhook PENDING for {wompi_tx_id}: awaiting final status, skipping"
            )
            return

        # ─── Paso 3: Idempotencia via event log ───────────────────────────────────
        try:
            # Buscar si ya procesamos este webhook
            stmt = select(WebhookEventLog).where(
                (WebhookEventLog.provider == "wompi") &
                (WebhookEventLog.provider_event_id == wompi_tx_id)
            )
            result = await db.execute(stmt)
            existing_event = result.scalar_one_or_none()

            if existing_event and existing_event.status in {
                WebhookEventStatusEnum.PROCESSED,
                WebhookEventStatusEnum.IGNORED,
            }:
                logger.info(
                    f"Webhook already processed: {wompi_tx_id} "
                    f"(status={existing_event.status.value}, processed_at={existing_event.processed_at})"
                )
                return

            # ─── Crear entrada en event log (marca como "processing") ─────────────
            if not existing_event:
                event_log = WebhookEventLog(
                    provider="wompi",
                    provider_event_id=wompi_tx_id,
                    event_type=payload.get("event", "transaction.updated"),
                    raw_payload=json.dumps(payload),
                    status=WebhookEventStatusEnum.PROCESSING,
                    ip_address=ip_address,
                )
                db.add(event_log)
                await db.flush()  # Asegurar que el insert ocurra antes de procesar
            else:
                existing_event.status = WebhookEventStatusEnum.PROCESSING
                existing_event.retry_count += 1

        except IntegrityError:
            # Race condition: otro proceso ya creó la entrada
            # Rollback y reintentar lectura
            await db.rollback()
            logger.info(f"Webhook race condition for {wompi_tx_id}, retrying...")
            # Reintentar lectura después de rollback
            stmt = select(WebhookEventLog).where(
                (WebhookEventLog.provider == "wompi") &
                (WebhookEventLog.provider_event_id == wompi_tx_id)
            )
            result = await db.execute(stmt)
            existing_event = result.scalar_one_or_none()
            if existing_event and existing_event.status in {
                WebhookEventStatusEnum.PROCESSED,
                WebhookEventStatusEnum.IGNORED,
                WebhookEventStatusEnum.PROCESSING,
            }:
                logger.info(
                    f"Another process owns or finished webhook {wompi_tx_id} "
                    f"(status={existing_event.status.value})"
                )
                return

        # ─── Paso 4: Buscar transacción local por provider_reference ──────────────
        stmt = select(TransactionORM).where(
            TransactionORM.provider_reference == wompi_tx_id
        )
        result = await db.execute(stmt)
        local_tx = result.scalar_one_or_none()

        if not local_tx:
            logger.warning(
                f"Wompi webhook received but no local transaction found for {wompi_tx_id}. "
                f"Status: {wompi_status}. This might be a stale or unsolicited webhook."
            )
            # Marcar como ignorado en event log
            stmt = select(WebhookEventLog).where(
                (WebhookEventLog.provider == "wompi") &
                (WebhookEventLog.provider_event_id == wompi_tx_id)
            )
            result = await db.execute(stmt)
            event_log = result.scalar_one_or_none()
            if event_log:
                event_log.status = WebhookEventStatusEnum.IGNORED
                event_log.error_message = "No local transaction found"
                event_log.processed_at = datetime.now(timezone.utc)
            await db.commit()
            return

        logger.info(
            f"Processing Wompi webhook: tx_id={wompi_tx_id} "
            f"local_tx={local_tx.id} status={wompi_status}"
        )

        # ─── Paso 5: Mapear estado de Wompi a estado local ─────────────────────────
        try:
            if wompi_status == "APPROVED":
                await self._process_topup_approved(db, local_tx, wompi_tx_id, event_data)
            elif wompi_status in {"DECLINED", "VOIDED", "REJECTED"}:
                await self._process_topup_declined(db, local_tx, wompi_status)
            else:
                logger.warning(f"Unknown Wompi status: {wompi_status} for {wompi_tx_id}")
                local_tx.settlement_status = SettlementStatusEnum.FAILED

            # ─── Marcar event log como procesado ──────────────────────────────────
            stmt = select(WebhookEventLog).where(
                (WebhookEventLog.provider == "wompi") &
                (WebhookEventLog.provider_event_id == wompi_tx_id)
            )
            result = await db.execute(stmt)
            event_log = result.scalar_one_or_none()
            if event_log:
                event_log.status = WebhookEventStatusEnum.PROCESSED
                event_log.processed_at = datetime.now(timezone.utc)
                event_log.related_transaction_id = local_tx.id

            await db.commit()
            logger.info(f"✓ Webhook processed successfully: {wompi_tx_id}")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing Wompi webhook {wompi_tx_id}: {e}", exc_info=True)
            # Marcar event log como FAILED (UPDATE directo: sesión limpia tras rollback)
            try:
                err_msg = str(e)[:1024]
                now = datetime.now(timezone.utc)
                await db.execute(
                    update(WebhookEventLog)
                    .where(
                        WebhookEventLog.provider == "wompi",
                        WebhookEventLog.provider_event_id == wompi_tx_id,
                    )
                    .values(
                        status=WebhookEventStatusEnum.FAILED,
                        error_message=err_msg,
                        processed_at=now,
                    )
                )
                await db.commit()
            except Exception as inner_e:
                logger.error(f"Failed to mark event as failed: {inner_e}")

    async def _process_topup_approved(
        self,
        db: AsyncSession,
        local_tx: TransactionORM,
        wompi_tx_id: str,
        event_data: dict,
    ) -> None:
        """
        Procesa aprobación de top-up: acredita saldo del usuario.

        Args:
            db: Sesión DB
            local_tx: Transacción local
            wompi_tx_id: ID de Wompi
            event_data: Datos del evento de Wompi
        """
        # Ya está marcada como aprobada (esperar la acreditación)
        if local_tx.settlement_status == SettlementStatusEnum.SETTLED:
            logger.info(f"Top-up already settled: {wompi_tx_id}")
            return

        # Buscar billetera del usuario (sender = usuario que hace top-up, receiver = sistema)
        stmt = select(WalletORM).where(
            WalletORM.user_id == local_tx.sender_id
        ).with_for_update()
        result = await db.execute(stmt)
        wallet = result.scalar_one_or_none()

        if not wallet:
            logger.error(f"Wallet not found for user {local_tx.sender_id}")
            local_tx.settlement_status = SettlementStatusEnum.FAILED
            return

        # Acreditar saldo
        with telemetry.span("wallet.credit") as credit_span:
            credit_span.set_attribute("wallet.user_id_hash", telemetry.hash_user_id(local_tx.sender_id))
            credit_span.set_attribute("wallet.amount_range", telemetry.amount_range(local_tx.amount_cop))
            credit_span.set_attribute("wallet.rail", "pse")

            logger.info(
                f"Crediting wallet: user={local_tx.sender_id} "
                f"amount=${local_tx.amount_cop / 100:,.0f} COP"
            )
            old_balance = wallet.display_balance_cop
            wallet.display_balance_cop += local_tx.amount_cop
            wallet.last_updated = datetime.now(timezone.utc)

            local_tx.settlement_status = SettlementStatusEnum.SETTLED
            local_tx.status = TransactionStatusEnum.COMPLETED
            local_tx.confirmed_at = datetime.now(timezone.utc)

            credit_span.set_attribute("wallet.result", "credited")

        # Track first deposit milestone
        if old_balance == 0:
            await kyc_funnel_service.track(
                db,
                local_tx.sender_id,
                KYCFunnelStepEnum.FIRST_DEPOSIT,
                result=KYCFunnelResultEnum.COMPLETED,
            )

        logger.info(
            f"✓ Top-up APPROVED and credited: {wompi_tx_id} "
            f"user={local_tx.sender_id} new_balance=${wallet.display_balance_cop / 100:,.0f} COP"
        )

    async def _process_topup_declined(
        self,
        db: AsyncSession,
        local_tx: TransactionORM,
        wompi_status: str,
    ) -> None:
        """
        Procesa rechazo/cancelación de top-up.

        Args:
            db: Sesión DB
            local_tx: Transacción local
            wompi_status: Estado de Wompi (DECLINED, VOIDED, etc)
        """
        logger.warning(
            f"Top-up {wompi_status}: tx={local_tx.id} "
            f"user={local_tx.sender_id} amount=${local_tx.amount_cop / 100:,.0f} COP"
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
        """
        Obtiene historial de top-ups del usuario.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
            limit: Número máximo de registros

        Returns:
            Lista de transacciones de tipo 'topup'
        """
        stmt = (
            select(TransactionORM)
            .where(
                (TransactionORM.sender_id == user_id) &
                (TransactionORM.rail == SettlementRailEnum.PSE)
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
