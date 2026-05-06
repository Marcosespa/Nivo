import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';

enum DemoViewState {
  success,
  loading,
  empty,
  error,
}

extension DemoViewStateX on DemoViewState {
  String get label => switch (this) {
        DemoViewState.success => 'Éxito',
        DemoViewState.loading => 'Cargando',
        DemoViewState.empty => 'Vacío',
        DemoViewState.error => 'Error',
      };

  IconData get icon => switch (this) {
        DemoViewState.success => Icons.check_circle_outline_rounded,
        DemoViewState.loading => Icons.hourglass_top_rounded,
        DemoViewState.empty => Icons.inbox_outlined,
        DemoViewState.error => Icons.error_outline_rounded,
      };
}

Future<void> showDemoStateSheet({
  required BuildContext context,
  required String tabLabel,
  required DemoViewState currentState,
  required ValueChanged<DemoViewState> onChanged,
}) {
  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: Colors.transparent,
    builder: (context) {
      return Container(
        decoration: BoxDecoration(
          color: NivoColors.paper,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        ),
        padding: const EdgeInsets.fromLTRB(24, 18, 24, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 42,
                height: 4,
                decoration: BoxDecoration(
                  color: NivoColors.line,
                  borderRadius: BorderRadius.circular(999),
                ),
              ),
            ),
            const SizedBox(height: 18),
            Text(
              'Vista demo · $tabLabel',
              style: GoogleFonts.jetBrainsMono(
                fontSize: 10,
                letterSpacing: 2,
                color: NivoColors.mist,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Cambiar estado de la pantalla',
              style: GoogleFonts.inter(
                fontSize: 22,
                fontWeight: FontWeight.w600,
                letterSpacing: -0.6,
                color: NivoColors.ink,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Úsalo para revisar loading, vacío, error y éxito dentro del mismo MVP visual.',
              style: GoogleFonts.inter(
                fontSize: 14,
                height: 1.5,
                color: NivoColors.stone,
              ),
            ),
            const SizedBox(height: 18),
            ...DemoViewState.values.map(
              (state) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: _StateOptionTile(
                  state: state,
                  active: state == currentState,
                  onTap: () {
                    Navigator.of(context).pop();
                    onChanged(state);
                  },
                ),
              ),
            ),
          ],
        ),
      );
    },
  );
}

class _StateOptionTile extends StatelessWidget {
  const _StateOptionTile({
    required this.state,
    required this.active,
    required this.onTap,
  });

  final DemoViewState state;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: active ? NivoColors.ink : NivoColors.cloudSoft,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              Icon(
                state.icon,
                size: 18,
                color: active ? NivoColors.paper : NivoColors.ink,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  state.label,
                  style: GoogleFonts.inter(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: active ? NivoColors.paper : NivoColors.ink,
                  ),
                ),
              ),
              if (active)
                Icon(
                  Icons.check_rounded,
                  size: 18,
                  color: NivoColors.paper,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class NivoEmptyState extends StatelessWidget {
  const NivoEmptyState({
    super.key,
    required this.title,
    required this.description,
    required this.icon,
    this.ctaLabel,
    this.onTap,
  });

  final String title;
  final String description;
  final IconData icon;
  final String? ctaLabel;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: NivoColors.cloudSoft,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: NivoColors.line),
              ),
              child: Icon(icon, size: 30, color: NivoColors.ink),
            ),
            const SizedBox(height: 20),
            Text(
              title,
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 24,
                fontWeight: FontWeight.w600,
                letterSpacing: -0.7,
                color: NivoColors.ink,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              description,
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 14,
                height: 1.5,
                color: NivoColors.stone,
              ),
            ),
            if (ctaLabel != null && onTap != null) ...[
              const SizedBox(height: 18),
              FilledButton(
                onPressed: onTap,
                child: Text(ctaLabel!),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class NivoErrorState extends StatelessWidget {
  const NivoErrorState({
    super.key,
    required this.title,
    required this.description,
    this.onRetry,
  });

  final String title;
  final String description;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 24),
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          color: NivoColors.cloudSoft,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: NivoColors.line),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.cloud_off_rounded,
              size: 30,
              color: NivoColors.ink,
            ),
            const SizedBox(height: 16),
            Text(
              title,
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 22,
                fontWeight: FontWeight.w600,
                letterSpacing: -0.6,
                color: NivoColors.ink,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              description,
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 14,
                height: 1.5,
                color: NivoColors.stone,
              ),
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 16),
              FilledButton(
                onPressed: onRetry,
                child: const Text('Reintentar'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class NivoLoadingBlock extends StatelessWidget {
  const NivoLoadingBlock({
    super.key,
    this.height = 16,
    this.width = double.infinity,
    this.radius = 12,
    this.margin,
  });

  final double height;
  final double width;
  final double radius;
  final EdgeInsets? margin;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: NivoColors.cloud,
        borderRadius: BorderRadius.circular(radius),
      ),
    );
  }
}
