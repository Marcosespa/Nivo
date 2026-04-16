## MES 5–6 — SPRINT 8–12: Escala, Modelo ML y Preparación Serie

---

### TASK-024 — Modelo de Fraude con ML (Isolation Forest)
**Estado:** [ ] PENDING
**Agente sugerido:** ml
**Estimado:** 12–16 horas
**Prioridad:** MEDIA

**Descripción:**
Implementar el primer modelo de ML para detección de fraude usando
comportamiento histórico del usuario (embeddings de secuencias de transacciones).

**Archivos a crear:**
- CREAR `backend/app/ml/fraud_model.py` — Modelo Isolation Forest
- CREAR `backend/app/ml/feature_engineering.py` — Extracción de features
- CREAR `backend/app/ml/model_training.py` — Script de entrenamiento
- CREAR `backend/ml_models/` — Directorio para artefactos de modelos

**Features a extraer por usuario (últimos 30 días):**
```python
features = {
    "avg_tx_amount": float,          # Monto promedio de transacciones
    "std_tx_amount": float,          # Desviación estándar de montos
    "tx_per_day_avg": float,         # Transacciones promedio por día
    "unique_recipients_count": int,  # Número de receptores únicos
    "night_tx_ratio": float,         # % de transacciones 10pm–6am
    "weekend_tx_ratio": float,       # % de transacciones en fin de semana
    "max_single_tx": float,          # Monto máximo en período
    "days_since_first_tx": int,      # Antigüedad del usuario
    "failed_tx_ratio": float,        # % de transacciones fallidas
}

# Para la transacción actual:
current_features = {
    "amount_vs_avg_ratio": float,    # Monto actual / promedio
    "time_since_last_tx_hours": float,
    "is_new_recipient": bool,
    "is_night_transaction": bool,
}
```

**Pipeline:**
```
1. Extraer features → feature_engineering.py
2. Normalizar con StandardScaler
3. Isolation Forest con contamination=0.05 (5% fraude esperado)
4. Score de anomalía → risk_score entre 0.0 y 1.0
5. Si risk_score > 0.7 → REVIEW
6. Si risk_score > 0.9 → BLOCK
```

**Criterios de éxito:**
- [ ] El modelo corre en < 20ms por transacción (tiempo de inferencia)
- [ ] El modelo se puede entrenar/reentrenar con `python model_training.py`
- [ ] El artefacto del modelo se carga al arrancar el servicio (pickle o joblib)
- [ ] La integración con `fraud_detection_service.py` reemplaza la regla 2 (monto inusual)

**Dependencias:** TASK-023, datos de transacciones reales o sintéticos para entrenar

---

### TASK-025 — Multi-Moneda: COP, USD, EUR
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** MEDIA

**Descripción:**
Implementar soporte para billeteras en USD y EUR (solo plan Pro).
Integrar API de tipo de cambio para conversiones.

**Archivos a crear:**
- CREAR `backend/app/services/fx_service.py` — Tipo de cambio en tiempo real
- MODIFICAR `backend/app/models/orm/wallet.py` — Soporte multi-wallet
- CREAR `backend/app/api/v1/fx.py` — Endpoints de cambio de divisa

**Especificaciones:**
```python
# fx_service.py — Usar API de Frankfurter (gratuita, sin API key)
# https://api.frankfurter.app/latest?from=USD&to=COP

# Spread: 1.5% sobre el tipo de cambio de mercado
# Ejemplo: mercado 4,200 COP/USD → Nivo: 4,137 COP/USD (venta)

# Actualizar tasas cada 1 hora y cachear en Redis
# Si la API falla, usar la última tasa conocida + badge de alerta
```

**Endpoints:**
```
GET  /api/v1/fx/rates               — Tasas actuales COP/USD/EUR
POST /api/v1/fx/convert             — Solicitar conversión
GET  /api/v1/fx/wallets             — Todas las billeteras del usuario por moneda
```

**Criterios de éxito:**
- [ ] Un usuario Pro puede tener saldo en COP, USD y EUR simultáneamente
- [ ] La conversión incluye el spread del 1.5% claramente mostrado al usuario
- [ ] Las tasas se actualizan sin downtime (refresh en Redis background)

**Dependencias:** TASK-003, TASK-001

---

### TASK-026 — Dashboard Web para Comercios (Next.js)
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 12–16 horas
**Prioridad:** MEDIA

**Descripción:**
Dashboard web para comercios: ver transacciones, generar reportes,
y configurar el perfil del negocio. Usar Next.js 15 + shadcn/ui.

**Archivos a crear:**
- CREAR `frontend/dashboard/` — Nuevo proyecto Next.js
- CREAR `frontend/dashboard/src/app/page.tsx` — Login
- CREAR `frontend/dashboard/src/app/dashboard/page.tsx` — Panel principal
- CREAR `frontend/dashboard/src/app/transactions/page.tsx` — Transacciones
- CREAR `frontend/dashboard/src/app/qr/page.tsx` — Gestión de QR codes
- CREAR `frontend/dashboard/src/app/settings/page.tsx` — Configuración

**Tech stack:**
```json
{
  "next": "15.x",
  "typescript": "^5.3.0",
  "tailwindcss": "^3.4.0",
  "@shadcn/ui": "latest",
  "recharts": "^2.x",
  "@tanstack/react-query": "^5.x",
  "axios": "^1.x"
}
```

**Dashboard principal debe mostrar:**
```
┌─────────────────────────────────────────────────────┐
│ Hoy: $X cobrado | Y transacciones | $Z ticket prom  │
├──────────────────────────┬──────────────────────────┤
│ Gráfica de cobros/hora   │ Últimas transacciones     │
│ (recharts BarChart)      │ (tabla con QR id, monto,  │
│                          │  hora, estado)            │
├──────────────────────────┴──────────────────────────┤
│ QR Activos: [lista de QR estáticos]                 │
│ Botón: "Generar nuevo QR de cobro"                  │
└─────────────────────────────────────────────────────┘
```

**Criterios de éxito:**
- [ ] `cd frontend/dashboard && npm run dev` arranca sin errores
- [ ] La gráfica de cobros se actualiza con datos reales del backend
- [ ] El export de transacciones genera un CSV descargable
- [ ] El dashboard es responsive (funciona en tablet)

**Dependencias:** TASK-016

---

### TASK-027 — Auditoría de Seguridad PQC Interna
**Estado:** [ ] PENDING
**Agente sugerido:** security
**Estimado:** 8–10 horas
**Prioridad:** ALTA

**Descripción:**
Revisión interna exhaustiva del módulo `CryptoService` y de todos los flujos
donde se maneja material criptográfico, antes de la auditoría externa del Mes 8.

**Revisiones requeridas:**

```
1. REVISIÓN DEL CÓDIGO CRYPTO:
   - ¿El nonce de AES-GCM es siempre aleatorio (os.urandom(12))? ¿Nunca reutilizado?
   - ¿La derivación HKDF incluye el contexto correcto (b"Nivo-hybrid-v1")?
   - ¿Las llaves privadas nunca aparecen en logs?
   - ¿Los errores de verificación retornan False sin revelar información?

2. REVISIÓN DE SECRETS EN BD:
   - ¿Las llaves privadas PQC nunca están en PostgreSQL en plano?
   - ¿Los números de cuenta bancaria están cifrados?
   - ¿Los OTPs se almacenan como hash (bcrypt), nunca en plano?
   - ¿Los tokens JWT están en blacklist después de logout?

3. REVISIÓN DE API:
   - ¿Todos los endpoints sensibles requieren autenticación JWT?
   - ¿Los webhooks de Wompi/Truora validan firma HMAC?
   - ¿Los rate limits están activos en producción?
   - ¿Los errores 500 no revelan stack traces al cliente?

4. REVISIÓN DE INFRAESTRUCTURA:
   - ¿Las variables de entorno con secretos no están en el repositorio?
   - ¿El Dockerfile.prod corre como usuario no-root?
   - ¿Las conexiones a BD usan SSL?
```

**Entregable:** Documento `docs/07-security-audit-internal.md` con:
- Cada punto revisado con resultado: PASS / FAIL / RISK
- Para cada FAIL: descripción del problema y solución implementada
- Checklist de items para auditoría externa

**Criterios de éxito:**
- [ ] Todos los ítems de la categoría "CRÍTICO" son PASS
- [ ] El documento `07-security-audit-internal.md` existe y está completo
- [ ] No hay ningún secreto (API key, password, private key) en el historial de git

**Dependencias:** TASK-004, TASK-002, TASK-007

---

### TASK-028 — Performance Testing y Optimización
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** MEDIA

**Descripción:**
Medir y optimizar el rendimiento del backend. El objetivo es soportar 1,000 transacciones
concurrentes sin degradación.

**Archivos a crear:**
- CREAR `backend/tests/load/test_payments_load.py` — Pruebas de carga con locust
- CREAR `backend/tests/load/locustfile.py`

**Métricas objetivo:**
```
P2P Payment (POST /payments/confirm):
  - Latencia P50: < 300ms
  - Latencia P95: < 800ms
  - Latencia P99: < 1500ms
  - Error rate: < 0.1%

Health check (GET /health):
  - Latencia P99: < 50ms

PQC Sign (POST /crypto/sign):
  - Latencia P95: < 200ms (incluye liboqs)
```

**Script de carga (locust):**
```python
# Simular 1,000 usuarios concurrentes haciendo pagos
# 80% pagos P2P, 10% consulta de historial, 10% consulta de saldo
# Duración: 10 minutos
# Ramping: 0→1000 usuarios en 2 minutos
```

**Optimizaciones a implementar si los números no se logran:**
1. Connection pooling de BD (ajustar `pool_size`)
2. Cache de Redis para saldo de usuario (TTL: 30 segundos)
3. Índices de BD faltantes (analizar EXPLAIN ANALYZE)
4. Async en todas las operaciones de BD (verificar no haya calls síncronos)

**Criterios de éxito:**
- [ ] `locust -f locustfile.py --headless -u 1000 -r 100 --run-time 10m` completa sin errores
- [ ] P95 de pagos < 800ms con 1,000 usuarios concurrentes
- [ ] El reporte de locust se guarda como `tests/load/reports/baseline.html`

**Dependencias:** TASK-003, TASK-019

---

### TASK-029 — Documentación de API y SDK Python Inicial
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** MEDIA

**Descripción:**
Crear la documentación pública de la API B2B y el SDK Python básico para facilitar
la integración de clientes enterprise.

**Archivos a crear:**
- CREAR `backend/sdk/python/Nivo_sdk/__init__.py`
- CREAR `backend/sdk/python/Nivo_sdk/client.py`
- CREAR `backend/sdk/python/Nivo_sdk/models.py`
- CREAR `backend/sdk/python/README.md`
- CREAR `backend/sdk/python/examples/sign_document.py`
- CREAR `backend/sdk/python/examples/key_exchange.py`

**SDK Python debe permitir:**
```python
from Nivo_sdk import NivoClient

client = NivoClient(api_key="nv_live_xxxxx")

# Firmar datos con llave administrada por Nivo/KMS/HSM
result = client.sign(data=b"datos a firmar", key_id="kms_receipts_prod")
print(result.signature_hex)    # ML-DSA-65 signature
print(result.fingerprint)      # SHA-256 de la llave pública

# Verificar
valid = client.verify(
    data=b"datos a firmar",
    signature_hex=result.signature_hex,
    public_key_hex=result.public_key_hex
)
# True

# Key exchange híbrido
exchange = client.key_exchange(
    recipient_pqc_key_hex="...",
    recipient_x25519_key_hex="..."
)
# exchange.pqc_ciphertext_hex + exchange.classical_public_key_hex se envían al receptor.
# El shared secret no se retorna en producción.
```

**Criterios de éxito:**
- [ ] `pip install -e .` desde `backend/sdk/python/` instala el SDK sin errores
- [ ] Los dos ejemplos en `examples/` corren contra el servidor de staging
- [ ] El README explica en < 10 minutos cómo integrar PQC a un sistema existente
- [ ] El SDK incluye modo client-side signing para clientes que no delegan firma a Nivo

**Dependencias:** TASK-021

---

### TASK-030 — Preparación para Ronda Seed: Métricas y Data Room
**Estado:** [ ] PENDING
**Agente sugerido:** ceo
**Estimado:** 8–10 horas
**Prioridad:** ALTA (Mes 6)

**Descripción:**
Crear todos los materiales técnicos para el data room de la ronda Seed.
Los VCs necesitan verificar que la tecnología es real.

**Archivos a crear:**
- CREAR `docs/08-technical-due-diligence.md` — Respuestas a preguntas típicas de VC
- CREAR `docs/09-metrics-dashboard.md` — Métricas clave con datos reales
- CREAR `scripts/generate_metrics_report.py` — Script que genera reporte de métricas desde BD

**`technical-due-diligence.md` debe responder:**
```
1. ¿Por qué liboqs y no implementación propia? (respuesta: nunca implementar crypto propio)
2. ¿Qué pasa si NIST depreca ML-KEM-768? (respuesta: crypto-agility, cambio en días)
3. ¿Cuál es el overhead de rendimiento de PQC vs. clásico? (datos reales del benchmark)
4. ¿Cómo está la competencia global en PQC para pagos? (Cloudflare, Google, Signal)
5. ¿Tienen auditoría de seguridad? (resultado de TASK-027)
6. ¿Cuál es el plan de migración para usuarios de Nequi? (análisis de switching costs)
7. ¿Cómo escala la infraestructura a 10M usuarios? (Cloud Run autoscaling + Cloud SQL read replicas)
```

**`metrics-dashboard.md` debe incluir (con datos reales del sistema):**
```
- Usuarios activos mensuales (MAU)
- Transacciones procesadas total y por día
- Volumen procesado en COP
- Latencia promedio P2P
- Uptime del sistema (últimos 30 días)
- Número de comercios activos
- MRR (Monthly Recurring Revenue)
- Contratos B2B firmados o en pipeline
- NPS score de usuarios beta
```

**Criterios de éxito:**
- [ ] El data room está completo y verificable (no afirmaciones sin datos)
- [ ] `python generate_metrics_report.py` genera un PDF con métricas reales
- [ ] La auditoría de seguridad interna está documentada y disponible para due diligence

**Dependencias:** TASK-027, datos de producción reales (beta cerrada)

---

