"""
Nivo Backend — API Principal
FastAPI + Post-Quantum Cryptography (liboqs)

Arquitectura: Python 3.11 + FastAPI + ML-KEM-768 + ML-DSA-65
Autor: Nivo Engineering
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, users, payments, crypto, health, kyc, topup, withdrawal, dev_seed
from app.crypto.service import CryptoService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización y cleanup del ciclo de vida de la app."""
    # Startup
    await init_db()

    # Verificar integridad del módulo PQC al arrancar
    crypto_service = CryptoService()
    pqc_ok = await crypto_service.health_check()
    if not pqc_ok:
        raise RuntimeError("PQC module failed health check — refusing to start")

    print(f"✅ Nivo API iniciada — PQC: {settings.PQC_ALGORITHM} | Hybrid: {settings.HYBRID_MODE}")

    yield

    # Shutdown
    print("🔒 Nivo API cerrando...")


app = FastAPI(
    title="Nivo API",
    description=(
        "API de la primera billetera digital quantum-safe de Colombia. "
        "Cifrado ML-KEM-768 + X25519 híbrido, firmas ML-DSA-65 en cada transacción."
    ),
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

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

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Usuarios"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Pagos"])
app.include_router(kyc.router, prefix="/api/v1/kyc", tags=["KYC"])
app.include_router(topup.router, prefix="/api/v1/topup", tags=["Top-ups"])
app.include_router(withdrawal.router, prefix="/api/v1/withdrawal", tags=["Retiros"])
app.include_router(crypto.router, prefix="/api/v1/crypto", tags=["PQC API B2B"])

# ⚠️  Dev-only: seed de datos de prueba — NO disponible en producción
if settings.ENVIRONMENT == "development":
    app.include_router(
        dev_seed.router,
        prefix="/api/v1/dev",
        tags=["⚠️ Dev Only"],
    )


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "Nivo API",
        "version": "0.1.0",
        "status": "operational",
        "pqc": settings.PQC_ALGORITHM,
        "hybrid": settings.HYBRID_MODE,
    }
