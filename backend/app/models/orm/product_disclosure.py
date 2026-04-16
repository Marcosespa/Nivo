"""Nivo — Product Disclosure ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProductTypeEnum(str, Enum):
    """Investment product type."""
    FX = "fx"
    CRYPTO = "crypto"
    STOCK = "stock"
    ETF = "etf"


class ProductDisclosure(Base):
    """
    Tabla de documentos de riesgo — versioning de textos de disclosure.
    Cada versión es identificada por (product_type, version).
    El hash permite auditar cambios y validar que el usuario aceptó la versión correcta.

    IMPORTANTE:
    - content_hash: SHA-256 del documento en plano (para auditoría)
    - is_active: solo un disclosure por producto puede estar activo
    """

    __tablename__ = "product_disclosures"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_type: Mapped[ProductTypeEnum] = mapped_column(
        SQLEnum(
            ProductTypeEnum,
            name="producttypeenum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(30), nullable=False)  # "1.0.0", "1.1.0", "2.0.0"
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 del content
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("product_type", "version", name="uq_product_version"),
    )

    def __repr__(self) -> str:
        return f"<ProductDisclosure {self.product_type.value} v{self.version}>"
