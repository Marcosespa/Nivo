# Docker Helper — Guía General Nivo

## Comando principal (levanta TODO)

```bash
# Desde la raíz del proyecto:
docker compose up --build

# En background:
docker compose up --build -d

# Ver logs en tiempo real:
docker compose logs -f

# Bajar todo:
docker compose down

# Reset completo (borra volúmenes y datos):
docker compose down -v
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
docker-compose.yml   ← Orquesta TODOS los servicios en uno
```

---

## Cuándo usar cada compose

| Situación                                      | Comando                                                               |
|------------------------------------------------|-----------------------------------------------------------------------|
| Desarrollo completo (todo junto)               | `docker compose up --build` (desde raíz)                             |
| Solo quiero las DBs, el backend corre local    | `docker compose -f docker_helper/docker-compose.databases.yml up -d` |
| Probar la API con Postman (sin frontend)        | `docker compose -f docker_helper/docker-compose.backend.yml up --build` |
| Solo buildear y probar el frontend             | `docker compose -f docker_helper/docker-compose.frontend.yml up --build` |
| Levantar workers auxiliares                    | `docker compose -f docker_helper/docker-compose.microservices.yml up -d` |

---

## Flujo de arranque del stack principal

```
postgres ──► (healthy)
redis    ──► (healthy)
              │
              ▼
           backend ──► alembic migrate ──► uvicorn start ──► (healthy)
              │
              ▼
           frontend ──► nginx start ──► (healthy)
```

Los `depends_on` con `condition: service_healthy` garantizan ese orden.

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
