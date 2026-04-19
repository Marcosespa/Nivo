import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';

class NivoTextField extends StatelessWidget {
  const NivoTextField({
    super.key,
    required this.label,
    this.hint,
    this.controller,
    this.obscure = false,
    this.keyboardType,
    this.textInputAction,
    this.autocorrect = true,
    this.onSubmitted,
    this.suffix,
  });

  final String label;
  final String? hint;
  final TextEditingController? controller;
  final bool obscure;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final bool autocorrect;
  final void Function(String)? onSubmitted;
  final Widget? suffix;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.2,
            color: NivoColors.stone,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          obscureText: obscure,
          keyboardType: keyboardType,
          textInputAction: textInputAction,
          autocorrect: autocorrect,
          onSubmitted: onSubmitted,
          style: GoogleFonts.inter(
            fontSize: 16,
            color: NivoColors.ink,
            fontWeight: FontWeight.w500,
          ),
          cursorColor: NivoColors.forest,
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: GoogleFonts.inter(
              color: NivoColors.mist,
              fontSize: 16,
            ),
            filled: true,
            fillColor: NivoColors.cloudSoft,
            contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
            suffixIcon: suffix,
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
          ),
        ),
      ],
    );
  }
}
