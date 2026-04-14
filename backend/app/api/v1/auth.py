"""
Nivo — Router de Autenticación

Flujo de onboarding:
  1. Usuario ingresa número de celular
  2. Se envía OTP por SMS (Twilio)
  3. Usuario confirma OTP → se crea cuenta + llaves PQC
  4. Se retorna JWT (access + refresh tokens)

Endpoints:
  POST /api/v1/auth/register     — Registrar nuevo usuario con OTP
  POST /api/v1/auth/login        — Login con OTP (passwordless)
  POST /api/v1/auth/verify-otp   — Verificar código OTP
  POST /api/v1/auth/refresh       — Renovar access token
  POST /api/v1/auth/logout        — Invalidar tokens
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.crypto.service import CryptoService

router = APIRouter()
crypto = CryptoService()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    phone_number: str   # +57 310 xxx xxxx
    device_id: str      # ID único del dispositivo móvil


class OTPRequest(BaseModel):
    phone_number: str


class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str
    device_id: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int        # segundos
    user_id: str
    is_new_user: bool
    pqc_key_fingerprint: str   # Fingerprint de las llaves PQC generadas


class RefreshRequest(BaseModel):
    refresh_token: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/request-otp",
    status_code=status.HTTP_200_OK,
    summary="Solicitar OTP por SMS",
    description="Envía un código OTP de 6 dígitos al número de celular. Válido por 5 minutos.",
)
async def request_otp(request: OTPRequest):
    """
    Flujo:
    1. Validar formato de número colombiano
    2. Generar OTP de 6 dígitos
    3. Almacenar en Redis con TTL de 5 minutos
    4. Enviar por SMS (Twilio)
    """
    # TODO: validar número colombiano
    # TODO: generar OTP y almacenar en Redis
    # TODO: enviar SMS por Twilio

    return {
        "message": "OTP enviado al número registrado",
        "expires_in_seconds": settings.REDIS_OTP_TTL,
        "phone_number": request.phone_number[:7] + "****",  # Enmascarar
    }


@router.post(
    "/verify-otp",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar OTP y autenticar",
    description=(
        "Verifica el OTP y retorna tokens JWT. Si el usuario es nuevo, "
        "genera automáticamente su par de llaves PQC (ML-KEM-768 + ML-DSA-65) "
        "y las almacena de forma segura."
    ),
)
async def verify_otp(request: OTPVerifyRequest) -> AuthResponse:
    """
    Flujo completo de autenticación:
    1. Verificar OTP contra Redis
    2. Si usuario nuevo: crear cuenta + generar llaves PQC
    3. Si usuario existente: verificar device_id
    4. Emitir JWT (access + refresh tokens)
    5. Retornar fingerprint de llaves PQC al cliente
    """
    # TODO: verificar OTP real contra Redis
    # TODO: crear/recuperar usuario de BD

    # Generar llaves PQC para nuevo usuario
    signing_kp = crypto.generate_signing_keypair()
    kem_kp = crypto.generate_kem_keypair()

    # TODO: almacenar llaves en BD + HSM (solo llave pública en BD, privada en HSM)
    # TODO: generar JWT real con jose o python-jose

    user_id = str(uuid.uuid4())
    is_new = True  # TODO: detectar si es usuario existente

    return AuthResponse(
        access_token="mock_access_token",   # TODO: JWT real
        refresh_token="mock_refresh_token", # TODO: JWT real
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user_id,
        is_new_user=is_new,
        pqc_key_fingerprint=signing_kp.public_key_fingerprint[:16],
    )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Renovar access token",
)
async def refresh_token(request: RefreshRequest) -> AuthResponse:
    """Renueva el access token usando el refresh token."""
    # TODO: verificar refresh token, emitir nuevo access token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented",
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión",
)
async def logout():
    """
    Invalida los tokens del usuario.
    El refresh token se agrega a una blacklist en Redis.
    """
    # TODO: agregar refresh token a blacklist en Redis
    return None
