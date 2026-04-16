## MES 1 — SPRINT 2 (Semanas 3–4): KYC y Recarga

---

### TASK-006 — Integrar Truora para KYC
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** ALTA

**Descripción:**
Integrar Truora Colombia para verificación de identidad. El flujo debe completarse en < 5 minutos
para el usuario. Los documentos se almacenan cifrados.

**Archivos a crear:**
- CREAR `backend/app/services/kyc_service.py`
- CREAR `backend/app/api/v1/kyc.py` — Endpoints KYC
- MODIFICAR `backend/app/main.py` — Incluir router KYC

**Endpoints requeridos:**
```
POST /api/v1/kyc/initiate       — Iniciar proceso KYC, retorna URL de Truora
POST /api/v1/kyc/webhook        — Webhook de Truora para resultado (NO requiere JWT)
GET  /api/v1/kyc/status         — Estado actual del KYC del usuario autenticado
```

**Flujo KYC:**
```
1. Usuario llama POST /api/v1/kyc/initiate con JWT
2. Backend llama API Truora: crear proceso de verificación
3. Truora retorna URL de verificación (front se redirige ahí)
4. Usuario completa la verificación en Truora (toma 2–4 minutos)
5. Truora llama webhook POST /api/v1/kyc/webhook con resultado
6. Backend actualiza users.kyc_status = 'verified' o 'rejected'
7. Se envía push notification al usuario con resultado

# Webhook payload de Truora (validar HMAC):
{
    "process_id": "...",
    "status": "approved" | "declined",
    "document_number": "...",
    "full_name": "..."
}
```

**Seguridad del webhook:**
- Verificar firma HMAC-SHA256 del payload usando `settings.KYC_API_KEY` como secret
- Retornar 200 incluso si falla la verificación (no revelar si fue inválido)
- Loggear intentos fallidos con IP del remitente

**Criterios de éxito:**
- [ ] El flujo completo KYC se puede simular con datos de test de Truora
- [ ] Webhook inválido (sin firma correcta) retorna 200 pero no actualiza el usuario
- [ ] `kyc_status` cambia a 'verified' tras webhook exitoso
- [ ] Los límites de transacción cambian automáticamente al verificar KYC

**Dependencias:** TASK-001, TASK-002

---

### TASK-007 — Integrar Pasarela PSE (Wompi) para Recargas
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
Integrar Wompi (o PayU como fallback) para recargas desde cuenta bancaria colombiana vía PSE.
Este es el único flujo de entrada de dinero real al MVP.

**Archivos a crear:**
- CREAR `backend/app/services/payment_gateway_service.py`
- CREAR `backend/app/api/v1/topup.py` — Endpoints de recarga
- MODIFICAR `backend/app/main.py` — Incluir router topup

**Endpoints requeridos:**
```
POST /api/v1/topup/initiate     — Iniciar recarga PSE, retorna URL de pago
POST /api/v1/topup/webhook      — Webhook de Wompi para confirmación
GET  /api/v1/topup/history      — Historial de recargas del usuario
```

**Flujo de recarga:**
```
1. Usuario solicita recarga de $100,000 COP
2. Backend crea transacción en Wompi (estado: PENDING)
3. Backend guarda referencia interna en BD con status='pending'
4. Backend retorna URL de pago de Wompi al frontend
5. Usuario completa PSE en Wompi
6. Wompi llama webhook con resultado
7. Si APPROVED: acreditar wallet del usuario + registrar en BD
8. Si DECLINED: marcar como fallida, notificar usuario

# Webhook Wompi:
{
    "event": "transaction.updated",
    "data": {
        "transaction": {
            "id": "wompi_tx_id",
            "reference": "Nivo_internal_ref",
            "status": "APPROVED" | "DECLINED" | "VOIDED",
            "amount_in_cents": 10000000
        }
    },
    "signature": { "checksum": "...", "properties": [...] }
}
```

**Validar firma Wompi:**
```python
# Concatenar: propiedades + timestamp + events_secret
# SHA-256 del resultado == checksum
```

**Criterios de éxito:**
- [ ] Con credenciales sandbox Wompi: flujo PSE completo funciona en staging
- [ ] Webhook con firma inválida: retorna 200 pero NO acredita la billetera
- [ ] Doble procesamiento del mismo webhook: idempotente (no se acredita dos veces)
- [ ] La billetera se acredita SOLO cuando status='APPROVED' en el webhook
- [ ] Test de concurrencia: dos webhooks del mismo pago simultáneos → crédito exacto una vez

**Dependencias:** TASK-001, TASK-003

---

### TASK-008 — Sistema de Retiros a Cuenta Bancaria (ACH)
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** MEDIA

**Descripción:**
Permitir al usuario retirar dinero a su cuenta bancaria colombiana. En MVP usar Wompi
disbursements o ACH directo según disponibilidad.

**Archivos a crear:**
- CREAR `backend/app/api/v1/withdrawal.py`
- CREAR `backend/app/models/orm/bank_account.py` — Cuentas bancarias registradas
- MODIFICAR `backend/app/main.py` — Incluir router withdrawal

**Tabla bank_accounts:**
```sql
id: UUID PK
user_id: UUID FK -> users.id
bank_code: VARCHAR(10)      -- código banco colombiano (ej: "001" = Bancolombia)
account_type: ENUM('savings','checking')
account_number_encrypted: BYTEA  -- cifrado AES-256-GCM
account_holder_name: VARCHAR(255)
is_verified: BOOLEAN DEFAULT FALSE
created_at: TIMESTAMPTZ DEFAULT NOW()
```

**Reglas de negocio:**
- Número de cuenta NUNCA en plano en BD — siempre cifrado con AES-256-GCM
- Verificación: pequeño depósito de $500 COP y el usuario confirma el monto
- Límite de retiro: mismo que límite diario del plan
- Comisión de retiro: $0 en plan Plus y Pro, $2,000 COP en Free
- Tiempo de procesamiento: 1–2 días hábiles (informar al usuario)

**Criterios de éxito:**
- [ ] El número de cuenta nunca es recuperable en plano desde la API
- [ ] La verificación de cuenta con microdepósito funciona en staging
- [ ] Si el usuario no tiene cuenta verificada, el retiro es rechazado con mensaje claro

**Dependencias:** TASK-003, TASK-007

---

