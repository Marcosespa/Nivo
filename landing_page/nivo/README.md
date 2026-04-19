# Nivo Landing

Landing y narrativa de producto para **Nivo**.

**Tagline:** Tu plata, en otro nivel.

Nivo es una cuenta simple para Colombia y LATAM: pagos, tarjeta virtual, cambio entre COP/USD/EUR, crypto, acciones y recibos verificables. La marca evita nombres largos o demasiado técnicos y se apoya en una palabra corta, fácil de decir y con sensación futurista.

## Rutas

- `/` → Landing principal
- `/app` → Cuenta diaria, pagos y tarjeta
- `/monedas` → Cambio entre COP, USD y EUR
- `/invertir` → Crypto, acciones y ETFs por partners
- `/seguridad` → KYC, antifraude y recibos verificables
- `/empresas` → API, B2B y pymes digitales

## Desarrollo

```bash
npm install
npm run dev
npm run build
```

## Archivos clave

- `src/App.tsx` → rutas y páginas internas
- `src/components/ui/logo.tsx` → logo y wordmark Nivo
- `src/components/ui/hero-with-video.tsx` → hero principal con navbar local, email CTA y media Earth-at-night
- `src/data/media-content.ts` → hero principal
- `src/data/feature-tabs.tsx` → módulos de producto
- `src/sections/architecture.tsx` → modelo con aliados regulados
- `src/sections/category-framing.tsx` → posicionamiento frente a Nequi/Revolut
- `src/sections/flywheel.tsx` → CTA de beta

## Sistema visual

### Dirección de arte

La landing sigue una dirección visual sobria inspirada en `Apple`, `Notion` y `Cobre`:

- composición editorial y mucho espacio negativo
- paleta casi monocromática
- un solo acento verde profundo
- tipografía suiza / grotesk para titulares
- grids finos como textura matemática / criptográfica
- nada de neón, glassmorphism o Web3 genérico

### Paleta de color

| Token | HEX | Uso |
|---|---:|---|
| `nivo-ink` | `#000000` | texto principal, logo, fondos oscuros puntuales |
| `nivo-paper` | `#FFFFFF` | fondo base |
| `nivo-stone` | `#4A4A4A` | texto secundario principal |
| `nivo-stone-soft` | `#6B6B6B` | texto secundario suave |
| `nivo-mist` | `#9A9A9A` | meta labels, microcopy, ayudas |
| `nivo-cloud` | `#E5E5E5` | bordes suaves y superficies neutras |
| `nivo-cloud-soft` | `#F3F3F3` | fondos de cards, paneles tranquilos |
| `nivo-forest` | `#1A3C34` | acento principal, CTA, estados activos |
| `nivo-forest-soft` | `#254F46` | hover/acento secundario |
| `nivo-line` | `#D4D4D4` | líneas, separadores, bordes |

### Reglas de uso del color

- El sistema debe leerse `90% neutral`.
- El verde `forest` se reserva para:
  - CTA principal
  - estados activos
  - highlights PQC
  - algunos íconos funcionales
- Evitar que el verde domine fondos completos salvo en momentos muy puntuales.

### Tipografía

#### Display / titulares

Stack:

```txt
Neue Haas Grotesk Display Pro
Neue Haas Grotesk
Inter Display
Inter
```

Uso:

- `h1` a `h4`
- wordmark Nivo
- titulares de secciones
- titulares de cards importantes

Tracking:

- `tightest` = `-0.035em`
- `tighter-1` = `-0.025em`

#### Body / UI

Stack:

```txt
Inter
Inter Display
ui-sans-serif
system-ui
```

Uso:

- párrafos
- navegación
- formularios
- botones
- texto de soporte

#### Mono / técnico

Stack:

```txt
JetBrains Mono
SF Mono
Menlo
Consolas
monospace
```

Uso:

- badges
- labels de estado
- timestamps
- texto técnico / API

### Fondos, grids y sombras

- `bg-nivo-grid` y `bg-nivo-grid-fine` crean una textura matemática sutil
- `shadow-card` se usa para contenedores principales
- `shadow-subtle` para elevación mínima
- `shadow-forest` solo para énfasis ligado al color de acento

## Hero principal

El hero actual vive en `src/components/ui/hero-with-video.tsx`.

Características:

- navbar local dentro del hero
- título principal con CTA por email
- video de fondo alusivo a la Tierra de noche
- asset local:

```txt
public/assets/blackmarble_2016_rotate_720p.mp4
```

Referencia del asset:

- NASA SVS, `Black Marble 2016 (Rotating Globe)`

Uso:

- se integra desde `src/sections/hero.tsx`
- el navbar global se oculta solo en la home para evitar duplicación

## Favicon y marca

- `public/favicon.svg` → versión SVG del mark actual
- `public/favicon.ico` → versión `.ico` para navegadores con cache o soporte más tradicional
- `public/assets/nivo-mark.svg` → mark monocromático fuente de marca

## Documentación de estilos

La documentación del sistema visual queda repartida en:

- `README.md` → visión general de marca, color y tipografía
- `tailwind.config.js` → tokens y comentarios de uso
- `src/styles/globals.css` → baseline tipográfico y notas globales

## Nota de marca

Nivo queda como nombre público recomendado para la landing. Antes de producción conviene validar marca, dominio, redes y posibles conflictos legales en Colombia, LATAM y mercados donde se planee operar.
