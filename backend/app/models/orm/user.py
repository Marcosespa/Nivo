"""Nivo — User ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserPlanEnum(str, Enum):
    """User subscription plan."""
    FREE = "free"
    PLUS = "plus"
    PRO = "pro"


class KYCStatusEnum(str, Enum):
    """KYC verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class User(Base):
    """
    Tabla de usuarios — el corazón del onboarding de Nivo.
    Cada usuario es identificado por su número de celular único.
    """

    __tablename__ = "users"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Plan y estado
    plan: Mapped[UserPlanEnum] = mapped_column(
        SQLEnum(
            UserPlanEnum,
            name="userplanenum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=UserPlanEnum.FREE,
    )
    kyc_status: Mapped[KYCStatusEnum] = mapped_column(
        SQLEnum(
            KYCStatusEnum,
            name="kycstatusenum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=KYCStatusEnum.PENDING,
    )
    kyc_provider_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

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

    # Relaciones
    wallet: Mapped[Wallet | None] = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    savings_pockets: Mapped[list[SavingsPocket]] = relationship("SavingsPocket", back_populates="user", cascade="all, delete-orphan")
    pqc_keys: Mapped[list[PQCKey]] = relationship("PQCKey", back_populates="user", cascade="all, delete-orphan")
    bank_accounts: Mapped[list[BankAccount]] = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    sent_transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )
    merchants: Mapped[list[Merchant]] = relationship("Merchant", back_populates="owner", cascade="all, delete-orphan")
    partner_orders: Mapped[list[PartnerOrder]] = relationship("PartnerOrder", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.phone_number} (plan={self.plan.value}, kyc={self.kyc_status.value})>"


# Import forward references for relationships
from .wallet import Wallet
from .savings_pocket import SavingsPocket
from .transaction import Transaction
from .pqc_key import PQCKey
from .merchant import Merchant
from .partner_order import PartnerOrder
from .bank_account import BankAccount
