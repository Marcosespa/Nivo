# Prompts de Investigación — Tareas de Negocio / Felipe
**Proyecto:** Nivo — Billetera digital post-cuántica colombiana
**Uso:** Copiar cada bloque completo a una IA de investigación (Perplexity, ChatGPT, Gemini, etc.)

---

## Contexto base del negocio (incluido en cada prompt, no repetir manualmente)

> Nivo es una billetera digital colombiana que usa criptografía post-cuántica certificada por el NIST
> (ML-KEM-768 para cifrado, ML-DSA-65 para firmas digitales). Opera en un modelo no-custodial:
> el dinero de los usuarios lo custodia un aliado regulado (Wompi/PSE), mientras Nivo actúa como
> capa de orquestación y seguridad. Tiene planes FREE / PLUS / PRO. Integra Wompi (pasarela de
> pagos), Truora (KYC), Twilio (SMS OTP) y GCP (infraestructura). La segunda línea de negocio
> es una API B2B que vende criptografía post-cuántica como servicio (PQC-as-a-Service) a empresas.
> El equipo es fundador-técnico, con sprint 2 activo hoy (mayo 2026). El lanzamiento público está
> planeado para Sprint 6 (agosto 2026).

---

## T-02 — Documentación de contratos comerciales con aliados

```
CONTEXTO DEL NEGOCIO:
Soy co-fundador de Nivo, una billetera digital colombiana con criptografía post-cuántica (NIST
FIPS 203/204). Operamos en modo no-custodial: integramos Wompi como pasarela de pagos PSE,
Truora para KYC (verificación de identidad con liveness y documentos), Twilio para SMS OTP,
y GCP como infraestructura cloud. El producto tiene planes FREE / PLUS / PRO para usuarios
finales y una API B2B (PQC-as-a-Service) para empresas. Estamos en sprint 2 (mayo 2026),
pre-lanzamiento público, y necesitamos tener claridad total sobre los costos y términos de cada
aliado antes de hablar con cualquier inversionista o proyectar ingresos.

PROBLEMA:
No tenemos documentación formal de los términos comerciales, costos por transacción/llamada,
SLAs ni estructura de escalabilidad de precio de ninguno de los cuatro aliados. Esto nos impide
construir unit economics reales ni hacer due diligence.

LO QUE NECESITO QUE INVESTIGUES:
1. WOMPI (Bancolombia fintech, Colombia):
   - Tarifas actuales de procesamiento PSE (porcentaje + tarifa fija por transacción)
   - Tarifas de pagos con tarjeta débito/crédito si aplica
   - Tarifa de su servicio de nómina o dispersión si aplica
   - Tiempo de acreditación al comercio (T+0, T+1?)
   - Modelo de cobro: ¿facturan mensual o descontado por transacción?
   - SLA de uptime publicado
   - Cómo se estructuran los contratos (mínimos mensuales, volumetría, exclusividad)
   - Si tienen un plan sandbox con límites gratuitos y cuándo empieza a cobrar

2. TRUORA (Colombia/LATAM, KYC):
   - Precio por verificación de identidad (documento + selfie + liveness)
   - Precio por consulta a listas restrictivas (OFAC, PEPs, etc.)
   - Precio por check de antecedentes (judiciales, financieros)
   - Si cobran por re-intento fallido o solo por verificación exitosa
   - SLA de tiempo de respuesta por consulta (segundos? minutos?)
   - Descuentos por volumen (umbrales)
   - Alternativas competidoras en Colombia con precios comparables:
     MetaMap (antes Mati), Jumio, Onfido, Acuant

3. TWILIO (SMS OTP, internacional):
   - Costo por SMS enviado a Colombia (número +57) en USD y COP
   - Diferencia de precio entre SMS transaccional y SMS marketing
   - Si tienen precios especiales para startups o early-stage
   - Alternativas más baratas para Colombia: AWS SNS, MessageBird, Infobip,
     Vonage — precio comparativo por SMS a Colombia
   - SLA de entregabilidad reportado para Colombia

4. GCP (Google Cloud Platform):
   - Costo estimado mensual para una fintech pre-lanzamiento en Colombia:
     Cloud Run (backend FastAPI), Cloud SQL PostgreSQL (db-f1-micro o db-g1-small),
     Cloud Memorystore Redis, Cloud Trace, Cloud Logging, Secret Manager
   - Créditos de GCP disponibles para startups (Google for Startups, equivalente)
   - Si hay precios regionales (us-central1 vs southamerica-east1) y cuánto impacta la latencia

5. ALIADOS FUTUROS — investiga opciones para las siguientes fases:
   - Custodia crypto (si Nivo añade BTC/ETH en el futuro): Fireblocks, BitGo, Anchorage
   - FX (conversión COP ↔ USD): Oanda, Currencycloud, Wise Platform
   - Emisor de tarjeta virtual en Colombia: Mastercard Fintech Program, Visa Ready,
     Pomelo, Highnote
   - Banco aliado / sponsor bancario en Colombia para operar sin licencia SEDPE:
     Bancolombia B89, Lulo Bank (Grupo Aval), iF Bank, Ualá Colombia

FORMATO DE RESPUESTA ESPERADO:
Para cada aliado, entrégame una tabla con:
| Aliado | Servicio | Costo unitario | Modelo de cobro | SLA | Notas / alternativas |

Luego, para Wompi + Truora + Twilio + GCP, calcula el costo variable mensual estimado asumiendo:
- 500 usuarios activos mensuales
- Promedio 4 transacciones por usuario por mes (2.000 transacciones)
- 100% de usuarios con KYC (500 verificaciones de onboarding)
- 2 SMS OTP por usuario activo por mes (1.000 SMS)
- Infraestructura GCP mínima viable

Esto me permitirá calcular el costo por usuario activo mensual (CPUAM) para validar
si los precios de PLUS y PRO tienen margen positivo.
```

---

## T-03 — Definición de pricing PLUS / PRO

```
CONTEXTO DEL NEGOCIO:
Soy co-fundador de Nivo, una billetera digital colombiana con criptografía post-cuántica
(NIST FIPS 203/204). El modelo de negocio es freemium: plan FREE con límites básicos,
y planes PLUS y PRO de pago mensual. Hoy (mayo 2026) los límites están en código
(transacciones diarias, monto máximo), pero no tenemos definido el precio de PLUS ni de PRO,
ni qué features adicionales justifican el pago. El lanzamiento público es en agosto 2026.

USUARIOS OBJETIVO DE NIVO:
- Segmento 1 — Usuario casual: 18-30 años, ciudades intermedias, usa Nequi para recibir
  plata de la familia o pagar arriendo. Promedio 2-4 transacciones al mes, monto < $200.000 COP.
- Segmento 2 — Freelancer / trabajador independiente: recibe pagos de clientes, necesita
  llevar un control de sus entradas. 8-20 transacciones al mes, monto $500.000 - $5.000.000.
- Segmento 3 — Power user tech: profesional que valora la seguridad digital, entiende qué
  es la criptografía post-cuántica, quiere los beneficios premium y está dispuesto a pagar
  más que Nequi. 15+ transacciones, montos altos.

EL DIFERENCIADOR DE NIVO vs. COMPETIDORES:
A diferencia de Nequi, Daviplata o Lulo, Nivo usa criptografía post-cuántica (NIST FIPS 203/204).
Cada transacción se firma con ML-DSA-65. Esto lo posiciona como la billetera más segura de
Colombia y potencialmente de LATAM. El argumento de venta no es "más barato" sino "más seguro".

COSTOS INTERNOS ESTIMADOS (para que calcules márgenes):
Usando los precios de mercado actuales de los aliados:
- SMS Twilio a Colombia: ~$0,04 USD por SMS (~$170 COP)
- KYC Truora (onboarding): ~$1,50 USD una sola vez (~$6.300 COP)
- Transacción Wompi PSE: ~1,5% + $600 COP fija
- GCP infraestructura: estimar ~$0,15-0,25 USD por usuario activo mensual

LO QUE NECESITO QUE INVESTIGUES:
1. BENCHMARK DE COMPETIDORES COLOMBIANOS Y REGIONALES:
   Para cada uno, documenta: planes disponibles, precio mensual, features incluidos,
   límites de transacciones/monto, modelo de conversión.
   - Nequi (Bancolombia)
   - Daviplata (Davivienda)
   - Lulo Bank
   - Ualá Colombia
   - RappiPay Colombia
   - Tpaga (ahora Movii?)
   - Comparativo internacional de referencia: Revolut, Wise, Nubank Brasil

2. PROPUESTA DE ESTRUCTURA DE PLANES:
   Basándote en el benchmark, propón:

   Plan FREE (adquisición, no monetización):
   - ¿Qué límites diarios/mensuales en COP son razonables para que el usuario sienta el
     producto pero quiera más?
   - ¿Qué features deberían ser exclusivos de planes pagos?

   Plan PLUS (conversión del usuario casual):
   - Precio sugerido en COP/mes y en COP/año (con descuento)
   - Features que justifican el pago vs FREE
   - Límites de transacción y monto
   - ¿Debe incluir algún beneficio tangible? (cashback, seguro, tarjeta)

   Plan PRO (power user / freelancer):
   - Precio sugerido en COP/mes y en COP/año
   - Features diferenciadores vs PLUS
   - ¿API acceso? ¿Reportes contables? ¿Soporte prioritario?

3. CÁLCULO DE MARGEN POR PLAN:
   Con los costos internos que te di arriba y los precios que propongas:
   - ¿Es el margen de PLUS positivo desde el primer suscriptor?
   - ¿Cuántos usuarios FREE se necesitan para cubrir la infraestructura base?
   - ¿Cuál es el precio mínimo de PLUS para tener margen positivo?

4. NARRATIVA DE VENTA (lenguaje para el usuario, no técnico):
   Para cada plan, escribe 3 bullets en español colombiano casual que expliquen el valor.
   No usar términos técnicos. Ejemplo de estilo correcto: "Tu plata protegida con el mismo
   cifrado que usan los gobiernos, disponible para ti desde hoy."

5. ESTRATEGIA DE CONVERSIÓN FREE → PLUS:
   - ¿Límite de transacciones mensuales o de monto total?
   - ¿Trial de 30 días? ¿Freemium permanente con límite o fremium con tiempo?
   - ¿Qué fricción convierte mejor: límite de monto, número de transacciones, o features bloqueados?
   - Benchmarks de tasas de conversión típicas en fintech freemium LATAM

FORMATO DE RESPUESTA:
1. Tabla comparativa de competidores
2. Tabla de estructura de planes propuesta con precios y features
3. Tabla de cálculo de margen por plan
4. Bullets de narrativa de venta por plan
5. Recomendación de estrategia de conversión con justificación
```

---

## T-06 — Plan formalizado de ruta regulatoria (SEDPE)

```
CONTEXTO DEL NEGOCIO:
Soy co-fundador de Nivo, una startup fintech colombiana que opera una billetera digital
con criptografía post-cuántica. Hoy (mayo 2026) operamos bajo un modelo no-custodial:
el dinero de los usuarios es custodiado por un aliado regulado (Wompi, que opera bajo
el paraguas de Bancolombia), y Nivo actúa como interfaz y capa de seguridad. Esto nos
permite operar sin licencia propia, pero tiene limitaciones estratégicas:
1. Pagamos comisión al aliado en cada transacción (comprime márgenes)
2. No podemos ofrecer intereses sobre saldo ni crédito sin licencia propia
3. Dependemos de la disponibilidad y políticas del aliado
4. Para captar inversión seria necesitamos mostrar un path regulatorio claro

El modelo de negocio de largo plazo requiere obtener una licencia SEDPE (Sociedad
Especializada en Depósitos y Pagos Electrónicos) de la Superintendencia Financiera
de Colombia (SFC), o al menos firmar un acuerdo formal con un banco aliado que nos
permita operar bajo su licencia mientras tramitamos la nuestra.

LO QUE NECESITO QUE INVESTIGUES:
1. MARCO REGULATORIO SEDPE EN COLOMBIA (actualizado a 2025-2026):
   - Qué es una SEDPE: definición legal, qué puede y no puede hacer
   - Marco legal base: Decreto 1491 de 2015, Decreto 222 de 2022, circulares de la SFC
   - Diferencia entre SEDPE y otras figuras: EC (Establecimiento de Crédito), CF (Compañía
     de Financiamiento), Sociedad de Servicios Financieros, PSE
   - ¿Qué operaciones está permitido hacer con licencia SEDPE vs. sin ella?
     (recepción de depósitos, dispersión, FX, crédito, tarjetas)

2. REQUISITOS PARA SOLICITAR LICENCIA SEDPE:
   - Capital mínimo requerido (en COP, referencia actual — aprox. COP 2.000M pero verificar)
   - Requisitos de gobierno corporativo: junta directiva, revisor fiscal, oficial de cumplimiento
   - Requisitos de infraestructura tecnológica y ciberseguridad exigidos por la SFC
   - Requisitos KYC/AML que exige la SFC: niveles de verificación, monitoreo de transacciones,
     umbrales de reporte, obligación UIAF
   - Tiempo estimado del trámite: desde solicitud hasta resolución (meses típicos)
   - Costo estimado del proceso: honorarios legales, capital mínimo, auditorías

3. ALTERNATIVAS REGULATORIAS (de menor a mayor tiempo/costo):
   Evalúa estas tres rutas y da un análisis de pros/contras para cada una:

   RUTA A — Operar bajo aliado bancario sponsor (más rápido, hoy posible):
   - ¿Qué implica legalmente? ¿El aliado asume responsabilidad regulatoria?
   - ¿Qué bancos en Colombia tienen programa activo de bancas como servicio (BaaS)?
   - ¿Cuánto cobra el banco por este servicio? ¿Cómo se estructura el revenue share?
   - ¿Limita el producto que Nivo puede construir?

   RUTA B — Registro como COT (Corresponsal de operaciones de tarjetas) o figura intermedia:
   - ¿Existe alguna figura regulatoria intermedia entre "sin licencia" y "SEDPE plena"?
   - Si sí: requisitos, tiempo, qué operaciones habilita
   - Ejemplos de fintechs colombianas que usaron esta ruta

   RUTA C — Solicitud directa de licencia SEDPE:
   - Paso a paso del trámite ante la SFC
   - Documentos requeridos
   - Timeline realista (meses)
   - Costo total estimado

4. GAPS ACTUALES DE NIVO vs. REQUISITOS SEDPE:
   Nivo hoy tiene:
   - KYC con Truora (verificación biométrica + documentos)
   - OTP por SMS para cada transacción (autenticación fuerte)
   - Registro de todas las transacciones con firma criptográfica
   - Arquitectura técnica cloud-native en GCP
   - Sin capital formal constituido todavía (startup pre-seed)

   ¿Qué le falta a Nivo para cada ruta? Lista los gaps por ruta.

5. ROADMAP DE CUMPLIMIENTO RECOMENDADO:
   Propón un cronograma en 3 fases con fechas tentativas desde junio 2026:
   - Fase 1 (0-6 meses): qué completar para poder operar bajo aliado
   - Fase 2 (6-18 meses): qué completar para solicitar SEDPE
   - Fase 3 (18-36 meses): obtención de licencia SEDPE

6. EJEMPLOS DE FINTECHS COLOMBIANAS QUE YA RECORRIERON ESTE CAMINO:
   - Daviplata, Nequi, Ualá, Tpaga, Movii, Iris (Bancolombia)
   - ¿Cuál fue la ruta de cada uno? ¿Empezaron con licencia o con aliado?
   - Qué aprendizajes son aplicables a Nivo

7. FIRMAS DE ABOGADOS ESPECIALIZADAS EN FINTECH / REGULACIÓN FINANCIERA EN COLOMBIA:
   - Identifica mínimo 5 firmas reconocidas con práctica fintech/SFC
   - Para cada una: nombre, socios conocidos en el área, referencia de cliente fintech atendido

FORMATO DE RESPUESTA:
1. Resumen ejecutivo de 1 página: qué puede hacer Nivo hoy vs. qué necesita para crecer
2. Tabla comparativa de las 3 rutas: tiempo, costo, qué habilita, riesgo
3. Tabla de gaps de Nivo vs. requisitos SEDPE
4. Cronograma de 3 fases en formato tabla
5. Lista de firmas de abogados recomendadas
6. Recomendación final: ¿cuál ruta debería tomar Nivo primero y por qué?
```

---

## T-07 — GTM de API B2B (segmento, pricing, pipeline)

```
CONTEXTO DEL NEGOCIO:
Soy co-fundador de Nivo, una fintech colombiana. Además de la billetera B2C, tenemos una
segunda línea de negocio: una API que vende criptografía post-cuántica como servicio
(PQC-as-a-Service). La API ya está construida técnicamente:
- POST /api/v1/crypto/sign — firma datos con ML-DSA-65 (estándar NIST FIPS 204)
- POST /api/v1/crypto/verify — verifica firma ML-DSA-65
- Soporte para ML-KEM-768 (encapsulación de llave, NIST FIPS 203)
- Latencia < 50ms por operación, infraestructura en GCP

El diferenciador real: somos la única API de criptografía post-cuántica de consumo en
Colombia y probablemente en LATAM. Los algoritmos que usamos son los que el NIST
estandarizó en 2024 como reemplazo a RSA y ECC frente a computación cuántica.

El problema: la API está lista técnicamente pero no tenemos clientes B2B, ni precio, ni
pipeline de ventas, ni documentación comercial. Este análisis define el go-to-market.

LO QUE NECESITO QUE INVESTIGUES:

1. DEFINICIÓN DEL ICP (CLIENTE IDEAL B2B):
   Analiza estos segmentos y determina cuál es el más viable para primeras ventas:

   Segmento A — Fintechs colombianas:
   - Wallets, neobancos, plataformas de pagos que necesitan firmas digitales verificables
   - ¿Cuántas fintechs activas hay en Colombia hoy? ¿Cuántas tienen capacidad de pagar API?
   - ¿Cuál es su posición frente a la criptografía post-cuántica?

   Segmento B — Sector financiero tradicional:
   - Bancos medianos (Bancamía, Confiar, Coofinep), cooperativas financieras, fondos de empleados
   - ¿Tienen mandatos regulatorios que los fuercen a actualizar su criptografía?
   - ¿Cuál es el proceso de compra típico y cuánto demora?

   Segmento C — Gobierno y sector público:
   - DIAN, Registraduría, MinTIC, Agencia Nacional Digital
   - ¿Colombia tiene mandatos de PQC para el sector público?
   - ¿Cómo se vende a gobierno en Colombia? ¿Licitaciones? ¿Contratos directos?

   Segmento D — Empresas con necesidad de firmas verificables:
   - Notarías digitales, plataformas de contratos electrónicos, gestores documentales
   - ¿Existe regulación colombiana que exija firmas con cierto nivel de seguridad?

2. MODELO DE PRICING DE LA API:
   Evalúa estos tres modelos y recomienda uno con justificación:

   Opción A — Pay per use (por llamada):
   - $X COP por cada 1.000 firmas procesadas
   - ¿Cuál es el precio de referencia en el mercado global de APIs crypto? (AWS KMS, GCP KMS)
   - Ventaja: alineado con el valor generado. Desventaja: ingresos impredecibles

   Opción B — Por usuario activo mensual del cliente:
   - El cliente paga por cada usuario final de su plataforma que usa la firma
   - ¿Cómo se verifica el número de usuarios activos? ¿Confianza o auditoría?

   Opción C — Plan plano mensual con tiers:
   - Tier Starter: hasta X firmas/mes, precio fijo
   - Tier Growth: hasta Y firmas/mes
   - Tier Enterprise: custom
   - Ventaja: predecible. Desventaja: el cliente paga aunque no use.

   Para el modelo recomendado, calcula:
   - Costo marginal por llamada a la API (compute GCP Cloud Run + liboqs)
   - Precio mínimo para tener margen positivo
   - Precio de mercado comparable (AWS KMS cobra ~$0.03 por 10.000 operaciones)

3. COMPETENCIA GLOBAL Y POSICIONAMIENTO:
   Investiga quién más vende APIs de criptografía post-cuántica hoy:
   - AWS (KMS con soporte PQC?)
   - Google Cloud (soporte CRYSTALS-Kyber/Dilithium?)
   - PQShield, evolutionQ, ISARA, Sandbox AQ
   - ¿Alguno opera en Colombia o tiene precios accesibles para startups colombianas?
   - ¿Cuál es el argumento de diferenciación de Nivo vs. estas opciones?

4. PIPELINE DE PRIMEROS 30 CLIENTES POTENCIALES:
   Dame una lista de 30 empresas colombianas reales que podrían ser clientes B2B de esta API.
   Para cada una incluye:
   | Empresa | Segmento | Por qué necesita PQC | Contacto/LinkedIn probable | Tamaño |

   Criterios de selección:
   - Fintechs con más de 10.000 usuarios activos
   - Bancos medianos o cooperativas con presupuesto tech
   - Empresas de firma electrónica o validación documental
   - Iniciativas del gobierno digital colombiano

5. PROCESO DE VENTAS B2B:
   Diseña el pipeline en 5 pasos específico para vender una API crypto a empresas en Colombia:
   - Paso 1: Contacto inicial (¿LinkedIn? ¿Email? ¿Eventos?)
   - Paso 2: Demo técnica (¿qué mostrar? ¿cómo probar la API en vivo?)
   - Paso 3: Prueba en sandbox (¿gratis? ¿30 días? ¿asistida?)
   - Paso 4: Propuesta económica (¿quién aprueba en el cliente? ¿cuánto demora?)
   - Paso 5: Cierre y onboarding

6. MATERIALES QUE NECESITAMOS CREAR:
   - Estructura del pitch deck de 1 página para enviar por email
   - Estructura del NDA estándar para prueba piloto
   - SLAs mínimos que deberíamos garantizar en contrato: uptime, latencia, soporte
   - Estructura de la documentación técnica que el cliente necesita para integrarse

7. MÉTRICAS DE ÉXITO DEL CANAL B2B:
   - ¿Cuántos leads calificados por mes es un buen objetivo para los primeros 6 meses?
   - ¿Cuál es la tasa de conversión típica en ventas de API B2B en LATAM?
   - ¿Cuánto MRR B2B debería generar Nivo al final del primer año para que valga la pena?

FORMATO DE RESPUESTA:
1. Tabla del ICP recomendado con justificación
2. Modelo de pricing recomendado con cálculo de margen
3. Tabla de 30 leads potenciales
4. Pipeline de ventas paso a paso
5. Lista de materiales a crear con estructura de cada uno
6. OKRs del canal B2B para los primeros 6 meses
```

---

## T-11 — Estrategia de adquisición y referral program

```
CONTEXTO DEL NEGOCIO:
Soy co-fundador de Nivo, una billetera digital colombiana con criptografía post-cuántica.
El lanzamiento público está planeado para agosto 2026. El producto tiene:
- Registro con OTP por SMS y KYC biométrico (Truora)
- Pagos P2P en COP
- Planes FREE / PLUS / PRO
- Diferenciador: la única billetera en Colombia con cifrado post-cuántico NIST

El reto: somos una startup con presupuesto de marketing limitado. No podemos competir en
publicidad pagada contra Nequi (Bancolombia) o Daviplata. Necesitamos un motor de
crecimiento orgánico y viral que nos lleve a los primeros 10.000 usuarios en 6 meses.

PERFIL DEL USUARIO OBJETIVO:
- Edad: 22-38 años
- Ciudades: Bogotá, Medellín, Cali, Barranquilla, Bucaramanga
- Perfil: freelancer, trabajador independiente, profesional tech, emprendedor, estudiante
  universitario con ingresos propios
- Comportamiento actual: usa Nequi para recibir plata pero desconfía de la seguridad
  digital después de haber visto o sufrido fraudes
- Motivación para cambiarse a Nivo: mayor seguridad percibida + tecnología de punta

LO QUE NECESITO QUE INVESTIGUES:

1. MECÁNICA ÓPTIMA DE REFERRAL PARA FINTECH EN COLOMBIA:
   - ¿Qué tipo de incentivo convierte mejor en billeteras digitales colombianas?
     (COP en cuenta, descuento en plan, beneficios no monetarios, puntos?)
   - ¿Doble incentivo (referidor + referido) vs. solo el referido?
   - ¿Cuándo entregar el incentivo? ¿Al registro? ¿Al completar KYC? ¿Al hacer la primera
     transacción? — Análisis de qué criterio protege mejor contra fraude
   - Casos referenciales: ¿cómo lo hizo Ualá en Colombia? ¿Neon en Brasil? ¿Nubank
     en su lanzamiento? ¿Revolut en UK?

2. ANTI-FRAUDE DEL PROGRAMA DE REFERRAL:
   En Colombia, los programas de referral de fintech han sido explotados con:
   - Múltiples registros con documentos falsos o de terceros
   - "Granjas de referidos" coordinadas en redes sociales
   - SIM swapping para crear cuentas masivas
   Propón reglas anti-fraude específicas:
   - ¿Máximo de referidos por usuario por mes?
   - ¿Periodo de vigencia del incentivo?
   - ¿Requiere completar KYC + primera transacción real para cobrar?
   - ¿Cómo detectar patrones sospechosos con los datos disponibles?

3. CÁLCULO DEL CAC SOSTENIBLE:
   Para esto necesito que investigues benchmarks de:
   - LTV típico de un usuario de billetera digital en Colombia (en USD o COP/año)
   - Ratio LTV:CAC mínimo recomendado para fintech (típicamente 3:1)
   - CAC máximo que Nivo podría gastar por usuario adquirido vía referral
   - CAC máximo por canal orgánico (SEO, comunidades, partnerships)
   Ejemplo de referencia: si el LTV promedio es $60.000 COP/año y el ratio objetivo es 3:1,
   el CAC máximo es $20.000 COP por usuario.

4. CANALES DE ADQUISICIÓN ORGÁNICA ESPECÍFICOS PARA COLOMBIA:
   Para cada canal, dame: alcance estimado, costo, tiempo de implementación, ejemplos reales

   Canal A — SEO fintech Colombia:
   - ¿Qué términos busca la gente relacionados con billeteras digitales, seguridad, pagos?
   - ¿Cuánto tráfico orgánico tiene Nequi.com.co? ¿Qué palabras clave dominan?
   - ¿Cuál es el volumen de búsqueda mensual en Colombia para: "billetera digital segura",
     "alternativa a Nequi", "pagos digitales Colombia"?

   Canal B — Comunidades tech y emprendedores:
   - ¿Qué comunidades digitales activas hay en Colombia?
     (Meetup, Slack, Telegram, Discord de startups, Google Developers, Facebook groups)
   - ¿Cuáles tienen mayor concentración del usuario objetivo de Nivo?
   - Estrategia concreta de entrada: ¿contenido educativo? ¿demo? ¿patrocinio?

   Canal C — LinkedIn y creadores de contenido fintech:
   - Lista de 10-15 creadores de contenido colombianos sobre finanzas personales,
     tecnología o emprendimiento con más de 5.000 seguidores
   - ¿Qué tipo de colaboración funciona mejor: review, tutorial, caso de uso?

   Canal D — Universidades y gremios:
   - ¿Qué universidades colombianas tienen comunidades tech activas donde un producto
     como Nivo tendría adopción natural? (Uniandes, EAFIT, Nacional, Javeriana, Los Andes)
   - ¿Qué gremios de freelancers o trabajadores independientes existen en Colombia?
     (Colombia Fintech, Asobancaria, CCCEP, gremios sectoriales)

5. DISEÑO DEL SCHEMA EN BD PARA EL PROGRAMA DE REFERRAL:
   Propón la estructura de tablas que necesitaríamos en PostgreSQL para rastrear el programa.
   Mínimo debe soportar:
   - Quién invitó a quién (referrer_id → referred_id)
   - Estado del referido (registrado, kyc_completo, primera_transacción_hecha, bono_pagado)
   - Monto del bono asignado y si ya se acreditó
   - Timestamp de cada evento para detectar patrones de fraude
   - Canal de referido (link único, código QR, etc.)

6. OKRs DE CRECIMIENTO PARA LOS PRIMEROS 90 DÍAS POST-LANZAMIENTO:
   Propón OKRs específicos, medibles y con referencias de benchmarks reales:
   - Objetivo 1: Usuarios registrados
   - Objetivo 2: Usuarios con KYC completo (tasa de conversión registro→KYC)
   - Objetivo 3: k-factor del referral (¿cuánto debe ser para ser sostenible?)
   - Objetivo 4: CAC por canal
   - Objetivo 5: Conversión FREE→PLUS en los primeros 90 días

FORMATO DE RESPUESTA:
1. Mecánica del referral recomendada con justificación
2. Reglas anti-fraude en bullets
3. Tabla de CAC sostenible con cálculo
4. Tabla de canales orgánicos con alcance, costo y priorización
5. Schema de BD para referral (SQL o pseudocódigo)
6. OKRs de crecimiento con valores objetivo y benchmarks de referencia
```

---

## T-12 — MoU con aliado bancario

```
CONTEXTO DEL NEGOCIO:
Soy co-fundador de Nivo, una startup fintech colombiana con criptografía post-cuántica.
Hoy operamos en modo no-custodial bajo Wompi (Bancolombia). Para crecer necesitamos:
1. Un aliado bancario formal que nos permita operar bajo su licencia mientras tramitamos
   nuestra propia licencia SEDPE
2. Un MoU (Memorando de Entendimiento) firmado que dé credibilidad institucional frente
   a inversionistas y potenciales clientes B2B
3. Acceso a APIs bancarias (ACH, dispersión, cuentas virtuales) para mejorar la experiencia

ESTADO ACTUAL DE NIVO:
- Producto: billetera digital con KYC biométrico, OTP por SMS, pagos P2P firmados con PQC
- Usuarios: pre-lanzamiento (target: agosto 2026)
- Tecnología: FastAPI + PostgreSQL + GCP + liboqs (ML-KEM-768, ML-DSA-65)
- Diferenciador: única billetera con criptografía post-cuántica NIST en Colombia/LATAM
- Capital: startup en etapa pre-seed, buscando primera ronda

POR QUÉ UN BANCO QUERRÍA ASOCIARSE CON NIVO:
- Acceso al segmento joven tech-savvy que los bancos tradicionales no están captando
- Diferenciador de seguridad PQC que el banco puede comunicar como parte de su narrativa
- Modelo de revenue share en transacciones
- Reducción de riesgo operacional (Nivo maneja la capa técnica, el banco aporta licencia)

LO QUE NECESITO QUE INVESTIGUES:

1. MAPEO DE BANCOS Y NEOBANCOS TARGET EN COLOMBIA:
   Para cada institución, investiga:
   - ¿Tiene programa activo de Banking-as-a-Service (BaaS) o API banking?
   - ¿Ha firmado MoUs o alianzas con otras fintechs? ¿Con cuáles?
   - ¿Cuál es su postura pública frente a fintechs (colaborativa o competitiva)?
   - ¿Quién es el decisor (Director de Innovación, VP Digital, Gerente de Alianzas)?
   - ¿Cuál es el tiempo típico de un proceso de alianza con esta institución?

   Instituciones a investigar:
   - Bancolombia (y su brazo fintech: Nequi, Movii)
   - Davivienda
   - Banco de Bogotá (Grupo Aval)
   - BBVA Colombia
   - Lulo Bank (100% digital, Grupo Aval)
   - iF Bank (Banco Pichincha Colombia)
   - Ualá Colombia (neobanco argentino con presencia en CO)
   - Nubank Colombia (si ya tiene presencia activa)
   - Bancamía, Confiar (bancos de nicho / cooperativas con apetito tech)

2. MODELO DE NEGOCIO DEL ACUERDO:
   Investiga cómo se estructuran típicamente estos acuerdos:
   - ¿Revenue share o fee fijo? ¿Porcentaje típico para el banco en acuerdos BaaS?
   - ¿El banco cobra por cuenta virtual creada, por transacción, por usuario activo?
   - ¿Qué le da el banco a la fintech exactamente? (licencia, APIs ACH, cuentas virtuales,
     soporte de compliance, mesa de dinero)
   - ¿Qué responsabilidades asume la fintech? (KYC, AML, soporte al usuario final)
   - Ejemplos de acuerdos públicos en Colombia o LATAM: Pomelo + bancos en LATAM,
     Treinta + Bancolombia, otras fintechs colombianas con sponsor bancario

3. ESTRUCTURA DEL MoU:
   Propón un índice detallado del MoU con las secciones que debe incluir:
   - Objeto del acuerdo
   - Definiciones (qué entiende cada parte por "usuario", "transacción", "incidente")
   - Obligaciones de Nivo
   - Obligaciones del banco
   - Modelo económico (revenue share o fee)
   - Protección de datos y compliance
   - SLAs técnicos de cada parte
   - Propiedad intelectual
   - Duración y terminación
   - Resolución de disputas

4. DUE DILIGENCE PACKET — LO QUE EL BANCO NOS VA A PEDIR:
   Investiga qué documentos exige típicamente un banco colombiano a una fintech
   antes de firmar un MoU. Lista mínima esperada:
   - Estructura legal y accionaria de la empresa
   - Certificados de constitución y RUT
   - Informe de auditoría técnica y de seguridad
   - Política de KYC/AML
   - Plan de negocio y proyecciones financieras
   - Información de los fundadores (hojas de vida, due diligence personal)
   - ¿Qué más?

5. ESTRATEGIA DE ACERCAMIENTO:
   Propón una secuencia de acciones concreta:
   - Semana 1: ¿Cómo identificar y contactar al decisor correcto en cada banco?
     (LinkedIn, eventos fintech, referidos, cold email)
   - Semana 2-3: ¿Cómo estructurar la reunión de exploración?
     ¿Qué mostrar? ¿Qué no revelar todavía?
   - Semana 4: ¿Cómo enviar el due diligence packet de manera profesional?
   - Semana 6-8: Negociación de términos — ¿qué ceder? ¿qué defender?
   - Eventos fintech en Colombia donde los bancos están presentes:
     Colombia Fintech Summit, ANIF Foro, eventos Asobancaria

6. NEOBANCOS COMO ALTERNATIVA MÁS ÁGIL:
   Los neobancos (Lulo, iF, Ualá) pueden ser más rápidos en decidir que la banca tradicional.
   Analiza:
   - ¿Algún neobanco colombiano tiene capacidad de ser sponsor bancario de otra fintech?
   - ¿O serían más bien competidores que potenciales aliados?
   - ¿Qué ofrece cada uno que podría complementar a Nivo?

FORMATO DE RESPUESTA:
1. Tabla de ranking de bancos por atractivo como aliado (prioridad de acercamiento)
2. Modelo de negocio típico del acuerdo BaaS con rangos de revenue share
3. Índice del MoU con descripción de cada sección
4. Lista del due diligence packet con descripción de cada documento
5. Plan de acercamiento semana a semana (cronograma de 8 semanas)
6. Análisis de neobancos: aliado vs. competidor
```

---

## T-13 — Métricas de negocio instrumentadas

```
CONTEXTO DEL NEGOCIO:
Soy co-fundador de Nivo, una billetera digital colombiana con criptografía post-cuántica.
El lanzamiento está planeado para agosto 2026. Antes de lanzar, necesitamos definir exactamente
qué vamos a medir y cómo, para poder operar con datos desde el día uno en lugar de navegar
a ciegas. El backend está en FastAPI + PostgreSQL + Redis + GCP.

CONTEXTO TÉCNICO DISPONIBLE:
- Backend: FastAPI con endpoints documentados (autenticación, pagos P2P, top-ups, KYC, crypto)
- Base de datos: PostgreSQL con tablas: users, wallets, transactions, partner_orders,
  otp_records, kyc_results, pqc_keys, webhook_event_logs
- Infra: GCP Cloud Run + Cloud SQL + Memorystore Redis + Cloud Logging
- Librerías ya en requirements.txt: opentelemetry-sdk, sentry-sdk (configurados parcialmente)

LO QUE NECESITO QUE INVESTIGUES:

1. MÉTRICAS DE NEGOCIO CANÓNICAS PARA FINTECH DE PAGOS:
   Define las métricas exactas que debe medir una billetera digital en etapa de lanzamiento.
   Para cada métrica dame: definición exacta, fórmula de cálculo, frecuencia de actualización,
   umbral de alerta (qué valor debe disparar una notificación), y en qué tabla de PostgreSQL
   está la fuente de datos.

   Métricas de volumen:
   - GMV (Gross Merchandise Volume) diario en COP
   - Número de transacciones P2P completadas (éxito vs. intento)
   - Número de top-ups procesados y monto total
   - Tasa de éxito de transacciones (completadas / iniciadas)

   Métricas de usuarios:
   - DAU (Daily Active Users), WAU, MAU
   - Nuevos registros por día
   - Conversión: registro → KYC completo → primera transacción
   - Churn mensual por plan (FREE, PLUS, PRO)
   - MRR (Monthly Recurring Revenue) por plan

   Métricas de KYC:
   - Tasa de aprobación KYC de Truora (aprobados / intentos)
   - Tiempo promedio de resolución de KYC (en minutos)
   - Motivos de rechazo más frecuentes (documento ilegible, liveness fail, datos inconsistentes)

   Métricas técnicas:
   - Latencia p50/p95/p99 por endpoint crítico
   - Error rate por endpoint (HTTP 4xx y 5xx)
   - Uptime semanal del servicio
   - Webhooks de Wompi: recibidos / procesados / fallidos

2. DISEÑO DE LA TABLA business_metrics_daily EN POSTGRESQL:
   Propón el schema SQL completo de una tabla que almacene un snapshot diario de las
   métricas de negocio. Debe ser calculada a medianoche por un job de agregación.
   La tabla debe permitir:
   - Comparar el día de hoy vs. el mismo día de la semana pasada
   - Detectar anomalías (caída > 30% en GMV)
   - Generar reportes por periodo

3. HERRAMIENTAS DE PRODUCT ANALYTICS — EVALUACIÓN:
   Evalúa estas opciones para el contexto de Nivo (startup colombiana, presupuesto limitado):
   - PostHog (open source, self-hosted o cloud)
   - Mixpanel (SaaS, pricing por eventos)
   - Amplitude (SaaS, pricing por usuarios)
   - Metabase (visualización sobre PostgreSQL propio, open source)
   - Google Looker Studio (gratuito, conectado a GCP)

   Para cada uno: precio real en 2025-2026, facilidad de integración con FastAPI,
   soporte para eventos custom, capacidad de análisis de funnels KYC.
   Recomendación: ¿cuál usar primero con < $100 USD/mes de presupuesto?

4. EVENTOS DE TRACKING EN LA APP MÓVIL:
   Propón la lista mínima de eventos que el frontend móvil (React Native o equivalente)
   debe enviar al backend o al sistema de analytics para medir el funnel de usuario:
   - screen_view (con nombre de pantalla)
   - Eventos de onboarding: registration_started, phone_verified, kyc_started,
     kyc_document_uploaded, kyc_selfie_taken, kyc_approved, kyc_rejected
   - Eventos de transacción: transfer_initiated, transfer_confirmed, transfer_completed,
     transfer_failed (con reason)
   - Eventos de plan: plan_upgrade_viewed, plan_upgrade_completed
   Para cada evento: nombre, propiedades que debe incluir, y para qué métrica sirve.

5. REPORTE AUTOMÁTICO DIARIO POR SLACK:
   Diseña el formato del mensaje de Slack que llegaría automáticamente cada mañana
   a las 8:00 AM con el resumen del día anterior. Debe ser legible en 30 segundos
   por alguien no técnico. Incluye:
   - Qué métricas mostrar
   - Formato del mensaje (texto plano, blocks de Slack, emojis de semáforo?)
   - Cómo manejar anomalías (si el GMV cayó >30%, el mensaje cambia?)

6. SISTEMA DE ALERTAS DE ANOMALÍAS:
   Define los umbrales de alerta que deben disparar una notificación inmediata en Slack:
   - GMV diario cae > 30% vs. promedio de los últimos 7 días
   - Tasa de éxito de transacciones cae < 90%
   - Tasa de aprobación KYC cae < 70% en las últimas 24 horas
   - Latencia p99 de un endpoint crítico supera 500ms
   - Error rate supera 1% en cualquier endpoint

   Para cada alerta: ¿quién debe ser notificado? ¿Con qué urgencia? ¿Qué acción inicial tomar?

7. DICCIONARIO DE DATOS:
   Para las 5 métricas más importantes, escribe la definición exacta y sin ambigüedad:
   - ¿Qué cuenta como "usuario activo"? ¿Login? ¿Transacción? ¿Cuál periodo?
   - ¿Qué cuenta como "transacción completada"? ¿Solo P2P o incluye top-ups?
   - ¿Cómo se calcula el GMV? ¿Se incluyen top-ups o solo P2P?
   - ¿Cómo se mide el churn? ¿Qué inactividad lo define?
   - ¿Cómo se calcula el MRR si hay planes anuales con descuento?

FORMATO DE RESPUESTA:
1. Tabla canónica de métricas con fórmulas, fuentes y umbrales de alerta
2. Schema SQL de business_metrics_daily
3. Tabla comparativa de herramientas de analytics con recomendación
4. Lista de eventos de tracking del frontend con propiedades
5. Plantilla del reporte diario de Slack (formato real, listo para implementar)
6. Tabla de alertas de anomalías con umbrales y responsables
7. Diccionario de datos de las 5 métricas principales
```

---

*Prompts generados el 2026-05-03 para el Sprint 2 de Nivo.*
*Cada prompt es autocontenido — incluye el contexto completo del negocio.*
*Usar con: Perplexity Deep Research, ChatGPT, Gemini Deep Research, Claude.ai.*
