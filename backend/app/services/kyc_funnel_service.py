"""Nivo — KYC Funnel Service (T-10: conversion analytics)."""

from __future__ import annotations
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.orm.kyc_funnel_event import (
    KYCFunnelEvent,
    KYCFunnelStepEnum,
    KYCFunnelResultEnum,
)

logger = logging.getLogger(__name__)

KYC_ALERT_THRESHOLD = 0.70   # Fire alert when approval rate < 70 %
KYC_ALERT_MIN_SAMPLE = 5     # Skip alert if fewer than 5 results (avoid noise)


class KYCFunnelService:
    """Tracks KYC funnel steps and exposes conversion analytics."""

    async def track(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        step: KYCFunnelStepEnum,
        result: Optional[KYCFunnelResultEnum] = None,
        failure_reason: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Records a funnel step. Calculates elapsed seconds from the previous step."""
        elapsed: Optional[int] = None
        try:
            prev_stmt = (
                select(KYCFunnelEvent)
                .where(KYCFunnelEvent.user_id == user_id)
                .order_by(KYCFunnelEvent.created_at.desc())
                .limit(1)
            )
            prev = (await db.execute(prev_stmt)).scalar_one_or_none()
            if prev:
                now = datetime.now(timezone.utc)
                prev_ts = prev.created_at
                if prev_ts.tzinfo is None:
                    prev_ts = prev_ts.replace(tzinfo=timezone.utc)
                elapsed = max(0, int((now - prev_ts).total_seconds()))
        except Exception as exc:
            logger.warning("Could not calculate elapsed for funnel event: %s", exc)

        db.add(KYCFunnelEvent(
            user_id=user_id,
            step=step,
            result=result,
            failure_reason=failure_reason,
            session_id=session_id,
            elapsed_seconds=elapsed,
        ))
        await db.flush()

    async def get_funnel_stats(self, db: AsyncSession, days: int = 1) -> dict:
        """
        Conversion rates per step for the last N days.
        Counts are de-duped by distinct user_id.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Users per step
        step_stmt = (
            select(
                KYCFunnelEvent.step,
                func.count(KYCFunnelEvent.user_id.distinct()).label("users"),
            )
            .where(KYCFunnelEvent.created_at >= since)
            .group_by(KYCFunnelEvent.step)
        )
        counts: dict = {row.step: row.users for row in (await db.execute(step_stmt)).all()}

        # KYC approval breakdown
        kyc_stmt = (
            select(
                KYCFunnelEvent.result,
                func.count(KYCFunnelEvent.user_id.distinct()).label("users"),
            )
            .where(
                KYCFunnelEvent.step == KYCFunnelStepEnum.KYC_RESULT,
                KYCFunnelEvent.created_at >= since,
            )
            .group_by(KYCFunnelEvent.result)
        )
        kyc_counts: dict = {row.result: row.users for row in (await db.execute(kyc_stmt)).all()}
        approved = kyc_counts.get(KYCFunnelResultEnum.COMPLETED, 0)
        rejected = kyc_counts.get(KYCFunnelResultEnum.FAILED, 0)
        total_results = approved + rejected
        kyc_rate = round(approved / total_results, 4) if total_results > 0 else None

        registered = counts.get(KYCFunnelStepEnum.REGISTERED, 0)

        def conv(step: KYCFunnelStepEnum) -> Optional[float]:
            return round(counts.get(step, 0) / registered, 4) if registered > 0 else None

        return {
            "period_days": days,
            "funnel": [
                {
                    "step": KYCFunnelStepEnum.REGISTERED,
                    "users": registered,
                    "conversion_from_registered": 1.0 if registered > 0 else None,
                },
                {
                    "step": KYCFunnelStepEnum.KYC_INITIATED,
                    "users": counts.get(KYCFunnelStepEnum.KYC_INITIATED, 0),
                    "conversion_from_registered": conv(KYCFunnelStepEnum.KYC_INITIATED),
                },
                {
                    "step": KYCFunnelStepEnum.KYC_RESULT,
                    "users": counts.get(KYCFunnelStepEnum.KYC_RESULT, 0),
                    "conversion_from_registered": conv(KYCFunnelStepEnum.KYC_RESULT),
                    "kyc_approval_rate": kyc_rate,
                    "kyc_approved": approved,
                    "kyc_rejected": rejected,
                },
                {
                    "step": KYCFunnelStepEnum.FIRST_DEPOSIT,
                    "users": counts.get(KYCFunnelStepEnum.FIRST_DEPOSIT, 0),
                    "conversion_from_registered": conv(KYCFunnelStepEnum.FIRST_DEPOSIT),
                },
            ],
            "alert_low_kyc_rate": (
                kyc_rate is not None
                and total_results >= KYC_ALERT_MIN_SAMPLE
                and kyc_rate < KYC_ALERT_THRESHOLD
            ),
        }

    async def get_kyc_approval_rate_24h(
        self, db: AsyncSession
    ) -> tuple[float | None, int]:
        """Returns (approval_rate, sample_size) for the last 24 hours."""
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        stmt = (
            select(
                KYCFunnelEvent.result,
                func.count().label("n"),
            )
            .where(
                KYCFunnelEvent.step == KYCFunnelStepEnum.KYC_RESULT,
                KYCFunnelEvent.created_at >= since,
            )
            .group_by(KYCFunnelEvent.result)
        )
        rows = (await db.execute(stmt)).all()
        counts = {row.result: row.n for row in rows}
        approved = counts.get(KYCFunnelResultEnum.COMPLETED, 0)
        total = approved + counts.get(KYCFunnelResultEnum.FAILED, 0)
        return (approved / total, total) if total > 0 else (None, 0)


kyc_funnel_service = KYCFunnelService()
