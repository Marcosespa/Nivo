"""Tests para Business Metrics (T-13): snapshots, anomalías y endpoints admin."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.business_metrics_daily import BusinessMetricsDaily
from app.models.orm.transaction import Transaction, TransactionStatusEnum, SettlementRailEnum
from app.models.orm.user import User as UserORM, UserPlanEnum, KYCStatusEnum
from app.models.orm.wallet import Wallet as WalletORM
from app.services.metrics_service import MetricsService, GMV_ANOMALY_THRESHOLD


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _make_user(db: AsyncSession, plan: UserPlanEnum = UserPlanEnum.FREE) -> UserORM:
    user = UserORM(
        phone_number=f"+57{uuid.uuid4().int % 10_000_000_000:010d}",
        plan=plan,
        kyc_status=KYCStatusEnum.PENDING,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    db.add(WalletORM(user_id=user.id, display_balance_cop=0))
    await db.flush()
    return user


async def _make_tx(
    db: AsyncSession,
    sender_id: uuid.UUID,
    receiver_id: uuid.UUID,
    amount_cop: int = 100_000,
    status: TransactionStatusEnum = TransactionStatusEnum.COMPLETED,
    rail: SettlementRailEnum = SettlementRailEnum.INTERNAL,
    created_at: datetime | None = None,
) -> Transaction:
    tx = Transaction(
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount_cop=amount_cop,
        status=status,
        rail=rail,
        created_at=created_at or datetime.now(timezone.utc),
    )
    db.add(tx)
    await db.flush()
    return tx


# ─── Unit tests: MetricsService ──────────────────────────────────────────────

class TestMetricsServiceSnapshot:
    async def test_snapshot_empty_db_returns_zeros(self, db_session: AsyncSession):
        svc = MetricsService()
        today = datetime.now(timezone.utc).date()
        row = await svc.calculate_and_save_daily_snapshot(db_session, snapshot_date=today)
        await db_session.commit()

        assert row.snapshot_date == today
        assert row.gmv_cop == 0
        assert row.p2p_transactions == 0
        assert row.new_users == 0

    async def test_snapshot_counts_completed_p2p_gmv(self, db_session: AsyncSession):
        u1 = await _make_user(db_session)
        u2 = await _make_user(db_session)
        await _make_tx(db_session, u1.id, u2.id, amount_cop=50_000_00)
        await _make_tx(db_session, u2.id, u1.id, amount_cop=30_000_00)
        await db_session.commit()

        svc = MetricsService()
        today = datetime.now(timezone.utc).date()
        row = await svc.calculate_and_save_daily_snapshot(db_session, snapshot_date=today)
        await db_session.commit()

        assert row.gmv_cop == 80_000_00
        assert row.p2p_transactions == 2
        assert row.p2p_success_rate == 1.0

    async def test_snapshot_excludes_failed_from_gmv(self, db_session: AsyncSession):
        u1 = await _make_user(db_session)
        u2 = await _make_user(db_session)
        await _make_tx(db_session, u1.id, u2.id, amount_cop=100_000_00)
        await _make_tx(
            db_session, u1.id, u2.id, amount_cop=50_000_00,
            status=TransactionStatusEnum.FAILED,
        )
        await db_session.commit()

        svc = MetricsService()
        today = datetime.now(timezone.utc).date()
        row = await svc.calculate_and_save_daily_snapshot(db_session, snapshot_date=today)
        await db_session.commit()

        assert row.gmv_cop == 100_000_00
        assert row.p2p_transactions == 2
        assert round(row.p2p_success_rate, 2) == 0.5

    async def test_snapshot_upserts_on_recalculate(self, db_session: AsyncSession):
        svc = MetricsService()
        today = datetime.now(timezone.utc).date()

        row1 = await svc.calculate_and_save_daily_snapshot(db_session, snapshot_date=today)
        await db_session.commit()
        row_id = row1.id

        u1 = await _make_user(db_session)
        u2 = await _make_user(db_session)
        await _make_tx(db_session, u1.id, u2.id, amount_cop=10_000_00)
        await db_session.commit()

        row2 = await svc.calculate_and_save_daily_snapshot(db_session, snapshot_date=today)
        await db_session.commit()

        assert row2.id == row_id  # same row updated
        assert row2.gmv_cop == 10_000_00

    async def test_snapshot_counts_plan_distribution(self, db_session: AsyncSession):
        await _make_user(db_session, UserPlanEnum.FREE)
        await _make_user(db_session, UserPlanEnum.FREE)
        await _make_user(db_session, UserPlanEnum.PLUS)
        await _make_user(db_session, UserPlanEnum.PRO)
        await db_session.commit()

        svc = MetricsService()
        today = datetime.now(timezone.utc).date()
        row = await svc.calculate_and_save_daily_snapshot(db_session, snapshot_date=today)

        assert row.plan_free_users == 2
        assert row.plan_plus_users == 1
        assert row.plan_pro_users == 1

    async def test_snapshot_counts_topup_transactions(self, db_session: AsyncSession):
        u1 = await _make_user(db_session)
        u2 = await _make_user(db_session)
        await _make_tx(
            db_session, u1.id, u2.id, amount_cop=200_000_00, rail=SettlementRailEnum.PSE
        )
        await db_session.commit()

        svc = MetricsService()
        today = datetime.now(timezone.utc).date()
        row = await svc.calculate_and_save_daily_snapshot(db_session, snapshot_date=today)

        assert row.topup_transactions == 1
        assert row.p2p_transactions == 0


class TestGMVAnomaly:
    async def _seed_snapshots(
        self, db: AsyncSession, gmv_values: list[int], start_date: date | None = None
    ) -> None:
        base = start_date or datetime.now(timezone.utc).date()
        for i, gmv in enumerate(gmv_values):
            d = base - timedelta(days=len(gmv_values) - 1 - i)
            existing = BusinessMetricsDaily(snapshot_date=d, gmv_cop=gmv)
            db.add(existing)
        await db.commit()

    async def test_no_anomaly_when_gmv_stable(self, db_session: AsyncSession):
        svc = MetricsService()
        today = datetime.now(timezone.utc).date()
        # 7 past days at 1M, today at 950k — within 30%
        gmv_past = [100_000_00] * 7
        await self._seed_snapshots(db_session, gmv_past, start_date=today - timedelta(days=1))
        today_row = BusinessMetricsDaily(snapshot_date=today, gmv_cop=95_000_00)
        db_session.add(today_row)
        await db_session.commit()

        is_anomaly, _ = await svc.check_gmv_anomaly(db_session)
        assert is_anomaly is False

    async def test_anomaly_detected_when_gmv_drops_over_threshold(self, db_session: AsyncSession):
        svc = MetricsService()
        today = datetime.now(timezone.utc).date()
        gmv_past = [100_000_00] * 7
        await self._seed_snapshots(db_session, gmv_past, start_date=today - timedelta(days=1))
        # 60% drop — above 30% threshold
        today_row = BusinessMetricsDaily(snapshot_date=today, gmv_cop=40_000_00)
        db_session.add(today_row)
        await db_session.commit()

        is_anomaly, context = await svc.check_gmv_anomaly(db_session)
        assert is_anomaly is True
        assert "caida" in context
        assert "gmv_hoy" in context

    async def test_no_anomaly_when_no_today_snapshot(self, db_session: AsyncSession):
        svc = MetricsService()
        is_anomaly, _ = await svc.check_gmv_anomaly(db_session)
        assert is_anomaly is False


# ─── Integration tests: Admin endpoints ──────────────────────────────────────

class TestAdminMetricsEndpoints:
    async def test_snapshot_endpoint_returns_ok(self, client: AsyncClient, db_session: AsyncSession):
        resp = await client.post("/api/v1/admin/metrics/snapshot")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "snapshot_date" in data
        assert "gmv_cop" in data

    async def test_snapshot_endpoint_accepts_date_param(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        resp = await client.post("/api/v1/admin/metrics/snapshot?snapshot_date=2026-01-15")
        assert resp.status_code == 200
        data = resp.json()
        assert data["snapshot_date"] == "2026-01-15"

    async def test_daily_metrics_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        # Seed a snapshot first
        await client.post("/api/v1/admin/metrics/snapshot")

        resp = await client.get("/api/v1/admin/metrics/daily")
        assert resp.status_code == 200
        data = resp.json()
        assert "snapshots" in data
        assert "period_days" in data
        assert data["period_days"] == 7

    async def test_daily_metrics_days_param(self, client: AsyncClient, db_session: AsyncSession):
        resp = await client.get("/api/v1/admin/metrics/daily?days=30")
        assert resp.status_code == 200
        assert resp.json()["period_days"] == 30

    async def test_report_endpoint_no_data(self, client: AsyncClient, db_session: AsyncSession):
        resp = await client.post("/api/v1/admin/metrics/report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["sent"] is False
        assert data["status"] == "no_data"

    async def test_report_endpoint_with_data(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        # Seed a snapshot so the report has data
        await client.post("/api/v1/admin/metrics/snapshot")

        with patch("app.services.alert_service.AlertService._send_slack", new_callable=AsyncMock):
            resp = await client.post("/api/v1/admin/metrics/report")

        assert resp.status_code == 200
