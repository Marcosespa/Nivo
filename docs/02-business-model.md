# Modelo de Negocio — Nivo

### Segmentos, Unit Economics y Metas Realistas

**Version:** 2.0 | **Fecha:** Mayo 2026 | **Clasificacion:** Confidencial

---

## 1. Resumen Ejecutivo

Nivo no debe salir al mercado como "otro neobanco para todos". El mercado colombiano ya tiene billeteras masivas y habitos digitales consolidados. La oportunidad esta en entrar por tres segmentos donde la combinacion de pagos simples, trazabilidad, proteccion post-cuantica y formalidad progresiva puede ser distinta:

1. **Economia popular y micronegocios** — vendedores, trabajadores independientes y pequenos comercios que necesitan cobrar, registrar ventas y construir historial.
2. **Colombianos globales y freelancers** — personas que reciben ingresos/remesas en USD/EUR y necesitan convertir, separar y mover dinero con trazabilidad.
3. **B2B regulado PQC** — fintechs, cooperativas, aseguradoras, bancos medianos y govtechs que necesitan empezar migracion post-cuantica sin crear un equipo criptografico propio.

La app B2C es el laboratorio vivo de confianza. El B2B PQC es la linea de mayor margen. El segmento social no es filantropia: es una estrategia de adquisicion con bajo CAC, datos transaccionales utiles y una narrativa regulatoria fuerte.

---

## 2. Fuentes y Supuestos Base

Los objetivos se construyen con estas referencias externas y restricciones internas:

- Colombia Fintech reporta 269 fintechs asociadas en 2024; pagos digitales crecio de 72 a 83 empresas entre 2023 y 2024. Mas de 60% del ecosistema asociado esta en credito digital y pagos digitales.
- Colombia Fintech tambien reporta que en 2023 las billeteras digitales alcanzaron 54,63 millones de usuarios/cuentas, mas de 3.000 millones de transacciones y cerca de COP $332 billones movidos. Esto valida adopcion, pero no significa que haya 54,63 millones de usuarios unicos.
- El Reporte de Inclusion Financiera citado por Colombia Fintech indica que 63% de las operaciones monetarias de 2023 fueron digitales y que 94,6% de adultos tenia acceso a algun producto financiero.
- DANE EMICRON 2024 muestra que la economia popular/micronegocios sigue siendo grande y mayoritariamente de cuenta propia; en vendedores ambulantes, 97,2% de propietarios eran trabajadores por cuenta propia.
- Banco de la Republica/analisis de mercado reportan remesas hacia Colombia por alrededor de USD 11.848 millones en 2024; es un flujo grande, pero muy competido y regulado.
- NIST publico FIPS 203, FIPS 204 y FIPS 205 en agosto de 2024 y recomienda iniciar migracion PQC; esto sostiene la narrativa B2B de cripto-agilidad.

**Consecuencia:** Nivo debe plantear metas de prueba de mercado, no metas de hipercrecimiento. En los primeros 24 meses el objetivo sano es demostrar retencion, frecuencia de uso, CAC bajo por comunidad y 2-5 pilotos B2B pagados.

---

## 3. Los Tres Segmentos

### Segmento 1 — Economia popular y micronegocios

**Cliente inicial:** vendedor independiente, negocio familiar, servicio profesional informal o microcomercio que cobra por transferencia/QR y necesita ordenar sus ventas.

**Dolor principal:**

- Cobra en multiples canales y pierde trazabilidad.
- No separa plata personal de negocio.
- No tiene historial limpio para acceder a credito formal.
- Le cuesta demostrar ingresos ante bancos, arriendos, proveedores o programas publicos.

**Propuesta de valor:**

"Cobra, registra y construye historial sin volverte contador."

Nivo ofrece QR/cobro por link, recibos verificables, registro simple de ingresos/gastos, bolsillos visuales y exportes mensuales. La proteccion post-cuantica se comunica como "recibos que siguen siendo verificables en el futuro", no como jerga tecnica.

**Monetizacion:**

| Producto | Precio inicial | Notas |
|---|---:|---|
| Nivo Base | COP $0/mes | Cobros, historial limitado, recibos basicos |
| Nivo Formal | COP $7.900/mes | Reporte mensual, bolsillos, recibos ampliados, soporte |
| Paquete recibos verificables | COP $3.900/mes | Para usuarios Base con mayor uso |
| Comision por cobro aliado | 0%-0,6% | Solo si el partner lo permite y sin encarecer el efectivo digital |

**Metas realistas:**

| Hito | Meta |
|---|---:|
| Mes 3 | 100 usuarios piloto en una ciudad/comunidad |
| Mes 6 | 350 usuarios activos mensuales, 80 pagos/semana |
| Mes 12 | 1.500 usuarios activos, 8% pagando Nivo Formal |
| Mes 24 | 8.000 usuarios activos, 12% pagando, churn mensual < 6% |

**Criterio de exito:** no es volumen total; es que al menos 35% de usuarios activos registre 4+ movimientos al mes y que 10% use reportes mensuales.

---

### Segmento 2 — Colombianos globales y freelancers

**Cliente inicial:** freelancer colombiano, trabajador remoto, estudiante/profesional en Europa o EE.UU., familia que recibe/remite dinero y necesita manejar COP/USD/EUR.

**Dolor principal:**

- Recibir dinero internacional es costoso y poco transparente.
- La conversion COP/USD/EUR tiene spreads dificiles de entender.
- Mezcla dinero de familia, ahorro, impuestos y gastos.
- Necesita comprobantes claros para justificar origen de fondos.

**Propuesta de valor:**

"Recibe, separa y mueve tu dinero entre monedas con trazabilidad clara."

El MVP no promete remesas propias ni FX propio sin aliado. Nivo empieza con bolsillos, recibos, trazabilidad, calculadora y flujos con partner-of-record. El usuario entiende cuanto recibio, cuanto costo, quien ejecuto y que recibo queda firmado.

**Monetizacion:**

| Producto | Precio inicial | Notas |
|---|---:|---|
| Nivo Global | COP $14.900/mes | Bolsillos multi-moneda visuales, reportes, recibos, alertas |
| FX/remesa via partner | 0,3%-0,9% neto para Nivo | Depende de acuerdo con IMC/banco/remesadora |
| Reporte fiscal/origen fondos | COP $9.900 por paquete | Exportes y soportes, sin asesoria tributaria |

**Metas realistas:**

| Hito | Meta |
|---|---:|
| Mes 3 | 50 usuarios beta desde red Europa-Colombia |
| Mes 6 | 150 usuarios activos, 30 pagos/recibos internacionales simulados o via partner |
| Mes 12 | 500 usuarios activos, 15% pagando Nivo Global |
| Mes 24 | 2.000 usuarios activos, 18% pagando, primer acuerdo partner operativo |

**Criterio de exito:** 20% de usuarios activos crea 2+ bolsillos y genera al menos 1 reporte/recibo mensual.

---

### Segmento 3 — B2B regulado PQC

**Cliente inicial:** fintech, cooperativa financiera, aseguradora, govtech o banco mediano que necesita una ruta practica para inventario criptografico, firma post-cuantica, recibos verificables o pilotos de migracion.

**Dolor principal:**

- PQC ya es un tema de roadmap, pero no hay equipo interno.
- Migrar core bancario es lento y riesgoso.
- Auditoria/compliance pide evidencia, no solo presentaciones.
- Necesitan pilotos acotados antes de tocar sistemas criticos.

**Propuesta de valor:**

"PQC-as-a-Service para probar migracion post-cuantica en semanas, no anos."

La oferta no empieza vendiendo "API infinita". Empieza con pilotos: firma de documentos/recibos, verificacion, inventario de algoritmos vulnerables y un sandbox con API key autenticada.

**Monetizacion:**

| Producto | Precio inicial | Notas |
|---|---:|---|
| Diagnostico PQC | USD $2.500-$7.500 unico | Inventario, mapa de riesgo, plan de migracion |
| Piloto API PQC | USD $500-$1.500/mes | Sandbox, soporte, limite de operaciones |
| Produccion controlada | USD $2.000-$5.000/mes | SLA, scopes, auditoria, llaves administradas/HSM |
| Servicios de integracion | USD $75-$120/hora | Paquetes cerrados, no consultoria abierta infinita |

**Metas realistas:**

| Hito | Meta |
|---|---:|
| Mes 3 | 5 conversaciones calificadas, 1 LOI |
| Mes 6 | 1 piloto pagado |
| Mes 12 | 2 clientes piloto pagados, MRR B2B >= USD $1.500 |
| Mes 24 | 5 clientes B2B, MRR B2B >= USD $10.000 |

**Criterio de exito:** convertir 20% de pilotos pagados a contrato anual o produccion controlada.

---

## 4. Proyeccion Conservadora 24 Meses

### Usuarios y clientes

| Mes | Economia popular activos | Global/freelancers activos | B2B pagados |
|---:|---:|---:|---:|
| 3 | 100 | 50 | 0 |
| 6 | 350 | 150 | 1 piloto |
| 12 | 1.500 | 500 | 2 pilotos |
| 18 | 4.000 | 1.100 | 3 clientes |
| 24 | 8.000 | 2.000 | 5 clientes |

### MRR esperado

| Mes | Economia popular | Global/freelancers | B2B PQC | Total MRR |
|---:|---:|---:|---:|---:|
| 3 | COP $0,2M | COP $0,1M | COP $0 | COP $0,3M |
| 6 | COP $0,7M | COP $0,3M | COP $2,1M | COP $3,1M |
| 12 | COP $2,8M | COP $1,5M | COP $6,3M | COP $10,6M |
| 18 | COP $9,0M | COP $4,2M | COP $16,8M | COP $30,0M |
| 24 | COP $22,0M | COP $10,0M | COP $42,0M | COP $74,0M |

**Nota:** usa TRM de referencia COP $4.200/USD. Excluye grants, consultorias puntuales grandes y revenue share no firmado. Es intencionalmente mas bajo que la version anterior porque prioriza evidencia y retencion.

---

## 5. Unit Economics Defensibles

### Supuestos iniciales a validar

| Variable | Supuesto Mes 0 | Como validarlo |
|---|---:|---|
| CAC comunidad economia popular | COP $8.000-$20.000 | pilotos presenciales, referidos, alianzas barriales |
| CAC global/freelancer | COP $25.000-$60.000 | contenido, comunidades, referidos Europa-Colombia |
| CAC B2B | USD $1.000-$4.000 | ventas directas, eventos, LinkedIn, referidos |
| Costo variable OTP/SMS | por confirmar con proveedor | cotizacion Twilio/alternativas locales |
| Costo KYC | por confirmar con Truora/MetaMap/Jumio | contrato startup + volumen |
| Margen bruto B2C | 35%-55% | depende de SMS, KYC, soporte y partner fees |
| Margen bruto B2B | 70%-85% | depende de soporte, HSM, auditoria y SLA |

### Break-even operativo

Con un burn fundador reducido de COP $35M-$55M/mes, el break-even no debe esperarse antes de Mes 24 salvo que B2B cierre antes. La meta realista no es rentabilidad temprana, sino:

- Mes 6: evidencia de uso recurrente.
- Mes 12: MRR suficiente para justificar seed/pre-seed o grants.
- Mes 24: B2B paga infraestructura, auditorias y parte del equipo.

---

## 6. Relacion con la Narrativa Post-Cuantica

La narrativa comercial P0 vive en:

- `ANALISIS_DE_NEGOCIO_RESPUESTAS.md`, seccion 2: propuesta por audiencia y pitch de 20 segundos.
- `docs/05-go-to-market.md`, seccion "Narrativa comercial del diferenciador post-cuantico".

En el modelo de negocio, PQC se usa de forma distinta por segmento:

- Economia popular: recibos verificables e historial confiable.
- Global/freelancers: trazabilidad de origen, conversion y soportes.
- B2B: migracion post-cuantica, auditoria, API y HSM.

---

## 7. Lo Que No Monetizamos Todavia

- Custodia propia de saldos sin SEDPE, COT, banco aliado o estructura equivalente.
- FX propio sin IMC/banco/aliado cambiario.
- Crypto propia sin exchange/VASP aliado y controles AML reforzados.
- Acciones/ETFs sin broker/comisionista o partner regulado.
- Credito propio sin underwriting, capital, aliado y aprobacion legal.

---

## 8. Siguientes Validaciones

1. Validar narrativa post-cuantica con 10 usuarios no tecnicos y 3 compradores B2B.
2. Cotizar SMS, KYC y partner de pagos para cerrar costo variable por usuario activo.
3. Ejecutar piloto economia popular con 100 usuarios y medir retencion de 30 dias.
4. Ejecutar beta global/freelancer con 50 usuarios y medir uso de bolsillos/reportes.
5. Conseguir 5 reuniones B2B calificadas y al menos 1 LOI antes de construir SDK publico completo.

---

## 9. Fuentes

- Superintendencia Financiera de Colombia y Banca de las Oportunidades, Reporte de Inclusion Financiera 2024.
- Colombia Fintech, Fintech Snapshot 2024.
- DANE, EMICRON 2024.
- Banco de la Republica, remesas hacia Colombia 2024.
- NIST, FIPS 203/204/205 y guia de migracion post-cuantica.
