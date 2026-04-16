## MES 4 — SPRINT 7 (Semanas 21–24): API B2B y Tarjeta Virtual

---

### TASK-021 — API B2B PQC-as-a-Service: Completar Implementación
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
El router `app/api/v1/crypto.py` existe pero está incompleto. Implementar el sistema
completo de API keys B2B con scopes, billing, rate limiting por tier, dashboard y
modelo seguro de llaves. La API pública NO debe aceptar llaves privadas en requests.

**Archivos a crear/modificar:**
- MODIFICAR `backend/app/api/v1/crypto.py` — Completar todos los endpoints
- CREAR `backend/app/models/orm/api_client.py` — Clientes B2B
- CREAR `backend/app/models/orm/api_usage.py` — Registro de uso para billing
- CREAR `backend/app/models/orm/api_key_material.py` — Referencias a llaves administradas/KMS/HSM
- CREAR `backend/app/services/api_key_service.py` — Gestión de API keys
- CREAR `backend/app/services/key_management_service.py` — Gestión de `key_id`, rotación y BYOK seguro
- CREAR `backend/app/api/v1/b2b_dashboard.py` — Dashboard B2B

**Tabla api_clients:**
```sql
id: UUID PK
organization_name: VARCHAR(255) NOT NULL
contact_email: VARCHAR(255) UNIQUE NOT NULL
api_key_hash: VARCHAR(64) NOT NULL  -- SHA-256 del API key, nunca el key en plano
scopes: JSONB NOT NULL              -- ["kem","sign","verify","receipt"]
tier: ENUM('starter','growth','enterprise') DEFAULT 'starter'
monthly_limit: INTEGER DEFAULT 100000  -- operaciones/mes
is_active: BOOLEAN DEFAULT TRUE
created_at: TIMESTAMPTZ DEFAULT NOW()

api_key_material:
id: UUID PK
client_id: UUID FK -> api_clients.id
key_id: VARCHAR(120) UNIQUE NOT NULL          -- referencia KMS/HSM/Vault, no secreto en BD
algorithm: VARCHAR(30) NOT NULL               -- ML-DSA-65, ML-KEM-768
public_key: BYTEA NOT NULL
key_fingerprint: VARCHAR(64) NOT NULL
management_mode: ENUM('nivo_managed','client_kms','byok_wrapped') NOT NULL
is_active: BOOLEAN DEFAULT TRUE
created_at: TIMESTAMPTZ DEFAULT NOW()

api_usage:
id: UUID PK
client_id: UUID FK -> api_clients.id
operation: VARCHAR(50)  -- 'sign', 'verify', 'key_exchange', 'hybrid_encrypt'
timestamp: TIMESTAMPTZ DEFAULT NOW()
success: BOOLEAN
latency_ms: INTEGER
INDEX: (client_id, timestamp)  -- para billing mensual
```

**Endpoint de key exchange completo:**
```python
POST /api/v1/crypto/key-exchange
# Implementar encapsulate Y decapsulate en el mismo endpoint según modo:
{
    "mode": "encapsulate",   # o "decapsulate"
    "recipient_pqc_public_key_hex": "...",
    "recipient_x25519_public_key_hex": "...",
    # Para decapsulate:
    "pqc_ciphertext_hex": "...",
    "sender_x25519_public_key_hex": "...",
    "key_id": "kms_or_hsm_reference"
}
```

**Endpoint de firma seguro:**
```python
POST /api/v1/crypto/sign
{
    "data_hex": "...",
    "key_id": "nivo_or_client_kms_key_id",
    "purpose": "receipt|payment_order|audit_record"
}

# PROHIBIDO:
# - aceptar signing_key_hex
# - registrar llaves privadas en logs
# - retornar secretos compartidos en producción
```

**Criterios de éxito:**
- [ ] Un cliente externo con API key y scope correcto puede hacer sign/verify correctamente usando `key_id`, nunca `signing_key_hex`
- [ ] Requests con `signing_key_hex`, `pqc_secret_key_hex` o secretos privados retornan 400 y se registran como intento inseguro
- [ ] El contador de uso se registra en BD para cada operación
- [ ] Al superar el límite mensual, la API retorna 429 con mensaje de upgrade
- [ ] Cada API key valida scopes por endpoint (`sign`, `verify`, `kem`, `receipt`)
- [ ] `GET /api/v1/b2b/dashboard` retorna uso del mes y costo estimado

**Dependencias:** TASK-001, TASK-004

---

### TASK-022 — Integrar Tarjeta Virtual (Pomelo o Dock)
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 10–12 horas
**Prioridad:** ALTA

**Descripción:**
Integrar un BaaS (Banking-as-a-Service) como Pomelo o Dock para emitir tarjetas
virtuales Visa/Mastercard a usuarios del plan Plus y Pro.

**Archivos a crear:**
- CREAR `backend/app/services/card_service.py`
- CREAR `backend/app/api/v1/cards.py`
- CREAR `backend/app/models/orm/virtual_card.py`

**Tabla virtual_cards:**
```sql
id: UUID PK
user_id: UUID FK -> users.id
card_provider_id: VARCHAR(255)  -- ID en Pomelo/Dock
last_four: VARCHAR(4) NOT NULL
brand: ENUM('visa','mastercard')
status: ENUM('active','frozen','cancelled') DEFAULT 'active'
created_at: TIMESTAMPTZ DEFAULT NOW()
-- NUNCA almacenar número completo, CVV, ni fecha de expiración en BD
```

**Endpoints:**
```
POST /api/v1/cards/issue         — Emitir nueva tarjeta virtual
GET  /api/v1/cards/me            — Ver mis tarjetas (número enmascarado)
POST /api/v1/cards/{id}/freeze   — Congelar tarjeta
POST /api/v1/cards/{id}/unfreeze — Descongelar
DELETE /api/v1/cards/{id}        — Cancelar tarjeta
GET  /api/v1/cards/{id}/details  — Ver número completo (requiere OTP)
POST /api/v1/cards/webhook       — Webhook de transacciones con tarjeta
```

**Seguridad crítica:**
- El número completo de la tarjeta SOLO se muestra previa verificación OTP
- La tarjeta es de un solo uso por número (generar nuevo número para cada compra online es feature Pro)
- Webhook de Pomelo/Dock debe validarse con HMAC

**Criterios de éxito:**
- [ ] En sandbox de Pomelo/Dock: tarjeta se emite en < 30 segundos
- [ ] El número completo NUNCA aparece en logs ni en respuestas sin OTP
- [ ] Congelar/descongelar se refleja en Pomelo/Dock en tiempo real

**Dependencias:** TASK-002, TASK-003

---

### TASK-023 — Detección de Fraude: Motor de Reglas v1
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** ALTA

**Descripción:**
Implementar el primer sistema de detección de fraude basado en reglas heurísticas.
El sistema ML vendrá en Mes 5–6. Las reglas son la base.

**Archivos a crear:**
- CREAR `backend/app/services/fraud_detection_service.py`
- CREAR `backend/app/models/orm/fraud_alert.py`

**Reglas a implementar (evaluar antes de cada transacción):**

```python
# Regla 1: Velocidad de transacciones
# Si el usuario hace más de 5 transacciones en 5 minutos → ALERT

# Regla 2: Monto inusual
# Si el monto es > 3x el promedio de los últimos 30 días del usuario → REVIEW

# Regla 3: Nuevo dispositivo + monto alto
# Si device_id nunca ha hecho pagos + monto > $1M COP → REQUIRE_OTP

# Regla 4: Receptor sin historial
# Si es el primer pago a este receptor y el monto > $500K → REVIEW

# Regla 5: Horario inusual
# Si es entre 2am–5am Colombia y monto > $200K → ALERT

# Regla 6: Geolocalización imposible
# Si el último login fue en Bogotá hace 30 min y ahora desde Medellín → ALERT

# Acción por nivel:
# PASS   → procesar normalmente
# REVIEW → procesar pero crear FraudAlert para revisión manual
# REQUIRE_OTP → pedir OTP adicional antes de procesar
# BLOCK  → rechazar y notificar al usuario
```

**Tabla fraud_alerts:**
```sql
id: UUID PK
transaction_id: UUID FK -> transactions.id
user_id: UUID FK -> users.id
rule_triggered: VARCHAR(100)
risk_score: DECIMAL(4,3)  -- 0.000 a 1.000
action_taken: ENUM('pass','review','require_otp','block')
resolved: BOOLEAN DEFAULT FALSE
created_at: TIMESTAMPTZ DEFAULT NOW()
```

**Criterios de éxito:**
- [ ] La detección de fraude añade < 50ms al tiempo de una transacción
- [ ] Un script de test puede triggear cada una de las 6 reglas
- [ ] Las alertas BLOCK notifican al usuario con mensaje en español
- [ ] Las alertas REVIEW aparecen en un endpoint de admin para revisión manual

**Dependencias:** TASK-003

---

