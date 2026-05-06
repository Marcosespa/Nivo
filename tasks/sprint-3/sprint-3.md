## MES 2 — SPRINT 3 (Semanas 5–8): Mobile App

---

### Hardening Sprint 3 — Backup y continuidad

| Prioridad | Tarea | Estado | Evidencia |
|---|---|---|---|
| P2 | Estrategia documentada de backup y DR de PostgreSQL | [x] DONE | `docs/08-postgresql-backup-dr.md` define PITR, retenciones, RPO/RTO, restauracion y ensayos |

---

### TASK-009 — Setup del Proyecto React Native
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 4–5 horas
**Prioridad:** CRÍTICA

**Descripción:**
Crear el proyecto React Native para la app móvil de Nivo desde cero con
Expo + TypeScript + NativeWind (Tailwind para RN).

**Archivos a crear:**
- CREAR `frontend/mobile/` — Nuevo directorio del proyecto RN
- CREAR `frontend/mobile/package.json`
- CREAR `frontend/mobile/app.json` — Config de Expo
- CREAR `frontend/mobile/tsconfig.json`
- CREAR `frontend/mobile/src/` — Estructura del proyecto
- CREAR `frontend/mobile/src/navigation/` — React Navigation
- CREAR `frontend/mobile/src/screens/` — Pantallas principales
- CREAR `frontend/mobile/src/components/` — Componentes reutilizables
- CREAR `frontend/mobile/src/services/api.ts` — Cliente HTTP hacia el backend
- CREAR `frontend/mobile/src/store/` — Estado global (Zustand)
- CREAR `frontend/mobile/src/theme/colors.ts` — Paleta de colores Nivo

**Stack:**
```json
{
  "expo": "~52.0.0",
  "react-native": "0.76.x",
  "typescript": "^5.3.0",
  "nativewind": "^4.0.0",
  "tailwindcss": "^3.4.0",
  "@react-navigation/native": "^7.0.0",
  "@react-navigation/stack": "^7.0.0",
  "@react-navigation/bottom-tabs": "^7.0.0",
  "zustand": "^5.0.0",
  "axios": "^1.7.0",
  "react-hook-form": "^7.53.0",
  "zod": "^3.23.0",
  "@tanstack/react-query": "^5.59.0",
  "expo-secure-store": "~14.0.0",
  "expo-notifications": "~0.29.0",
  "react-native-reanimated": "~3.16.0"
}
```

**Colores Nivo (definir en `theme/colors.ts`):**
```typescript
export const colors = {
  primary: '#38BDF8',       // sky-400 — Nivo Blue
  primaryLight: '#7DD3FC',  // sky-300
  primaryDark: '#0284C7',   // sky-600
  background: '#0B1120',    // slate-950
  surface: '#1E293B',       // slate-800
  surfaceLight: '#334155',  // slate-700
  text: '#F8FAFC',          // slate-50
  textMuted: '#94A3B8',     // slate-400
  success: '#22C55E',       // green-500
  error: '#EF4444',         // red-500
  warning: '#F59E0B',       // amber-500
  quantum: '#38BDF8',       // mismo que primary — alias semántico
}
```

**Estructura de navegación:**
```
Root Navigator (Stack)
├── AuthStack (cuando no hay sesión)
│   ├── SplashScreen
│   ├── OnboardingScreen
│   ├── PhoneInputScreen
│   └── OTPVerifyScreen
└── AppStack (cuando hay sesión)
    └── BottomTabs
        ├── HomeTab → HomeScreen
        ├── SendTab → SendMoneyScreen
        ├── HistoryTab → HistoryScreen
        └── ProfileTab → ProfileScreen
```

**Criterios de éxito:**
- [ ] `cd frontend/mobile && npx expo start` — arranca sin errores
- [ ] La pantalla inicial se ve en iOS Simulator y Android Emulator
- [ ] NativeWind funciona: `<View className="bg-slate-950 flex-1" />` aplica el estilo
- [ ] TypeScript no tiene errores: `npx tsc --noEmit`
- [ ] El cliente API apunta a `http://localhost:8000` en desarrollo y es configurable

**Dependencias:** Ninguna (es paralelo al backend)

---

### TASK-010 — Pantalla de Onboarding y Registro por Celular
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 6–8 horas
**Prioridad:** CRÍTICA

**Descripción:**
Implementar el flujo completo de registro: onboarding de 3 slides, entrada del número
de celular colombiano, y verificación OTP con teclado numérico.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/auth/SplashScreen.tsx`
- CREAR `frontend/mobile/src/screens/auth/OnboardingScreen.tsx`
- CREAR `frontend/mobile/src/screens/auth/PhoneInputScreen.tsx`
- CREAR `frontend/mobile/src/screens/auth/OTPVerifyScreen.tsx`
- CREAR `frontend/mobile/src/components/auth/OTPInput.tsx` — Input de 6 dígitos
- CREAR `frontend/mobile/src/components/auth/PhoneInput.tsx` — Input con bandera 🇨🇴

**Especificaciones de diseño (dark theme, colores Nivo):**

```
SplashScreen:
- Fondo slate-950
- Logo Nivo (átomo blindado) centrado con animación de glow pulsante
- Transición automática a OnboardingScreen después de 2.5 segundos

OnboardingScreen (3 slides con swipe):
Slide 1:
  - Ícono: escudo cuántico animado
  - Título: "La billetera más segura de Colombia"
  - Subtítulo: "Cifrado post-cuántico en cada pago. El mismo estándar que usan los gobiernos."

Slide 2:
  - Ícono: teléfono con transferencia animada
  - Título: "Paga por número de celular"
  - Subtítulo: "Sin cuentas bancarias. Sin formularios. Solo el número y listo."

Slide 3:
  - Ícono: escudo con checkmark
  - Título: "Tu plata, blindada para siempre"
  - Subtítulo: "Las firmas cuánticas de hoy protegen tus transacciones en 20 años."

Botón final: "Crear mi billetera" → PhoneInputScreen

PhoneInputScreen:
- Header: "¿Cuál es tu número?" con subtítulo "Te enviaremos un código de verificación"
- Input con prefijo +57 fijo y bandera colombiana
- Validación: solo números, exactamente 10 dígitos después del +57
- Botón "Enviar código" deshabilitado hasta que el número sea válido
- Al enviar: indicador de carga, luego navegar a OTPVerifyScreen

OTPVerifyScreen:
- Muestra el número (enmascarado: +57 310 *** **56)
- Texto: "Ingresa el código de 6 dígitos que enviamos a tu número"
- Componente OTPInput: 6 cajas individuales, focus automático
- Auto-verificar cuando los 6 dígitos están completos
- Link "Reenviar código" (deshabilitado por 60 segundos con countdown)
- En éxito: navegar a HomeScreen con animación de escudo cuántico

OTPInput component:
- 6 TextInput individuales
- Al escribir en uno, focus pasa automáticamente al siguiente
- Al borrar, focus vuelve al anterior
- En iOS/Android muestra teclado numérico
- Animación de shake si el código es incorrecto
```

**Criterios de éxito:**
- [ ] El flujo completo de onboarding funciona sin errores en iOS y Android
- [ ] El input de número valida el formato colombiano (+57 + 10 dígitos)
- [ ] El OTP input tiene focus automático y backspace funciona correctamente
- [ ] Al completar el OTP, se llama `POST /api/v1/auth/verify-otp` real
- [ ] Los 3 slides tienen animaciones fluidas con `react-native-reanimated`

**Dependencias:** TASK-009

---

### TASK-011 — Pantalla Home (Billetera + Saldo + Acciones rápidas)
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 6–8 horas
**Prioridad:** CRÍTICA

**Descripción:**
La pantalla principal de la app. Muestra el saldo, el escudo cuántico activo,
y los botones de acciones rápidas (Enviar, Recibir, Recargar, Historial).

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/HomeScreen.tsx`
- CREAR `frontend/mobile/src/components/wallet/BalanceCard.tsx`
- CREAR `frontend/mobile/src/components/wallet/QuantumShieldBadge.tsx`
- CREAR `frontend/mobile/src/components/wallet/QuickActions.tsx`
- CREAR `frontend/mobile/src/components/wallet/RecentTransactions.tsx`

**Especificaciones de diseño:**

```
HomeScreen layout (dark, slate-950 background):

─────────────────────────────────────────────
  Header:
  "Hola, [nombre]"            [Foto / Avatar]
  [Fecha: Martes 14 Abr]

─────────────────────────────────────────────
  BalanceCard (rounded-3xl, gradient slate-900→sky-950):
  ┌─────────────────────────────────────────┐
  │  Saldo disponible                        │
  │  $1.250.000 COP               [👁 ocultar]│
  │                                          │
  │  ⚛️ Escudo Cuántico Activo               │
  │  ML-KEM-768 · ML-DSA-65                 │
  └─────────────────────────────────────────┘

  QuantumShieldBadge:
  - Pequeño indicador verde pulsante: "Protegido"
  - Al tocar: modal explicando qué es PQC en lenguaje simple

─────────────────────────────────────────────
  QuickActions (4 botones en fila):
  [↑ Enviar]  [↓ Recibir]  [+ Recargar]  [↕ Retirar]
  Íconos con fondo sky-400/10, texto sky-300

─────────────────────────────────────────────
  Últimas transacciones (flat list):
  Sección "Recientes" con 5 últimas transacciones
  Cada item: [Avatar] [Nombre/Número] [Monto] [Estado]
  Link "Ver todo" → HistoryScreen
─────────────────────────────────────────────
```

**QuantumShieldBadge modal (cuando el usuario toca el badge):**
```
Título: "¿Qué es el Escudo Cuántico?"
Texto: "Cada transacción en Nivo está protegida con ML-KEM-768,
el estándar de cifrado post-cuántico certificado por el gobierno de EE.UU. en 2024.
Esto significa que tus pagos están seguros incluso contra computadoras del futuro.
Ninguna otra billetera colombiana ofrece esto."
Botón: "Entendido"
```

**Criterios de éxito:**
- [ ] El saldo se carga desde `GET /api/v1/users/me/wallet` real
- [ ] El botón de ocultar saldo muestra `$••••••• COP`
- [ ] El QuantumShieldBadge pulsa suavemente con `react-native-reanimated`
- [ ] Las 5 últimas transacciones se cargan desde `GET /api/v1/payments/?page=1&page_size=5`
- [ ] Pull-to-refresh refresca el saldo y las transacciones

**Dependencias:** TASK-009, TASK-003

---

### TASK-012 — Flujo Completo de Envío de Dinero P2P
**Estado:** [ ] PENDING
**Agente sugerido:** frontend
**Estimado:** 8–10 horas
**Prioridad:** CRÍTICA

**Descripción:**
El flujo de pago P2P completo en la app: seleccionar receptor, ingresar monto,
confirmar con OTP, y ver el recibo con escudo cuántico.

**Archivos a crear:**
- CREAR `frontend/mobile/src/screens/app/SendMoneyScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/ConfirmPaymentScreen.tsx`
- CREAR `frontend/mobile/src/screens/app/PaymentSuccessScreen.tsx`
- CREAR `frontend/mobile/src/components/payment/AmountInput.tsx`
- CREAR `frontend/mobile/src/components/payment/QuantumReceipt.tsx`

**Flujo de pantallas:**
```
SendMoneyScreen:
  - Input: número de celular del receptor con autocompletar de contactos recientes
  - Input: monto en COP con formateador automático ($1.000.000)
  - Input: mensaje opcional (máx 100 chars)
  - Botón "Continuar" → ConfirmPaymentScreen

ConfirmPaymentScreen:
  - Resumen: "Vas a enviar $X a +57 3XX"
  - Badge: "⚛️ Protegido con ML-DSA-65"
  - Desglose: monto + comisión ($0 en Plus/Pro, $500 en Free si aplica)
  - OTP Input: "Confirma con tu código de seguridad"
  - Botón "Confirmar y Pagar"
  - Estado de carga: "Firmando con cifrado cuántico..." (0.5s) → "Procesando..." → éxito

PaymentSuccessScreen:
  - Animación: escudo cuántico que "cierra" con checkmark ✓
  - Título: "¡Listo! Enviaste $X"
  - Subtitle: "Recibido en segundos. Firmado cuánticamente."
  - QuantumReceipt component (tarjeta elegante con detalles):
    - ID de transacción (últimos 8 chars)
    - Fecha y hora
    - Monto
    - Receptor
    - "Firma cuántica: ML-DSA-65 ✓" con fingerprint (16 chars)
    - Botón "Compartir comprobante"
  - Botones: "Volver al inicio" | "Enviar otro"
```

**Criterios de éxito:**
- [ ] El flujo completo funciona de extremo a extremo con el backend real
- [ ] Si el usuario no tiene saldo suficiente, muestra error en español amigable
- [ ] La animación de éxito usa `react-native-reanimated` y dura ~1 segundo
- [ ] El comprobante se puede compartir como imagen via `expo-sharing`
- [ ] El fingerprint de firma ML-DSA-65 aparece en el recibo

**Dependencias:** TASK-009, TASK-011, TASK-003

---
