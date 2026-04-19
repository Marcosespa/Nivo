# Business Gaps Sprint 0 y 1

Este documento resume los hallazgos de negocio y cumplimiento detectados al auditar lo implementado en Sprint 0 y Sprint 1. Complementa el análisis técnico en `tasks/ANALISIS-SPRINT-0-1.md`.

## 1. Riesgos de negocio abiertos

### 1.1 Narrativa comercial de PQC
- Hoy existe una base técnica atractiva para firma y verificación post-cuántica.
- Aún falta aterrizar la propuesta de valor por segmento: fintech, banca, gobierno y aliados regulatorios.
- Acción recomendada: definir 3 casos de uso vendibles con problema, impacto, buyer persona y pricing inicial.

### 1.2 Pricing y monetización
- No está cerrado el esquema comercial de `FREE`, `PLUS` y `PRO`.
- Tampoco existe todavía una política formal para el producto B2B de firma/verificación PQC.
- Acción recomendada: documentar tabla de planes, límites operativos, costos variables y margen esperado.

### 1.3 Unit economics
- Ya existen flujos que dependen de terceros como Twilio, Truora, Wompi y nube.
- Falta consolidar costo por usuario activo, costo por onboarding, costo por transacción y costo por operación B2B.
- Acción recomendada: crear una hoja base con CAC operativo técnico por flujo.

### 1.4 Ruta regulatoria
- El backend refleja una intención de operar como middleware no custodial, pero sigue faltando una definición formal de ruta regulatoria.
- Debe aclararse cuándo el producto sigue siendo middleware y cuándo entra en terreno de SEDPE, emisor, adquirente, broker o proveedor de servicios tecnológicos regulados.
- Acción recomendada: abrir un memo legal-operativo con escenarios permitidos y prohibidos.

### 1.5 Dependencia de partners
- La solución depende de contratos y SLAs con proveedores críticos.
- Faltan criterios documentados para fallback, reemplazo o suspensión operativa por proveedor.
- Acción recomendada: documentar matriz de dependencia con dueño, SLA, riesgo y plan de contingencia.

## 2. Documentos de negocio/compliance que faltan

- Contratos y términos con Wompi.
- Contratos y términos con Truora.
- Contratos y términos con Twilio.
- Definición comercial y contractual de cloud/KMS/HSM si la firma deja de ser efímera.
- Política de precios para B2C (`FREE`, `PLUS`, `PRO`).
- Política de precios para API B2B PQC.
- Memo regulatorio de operación no custodial vs. ruta SEDPE.
- Matriz de riesgos operativos por proveedor.

## 3. Decisiones de negocio que bloquean fases siguientes

### Alta prioridad
- Definir si la API B2B PQC se ofrecerá como producto público, privada por convenio o piloto cerrado.
- Definir si el saldo mostrado en wallet seguirá siendo solo visual en Sprint 2+ o si habrá integración contable con partner regulado.
- Definir el modelo de monetización principal del MVP: comisión por pago, suscripción, revenue share o B2B API.

### Prioridad media
- Definir límites comerciales por plan.
- Definir qué segmentos de clientes entran primero al GTM.
- Definir discurso comercial para “quantum shield” sin prometer cobertura regulatoria o legal que aún no exista.

## 4. Recomendación operativa

Antes de seguir ampliando backend, conviene cerrar un paquete mínimo de negocio:

1. Tabla de planes y límites.
2. Matriz de proveedores y contratos.
3. Memo regulatorio de operación.
4. One-pager comercial del producto PQC B2B.
5. Modelo base de unit economics.

## 5. Estado de esta auditoría

- Parte técnica: se están corrigiendo desalineaciones detectadas entre análisis y código.
- Parte de negocio: sigue abierta y requiere decisiones de producto, comercial y compliance.
- Este documento no reemplaza revisión legal; funciona como backlog de negocio/compliance para continuar la ejecución.
