"""
Nivo — Top-up Router (Wompi PSE/ACH)

Endpoints:
  POST /api/v1/topup/initiate   — Start PSE recharge
  POST /api/v1/topup/webhook    — Wompi callback (NO JWT)
  GET  /api/v1/topup/history    — User's top-up history
"""

from __future__ import annotations
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.payment_gateway_service import (
    PaymentGatewayService,
    PaymentGatewayError,
    PaymentGatewayUnavailableError,
    InvalidWebhookSignatureError,
)

router = APIRouter()
gateway_service = PaymentGatewayService()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class TopupInitiateRequest(BaseModel):
    """Solicitud para iniciar un top-up."""
    amount_cop: int  # En centavos
    bank_code: str   # Código del banco (ej: "001" para Bancolombia)

    @field_validator("amount_cop")
    @classmethod
    def validate_amount(cls, v: int) -> int:
        if v < 5_000_00:  # $5,000 COP
            raise ValueError("Monto mínimo: $5.000 COP")
        if v > 10_000_000_00:  # $10,000,000 COP máximo en MVP
            raise ValueError("Monto máximo: $10.000.000 COP")
        return v

    @field_validator("bank_code")
    @classmethod
    def validate_bank_code(cls, v: str) -> str:
        if not v or len(v) > 10:
            raise ValueError("Código de banco inválido")
        return v


class TopupInitiateResponse(BaseModel):
    """Respuesta de iniciación de top-up."""
    payment_link_url: str
    reference: str
    expires_in_minutes: int = 30  # PSE link válido por 30 minutos
    amount_cop: int
    amount_display: str


class TopupHistoryItem(BaseModel):
    """Un item en el historial de top-ups."""
    id: str
    amount_cop: int
    amount_display: str
    status: str  # "completed", "failed", "pending"
    settlement_status: str
    created_at: str


class TopupHistoryResponse(BaseModel):
    """Respuesta con historial de top-ups."""
    topups: list[TopupHistoryItem]
    total_count: int


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/initiate",
    response_model=TopupInitiateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar recarga (top-up)",
    description="Inicia un top-up PSE. Retorna URL de Wompi para que el usuario complete el pago.",
)
async def initiate_topup(
    request: TopupInitiateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TopupInitiateResponse:
    """
    Inicia un top-up de saldo a través de PSE.

    El usuario recibe una URL para completar el pago en Wompi.
    El proceso toma 5-10 minutos.

    Returns:
        payment_link_url: URL donde el usuario completa el pago
        amount_display: Formato legible del monto
    """
    try:
        result = await gateway_service.initiate_topup(
            db,
            current_user.id,
            request.amount_cop,
            request.bank_code,
        )

        return TopupInitiateResponse(
            payment_link_url=result["payment_link_url"],
            reference=result["reference"],
            amount_cop=request.amount_cop,
            amount_display=f"${request.amount_cop / 100:,.0f} COP",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PaymentGatewayUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except PaymentGatewayError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Webhook de Wompi",
    description="Endpoint para que Wompi reporte el resultado del pago. "
    "NO requiere JWT. Siempre retorna 200.",
    include_in_schema=False,  # No mostrar en OpenAPI (endpoint backend)
)
async def wompi_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Webhook de Wompi para reportar resultado de pago.

    Wompi envía:
    - Payload JSON en el body
    - Firma SHA-256 en el header X-Event-Checksum

    IMPORTANTE: Siempre retorna 200 para no alertar a atacantes.
    """
    # Extraer firma del header
    signature = request.headers.get("X-Event-Checksum", "")
    ip_address = request.client.host if request.client else "unknown"

    # Leer payload
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ok"}

    if not signature:
        signature = payload.get("signature", {}).get("checksum", "")

    # Procesar webhook
    try:
        await gateway_service.process_webhook(db, payload, signature, ip_address)
    except InvalidWebhookSignatureError:
        # Log pero no fallar
        pass
    except Exception:
        # Cualquier otro error, también silencioso
        pass

    return {"status": "ok"}


@router.get(
    "/history",
    response_model=TopupHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Historial de top-ups",
    description="Retorna historial de top-ups del usuario.",
)
async def get_topup_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 20,
) -> TopupHistoryResponse:
    """
    Obtiene el historial de top-ups del usuario.

    Returns:
        topups: Lista de top-ups ordenados por fecha descendente
        total_count: Número total de top-ups
    """
    try:
        topups = await gateway_service.get_topup_history(db, current_user.id, limit)

        return TopupHistoryResponse(
            topups=[TopupHistoryItem(**t) for t in topups],
            total_count=len(topups),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error consultando historial de top-ups",
        )
