# Nivo Brand Style Guide (MVP)

Este documento define la identidad visual base de Nivo para el MVP, usando como fuente oficial:

- `mobile/nivo_mvp/lib/theme/nivo_colors.dart`
- `mobile/nivo_mvp/lib/theme/nivo_theme.dart`

## 1) Principios visuales

- Estilo editorial, limpio y sobrio.
- Contraste alto para lectura clara en mobile.
- Verde `forest` como acento primario de marca.
- Componentes suaves (bordes redondeados) con jerarquias tipograficas simples.
- Soporte dual de modo `light` y `dark`.

## 2) Tipografia oficial

- **Familia principal**: `Inter` (via `GoogleFonts.inter`).
- **Uso global**: `GoogleFonts.interTextTheme(...)` para todo el sistema.
- **Pesos frecuentes**:
  - `w600` para titulos y acciones principales.
  - `w500` para contenido destacado en feedback (ej. snackbars).
  - regular para texto de cuerpo.

### Escalas observadas en tema

- App bar title: `17`, `w600`.
- Filled button text: `14`, `w600`.
- Input hint: `16`.
- Input label: `12`, `w600`.

> Regla: mantener Inter como unica familia tipografica de producto para consistencia de marca en el MVP.

## 3) Colores de marca

## 3.1 Paleta Light (base)

| Token | Hex | Uso recomendado |
|---|---|---|
| `ink` | `#000000` | Texto principal, iconos de alto contraste |
| `paper` | `#FFFFFF` | Fondo principal |
| `stone` | `#4A4A4A` | Texto secundario |
| `stoneSoft` | `#6B6B6B` | Texto secundario suave |
| `mist` | `#9A9A9A` | Placeholder, texto terciario |
| `cloud` | `#E5E5E5` | Superficies neutras |
| `cloudSoft` | `#F3F3F3` | Fondo de cards/campos |
| `forest` | `#1A3C34` | Color primario de marca |
| `forestSoft` | `#254F46` | Variante suave del primario |
| `line` | `#D4D4D4` | Bordes y divisores |

## 3.2 Paleta Dark

| Token | Hex | Uso recomendado |
|---|---|---|
| `ink` | `#F4F4F1` | Texto principal en dark |
| `paper` | `#0B0B0B` | Fondo principal dark |
| `stone` | `#B8B8B6` | Texto secundario |
| `stoneSoft` | `#9E9E9C` | Texto secundario suave |
| `mist` | `#6F6F6D` | Placeholder, texto terciario |
| `cloud` | `#242424` | Superficies neutras |
| `cloudSoft` | `#161616` | Fondo de cards/campos |
| `forest` | `#8FE3C5` | Primario de marca en dark (mas brillante) |
| `forestSoft` | `#5FC1A0` | Variante suave del primario |
| `line` | `#2A2A2A` | Bordes y divisores |

## 3.3 Color de error

- `error`: `#E05A4B`

## 4) Tokens de UI y reglas de componente

## 4.1 Superficies y fondos

- Fondo global: `paper`.
- Cards y campos rellenos: `cloudSoft`.
- Divisores/bordes: `line`.

## 4.2 Botones

- **Filled (primario)**:
  - Background: `forest`
  - Foreground:
    - Light: `paper`
    - Dark: `ink`
  - Padding: `horizontal 22`, `vertical 14`
  - Radio: `999` (pill)
  - Texto: Inter `14`, `w600`

- **Outlined (secundario)**:
  - Foreground: `ink`
  - Borde: `1px` con `ink`
  - Padding: `horizontal 20`, `vertical 14`
  - Radio: `999` (pill)

## 4.3 Inputs

- Relleno: `cloudSoft`.
- Padding interno: `18 x 16`.
- Radio: `14`.
- Borde normal: `line`.
- Borde foco: `forest` con `1.5`.
- Hint: Inter `16`, color `mist`.
- Label: Inter `12`, `w600`, color `stone`.

## 4.4 App bar

- Fondo: `paper` con alpha `0.92`.
- Titulo: Inter `17`, `w600`, color `ink`.
- Elevacion: `0`.

## 4.5 Snackbar

- Fondo: `ink`.
- Texto: `paper`, Inter `w500`.
- Radio: `14`.

## 4.6 Checkbox

- Estado seleccionado: fill `forest`.
- Estado no seleccionado: fill `cloudSoft`.
- Check color: `paper`.
- Borde: `line`, ancho `1.5`.
- Radio: `5`.

## 5) Forma y espaciado (MVP)

- Radios principales:
  - `5` (controles pequenos, como checkbox)
  - `14` (inputs, snackbars)
  - `16` (cards)
  - `999` (acciones tipo pill)
- Espaciado vertical de controles primarios: `14` a `16`.
- Componentes con baja elevacion (estetica plana/editorial).

## 6) Modo claro/oscuro

- El cambio de tema se controla por `NivoThemeController`.
- Al cambiar modo:
  1. se actualiza la paleta activa,
  2. se aplican tokens a `NivoColors`,
  3. se reconstruye el arbol UI.

## 7) Source of truth

Para evitar drift entre documentacion y codigo, los archivos de verdad son:

- `mobile/nivo_mvp/lib/theme/nivo_colors.dart` (tokens y paletas)
- `mobile/nivo_mvp/lib/theme/nivo_theme.dart` (aplicacion de tokens en componentes)

Este documento resume y estandariza su uso para producto, diseno y desarrollo.
