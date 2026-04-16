### TASK-004 — Tests Unitarios del Módulo CryptoService
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 4–5 horas
**Prioridad:** CRÍTICA

**Descripción:**
El módulo `app/crypto/service.py` es el corazón de Nivo. Necesita cobertura de tests
exhaustiva ≥ 90% incluyendo casos negativos (signatures alteradas, claves incorrectas).

**Archivos a crear:**
- CREAR `backend/tests/test_crypto_service.py`
- CREAR `backend/tests/conftest.py` — Fixtures compartidas
- CREAR `backend/tests/__init__.py`

**Tests requeridos (mínimo):**

```python
# test_crypto_service.py

class TestMLDSASignatures:
    def test_sign_and_verify_returns_true()
    def test_verify_with_wrong_public_key_returns_false()
    def test_verify_with_tampered_payload_returns_false()
    def test_verify_with_truncated_signature_returns_false()
    def test_sign_empty_payload()
    def test_sign_large_payload_1mb()
    def test_public_key_fingerprint_is_64_chars_hex()
    def test_two_different_payloads_have_different_signatures()

class TestMLKEMKeyExchange:
    def test_generate_kem_keypair_returns_valid_sizes()
    def test_hybrid_encapsulate_returns_32_byte_secret()
    def test_hybrid_encapsulate_decapsulate_same_secret()
    def test_encapsulate_with_wrong_key_raises_error()

class TestAESGCMEncryption:
    def test_encrypt_decrypt_roundtrip()
    def test_decrypt_with_wrong_key_raises_error()
    def test_decrypt_with_wrong_nonce_raises_error()
    def test_encrypt_produces_different_nonces()

class TestHealthCheck:
    async def test_health_check_returns_true()
    async def test_health_check_completes_under_500ms()

class TestCryptoAgility:
    """Verificar que cambiar algoritmos no rompe la interfaz."""
    def test_service_interface_stable()
```

**Criterios de éxito:**
- [ ] `pytest tests/test_crypto_service.py -v` — todos los tests pasan
- [ ] `pytest --cov=app/crypto --cov-report=term-missing` — cobertura ≥ 90%
- [ ] Tests corren en < 30 segundos (sin liboqs, en modo mock)
- [ ] `test_verify_with_tampered_payload_returns_false` DEBE pasar — es la prueba más importante

**Dependencias:** Ninguna (CryptoService ya existe)

