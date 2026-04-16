"""Nivo — Bank Account ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, Boolean, BigInteger, DateTime, Enum as SQLEnum, ForeignKey, LargeBinary, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AccountTypeEnum(str, Enum):
    """Tipo de cuenta bancaria."""
    SAVINGS = "savings"
    CHECKING = "checking"


class BankAccount(Base):
    """
    Tabla de cuentas bancarias — permite retiros a ACH.

    SEGURIDAD NO-NEGOCIABLE:
    - account_number_encrypted: NUNCA en plaintext, siempre AES-256-GCM
    - account_number_encrypted: NUNCA retornar en API, solo últimos 4 dígitos
    - Micro-deposit: cantidad aleatoria 501-999 COP, almacenada hashed
    - Retiros solo a cuentas VERIFIED
    """

    __tablename__ = "bank_accounts"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bank_code: Mapped[str] = mapped_column(String(10), nullable=False)  # "001", "051", etc
    account_type: Mapped[AccountTypeEnum] = mapped_column(
        SQLEnum(
            AccountTypeEnum,
            name="accounttypeenum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    account_number_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # AES-256-GCM
    account_holder_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Verificación
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_amount_cop: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # Cantidad del micro-depósito
    verification_amount_hash: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)  # SHA-256 hash

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Índices
    __table_args__ = (
        Index("idx_user_verified", "user_id", "is_verified"),
    )

    # Relaciones
    user: Mapped[User] = relationship("User", back_populates="bank_accounts")

    def __repr__(self) -> str:
        return f"<BankAccount user_id={self.user_id} verified={self.is_verified}>"


# Import forward reference
from .user import User
