import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'nivo_colors.dart';

abstract final class NivoTheme {
  static ThemeData light() {
    final base = ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: const ColorScheme.light(
        surface: NivoColors.paper,
        onSurface: NivoColors.ink,
        primary: NivoColors.forest,
        onPrimary: NivoColors.paper,
        secondary: NivoColors.stone,
        outline: NivoColors.line,
      ),
      scaffoldBackgroundColor: NivoColors.paper,
      dividerColor: NivoColors.line,
    );

    return base.copyWith(
      textTheme: GoogleFonts.interTextTheme(base.textTheme).apply(
        bodyColor: NivoColors.ink,
        displayColor: NivoColors.ink,
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: NivoColors.paper.withValues(alpha: 0.92),
        foregroundColor: NivoColors.ink,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 17,
          fontWeight: FontWeight.w600,
          color: NivoColors.ink,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: NivoColors.line),
        ),
        color: NivoColors.cloudSoft,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: NivoColors.forest,
          foregroundColor: NivoColors.paper,
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
          foregroundColor: NivoColors.ink,
          side: const BorderSide(color: NivoColors.ink),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: NivoColors.ink,
        contentTextStyle: GoogleFonts.inter(
          color: NivoColors.paper,
          fontWeight: FontWeight.w500,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: NivoColors.cloudSoft,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: NivoColors.line),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: NivoColors.line),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: NivoColors.forest, width: 1.5),
        ),
        hintStyle: GoogleFonts.inter(color: NivoColors.mist, fontSize: 16),
        labelStyle: GoogleFonts.inter(
          color: NivoColors.stone,
          fontWeight: FontWeight.w600,
          fontSize: 12,
        ),
      ),
      checkboxTheme: CheckboxThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return NivoColors.forest;
          }
          return NivoColors.cloudSoft;
        }),
        checkColor: WidgetStateProperty.all(NivoColors.paper),
        side: const BorderSide(color: NivoColors.line, width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(5)),
      ),
    );
  }
}
