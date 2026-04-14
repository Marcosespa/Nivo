# Visión Estratégica — Nivo
### Decisiones del CEO | Documento Fundacional v1.0

**Fecha:** Abril 2026
**Autor:** CEO, Nivo
**Clasificación:** Confidencial — Interno

---

## 1. La Tesis Central

> **Nivo existe porque el sistema financiero digital está construido sobre arena cuántica.**

Las instituciones financieras colombianas y latinoamericanas corren sobre criptografía de curva elíptica (ECC) y RSA. Estos algoritmos funcionan perfectamente hoy. El problema es mañana: los expertos del NIST proyectan que una computadora cuántica con suficiente potencia podría romper RSA-2048 y ECC-256 en horas. La pregunta no es *si* — es *cuándo*.

Nuestra apuesta: las empresas que integren PQC hoy dominarán los contratos gubernamentales, bancarios y de infraestructura crítica en LATAM en los próximos 5–7 años. Somos los primeros en movernos en Colombia. La ventana es real y estrecha.

---

## 2. Decisiones Estratégicas del CEO

### 2.1 — Por qué Colombia primero

**Decisión:** Lanzar exclusivamente en Colombia durante los primeros 18 meses antes de expandir.

**Razonamiento:**
- Colombia tiene el ecosistema fintech más maduro de LATAM después de Brasil y México, con regulación activa de la SFC y avances recientes en finanzas abiertas
- Nequi ya educó al mercado: 18M+ usuarios saben qué es una billetera digital
- La regulación de finanzas abiertas y el Sandbox/COT de la SFC crean una ventana para nuevos actores con propuestas diferenciadoras, siempre que el MVP no confunda tecnología con captación de recursos
- Bogotá y Medellín tienen ecosistemas de talento técnico de primer nivel para construir el equipo inicial
- Precedente inmediato: Ankatech (2025) ya convence al primer banco colombiano de adoptar defensa cuántica — el mercado existe y está siendo educado

**Riesgo aceptado:** Perdemos velocidad vs. expansión multi-país. Lo acepto. Mejor dominar un mercado que ser mediocres en cinco.

---

### 2.2 — Blindaje cuántico para todos

**Decisión:** Mantener lo cuántico como promesa central de Nivo para todos los usuarios, no solo para B2B. El lenguaje técnico se adapta por audiencia: simple y emocional en B2C, profundo y certificable en B2B.

**Razonamiento:**
El usuario final no compra siglas, pero si compra tranquilidad. Nivo debe decir con claridad que su dinero, identidad y datos nacen protegidos para la era post-cuántica. PQC no es un adorno tecnico: es parte del producto diario, igual que una tarjeta congelable, una alerta antifraude o un recibo verificable.

**Implementación:**
- Pantalla de "Blindaje cuántico activo" en cada transacción
- Certificado digital descargable por transacción (para usuarios pro)
- Sello verificable "Recibo protegido" visible en recibos
- Educación en-app sobre privacidad, fraude, protección familiar, computación cuántica y recibos verificables
- Lenguaje PQC completo en documentación técnica, ventas B2B, auditorías y pantallas avanzadas para usuarios curiosos

**Riesgo aceptado:** Algunos usuarios no entenderán PQC al inicio. Lo resolvemos con producto, no escondiendo la idea: "tu plata y tus datos siguen protegidos cuando la tecnología cambie".

---

### 2.3 — Modelo híbrido desde el día 0

**Decisión:** Implementar cifrado híbrido PQC + X25519 desde el primer día, no solo PQC puro.

**Razonamiento técnico:**
- PQC puro hoy crea incompatibilidades con sistemas heredados (bancos, pasarelas de pago)
- El estándar de la industria durante la transición es el cifrado híbrido (ver: Cloudflare, Google, Thales)
- Un fallo de compatibilidad en una transacción de pago destruye la confianza del usuario irreversiblemente
- ML-KEM-768 + X25519 simultáneo da seguridad cuántica sin sacrificar interoperabilidad

**Esto es no negociable técnicamente.** Cualquier shortcut aquí es una deuda que destruirá el producto.

---

### 2.4 — B2C es la misión, B2B financia y valida

**Decisión:** Construir Nivo como banco de consumo primero, con B2B como línea de ingresos y validación técnica. La app B2C no es solo demo: es el producto principal y el lugar donde se gana confianza de marca.

**Razonamiento económico:**
- Una billetera B2C en Colombia compite con Nequi (18M usuarios, respaldo Bancolombia), Daviplata (Davivienda) y Bancolombia App. El CAC va a ser alto.
- El LTV de un cliente B2B (fintech, banco, gobierno) es 100–1000x el de un usuario individual
- Nuestra estrategia: usar la app B2C para demostrar que PQC, recibos verificables, antifraude y UX financiera funcionan en producción real; usar esa prueba para vender API y confianza a terceros

**La app de consumo es el corazón de la compañía.** Cada transacción procesada es confianza de usuario y caso de estudio para alianzas.

---

### 2.5 — Bancolombia como aliado, no como competidor

**Decisión:** Posicionarnos activamente como proveedor tecnológico para Bancolombia, no solo como competencia directa.

**Razonamiento:**
- Bancolombia ya está estudiando PQC internamente. Ellos tienen la distribución (millones de clientes), nosotros tenemos la tecnología lista
- Un acuerdo de licenciamiento B2B con Bancolombia vale más que 1M de usuarios en nuestra billetera
- La estrategia: construir la billetera, demostrar en producción, acercarse a Bancolombia en el mes 6–9 con propuesta concreta de licenciamiento de la capa PQC

**Esto requiere que nuestro código sea auditado, documentado y certificable.** No podemos venderle a un banco una caja negra.

---

### 2.6 — Banco como destino, no como punto de partida regulatorio

**Decisión:** El destino de Nivo es ser el neobanco quantum-safe de Colombia y LATAM. La ruta inicial no debe asumir captación directa hasta tener SEDPE, COT, banco aliado o cobertura equivalente.

**Razonamiento:**
- Captar saldos de usuarios dispara ruta SFC como entidad vigilada, probablemente SEDPE, con tiempos y costos incompatibles con un MVP rápido
- El valor diferencial inicial no está en custodiar dinero; está en firma PQC, trazabilidad, UX, KYC, conciliación, ahorro visual, acceso modular a productos y confianza
- PSE/ACH, banco aliado y emisores BaaS permiten mover dinero real mientras Nivo valida demanda
- El Sandbox/COT de la SFC es una herramienta, no una promesa de aprobación ni un sustituto de asesoría legal

**Regla de producto:** mientras no exista COT, SEDPE o banco aliado que cubra la operación, Nivo no será el ledger legal de saldos de usuarios. Pero la experiencia debe sentirse como una cuenta bancaria moderna desde el primer día.

---

### 2.7 — Superapp tipo Revolut, por módulos regulados

**Decisión:** La visión de producto es una app tipo Revolut para Colombia: pagos, ahorro, tarjeta, multi-moneda, crypto, acciones, finanzas personales y seguridad cuántica. La ejecución será modular, no un big bang regulatorio.

**Razonamiento:**
- Multi-moneda es el puente natural hacia freelancers, colombianos en el exterior y pymes exportadoras
- Acciones y ETFs aumentan LTV, pero requieren broker/comisionista o socio regulado; Nivo no debe convertirse en intermediario de valores en el MVP
- Crypto puede atraer early adopters, pero debe vivir en un módulo separado, con exchange/VASP aliado, disclosures y límites
- Los bolsillos de ahorro son una pieza central de la experiencia, aunque al inicio puedan ser metas visuales o subcuentas del aliado
- La ventaja de Nivo no es tomar balance sheet risk antes de tiempo; es UX, confianza, PQC, antifraude, trazabilidad, educación financiera y orquestación

**Orden de lanzamiento:**
1. P2P + KYC + recibos ML-DSA
2. Bolsillos de ahorro y control financiero
3. Tarjeta virtual con emisor
4. Cambio COP/USD/EUR vía aliado cambiario
5. API PQC B2B
6. Crypto y acciones vía partners, sin asesoría de inversión

**Regla de producto:** ningún módulo de inversión o crypto se activa sin responsable regulatorio, disclosure de riesgo, límites, monitoreo AML/LAFT y revisión legal.

---

## 3. Propuesta de Valor por Segmento

### Consumidor final (B2C)
*"Paga con la seguridad que los bancos no te ofrecen todavía."*

La billetera más segura de Colombia, con la misma facilidad de Nequi. Para quien mueve plata y le importa que sea privada hoy y en 20 años.

### Pymes y comercios
*"Acepta pagos con la misma tecnología que usan los gobiernos más avanzados del mundo."*

Terminal de cobros QR con firma ML-DSA. Cada transacción es inmutable y cuánticamente segura. Para quien necesita que sus registros sean auditables para siempre.

### Fintechs y bancos (B2B)
*"Agrega seguridad post-cuántica a tu producto existente en semanas, no años."*

API de cifrado PQC-as-a-Service. Sin reconstruir tu infraestructura. Con soporte de migración y certificación de cripto-agilidad.

### Usuarios multi-moneda e inversión
*"Cambia, invierte y protege tu dinero desde una sola app."*

COP, USD y EUR para freelancers, pymes exportadoras y colombianos en el exterior. Crypto y acciones como módulos con aliados, sin prometer rentabilidad y con trazabilidad PQC de órdenes y recibos.

---

## 4. Lo que NO vamos a hacer (Decisiones de NO)

Estas son igualmente importantes que las decisiones de SÍ:

| No haremos | Por qué |
|-----------|---------|
| Blockchain propia, token propio o yield cripto | Distracción del core, riesgo reputacional y regulatorio |
| Préstamos o crédito en el MVP | Requiere capital de riesgo, regulación de crédito compleja, nos distrae |
| Captar saldos propios sin cobertura regulatoria | Dispara ruta SFC/SEDPE antes de validar demanda |
| Ser broker o exchange propio en el MVP | Multiplica regulación, capital y riesgo operacional |
| Dar recomendaciones de inversión | Exige controles de asesoría y eleva responsabilidad legal |
| Expansión a Brasil en año 1 | Brasil requiere regulación diferente (Banco Central), idioma distinto, equipo propio |
| PQC "solo como marketing" | Destruye la credibilidad técnica que es nuestra única ventaja competitiva real |
| Construir nuestra propia criptografía | Nunca. Usamos liboqs (Open Quantum Safe), auditado y estandarizado por NIST |

---

## 5. Principios de Liderazgo para el Equipo

1. **Seguridad no es negociable.** Ningún shortcut criptográfico, sin importar la presión de tiempo.
2. **Velocidad con criterio.** MVP en 4 meses es posible porque tenemos scope claro, no porque acortemos calidad.
3. **Documentar todo.** Somos una empresa de tecnología con aspiraciones de venderle a bancos. Los bancos auditan todo.
4. **El usuario no es estúpido.** Puede entender PQC si se lo explicamos bien. Es nuestra responsabilidad explicarlo.
5. **Construir para crecer.** Cada decisión técnica debe poder escalar a 10M de transacciones/día.

---

## 6. Métricas de Éxito — Año 1

| Métrica | Meta |
|---------|------|
| Usuarios activos B2C (Mes 12) | 50,000 |
| Transacciones procesadas/día (Mes 12) | 10,000 |
| Comercios con terminal QR | 500 |
| Contratos B2B firmados | 3 |
| Ingresos MRR (Mes 12) | COP 150M (~$35K USD) |
| Tiempo de uptime del sistema | 99.9% |
| Incidentes de seguridad críticos | 0 |
| Auditoría PQC completada | Sí (Mes 8) |

---

## 7. Riesgos Estratégicos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|-----------|
| Regulación SFC retrasa operación | Media | Alto | MVP sin captación directa, memo legal Mes 1, aliado jurídico especializado y ruta COT/SEDPE solo si aplica |
| Nequi/Bancolombia lanza PQC propio | Baja | Muy alto | Acelerar B2B antes de que el mercado se consolide; el timing es nuestra ventaja |
| liboqs tiene vulnerabilidad | Muy baja | Crítico | Crypto-agility: arquitectura modular permite cambiar algoritmo sin rediseño total |
| Adopción lenta por desconocimiento de PQC | Alta | Medio | Estrategia de educación + early adopters técnicos como evangelistas |
| Competencia de Cyte (startup PQC colombiana) | Media | Medio | Evaluar alianza o diferenciación clara; ellos son B2B, nosotros somos B2C+B2B |
| Captación de talento técnico PQC | Alta | Medio | Contratar early, opciones de equity competitivas, remote-first |

---

*Próxima revisión estratégica: Trimestre 2 — post-MVP*
*Aprobado por: CEO, Nivo*
