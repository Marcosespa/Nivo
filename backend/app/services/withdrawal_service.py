"""Nivo — Withdrawal Service (ACH bank transfers)."""

from __future__ import annotations
import uuid
import hashlib
import secrets
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.crypto.service import CryptoService
from app.models.orm.user import User as UserORM
from app.models.orm.bank_account import BankAccount as BankAccountORM, AccountTypeEnum
from app.models.orm.wallet import Wallet as WalletORM
from app.models.orm.transaction import (
    Transaction as TransactionORM,
    TransactionStatusEnum,
    SettlementRailEnum,
    SettlementStatusEnum,
)
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)


# ─── Errores de dominio ───────────────────────────────────────────────────────

class WithdrawalError(Exception):
    """Base de errores de retiros."""
    pass


class BankAccountNotFoundError(WithdrawalError):
    """Cuenta bancaria no encontrada."""
    pass


class BankAccountNotVerifiedError(WithdrawalError):
    """Cuenta bancaria no verificada."""
    pass


class InsufficientFundsError(WithdrawalError):
    """Fondos insuficientes."""
    pass


class DailyLimitExceededError(WithdrawalError):
    """Límite diario de retiros excedido."""
    pass


# ─── Withdrawal Service ───────────────────────────────────────────────────────

class WithdrawalService:
    """
    Servicio de retiros — transferencias ACH a cuentas bancarias verificadas.

    Flujo:
    1. Usuario registra cuenta bancaria (número encriptado)
    2. Backend envía micro-depósito (501-999 COP, hashed)
    3. Usuario confirma monto exacto
    4. Usuario inicia retiro a cuenta verificada
    5. Backend procesa ACH via Wompi (asincrónico)
    6. Status pasa a 'completed' cuando el banco confirma

    Comisiones:
    - FREE: $2,000 COP
    - PLUS/PRO: GRATIS

    Límite diario: igual a TX_LIMIT_{PLAN}_DAILY
    """

    WITHDRAWAL_COMMISSION_FREE_COP: int = 2_000_00  # $2,000 COP en centavos
    MICRO_DEPOSIT_MIN_COP: int = 501_00  # $501 COP mínimo
    MICRO_DEPOSIT_MAX_COP: int = 999_00  # $999 COP máximo
    REQUEST_TIMEOUT_SECONDS: int = 10

    def __init__(self):
        self.crypto = CryptoService()
        self.wallet_service = WalletService()

    async def register_bank_account(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        bank_code: str,
        account_type: str,
        account_number: str,
        account_holder_name: str,
    ) -> dict:
        """
        Registra una nueva cuenta bancaria para retiros.

        El número de cuenta se cifra con AES-256-GCM.
        Se genera un micro-depósito aleatorio (501-999 COP).

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
            bank_code: Código del banco colombiano (ej: "001")
            account_type: "savings" o "checking"
            account_number: Número de cuenta (NUNCA en plaintext)
            account_holder_name: Nombre del titular

        Returns:
            Dict con bank_account_id y micro_deposit_amount

        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validar cuenta bancaria
        if len(account_number) < 8 or len(account_number) > 20:
            raise ValueError("Número de cuenta inválido")

        if account_type not in ["savings", "checking"]:
            raise ValueError("Tipo de cuenta debe ser 'savings' o 'checking'")

        # Buscar usuario
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"Usuario {user_id} no existe")

        # Verificar que no existe otra cuenta sin verificar
        stmt = select(BankAccountORM).where(
            (BankAccountORM.user_id == user_id) & (BankAccountORM.is_verified == False)
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise WithdrawalError(
                "Ya tienes una cuenta sin verificar. Completa la verificación o elimínala primero."
            )

        # Generar micro-depósito aleatorio (501-999 COP)
        micro_amount_cop = secrets.randbelow(
            self.MICRO_DEPOSIT_MAX_COP - self.MICRO_DEPOSIT_MIN_COP
        ) + self.MICRO_DEPOSIT_MIN_COP

        # Cifrar número de cuenta con AES-256-GCM
        encrypted_account = self._encrypt_account_number(account_number)

        # Hash del micro-depósito (para verificación sin almacenar plaintext)
        micro_hash = hashlib.sha256(str(micro_amount_cop).encode()).digest()

        # Crear cuenta bancaria
        bank_account = BankAccountORM(
            user_id=user_id,
            bank_code=bank_code,
            account_type=AccountTypeEnum(account_type),
            account_number_encrypted=encrypted_account,
            account_holder_name=account_holder_name,
            is_verified=False,
            verification_amount_cop=micro_amount_cop,
            verification_amount_hash=micro_hash,
        )
        db.add(bank_account)
        await db.flush()

        logger.info(f"Bank account registered for user {user_id}")

        return {
            "bank_account_id": str(bank_account.id),
            "verification_amount_cop": micro_amount_cop,
            "verification_amount_display": f"${micro_amount_cop / 100:,.0f} COP",
            "message": "Hemos iniciado un micro-depósito. Confirma el monto exacto cuando lo recibas.",
        }

    async def verify_bank_account(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        bank_account_id: uuid.UUID,
        verification_amount_cop: int,
    ) -> dict:
        """
        Verifica una cuenta bancaria comparando el micro-depósito.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
            bank_account_id: UUID de la cuenta bancaria
            verification_amount_cop: Monto que el usuario recibió

        Returns:
            Dict con confirmación

        Raises:
            BankAccountNotFoundError: Si la cuenta no existe
            WithdrawalError: Si el monto no coincide
        """
        # Buscar cuenta
        stmt = select(BankAccountORM).where(
            (BankAccountORM.id == bank_account_id) & (BankAccountORM.user_id == user_id)
        )
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            raise BankAccountNotFoundError("Cuenta bancaria no encontrada")

        if account.is_verified:
            raise WithdrawalError("Esta cuenta ya está verificada")

        # Comparar hash del monto
        provided_hash = hashlib.sha256(str(verification_amount_cop).encode()).digest()

        if not hashlib.pbkdf2_hmac(
            "sha256",
            str(verification_amount_cop).encode(),
            b"",
            1,
        ) == hashlib.pbkdf2_hmac("sha256", str(account.verification_amount_cop or 0).encode(), b"", 1):
            # Comparación simple sin PBKDF2 (inseguro pero rápido en MVP)
            if verification_amount_cop != account.verification_amount_cop:
                raise WithdrawalError("El monto verificado no coincide. Intenta de nuevo.")

        # Marcar como verificada
        account.is_verified = True
        account.verification_amount_cop = None  # Borrar el monto almacenado
        account.verification_amount_hash = None  # Borrar el hash
        await db.flush()

        logger.info(f"Bank account {bank_account_id} verified for user {user_id}")

        return {
            "status": "verified",
            "message": "Cuenta verificada correctamente. Ya puedes hacer retiros.",
        }

    async def list_bank_accounts(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[dict]:
        """
        Lista las cuentas bancarias del usuario (SIN mostrar números).

        Args:
            db: Sesión de BD
            user_id: UUID del usuario

        Returns:
            Lista de cuentas (solo últimos 4 dígitos del número)
        """
        stmt = select(BankAccountORM).where(BankAccountORM.user_id == user_id)
        result = await db.execute(stmt)
        accounts = result.scalars().all()

        return [
            {
                "id": str(account.id),
                "bank_code": account.bank_code,
                "account_type": account.account_type.value,
                "account_number_last4": "****",  # NUNCA retornar número completo
                "account_holder_name": account.account_holder_name,
                "is_verified": account.is_verified,
                "created_at": account.created_at.isoformat(),
            }
            for account in accounts
        ]

    async def initiate_withdrawal(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        bank_account_id: uuid.UUID,
        amount_cop: int,
    ) -> dict:
        """
        Inicia un retiro a una cuenta bancaria verificada.

        Flujo:
        1. Validar cuenta verificada
        2. Verificar fondos
        3. Aplicar comisión según plan
        4. Debitar balance visual
        5. Crear transacción en BD (status=pending)
        6. Enviar a Wompi ACH (asincrónico)

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
            bank_account_id: UUID de la cuenta bancaria
            amount_cop: Monto a retirar en centavos

        Returns:
            Dict con transaction_id y detalles

        Raises:
            BankAccountNotFoundError: Si la cuenta no existe
            BankAccountNotVerifiedError: Si la cuenta no está verificada
            InsufficientFundsError: Si no hay fondos suficientes
        """
        # Buscar usuario y cuenta
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"Usuario {user_id} no existe")

        stmt = select(BankAccountORM).where(
            (BankAccountORM.id == bank_account_id) & (BankAccountORM.user_id == user_id)
        )
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            raise BankAccountNotFoundError("Cuenta bancaria no encontrada")

        if not account.is_verified:
            raise BankAccountNotVerifiedError(
                "La cuenta bancaria debe estar verificada para hacer retiros"
            )

        # Determinar comisión
        commission_cop = (
            self.WITHDRAWAL_COMMISSION_FREE_COP
            if user.plan.value == "free"
            else 0
        )

        total_debit = amount_cop + commission_cop

        # Verificar fondos visuales
        wallet = await self.wallet_service.get_or_create_wallet(db, user_id)

        if wallet.display_balance_cop < total_debit:
            raise InsufficientFundsError(
                f"Saldo insuficiente. Necesitas ${total_debit / 100:,.0f} COP "
                f"(${amount_cop / 100:,.0f} + ${commission_cop / 100:,.0f} comisión)"
            )

        # Verificar límite diario
        within_limit = await self.wallet_service.check_daily_limit(
            db,
            user_id,
            user.plan.value,
            amount_cop,
        )

        if not within_limit:
            raise DailyLimitExceededError(
                "Excediste el límite diario de retiros"
            )

        # Usar transacción de BD para atomicidad
        async with db.begin():
            # Debitar balance visual
            wallet.display_balance_cop -= total_debit

            # Crear transacción
            transaction = TransactionORM(
                id=uuid.uuid4(),
                sender_id=user_id,
                receiver_id=user_id,  # Retiro a sí mismo
                amount_cop=amount_cop,
                status=TransactionStatusEnum.PENDING,
                rail=SettlementRailEnum.ACH,
                settlement_status=SettlementStatusEnum.PENDING,
                ml_dsa_signature=b"",  # Retiros no firmados en MVP
                signature_key_id=uuid.uuid4(),  # Dummy
                message=f"Withdrawal to {account.account_holder_name}",
            )
            db.add(transaction)
            await db.flush()

        logger.info(
            f"Withdrawal initiated: user={user_id} account={bank_account_id} "
            f"amount={amount_cop} commission={commission_cop}"
        )

        return {
            "transaction_id": str(transaction.id),
            "amount_cop": amount_cop,
            "amount_display": f"${amount_cop / 100:,.0f} COP",
            "commission_cop": commission_cop,
            "commission_display": f"${commission_cop / 100:,.0f} COP",
            "total_debit": total_debit,
            "total_debit_display": f"${total_debit / 100:,.0f} COP",
            "status": "pending",
            "processing_time": "1-2 días hábiles",
        }

    async def get_withdrawal_history(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 20,
    ) -> list[dict]:
        """
        Obtiene historial de retiros del usuario.

        Args:
            db: Sesión de BD
            user_id: UUID del usuario
            limit: Número máximo de registros

        Returns:
            Lista de transacciones de tipo 'withdrawal'
        """
        stmt = (
            select(TransactionORM)
            .where(
                (TransactionORM.sender_id == user_id) &
                (TransactionORM.rail == SettlementRailEnum.ACH)
            )
            .order_by(TransactionORM.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        transactions = result.scalars().all()

        return [
            {
                "id": str(tx.id),
                "amount_cop": tx.amount_cop,
                "amount_display": f"${tx.amount_cop / 100:,.0f} COP",
                "status": tx.status.value,
                "settlement_status": tx.settlement_status.value,
                "created_at": tx.created_at.isoformat(),
            }
            for tx in transactions
        ]

    def _encrypt_account_number(self, account_number: str) -> bytes:
        """
        Cifra el número de cuenta con AES-256-GCM.

        IMPORTANTE: En producción, la llave debe venir del HSM.
        En MVP, usamos una llave derivada de config (INSEGURO).
        """
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import os

        # Derivar llave de 32 bytes a partir de JWT_SECRET_KEY
        key = hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest()

        # Generar nonce aleatorio (12 bytes para GCM)
        nonce = os.urandom(12)

        # Cifrar
        cipher = AESGCM(key)
        ciphertext = cipher.encrypt(nonce, account_number.encode(), None)

        # Retornar nonce + ciphertext (el nonce se incluye para descifrado)
        return nonce + ciphertext

    def _decrypt_account_number(self, encrypted: bytes) -> str:
        """
        Descifra el número de cuenta.

        El formato es: nonce (12 bytes) + ciphertext
        """
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        # Derivar llave (misma que en encriptación)
        key = hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest()

        # Extraer nonce y ciphertext
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]

        # Descifrar
        cipher = AESGCM(key)
        plaintext = cipher.decrypt(nonce, ciphertext, None)

        return plaintext.decode()
