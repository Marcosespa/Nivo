# Nivo

Nivo es un neobanco colombiano quantum-safe en construcción. El MVP combina backend FastAPI, criptografía post-cuántica, pagos P2P, top-ups por Wompi/PSE, consola web, landing pública y app móvil Flutter.

## Estructura

```text
Nivo/
├── backend/             # FastAPI, SQLAlchemy, Alembic, servicios financieros y PQC
├── frontend/            # Consola web interna/API console
├── landing_page/nivo/   # Landing pública React/Vite
├── mobile/nivo_mvp/     # MVP móvil Flutter
├── docs/                # Arquitectura, negocio, compliance, DR y readiness
├── docker_helper/       # Compose auxiliares y documentación Docker
├── infra/               # Infraestructura local/dev
└── .github/workflows/   # CI
```

## Requisitos

- Python 3.11 para producción/CI. La suite local también corre en la venv actual.
- Node.js 20+ para `frontend/` y `landing_page/nivo/`.
- Docker y Docker Compose para stack local.
- liboqs instalado en producción para PQC real. En tests puede operar en modo simulado.

## Configuración

Backend:

```bash
cd backend
cp .env.example .env
```

Edita `.env` y reemplaza todos los `replace_with_*`. Variables principales:

| Variable | Uso |
| --- | --- |
| `ENVIRONMENT` | `development`, `staging` o `production`. |
| `JWT_SECRET_KEY` | Firma de tokens. Mínimo 32 caracteres; usar secret manager en staging/prod. |
| `DATABASE_URL` | URL SQLAlchemy async, por ejemplo `postgresql+asyncpg://...`. |
| `REDIS_URL` | Redis para OTP/rate helpers. |
| `B2B_API_KEYS` | Lista JSON de API keys B2B para compatibilidad dev/staging. |
| `WOMPI_EVENTS_SECRET` | Validación HMAC de webhooks Wompi. Obligatoria en producción. |
| `WOMPI_MOCK_MODE` | `true` solo en local/CI para evitar llamadas reales. |
| `ALLOWED_ORIGINS` / `ALLOWED_HOSTS` | CORS y hosts confiables. Cerrar en producción. |
| `TELEMETRY_ENABLED` / `OTEL_EXPORTER_OTLP_ENDPOINT` | Observabilidad OpenTelemetry. |

Docker Compose:

```bash
cp .env.compose.example .env
cp backend/.env.docker.example backend/.env.docker
```

Actualiza ambos archivos antes de levantar el stack. No uses los ejemplos como secretos reales.

## Ejecución Local

### Quickstart recomendado (Postgres+Redis en Docker, backend nativo)

Es el flujo verificado funcional hoy. Usa la `.venv` ya inicializada con `liboqs`.

```bash
# Terminal 1 — DB + Redis
cd /Users/marcosespana/Desktop/Nivo
docker compose --env-file .env.compose.example -f docker_helper/docker-compose.postgres.yml up -d

# Terminal 2 — backend
cd /Users/marcosespana/Desktop/Nivo/backend
source .venv/bin/activate
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1
```

Mantén la DB levantada entre sesiones (`docker compose ... down` solo si vas a recrearla). Para detalles de migraciones, troubleshooting y comandos extra, ver [docs/07-local-dev-guide.md](docs/07-local-dev-guide.md) y [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

### Setup inicial del backend (primera vez)

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/alembic upgrade head
```

Landing pública:

```bash
cd landing_page/nivo
npm ci
npm run dev
```

Consola web:

```bash
cd frontend
npm ci
npm run dev
```

Stack Docker:

```bash
docker compose --env-file .env up --build
```

Servicios por defecto:

- Backend: `http://localhost:8001`
- Swagger: `http://localhost:8001/docs` en `development`/`staging`
- Frontend consola: `http://localhost:3000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- pgAdmin: `http://localhost:5050`

## Pruebas y Calidad

Backend:

```bash
cd backend
./.venv/bin/python -m pytest
./.venv/bin/python -m compileall app tests
```

Landing:

```bash
cd landing_page/nivo
npm run build
```

CI:

- Ruff para backend.
- Alembic migration check.
- Pytest con cobertura.
- Build de landing.
- Triggers en `main` y `develop`.

## API

FastAPI genera OpenAPI automáticamente:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

Swagger ahora incluye tambien webhooks, probes y aliases internos para que la
documentacion operativa viva en una sola fuente.

Routers principales:

| Prefijo | Descripción |
| --- | --- |
| `/health` | Estado del servicio, DB y módulo PQC. |
| `/api/v1/auth` | OTP, verificación, refresh y logout. |
| `/api/v1/users` | Perfil y wallet del usuario autenticado. |
| `/api/v1/payments` | Inicio, confirmación e historial de pagos P2P. |
| `/api/v1/topup` | Inicio de recargas y webhook Wompi. |
| `/api/v1/withdrawal` | Cuentas bancarias y retiros. |
| `/api/v1/crypto` | API B2B PQC protegida por `X-Nivo-Key`. |
| `/api/v1/kyc` | Flujo KYC y estado del usuario. |

Notas:

- Los endpoints dev/admin solo se montan en `development` y `staging`.
- `dev_otp` solo se expone en `development` y desde localhost.
- En producción los webhooks Wompi requieren firma válida.

## Troubleshooting

| Síntoma | Causa común | Solución |
| --- | --- | --- |
| `ModuleNotFoundError: opentelemetry.instrumentation` | Dependencias incompletas en la venv. | Reinstalar `pip install -r backend/requirements.txt`; el backend degrada sin instrumentación FastAPI opcional. |
| `liboqs no está instalado` | Entorno local sin liboqs C. | Aceptable en tests; para staging/prod usar `backend/Dockerfile` o instalar liboqs. |
| Webhook Wompi no acredita saldo | `provider_reference` no coincide o firma inválida. | Verificar `WOMPI_EVENTS_SECRET`, `WOMPI_MOCK_MODE` y payload `id/reference`. |
| `dev_otp` no aparece | Petición no viene de localhost o `ENVIRONMENT` no es `development`. | Usar `127.0.0.1`/`::1` y revisar `.env`. |
| Docker Compose falla por variables faltantes | `.env` raíz no existe o faltan credenciales. | Copiar `.env.compose.example` a `.env` y completar valores. |
| CORS bloquea frontend | `ALLOWED_ORIGINS` no incluye origen real. | Añadir origen exacto, sin wildcard en producción. |

## Seguridad

- No commitear `.env`, credenciales Wompi, JWT secrets, API keys B2B, tokens Cloudflare ni credenciales Firebase.
- Usar secret manager en staging/producción.
- Mantener `WOMPI_MOCK_MODE=false` en producción.
- Mantener `/docs` y `/redoc` deshabilitados en producción.
- Revisar logs para que no incluyan teléfonos completos, tokens, payloads sensibles ni headers de autorización.

## Documentación Complementaria

| Documento | Descripción |
| --- | --- |
| [docs/03-technical-architecture.md](docs/03-technical-architecture.md) | Arquitectura técnica y decisiones principales. |
| [docs/07-local-dev-guide.md](docs/07-local-dev-guide.md) | Guía detallada de desarrollo local. |
| [docs/08-postgresql-backup-dr.md](docs/08-postgresql-backup-dr.md) | Backups, PITR y recuperación. |
| [docs/ADR-003-hsm-key-management.md](docs/ADR-003-hsm-key-management.md) | Manejo futuro de llaves HSM/KMS. |
| [docs/09-production-readiness-report.md](docs/09-production-readiness-report.md) | Auditoría de estabilidad, seguridad, DevOps y roadmap v2. |

## Licencia

Propietario — Nivo SAS © 2025-2026. Todos los derechos reservados.
