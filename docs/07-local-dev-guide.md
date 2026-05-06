# Nivo - Guia Local del Repositorio

Esta guia junta en un solo lugar:

- donde esta cada parte del proyecto
- como levantar lo principal en local
- como correr los tests
- que documentos mirar primero segun lo que quieras tocar

Sirve como mapa rapido del repo para desarrollo.

---

## 1. Mapa del repo

Arbol resumido:

```text
Nivo/
├── README.md
├── RUNNING.md
├── ENDPOINTS_OVERVIEW.md
├── POSTMAN_DOCKER_TUTORIAL.md
├── docs/
├── backend/
├── frontend/
├── landing_page/
├── mobile/
├── docker_helper/
├── postman/
├── tests/
├── scripts/
└── tasks/
```

### Que hay en cada carpeta

#### `/backend`

Backend principal en FastAPI.

```text
backend/
├── app/
│   ├── api/v1/        # endpoints HTTP
│   ├── core/          # config, seguridad, base de datos
│   ├── crypto/        # servicio de criptografia post-cuantica
│   ├── models/        # ORM y modelos de dominio
│   ├── services/      # logica de negocio
│   └── utils/         # helpers
├── alembic/           # migraciones
├── tests/             # tests backend
├── requirements.txt
├── pytest.ini
└── Dockerfile
```

Archivos importantes:

- `backend/app/main.py`: arranque de la API
- `backend/app/api/v1/auth.py`: auth OTP/login
- `backend/app/api/v1/payments.py`: flujo P2P
- `backend/app/api/v1/crypto.py`: API B2B de PQC
- `backend/app/services/payment_service.py`: core del flujo de pagos
- `backend/app/core/config.py`: variables de entorno
- `backend/tests/`: suite de tests

#### `/frontend`

Frontend web en Vite + React.

```text
frontend/
├── src/
│   ├── pages/
│   ├── services/
│   ├── components/
│   └── store/
├── package.json
└── vite.config.ts
```

Usalo si quieres tocar la consola web interna / dashboard.

#### `/landing_page/nivo`

Landing publica del proyecto.

```text
landing_page/nivo/
├── src/
├── public/
├── package.json
└── vite.config.ts
```

Usalo si quieres tocar marketing site, narrativa publica o secciones visuales.

#### `/mobile/nivo_mvp`

App mobile MVP en Flutter.

```text
mobile/nivo_mvp/
├── lib/
│   ├── screens/
│   ├── widgets/
│   ├── data/
│   ├── theme/
│   └── navigation/
├── pubspec.yaml
└── test/
```

Usalo si quieres tocar UX mobile, pantallas demo y prototipo de billetera.

#### `/docker_helper`

Composes y docs para levantar servicios por partes.

Archivos mas utiles:

- `docker_helper/docker-compose.postgres.yml`: Postgres + Redis + pgAdmin
- `docker_helper/docker-compose.backend.yml`: backend + DB
- `docker_helper/docker-compose.full.yml`: stack mas completo
- `docker_helper/README.md`: resumen de estos composes

#### `/docs`

Documentacion de producto, negocio y arquitectura.

Recomendados:

- `docs/03-technical-architecture.md`: arquitectura tecnica
- `docs/04-roadmap.md`: roadmap
- `docs/05-go-to-market.md`: GTM
- `docs/07-local-dev-guide.md`: esta guia

#### `/postman`

Colecciones y environments para pruebas manuales.

#### `/tests`

Assets de testing fuera del backend, incluyendo colecciones Postman.

#### `/tasks`

Backlog por sprints, pendientes, analisis y desglose historico del proyecto.

---

## 2. Que leer primero segun lo que quieras hacer

### Quiero entender el proyecto rapido

1. `README.md`
2. `docs/03-technical-architecture.md`
3. `RUNNING.md`

### Quiero tocar pagos P2P

1. `backend/app/api/v1/payments.py`
2. `backend/app/services/payment_service.py`
3. `backend/tests/test_p2p_integration.py`
4. `backend/tests/test_payments_flow.py`

### Quiero tocar el endpoint B2B

1. `backend/app/api/v1/crypto.py`
2. `backend/app/models/orm/b2b_client.py`
3. `backend/tests/test_b2b_auth_integration.py`

### Quiero tocar auth

1. `backend/app/api/v1/auth.py`
2. `backend/app/services/auth_service.py`
3. `backend/app/services/otp_service.py`
4. `backend/tests/test_auth_flow.py`

### Quiero tocar frontend web

1. `frontend/src/App.tsx`
2. `frontend/src/pages/`
3. `frontend/src/services/`

### Quiero tocar landing

1. `landing_page/nivo/src/App.tsx`
2. `landing_page/nivo/src/pages/home.tsx`
3. `landing_page/nivo/src/sections/`

### Quiero tocar mobile

1. `mobile/nivo_mvp/lib/main.dart`
2. `mobile/nivo_mvp/lib/screens/`
3. `mobile/nivo_mvp/lib/widgets/`

---

## 3. Como levantar el backend

La forma mas comoda para desarrollo local es:

- Postgres y Redis por Docker
- API FastAPI corriendo local

### Paso 1: levantar bases de datos

Desde la raiz del repo:

```bash
docker compose --env-file .env.compose.example -f docker_helper/docker-compose.postgres.yml up -d
```

Verifica:

```bash
docker compose --env-file .env.compose.example -f docker_helper/docker-compose.postgres.yml ps
```

Servicios esperados:

- PostgreSQL en `localhost:5432`
- Redis en `localhost:6379`
- pgAdmin en `http://localhost:5050`

### Paso 2: entrar al backend

```bash
cd backend
```

### Paso 3: crear entorno virtual

Recomendado: Python 3.11.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Paso 4: instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 5: crear `.env`

Puedes partir de:

- `backend/.env.example`
- o `docker_helper/backend.postgres.env.example`

Variables minimas para local:

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://Nivo:Nivo@localhost:5432/Nivo_dev
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=dev_secret_key_minimum_32_chars_here
PQC_ALGORITHM=ML-KEM-768
PQC_SIGNATURE_ALGORITHM=ML-DSA-65
HYBRID_MODE=true
```

### Paso 6: correr migraciones

```bash
.venv/bin/alembic upgrade head
```

### Paso 7: levantar la API

```bash
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Paso 8: comprobar

Abre:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`
- `http://127.0.0.1:8000/health`

---

## 4. Como correr tests del backend

Desde `backend/`:

```bash
source .venv/bin/activate
```

### Todos los tests

```bash
.venv/bin/pytest tests/ -q
```

### Auth

```bash
.venv/bin/pytest tests/test_auth_flow.py -q
```

### Pagos P2P

```bash
.venv/bin/pytest tests/test_p2p_integration.py -q
.venv/bin/pytest tests/test_payments_flow.py -q
.venv/bin/pytest tests/test_priority_fixes_flows.py -q
```

### Endpoint B2B / PQC

```bash
.venv/bin/pytest tests/test_b2b_auth_integration.py -q
.venv/bin/pytest tests/test_crypto_service.py -q
```

### Integracion Sprint 1

```bash
.venv/bin/pytest tests/test_integration_sprint1.py -q
```

### Con coverage

```bash
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing
```

Notas:

- muchos tests usan SQLite temporal y FakeRedis
- no todos necesitan Postgres real
- para desarrollo igual conviene tener Postgres/Redis levantados para probar manualmente la API

---

## 5. Como probar la API manualmente

### Swagger / ReDoc

Con la API arriba:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Postman

Archivos utiles:

- `postman/nivo-sprint-1.postman_collection.json`
- `postman/nivo-local.postman_environment.json`
- `tests/Nivo_Sprint1.postman_collection.json`

Flujo base:

1. `POST /api/v1/auth/request-otp`
2. `POST /api/v1/auth/verify-otp`
3. `GET /api/v1/users/me`
4. `GET /api/v1/users/me/wallet`
5. `POST /api/v1/payments/initiate`
6. `POST /api/v1/payments/confirm`

Para `crypto`:

- usa el header `X-Nivo-Key`
- en dev puedes configurar `B2B_API_KEYS` en el `.env`

---

## 6. Como levantar el frontend web

Desde la raiz:

```bash
cd frontend
npm install
npm run dev
```

Normalmente queda en:

- `http://localhost:5173`

Carpetas clave:

- `frontend/src/pages/`
- `frontend/src/services/`
- `frontend/src/components/`

---

## 7. Como levantar la landing

```bash
cd landing_page/nivo
npm install
npm run dev
```

Carpetas clave:

- `landing_page/nivo/src/pages/`
- `landing_page/nivo/src/sections/`
- `landing_page/nivo/src/data/`

---

## 8. Como levantar mobile

Proyecto Flutter:

```bash
cd mobile/nivo_mvp
flutter pub get
flutter run
```

Carpetas clave:

- `mobile/nivo_mvp/lib/screens/`
- `mobile/nivo_mvp/lib/widgets/`
- `mobile/nivo_mvp/lib/data/`
- `mobile/nivo_mvp/lib/theme/`

Tests:

```bash
flutter test
```

---

## 9. Comandos utiles

### Ver logs de Docker

```bash
docker compose -f docker_helper/docker-compose.postgres.yml logs -f
```

### Resetear DB local

```bash
cd backend
.venv/bin/alembic downgrade base
.venv/bin/alembic upgrade head
```

### Abrir psql

```bash
docker exec -it nivo-postgres psql -U Nivo -d Nivo_dev
```

### Abrir redis-cli

```bash
docker exec -it nivo-redis redis-cli
```

---

## 10. Documentos ya existentes

Antes de abrir esta guia o junto con ella, te sirven:

- `README.md`: vision general
- `RUNNING.md`: guia de arranque local
- `docker_helper/README.md`: que compose usar
- `ENDPOINTS_OVERVIEW.md`: resumen de endpoints
- `POSTMAN_DOCKER_TUTORIAL.md`: flujo manual por Postman y Docker

---

## 11. Recomendacion practica

Si vas a trabajar en backend, esta suele ser la ruta mas rapida:

1. `docker compose --env-file .env.compose.example -f docker_helper/docker-compose.postgres.yml up -d`
2. `cd backend`
3. `source .venv/bin/activate`
4. `.venv/bin/alembic upgrade head`
5. `.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
6. `.venv/bin/pytest tests/test_auth_flow.py tests/test_p2p_integration.py tests/test_b2b_auth_integration.py -q`

Si vas a trabajar en UI:

1. backend arriba en `:8000`
2. `cd frontend && npm run dev`
3. o `cd landing_page/nivo && npm run dev`

