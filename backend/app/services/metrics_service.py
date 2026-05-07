"""Business metrics daily snapshot service — T-13."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

import redis.asyncio as redis
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.business_metrics_daily import BusinessMetricsDaily
from app.models.orm.transaction import Transaction, TransactionStatusEnum, SettlementRailEnum
from app.models.orm.user import User as UserORM, UserPlanEnum
from app.models.orm.kyc_funnel_event import KYCFunnelEvent, KYCFunnelStepEnum, KYCFunnelResultEnum
from app.models.orm.otp import OTP
from app.services.alert_service import AlertService, AlertEvent
from app.core.config import settings

logger = logging.getLogger(__name__)

GMV_ANOMALY_THRESHOLD = 0.30  # alert if current GMV drops >30% vs 7-day avg


class MetricsService:

    async def calculate_and_save_daily_snapshot(
        self,
        db: AsyncSession,
        snapshot_date: date | None = None,
        redis_client: redis.Redis | None = None,
    ) -> BusinessMetricsDaily:
        """
        Calculates all business metrics for `snapshot_date` (default: yesterday)
        and upserts a row in business_metrics_daily.
        """
        if snapshot_date is None:
            snapshot_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()

        day_start = datetime(
            snapshot_date.year, snapshot_date.month, snapshot_date.day,
            tzinfo=timezone.utc,
        )
        day_end = day_start + timedelta(days=1)

        # ── GMV: sum of COMPLETED transaction amounts ──────────────────────────
        gmv_result = await db.execute(
            select(func.coalesce(func.sum(Transaction.amount_cop), 0)).where(
                and_(
                    Transaction.status == TransactionStatusEnum.COMPLETED,
                    Transaction.created_at >= day_start,
                    Transaction.created_at < day_end,
                )
            )
        )
        gmv_cop: int = gmv_result.scalar_one()

        # ── P2P transactions (INTERNAL rail) ───────────────────────────────────
        p2p_total_result = await db.execute(
            select(func.count()).where(
                and_(
                    Transaction.rail == SettlementRailEnum.INTERNAL,
                    Transaction.created_at >= day_start,
                    Transaction.created_at < day_end,
                )
            )
        )
        p2p_total: int = p2p_total_result.scalar_one()

        p2p_ok_result = await db.execute(
            select(func.count()).where(
                and_(
                    Transaction.rail == SettlementRailEnum.INTERNAL,
                    Transaction.status == TransactionStatusEnum.COMPLETED,
                    Transaction.created_at >= day_start,
                    Transaction.created_at < day_end,
                )
            )
        )
        p2p_ok: int = p2p_ok_result.scalar_one()
        p2p_success_rate = (p2p_ok / p2p_total) if p2p_total > 0 else 0.0

        # ── Top-up transactions (PSE / ACH rails) ─────────────────────────────
        topup_result = await db.execute(
            select(func.count()).where(
                and_(
                    Transaction.rail.in_([SettlementRailEnum.PSE, SettlementRailEnum.ACH]),
                    Transaction.status == TransactionStatusEnum.COMPLETED,
                    Transaction.created_at >= day_start,
                    Transaction.created_at < day_end,
                )
            )
        )
        topup_transactions: int = topup_result.scalar_one()

        # ── New users registered that day ──────────────────────────────────────
        new_users_result = await db.execute(
            select(func.count()).where(
                and_(
                    UserORM.created_at >= day_start,
                    UserORM.created_at < day_end,
                )
            )
        )
        new_users: int = new_users_result.scalar_one()

        # ── Active users: distinct senders with a COMPLETED tx that day ────────
        active_result = await db.execute(
            select(func.count(func.distinct(Transaction.sender_id))).where(
                and_(
                    Transaction.status == TransactionStatusEnum.COMPLETED,
                    Transaction.created_at >= day_start,
                    Transaction.created_at < day_end,
                )
            )
        )
        active_users: int = active_result.scalar_one()

        # ── KYC funnel results that day ────────────────────────────────────────
        kyc_approved_result = await db.execute(
            select(func.count()).where(
                and_(
                    KYCFunnelEvent.step == KYCFunnelStepEnum.KYC_RESULT,
                    KYCFunnelEvent.result == KYCFunnelResultEnum.COMPLETED,
                    KYCFunnelEvent.created_at >= day_start,
                    KYCFunnelEvent.created_at < day_end,
                )
            )
        )
        kyc_approved: int = kyc_approved_result.scalar_one()

        kyc_rejected_result = await db.execute(
            select(func.count()).where(
                and_(
                    KYCFunnelEvent.step == KYCFunnelStepEnum.KYC_RESULT,
                    KYCFunnelEvent.result == KYCFunnelResultEnum.FAILED,
                    KYCFunnelEvent.created_at >= day_start,
                    KYCFunnelEvent.created_at < day_end,
                )
            )
        )
        kyc_rejected: int = kyc_rejected_result.scalar_one()

        # ── OTPs: Redis counters (source of truth); DB table is audit-only ────
        date_str = snapshot_date.strftime("%Y%m%d")
        if redis_client is not None:
            _gen = await redis_client.get(f"metrics:otp:gen:{date_str}")
            _ok = await redis_client.get(f"metrics:otp:ok:{date_str}")
            _fail = await redis_client.get(f"metrics:otp:fail:{date_str}")
            otps_generated: int = int(_gen or 0)
            otps_verified: int = int(_ok or 0)
            otps_failed: int = int(_fail or 0)
        else:
            otps_result = await db.execute(
                select(func.count()).where(
                    and_(
                        OTP.created_at >= day_start,
                        OTP.created_at < day_end,
                    )
                )
            )
            otps_generated = otps_result.scalar_one()
            otps_verified = 0
            otps_failed = 0

        # ── P2P latency percentiles from Redis samples ─────────────────────────
        p2p_latency_p50_ms: float | None = None
        p2p_latency_p95_ms: float | None = None
        if redis_client is not None:
            raw = await redis_client.lrange(f"metrics:latency:p2p:{date_str}", 0, -1)
            if raw:
                latencies = sorted(float(v) for v in raw)
                n = len(latencies)
                p2p_latency_p50_ms = latencies[int(n * 0.50)]
                p2p_latency_p95_ms = latencies[min(int(n * 0.95), n - 1)]

        # ── Plan distribution snapshot (current totals) ────────────────────────
        async def _count_plan(plan: UserPlanEnum) -> int:
            r = await db.execute(
                select(func.count()).where(
                    and_(UserORM.plan == plan, UserORM.is_active.is_(True))
                )
            )
            return r.scalar_one()

        plan_free_users = await _count_plan(UserPlanEnum.FREE)
        plan_plus_users = await _count_plan(UserPlanEnum.PLUS)
        plan_pro_users = await _count_plan(UserPlanEnum.PRO)

        # ── Upsert ─────────────────────────────────────────────────────────────
        existing = await db.execute(
            select(BusinessMetricsDaily).where(
                BusinessMetricsDaily.snapshot_date == snapshot_date
            )
        )
        row = existing.scalar_one_or_none()

        if row is None:
            row = BusinessMetricsDaily(snapshot_date=snapshot_date)
            db.add(row)

        row.gmv_cop = gmv_cop
        row.p2p_transactions = p2p_total
        row.topup_transactions = topup_transactions
        row.p2p_success_rate = p2p_success_rate
        row.new_users = new_users
        row.active_users = active_users
        row.kyc_approved = kyc_approved
        row.kyc_rejected = kyc_rejected
        row.otps_generated = otps_generated
        row.otps_verified = otps_verified
        row.otps_failed = otps_failed
        row.p2p_latency_p50_ms = p2p_latency_p50_ms
        row.p2p_latency_p95_ms = p2p_latency_p95_ms
        row.plan_free_users = plan_free_users
        row.plan_plus_users = plan_plus_users
        row.plan_pro_users = plan_pro_users
        row.calculated_at = datetime.now(timezone.utc)

        await db.flush()
        return row

    async def get_recent_snapshots(
        self, db: AsyncSession, days: int = 7
    ) -> list[BusinessMetricsDaily]:
        """Returns the last `days` snapshots ordered newest-first."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date()
        result = await db.execute(
            select(BusinessMetricsDaily)
            .where(BusinessMetricsDaily.snapshot_date >= cutoff)
            .order_by(BusinessMetricsDaily.snapshot_date.desc())
        )
        return list(result.scalars().all())

    async def check_gmv_anomaly(self, db: AsyncSession) -> tuple[bool, dict[str, Any]]:
        """
        Returns (is_anomaly, context_dict).
        Anomaly = today's GMV is >30% below the 7-day average (excl. today).
        """
        today = datetime.now(timezone.utc).date()
        snapshots = await self.get_recent_snapshots(db, days=8)

        today_row = next((s for s in snapshots if s.snapshot_date == today), None)
        past_rows = [s for s in snapshots if s.snapshot_date != today]

        if today_row is None or len(past_rows) == 0:
            return False, {}

        avg_gmv = sum(s.gmv_cop for s in past_rows) / len(past_rows)
        if avg_gmv == 0:
            return False, {}

        drop = (avg_gmv - today_row.gmv_cop) / avg_gmv
        is_anomaly = drop > GMV_ANOMALY_THRESHOLD

        context = {
            "gmv_hoy": f"${today_row.gmv_cop / 100:,.0f} COP",
            "promedio_7d": f"${avg_gmv / 100:,.0f} COP",
            "caida": f"{drop:.1%}",
            "umbral": f"{GMV_ANOMALY_THRESHOLD:.0%}",
        }
        return is_anomaly, context

    async def send_daily_slack_report(
        self, db: AsyncSession, redis_client: redis.Redis
    ) -> bool:
        """
        Sends a daily business metrics summary to Slack with 5 key metrics.
        Returns True if sent successfully.
        """
        snapshots = await self.get_recent_snapshots(db, days=8)
        if not snapshots:
            logger.warning("metrics_service: no snapshots for daily report")
            return False

        today = snapshots[0]
        past = snapshots[1:]
        avg_gmv = (sum(s.gmv_cop for s in past) / len(past)) if past else 0

        kyc_total = today.kyc_approved + today.kyc_rejected
        kyc_rate = (today.kyc_approved / kyc_total) if kyc_total > 0 else None
        gmv_vs_avg = (
            ((today.gmv_cop - avg_gmv) / avg_gmv * 100) if avg_gmv > 0 else None
        )

        context = {
            "gmv_cop": f"${today.gmv_cop / 100:,.0f}",
            "p2p_transacciones": str(today.p2p_transactions),
            "nuevos_usuarios": str(today.new_users),
            "tasa_kyc": f"{kyc_rate:.1%}" if kyc_rate is not None else "N/A",
            "usuarios_activos": str(today.active_users),
        }

        if gmv_vs_avg is not None:
            sign = "+" if gmv_vs_avg >= 0 else ""
            context["gmv_vs_7d_avg"] = f"{sign}{gmv_vs_avg:.1f}%"

        await AlertService(redis_client).send_rate_alert(
            AlertEvent.DAILY_METRICS_REPORT, context
        )
        return True


metrics_service = MetricsService()
