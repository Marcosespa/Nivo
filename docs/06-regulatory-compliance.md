# Regulación & Compliance — Nivo
### SFC · UIAF · SIC · AML/LAFT · KYC · PCI-DSS · NIST PQC Standards

**Versión:** 1.0 | **Fecha:** Abril 2026 | **DISCLAIMER:** Este documento es orientativo. Todo lo relacionado con regulación debe ser revisado y validado por un abogado especializado en derecho financiero colombiano.

---

## 1. Marco Regulatorio Colombiano

### Entidades reguladoras relevantes

| Entidad | Rol | Relevancia para Nivo |
|---------|-----|--------------------------|
| **SFC** (Superintendencia Financiera) | Inspección, vigilancia y control financiero | SEDPE, Sandbox/COT, finanzas abiertas, protección al consumidor financiero |
| **UIAF** (Unidad de Información y Análisis Financiero) | AML/LAFT | Reporte de operaciones sospechosas cuando aplique |
| **SIC** (Superintendencia de Industria y Comercio) | Datos personales y consumidor | Ley 1581 de 2012, habeas data, tratamiento de datos |
| **Ministerio de Hacienda** | Política y decretos financieros | Decreto 2555, SEDPE, finanzas abiertas |
| **Registraduría** | Identidad | Verificación KYC de documentos colombianos |

### Decisión crítica: captación vs. middleware

La primera pregunta legal no es técnica: **¿Nivo captará dinero de usuarios?**

| Respuesta | Lectura regulatoria | Decisión MVP |
|-----------|---------------------|--------------|
| **Sí, guarda saldo propio** | Ruta SFC como SEDPE o entidad vigilada equivalente; requiere autorización, capital, gobierno corporativo, SARLAFT completo y supervisión. | No para MVP público. Preparar solo como ruta de escala. |
| **No, solo orquesta pagos sobre terceros** | Puede operar como capa tecnológica, agregador/middleware o proveedor de servicios a una entidad regulada, sujeto a contratos, AML/LAFT proporcional, datos personales y consumidor. | Ruta recomendada para MVP. |
| **Prueba actividad vigilada innovadora** | Evaluar Sandbox SFC / Certificado de Operación Temporal (COT). | Aplicar solo si el abogado confirma que el caso toca actividad vigilada. |

La SFC ha señalado que las SEDPE captan recursos del público exclusivamente mediante depósitos electrónicos y son instituciones financieras vigiladas. Por eso el MVP no debe prometer saldos custodiales propios hasta tener ruta SEDPE, COT o banco aliado.

### Modalidades de operación

**Opción A: Middleware financiero sin captación directa (recomendada para MVP)**
- Nivo no recibe ni mantiene fondos del público en cuentas propias.
- El dinero se mueve por PSE/ACH, pasarela, banco aliado o proveedor regulado.
- La app muestra estados, recibos, conciliación y firmas PQC; el saldo legal vive en el tercero regulado.
- Requiere contratos robustos, KYC proporcional, AML/LAFT, protección de datos y términos transparentes.

**Opción B: Banco/SEDPE/entidad vigilada aliada**
- Operar bajo el paraguas regulatorio de un banco socio (ej: Bancolombia, Lulo Bank)
- Nivo provee la tecnología, el banco provee la licencia
- Más rápido de implementar, menor riesgo regulatorio inicial
- Menor autonomía de producto en el corto plazo

**Opción C: Sandbox SFC / Certificado de Operación Temporal**
- Permite probar desarrollos tecnológicos innovadores en actividades propias de entidades vigiladas, bajo condiciones definidas por la SFC.
- El COT puede durar hasta 2 años y exige plan de prueba, plan de transición/desmonte, consumidores máximos, montos máximos si hay captación y medidas AML/LAFT.
- No asumir aprobación automática ni plazo fijo de respuesta. El abogado debe preparar solicitud y conversación previa con SFC.

**Opción D: Licencia SEDPE formal**
- Ruta para custodiar depósitos electrónicos y hacer pagos/traspasos como institución financiera.
- Probablemente toma más de un año entre estructuración legal, capital, autorización, auditorías, cumplimiento y puesta en marcha.
- Debe activarse cuando haya tracción, unit economics y funding suficiente.

---

## 2. Compliance AML/LAFT

### Obligaciones

Nivo debe implementar prevención AML/LAFT desde el primer día. El nivel formal depende de la modalidad:

- **Si es SEDPE o entidad vigilada:** aplica SARLAFT completo según la regulación de la SFC.
- **Si opera como pasarela, agregador o middleware:** no debe asumirse SARLAFT completo por defecto, pero sí políticas y procedimientos mínimos de prevención y control de LA/FT, KYC, monitoreo, reportes contractuales y trazabilidad.
- **Si trabaja con banco/SEDPE aliado:** debe heredar controles contractuales del aliado y entregar logs/auditoría en formato usable.

**Requerimientos:**
- Designar responsable interno de cumplimiento desde el MVP
- Implementar sistema de monitoreo de transacciones inusuales
- Reportar operaciones sospechosas a la UIAF cuando el marco aplicable lo exija
- Políticas de Conocimiento del Cliente (KYC) documentadas
- Conservar registros de transacciones y evidencia de verificación según contrato y norma aplicable

**Implementación técnica:**
- Motor de reglas AML integrado en el flujo de pagos
- Alertas automáticas por: montos inusuales, frecuencia anormal, patrones de layering
- Controles antifraude para pagos inmediatos/Bre-B cuando se integre: límites progresivos, device fingerprinting, detección de SIM swap, velocity rules y step-up authentication
- Reporte exportable para UIAF/aliado regulado cuando corresponda
- Logs inmutables de transacciones (facilitado por firmas ML-DSA-65)

---

## 3. KYC (Know Your Customer)

### Niveles de verificación

| Nivel | Verificación | Límites | Tiempo onboarding |
|-------|-------------|---------|------------------|
| Básico | Número celular + cédula | $500K COP/día | < 2 min |
| Intermedio | Básico + selfie + validación Registraduría | $5M COP/día | < 5 min |
| Completo | Intermedio + comprobante de ingresos | $50M COP/día | < 24 horas |

### Proveedores KYC candidatos

**Truora (preferido para Colombia MVP):**
- Integración con Registraduría, Migración y listas negras internacionales
- Verificación biométrica (selfie vs. foto cédula)
- API REST, documentada, con SDK para Colombia
- Tiempo de respuesta: 30–60 segundos para verificación básica
- Costo estimado: $0.8–$1.5 USD por verificación

**Alternativas a evaluar:**
- MetaMap: cobertura LATAM, flujos configurables, útil si expansión regional pesa desde temprano
- Jumio: proveedor global, mayor costo probable, fuerte para compliance enterprise

**Decisión MVP:** integrar un proveedor externo; no construir KYC propio.

### Retención de datos KYC

Los documentos KYC se almacenan cifrados con AES-256-GCM (llave derivada híbrida PQC + X25519). Los metadatos de identidad se almacenan en PostgreSQL. Los documentos físicos (fotos, PDFs) se almacenan en GCP Cloud Storage con cifrado en reposo.

---

## 4. Privacidad de Datos (Ley 1581 de 2012)

### Obligaciones

Colombia tiene la Ley Estatutaria 1581 de 2012 de Protección de Datos Personales:
- Registro ante SIC como responsable del tratamiento de datos
- Política de privacidad publicada y accesible
- Consentimiento explícito del usuario para tratamiento de datos
- Derecho al olvido: proceso para eliminar datos a solicitud del usuario
- Transferencia internacional de datos: solo a países con nivel adecuado de protección

**Implementación:**
- Política de privacidad en lenguaje claro (no legalese)
- Pantalla de consentimiento en onboarding con opt-in explícito
- Dashboard de usuario con control de sus datos
- Proceso de eliminación de cuenta en < 30 días

---

## 5. PCI-DSS y tarjeta virtual

Si Nivo ofrece tarjeta virtual, la decisión de arquitectura debe minimizar el alcance PCI-DSS:

- No almacenar PAN, CVV ni datos sensibles de autenticación de tarjeta en infraestructura propia.
- Usar Pomelo, Dock, Adyen, Visa/Mastercard u otro emisor/procesador que tokenice y custodie los datos de tarjeta.
- Guardar solo tokens, últimos 4 dígitos, marca, estado y referencias del proveedor.
- Segmentar el entorno de pagos y documentar el flujo de datos antes de lanzar tarjeta.
- Exigir attestation/compliance del proveedor y revisar responsabilidades compartidas.

**Decisión MVP:** tarjeta virtual solo mediante proveedor BaaS/emisor; Nivo no toca datos sensibles de tarjeta.

---

## 6. Finanzas Abiertas Colombia

La SFC y el Ministerio de Hacienda avanzan en el Sistema de Finanzas Abiertas. Para Nivo esto permite conectar cuentas bancarias existentes sin convertirse en banco desde el día 1.

**Casos de uso relevantes:**
- Consulta autorizada de cuentas para UX multi-banco.
- Iniciación o preparación de pagos cuando el marco y los aliados lo permitan.
- Scoring alternativo y prevención de fraude con consentimiento explícito.
- Conciliación de recargas/retiros sin custodiar saldo propio.

**Decisión MVP:** diseñar la arquitectura con conectores Open Finance, pero no depender de que todas las APIs estén maduras para lanzar.

---

## 7. Cambio de divisas y multi-moneda

El módulo COP/USD/EUR debe tratarse como producto cambiario, no como simple conversión interna de una base de datos.

**Regla de lanzamiento:**
- Nivo no actúa como Intermediario del Mercado Cambiario (IMC) propio en el MVP.
- La ejecución de cambio se hace vía banco, IMC, pasarela autorizada o partner cambiario validado por abogado.
- La app puede mostrar cotización, fee/spread, orden firmada, recibo y conciliación.
- Debe quedar claro si el saldo multi-moneda es balance real en partner, dinero electrónico, cuenta bancaria, o solo vista informativa.
- Se deben guardar tasa, timestamp, spread, partner, aceptación del usuario y comprobante ML-DSA.

**Decisión:** FX va después de P2P/KYC/tarjeta, no antes.

---

## 8. Acciones, ETFs y valores

Comprar y vender acciones desde la app toca regulación del mercado de valores. En Colombia, la intermediación de valores y la asesoría de inversión requieren actores autorizados, registros y controles específicos.

**Regla de lanzamiento:**
- Nivo no será broker/comisionista en el MVP.
- Acciones/ETFs se ofrecen solo con broker partner o comisionista autorizado.
- Nivo no da recomendaciones, rankings personalizados ni asesoría de inversión salvo que exista licencia/partner que lo cubra.
- Todas las órdenes deben incluir disclosure de riesgo, idoneidad/appropriateness cuando aplique, trazabilidad y firma ML-DSA.
- El portafolio mostrado en app es snapshot del partner; el broker es book of record.
- Cualquier agente automatizado de portafolio queda fuera del MVP: solo puede probarse en simulación o piloto cerrado, con consentimiento explícito, límites de pérdida, disclosure de que puede perder dinero y partner/licencia que cubra asesoría o gestión automatizada.

**Decisión:** acciones/ETFs son módulo Año 2+, posterior a contrato legal y due diligence del broker.

---

## 9. Criptoactivos

Crypto puede ser parte de la experiencia tipo Revolut, pero debe vivir separado del saldo de pagos. La SFC ha usado laArenera para pilotos de cash-in/cash-out con plataformas de criptoactivos y entidades financieras, lo cual valida que el tema existe, pero no equivale a autorización general para operar exchange propio.

**Regla de lanzamiento:**
- Nivo no custodia criptoactivos directamente en el MVP.
- Compra/venta se hace vía exchange/VASP aliado, con cuenta separada y disclosure explícito de volatilidad, pérdida total, irreversibilidad y ausencia de garantía estatal.
- No usar crypto como depósito electrónico, saldo transaccional principal ni promesa de rendimiento.
- AML reforzado: listas, monitoreo de wallets si aplica, límites, travel-rule readiness, device fingerprinting, velocity limits y revisión manual de alertas.
- No lanzar staking, lending, derivados, apalancamiento ni stablecoin-yield.

**Decisión:** crypto entra solo como piloto cerrado o módulo Año 2, cuando existan partner, abogado y matriz AML aprobados.

---

## 10. Estándares PQC — NIST

### Estándares implementados

| Estándar | Algoritmo | Estado | Uso en Nivo |
|---------|---------|--------|-----------------|
| NIST FIPS 203 | ML-KEM-768 | **Finalizado Agosto 2024** | Key exchange en todos los handshakes |
| NIST FIPS 204 | ML-DSA-65 | **Finalizado Agosto 2024** | Firma de transacciones |
| NIST FIPS 205 | SLH-DSA | Finalizado Agosto 2024 | Reservado para certificados de larga duración |

### Crypto-Agilidad

El módulo `CryptoService` está diseñado para cambiar de algoritmo sin modificar el resto de la aplicación. Si NIST depreca algún algoritmo (como ocurrió con NTRU), Nivo puede migrar en días, no meses. Esta flexibilidad es parte del pitch a clientes enterprise.

---

## 11. Auditoría de Seguridad

### Plan de auditoría (Mes 8)

**Alcance:**
- Revisión completa del módulo `CryptoService`
- Penetration testing del API (OWASP Top 10 + pagos)
- Revisión de implementación PQC vs. FIPS 203/204
- Auditoría de gestión de secretos (llaves privadas, JWT secrets)
- Revisión de cumplimiento AML/LAFT

**Proveedores candidatos:**
- Fluid Attacks (Colombia) — penetration testing
- BDO Colombia — auditoría financiera y compliance
- NCC Group (internacional) — revisión criptográfica PQC

**Presupuesto estimado:** USD $15,000–$35,000

**Resultado esperado:** Certificado de seguridad utilizable en pitch a clientes enterprise y bancos.

---

## 12. Checklist Regulatorio — Mes 1

- [ ] Contratar abogado especializado en SFC/SIC/fintech colombiano
- [ ] Definir por escrito si el MVP opera sin captación directa
- [ ] Constituir Nivo SAS con objeto social apropiado para tecnología financiera y servicios cripto/PQC
- [ ] Iniciar proceso de registro ante SIC (tratamiento de datos)
- [ ] Redactar política de privacidad y términos de servicio
- [ ] Preparar memo legal: middleware, banco aliado, COT o SEDPE
- [ ] Presentar solicitud de Sandbox/COT solo si el abogado confirma que aplica
- [ ] Designar responsable de cumplimiento (puede ser CEO inicialmente)
- [ ] Documentar políticas AML/LAFT y SARLAFT si aplica
- [ ] Negociar contrato con Truora, MetaMap o Jumio para KYC
- [ ] Negociar PSE/ACH mediante pasarela o aliado regulado
- [ ] Evaluar Pomelo/Dock/Adyen para tarjeta virtual sin alcance PCI completo
- [ ] Evaluar aliado IMC/banco para cambio COP/USD/EUR
- [ ] Evaluar broker/comisionista partner para acciones/ETFs, sin asesoría propia
- [ ] Evaluar exchange/VASP aliado para crypto, separado del saldo de pagos
- [ ] Redactar disclosures de riesgo para FX, crypto y acciones
- [ ] Abrir cuenta bancaria corporativa (Bancolombia o Davivienda)

---

## 13. Fuentes regulatorias de referencia

- SFC — SEDPE, captación exclusiva mediante depósitos electrónicos: https://www.superfinanciera.gov.co/publicaciones/10087941/sedpe-captacion-exclusiva-mediante-depositos-electronicos-10087941/
- Decreto 1234 de 2020 — Espacio Controlado de Prueba y Certificado de Operación Temporal: https://www.funcionpublica.gov.co/eva/gestornormativo/norma_pdf.php?i=142005
- SFC — Pasarelas de pago y políticas AML/LAFT: https://www.superfinanciera.gov.co/publicaciones/10098492/normativanormativa-generalboletin-juridico-superintendencia-financieraboletin-juridico-numero-otros-conceptos-sintesis-10098492/
- Ministerio de Hacienda — Decreto 0368 de 2026, Sistema de Finanzas Abiertas: https://www.minhacienda.gov.co/decretos-2026/-/document_library/eryu/view_file/3171602
- Banco de la República — conceptos básicos de regulación y operaciones cambiarias: https://www.banrep.gov.co/es/politica-monetaria-cambiaria/regulacion-operaciones-cambiarias/conceptos-basicos
- SFC — Mercado público de valores: https://www.superfinanciera.gov.co/preguntas-frecuentes/25/25-mercado-publico-de-valores/
- SFC — laArenera y pilotos de criptoactivos: https://www.superfinanciera.gov.co/publicaciones/10107301/innovasfcpruebas-en-el-sandbox-10107301/
- NIST — FIPS 203/204/205: https://csrc.nist.gov/pubs/fips/203/final
- Open Quantum Safe — liboqs: https://openquantumsafe.org/liboqs/
- PCI Security Standards Council — merchant resources and PCI DSS scope: https://www.pcisecuritystandards.org/merchants/

---

*Toda decisión regulatoria debe ser validada por asesor jurídico antes de implementarse.*
