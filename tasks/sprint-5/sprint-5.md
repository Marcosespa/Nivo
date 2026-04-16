## MES 3 — SPRINT 5 (Semanas 13–16): Comercios y QR

---

### TASK-016 — Backend: Sistema de Comercios y Terminal QR
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
Implementar el módulo de comercios: registro, QR dinámico firmado con ML-DSA-65, y cobros.

**Archivos a crear:**
- CREAR `backend/app/api/v1/merchants.py`
- CREAR `backend/app/services/merchant_service.py`
- CREAR `backend/app/services/qr_service.py`

**Endpoints:**
```
POST /api/v1/merchants/register          — Registrar nuevo comercio
GET  /api/v1/merchants/me                — Info del comercio del usuario
POST /api/v1/merchants/qr/static         — Generar QR estático (firmado ML-DSA)
POST /api/v1/merchants/qr/dynamic        — Generar QR dinámico con monto (firmado ML-DSA)
POST /api/v1/merchants/charge            — Procesar cobro desde QR
GET  /api/v1/merchants/transactions      — Historial de cobros del comercio
GET  /api/v1/merchants/dashboard/summary — Resumen del día (total cobros, #transacciones)
```

**Especificaciones del QR:**
```python
# Estructura del payload del QR (JSON en el QR code):
{
    "version": "1.0",
    "merchant_id": "uuid",
    "merchant_name": "Restaurante El Cielo",
    "amount_cop": 50000_00,  # null en QR estático, monto fijo en dinámico
    "qr_id": "uuid",         # ID único del QR para evitar replay attacks
    "expires_at": "iso_timestamp",  # QR dinámico expira en 10 minutos
    "ml_dsa_signature": "hex",      # Firma del merchant sobre el payload anterior
    "algorithm": "ML-DSA-65"
}

# Al procesar un cobro desde QR:
1. Parsear el JSON del QR
2. Verificar la firma ML-DSA-65 del merchant
3. Verificar que qr_id no ha sido usado antes (Redis lookup)
4. Verificar que expires_at no ha vencido (solo QR dinámico)
5. Ejecutar payment_service.execute_payment()
6. Marcar qr_id como usado en Redis con TTL de 1 hora
```

**Criterios de éxito:**
- [ ] El QR generado se puede escanear con cualquier lector de QR y mostrar el JSON
- [ ] Un QR dinámico procesado dos veces retorna error en el segundo intento
- [ ] La firma ML-DSA-65 en el QR es verificable independientemente del backend
- [ ] El dashboard muestra el total cobrado del día en tiempo real

**Dependencias:** TASK-003, TASK-004

---

### TASK-017 — Frontend: App "Nivo Negocios" (modo comercio)
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
Modo comercio dentro de la app: generar QR de cobro, ver pagos recibidos en tiempo real,
y resumen del día.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/merchant/MerchantHomeScreen.tsx`
- CREAR `frontend/mobile/src/screens/merchant/GenerateQRScreen.tsx`
- CREAR `frontend/mobile/src/screens/merchant/MerchantTransactionsScreen.tsx`
- CREAR `frontend/mobile/src/components/merchant/QRDisplay.tsx`
- CREAR `frontend/mobile/src/components/merchant/PaymentReceivedAlert.tsx`

**Especificaciones:**
```
MerchantHomeScreen:
  - Resumen del día: Total cobrado | # Transacciones | Ticket promedio
  - Botón grande: "Generar código de cobro" (principal acción)
  - Lista de últimos cobros con tiempo transcurrido ("hace 5 min")
  - Indicador de conexión (⚛️ Quantum-Safe activo)

GenerateQRScreen:
  - Switch: QR Fijo (no pone monto) | QR con monto
  - Si QR con monto: input de monto
  - Botón "Generar QR"
  - QR Display: QR code grande, centered, fondo blanco (para escanear)
  - Bajo el QR: "Firmado con ML-DSA-65 ⚛️"
  - Timer si es QR dinámico: "Expira en 09:45"
  - Botón "Nuevo QR" para generar otro

PaymentReceivedAlert:
  - Modal/Toast que aparece cuando se recibe un pago
  - "💚 ¡Recibiste $X de [nombre]!"
  - Animación de entrada desde la parte superior
  - Auto-dismiss en 5 segundos
```

**Criterios de éxito:**
- [ ] El QR se genera y se puede escanear con la cámara del celular
- [ ] Al pagar con otro dispositivo, el PaymentReceivedAlert aparece en < 3 segundos
- [ ] El resumen del día se actualiza en tiempo real (polling cada 30s o WebSocket)

**Dependencias:** TASK-009, TASK-016

---

