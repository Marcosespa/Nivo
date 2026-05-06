# Conectar tabla `b2b_clients` al verificador de API keys

**Cerrada:** 2026-05-06
**Origen:** TODO documentado en `backend/CLAUDE.md` ("`verify_api_key` currently only validates key length"). Bloqueante de la línea de negocio B2B (PQC-as-a-Service).

## Qué quedó listo

- **`crypto.py:verify_b2b_api_key`** ya estaba conectado a la tabla. Validado: hash SHA-256 → lookup en `b2b_clients` → fallback a `settings.B2B_API_KEYS` para tests/dev.
- **Endpoint admin nuevo `POST /api/v1/admin/b2b-clients`**:
  - Genera `secrets.token_urlsafe(48)` como key.
  - Persiste **sólo el SHA-256** (la columna se llama `api_key_hash`).
  - Retorna la key en claro **una sola vez** en la response — el llamador la guarda en su gestor de secretos.
- **`GET /api/v1/admin/b2b-clients`** — lista clientes con prefijo del hash para confirmar identidad sin exponer el hash completo. Filtro `only_active` (default true).
- **`POST /api/v1/admin/b2b-clients/{id}/deactivate`** — marca `is_active=False`. Las keys del cliente dejan de validar contra la BD.
- **Tests `tests/test_admin_b2b_clients.py`** (3 escenarios):
  1. Emisión: la key emitida valida contra `/api/v1/crypto/algorithms`. En BD sólo queda el hash.
  2. Listado: `only_active=false` lista activos+inactivos; `only_active=true` filtra.
  3. Desactivación: la key emitida deja de validar después del `POST /deactivate`.

## Lo que NO se hizo (deuda explícita)

- **Auth del endpoint admin** — `/admin/*` se monta solo si `ENVIRONMENT in {development, staging}` (en `main.py`). En producción no existe la ruta. Para producción habrá que ponerlo detrás de un panel admin con MFA o de un script con credenciales rotadas. Misma postura que el resto de `/admin/*` actuales.
- **Billing por operación** — la tabla `b2b_clients` no tiene contadores de uso. Se añadirá cuando el equipo de negocio cierre pricing (ver `ANALISIS_DE_NEGOCIO_RESPUESTAS.md`).
- **Rotación de keys** — no hay endpoint `rotate-key`. Si una key se compromete, se desactiva el cliente y se emite uno nuevo.
