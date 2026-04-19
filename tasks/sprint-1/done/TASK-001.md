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
