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

"""
Nivo — Router de Autenticación

Flujo de onboarding:
  1. Usuario ingresa número de celular
  2. Se envía OTP por SMS (Twilio)
  3. Usuario confirma OTP → se crea cuenta + llaves PQC
  4. Se retorna JWT (access + refresh tokens)

Endpoints:
  POST /api/v1/auth/request-otp    — Solicitar OTP por SMS
  POST /api/v1/auth/verify-otp     — Verificar código OTP y autenticar
  POST /api/v1/auth/refresh        — Renovar access token
  POST /api/v1/auth/logout         — Invalidar tokens
"""

from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.services.otp_service import OTPService
from app.services.auth_service import AuthService
from app.utils.validators import validate_colombian_phone

router = APIRouter()
auth_service = AuthService()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class OTPRequest(BaseModel):
    phone_number: str   # +57 310 xxx xxxx


class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str
    device_id: str      # ID del dispositivo


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int        # segundos (TTL del access token)
    user_id: str
    is_new_user: bool
    pqc_key_fingerprint: str   # Fingerprint de llave PQC


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ─── Dependencia: Redis ────────────────────────────────────────────────────────

async def get_redis() -> redis.Redis:
    """Obtiene cliente Redis."""
    return await redis.from_url(settings.REDIS_URL)


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/request-otp",
    status_code=status.HTTP_200_OK,
    summary="Solicitar OTP por SMS",
    description="Envía un código OTP de 6 dígitos al número de celular. Válido por 5 minutos.",
)
async def request_otp(
    request: OTPRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
):
    """
    Solicita un OTP por SMS.

    Flujo:
    1. Validar formato de número colombiano
    2. Generar OTP de 6 dígitos
    3. Almacenar hash en Redis con TTL de 5 minutos
    4. Enviar por SMS (integración Twilio)
    """
    # Validar formato
    try:
        phone_normalized = validate_colombian_phone(request.phone_number)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Crear servicio OTP
    otp_service = OTPService(redis_client)

    # Generar OTP
    try:
        otp_code = await otp_service.generate_and_store(phone_normalized, "login")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )

    # TODO: Integrar Twilio para enviar SMS
    # sms_service = SMSService()
    # await sms_service.send_otp(phone_normalized, otp_code)

    # En desarrollo, loggear OTP (NUNCA en producción)
    if settings.ENVIRONMENT == "development":
        import logging
        logging.getLogger(__name__).info(
            f"[DEV] OTP para {phone_normalized[:7]}****: {otp_code}"
        )

    return {
        "message": "OTP enviado al número registrado",
        "expires_in_seconds": settings.REDIS_OTP_TTL,
        "phone_number": phone_normalized[:7] + "****",  # Enmascarar
    }


@router.post(
    "/verify-otp",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar OTP y autenticar",
    description=(
        "Verifica el OTP y retorna tokens JWT. Si el usuario es nuevo, "
        "genera automáticamente su par de llaves PQC (ML-DSA-65) "
        "y crea su billetera."
    ),
)
async def verify_otp(
    request: OTPVerifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> AuthResponse:
    """
    Flujo completo de autenticación:
    1. Validar formato de número
    2. Verificar OTP contra Redis
    3. get_or_create_user en BD
    4. Si usuario nuevo: generar llaves PQC
    5. Emitir JWT (access + refresh tokens)
    6. Retornar respuesta
    """
    # Validar formato
    try:
        phone_normalized = validate_colombian_phone(request.phone_number)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Verificar OTP
    otp_service = OTPService(redis_client)
    try:
        is_valid = await otp_service.verify(phone_normalized, request.otp_code, "login")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código OTP inválido o expirado",
        )

    # Obtener o crear usuario
    user, is_new = await auth_service.get_or_create_user(db, phone_normalized)
    await db.commit()

    # Si es nuevo usuario: crear llaves PQC
    pqc_key = None
    if is_new:
        pqc_key = await auth_service.create_pqc_keys_for_user(db, user.id)
        await db.commit()
    else:
        # Si es usuario existente, recuperar llave activa
        from sqlalchemy import select
        from app.models.orm.pqc_key import PQCKey as PQCKeyORM

        stmt = select(PQCKeyORM).where(
            (PQCKeyORM.user_id == user.id) & (PQCKeyORM.is_active == True)
        )
        result = await db.execute(stmt)
        pqc_key = result.scalar_one()

    # Generar tokens JWT
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

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        is_new_user=is_new,
        pqc_key_fingerprint=pqc_key.key_fingerprint[:16],
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar access token",
    description="Renueva el access token usando un refresh token válido.",
)
async def refresh_token(
    request: RefreshRequest,
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> RefreshResponse:
    """
    Renueva el access token.

    Flujo:
    1. Decodificar refresh token
    2. Verificar que type="refresh"
    3. Verificar que no está en blacklist
    4. Emitir nuevo access token
    5. Invalidar refresh token anterior
    """
    # Decodificar token
    payload = await decode_token(request.refresh_token)

    # Verificar tipo
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no es un refresh token válido",
        )

    # Verificar no está en blacklist
    jti = payload.get("jti")
    if await auth_service.is_token_blacklisted(redis_client, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token ha sido invalidado",
        )

    # Extraer datos del payload
    user_id = uuid.UUID(payload.get("sub"))
    phone_number = payload.get("phone")
    plan = payload.get("plan")

    # Generar nuevo access token
    new_access_token = create_access_token(
        user_id=user_id,
        phone_number=phone_number,
        plan=plan,
    )

    # Invalidar refresh token anterior (agregarlo a blacklist)
    await auth_service.invalidate_refresh_token(
        redis_client,
        jti,
        settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,  # convertir días a segundos
    )

    return RefreshResponse(
        access_token=new_access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión",
    description="Invalida los tokens del usuario.",
)
async def logout(
    authorization: Annotated[str, Depends(lambda creds=Depends(lambda: None): "")],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
):
    """
    Cierra la sesión invalidando los tokens.

    El refresh token se agrega a una blacklist en Redis.
    """
    # TODO: Implementar logout real extrayendo el refresh token del header
    # Por ahora, es un endpoint placeholder
    return None
