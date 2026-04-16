"""Nivo — Merchant ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MerchantPlanEnum(str, Enum):
    """Merchant subscription plan."""
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Merchant(Base):
    """
    Tabla de comercios — usuarios que actúan como vendedores en Nivo.
    Cada comercio tiene un propietario (usuario) y genera códigos QR para cobros.
    """

    __tablename__ = "merchants"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    nit: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)  # NIT opcional
    plan: Mapped[MerchantPlanEnum] = mapped_column(
        SQLEnum(
            MerchantPlanEnum,
            name="merchantplanenum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=MerchantPlanEnum.BASIC,
    )
    qr_code_signature: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)  # Firma del código QR
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Relaciones
    owner: Mapped[User] = relationship("User", back_populates="merchants")

    def __repr__(self) -> str:
        return f"<Merchant {self.business_name} plan={self.plan.value}>"


# Import forward reference
from .user import User
