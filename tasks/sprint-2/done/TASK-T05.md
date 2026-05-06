# TASK-T05 — OpenTelemetry: Instrumentación en rutas críticas

**Estado:** [x] DONE
**Completado:** 2026-05-04
**Tests:** 82/82 passed (sin regresiones)

---

## Qué se hizo

### 1. Paquetes añadidos (`backend/requirements.txt`)
- `opentelemetry-instrumentation-sqlalchemy==0.49b0`
- `opentelemetry-exporter-otlp-proto-http==1.28.0`

### 2. Configuración (`backend/app/core/config.py`)
- `TELEMETRY_ENABLED: bool = True`
- `OTEL_EXPORTER_OTLP_ENDPOINT: str = ""`  — vacío → ConsoleSpanExporter; con URL → OTLP HTTP

### 3. Wiring en startup (`backend/app/main.py`)
- `setup_telemetry()` en lifespan con engine SQLAlchemy → spans de DB automáticos
- `FastAPIInstrumentor.instrument_app(app, excluded_urls="health,^/$")` a nivel módulo → spans HTTP automáticos en cada request

### 4. Span manual — verificación de firma Wompi (`backend/app/services/payment_gateway_service.py`)
- Span: `webhook.wompi.signature_verify`
- Atributos: `webhook.provider`, `webhook.status`, `webhook.ip`, `webhook.tx_id_prefix`, `webhook.signature_result` (valid/invalid/missing)

### 5. Span manual — crédito de billetera (`backend/app/services/payment_gateway_service.py`)
- Span: `wallet.credit`
- Atributos: `wallet.user_id_hash`, `wallet.amount_range`, `wallet.rail`, `wallet.result`

### 6. Span manual — ejecución atómica P2P (`backend/app/services/payment_service.py`)
- Span: `payment.p2p.execute` — envuelve el bloque `async with db.begin():`
- Atributos: `payment.user_id_hash`, `payment.amount_range`, `payment.rail`, `payment.pqc_algorithm`, `payment.result`

### 7. Span manual — verificación OTP (`backend/app/api/v1/auth.py`)
- Span: `auth.otp.verify`
- Atributos: `auth.phone_hash`, `auth.result` (valid/invalid/rate_limited)

### 8. `.env.example`
- Añadido: `TELEMETRY_ENABLED=true` y `OTEL_EXPORTER_OTLP_ENDPOINT=`

---

## Política PII en spans

Ningún span expone PII directamente:
- Teléfonos / UUIDs → `hash_user_id()` → SHA-256 hex[:16]
- Montos → `amount_range()` → buckets (< $10k, $10k-$50k, …)
- IPs → pasadas como está (no PII colombiana; Wompi puede estar en whitelist)

---

## Criterio de hecho cumplido

- Cada request a endpoints críticos (auth, pagos, top-up) genera un trace completo
- Los spans tienen duración, status y contexto sin PII
- `OTEL_EXPORTER_OTLP_ENDPOINT` vacío → ConsoleSpanExporter (dev); con endpoint → Cloud Trace / Jaeger
- 82/82 tests sin regresiones
