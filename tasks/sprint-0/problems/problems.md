# Problems — Sprint 0

> Registra aquí bugs encontrados, inconsistencias detectadas o blockers durante la ejecución del sprint.
> Formato: fecha | tarea relacionada | descripción | estado | resolución

---

## Issues Encontrados

| # | Fecha | Tarea | Descripción | Estado | Resolución |
|---|-------|-------|-------------|--------|------------|
| 1 | 2026-04-16 | FIX-001 | `init_db()` fallaba con `AttributeError` en SQLAlchemy 2.0 por uso de `c.text()` en `run_sync` | RESUELTO | Reemplazado por `async_sessionmaker` y `text()` directo |
| 2 | 2026-04-16 | FIX-002 | `shared_secret_hex` expuesto en response de `/key-exchange` — vulnerabilidad crítica | RESUELTO | Campo eliminado del modelo `KeyExchangeResponse` |
| 3 | 2026-04-16 | FIX-003 | `SignRequest` aceptaba llave privada ML-DSA-65 en el body — violación del ADR-002 | RESUELTO | Rediseñado para usar keypair efímero del lado del servidor |
| 4 | 2026-04-16 | FIX-004 | Algoritmos PQC hardcodeados en `CryptoService` — viola crypto-agility del ADR-002 | RESUELTO | Algoritmos leídos desde `settings` en `__init__` |
| 5 | 2026-04-16 | FIX-005 | Routers sin `db: AsyncSession = Depends(get_db)` — endpoints sin acceso a BD | RESUELTO | Sesión inyectada en `payments.py`, `users.py`, `auth.py` |
| 6 | 2026-04-16 | FIX-006 | Modelo `Transaction` Pydantic sin campos regulatorios `rail`, `provider_reference`, `settlement_status` | RESUELTO | Campos agregados con sus enums `SettlementRail` y `SettlementStatus` |
| 7 | 2026-04-16 | FIX-007 | Dominios con mayúsculas en CORS (`Nivo.co`) — CORS rechaza requests legítimos | RESUELTO | Corregido a minúsculas en `config.py` |
| 8 | 2026-04-16 | FIX-008 | Ruta `GET /history` capturada por `GET /{tx_id}` por orden incorrecto en FastAPI | RESUELTO | Rutas estáticas declaradas antes de rutas dinámicas |
| 9 | 2026-04-16 | FIX-009 | `httpx==0.27.2` duplicado en `requirements.txt` | RESUELTO | Entrada duplicada eliminada |

---

## Notas
- Todos los issues del Sprint 0 fueron detectados en revisión de código antes del inicio de implementación.
- Ninguno bloqueó features — eran pre-condiciones para que Sprint 1 pudiera ejecutarse correctamente.
