# Roadmap — Nivo
### MVP a 24 Meses | Hitos, Entregables y Criterios de Éxito

**Versión:** 1.0 | **Fecha:** Abril 2026

---

## Visión del Roadmap

```
Mes 1–4       Mes 5–8         Mes 9–12        Año 2
   │               │               │              │
[MVP Core]  [Comercios +   [API B2B PQC   [LATAM
[P2P + PQC]  Tarj. Virtual]  + Lanzamiento]  Expansión]
```

---

## FASE 1 — MVP Core (Mes 1–4)
### "La billetera más segura de Colombia"

**Objetivo:** Tener un MVP P2P funcional con PQC híbrido, KYC y recibos firmados, listo para beta cerrada con 500 usuarios reales **sin captación directa de dinero**. El saldo legal y el movimiento de fondos viven en pasarela/banco/aliado regulado.

### Mes 1 — Fundaciones

**Backend:**
- [ ] Setup de repositorio, CI/CD, entornos (dev/staging/prod)
- [ ] Módulo `CryptoService` con ML-KEM-768 + X25519 híbrido
- [ ] Módulo de firma ML-DSA-65 para transacciones
- [ ] Modelos de base de datos: users, wallets, transactions, pqc_keys
- [ ] Endpoint de health check incluyendo `/health/pqc`
- [ ] Tests unitarios para módulo crypto (cobertura >90%)

**Infraestructura:**
- [ ] GCP project setup + Cloud Run + Cloud SQL (staging)
- [ ] Cloudflare configurado como proxy con ML-KEM habilitado
- [ ] Variables de entorno y secrets management (GCP Secret Manager)
- [ ] Pipeline CI/CD básico (GitHub Actions)

**Legal/Regulatory:**
- [ ] Constitución de Nivo SAS en Colombia
- [ ] Memo legal de modalidad MVP: middleware sin captación, banco aliado, Sandbox/COT o SEDPE
- [ ] Conversación exploratoria con abogado sobre Sandbox/COT SFC si el flujo toca actividad vigilada
- [ ] Contratación abogado especializado en SFC/pagos digitales
- [ ] Políticas AML/LAFT básicas y responsable de cumplimiento designado

**Equipo:**
- [ ] CTO/Lead Backend contratado
- [ ] 1 Backend Developer senior contratado
- [ ] 1 Mobile Developer React Native contratado

**Hito del Mes 1:** `POST /api/v1/crypto/test-transaction` funcional con PQC híbrido ✓

---

### Mes 2 — Core de Pagos

**Backend:**
- [ ] Sistema de registro y autenticación de usuarios (phone + OTP)
- [ ] Onboarding KYC básico (integración Truora API)
- [ ] Vista de cuenta/wallet no custodial: estados, límites, proveedor de fondos y saldo mostrado desde aliado
- [ ] Flujo completo de transacción P2P:
  - `POST /api/v1/payments/initiate`
  - `POST /api/v1/payments/confirm`
  - `GET /api/v1/payments/{tx_id}`
- [ ] Sistema de notificaciones push (Firebase FCM)
- [ ] Rate limiting y protección básica contra fraude (reglas heurísticas)

**Mobile:**
- [ ] Pantallas: Splash, Onboarding, Registro por celular
- [ ] Pantalla de billetera con saldo
- [ ] Flujo de envío de dinero por número de celular
- [ ] Recibo de transacción con "Protección activa" visible

**Hito del Mes 2:** Primera transacción de pago real (interna) con firma ML-DSA verificable ✓

---

### Mes 3 — Recarga y Retiro

**Backend:**
- [ ] Integración PSE mediante PayU, Wompi, ACH Colombia o banco aliado
- [ ] Flujo de pago/recarga sin custodia: Nivo inicia, firma y concilia; el aliado mueve fondos
- [ ] Flujo de retiro a cuenta bancaria vía ACH/aliado, sin saldo propio en Nivo
- [ ] Historial de transacciones paginado
- [ ] Descarga de comprobantes de transacción (PDF firmado)

**Mobile:**
- [ ] Pantalla de recarga (PSE)
- [ ] Pantalla de retiro
- [ ] Historial de movimientos
- [ ] Perfil de usuario y configuración
- [ ] Sistema de recibo verificable visible al usuario ("¿Qué protege esto?" educación en-app)

**Testing:**
- [ ] Tests de integración E2E para flujo completo
- [ ] Pruebas de carga básicas (100 tx concurrentes)
- [ ] Revisión de seguridad interna del módulo crypto

**Hito del Mes 3:** Recarga PSE + pago P2P + retiro bancario funcionando en staging ✓

---

### Mes 4 — Beta Cerrada

**Estabilización:**
- [ ] Resolución de bugs críticos de Mes 1–3
- [ ] Optimización de latencia (objetivo: <800ms P2P)
- [ ] Monitoreo completo (Cloud Monitoring + Sentry + Jaeger)
- [ ] Runbooks operacionales documentados
- [ ] Plan de respuesta a incidentes

**Beta:**
- [ ] Invitación a 500 usuarios beta (red de conocidos, comunidades tech Bogotá/Medellín)
- [ ] Programa de feedback estructurado (Notion + encuestas semanales)
- [ ] Límites de transacción conservadores: máx $500K COP/día por usuario
- [ ] Soporte manual por WhatsApp Business

**Métricas de éxito Fase 1:**
- 500 usuarios beta activos
- 1,000 transacciones procesadas sin incidentes
- Latencia P2P < 800ms (percentil 95)
- 0 incidentes de seguridad
- NPS > 50 en encuesta de beta

---

## FASE 2 — Comercios + Tarjeta Virtual (Mes 5–8)
### "El datafóno del futuro"

**Objetivo:** Habilitar pagos en comercios y tarjeta virtual, llegar a 8,000 usuarios activos.

### Mes 5–6 — Terminal QR para Comercios

**Backend:**
- [ ] Sistema de registro de comercios (CRUD merchant)
- [ ] Generación de QR dinámico con firma ML-DSA-65
- [ ] Endpoint de cobro desde QR: `POST /api/v1/merchant/charge`
- [ ] Dashboard web para comercios (Next.js)
- [ ] Reportes y conciliación diaria
- [ ] Integración básica facturación electrónica DIAN

**Mobile (comerciante):**
- [ ] App separada "Nivo Negocio" o modo comerciante en app principal
- [ ] Generación y display de QR de cobro
- [ ] Notificación instantánea de pago recibido
- [ ] Reporte de ventas del día

**Planes comercio:**
- [ ] Lanzamiento plan Comercio Básico (0/mes, 1.8% comisión)
- [ ] Lanzamiento plan Comercio Pro ($59,900/mes, 1.2%)

**Hito Mes 6:** 50 comercios activos procesando pagos reales ✓

---

### Mes 7–8 — Tarjeta Virtual y Lanzamiento Público

**Tarjeta Virtual:**
- [ ] Integración con emisor de tarjetas (Pomelo, Dock, Adyen o aliado equivalente)
- [ ] Emisión de tarjeta virtual Visa/Mastercard por usuario Plus
- [ ] Generación de número virtual para compras online
- [ ] Congelamiento/descongelamiento instantáneo desde app
- [ ] Notificaciones de uso de tarjeta en tiempo real
- [ ] Confirmación de alcance PCI-DSS: Nivo solo maneja tokens, no PAN/CVV

**Marketing y Lanzamiento:**
- [ ] Landing page cuantapay.co
- [ ] Campaña de referidos (invita 3, gana 1 mes gratis de Plus)
- [ ] Contenido educativo: "¿Por qué tu billetera actual no es segura?" (blog, LinkedIn, TikTok)
- [ ] Eventos en Bogotá Tech Week y Campus Party Colombia
- [ ] Programa de afiliados para comercios

**Lanzamiento Público:**
- [ ] Apertura a registro sin invitación
- [ ] Plan freemium activo con todos los features de Free tier
- [ ] Proceso de onboarding KYC automatizado (<5 min)
- [ ] Soporte en app + email

**Métricas de éxito Fase 2:**
- 8,000 usuarios activos totales
- 500 comercios con terminal QR
- MRR > COP $19M (~$4,500 USD)
- Tiempo de onboarding KYC < 5 minutos
- Rating app: > 4.2 estrellas

---

## FASE 3 — API B2B + Escala (Mes 9–12)
### "Infraestructura PQC para Colombia"

**Objetivo:** Lanzar API B2B de PQC-as-a-Service, cerrar 3 contratos B2B, 50,000 usuarios activos.

### Mes 9–10 — API B2B PQC

**Backend:**
- [ ] API de PQC-as-a-Service pública con autenticación por API key
- [ ] Endpoints:
  - `POST /api/v1/crypto/key-exchange` (ML-KEM encapsulate/decapsulate)
  - `POST /api/v1/crypto/sign` (ML-DSA-65 firma)
  - `POST /api/v1/crypto/verify` (verificación de firma)
  - `POST /api/v1/crypto/hybrid-encrypt` (AES-GCM con llave híbrida)
- [ ] SDK Python y Node.js (open source en GitHub)
- [ ] Documentación API completa (Swagger + guías de integración)
- [ ] Dashboard de uso para clientes B2B (métricas de operaciones)
- [ ] Sistema de billing por operación

**Ventas B2B:**
- [ ] Material de ventas (deck, one-pager técnico)
- [ ] Contacto con 20 fintechs colombianas objetivo
- [ ] Contacto con Bancolombia para licenciamiento
- [ ] Participación en Colombia Fintech Summit
- [ ] Propuesta para MinTIC (programa de gobierno digital)

**Hito Mes 10:** 1 contrato B2B firmado (fintech o banco) ✓

---

### Mes 11–12 — Consolidación y Preparación Año 2

**Producto:**
- [ ] Multi-moneda: COP, USD, EUR como experiencia visual y contable vía aliado cambiario
- [ ] Cambio de divisas in-app (spread 0.5%–1.5%) con IMC/banco/partner aprobado
- [ ] Finanzas personales: categorización automática de gastos
- [ ] Detección de fraude ML Fase 1 (modelos de comportamiento)
- [ ] Diseño técnico/legal de módulos crypto y acciones (sin lanzamiento público hasta partner aprobado)

**Compliance:**
- [ ] Auditoría PQC externa (firma de ciberseguridad certificada)
- [ ] Obtención de certificación ISO 27001 (proceso iniciado)
- [ ] Compliance AML/LAFT actualizado con abogado y aliado regulado
- [ ] Decisión formal: seguir sin captación, aplicar a Sandbox/COT o iniciar ruta SEDPE

**Fundraising:**
- [ ] Preparación deck para ronda Seed
- [ ] Due diligence materials listos
- [ ] Cierre de ronda Seed objetivo: USD $500K–1.5M

**Métricas de éxito Fase 3:**
- 50,000 usuarios activos
- 3 contratos B2B firmados
- MRR > COP $253M (~$60K USD)
- Auditoría PQC completada
- Ronda Seed en proceso o cerrada

---

## AÑO 2 — Expansión LATAM (Mes 13–24)

**Hitos principales:**
- [ ] Lanzamiento en Ecuador (Q1 Año 2)
- [ ] Lanzamiento en Perú (Q2 Año 2)
- [ ] Licencia operativa en Ecuador y Perú
- [ ] Lanzamiento controlado de crypto compra/venta vía exchange/VASP aliado
- [ ] Lanzamiento controlado de acciones/ETFs vía broker/comisionista partner
- [ ] Prototipo cerrado de agentes de portafolio: el usuario asigna una parte limitada, ve claramente que opera un agente automatizado y acepta que puede ganar o perder dinero
- [ ] 250,000 usuarios activos multi-país
- [ ] API B2B con 10+ clientes enterprise
- [ ] Serie A cerrada (USD $5–15M)
- [ ] Equipo: 25–35 personas

---

## Criterios de Éxito Global (Fin de Año 1)

| KPI | Meta | Indicador de alarma |
|-----|------|-------------------|
| Usuarios activos | 50,000 | < 30,000 = replantear GTM |
| MRR | COP $253M | < COP $100M = revisar pricing |
| Contratos B2B | 3 | 0 = replantear estrategia B2B |
| NPS | > 50 | < 30 = crisis de producto |
| Uptime | 99.9% | < 99.5% = problema de infraestructura |
| Incidentes seguridad críticos | 0 | Cualquiera = protocolo de crisis inmediato |
| Tiempo onboarding KYC | < 5 min | > 10 min = abandono de usuarios |

---

## Dependencias Críticas del Roadmap

| Dependencia | Responsable | Fecha límite | Riesgo si falla |
|------------|-------------|-------------|----------------|
| Memo legal no-captación / COT / SEDPE | CEO + abogado | Mes 1 | El MVP puede nacer como producto vigilado sin presupuesto |
| Integración Truora KYC | Backend Dev | Mes 2 | Manual KYC (escala lenta) |
| Convenio PSE (PayU/Wompi) | CEO | Mes 3 | Sin recarga bancaria en MVP |
| Integración Pomelo/Dock (tarjeta) | Backend Dev | Mes 7 | Sin tarjeta virtual en lanzamiento |
| Aliado IMC/banco para FX | CEO + abogado | Mes 9 | Sin multi-moneda real |
| Broker/exchange partners | CEO + abogado | Año 2 | Sin acciones/crypto dentro de app |
| Auditoría PQC externa | CEO + CTO | Mes 8 | Sin credencial para ventas B2B |

---

## Ruta resumida regulatorio-first

| Etapa | Acción | Tiempo | Validación |
|-------|--------|--------|------------|
| Validación | Definir MVP sin captación directa + ruta Sandbox/COT si aplica | Mes 1–2 | Memo legal aprobado |
| Producto | App P2P con PQC híbrido + KYC externo | Mes 2–4 | 500 beta users sin incidentes |
| Primeros usuarios | Red personal + comunidades colombianas en exterior | Mes 3–5 | 1,000 transacciones firmadas |
| Monetización | Tarjeta virtual con aliado + API PQC B2B | Mes 6–9 | Primer MRR |
| Multi-moneda | COP/USD/EUR con aliado IMC/banco | Mes 9–12 | FX funcional sin ser IMC propio |
| Inversiones | Crypto y acciones vía partners | Año 2 | Contratos, disclosures y AML reforzado |
| Escalabilidad | Decidir SEDPE formal, banco aliado o expansión regional | Año 2 | Compliance y unit economics listos |

---

*El roadmap se revisa mensualmente en sprint review. Cambios de alcance requieren aprobación del CEO.*
*Metodología: Sprint de 2 semanas, revisión semanal de métricas, retrospectiva mensual de roadmap.*
