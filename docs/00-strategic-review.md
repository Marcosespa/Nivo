# Memo Estrategico — Ruta Regulatoria-First
### Revision de idea, nombre y camino MVP para Colombia

**Version:** 1.0 | **Fecha:** Abril 2026 | **Clasificacion:** Confidencial

---

## 1. Nombre recomendado

**Recomendacion:** mantener **Nivo** como marca publica candidata, sujeta a busqueda formal de marca, dominios y redes.

**Por que mejora la idea:**
- Es corto, simple y facil de pronunciar en Colombia y LATAM.
- Suena futurista sin obligar al usuario a entender fisica cuantica.
- Funciona para B2C, comercios y API B2B: wallet, tarjetas, monedas, inversion, seguridad y compliance caben bajo la misma marca.
- Evita el problema de `QuantumPay`, que ya aparece usado por terceros en pagos y suena demasiado literal para una marca de consumo.
- Conecta con el nuevo activo de landing: `landing_page/nivo`.

**Uso interno inmediato:** mantener `Nivo` como nombre de producto y repositorio hasta hacer busqueda formal de marca, dominios y redes. Si legal confirma disponibilidad, consolidar todos los dominios, documentos y activos bajo Nivo.

---

## 2. Tesis ajustada: banco como destino, licencia por etapas

La idea principal de Nivo si debe ser bancaria: una app tipo Revolut para Colombia y LATAM, con pagos, ahorro, tarjeta, multi-moneda, inversiones, crypto y seguridad post-cuantica para todos. La diferencia es que no debe intentar operar todos esos productos con licencia propia desde el dia 1.

El camino mas rapido hacia ese banco digital es:

1. Lanzar primero una **experiencia bancaria quantum-safe** con infraestructura regulada por terceros.
2. No custodiar saldos propios hasta tener SEDPE, Certificado de Operacion Temporal, banco aliado o estructura legal equivalente.
3. Usar infraestructura regulada para mover dinero: Bre-B/PSE/ACH, banco aliado, emisor de tarjetas, proveedor KYC, broker, IMC y exchange/VASP cuando aplique.
4. Construir la diferenciacion propia donde si hay ventaja: UX, cifrado PQC, recibos firmados, antifraude, conciliacion, educacion financiera y confianza.
5. Preparar licencia SEDPE, COT o estructura de banco aliado como ruta de escala, no como condicion para validar el producto.

La pregunta que define todo es: **la app capta dinero de usuarios o solo orquesta pagos sobre terceros regulados?**

---

## 3. Decision regulatoria

### Si capta dinero

Si el producto guarda saldos propios de usuarios o recibe recursos del publico mediante depositos electronicos, entra en ruta SFC. La figura natural es SEDPE, con autorizacion, gobierno corporativo, capital, SARLAFT y supervision.

**Implicacion:** no prometer un wallet custodial publico sin abogado financiero, plan de autorizacion y presupuesto regulatorio.

### Si no capta dinero

Si el MVP solo inicia pagos, consulta cuentas, cifra recibos, firma transacciones y envia instrucciones a pasarelas/bancos/aliados, puede moverse mas rapido como capa tecnologica o agregador/middleware. Eso no elimina compliance: desde el dia 1 debe existir KYC proporcional, monitoreo AML/LAFT, terminos claros y trazabilidad.

**Decision de producto:** el MVP queda en modo **sin captacion directa**, pero la arquitectura, marca y producto se disenan como el primer paso hacia un neobanco completo.

---

## 4. Producto MVP

**Primer producto:** cuenta Nivo con pagos, cobros simples, recibos verificables y blindaje cuantico visible, pero sin balance custodial propio mientras no exista cobertura regulatoria.

**Stack de aliados:**
- **PSE/ACH Colombia:** recargas, pagos y retiros hacia cuentas existentes.
- **Truora, MetaMap o Jumio:** verificacion KYC y biometria.
- **Pomelo, Dock, Visa/Mastercard o Adyen:** tarjeta virtual sin emitir como banco desde cero.
- **Open Finance Colombia:** conectar cuentas existentes mediante APIs reguladas cuando este disponible para el caso de uso.

**Diferenciador que si construimos:**
- TLS hibrido con ML-KEM-768 cuando la infraestructura lo permita.
- Firmas ML-DSA-65 en recibos y transacciones.
- Recibos verificables para usuarios, comercios y clientes B2B.
- "Proteccion cuantica activa" como parte de la experiencia diaria, no solo como claim enterprise.
- API PQC para fintechs pequenas que no tienen equipo criptografico propio.

---

## 5. Vision Revolut-like

El objetivo de producto es parecerse a Revolut en experiencia: una sola app para mover, cambiar, invertir y proteger dinero. La diferencia es que en Colombia cada modulo debe tener un responsable regulatorio claro.

| Modulo | Momento | Como lanzarlo sin romper compliance |
|--------|---------|--------------------------------------|
| Cuenta y pagos | MVP | Bre-B/PSE/ACH/banco aliado; Nivo firma, concilia y muestra recibos verificables |
| Bolsillos de ahorro | MVP/mes 5+ | Si no hay custodia propia, son metas visuales o subcuentas del aliado; con SEDPE/banco aliado pueden ser saldos reales |
| Tarjeta virtual | Mes 6+ | Pomelo, Dock, Adyen o emisor equivalente; Nivo usa tokens, no PAN/CVV |
| Multi-moneda COP/USD/EUR | Mes 9+ | Aliado IMC/banco/pasarela cambiaria; Nivo muestra precio, firma orden y concilia |
| Crypto compra/venta | Piloto cerrado/Ano 2 | Exchange/VASP aliado, cuenta separada, disclosure de riesgo, sin prometer rendimiento ni usar crypto como deposito |
| Acciones/ETFs | Piloto cerrado/Ano 2 | Broker/comisionista regulado o broker internacional validado legalmente; Nivo no da asesoria de inversion |
| Finanzas personales | Desde MVP | Clasificacion, alertas, presupuesto y reportes, sin tocar actividad vigilada adicional |

**Regla:** Nivo puede ser la interfaz, la capa PQC, el sistema de recibos y el sistema operativo financiero del usuario. El partner debe ser el banco, SEDPE, broker, exchange, IMC, emisor o entidad responsable cuando el modulo toque valores, cripto, divisas o custodia hasta que Nivo tenga licencia propia.

---

## 6. Mercado y primeros clientes

El mercado colombiano ya esta educado en billeteras digitales. La oportunidad no es explicar que es una billetera; es convencer a un nicho inicial de que seguridad, privacidad y multi-moneda importan.

### Meses 1-3: primeros 100 usuarios

**Canal principal:** comunidad, no pauta.

- Colombianos en el exterior que manejan COP/EUR/USD, remesas o pagos familiares.
- Freelancers, emprendedores y nomadas digitales colombianos.
- Grupos de WhatsApp, Telegram, LinkedIn y comunidades fintech/tech.
- Referidos: 0% de comision o Plus gratis por 3 meses si invitan 3 contactos activos.

### Meses 4-6: primeros 1.000 usuarios

- Pymes digitales y freelancers que cobran en USD/EUR y necesitan recibir en COP.
- Colombia Fintech como red institucional y canal de credibilidad.
- Contenido educativo en LinkedIn/TikTok: PQC en lenguaje simple, no papers.
- Pymes exportadoras pequenas que necesitan trazabilidad para clientes europeos.
- Sectores salud/legal donde confidencialidad y auditoria pesan mas que cashback.

### Mes 7+: escala B2B

- Vender API PQC a fintechs pequenas y medianas.
- Pilotos con bancos medianos y proveedores de pagos.
- Alianzas con emisores o BaaS para tarjeta virtual.

---

## 7. Hoja de ruta ejecutiva

| Etapa | Accion | Tiempo | Criterio de validacion |
|-------|--------|--------|------------------------|
| Validacion legal | Definir con abogado si el MVP no capta dinero y que permisos necesita | Mes 1 | Memo legal aprobado |
| Producto | MVP P2P sin custodia + KYC + recibo ML-DSA | Mes 2-4 | 100 usuarios reales |
| Regulacion | Conversacion SFC/Sandbox si el producto toca actividad vigilada | Mes 1-4 | Ruta COT, aliado o no-captacion definida |
| Primeros usuarios | Red personal + comunidades colombianas en exterior | Mes 3-5 | 1.000 transacciones sin incidentes |
| Monetizacion | Tarjeta virtual con aliado + API PQC B2B | Mes 6-9 | Primer ingreso recurrente |
| Multi-moneda | FX COP/USD/EUR con aliado IMC/banco | Mes 9-12 | Spread/fee validado sin reclamos |
| Inversiones | Crypto y acciones via partners separados | Ano 2 | Licencias/contratos/disclosures aprobados |
| Escala | SEDPE formal o banco aliado + Peru/Ecuador | Ano 2 | Unit economics y compliance listos |

---

## 8. Los 6 problemas serios y como superarlos

### Problema 1: laberinto regulatorio colombiano

La SFC exige autorizacion si la app capta dinero de usuarios. La licencia SEDPE puede tardar mas de 12 meses y consumir una parte importante del runway entre abogados, tramites, capital y auditorias. Ademas, pagos inmediatos y finanzas abiertas siguen madurando, asi que el producto no puede depender de que todo el ecosistema este listo.

**Como superarlo:** empezar sin licencia propia, con MVP sin captacion directa, Sandbox/COT solo si aplica, y una SEDPE/banco aliado como infraestructura financiera. Movii, Tpaga u otra entidad regulada pueden ser evaluadas como partner; Nivo pone frontend, UX, cifrado PQC y recibos.

### Problema 2: PQC puede ralentizar transacciones

ML-KEM y ML-DSA usan llaves y firmas mas grandes que ECC/ECDSA. En moviles gama media y redes 3G/4G inestables, eso puede afectar memoria, latencia y tasa de abandono.

**Como superarlo:** usar PQC de forma selectiva e hibrida: datos de larga vida, tokens de identidad, recibos y transacciones firmadas; mantener sesiones, cache TLS y fallback clasico donde el riesgo sea efimero. Optimizar serializacion, reusar sesiones y medir p95/p99 en dispositivos reales.

### Problema 3: nadie entiende ni le importa PQC

El usuario final no compra algoritmos. Compra tranquilidad, privacidad y confianza.

**Como superarlo:** marketing B2C sin jerga. Mensaje: "tus datos de hoy siguen protegidos en 10 anos". PQC se reserva para B2B, bancos, salud, legal y clientes que si valoran certificacion tecnica.

### Problema 4: competir contra Nequi, Daviplata y Bancolombia

Competir por pagos basicos contra jugadores con millones de usuarios es caro y lento.

**Como superarlo:** atacar nichos desatendidos: freelancers y nomadas que cobran en USD/EUR, pymes exportadoras, salud/legal, y usuarios con necesidad real de multi-moneda + privacidad + trazabilidad.

### Problema 5: fraude y robo de identidad

KYC debil, SIM swapping, phishing y fraude en pagos inmediatos pueden destruir la confianza de una billetera nueva.

**Como superarlo:** KYC biometrico desde dia 1, anomaly detection en tiempo real, limites progresivos, device fingerprinting, step-up authentication y firmas ML-DSA para recibos/ordenes irrepudiables.

### Problema 6: financiacion y runway

PQC, KYC, pasarelas, auditorias y compliance cuestan antes de que B2C pague suficiente.

**Como superarlo:** correr tres vias en paralelo: iNNpulsa/Apps.co/Ruta N, angeles LATAM via Colombia Fintech, y revenue B2B desde mes 6 vendiendo API PQC antes de escalar el B2C.

| Fuente | Monto estimado | Como acceder |
|--------|----------------|--------------|
| iNNpulsa Colombia | COP $50M-$200M | Convocatorias de innovacion tecnologica |
| Ruta N / Apps.co | COP $20M-$100M | Aceleradoras y programas estatales |
| Angeles LATAM | USD $50K-$200K | Red Colombia Fintech, founders y angels fintech |
| Revenue B2B | Desde mes 6 | API PQC, auditorias y pilotos pagados |

---

## 9. Riesgos de la idea

| Riesgo | Lectura actual | Mitigacion |
|--------|----------------|------------|
| Regulacion por captacion | Alto si se guarda saldo propio | MVP sin custodia; aliado regulado; abogado desde mes 1 |
| PQC como mensaje demasiado tecnico | Alto en B2C masivo | Traducir a "recibos verificables" y "proteccion de largo plazo" |
| Competir contra Nequi por habito | Alto | Nicho inicial: exterior, freelancers, pymes digitales |
| Nombres similares en pagos | Medio/alto | Validar Nivo y abandonar QuantumPay u otros nombres demasiado cercanos a pagos genéricos |
| Costos PCI/tarjeta | Medio | Tarjeta virtual via emisor/BaaS, no manejo directo de PAN |
| Crypto/acciones dentro de la misma app | Alto regulatoriamente | Modulos separados con partner responsable, disclosures y sin asesoria |

---

## 10. Fuentes verificadas

- SFC, concepto SEDPE sobre captacion mediante depositos electronicos: https://www.superfinanciera.gov.co/publicaciones/10087941/sedpe-captacion-exclusiva-mediante-depositos-electronicos-10087941/
- Decreto 1234 de 2020, espacio controlado de prueba y Certificado de Operacion Temporal: https://www.funcionpublica.gov.co/eva/gestornormativo/norma_pdf.php?i=142005
- SFC, concepto sobre pasarelas de pago y politicas AML/LAFT: https://www.superfinanciera.gov.co/publicaciones/10098492/normativanormativa-generalboletin-juridico-superintendencia-financieraboletin-juridico-numero-otros-conceptos-sintesis-10098492/
- Ministerio de Hacienda, Decreto 0368 de 2026 sobre Sistema de Finanzas Abiertas: https://www.minhacienda.gov.co/decretos-2026/-/document_library/eryu/view_file/3171602
- SFC laArenera, piloto cash-in/cash-out con plataformas de criptoactivos: https://www.superfinanciera.gov.co/publicaciones/10107301/innovasfcpruebas-en-el-sandbox-10107301/
- NIST FIPS 203/204/205, estandares PQC finales publicados en agosto de 2024: https://csrc.nist.gov/pubs/fips/203/final
- Open Quantum Safe liboqs: https://openquantumsafe.org/liboqs/
- PSE, pagos seguros en linea: https://www.pse.com.co/
