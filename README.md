# Nivo
### Tu plata, en otro nivel

> **Nombre público recomendado:** Nivo. 

> *"El futuro de las finanzas digitales no solo debe ser rápido e inclusivo — debe ser inquebrantable."*
> — CEO, Nivo

---

## ¿Qué es Nivo?

Nivo es un neobanco colombiano quantum-safe en construcción: una cuenta móvil tipo Revolut, diseñada primero para Colombia y luego para LATAM, que combina:

- **Experiencia UX tipo Revolut** — tarjeta virtual, multi-moneda, finanzas personales
- **Inmediatez tipo Bizum** — pagos P2P instantáneos por número de celular
- **Blindaje cuántico para todos** — el primer producto financiero de consumo en Colombia diseñado con ML-KEM-768, ML-DSA y cifrado híbrido desde la base
- **Ahorro, inversión y crypto en una sola app** — bolsillos de ahorro, cambio COP/USD/EUR, compra/venta de criptoactivos y acciones vía partners o licencias reguladas

**North star:** construir el banco digital que la banca colombiana todavía no ofrece: pagos, ahorro, tarjeta, multi-moneda, inversión, crypto, recibos verificables y protección post-cuántica en una sola experiencia.

**Estrategia MVP:** salir primero con arquitectura de neobanco por capas: app bancaria, KYC, pagos, recibos firmados, tarjeta y módulos financieros mediante aliados regulados o infraestructura autorizada. Si Nivo custodia saldos propios o emite depósitos electrónicos, activa ruta SEDPE/COT/banco aliado. Crypto, acciones, FX y ahorro se diseñan desde el día 0, pero se lanzan por módulos con partner-of-record, disclosures y aprobación legal previa.

### El problema que resolvemos

Nequi, Daviplata y Bancolombia App ya resolvieron parte del hábito digital, pero no ofrecen una experiencia completa tipo Revolut para Colombia: ahorro flexible, multi-moneda, inversión, crypto, recibos verificables y seguridad post-cuántica entendible para el usuario final.

Al mismo tiempo, gran parte del sistema financiero digital aún depende de RSA y ECC, algoritmos vulnerables a una computadora cuántica suficientemente potente. El ataque *"harvest now, decrypt later"* permite capturar datos cifrados hoy para descifrarlos mañana. Nivo convierte esa amenaza en una ventaja de producto: cada usuario, no solo clientes enterprise, debe sentir que su dinero y sus datos están protegidos para la era post-cuántica.

### Ámbito social y formalidad progresiva

El **core de negocio** incluye una apuesta de impacto: ayudar a mitigar la exclusión de quienes trabajan en informalidad (formación, crédito, bienestar), avanzando en la **escalera de la formalidad progresiva** —billeteras digitales, historia crediticia real, alternativas al crédito “gota a gota” con productos formales y apoyo sin persecución— según lo describe [**AMBITO_SOCIAL.md**](AMBITO_SOCIAL.md). La síntesis en modelo de negocio está en [docs/02-business-model.md](docs/02-business-model.md).

---

## Repositorio — Estructura del Proyecto

```
Nivo/
├── README.md                  ← Este archivo
├── AMBITO_SOCIAL.md           ← Misión social, formalidad progresiva, inclusión
├── docs/
│   ├── 00-strategic-review.md ← Memo estratégico regulatorio-first
│   ├── 01-vision-strategy.md  ← CEO vision, decisiones estratégicas
│   ├── 02-business-model.md   ← Modelo de negocio, unit economics
│   ├── 03-technical-architecture.md ← Stack, ADRs, diagramas
│   ├── 04-roadmap.md          ← Roadmap MVP a 12 meses
│   ├── 05-go-to-market.md     ← GTM, competidores, aliados
│   ├── 06-regulatory-compliance.md  ← SFC, UIAF, KYC, PCI, PQC compliance
│   └── 08-postgresql-backup-dr.md   ← Backups, PITR y disaster recovery
├── backend/
│   ├── app/
│   │   ├── api/               ← Endpoints FastAPI (routers)
│   │   ├── core/              ← Config, security, settings
│   │   ├── models/            ← Pydantic models & DB schemas
│   │   ├── services/          ← Lógica de negocio
│   │   └── crypto/            ← Módulo PQC (liboqs wrapper)
│   └── tests/
├── frontend/                  ← React Native (móvil)
├── landing_page/nivo/         ← Landing web pública
├── infra/
│   ├── terraform/             ← IaC para GCP + Cloudflare
│   └── docker/                ← Dockerfiles y compose
└── scripts/                   ← Scripts de setup y CI
```

---

## Quick Start (Desarrollo Local)

### Prerrequisitos

- Python 3.11+
- Docker & Docker Compose
- liboqs >= 0.10.0
- Node.js 20+ (para frontend)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Con Docker

```bash
docker-compose -f infra/docker/docker-compose.dev.yml up
```

### Variables de entorno requeridas

```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
PQC_SECURITY_LEVEL=3          # ML-KEM-768 (NIST Level 3)
HYBRID_MODE=true               # PQC + X25519 simultáneo
MONEY_CUSTODY_MODE=non_custodial_middleware
SETTLEMENT_RAIL=pse
CARD_ISSUER_PROVIDER=none
ENABLE_FX_EXCHANGE=false
ENABLE_CRYPTO_TRADING=false
ENABLE_STOCK_TRADING=false
JWT_SECRET_KEY=...
CLOUDFLARE_API_TOKEN=...
GCP_PROJECT_ID=Nivo-prod
```

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [Memo Estratégico](docs/00-strategic-review.md) | Revisión ejecutiva de nombre, regulación, mercado y ruta MVP |
| [Visión & Estrategia](docs/01-vision-strategy.md) | Decisiones del CEO, propuesta de valor, posicionamiento |
| [Ámbito social](AMBITO_SOCIAL.md) | Formalidad progresiva, inclusión financiera, impacto |
| [Modelo de Negocio](docs/02-business-model.md) | Segmentos, monetización, unit economics |
| [Arquitectura Técnica](docs/03-technical-architecture.md) | Stack, decisiones de arquitectura (ADRs), PQC |
| [Roadmap](docs/04-roadmap.md) | MVP a 12 meses, hitos, entregables |
| [Go-to-Market](docs/05-go-to-market.md) | GTM, competidores, aliados estratégicos |
| [Regulación & Compliance](docs/06-regulatory-compliance.md) | SFC, UIAF, AML/LAFT, KYC, PCI-DSS, PQC standards |
| [Backup & DR PostgreSQL](docs/08-postgresql-backup-dr.md) | Backups, PITR, RPO/RTO y restauración operativa |

---

## Stack Principal

| Capa | Tecnología |
|------|-----------|
| Backend API | Python 3.11 + FastAPI |
| Cifrado PQC | liboqs (ML-KEM-768, ML-DSA-65) |
| Cifrado híbrido | PQC + X25519 (compatibilidad total) |
| Base de datos | PostgreSQL 16 + Redis |
| CDN/Proxy | Cloudflare (ML-KEM en producción) |
| Cloud | GCP (Cloud Run + Cloud SQL) |
| Fraude/AI | Modelos de anomalía con embeddings + RAG |
| Mobile | React Native |

---

## Donde SÍ podría entrar Phoenix

Más adelante, Phoenix tendría sentido en capas donde la concurrencia y el realtime sean el centro del problema:

1. **Sistema de eventos en tiempo real**
   - Notificaciones
   - Activity feed
   - Live transactions

2. **P2P a escala masiva**
   - Tipo Bizum realtime
   - Millones de conexiones concurrentes

3. **Microservicio específico**
   - Servicio aislado para eventos, sockets, presencia y notificaciones
   - Sin reemplazar el core financiero ni el módulo PQC

### Arquitectura híbrida

- 🐍 **Python** → core financiero + PQC
- 🟣 **Elixir/Phoenix** → realtime layer

### Recomendación arquitectónica

Para Nivo:

🥇 **MVP — correcto como está**

- FastAPI
- PostgreSQL
- Redis
- liboqs

🥈 **Escala — fase 2–3**

Agregar **Elixir/Phoenix** como servicio separado:

```text
[ Mobile App ]
       ↓
[ FastAPI (core financiero + PQC) ]
       ↓
[ Phoenix (realtime / events / notifications) ]
```

### Resumen brutalmente honesto

- Phoenix es mejor en concurrencia
- Python es mejor en fintech + crypto + velocidad MVP

---

## Estado del Proyecto

| Fase | Estado | Timeline |
|------|--------|----------|
| Documentación fundacional | 🟡 En progreso | Semana 1 |
| MVP Backend (PQC Core) | ⬜ Pendiente | Mes 1–2 |
| MVP Billetera P2P | ⬜ Pendiente | Mes 3–4 |
| Beta cerrada | ⬜ Pendiente | Mes 5 |
| Lanzamiento comercial | ⬜ Pendiente | Mes 8–9 |
| API B2B PQC | ⬜ Pendiente | Mes 9–12 |

---

## Principios de Desarrollo

1. **Security-first** — PQC no es un feature adicional, es la fundación
2. **Crypto-agility** — arquitectura modular para cambiar algoritmos sin rediseño
3. **Compliance-by-design** — regulación colombiana integrada desde el día 0
4. **User trust** — la seguridad debe ser visible y verificable para el usuario final

---

## Licencia

Propietario — Nivo SAS © 2025-2026. Todos los derechos reservados.

---

*Para contribuir ver [CONTRIBUTING.md](CONTRIBUTING.md). Para reportar vulnerabilidades de seguridad, ver [SECURITY.md](SECURITY.md).*
