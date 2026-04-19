"""
Nivo CryptoService — Módulo de Criptografía Post-Cuántica

PRINCIPIO DE CRYPTO-AGILIDAD:
Ningún otro módulo importa liboqs directamente.
Todo pasa por esta interfaz. Si NIST cambia el estándar,
solo se modifica este archivo — el resto de la app no se toca.

Algoritmos:
  - ML-KEM-768 (FIPS 203): intercambio de llaves post-cuántico
  - ML-DSA-65 (FIPS 204): firma digital post-cuántica
  - X25519: intercambio clásico (modo híbrido)
  - AES-256-GCM: cifrado simétrico con llave derivada
  - HKDF-SHA256: derivación de llave combinada híbrida
"""

import os
import hashlib
import hmac
from dataclasses import dataclass
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from opentelemetry import trace

_tracer = trace.get_tracer(__name__)

# Import condicional de liboqs
# En producción, liboqs debe estar instalado.
# En CI sin liboqs, se usa modo de simulación (solo para tests).
try:
    import oqs
    LIBOQS_AVAILABLE = True
except ImportError:
    LIBOQS_AVAILABLE = False
    import warnings
    warnings.warn(
        "liboqs no está instalado. Usando modo simulación para PQC. "
        "NO USAR EN PRODUCCIÓN.",
        RuntimeWarning,
        stacklevel=2,
    )


# ─── Modelos de datos ─────────────────────────────────────────────────────────

@dataclass
class PQCKeyPair:
    """Par de llaves post-cuántico (pública + privada)."""
    algorithm: str
    public_key: bytes
    secret_key: bytes
    public_key_fingerprint: str  # SHA-256 hex de la llave pública


@dataclass
class HybridEncapsulation:
    """
    Resultado de una encapsulación híbrida.
    Contiene los datos necesarios para que el receptor derive la misma llave.
    """
    pqc_ciphertext: bytes          # Texto cifrado ML-KEM (enviar al receptor)
    classical_public_key: bytes    # Llave pública X25519 efímera (enviar al receptor)
    shared_secret: bytes           # Secreto compartido derivado (NO enviar — es la llave)


@dataclass
class SignedTransaction:
    """Transacción firmada con ML-DSA-65."""
    tx_id: str
    payload: bytes
    signature: bytes
    public_key_fingerprint: str
    algorithm: str = "ML-DSA-65"


# ─── CryptoService ────────────────────────────────────────────────────────────

class CryptoService:
    """
    Servicio central de criptografía post-cuántica de Nivo.

    Uso:
        service = CryptoService()

        # Generar llave de firma para un usuario
        signing_key = service.generate_signing_keypair()

        # Firmar transacción
        signed_tx = service.sign_transaction(tx_id, payload, signing_key.secret_key)

        # Verificar firma
        valid = service.verify_signature(signed_tx, signing_key.public_key)

        # Establecer canal seguro (key exchange híbrido)
        encap = service.hybrid_encapsulate(recipient_pqc_public_key, recipient_x25519_public_key)
        session_key = encap.shared_secret  # usar para AES-256-GCM
    """

    def __init__(self):
        from app.core.config import settings
        self.KEM_ALGORITHM = settings.PQC_ALGORITHM
        self.SIG_ALGORITHM = settings.PQC_SIGNATURE_ALGORITHM
        self._liboqs_available = LIBOQS_AVAILABLE

    # ─── Generación de llaves ─────────────────────────────────────────────────

    def generate_kem_keypair(self) -> PQCKeyPair:
        """
        Genera un par de llaves ML-KEM-768 para intercambio de llaves.
        Usar para: handshake inicial, establecer canal seguro.
        """
        if not self._liboqs_available:
            return self._mock_keypair(self.KEM_ALGORITHM)

        with oqs.KeyEncapsulation(self.KEM_ALGORITHM) as kem:
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()

        return PQCKeyPair(
            algorithm=self.KEM_ALGORITHM,
            public_key=public_key,
            secret_key=secret_key,
            public_key_fingerprint=self._fingerprint(public_key),
        )

    def generate_signing_keypair(self) -> PQCKeyPair:
        """
        Genera un par de llaves ML-DSA-65 para firma de transacciones.
        Usar para: firmar pagos, comprobantes, y documentos financieros.
        """
        if not self._liboqs_available:
            return self._mock_keypair(self.SIG_ALGORITHM)

        with oqs.Signature(self.SIG_ALGORITHM) as signer:
            public_key = signer.generate_keypair()
            secret_key = signer.export_secret_key()

        return PQCKeyPair(
            algorithm=self.SIG_ALGORITHM,
            public_key=public_key,
            secret_key=secret_key,
            public_key_fingerprint=self._fingerprint(public_key),
        )

    # ─── Key Exchange Híbrido (ML-KEM-768 + X25519) ───────────────────────────

    def hybrid_encapsulate(
        self,
        recipient_pqc_public_key: bytes,
        recipient_x25519_public_key: bytes,
    ) -> HybridEncapsulation:
        """
        Encapsulación híbrida: ML-KEM-768 + X25519 simultáneo.

        Produce un shared_secret que es seguro si CUALQUIERA de los dos
        algoritmos permanece seguro (seguridad composicional).

        El pqc_ciphertext y classical_public_key deben enviarse al receptor.
        El shared_secret es la llave de sesión AES-256-GCM.
        """
        # 1. ML-KEM-768 encapsulate
        if self._liboqs_available:
            with oqs.KeyEncapsulation(self.KEM_ALGORITHM) as kem:
                pqc_ciphertext, pqc_shared_secret = kem.encap_secret(
                    recipient_pqc_public_key
                )
        else:
            # Simulación: el ciphertext es aleatorio pero el shared secret
            # se deriva deterministicamente de él, igual que en KEM real.
            pqc_ciphertext = os.urandom(1088)   # tamaño real ML-KEM-768
            pqc_shared_secret = hashlib.sha256(pqc_ciphertext).digest()

        # 2. X25519 Diffie-Hellman efímero
        my_x25519_private = X25519PrivateKey.generate()
        my_x25519_public = my_x25519_private.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
        recipient_x25519 = X25519PublicKey.from_public_bytes(recipient_x25519_public_key)
        classical_shared_secret = my_x25519_private.exchange(recipient_x25519)

        # 3. Combinar con HKDF-SHA256 (ver ADR-002)
        combined = self._derive_hybrid_key(pqc_shared_secret, classical_shared_secret)

        return HybridEncapsulation(
            pqc_ciphertext=pqc_ciphertext,
            classical_public_key=my_x25519_public,
            shared_secret=combined,
        )

    def hybrid_decapsulate(
        self,
        pqc_ciphertext: bytes,
        pqc_secret_key: bytes,
        sender_x25519_public_key: bytes,
        my_x25519_private_key: bytes,
    ) -> bytes:
        """
        Decapsulación híbrida en el receptor.
        Reproduce el mismo shared_secret que el emisor calculó.
        """
        # 1. ML-KEM-768 decapsulate
        if self._liboqs_available:
            with oqs.KeyEncapsulation(self.KEM_ALGORITHM, pqc_secret_key) as kem:
                pqc_shared_secret = kem.decap_secret(pqc_ciphertext)
        else:
            # Simulación: derivar el mismo secret que el emisor calculó
            # (en KEM real, el ciphertext contiene el secret cifrado con pk)
            pqc_shared_secret = hashlib.sha256(pqc_ciphertext).digest()

        # 2. X25519 DH
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
        my_private = X25519PrivateKey.from_private_bytes(my_x25519_private_key)
        sender_public = X25519PublicKey.from_public_bytes(sender_x25519_public_key)
        classical_shared_secret = my_private.exchange(sender_public)

        # 3. Derivar la misma llave combinada
        return self._derive_hybrid_key(pqc_shared_secret, classical_shared_secret)

    # ─── Firma de Transacciones (ML-DSA-65) ────────────────────────────────────

    def sign_transaction(
        self,
        tx_id: str,
        payload: bytes,
        signing_secret_key: bytes,
        public_key_fingerprint: str,
    ) -> SignedTransaction:
        """
        Firma una transacción con ML-DSA-65.
        El payload debe incluir: tx_id, monto, timestamp, sender_hash, receiver_hash.

        NOTA: `signing_secret_key` es la llave privada ML-DSA-65. En desarrollo
        viene del keypair efímero generado por `generate_signing_keypair()`.
        En producción este parámetro será reemplazado por un handle opaco a
        GCP/AWS KMS o HashiCorp Vault sin cambiar la firma del método
        (ver ADR-003 pendiente).
        """
        return self.sign(
            tx_id=tx_id,
            payload=payload,
            signing_secret_key=signing_secret_key,
            public_key_fingerprint=public_key_fingerprint,
        )

    # Alias expuesto para tracing de alto nivel (solicitado en plan P1).
    def sign(
        self,
        tx_id: str,
        payload: bytes,
        signing_secret_key: bytes,
        public_key_fingerprint: str,
    ) -> SignedTransaction:
        """Punto único de firma para migrar a HSM/KMS sin romper llamadores."""
        with _tracer.start_as_current_span("crypto.sign") as span:
            span.set_attribute("nivo.tx_id", tx_id)
            span.set_attribute("nivo.algorithm", self.SIG_ALGORITHM)
            span.set_attribute("nivo.payload_size_bytes", len(payload))

            if self._liboqs_available:
                with oqs.Signature(self.SIG_ALGORITHM, signing_secret_key) as signer:
                    signature = signer.sign(payload)
            else:
                hmac_key = hashlib.sha256(signing_secret_key).digest()
                signature = hmac.new(hmac_key, payload, hashlib.sha256).digest()

            return SignedTransaction(
                tx_id=tx_id,
                payload=payload,
                signature=signature,
                public_key_fingerprint=public_key_fingerprint,
            )

    def verify_transaction_signature(
        self,
        signed_tx: SignedTransaction,
        signer_public_key: bytes,
    ) -> bool:
        """
        Verifica la firma ML-DSA-65 de una transacción.
        Retorna True si la firma es válida, False si fue alterada.
        """
        if self._liboqs_available:
            try:
                with oqs.Signature(self.SIG_ALGORITHM) as verifier:
                    return verifier.verify(
                        signed_tx.payload,
                        signed_tx.signature,
                        signer_public_key,
                    )
            except Exception:
                return False
        else:
            # Simulación: pk = SHA256(sk), usamos pk directamente como clave HMAC.
            # El firmador usó SHA256(sk) como clave, y pk == SHA256(sk), así que coincide.
            expected = hmac.new(signer_public_key, signed_tx.payload, hashlib.sha256).digest()
            return hmac.compare_digest(expected, signed_tx.signature)

    # ─── Cifrado Simétrico (AES-256-GCM) ─────────────────────────────────────

    def encrypt(self, plaintext: bytes, key: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
        """
        Cifra con AES-256-GCM usando una llave de 32 bytes (derivada del key exchange híbrido).
        Retorna (ciphertext, nonce). El nonce debe almacenarse junto al ciphertext.
        """
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, aad or None)
        return ciphertext, nonce

    def decrypt(
        self, ciphertext: bytes, key: bytes, nonce: bytes, aad: bytes = b""
    ) -> bytes:
        """Descifra con AES-256-GCM."""
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, aad or None)

    # ─── Health Check ─────────────────────────────────────────────────────────

    async def health_check(self) -> bool:
        """
        Verifica que el módulo PQC funcione correctamente.
        Se ejecuta al arrancar la app y cada 60 segundos en producción.
        """
        try:
            # Test de roundtrip: generar llaves, firmar, verificar
            signing_kp = self.generate_signing_keypair()
            test_payload = b"Nivo_pqc_health_check_v1"

            signed = self.sign_transaction(
                tx_id="health_check",
                payload=test_payload,
                signing_secret_key=signing_kp.secret_key,
                public_key_fingerprint=signing_kp.public_key_fingerprint,
            )
            valid = self.verify_transaction_signature(signed, signing_kp.public_key)

            if not valid:
                return False

            # Test de roundtrip KEM (opcional, requiere liboqs)
            if self._liboqs_available:
                kem_kp = self.generate_kem_keypair()
                x25519_private = X25519PrivateKey.generate()
                x25519_public = x25519_private.public_key().public_bytes(
                    serialization.Encoding.Raw,
                    serialization.PublicFormat.Raw,
                )
                encap = self.hybrid_encapsulate(kem_kp.public_key, x25519_public)
                if len(encap.shared_secret) != 32:
                    return False

            return True

        except Exception as e:
            print(f"❌ PQC health check failed: {e}")
            return False

    # ─── Utilidades privadas ──────────────────────────────────────────────────

    def _fingerprint(self, public_key: bytes) -> str:
        """SHA-256 hex de una llave pública — identificador único de 64 chars."""
        return hashlib.sha256(public_key).hexdigest()

    def _derive_hybrid_key(
        self,
        pqc_secret: bytes,
        classical_secret: bytes,
        info: bytes = b"Nivo-hybrid-v1",
    ) -> bytes:
        """
        Combina los dos shared secrets en una única llave de 32 bytes con HKDF-SHA256.
        Si cualquiera de los dos algoritmos es seguro, la llave resultante es segura.
        """
        combined_ikm = pqc_secret + classical_secret
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=info,
        )
        return hkdf.derive(combined_ikm)

    def _mock_keypair(self, algorithm: str) -> PQCKeyPair:
        """
        Llave simulada para entornos sin liboqs (solo desarrollo/CI).

        Invariante de simulación:
          pk = SHA256(sk)  →  permite sign/verify consistentes con HMAC(pk, payload).
        """
        sk = os.urandom(64)
        pk = hashlib.sha256(sk).digest()  # pk determinista a partir de sk
        return PQCKeyPair(
            algorithm=algorithm,
            public_key=pk,
            secret_key=sk,
            public_key_fingerprint=self._fingerprint(pk),
        )
