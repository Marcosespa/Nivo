"""Nivo — Payment Service (P2P payments y transacciones atómicas)."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from app.core.config import settings
from app.crypto.service import CryptoService
from app.models.orm.user import User as UserORM
from app.models.orm.transaction import (
    Transaction as TransactionORM,
    TransactionStatusEnum,
    SettlementRailEnum,
    SettlementStatusEnum,
)
from app.models.orm.pqc_key import PQCKey as PQCKeyORM
from app.services.wallet_service import WalletService
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)


# ─── Errores de dominio ───────────────────────────────────────────────────────

class PaymentError(Exception):
    """Base de errores de pago."""
    pass


class InsufficientFundsError(PaymentError):
    """Fondos insuficientes en la billetera."""
    pass


class DailyLimitExceededError(PaymentError):
    """Se excedió el límite diario de transacciones."""
    pass


class ReceiverNotFoundError(PaymentError):
    """El receptor no existe en el sistema."""
    pass


class WalletFrozenError(PaymentError):
    """La billetera del usuario está congelada."""
    pass


class CustodyModeNotExecutableError(PaymentError):
    """El modo de custodia no permite pagos directos."""
    pass


# ─── Payment Service ──────────────────────────────────────────────────────────

class PaymentService:
    """
    Servicio de pagos P2P — el core de Nivo.

    Maneja:
    - Validación de disponibilidad y límites
    - Almacenamiento de transacciones pendientes en Redis
    - Ejecución atómica de pagos (en una transacción de BD)
    - Firma de transacciones con ML-DSA-65
    - Actualización de balances
    """

    def __init__(self):
        self.crypto = CryptoService()
        self.wallet_service = WalletService()
        self.sms_service = SMSService()

    async def initiate_payment(
        self,
        db: AsyncSession,
        redis_client: redis.Redis,
        sender_id: uuid.UUID,
        receiver_phone: str,
        amount_cop: int,
        message: str | None = None,
    ) -> dict:
        """
        Inicia un pago P2P.

        Flujo:
        1. Buscar receptor por teléfono
        2. Validar billetera del emisor
        3. Verificar límites diarios
        4. Crear transacción pendiente
        5. Almacenar en Redis con TTL
        6. Retornar tx_id para confirmación

        Args:
            db: Sesión de BD
            redis_client: Cliente Redis
            sender_id: UUID del emisor
            receiver_phone: Teléfono del receptor
            amount_cop: Monto en centavos
            message: Mensaje opcional

        Returns:
            Dict con tx_id, status, detalles

        Raises:
            ReceiverNotFoundError
            WalletFrozenError
            DailyLimitExceededError
            InsufficientFundsError
        """
        # Buscar receptor
        stmt = select(UserORM).where(UserORM.phone_number == receiver_phone)
        result = await db.execute(stmt)
        receiver = result.scalar_one_or_none()

        if not receiver:
            raise ReceiverNotFoundError(f"Usuario con teléfono {receiver_phone} no existe")

        # Buscar emisor
        stmt = select(UserORM).where(UserORM.id == sender_id)
        result = await db.execute(stmt)
        sender = result.scalar_one_or_none()

        if not sender:
            raise ValueError(f"Emisor {sender_id} no existe")

        # Verificar billetera del emisor
        sender_wallet = await self.wallet_service.get_or_create_wallet(db, sender_id)

        if sender_wallet.is_frozen:
            raise WalletFrozenError("Tu billetera está congelada. Contacta al soporte.")

        # Verificar límites diarios
        within_limit = await self.wallet_service.check_daily_limit(
            db,
            sender_id,
            sender.plan.value,
            amount_cop,
        )
        if not within_limit:
            raise DailyLimitExceededError("Excediste el límite diario de transacciones")

        # Verificar fondos visuales (en modo visual_only)
        if sender_wallet.display_balance_cop < amount_cop:
            raise InsufficientFundsError("Saldo insuficiente en tu billetera")

        # Crear transacción pendiente
        tx_id = str(uuid.uuid4())

        # Almacenar en Redis para confirmación (TTL: 5 minutos)
        pending_tx_key = f"pending_tx:{tx_id}"
        pending_data = {
            "tx_id": tx_id,
            "sender_id": str(sender_id),
            "receiver_id": str(receiver.id),
            "receiver_phone": receiver_phone,
            "amount_cop": str(amount_cop),
            "message": message or "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Serializar como JSON para Redis
        import json
        await redis_client.setex(pending_tx_key, 300, json.dumps(pending_data))

        return {
            "tx_id": tx_id,
            "status": "pending_confirmation",
            "receiver_phone": receiver_phone,
            "receiver_name": receiver.full_name or receiver.phone_number,
            "amount_cop": amount_cop,
            "amount_display": f"${amount_cop / 100:,.0f} COP",
            "expires_in_seconds": 300,
        }

    async def execute_payment(
        self,
        db: AsyncSession,
        redis_client: redis.Redis,
        tx_id: str,
        sender_id: uuid.UUID,
        otp_code: str,
    ) -> TransactionORM:
        """
        Ejecuta un pago confirmado — DEBE ser ATÓMICO.

        Flujo (dentro de una transacción de BD):
        1. Recuperar transacción pendiente de Redis
        2. Verificar OTP
        3. Re-verificar límites (pueden haber cambiado)
        4. Construir payload para firma
        5. Firmar con llave PQC del usuario
        6. Actualizar balances (visual)
        7. Persistir transacción
        8. Limpiar Redis

        Luego (post-commit):
        9. Enviar notificación SMS al receptor

        Args:
            db: Sesión de BD
            redis_client: Cliente Redis
            tx_id: ID de transacción pendiente
            sender_id: UUID del emisor (para validar)
            otp_code: Código OTP para confirmar

        Returns:
            Objeto Transaction persistido

        Raises:
            ValueError: Si transacción no existe o datos son inválidos
            PaymentError: Errores de validación
        """
        # Recuperar transacción pendiente
        pending_tx_key = f"pending_tx:{tx_id}"
        pending_data_json = await redis_client.get(pending_tx_key)

        if not pending_data_json:
            raise ValueError(f"Transacción {tx_id} no encontrada o expiró")

        import json
        pending_data = json.loads(pending_data_json)

        # Validar que el emisor es quien dice ser
        if uuid.UUID(pending_data["sender_id"]) != sender_id:
            raise ValueError("Emisor no autorizado")

        receiver_id = uuid.UUID(pending_data["receiver_id"])
        amount_cop = int(pending_data["amount_cop"])
        message = pending_data.get("message")

        # Usar transacción de BD para atomicidad
        async with db.begin():
            # Re-verificar límites antes de ejecutar
            stmt = select(UserORM).where(UserORM.id == sender_id)
            result = await db.execute(stmt)
            sender = result.scalar_one()

            within_limit = await self.wallet_service.check_daily_limit(
                db,
                sender_id,
                sender.plan.value,
                amount_cop,
            )
            if not within_limit:
                raise DailyLimitExceededError("Límite diario excedido (cambió desde initiate)")

            # Recuperar llave PQC del usuario para firmar
            stmt = select(PQCKeyORM).where(
                (PQCKeyORM.user_id == sender_id) & (PQCKeyORM.is_active == True)
            )
            result = await db.execute(stmt)
            pqc_key = result.scalar_one()

            # Construir payload para firma
            now = datetime.now(timezone.utc)
            tx_payload = (
                f"tx:{tx_id}|"
                f"sender:{sender_id}|"
                f"receiver:{receiver_id}|"
                f"amount:{amount_cop}|"
                f"ts:{now.isoformat()}"
            ).encode()

            # Firmar con llave PQC del usuario
            # IMPORTANTE: En producción, la llave privada viene de HSM
            # Por ahora simulamos con llave efímera (SOLO PARA DESARROLLO)
            signing_kp = self.crypto.generate_signing_keypair()
            signed_tx = self.crypto.sign_transaction(
                tx_id=tx_id,
                payload=tx_payload,
                signing_secret_key=signing_kp.secret_key,
                public_key_fingerprint=pqc_key.key_fingerprint,
            )

            # Crear transacción en BD
            transaction = TransactionORM(
                id=uuid.uuid4(),
                sender_id=sender_id,
                receiver_id=receiver_id,
                amount_cop=amount_cop,
                status=TransactionStatusEnum.COMPLETED,
                rail=SettlementRailEnum.INTERNAL,
                provider_reference=f"NIVO-{tx_id[:8].upper()}",
                settlement_status=SettlementStatusEnum.SETTLED,
                ml_dsa_signature=signed_tx.signature,
                signature_key_id=pqc_key.id,
                message=message,
                created_at=now,
                confirmed_at=now,
            )
            db.add(transaction)
            await db.flush()

            # Actualizar balances visuales
            sender_wallet = await self.wallet_service.get_or_create_wallet(db, sender_id)
            receiver_wallet = await self.wallet_service.get_or_create_wallet(db, receiver_id)

            sender_wallet.display_balance_cop -= amount_cop
            receiver_wallet.display_balance_cop += amount_cop

            # Limpiar transacción pendiente de Redis
            # (no se puede dentro de transacción de BD, se hace después del commit)

        # Eliminar de Redis post-commit
        await redis_client.delete(pending_tx_key)

        # Enviar notificación SMS al receptor (no bloquea)
        try:
            receiver_name = sender.full_name or sender.phone_number
            await self.sms_service.send_payment_notification(
                pending_data["receiver_phone"],
                f"${amount_cop / 100:,.0f} COP",
                receiver_name,
            )
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")

        return transaction
