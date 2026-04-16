## MES 2 — SPRINT 4 (Semanas 9–12): Recarga, Historial y Perfil

---

### TASK-013 — Pantalla de Recarga PSE y Retiro
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 5–6 horas
**Prioridad:** ALTA

**Descripción:**
Pantallas de recarga desde PSE (Wompi) y retiro a cuenta bancaria.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/TopUpScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/WithdrawScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/AddBankAccountScreen.tsx`

**Flujo recarga:**
```
TopUpScreen:
  - Input: monto a recargar
  - Montos sugeridos: $50K, $100K, $200K, $500K (botones rápidos)
  - Nota: "Te redirigiremos a PSE para completar el pago"
  - Botón "Recargar" → abre WebView con URL de Wompi
  - WebView monitorea la URL de retorno para detectar éxito/fallo
  - Al volver: mostrar pantalla de confirmación o error
```

**Criterios de éxito:**
- [ ] La WebView de Wompi se abre y el usuario puede completar PSE en sandbox
- [ ] Al volver de Wompi exitoso, el saldo se actualiza en HomeScreen
- [ ] El formulario de cuenta bancaria valida el número de cuenta (8–16 dígitos)

**Dependencias:** TASK-009, TASK-007, TASK-008

---

### TASK-014 — Historial de Transacciones y Detalle
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 4–5 horas
**Prioridad:** ALTA

**Descripción:**
Lista paginada de movimientos con filtros y vista de detalle de cada transacción.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/HistoryScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/TransactionDetailScreen.tsx`
- CREAR `frontend/mobile/src/components/history/TransactionItem.tsx`

**Especificaciones:**
```
HistoryScreen:
  - FlatList con paginación (cargar 20 por scroll)
  - Filtros: Todos | Enviados | Recibidos | Recargas
  - Cada TransactionItem muestra:
    - Ícono dirección (flecha arriba/abajo)
    - Nombre/teléfono del otro lado
    - Monto (verde si recibido, rojo si enviado)
    - Fecha/hora
    - Indicador ⚛️ si tiene firma cuántica (siempre en Nivo)

TransactionDetailScreen:
  - Todos los datos de la tx
  - Sección "Seguridad cuántica":
    - Algoritmo: ML-DSA-65
    - Fingerprint de firma: [16 chars]
    - "Esta firma es verificable a perpetuidad"
  - Botón: "Descargar comprobante PDF"
```

**Criterios de éxito:**
- [ ] La lista carga desde API con paginación real (no todo de una vez)
- [ ] Los filtros funcionan cambiando el parámetro `direction` en la API
- [ ] El scroll infinito carga la siguiente página al llegar al final

**Dependencias:** TASK-009, TASK-011

---

### TASK-015 — Perfil de Usuario, KYC y Configuración
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 4–5 horas
**Prioridad:** MEDIA

**Descripción:**
Pantalla de perfil con estado de KYC, plan actual, y configuraciones de seguridad.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/ProfileScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/KYCScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/SecurityScreen.tsx`

**Secciones del perfil:**
```
ProfileScreen:
  [Avatar generado con iniciales]
  [Nombre / +57 310 xxx]
  [Plan: FREE / PLUS / PRO] → link a upgrade

  Sección "Verificación":
  [Estado KYC: ✓ Verificado | ⏳ Pendiente | ✗ Rechazado]
  → Si pendiente: botón "Verificar ahora" → KYCScreen

  Sección "Seguridad cuántica":
  [🔑 Mis llaves PQC] → ver fingerprint de llaves
  [⚛️ Algoritmo activo: ML-KEM-768]

  Sección "Configuración":
  [Notificaciones]
  [Idioma]
  [Cerrar sesión]
```

**Criterios de éxito:**
- [ ] El estado de KYC se muestra correctamente según el backend
- [ ] El fingerprint de llave PQC del usuario es visible y copiable
- [ ] "Cerrar sesión" llama `POST /api/v1/auth/logout` y limpia `expo-secure-store`

**Dependencias:** TASK-009, TASK-006

---

