import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';
import 'nivo_logo.dart';

class NivoTopBar extends StatelessWidget {
  const NivoTopBar({
    super.key,
    required this.totalBalance,
    required this.onAvatarTap,
    this.brand = 'NIVO',
  });

  final String brand;
  final String totalBalance;
  final VoidCallback onAvatarTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 6),
      child: Row(
        children: [
          const Expanded(
            flex: 2,
            child: Align(
              alignment: Alignment.centerLeft,
              child: NivoLogo(size: 30),
            ),
          ),
          Expanded(
            flex: 3,
            child: Center(
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: NivoColors.cloudSoft,
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: NivoColors.line),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      brand,
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 8,
                        letterSpacing: 1.6,
                        color: NivoColors.mist,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      totalBalance,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        letterSpacing: -0.3,
                        color: NivoColors.ink,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Align(
              alignment: Alignment.centerRight,
              child: GestureDetector(
                onTap: onAvatarTap,
                child: Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: NivoColors.ink,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Center(
                    child: Text(
                      'ME',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: NivoColors.paper,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class NivoBottomTabBar extends StatelessWidget {
  const NivoBottomTabBar({
    super.key,
    required this.currentIndex,
    required this.items,
    required this.onChanged,
  });

  final int currentIndex;
  final List<NivoTabItem> items;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        decoration: BoxDecoration(
          color: NivoColors.paper,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: NivoColors.line),
          boxShadow: [
            BoxShadow(
              color: NivoColors.ink.withValues(alpha: 0.08),
              blurRadius: 28,
              offset: const Offset(0, 14),
            ),
          ],
        ),
        child: Row(
          children: List.generate(items.length, (index) {
            final item = items[index];
            final active = currentIndex == index;
            return Expanded(
              child: GestureDetector(
                onTap: () => onChanged(index),
                behavior: HitTestBehavior.opaque,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 220),
                  curve: Curves.easeOutCubic,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  decoration: BoxDecoration(
                    color: active ? NivoColors.ink : Colors.transparent,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        item.icon,
                        size: 20,
                        color: active ? NivoColors.paper : NivoColors.stone,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        item.label,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        softWrap: false,
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: active ? NivoColors.paper : NivoColors.stone,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }),
        ),
      ),
    );
  }
}

class NivoTabItem {
  const NivoTabItem({
    required this.label,
    required this.icon,
  });

  final String label;
  final IconData icon;
}

class NivoSurface extends StatelessWidget {
  const NivoSurface({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(18),
    this.color,
    this.radius = 26,
  });

  final Widget child;
  final EdgeInsets padding;
  final Color? color;
  final double radius;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: color ?? NivoColors.paper,
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: NivoColors.line),
      ),
      child: child,
    );
  }
}

class NivoSectionHeader extends StatelessWidget {
  const NivoSectionHeader({
    super.key,
    required this.kicker,
    required this.title,
    this.subtitle,
    this.trailing,
  });

  final String kicker;
  final String title;
  final String? subtitle;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                kicker.toUpperCase(),
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 10,
                  letterSpacing: 2,
                  color: NivoColors.mist,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: GoogleFonts.inter(
                  fontSize: 22,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.6,
                  color: NivoColors.ink,
                ),
              ),
              if (subtitle != null) ...[
                const SizedBox(height: 6),
                Text(
                  subtitle!,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    height: 1.5,
                    color: NivoColors.stone,
                  ),
                ),
              ],
            ],
          ),
        ),
        if (trailing != null) ...[
          const SizedBox(width: 12),
          trailing!,
        ],
      ],
    );
  }
}

class NivoSearchField extends StatelessWidget {
  const NivoSearchField({
    super.key,
    required this.controller,
    required this.hint,
    this.onChanged,
  });

  final TextEditingController controller;
  final String hint;
  final ValueChanged<String>? onChanged;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      onChanged: onChanged,
      decoration: InputDecoration(
        hintText: hint,
        prefixIcon: const Icon(Icons.search_rounded, size: 20),
        suffixIcon: controller.text.isEmpty
            ? null
            : IconButton(
                onPressed: () {
                  controller.clear();
                  onChanged?.call('');
                },
                icon: const Icon(Icons.close_rounded, size: 18),
              ),
      ),
    );
  }
}

class NivoSegmentedControl extends StatelessWidget {
  const NivoSegmentedControl({
    super.key,
    required this.labels,
    required this.selectedIndex,
    required this.onChanged,
  });

  final List<String> labels;
  final int selectedIndex;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: NivoColors.cloudSoft,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: NivoColors.line),
      ),
      child: Row(
        children: List.generate(labels.length, (index) {
          final active = index == selectedIndex;
          return Expanded(
            child: GestureDetector(
              onTap: () => onChanged(index),
              behavior: HitTestBehavior.opaque,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 220),
                curve: Curves.easeOutCubic,
                padding: const EdgeInsets.symmetric(
                  vertical: 10,
                  horizontal: 6,
                ),
                decoration: BoxDecoration(
                  color: active ? NivoColors.ink : Colors.transparent,
                  borderRadius: BorderRadius.circular(999),
                ),
                // FittedBox reduce el tamaño del label sólo cuando no cabe,
                // evitando que "Transferencias" parta a dos líneas.
                child: FittedBox(
                  fit: BoxFit.scaleDown,
                  alignment: Alignment.center,
                  child: Text(
                    labels[index],
                    textAlign: TextAlign.center,
                    maxLines: 1,
                    softWrap: false,
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: active ? NivoColors.paper : NivoColors.stone,
                    ),
                  ),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
}
