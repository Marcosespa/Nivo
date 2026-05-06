# TASK-T13 — Métricas de negocio instrumentadas

**Estado:** [x] DONE
**Completado:** 2026-05-04
**Tests:** 109/109 passed (15 tests nuevos)

---

## Qué se hizo

### Nuevos archivos
- `backend/app/models/orm/business_metrics_daily.py` — ORM model `BusinessMetricsDaily` con UNIQUE constraint en `snapshot_date`
- `backend/app/services/metrics_service.py` — `MetricsService` con `calculate_and_save_daily_snapshot()`, `get_recent_snapshots()`, `check_gmv_anomaly()`, `send_daily_slack_report()`. Singleton `metrics_service`
- `backend/alembic/versions/0006_add_business_metrics_daily.py` — migración con UNIQUE constraint + índice en `snapshot_date`
- `backend/tests/test_metrics.py` — 15 tests (unit + integración)

### Archivos modificados
- `backend/app/models/orm/__init__.py` — registra `BusinessMetricsDaily`
- `backend/app/services/alert_service.py` — añade `GMV_ANOMALY` y `DAILY_METRICS_REPORT` a `AlertEvent` + config en `_ALERT_CONFIG`
- `backend/app/api/v1/admin.py` — añade `POST /api/v1/admin/metrics/snapshot`, `GET /api/v1/admin/metrics/daily`, `POST /api/v1/admin/metrics/report`; también añade imports de `get_db`, `metrics_service`
- `backend/tests/conftest.py` — añade override de `admin.get_redis` al fixture `client`

---

## Schema: business_metrics_daily

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID PK | Auto |
| `snapshot_date` | Date UNIQUE | Fecha del snapshot |
| `gmv_cop` | BigInteger | Suma de transacciones COMPLETED (centavos) |
| `p2p_transactions` | Integer | Total P2P iniciadas (INTERNAL rail) |
| `topup_transactions` | Integer | Top-ups completados (PSE + ACH) |
| `p2p_success_rate` | Float | p2p_ok / p2p_total |
| `new_users` | Integer | Usuarios creados ese día |
| `active_users` | Integer | Distinct senders con tx COMPLETED |
| `kyc_approved` | Integer | KYC_RESULT = COMPLETED del día |
| `kyc_rejected` | Integer | KYC_RESULT = FAILED del día |
| `otps_generated` | Integer | OTPs creados ese día |
| `plan_free_users` | Integer | Snapshot total usuarios FREE activos |
| `plan_plus_users` | Integer | Snapshot total usuarios PLUS activos |
| `plan_pro_users` | Integer | Snapshot total usuarios PRO activos |
| `calculated_at` | DateTime | Timestamp de cálculo |

## Endpoints

```
POST /api/v1/admin/metrics/snapshot?snapshot_date=YYYY-MM-DD
  → calcula y upserta snapshot (default: ayer)
  → retorna resumen del snapshot

GET /api/v1/admin/metrics/daily?days=7
  → retorna últimos N días de snapshots

POST /api/v1/admin/metrics/report
  → dispara send_daily_slack_report()
  → retorna {"status": "ok"|"no_data", "sent": bool}
```

## Alertas nuevas

- `GMV_ANOMALY` — caída > 30% vs promedio 7 días → severity high
- `DAILY_METRICS_REPORT` — reporte informativo diario → severity medium (re-usa `send_rate_alert` con rate-limit)

## Criterio de hecho

- `POST /api/v1/admin/metrics/snapshot` calcula y persiste snapshot correcto
- `GET /api/v1/admin/metrics/daily` devuelve series temporales para dashboard
- Detección de anomalía GMV > 30% caída vs 7-day avg
- `send_daily_slack_report()` envía 5 métricas clave al canal
- Upsert idempotente: recalcular el mismo día actualiza el row existente
- 109/109 tests sin regresiones
