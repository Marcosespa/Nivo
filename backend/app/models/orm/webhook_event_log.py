"""Nivo — Webhook Event Log ORM Model (idempotencia)."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, DateTime, Enum as SQLEnum, BigInteger, func, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class WebhookEventStatusEnum(str, Enum):
    """Webhook event processing status."""
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"


class WebhookEventLog(Base):
    """
    Tabla de rastreo de eventos webhook — idempotencia garantizada.

    Garantiza que cada webhook se procese exactamente una vez:
    - provider_id + event_id es único (no puede haber duplicados)
    - Registra intento de reproceso
    - Permite retry con estado FAILED → PROCESSING
    """

    __tablename__ = "webhook_event_logs"

    # Campos principales
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "wompi", "truora", etc
    provider_event_id: Mapped[str] = mapped_column(String(256), nullable=False)  # ID del evento en el proveedor
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "transaction.updated", "kyc.verified", etc
    
    # Payload almacenado para auditoría y replay
    raw_payload: Mapped[str] = mapped_column(String(8192), nullable=False)  # JSON serializado
    
    # Seguimiento de procesamiento
    status: Mapped[WebhookEventStatusEnum] = mapped_column(
        SQLEnum(
            WebhookEventStatusEnum,
            name="webhookeventstatusenum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=WebhookEventStatusEnum.RECEIVED,
        index=True,
    )
    
    # Detalle de procesamiento
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv4 o IPv6
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    retry_count: Mapped[int] = mapped_column(BigInteger, default=0)
    related_transaction_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    
    # Timestamps
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Constraint: (provider, provider_event_id) debe ser único
    __table_args__ = (
        UniqueConstraint("provider", "provider_event_id", name="uc_webhook_provider_event_id"),
        Index("idx_webhook_status_received", "status", "received_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<WebhookEventLog provider={self.provider} event_id={self.provider_event_id} "
            f"status={self.status.value}>"
        )
