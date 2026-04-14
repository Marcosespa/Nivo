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

from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel

from app.core.config import settings
from app.crypto.service import CryptoService

router = APIRouter()
crypto = CryptoService()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class KeyExchangeRequest(BaseModel):
    recipient_pqc_public_key_hex: str    # Llave pública ML-KEM del receptor
    recipient_x25519_public_key_hex: str  # Llave pública X25519 del receptor


class KeyExchangeResponse(BaseModel):
    pqc_ciphertext_hex: str          # Texto cifrado ML-KEM para enviar al receptor
    classical_public_key_hex: str    # Llave pública X25519 efímera del emisor
    algorithm: str = "ML-KEM-768 + X25519 (hybrid)"
    shared_secret_hex: str           # SOLO para debug — en producción NO incluir


class SignRequest(BaseModel):
    data_hex: str           # Datos a firmar (hex)
    signing_key_hex: str    # Llave privada ML-DSA-65 (hex) — nunca almacenar aquí


class SignResponse(BaseModel):
    signature_hex: str
    public_key_fingerprint: str
    algorithm: str = "ML-DSA-65"


class VerifyRequest(BaseModel):
    data_hex: str
    signature_hex: str
    public_key_hex: str


class VerifyResponse(BaseModel):
    valid: bool
    algorithm: str = "ML-DSA-65"


# ─── Dependencia de API Key ───────────────────────────────────────────────────

async def verify_api_key(x_Nivo_key: str = Header(...)):
    """Verifica la API key del cliente B2B."""
    # TODO: verificar key contra BD de clientes B2B
    # TODO: verificar límites de rate y billing
    if not x_Nivo_key or len(x_Nivo_key) < 32:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida. Obtén tu key en dashboard.Nivo.co",
        )
    return x_Nivo_key


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "/algorithms",
    summary="Algoritmos PQC soportados",
)
async def list_algorithms():
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
        "La firma resultante es verificable a perpetuidad, "
        "independiente de futuros avances en computación cuántica."
    ),
)
async def sign_data(request: SignRequest) -> SignResponse:
    """Firma datos con ML-DSA-65."""
    try:
        data = bytes.fromhex(request.data_hex)
        signing_key = bytes.fromhex(request.signing_key_hex)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los datos y la llave deben estar en formato hex",
        )

    # Generar keypair temporal para derivar public_key_fingerprint
    # En producción, el cliente maneja sus propias llaves
    import hashlib
    pk_mock = bytes.fromhex(request.signing_key_hex[:64])

    signed = crypto.sign_transaction(
        tx_id="b2b_api",
        payload=data,
        signing_secret_key=signing_key,
        public_key_fingerprint=hashlib.sha256(pk_mock).hexdigest(),
    )

    return SignResponse(
        signature_hex=signed.signature.hex(),
        public_key_fingerprint=signed.public_key_fingerprint,
    )


@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Verificar firma ML-DSA-65",
)
async def verify_signature(request: VerifyRequest) -> VerifyResponse:
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
