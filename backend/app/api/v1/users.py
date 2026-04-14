"""Nivo — Router de Usuarios."""

from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


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
async def get_profile(current_user: Annotated[User, Depends(get_current_user)]):
    """Retorna el perfil del usuario autenticado."""
    return UserProfileResponse(
        id=current_user.id,
        phone_number=current_user.phone_number,
        plan=current_user.plan.value,
        kyc_status=current_user.kyc_status.value,
        pqc_key_fingerprint=current_user.pqc_key_fingerprint,
    )


@router.get("/me/wallet", response_model=WalletResponse)
async def get_wallet(current_user: Annotated[User, Depends(get_current_user)]):
    """Retorna el saldo visual y estado de la billetera del usuario."""
    # TODO: consultar saldo visual desde el aliado regulado configurado.
    # En modo MVP, Nivo no es el ledger legal de fondos del usuario.
    return WalletResponse(
        balance_cop=0,
        balance_display="$0 COP",
        is_frozen=False,
        custody_mode=settings.MONEY_CUSTODY_MODE,
    )
