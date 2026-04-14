"""Nivo — Wallet Service (saldos visuales y gestión de billeteras)."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import settings
from app.models.orm.wallet import Wallet as WalletORM
from app.models.orm.transaction import Transaction as TransactionORM, TransactionStatusEnum


class WalletService:
    """
    Servicio de billetera — gestiona saldos visuales.

    IMPORTANTE:
    - En MVP, el display_balance_cop es VISUAL, no es el saldo legal
    - El saldo legal está en el aliado regulado (PSE, ACH, banco)
    - Aquí solo cacheamos lo que el usuario ve en pantalla
    """

    async def get_or_create_wallet(self, db: AsyncSession, user_id: uuid.UUID) -> WalletORM:
        """
        Obtiene la billetera de un usuario o la crea.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario

        Returns:
            Objeto Wallet
        """
        stmt = select(WalletORM).where(WalletORM.user_id == user_id)
        result = await db.execute(stmt)
        wallet = result.scalar_one_or_none()

        if wallet:
            return wallet

        # Crear billetera nueva
        wallet = WalletORM(
            user_id=user_id,
            display_balance_cop=0,
        )
        db.add(wallet)
        await db.flush()
        return wallet

    async def get_display_balance(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        """
        Obtiene el saldo visual de la billetera del usuario.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario

        Returns:
            Saldo en centavos de COP
        """
        wallet = await self.get_or_create_wallet(db, user_id)
        return wallet.display_balance_cop

    async def check_daily_limit(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        plan: str,
        amount_cop: int,
    ) -> bool:
        """
        Verifica si el usuario está dentro del límite diario de transacciones.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
            plan: Plan del usuario ("free", "plus", "pro")
            amount_cop: Monto a transferir en centavos

        Returns:
            True si está dentro del límite; False en caso contrario
        """
        # Determinar límite según plan
        limits = {
            "free": settings.TX_LIMIT_FREE_DAILY,
            "plus": settings.TX_LIMIT_PLUS_DAILY,
            "pro": settings.TX_LIMIT_PRO_DAILY,
        }
        daily_limit = limits.get(plan, settings.TX_LIMIT_FREE_DAILY)

        # Calcular inicio del día (medianoche Colombia UTC-5)
        now = datetime.now(timezone.utc)
        # Convertir a hora colombiana (UTC-5)
        colombia_tz_offset = timedelta(hours=-5)
        now_colombia = now + colombia_tz_offset
        midnight = now_colombia.replace(hour=0, minute=0, second=0, microsecond=0)
        midnight_utc = midnight - colombia_tz_offset

        # Sumar transacciones completadas hoy
        stmt = select(func.sum(TransactionORM.amount_cop)).where(
            (TransactionORM.sender_id == user_id)
            & (TransactionORM.status == TransactionStatusEnum.COMPLETED)
            & (TransactionORM.created_at >= midnight_utc)
        )
        result = await db.execute(stmt)
        total_today = result.scalar() or 0

        # Verificar si el nuevo monto sobrepasa el límite
        return (total_today + amount_cop) <= daily_limit

    async def freeze_wallet(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        """
        Congela la billetera de un usuario (desactiva pagos).

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
        """
        wallet = await self.get_or_create_wallet(db, user_id)
        wallet.is_frozen = True
        await db.flush()

    async def unfreeze_wallet(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        """
        Descongela la billetera de un usuario.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
        """
        wallet = await self.get_or_create_wallet(db, user_id)
        wallet.is_frozen = False
        await db.flush()
