import 'package:flutter/material.dart';

/// Tokens alineados con la landing (`tailwind.config.js` / `globals.css`).
///
/// Los campos no son `const` a propósito: el MVP soporta dark mode aplicando
/// una paleta distinta vía [NivoThemeController] + [NivoColors.apply].
abstract final class NivoColors {
  static Color ink = NivoPalette.light.ink;
  static Color paper = NivoPalette.light.paper;
  static Color stone = NivoPalette.light.stone;
  static Color stoneSoft = NivoPalette.light.stoneSoft;
  static Color mist = NivoPalette.light.mist;
  static Color cloud = NivoPalette.light.cloud;
  static Color cloudSoft = NivoPalette.light.cloudSoft;
  static Color forest = NivoPalette.light.forest;
  static Color forestSoft = NivoPalette.light.forestSoft;
  static Color line = NivoPalette.light.line;

  static void apply(NivoPalette palette) {
    ink = palette.ink;
    paper = palette.paper;
    stone = palette.stone;
    stoneSoft = palette.stoneSoft;
    mist = palette.mist;
    cloud = palette.cloud;
    cloudSoft = palette.cloudSoft;
    forest = palette.forest;
    forestSoft = palette.forestSoft;
    line = palette.line;
  }
}

/// Paleta inmutable para un modo concreto del MVP.
@immutable
class NivoPalette {
  const NivoPalette({
    required this.ink,
    required this.paper,
    required this.stone,
    required this.stoneSoft,
    required this.mist,
    required this.cloud,
    required this.cloudSoft,
    required this.forest,
    required this.forestSoft,
    required this.line,
    required this.brightness,
  });

  final Color ink;
  final Color paper;
  final Color stone;
  final Color stoneSoft;
  final Color mist;
  final Color cloud;
  final Color cloudSoft;
  final Color forest;
  final Color forestSoft;
  final Color line;
  final Brightness brightness;

  static const NivoPalette light = NivoPalette(
    ink: Color(0xFF000000),
    paper: Color(0xFFFFFFFF),
    stone: Color(0xFF4A4A4A),
    stoneSoft: Color(0xFF6B6B6B),
    mist: Color(0xFF9A9A9A),
    cloud: Color(0xFFE5E5E5),
    cloudSoft: Color(0xFFF3F3F3),
    forest: Color(0xFF1A3C34),
    forestSoft: Color(0xFF254F46),
    line: Color(0xFFD4D4D4),
    brightness: Brightness.light,
  );

  /// Dark mode mantiene tonalidad "editorial": fondo off-black, texto warm-white,
  /// verde forest ligeramente más brillante para legibilidad.
  static const NivoPalette dark = NivoPalette(
    ink: Color(0xFFF4F4F1),
    paper: Color(0xFF0B0B0B),
    stone: Color(0xFFB8B8B6),
    stoneSoft: Color(0xFF9E9E9C),
    mist: Color(0xFF6F6F6D),
    cloud: Color(0xFF242424),
    cloudSoft: Color(0xFF161616),
    forest: Color(0xFF8FE3C5),
    forestSoft: Color(0xFF5FC1A0),
    line: Color(0xFF2A2A2A),
    brightness: Brightness.dark,
  );
}

/// Controller global para el toggle de modo claro/oscuro del MVP.
///
/// Al cambiar el modo:
///  1. Se actualiza la paleta estática en [NivoColors] (afecta a widgets que la
///     leen directamente).
///  2. Se notifica a los listeners para que el árbol se reconstruya.
class NivoThemeController extends ChangeNotifier {
  NivoThemeController._();
  static final NivoThemeController instance = NivoThemeController._();

  NivoPalette _palette = NivoPalette.light;
  NivoPalette get palette => _palette;
  Brightness get brightness => _palette.brightness;
  bool get isDark => _palette.brightness == Brightness.dark;

  void toggle() => setDark(!isDark);

  void setDark(bool value) {
    final next = value ? NivoPalette.dark : NivoPalette.light;
    if (next == _palette) return;
    _palette = next;
    NivoColors.apply(next);
    notifyListeners();
  }
}
