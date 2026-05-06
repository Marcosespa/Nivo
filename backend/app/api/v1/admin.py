"""
Nivo — Admin Router

Available only in development and staging (registered conditionally in main.py).

Endpoints:
  POST /api/v1/admin/alerts/test        — Verify Slack alert channel is active
  POST /api/v1/admin/metrics/snapshot   — Trigger daily metrics calculation
  GET  /api/v1/admin/metrics/daily      — Retrieve recent snapshots
  POST /api/v1/admin/metrics/report     — Send daily Slack report manually
  POST /api/v1/admin/b2b-clients        — Issue a new B2B API key
  GET  /api/v1/admin/b2b-clients        — List active B2B clients
"""

from __future__ import annotations
import hashlib
import secrets
from datetime import date
from typing import Annotated, Optional

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import get_db
from app.models.orm.b2b_client import B2BClient
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


# ─── B2B clients (issue/list API keys) ──────────────────────────────────────
#
# Registro de clientes B2B que consumen /api/v1/crypto. Sólo disponible en
# development/staging — en producción los keys deben emitirse vía panel admin
# autenticado o automatización con MFA, no por endpoint REST sin auth fuerte.

class CreateB2BClientRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)


class CreateB2BClientResponse(BaseModel):
    id: str
    name: str
    api_key: str  # Mostrado UNA SOLA VEZ — guardar en secret manager.
    api_key_hash_prefix: str  # Primeros 8 chars del hash (para confirmar después).
    is_active: bool


class B2BClientItem(BaseModel):
    id: str
    name: str
    api_key_hash_prefix: str
    is_active: bool
    created_at: str


@router.post(
    "/b2b-clients",
    response_model=CreateB2BClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Emitir API key B2B",
    description=(
        "Genera un API key aleatorio (48 bytes URL-safe) para un cliente B2B "
        "y persiste sólo el SHA-256. La key en claro se retorna UNA sola vez "
        "en esta respuesta — guárdala en un gestor de secretos."
    ),
)
async def create_b2b_client(
    body: CreateB2BClientRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CreateB2BClientResponse:
    api_key = secrets.token_urlsafe(48)
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    client = B2BClient(
        name=body.name,
        api_key_hash=api_key_hash,
        is_active=True,
    )
    db.add(client)
    try:
        await db.flush()
    except IntegrityError:
        # Colisión astronómicamente improbable, pero la manejamos.
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Colisión de API key, vuelve a intentar.",
        )
    await db.commit()

    return CreateB2BClientResponse(
        id=str(client.id),
        name=client.name,
        api_key=api_key,
        api_key_hash_prefix=api_key_hash[:8],
        is_active=client.is_active,
    )


@router.get(
    "/b2b-clients",
    summary="Listar clientes B2B",
    description="Retorna los clientes B2B registrados (sin exponer el hash completo).",
)
async def list_b2b_clients(
    db: Annotated[AsyncSession, Depends(get_db)],
    only_active: bool = Query(default=True),
) -> dict:
    stmt = select(B2BClient).order_by(B2BClient.created_at.desc())
    if only_active:
        stmt = stmt.where(B2BClient.is_active.is_(True))
    result = await db.execute(stmt)
    clients = result.scalars().all()
    return {
        "count": len(clients),
        "clients": [
            B2BClientItem(
                id=str(c.id),
                name=c.name,
                api_key_hash_prefix=c.api_key_hash[:8],
                is_active=c.is_active,
                created_at=c.created_at.isoformat(),
            ).model_dump()
            for c in clients
        ],
    }


@router.post(
    "/b2b-clients/{client_id}/deactivate",
    summary="Desactivar cliente B2B",
    description="Marca el cliente como inactivo. Las API keys dejan de validar.",
)
async def deactivate_b2b_client(
    client_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    import uuid as _uuid
    try:
        cid = _uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID inválido")

    client = await db.scalar(select(B2BClient).where(B2BClient.id == cid))
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    client.is_active = False
    await db.commit()
    return {"status": "deactivated", "id": str(client.id)}
