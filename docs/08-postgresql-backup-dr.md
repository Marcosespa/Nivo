# Backup y DR de PostgreSQL — Nivo

**Estado:** Aprobado para Sprint 3  
**Owner:** Backend/Infra  
**Alcance:** PostgreSQL transaccional de Nivo (`users`, `wallets`, `transactions`, `pqc_keys`, `b2b_clients`, KYC y ordenes de partner).

---

## 1. Objetivos de Recuperacion

| Escenario | RPO | RTO | Respuesta |
|---|---:|---:|---|
| Error humano menor | 15 min | 1 h | Point-in-time recovery (PITR) a una instancia temporal y restauracion selectiva |
| Corrupcion o bug de escritura | 15 min | 2 h | PITR antes del evento, verificacion, promote/swap |
| Caida regional primaria | 15 min | 4 h | Replica/restore en region secundaria y cambio de trafico |
| Compromiso de credenciales | 24 h | 8 h | Restaurar backup limpio, rotar secretos, auditoria forense |

**Regla:** para datos financieros, nunca se restaura sobre produccion sin ensayo en instancia temporal y validacion de conciliacion.

---

## 2. Politica de Backups

### Produccion

- Cloud SQL PostgreSQL con backups automaticos diarios.
- PITR habilitado con WAL retention minimo de 7 dias.
- Retencion de backups diarios: 30 dias.
- Snapshot semanal exportado a bucket GCS versionado: 12 semanas.
- Snapshot mensual exportado a bucket GCS con retention lock: 12 meses.
- Cifrado en reposo con KMS administrado por Nivo cuando este disponible.

### Staging

- Backup diario con retencion de 7 dias.
- PITR opcional si staging procesa datos anonimizados de produccion.
- Restauraciones de prueba mensuales usando copia anonima.

### Desarrollo local

- Sin datos reales.
- Dumps manuales solo para reproducir bugs, anonimizados antes de compartirse.

---

## 3. Procedimiento Operativo

### Backup manual antes de cambios riesgosos

```bash
gcloud sql backups create \
  --instance=nivo-postgres-prod \
  --description="pre-deploy-YYYY-MM-DD"
```

Usar antes de migraciones Alembic destructivas, cambios de schema financiero o backfills masivos.

### Restauracion PITR en instancia temporal

```bash
gcloud sql instances clone nivo-postgres-prod nivo-postgres-restore-YYYYMMDD \
  --point-in-time="YYYY-MM-DDTHH:MM:SSZ"
```

Validar:

- Migraciones Alembic en estado esperado.
- Conteo de filas por tabla critica.
- Checks de saldos vs transacciones confirmadas.
- Muestra de recibos ML-DSA verificables.
- Ausencia del bug/incidente que disparo la restauracion.

### Promocion / cambio de trafico

1. Congelar escrituras en la API o activar modo mantenimiento.
2. Ejecutar conciliacion final con proveedor regulado.
3. Actualizar `DATABASE_URL` via Secret Manager.
4. Reiniciar Cloud Run.
5. Ejecutar smoke tests: `/health`, login OTP, consulta wallet, historial P2P.
6. Registrar incidente, hora de corte, RPO real y aprobador.

---

## 4. Pruebas de DR

- Ensayo trimestral obligatorio de restauracion PITR.
- Ensayo semestral de caida regional simulada.
- Cada ensayo debe producir un reporte con:
  - tiempo real de restauracion,
  - perdida maxima estimada,
  - checks ejecutados,
  - gaps encontrados,
  - acciones correctivas y owner.

**Criterio de aprobacion:** restaurar una copia usable, pasar smoke tests y verificar conciliacion de saldos sin intervencion manual no documentada.

---

## 5. Controles de Seguridad

- Acceso a backups limitado a rol `infra-admin` con MFA.
- Buckets de exportacion con versioning, retention policy e IAM minimo.
- Prohibido descargar dumps de produccion a maquinas personales.
- Dumps para soporte o analisis deben anonimizar telefono, email, documento, metadatos KYC y referencias externas sensibles.
- Secretos de BD rotados despues de incidente severo o exposicion sospechada.

---

## 6. Tablas Criticas y Validaciones

| Tabla | Validacion minima post-restore |
|---|---|
| `users` | usuarios activos, telefonos unicos, KYC coherente |
| `wallets` | una wallet por usuario, saldos no negativos salvo regla explicita |
| `transactions` | montos positivos, `provider_reference` presente si completed, firmas verificables |
| `pqc_keys` | solo una llave activa por usuario, fingerprints unicos |
| `b2b_clients` | API keys hasheadas, clientes inactivos siguen bloqueados |
| `partner_orders` | ordenes con disclosure, partner y firma |

---

## 7. Backlog Asociado

- Automatizar verificacion de restauracion con script `scripts/dr_smoke_check.py`.
- Crear runbook especifico para Cloud SQL production cuando existan nombres finales de proyecto/instancia.
- Integrar alertas de backup fallido en Sentry/Slack.
- Definir dashboard de RPO/RTO real por ensayo.
