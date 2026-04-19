# Nivo MVP (Flutter)

MVP visual móvil de **Nivo** con estructura tipo fintech global, inspirado en la claridad operativa de Revolut pero adaptado al lenguaje editorial de Nivo: más limpio, más sobrio y en **modo claro** como referencia principal.

## Requisitos

- [Flutter SDK](https://docs.flutter.dev/get-started/install) estable (3.16+ recomendado).
- Xcode (iOS) y/o Android Studio / SDK (Android) para compilar en dispositivo o emulador.

## Primera vez en esta carpeta

Si solo tienes `lib/` y `pubspec.yaml` y **faltan** las carpetas `android/` e `ios/`:

```bash
cd mobile/nivo_mvp
flutter create . --project-name nivo_mvp --org money.nivo
```

Esto añade plataformas sin borrar tu `lib/`. Luego:

```bash
flutter pub get
flutter run
```

## Comandos útiles

```bash
flutter analyze
flutter test
flutter build apk        # Android
flutter build ios        # iOS (macOS + Xcode)
```

## Flujo actual

La app arranca directamente en el **shell principal** para revisar el MVP visual sin fricción.

Rutas de apoyo que siguen disponibles:

1. **Landing** — scroll narrativo + mock del producto.
2. **Login / Registro** — pantallas de acceso de maqueta.
3. **Home shell** — navegación principal de producto.

## Qué se diseñó en esta iteración

- **Top bar global** con logo Nivo, saldo total y avatar.
- **Bottom tab bar de 5 pestañas**:
  - Home
  - Movimientos
  - Divisas
  - Trading
  - Crypto
- **Home simplificado**:
  - saldo prominente
  - 4 tarjetas rápidas
  - acciones grandes
  - acceso a dashboard expandido por modal
- **Movimientos**:
  - búsqueda
  - filtros
  - lista con detalle en modal
  - estado vacío bonito
- **Divisas**:
  - balances multi-currency
  - convertidor
  - mini chart de tasa
  - confirmación de cambio
- **Trading**:
  - búsqueda de acciones
  - posiciones abiertas
  - gráfico candlestick simple
  - buy / sell
  - watchlist
- **Crypto**:
  - saldo total
  - holdings
  - gráfico del activo seleccionado
  - tendencias
- **Estados demo completos** por pestaña:
  - éxito
  - loading
  - vacío
  - error
- **Landing narrativa y auth** siguen presentes como soporte de demo.

## Estructura

| Ruta | Rol |
|------|-----|
| `lib/main.dart` | `MaterialApp`, rutas nombradas |
| `lib/navigation/` | `AppNavigator` + transiciones (`slideFade`, `authSwap`, `fadeThrough`) |
| `lib/theme/` | Colores, inputs, snackbars, checkboxes (alineado a la web) |
| `lib/utils/nivo_formatters.dart` | Formateo simple de dinero, porcentaje y unidades |
| `lib/data/landing_content.dart` | Textos landing (editable) |
| `lib/data/app_preview_content.dart` | Datos mock del producto móvil |
| `lib/data/fintech_mvp_content.dart` | Datos mock del nuevo MVP fintech |
| `lib/screens/landing_screen.dart` | Scroll + animación + mock del producto |
| `lib/screens/auth/` | Login y registro |
| `lib/screens/post_auth_home_screen.dart` | Shell principal con top bar + bottom tabs |
| `lib/screens/app/` | Home, Movimientos, Divisas, Trading y Crypto |
| `lib/widgets/demo_preview.dart` | Estados demo y vistas empty/error/loading |
| `lib/widgets/nivo_app_chrome.dart` | Top bar, bottom tabs y superficies |
| `lib/widgets/nivo_charts.dart` | Sparkline, score ring y candlestick simple |
| `lib/widgets/` | Logo, campos, `FadeInUp`, frase rotativa y utilidades |

## Dirección visual

- **90% neutro**: blanco, negro, grises piedra
- **acento único**: `forest`
- **modo claro** como base del MVP
- **sin gradientes candy**
- **sin UI cripto-especulativa**
- **copy operativo** dentro del shell, no marketing de landing
- **una sola idea dominante por bloque**

## Nota legal / producto

Los textos son **presentación**; validá claims regulatorios y de mercado antes de publicar en tiendas.
