"""
Nivo — Router de Pagos P2P

Endpoints:
  POST /api/v1/payments/initiate    — Iniciar pago P2P
  POST /api/v1/payments/confirm     — Confirmar pago
  GET  /api/v1/payments/{tx_id}     — Consultar estado de transacción
  GET  /api/v1/payments/history     — Historial de movimientos

Cada transacción se firma con ML-DSA-65 antes de persistirse.
Latencia objetivo: < 800ms end-to-end.

MVP regulatorio: por defecto opera sin captación directa. Nivo
orquesta, firma y concilia; PSE/ACH/banco aliado mueve y custodia fondos.
"""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
import redis.asyncio as redis

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm.user import User
from app.models.orm.transaction import (
    Transaction as TransactionORM,
    TransactionStatusEnum,
    SettlementStatusEnum,
    SettlementRailEnum,
)
from app.services.otp_service import OTPService
from app.services.payment_service import (
    PaymentService,
    ReceiverNotFoundError,
    WalletFrozenError,
    DailyLimitExceededError,
    InsufficientFundsError,
    CustodyModeNotExecutableError,
)

router = APIRouter()
payment_svc = PaymentService()


# ─── Dependencia: Redis ────────────────────────────────────────────────────────

async def get_redis() -> redis.Redis:
    """Obtiene cliente Redis."""
    return await redis.from_url(settings.REDIS_URL)


# ─── Schemas de request/response ─────────────────────────────────────────────

class PaymentInitiateRequest(BaseModel):
    """Solicitud para iniciar un pago P2P."""
    receiver_phone: str       # +57 310 xxx xxxx
    amount_cop: int           # En centavos (ej: 50000_00 = $500,000 COP)
    message: str | None = None

    @field_validator("amount_cop")
    @classmethod
    def validate_amount(cls, v: int) -> int:
        if v < settings.TX_MIN_AMOUNT:
            raise ValueError(f"Monto mínimo: ${settings.TX_MIN_AMOUNT / 100:,.0f} COP")
        return v

    @field_validator("receiver_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Normalizar formato colombiano
        clean = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not clean.startswith("+57"):
            clean = f"+57{clean.lstrip('0')}"
        if len(clean) != 13:
            raise ValueError("Número de celular inválido. Formato: +57 3XX XXX XXXX")
        return clean


class PaymentInitiateResponse(BaseModel):
    """Respuesta inicial: la transacción está pendiente de confirmación."""
    tx_id: str
    status: str           # "pending_confirmation"
    receiver_phone: str
    amount_cop: int
    amount_display: str   # "$500.000 COP"
    quantum_shield: bool  # Siempre True en Nivo
    pqc_algorithm: str
    expires_in_seconds: int = 300   # 5 minutos para confirmar


class PaymentConfirmRequest(BaseModel):
    tx_id: str
    otp_code: str         # OTP enviado por SMS


class PaymentConfirmResponse(BaseModel):
    tx_id: str
    status: str           # "completed"
    amount_cop: int
    amount_display: str
    receiver_phone: str
    completed_at: datetime
    ml_dsa_signature_fingerprint: str   # Fingerprint de la firma cuántica
    provider_reference: str | None = None
    settlement_status: str
    quantum_shield: bool = True
    receipt_url: str       # URL del comprobante PDF firmado


class TransactionDetail(BaseModel):
    tx_id: str
    status: TransactionStatusEnum
    amount_cop: int
    amount_display: str
    sender_phone: str
    receiver_phone: str
    message: str | None
    created_at: datetime
    confirmed_at: datetime | None
    ml_dsa_signature_fingerprint: str
    provider_reference: str | None = None
    settlement_status: str
    quantum_shield: bool = True
    pqc_algorithm: str


class PaymentHistoryItem(BaseModel):
    tx_id: str
    status: TransactionStatusEnum
    amount_cop: int
    amount_display: str
    direction: str
    created_at: datetime
    confirmed_at: datetime | None
    ml_dsa_signature_fingerprint: str
    provider_reference: str | None = None
    settlement_status: str
    rail: str


class PaymentHistoryResponse(BaseModel):
    transactions: list[PaymentHistoryItem]
    page: int
    page_size: int
    total: int


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Iniciar pago P2P",
    description=(
        "Inicia una transferencia P2P. La transacción queda en estado 'pending_confirmation' "
        "hasta que el usuario confirme con el OTP enviado por SMS. "
        "El canal está cifrado con ML-KEM-768 + X25519 (híbrido). "
        "En MVP, el dinero se mueve por el aliado configurado; Nivo no custodia saldo."
    ),
)
async def initiate_payment(
    request: PaymentInitiateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> PaymentInitiateResponse:
    """
    Flujo de pago:
    1. Validar KYC, límites y disponibilidad contra el aliado regulado
    2. Verificar que el receptor existe (buscar por teléfono)
    3. Verificar límites diarios del usuario
    4. Crear transacción pendiente
    5. Enviar OTP por SMS para confirmación
    6. Retornar tx_id y detalles para confirmar
    """
    try:
        result = await payment_svc.initiate_payment(
            db=db,
            redis_client=redis_client,
            sender_id=current_user.id,
            receiver_phone=request.receiver_phone,
            amount_cop=request.amount_cop,
            message=request.message,
        )
        otp_code = await OTPService(redis_client).generate_and_store(
            current_user.phone_number,
            "payment",
        )
        sms_sent = await payment_svc.sms_service.send_otp(current_user.phone_number, otp_code)
        if not sms_sent:
            raise HTTPException(status_code=503, detail="No pudimos enviar el OTP de confirmación")
    except ReceiverNotFoundError:
        raise HTTPException(status_code=404, detail="Receptor no encontrado en Nivo")
    except WalletFrozenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (DailyLimitExceededError, InsufficientFundsError, CustodyModeNotExecutableError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    return PaymentInitiateResponse(
        tx_id=result["tx_id"],
        status=result["status"],
        receiver_phone=result["receiver_phone"],
        amount_cop=result["amount_cop"],
        amount_display=result["amount_display"],
        quantum_shield=True,
        pqc_algorithm=settings.PQC_ALGORITHM,
        expires_in_seconds=result["expires_in_seconds"],
    )


@router.post(
    "/confirm",
    response_model=PaymentConfirmResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirmar pago con OTP",
    description=(
        "Confirma y ejecuta la transacción pendiente. "
        "Cada pago es firmado con ML-DSA-65 antes de persistirse — "
        "la firma es verificable a perpetuidad."
    ),
)
async def confirm_payment(
    request: PaymentConfirmRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> PaymentConfirmResponse:
    """
    Flujo de confirmación:
    1. Verificar OTP
    2. Verificar que tx_id existe y pertenece al usuario
    3. Construir payload de transacción para firma
    4. Firmar payload con ML-DSA-65
    5. Enviar instrucción firmada al rail configurado (PSE/ACH/banco aliado)
    6. Conciliar provider_reference y settlement_status
    7. Persistir transacción con firma y referencia del proveedor
    8. Enviar notificación push al receptor
    9. Retornar comprobante con fingerprint de firma
    """
    is_valid = await OTPService(redis_client).verify(
        current_user.phone_number,
        request.otp_code,
        "payment",
    )
    if not is_valid:
        raise HTTPException(status_code=401, detail="Código OTP inválido o expirado")

    try:
        transaction = await payment_svc.execute_payment(
            db=db,
            redis_client=redis_client,
            tx_id=request.tx_id,
            sender_id=current_user.id,
            otp_code=request.otp_code,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (DailyLimitExceededError, InsufficientFundsError, CustodyModeNotExecutableError, WalletFrozenError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    return PaymentConfirmResponse(
        tx_id=str(transaction.id),
        status=transaction.status.value,
        amount_cop=transaction.amount_cop,
        amount_display=f"${transaction.amount_cop / 100:,.0f} COP",
        receiver_phone=transaction.receiver.phone_number,
        completed_at=transaction.confirmed_at or transaction.created_at,
        ml_dsa_signature_fingerprint=transaction.ml_dsa_signature.hex()[:16] if transaction.ml_dsa_signature else "none",
        provider_reference=transaction.provider_reference,
        settlement_status=transaction.settlement_status.value,
        receipt_url=f"https://api.nivo.co/receipts/{transaction.id}.pdf",
    )


@router.get(
    "/history",
    response_model=PaymentHistoryResponse,
    summary="Historial de movimientos",
)
async def get_payment_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 20,
    direction: str = "all",   # "sent", "received", "all"
):
    """
    Retorna el historial paginado de transacciones del usuario.
    Cada movimiento incluye el fingerprint de firma ML-DSA-65.
    """
    stmt = select(TransactionORM).order_by(TransactionORM.created_at.desc())
    if direction == "sent":
        stmt = stmt.where(TransactionORM.sender_id == current_user.id)
    elif direction == "received":
        stmt = stmt.where(TransactionORM.receiver_id == current_user.id)
    else:
        stmt = stmt.where(
            or_(
                TransactionORM.sender_id == current_user.id,
                TransactionORM.receiver_id == current_user.id,
            )
        )
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    transactions = result.scalars().all()

    return PaymentHistoryResponse(
        transactions=[
            PaymentHistoryItem(
                tx_id=str(tx.id),
                status=tx.status,
                amount_cop=tx.amount_cop,
                amount_display=f"${tx.amount_cop / 100:,.0f} COP",
                direction="sent" if tx.sender_id == current_user.id else "received",
                created_at=tx.created_at,
                confirmed_at=tx.confirmed_at,
                ml_dsa_signature_fingerprint=tx.ml_dsa_signature.hex()[:16] if tx.ml_dsa_signature else "none",
                provider_reference=tx.provider_reference,
                settlement_status=tx.settlement_status.value,
                rail=tx.rail.value,
            )
            for tx in transactions
        ],
        page=page,
        page_size=page_size,
        total=len(transactions),
    )


@router.get(
    "/{tx_id}",
    response_model=TransactionDetail,
    summary="Consultar transacción",
)
async def get_transaction(
    tx_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionDetail:
    """Consulta el estado y detalles de una transacción específica."""
    try:
        tx_uuid = uuid.UUID(tx_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de transacción inválido")

    stmt = select(TransactionORM).where(
        (TransactionORM.id == tx_uuid)
        & or_(
            TransactionORM.sender_id == current_user.id,
            TransactionORM.receiver_id == current_user.id,
        )
    ).options(
        selectinload(TransactionORM.sender),
        selectinload(TransactionORM.receiver),
    )
    result = await db.execute(stmt)
    tx = result.scalar_one_or_none()

    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    return TransactionDetail(
        tx_id=str(tx.id),
        status=tx.status,
        amount_cop=tx.amount_cop,
        amount_display=f"${tx.amount_cop / 100:,.0f} COP",
        sender_phone=tx.sender.phone_number,
        receiver_phone=tx.receiver.phone_number,
        message=tx.message,
        created_at=tx.created_at,
        confirmed_at=tx.confirmed_at,
        ml_dsa_signature_fingerprint=tx.ml_dsa_signature.hex()[:16] if tx.ml_dsa_signature else "none",
        provider_reference=tx.provider_reference,
        settlement_status=tx.settlement_status.value,
        pqc_algorithm=settings.PQC_ALGORITHM,
    )
