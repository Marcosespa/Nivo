"""
Nivo — Endpoints de Health Check

/health        — Estado general del servicio
/health/pqc    — Estado específico del módulo PQC (verificado cada 60s en prod)
/health/db     — Estado de conexión a PostgreSQL
/health/ready  — Readiness probe para Kubernetes/Cloud Run
"""

from datetime import datetime, timezone
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.crypto.service import CryptoService

router = APIRouter()
crypto = CryptoService()


@router.get("", status_code=status.HTTP_200_OK, include_in_schema=False)
async def health():
    """Health check básico."""
    return {
        "status": "ok",
        "service": "Nivo-api",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/pqc",
    summary="Estado del módulo PQC",
    description=(
        "Verifica la integridad del módulo de criptografía post-cuántica. "
        "Ejecuta un ciclo completo de firma y verificación ML-DSA-65. "
        "Retorna 503 si el módulo PQC falla — el servicio no debe operar sin PQC."
    ),
)
async def health_pqc():
    """
    Verificación de integridad del módulo PQC.
    Ejecuta un roundtrip real de firma/verificación.
    """
    pqc_ok = await crypto.health_check()

    if not pqc_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "pqc": "FAIL",
                "message": "PQC module integrity check failed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    return {
        "status": "ok",
        "pqc": "PASS",
        "algorithm_kem": settings.PQC_ALGORITHM,
        "algorithm_sig": settings.PQC_SIGNATURE_ALGORITHM,
        "hybrid_mode": settings.HYBRID_MODE,
        "liboqs_available": crypto._liboqs_available,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", include_in_schema=False)
async def readiness():
    """Readiness probe para Cloud Run."""
    return {"ready": True}


@router.get("/live", include_in_schema=False)
async def liveness():
    """Liveness probe para Cloud Run."""
    return {"alive": True}
