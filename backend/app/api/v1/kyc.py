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

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

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

router = APIRouter()
kyc_service = KYCService()


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
    try:
        await kyc_service.process_webhook(db, payload, signature, ip_address)
    except InvalidWebhookSignatureError:
        # Log pero no fallar (siempre retornar 200)
        pass
    except Exception:
        # Cualquier otro error, también silencioso
        pass

    return {"status": "ok"}


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
