# Nivo — Guía de Arranque Local

Paso a paso para levantar el backend de Nivo en tu máquina.

---

## ✅ Verificación confirmada

**29 tests pasando** — `pytest tests/test_crypto_service.py tests/test_auth_flow.py tests/test_payments_flow.py -q` → `29 passed`

PostgreSQL y Redis levantados por Docker, migraciones aplicadas, API corriendo en `http://127.0.0.1:8000`. El health devuelve `status: ok`.

---

## Paso a paso verificado (comandos exactos)

### 1. Levantar BD y Redis

```bash
docker compose -f docker_helper/docker-compose.postgres.yml up -d
```

### 2. Configurar entorno

Entra a `backend/` y crea tu `.env` tomando como base `docker_helper/backend.postgres.env.example`.

### 3. Instalar dependencias

> **Recomendación:** usar Python 3.11. Varias versiones fijadas en el repo no son cómodas en 3.14+.

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Correr migraciones

```bash
env DATABASE_URL=postgresql+asyncpg://Nivo:Nivo@localhost:5432/Nivo_dev \
    .venv/bin/alembic upgrade head
```

### 5. Levantar la API

```bash
env DATABASE_URL=postgresql+asyncpg://Nivo:Nivo@localhost:5432/Nivo_dev \
    REDIS_URL=redis://localhost:6379/0 \
    JWT_SECRET_KEY=dev_secret_key_minimum_32_chars_here \
    ENVIRONMENT=development \
    .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 6. Correr tests

```bash
.venv/bin/pytest tests/test_crypto_service.py tests/test_auth_flow.py tests/test_payments_flow.py -q
```

### 7. Importar en Postman

Importa estos dos archivos:

- `postman/nivo-sprint-1.postman_collection.json`
- `postman/nivo-local.postman_environment.json`

**Flujo manual en Postman:**

1. `POST /api/v1/auth/request-otp` — solicita el OTP
2. Toma el OTP desde los logs del backend (en `ENVIRONMENT=development` aparece en consola)
3. `POST /api/v1/auth/verify-otp` — autentica y guarda el token
4. `GET /api/v1/users/me` — perfil del usuario
5. `GET /api/v1/users/me/wallet` — saldo de la billetera
6. Pagos P2P → ver nota abajo

> **⚠️ Nota sobre pagos en Postman:** para que el flujo de pagos funcione manualmente necesitas que exista un usuario receptor y que el emisor tenga saldo suficiente en su wallet. En los tests esto se siembra automáticamente, pero en Postman tienes que preparar esos usuarios/datos de antemano (o usar un script seed). El siguiente paso natural es un flujo seed/manual más cómodo para crear usuarios con saldo inicial y dejar la demo de pagos totalmente reproducible.

---

---

## Prerrequisitos

| Herramienta | Versión mínima | Verificar |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Docker Desktop | 24+ | `docker --version` |
| Docker Compose | v2 (incluido en Docker Desktop) | `docker compose version` |
| Git | cualquiera | `git --version` |

---

## Opción A — Solo bases de datos en Docker (API corre local)

Esta es la opción recomendada para desarrollo activo porque tienes hot-reload nativo.

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd Nivo
```

### 2. Levantar PostgreSQL + Redis con Docker

```bash
docker compose -f docker_helper/docker-compose.postgres.yml up -d
```

Espera hasta que los contenedores estén healthy:

```bash
docker compose -f docker_helper/docker-compose.postgres.yml ps
# STATUS debe decir "healthy" para postgres y redis
```

**Servicios disponibles:**
- PostgreSQL: `localhost:5432` (user: `Nivo`, pass: `Nivo`, db: `Nivo_dev`)
- Redis: `localhost:6379`
- pgAdmin: `http://localhost:5050` (admin@nivo.co / nivo_admin)

### 3. Configurar variables de entorno

```bash
cd backend
cp .env.example .env
```

Edita `.env` con tus valores. Para desarrollo básico, los únicos campos obligatorios son:

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://Nivo:Nivo@localhost:5432/Nivo_dev
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=mi_clave_secreta_de_desarrollo_32chars
PQC_ALGORITHM=ML-KEM-768
HYBRID_MODE=true
```

> **Twilio:** Si dejas `TWILIO_ACCOUNT_SID` vacío, el servicio SMS entra en modo mock y el OTP se imprime en los logs del servidor (solo en ENVIRONMENT=development).

### 4. Crear entorno virtual Python e instalar dependencias

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

> **Nota liboqs:** `liboqs-python` requiere que la librería C `liboqs` esté instalada en el sistema. Si la instalación falla, el servicio cae automáticamente en modo de simulación PQC (funcional para desarrollo, no para producción).
>
> Instalación en macOS: `brew install liboqs`
> Instalación en Ubuntu: ver [instrucciones oficiales](https://github.com/open-quantum-safe/liboqs)

### 5. Correr migraciones de base de datos

```bash
cd backend
alembic upgrade head
```

Deberías ver algo como:

```
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, create users table
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, create wallets table
...
```

### 6. Arrancar el servidor

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Si todo está bien verás:

```
✅ Base de datos conectada
✅ Nivo API iniciada — PQC: ML-KEM-768 | Hybrid: True
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7. Verificar que funciona

```bash
curl http://localhost:8000/health
# {"status":"healthy","pqc":true,...}

curl http://localhost:8000/docs
# Abre en el navegador para ver Swagger UI
```

---

## Opción B — Stack completo en Docker (API + DB)

Ideal para demo, QA o cuando no tienes Python instalado.

```bash
# Desde la raíz del proyecto
docker compose -f docker_helper/docker-compose.full.yml up --build
```

La primera vez tarda varios minutos porque compila `liboqs` desde cero.

Los logs mostrarán:
```
nivo-api    | ✅ Base de datos conectada
nivo-api    | ✅ Nivo API iniciada — PQC: ML-KEM-768 | Hybrid: True
nivo-api    | INFO:     Uvicorn running on http://0.0.0.0:8000
```

Para apagar:
```bash
docker compose -f docker_helper/docker-compose.full.yml down
```

Para apagar y eliminar todos los datos:
```bash
docker compose -f docker_helper/docker-compose.full.yml down -v
```

---

## Correr los tests

Con las bases de datos ya levantadas (Opción A):

```bash
cd backend
source venv/bin/activate

# Todos los tests
pytest tests/ -v

# Solo tests de integración Sprint 1
pytest tests/test_integration_sprint1.py -v

# Solo tests de crypto
pytest tests/test_crypto_service.py -v

# Con reporte de cobertura
pytest tests/ -v --cov=app --cov-report=term-missing
```

Los tests usan mocks de DB y Redis — no necesitan conexión real.

---

## Importar colección Postman

1. Abre Postman
2. Click en **Import**
3. Selecciona el archivo: `tests/Nivo_Sprint1.postman_collection.json`
4. La colección aparece con 5 carpetas: Auth, Users, Payments, PQC Crypto, Health

**Configurar antes de ejecutar:**
- Variable `phone_number`: número colombiano válido (ej: `+573001234567`)
- Variable `receiver_phone`: número diferente para recibir pagos (ej: `+573009876543`)
- Variable `otp_code`: el OTP que aparece en los logs del servidor (en modo dev)
- Variable `b2b_api_key`: cualquier string de 32+ caracteres para el crypto API

**Orden de ejecución:**
1. Auth → Request OTP
2. Auth → Verify OTP ← guarda `access_token` automáticamente
3. Users → Get Profile
4. Users → Get Wallet
5. Payments → Initiate Payment ← guarda `tx_id` automáticamente
6. Payments → Confirm Payment
7. Payments → Get Transaction
8. PQC Crypto → Sign Data ← guarda firma automáticamente
9. PQC Crypto → Verify Signature (válida)

---

## Acceder a pgAdmin

Con el docker_helper levantado:

1. Abre `http://localhost:5050`
2. Login: `admin@nivo.co` / `nivo_admin`
3. Agregar servidor:
   - Hostname: `postgres` (dentro de Docker) o `localhost` (desde el host)
   - Port: `5432`
   - Database: `Nivo_dev`
   - Username: `Nivo`
   - Password: `Nivo`

---

## Comandos útiles

```bash
# Ver logs de PostgreSQL
docker compose -f docker_helper/docker-compose.postgres.yml logs postgres -f

# Ver logs de Redis
docker compose -f docker_helper/docker-compose.postgres.yml logs redis -f

# Conectarse a PostgreSQL directamente
docker exec -it nivo-postgres psql -U Nivo -d Nivo_dev

# Inspeccionar Redis
docker exec -it nivo-redis redis-cli

# Resetear la base de datos (borra todo y re-crea)
cd backend
alembic downgrade base
alembic upgrade head

# Crear una nueva migración después de cambiar modelos ORM
cd backend
alembic revision --autogenerate -m "describe_your_change"
alembic upgrade head
```

---

## Troubleshooting

**Error: `ConnectionRefusedError` al arrancar la API**
→ Las bases de datos no están levantadas. Corre `docker compose -f docker_helper/docker-compose.postgres.yml up -d` primero.

**Error: `liboqs not found`**
→ La app sigue funcionando en modo simulación PQC. Para PQC real, instala liboqs C en tu sistema.

**Error: `alembic.util.exc.CommandError: Can't locate revision`**
→ Corre `alembic upgrade head` en lugar de `alembic upgrade <hash>`.

**Error: OTP no llega por SMS**
→ En modo desarrollo, el OTP se imprime en los logs del servidor. Busca la línea:
```
INFO [DEV] OTP para +573001****: 123456
```

**Puerto 5432 ya en uso**
→ Tienes PostgreSQL corriendo nativamente. Para en macOS: `brew services stop postgresql@16`

**Los tests fallan con `ConnectionRefusedError`**
→ Los tests usan mocks y no necesitan DB real. Asegúrate de no tener `DATABASE_URL` apuntando a Postgres en tu entorno de test. Los tests se auto-configuran.
