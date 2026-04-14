# Go-to-Market & Análisis Competitivo — Nivo

**Versión:** 1.0 | **Fecha:** Abril 2026

---

## 1. Análisis Competitivo

### Competidores directos (billeteras digitales Colombia)

| Billetera | Usuarios | Respaldo | PQC | Debilidad que explotamos |
|-----------|---------|---------|-----|------------------------|
| Nequi | 18M+ | Bancolombia | ❌ RSA/ECC | Sin seguridad cuántica, UX compleja para pagos rápidos |
| Daviplata | 12M+ | Davivienda | ❌ RSA/ECC | Sin tarjeta virtual, sin multi-moneda |
| Bancolombia App | 9M+ | Bancolombia | ❌ (estudiando) | Legacy bancario, no fintech-first |
| Rappipay | 3M+ | Rappi + Davivienda | ❌ | Dependiente del ecosistema Rappi |
| **Nivo** | 0 → 50K meta | Bootstrap | ✅ ML-KEM-768 | Primera mover en PQC |

### Competidores en PQC (no billeteras)

| Empresa | País | Foco | Relación con Nivo |
|---------|------|------|----------------------|
| Ankatech | Colombia | B2B bancos | Posible aliado o validador del mercado |
| Cyte | Colombia | B2B empresas | Posible aliado técnico o competidor en API B2B |
| PQShield | UK | Chips/hardware PQC | No competidor directo — ecosistema |
| ISARA | Canadá | Consultoría PQC | Competidor en consultoría enterprise |

### Ventana de diferenciación

Ankatech ya está convenciendo al primer banco colombiano de adoptar PQC en 2025. Esto valida que el mercado existe. La diferencia: Ankatech es B2B puro. Nosotros llegamos al usuario final Y vendemos B2B. El usuario final es nuestra prueba de concepto en producción más poderosa.

---

## 2. Estrategia Go-to-Market

### Fase 1 — Primeros 100 usuarios: comunidad antes que pauta (Mes 1–3)

**Canal:** red personal, colombianos en el exterior, freelancers, emprendedores y comunidades tech/fintech.

**Mensajes:**
- "Tus datos de hoy siguen protegidos en 10 años"
- "Una app para mover, cambiar y proteger tu dinero"
- "Recibos verificables para mover plata entre países sin perder trazabilidad"

**Tácticas:**
- Lista beta cerrada desde red de colombianos en Praga/Europa y familias en Colombia
- Grupos de WhatsApp/Telegram de freelancers, nómadas digitales y emprendedores colombianos
- Referidos: 0% de comisión o Plus gratis por 3 meses si invitan 3 contactos activos
- Presencia en meetups de ciberseguridad en Bogotá/Medellín (OWASP, ISACA Colombia)
- AMA (Ask Me Anything) en comunidades de FinTech Colombia y CriptoX

**KPI:** 100 usuarios activos, 300 transacciones firmadas, NPS > 50

---

### Fase 2 — Primeros 1.000 usuarios: freelancers y pymes digitales (Mes 4–6)

**Canal:** comunidades profesionales + gremio fintech + contenido educativo.

**Mensajes simplificados para público general:**
- "Paga, cambia y controla tu plata desde una sola app"
- "Privacidad y trazabilidad para quienes cobran fuera y viven en Colombia"
- Evitar jerga técnica: PQC se menciona solo en contenido B2B, compliance, salud/legal y pitch técnico

**Tácticas:**
- Ofrecer cobro en USD/EUR y recepción en COP mediante aliados cuando el flujo esté habilitado
- Inscribirse o participar activamente en Colombia Fintech para red, eventos y credibilidad
- Contenido educativo en LinkedIn/TikTok: privacidad, fraude, multi-moneda y recibos verificables
- Programa de referidos masivo: $5,000 COP por cada amigo que se una y haga su primer pago
- Influencer marketing: finanzas personales + tech (TikTok, YouTube Colombia)
- PR en medios: Semana, Portafolio, El Tiempo Economía — ángulo de "la startup colombiana que está un paso adelante"
- Alianza con Platzi: "Curso gratis de finanzas digitales" patrocinado por Nivo
- Participación en Colombia Fintech Summit y Campus Party Colombia
- Waitlist separada para multi-moneda, crypto y acciones, sin prometer fecha hasta tener partner legal

**KPI:** 1,000 usuarios activos, 1,000 transacciones firmadas, primeras pymes/freelancers recurrentes

---

### Fase 3 — Escala B2B (Mes 7+)

**Canal:** Ventas directas + events + partnerships

**Target empresas:**
1. Fintechs colombianas con producto existente (Addi, Bold, Lulo Bank)
2. Bancos medianos (Banco Popular, Itaú Colombia, Banco Falabella)
3. Gobierno (MinTIC, SENA, agencias con datos críticos)
4. Empresas aseguradoras (Sura, Bolívar)

**Tácticas:**
- Demo en vivo: "Tu sistema actual vs. sistema con Nivo API — en 15 minutos"
- Caso de estudio vivo: "Nivo procesa X transacciones/día con PQC. Tu banco puede hacer lo mismo."
- Contacto directo con CTOs en LinkedIn con propuesta de piloto gratuito (1 mes)
- Colombia Fintech Forum + Asobancaria: participación activa
- Oferta API para fintechs pequeñas: ML-KEM/ML-DSA sin contratar equipo criptográfico propio
- Alianza con Pomelo, Dock o Adyen para tarjeta virtual sin ser banco
- Alianza con IMC/banco para FX y con broker/exchange para módulos tipo Revolut

---

## 3. Aliados Estratégicos

| Aliado | Por qué | Cómo activarlo |
|--------|---------|---------------|
| **Bancolombia** | 12M usuarios, están estudiando PQC internamente. Un acuerdo de licenciamiento vale más que todos nuestros usuarios B2C en año 1. | Primer contacto Mes 6 con deck técnico + demo live. Proponer piloto de 90 días. |
| **iNNpulsa Colombia** | Financiamiento no dilutivo para startups colombianas. Ideal para cubrir costos de regulación y auditoría. | Aplicar en Mes 1 al Fondo iNNpulsa Mipymes Innovadoras. |
| **Cloudflare for Startups** | Programa gratuito para startups: $50K en créditos. Credibilidad técnica PQC (ya usan ML-KEM en prod). | Aplicar en Mes 1. Usar logo "Powered by Cloudflare" en credenciales de seguridad. |
| **GCP for Startups** | Hasta $200K en créditos. Infraestructura en Colombia (São Paulo = latencia ~30ms). | Aplicar via Google for Startups en Mes 1. |
| **Mastercard / Visa** | Tarjeta virtual — habilita revenue de interchange y diferenciación de producto. | Contacto via Pomelo o Dock (BaaS LATAM) como intermediarios. |
| **Truora** | KYC automatizado para Colombia. Ya tienen integración con la Registraduría. | Negociar pricing startup en Mes 1, integrar en Mes 2. |
| **Ankatech** | Startup PQC colombiana — validadores del mercado. Posible co-marketing o referidos B2B. | Contacto directo con fundadores, evaluar alianza no competitiva. |

---

## 4. Posicionamiento de Marca

### Nombre recomendado: Nivo

**Decisión:** `Nivo` queda como codename técnico. La marca pública recomendada es **Nivo**, sujeta a búsqueda legal de marca, dominios y redes.

**Por qué Nivo es más fuerte:**
- Es corto, memorable y fácil de pronunciar en Colombia y LATAM
- Suena a "nuevo nivel", con una sensación futurista sin ser técnico
- Funciona para usuario final, comercios, multi-moneda, inversión y API B2B
- Es más fácil de explicar: "tu plata, en otro nivel"
- Conecta con el proyecto de landing actualizado (`LANDING PAGE/nivo`)
- Evita la cercanía con `QuantumPay`, que ya aparece usado por terceros en pagos

**Alternativas consideradas y rechazadas:**
- ~~BastionPay~~ — comunica seguridad, pero es más largo y menos cotidiano para consumo masivo
- ~~QuantoBank~~ — connota banco, regulación más pesada
- ~~PQPay~~ — demasiado técnico
- ~~CuánticoPay~~ — español, limita expansión internacional
- ~~ShieldPay~~ — nombre genérico, sin diferenciación cuántica
- ~~QuantumPay~~ — conflicto de nombre en pagos; demasiado literal
- ~~Nivo~~ — buen codename, pero cercano a QuantumPay y menos claro para usuarios no técnicos

### Paleta de marca
- **Primario:** Sky Blue (#38BDF8) — tecnología, futuro, cielo digital
- **Fondo:** Slate 950 (#0B1120) — oscuridad del cosmos cuántico
- **Acento:** Sky 300 (#7DD3FC) — glow cuántico
- **Tipografía:** Inter o Geist — moderna, técnica, legible

### Taglines por segmento
- **B2C:** *"Tu plata, blindada para siempre"*
- **Comercios:** *"Cobra con la tecnología del futuro"*
- **B2B:** *"PQC-as-a-Service para el sistema financiero"*
- **General:** *"Quantum-safe · Colombia"*

---

*Revisar estrategia GTM trimestral con datos de métricas reales.*
