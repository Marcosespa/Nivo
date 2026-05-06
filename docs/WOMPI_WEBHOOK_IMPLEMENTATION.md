# Webhook Wompi: Implementacion Relevante

Fecha: 2026-04-24
Estado: implementado

## Objetivo

Completar el flujo de top-up por webhook de Wompi con:
- validacion de firma
- idempotencia
- acreditacion de saldo
- manejo de estados

## Cambios de Codigo

### 1) Event log para idempotencia

Archivo: backend/app/models/orm/webhook_event_log.py

Se crea una tabla de eventos de webhook con constraint unico por:
- provider
- provider_event_id

Estados de procesamiento:
- RECEIVED
- PROCESSING
- PROCESSED
- FAILED
- IGNORED

### 2) Procesamiento de webhook

Archivo: backend/app/services/payment_gateway_service.py

Se refactoriza process_webhook para este flujo:
1. Extraer datos de evento (id, status, timestamp).
2. Validar firma SHA-256 con WOMPI_EVENTS_SECRET.
3. Aplicar idempotencia con webhook_event_log.
4. Buscar transaccion local por provider_reference.
5. Resolver por estado:
   - APPROVED: acreditar saldo y marcar SETTLED/COMPLETED.
   - DECLINED o VOIDED: marcar FAILED.
   - Sin transaccion local: marcar IGNORED.
6. Marcar evento como PROCESSED.

Metodos clave agregados:
- _process_topup_approved
- _process_topup_declined

### 3) Migracion

Archivo: backend/alembic/versions/0002_webhook_event_log.py

Se agrega tabla webhook_event_logs con indices de consulta.

### 4) Tests

Archivo: backend/tests/test_topup_webhook_wompi.py

Cobertura funcional incluida para:
- acreditacion en APPROVED
- idempotencia ante duplicados
- rechazo por firma invalida
- manejo DECLINED
- evento sin transaccion local
- concurrencia

## Ejecucion

1. Aplicar migraciones:

```bash
cd backend
alembic upgrade head
```

2. Ejecutar tests de webhook:

```bash
pytest tests/test_topup_webhook_wompi.py -v
```

## Verificaciones Esperadas

- Un webhook APPROVED acredita balance una sola vez.
- Un webhook duplicado no vuelve a acreditar.
- Un webhook con firma invalida no acredita.
- Una transaccion DECLINED/VOIDED queda FAILED.
- Los eventos quedan auditados en webhook_event_logs.

## Notas Operativas

- En produccion, WOMPI_EVENTS_SECRET debe estar configurado.
- El flujo esta preparado para reintentos de webhook sin duplicar efectos.
- La logica de idempotencia puede reutilizarse para otros proveedores.
