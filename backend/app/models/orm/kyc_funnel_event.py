"""Nivo — KYC Funnel Event ORM model (T-10: conversion analytics)."""

from __future__ import annotations
import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class KYCFunnelStepEnum(str, enum.Enum):
    REGISTERED = "registered"
    KYC_INITIATED = "kyc_initiated"
    KYC_RESULT = "kyc_result"
    FIRST_DEPOSIT = "first_deposit"


class KYCFunnelResultEnum(str, enum.Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class KYCFunnelEvent(Base):
    __tablename__ = "kyc_funnel_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    step: Mapped[KYCFunnelStepEnum] = mapped_column(
        sa.Enum(KYCFunnelStepEnum, name="kycfunnelstepenum"), nullable=False
    )
    result: Mapped[Optional[KYCFunnelResultEnum]] = mapped_column(
        sa.Enum(KYCFunnelResultEnum, name="kycfunnelresultenum"), nullable=True
    )
    failure_reason: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    elapsed_seconds: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.text("NOW()"),
    )

    __table_args__ = (
        sa.Index("ix_kyc_funnel_events_user_id", "user_id"),
        sa.Index("ix_kyc_funnel_events_step", "step"),
        sa.Index("ix_kyc_funnel_events_created_at", "created_at"),
    )
