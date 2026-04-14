"""
Nivo — Withdrawal Router (ACH bank transfers)

Endpoints:
  POST /api/v1/withdrawal/accounts              — Register bank account
  GET  /api/v1/withdrawal/accounts              — List user's accounts
  POST /api/v1/withdrawal/accounts/{id}/verify  — Verify micro-deposit
  POST /api/v1/withdrawal/initiate              — Initiate withdrawal
  GET  /api/v1/withdrawal/history               — Withdrawal history
"""

from __future__ import annotations
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.withdrawal_service import (
    WithdrawalService,
    WithdrawalError,
    BankAccountNotFoundError,
    BankAccountNotVerifiedError,
    InsufficientFundsError,
    DailyLimitExceededError,
)

router = APIRouter()
withdrawal_service = WithdrawalService()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class RegisterBankAccountRequest(BaseModel):
    """Solicitud para registrar una cuenta bancaria."""
    bank_code: str
    account_type: str  # "savings" or "checking"
    account_number: str
    account_holder_name: str


class RegisterBankAccountResponse(BaseModel):
    """Respuesta de registro de cuenta bancaria."""
    bank_account_id: str
    verification_amount_cop: int
    verification_amount_display: str
    message: str


class BankAccountDetail(BaseModel):
    """Detalle de una cuenta bancaria."""
    id: str
    bank_code: str
    account_type: str
    account_number_last4: str
    account_holder_name: str
    is_verified: bool
    created_at: str


class ListBankAccountsResponse(BaseModel):
    """Respuesta con lista de cuentas bancarias."""
    accounts: list[BankAccountDetail]
    total_count: int


class VerifyBankAccountRequest(BaseModel):
    """Solicitud para verificar una cuenta bancaria."""
    verification_amount_cop: int


class VerifyBankAccountResponse(BaseModel):
    """Respuesta de verificación."""
    status: str
    message: str


class InitiateWithdrawalRequest(BaseModel):
    """Solicitud para iniciar un retiro."""
    bank_account_id: str
    amount_cop: int

    @field_validator("amount_cop")
    @classmethod
    def validate_amount(cls, v: int) -> int:
        if v < settings.TX_MIN_AMOUNT:
            raise ValueError(f"Monto mínimo: ${settings.TX_MIN_AMOUNT / 100:,.0f} COP")
        return v


class InitiateWithdrawalResponse(BaseModel):
    """Respuesta de iniciación de retiro."""
    transaction_id: str
    amount_cop: int
    amount_display: str
    commission_cop: int
    commission_display: str
    total_debit: int
    total_debit_display: str
    status: str
    processing_time: str


class WithdrawalHistoryItem(BaseModel):
    """Un item en el historial de retiros."""
    id: str
    amount_cop: int
    amount_display: str
    status: str
    settlement_status: str
    created_at: str


class WithdrawalHistoryResponse(BaseModel):
    """Respuesta con historial de retiros."""
    withdrawals: list[WithdrawalHistoryItem]
    total_count: int


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/accounts",
    response_model=RegisterBankAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar cuenta bancaria",
    description="Registra una nueva cuenta bancaria para retiros. Se genera un micro-depósito para verificación.",
)
async def register_bank_account(
    request: RegisterBankAccountRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RegisterBankAccountResponse:
    """
    Registra una nueva cuenta bancaria para retiros.

    El número de cuenta se cifra con AES-256-GCM.
    Se genera un micro-depósito de 501-999 COP para verificación.

    Returns:
        bank_account_id: UUID de la cuenta registrada
        verification_amount_cop: Monto del micro-depósito
    """
    try:
        result = await withdrawal_service.register_bank_account(
            db,
            current_user.id,
            request.bank_code,
            request.account_type,
            request.account_number,
            request.account_holder_name,
        )

        return RegisterBankAccountResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except WithdrawalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/accounts",
    response_model=ListBankAccountsResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar cuentas bancarias",
    description="Retorna las cuentas bancarias del usuario (SIN números de cuenta completos).",
)
async def list_bank_accounts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ListBankAccountsResponse:
    """
    Lista las cuentas bancarias del usuario.

    Por seguridad, no se retornan números de cuenta completos.
    """
    try:
        accounts = await withdrawal_service.list_bank_accounts(db, current_user.id)

        return ListBankAccountsResponse(
            accounts=[BankAccountDetail(**a) for a in accounts],
            total_count=len(accounts),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error consultando cuentas bancarias",
        )


@router.post(
    "/accounts/{account_id}/verify",
    response_model=VerifyBankAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar micro-depósito",
    description="Confirma el monto del micro-depósito para verificar la cuenta bancaria.",
)
async def verify_bank_account(
    account_id: str = Path(..., description="UUID de la cuenta bancaria"),
    request: VerifyBankAccountRequest = ...,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> VerifyBankAccountResponse:
    """
    Verifica una cuenta bancaria confirmando el monto del micro-depósito.

    El usuario recibe un micro-depósito de 501-999 COP y debe confirmar
    el monto exacto.
    """
    try:
        result = await withdrawal_service.verify_bank_account(
            db,
            current_user.id,
            uuid.UUID(account_id),
            request.verification_amount_cop,
        )

        return VerifyBankAccountResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UUID de cuenta inválido",
        )
    except BankAccountNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except WithdrawalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/initiate",
    response_model=InitiateWithdrawalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar retiro",
    description="Inicia un retiro a una cuenta bancaria verificada.",
)
async def initiate_withdrawal(
    request: InitiateWithdrawalRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> InitiateWithdrawalResponse:
    """
    Inicia un retiro a una cuenta bancaria verificada.

    El retiro se procesa de manera asincrónica y tarda 1-2 días hábiles.

    Returns:
        transaction_id: ID de la transacción
        amount_display: Monto formateado
        commission_display: Comisión (0 para PLUS/PRO, $2.000 para FREE)
    """
    try:
        result = await withdrawal_service.initiate_withdrawal(
            db,
            current_user.id,
            uuid.UUID(request.bank_account_id),
            request.amount_cop,
        )

        return InitiateWithdrawalResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except BankAccountNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except BankAccountNotVerifiedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DailyLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )
    except WithdrawalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/history",
    response_model=WithdrawalHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Historial de retiros",
    description="Retorna historial de retiros del usuario.",
)
async def get_withdrawal_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 20,
) -> WithdrawalHistoryResponse:
    """
    Obtiene el historial de retiros del usuario.

    Returns:
        withdrawals: Lista de retiros ordenados por fecha descendente
        total_count: Número total de retiros
    """
    try:
        withdrawals = await withdrawal_service.get_withdrawal_history(
            db, current_user.id, limit
        )

        return WithdrawalHistoryResponse(
            withdrawals=[WithdrawalHistoryItem(**w) for w in withdrawals],
            total_count=len(withdrawals),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error consultando historial de retiros",
        )
