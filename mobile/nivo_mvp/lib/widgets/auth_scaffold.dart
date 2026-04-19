import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';
import 'nivo_logo.dart';

/// Layout común para login / registro: fondo limpio, logo, título editorial.
class AuthScaffold extends StatelessWidget {
  const AuthScaffold({
    super.key,
    required this.title,
    required this.subtitle,
    required this.child,
    this.showBack = true,
  });

  final String title;
  final String subtitle;
  final Widget child;
  final bool showBack;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NivoColors.paper,
      body: SafeArea(
        child: CustomScrollView(
          physics: const BouncingScrollPhysics(),
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(8, 4, 12, 0),
                child: Row(
                  children: [
                    if (showBack)
                      IconButton(
                        onPressed: () => Navigator.of(context).maybePop(),
                        icon: const Icon(Icons.arrow_back_ios_new_rounded,
                            size: 20),
                        color: NivoColors.ink,
                        tooltip: 'Volver',
                      )
                    else
                      const SizedBox(width: 48),
                    const Expanded(child: Center(child: NivoLogo(size: 30))),
                    const SizedBox(width: 48),
                  ],
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(24, 28, 24, 40),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: NivoColors.cloudSoft,
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(color: NivoColors.line),
                    ),
                    child: Text(
                      'VISTA PREVIA DEL FLUJO',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 9,
                        letterSpacing: 1.8,
                        fontWeight: FontWeight.w600,
                        color: NivoColors.stone,
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    title,
                    style: GoogleFonts.inter(
                      fontSize: 32,
                      fontWeight: FontWeight.w600,
                      height: 1.08,
                      letterSpacing: -1.1,
                      color: NivoColors.ink,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    subtitle,
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      height: 1.5,
                      color: NivoColors.stone,
                    ),
                  ),
                  const SizedBox(height: 18),
                  const Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _AuthHintPill(label: 'PQC activo'),
                      _AuthHintPill(label: 'Recibos verificables'),
                      _AuthHintPill(label: 'Diseño Nivo'),
                    ],
                  ),
                  const SizedBox(height: 32),
                  child,
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AuthHintPill extends StatelessWidget {
  const _AuthHintPill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: NivoColors.paper,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: NivoColors.line),
      ),
      child: Text(
        label,
        style: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: NivoColors.ink,
        ),
      ),
    );
  }
}
