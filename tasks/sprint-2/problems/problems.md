# Problems — sprint-2

> Registra aquí bugs encontrados, inconsistencias detectadas o blockers durante la ejecución del sprint.
> Formato: fecha | tarea relacionada | descripción | estado | resolución

---

## Issues Encontrados

| # | Fecha | Tarea | Descripción | Estado | Resolución |
|---|-------|-------|-------------|--------|------------|
| 1 | 2026-05-04 | T-09 | El webhook `/topup/webhook` no tenía Redis inyectado — no podía usarse `AlertService`. Se agregó `Depends(get_redis)` al handler. | RESUELTO | Añadido `get_redis()` local en `topup.py` y `redis_client` como parámetro del endpoint. |
| 2 | 2026-05-04 | T-09 | `dev_seed` solo se registraba en `development` pero `admin` debe estar disponible también en `staging` (para test del canal antes de ir a prod). | RESUELTO | Cambio de `== "development"` a `in {"development", "staging"}` en `main.py`. |
| 3 | 2026-05-07 | TASK-031 | `otps_generated` en `business_metrics_daily` siempre era 0 — `metrics_service` hacía SELECT a la tabla `otps` pero `otp_service.py` nunca escribe en esa tabla (solo Redis). Bug silencioso desde Sprint 1. | RESUELTO | `otp_service.py` ahora incrementa contadores Redis `metrics:otp:gen/ok/fail:{YYYYMMDD}` (pipeline, TTL 48h). `metrics_service` lee de Redis cuando disponible, DB como fallback. |
| 4 | 2026-05-07 | TASK-031 | No había medición de latencia P2P a pesar de que TASK-003 requería < 800ms con `time.perf_counter()`. Métrica prometida pero no implementada. | RESUELTO | `payment_service.execute_payment()` mide ms desde start hasta post-commit con `time.perf_counter()`, LPUSH a `metrics:latency:p2p:{date}` (máx 500 muestras, TTL 48h). P50/P95 se calculan en snapshot diario. |
| 5 | 2026-05-07 | TASK-031 | Métricas de negocio instrumentadas (volumen, OTPs, latencias) no tenían spec explícita en Sprint 0 ni 1 — quedaron implícitas en TASK-031 (transversal), sin IDs de tarea ni criterios de éxito de código. Gap de planning detectado. | ABIERTO | Decisión de diseño: las métricas de instrumentación en código pertenecen a Sprint 1 (fundaciones); el monitoreo de infraestructura (Sentry, GCP Cloud Monitoring) pertenece a TASK-031. Considerar split en TASK-031a / TASK-031b en el backlog. |

---

## Cómo registrar un issue

Cuando encuentres un problema durante la implementación, agrega una fila a la tabla:

```
| N | YYYY-MM-DD | TASK-XXX | Descripción clara del problema | ABIERTO / RESUELTO / BLOQUEADO | Cómo se resolvió o quién lo está investigando |
```

## Notas
