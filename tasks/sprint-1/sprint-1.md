## MES 1 — SPRINT 1 (Semanas 1–2): Fundaciones Técnicas

---

### TASK-001 — Configurar Base de Datos con SQLAlchemy ORM
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 4–6 horas
**Prioridad:** CRÍTICA

**Descripción:**
Crear todos los modelos ORM de SQLAlchemy para las tablas principales de Nivo.
Actualmente solo existen modelos Pydantic. Se necesitan los modelos SQLAlchemy completos
con relaciones, constraints, e índices.

**Archivos a crear/modificar:**
- CREAR `backend/app/models/orm/user.py` — Modelo SQLAlchemy de usuarios
- CREAR `backend/app/models/orm/wallet.py` — Modelo SQLAlchemy de billeteras/cuenta visual
- CREAR `backend/app/models/orm/savings_pocket.py` — Bolsillos de ahorro/metas
- CREAR `backend/app/models/orm/transaction.py` — Modelo SQLAlchemy de transacciones
- CREAR `backend/app/models/orm/partner_order.py` — Órdenes FX/crypto/acciones por partner
- CREAR `backend/app/models/orm/product_disclosure.py` — Versiones de disclosures aceptados
- CREAR `backend/app/models/orm/pqc_key.py` — Modelo SQLAlchemy de llaves PQC
- CREAR `backend/app/models/orm/merchant.py` — Modelo SQLAlchemy de comercios
- CREAR `backend/app/models/orm/otp.py` — Modelo SQLAlchemy de OTPs (con TTL)
- CREAR `backend/alembic.ini` — Configuración de Alembic para migraciones
- CREAR `backend/alembic/env.py` — Entorno de migraciones
- CREAR `backend/alembic/versions/0001_initial_schema.py` — Primera migración

**Especificaciones exactas de cada tabla:**

```python
# users
id: UUID PK
phone_number: VARCHAR(15) UNIQUE NOT NULL
email: VARCHAR(255) UNIQUE NULLABLE
full_name: VARCHAR(255) NULLABLE
plan: ENUM('free','plus','pro') DEFAULT 'free'
kyc_status: ENUM('pending','verified','rejected') DEFAULT 'pending'
is_active: BOOLEAN DEFAULT TRUE
created_at: TIMESTAMPTZ DEFAULT NOW()
updated_at: TIMESTAMPTZ DEFAULT NOW()

# wallets
id: UUID PK
user_id: UUID FK -> users.id UNIQUE
display_balance_cop: BIGINT DEFAULT 0  # cache visual en centavos; no ledger legal si MVP sin custodia
currency: VARCHAR(3) DEFAULT 'COP'
custody_mode: ENUM('visual_only','partner_ledger','sedpe','bank_partner') DEFAULT 'visual_only'
provider_account_ref: VARCHAR(120) NULLABLE
is_frozen: BOOLEAN DEFAULT FALSE
last_updated: TIMESTAMPTZ DEFAULT NOW()
CONSTRAINT: display_balance_cop >= 0

# savings_pockets
id: UUID PK
user_id: UUID FK -> users.id
name: VARCHAR(80) NOT NULL
target_amount_cop: BIGINT NULLABLE
display_balance_cop: BIGINT DEFAULT 0
provider_subaccount_ref: VARCHAR(120) NULLABLE  # solo si banco/SEDPE/partner soporta subcuentas reales
mode: ENUM('visual_goal','partner_subaccount','custodial') DEFAULT 'visual_goal'
ml_dsa_last_state_signature: BYTEA NULLABLE
created_at: TIMESTAMPTZ DEFAULT NOW()

# partner_orders
id: UUID PK
user_id: UUID FK -> users.id
product_type: ENUM('fx','crypto','stock','etf') NOT NULL
partner: VARCHAR(80) NOT NULL
partner_order_id: VARCHAR(120) NULLABLE
instrument_symbol: VARCHAR(30) NOT NULL
side: ENUM('buy','sell','convert') NOT NULL
notional_amount: BIGINT NOT NULL
source_currency: VARCHAR(10)
target_currency: VARCHAR(10)
execution_status: ENUM('pending','submitted','executed','failed','cancelled') DEFAULT 'pending'
risk_disclosure_version: VARCHAR(30) NOT NULL
accepted_disclosure_hash: VARCHAR(64) NOT NULL
signed_order_payload: BYTEA NOT NULL
ml_dsa_signature: BYTEA NOT NULL
created_at: TIMESTAMPTZ DEFAULT NOW()
executed_at: TIMESTAMPTZ NULLABLE

# transactions
id: UUID PK
sender_id: UUID FK -> users.id
receiver_id: UUID FK -> users.id
amount_cop: BIGINT NOT NULL  # centavos
status: ENUM('pending','pending_confirmation','completed','failed','reversed')
ml_dsa_signature: BYTEA NOT NULL
signature_key_id: UUID FK -> pqc_keys.id
message: VARCHAR(500) NULLABLE
metadata_encrypted: BYTEA NULLABLE  # AES-256-GCM
created_at: TIMESTAMPTZ DEFAULT NOW()
confirmed_at: TIMESTAMPTZ NULLABLE
CONSTRAINT: amount_cop > 0
INDEX: (sender_id, created_at DESC)
INDEX: (receiver_id, created_at DESC)
INDEX: (status)

# pqc_keys
id: UUID PK
user_id: UUID FK -> users.id
algorithm: VARCHAR(30) NOT NULL  # 'ML-KEM-768' o 'ML-DSA-65'
public_key: BYTEA NOT NULL
key_fingerprint: VARCHAR(64) UNIQUE NOT NULL  # SHA-256 hex
created_at: TIMESTAMPTZ DEFAULT NOW()
expires_at: TIMESTAMPTZ NULLABLE
is_active: BOOLEAN DEFAULT TRUE
INDEX: (user_id, algorithm, is_active)

# merchants
id: UUID PK
owner_id: UUID FK -> users.id
business_name: VARCHAR(255) NOT NULL
nit: VARCHAR(20) UNIQUE NULLABLE
plan: ENUM('basic','pro','enterprise') DEFAULT 'basic'
qr_code_signature: BYTEA  # Firma ML-DSA-65 del QR estático
is_active: BOOLEAN DEFAULT TRUE
created_at: TIMESTAMPTZ DEFAULT NOW()

# otps
id: UUID PK
phone_number: VARCHAR(15) NOT NULL
otp_hash: VARCHAR(64) NOT NULL  # hash del OTP; en el flujo activo se usa HMAC-SHA256 en Redis, nunca en plano
purpose: ENUM('login','payment','kyc')
used: BOOLEAN DEFAULT FALSE
expires_at: TIMESTAMPTZ NOT NULL
created_at: TIMESTAMPTZ DEFAULT NOW()
INDEX: (phone_number, expires_at)
```

**Criterios de éxito:**
- [ ] `python -c "from app.models.orm.user import User; print('OK')"` no lanza errores
- [ ] `alembic upgrade head` crea todas las tablas sin errores
- [ ] Todas las foreign keys tienen `ondelete="CASCADE"` o `ondelete="RESTRICT"` explícito
- [ ] El constraint `display_balance_cop >= 0` está en la BD (no solo en Python)
- [ ] `wallets.custody_mode` permite distinguir meta visual, ledger de partner, banco aliado y SEDPE
- [ ] `partner_orders` puede registrar FX, crypto, acciones y ETFs sin convertir a Nivo en broker/exchange propio

**Dependencias:** Ninguna

---

### TASK-002 — Implementar JWT Real y Autenticación Completa
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** CRÍTICA

**Descripción:**
Actualmente `app/core/security.py` tiene un usuario mock. Implementar JWT real con
access + refresh tokens, blacklist en Redis, y la dependencia `get_current_user` funcional.

**Archivos a crear/modificar:**
- MODIFICAR `backend/app/core/security.py` — Implementar JWT real
- MODIFICAR `backend/app/api/v1/auth.py` — Conectar con BD y Redis reales
- CREAR `backend/app/services/auth_service.py` — Lógica de negocio de auth
- CREAR `backend/app/services/otp_service.py` — Generación y verificación de OTP

**Especificaciones:**

```python
# Estructura del JWT payload
{
    "sub": "user_uuid",         # user.id
    "phone": "+57310xxxxxxx",   # para referencia rápida sin BD hit
    "plan": "free",             # plan del usuario
    "jti": "uuid",              # JWT ID único para blacklist
    "exp": timestamp,
    "iat": timestamp,
    "type": "access" | "refresh"
}

# OTP
- 6 dígitos numéricos
- Generado con secrets.randbelow(1000000)
- Almacenado como HMAC-SHA256 del OTP en Redis con key: f"otp:{phone_number}:{purpose}"
- TTL: 300 segundos (5 minutos)
- Máximo 3 intentos fallidos antes de invalidar (contador en Redis)
- Rate limit: máximo 3 OTPs por teléfono por hora

# Refresh token rotation
- Al usar refresh token, se emite nuevo par (access + refresh)
- El refresh token usado se agrega a blacklist en Redis
- Key de blacklist: f"blacklist:jti:{jti}" con TTL = tiempo restante del token
```

**Criterios de éxito:**
- [ ] `POST /api/v1/auth/request-otp` guarda hash en Redis y retorna `expires_in_seconds`
- [ ] `POST /api/v1/auth/verify-otp` con código correcto retorna JWT válido
- [ ] `POST /api/v1/auth/verify-otp` con código incorrecto retorna 401
- [ ] `GET /api/v1/users/me` con JWT válido retorna datos del usuario
- [ ] `GET /api/v1/users/me` con JWT expirado retorna 401
- [ ] `POST /api/v1/auth/logout` invalida el refresh token
- [ ] Test de rate limiting: 4to OTP en 1 hora retorna 429

**Dependencias:** TASK-001 (modelos ORM)

---

### TASK-003 — Implementar Cuenta Nivo, Wallet Visual y Transacciones Atómicas
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** CRÍTICA

**Descripción:**
Implementar el core financiero inicial: cuenta Nivo, wallet visual, referencias de partner,
transacciones P2P atómicas, integración con el módulo PQC para firma de transacciones,
y flujo completo de pago. En MVP sin licencia propia, `wallets` no es el ledger legal:
guarda estado visual, límites, `custody_mode` y referencias del proveedor regulado.

**Archivos a crear/modificar:**
- CREAR `backend/app/services/wallet_service.py` — Operaciones de billetera
- CREAR `backend/app/services/payment_service.py` — Lógica de pagos P2P
- MODIFICAR `backend/app/api/v1/payments.py` — Conectar con servicios reales
- CREAR `backend/app/services/notification_service.py` — Push notifications placeholder

**Especificaciones críticas:**

```python
# payment_service.py — execute_payment() debe ser ATÓMICO

async def execute_payment(
    db: AsyncSession,
    tx_id: str,
    sender_id: str,
    receiver_id: str,
    amount_cop: int,
) -> Transaction:
    """
    DEBE ejecutarse en una sola transacción de BD.
    Si cualquier paso falla, ROLLBACK de todo.

    Pasos:
    1. SELECT sender_wallet FOR UPDATE  (lock para evitar race condition)
    2. Verificar disponibilidad según custody_mode:
       - visual_only: consultar/validar contra provider o rechazar ejecución real
       - partner_ledger/bank_partner/sedpe: validar saldo/referencia autorizada
    3. Verificar límites diarios del usuario (según plan)
    4. Enviar instrucción al rail/partner configurado y obtener provider_reference
    5. Actualizar display_balance_cop solo como cache/estado visual post-conciliación
    6. Construir payload de tx para firma PQC:
       payload = f"tx:{tx_id}|sender:{sender_id}|receiver:{receiver_id}|amount:{amount_cop}|ts:{now_iso}"
    7. Firmar payload con ML-DSA-65 (llave del servidor, no del usuario en MVP)
    8. INSERT INTO transactions (id, sender_id, receiver_id, amount_cop, status='completed',
                                  rail, provider_reference, settlement_status,
                                  ml_dsa_signature, signature_key_id, confirmed_at=now)
    9. COMMIT
    10. (post-commit) Enviar push notification al receptor
    """

# Errores específicos a implementar:
class InsufficientFundsError(Exception): ...
class DailyLimitExceededError(Exception): ...
class ReceiverNotFoundError(Exception): ...
class WalletFrozenError(Exception): ...
class PartnerSettlementError(Exception): ...
class CustodyModeNotExecutableError(Exception): ...
```

**Verificaciones de límites diarios:**
```
Plan FREE:  $500,000 COP/día = 50_000_00 centavos
Plan PLUS:  $5,000,000 COP/día = 500_000_00 centavos
Plan PRO:   $50,000,000 COP/día = 5_000_000_00 centavos
Calcular: SUM(amount_cop) WHERE sender_id=? AND created_at >= today_start AND status='completed'
```

**Criterios de éxito:**
- [ ] Pago P2P completo en < 800ms (medir con `time.perf_counter()`)
- [ ] Si el emisor no tiene disponibilidad confirmada por el partner, retorna 422 con mensaje en español
- [ ] Si hay race condition (dos pagos simultáneos con saldo justo), exactamente uno falla
- [ ] La firma ML-DSA-65 se almacena en la BD para cada transacción
- [ ] Cada transacción completada guarda `rail`, `provider_reference` y `settlement_status`
- [ ] El historial paginado retorna transacciones con su `ml_dsa_signature_fingerprint`

**Dependencias:** TASK-001, TASK-002

---

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

---

### TASK-005 — Integrar Twilio para Envío de OTP
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 3–4 horas
**Prioridad:** ALTA

**Descripción:**
Implementar el envío real de SMS con Twilio. Actualmente el endpoint de OTP no envía nada.

**Archivos a crear/modificar:**
- CREAR `backend/app/services/sms_service.py`
- MODIFICAR `backend/app/services/otp_service.py` — Conectar con SMSService

**Especificaciones:**

```python
# sms_service.py

class SMSService:
    def __init__(self):
        self.client = twilio.Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    async def send_otp(self, phone_number: str, otp_code: str) -> bool:
        """
        Envía OTP por SMS.
        Mensaje exacto: "Tu código Nivo es: {otp_code}. Válido 5 minutos. No lo compartas."
        Retorna True si enviado, False si falló.
        Loggear el SID de Twilio para debugging (NO el código OTP).
        """

    async def send_payment_notification(
        self, phone_number: str, amount_display: str, sender_name: str
    ) -> bool:
        """
        Mensaje: "Nivo: Recibiste {amount_display} de {sender_name}. ¡Ya está en tu billetera!"
        """
```

**Modo de desarrollo (sin Twilio real):**
Si `settings.TWILIO_ACCOUNT_SID` está vacío, loggear el OTP en consola con formato:
`[DEV OTP] +573XXXXXXXXX -> 123456` (solo en `ENVIRONMENT=development`)

**Criterios de éxito:**
- [ ] Con credenciales de Twilio sandbox: SMS llega al número de prueba
- [ ] Sin credenciales: OTP se imprime en consola y el flujo funciona
- [ ] El OTP NUNCA se almacena en plano — solo hash HMAC-SHA256 en Redis
- [ ] Máximo 3 OTPs por teléfono por hora (Redis counter)

**Dependencias:** TASK-002

---
