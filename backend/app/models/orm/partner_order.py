"""Nivo — Partner Order ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, BigInteger, DateTime, Enum as SQLEnum, ForeignKey, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProductTypeEnum(str, Enum):
    """Investment product type."""
    FX = "fx"
    CRYPTO = "crypto"
    STOCK = "stock"
    ETF = "etf"


class SideEnum(str, Enum):
    """Buy/sell side."""
    BUY = "buy"
    SELL = "sell"
    CONVERT = "convert"


class ExecutionStatusEnum(str, Enum):
    """Order execution status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PartnerOrder(Base):
    """
    Tabla de órdenes de inversión — FX, crypto, stocks y ETFs.
    El usuario acepta riesgos antes de colocar la orden.
    Cada orden es firmada con ML-DSA-65 para inmutabilidad regulatoria.

    IMPORTANTE:
    - accepted_disclosure_hash: SHA-256 del documento de riesgo que el usuario aceptó
    - signed_order_payload: payload serializado que fue firmado
    - ml_dsa_signature: firma cuántica de la orden (prueba de aceptación)
    """

    __tablename__ = "partner_orders"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_type: Mapped[ProductTypeEnum] = mapped_column(SQLEnum(ProductTypeEnum), nullable=False)
    partner: Mapped[str] = mapped_column(String(80), nullable=False)  # "Criptoyá", "IMC FX", etc.
    partner_order_id: Mapped[str | None] = mapped_column(String(120), nullable=True)  # ID del proveedor
    instrument_symbol: Mapped[str] = mapped_column(String(30), nullable=False)  # "BTC", "EURUSD", "AAPL"
    side: Mapped[SideEnum] = mapped_column(SQLEnum(SideEnum), nullable=False)
    notional_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # En centavos
    source_currency: Mapped[str] = mapped_column(String(10), nullable=False)  # "COP", "USD"
    target_currency: Mapped[str] = mapped_column(String(10), nullable=False)  # "BTC", "EUR", etc.
    execution_status: Mapped[ExecutionStatusEnum] = mapped_column(SQLEnum(ExecutionStatusEnum), default=ExecutionStatusEnum.PENDING)

    # Firma y riesgos
    risk_disclosure_version: Mapped[str] = mapped_column(String(30), nullable=False)  # "1.0.0", "2.1.0"
    accepted_disclosure_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 del disclosure
    signed_order_payload: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Payload que fue firmado
    ml_dsa_signature: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Firma cuántica

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relaciones
    user: Mapped[User] = relationship("User", back_populates="partner_orders")

    def __repr__(self) -> str:
        return f"<PartnerOrder {self.instrument_symbol} {self.side.value} status={self.execution_status.value}>"


# Import forward reference
from .user import User
