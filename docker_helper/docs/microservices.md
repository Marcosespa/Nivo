# Docker — Microservicios y auxiliares

**Compose:** `docker_helper/docker-compose.microservices.yml`

## Objetivo

Este compose no reemplaza al backend principal. Agrupa servicios auxiliares
de desarrollo y placeholders de workers que apareceran en sprints futuros.

## Servicio activo hoy

### Mailhog

- UI: `http://localhost:8025`
- SMTP: `localhost:1025`

Mailhog captura correos salientes en desarrollo para inspeccionarlos sin
entregar mensajes reales.

## Servicios planeados

- `pqc-gateway`
- `kyc-worker`
- `sms-worker`
- `notifications`

Hoy se dejan documentados y comentados para que el stack tenga una ruta clara
de crecimiento sin fingir que esos servicios ya existen.

## Uso

```bash
docker compose -f docker_helper/docker-compose.microservices.yml up -d
docker compose -f docker_helper/docker-compose.microservices.yml down
```
