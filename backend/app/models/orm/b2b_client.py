"""Nivo — B2B Client ORM Model."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, func, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class B2BClient(Base):
    """
    Cliente B2B de Nivo (consumidor de PQC-as-a-Service).

    `api_key_hash` almacena SHA-256 del API key. La clave en claro solo se
    muestra una vez al emisor y no se persiste.

    Nota de negocio: este modelo habilita autenticación real del endpoint
    B2B en desarrollo/staging para que no sea abusable. El billing por
    operación NO está implementado aún — se definirá cuando el equipo de
    negocio cierre pricing y pipeline (ver ANALISIS_DE_NEGOCIO_RESPUESTAS.md).
    """

    __tablename__ = "b2b_clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("api_key_hash", name="uq_b2b_clients_api_key_hash"),
        Index("ix_b2b_clients_api_key_hash", "api_key_hash"),
    )

    def __repr__(self) -> str:
        return f"<B2BClient name={self.name} active={self.is_active}>"
