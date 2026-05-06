# Nivo — Production/Staging Readiness Report

Fecha: 2026-05-06

## Resumen Ejecutivo

El sistema ya estaba funcionalmente verificado. Esta pasada se enfocó en estabilidad, seguridad operativa, documentación y despliegue. El resultado deja el proyecto listo para un despliegue de staging controlado, con algunos requisitos explícitos antes de producción: secretos reales en secret manager, configuración de dominios/hosts, liboqs real y revisión de observabilidad.

## Mejoras Realizadas

### Estabilidad y deuda técnica

- Se reemplazaron `print()` de arranque, base de datos y health check PQC por logging estándar (`logging.getLogger`) para integrar mejor con Docker, Cloud Run y agregadores de logs.
- El import de instrumentación FastAPI/OpenTelemetry ya es tolerante a entornos incompletos; si falta la dependencia opcional, el backend arranca sin romper tests o desarrollo local.
- El flujo de top-up/Wompi quedó validado con idempotencia por `WebhookEventLog`, lock local por `wompi_tx_id`, compatibilidad con `provider_reference` histórico y mocks de desarrollo.
- La respuesta de errores de Wompi ya no vuelca `response.text` ni payloads completos al log; registra estado y metadatos no sensibles.

### Optimización y escalabilidad

- Se preservan consultas con `SELECT ... FOR UPDATE` para operaciones de wallet/top-up que requieren consistencia.
- Se evita doble acreditación por webhooks repetidos o carreras simples mediante event log único y lock por transacción Wompi.
- El CI ahora cubre backend y landing, y se ejecuta contra `main` y `develop`.
- Docker backend corre como usuario no-root y mantiene healthcheck HTTP.

### Documentación

- `README.md` fue reescrito con estructura actual del monorepo, instalación, variables, ejecución local, Docker, pruebas, API y troubleshooting.
- Se documentaron endpoints principales expuestos por FastAPI y dónde consultar Swagger/OpenAPI.
- Se agregó esta guía de readiness con checklist y roadmap v2.
- Se validó también la consola web (`frontend/`) con build de TypeScript/Vite.

### Seguridad y DevOps

- Se removieron valores tipo secreto de `backend/.env.example` y `backend/.env.docker.example`.
- Se agregó `.env.compose.example` para parametrizar credenciales del stack Docker.
- `docker-compose.yml` ahora exige variables para PostgreSQL y pgAdmin en vez de fijar credenciales en el YAML.
- Se redujo el riesgo de logs sensibles en el servicio de Wompi.

## Estado de Documentación Técnica

| Área | Estado | Notas |
| --- | --- | --- |
| Instalación local | Actualizada | README cubre backend, landing, frontend y Docker. |
| Variables de entorno | Actualizada | Ejemplos sin secretos reales. Producción debe usar secret manager. |
| API/OpenAPI | Disponible | `/docs`, `/redoc`, `/openapi.json` en development/staging. |
| Troubleshooting | Actualizado | README cubre fallos vistos en tests: OTel, liboqs, Wompi, dev OTP, CORS. |
| Backups/DR | Existente | Ver `docs/08-postgresql-backup-dr.md`. |
| Gestión de llaves | Existente | Ver `docs/ADR-003-hsm-key-management.md`; aún pendiente implementación HSM/KMS real. |

## Auditoría de Seguridad

### Revisado

- Secretos en ejemplos `.env`.
- Credenciales fijas en compose principal.
- Logs de Wompi y arranque.
- Exposure de `dev_otp`.
- Webhooks Wompi con HMAC y modo mock.
- Montaje de docs solo fuera de producción.

### Riesgos Residuales

- Algunos documentos históricos en `tasks/` y colecciones de prueba conservan snippets de ejemplo. No deben usarse como configuración de producción.
- Los archivos `__pycache__` están trackeados en el repo. No rompen runtime, pero agregan ruido y deberían limpiarse en una tarea separada con `.gitignore` y migración del índice.
- La validación B2B permite fallback a `settings.B2B_API_KEYS` por compatibilidad dev/staging. Producción debería validar contra tabla `b2b_clients` y rotación/auditoría.
- Las llaves PQC de usuario aún tienen camino de desarrollo/simulación. Producción debe conectar HSM/KMS según ADR-003.

## Checklist de Despliegue

### Listo para staging

- [x] Backend compila.
- [x] Suite backend pasa completa.
- [x] Landing pública compila.
- [x] Frontend consola compila.
- [x] Docker backend usa usuario no-root.
- [x] Healthchecks configurados.
- [x] README actualizado.
- [x] Swagger/OpenAPI disponible en entornos no productivos.
- [x] Ejemplos `.env` saneados.
- [x] Compose principal parametrizado con variables.
- [x] CI cubre backend y landing en `main`/`develop`.

### Requerido antes de producción

- [ ] Provisionar secretos en Secret Manager/Vault, no `.env`.
- [ ] Configurar `ENVIRONMENT=production`, `DEBUG=false`, `WOMPI_MOCK_MODE=false`.
- [ ] Definir `ALLOWED_ORIGINS` y `ALLOWED_HOSTS` con dominios reales.
- [ ] Validar liboqs real en la imagen productiva y bloquear modo simulado.
- [ ] Activar OTLP/Sentry con redacción de PII.
- [ ] Ejecutar migraciones Alembic contra staging snapshot.
- [ ] Configurar backups/PITR de PostgreSQL y probar restore.
- [ ] Retirar o ignorar `__pycache__` trackeado en una limpieza controlada.
- [ ] Añadir escaneo de secrets/dependencias en CI.

## Roadmap v2.0

1. HSM/KMS para llaves PQC y rotación.
   Migrar firmas y manejo de llaves privadas a un proveedor gestionado u HSM. Objetivo: ninguna llave privada sensible en memoria persistente de aplicación.

2. Validación B2B productiva con gestión de clientes.
   Completar autenticación de `X-Nivo-Key` contra `b2b_clients`, scopes, rate limits por cliente, rotación y auditoría.

3. Observabilidad financiera y antifraude en tiempo real.
   Agregar métricas de negocio, alertas por anomalía transaccional, trazas por rail de pago y dashboard de incidentes operativos.

## Comandos de Verificación Ejecutados

```bash
cd backend
./.venv/bin/python -m compileall app tests
./.venv/bin/python -m pytest
```

```bash
cd landing_page/nivo
npm run build
```

```bash
cd frontend
npm run build
```

Resultado esperado de la última corrida backend: `122 passed`.
