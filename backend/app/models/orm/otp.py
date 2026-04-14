"""Nivo — OTP ORM Model."""

from __future__ import annotations
from datetime import datetime, timezone
import uuid
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OTPPurposeEnum(str, Enum):
    """Purpose of OTP."""
    LOGIN = "login"
    PAYMENT = "payment"
    KYC = "kyc"


class OTP(Base):
    """
    Tabla de OTPs — códigos de un solo uso para verificación.
    Almacena el hash bcrypt del OTP, nunca el código en plano.

    En producción, los OTPs se expiran después de 5 minutos.
    Se intenta máximo 3 veces antes de invalidar.
    """

    __tablename__ = "otps"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    otp_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # Bcrypt hash (no SHA)
    purpose: Mapped[OTPPurposeEnum] = mapped_column(SQLEnum(OTPPurposeEnum), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Índices compuestos
    __table_args__ = (
        Index("idx_phone_expires", "phone_number", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<OTP {self.phone_number[-4:]}... purpose={self.purpose.value} used={self.used}>"
