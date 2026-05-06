"""
Nivo — API Pública PQC-as-a-Service (B2B)

Esta API permite a fintechs y bancos integrar cifrado post-cuántico
a sus sistemas existentes sin reconstruir su infraestructura.

Endpoints:
  POST /api/v1/crypto/key-exchange     — ML-KEM encapsulate/decapsulate
  POST /api/v1/crypto/sign             — ML-DSA-65 firma de datos
  POST /api/v1/crypto/verify           — Verificación de firma
  POST /api/v1/crypto/hybrid-encrypt   — Cifrado AES-GCM con llave híbrida
  GET  /api/v1/crypto/algorithms       — Algoritmos soportados

Autenticación: API Key en header X-Nivo-Key
Billing: por operación en el dashboard B2B
"""

from __future__ import annotations

import hashlib
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from opentelemetry import trace

from app.core.config import settings
from app.core.database import get_db
from app.crypto.service import CryptoService
from app.models.orm.b2b_client import B2BClient

router = APIRouter()
crypto = CryptoService()
tracer = trace.get_tracer(__name__)


# ─── Schemas ──────────────────────────────────────────────────────────────────

class KeyExchangeRequest(BaseModel):
    recipient_pqc_public_key_hex: str    # Llave pública ML-KEM del receptor
    recipient_x25519_public_key_hex: str  # Llave pública X25519 del receptor


class KeyExchangeResponse(BaseModel):
    pqc_ciphertext_hex: str          # Texto cifrado ML-KEM para enviar al receptor
    classical_public_key_hex: str    # Llave pública X25519 efímera del emisor
    algorithm: str = "ML-KEM-768 + X25519 (hybrid)"


class SignRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    data_hex: str           # Datos a firmar (hex)


class SignResponse(BaseModel):
    signature_hex: str
    public_key_hex: str                 # Llave PÚBLICA para que el llamador verifique
    public_key_fingerprint: str
    algorithm: str = "ML-DSA-65"


class VerifyRequest(BaseModel):
    data_hex: str
    signature_hex: str
    public_key_hex: str


class VerifyResponse(BaseModel):
    valid: bool
    algorithm: str = "ML-DSA-65"


# ─── Dependencia de API Key B2B ───────────────────────────────────────────────
#
# Autenticación en dos capas:
#   1. Tabla `b2b_clients` con SHA-256 del API key (fuente canónica).
#   2. Fallback a `settings.B2B_API_KEYS` (compatibilidad con tests/dev).
#
# IMPORTANTE: el billing por operación aún no está implementado. Esta
# verificación impide que el endpoint sea abusable mientras el equipo de
# negocio define pricing y pipeline B2B.

async def verify_b2b_api_key(
    x_nivo_key: str = Header(..., alias="X-Nivo-Key"),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Valida la API key contra `b2b_clients.api_key_hash` o el fallback de settings."""
    if not x_nivo_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el header X-Nivo-Key",
        )

    key_hash = hashlib.sha256(x_nivo_key.encode()).hexdigest()

    try:
        stmt = select(B2BClient).where(
            (B2BClient.api_key_hash == key_hash) & (B2BClient.is_active == True)
        )
        result = await db.execute(stmt)
        client = result.scalar_one_or_none()
    except Exception:
        # Si la tabla todavía no existe (dev recién creado), caer al fallback.
        client = None

    if client is not None:
        return x_nivo_key

    # Fallback: lista estática (útil para tests/dev sin seed en BD).
    configured_keys = [api_key for api_key in settings.B2B_API_KEYS if api_key]
    if configured_keys and any(
        secrets.compare_digest(x_nivo_key, api_key) for api_key in configured_keys
    ):
        return x_nivo_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key inválida. Contacta al equipo B2B para obtener una.",
    )


# Alias retrocompatible
verify_api_key = verify_b2b_api_key


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "/algorithms",
    summary="Algoritmos PQC soportados",
)
async def list_algorithms(
    _: Annotated[str, Depends(verify_api_key)],
):
    """Lista los algoritmos PQC disponibles y sus parámetros."""
    return {
        "kem": [
            {
                "name": "ML-KEM-768",
                "nist_standard": "FIPS 203",
                "security_level": 3,
                "public_key_size_bytes": 1184,
                "ciphertext_size_bytes": 1088,
                "shared_secret_size_bytes": 32,
                "recommended": True,
            },
            {
                "name": "ML-KEM-1024",
                "nist_standard": "FIPS 203",
                "security_level": 5,
                "public_key_size_bytes": 1568,
                "ciphertext_size_bytes": 1568,
                "shared_secret_size_bytes": 32,
                "recommended": False,
                "note": "Para datos ultra-sensibles (gobierno, defensa)",
            },
        ],
        "signature": [
            {
                "name": "ML-DSA-65",
                "nist_standard": "FIPS 204",
                "security_level": 3,
                "public_key_size_bytes": 1952,
                "signature_size_bytes": 3293,
                "recommended": True,
            },
        ],
        "hybrid_mode": settings.HYBRID_MODE,
        "classical_supplement": "X25519 (always active in hybrid mode)",
    }


@router.post(
    "/sign",
    response_model=SignResponse,
    summary="Firmar datos con ML-DSA-65",
    description=(
        "Firma datos arbitrarios con ML-DSA-65. "
        "Genera un keypair efímero, firma los datos y retorna la firma + llave PÚBLICA. "
        "La firma resultante es verificable a perpetuidad, "
        "independiente de futuros avances en computación cuántica."
    ),
)
async def sign_data(
    request: SignRequest,
    _api_key: Annotated[str, Depends(verify_api_key)],
) -> SignResponse:
    """
    Firma datos con ML-DSA-65.
    Genera un keypair efímero, firma los datos, y retorna firma + llave pública.
    Las llaves privadas NUNCA viajan por la API.
    """
    with tracer.start_as_current_span("crypto.api.sign") as span:
        span.set_attribute("nivo.pqc_algorithm", settings.PQC_SIGNATURE_ALGORITHM)
        # Validar que el request no contiene claves privadas
        extra_fields = set((request.model_extra or {}).keys())
        if any(
            ("private" in field.lower())
            or ("secret" in field.lower())
            or ("signing" in field.lower() and "key" in field.lower())
            for field in extra_fields
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las llaves privadas NUNCA deben enviarse en esta API. Use HSM/KMS.",
            )

        try:
            data = bytes.fromhex(request.data_hex)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los datos deben estar en formato hex válido",
            )

        # Generar keypair efímero ML-DSA-65.
        # Diseñado para migración a HSM (GCP/AWS KMS) sin cambios en llamadores:
        # en producción, generate_signing_keypair() delegará a KMS y signing_secret_key
        # será un handle opaco nunca materializado en memoria (ver ADR-003 pendiente).
        signing_kp = crypto.generate_signing_keypair()
        signed = crypto.sign_transaction(
            tx_id="b2b_api",
            payload=data,
            signing_secret_key=signing_kp.secret_key,
            public_key_fingerprint=signing_kp.public_key_fingerprint,
        )
        span.set_attribute("nivo.data_size_bytes", len(data))

        return SignResponse(
            signature_hex=signed.signature.hex(),
            public_key_hex=signing_kp.public_key.hex(),
            public_key_fingerprint=signed.public_key_fingerprint,
        )


@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Verificar firma ML-DSA-65",
)
async def verify_signature(
    request: VerifyRequest,
    _api_key: Annotated[str, Depends(verify_api_key)],
) -> VerifyResponse:
    """Verifica que una firma ML-DSA-65 sea válida para los datos dados."""
    try:
        from app.crypto.service import SignedTransaction
        data = bytes.fromhex(request.data_hex)
        signature = bytes.fromhex(request.signature_hex)
        public_key = bytes.fromhex(request.public_key_hex)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Todos los campos deben estar en formato hex",
        )

    import hashlib
    signed_tx = SignedTransaction(
        tx_id="verify_request",
        payload=data,
        signature=signature,
        public_key_fingerprint=hashlib.sha256(public_key).hexdigest(),
    )
    valid = crypto.verify_transaction_signature(signed_tx, public_key)

    return VerifyResponse(valid=valid)
