"""Nivo — Authentication Service."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crypto.service import CryptoService
from app.models.orm.user import User as UserORM, UserPlanEnum, KYCStatusEnum
from app.models.orm.pqc_key import PQCKey as PQCKeyORM
from app.models.orm.wallet import Wallet as WalletORM


class AuthService:
    """
    Servicio de autenticación y onboarding de usuarios.

    Flujo:
    1. get_or_create_user: obtiene usuario existente o crea uno nuevo
    2. create_pqc_keys_for_user: genera y almacena llaves PQC para firmar transacciones
    """

    def __init__(self):
        self.crypto = CryptoService()

    async def get_or_create_user(self, db: AsyncSession, phone_number: str) -> tuple[UserORM, bool]:
        """
        Obtiene un usuario existente o crea uno nuevo.

        Args:
            db: Sesión de BD asincrónica
            phone_number: Número de celular en formato +57XXXXXXXXX

        Returns:
            Tupla (user_orm, is_new) donde is_new=True si fue creado
        """
        # Buscar usuario existente
        stmt = select(UserORM).where(UserORM.phone_number == phone_number)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            return user, False

        # Crear usuario nuevo
        user = UserORM(
            phone_number=phone_number,
            plan=UserPlanEnum.FREE,
            kyc_status=KYCStatusEnum.PENDING,
            is_active=True,
        )
        db.add(user)
        await db.flush()  # Para obtener el ID antes de hacer commit

        # Crear billetera para el nuevo usuario
        wallet = WalletORM(
            user_id=user.id,
            display_balance_cop=0,
        )
        db.add(wallet)
        await db.flush()

        return user, True

    async def create_pqc_keys_for_user(self, db: AsyncSession, user_id: uuid.UUID) -> PQCKeyORM:
        """
        Genera un par de llaves ML-DSA-65 para firma de transacciones.
        Almacena la llave PÚBLICA en BD; la privada se logea en desarrollo.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario

        Returns:
            Objeto PQCKey almacenado en BD

        Raises:
            ValueError: Si el usuario ya tiene una llave activa
        """
        # Verificar si ya existe llave activa
        stmt = select(PQCKeyORM).where(
            (PQCKeyORM.user_id == user_id) & (PQCKeyORM.is_active == True)
        )
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            raise ValueError(f"Usuario {user_id} ya tiene una llave PQC activa")

        # Generar keypair
        signing_kp = self.crypto.generate_signing_keypair()

        # Crear registro en BD (solo llave pública)
        pqc_key = PQCKeyORM(
            user_id=user_id,
            algorithm=signing_kp.algorithm,
            public_key=signing_kp.public_key,
            key_fingerprint=signing_kp.public_key_fingerprint,
            is_active=True,
        )
        db.add(pqc_key)
        await db.flush()

        # En desarrollo: loggear la llave privada (NUNCA en producción)
        import logging
        logger = logging.getLogger(__name__)
        if False:  # TODO: cambiar a settings.DEBUG y refactorizar para evitar logs
            logger.debug(f"[DEV] Private key for {user_id}: {signing_kp.secret_key.hex()[:64]}...")

        return pqc_key

    async def invalidate_refresh_token(self, redis, jti: str, ttl: int) -> None:
        """
        Agrega un refresh token a la blacklist en Redis.

        Args:
            redis: Cliente Redis
            jti: ID único del JWT (claim 'jti')
            ttl: Segundos para expirar
        """
        blacklist_key = f"blacklist:jti:{jti}"
        await redis.setex(blacklist_key, ttl, "1")

    async def is_token_blacklisted(self, redis, jti: str) -> bool:
        """
        Verifica si un JWT está en la blacklist.

        Args:
            redis: Cliente Redis
            jti: ID único del JWT

        Returns:
            True si está en blacklist; False en caso contrario
        """
        blacklist_key = f"blacklist:jti:{jti}"
        result = await redis.get(blacklist_key)
        return result is not None
