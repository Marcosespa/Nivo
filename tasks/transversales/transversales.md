## TAREAS TRANSVERSALES (todo el período)

---

### TASK-031 — Monitoreo y Alertas de Producción
**Estado:** [ ] PENDING
**Agente sugerido:** devops
**Estimado:** 4–5 horas
**Prioridad:** ALTA

**Descripción:**
Configurar Sentry + GCP Cloud Monitoring + alertas para el equipo.

**Alertas a configurar:**
```
CRÍTICO (PagerDuty/SMS inmediato):
  - /health/pqc retorna 503
  - Error rate > 1% en /payments/confirm
  - Tiempo de respuesta P99 > 3 segundos por 5 minutos
  - BD sin conexión

ALTA (Slack/email en < 5 minutos):
  - Error rate > 0.5% en cualquier endpoint
  - Memoria del contenedor > 80%
  - Cola de OTPs pendientes > 1000
  - Número de fraud_alerts de nivel BLOCK > 10 en 1 hora

MEDIA (email diario):
  - Espacio de disco > 70%
  - Latencia P95 > 500ms
  - Errores de webhook de Wompi/Truora
```

**Criterios de éxito:**
- [ ] Cada alerta tiene runbook documentado en `docs/runbooks/`
- [ ] Una alerta de test dispara el canal de Slack correcto

**Dependencias:** TASK-019

---

### TASK-032 — Prueba de Concepto liboqs en Producción (GCP Cloud Run)
**Estado:** [ ] PENDING
**Agente sugerido:** devops
**Estimado:** 4–5 horas
**Prioridad:** CRÍTICA

**Descripción:**
Verificar que liboqs funciona correctamente en el ambiente de Cloud Run de GCP.
Hay consideraciones de CPU y memoria que deben validarse.

**Pasos:**
```
1. Build de Dockerfile.prod con liboqs compilado desde fuente
2. Push a Google Container Registry (gcr.io/Nivo-staging/api)
3. Deploy a Cloud Run staging con:
   - CPU: 1 vCPU mínimo
   - Memoria: 512MB mínimo
   - Concurrencia: 100 requests por instancia
4. Ejecutar test de health PQC: GET /health/pqc debe retornar {"pqc": "PASS"}
5. Ejecutar benchmark de ML-DSA sign: medir latencia real en Cloud Run
6. Verificar que liboqs_available=true en el response
```

**Problema potencial:**
Cloud Run usa contenedores efímeros. Verificar que liboqs (biblioteca C compartida)
está disponible en el PATH del contenedor en producción y no solo en el builder stage.

**Criterios de éxito:**
- [ ] `GET https://staging-api.Nivo.co/health/pqc` retorna `{"pqc": "PASS", "liboqs_available": true}`
- [ ] Latencia de sign en Cloud Run staging: < 10ms
- [ ] El contenedor arranca en < 10 segundos (cold start)

**Dependencias:** TASK-019

---

### TASK-033 — FUTURO: Agentes de Portafolio con Riesgo Transparente
**Estado:** [ ] PENDING
**Agente sugerido:** product + legal + ml
**Estimado:** 2–4 semanas para discovery + prototipo cerrado
**Prioridad:** FUTURA

**Descripción:**
Diseñar un módulo donde el usuario pueda asignar una parte limitada de su portafolio a un agente de inversión automatizado. El producto debe ser absolutamente claro en la interfaz: es un agente, no una persona; puede tomar decisiones buenas o malas; puede generar ganancias o pérdidas; y no existe rendimiento garantizado.

**Principio de producto:**
El usuario siempre debe entender:
- Qué agente está actuando
- Qué parte del portafolio puede tocar
- Qué estrategia o reglas está siguiendo
- Cuánto puede perder
- Cómo pausarlo o apagarlo inmediatamente
- Quién es el partner regulado responsable de ejecución/custodia

**Alcance futuro:**
- Crear perfil de agente visible: nombre, estrategia, activos permitidos, horizonte, riesgo y comisiones
- Permitir asignación parcial del portafolio, nunca el 100% por defecto
- Definir límites duros: monto máximo, pérdida máxima, rebalanceo máximo, activos permitidos y frecuencia de operación
- Mostrar disclosure antes de activar: "Este agente puede equivocarse. Puedes ganar o perder dinero. Nivo no garantiza resultados."
- Requerir consentimiento explícito y renovable para cada estrategia
- Registrar cada decisión del agente con explicación simple, timestamp, datos usados y recibo verificable
- Agregar botón "Pausar agente" y "Retirar permisos" visible en todo momento
- Crear simulador/paper trading antes de permitir dinero real
- Separar agentes educativos, agentes de simulación y agentes con ejecución real

**Bloqueos regulatorios y legales:**
- No lanzar con dinero real sin broker/comisionista/partner autorizado o licencia que cubra asesoría/gestión automatizada
- No presentar el agente como asesor financiero humano
- No usar lenguaje de promesa: prohibido "garantizado", "seguro", "sin riesgo", "rentabilidad fija"
- Validar si el módulo constituye asesoría de inversión, administración de portafolio, gestión discrecional o intermediación de valores
- Incluir suitability/appropriateness cuando aplique y limitar acceso según perfil de riesgo del usuario

**Criterios de éxito del prototipo cerrado:**
- [ ] UX muestra claramente que es un agente automatizado antes, durante y después de la activación
- [ ] El usuario debe aceptar un disclosure de pérdida posible antes de activar
- [ ] El agente solo puede operar el porcentaje asignado por el usuario
- [ ] Existen límites configurables de pérdida, monto, frecuencia y activos
- [ ] Todas las decisiones quedan auditadas con explicación y recibo verificable
- [ ] El usuario puede pausar o revocar permisos en menos de 2 taps
- [ ] Modo simulación/paper trading funciona antes del modo con dinero real
- [ ] Legal aprueba partner, disclosures, términos y alcance regulatorio antes de cualquier piloto con fondos reales

**Dependencias:** TASK-025, diseño legal de crypto/acciones, broker/comisionista o partner autorizado, revisión compliance SFC/mercado de valores

---

### TASK-034 — Bolsillos de Ahorro y Metas Nivo
**Estado:** [ ] PENDING
**Agente sugerido:** product + backend + mobile + legal
**Estimado:** 1–2 semanas
**Prioridad:** ALTA

**Descripción:**
Implementar bolsillos de ahorro como parte central de la experiencia tipo Revolut. En MVP
pueden ser metas visuales; si existe banco/SEDPE/partner que soporte saldos reales, deben
sincronizarse mediante `provider_subaccount_ref` y mostrar claramente quién custodia el dinero.

**Archivos a crear/modificar:**
- CREAR `backend/app/api/v1/savings.py`
- CREAR `backend/app/services/savings_service.py`
- CREAR `backend/app/models/orm/savings_pocket.py`
- MODIFICAR mobile Home para mostrar bolsillos, progreso y reglas
- MODIFICAR términos/UX para distinguir `visual_goal`, `partner_subaccount` y `custodial`

**Reglas de producto:**
- El usuario puede crear metas: emergencia, viaje, impuestos, inversión, familia.
- Cada bolsillo tiene `mode`: `visual_goal`, `partner_subaccount` o `custodial`.
- Si el modo no es custodial, la UI no puede decir "depósito Nivo" ni "cuenta de ahorros Nivo".
- Cambios de estado y reglas automáticas se firman con ML-DSA para recibo verificable.
- Reglas opcionales: redondeo de compras, monto recurrente, porcentaje de ingreso.

**Criterios de éxito:**
- [ ] Crear, editar y eliminar bolsillos desde API y mobile
- [ ] Cada bolsillo muestra quién custodia el saldo o si es meta visual
- [ ] Reglas de ahorro generan movimientos/referencias firmadas sin duplicar transacciones
- [ ] No hay copy de captación propia si `mode=visual_goal` o `partner_subaccount`
- [ ] Tests cubren cambios de modo, límites y firma de estado

**Dependencias:** TASK-001, TASK-002, TASK-003

---

### TASK-035 — Módulos Regulados de Inversión, Crypto y FX
**Estado:** [ ] PENDING
**Agente sugerido:** product + backend + legal + compliance
**Estimado:** 2–4 semanas discovery + prototipo cerrado
**Prioridad:** ALTA

**Descripción:**
Diseñar e implementar la capa común de productos regulados para FX, crypto, acciones y ETFs.
Nivo mantiene la experiencia de una sola app, pero cada ejecución vive en el partner autorizado
hasta tener licencia propia.

**Archivos a crear/modificar:**
- CREAR `backend/app/api/v1/partner_orders.py`
- CREAR `backend/app/services/partner_order_service.py`
- CREAR `backend/app/services/disclosure_service.py`
- CREAR `backend/app/models/orm/partner_order.py`
- CREAR `backend/app/models/orm/product_disclosure.py`
- CREAR adapters: `fx_partner_adapter.py`, `crypto_partner_adapter.py`, `broker_partner_adapter.py`

**Reglas por módulo:**
- FX: mostrar tasa, spread/fee, vigencia, partner, fuente y tiempo estimado antes de confirmar.
- Crypto: disclosure de volatilidad, pérdida total, irreversibilidad, ausencia de garantía estatal, límites y AML reforzado.
- Acciones/ETFs: partner/broker visible, tipo de orden, costos, suitability/appropriateness si aplica, sin asesoría propia.
- Todas las órdenes guardan `risk_disclosure_version`, `accepted_disclosure_hash`, `partner`, `partner_order_id` y firma ML-DSA.
- El usuario debe poder ver "quién ejecuta" y "quién custodia" antes de confirmar.

**Criterios de éxito:**
- [ ] Se puede crear una orden simulada de FX/crypto/stock con disclosure aceptado
- [ ] La orden se firma con ML-DSA antes de enviarse al adapter del partner
- [ ] La API rechaza órdenes si falta partner, disclosure o perfil KYC requerido
- [ ] La UI muestra costos, riesgos, partner y estado de ejecución sin prometer rendimiento
- [ ] Legal/compliance aprueba texto de disclosures antes de cualquier piloto real

**Dependencias:** TASK-001, TASK-002, TASK-003, TASK-006, TASK-023, revisión legal/partner aprobado

---

