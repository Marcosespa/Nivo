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

## Behavioral guidelines

*Tradeoff:* These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

*Don't assume. Don't hide confusion. Surface tradeoffs.*

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

*Minimum code that solves the problem. Nothing speculative.*

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

*Touch only what you must. Clean up only your own mess.*

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

*Define success criteria. Loop until verified.*

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## Sistema de tracking — TASKS.md

`TASKS.md` en la raíz es el **registro de completación de todos los agentes**.  
Formato: `FIX-001..009` (Sprint 0) y `TASK-001..035` (Sprint 1 en adelante).  
Fuente de verdad permanente. **Actualizarlo siempre que se complete una tarea oficial.**

---

## Cómo trabajar en este repositorio

### 1. Antes de implementar cualquier cosa
- Leer el archivo de sprint activo en `tasks/sprint-X/sprint-X.md`
- El archivo `tasks/README.md` tiene el índice y estado general de todos los sprints
- `TASKS.md` en la raíz tiene el estado completo de cada tarea — leerlo para no duplicar trabajo

### 2. Después de cada grupo de cambios importantes
- Documentar los cambios en `tasks/sprint-X/done/TASK-XXX.md` (crear el archivo)
- Si hay problemas encontrados o decisiones técnicas no obvias, añadirlos a `tasks/sprint-X/problems/problems.md`
- **Actualizar `TASKS.md`**: cambiar `[ ] PENDING` → `[x] DONE` para la TASK-XXX correspondiente
- Actualizar el README en `tasks/README.md` si cambia el progreso del sprint

### 3. Registro de problemas
Cada sprint tiene su carpeta `problems/problems.md`. Añadir ahí:
- Bugs encontrados durante la implementación
- Decisiones técnicas con justificación
- Comportamientos inesperados o edge cases descubiertos
- Deuda técnica identificada

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
- TASK-007: ✅ Integración Wompi PSE top-ups — done (webhook + crédito atómico, 10 tests)
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