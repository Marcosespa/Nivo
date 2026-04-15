"""Nivo — Router de Usuarios."""

from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm.user import User as UserORM
from app.models.orm.pqc_key import PQCKey as PQCKeyORM
from app.services.wallet_service import WalletService

router = APIRouter()
wallet_service = WalletService()


class UserProfileResponse(BaseModel):
    id: str
    phone_number: str
    plan: str
    kyc_status: str
    pqc_key_fingerprint: str | None


class WalletResponse(BaseModel):
    balance_cop: int
    balance_display: str
    currency: str = "COP"
    is_frozen: bool
    custody_mode: str
    is_legal_balance: bool = False
    provider_account_ref: str | None = None


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(
    current_user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retorna el perfil del usuario autenticado."""
    pqc_stmt = (
        select(PQCKeyORM)
        .where((PQCKeyORM.user_id == current_user.id) & (PQCKeyORM.is_active == True))
        .order_by(PQCKeyORM.created_at.desc())
    )
    pqc_result = await db.execute(pqc_stmt)
    active_key = pqc_result.scalar_one_or_none()

    return UserProfileResponse(
        id=str(current_user.id),
        phone_number=current_user.phone_number,
        plan=current_user.plan.value,
        kyc_status=current_user.kyc_status.value,
        pqc_key_fingerprint=active_key.key_fingerprint[:16] if active_key else None,
    )


@router.get("/me/wallet", response_model=WalletResponse)
async def get_wallet(
    current_user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retorna el saldo visual y estado de la billetera del usuario."""
    wallet = await wallet_service.get_or_create_wallet(db, current_user.id)
    return WalletResponse(
        balance_cop=wallet.display_balance_cop,
        balance_display=f"${wallet.display_balance_cop / 100:,.0f} COP",
        currency=wallet.currency,
        is_frozen=wallet.is_frozen,
        custody_mode=wallet.custody_mode.value,
        provider_account_ref=wallet.provider_account_ref,
    )
