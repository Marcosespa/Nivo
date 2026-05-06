"""Tests para KYC Funnel (T-10): conversión, alertas y endpoint /kyc/funnel."""

from __future__ import annotations
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.kyc_funnel_event import KYCFunnelEvent, KYCFunnelStepEnum, KYCFunnelResultEnum
from app.models.orm.user import User as UserORM, UserPlanEnum, KYCStatusEnum
from app.models.orm.wallet import Wallet as WalletORM
from app.services.kyc_funnel_service import KYCFunnelService, KYC_ALERT_THRESHOLD


# ─── Unit tests: KYCFunnelService ────────────────────────────────────────────

class TestKYCFunnelServiceTrack:
    async def test_track_creates_event(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        svc = KYCFunnelService()
        await svc.track(db_session, user_id, KYCFunnelStepEnum.REGISTERED)
        await db_session.commit()

        from sqlalchemy import select
        stmt = select(KYCFunnelEvent).where(KYCFunnelEvent.user_id == user_id)
        result = (await db_session.execute(stmt)).scalar_one()
        assert result.step == KYCFunnelStepEnum.REGISTERED
        assert result.result is None
        assert result.elapsed_seconds is None  # first event has no previous

    async def test_track_calculates_elapsed_from_previous(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        svc = KYCFunnelService()
        await svc.track(db_session, user_id, KYCFunnelStepEnum.REGISTERED)
        await svc.track(db_session, user_id, KYCFunnelStepEnum.KYC_INITIATED)
        await db_session.commit()

        from sqlalchemy import select
        stmt = (
            select(KYCFunnelEvent)
            .where(KYCFunnelEvent.user_id == user_id)
            .order_by(KYCFunnelEvent.created_at)
        )
        events = (await db_session.execute(stmt)).scalars().all()
        assert events[0].elapsed_seconds is None
        assert events[1].elapsed_seconds is not None
        assert events[1].elapsed_seconds >= 0

    async def test_track_stores_result_and_failure_reason(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        svc = KYCFunnelService()
        await svc.track(
            db_session, user_id, KYCFunnelStepEnum.KYC_RESULT,
            result=KYCFunnelResultEnum.FAILED,
            failure_reason="liveness_fail",
        )
        await db_session.commit()

        from sqlalchemy import select
        event = (await db_session.execute(
            select(KYCFunnelEvent).where(KYCFunnelEvent.user_id == user_id)
        )).scalar_one()
        assert event.result == KYCFunnelResultEnum.FAILED
        assert event.failure_reason == "liveness_fail"


class TestKYCFunnelStats:
    async def _seed(self, db: AsyncSession, svc: KYCFunnelService, n_approved: int, n_rejected: int):
        for _ in range(n_approved):
            uid = uuid.uuid4()
            await svc.track(db, uid, KYCFunnelStepEnum.REGISTERED)
            await svc.track(db, uid, KYCFunnelStepEnum.KYC_INITIATED)
            await svc.track(db, uid, KYCFunnelStepEnum.KYC_RESULT, result=KYCFunnelResultEnum.COMPLETED)
        for _ in range(n_rejected):
            uid = uuid.uuid4()
            await svc.track(db, uid, KYCFunnelStepEnum.REGISTERED)
            await svc.track(db, uid, KYCFunnelStepEnum.KYC_RESULT, result=KYCFunnelResultEnum.FAILED)
        await db.commit()

    async def test_funnel_stats_counts_correctly(self, db_session: AsyncSession):
        svc = KYCFunnelService()
        await self._seed(db_session, svc, n_approved=3, n_rejected=1)

        stats = await svc.get_funnel_stats(db_session, days=1)
        funnel = {step["step"]: step for step in stats["funnel"]}

        assert funnel[KYCFunnelStepEnum.REGISTERED]["users"] == 4
        assert funnel[KYCFunnelStepEnum.KYC_INITIATED]["users"] == 3
        assert funnel[KYCFunnelStepEnum.KYC_RESULT]["kyc_approved"] == 3
        assert funnel[KYCFunnelStepEnum.KYC_RESULT]["kyc_rejected"] == 1
        assert funnel[KYCFunnelStepEnum.KYC_RESULT]["kyc_approval_rate"] == 0.75

    async def test_alert_flag_set_when_rate_below_threshold(self, db_session: AsyncSession):
        svc = KYCFunnelService()
        # 2 approved, 8 rejected → 20% approval
        await self._seed(db_session, svc, n_approved=2, n_rejected=8)

        stats = await svc.get_funnel_stats(db_session, days=1)
        assert stats["alert_low_kyc_rate"] is True

    async def test_alert_flag_not_set_above_threshold(self, db_session: AsyncSession):
        svc = KYCFunnelService()
        await self._seed(db_session, svc, n_approved=8, n_rejected=2)

        stats = await svc.get_funnel_stats(db_session, days=1)
        assert stats["alert_low_kyc_rate"] is False

    async def test_alert_flag_not_set_below_min_sample(self, db_session: AsyncSession):
        svc = KYCFunnelService()
        # Only 1 rejected — below KYC_ALERT_MIN_SAMPLE
        uid = uuid.uuid4()
        await svc.track(db_session, uid, KYCFunnelStepEnum.KYC_RESULT, result=KYCFunnelResultEnum.FAILED)
        await db_session.commit()

        stats = await svc.get_funnel_stats(db_session, days=1)
        assert stats["alert_low_kyc_rate"] is False

    async def test_conversion_rates_calculated(self, db_session: AsyncSession):
        svc = KYCFunnelService()
        await self._seed(db_session, svc, n_approved=5, n_rejected=0)

        stats = await svc.get_funnel_stats(db_session, days=1)
        funnel = {step["step"]: step for step in stats["funnel"]}

        assert funnel[KYCFunnelStepEnum.REGISTERED]["conversion_from_registered"] == 1.0
        assert funnel[KYCFunnelStepEnum.KYC_INITIATED]["conversion_from_registered"] == 1.0
        assert funnel[KYCFunnelStepEnum.KYC_RESULT]["conversion_from_registered"] == 1.0


# ─── Integration tests: GET /api/v1/kyc/funnel ───────────────────────────────

class TestKYCFunnelEndpoint:
    async def _get_auth_token(self, client: AsyncClient, db_session: AsyncSession) -> str:
        from app.models.orm.pqc_key import PQCKey as PQCKeyORM
        from app.core.security import create_access_token

        user = UserORM(
            phone_number="+573001234567",
            plan=UserPlanEnum.FREE,
            kyc_status=KYCStatusEnum.PENDING,
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
        db_session.add(WalletORM(user_id=user.id, display_balance_cop=0))
        db_session.add(PQCKeyORM(
            user_id=user.id,
            algorithm="ML-DSA-65",
            public_key=b"pk-" + uuid.uuid4().bytes,
            key_fingerprint=uuid.uuid4().hex * 2,
            is_active=True,
        ))
        await db_session.commit()
        await db_session.refresh(user)
        return create_access_token(user_id=user.id, phone_number=user.phone_number, plan="free")

    async def test_funnel_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/kyc/funnel")
        assert resp.status_code in {401, 403}

    async def test_funnel_returns_stats(self, client: AsyncClient, db_session: AsyncSession):
        token = await self._get_auth_token(client, db_session)
        resp = await client.get(
            "/api/v1/kyc/funnel",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "funnel" in data
        assert "period_days" in data
        assert len(data["funnel"]) == 4  # 4 steps

    async def test_funnel_days_param_validated(self, client: AsyncClient, db_session: AsyncSession):
        token = await self._get_auth_token(client, db_session)
        resp = await client.get(
            "/api/v1/kyc/funnel?days=0",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400


# ─── Integration: REGISTERED tracked via verify-otp ─────────────────────────

class TestFunnelRegisteredTracked:
    async def test_new_user_registration_creates_funnel_event(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        from sqlalchemy import select

        with patch("app.services.sms_service.SMSService.send_otp", new_callable=AsyncMock, return_value=True):
            otp_resp = await client.post(
                "/api/v1/auth/request-otp",
                json={"phone_number": "+573009999001"},
            )
        assert otp_resp.status_code == 200
        otp_code = otp_resp.json().get("dev_otp")
        if otp_code is None:
            pytest.skip("dev_otp not available outside localhost")

        with patch("app.services.sms_service.SMSService.send_otp", new_callable=AsyncMock, return_value=True):
            verify_resp = await client.post(
                "/api/v1/auth/verify-otp",
                json={
                    "phone_number": "+573009999001",
                    "otp_code": otp_code,
                    "device_id": "test-device",
                },
            )
        assert verify_resp.status_code == 200
        assert verify_resp.json()["is_new_user"] is True

        stmt = select(KYCFunnelEvent).where(KYCFunnelEvent.step == KYCFunnelStepEnum.REGISTERED)
        events = (await db_session.execute(stmt)).scalars().all()
        assert len(events) == 1
