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
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator

from app.core.config import settings
from app.core.security import get_current_user
from app.crypto.service import CryptoService
from app.models.user import User
from app.models.transaction import TransactionStatus

router = APIRouter()
crypto = CryptoService()


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
    quantum_shield: bool = True
    receipt_url: str       # URL del comprobante PDF firmado


class TransactionDetail(BaseModel):
    tx_id: str
    status: TransactionStatus
    amount_cop: int
    amount_display: str
    sender_phone: str
    receiver_phone: str
    message: str | None
    created_at: datetime
    confirmed_at: datetime | None
    ml_dsa_signature_fingerprint: str
    quantum_shield: bool = True
    pqc_algorithm: str


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
    # TODO: consultar disponibilidad/fondos en PSE/ACH/banco aliado
    # TODO: implementar lookup de receptor por teléfono
    # TODO: implementar verificación de límites diarios
    # TODO: implementar envío de OTP (Twilio)

    tx_id = str(uuid.uuid4())

    return PaymentInitiateResponse(
        tx_id=tx_id,
        status="pending_confirmation",
        receiver_phone=request.receiver_phone,
        amount_cop=request.amount_cop,
        amount_display=f"${request.amount_cop / 100:,.0f} COP",
        quantum_shield=True,
        pqc_algorithm=settings.PQC_ALGORITHM,
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
    # TODO: verificar OTP contra Redis
    # TODO: recuperar transacción pendiente de Redis
    # TODO: ejecutar instrucción con el aliado regulado y conciliar resultado
    # TODO: enviar push notification al receptor

    # Construcción del payload de firma (incluye todos los datos de la tx)
    now = datetime.now(timezone.utc)
    tx_payload = (
        f"tx:{request.tx_id}|"
        f"sender:{current_user.id}|"
        f"ts:{now.isoformat()}"
    ).encode()

    # Firma ML-DSA-65 (en producción: recuperar signing_key del usuario desde HSM)
    signing_kp = crypto.generate_signing_keypair()  # TODO: usar llave persistida del usuario
    signed_tx = crypto.sign_transaction(
        tx_id=request.tx_id,
        payload=tx_payload,
        signing_secret_key=signing_kp.secret_key,
        public_key_fingerprint=signing_kp.public_key_fingerprint,
    )

    return PaymentConfirmResponse(
        tx_id=request.tx_id,
        status="completed",
        amount_cop=0,      # TODO: recuperar de BD
        amount_display="$0 COP",
        receiver_phone="",  # TODO: recuperar de BD
        completed_at=now,
        ml_dsa_signature_fingerprint=signed_tx.public_key_fingerprint[:16],
        receipt_url=f"https://api.Nivo.co/receipts/{request.tx_id}.pdf",
    )


@router.get(
    "/{tx_id}",
    response_model=TransactionDetail,
    summary="Consultar transacción",
)
async def get_transaction(
    tx_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> TransactionDetail:
    """Consulta el estado y detalles de una transacción específica."""
    # TODO: implementar consulta real a BD
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Transacción {tx_id} no encontrada",
    )


@router.get(
    "/",
    summary="Historial de movimientos",
)
async def get_payment_history(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = 1,
    page_size: int = 20,
    direction: str = "all",   # "sent", "received", "all"
):
    """
    Retorna el historial paginado de transacciones del usuario.
    Cada movimiento incluye el fingerprint de firma ML-DSA-65.
    """
    # TODO: implementar consulta paginada a BD
    return {
        "transactions": [],
        "page": page,
        "page_size": page_size,
        "total": 0,
    }
