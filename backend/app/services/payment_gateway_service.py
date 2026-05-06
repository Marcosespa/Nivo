"""Nivo — Payment Gateway Service (Wompi PSE/ACH integration)."""

from __future__ import annotations
import uuid
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from opentelemetry import trace

from app.core.config import settings
from app.models.orm.user import User as UserORM
from app.models.orm.wallet import Wallet as WalletORM
from app.models.orm.pqc_key import PQCKey as PQCKeyORM
from app.models.orm.transaction import (
    Transaction as TransactionORM,
    TransactionStatusEnum,
    SettlementRailEnum,
    SettlementStatusEnum,
)
from app.crypto.service import CryptoService

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


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
    2. Backend crea Transaction local en estado PENDING (firmada con PQC)
    3. Backend llama Wompi (o simula en MOCK_MODE) y obtiene payment_link_url
    4. Usuario completa pago en Wompi (5-10 minutos)
    5. Wompi llama webhook POST /api/v1/topup/webhook
    6. Backend valida firma, localiza transacción por reference
    7. Backend acredita balance visual al usuario y marca SETTLED (atómico, SELECT ... FOR UPDATE)

    Modo desarrollo:
    - WOMPI_MOCK_MODE=true genera payment_link_url sintético sin llamar Wompi.
    - WOMPI_BASE_URL permite apuntar a un sandbox/mock alternativo.
    """

    WOMPI_SANDBOX_URL: str = "https://sandbox.wompi.co/v1"
    WOMPI_PRODUCTION_URL: str = "https://production.wompi.co/v1"
    REQUEST_TIMEOUT_SECONDS: int = 10
    MINIMUM_TOPUP_COP: int = 5_000_00  # $5,000 COP en centavos

    def __init__(self):
        # WOMPI_BASE_URL tiene prioridad (permite apuntar a mock local en dev).
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

    async def initiate_topup(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        amount_cop: int,
        bank_code: str,
    ) -> dict:
        """
        Inicia un top-up (recarga) a través de PSE.

        Crea una Transaction local en PENDING firmada con PQC, y solicita a Wompi
        un payment_link_url. En MOCK_MODE se omite la llamada a Wompi y se genera
        un link sintético para pruebas locales.
        """
        with tracer.start_as_current_span("payment_gateway.initiate_topup") as span:
            span.set_attribute("nivo.user_id", str(user_id))
            span.set_attribute("nivo.amount_cop", amount_cop)
            span.set_attribute("nivo.mock_mode", self.mock_mode)

            if amount_cop < self.MINIMUM_TOPUP_COP:
                raise ValueError(
                    f"Monto mínimo para top-up: ${self.MINIMUM_TOPUP_COP / 100:,.0f} COP"
                )

            stmt = select(UserORM).where(UserORM.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
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

            # Recuperar llave PQC activa para firmar la Transaction PENDING
            pqc_stmt = select(PQCKeyORM).where(
                (PQCKeyORM.user_id == user_id) & (PQCKeyORM.is_active == True)
            )
            pqc_result = await db.execute(pqc_stmt)
            pqc_key = pqc_result.scalar_one_or_none()
            if pqc_key is None:
                raise ValueError("Usuario sin llave PQC activa")

            reference = str(uuid.uuid4())
            now = datetime.now(timezone.utc)

            # Firmar metadata del top-up. Llave privada es efímera en dev;
            # en producción proviene de HSM/KMS (ver docs/ADR-003-hsm-key-management.md).
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

            transaction = TransactionORM(
                id=uuid.uuid4(),
                sender_id=user_id,
                receiver_id=user_id,  # top-up: entra a la misma billetera
                amount_cop=amount_cop,
                status=TransactionStatusEnum.PENDING,
                rail=SettlementRailEnum.PSE,
                provider_reference=reference,
                settlement_status=SettlementStatusEnum.PENDING,
                ml_dsa_signature=signed.signature,
                signature_key_id=pqc_key.id,
                message=f"Top-up {bank_code}",
                created_at=now,
            )
            db.add(transaction)
            await db.flush()

            if self.mock_mode:
                wompi_tx_id = f"mock_{reference[:8]}"
                payment_link = f"{self.base_url or 'http://localhost:8001/mock'}/pay/{reference}"
                logger.info(
                    f"[MOCK] Wompi top-up initiated for {user_id} — ref={reference}"
                )
                return {
                    "wompi_transaction_id": wompi_tx_id,
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
                    return {
                        "wompi_transaction_id": wompi_tx_id,
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
        Procesa webhook de Wompi — valida firma SHA-256 y acredita saldo atómicamente.

        En WOMPI_MOCK_MODE la validación de firma se omite para permitir pruebas locales
        con Postman/ngrok sin configurar WOMPI_EVENTS_SECRET.
        """
        with tracer.start_as_current_span("payment_gateway.process_webhook") as span:
            span.set_attribute("nivo.webhook_ip", ip_address)
            span.set_attribute("nivo.mock_mode", self.mock_mode)

            timestamp = payload.get("timestamp") or payload.get("signature", {}).get("timestamp", "")
            event_data = payload.get("data", {})
            if isinstance(event_data, dict) and isinstance(event_data.get("transaction"), dict):
                event_data = event_data["transaction"]

            if not self.mock_mode:
                event_json = json.dumps(event_data, separators=(",", ":"), sort_keys=True)
                to_sign = f"{event_json}.{timestamp}.{settings.WOMPI_EVENTS_SECRET}"
                expected_signature = hashlib.sha256(to_sign.encode()).hexdigest()
                if not hmac.compare_digest(signature, expected_signature):
                    logger.warning(
                        f"Invalid Wompi webhook signature from {ip_address} — "
                        f"expected {expected_signature[:8]}... got {signature[:8]}..."
                    )
                    raise InvalidWebhookSignatureError("Firma inválida")

            reference = event_data.get("reference")
            wompi_status = event_data.get("status")
            wompi_tx_id = event_data.get("id")

            if not reference or not wompi_status:
                logger.error(f"Webhook payload missing required fields: {payload}")
                return

            span.set_attribute("nivo.wompi_status", wompi_status)
            span.set_attribute("nivo.reference", reference)

            # Evitar problemas con transacciones implícitas previas
            await db.rollback()

            async with db.begin():
                tx_stmt = (
                    select(TransactionORM)
                    .where(TransactionORM.provider_reference == reference)
                    .with_for_update()
                )
                tx_result = await db.execute(tx_stmt)
                transaction = tx_result.scalar_one_or_none()

                if transaction is None:
                    logger.warning(f"Webhook: transacción no encontrada para reference={reference}")
                    return

                # Idempotencia: si ya está SETTLED, no procesar de nuevo
                if transaction.settlement_status == SettlementStatusEnum.SETTLED:
                    logger.info(f"Webhook idempotente — ya procesado: {reference}")
                    return

                if wompi_status == "APPROVED":
                    wallet_stmt = (
                        select(WalletORM)
                        .where(WalletORM.user_id == transaction.receiver_id)
                        .with_for_update()
                    )
                    wallet_result = await db.execute(wallet_stmt)
                    wallet = wallet_result.scalar_one_or_none()
                    if wallet is None:
                        logger.error(
                            f"Webhook: billetera no encontrada para user={transaction.receiver_id}"
                        )
                        return

                    wallet.display_balance_cop += transaction.amount_cop
                    transaction.status = TransactionStatusEnum.COMPLETED
                    transaction.settlement_status = SettlementStatusEnum.SETTLED
                    transaction.confirmed_at = datetime.now(timezone.utc)
                    if wompi_tx_id:
                        transaction.message = (transaction.message or "") + f"|wompi:{wompi_tx_id}"
                    logger.info(
                        f"Top-up acreditado: user={transaction.receiver_id} "
                        f"+${transaction.amount_cop / 100:,.0f} COP (ref={reference})"
                    )

                elif wompi_status == "DECLINED":
                    transaction.status = TransactionStatusEnum.FAILED
                    transaction.settlement_status = SettlementStatusEnum.FAILED
                    logger.info(f"Top-up rechazado por Wompi: ref={reference}")

                elif wompi_status == "VOIDED":
                    transaction.status = TransactionStatusEnum.REVERSED
                    transaction.settlement_status = SettlementStatusEnum.REVERSED
                    logger.info(f"Top-up anulado: ref={reference}")

                else:
                    # PENDING u otros estados — no tocar saldo
                    logger.info(f"Wompi webhook status no terminal: {wompi_status}")

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
