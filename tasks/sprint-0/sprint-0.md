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
