# Troubleshooting — Nivo

Guía rápida de los fallos más comunes al levantar el stack en local. Si tu problema no está aquí, revisa primero [docs/07-local-dev-guide.md](07-local-dev-guide.md) y luego abre un issue.

---

## Backend

### `ModuleNotFoundError: No module named 'fastapi'` (o cualquier dep)

La `.venv` no está activada o no instaló dependencias.

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

Si la `.venv` no existe:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### `RuntimeError: PQC module failed health check — refusing to start`

`liboqs` no está disponible. Opciones:

- **Instalar liboqs nativo** (macOS):
  ```bash
  brew install liboqs
  pip install --force-reinstall liboqs-python
  ```
- **Bypass en dev** (sólo para iterar lógica que no toca firma): poner `PQC_ALGORITHM=mock` en `backend/.env`. **No funciona en producción** — el health check exige liboqs real cuando `ENVIRONMENT=production`.

### `ValueError: JWT_SECRET_KEY contiene un placeholder`

El validador rechaza `CHANGE_ME`, `replace_with`, `dev_secret`, etc. cuando `ENVIRONMENT=staging|production`. Genera un secreto real:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Y pégalo en `JWT_SECRET_KEY` del `.env` correspondiente. En `development` el validador sólo exige longitud ≥32.

### `sqlalchemy.exc.OperationalError: connection refused` a Postgres

La DB no está levantada o los puertos no coinciden.

```bash
# Verifica estado
docker compose --env-file .env.compose.example -f docker_helper/docker-compose.postgres.yml ps

# Si no está corriendo
docker compose --env-file .env.compose.example -f docker_helper/docker-compose.postgres.yml up -d

# Logs
docker compose -f docker_helper/docker-compose.postgres.yml logs -f postgres
```

`DATABASE_URL` por defecto apunta a `localhost:5432`. Si cambiaste el puerto en compose, actualiza también el `.env`.

### `redis.exceptions.ConnectionError: Error connecting to Redis`

Mismo patrón:

```bash
docker compose -f docker_helper/docker-compose.postgres.yml ps redis
```

`REDIS_URL=redis://localhost:6379/0` debe coincidir con el puerto expuesto.

---

## Migraciones (Alembic)

### `Multiple head revisions are present`

Pasó cuando dos ramas crearon una migración con el mismo `down_revision`.

```bash
.venv/bin/alembic heads        # lista los heads
.venv/bin/alembic merge heads -m "merge alembic heads"
.venv/bin/alembic upgrade head
```

### `Target database is not up to date`

Aplica las migraciones pendientes:

```bash
.venv/bin/alembic upgrade head
```

Si quieres resetear todo en local:

```bash
.venv/bin/alembic downgrade base
.venv/bin/alembic upgrade head
```

### Tests fallan con `no such table` en SQLite

La fixture de tests usa SQLite efímero — si lo invocaste sin que el `metadata.create_all` corriera (por ejemplo, importando un modelo nuevo después del fixture), reinicia con:

```bash
.venv/bin/pytest --cache-clear -q
```

---

## Wompi / Top-ups

### Webhooks llegan pero no se acreditan al usuario

Síntoma: log dice `Webhook: transacción no encontrada para reference=…`.

Causa típica: `WOMPI_MOCK_MODE=true` se usó para generar un `wompi_tx_id` sintético (`mock_xxxxx`), pero ahora apuntas a un sandbox real cuyo webhook no encuentra la fila local.

Solución: o bien (1) probar end-to-end desde `initiate_topup` real (no mezclar mock + real), o (2) borrar transacciones de pruebas:

```sql
DELETE FROM transactions WHERE provider_reference LIKE 'mock_%';
```

### `InvalidWebhookSignatureError: Firma inválida`

- Verifica que `WOMPI_EVENTS_SECRET` en tu `.env` sea el mismo que muestra el panel de Wompi.
- En desarrollo puedes activar `WOMPI_MOCK_MODE=true` para saltarte la firma — pero **no funciona en producción** (el flag se ignora cuando `ENVIRONMENT=production`).
- Si Wompi reenvía un evento, el HMAC se construye sobre `data` ordenado lexicográficamente; un proxy que reordene JSON romperá la firma.

### El webhook responde 200 pero no procesa

Wompi siempre recibe `{"status": "ok"}` — esto es intencional para no filtrar estado interno. Para diagnosticar, mira los logs del backend:

```bash
docker compose logs -f backend  # si corres todo en compose
# o el output del uvicorn si corres el backend nativo
```

Busca `Webhook processed successfully` o `Error processing Wompi webhook`.

### Race condition en webhook (`Webhook race condition for ...`)

Es esperado y manejado: si Wompi envía dos veces el mismo evento simultáneamente, una de las inserciones falla por la UNIQUE de `webhook_event_logs(provider, provider_event_id)` y se hace rollback + relectura. Si el log se repite muchas veces, revisa que Wompi no esté reintentando en bucle por algún 5xx no relacionado.

---

## Frontend / Landing

### `npm ci` falla con `EACCES`

```bash
rm -rf node_modules package-lock.json
npm install
```

### Landing no encuentra los videos en `public/assets/`

Los archivos `.mp4` están versionados (Git LFS no se usa todavía). Si después de `git pull` faltan, verifica que el `.gitattributes` no los excluya. Si pesan demasiado para el repo, considera mover a Cloudflare R2.

---

## Repo

### `.pyc` o `__pycache__` aparecen en `git status`

`.gitignore` ya los excluye. Si ves alguno tracked, fue commiteado antes de la limpieza:

```bash
git rm --cached -r '**/__pycache__'
git commit -m "chore: untrack bytecode"
```

### Conflictos de merge en `.pyc`

Nunca resolver — son binarios. Eliminar del índice y dejar que se regeneren:

```bash
git rm -f $(git diff --name-only --diff-filter=U | grep '\.pyc$')
```

### `git status` muestra muchos archivos modificados sin sentido tras un pull

Probablemente es line-ending (CRLF/LF). Revisa `.gitattributes`. En macOS:

```bash
git config core.autocrlf input
```

---

## CI

### CI rojo en `Alembic migration check` pero local está bien

El job corre `alembic upgrade head` desde una BD vacía — si una migración depende de datos pre-existentes (semilla manual), va a fallar. Las migraciones deben ser idempotentes y self-contained.

### `pytest` pasa local pero falla en CI

Las diferencias más comunes:

- Variables de entorno: CI usa `backend/.env.example` o defaults; local puede tener overrides en `.env`.
- Zona horaria: tests que comparan `datetime.now()` sin `timezone.utc` se rompen.
- Dependencias C (liboqs): CI puede no tenerlas — el código tiene fallback a modo simulación, pero si tu test pide firma real, fallará.

---

## Última opción: reset de local

Si nada funciona y quieres empezar limpio (sin perder código):

```bash
# Para la DB
docker compose -f docker_helper/docker-compose.postgres.yml down -v

# Reinstala deps
cd backend
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Re-levanta
docker compose --env-file .env.compose.example -f docker_helper/docker-compose.postgres.yml up -d
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1
```
