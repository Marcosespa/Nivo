import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';

class NivoTabItem {
  const NivoTabItem({required this.icon, required this.label});
  final IconData icon;
  final String label;
}

/// Bottom nav flotante de 5 pestañas — activo = pill ink con label,
/// inactivos = solo icono. Inspirado en Revolut pero con paleta Nivo.
class NivoBottomTabs extends StatelessWidget {
  const NivoBottomTabs({
    super.key,
    required this.items,
    required this.index,
    required this.onChanged,
  });

  final List<NivoTabItem> items;
  final int index;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(12, 0, 12, 12),
      top: false,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
        decoration: BoxDecoration(
          color: NivoColors.paper,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: NivoColors.line),
          boxShadow: [
            BoxShadow(
              color: NivoColors.ink.withValues(alpha: 0.06),
              blurRadius: 24,
              offset: const Offset(0, 12),
            ),
          ],
        ),
        child: Row(
          children: [
            for (int i = 0; i < items.length; i++)
              Expanded(
                flex: i == index ? 14 : 8,
                child: _TabButton(
                  item: items[i],
                  active: i == index,
                  onTap: () => onChanged(i),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _TabButton extends StatelessWidget {
  const _TabButton({
    required this.item,
    required this.active,
    required this.onTap,
  });

  final NivoTabItem item;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 240),
        curve: Curves.easeOutCubic,
        margin: const EdgeInsets.symmetric(horizontal: 2),
        padding: EdgeInsets.symmetric(
          horizontal: active ? 14 : 10,
          vertical: 10,
        ),
        decoration: BoxDecoration(
          color: active ? NivoColors.ink : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              item.icon,
              size: 18,
              color: active ? NivoColors.paper : NivoColors.stone,
            ),
            if (active) ...[
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  item.label,
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: NivoColors.paper,
                    letterSpacing: -0.2,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
