"""Nivo — KYC Service (Truora integration)."""

from __future__ import annotations
import uuid
import hmac
import hashlib
import logging
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.orm.user import User as UserORM, KYCStatusEnum

logger = logging.getLogger(__name__)


# ─── Errores de dominio ───────────────────────────────────────────────────────

class KYCError(Exception):
    """Base de errores de KYC."""
    pass


class KYCServiceUnavailableError(KYCError):
    """Servicio de KYC no disponible."""
    pass


class InvalidWebhookSignatureError(KYCError):
    """Firma de webhook inválida."""
    pass


class KYCNotInitiatedError(KYCError):
    """Usuario no ha iniciado KYC."""
    pass


# ─── KYC Service ──────────────────────────────────────────────────────────────

class KYCService:
    """
    Servicio de KYC — integración con Truora para verificación de identidad.

    Flujo:
    1. Usuario llama POST /api/v1/kyc/initiate
    2. Backend llama Truora API: POST /v1/checks
    3. Truora retorna verification URL
    4. Usuario completa verificación en Truora (2-4 minutos)
    5. Truora llama webhook POST /api/v1/kyc/webhook
    6. Backend actualiza kyc_status en users
    """

    TRUORA_BASE_URL: str = "https://api.truora.com"
    REQUEST_TIMEOUT_SECONDS: int = 10

    async def initiate_verification(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> dict:
        """
        Inicia un proceso de verificación de identidad con Truora.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario

        Returns:
            Dict con check_id y verification_url

        Raises:
            KYCNotInitiatedError: Si el usuario ya fue verificado
            KYCServiceUnavailableError: Si Truora API no responde
        """
        # Buscar usuario
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"Usuario {user_id} no existe")

        # Verificar que el usuario está en estado 'pending'
        if user.kyc_status != KYCStatusEnum.PENDING:
            raise KYCNotInitiatedError(
                f"El usuario ya fue verificado o rechazado. Estado: {user.kyc_status.value}"
            )

        # Preparar payload para Truora
        payload = {
            "country": "CO",
            "type": "person",
            "user_authorized": True,
            "send_result_email": False,
            "language": "es-CO",
            "metadata": {
                "nivo_user_id": str(user_id),
            },
        }

        # Llamar Truora API
        async with httpx.AsyncClient(timeout=self.REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.post(
                    f"{self.TRUORA_BASE_URL}/v1/checks",
                    json=payload,
                    headers={
                        "Truora-API-Key": settings.KYC_API_KEY,
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code != 201:
                    logger.error(
                        f"Truora API error: {response.status_code} — {response.text}"
                    )
                    raise KYCServiceUnavailableError(
                        "No pudimos contactar al servicio de verificación. Intenta más tarde."
                    )

                data = response.json()
                check_id = data.get("check_id")
                verification_link = data.get("link")

                if not check_id or not verification_link:
                    logger.error(f"Truora response missing fields: {data}")
                    raise KYCServiceUnavailableError("Respuesta inválida del servicio de KYC")

                # Guardar check_id en la BD (campo kyc_provider_id)
                user.kyc_provider_id = check_id
                await db.flush()

                return {
                    "check_id": check_id,
                    "verification_url": verification_link,
                }

            except httpx.TimeoutException:
                logger.error("Truora API timeout")
                raise KYCServiceUnavailableError(
                    "El servicio de verificación está tardando. Intenta más tarde."
                )
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling Truora API: {e}")
                raise KYCServiceUnavailableError(
                    "Error de conexión con el servicio de verificación"
                )

    async def process_webhook(
        self,
        db: AsyncSession,
        payload: dict,
        signature: str,
        ip_address: str,
    ) -> None:
        """
        Procesa webhook de Truora — IMPORTANTE: valida firma HMAC-SHA256.

        Args:
            db: Sesión de BD
            payload: Datos del webhook
            signature: Firma HMAC-SHA256 en header X-Truora-Signature
            ip_address: IP de origen (para logging)

        Raises:
            InvalidWebhookSignatureError: Si la firma no es válida
        """
        # Validar firma HMAC-SHA256
        import json
        payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        expected_signature = hmac.new(
            settings.KYC_API_KEY.encode(),
            payload_json.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.warning(
                f"Invalid webhook signature from {ip_address} — "
                f"expected {expected_signature[:8]}... got {signature[:8]}..."
            )
            raise InvalidWebhookSignatureError("Firma inválida")

        # Extraer datos del webhook
        check_id = payload.get("check_id")
        status = payload.get("status")  # "approved" o "declined"
        document_number = payload.get("document_number")
        full_name = payload.get("full_name")

        if not check_id or not status:
            logger.error(f"Webhook payload missing required fields: {payload}")
            raise ValueError("Webhook payload inválido")

        # Buscar usuario por check_id
        stmt = select(UserORM).where(UserORM.kyc_provider_id == check_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"Webhook check_id not found in DB: {check_id}")
            return

        # Actualizar estado KYC
        if status == "approved":
            user.kyc_status = KYCStatusEnum.VERIFIED
            logger.info(f"KYC verified for user {user.id}")
        elif status == "declined":
            user.kyc_status = KYCStatusEnum.REJECTED
            logger.info(f"KYC rejected for user {user.id}")
        else:
            logger.warning(f"Unknown webhook status: {status}")
            return

        await db.flush()

    async def get_status(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> dict:
        """
        Obtiene el estado de KYC del usuario.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario

        Returns:
            Dict con status y detalles
        """
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"Usuario {user_id} no existe")

        return {
            "kyc_status": user.kyc_status.value,
            "can_retry": user.kyc_status == KYCStatusEnum.REJECTED,
        }
