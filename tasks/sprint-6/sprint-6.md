## MES 3–4 — SPRINT 6 (Semanas 17–20): Lanzamiento Público

---

### TASK-018 — Landing Page: Completar Versión Producción
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 6–8 horas
**Prioridad:** ALTA

**Descripción:**
Completar la landing page existente en `landing_page/nivo/`:
agregar sección de pricing, sección de testimonios, formulario de lista de espera beta,
y optimizar para móvil.

**Archivos a modificar/crear:**
- MODIFICAR `landing_page/nivo/src/pages/home.tsx` — Agregar nuevas secciones
- CREAR `landing_page/nivo/src/sections/pricing.tsx` — Planes y precios
- CREAR `landing_page/nivo/src/sections/waitlist.tsx` — Formulario de beta
- CREAR `landing_page/nivo/src/sections/social-proof.tsx` — Logos y números
- MODIFICAR `landing_page/nivo/src/sections/flywheel.tsx` — Ya tiene CTA, mejorar

**Sección de Pricing:**
```
3 planes en cards:
┌─────────────┐ ┌──────────────┐ ┌─────────────┐
│ FREE        │ │ PLUS ⭐      │ │ PRO         │
│ $0/mes      │ │ $9.900/mes   │ │ $24.900/mes │
│             │ │              │ │             │
│ ✓ Pagos P2P │ │ ✓ Todo FREE  │ │ ✓ Todo PLUS │
│ ✓ PQC básico│ │ ✓ Tarj. virt.│ │ ✓ Multi-moneda│
│ ✓ Recarga   │ │ ✓ Límite $5M │ │ ✓ COP/USD/EUR│
│   PSE       │ │ ✓ Recibos    │ │ ✓ API básica │
│             │ │   cert.      │ │ ✓ Soporte   │
│             │ │              │ │   prioritario│
└─────────────┘ └──────────────┘ └─────────────┘

Card PLUS tiene badge "Más popular" y borde sky-400
```

**Formulario de lista de espera:**
```
Título: "Únete a la beta cerrada"
Input: número de celular
Input: email (opcional)
Checkbox: "Soy desarrollador / tengo una empresa" (para priorizar B2B)
Botón: "Reservar mi lugar"
→ POST a https://formspree.io o servicio similar
→ Mostrar confirmación: "¡Estás en la lista! Te avisamos cuando lancemos."
```

**Criterios de éxito:**
- [ ] La landing page tiene score > 90 en Lighthouse Mobile
- [ ] El formulario de lista de espera envía datos (probar con email real)
- [ ] La página es completamente responsive (probar en 375px, 768px, 1440px)
- [ ] Todas las secciones tienen sus textos en español colombiano

**Dependencias:** Ninguna

---

### TASK-019 — CI/CD Pipeline con GitHub Actions
**Estado:** [ ] PENDING
**Agente sugerido:** devops
**Estimado:** 6–8 horas
**Prioridad:** ALTA

**Descripción:**
Configurar pipelines de CI/CD para el backend. Cada PR debe pasar tests antes de merge.
Cada push a main debe deployar automáticamente a staging.

**Archivos a crear:**
- CREAR `.github/workflows/backend-ci.yml` — Tests en cada PR
- CREAR `.github/workflows/backend-deploy-staging.yml` — Deploy automático a staging
- CREAR `.github/workflows/backend-deploy-prod.yml` — Deploy manual a producción
- CREAR `backend/Dockerfile.prod` — Imagen de producción optimizada

**`backend-ci.yml` debe:**
```yaml
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: # imagen postgres:16-alpine
      redis:    # imagen redis:7-alpine
    steps:
      - Checkout
      - Setup Python 3.11
      - Install liboqs (desde fuente)
      - pip install -r requirements.txt
      - ruff check .
      - mypy app/ --ignore-missing-imports
      - pytest tests/ -v --cov=app --cov-fail-under=80
      - Upload coverage report
```

**`Dockerfile.prod` requisitos:**
```dockerfile
# Multi-stage build para imagen pequeña
# Stage 1: builder (instala liboqs y compilaciones)
# Stage 2: runtime (solo lo necesario para correr)
# Usuario no-root para seguridad
# Health check incluido
# Tamaño final objetivo: < 500MB
```

**Criterios de éxito:**
- [ ] Cada PR abre un check "backend-ci" que pasa o falla automáticamente
- [ ] Un push a `main` dispara deploy a staging en < 5 minutos
- [ ] El deploy a producción requiere aprobación manual (environment protection)
- [ ] La imagen Docker de producción corre como usuario no-root

**Dependencias:** TASK-004 (tests deben existir antes del CI)

---

### TASK-020 — Sistema de Notificaciones Push (Firebase)
**Estado:** [ ] PENDING
**Agente sugerido:** backend
**Estimado:** 4–5 horas
**Prioridad:** MEDIA

**Descripción:**
Implementar notificaciones push para: pago recibido, recarga confirmada, alerta de fraude.

**Archivos a crear/modificar:**
- MODIFICAR `backend/app/services/notification_service.py` — Implementación real
- CREAR `backend/app/models/orm/device_token.py` — Tokens de dispositivos

**Tabla device_tokens:**
```sql
id: UUID PK
user_id: UUID FK -> users.id
token: VARCHAR(500) NOT NULL
platform: ENUM('ios','android')
is_active: BOOLEAN DEFAULT TRUE
created_at: TIMESTAMPTZ DEFAULT NOW()
INDEX: (user_id, is_active)
```

**Notificaciones a implementar:**
```python
async def notify_payment_received(receiver_id, amount_display, sender_name):
    title = "💚 ¡Recibiste dinero!"
    body = f"Te enviaron {amount_display} — ya está en tu billetera Nivo"

async def notify_topup_confirmed(user_id, amount_display):
    title = "✅ Recarga exitosa"
    body = f"{amount_display} fueron agregados a tu billetera"

async def notify_fraud_alert(user_id, transaction_details):
    title = "⚠️ Actividad inusual detectada"
    body = "Detectamos un intento de transacción inusual. Tu billetera está protegida."
```

**Criterios de éxito:**
- [ ] Al completar un pago P2P, el receptor recibe push en < 3 segundos
- [ ] Si el token FCM está inactivo, se elimina de BD automáticamente
- [ ] Las notificaciones funcionan con la app en segundo plano y cerrada

**Dependencias:** TASK-003

---

