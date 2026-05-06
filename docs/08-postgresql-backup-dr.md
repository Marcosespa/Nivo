# Backup y DR de PostgreSQL — Nivo

**Estado:** Propuesto para servidor propio  
**Owner:** Backend/Infra  
**Alcance:** PostgreSQL transaccional de Nivo (`users`, `wallets`, `transactions`, `pqc_keys`, `b2b_clients`, KYC y ordenes de partner).

---

## 1. Contexto

Nivo operara PostgreSQL en servidor propio, no en Cloud SQL/GCP. Eso cambia la estrategia: la responsabilidad de backups, cifrado, replicacion, monitoreo, pruebas de restauracion y custodia fisica/logica queda en Nivo.

El objetivo no es solo "tener dumps". El objetivo es poder restaurar una base consistente, con perdida acotada, y demostrarlo con ensayos.

---

## 2. Objetivos de Recuperacion

| Escenario | RPO objetivo | RTO objetivo | Respuesta |
|---|---:|---:|---|
| Error humano menor | 15 min | 1 h | PITR a instancia temporal y restauracion selectiva |
| Bug de escritura/corrupcion logica | 15 min | 2 h | PITR antes del evento, validacion, cambio controlado |
| Falla de disco servidor primario | 15 min | 2-4 h | Promover replica o restaurar en servidor standby |
| Perdida total del servidor | 1 h | 4-8 h | Restaurar backup externo en hardware/VM alterna |
| Compromiso de credenciales | 24 h | 8-24 h | Restaurar backup limpio, rotar secretos, auditoria forense |

**Regla:** ningun restore se hace sobre produccion sin validarlo primero en instancia temporal, salvo desastre total y aprobacion explicita.

---

## 3. Arquitectura Recomendada

### Servidores

- `pg-primary`: servidor principal PostgreSQL.
- `pg-standby`: replica fisica por streaming replication en otra maquina/red.
- `backup-host`: maquina separada que ejecuta backups, verifica integridad y empuja copias cifradas.
- `restore-drill`: maquina temporal para ensayos de restauracion.

### Almacenamiento

- Discos locales con RAID1/RAID10 o volumen redundante.
- Filesystem con snapshots si esta disponible (ZFS/Btrfs/LVM), pero snapshots no reemplazan backups PostgreSQL.
- Backups externos cifrados en al menos dos destinos:
  - NAS/offsite propio.
  - almacenamiento S3-compatible o servidor remoto via `rclone`/`restic`.

---

## 4. Politica de Backups

### Produccion

- Backups fisicos con `pgBackRest` o `Barman`.
- WAL archiving continuo para PITR.
- Backup completo semanal.
- Backup diferencial diario.
- Backup incremental cada 6 horas si el volumen lo justifica.
- Retencion local: 7 dias.
- Retencion offsite diaria: 30 dias.
- Retencion mensual offsite: 12 meses.
- Cifrado de backups con llave separada del servidor de base de datos.

### Staging

- Backup diario con retencion de 7 dias.
- Datos anonimizados si provienen de produccion.

### Desarrollo

- Sin datos reales.
- Dumps manuales solo anonimizados.

---

## 5. Implementacion Base con pgBackRest

### Configuracion conceptual

`pg-primary` debe archivar WAL:

```conf
archive_mode = on
archive_command = 'pgbackrest --stanza=nivo archive-push %p'
wal_level = replica
max_wal_senders = 10
hot_standby = on
```

`pgBackRest` debe tener repositorio cifrado en `backup-host` y copia offsite.

### Comandos operativos

Crear stanza:

```bash
pgbackrest --stanza=nivo stanza-create
pgbackrest --stanza=nivo check
```

Backup completo semanal:

```bash
pgbackrest --stanza=nivo --type=full backup
```

Backup diferencial diario:

```bash
pgbackrest --stanza=nivo --type=diff backup
```

Restauracion PITR en maquina temporal:

```bash
systemctl stop postgresql
pgbackrest --stanza=nivo --delta \
  --type=time \
  --target="2026-05-06 10:30:00+00" \
  restore
systemctl start postgresql
```

---

## 6. Validaciones Post-Restore

Antes de promover una restauracion:

- `alembic current` coincide con el estado esperado.
- Conteo de filas por tabla critica.
- `transactions.completed` tienen `provider_reference`.
- Saldos visuales cuadran contra transacciones confirmadas.
- Firmas ML-DSA verifican contra public key/fingerprint.
- Clientes B2B inactivos siguen rechazados.
- Smoke tests: `/health`, login OTP, wallet, historial P2P, `/api/v1/crypto/algorithms` con API key valida.

---

## 7. Seguridad

- Usuario `postgres` sin login remoto directo.
- Acceso SSH solo por llaves, MFA si hay bastion/VPN, sin password.
- Backups cifrados antes de salir del servidor.
- Llave de cifrado guardada fuera de `pg-primary`; idealmente en HSM/Vault/offline split knowledge.
- Dumps de produccion prohibidos en laptops personales.
- Backups de KYC/documentos separados de la base transaccional si contienen binarios sensibles.
- Prueba trimestral de restore y prueba semestral de perdida total del servidor.

---

## 8. Monitoreo y Alertas

Alertas minimas:

- Falla de backup.
- WAL archiving detenido.
- Replica con lag > 60 segundos.
- Disco > 75% y > 90%.
- Tiempo de backup fuera de ventana.
- Error de `pgbackrest check`.
- No se ha ejecutado restore drill en 90 dias.

---

## 9. Runbook de Desastre

1. Declarar incidente y congelar escrituras si la API sigue viva.
2. Identificar ultimo punto sano: timestamp, deploy, migracion o evento.
3. Restaurar en `restore-drill` o promover `pg-standby`.
4. Ejecutar validaciones post-restore.
5. Cambiar `DATABASE_URL` de la API al servidor recuperado.
6. Reiniciar servicios.
7. Ejecutar smoke tests.
8. Registrar RPO real, RTO real, causa, aprobador y acciones correctivas.

---

## 10. Backlog Asociado

- Crear scripts `scripts/backup_check.sh` y `scripts/dr_smoke_check.py`.
- Definir nombres finales de servidores, usuarios y rutas.
- Automatizar reportes de restore drill.
- Documentar procedimiento de rotacion de llaves de cifrado de backups.
- Integrar alertas con Sentry/Slack/email.
