# Modelo de Negocio — Nivo
### Revenue Model, Unit Economics & Proyecciones Financieras

**Versión:** 1.0 | **Fecha:** Abril 2026 | **Clasificación:** Confidencial

---

## 1. Resumen Ejecutivo del Modelo

Nivo opera un modelo **neobanco freemium multi-segmento** con varias fuentes de ingresos:

1. **Subscripción B2C** — usuarios premium con funciones avanzadas
2. **Transaccional** — comisiones por cambio de divisa, tarjeta virtual y productos habilitados por aliados
3. **SaaS B2B** — terminal de cobros para pymes (mensual + comisión)
4. **API B2B** — PQC-as-a-Service para fintechs y bancos (licenciamiento por volumen)
5. **FX multi-moneda** — spread transparente COP/USD/EUR vía aliado cambiario
6. **Inversiones vía partner** — revenue share por acciones/ETFs, sin ser broker propio
7. **Crypto vía exchange aliado** — fee/revenue share por compra/venta, con disclosure de riesgo

El insight clave: **la app B2C es la misión y el activo de marca**, mientras que B2B/API ayuda a financiar auditorías, credibilidad y ventas enterprise. El margen bruto de la API B2B puede ser ~85%, mientras que el margen de la app B2C depende de partners, interchange, FX y suscripciones.

**Ajuste regulatorio MVP:** durante la validación inicial, Nivo no monetiza por custodiar saldos propios. Monetiza por suscripción, tarjeta virtual con aliado, spread/fee permitido sobre servicios de terceros, recibos verificables y API PQC. La captación directa queda fuera del MVP hasta tener SEDPE, COT/Sandbox o entidad vigilada aliada. Ahorro, crypto, acciones y FX se diseñan como módulos del neobanco, pero la ejecución/custodia vive en el partner autorizado hasta que Nivo tenga licencia propia.

### Ámbito social (core de negocio)

Parte de la propuesta de Nivo es contribuir a **mitigar la exclusión** que afecta a quienes trabajan en informalidad en Colombia —formación, crédito formal, bienestar— mediante la **escalera de la formalidad progresiva**: billeteras digitales que habiliten **historia crediticia real** para trabajadores informales y vendedores ambulantes, con miras a **alternativas al crédito informal** (incluido el “gota a gota”) vía productos formales y **crédito garantizado por el Estado** cuando el marco y los aliados lo permitan, siempre con **apoyo sin persecución**. El detalle narrativo y de alineación estratégica está en [**AMBITO_SOCIAL.md**](../AMBITO_SOCIAL.md) en la raíz del repositorio.

---

## 2. Segmentos y Propuesta de Valor

### Segmento 1 — Usuarios B2C (Consumidores)

**Perfil objetivo:**
- Millennials y Gen Z en Colombia (25–40 años)
- Ingreso medio-alto, familiarizados con apps financieras
- Preocupados por privacidad y seguridad digital
- Early adopters de tecnología
- Colombianos en el exterior que manejan COP/EUR/USD o envían dinero a Colombia

**Tamaño de mercado:**
- Colombia: 52M habitantes, 35M con smartphone
- Usuarios activos de billeteras digitales: ~22M (Nequi + Daviplata + otros)
- Cifras de "usuarios/cuentas" de billeteras pueden sumar más que la población por duplicidad entre productos; usarlas como señal de adopción, no como usuarios únicos reales
- TAM objetivo: 3M (usuarios con perfil tech-savvy, ingresos > $1.5M COP/mes)
- SAM año 1: 200K (Bogotá + Medellín, early adopters)
- SOM año 1: 50K usuarios activos

**Estructura de planes:**

| Plan | Precio | Incluye |
|------|--------|---------|
| Nivo Free | COP $0/mes | Pagos P2P, recarga PSE, bolsillos de ahorro visuales, límite $500K/transacción, recibo protegido básico |
| Nivo Plus | COP $9,900/mes | Todo lo anterior + tarjeta virtual, límites más altos, finanzas personales, recibos certificados |
| Nivo Pro | COP $24,900/mes | Todo Plus + multi-moneda (COP/USD/EUR), cambio de divisas, acceso anticipado a inversión/crypto por partner, soporte prioritario |

**Ingresos adicionales B2C:**
- Cambio de divisas: spread del 1.5% (vs. 2.5–3.5% bancos tradicionales)
- Tarjeta virtual con emisor/BaaS: COP $4,900 de activación (incluida en Plus/Pro)
- Recargas por PSE: $0 para crecimiento si el costo del aliado lo permite
- Recibos certificados ML-DSA para usuarios Pro: incluido o cobro por paquete
- Módulos de inversión/crypto: revenue share o fee permitido por partner, siempre con disclosure y sin prometer rendimiento

---

### Segmento 2 — Pymes y Comercios

**Perfil objetivo:**
- Restaurantes, tiendas, servicios profesionales en Colombia
- Facturación entre $5M–$500M COP/mes
- Frustrados con las comisiones de datafóno (2.5–3.5%)
- Necesitan comprobantes digitales con validez legal

**Propuesta de valor:**
Terminal de cobros QR con firma digital ML-DSA. Cada cobro es una transacción con firma post-cuántica — inmutable, auditable, reconocida por la DIAN para facturación electrónica.

**Estructura de precios:**

| Plan | Precio | Comisión | Incluye |
|------|--------|----------|---------|
| Comercio Básico | COP $0/mes | 1.8% por transacción | QR estático, dashboard básico |
| Comercio Pro | COP $59,900/mes | 1.2% por transacción | QR dinámico, facturación electrónica DIAN, reportes, ML-DSA certificados |
| Comercio Enterprise | COP $199,900/mes | 0.8% por transacción | Todo Pro + integración ERP, API webhooks, soporte dedicado |

**Comparativo vs. competencia:**

| Solución | Comisión | Certificación PQC | Facturación DIAN |
|---------|---------|------------------|-----------------|
| Datafóno tradicional | 2.5–3.5% | No | No nativa |
| Wompi | 2.9% + $900 fijo | No | No |
| Bold | 2.79% | No | No |
| **Nivo Comercio Pro** | **1.2%** | **Sí (ML-DSA)** | **Sí** |

---

### Segmento 3 — Fintechs / Bancos (API B2B)

**Perfil objetivo:**
- Fintechs colombianas (Addi, Rappi Pay, Lulo Bank, Bold)
- Fintechs pequeñas y medianas que no tienen equipo para implementar PQC
- Bancos medianos que necesitan compliance PQC (Banco Popular, Itaú Colombia, Banco Falabella)
- Gobierno colombiano (MinTIC, agencias con requisitos de seguridad crítica)

**Propuesta de valor:**
PQC-as-a-Service: integra cifrado post-cuántico a tu producto existente en semanas. API REST con SDKs en Python, Node.js y Java. SLA del 99.99%. Certificación de cripto-agilidad incluida.

**Estructura de precios API:**

| Tier | Volumen mensual | Precio |
|------|----------------|--------|
| Starter | Hasta 100K operaciones | USD $500/mes |
| Growth | 100K – 1M operaciones | USD $0.004 por operación |
| Enterprise | +1M operaciones | Negociado (estimado USD $0.002/op) |
| Licencia On-Premise | Instalación propia | USD $50,000/año + soporte |

**Operaciones facturables:** key exchange (ML-KEM), firma digital (ML-DSA), verificación de firma, re-encriptación de datos históricos.

---

### Segmento 4 — Consultoría PQC

**Perfil objetivo:**
- Empresas del sector financiero, salud, energía con datos altamente sensibles
- Organizaciones que necesitan auditoría de cripto-agilidad
- Empresas con mandatos de compliance (gobierno, defensa)

**Servicios:**

| Servicio | Precio | Duración |
|---------|--------|----------|
| Auditoría de cripto-agilidad | USD $15,000 – $40,000 | 4–8 semanas |
| Plan de migración PQC | USD $25,000 – $80,000 | 8–16 semanas |
| Implementación y acompañamiento | USD $10,000/mes | Contrato mínimo 3 meses |
| Capacitación equipos técnicos | USD $3,000/día | 1–5 días |

---

### Segmento 5 — Ahorro, multi-moneda, acciones y crypto

**Perfil objetivo:**
- Freelancers colombianos que cobran en USD/EUR y pagan gastos en COP
- Colombianos en el exterior que mueven dinero entre Europa/EE.UU. y Colombia
- Pymes exportadoras pequeñas con pagos internacionales
- Usuarios tech-savvy que ya compran crypto o acciones en apps extranjeras

**Propuesta de valor:**
Una experiencia tipo Revolut para Colombia: ahorrar en bolsillos, cambiar COP/USD/EUR, comprar/vender crypto y acceder a acciones/ETFs desde una sola app, con órdenes firmadas, trazabilidad PQC y aliados responsables de ejecución/custodia.

**Principios regulatorios:**
- Nivo no actúa como IMC, broker, comisionista ni exchange propio sin licencia.
- El ahorro real con saldo custodiado requiere banco aliado, SEDPE, COT o estructura equivalente; antes de eso, los bolsillos son metas visuales o subcuentas del aliado.
- FX se ejecuta vía banco/IMC/aliado cambiario.
- Acciones/ETFs se ejecutan vía broker regulado o partner internacional validado legalmente.
- Crypto se ejecuta vía exchange/VASP aliado, separado del saldo de pagos.
- No se dan recomendaciones de inversión; solo ejecución bajo instrucciones del usuario.

**Estructura de monetización:**

| Producto | Revenue | Condición de lanzamiento |
|----------|---------|--------------------------|
| Bolsillos de ahorro | Suscripción Plus/Pro, revenue share permitido o fee de cuenta | Banco aliado/SEDPE/COT si hay saldo real; visual si no hay custodia |
| FX COP/USD/EUR | Spread 0.5%–1.5% o fee fijo | Aliado cambiario + términos aprobados |
| Acciones/ETFs | Revenue share, fee por orden o suscripción Pro | Broker partner + disclosure de riesgo |
| Crypto | Fee de compra/venta 0.5%–1.5% | Exchange/VASP aliado + AML reforzado |
| Recibos/órdenes PQC | Incluido en Pro o fee por paquete | `CryptoService` auditado |

---

## 3. Proyecciones Financieras — 24 Meses

### Supuestos Clave

- Conversión Free → Plus: 8% de usuarios activos mensuales
- Conversión Free → Pro: 2%
- CAC B2C (digital marketing): COP $15,000 (~$3.5 USD)
- CAC B2B API (ventas directas): USD $2,000
- Churn mensual B2C: 5%
- Churn mensual B2B: 2%
- Tipo de cambio referencia: 1 USD = 4,200 COP

### Proyección de Usuarios B2C

| Mes | Usuarios Activos | Free | Plus | Pro |
|-----|-----------------|------|------|-----|
| 3 | 2,000 | 1,800 | 160 | 40 |
| 6 | 8,000 | 7,000 | 640 | 160 |
| 9 | 20,000 | 17,400 | 1,600 | 400 |
| 12 | 50,000 | 43,500 | 4,000 | 1,000 |
| 18 | 120,000 | 104,400 | 9,600 | 2,400 |
| 24 | 250,000 | 217,500 | 20,000 | 5,000 |

### Proyección de Ingresos Mensuales (COP Millones)

| Mes | B2C Subs | B2C Transac. | Comercios | API B2B | Consultoría | **Total MRR** |
|-----|---------|-------------|----------|---------|-------------|--------------|
| 3 | 2.6M | 0.8M | 0 | 0 | 0 | **3.4M** |
| 6 | 10.3M | 3.2M | 5.9M | 0 | 0 | **19.4M** |
| 9 | 25.8M | 8.0M | 23.9M | 8.4M | 42M | **108M** |
| 12 | 64.5M | 20M | 59.9M | 25.2M | 84M | **253M** |
| 18 | 154.8M | 48M | 149.8M | 63M | 126M | **541M** |
| 24 | 322.5M | 100M | 349.5M | 168M | 210M | **1,150M** |

*Nota: Mes 12 MRR ~$60K USD. Mes 24 MRR ~$275K USD. La consultoría es lumpy (proyectos puntuales), no lineal.*

### Estructura de Costos

**Costos fijos mensuales (Mes 1–6):**

| Ítem | Costo/mes (COP) |
|------|----------------|
| Equipo técnico (3 devs senior) | $30M |
| CEO + 1 BD | $20M |
| Legal + compliance | $5M |
| Infraestructura cloud (GCP + Cloudflare) | $3M |
| Herramientas + SaaS | $1M |
| Marketing digital | $5M |
| **Total burn mensual** | **$64M (~$15K USD)** |

**Runway objetivo:** 18 meses con ronda seed de USD $400K–$600K.

---

## 4. Unit Economics

### B2C

| Métrica | Valor |
|---------|-------|
| ARPU mensual (promedio ponderado) | COP $4,200 (~$1 USD) |
| CAC digital | COP $15,000 (~$3.5 USD) |
| LTV (24 meses, 5% churn) | COP $63,000 (~$15 USD) |
| **LTV/CAC** | **4.2x** |
| Margen bruto B2C | ~45% |
| Payback period | ~3.6 meses |

### B2B API

| Métrica | Valor |
|---------|-------|
| ARPU mensual (Starter) | USD $500 |
| CAC (ventas directas) | USD $2,000 |
| LTV (36 meses, 2% churn) | USD $17,600 |
| **LTV/CAC** | **8.8x** |
| Margen bruto API | ~85% |
| Payback period | ~4 meses |

---

## 5. Estrategia de Fundraising

### Pre-seed (Actual — Mes 0)
- **Monto:** USD $150K–$250K
- **Fuente:** FFF (Founders, Friends, Family) + iNNpulsa Colombia
- **Uso:** MVP técnico, equipo fundador mínimo (3 personas), licencias y hosting
- **Hito para próxima ronda:** MVP funcionando + 500 usuarios activos

### Seed (Mes 6–9)
- **Monto:** USD $500K–$1.5M
- **Fuente:** VCs LATAM (Magma Partners, Platanus Ventures, Kaszek Ventures)
- **Valoración objetivo:** USD $5–8M pre-money
- **Uso:** Equipo completo (10 personas), marketing de lanzamiento, proceso regulatorio SFC
- **Hito para próxima ronda:** $30K MRR + 1 contrato B2B firmado

### Serie A (Mes 18–24)
- **Monto:** USD $5–15M
- **Fuente:** VCs internacionales + corporate VCs (bancarios latinoamericanos)
- **Uso:** Expansión Ecuador/Perú, equipo de ventas B2B enterprise, certificación internacional PQC

---

## 6. Alianzas Estratégicas con Impacto Financiero

| Aliado | Tipo | Impacto en Revenue |
|--------|------|-------------------|
| Pomelo / Dock / Adyen | Tarjeta virtual/BaaS | Reduce alcance PCI y evita emitir tarjeta desde cero |
| Mastercard / Visa | Red de tarjeta | Habilita revenue de interchange mediante emisor aliado |
| ACH Colombia / PSE | Transferencias | Habilita pagos y recargas sin captación directa |
| Truora / MetaMap / Jumio | KYC | Onboarding obligatorio sin construir verificación propia |
| IMC / banco aliado | Cambio de divisas | Habilita multi-moneda COP/USD/EUR sin licencia cambiaria propia |
| Broker/comisionista partner | Acciones/ETFs | Habilita inversión sin ser intermediario de valores |
| Exchange/VASP aliado | Crypto | Habilita compra/venta sin custodiar criptoactivos directamente |
| Colombia Fintech | Gremio | Credibilidad, eventos, contactos y validación institucional |
| Cloudflare | Infraestructura | Descuento startup + credibilidad técnica PQC |
| Bancolombia | Licenciamiento B2B | Potencial contrato de $500K–$2M USD/año |
| iNNpulsa Colombia | Subvención | $100–$300M COP no dilutivo |
| MinTIC Colombia | Contrato gobierno | $200M–$1B COP (largo plazo, alta probabilidad post-compliance) |

---

*Revisión trimestral de proyecciones obligatoria. Los números son estimaciones con supuestos conservadores.*
*CFO por contratar — Mes 8 como prioridad de hiring.*
