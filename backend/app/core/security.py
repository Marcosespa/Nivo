"""Nivo — Utilidades de seguridad JWT."""

from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Dependencia FastAPI para obtener el usuario autenticado."""
    # TODO: decodificar JWT y recuperar usuario de BD
    # Por ahora retorna un usuario mock para desarrollo
    return User(
        id="mock_user_id",
        phone_number="+57 310 000 0000",
        created_at=datetime.now(timezone.utc),
    )
