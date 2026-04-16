# Task Done

## Sprint 0

- [x] FIX-001 — Corregir bug `init_db()` en `database.py` (SQLAlchemy 2.0)
- [x] FIX-002 — Eliminar `shared_secret_hex` de `KeyExchangeResponse`
- [x] FIX-003 — Eliminar entrada de llave privada en `SignRequest`
- [x] FIX-004 — Conectar algoritmos PQC desde `settings` en `CryptoService`
- [x] FIX-005 — Inyectar sesión de BD en routers (`payments.py`, `users.py`, `auth.py`)
- [x] FIX-006 — Agregar campos regulatorios a modelo `Transaction` Pydantic
- [x] FIX-007 — Corregir URLs en CORS y `ALLOWED_HOSTS`
- [x] FIX-008 — Corregir orden de rutas y agregar `/history` en `payments.py`
- [x] FIX-009 — Eliminar entrada duplicada de `httpx` en `requirements.txt`

## Sprint 1

- [x] TASK-001 — Configurar Base de Datos con SQLAlchemy ORM
- [x] TASK-002 — Implementar JWT Real y Autenticación Completa
- [x] TASK-003 — Implementar Cuenta Nivo, Wallet Visual y Transacciones Atómicas
- [x] TASK-004 — Tests Unitarios del Módulo CryptoService
- [x] TASK-005 — Integrar Twilio para Envío de OTP

## Notas

- Solo se marcaron tareas verificadas de sprint 0 y sprint 1.
- `TASK-006`, `TASK-007` y `TASK-008` no se marcaron porque en el roadmap detallado pertenecen al sprint 2.

## Auditoria de consistencia - 2026-04-16

- `TASKS.md` y `TASK_DONE.md` quedaron sincronizados para sprint 0: `FIX-001` a `FIX-009` estan en estado `DONE`.
- `TASKS.md` y `TASK_DONE.md` quedaron sincronizados para sprint 1: `TASK-001` a `TASK-005` estan en estado `DONE`.
- `TASK-006`, `TASK-007` y `TASK-008` siguen fuera de `TASK_DONE.md` porque permanecen pendientes y corresponden al sprint 2 en el roadmap detallado.
