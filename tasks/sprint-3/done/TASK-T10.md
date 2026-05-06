# TASK-T10 — Métricas de conversión KYC

**Estado:** [x] DONE
**Completado:** 2026-05-04
**Tests:** 94/94 passed (12 tests nuevos)

---

## Qué se hizo

### Nuevos archivos
- `backend/app/models/orm/kyc_funnel_event.py` — ORM model `KYCFunnelEvent` con `KYCFunnelStepEnum` (registered, kyc_initiated, kyc_result, first_deposit) y `KYCFunnelResultEnum` (completed, failed)
- `backend/app/services/kyc_funnel_service.py` — `KYCFunnelService` con `track()`, `get_funnel_stats()`, `get_kyc_approval_rate_24h()`. Singleton `kyc_funnel_service`
- `backend/alembic/versions/0005_add_kyc_funnel_events.py` — migración con 3 índices (user_id, step, created_at)
- `backend/tests/test_kyc_funnel.py` — 12 tests (unit + integración)

### Archivos modificados
- `backend/app/models/orm/__init__.py` — registra `KYCFunnelEvent`
- `backend/app/services/alert_service.py` — añade `KYC_LOW_APPROVAL_RATE` a `AlertEvent` + `send_rate_alert()` (alerta directa con rate-limit, sin threshold de conteo)
- `backend/app/api/v1/auth.py` — track `REGISTERED` cuando is_new=True (mismo commit que PQC key)
- `backend/app/services/kyc_service.py` — track `KYC_INITIATED` en `initiate_verification()`, track `KYC_RESULT` en `process_webhook()` con `failure_reason` de Truora
- `backend/app/services/payment_gateway_service.py` — track `FIRST_DEPOSIT` en `_process_topup_approved()` cuando `old_balance == 0`
- `backend/app/api/v1/kyc.py` — agrega `GET /api/v1/kyc/funnel` (requires JWT, param `days`), Redis en webhook para alerta tasa < 70%
- `backend/tests/conftest.py` — `FakeRedis.set()` soporta `nx` y `ex` kwargs; override de `kyc.get_redis` y `topup.get_redis`

---

## Funnel instrumentado

```
REGISTERED       ← auth.py → verify_otp (is_new=True)
  ↓
KYC_INITIATED    ← kyc_service.py → initiate_verification()
  ↓
KYC_RESULT       ← kyc_service.py → process_webhook()
  result: completed | failed
  failure_reason: de Truora (rejection_reason / reason / failure_details)
  ↓
FIRST_DEPOSIT    ← payment_gateway_service.py → _process_topup_approved() si old_balance==0
```

## Alertas

- `GET /api/v1/kyc/funnel` devuelve `alert_low_kyc_rate: bool` calculado en tiempo real
- Webhook Truora: si muestra ≥ 5 y tasa 24h < 70% → `AlertService.send_rate_alert(KYC_LOW_APPROVAL_RATE)` → Slack
- Rate limit de alerta: max 1 por 5 minutos del mismo tipo

## Criterio de hecho

- Founders pueden llamar `GET /api/v1/kyc/funnel?days=7` y ver tasas de conversión por etapa
- `alert_low_kyc_rate: true` cuando tasa < 70% con muestra ≥ 5
- Alerta Slack automática en webhook de Truora cuando tasa cae bajo umbral
- 94/94 tests sin regresiones
