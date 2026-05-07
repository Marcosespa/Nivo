"""Nivo — PQC Key ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, ForeignKey, LargeBinary, func, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PQCKey(Base):
    """
    Tabla de llaves post-cuánticas — almacena llaves PÚBLICAS de usuarios.
    Las llaves privadas NUNCA se almacenan en BD — van a HSM/KMS en producción.

    Un usuario puede tener múltiples llaves (para rotación, respaldo, etc).
    Cada llave tiene un fingerprint único (SHA-256 hex).
    """

    __tablename__ = "pqc_keys"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    algorithm: Mapped[str] = mapped_column(String(30), nullable=False)  # "ML-DSA-65", "ML-KEM-768"
    public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Llave pública en crudo
    key_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 hex
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Índices compuestos
    __table_args__ = (
        Index("idx_user_algo_active", "user_id", "algorithm", "is_active"),
        UniqueConstraint("key_fingerprint", name="uq_pqc_key_fingerprint"),
        Index("ix_pqc_keys_key_fingerprint", "key_fingerprint"),
    )

    # Relaciones
    user: Mapped[User] = relationship("User", back_populates="pqc_keys")
    transactions: Mapped[list[Transaction]] = relationship("Transaction", back_populates="signature_key")

    def __repr__(self) -> str:
        return f"<PQCKey {self.algorithm} fingerprint={self.key_fingerprint[:16]}...>"


# Import forward references
from .user import User
from .transaction import Transaction
