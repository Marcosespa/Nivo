# Docker — Bases de Datos (PostgreSQL + Redis + pgAdmin)

**Compose:** `docker_helper/docker-compose.databases.yml`

---

## Servicios incluidos

### PostgreSQL 16

Base de datos relacional principal. Almacena:
- Usuarios y autenticación
- Wallets y saldos
- Transacciones
- Llaves PQC
- KYC, OTPs, cuentas bancarias

```yaml
imagen:      postgres:16-alpine
usuario:     Nivo
contraseña:  Nivo
base:        Nivo_dev
puerto:      5432
volumen:     nivo_postgres_data → /var/lib/postgresql/data
```

**Por qué alpine:** la imagen alpine es ~80 MB vs ~380 MB de la imagen completa.
No necesitamos las herramientas extra para un contenedor de base de datos.

**Init scripts:** cualquier archivo `.sql` en `docker_helper/init-scripts/`
se ejecuta automáticamente la primera vez que se crea el volumen.

---

### Redis 7

Cache en memoria y almacén de sesiones. Usa para:
- TTL de OTPs (5 minutos)
- Sesiones JWT revocadas (blacklist)
- Rate limiting por usuario
- Caché de respuestas frecuentes

```yaml
imagen:      redis:7-alpine
puerto:      6379
volumen:     nivo_redis_data → /data
persistencia: save 60 1  (escribe al disco si hay ≥1 cambio en 60s)
```

**Comando `save 60 1`:** garantiza que los datos sobreviven un reinicio del
contenedor. En producción usa `appendonly yes` para durabilidad total.

---

### pgAdmin 4

Interfaz web para explorar y administrar PostgreSQL visualmente.

```yaml
imagen:      dpage/pgadmin4:latest
email:       admin@nivo.co
contraseña:  nivo_admin
puerto:      5050
```

**Cómo conectarse desde pgAdmin:**
1. Abrir http://localhost:5050
2. Clic en "Add New Server"
3. **Name:** Nivo Dev
4. **Host:** postgres (nombre del servicio Docker)
5. **Port:** 5432
6. **Username:** Nivo
7. **Password:** Nivo

---

## Comandos

```bash
# Levantar solo las DBs (background)
docker compose -f docker_helper/docker-compose.databases.yml up -d

# Ver logs de PostgreSQL
docker compose -f docker_helper/docker-compose.databases.yml logs -f postgres

# Conectarse a PostgreSQL directamente
docker compose -f docker_helper/docker-compose.databases.yml exec postgres \
  psql -U Nivo -d Nivo_dev

# Conectarse a Redis
docker compose -f docker_helper/docker-compose.databases.yml exec redis redis-cli

# Ver claves en Redis
docker compose exec redis redis-cli KEYS "*"

# Hacer backup de PostgreSQL
docker compose exec postgres pg_dump -U Nivo Nivo_dev > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker compose exec -T postgres psql -U Nivo -d Nivo_dev < backup.sql

# Bajar y borrar datos (reset total)
docker compose -f docker_helper/docker-compose.databases.yml down -v
```

---

## Volúmenes y persistencia

Los datos sobreviven entre reinicios del contenedor gracias a los volúmenes Docker:

| Volumen              | Contenedor  | Datos que guarda                   |
|----------------------|-------------|------------------------------------|
| `nivo_postgres_data` | postgres    | Tablas, índices, migraciones       |
| `nivo_redis_data`    | redis       | Sesiones, caché, OTPs              |
| `nivo_pgadmin_data`  | pgadmin     | Conexiones guardadas en pgAdmin    |

Para ver dónde están físicamente:
```bash
docker volume inspect nivo_postgres_data
```

---

## Healthchecks

| Servicio   | Comando de verificación                          | Intervalo |
|------------|--------------------------------------------------|-----------|
| PostgreSQL | `pg_isready -U Nivo -d Nivo_dev`                 | 5s        |
| Redis      | `redis-cli ping`                                 | 5s        |

El backend esperará hasta que ambos healthchecks respondan OK antes de iniciar.

---

## Puertos

| Puerto host | Servicio   | Descripción              |
|-------------|------------|--------------------------|
| 5432        | PostgreSQL | Conexión directa a la DB |
| 6379        | Redis      | Conexión directa a Redis |
| 5050        | pgAdmin    | Panel web                |
