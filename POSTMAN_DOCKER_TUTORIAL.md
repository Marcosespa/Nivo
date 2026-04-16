# Nivo - Tutorial Docker + Postman

Esta guia deja el backend en modo de pruebas manuales, con logs visibles y una coleccion Postman lista para validar sprint 0 y sprint 1.

## Que archivo importar en Postman

- Coleccion: `postman/nivo-sprint-1.postman_collection.json`
- Environment: `postman/nivo-local.postman_environment.json`

## Archivos `.env` que te deje

- Local con Python en tu maquina: `backend/.env.example`
- Docker completo: `backend/.env.docker.example`

Nota importante: el runtime de la app solo acepta `development`, `staging` y `production`. Para pruebas manuales deje todo en `development`, que es el modo correcto para ver logs, OTPs en consola y usar `/api/v1/dev/seed`.

Nota de puertos: el stack Docker completo usa `http://localhost:8001` para evitar choques con procesos locales que ya esten usando `8000`. Si corres la API fuera de Docker, puedes seguir usando `8000`.

## Conexiones de base de datos

### Postgres desde tu maquina

- Host: `localhost`
- Port: `5432`
- Database: `Nivo_dev`
- User: `Nivo`
- Password: `Nivo`
- URL async SQLAlchemy:

```text
postgresql+asyncpg://Nivo:Nivo@localhost:5432/Nivo_dev
```

- URL Postgres clasica:

```text
postgresql://Nivo:Nivo@localhost:5432/Nivo_dev
```

### Redis desde tu maquina

- Host: `localhost`
- Port: `6379`
- URL:

```text
redis://localhost:6379/0
```

### pgAdmin

- URL: `http://localhost:5050`
- Email: `admin@nivo.co`
- Password: `nivo_admin`

## Opcion A - Levantar todo con Docker

Esta es la mas facil para probar con Postman sin instalar nada extra fuera de Docker.

### 1. Levantar el stack

```bash
docker compose -f docker_helper/docker-compose.full.yml down
docker compose -f docker_helper/docker-compose.full.yml up --build
```

Eso levanta:

- API en `http://localhost:8001`
- PostgreSQL en `localhost:5432`
- Redis en `localhost:6379`
- pgAdmin en `http://localhost:5050`

### 2. Ver logs de la API

En esa misma consola vas a ver:

- access logs de Uvicorn
- logs de OTP en development
- logs de notificaciones mock
- errores de requests para depurar Postman

Si lo levantaste detached:

```bash
docker compose -f docker_helper/docker-compose.full.yml logs -f api
```

### 3. Verificar health

```bash
curl http://localhost:8001/health
curl http://localhost:8001/health/pqc
```

### 4. Apagar todo

```bash
docker compose -f docker_helper/docker-compose.full.yml down
```

Para borrar datos tambien:

```bash
docker compose -f docker_helper/docker-compose.full.yml down -v
```

## Opcion B - Docker para DB y API local

Si quieres correr la API localmente pero dejar Postgres y Redis en Docker:

### 1. Levantar Postgres, Redis y pgAdmin

```bash
docker compose -f docker_helper/docker-compose.postgres.yml up -d
```

### 2. Preparar `.env`

```bash
cd backend
cp .env.example .env
```

### 3. Instalar dependencias y correr migraciones

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/alembic upgrade head
```

### 4. Levantar la API con logs utiles

```bash
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

## Como usar Postman

## Flujo recomendado para probar sprint 0 y sprint 1

### Camino rapido: usar seed de desarrollo

Este camino no depende de leer OTP primero y deja datos reproducibles para pagos.

1. Ejecuta `POST /api/v1/dev/seed`
2. El request guarda automaticamente:
   - `access_token`
   - `refresh_token`
   - `receiver_phone`
   - tokens del sender y receiver seed
3. Ejecuta:
   - `GET /api/v1/users/me`
   - `GET /api/v1/users/me/wallet`
   - `POST /api/v1/payments/initiate`
4. Mira en logs el OTP de pago
5. Copia el OTP en la variable `otp_code`
6. Ejecuta `POST /api/v1/payments/confirm`
7. Ejecuta:
   - `GET /api/v1/payments/history`
   - `GET /api/v1/payments/{tx_id}`

### Camino completo de auth por OTP

1. Ejecuta `POST /api/v1/auth/request-otp`
2. Mira el OTP en logs
3. Pon el codigo en `otp_code`
4. Ejecuta `POST /api/v1/auth/verify-otp`
5. Sigue con:
   - `POST /api/v1/auth/refresh`
   - `POST /api/v1/auth/logout`
   - `GET /api/v1/users/me`
   - `GET /api/v1/users/me/wallet`

## Orden sugerido de carpetas en Postman

### 00. Health y Root

Valida que todo haya subido bien.

### 01. Dev Seed Helpers

Prepara sender y receiver con saldo para pruebas manuales.

### 02. Sprint 0 - Crypto y Hardening

Valida:

- `GET /api/v1/crypto/algorithms`
- `POST /api/v1/crypto/sign`
- `POST /api/v1/crypto/verify`
- rechazo de `signing_key_hex`

### 03. Auth OTP

Valida request OTP, verify, refresh y logout.

### 04. Users

Valida perfil y wallet real.

### 05. Payments

Valida initiate, confirm, history y detalle.

## Que cubre la coleccion respecto a sprint 0 y sprint 1

### Sprint 0

- health y startup base
- crypto algorithms desde config
- firma y verificacion
- rechazo de payload inseguro con `signing_key_hex`
- endpoints finales alineados con los fixes ya marcados

### Sprint 1

- auth completo con OTP y JWT
- refresh token rotado
- logout con invalidacion
- perfil de usuario
- wallet visual
- pagos atomicos
- historial y detalle de transacciones
- Twilio en modo mock por logs cuando las credenciales estan vacias

## Como leer los OTP desde logs

En development, si Twilio esta vacio, el backend imprime algo como:

```text
[DEV OTP] +5730012**** -> 123456
```

Ese valor lo copias en la variable `otp_code` del environment de Postman.

## Variables importantes del environment de Postman

- `base_url`
- `otp_code`
- `access_token`
- `refresh_token`
- `receiver_phone`
- `payment_tx_id`
- `seed_sender_phone`
- `seed_receiver_phone`
- `seed_balance_cop`

## Tip de prueba reproducible

Antes de volver a probar pagos desde cero:

1. Ejecuta `DELETE /api/v1/dev/seed`
2. Ejecuta otra vez `POST /api/v1/dev/seed`

Asi reinicias sender, receiver y saldo semilla.

## Si algo falla

- Revisa `docker compose -f docker_helper/docker-compose.full.yml logs -f api`
- Confirma que `http://localhost:8001/health/pqc` responda `ok`
- Confirma que Postman este usando el environment `Nivo Local Test`
- Si cambiaste puertos, actualiza `base_url`
