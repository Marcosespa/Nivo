import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../data/nivo_app_content.dart';
import '../theme/nivo_colors.dart';

/// Mini candlestick chart editorial (sin librerías externas).
class NivoCandles extends StatelessWidget {
  const NivoCandles({
    super.key,
    required this.candles,
    this.height = 200,
  });

  final List<Candle> candles;
  final double height;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      width: double.infinity,
      child: CustomPaint(
        painter: _CandlePainter(candles: candles),
      ),
    );
  }
}

class _CandlePainter extends CustomPainter {
  _CandlePainter({required this.candles});
  final List<Candle> candles;

  @override
  void paint(Canvas canvas, Size size) {
    if (candles.isEmpty) return;

    double minV = candles.first.low;
    double maxV = candles.first.high;
    for (final c in candles) {
      minV = math.min(minV, c.low);
      maxV = math.max(maxV, c.high);
    }
    final range = maxV - minV == 0 ? 1 : maxV - minV;

    const padTop = 16.0;
    const padBottom = 24.0;
    const padLeft = 40.0;
    const padRight = 4.0;
    final plotW = size.width - padLeft - padRight;
    final plotH = size.height - padTop - padBottom;

    // Grid horizontal
    final gridPaint = Paint()
      ..color = NivoColors.line.withValues(alpha: 0.55)
      ..strokeWidth = 0.6;
    final textStyle = GoogleFonts.jetBrainsMono(
      fontSize: 9,
      letterSpacing: 1.1,
      color: NivoColors.mist,
      fontWeight: FontWeight.w500,
    );
    const rows = 4;
    for (int i = 0; i <= rows; i++) {
      final y = padTop + plotH * (i / rows);
      _dashLine(
        canvas,
        Offset(padLeft, y),
        Offset(size.width - padRight, y),
        gridPaint,
      );
      final value = maxV - range * (i / rows);
      final label = value.toStringAsFixed(1);
      final tp = TextPainter(
        text: TextSpan(text: label, style: textStyle),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, Offset(padLeft - tp.width - 6, y - tp.height / 2));
    }

    // Candles
    final spacing = plotW / candles.length;
    final bodyW = math.max(3.0, spacing * 0.55);

    for (int i = 0; i < candles.length; i++) {
      final c = candles[i];
      final cx = padLeft + spacing * (i + 0.5);

      double map(double v) => padTop + plotH * (1 - (v - minV) / range);

      final isUp = c.close >= c.open;
      final bodyTop = map(math.max(c.open, c.close));
      final bodyBottom = map(math.min(c.open, c.close));
      final wickTop = map(c.high);
      final wickBottom = map(c.low);

      final color = isUp ? NivoColors.forest : NivoColors.ink;

      // Wick
      canvas.drawLine(
        Offset(cx, wickTop),
        Offset(cx, wickBottom),
        Paint()
          ..color = color
          ..strokeWidth = 1.1,
      );

      // Body
      final bodyRect = Rect.fromLTRB(
        cx - bodyW / 2,
        bodyTop,
        cx + bodyW / 2,
        bodyBottom == bodyTop ? bodyTop + 1 : bodyBottom,
      );
      canvas.drawRRect(
        RRect.fromRectAndRadius(bodyRect, const Radius.circular(2)),
        Paint()..color = color,
      );
    }

    // X labels (primero, medio, último)
    final xLabels = ['09:30', '12:00', '15:30', '18:00'];
    const divs = 3;
    for (int i = 0; i <= divs; i++) {
      final x = padLeft + plotW * (i / divs);
      final tp = TextPainter(
        text: TextSpan(text: xLabels[i], style: textStyle),
        textDirection: TextDirection.ltr,
      )..layout();
      double dx = x - tp.width / 2;
      if (i == 0) dx = x;
      if (i == divs) dx = x - tp.width;
      tp.paint(canvas, Offset(dx, size.height - padBottom + 8));
    }
  }

  void _dashLine(Canvas canvas, Offset p1, Offset p2, Paint paint) {
    const dash = 2.5;
    const gap = 3.0;
    final total = (p2 - p1).distance;
    if (total == 0) return;
    final dir = (p2 - p1) / total;
    double covered = 0;
    while (covered < total) {
      final start = p1 + dir * covered;
      final end = p1 + dir * math.min(covered + dash, total);
      canvas.drawLine(start, end, paint);
      covered += dash + gap;
    }
  }

  @override
  bool shouldRepaint(covariant _CandlePainter old) => old.candles != candles;
}
