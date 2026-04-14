"""Nivo — Transaction ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, BigInteger, DateTime, Enum as SQLEnum, ForeignKey, LargeBinary, func, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TransactionStatusEnum(str, Enum):
    """Transaction status."""
    PENDING = "pending"
    PENDING_CONFIRMATION = "pending_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class SettlementRailEnum(str, Enum):
    """Settlement rail (how funds move)."""
    PSE = "pse"
    ACH = "ach"
    BANK_PARTNER = "bank_partner"
    INTERNAL = "internal"


class SettlementStatusEnum(str, Enum):
    """Settlement status with regulated provider."""
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"
    REVERSED = "reversed"


class Transaction(Base):
    """
    Tabla de transacciones — el core ledger de movimientos en Nivo.
    Cada transacción es inmutable y firmada con ML-DSA-65.

    IMPORTANTE:
    - sender_id y receiver_id: UUID de usuarios en el sistema
    - amount_cop: siempre positivo, en centavos
    - ml_dsa_signature: firma cuántica resistente de la transacción
    - rail: cómo se liquidó (PSE, ACH, banco aliado o interno visual)
    - provider_reference: ID que el aliado retorna (para conciliación)
    - settlement_status: estado en el lado del proveedor regulado
    """

    __tablename__ = "transactions"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    receiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount_cop: Mapped[int] = mapped_column(BigInteger, nullable=False)  # centavos
    status: Mapped[TransactionStatusEnum] = mapped_column(SQLEnum(TransactionStatusEnum), default=TransactionStatusEnum.PENDING, index=True)

    # Firma cuántica
    ml_dsa_signature: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    signature_key_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pqc_keys.id", ondelete="RESTRICT"), nullable=False)

    # Regulatorio / Settlement
    rail: Mapped[SettlementRailEnum] = mapped_column(SQLEnum(SettlementRailEnum), default=SettlementRailEnum.INTERNAL)
    provider_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)  # ID del proveedor (PSE, ACH, etc)
    settlement_status: Mapped[SettlementStatusEnum] = mapped_column(SQLEnum(SettlementStatusEnum), default=SettlementStatusEnum.PENDING)

    # Metadata
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)  # Para datos sensibles cifrados

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint("amount_cop > 0", name="ck_transaction_amount_positive"),
        Index("idx_sender_created", "sender_id", "created_at"),
        Index("idx_receiver_created", "receiver_id", "created_at"),
    )

    # Relaciones
    sender: Mapped[User] = relationship("User", foreign_keys=[sender_id], back_populates="sent_transactions")
    receiver: Mapped[User] = relationship("User", foreign_keys=[receiver_id], back_populates="received_transactions")
    signature_key: Mapped[PQCKey] = relationship("PQCKey", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} amount={self.amount_cop} status={self.status.value}>"


# Import forward references
from .user import User
from .pqc_key import PQCKey
