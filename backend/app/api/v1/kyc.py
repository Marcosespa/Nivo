"""
Nivo — KYC Router (Truora integration)

Endpoints:
  POST /api/v1/kyc/initiate   — Start verification, get Truora URL
  POST /api/v1/kyc/webhook    — Truora callback (NO JWT)
  GET  /api/v1/kyc/status     — Current KYC status
"""

from __future__ import annotations
import uuid
from typing import Annotated

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm.user import User as UserORM
from app.models.user import User
from app.services.kyc_service import (
    KYCService,
    KYCError,
    KYCNotInitiatedError,
    InvalidWebhookSignatureError,
    KYCServiceUnavailableError,
)
from app.services.kyc_funnel_service import kyc_funnel_service, KYC_ALERT_THRESHOLD, KYC_ALERT_MIN_SAMPLE
from app.services.alert_service import AlertService, AlertEvent

router = APIRouter()
kyc_service = KYCService()


async def get_redis() -> redis.Redis:
    return await redis.from_url(settings.REDIS_URL)


# ─── Schemas ──────────────────────────────────────────────────────────────────

class KYCInitiateResponse(BaseModel):
    """Respuesta de iniciación de KYC."""
    check_id: str
    verification_url: str
    expires_in_minutes: int = 1440  # 24 horas


class KYCStatusResponse(BaseModel):
    """Respuesta de estado de KYC."""
    kyc_status: str  # "pending", "verified", "rejected"
    can_retry: bool


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/initiate",
    response_model=KYCInitiateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar verificación de identidad",
    description="Inicia un proceso KYC con Truora. Retorna URL para que el usuario complete la verificación.",
)
async def initiate_kyc(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> KYCInitiateResponse:
    """
    Inicia un proceso de verificación KYC.

    El usuario recibe una URL para completar la verificación en Truora.
    El proceso toma 2-4 minutos.

    Returns:
        verification_url: URL donde el usuario completará la verificación
    """
    try:
        result = await kyc_service.initiate_verification(db, current_user.id)
        return KYCInitiateResponse(
            check_id=result["check_id"],
            verification_url=result["verification_url"],
        )

    except KYCNotInitiatedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except KYCServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except KYCError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Webhook de Truora",
    description="Endpoint para que Truora reporte el resultado de la verificación. "
    "NO requiere JWT. Siempre retorna 200 (incluso si la firma falla).",
    include_in_schema=False,  # No mostrar en OpenAPI (endpoint backend)
)
async def truora_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> dict:
    """
    Webhook de Truora para reportar resultado de verificación.

    Truora envía:
    - Payload JSON en el body
    - Firma HMAC-SHA256 en header X-Truora-Signature

    IMPORTANTE: Siempre retorna 200 para no alertar a atacantes.
    Las validaciones fallidas se loguean pero no se propagan al cliente.
    """
    # Extraer firma del header
    signature = request.headers.get("X-Truora-Signature", "")
    ip_address = request.client.host if request.client else "unknown"

    # Leer payload
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ok"}

    # Procesar webhook
    kyc_result_processed = False
    try:
        await kyc_service.process_webhook(db, payload, signature, ip_address)
        kyc_result_processed = payload.get("status") in {"approved", "declined"}
    except InvalidWebhookSignatureError:
        pass
    except Exception:
        pass

    # Chequear tasa de aprobación KYC y alertar si cae < 70%
    if kyc_result_processed:
        try:
            rate, sample = await kyc_funnel_service.get_kyc_approval_rate_24h(db)
            if rate is not None and sample >= KYC_ALERT_MIN_SAMPLE and rate < KYC_ALERT_THRESHOLD:
                await AlertService(redis_client).send_rate_alert(
                    AlertEvent.KYC_LOW_APPROVAL_RATE,
                    {"tasa_24h": f"{rate:.1%}", "muestra": str(sample)},
                )
        except Exception:
            pass

    return {"status": "ok"}


@router.get(
    "/funnel",
    status_code=status.HTTP_200_OK,
    summary="Funnel de conversión KYC",
    description=(
        "Retorna tasas de conversión por etapa para los últimos N días. "
        "Datos de negocio agregados — sin PII. Requiere JWT."
    ),
)
async def get_kyc_funnel(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    days: int = 1,
) -> dict:
    """
    Funnel de conversión KYC:
      REGISTERED → KYC_INITIATED → KYC_RESULT → FIRST_DEPOSIT

    Parámetros:
      days: ventana de tiempo en días (default 1 = últimas 24h)
    """
    if days < 1 or days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="days debe estar entre 1 y 90",
        )
    return await kyc_funnel_service.get_funnel_stats(db, days=days)


@router.get(
    "/status",
    response_model=KYCStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estado de KYC",
    description="Retorna el estado actual de verificación KYC del usuario.",
)
async def get_kyc_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> KYCStatusResponse:
    """
    Obtiene el estado de KYC del usuario autenticado.

    Returns:
        kyc_status: "pending", "verified", o "rejected"
        can_retry: Si el usuario puede reintentar (true si fue rechazado)
    """
    try:
        result = await kyc_service.get_status(db, current_user.id)
        return KYCStatusResponse(
            kyc_status=result["kyc_status"],
            can_retry=result["can_retry"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error consultando estado de KYC",
        )
