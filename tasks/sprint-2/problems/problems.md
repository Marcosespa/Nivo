# Problems — sprint-2

> Registra aquí bugs encontrados, inconsistencias detectadas o blockers durante la ejecución del sprint.
> Formato: fecha | tarea relacionada | descripción | estado | resolución

---

## Issues Encontrados

| # | Fecha | Tarea | Descripción | Estado | Resolución |
|---|-------|-------|-------------|--------|------------|
| 1 | 2026-05-04 | T-09 | El webhook `/topup/webhook` no tenía Redis inyectado — no podía usarse `AlertService`. Se agregó `Depends(get_redis)` al handler. | RESUELTO | Añadido `get_redis()` local en `topup.py` y `redis_client` como parámetro del endpoint. |
| 2 | 2026-05-04 | T-09 | `dev_seed` solo se registraba en `development` pero `admin` debe estar disponible también en `staging` (para test del canal antes de ir a prod). | RESUELTO | Cambio de `== "development"` a `in {"development", "staging"}` en `main.py`. |

---

## Cómo registrar un issue

Cuando encuentres un problema durante la implementación, agrega una fila a la tabla:

```
| N | YYYY-MM-DD | TASK-XXX | Descripción clara del problema | ABIERTO / RESUELTO / BLOQUEADO | Cómo se resolvió o quién lo está investigando |
```

## Notas
