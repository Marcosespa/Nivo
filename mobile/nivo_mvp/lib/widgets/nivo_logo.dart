import 'package:flutter/material.dart';

import '../theme/nivo_colors.dart';

enum NivoLogoTone { ink, paper }

/// Marca simplificada (rectángulo redondeado + “N”) inspirada en el SVG de la web.
class NivoLogo extends StatelessWidget {
  const NivoLogo({
    super.key,
    this.size = 36,
    this.tone = NivoLogoTone.ink,
  });

  final double size;
  final NivoLogoTone tone;

  @override
  Widget build(BuildContext context) {
    final foreground =
        tone == NivoLogoTone.ink ? NivoColors.ink : NivoColors.paper;
    final inverse =
        tone == NivoLogoTone.ink ? NivoColors.paper : NivoColors.ink;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: foreground,
            borderRadius: BorderRadius.circular(size * 0.19),
          ),
          child: Center(
            child: CustomPaint(
              size: Size(size * 0.45, size * 0.45),
              painter: _NivoMarkPainter(color: inverse),
            ),
          ),
        ),
        SizedBox(width: size * 0.28),
        Text(
          'Nivo',
          style: TextStyle(
            fontSize: size * 0.58,
            fontWeight: FontWeight.w600,
            letterSpacing: -0.8,
            color: foreground,
            height: 1,
          ),
        ),
      ],
    );
  }
}

class _NivoMarkPainter extends CustomPainter {
  _NivoMarkPainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = size.shortestSide * 0.12
      ..strokeCap = StrokeCap.square;

    final w = size.width;
    final h = size.height;
    final p = size.shortestSide * 0.08;

    // N estilizada (dos trazos)
    canvas.drawLine(Offset(p, h - p), Offset(p, p), paint);
    canvas.drawLine(Offset(p, p), Offset(w - p, h - p), paint);
    canvas.drawLine(Offset(w - p, h - p), Offset(w - p, p), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
