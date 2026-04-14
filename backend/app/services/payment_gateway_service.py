"""Nivo — Payment Gateway Service (Wompi PSE/ACH integration)."""

from __future__ import annotations
import uuid
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.orm.user import User as UserORM
from app.models.orm.wallet import Wallet as WalletORM
from app.models.orm.transaction import (
    Transaction as TransactionORM,
    TransactionStatusEnum,
    SettlementRailEnum,
    SettlementStatusEnum,
)

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
        Procesa webhook de Wompi — valida firma SHA-256.

        Wompi signature validation:
        1. Sort properties alphabetically
        2. Concatenate: property_values + "." + timestamp + "." + events_secret
        3. SHA-256 of that string == checksum in request

        Args:
            db: Sesión de BD
            payload: Datos del webhook
            signature: Checksum SHA-256 en header o body
            ip_address: IP de origen (para logging)

        Raises:
            InvalidWebhookSignatureError: Si la firma no es válida
        """
        # Extraer timestamp del payload
        timestamp = payload.get("timestamp", "")

        # Recolectar valores del payload del evento
        event_data = payload.get("data", {})

        # Construir string a firmar: valores + timestamp + secret
        # En Wompi, necesitamos concatenar los valores del evento en orden
        import json

        # Serializar el evento (data) y concatenar con timestamp y secret
        event_json = json.dumps(event_data, separators=(",", ":"), sort_keys=True)
        to_sign = f"{event_json}.{timestamp}.{settings.WOMPI_EVENTS_SECRET}"

        expected_signature = hashlib.sha256(to_sign.encode()).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.warning(
                f"Invalid Wompi webhook signature from {ip_address} — "
                f"expected {expected_signature[:8]}... got {signature[:8]}..."
            )
            raise InvalidWebhookSignatureError("Firma inválida")

        # Extraer datos de la transacción
        reference = event_data.get("reference")
        wompi_status = event_data.get("status")  # "APPROVED", "DECLINED", "PENDING"
        wompi_tx_id = event_data.get("id")

        if not reference or not wompi_status or not wompi_tx_id:
            logger.error(f"Webhook payload missing required fields: {payload}")
            return

        # Buscar transacción por referencia (idempotency)
        stmt = select(TransactionORM).where(
            TransactionORM.provider_reference == wompi_tx_id
        )
        result = await db.execute(stmt)
        existing_tx = result.scalar_one_or_none()

        # Si ya fue procesada y aprobada, no procesar de nuevo
        if existing_tx and existing_tx.settlement_status == SettlementStatusEnum.SETTLED:
            logger.info(f"Transaction already settled: {wompi_tx_id}")
            return

        # Buscar usuario por referencia (UUID en el reference)
        # En este MVP, buscamos por el provider_reference más reciente sin asignar usuario
        # Una alternativa es incluir user_id en los metadatos de Wompi
        logger.info(f"Processing Wompi webhook: {wompi_tx_id} status={wompi_status}")

        # Por ahora, solo loguear. En producción, asociar con usuario via metadatos
        if wompi_status == "APPROVED":
            logger.info(f"Wompi transaction approved: {wompi_tx_id}")
        elif wompi_status == "DECLINED":
            logger.info(f"Wompi transaction declined: {wompi_tx_id}")

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
