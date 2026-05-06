# Docker — Backend (FastAPI + PQC)

**Archivo:** `backend/Dockerfile`
**Compose:** `docker_helper/docker-compose.backend.yml`

---

## Qué hace este contenedor

Corre la API REST de Nivo construida con **FastAPI + Python 3.11**.
Lo especial de este Dockerfile es que compila **liboqs** desde código fuente
(la librería C de criptografía post-cuántica del NIST) durante el build.

```
Stage 1 (builder): python:3.11-slim
  └─ Instala dependencias del sistema (cmake, gcc, libssl-dev...)
  └─ Clona y compila liboqs (ML-KEM-768, ML-DSA-65)
  └─ pip install -r requirements.txt

Stage 2 (runtime): python:3.11-slim
  └─ Copia liboqs compilado
  └─ Copia dependencias Python del builder
  └─ Copia código fuente
  └─ Corre como usuario no-root "nivo"
  └─ Expone puerto 8000
```

**Por qué multi-etapa:** el builder necesita ~500 MB de herramientas de compilación
(cmake, gcc, make). La imagen final solo carga lo compilado → ~200 MB.

---

## Secuencia de arranque

Al iniciar, el contenedor ejecuta:

```bash
alembic upgrade head    # Corre todas las migraciones pendientes
uvicorn app.main:app    # Inicia el servidor ASGI
```

Las migraciones (`alembic`) deben correr **antes** de que la API acepte requests,
por eso están en el `command` y no en el `entrypoint`.

---

## Variables de entorno clave

| Variable              | Valor por defecto (dev)                              | Descripción                        |
|-----------------------|------------------------------------------------------|------------------------------------|
| `DATABASE_URL`        | `postgresql+asyncpg://nivo_user:***@postgres:5432/nivo_dev` | Conexión a PostgreSQL        |
| `REDIS_URL`           | `redis://redis:6379/0`                               | Conexión a Redis                   |
| `JWT_SECRET_KEY`      | *(cambiar en producción)*                            | Firma de tokens JWT                |
| `PQC_ALGORITHM`       | `ML-KEM-768`                                         | Algoritmo PQC NIST Level 3         |
| `PQC_SIGNATURE_ALGORITHM` | `ML-DSA-65`                                    | Firma post-cuántica                |
| `HYBRID_MODE`         | `true`                                               | PQC + X25519 simultáneo            |
| `ENVIRONMENT`         | `development`                                        | `development` o `production`       |
| `ALLOWED_ORIGINS`     | `["http://localhost:3000",...]`                      | CORS whitelist                     |

El archivo completo de variables está en `backend/.env.docker.example`.

---

## Endpoints cubiertos en este stack

| Metodo | Ruta |
|---|---|
| GET | `/health` |
| GET | `/health/pqc` |
| GET | `/health/ready` |
| POST | `/api/v1/dev/seed` |
| POST | `/api/v1/auth/request-otp` |
| POST | `/api/v1/auth/verify-otp` |
| POST | `/api/v1/auth/refresh` |
| POST | `/api/v1/auth/logout` |
| GET | `/api/v1/users/me` |
| GET | `/api/v1/users/me/wallet` |
| POST | `/api/v1/payments/initiate` |
| POST | `/api/v1/payments/confirm` |
| GET | `/api/v1/payments/history` |
| GET | `/api/v1/payments/{tx_id}` |
| POST | `/api/v1/kyc/initiate` |
| GET | `/api/v1/kyc/status` |
| POST | `/api/v1/topup/initiate` |
| GET | `/api/v1/topup/history` |
| POST | `/api/v1/withdrawal/accounts` |
| GET | `/api/v1/withdrawal/accounts` |
| POST | `/api/v1/withdrawal/accounts/{account_id}/verify` |
| POST | `/api/v1/withdrawal/initiate` |
| GET | `/api/v1/withdrawal/history` |
| GET | `/api/v1/crypto/algorithms` |
| POST | `/api/v1/crypto/sign` |
| POST | `/api/v1/crypto/verify` |

Documentación interactiva: **http://localhost:8001/docs**

---

## Comandos

```bash
# Levantar backend + DBs
docker compose -f docker_helper/docker-compose.backend.yml up --build

# Ver logs del API
docker compose -f docker_helper/docker-compose.backend.yml logs -f backend

# Correr migraciones manualmente
docker compose exec backend alembic upgrade head

# Revertir última migración
docker compose exec backend alembic downgrade -1

# Entrar al contenedor
docker compose exec backend sh

# Correr tests dentro del contenedor
docker compose exec backend pytest tests/ -v
```

---

## Healthcheck

`http://localhost:8001/health`

El backend necesita ~20-30 segundos en su primer arranque mientras compila
dependencias nativas y corre migraciones. Los `depends_on` del frontend esperan
a que el healthcheck responda antes de arrancar nginx.

---

## Puertos

| Puerto host | Puerto contenedor | Descripcion |
|---|---|---|
| 8001 | 8000 | FastAPI REST + Swagger UI |
