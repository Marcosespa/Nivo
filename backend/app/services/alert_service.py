"""Nivo — Alert Service: Slack notifications for critical webhook failures."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import httpx
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class AlertEvent(str, Enum):
    WEBHOOK_INVALID_SIGNATURE = "webhook_firma_invalida"
    WEBHOOK_PROCESSING_FAILED = "webhook_procesamiento_fallido"
    WEBHOOK_MAX_RETRIES = "webhook_max_reintentos"
    BALANCE_NOT_CREDITED = "saldo_no_acreditado_tras_pago"
    KYC_LOW_APPROVAL_RATE = "kyc_tasa_aprobacion_baja"
    GMV_ANOMALY = "gmv_caida_anomala"
    DAILY_METRICS_REPORT = "reporte_metricas_diario"


_SEVERITY_EMOJI = {"critical": "🔴", "high": "🟠", "medium": "🟡"}

_ALERT_CONFIG: dict[str, dict[str, str]] = {
    AlertEvent.WEBHOOK_INVALID_SIGNATURE: {
        "title": "Webhook con firma inválida",
        "severity": "high",
        "description": "Múltiples webhooks con firma SHA-256 inválida detectados.",
        "action": "Verificar WOMPI_EVENTS_SECRET en prod. Revisar IPs de origen en logs.",
    },
    AlertEvent.WEBHOOK_PROCESSING_FAILED: {
        "title": "Error procesando webhook",
        "severity": "critical",
        "description": "El procesamiento del webhook de Wompi está fallando repetidamente.",
        "action": "Revisar logs. Verificar conexión a BD. Chequear estructura del payload.",
    },
    AlertEvent.WEBHOOK_MAX_RETRIES: {
        "title": "Webhook alcanzó máximo de reintentos",
        "severity": "critical",
        "description": "Un webhook no pudo procesarse tras múltiples intentos.",
        "action": "Revisar webhook_event_logs. Puede requerirse procesamiento manual.",
    },
    AlertEvent.BALANCE_NOT_CREDITED: {
        "title": "Saldo no acreditado tras pago aprobado",
        "severity": "critical",
        "description": "Wompi aprobó el pago pero el saldo del usuario no se acreditó.",
        "action": "URGENTE: Revisar wallet del usuario. Verificar acreditación manual.",
    },
    AlertEvent.KYC_LOW_APPROVAL_RATE: {
        "title": "Tasa de aprobación KYC por debajo del 70%",
        "severity": "high",
        "description": "La tasa de aprobación KYC de las últimas 24h cayó por debajo del umbral.",
        "action": "Revisar rechazos recientes en kyc_funnel_events. Chequear estado de Truora API.",
    },
    AlertEvent.GMV_ANOMALY: {
        "title": "Caída anómala de GMV diario",
        "severity": "high",
        "description": "El GMV de hoy cayó más del 30% respecto al promedio de los últimos 7 días.",
        "action": "Revisar transacciones fallidas, estado de Wompi y errores en payment_gateway_service.",
    },
    AlertEvent.DAILY_METRICS_REPORT: {
        "title": "Reporte diario de métricas — Nivo",
        "severity": "medium",
        "description": "Resumen de métricas de negocio del día anterior.",
        "action": "Solo informativo.",
    },
}


class AlertService:
    """
    Tracks failure frequency per event type in Redis and sends Slack alerts
    when the threshold is exceeded.

    Rate limiting: max 1 alert of the same type every ALERT_RATE_LIMIT_SECONDS.
    Threshold: send alert after ALERT_FAILURE_THRESHOLD failures within
    ALERT_FAILURE_WINDOW_SECONDS.

    Never raises — designed to be called in exception handlers without risk.
    """

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    async def track_and_alert(
        self,
        event: AlertEvent,
        context: dict[str, Any],
        correlation_id: str | None = None,
    ) -> None:
        """Register a failure and alert Slack if the threshold is exceeded."""
        try:
            fail_key = f"nivo:alert:fail:{event.value}"
            count = await self._redis.incr(fail_key)
            if count == 1:
                await self._redis.expire(fail_key, settings.ALERT_FAILURE_WINDOW_SECONDS)

            logger.debug(
                "alert_tracker event=%s count=%d threshold=%d",
                event.value,
                count,
                settings.ALERT_FAILURE_THRESHOLD,
            )

            if count < settings.ALERT_FAILURE_THRESHOLD:
                return

            # One alert of the same type per rate-limit window
            ratelimit_key = f"nivo:alert:ratelimit:{event.value}"
            acquired = await self._redis.set(
                ratelimit_key, "1", nx=True, ex=settings.ALERT_RATE_LIMIT_SECONDS
            )
            if not acquired:
                return

            await self._send_slack(event, context, count, correlation_id)

        except Exception:
            logger.exception("AlertService.track_and_alert failed (silenced)")

    async def send_rate_alert(
        self,
        event: AlertEvent,
        context: dict[str, Any],
    ) -> None:
        """
        Sends an alert immediately (no count threshold) with rate limiting.
        Used for metric-based alerts where a single reading is enough to alert.
        """
        try:
            ratelimit_key = f"nivo:alert:ratelimit:{event.value}"
            acquired = await self._redis.set(
                ratelimit_key, "1", nx=True, ex=settings.ALERT_RATE_LIMIT_SECONDS
            )
            if not acquired:
                return
            await self._send_slack(event, context, count=1, correlation_id=None)
        except Exception:
            logger.exception("AlertService.send_rate_alert failed (silenced)")

    async def test_channel(self) -> bool:
        """Send a test message to Slack. Returns True if the channel responded 200."""
        if not settings.SLACK_WEBHOOK_URL:
            logger.warning("SLACK_WEBHOOK_URL not set — test skipped")
            return False

        payload = {
            "text": "✅ Canal de alertas Nivo activo",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "✅ *Test de canal de alertas — Nivo*\n"
                            f"Timestamp: `{datetime.now(timezone.utc).isoformat()}`\n"
                            f"Ambiente: `{settings.ENVIRONMENT}`\n\n"
                            "El canal #alertas-criticas está funcionando correctamente."
                        ),
                    },
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(settings.SLACK_WEBHOOK_URL, json=payload)
                ok = response.status_code == 200
                if not ok:
                    logger.error("Slack test HTTP %d: %s", response.status_code, response.text)
                return ok
        except Exception:
            logger.exception("Slack test_channel failed")
            return False

    async def _send_slack(
        self,
        event: AlertEvent,
        context: dict[str, Any],
        count: int,
        correlation_id: str | None,
    ) -> None:
        if not settings.SLACK_WEBHOOK_URL:
            logger.warning(
                "SLACK_WEBHOOK_URL not configured — alert dropped: %s (count=%d)",
                event.value,
                count,
            )
            return

        cfg = _ALERT_CONFIG.get(event, {})
        severity = cfg.get("severity", "high")
        emoji = _SEVERITY_EMOJI.get(severity, "⚠️")
        title = cfg.get("title", event.value)

        ctx_lines = "\n".join(
            f"• *{k}:* `{v}`" for k, v in context.items() if v is not None
        )
        if correlation_id:
            ctx_lines = f"• *correlation_id:* `{correlation_id}`\n" + ctx_lines

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        blocks: list[dict] = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{emoji} [{severity.upper()}] {title}"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Ambiente:*\n`{settings.ENVIRONMENT}`"},
                    {"type": "mrkdwn", "text": f"*Ocurrencias (ventana 10 min):*\n`{count}`"},
                    {"type": "mrkdwn", "text": f"*Timestamp:*\n`{ts}`"},
                    {"type": "mrkdwn", "text": f"*Evento:*\n`{event.value}`"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Descripción:*\n{cfg.get('description', '')}",
                },
            },
        ]

        if ctx_lines:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Contexto:*\n{ctx_lines}"},
                }
            )

        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Acción recomendada:*\n{cfg.get('action', 'Revisar logs.')}",
                },
            }
        )

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    settings.SLACK_WEBHOOK_URL,
                    json={"text": f"{emoji} [{severity.upper()}] {title}", "blocks": blocks},
                )
                if response.status_code == 200:
                    logger.info("Slack alert sent: %s (count=%d)", event.value, count)
                else:
                    logger.error(
                        "Slack alert failed HTTP %d: %s", response.status_code, response.text
                    )
        except Exception:
            logger.exception("Error sending Slack alert for %s", event.value)
