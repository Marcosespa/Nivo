# Docker Helper — Nivo

Colección de composes para levantar el proyecto por partes o completo.

## Archivos principales

| Archivo | Qué levanta |
|---|---|
| `docker-compose.full.yml` | Frontend + Backend + PostgreSQL + Redis + pgAdmin |
| `docker-compose.frontend.yml` | Solo frontend React servido con Nginx |
| `docker-compose.backend.yml` | Backend FastAPI + PostgreSQL + Redis + pgAdmin |
| `docker-compose.databases.yml` | PostgreSQL + Redis + pgAdmin |
| `docker-compose.microservices.yml` | Servicios auxiliares y futuros workers |
| `docker-compose.postgres.yml` | Alias legacy del stack de bases de datos |

## Uso rapido

```bash
# Todo el stack
docker compose -f docker_helper/docker-compose.full.yml up --build

# Solo frontend
docker compose -f docker_helper/docker-compose.frontend.yml up --build

# Solo backend con DBs
docker compose -f docker_helper/docker-compose.backend.yml up --build

# Solo bases de datos
docker compose -f docker_helper/docker-compose.databases.yml up -d

# Microservicios auxiliares
docker compose -f docker_helper/docker-compose.microservices.yml up -d
```

## Documentacion por stack

- [Resumen general](./docs/overview.md)
- [Frontend](./docs/frontend.md)
- [Backend](./docs/backend.md)
- [Bases de datos](./docs/databases.md)
- [Microservicios](./docs/microservices.md)

Ver tambien [POSTMAN_DOCKER_TUTORIAL.md](/Users/marcosespana/Desktop/Nivo/POSTMAN_DOCKER_TUTORIAL.md) y [RUNNING.md](/Users/marcosespana/Desktop/Nivo/RUNNING.md).
