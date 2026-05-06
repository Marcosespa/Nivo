"""
Nivo — Dev Seed Endpoint  ⚠️  SOLO DEVELOPMENT

Crea usuarios de prueba con saldo pre-cargado y retorna tokens JWT directos,
sin pasar por el flujo de OTP. Permite demos y pruebas en Postman sin depender
de Twilio ni de leer logs.

Endpoint:
  POST /api/v1/dev/seed   — Crea/resetea sender + receiver, siembra saldo

IMPORTANTE: este router SOLO se registra cuando ENVIRONMENT == "development".
En staging o producción nunca existe. No hay forma de bypassear auth con él.
"""

from __future__ import annotations
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.models.orm.user import User as UserORM
from app.models.orm.wallet import Wallet as WalletORM
from app.models.orm.pqc_key import PQCKey as PQCKeyORM
from app.models.orm.transaction import Transaction as TransactionORM
from app.services.auth_service import AuthService
from app.utils.validators import validate_colombian_phone

router = APIRouter()
_auth_service = AuthService()

# Saldo semilla por defecto: $500.000 COP (en centavos)
DEFAULT_SEED_BALANCE = 50_000_000


# ─── Schemas ──────────────────────────────────────────────────────────────────

class SeedRequest(BaseModel):
    sender_phone: str = "+573001234567"
    receiver_phone: str = "+573009876543"
    seed_balance_cop: int = DEFAULT_SEED_BALANCE  # centavos


class SeedUserInfo(BaseModel):
    user_id: str
    phone_number: str
    access_token: str
    refresh_token: str
    wallet_balance_cop: int
    wallet_balance_display: str
    pqc_key_fingerprint: str
    is_new: bool


class SeedResponse(BaseModel):
    message: str
    sender: SeedUserInfo
    receiver: SeedUserInfo
    tip: str


class SeedCleanupResponse(BaseModel):
    message: str


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _provision_user(
    db: AsyncSession,
    phone_number: str,
    balance_cop: int,
) -> SeedUserInfo:
    """Crea o recupera un usuario, siembra su saldo y devuelve tokens JWT."""

    # Normalizar teléfono
    try:
        phone_normalized = validate_colombian_phone(phone_number)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Crear o recuperar usuario
    user, is_new = await _auth_service.get_or_create_user(db, phone_normalized)

    # Asegurar que tenga llaves PQC
    stmt = select(PQCKeyORM).where(
        (PQCKeyORM.user_id == user.id) & (PQCKeyORM.is_active == True)
    )
    result = await db.execute(stmt)
    pqc_key = result.scalar_one_or_none()
    if pqc_key is None:
        pqc_key = await _auth_service.create_pqc_keys_for_user(db, user.id)

    # Asegurar que tenga billetera y sembrar saldo
    stmt = select(WalletORM).where(WalletORM.user_id == user.id)
    result = await db.execute(stmt)
    wallet = result.scalar_one_or_none()

    if wallet is None:
        wallet = WalletORM(user_id=user.id, display_balance_cop=balance_cop)
        db.add(wallet)
    else:
        wallet.display_balance_cop = balance_cop

    await db.flush()

    # Generar tokens JWT (sin OTP — solo dev)
    access_token = create_access_token(
        user_id=user.id,
        phone_number=user.phone_number,
        plan=user.plan.value,
    )
    refresh_token = create_refresh_token(
        user_id=user.id,
        phone_number=user.phone_number,
        plan=user.plan.value,
    )

    return SeedUserInfo(
        user_id=str(user.id),
        phone_number=user.phone_number,
        access_token=access_token,
        refresh_token=refresh_token,
        wallet_balance_cop=wallet.display_balance_cop,
        wallet_balance_display=f"${wallet.display_balance_cop / 100:,.0f} COP",
        pqc_key_fingerprint=pqc_key.key_fingerprint[:16],
        is_new=is_new,
    )


# ─── Endpoint ─────────────────────────────────────────────────────────────────

@router.post(
    "/seed",
    response_model=SeedResponse,
    status_code=status.HTTP_200_OK,
    summary="⚠️ Seed de datos de prueba (SOLO DEV)",
    description=(
        "Crea o resetea dos usuarios de prueba (sender y receiver) con saldo "
        "pre-cargado. Retorna tokens JWT listos para usar en Postman sin necesidad "
        "de OTP. **Solo disponible en ENVIRONMENT=development.**"
    ),
)
async def seed_test_data(
    body: SeedRequest,
    http_request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SeedResponse:
    """
    Siembra datos de prueba reproducibles para demos y testing manual en Postman.

    - Crea sender y receiver si no existen, o los recupera si ya existen.
    - Resetea el saldo del sender al valor indicado (default $500.000 COP).
    - El receiver siempre queda con saldo 0 (solo recibe).
    - Retorna access_token y refresh_token listos para usar.
    """
    _host = http_request.client.host if http_request.client else ""
    if _host not in {"127.0.0.1", "::1"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    sender_info = await _provision_user(db, body.sender_phone, body.seed_balance_cop)
    receiver_info = await _provision_user(db, body.receiver_phone, 0)

    await db.commit()

    return SeedResponse(
        message="✅ Usuarios de prueba listos",
        sender=sender_info,
        receiver=receiver_info,
        tip=(
            "Copia sender.access_token al header Authorization: Bearer <token> "
            "para ejecutar el flujo de pagos directamente."
        ),
    )


@router.delete(
    "/seed",
    response_model=SeedCleanupResponse,
    status_code=status.HTTP_200_OK,
    summary="⚠️ Limpiar datos de prueba (SOLO DEV)",
    description="Elimina los usuarios de prueba creados por /seed. Solo DEV.",
)
async def clear_seed_data(
    body: SeedRequest,
    http_request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SeedCleanupResponse:
    """Elimina los usuarios de prueba para un reset limpio."""
    _host = http_request.client.host if http_request.client else ""
    if _host not in {"127.0.0.1", "::1"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    user_ids: list[uuid.UUID] = []

    for phone in [body.sender_phone, body.receiver_phone]:
        try:
            phone_normalized = validate_colombian_phone(phone)
        except ValueError:
            continue

        stmt = select(UserORM).where(UserORM.phone_number == phone_normalized)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user_ids.append(user.id)

    if user_ids:
        await db.execute(
            delete(TransactionORM).where(
                or_(
                    TransactionORM.sender_id.in_(user_ids),
                    TransactionORM.receiver_id.in_(user_ids),
                )
            )
        )
        await db.execute(delete(PQCKeyORM).where(PQCKeyORM.user_id.in_(user_ids)))
        await db.execute(delete(WalletORM).where(WalletORM.user_id.in_(user_ids)))
        await db.execute(delete(UserORM).where(UserORM.id.in_(user_ids)))

    await db.commit()
    return SeedCleanupResponse(message="✅ Usuarios de prueba eliminados")
