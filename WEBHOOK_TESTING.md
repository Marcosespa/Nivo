## Probar webhooks fallidos — Local

### Requisitos

- Backend corriendo: `uvicorn app.main:app --reload` en `backend/`
- Wompi secret en `.env` (opcional, algunas pruebas fallarán sin él)
- Redis en `localhost:6379` (para contador de alertas)

### Ejecutar

**Opción 1: Sin credenciales (desarrollo local)**
```powershell
cd C:\Users\Sebastian\Desktop\Nivo
.\test_webhooks.ps1
```

**Opción 2: Con credenciales de Wompi**
```powershell
$env:WOMPI_INTEGRITY_SECRET = "tu-wompi-secret-de-.env"
.\test_webhooks.ps1
```

**Opción 3: Saltar test de Truora (no tienes llave KYC)**
```powershell
.\test_webhooks.ps1 -SkipTruora
```

---

### Qué prueban los tests

| Test | Qué | Esperas |
|------|-----|---------|
| 1 | Firma inválida 3x | Alerta Slack después del 3er request |
| 2 | Wompi DECLINED | `transactions.status = 'failed'` en BD |
| 3 | Truora mock KYC rejected | `kyc_funnel_events` con `result = failed` |
| 4 | Idempotencia | Solo 1 webhook guardado (no 2) |

---

### Verificar resultados

**En BD (PostgreSQL local)**
```sql
-- Ver última transacción rechazada
SELECT id, status, created_at FROM transactions 
WHERE status = 'failed' ORDER BY created_at DESC LIMIT 1;

-- Ver evento KYC rechazado
SELECT step, result, failure_reason, created_at FROM kyc_funnel_events
WHERE result = 'failed' ORDER BY created_at DESC LIMIT 1;

-- Ver logs de webhook
SELECT * FROM webhook_event_logs 
ORDER BY created_at DESC LIMIT 5;
```

**En Slack**
- Canal: `#alertas-criticas`
- Buscar: `WEBHOOK_INVALID_SIGNATURE` (después del 3er request del Test 1)

**En Redis**
```powershell
# Si tienes redis-cli:
redis-cli -u redis://localhost:6379/0 KEYS "nivo:alert:*"
redis-cli -u redis://localhost:6379/0 GET "nivo:alert:fail:webhook_firma_invalida"
```

---

### Cuando tengas llaves de Truora

1. Actualiza `.env` con `KYC_API_KEY=tu-llave`
2. Quita `--SkipTruora` del script
3. El Test 3 validará la firma real
