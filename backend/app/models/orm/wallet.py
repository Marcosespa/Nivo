"""Nivo — Wallet ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, Boolean, BigInteger, DateTime, Enum as SQLEnum, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CustodyModeEnum(str, Enum):
    """Custody mode for wallet funds."""
    VISUAL_ONLY = "visual_only"
    PARTNER_LEDGER = "partner_ledger"
    SEDPE = "sedpe"
    BANK_PARTNER = "bank_partner"


class Wallet(Base):
    """
    Tabla de billeteras — un usuario, una billetera.
    La relación es 1:1 con users (cascade delete).

    El display_balance_cop es SOLO visual en MVP — el ledger legal está en el aliado.
    En modo visual_only, es un número que el usuario ve, no un balance auditable.
    """

    __tablename__ = "wallets"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="COP")
    display_balance_cop: Mapped[int] = mapped_column(BigInteger, default=0)  # centavos
    custody_mode: Mapped[CustodyModeEnum] = mapped_column(
        SQLEnum(
            CustodyModeEnum,
            name="custodymodeenum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=CustodyModeEnum.VISUAL_ONLY,
    )
    provider_account_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_frozen: Mapped[bool] = mapped_column(Boolean, default=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("display_balance_cop >= 0", name="ck_wallet_balance_nonnegative"),
    )

    # Relaciones
    user: Mapped[User] = relationship("User", back_populates="wallet")

    def __repr__(self) -> str:
        return f"<Wallet user_id={self.user_id} balance={self.display_balance_cop}>"


# Import forward reference
from .user import User
