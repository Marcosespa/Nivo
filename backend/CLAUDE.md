# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_payments_flow.py

# Run a single test by name
pytest tests/test_payments_flow.py::test_payment_full_flow

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Lint
ruff check app/ tests/

# Type check
mypy app/

# Run the dev server
uvicorn app.main:app --reload --port 8000

# Migrations
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "description"
alembic current

# Docker (full stack)
docker build -t nivo-api .
docker run -p 8000:8000 --env-file .env nivo-api
```

## Architecture

### Request lifecycle

Every authenticated request goes through `app/core/security.py:get_current_user`, which decodes the JWT, verifies `type == "access"`, and hydrates the `UserORM` from PostgreSQL. The `jti` claim supports a Redis-backed token blacklist for logout. Redis is injected as a FastAPI dependency (`get_redis`) defined locally in each router file — override it in tests via `app.dependency_overrides`.

### Two-phase payment flow (P2P)

1. `POST /api/v1/payments/initiate` — validates sender balance, daily limit, and receiver existence, then stores a pending transaction in Redis (TTL-bound).
2. `POST /api/v1/payments/confirm` — verifies OTP, retrieves the pending tx from Redis, then calls `PaymentService.execute_payment()` which runs atomically: `SELECT ... FOR UPDATE` on both wallets, debit/credit in one DB transaction, and signs the committed tx with ML-DSA-65.

Domain errors (`InsufficientFundsError`, `DailyLimitExceededError`, etc.) are raised in `payment_service.py` and caught in the router to map to specific HTTP codes.

### Top-up / Wompi webhook flow

`POST /api/v1/topup/initiate` creates a Wompi payment link. `POST /api/v1/topup/webhook` (no JWT) is the Wompi callback. The handler in `PaymentGatewayService.process_webhook()` does:
1. HMAC-SHA256 signature verification against `WOMPI_EVENTS_SECRET`
2. Idempotency check via `webhook_event_logs` table (unique constraint on `(provider, provider_event_id)`)
3. Status state machine: only `APPROVED` credits the wallet; `PENDING` is skipped; `DECLINED/VOIDED` marks the transaction failed.

Webhooks always return HTTP 200 regardless of processing outcome to avoid leaking internal state to Wompi.

### PQC cryptography

`app/crypto/service.py` wraps `liboqs-python`. Algorithms are read from `settings.PQC_ALGORITHM` (ML-KEM-768) and `settings.PQC_SIGNATURE_ALGORITHM` (ML-DSA-65). When `liboqs` is unavailable (CI without the C library), the service falls back to a simulation mode — `health_check()` returns `False` in that case. The app refuses to start if `health_check()` fails, so set `PQC_ALGORITHM=mock` or ensure liboqs is installed before running locally.

Each user gets a keypair at onboarding (stored in `pqc_keys` table). Payments are signed with ML-DSA-65 at confirmation time; the signature is stored in `transactions.ml_dsa_signature`.

### B2B crypto API

`app/api/v1/crypto.py` exposes PQC-as-a-Service endpoints authenticated by `X-Nivo-Key` header. The `verify_api_key` dependency currently only validates key length (≥32 chars) — full B2B client DB validation is a pending TODO.

### Database

All models are in `app/models/orm/`. SQLAlchemy async sessions come from `get_db()` in `database.py`, which auto-commits on success and auto-rollbacks on exception. Alembic reads `settings.database_url_sync` (strips `+asyncpg`) for migration runs.

Monetary amounts are stored as integers in **centavos de COP** (e.g., `50_000_00` = $500,000 COP). Daily transaction limits by plan are configured in `settings` (`TX_LIMIT_FREE_DAILY`, etc.) and enforced in `payment_service.py`.

### Test setup

Tests use SQLite (`aiosqlite`) in a temp file per test session. `FakeRedis` (in `conftest.py`) is a minimal in-memory async Redis replacement. The `created_user` fixture is a factory — call it with a phone number and optional `balance_cop`, `plan`, `kyc_status`. DB and Redis are injected via `app.dependency_overrides` in the `client` fixture.

`pytest.ini` sets `asyncio_mode = auto`, so all `async def test_*` functions run without decorators.

### Key env vars

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | `development` enables `/api/v1/dev/*` routes and optional webhook signature check |
| `WOMPI_EVENTS_SECRET` | HMAC-SHA256 secret used to verify Wompi webhook signatures (`X-Event-Checksum`). Required in production. |
| `WOMPI_INTEGRITY_SECRET` | Used to sign payment link creation requests against the Wompi API. |
| `WOMPI_BASE_URL` | Override of the Wompi API base URL. Empty → `sandbox.wompi.co/v1` in non-prod, `production.wompi.co/v1` in prod. Set to `http://localhost:8001/mock` for a local mock server. |
| `WOMPI_MOCK_MODE` | `true` skips outbound calls to Wompi and HMAC validation on the webhook (dev/CI only — automatically disabled when `ENVIRONMENT=production`). |
| `PQC_ALGORITHM` | Swappable without code changes — crypto-agility by design |
| `MONEY_CUSTODY_MODE` | Controls custody model; `non_custodial_middleware` for MVP |
| `DATABASE_URL` | Use `postgresql+asyncpg://` for runtime; Alembic strips `+asyncpg` automatically |
| `JWT_SECRET_KEY` | ≥32 chars. Validator rejects placeholders (`CHANGE_ME`, `replace_with`, etc.) when `ENVIRONMENT=staging\|production`. |

## Task tracking

All work — completed and in progress — is documented in `../tasks/` (one level above this repo). **Before implementing anything, check that folder first** to avoid duplicating work or missing exact specifications that were already written.

### Structure

```
tasks/
├── README.md                   ← index with sprint status and overall progress
├── ANALISIS-SPRINT-0-1.md      ← senior + business analysis of the codebase
├── sprint-0/
│   ├── sprint-0.md             ← all FIX tasks with exact code changes
│   └── done/FIX-001..FIX-009  ← individual files for each completed fix
├── sprint-1/
│   ├── sprint-1.md             ← TASK-001..TASK-005 with full specifications
│   └── done/TASK-001..TASK-005
├── sprint-2/
│   └── sprint-2.md             ← TASK-006..TASK-008 (current sprint, 0/3 done)
├── sprint-3/ … sprint-8-12/    ← future sprints
└── transversales/              ← cross-cutting tasks (TASK-031..TASK-035)
```

### Status convention

```
[ ] PENDING      — not started
[>] IN_PROGRESS  — being worked on by an agent
[x] DONE         — completed and verified
[!] BLOCKED      — waiting on a dependency
```

### Current state (as of Sprint 2)

| Sprint | Tasks | Status |
|--------|-------|--------|
| Sprint 0 — Pre-implementation fixes | FIX-001 → FIX-009 | ✅ 9/9 done |
| Sprint 1 — Technical foundations | TASK-001 → TASK-005 | ✅ 5/5 done |
| Sprint 2 — KYC & top-ups (**active**) | TASK-006 → TASK-008 | ⏳ 0/3 done |
| Sprint 3 → 8-12 | TASK-009 → TASK-030 | ⏳ pending |
| Transversales | TASK-031 → TASK-035 | ⏳ pending |

Sprint 2 tasks pending: TASK-006 (Truora KYC), TASK-007 (Wompi PSE top-ups), TASK-008 (ACH withdrawals). Note: the backend already has implementations of KYC and top-up that go beyond the spec in sprint-2.md — check the actual code state before treating these as unstarted.

### Task format

Each task file contains: `Estado`, `Agente sugerido`, `Estimado`, `Prioridad`, a `Descripción`, an exact list of files to create/modify with precise code snippets, and `Criterios de éxito` (acceptance checklist). The specifications are authoritative — they define the exact schema, method signatures, and business rules to implement.
