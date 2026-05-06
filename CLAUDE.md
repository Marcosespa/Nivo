# CLAUDE.md — Nivo
> Guía de trabajo para Claude Code en este repositorio.

## Qué es este proyecto

Nivo es un neobanco colombiano quantum-safe. App móvil tipo Revolut para Colombia/LATAM con:
- Criptografía post-cuántica NIST (ML-KEM-768, ML-DSA-65) como capa base
- Pagos P2P instantáneos por celular
- KYC biométrico (Truora), OTP SMS (Twilio), pagos PSE (Wompi)
- Modelo no-custodial: Wompi custodia los fondos, Nivo orquesta
- Planes FREE / PLUS / PRO
- Segunda línea de negocio: API B2B de PQC-as-a-Service

**Stack:** Python 3.11 + FastAPI · PostgreSQL 16 + Redis · liboqs (ML-KEM-768, ML-DSA-65) · GCP (Cloud Run + Cloud SQL) · React Native (móvil) · Cloudflare

**Lanzamiento público:** Sprint 6, agosto 2026. Hoy: Sprint 2 activo (mayo 2026).

---

## Perfil del equipo técnico

El usuario es **co-fundador técnico de Nivo** con rol de ingeniero senior / tech lead. Trabaja en Python (FastAPI), seguridad, arquitectura de sistemas financieros y lógica de negocio fintech. Entiende regulación colombiana (SFC, UIAF, SEDPE) y criptografía aplicada. Las respuestas y decisiones deben asumir ese nivel — no explicar lo básico, ir directo a lo técnico y relevante.

---

## Dos sistemas de tracking — entenderlos antes de tocar cualquier tarea

Nivo usa **dos sistemas de tracking distintos** con numeraciones diferentes. No mezclarlos:

### Sistema A — TASKS.md (registro maestro oficial)
`TASKS.md` en la raíz es el **registro de completación de todos los agentes**.  
Formato: `FIX-001..009` (Sprint 0) y `TASK-001..035` (Sprint 1 en adelante).  
Fuente de verdad permanente. **Actualizarlo siempre que se complete una tarea oficial.**

### Sistema B — `felipe_tareas.txt` (lista personal de Felipe)
`c:\Users\Sebastian\Downloads\felipe_tareas.txt` usa numeración propia `[T-01]..[T-13]`.  
**Este archivo varía por conversación — NO es la fuente de verdad, no guardarlo en memoria.**  
Cuando Felipe pasa tareas T-XX, mapearlas al TASK-XXX correspondiente en TASKS.md para actualizar el estado ahí.

**Tabla de mapeo T-XX → TASK-XXX:**
| T-XX (felipe_tareas.txt) | TASK-XXX (TASKS.md) | Estado | Scope |
|---|---|---|---|
| T-01 Webhook Wompi | TASK-007 | ✅ Done | Webhook + crédito atómico, 10 tests |
| T-04 Alembic CI | TASK-019 | ✅ Done (parcial) | Solo el job migration-check; TASK-019 completa = CD pipeline |
| T-05 OpenTelemetry | TASK-031 | ✅ Done (parcial) | OTel spans en rutas críticas; TASK-031 completa = Sentry + runbooks |
| T-08 dev_otp gate | (sin entrada propia) | ✅ Done | Fix de seguridad puntual, 5 tests |
| T-09 Canal alertas | TASK-031 | ✅ Done (parcial) | Slack AlertService; TASK-031 completa = GCP Monitoring |
| T-10 Métricas KYC | (sin entrada propia — Sprint 3) | ✅ Done | `kyc_funnel_events`, funnel instrumentation, /kyc/funnel, alerta Slack |
| T-13 Métricas negocio | TASK-030 (parcial) | ✅ Done | `business_metrics_daily` ORM + MetricsService + admin endpoints; Metabase/PostHog pendiente |

---

## Cómo trabajar en este repositorio

### 1. Antes de implementar cualquier cosa
- Leer el archivo de sprint activo en `tasks/sprint-X/sprint-X.md`
- El archivo `tasks/README.md` tiene el índice y estado general de todos los sprints
- `TASKS.md` en la raíz tiene el estado completo de cada tarea — leerlo para no duplicar trabajo

### 2. Después de cada grupo de cambios importantes
- Documentar los cambios en `tasks/sprint-X/done/TASK-XXX.md` (crear el archivo)
  - Si la tarea viene de `felipe_tareas.txt`, nombrar el archivo `TASK-T-XX.md` en la carpeta del sprint correspondiente
- Si hay problemas encontrados o decisiones técnicas no obvias, añadirlos a `tasks/sprint-X/problems/problems.md`
- **Actualizar `TASKS.md`**: cambiar `[ ] PENDING` → `[x] DONE` para la TASK-XXX correspondiente
  - Si una T-XX completa parcialmente una TASK-XXX, anotar qué parte quedó hecha en la descripción de la tarea en TASKS.md
- Actualizar el README en `tasks/README.md` si cambia el progreso del sprint

### 3. Registro de problemas
Cada sprint tiene su carpeta `problems/problems.md`. Añadir ahí:
- Bugs encontrados durante la implementación
- Decisiones técnicas con justificación
- Comportamientos inesperados o edge cases descubiertos
- Deuda técnica identificada

### 4. Archivos NO relevantes por chat
- `c:\Users\Sebastian\Downloads\felipe_tareas.txt` — varía por conversación, no guardar en memoria ni referenciar como fuente de verdad. Usar la tabla de mapeo de arriba para conectar T-XX con TASKS.md.

---

## Estructura de tasks

```
tasks/
├── README.md                    ← índice de sprints con estado general
├── ANALISIS-SPRINT-0-1.md       ← análisis senior del codebase
├── sprint-0/done/FIX-001..009   ← completado: 9/9 fixes
├── sprint-1/done/TASK-001..005  ← completado: 5/5 fundaciones técnicas
├── sprint-2/sprint-2.md         ← ACTIVO: TASK-006 (KYC), 007 (Wompi PSE), 008 (ACH)
├── sprint-3/ → sprint-8-12/     ← pendiente
└── transversales/               ← TASK-031..035 cross-cutting
```

**Sprint 2 activo — estado:**
- TASK-006: ⏳ Integración Truora KYC (kyc_service.py, endpoints /kyc/)
- TASK-007: ✅ Integración Wompi PSE top-ups — done (T-01: webhook + crédito atómico, 10 tests)
- TASK-008: ⏳ Retiros ACH (/withdrawal/)

> Nota: el backend ya tiene implementaciones parciales de KYC y top-up que pueden estar adelantadas respecto al spec — verificar el código real antes de tratar como sin hacer.

---

## Estado del proyecto (mayo 2026)

| Sprint | Tasks | Estado |
|--------|-------|--------|
| Sprint 0 — Pre-implementation fixes | FIX-001→009 | ✅ 9/9 DONE |
| Sprint 1 — Fundaciones técnicas | TASK-001→005 | ✅ 5/5 DONE |
| Sprint 2 — KYC y Recarga (**activo**) | TASK-006→008 | ⏳ 1/3 (007 ✅) |
| Sprint 3→8-12 | TASK-009→030 | ⏳ pendiente |
| Transversales | TASK-031→035 | ⏳ pendiente |

**Total:** 16/49 completadas

---

## Principios de desarrollo en Nivo

1. **Security-first** — PQC no es un feature, es la fundación; nunca retornar llaves privadas por la API
2. **Crypto-agility** — algoritmos leídos de `settings`, no hardcodeados en el código
3. **Compliance-by-design** — regulación colombiana integrada desde el día 0
4. **Montos en centavos** — todos los montos en BD son enteros en centavos de COP
5. **No retornar secrets** — `shared_secret_hex`, `signing_key_hex`, private keys nunca viajan por red

---

## Backend CLAUDE.md

El archivo `backend/CLAUDE.md` tiene detalles específicos del backend: comandos de desarrollo, arquitectura de pagos, PQC, tests y variables de entorno clave. Leerlo antes de trabajar en el backend.
