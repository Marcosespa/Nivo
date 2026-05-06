import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'nivo_colors.dart';

abstract final class NivoTheme {
  static ThemeData light() => _build(NivoPalette.light);
  static ThemeData dark() => _build(NivoPalette.dark);
  static ThemeData fromController() =>
      _build(NivoThemeController.instance.palette);

  static ThemeData _build(NivoPalette p) {
    final base = ThemeData(
      useMaterial3: true,
      brightness: p.brightness,
      colorScheme: ColorScheme(
        brightness: p.brightness,
        surface: p.paper,
        onSurface: p.ink,
        primary: p.forest,
        onPrimary: p.brightness == Brightness.dark ? p.ink : p.paper,
        secondary: p.stone,
        onSecondary: p.paper,
        error: const Color(0xFFE05A4B),
        onError: p.paper,
        outline: p.line,
      ),
      scaffoldBackgroundColor: p.paper,
      dividerColor: p.line,
    );

    return base.copyWith(
      textTheme: GoogleFonts.interTextTheme(base.textTheme).apply(
        bodyColor: p.ink,
        displayColor: p.ink,
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: p.paper.withValues(alpha: 0.92),
        foregroundColor: p.ink,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 17,
          fontWeight: FontWeight.w600,
          color: p.ink,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: p.line),
        ),
        color: p.cloudSoft,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: p.forest,
          foregroundColor: p.brightness == Brightness.dark ? p.ink : p.paper,
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          textStyle: GoogleFonts.inter(
            fontWeight: FontWeight.w600,
            fontSize: 14,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: p.ink,
          side: BorderSide(color: p.ink),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: p.ink,
        contentTextStyle: GoogleFonts.inter(
          color: p.paper,
          fontWeight: FontWeight.w500,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: p.cloudSoft,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: p.line),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: p.line),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: p.forest, width: 1.5),
        ),
        hintStyle: GoogleFonts.inter(color: p.mist, fontSize: 16),
        labelStyle: GoogleFonts.inter(
          color: p.stone,
          fontWeight: FontWeight.w600,
          fontSize: 12,
        ),
      ),
      checkboxTheme: CheckboxThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return p.forest;
          }
          return p.cloudSoft;
        }),
        checkColor: WidgetStateProperty.all(p.paper),
        side: BorderSide(color: p.line, width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(5)),
      ),
    );
  }
}
