# T-08 — Gate adicional para dev_otp (host local)
**Estado:** [x] DONE
**Sprint:** 2 (P2 — Mejoras)
**Fecha:** 2026-05-04

## Estado al revisar

Ya estaba completamente implementado desde Sprint 1. Verificado en código y tests.

## Qué existe

**Doble gate en `auth.py` línea 160:**
```python
if settings.ENVIRONMENT == "development" and _client_host in {"127.0.0.1", "::1"}:
    response["dev_otp"] = otp_code
```

**Doble gate en `payments.py` línea 219:**
```python
dev_otp=(
    otp_code
    if settings.ENVIRONMENT == "development"
    and http_request.client is not None
    and http_request.client.host in {"127.0.0.1", "::1"}
    else None
),
```

**`dev_seed.py` retorna 404 desde IP externa:**
```python
if _host not in {"127.0.0.1", "::1"}:
    raise HTTPException(status_code=404, detail="Not found")
```

**Tests en `tests/test_dev_otp_gate.py`:** 5 tests, todos pasan.

## Auditoría de endpoints /dev o /debug

- `/api/v1/dev/seed` — gated: router solo registrado en development, + check localhost → 404 ✅
- `/api/v1/dev/seed` (DELETE) — mismo check localhost ✅
- `dev_otp` en `/auth/request-otp` — doble gate ✅
- `dev_otp` en `/payments/initiate` — doble gate ✅
- No existen otros endpoints `/debug` en el codebase ✅

## Resultado de tests
```
5/5 test_dev_otp_gate.py PASSED
82/82 suite completa PASSED
```
