# Docker Helper — Guia General Nivo

## Comando principal

```bash
# Stack completo desde docker_helper
docker compose -f docker_helper/docker-compose.full.yml up --build

# Stack completo desde la raíz
docker compose up --build
```

---

## Mapa de puertos

| Servicio    | URL de acceso                    | Descripción                        |
|-------------|----------------------------------|------------------------------------|
| Frontend    | http://localhost:3000            | App React (Nivo)                   |
| Backend     | http://localhost:8001            | FastAPI REST                       |
| Swagger UI  | http://localhost:8001/docs       | Documentación interactiva de la API|
| ReDoc       | http://localhost:8001/redoc      | Documentación alternativa          |
| PostgreSQL  | localhost:5432                   | Base de datos relacional           |
| Redis       | localhost:6379                   | Cache y sesiones                   |
| pgAdmin     | http://localhost:5050            | Panel web de PostgreSQL            |
| Mailhog     | http://localhost:8025            | UI de correo en desarrollo (si levantas microservices) |

---

## Credenciales de desarrollo

| Servicio   | Usuario          | Contraseña  | Base de datos |
|------------|------------------|-------------|---------------|
| PostgreSQL | Nivo             | Nivo        | Nivo_dev      |
| pgAdmin    | admin@nivo.co    | nivo_admin  | —             |

---

## Estructura de composes

```
docker_helper/
├── docker-compose.databases.yml      # Solo DB (Postgres + Redis + pgAdmin)
├── docker-compose.backend.yml        # API + DB (sin frontend)
├── docker-compose.frontend.yml       # Solo frontend
├── docker-compose.microservices.yml  # Servicios auxiliares / workers
└── docs/
    ├── overview.md          ← este archivo
    ├── frontend.md          ← guía del frontend container
    ├── backend.md           ← guía del backend container
    ├── databases.md         ← guía de bases de datos
    └── microservices.md     ← guía de microservicios
```

Y en la raíz del proyecto:

```
docker-compose.yml   ← Alias del stack completo
```

---

## Cuándo usar cada compose

| Situación | Comando |
|---|---|
| Desarrollo completo | `docker compose up --build` |
| Stack completo desde helper | `docker compose -f docker_helper/docker-compose.full.yml up --build` |
| Solo DBs | `docker compose -f docker_helper/docker-compose.databases.yml up -d` |
| Postman + API | `docker compose -f docker_helper/docker-compose.backend.yml up --build` |
| Solo frontend | `docker compose -f docker_helper/docker-compose.frontend.yml up --build` |
| Microservicios | `docker compose -f docker_helper/docker-compose.microservices.yml up -d` |

---

## Flujo de arranque del stack principal

```
postgres -> healthy
redis -> healthy
backend -> alembic -> uvicorn -> healthy
frontend -> nginx -> healthy
```

---

## Tips útiles

```bash
# Ver estado de todos los contenedores
docker compose ps

# Entrar al contenedor del backend
docker compose exec backend bash

# Entrar al contenedor de postgres
docker compose exec postgres psql -U Nivo -d Nivo_dev

# Ver logs solo del backend
docker compose logs -f backend

# Rebuild solo un servicio sin bajar los demás
docker compose up --build frontend

# Limpiar imágenes sin usar
docker image prune -f
```
