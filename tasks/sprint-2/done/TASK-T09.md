# T-09 — Canal de alertas para webhooks fallidos
**Estado:** [x] DONE
**Sprint:** 2 (P2 — Mejoras)
**Fecha:** 2026-05-04

## Qué se hizo

**Archivos creados:**
- `backend/app/services/alert_service.py` — `AlertService` con tracking de fallos en Redis y envío a Slack

**Archivos modificados:**
- `backend/app/core/config.py` — 4 nuevas settings: `SLACK_WEBHOOK_URL`, `ALERT_FAILURE_THRESHOLD` (3), `ALERT_FAILURE_WINDOW_SECONDS` (600), `ALERT_RATE_LIMIT_SECONDS` (300)
- `backend/app/api/v1/topup.py` — inyección de Redis en `/webhook`, llamadas a `AlertService` en los except
- `backend/app/main.py` — registro del router `admin` en dev/staging
- `backend/app/api/v1/admin.py` — endpoint `POST /api/v1/admin/alerts/test`
- `backend/.env.example` — variables de alerta documentadas

## Diseño

**Tracking de fallos (Redis):**
- Key `nivo:alert:fail:{event}` — INCR con TTL de 10 minutos (ventana deslizante)
- Al superar `ALERT_FAILURE_THRESHOLD` (3 fallos), intenta adquirir key de rate-limit
- Key `nivo:alert:ratelimit:{event}` — SET NX con TTL de 5 minutos → solo 1 alerta por tipo cada 5 min

**Catálogo de eventos (`AlertEvent`):**
- `webhook_firma_invalida` — firma SHA-256 incorrecta (severity: high)
- `webhook_procesamiento_fallido` — excepción en `process_webhook` (severity: critical)
- `webhook_max_reintentos` — webhook en estado FAILED tras retry_count alto (severity: critical)
- `saldo_no_acreditado_tras_pago` — para uso futuro en acreditación (severity: critical)

**Slack Block Kit:** header con emoji semáforo + campos: ambiente, ocurrencias, timestamp, evento, descripción, contexto (IP, wompi_tx_id), acción recomendada.

**Endpoint de test:** `POST /api/v1/admin/alerts/test` — solo dev/staging — envía mensaje de prueba y retorna `status: ok/error`.

## Criterios cumplidos
- [x] Webhook con firma inválida genera alerta en Slack tras 3 intentos en 10 min
- [x] Webhook con error de procesamiento genera alerta
- [x] Rate limiting: máx 1 alerta del mismo tipo cada 5 minutos
- [x] Las alertas incluyen IP, wompi_tx_id, timestamp, ambiente
- [x] `AlertService` nunca lanza excepciones (silenced via try/except general)
- [x] Endpoint `/admin/alerts/test` para verificar canal antes de producción
- [x] Solo requiere `SLACK_WEBHOOK_URL` en `.env` — sin dependencia si no está configurado
