"""
Nivo — Admin Router

Available only in development and staging (registered conditionally in main.py).

Endpoints:
  POST /api/v1/admin/alerts/test        — Verify Slack alert channel is active
  POST /api/v1/admin/metrics/snapshot   — Trigger daily metrics calculation
  GET  /api/v1/admin/metrics/daily      — Retrieve recent snapshots
  POST /api/v1/admin/metrics/report     — Send daily Slack report manually
"""

from __future__ import annotations
from datetime import date
from typing import Annotated, Optional

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.alert_service import AlertService, AlertEvent
from app.services.metrics_service import metrics_service

router = APIRouter()


async def get_redis() -> redis.Redis:
    return await redis.from_url(settings.REDIS_URL)


@router.post(
    "/alerts/test",
    summary="Verificar canal de alertas Slack",
    description=(
        "Envía un mensaje de prueba al canal #alertas-criticas. "
        "Solo disponible en desarrollo y staging."
    ),
)
async def test_alert_channel(
    redis_client: redis.Redis = Depends(get_redis),
) -> dict:
    """
    Verifica que el canal de Slack esté configurado y activo.
    Útil para confirmar la configuración antes de ir a producción.
    """
    svc = AlertService(redis_client)
    ok = await svc.test_channel()

    if ok:
        return {
            "status": "ok",
            "channel": "slack",
            "slack_url_configured": bool(settings.SLACK_WEBHOOK_URL),
            "message": "Mensaje de prueba enviado a #alertas-criticas.",
        }

    return {
        "status": "error",
        "channel": "slack",
        "slack_url_configured": bool(settings.SLACK_WEBHOOK_URL),
        "message": (
            "No se pudo enviar el mensaje. "
            "Verifica que SLACK_WEBHOOK_URL esté configurado."
        ),
    }


@router.post(
    "/metrics/snapshot",
    status_code=status.HTTP_200_OK,
    summary="Calcular snapshot de métricas",
    description=(
        "Dispara el cálculo y guardado del snapshot diario de métricas de negocio. "
        "Por defecto usa el día de ayer. Idempotente (upserta)."
    ),
)
async def trigger_metrics_snapshot(
    db: Annotated[AsyncSession, Depends(get_db)],
    snapshot_date: Optional[date] = Query(default=None, description="Fecha YYYY-MM-DD (default: ayer)"),
) -> dict:
    row = await metrics_service.calculate_and_save_daily_snapshot(db, snapshot_date)
    return {
        "status": "ok",
        "snapshot_date": row.snapshot_date.isoformat(),
        "gmv_cop": row.gmv_cop,
        "p2p_transactions": row.p2p_transactions,
        "new_users": row.new_users,
        "active_users": row.active_users,
        "kyc_approved": row.kyc_approved,
        "kyc_rejected": row.kyc_rejected,
        "calculated_at": row.calculated_at.isoformat(),
    }


@router.get(
    "/metrics/daily",
    status_code=status.HTTP_200_OK,
    summary="Obtener snapshots diarios recientes",
    description="Retorna los últimos N días de snapshots de métricas de negocio.",
)
async def get_daily_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(default=7, ge=1, le=90),
) -> dict:
    snapshots = await metrics_service.get_recent_snapshots(db, days=days)
    return {
        "period_days": days,
        "count": len(snapshots),
        "snapshots": [
            {
                "snapshot_date": s.snapshot_date.isoformat(),
                "gmv_cop": s.gmv_cop,
                "p2p_transactions": s.p2p_transactions,
                "topup_transactions": s.topup_transactions,
                "p2p_success_rate": s.p2p_success_rate,
                "new_users": s.new_users,
                "active_users": s.active_users,
                "kyc_approved": s.kyc_approved,
                "kyc_rejected": s.kyc_rejected,
                "otps_generated": s.otps_generated,
                "plan_free_users": s.plan_free_users,
                "plan_plus_users": s.plan_plus_users,
                "plan_pro_users": s.plan_pro_users,
                "calculated_at": s.calculated_at.isoformat(),
            }
            for s in snapshots
        ],
    }


@router.post(
    "/metrics/report",
    status_code=status.HTTP_200_OK,
    summary="Enviar reporte diario de métricas a Slack",
    description="Envía manualmente el reporte diario de métricas al canal de Slack.",
)
async def send_metrics_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> dict:
    ok = await metrics_service.send_daily_slack_report(db, redis_client)
    return {"status": "ok" if ok else "no_data", "sent": ok}
