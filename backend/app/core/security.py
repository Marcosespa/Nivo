"""Nivo — Utilidades de seguridad JWT."""

from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.orm.user import User as UserORM

security = HTTPBearer()


def create_access_token(
    user_id: uuid.UUID,
    phone_number: str,
    plan: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Crea un JWT de acceso.

    Payload:
    {
        "sub": "user_uuid",
        "phone": "+57310xxxxxxx",
        "plan": "free",
        "jti": "uuid_único",
        "exp": timestamp,
        "iat": timestamp,
        "type": "access"
    }
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": str(user_id),
        "phone": phone_number,
        "plan": plan,
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(
    user_id: uuid.UUID,
    phone_number: str,
    plan: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Crea un JWT de renovación (refresh token).

    Payload igual al access token pero con "type": "refresh"
    y TTL más largo.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "sub": str(user_id),
        "phone": phone_number,
        "plan": plan,
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


async def decode_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.

    Returns:
        Payload decodificado

    Raises:
        HTTPException: Si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido o expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserORM:
    """
    Dependencia FastAPI para obtener el usuario autenticado.

    Verifica el JWT, busca el usuario en BD, y valida que esté activo.
    """
    token = credentials.credentials

    # Decodificar JWT
    payload = await decode_token(token)

    # Verificar tipo de token
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (no es access token)",
        )

    # Obtener user_id del payload
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (sin sub claim)",
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (sub no es UUID válido)",
        )

    # Buscar usuario en BD
    stmt = select(UserORM).where(UserORM.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return user
