# Docker Helper — Nivo

Archivos Docker Compose para desarrollo local.

## Archivos disponibles

| Archivo | Propósito |
|---|---|
| `docker-compose.postgres.yml` | Solo bases de datos: PostgreSQL 16 + Redis 7 + pgAdmin |
| `docker-compose.full.yml` | Stack completo: API + PostgreSQL + Redis |

---

## Solo bases de datos (recomendado para dev activo)

```bash
# Levantar
docker compose -f docker_helper/docker-compose.postgres.yml up -d

# Ver estado
docker compose -f docker_helper/docker-compose.postgres.yml ps

# Ver logs
docker compose -f docker_helper/docker-compose.postgres.yml logs -f

# Apagar (conserva datos)
docker compose -f docker_helper/docker-compose.postgres.yml down

# Apagar y eliminar datos
docker compose -f docker_helper/docker-compose.postgres.yml down -v
```

**Servicios:**
- PostgreSQL: `localhost:5432` (Nivo/Nivo/Nivo_dev)
- Redis: `localhost:6379`
- pgAdmin: `http://localhost:5050` (admin@nivo.co / nivo_admin)

---

## Stack completo con la API

```bash
# Construir y levantar
docker compose -f docker_helper/docker-compose.full.yml up --build

# Solo levantar (si ya construiste antes)
docker compose -f docker_helper/docker-compose.full.yml up

# Apagar
docker compose -f docker_helper/docker-compose.full.yml down
```

**Servicios:**
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

Ver `RUNNING.md` en la raíz del proyecto para la guía completa paso a paso.
