import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';
import 'nivo_logo.dart';

/// Top bar común del MVP: logo NIVO · saldo compacto · avatar.
class NivoTopBar extends StatelessWidget {
  const NivoTopBar({
    super.key,
    required this.totalDisplay,
    required this.initials,
    this.onAvatarTap,
    this.onNotificationsTap,
    this.showBalance = true,
    this.action,
  });

  final String totalDisplay;
  final String initials;
  final VoidCallback? onAvatarTap;
  final VoidCallback? onNotificationsTap;
  final bool showBalance;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 10),
      child: Row(
        children: [
          const NivoLogo(size: 26),
          const Spacer(),
          if (showBalance)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: NivoColors.cloudSoft,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: NivoColors.line),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: NivoColors.forest,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    totalDisplay,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: NivoColors.ink,
                      letterSpacing: -0.2,
                    ),
                  ),
                ],
              ),
            ),
          const Spacer(),
          if (action != null) ...[
            action!,
            const SizedBox(width: 8),
          ] else ...[
            _GhostIcon(
              icon: Icons.notifications_none_rounded,
              onTap: onNotificationsTap,
            ),
            const SizedBox(width: 8),
          ],
          GestureDetector(
            onTap: onAvatarTap,
            child: Container(
              width: 34,
              height: 34,
              decoration: BoxDecoration(
                color: NivoColors.ink,
                shape: BoxShape.circle,
                border: Border.all(color: NivoColors.ink),
              ),
              alignment: Alignment.center,
              child: Text(
                initials,
                style: GoogleFonts.inter(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: NivoColors.paper,
                  letterSpacing: 0.2,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _GhostIcon extends StatelessWidget {
  const _GhostIcon({required this.icon, this.onTap});
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      shape: CircleBorder(side: BorderSide(color: NivoColors.line)),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: Icon(icon, size: 18, color: NivoColors.ink),
        ),
      ),
    );
  }
}
