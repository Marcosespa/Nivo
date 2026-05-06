import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';

class NivoSectionTitle extends StatelessWidget {
  const NivoSectionTitle({
    super.key,
    required this.eyebrow,
    required this.title,
    this.trailing,
    this.description,
  });

  final String eyebrow;
  final String title;
  final Widget? trailing;
  final String? description;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    eyebrow.toUpperCase(),
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 10,
                      letterSpacing: 2.2,
                      color: NivoColors.mist,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    title,
                    style: GoogleFonts.inter(
                      fontSize: 20,
                      fontWeight: FontWeight.w600,
                      letterSpacing: -0.6,
                      color: NivoColors.ink,
                    ),
                  ),
                ],
              ),
            ),
            if (trailing != null) trailing!,
          ],
        ),
        if (description != null) ...[
          const SizedBox(height: 6),
          Text(
            description!,
            style: GoogleFonts.inter(
              fontSize: 13,
              height: 1.45,
              color: NivoColors.stone,
            ),
          ),
        ],
      ],
    );
  }
}
