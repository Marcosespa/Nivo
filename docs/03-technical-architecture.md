# Arquitectura Técnica — Nivo
### Architecture Decision Records (ADRs) & Stack Técnico

**Versión:** 1.0 | **Fecha:** Abril 2026 | **Autor:** CTO/CEO, Nivo

---

## 1. Stack Principal

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOBILE CLIENTS                           │
│              React Native (iOS + Android)                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTPS/TLS 1.3 + ML-KEM-768 (híbrido)
┌─────────────────────▼───────────────────────────────────────────┐
│                   CLOUDFLARE EDGE                               │
│         WAF + DDoS + ML-KEM TLS Termination                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    API GATEWAY                                  │
│         FastAPI (Python 3.11) — Cloud Run (GCP)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Auth    │  │ Payments │  │  Users   │  │  PQC Crypto   │  │
│  │ Router   │  │ Router   │  │  Router  │  │  Router (API) │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┴───────────────┐
        │                             │
┌───────▼───────┐           ┌─────────▼───────┐
│  PostgreSQL   │           │     Redis         │
│  (Cloud SQL)  │           │  (Memorystore)   │
│  Transacciones│           │  Sessions/Cache  │
│  Usuarios     │           │  Rate limiting   │
└───────────────┘           └─────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│          REGULATED MONEY MOVEMENT PROVIDERS                     │
│     PSE/ACH · Banco aliado · Pomelo/Dock/Adyen · KYC provider   │
│     Nivo firma, concilia y audita; el aliado custodia      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│            INVESTMENT / FX / CRYPTO PARTNER MODULES             │
│       IMC/Banco FX · Broker partner · Exchange/VASP partner      │
│        Orden firmada por Nivo; ejecucion/custodia externa   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    PQC CRYPTO MODULE                            │
│              liboqs (Open Quantum Safe)                         │
│   ML-KEM-768 (key exchange) + ML-DSA-65 (signatures)          │
│              + X25519 (compatibilidad híbrida)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Decisiones de Arquitectura (ADRs)

### ADR-001: Python + FastAPI como backend principal

**Estado:** Aprobado ✅

**Contexto:**
Necesitamos un backend que integre con liboqs (biblioteca C con bindings Python), tenga alto rendimiento async, y sea mantenible por un equipo pequeño inicialmente.

**Decisión:**
Python 3.11 + FastAPI con uvicorn/gunicorn.

**Justificación:**
- `liboqs-python` es el binding oficial de Open Quantum Safe, mantenido por el proyecto OQS
- FastAPI tiene el mejor rendimiento en Python async y documentación automática OpenAPI
- La expertise del equipo fundador está en Python (FastAPI, LLMs, RAG)
- Pydantic v2 da validación de schemas con rendimiento cercano a Go
- Facilita integración futura de modelos de ML para detección de fraude

**Consecuencias:**
- Rendimiento inferior a Go/Rust para cargas extremas, pero suficiente hasta 10M tx/día con scaling horizontal
- Deuda técnica aceptable: posible reescritura de componentes críticos en Rust en Año 2 si el volumen lo justifica

**Alternativas rechazadas:** Go (menor ecosystem PQC), Rust (curva de aprendizaje alta para equipo inicial), Node.js (bindings liboqs menos maduros)

---

### ADR-002: Cifrado Híbrido ML-KEM-768 + X25519

**Estado:** Aprobado ✅ — NO NEGOCIABLE

**Contexto:**
Implementar PQC puro crea incompatibilidades con sistemas heredados. Implementar solo clásico no da protección cuántica.

**Decisión:**
Cifrado híbrido obligatorio: ML-KEM-768 (Kyber) + X25519 ejecutados simultáneamente. El secreto final se deriva combinando ambos shared secrets con HKDF-SHA256.

```python
# Pseudocódigo del protocolo híbrido
pqc_shared_secret = ml_kem_768_decapsulate(ciphertext, pqc_private_key)
classical_shared_secret = x25519_dh(my_private_key, their_public_key)
combined_secret = HKDF(
    ikm=pqc_shared_secret + classical_shared_secret,
    salt=nonce,
    info=b"Nivo-v1",
    length=32
)
session_key = AES_256_GCM_key(combined_secret)
```

**Justificación:**
- Seguridad composicional: si uno de los dos algoritmos falla, el otro mantiene la seguridad
- Compatibilidad: X25519 asegura interoperabilidad con sistemas sin soporte PQC
- Estándar de industria: Cloudflare, Google, Signal usan este patrón
- NIST SP 800-227 (borrador) recomienda híbrido durante el período de transición

**Niveles de seguridad:**
- ML-KEM-768 = NIST Security Level 3 (equivalente a AES-192)
- Para datos ultra-sensibles (API enterprise): ML-KEM-1024 (Level 5)

---

### ADR-003: ML-DSA-65 para firma de transacciones

**Estado:** Aprobado ✅

**Contexto:**
Cada transacción necesita una firma digital que sea válida y verificable en el largo plazo (imagina una disputa 10 años después — la firma debe seguir siendo válida aunque RSA/ECDSA estén comprometidos).

**Decisión:**
ML-DSA-65 (Dilithium, estandarizado NIST FIPS 204) para firmar todas las transacciones de pago.

**Justificación:**
- FIPS 204 fue finalizado por NIST en Agosto 2024 — es el estándar oficial
- Firmas de ~2.4KB (vs 64 bytes ECDSA) — costo aceptable dado el volumen esperado
- Tiempo de firma: ~0.5ms en hardware moderno — no impacta UX
- Las firmas son almacenadas y verificables a perpetuidad, independiente de avances cuánticos

**Almacenamiento:**
Cada transacción almacena: `{tx_id, amount, timestamp, sender_hash, receiver_hash, ml_dsa_signature, public_key_id}`. El registro es inmutable post-confirmación.

---

### ADR-004: Infraestructura GCP + Cloudflare

**Estado:** Aprobado ✅

**Contexto:**
Necesitamos infraestructura cloud con soporte PQC nativo, cumplimiento en Colombia (datos en LATAM), y costo razonable para una startup en etapa temprana.

**Decisión:**
- **GCP** (Cloud Run + Cloud SQL + Memorystore) como plataforma principal
- **Cloudflare** como CDN, WAF, y terminación TLS con ML-KEM

**Justificación Cloudflare:**
- Cloudflare es el único CDN que tiene ML-KEM en producción al 50%+ del tráfico global (2024)
- Su servicio de Workers permite lógica edge sin latencia
- WAF con reglas financieras preconfiguradas
- Costo: $0 en plan free para startup, $20/mes Pro para producción inicial

**Justificación GCP:**
- Cloud Run: serverless containers, escala a 0, pago por uso — ideal para startup
- Cloud SQL: PostgreSQL managed con backups automáticos y cifrado en reposo
- Región: us-central1 + southamerica-east1 (São Paulo) para latencia Colombia
- GCP tiene programa de créditos para startups: hasta $200K USD

**Alternativas rechazadas:** AWS (más caro, PQC support más tardío), Azure (menos experiencia del equipo), self-hosted (riesgo operacional inaceptable en etapa temprana)

---

### ADR-005: Detección de Fraude con ML

**Estado:** Planificado para Mes 6+ ⏳

**Contexto:**
El fraude en pagos digitales en Colombia creció 40% en 2023. Necesitamos detección en tiempo real sin sacrificar UX.

**Decisión:**
Sistema de detección de anomalías con dos capas:
1. **Reglas heurísticas** (Mes 1–6): velocidad de transacciones, montos fuera de patrón, geolocalización
2. **Modelo de comportamiento** (Mes 6+): embeddings de comportamiento del usuario + modelo de anomalía (Isolation Forest o LSTM)

**Expertise aplicado:**
La experiencia del equipo en RAG y LLMs se aplica aquí para construir perfiles de comportamiento por usuario basados en embeddings de secuencias de transacciones — patrón similar a modelos de lenguaje pero sobre eventos financieros.

**Stack ML:**
- Feature store: Redis (features en tiempo real) + BigQuery (features históricos)
- Model serving: Cloud Run con FastAPI (mismo stack que API principal)
- Latencia objetivo: <50ms para decisión de fraude en el flujo de pago

---

### ADR-006: KYC con certificados híbridos quantum-safe

**Estado:** En investigación 🔍

**Contexto:**
El onboarding KYC requiere verificar identidad del usuario y almacenar documentos. En Colombia, el proceso debe cumplir con la Circular Básica Jurídica de la SFC.

**Decisión preliminar:**
- Proveedor KYC tercero (Truora o Jumio) para la verificación base
- Certificados digitales del usuario emitidos con criptografía híbrida (X.509 con extensión PQC)
- Los certificados son la "identidad digital quantum-safe" del usuario en Nivo

**Pendiente:** Negociación con Truora Colombia para integración API + evaluación de costos

---

### ADR-007: MVP sin captación directa de dinero

**Estado:** Aprobado ✅ — requisito regulatorio MVP

**Contexto:**
Si Nivo guarda saldos propios de usuarios, el producto entra en ruta SEDPE/SFC. Eso cambia tiempos, capital, compliance y riesgo operativo. Para llegar al mercado rápido, el MVP debe probar valor sin custodiar recursos del público.

**Decisión:**
El MVP opera como capa de orquestación, firma, trazabilidad y UX. Los fondos se mueven y custodian en pasarelas, PSE/ACH, banco aliado o proveedor regulado. Nivo no será el ledger legal de saldos hasta tener COT/Sandbox, SEDPE o contrato con entidad vigilada que cubra esa operación.

**Implicaciones técnicas:**
- `wallets` no es fuente legal de saldo; almacena estado de visualización, referencias del proveedor y límites.
- Toda transacción debe tener `provider_reference`, `rail`, `settlement_status` y evidencia de conciliación.
- Los recibos ML-DSA firman la instrucción, el estado y el resultado del proveedor, no una promesa de custodia propia.
- Los retiros y recargas se diseñan como instrucciones a terceros regulados.
- Tarjeta virtual se implementa con tokens del emisor; Nivo no almacena PAN/CVV.

**Criterio de cambio:**
Solo se habilita balance custodial propio cuando legal confirme SEDPE, Certificado de Operación Temporal o estructura equivalente con entidad vigilada.

---

### ADR-008: Módulos tipo Revolut por partner-of-record

**Estado:** Aprobado ✅ — visión Año 1/Año 2

**Contexto:**
La visión de producto incluye ahorro, cambio de monedas, crypto y acciones. Esos productos tocan mundos regulatorios distintos: captación/depósitos, cambiario, valores y criptoactivos. Si Nivo intenta operar todo con licencia propia desde el inicio, el roadmap se vuelve inviable.

**Decisión:**
Nivo será la interfaz bancaria, capa de seguridad, firma, auditoría, antifraude y conciliación. La ejecución y custodia de ahorro real, FX, acciones y crypto vive en partners especializados hasta que Nivo tenga licencia propia:
- Ahorro/saldos: banco aliado, SEDPE, COT o subcuentas/cuentas del proveedor.
- FX: IMC, banco o aliado cambiario.
- Acciones/ETFs: broker/comisionista o broker internacional validado legalmente.
- Crypto: exchange/VASP aliado, separado del saldo de pagos.

**Implicaciones técnicas:**
- Los bolsillos de ahorro pueden existir como metas visuales desde MVP; si representan saldos reales, deben mapear a una cuenta/subcuenta del partner o licencia aplicable.
- Cada orden de FX/inversión/crypto se firma con ML-DSA antes de enviarse al partner.
- La tabla de órdenes almacena `partner`, `partner_order_id`, `instrument_type`, `execution_status`, `risk_disclosure_version` y hash del disclosure aceptado.
- Los balances de inversión son snapshots informativos desde el partner; Nivo no es book of record.
- El motor AML/fraude aumenta controles para crypto: velocity limits, device fingerprint, listas, travel-rule readiness y monitoreo de patrones.
- No se implementan recomendaciones de inversión ni copy-trading en el MVP.

---

### ADR-009: PQC para todos y API B2B sin llaves privadas entrantes

**Estado:** Aprobado ✅

**Contexto:**
La promesa de Nivo es que todos los usuarios, no solo bancos o clientes enterprise, reciban protección post-cuántica. Al mismo tiempo, la API B2B no puede pedir ni recibir llaves privadas de clientes porque eso destruye el modelo de confianza.

**Decisión:**
- La app B2C usa "blindaje cuántico activo" como parte visible de pagos, recibos, sesiones y órdenes.
- La API B2B soporta verificación, emisión de recibos, key exchange y firma server-side solo con llaves administradas por Nivo/KMS/HSM o con material explícitamente provisionado mediante flujo BYOK seguro.
- Los clientes B2B que quieran firmar con sus propias llaves deben hacerlo client-side o mediante KMS/HSM controlado por ellos. Nivo puede verificar firmas y registrar evidencias, pero no debe recibir llaves privadas por request.
- Toda API key B2B se guarda hasheada, con scopes, límites, rotación, auditoría y billing.

**Implicaciones técnicas:**
- El endpoint público `POST /api/v1/crypto/sign` no acepta `signing_key_hex`.
- Se introduce `key_id`, `client_id`, scopes (`sign`, `verify`, `receipt`, `kem`) y logs inmutables.
- Las respuestas nunca devuelven `shared_secret_hex` en producción; solo ciphertext, public keys efímeras y metadatos necesarios.
- Los SDKs deben incluir modo client-side signing para clientes que no quieran delegar firma a Nivo.

---

## 3. Modelo de Datos Principal

```sql
-- Usuarios
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(15) UNIQUE NOT NULL,   -- identificador primario (como Bizum)
    email VARCHAR(255) UNIQUE,
    pqc_public_key_id UUID REFERENCES pqc_keys(id),
    kyc_status VARCHAR(20) DEFAULT 'pending',   -- pending/verified/rejected
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Llaves PQC por usuario
CREATE TABLE pqc_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    algorithm VARCHAR(30) NOT NULL,            -- 'ML-KEM-768', 'ML-DSA-65'
    public_key BYTEA NOT NULL,
    key_fingerprint VARCHAR(64) NOT NULL,      -- SHA-256 de la llave pública
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

-- Transacciones
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID REFERENCES users(id),
    receiver_id UUID REFERENCES users(id),
    amount_cop BIGINT NOT NULL,                -- en centavos
    rail VARCHAR(30) NOT NULL,                 -- pse/ach/bank_partner/card/ledger
    provider_reference VARCHAR(120),           -- id externo del aliado regulado
    settlement_status VARCHAR(30) DEFAULT 'pending',
    status VARCHAR(20) DEFAULT 'pending',      -- pending/completed/failed/reversed
    ml_dsa_signature BYTEA NOT NULL,           -- firma ML-DSA-65
    signature_key_id UUID REFERENCES pqc_keys(id),
    encrypted_metadata BYTEA,                  -- cifrado con AES-256-GCM
    created_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    CONSTRAINT positive_amount CHECK (amount_cop > 0)
);

-- Billeteras
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) UNIQUE,
    display_balance_cop BIGINT DEFAULT 0,      -- cache visual; no ledger legal en MVP
    currency VARCHAR(3) DEFAULT 'COP',
    custody_mode VARCHAR(30) DEFAULT 'non_custodial',
    provider_account_ref VARCHAR(120),         -- cuenta/token del aliado regulado
    is_frozen BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Bolsillos de ahorro: metas visuales o subcuentas de partner/licencia
CREATE TABLE savings_pockets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(80) NOT NULL,
    target_amount_cop BIGINT,
    display_balance_cop BIGINT DEFAULT 0,
    mode VARCHAR(30) DEFAULT 'visual_goal',     -- visual_goal/partner_subaccount/custodial
    provider_subaccount_ref VARCHAR(120),
    ml_dsa_last_state_signature BYTEA,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT positive_pocket_balance CHECK (display_balance_cop >= 0)
);

-- Órdenes reguladas por partner: FX, acciones, ETFs, crypto
CREATE TABLE partner_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    product_type VARCHAR(30) NOT NULL,          -- fx/stock/etf/crypto
    partner VARCHAR(60) NOT NULL,
    partner_order_id VARCHAR(120),
    instrument_symbol VARCHAR(30) NOT NULL,     -- USD/COP, AAPL, BTC, etc.
    side VARCHAR(10) NOT NULL,                  -- buy/sell/convert
    notional_amount BIGINT NOT NULL,            -- menor unidad de la moneda origen
    source_currency VARCHAR(3),
    target_currency VARCHAR(10),
    execution_status VARCHAR(30) DEFAULT 'pending',
    risk_disclosure_version VARCHAR(30) NOT NULL,
    signed_order_payload BYTEA NOT NULL,
    ml_dsa_signature BYTEA NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ
);
```

---

## 4. Flujo de una Transacción P2P

```
Usuario A (pagador)                    Usuario B (receptor)
       |                                       |
       |--[1. Inicia pago $50K COP]----------->|
       |                                       |
       |         API Nivo                 |
       |              |                        |
       |--[2. POST /api/v1/payments/initiate]->|
       |              |                        |
       |         [3. Verificar KYC/límites A]  |
       |         [4. ML-KEM key exchange]      |
       |         [5. Construir tx payload]     |
       |         [6. Firmar con ML-DSA-65]     |
       |         [7. Enviar instrucción al     |
       |              aliado PSE/ACH/banco]    |
       |         [8. Conciliar resultado]      |
       |         [9. Guardar tx + firma +      |
       |              provider_reference]       |
       |              |                        |
       |<-[10. 200 OK + tx_id + receipt]------|
       |                                       |
       |         [11. Push notification → B]  |
       |                                       |
  Recibe confirmación                    Recibe dinero
  con recibo protegido                   + notificación
```

**Latencia objetivo:** < 800ms end-to-end para transacciones P2P Colombia

---

## 5. Seguridad y Crypto-Agilidad

### Principio de Crypto-Agilidad

El módulo de criptografía está **completamente abstraído** del resto de la aplicación. Ningún otro módulo importa directamente liboqs o cualquier implementación criptográfica. Todo pasa por el `CryptoService`:

```python
# crypto/service.py — interfaz unificada
class CryptoService:
    def sign(self, data: bytes, key_id: str) -> bytes: ...
    def verify(self, data: bytes, signature: bytes, key_id: str) -> bool: ...
    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]: ...  # ciphertext, shared_secret
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes: ...
```

Si mañana NIST retira ML-KEM-768 y lo reemplaza con otro algoritmo, **solo cambia el módulo `CryptoService`**. El resto de la aplicación no se toca.

### Rotación de Llaves

- Llaves ML-KEM: rotación cada 90 días por usuario
- Llaves ML-DSA para firma de transacciones: rotación anual (o ante compromiso)
- Las llaves antiguas se mantienen en read-only para verificación de firmas históricas

### Secrets Management

- **HashiCorp Vault** (en GCP) para gestión de llaves privadas del servidor
- **GCP Secret Manager** para credenciales de infraestructura
- Las llaves privadas de usuarios se derivan de material de usuario + HSM del servidor (no almacenadas en plano)

---

## 6. Monitoreo y Observabilidad

| Herramienta | Uso |
|------------|-----|
| GCP Cloud Monitoring | Métricas de infraestructura, alertas |
| OpenTelemetry + Jaeger | Trazabilidad distribuida de transacciones |
| Sentry | Error tracking y alertas de aplicación |
| PQC Health Checks | Endpoint `/health/pqc` — verifica integridad del módulo cripto cada 60s |
| Audit logs | Cada operación criptográfica se registra en log inmutable |

---

## 7. Plan de Crecimiento de Infraestructura

| Fase | Usuarios | Infraestructura |
|------|---------|----------------|
| MVP (0–10K usuarios) | < 10K | Cloud Run 2 instancias, Cloud SQL db-g1-small |
| Crecimiento (10K–100K) | 10K–100K | Cloud Run autoscaling, Cloud SQL db-standard-2, Redis cluster |
| Escala (100K–1M) | 100K–1M | Cloud Run 10+ instancias, Cloud SQL db-standard-8, Read replicas, CDN agresivo |
| Expansión LATAM | 1M+ | Multi-región GCP, base de datos por país, arquitectura event-driven |

**Costo estimado infraestructura:**
- MVP: ~$200/mes
- 50K usuarios: ~$800/mes
- 250K usuarios: ~$3,000/mes

---

*ADRs adicionales se agregarán conforme el producto evolucione. Toda decisión de arquitectura debe documentarse aquí antes de implementarse.*
