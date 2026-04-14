"""Nivo — Unit tests for CryptoService."""

from __future__ import annotations
import pytest

from app.crypto.service import CryptoService


@pytest.fixture
def crypto():
    """Fixture: instancia de CryptoService."""
    return CryptoService()


# ─── Tests de Firma ML-DSA-65 ─────────────────────────────────────────────────

class TestMLDSASignatures:
    """Tests para firma y verificación con ML-DSA-65."""

    def test_sign_and_verify_returns_true(self, crypto):
        """Verifica que una firma válida retorna True."""
        kp = crypto.generate_signing_keypair()
        payload = b"test message"

        signed = crypto.sign_transaction(
            tx_id="test1",
            payload=payload,
            signing_secret_key=kp.secret_key,
            public_key_fingerprint=kp.public_key_fingerprint,
        )

        is_valid = crypto.verify_transaction_signature(signed, kp.public_key)
        assert is_valid is True

    def test_verify_with_wrong_public_key_returns_false(self, crypto):
        """Verifica que una firma con llave pública incorrecta retorna False."""
        kp1 = crypto.generate_signing_keypair()
        kp2 = crypto.generate_signing_keypair()
        payload = b"test message"

        signed = crypto.sign_transaction(
            tx_id="test2",
            payload=payload,
            signing_secret_key=kp1.secret_key,
            public_key_fingerprint=kp1.public_key_fingerprint,
        )

        # Verificar con llave pública diferente
        is_valid = crypto.verify_transaction_signature(signed, kp2.public_key)
        assert is_valid is False

    def test_verify_with_tampered_payload_returns_false(self, crypto):
        """Verifica que alterar el payload invalida la firma."""
        kp = crypto.generate_signing_keypair()
        payload = b"original message"

        signed = crypto.sign_transaction(
            tx_id="test3",
            payload=payload,
            signing_secret_key=kp.secret_key,
            public_key_fingerprint=kp.public_key_fingerprint,
        )

        # Alterar el payload en el objeto SignedTransaction
        from app.crypto.service import SignedTransaction
        tampered = SignedTransaction(
            tx_id=signed.tx_id,
            payload=b"tampered message",
            signature=signed.signature,
            public_key_fingerprint=signed.public_key_fingerprint,
        )

        is_valid = crypto.verify_transaction_signature(tampered, kp.public_key)
        assert is_valid is False

    def test_verify_with_truncated_signature_returns_false(self, crypto):
        """Verifica que una firma truncada es inválida."""
        kp = crypto.generate_signing_keypair()
        payload = b"test message"

        signed = crypto.sign_transaction(
            tx_id="test4",
            payload=payload,
            signing_secret_key=kp.secret_key,
            public_key_fingerprint=kp.public_key_fingerprint,
        )

        # Truncar firma
        from app.crypto.service import SignedTransaction
        truncated = SignedTransaction(
            tx_id=signed.tx_id,
            payload=payload,
            signature=signed.signature[:-10],  # Remover últimos 10 bytes
            public_key_fingerprint=signed.public_key_fingerprint,
        )

        is_valid = crypto.verify_transaction_signature(truncated, kp.public_key)
        assert is_valid is False

    def test_sign_empty_payload(self, crypto):
        """Verifica que se pueden firmar payloads vacíos."""
        kp = crypto.generate_signing_keypair()
        payload = b""

        signed = crypto.sign_transaction(
            tx_id="test5",
            payload=payload,
            signing_secret_key=kp.secret_key,
            public_key_fingerprint=kp.public_key_fingerprint,
        )

        is_valid = crypto.verify_transaction_signature(signed, kp.public_key)
        assert is_valid is True

    def test_sign_large_payload_1mb(self, crypto):
        """Verifica que se pueden firmar payloads grandes (1 MB)."""
        kp = crypto.generate_signing_keypair()
        payload = b"x" * (1024 * 1024)  # 1 MB

        signed = crypto.sign_transaction(
            tx_id="test6",
            payload=payload,
            signing_secret_key=kp.secret_key,
            public_key_fingerprint=kp.public_key_fingerprint,
        )

        is_valid = crypto.verify_transaction_signature(signed, kp.public_key)
        assert is_valid is True

    def test_public_key_fingerprint_is_64_chars_hex(self, crypto):
        """Verifica que el fingerprint es SHA-256 hex (64 caracteres)."""
        kp = crypto.generate_signing_keypair()

        # 64 caracteres hex es SHA-256
        assert len(kp.public_key_fingerprint) == 64
        # Verificar que es hexadecimal válido
        int(kp.public_key_fingerprint, 16)  # Esto lanzaría ValueError si no es hex

    def test_two_different_payloads_have_different_signatures(self, crypto):
        """Verifica que payloads diferentes generan firmas diferentes."""
        kp = crypto.generate_signing_keypair()

        signed1 = crypto.sign_transaction(
            tx_id="test7a",
            payload=b"payload1",
            signing_secret_key=kp.secret_key,
            public_key_fingerprint=kp.public_key_fingerprint,
        )

        signed2 = crypto.sign_transaction(
            tx_id="test7b",
            payload=b"payload2",
            signing_secret_key=kp.secret_key,
            public_key_fingerprint=kp.public_key_fingerprint,
        )

        assert signed1.signature != signed2.signature


# ─── Tests de Key Exchange ML-KEM ──────────────────────────────────────────────

class TestMLKEMKeyExchange:
    """Tests para encapsulación/desencapsulación ML-KEM."""

    def test_generate_kem_keypair_returns_valid_sizes(self, crypto):
        """Verifica que los tamaños de llave KEM son válidos."""
        kp = crypto.generate_kem_keypair()

        # ML-KEM-768: public_key=1184 bytes, secret_key=2400 bytes
        assert len(kp.public_key) > 0
        assert len(kp.secret_key) > 0
        assert kp.algorithm == "ML-KEM-768"

    def test_hybrid_encapsulate_returns_32_byte_secret(self, crypto):
        """Verifica que el shared_secret derivado tiene 32 bytes."""
        kem_kp = crypto.generate_kem_keypair()

        # X25519 para el lado clásico
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        x25519_private = X25519PrivateKey.generate()
        x25519_public = x25519_private.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )

        encap = crypto.hybrid_encapsulate(kem_kp.public_key, x25519_public)

        assert len(encap.shared_secret) == 32
        assert len(encap.pqc_ciphertext) > 0
        assert len(encap.classical_public_key) == 32  # X25519 public key

    def test_hybrid_encapsulate_decapsulate_same_secret(self, crypto):
        """Verifica que encapsulate/decapsulate producen el mismo secret."""
        kem_kp = crypto.generate_kem_keypair()

        # X25519
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        x25519_private = X25519PrivateKey.generate()
        x25519_public = x25519_private.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )

        # Encapsulate
        encap = crypto.hybrid_encapsulate(kem_kp.public_key, x25519_public)

        # Decapsulate
        decap_secret = crypto.hybrid_decapsulate(
            encap.pqc_ciphertext,
            kem_kp.secret_key,
            encap.classical_public_key,
            x25519_private.private_bytes(
                serialization.Encoding.Raw,
                serialization.PrivateFormat.Raw,
                serialization.NoEncryption(),
            ),
        )

        assert encap.shared_secret == decap_secret


# ─── Tests de Cifrado AES-GCM ─────────────────────────────────────────────────

class TestAESGCMEncryption:
    """Tests para cifrado y descifrado AES-256-GCM."""

    def test_encrypt_decrypt_roundtrip(self, crypto):
        """Verifica que encrypt/decrypt produce el plaintext original."""
        import os
        key = os.urandom(32)  # AES-256
        plaintext = b"mensaje secreto de Nivo"

        ciphertext, nonce = crypto.encrypt(plaintext, key)
        decrypted = crypto.decrypt(ciphertext, key, nonce)

        assert decrypted == plaintext

    def test_decrypt_with_wrong_key_raises_error(self, crypto):
        """Verifica que descifrar con llave incorrecta lanza error."""
        import os
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        plaintext = b"mensaje secreto"

        ciphertext, nonce = crypto.encrypt(plaintext, key1)

        with pytest.raises(Exception):  # cryptography.hazmat lanza InvalidTag
            crypto.decrypt(ciphertext, key2, nonce)

    def test_decrypt_with_wrong_nonce_raises_error(self, crypto):
        """Verifica que descifrar con nonce incorrecto lanza error."""
        import os
        key = os.urandom(32)
        plaintext = b"mensaje secreto"

        ciphertext, nonce = crypto.encrypt(plaintext, key)
        wrong_nonce = os.urandom(12)

        with pytest.raises(Exception):
            crypto.decrypt(ciphertext, key, wrong_nonce)

    def test_encrypt_produces_different_nonces(self, crypto):
        """Verifica que cada encriptación produce un nonce diferente."""
        import os
        key = os.urandom(32)
        plaintext = b"mensaje"

        _, nonce1 = crypto.encrypt(plaintext, key)
        _, nonce2 = crypto.encrypt(plaintext, key)

        assert nonce1 != nonce2


# ─── Tests de Health Check ────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestHealthCheck:
    """Tests para verificación de integridad del módulo PQC."""

    async def test_health_check_returns_true(self, crypto):
        """Verifica que health_check retorna True."""
        result = await crypto.health_check()
        assert result is True

    async def test_health_check_completes_under_2000ms(self, crypto):
        """Verifica que health_check completa en menos de 2 segundos."""
        import time
        start = time.time()
        await crypto.health_check()
        elapsed = (time.time() - start) * 1000
        assert elapsed < 2000


# ─── Tests de Agilidad Criptográfica ──────────────────────────────────────────

class TestCryptoAgility:
    """Tests para verificar que los algoritmos vienen de settings."""

    def test_algorithm_names_come_from_config(self, crypto):
        """Verifica que KEM y SIG algorithms vienen de settings."""
        from app.core.config import settings

        assert crypto.KEM_ALGORITHM == settings.PQC_ALGORITHM
        assert crypto.SIG_ALGORITHM == settings.PQC_SIGNATURE_ALGORITHM
