"""Business metrics daily snapshot — T-13."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, Date, DateTime, Float, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BusinessMetricsDaily(Base):
    __tablename__ = "business_metrics_daily"
    __table_args__ = (UniqueConstraint("snapshot_date", name="uq_business_metrics_date"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Volume
    gmv_cop: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    p2p_transactions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    topup_transactions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    p2p_success_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Users
    new_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # KYC
    kyc_approved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    kyc_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Auth
    otps_generated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    otps_verified: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    otps_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Latencies (ms, from Redis samples — None when no payments that day)
    p2p_latency_p50_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    p2p_latency_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Plans (for MRR proxy)
    plan_free_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    plan_plus_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    plan_pro_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
