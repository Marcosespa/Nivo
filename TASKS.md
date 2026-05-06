# TASKS.md — Nivo
## Plan de Ejecución 6 Meses | Abril 2026 → Octubre 2026
### Diseñado para ejecución por múltiples agentes en paralelo

---

> **Cómo usar este archivo:**
> Cada tarea tiene un ID único, descripción explícita de exactamente qué hacer, archivos involucrados,
> criterios de éxito verificables, y dependencias. Los agentes deben marcar el estado al iniciar (`IN_PROGRESS`)
> y al terminar (`DONE`). Una tarea no está DONE hasta que todos sus criterios de éxito son verificables.
> Existe el archivo Task_Done, el cual se encarga de poner las tasks que ya esten hechas

---

## ESTADO DE TAREAS
```
[ ] PENDING    — No iniciada
[>] IN_PROGRESS — En ejecución por un agente
[x] DONE       — Completada y verificada
[!] BLOCKED    — Bloqueada por dependencia
```

---

## SPRINT 0 — Correcciones de Alineación (Antes de cualquier implementación)
> Estas tareas corrigen bugs, vulnerabilidades de seguridad e inconsistencias detectadas
> en la revisión del código base existente. **Deben completarse antes de TASK-001.**
> No son features nuevas — son pre-condiciones para que el stack arranque limpio y seguro.

---

### FIX-001 — Corregir bug `init_db()` en `database.py` (SQLAlchemy 2.0)
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 30 minutos
**Prioridad:** CRÍTICA — la app no arranca correctamente sin este fix

**Descripción:**
`init_db()` llama `c.text()` dentro de `run_sync`, que no existe en SQLAlchemy 2.0.
Lanza `AttributeError` en el startup. Adicionalmente, `sessionmaker` está deprecado
en SQLAlchemy 2.x y debe reemplazarse por `async_sessionmaker`.

**Archivos a modificar:**
- MODIFICAR `backend/app/core/database.py`

**Cambios exactos:**

```python
# ANTES (incorrecto en SQLAlchemy 2.0):
from sqlalchemy.orm import sessionmaker, DeclarativeBase

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: c.execute(c.text("SELECT 1")))

# DESPUÉS (correcto):
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    print("✅ Base de datos conectada")
```

**Criterios de éxito:**
- [ ] `uvicorn app.main:app --reload` arranca sin `AttributeError` en `init_db`
- [ ] `python -c "from app.core.database import AsyncSessionLocal; print(type(AsyncSessionLocal))"` muestra `async_sessionmaker`
- [ ] El log muestra `✅ Base de datos conectada` al arrancar

**Dependencias:** Ninguna

---

### FIX-002 — Eliminar `shared_secret_hex` de `KeyExchangeResponse` (Vulnerabilidad crítica de seguridad)
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 30 minutos
**Prioridad:** CRÍTICA — exponer el shared secret invalida toda la protección de ML-KEM

**Descripción:**
`KeyExchangeResponse` incluye `shared_secret_hex` con el comentario "SOLO para debug".
El shared secret ES la llave de sesión AES-256-GCM. Retornarlo en el response lo expone
a cualquier intermediario, log, proxy o atacante que capture la respuesta. Destruye
la seguridad que ML-KEM-768 debería proveer. Este campo debe eliminarse del response
en todos los ambientes, incluso en desarrollo.

**Archivo a modificar:**
- MODIFICAR `backend/app/api/v1/crypto.py`

**Cambios exactos:**

```python
# ELIMINAR este campo del modelo:
class KeyExchangeResponse(BaseModel):
    pqc_ciphertext_hex: str
    classical_public_key_hex: str
    algorithm: str = "ML-KEM-768 + X25519 (hybrid)"
    # shared_secret_hex: str  ← ELIMINAR COMPLETAMENTE, nunca retornar

# El endpoint /key-exchange debe retornar SOLO los datos que el receptor necesita
# para derivar el mismo secreto. El shared_secret se usa internamente (AES-GCM)
# y nunca viaja por la red.
```

**Criterios de éxito:**
- [ ] `KeyExchangeResponse` no tiene ningún campo con `secret` en el nombre
- [ ] El endpoint `/api/v1/crypto/key-exchange` no retorna el secreto compartido
- [ ] `grep -r "shared_secret_hex" backend/app/api/` retorna vacío

**Dependencias:** Ninguna

---

### FIX-003 — Eliminar `signing_key_hex` de `SignRequest` (Vulnerabilidad crítica de seguridad)
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 2–3 horas
**Prioridad:** CRÍTICA — aceptar llaves privadas vía API es un patrón de seguridad roto

**Descripción:**
`SignRequest` en `crypto.py` acepta `signing_key_hex` (llave privada ML-DSA-65) en el
body del request. Esto viola el ADR-002 y TASKS TASK-021 que explícitamente prohíbe
que llaves privadas viajen por la API. Un atacante con acceso a los logs, un proxy,
o una vulnerabilidad de transporte obtiene la llave privada del cliente.

La corrección temporal (hasta que TASK-021 implemente el sistema completo de `key_id`)
es rediseñar el endpoint para que genere un keypair efímero del lado del servidor,
firme los datos, y retorne la firma junto con la llave **pública** (no privada) para
que el llamador pueda verificar. El cliente que necesite BYOK debe usar el SDK
client-side (ver TASK-029) y nunca enviar su llave privada al servidor.

**Archivo a modificar:**
- MODIFICAR `backend/app/api/v1/crypto.py`

**Cambios exactos:**

```python
# ANTES (inseguro — acepta llave privada en el request):
class SignRequest(BaseModel):
    data_hex: str
    signing_key_hex: str    # ← NUNCA. Llave privada viajando por la red.

# DESPUÉS (seguro — servidor firma con llave efímera o key_id):
class SignRequest(BaseModel):
    data_hex: str
    # key_id: str | None = None  # Futuro: apunta a llave en KMS/HSM (TASK-021)
    # Por ahora: el servidor genera un keypair efímero y firma
    # El cliente recibe firma + public_key para verificación independiente

class SignResponse(BaseModel):
    signature_hex: str
    public_key_hex: str          # ← Llave PÚBLICA para que el llamador verifique
    public_key_fingerprint: str
    algorithm: str = "ML-DSA-65"
    # Nota: en TASK-021 esto se reemplaza por key_id + KMS/HSM real

# El endpoint debe además rechazar cualquier campo que suene a llave privada:
# signing_key_hex, secret_key_hex, private_key_hex → retornar 400
```

**Criterios de éxito:**
- [ ] `SignRequest` no tiene ningún campo con `secret_key` o `signing_key` o `private_key`
- [ ] `POST /api/v1/crypto/sign` con `{"data_hex": "...", "signing_key_hex": "..."}` retorna `400 Bad Request`
- [ ] `POST /api/v1/crypto/sign` con solo `data_hex` retorna firma válida + llave pública
- [ ] La firma retornada puede verificarse con `/api/v1/crypto/verify` usando la `public_key_hex` del response
- [ ] `grep -r "signing_key_hex" backend/app/` retorna vacío

**Dependencias:** Ninguna (fix inmediato; TASK-021 reemplazará esto con key_id completo)

---

### FIX-004 — Conectar algoritmos PQC desde `settings` en `CryptoService` (Crypto-agility)
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 30 minutos
**Prioridad:** ALTA — viola ADR-002 (crypto-agility)

**Descripción:**
`CryptoService` tiene los algoritmos hardcodeados como constantes de clase:
```python
KEM_ALGORITHM = "ML-KEM-768"
SIG_ALGORITHM = "ML-DSA-65"
```
El ADR-002 establece que si NIST cambia el estándar, solo se modifica `service.py`.
Pero si están hardcodeados, cambiar el algoritmo requiere editar código, no solo config.
Asimismo, `health.py` hardcodea `"algorithm_sig": "ML-DSA-65"` en lugar de leer de settings.

**Archivos a modificar:**
- MODIFICAR `backend/app/crypto/service.py`
- MODIFICAR `backend/app/api/v1/health.py`

**Cambios exactos:**

```python
# service.py — leer de settings en __init__:
from app.core.config import settings

class CryptoService:
    def __init__(self):
        self.KEM_ALGORITHM = settings.PQC_ALGORITHM           # "ML-KEM-768"
        self.SIG_ALGORITHM = settings.PQC_SIGNATURE_ALGORITHM  # "ML-DSA-65"
        self._liboqs_available = LIBOQS_AVAILABLE

# health.py — leer de settings:
return {
    "algorithm_kem": settings.PQC_ALGORITHM,
    "algorithm_sig": settings.PQC_SIGNATURE_ALGORITHM,  # no hardcodear
    ...
}
```

**Criterios de éxito:**
- [ ] Cambiar `PQC_ALGORITHM=ML-KEM-1024` en `.env` y reiniciar refleja el cambio en `/health/pqc`
- [ ] `CryptoService` no tiene ninguna constante de clase con nombre de algoritmo hardcodeado
- [ ] `grep -n "ML-KEM-768\|ML-DSA-65" backend/app/crypto/service.py` retorna solo comentarios, nunca strings asignados a variables

**Dependencias:** Ninguna

---

### FIX-005 — Inyectar sesión de BD en routers (`payments.py`, `users.py`, `auth.py`)
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 1–2 horas
**Prioridad:** ALTA — sin esto, ningún endpoint puede leer ni escribir en la BD

**Descripción:**
Los routers de pagos, usuarios y autenticación no tienen acceso a la sesión de base
de datos. Ninguno inyecta `db: AsyncSession = Depends(get_db)`. Cuando TASK-001 cree
los modelos ORM, los endpoints seguirán sin poder usarlos porque no tienen la sesión.
Esto debe corregirse ahora para que TASK-002 y TASK-003 puedan implementarse correctamente.

**Archivos a modificar:**
- MODIFICAR `backend/app/api/v1/payments.py`
- MODIFICAR `backend/app/api/v1/users.py`
- MODIFICAR `backend/app/api/v1/auth.py`

**Patrón correcto a aplicar en cada endpoint que acceda a BD:**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

@router.post("/initiate")
async def initiate_payment(
    request: PaymentInitiateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),   # ← inyectar sesión
) -> PaymentInitiateResponse:
    ...
```

**Nota:** Los endpoints que aún tienen lógica mock (TODO) deben recibir `db` como
parámetro aunque no lo usen todavía — así cuando TASK-002/003 implementen la lógica
real, la firma del endpoint ya es correcta y no rompe contratos.

**Criterios de éxito:**
- [ ] Todos los endpoints de `payments.py` reciben `db: AsyncSession = Depends(get_db)`
- [ ] Todos los endpoints de `users.py` que acceden a datos reciben `db`
- [ ] Todos los endpoints de `auth.py` reciben `db`
- [ ] `python -c "from app.api.v1.payments import router; print('OK')"` sin errores de importación

**Dependencias:** FIX-001 (database.py debe estar correcto primero)

---

### FIX-006 — Agregar campos regulatorios a modelo `Transaction` Pydantic
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 30 minutos
**Prioridad:** ALTA — sin estos campos la conciliación con el aliado regulado es imposible

**Descripción:**
El modelo Pydantic `Transaction` en `models/transaction.py` no tiene los campos
`rail`, `provider_reference`, ni `settlement_status`. Estos son obligatorios por
arquitectura regulatoria: Nivo debe rastrear qué rail procesó cada pago, con qué
referencia del proveedor, y cuál es el estado de liquidación. Sin esto, la conciliación
es imposible y el modelo ORM (TASK-001) ya los especifica — el Pydantic debe estar alineado.

**Archivo a modificar:**
- MODIFICAR `backend/app/models/transaction.py`

**Campos a agregar:**

```python
from enum import Enum
from typing import Literal

class SettlementRail(str, Enum):
    PSE = "pse"
    ACH = "ach"
    BANK_PARTNER = "bank_partner"
    INTERNAL = "internal"  # para simulaciones y desarrollo

class SettlementStatus(str, Enum):
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"
    REVERSED = "reversed"

class Transaction(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    amount_cop: int
    status: TransactionStatus
    ml_dsa_signature: bytes
    signature_key_id: str
    message: str | None = None
    # Campos regulatorios — obligatorios para conciliación:
    rail: SettlementRail = SettlementRail.INTERNAL
    provider_reference: str | None = None      # ID de la transacción en el aliado (PSE ref, ACH ref)
    settlement_status: SettlementStatus = SettlementStatus.PENDING
    created_at: datetime
    confirmed_at: datetime | None = None

    @property
    def amount_display(self) -> str:
        return f"${self.amount_cop / 100:,.0f} COP"
```

**Criterios de éxito:**
- [ ] `python -c "from app.models.transaction import Transaction; print(Transaction.model_fields.keys())"` muestra `rail`, `provider_reference`, `settlement_status`
- [ ] Los campos en `Transaction` Pydantic coinciden con las columnas del ORM en TASK-001
- [ ] `PaymentConfirmResponse` en `payments.py` retorna `settlement_status` y `provider_reference`

**Dependencias:** Ninguna

---

### FIX-007 — Corregir URLs en CORS y `ALLOWED_HOSTS` (mayúsculas en dominios)
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 15 minutos
**Prioridad:** MEDIA — en producción rompe requests legítimos cross-origin

**Descripción:**
Las URLs en `config.py` tienen `Nivo` con mayúscula: `"https://Nivo.co"`, `"https://app.Nivo.co"`.
Los dominios en URLs son case-sensitive en los headers HTTP. El browser envía el header
`Origin: https://nivo.co` (minúsculas) y el CORS middleware lo rechazará porque no
coincide con `"https://Nivo.co"`. Mismo problema con `ALLOWED_HOSTS`.

**Archivo a modificar:**
- MODIFICAR `backend/app/core/config.py`

**Cambios exactos:**

```python
# ANTES:
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://Nivo.co",        # ← mayúscula incorrecta
    "https://app.Nivo.co",    # ← mayúscula incorrecta
]
ALLOWED_HOSTS: list[str] = ["Nivo.co", "api.Nivo.co"]  # ← mayúsculas incorrectas

# DESPUÉS:
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://nivo.co",
    "https://app.nivo.co",
]
ALLOWED_HOSTS: list[str] = ["nivo.co", "api.nivo.co"]
```

**Criterios de éxito:**
- [ ] `grep -n "Nivo\.co" backend/app/core/config.py` retorna vacío (solo minúsculas)
- [ ] Un request con `Origin: https://nivo.co` pasa el CORS middleware en producción

**Dependencias:** Ninguna

---

### FIX-008 — Corregir orden de rutas y agregar `/history` en `payments.py`
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 30 minutos
**Prioridad:** MEDIA — el router actual tiene `GET /` donde debería ser `GET /history`

**Descripción:**
En FastAPI, las rutas se evalúan en orden de declaración. El historial de transacciones
está en `GET /` pero el roadmap requiere `GET /history`. Si se agrega `GET /history`
después de `GET /{tx_id}`, FastAPI lo captura como `tx_id = "history"` antes de llegar
al endpoint correcto. La ruta actual `GET /` también es ambigua y confusa para los clientes.

Adicionalmente, `GET /` como lista de recursos no sigue REST semántico; debe ser
`GET /history` o `GET /` documentado explícitamente.

**Archivo a modificar:**
- MODIFICAR `backend/app/api/v1/payments.py`

**Orden correcto de declaración de rutas:**

```python
# 1. Rutas estáticas primero (antes de cualquier /{param}):
@router.post("/initiate", ...)
@router.post("/confirm", ...)
@router.get("/history", ...)     # ← mover aquí, ANTES de /{tx_id}

# 2. Rutas dinámicas al final:
@router.get("/{tx_id}", ...)     # ← siempre al final
```

**Criterios de éxito:**
- [ ] `GET /api/v1/payments/history` retorna el historial (no un 404 de tx_id no encontrado)
- [ ] `GET /api/v1/payments/{uuid}` sigue funcionando para consultas individuales
- [ ] No existe `GET /` en el router de payments (reemplazado por `/history`)

**Dependencias:** Ninguna

---

### FIX-009 — Eliminar entrada duplicada de `httpx` en `requirements.txt`
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 5 minutos
**Prioridad:** BAJA — no rompe nada pero es ruido que puede confundir en auditorías

**Descripción:**
`httpx==0.27.2` aparece dos veces en `requirements.txt` (línea 38 y línea 52).
`pip` lo instala bien, pero genera advertencias en algunos entornos y confunde
en code reviews y auditorías de dependencias.

**Archivo a modificar:**
- MODIFICAR `backend/requirements.txt`

**Cambio:** Eliminar la segunda aparición de `httpx==0.27.2` (la que está en la
sección `Dev / Testing`). Mantener la que está en `HTTP Client`.

**Criterios de éxito:**
- [ ] `grep -c "httpx" backend/requirements.txt` retorna `1`
- [ ] `pip install -r requirements.txt` no muestra warnings de duplicados

**Dependencias:** Ninguna

---

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
otp_hash: VARCHAR(64) NOT NULL  # bcrypt del OTP, nunca el OTP en plano
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
- Almacenado como bcrypt hash en Redis con key: f"otp:{phone_number}:{purpose}"
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
- [ ] El OTP NUNCA se almacena en plano — solo el bcrypt hash en Redis
- [ ] Máximo 3 OTPs por teléfono por hora (Redis counter)

**Dependencias:** TASK-002

---

## MES 1 — SPRINT 2 (Semanas 3–4): KYC y Recarga

---

### TASK-006 — Integrar Truora para KYC
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** ALTA

**Descripción:**
Integrar Truora Colombia para verificación de identidad. El flujo debe completarse en < 5 minutos
para el usuario. Los documentos se almacenan cifrados.

**Archivos a crear:**
- CREAR `backend/app/services/kyc_service.py`
- CREAR `backend/app/api/v1/kyc.py` — Endpoints KYC
- MODIFICAR `backend/app/main.py` — Incluir router KYC

**Endpoints requeridos:**
```
POST /api/v1/kyc/initiate       — Iniciar proceso KYC, retorna URL de Truora
POST /api/v1/kyc/webhook        — Webhook de Truora para resultado (NO requiere JWT)
GET  /api/v1/kyc/status         — Estado actual del KYC del usuario autenticado
```

**Flujo KYC:**
```
1. Usuario llama POST /api/v1/kyc/initiate con JWT
2. Backend llama API Truora: crear proceso de verificación
3. Truora retorna URL de verificación (front se redirige ahí)
4. Usuario completa la verificación en Truora (toma 2–4 minutos)
5. Truora llama webhook POST /api/v1/kyc/webhook con resultado
6. Backend actualiza users.kyc_status = 'verified' o 'rejected'
7. Se envía push notification al usuario con resultado

# Webhook payload de Truora (validar HMAC):
{
    "process_id": "...",
    "status": "approved" | "declined",
    "document_number": "...",
    "full_name": "..."
}
```

**Seguridad del webhook:**
- Verificar firma HMAC-SHA256 del payload usando `settings.KYC_API_KEY` como secret
- Retornar 200 incluso si falla la verificación (no revelar si fue inválido)
- Loggear intentos fallidos con IP del remitente

**Criterios de éxito:**
- [ ] El flujo completo KYC se puede simular con datos de test de Truora
- [ ] Webhook inválido (sin firma correcta) retorna 200 pero no actualiza el usuario
- [ ] `kyc_status` cambia a 'verified' tras webhook exitoso
- [ ] Los límites de transacción cambian automáticamente al verificar KYC

**Dependencias:** TASK-001, TASK-002

---

### TASK-007 — Integrar Pasarela PSE (Wompi) para Recargas
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
Integrar Wompi (o PayU como fallback) para recargas desde cuenta bancaria colombiana vía PSE.
Este es el único flujo de entrada de dinero real al MVP.

**Archivos a crear:**
- CREAR `backend/app/services/payment_gateway_service.py`
- CREAR `backend/app/api/v1/topup.py` — Endpoints de recarga
- MODIFICAR `backend/app/main.py` — Incluir router topup

**Endpoints requeridos:**
```
POST /api/v1/topup/initiate     — Iniciar recarga PSE, retorna URL de pago
POST /api/v1/topup/webhook      — Webhook de Wompi para confirmación
GET  /api/v1/topup/history      — Historial de recargas del usuario
```

**Flujo de recarga:**
```
1. Usuario solicita recarga de $100,000 COP
2. Backend crea transacción en Wompi (estado: PENDING)
3. Backend guarda referencia interna en BD con status='pending'
4. Backend retorna URL de pago de Wompi al frontend
5. Usuario completa PSE en Wompi
6. Wompi llama webhook con resultado
7. Si APPROVED: acreditar wallet del usuario + registrar en BD
8. Si DECLINED: marcar como fallida, notificar usuario

# Webhook Wompi:
{
    "event": "transaction.updated",
    "data": {
        "transaction": {
            "id": "wompi_tx_id",
            "reference": "Nivo_internal_ref",
            "status": "APPROVED" | "DECLINED" | "VOIDED",
            "amount_in_cents": 10000000
        }
    },
    "signature": { "checksum": "...", "properties": [...] }
}
```

**Validar firma Wompi:**
```python
# Concatenar: propiedades + timestamp + events_secret
# SHA-256 del resultado == checksum
```

**Criterios de éxito:**
- [ ] Con credenciales sandbox Wompi: flujo PSE completo funciona en staging
- [ ] Webhook con firma inválida: retorna 200 pero NO acredita la billetera
- [ ] Doble procesamiento del mismo webhook: idempotente (no se acredita dos veces)
- [ ] La billetera se acredita SOLO cuando status='APPROVED' en el webhook
- [ ] Test de concurrencia: dos webhooks del mismo pago simultáneos → crédito exacto una vez

**Dependencias:** TASK-001, TASK-003

---

### TASK-008 — Sistema de Retiros a Cuenta Bancaria (ACH)
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** MEDIA

**Descripción:**
Permitir al usuario retirar dinero a su cuenta bancaria colombiana. En MVP usar Wompi
disbursements o ACH directo según disponibilidad.

**Archivos a crear:**
- CREAR `backend/app/api/v1/withdrawal.py`
- CREAR `backend/app/models/orm/bank_account.py` — Cuentas bancarias registradas
- MODIFICAR `backend/app/main.py` — Incluir router withdrawal

**Tabla bank_accounts:**
```sql
id: UUID PK
user_id: UUID FK -> users.id
bank_code: VARCHAR(10)      -- código banco colombiano (ej: "001" = Bancolombia)
account_type: ENUM('savings','checking')
account_number_encrypted: BYTEA  -- cifrado AES-256-GCM
account_holder_name: VARCHAR(255)
is_verified: BOOLEAN DEFAULT FALSE
created_at: TIMESTAMPTZ DEFAULT NOW()
```

**Reglas de negocio:**
- Número de cuenta NUNCA en plano en BD — siempre cifrado con AES-256-GCM
- Verificación: pequeño depósito de $500 COP y el usuario confirma el monto
- Límite de retiro: mismo que límite diario del plan
- Comisión de retiro: $0 en plan Plus y Pro, $2,000 COP en Free
- Tiempo de procesamiento: 1–2 días hábiles (informar al usuario)

**Criterios de éxito:**
- [ ] El número de cuenta nunca es recuperable en plano desde la API
- [ ] La verificación de cuenta con microdepósito funciona en staging
- [ ] Si el usuario no tiene cuenta verificada, el retiro es rechazado con mensaje claro

**Dependencias:** TASK-003, TASK-007

---

## MES 2 — SPRINT 3 (Semanas 5–8): Mobile App

---

### TASK-009 — Setup del Proyecto React Native
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 4–5 horas
**Prioridad:** CRÍTICA

**Descripción:**
Crear el proyecto React Native para la app móvil de Nivo desde cero con
Expo + TypeScript + NativeWind (Tailwind para RN).

**Archivos a crear:**
- CREAR `frontend/mobile/` — Nuevo directorio del proyecto RN
- CREAR `frontend/mobile/package.json`
- CREAR `frontend/mobile/app.json` — Config de Expo
- CREAR `frontend/mobile/tsconfig.json`
- CREAR `frontend/mobile/src/` — Estructura del proyecto
- CREAR `frontend/mobile/src/navigation/` — React Navigation
- CREAR `frontend/mobile/src/screens/` — Pantallas principales
- CREAR `frontend/mobile/src/components/` — Componentes reutilizables
- CREAR `frontend/mobile/src/services/api.ts` — Cliente HTTP hacia el backend
- CREAR `frontend/mobile/src/store/` — Estado global (Zustand)
- CREAR `frontend/mobile/src/theme/colors.ts` — Paleta de colores Nivo

**Stack:**
```json
{
  "expo": "~52.0.0",
  "react-native": "0.76.x",
  "typescript": "^5.3.0",
  "nativewind": "^4.0.0",
  "tailwindcss": "^3.4.0",
  "@react-navigation/native": "^7.0.0",
  "@react-navigation/stack": "^7.0.0",
  "@react-navigation/bottom-tabs": "^7.0.0",
  "zustand": "^5.0.0",
  "axios": "^1.7.0",
  "react-hook-form": "^7.53.0",
  "zod": "^3.23.0",
  "@tanstack/react-query": "^5.59.0",
  "expo-secure-store": "~14.0.0",
  "expo-notifications": "~0.29.0",
  "react-native-reanimated": "~3.16.0"
}
```

**Colores Nivo (definir en `theme/colors.ts`):**
```typescript
export const colors = {
  primary: '#38BDF8',       // sky-400 — Nivo Blue
  primaryLight: '#7DD3FC',  // sky-300
  primaryDark: '#0284C7',   // sky-600
  background: '#0B1120',    // slate-950
  surface: '#1E293B',       // slate-800
  surfaceLight: '#334155',  // slate-700
  text: '#F8FAFC',          // slate-50
  textMuted: '#94A3B8',     // slate-400
  success: '#22C55E',       // green-500
  error: '#EF4444',         // red-500
  warning: '#F59E0B',       // amber-500
  quantum: '#38BDF8',       // mismo que primary — alias semántico
}
```

**Estructura de navegación:**
```
Root Navigator (Stack)
├── AuthStack (cuando no hay sesión)
│   ├── SplashScreen
│   ├── OnboardingScreen
│   ├── PhoneInputScreen
│   └── OTPVerifyScreen
└── AppStack (cuando hay sesión)
    └── BottomTabs
        ├── HomeTab → HomeScreen
        ├── SendTab → SendMoneyScreen
        ├── HistoryTab → HistoryScreen
        └── ProfileTab → ProfileScreen
```

**Criterios de éxito:**
- [ ] `cd frontend/mobile && npx expo start` — arranca sin errores
- [ ] La pantalla inicial se ve en iOS Simulator y Android Emulator
- [ ] NativeWind funciona: `<View className="bg-slate-950 flex-1" />` aplica el estilo
- [ ] TypeScript no tiene errores: `npx tsc --noEmit`
- [ ] El cliente API apunta a `http://localhost:8000` en desarrollo y es configurable

**Dependencias:** Ninguna (es paralelo al backend)

---

### TASK-010 — Pantalla de Onboarding y Registro por Celular
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 6–8 horas
**Prioridad:** CRÍTICA

**Descripción:**
Implementar el flujo completo de registro: onboarding de 3 slides, entrada del número
de celular colombiano, y verificación OTP con teclado numérico.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/auth/SplashScreen.tsx`
- CREAR `frontend/mobile/src/screens/auth/OnboardingScreen.tsx`
- CREAR `frontend/mobile/src/screens/auth/PhoneInputScreen.tsx`
- CREAR `frontend/mobile/src/screens/auth/OTPVerifyScreen.tsx`
- CREAR `frontend/mobile/src/components/auth/OTPInput.tsx` — Input de 6 dígitos
- CREAR `frontend/mobile/src/components/auth/PhoneInput.tsx` — Input con bandera 🇨🇴

**Especificaciones de diseño (dark theme, colores Nivo):**

```
SplashScreen:
- Fondo slate-950
- Logo Nivo (átomo blindado) centrado con animación de glow pulsante
- Transición automática a OnboardingScreen después de 2.5 segundos

OnboardingScreen (3 slides con swipe):
Slide 1:
  - Ícono: escudo cuántico animado
  - Título: "La billetera más segura de Colombia"
  - Subtítulo: "Cifrado post-cuántico en cada pago. El mismo estándar que usan los gobiernos."

Slide 2:
  - Ícono: teléfono con transferencia animada
  - Título: "Paga por número de celular"
  - Subtítulo: "Sin cuentas bancarias. Sin formularios. Solo el número y listo."

Slide 3:
  - Ícono: escudo con checkmark
  - Título: "Tu plata, blindada para siempre"
  - Subtítulo: "Las firmas cuánticas de hoy protegen tus transacciones en 20 años."

Botón final: "Crear mi billetera" → PhoneInputScreen

PhoneInputScreen:
- Header: "¿Cuál es tu número?" con subtítulo "Te enviaremos un código de verificación"
- Input con prefijo +57 fijo y bandera colombiana
- Validación: solo números, exactamente 10 dígitos después del +57
- Botón "Enviar código" deshabilitado hasta que el número sea válido
- Al enviar: indicador de carga, luego navegar a OTPVerifyScreen

OTPVerifyScreen:
- Muestra el número (enmascarado: +57 310 *** **56)
- Texto: "Ingresa el código de 6 dígitos que enviamos a tu número"
- Componente OTPInput: 6 cajas individuales, focus automático
- Auto-verificar cuando los 6 dígitos están completos
- Link "Reenviar código" (deshabilitado por 60 segundos con countdown)
- En éxito: navegar a HomeScreen con animación de escudo cuántico

OTPInput component:
- 6 TextInput individuales
- Al escribir en uno, focus pasa automáticamente al siguiente
- Al borrar, focus vuelve al anterior
- En iOS/Android muestra teclado numérico
- Animación de shake si el código es incorrecto
```

**Criterios de éxito:**
- [ ] El flujo completo de onboarding funciona sin errores en iOS y Android
- [ ] El input de número valida el formato colombiano (+57 + 10 dígitos)
- [ ] El OTP input tiene focus automático y backspace funciona correctamente
- [ ] Al completar el OTP, se llama `POST /api/v1/auth/verify-otp` real
- [ ] Los 3 slides tienen animaciones fluidas con `react-native-reanimated`

**Dependencias:** TASK-009

---

### TASK-011 — Pantalla Home (Billetera + Saldo + Acciones rápidas)
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 6–8 horas
**Prioridad:** CRÍTICA

**Descripción:**
La pantalla principal de la app. Muestra el saldo, el escudo cuántico activo,
y los botones de acciones rápidas (Enviar, Recibir, Recargar, Historial).

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/HomeScreen.tsx`
- CREAR `frontend/mobile/src/components/wallet/BalanceCard.tsx`
- CREAR `frontend/mobile/src/components/wallet/QuantumShieldBadge.tsx`
- CREAR `frontend/mobile/src/components/wallet/QuickActions.tsx`
- CREAR `frontend/mobile/src/components/wallet/RecentTransactions.tsx`

**Especificaciones de diseño:**

```
HomeScreen layout (dark, slate-950 background):

─────────────────────────────────────────────
  Header:
  "Hola, [nombre]"            [Foto / Avatar]
  [Fecha: Martes 14 Abr]

─────────────────────────────────────────────
  BalanceCard (rounded-3xl, gradient slate-900→sky-950):
  ┌─────────────────────────────────────────┐
  │  Saldo disponible                        │
  │  $1.250.000 COP               [👁 ocultar]│
  │                                          │
  │  ⚛️ Escudo Cuántico Activo               │
  │  ML-KEM-768 · ML-DSA-65                 │
  └─────────────────────────────────────────┘

  QuantumShieldBadge:
  - Pequeño indicador verde pulsante: "Protegido"
  - Al tocar: modal explicando qué es PQC en lenguaje simple

─────────────────────────────────────────────
  QuickActions (4 botones en fila):
  [↑ Enviar]  [↓ Recibir]  [+ Recargar]  [↕ Retirar]
  Íconos con fondo sky-400/10, texto sky-300

─────────────────────────────────────────────
  Últimas transacciones (flat list):
  Sección "Recientes" con 5 últimas transacciones
  Cada item: [Avatar] [Nombre/Número] [Monto] [Estado]
  Link "Ver todo" → HistoryScreen
─────────────────────────────────────────────
```

**QuantumShieldBadge modal (cuando el usuario toca el badge):**
```
Título: "¿Qué es el Escudo Cuántico?"
Texto: "Cada transacción en Nivo está protegida con ML-KEM-768,
el estándar de cifrado post-cuántico certificado por el gobierno de EE.UU. en 2024.
Esto significa que tus pagos están seguros incluso contra computadoras del futuro.
Ninguna otra billetera colombiana ofrece esto."
Botón: "Entendido"
```

**Criterios de éxito:**
- [ ] El saldo se carga desde `GET /api/v1/users/me/wallet` real
- [ ] El botón de ocultar saldo muestra `$••••••• COP`
- [ ] El QuantumShieldBadge pulsa suavemente con `react-native-reanimated`
- [ ] Las 5 últimas transacciones se cargan desde `GET /api/v1/payments/?page=1&page_size=5`
- [ ] Pull-to-refresh refresca el saldo y las transacciones

**Dependencias:** TASK-009, TASK-003

---

### TASK-012 — Flujo Completo de Envío de Dinero P2P
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 8–10 horas
**Prioridad:** CRÍTICA

**Descripción:**
El flujo de pago P2P completo en la app: seleccionar receptor, ingresar monto,
confirmar con OTP, y ver el recibo con escudo cuántico.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/SendMoneyScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/ConfirmPaymentScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/PaymentSuccessScreen.tsx`
- CREAR `frontend/mobile/src/components/payment/AmountInput.tsx`
- CREAR `frontend/mobile/src/components/payment/QuantumReceipt.tsx`

**Flujo de pantallas:**
```
SendMoneyScreen:
  - Input: número de celular del receptor con autocompletar de contactos recientes
  - Input: monto en COP con formateador automático ($1.000.000)
  - Input: mensaje opcional (máx 100 chars)
  - Botón "Continuar" → ConfirmPaymentScreen

ConfirmPaymentScreen:
  - Resumen: "Vas a enviar $X a +57 3XX"
  - Badge: "⚛️ Protegido con ML-DSA-65"
  - Desglose: monto + comisión ($0 en Plus/Pro, $500 en Free si aplica)
  - OTP Input: "Confirma con tu código de seguridad"
  - Botón "Confirmar y Pagar"
  - Estado de carga: "Firmando con cifrado cuántico..." (0.5s) → "Procesando..." → éxito

PaymentSuccessScreen:
  - Animación: escudo cuántico que "cierra" con checkmark ✓
  - Título: "¡Listo! Enviaste $X"
  - Subtitle: "Recibido en segundos. Firmado cuánticamente."
  - QuantumReceipt component (tarjeta elegante con detalles):
    - ID de transacción (últimos 8 chars)
    - Fecha y hora
    - Monto
    - Receptor
    - "Firma cuántica: ML-DSA-65 ✓" con fingerprint (16 chars)
    - Botón "Compartir comprobante"
  - Botones: "Volver al inicio" | "Enviar otro"
```

**Criterios de éxito:**
- [ ] El flujo completo funciona de extremo a extremo con el backend real
- [ ] Si el usuario no tiene saldo suficiente, muestra error en español amigable
- [ ] La animación de éxito usa `react-native-reanimated` y dura ~1 segundo
- [ ] El comprobante se puede compartir como imagen via `expo-sharing`
- [ ] El fingerprint de firma ML-DSA-65 aparece en el recibo

**Dependencias:** TASK-009, TASK-011, TASK-003

---

## MES 2 — SPRINT 4 (Semanas 9–12): Recarga, Historial y Perfil

---

### TASK-013 — Pantalla de Recarga PSE y Retiro
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 5–6 horas
**Prioridad:** ALTA

**Descripción:**
Pantallas de recarga desde PSE (Wompi) y retiro a cuenta bancaria.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/TopUpScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/WithdrawScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/AddBankAccountScreen.tsx`

**Flujo recarga:**
```
TopUpScreen:
  - Input: monto a recargar
  - Montos sugeridos: $50K, $100K, $200K, $500K (botones rápidos)
  - Nota: "Te redirigiremos a PSE para completar el pago"
  - Botón "Recargar" → abre WebView con URL de Wompi
  - WebView monitorea la URL de retorno para detectar éxito/fallo
  - Al volver: mostrar pantalla de confirmación o error
```

**Criterios de éxito:**
- [ ] La WebView de Wompi se abre y el usuario puede completar PSE en sandbox
- [ ] Al volver de Wompi exitoso, el saldo se actualiza en HomeScreen
- [ ] El formulario de cuenta bancaria valida el número de cuenta (8–16 dígitos)

**Dependencias:** TASK-009, TASK-007, TASK-008

---

### TASK-014 — Historial de Transacciones y Detalle
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 4–5 horas
**Prioridad:** ALTA

**Descripción:**
Lista paginada de movimientos con filtros y vista de detalle de cada transacción.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/HistoryScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/TransactionDetailScreen.tsx`
- CREAR `frontend/mobile/src/components/history/TransactionItem.tsx`

**Especificaciones:**
```
HistoryScreen:
  - FlatList con paginación (cargar 20 por scroll)
  - Filtros: Todos | Enviados | Recibidos | Recargas
  - Cada TransactionItem muestra:
    - Ícono dirección (flecha arriba/abajo)
    - Nombre/teléfono del otro lado
    - Monto (verde si recibido, rojo si enviado)
    - Fecha/hora
    - Indicador ⚛️ si tiene firma cuántica (siempre en Nivo)

TransactionDetailScreen:
  - Todos los datos de la tx
  - Sección "Seguridad cuántica":
    - Algoritmo: ML-DSA-65
    - Fingerprint de firma: [16 chars]
    - "Esta firma es verificable a perpetuidad"
  - Botón: "Descargar comprobante PDF"
```

**Criterios de éxito:**
- [ ] La lista carga desde API con paginación real (no todo de una vez)
- [ ] Los filtros funcionan cambiando el parámetro `direction` en la API
- [ ] El scroll infinito carga la siguiente página al llegar al final

**Dependencias:** TASK-009, TASK-011

---

### TASK-015 — Perfil de Usuario, KYC y Configuración
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 4–5 horas
**Prioridad:** MEDIA

**Descripción:**
Pantalla de perfil con estado de KYC, plan actual, y configuraciones de seguridad.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/ProfileScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/KYCScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/SecurityScreen.tsx`

**Secciones del perfil:**
```
ProfileScreen:
  [Avatar generado con iniciales]
  [Nombre / +57 310 xxx]
  [Plan: FREE / PLUS / PRO] → link a upgrade

  Sección "Verificación":
  [Estado KYC: ✓ Verificado | ⏳ Pendiente | ✗ Rechazado]
  → Si pendiente: botón "Verificar ahora" → KYCScreen

  Sección "Seguridad cuántica":
  [🔑 Mis llaves PQC] → ver fingerprint de llaves
  [⚛️ Algoritmo activo: ML-KEM-768]

  Sección "Configuración":
  [Notificaciones]
  [Idioma]
  [Cerrar sesión]
```

**Criterios de éxito:**
- [ ] El estado de KYC se muestra correctamente según el backend
- [ ] El fingerprint de llave PQC del usuario es visible y copiable
- [ ] "Cerrar sesión" llama `POST /api/v1/auth/logout` y limpia `expo-secure-store`

**Dependencias:** TASK-009, TASK-006

---

## MES 3 — SPRINT 5 (Semanas 13–16): Comercios y QR

---

### TASK-016 — Backend: Sistema de Comercios y Terminal QR
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
Implementar el módulo de comercios: registro, QR dinámico firmado con ML-DSA-65, y cobros.

**Archivos a crear:**
- CREAR `backend/app/api/v1/merchants.py`
- CREAR `backend/app/services/merchant_service.py`
- CREAR `backend/app/services/qr_service.py`

**Endpoints:**
```
POST /api/v1/merchants/register          — Registrar nuevo comercio
GET  /api/v1/merchants/me                — Info del comercio del usuario
POST /api/v1/merchants/qr/static         — Generar QR estático (firmado ML-DSA)
POST /api/v1/merchants/qr/dynamic        — Generar QR dinámico con monto (firmado ML-DSA)
POST /api/v1/merchants/charge            — Procesar cobro desde QR
GET  /api/v1/merchants/transactions      — Historial de cobros del comercio
GET  /api/v1/merchants/dashboard/summary — Resumen del día (total cobros, #transacciones)
```

**Especificaciones del QR:**
```python
# Estructura del payload del QR (JSON en el QR code):
{
    "version": "1.0",
    "merchant_id": "uuid",
    "merchant_name": "Restaurante El Cielo",
    "amount_cop": 50000_00,  # null en QR estático, monto fijo en dinámico
    "qr_id": "uuid",         # ID único del QR para evitar replay attacks
    "expires_at": "iso_timestamp",  # QR dinámico expira en 10 minutos
    "ml_dsa_signature": "hex",      # Firma del merchant sobre el payload anterior
    "algorithm": "ML-DSA-65"
}

# Al procesar un cobro desde QR:
1. Parsear el JSON del QR
2. Verificar la firma ML-DSA-65 del merchant
3. Verificar que qr_id no ha sido usado antes (Redis lookup)
4. Verificar que expires_at no ha vencido (solo QR dinámico)
5. Ejecutar payment_service.execute_payment()
6. Marcar qr_id como usado en Redis con TTL de 1 hora
```

**Criterios de éxito:**
- [ ] El QR generado se puede escanear con cualquier lector de QR y mostrar el JSON
- [ ] Un QR dinámico procesado dos veces retorna error en el segundo intento
- [ ] La firma ML-DSA-65 en el QR es verificable independientemente del backend
- [ ] El dashboard muestra el total cobrado del día en tiempo real

**Dependencias:** TASK-003, TASK-004

---

### TASK-017 — Frontend: App "Nivo Negocios" (modo comercio)
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
Modo comercio dentro de la app: generar QR de cobro, ver pagos recibidos en tiempo real,
y resumen del día.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/merchant/MerchantHomeScreen.tsx`
- CREAR `frontend/mobile/src/screens/merchant/GenerateQRScreen.tsx`
- CREAR `frontend/mobile/src/screens/merchant/MerchantTransactionsScreen.tsx`
- CREAR `frontend/mobile/src/components/merchant/QRDisplay.tsx`
- CREAR `frontend/mobile/src/components/merchant/PaymentReceivedAlert.tsx`

**Especificaciones:**
```
MerchantHomeScreen:
  - Resumen del día: Total cobrado | # Transacciones | Ticket promedio
  - Botón grande: "Generar código de cobro" (principal acción)
  - Lista de últimos cobros con tiempo transcurrido ("hace 5 min")
  - Indicador de conexión (⚛️ Quantum-Safe activo)

GenerateQRScreen:
  - Switch: QR Fijo (no pone monto) | QR con monto
  - Si QR con monto: input de monto
  - Botón "Generar QR"
  - QR Display: QR code grande, centered, fondo blanco (para escanear)
  - Bajo el QR: "Firmado con ML-DSA-65 ⚛️"
  - Timer si es QR dinámico: "Expira en 09:45"
  - Botón "Nuevo QR" para generar otro

PaymentReceivedAlert:
  - Modal/Toast que aparece cuando se recibe un pago
  - "💚 ¡Recibiste $X de [nombre]!"
  - Animación de entrada desde la parte superior
  - Auto-dismiss en 5 segundos
```

**Criterios de éxito:**
- [ ] El QR se genera y se puede escanear con la cámara del celular
- [ ] Al pagar con otro dispositivo, el PaymentReceivedAlert aparece en < 3 segundos
- [ ] El resumen del día se actualiza en tiempo real (polling cada 30s o WebSocket)

**Dependencias:** TASK-009, TASK-016

---

## MES 3–4 — SPRINT 6 (Semanas 17–20): Lanzamiento Público

---

### TASK-018 — Landing Page: Completar Versión Producción
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 6–8 horas
**Prioridad:** ALTA

**Descripción:**
Completar la landing page existente en `landing_page/nivo/`:
agregar sección de pricing, sección de testimonios, formulario de lista de espera beta,
y optimizar para móvil.

**Archivos a modificar/crear:**
- MODIFICAR `landing_page/nivo/src/pages/home.tsx` — Agregar nuevas secciones
- CREAR `landing_page/nivo/src/sections/pricing.tsx` — Planes y precios
- CREAR `landing_page/nivo/src/sections/waitlist.tsx` — Formulario de beta
- CREAR `landing_page/nivo/src/sections/social-proof.tsx` — Logos y números
- MODIFICAR `landing_page/nivo/src/sections/flywheel.tsx` — Ya tiene CTA, mejorar

**Sección de Pricing:**
```
3 planes en cards:
┌─────────────┐ ┌──────────────┐ ┌─────────────┐
│ FREE        │ │ PLUS ⭐      │ │ PRO         │
│ $0/mes      │ │ $9.900/mes   │ │ $24.900/mes │
│             │ │              │ │             │
│ ✓ Pagos P2P │ │ ✓ Todo FREE  │ │ ✓ Todo PLUS │
│ ✓ PQC básico│ │ ✓ Tarj. virt.│ │ ✓ Multi-moneda│
│ ✓ Recarga   │ │ ✓ Límite $5M │ │ ✓ COP/USD/EUR│
│   PSE       │ │ ✓ Recibos    │ │ ✓ API básica │
│             │ │   cert.      │ │ ✓ Soporte   │
│             │ │              │ │   prioritario│
└─────────────┘ └──────────────┘ └─────────────┘

Card PLUS tiene badge "Más popular" y borde sky-400
```

**Formulario de lista de espera:**
```
Título: "Únete a la beta cerrada"
Input: número de celular
Input: email (opcional)
Checkbox: "Soy desarrollador / tengo una empresa" (para priorizar B2B)
Botón: "Reservar mi lugar"
→ POST a https://formspree.io o servicio similar
→ Mostrar confirmación: "¡Estás en la lista! Te avisamos cuando lancemos."
```

**Criterios de éxito:**
- [ ] La landing page tiene score > 90 en Lighthouse Mobile
- [ ] El formulario de lista de espera envía datos (probar con email real)
- [ ] La página es completamente responsive (probar en 375px, 768px, 1440px)
- [ ] Todas las secciones tienen sus textos en español colombiano

**Dependencias:** Ninguna

---

### TASK-019 — CI/CD Pipeline con GitHub Actions
**Estado:** [>] IN_PROGRESS
**Agente sugerido:** devops
**Estimado:** 6–8 horas
**Prioridad:** ALTA
**Nota parcial (T-04 done):** Job `migration-check` en `.github/workflows/ci.yml` implementado — PostgreSQL 16 limpio, `alembic upgrade head`, `alembic check`, downgrade/upgrade cycle. Falta: `backend-deploy-staging.yml`, `backend-deploy-prod.yml`, `Dockerfile.prod`, branch protection en GitHub (UI).

**Descripción:**
Configurar pipelines de CI/CD para el backend. Cada PR debe pasar tests antes de merge.
Cada push a main debe deployar automáticamente a staging.

**Archivos a crear:**
- CREAR `.github/workflows/backend-ci.yml` — Tests en cada PR
- CREAR `.github/workflows/backend-deploy-staging.yml` — Deploy automático a staging
- CREAR `.github/workflows/backend-deploy-prod.yml` — Deploy manual a producción
- CREAR `backend/Dockerfile.prod` — Imagen de producción optimizada

**`backend-ci.yml` debe:**
```yaml
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: # imagen postgres:16-alpine
      redis:    # imagen redis:7-alpine
    steps:
      - Checkout
      - Setup Python 3.11
      - Install liboqs (desde fuente)
      - pip install -r requirements.txt
      - ruff check .
      - mypy app/ --ignore-missing-imports
      - pytest tests/ -v --cov=app --cov-fail-under=80
      - Upload coverage report
```

**`Dockerfile.prod` requisitos:**
```dockerfile
# Multi-stage build para imagen pequeña
# Stage 1: builder (instala liboqs y compilaciones)
# Stage 2: runtime (solo lo necesario para correr)
# Usuario no-root para seguridad
# Health check incluido
# Tamaño final objetivo: < 500MB
```

**Criterios de éxito:**
- [ ] Cada PR abre un check "backend-ci" que pasa o falla automáticamente
- [ ] Un push a `main` dispara deploy a staging en < 5 minutos
- [ ] El deploy a producción requiere aprobación manual (environment protection)
- [ ] La imagen Docker de producción corre como usuario no-root

**Dependencias:** TASK-004 (tests deben existir antes del CI)

---

### TASK-020 — Sistema de Notificaciones Push (Firebase)
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 4–5 horas
**Prioridad:** MEDIA

**Descripción:**
Implementar notificaciones push para: pago recibido, recarga confirmada, alerta de fraude.

**Archivos a crear/modificar:**
- MODIFICAR `backend/app/services/notification_service.py` — Implementación real
- CREAR `backend/app/models/orm/device_token.py` — Tokens de dispositivos

**Tabla device_tokens:**
```sql
id: UUID PK
user_id: UUID FK -> users.id
token: VARCHAR(500) NOT NULL
platform: ENUM('ios','android')
is_active: BOOLEAN DEFAULT TRUE
created_at: TIMESTAMPTZ DEFAULT NOW()
INDEX: (user_id, is_active)
```

**Notificaciones a implementar:**
```python
async def notify_payment_received(receiver_id, amount_display, sender_name):
    title = "💚 ¡Recibiste dinero!"
    body = f"Te enviaron {amount_display} — ya está en tu billetera Nivo"

async def notify_topup_confirmed(user_id, amount_display):
    title = "✅ Recarga exitosa"
    body = f"{amount_display} fueron agregados a tu billetera"

async def notify_fraud_alert(user_id, transaction_details):
    title = "⚠️ Actividad inusual detectada"
    body = "Detectamos un intento de transacción inusual. Tu billetera está protegida."
```

**Criterios de éxito:**
- [ ] Al completar un pago P2P, el receptor recibe push en < 3 segundos
- [ ] Si el token FCM está inactivo, se elimina de BD automáticamente
- [ ] Las notificaciones funcionan con la app en segundo plano y cerrada

**Dependencias:** TASK-003

---

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

## MES 5–6 — SPRINT 8–12: Escala, Modelo ML y Preparación Serie

---

### TASK-024 — Modelo de Fraude con ML (Isolation Forest)
**Estado:** [ ] PENDING
**Agente sugerido:** ml
**Estimado:** 12–16 horas
**Prioridad:** MEDIA

**Descripción:**
Implementar el primer modelo de ML para detección de fraude usando
comportamiento histórico del usuario (embeddings de secuencias de transacciones).

**Archivos a crear:**
- CREAR `backend/app/ml/fraud_model.py` — Modelo Isolation Forest
- CREAR `backend/app/ml/feature_engineering.py` — Extracción de features
- CREAR `backend/app/ml/model_training.py` — Script de entrenamiento
- CREAR `backend/ml_models/` — Directorio para artefactos de modelos

**Features a extraer por usuario (últimos 30 días):**
```python
features = {
    "avg_tx_amount": float,          # Monto promedio de transacciones
    "std_tx_amount": float,          # Desviación estándar de montos
    "tx_per_day_avg": float,         # Transacciones promedio por día
    "unique_recipients_count": int,  # Número de receptores únicos
    "night_tx_ratio": float,         # % de transacciones 10pm–6am
    "weekend_tx_ratio": float,       # % de transacciones en fin de semana
    "max_single_tx": float,          # Monto máximo en período
    "days_since_first_tx": int,      # Antigüedad del usuario
    "failed_tx_ratio": float,        # % de transacciones fallidas
}

# Para la transacción actual:
current_features = {
    "amount_vs_avg_ratio": float,    # Monto actual / promedio
    "time_since_last_tx_hours": float,
    "is_new_recipient": bool,
    "is_night_transaction": bool,
}
```

**Pipeline:**
```
1. Extraer features → feature_engineering.py
2. Normalizar con StandardScaler
3. Isolation Forest con contamination=0.05 (5% fraude esperado)
4. Score de anomalía → risk_score entre 0.0 y 1.0
5. Si risk_score > 0.7 → REVIEW
6. Si risk_score > 0.9 → BLOCK
```

**Criterios de éxito:**
- [ ] El modelo corre en < 20ms por transacción (tiempo de inferencia)
- [ ] El modelo se puede entrenar/reentrenar con `python model_training.py`
- [ ] El artefacto del modelo se carga al arrancar el servicio (pickle o joblib)
- [ ] La integración con `fraud_detection_service.py` reemplaza la regla 2 (monto inusual)

**Dependencias:** TASK-023, datos de transacciones reales o sintéticos para entrenar

---

### TASK-025 — Multi-Moneda: COP, USD, EUR
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** MEDIA

**Descripción:**
Implementar soporte para billeteras en USD y EUR (solo plan Pro).
Integrar API de tipo de cambio para conversiones.

**Archivos a crear:**
- CREAR `backend/app/services/fx_service.py` — Tipo de cambio en tiempo real
- MODIFICAR `backend/app/models/orm/wallet.py` — Soporte multi-wallet
- CREAR `backend/app/api/v1/fx.py` — Endpoints de cambio de divisa

**Especificaciones:**
```python
# fx_service.py — Usar API de Frankfurter (gratuita, sin API key)
# https://api.frankfurter.app/latest?from=USD&to=COP

# Spread: 1.5% sobre el tipo de cambio de mercado
# Ejemplo: mercado 4,200 COP/USD → Nivo: 4,137 COP/USD (venta)

# Actualizar tasas cada 1 hora y cachear en Redis
# Si la API falla, usar la última tasa conocida + badge de alerta
```

**Endpoints:**
```
GET  /api/v1/fx/rates               — Tasas actuales COP/USD/EUR
POST /api/v1/fx/convert             — Solicitar conversión
GET  /api/v1/fx/wallets             — Todas las billeteras del usuario por moneda
```

**Criterios de éxito:**
- [ ] Un usuario Pro puede tener saldo en COP, USD y EUR simultáneamente
- [ ] La conversión incluye el spread del 1.5% claramente mostrado al usuario
- [ ] Las tasas se actualizan sin downtime (refresh en Redis background)

**Dependencias:** TASK-003, TASK-001

---

### TASK-026 — Dashboard Web para Comercios (Next.js)
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 12–16 horas
**Prioridad:** MEDIA

**Descripción:**
Dashboard web para comercios: ver transacciones, generar reportes,
y configurar el perfil del negocio. Usar Next.js 15 + shadcn/ui.

**Archivos a crear:**
- CREAR `frontend/dashboard/` — Nuevo proyecto Next.js
- CREAR `frontend/dashboard/src/app/page.tsx` — Login
- CREAR `frontend/dashboard/src/app/dashboard/page.tsx` — Panel principal
- CREAR `frontend/dashboard/src/app/transactions/page.tsx` — Transacciones
- CREAR `frontend/dashboard/src/app/qr/page.tsx` — Gestión de QR codes
- CREAR `frontend/dashboard/src/app/settings/page.tsx` — Configuración

**Tech stack:**
```json
{
  "next": "15.x",
  "typescript": "^5.3.0",
  "tailwindcss": "^3.4.0",
  "@shadcn/ui": "latest",
  "recharts": "^2.x",
  "@tanstack/react-query": "^5.x",
  "axios": "^1.x"
}
```

**Dashboard principal debe mostrar:**
```
┌─────────────────────────────────────────────────────┐
│ Hoy: $X cobrado | Y transacciones | $Z ticket prom  │
├──────────────────────────┬──────────────────────────┤
│ Gráfica de cobros/hora   │ Últimas transacciones     │
│ (recharts BarChart)      │ (tabla con QR id, monto,  │
│                          │  hora, estado)            │
├──────────────────────────┴──────────────────────────┤
│ QR Activos: [lista de QR estáticos]                 │
│ Botón: "Generar nuevo QR de cobro"                  │
└─────────────────────────────────────────────────────┘
```

**Criterios de éxito:**
- [ ] `cd frontend/dashboard && npm run dev` arranca sin errores
- [ ] La gráfica de cobros se actualiza con datos reales del backend
- [ ] El export de transacciones genera un CSV descargable
- [ ] El dashboard es responsive (funciona en tablet)

**Dependencias:** TASK-016

---

### TASK-027 — Auditoría de Seguridad PQC Interna
**Estado:** [ ] PENDING
**Agente sugerido:** security
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
Revisión interna exhaustiva del módulo `CryptoService` y de todos los flujos
donde se maneja material criptográfico, antes de la auditoría externa del Mes 8.

**Revisiones requeridas:**

```
1. REVISIÓN DEL CÓDIGO CRYPTO:
   - ¿El nonce de AES-GCM es siempre aleatorio (os.urandom(12))? ¿Nunca reutilizado?
   - ¿La derivación HKDF incluye el contexto correcto (b"Nivo-hybrid-v1")?
   - ¿Las llaves privadas nunca aparecen en logs?
   - ¿Los errores de verificación retornan False sin revelar información?

2. REVISIÓN DE SECRETS EN BD:
   - ¿Las llaves privadas PQC nunca están en PostgreSQL en plano?
   - ¿Los números de cuenta bancaria están cifrados?
   - ¿Los OTPs se almacenan como hash (bcrypt), nunca en plano?
   - ¿Los tokens JWT están en blacklist después de logout?

3. REVISIÓN DE API:
   - ¿Todos los endpoints sensibles requieren autenticación JWT?
   - ¿Los webhooks de Wompi/Truora validan firma HMAC?
   - ¿Los rate limits están activos en producción?
   - ¿Los errores 500 no revelan stack traces al cliente?

4. REVISIÓN DE INFRAESTRUCTURA:
   - ¿Las variables de entorno con secretos no están en el repositorio?
   - ¿El Dockerfile.prod corre como usuario no-root?
   - ¿Las conexiones a BD usan SSL?
```

**Entregable:** Documento `docs/07-security-audit-internal.md` con:
- Cada punto revisado con resultado: PASS / FAIL / RISK
- Para cada FAIL: descripción del problema y solución implementada
- Checklist de items para auditoría externa

**Criterios de éxito:**
- [ ] Todos los ítems de la categoría "CRÍTICO" son PASS
- [ ] El documento `07-security-audit-internal.md` existe y está completo
- [ ] No hay ningún secreto (API key, password, private key) en el historial de git

**Dependencias:** TASK-004, TASK-002, TASK-007

---

### TASK-028 — Performance Testing y Optimización
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** MEDIA

**Descripción:**
Medir y optimizar el rendimiento del backend. El objetivo es soportar 1,000 transacciones
concurrentes sin degradación.

**Archivos a crear:**
- CREAR `backend/tests/load/test_payments_load.py` — Pruebas de carga con locust
- CREAR `backend/tests/load/locustfile.py`

**Métricas objetivo:**
```
P2P Payment (POST /payments/confirm):
  - Latencia P50: < 300ms
  - Latencia P95: < 800ms
  - Latencia P99: < 1500ms
  - Error rate: < 0.1%

Health check (GET /health):
  - Latencia P99: < 50ms

PQC Sign (POST /crypto/sign):
  - Latencia P95: < 200ms (incluye liboqs)
```

**Script de carga (locust):**
```python
# Simular 1,000 usuarios concurrentes haciendo pagos
# 80% pagos P2P, 10% consulta de historial, 10% consulta de saldo
# Duración: 10 minutos
# Ramping: 0→1000 usuarios en 2 minutos
```

**Optimizaciones a implementar si los números no se logran:**
1. Connection pooling de BD (ajustar `pool_size`)
2. Cache de Redis para saldo de usuario (TTL: 30 segundos)
3. Índices de BD faltantes (analizar EXPLAIN ANALYZE)
4. Async en todas las operaciones de BD (verificar no haya calls síncronos)

**Criterios de éxito:**
- [ ] `locust -f locustfile.py --headless -u 1000 -r 100 --run-time 10m` completa sin errores
- [ ] P95 de pagos < 800ms con 1,000 usuarios concurrentes
- [ ] El reporte de locust se guarda como `tests/load/reports/baseline.html`

**Dependencias:** TASK-003, TASK-019

---

### TASK-029 — Documentación de API y SDK Python Inicial
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** MEDIA

**Descripción:**
Crear la documentación pública de la API B2B y el SDK Python básico para facilitar
la integración de clientes enterprise.

**Archivos a crear:**
- CREAR `backend/sdk/python/Nivo_sdk/__init__.py`
- CREAR `backend/sdk/python/Nivo_sdk/client.py`
- CREAR `backend/sdk/python/Nivo_sdk/models.py`
- CREAR `backend/sdk/python/README.md`
- CREAR `backend/sdk/python/examples/sign_document.py`
- CREAR `backend/sdk/python/examples/key_exchange.py`

**SDK Python debe permitir:**
```python
from Nivo_sdk import NivoClient

client = NivoClient(api_key="nv_live_xxxxx")

# Firmar datos con llave administrada por Nivo/KMS/HSM
result = client.sign(data=b"datos a firmar", key_id="kms_receipts_prod")
print(result.signature_hex)    # ML-DSA-65 signature
print(result.fingerprint)      # SHA-256 de la llave pública

# Verificar
valid = client.verify(
    data=b"datos a firmar",
    signature_hex=result.signature_hex,
    public_key_hex=result.public_key_hex
)
# True

# Key exchange híbrido
exchange = client.key_exchange(
    recipient_pqc_key_hex="...",
    recipient_x25519_key_hex="..."
)
# exchange.pqc_ciphertext_hex + exchange.classical_public_key_hex se envían al receptor.
# El shared secret no se retorna en producción.
```

**Criterios de éxito:**
- [ ] `pip install -e .` desde `backend/sdk/python/` instala el SDK sin errores
- [ ] Los dos ejemplos en `examples/` corren contra el servidor de staging
- [ ] El README explica en < 10 minutos cómo integrar PQC a un sistema existente
- [ ] El SDK incluye modo client-side signing para clientes que no delegan firma a Nivo

**Dependencias:** TASK-021

---

### TASK-030 — Preparación para Ronda Seed: Métricas y Data Room
**Estado:** [>] IN_PROGRESS
**Parcialmente completado (T-13):** business_metrics_daily ORM + MetricsService + admin endpoints + 15 tests. Pendiente: dashboard Metabase, data dictionary, PostHog/Mixpanel evaluation.
**Agente sugerido:** ceo
**Estimado:** 8–10 horas
**Prioridad:** ALTA (Mes 6)

**Descripción:**
Crear todos los materiales técnicos para el data room de la ronda Seed.
Los VCs necesitan verificar que la tecnología es real.

**Archivos a crear:**
- CREAR `docs/08-technical-due-diligence.md` — Respuestas a preguntas típicas de VC
- CREAR `docs/09-metrics-dashboard.md` — Métricas clave con datos reales
- CREAR `scripts/generate_metrics_report.py` — Script que genera reporte de métricas desde BD

**`technical-due-diligence.md` debe responder:**
```
1. ¿Por qué liboqs y no implementación propia? (respuesta: nunca implementar crypto propio)
2. ¿Qué pasa si NIST depreca ML-KEM-768? (respuesta: crypto-agility, cambio en días)
3. ¿Cuál es el overhead de rendimiento de PQC vs. clásico? (datos reales del benchmark)
4. ¿Cómo está la competencia global en PQC para pagos? (Cloudflare, Google, Signal)
5. ¿Tienen auditoría de seguridad? (resultado de TASK-027)
6. ¿Cuál es el plan de migración para usuarios de Nequi? (análisis de switching costs)
7. ¿Cómo escala la infraestructura a 10M usuarios? (Cloud Run autoscaling + Cloud SQL read replicas)
```

**`metrics-dashboard.md` debe incluir (con datos reales del sistema):**
```
- Usuarios activos mensuales (MAU)
- Transacciones procesadas total y por día
- Volumen procesado en COP
- Latencia promedio P2P
- Uptime del sistema (últimos 30 días)
- Número de comercios activos
- MRR (Monthly Recurring Revenue)
- Contratos B2B firmados o en pipeline
- NPS score de usuarios beta
```

**Criterios de éxito:**
- [ ] El data room está completo y verificable (no afirmaciones sin datos)
- [ ] `python generate_metrics_report.py` genera un PDF con métricas reales
- [ ] La auditoría de seguridad interna está documentada y disponible para due diligence

**Dependencias:** TASK-027, datos de producción reales (beta cerrada)

---

## TAREAS TRANSVERSALES (todo el período)

---

### TASK-031 — Monitoreo y Alertas de Producción
**Estado:** [>] IN_PROGRESS
**Agente sugerido:** devops
**Estimado:** 4–5 horas
**Prioridad:** ALTA
**Nota parcial (T-05 + T-09 done):** OpenTelemetry instrumentado en rutas críticas (auth OTP, P2P execute, webhook firma, wallet credit) con FastAPIInstrumentor + SQLAlchemyInstrumentor. AlertService con Slack Block Kit para webhooks fallidos (3 fallos/10 min → alerta, rate limit 5 min). Falta: Sentry integration, GCP Cloud Monitoring, runbooks en `docs/runbooks/`, dashboard golden signals.

**Descripción:**
Configurar Sentry + GCP Cloud Monitoring + alertas para el equipo.

**Alertas a configurar:**
```
CRÍTICO (PagerDuty/SMS inmediato):
  - /health/pqc retorna 503
  - Error rate > 1% en /payments/confirm
  - Tiempo de respuesta P99 > 3 segundos por 5 minutos
  - BD sin conexión

ALTA (Slack/email en < 5 minutos):
  - Error rate > 0.5% en cualquier endpoint
  - Memoria del contenedor > 80%
  - Cola de OTPs pendientes > 1000
  - Número de fraud_alerts de nivel BLOCK > 10 en 1 hora

MEDIA (email diario):
  - Espacio de disco > 70%
  - Latencia P95 > 500ms
  - Errores de webhook de Wompi/Truora
```

**Criterios de éxito:**
- [ ] Cada alerta tiene runbook documentado en `docs/runbooks/`
- [ ] Una alerta de test dispara el canal de Slack correcto

**Dependencias:** TASK-019

---

### TASK-032 — Prueba de Concepto liboqs en Producción (GCP Cloud Run)
**Estado:** [ ] PENDING
**Agente sugerido:** devops
**Estimado:** 4–5 horas
**Prioridad:** CRÍTICA

**Descripción:**
Verificar que liboqs funciona correctamente en el ambiente de Cloud Run de GCP.
Hay consideraciones de CPU y memoria que deben validarse.

**Pasos:**
```
1. Build de Dockerfile.prod con liboqs compilado desde fuente
2. Push a Google Container Registry (gcr.io/Nivo-staging/api)
3. Deploy a Cloud Run staging con:
   - CPU: 1 vCPU mínimo
   - Memoria: 512MB mínimo
   - Concurrencia: 100 requests por instancia
4. Ejecutar test de health PQC: GET /health/pqc debe retornar {"pqc": "PASS"}
5. Ejecutar benchmark de ML-DSA sign: medir latencia real en Cloud Run
6. Verificar que liboqs_available=true en el response
```

**Problema potencial:**
Cloud Run usa contenedores efímeros. Verificar que liboqs (biblioteca C compartida)
está disponible en el PATH del contenedor en producción y no solo en el builder stage.

**Criterios de éxito:**
- [ ] `GET https://staging-api.Nivo.co/health/pqc` retorna `{"pqc": "PASS", "liboqs_available": true}`
- [ ] Latencia de sign en Cloud Run staging: < 10ms
- [ ] El contenedor arranca en < 10 segundos (cold start)

**Dependencias:** TASK-019

---

### TASK-033 — FUTURO: Agentes de Portafolio con Riesgo Transparente
**Estado:** [ ] PENDING
**Agente sugerido:** product + legal + ml
**Estimado:** 2–4 semanas para discovery + prototipo cerrado
**Prioridad:** FUTURA

**Descripción:**
Diseñar un módulo donde el usuario pueda asignar una parte limitada de su portafolio a un agente de inversión automatizado. El producto debe ser absolutamente claro en la interfaz: es un agente, no una persona; puede tomar decisiones buenas o malas; puede generar ganancias o pérdidas; y no existe rendimiento garantizado.

**Principio de producto:**
El usuario siempre debe entender:
- Qué agente está actuando
- Qué parte del portafolio puede tocar
- Qué estrategia o reglas está siguiendo
- Cuánto puede perder
- Cómo pausarlo o apagarlo inmediatamente
- Quién es el partner regulado responsable de ejecución/custodia

**Alcance futuro:**
- Crear perfil de agente visible: nombre, estrategia, activos permitidos, horizonte, riesgo y comisiones
- Permitir asignación parcial del portafolio, nunca el 100% por defecto
- Definir límites duros: monto máximo, pérdida máxima, rebalanceo máximo, activos permitidos y frecuencia de operación
- Mostrar disclosure antes de activar: "Este agente puede equivocarse. Puedes ganar o perder dinero. Nivo no garantiza resultados."
- Requerir consentimiento explícito y renovable para cada estrategia
- Registrar cada decisión del agente con explicación simple, timestamp, datos usados y recibo verificable
- Agregar botón "Pausar agente" y "Retirar permisos" visible en todo momento
- Crear simulador/paper trading antes de permitir dinero real
- Separar agentes educativos, agentes de simulación y agentes con ejecución real

**Bloqueos regulatorios y legales:**
- No lanzar con dinero real sin broker/comisionista/partner autorizado o licencia que cubra asesoría/gestión automatizada
- No presentar el agente como asesor financiero humano
- No usar lenguaje de promesa: prohibido "garantizado", "seguro", "sin riesgo", "rentabilidad fija"
- Validar si el módulo constituye asesoría de inversión, administración de portafolio, gestión discrecional o intermediación de valores
- Incluir suitability/appropriateness cuando aplique y limitar acceso según perfil de riesgo del usuario

**Criterios de éxito del prototipo cerrado:**
- [ ] UX muestra claramente que es un agente automatizado antes, durante y después de la activación
- [ ] El usuario debe aceptar un disclosure de pérdida posible antes de activar
- [ ] El agente solo puede operar el porcentaje asignado por el usuario
- [ ] Existen límites configurables de pérdida, monto, frecuencia y activos
- [ ] Todas las decisiones quedan auditadas con explicación y recibo verificable
- [ ] El usuario puede pausar o revocar permisos en menos de 2 taps
- [ ] Modo simulación/paper trading funciona antes del modo con dinero real
- [ ] Legal aprueba partner, disclosures, términos y alcance regulatorio antes de cualquier piloto con fondos reales

**Dependencias:** TASK-025, diseño legal de crypto/acciones, broker/comisionista o partner autorizado, revisión compliance SFC/mercado de valores

---

### TASK-034 — Bolsillos de Ahorro y Metas Nivo
**Estado:** [ ] PENDING
**Agente sugerido:** product + backend + mobile + legal
**Estimado:** 1–2 semanas
**Prioridad:** ALTA

**Descripción:**
Implementar bolsillos de ahorro como parte central de la experiencia tipo Revolut. En MVP
pueden ser metas visuales; si existe banco/SEDPE/partner que soporte saldos reales, deben
sincronizarse mediante `provider_subaccount_ref` y mostrar claramente quién custodia el dinero.

**Archivos a crear/modificar:**
- CREAR `backend/app/api/v1/savings.py`
- CREAR `backend/app/services/savings_service.py`
- CREAR `backend/app/models/orm/savings_pocket.py`
- MODIFICAR mobile Home para mostrar bolsillos, progreso y reglas
- MODIFICAR términos/UX para distinguir `visual_goal`, `partner_subaccount` y `custodial`

**Reglas de producto:**
- El usuario puede crear metas: emergencia, viaje, impuestos, inversión, familia.
- Cada bolsillo tiene `mode`: `visual_goal`, `partner_subaccount` o `custodial`.
- Si el modo no es custodial, la UI no puede decir "depósito Nivo" ni "cuenta de ahorros Nivo".
- Cambios de estado y reglas automáticas se firman con ML-DSA para recibo verificable.
- Reglas opcionales: redondeo de compras, monto recurrente, porcentaje de ingreso.

**Criterios de éxito:**
- [ ] Crear, editar y eliminar bolsillos desde API y mobile
- [ ] Cada bolsillo muestra quién custodia el saldo o si es meta visual
- [ ] Reglas de ahorro generan movimientos/referencias firmadas sin duplicar transacciones
- [ ] No hay copy de captación propia si `mode=visual_goal` o `partner_subaccount`
- [ ] Tests cubren cambios de modo, límites y firma de estado

**Dependencias:** TASK-001, TASK-002, TASK-003

---

### TASK-035 — Módulos Regulados de Inversión, Crypto y FX
**Estado:** [ ] PENDING
**Agente sugerido:** product + backend + legal + compliance
**Estimado:** 2–4 semanas discovery + prototipo cerrado
**Prioridad:** ALTA

**Descripción:**
Diseñar e implementar la capa común de productos regulados para FX, crypto, acciones y ETFs.
Nivo mantiene la experiencia de una sola app, pero cada ejecución vive en el partner autorizado
hasta tener licencia propia.

**Archivos a crear/modificar:**
- CREAR `backend/app/api/v1/partner_orders.py`
- CREAR `backend/app/services/partner_order_service.py`
- CREAR `backend/app/services/disclosure_service.py`
- CREAR `backend/app/models/orm/partner_order.py`
- CREAR `backend/app/models/orm/product_disclosure.py`
- CREAR adapters: `fx_partner_adapter.py`, `crypto_partner_adapter.py`, `broker_partner_adapter.py`

**Reglas por módulo:**
- FX: mostrar tasa, spread/fee, vigencia, partner, fuente y tiempo estimado antes de confirmar.
- Crypto: disclosure de volatilidad, pérdida total, irreversibilidad, ausencia de garantía estatal, límites y AML reforzado.
- Acciones/ETFs: partner/broker visible, tipo de orden, costos, suitability/appropriateness si aplica, sin asesoría propia.
- Todas las órdenes guardan `risk_disclosure_version`, `accepted_disclosure_hash`, `partner`, `partner_order_id` y firma ML-DSA.
- El usuario debe poder ver "quién ejecuta" y "quién custodia" antes de confirmar.

**Criterios de éxito:**
- [ ] Se puede crear una orden simulada de FX/crypto/stock con disclosure aceptado
- [ ] La orden se firma con ML-DSA antes de enviarse al adapter del partner
- [ ] La API rechaza órdenes si falta partner, disclosure o perfil KYC requerido
- [ ] La UI muestra costos, riesgos, partner y estado de ejecución sin prometer rendimiento
- [ ] Legal/compliance aprueba texto de disclosures antes de cualquier piloto real

**Dependencias:** TASK-001, TASK-002, TASK-003, TASK-006, TASK-023, revisión legal/partner aprobado

---

## RESUMEN DE DEPENDENCIAS

```
SPRINT 0 — Correcciones (sin dependencias entre sí, se pueden hacer en paralelo):
  FIX-001 (init_db bug)
  FIX-002 (shared_secret exposure)
  FIX-003 (signing_key_hex)
  FIX-004 (crypto-agility config)
  FIX-005 (DB session injection) → depende de FIX-001
  FIX-006 (Transaction campos regulatorios)
  FIX-007 (CORS URLs)
  FIX-008 (rutas payments)
  FIX-009 (httpx duplicado)

TASK-001 (ORM)
  └─→ TASK-002 (JWT)
  └─→ TASK-003 (Pagos)
      └─→ TASK-007 (Wompi)
      └─→ TASK-008 (Retiros)
      └─→ TASK-020 (Push)
      └─→ TASK-023 (Fraude)
          └─→ TASK-024 (ML)
  └─→ TASK-006 (KYC)
  └─→ TASK-016 (Comercios)
      └─→ TASK-017 (Mobile comercios)
      └─→ TASK-026 (Dashboard)

TASK-004 (Tests crypto)
  └─→ TASK-019 (CI/CD)
      └─→ TASK-028 (Performance)
      └─→ TASK-031 (Monitoreo)
  └─→ TASK-021 (API B2B)
      └─→ TASK-029 (SDK)

TASK-009 (Setup RN)
  └─→ TASK-010 (Onboarding)
  └─→ TASK-011 (Home)
      └─→ TASK-012 (Pago P2P mobile)
      └─→ TASK-014 (Historial)
      └─→ TASK-034 (Bolsillos ahorro)
  └─→ TASK-013 (Recarga mobile)
  └─→ TASK-015 (Perfil)

TASK-025 (Multi-moneda)
  └─→ TASK-035 (FX / crypto / acciones por partner)

TASK-027 (Audit) → TASK-030 (Seed prep)
TASK-032 (liboqs GCP) → TASK-028 (Performance)
TASK-033 (Agentes portafolio) → Año 2+ con partner autorizado + legal aprobado
TASK-034 (Ahorro) → Fase 2 cuenta tipo Revolut
TASK-035 (Productos regulados) → Fase 3/Año 2 con partner autorizado
```

---

## ESTRUCTURA DE SPRINTS (OPTIMIZADA)

### ⚠️ SPRINT 0 — Hardening & Fixes Críticos (Día 0–2)

**Objetivo:** Que el sistema arranque seguro, sin bugs ni vulnerabilidades.  
**Bloqueante** de todo lo demás.

**Tasks:**
- FIX-001 — DB init bug
- FIX-002 — Eliminar `shared_secret`
- FIX-003 — Eliminar `signing_key_hex`
- FIX-004 — Crypto-agility desde `settings`
- FIX-006 — Campos regulatorios `Transaction`
- FIX-007 — CORS URLs
- FIX-008 — Rutas `payments`
- FIX-009 — `httpx` duplicado

**Luego:**
- FIX-005 (depende de FIX-001)

---

### 🧱 SPRINT 1 — Core Backend Foundation (Semana 1–2)

**Objetivo:** Backend funcional real (DB + Auth + Crypto testeado).

**Backend core:**
- TASK-001 — ORM SQLAlchemy
- TASK-002 — JWT + OTP + Redis
- TASK-004 — Tests Crypto (crítico para CI)
- TASK-005 — Twilio OTP

**Infra crítica:**
- TASK-032 — liboqs en GCP (validación real)

**Resultado esperado:**
- Backend autenticado
- Crypto validado
- DB lista

---

### 💸 SPRINT 2 — Motor de Pagos (Core Producto) (Semana 2–4)

**Objetivo:** Dinero se mueve end-to-end.

**Core payments:**
- TASK-003 — Pagos atómicos
- TASK-007 — Recarga PSE (Wompi)
- TASK-008 — Retiros ACH

**Compliance básico:**
- TASK-006 — KYC Truora

**Resultado esperado:**
- Registro → recarga → envío → retiro

---

### 📱 SPRINT 3 — Mobile MVP (App usable) (Semana 5–8)

**Objetivo:** App funcional completa.

**Setup + Auth:**
- TASK-009 — Setup RN
- TASK-010 — Onboarding + OTP

**Core UX:**
- TASK-011 — Home
- TASK-012 — Pago P2P

**Soporte:**
- TASK-013 — Recarga mobile
- TASK-014 — Historial
- TASK-015 — Perfil

**Resultado esperado:**
- App usable end-to-end (MVP real)

---

### 🏪 SPRINT 4 — Comercios + Infra Base (Semana 9–12)

**Objetivo:** Primer loop de monetización (QR).

**Comercios:**
- TASK-016 — Backend merchants + QR
- TASK-017 — Mobile modo comercio

**Infra:**
- TASK-019 — CI/CD
- TASK-020 — Push notifications

**Growth:**
- TASK-018 — Landing page

**Resultado esperado:**
- Comercios pueden cobrar
- Infra lista para escalar

---

### 🔐 SPRINT 5 — Seguridad, B2B y Monetización (Semana 13–16)

**Objetivo:** Producto serio + revenue streams.

**B2B:**
- TASK-021 — API PQC completa
- TASK-029 — SDK Python

**Fintech:**
- TASK-022 — Tarjeta virtual

**Riesgo:**
- TASK-023 — Fraude (reglas)

**Resultado esperado:**
- API vendible
- Primer revenue B2B
- Protección antifraude

---

### 🌍 SPRINT 6 — Escala & Expansión (Semana 17–20)

**Objetivo:** Expandir capacidades del producto.

**Finanzas avanzadas:**
- TASK-025 — Multi-moneda
- TASK-035 — Productos (FX / crypto / stocks)

**Comercios:**
- TASK-026 — Dashboard web

**Ahorro:**
- TASK-034 — Bolsillos

**Resultado esperado:**
- Producto tipo Revolut-lite

---

### 🧪 SPRINT 7 — Optimización & ML (Semana 21–22)

**Objetivo:** Performance + inteligencia.

**Tasks:**
- TASK-028 — Performance testing
- TASK-024 — Modelo ML fraude

**Resultado esperado:**
- Sistema robusto a escala
- Inteligencia antifraude

---

### 🛡️ SPRINT 8 — Auditoría & Producción Ready (Semana 23)

**Objetivo:** Preparar auditoría real.

**Tasks:**
- TASK-027 — Auditoría seguridad
- TASK-031 — Monitoreo y alertas

**Resultado esperado:**
- Listo para auditoría externa

---

### 💰 SPRINT 9 — Fundraising Ready (Semana 24)

**Objetivo:** Levantar capital.

**Tasks:**
- TASK-030 — Data room + métricas

**Resultado esperado:**
- Startup lista para levantar Seed

---

### 📊 Resumen Simplificado

- S0: Hardening obligatorio
- S1: Base backend lista
- S2: Dinero moviéndose end-to-end
- S3: Mobile MVP usable
- S4: Comercios + base de escala
- S5: Seguridad/B2B monetizable
- S6: Expansión de capacidades financieras
- S7: Optimización + ML
- S8: Auditoría y operación estable
- S9: Fundraising

**Backlog fuera de roadmap de 24 semanas:**
- TASK-033 — Agentes de Portafolio con Riesgo Transparente (Año 2+)

---

## TRACKING DE PROGRESO

| Task | Descripción corta | Mes | Estado |
|------|------------------|-----|--------|
| FIX-001 | Bug init_db() SQLAlchemy 2.0 | 0 | [x] |
| FIX-002 | Eliminar shared_secret de KeyExchangeResponse | 0 | [x] |
| FIX-003 | Eliminar signing_key_hex de SignRequest | 0 | [x] |
| FIX-004 | Conectar algoritmos PQC desde settings | 0 | [x] |
| FIX-005 | Inyectar sesión BD en routers | 0 | [x] |
| FIX-006 | Agregar campos regulatorios a Transaction | 0 | [x] |
| FIX-007 | Corregir URLs CORS (mayúsculas) | 0 | [x] |
| FIX-008 | Corregir orden de rutas payments.py | 0 | [x] |
| FIX-009 | Eliminar httpx duplicado en requirements | 0 | [x] |
| TASK-001 | ORM SQLAlchemy | 1 | [x] |
| TASK-002 | JWT Real | 1 | [x] |
| TASK-003 | Pagos Atómicos | 1 | [x] |
| TASK-004 | Tests Crypto | 1 | [x] |
| TASK-005 | Twilio OTP | 1 | [x] |
| TASK-006 | KYC Truora | 1 | [ ] |
| TASK-007 | PSE Wompi | 1 | [ ] |
| TASK-008 | Retiros ACH | 1 | [ ] |
| TASK-009 | Setup React Native | 2 | [ ] |
| TASK-010 | Onboarding Mobile | 2 | [ ] |
| TASK-011 | Home Screen | 2 | [ ] |
| TASK-012 | Pago P2P Mobile | 2 | [ ] |
| TASK-013 | Recarga Mobile | 2 | [ ] |
| TASK-014 | Historial Mobile | 2 | [ ] |
| TASK-015 | Perfil Mobile | 2 | [ ] |
| TASK-016 | Backend Comercios | 3 | [ ] |
| TASK-017 | Mobile Comercios | 3 | [ ] |
| TASK-018 | Landing Page Prod | 3 | [ ] |
| TASK-019 | CI/CD GitHub | 3 | [ ] |
| TASK-020 | Push Notifications | 3 | [ ] |
| TASK-021 | API B2B Completa | 4 | [ ] |
| TASK-022 | Tarjeta Virtual | 4 | [ ] |
| TASK-023 | Fraude v1 Reglas | 4 | [ ] |
| TASK-024 | Fraude ML | 5 | [ ] |
| TASK-025 | Multi-Moneda | 5 | [ ] |
| TASK-026 | Dashboard Web | 5 | [ ] |
| TASK-027 | Auditoría Interna | 5 | [ ] |
| TASK-028 | Performance Tests | 5 | [ ] |
| TASK-029 | SDK Python | 5 | [ ] |
| TASK-030 | Prep Ronda Seed | 6 | [ ] |
| TASK-031 | Monitoreo | Continuo | [ ] |
| TASK-032 | liboqs en GCP | 1 | [ ] |
| TASK-033 | Agentes de Portafolio | Año 2+ | [ ] |
| TASK-034 | Bolsillos de Ahorro | 4 | [ ] |
| TASK-035 | Inversión/Crypto/FX Partner | 5 | [ ] |

---

*Última actualización: Abril 2026*
*Mantener este archivo actualizado es obligatorio para todos los agentes.*
*Al iniciar una tarea: cambiar `[ ]` a `[>]`. Al terminar: cambiar a `[x]`.*
