"""
Nivo Backend — API Principal
FastAPI + Post-Quantum Cryptography (liboqs)

Arquitectura: Python 3.11 + FastAPI + ML-KEM-768 + ML-DSA-65
Autor: Nivo Engineering
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FASTAPI_INSTRUMENTATION_AVAILABLE = True
except ImportError:
    FASTAPI_INSTRUMENTATION_AVAILABLE = False

try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.util import get_remote_address
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False

from app.core.config import settings
from app.core.database import init_db
from app.core.telemetry import setup_telemetry
from app.api.v1 import auth, users, payments, crypto, health, kyc, topup, withdrawal, dev_seed, admin
from app.crypto.service import CryptoService

logger = logging.getLogger(__name__)

OPENAPI_DESCRIPTION = """
API de la primera billetera digital quantum-safe de Colombia.

## Como usar esta documentacion

- Local directo: `http://localhost:8000/docs`
- Docker Compose: `http://localhost:8001/docs`
- OpenAPI JSON: `/openapi.json`
- En `ENVIRONMENT=production`, Swagger y ReDoc se desactivan.

## Autenticacion

| Tipo | Header | Usado por |
| --- | --- | --- |
| Usuario JWT | `Authorization: Bearer <access_token>` | Usuarios, pagos, KYC, top-ups y retiros. |
| API key B2B | `X-Nivo-Key: <api_key>` | Endpoints `/api/v1/crypto/*`. |
| Webhook proveedor | `X-Event-Checksum` o `X-Truora-Signature` | Wompi y Truora. |

## Modulos principales

| Tag | Descripcion |
| --- | --- |
| Health | Estado del servicio, PQC, readiness y liveness. |
| Autenticacion | Solicitud/verificacion OTP, refresh y logout. |
| Usuarios | Perfil y wallet del usuario autenticado. |
| Pagos | Pagos P2P, confirmacion OTP, historial y consulta. |
| KYC | Inicio KYC, estado, funnel y webhook Truora. |
| Top-ups | Inicio de recarga, historial y webhook Wompi. |
| Retiros | Cuentas bancarias, micro-deposito y retiros. |
| PQC API B2B | Firma/verificacion post-cuantica para clientes B2B. |
| Dev/Admin | Herramientas disponibles solo en `development`/`staging`. |

## Endpoints internos ahora visibles

Los webhooks, probes y aliases legacy tambien aparecen en Swagger para que el
equipo pueda probarlos y entenderlos desde una sola fuente. En produccion se
deben proteger por red, firma HMAC, allowlists o controles del proveedor.

## Codigos de error comunes

| Codigo | Significado |
| --- | --- |
| `400` | Request invalido, UUID mal formado o payload no parseable. |
| `401` | Token JWT/API key invalida u OTP incorrecto. |
| `402` | Saldo insuficiente. |
| `403` | Wallet congelada, usuario inactivo o endpoint dev bloqueado. |
| `404` | Recurso no encontrado. |
| `422` | Limites, monto invalido o modo custodia no ejecutable. |
| `429` | Rate limit excedido. |
| `503` | Dependencia externa o modulo PQC no disponible. |
"""

OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "Estado operativo del servicio, readiness/liveness y verificación del módulo PQC.",
    },
    {
        "name": "Autenticación",
        "description": "Flujo OTP, emisión/renovación de tokens JWT y cierre de sesión.",
    },
    {
        "name": "Usuarios",
        "description": "Perfil, billetera visual y datos del usuario autenticado.",
    },
    {
        "name": "Pagos",
        "description": "Pagos P2P, confirmación por OTP, historial y consulta de transacciones.",
    },
    {
        "name": "KYC",
        "description": "Verificación de identidad, estado KYC y métricas de funnel.",
    },
    {
        "name": "Top-ups",
        "description": "Recargas PSE/Wompi, historial y conciliación por webhook.",
    },
    {
        "name": "Retiros",
        "description": "Cuentas bancarias, micro-depósitos y retiros ACH/banco aliado.",
    },
    {
        "name": "PQC API B2B",
        "description": "Firma/verificación post-cuántica expuesta para clientes B2B con `X-Nivo-Key`.",
    },
    {
        "name": "⚠️ Dev Only",
        "description": "Herramientas disponibles solo fuera de producción.",
    },
    {
        "name": "⚠️ Admin",
        "description": "Operaciones administrativas de métricas y alertas para entornos controlados.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización y cleanup del ciclo de vida de la app."""
    # OpenTelemetry — must run before first request
    if settings.TELEMETRY_ENABLED:
        from app.core.database import engine as _db_engine
        setup_telemetry(
            service_name=settings.APP_NAME,
            otlp_endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            environment=settings.ENVIRONMENT,
            engine=_db_engine.sync_engine,
        )

    await init_db()

    crypto_service = CryptoService()
    pqc_ok = await crypto_service.health_check()
    if not pqc_ok:
        raise RuntimeError("PQC module failed health check — refusing to start")

    logger.info(
        "Nivo API started — PQC=%s hybrid=%s environment=%s",
        settings.PQC_ALGORITHM,
        settings.HYBRID_MODE,
        settings.ENVIRONMENT,
    )

    yield

    # Shutdown
    logger.info("Nivo API shutting down")


app = FastAPI(
    title="Nivo API",
    description=OPENAPI_DESCRIPTION,
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    servers=[
        {"url": "http://localhost:8000", "description": "Backend local directo"},
        {"url": "http://localhost:8001", "description": "Backend via Docker Compose"},
    ],
)

# FastAPI auto-instrumentation — uses global TracerProvider set during lifespan
if FASTAPI_INSTRUMENTATION_AVAILABLE:
    FastAPIInstrumentor.instrument_app(app, excluded_urls="health,^/$")

# ─── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# ─── Rate limiting global por IP (slowapi) ────────────────────────────────────
# Defensa contra fuerza bruta / scraping. Usa RATE_LIMIT_GENERAL (default
# "100/minute"). Las rutas críticas pueden sobreescribir con @limiter.limit(...).
if SLOWAPI_AVAILABLE:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT_GENERAL],
    )
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Demasiadas solicitudes. Intenta en un minuto."},
        )

    app.add_middleware(SlowAPIMiddleware)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Usuarios"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Pagos"])
app.include_router(kyc.router, prefix="/api/v1/kyc", tags=["KYC"])
app.include_router(topup.router, prefix="/api/v1/topup", tags=["Top-ups"])
app.include_router(withdrawal.router, prefix="/api/v1/withdrawal", tags=["Retiros"])
app.include_router(crypto.router, prefix="/api/v1/crypto", tags=["PQC API B2B"])

# ⚠️  Dev/staging only — no disponible en producción
if settings.ENVIRONMENT in {"development", "staging"}:
    app.include_router(
        dev_seed.router,
        prefix="/api/v1/dev",
        tags=["⚠️ Dev Only"],
    )
    app.include_router(
        admin.router,
        prefix="/api/v1/admin",
        tags=["⚠️ Admin"],
    )


@app.get(
    "/",
    summary="Metadata pública del servicio",
    description=(
        "Retorna metadata básica de la API: nombre del servicio, versión, estado "
        "operativo y configuración PQC pública. No requiere autenticación."
    ),
    tags=["Health"],
)
async def root():
    return {
        "service": "Nivo API",
        "version": "0.1.0",
        "status": "operational",
        "pqc": settings.PQC_ALGORITHM,
        "hybrid": settings.HYBRID_MODE,
    }
