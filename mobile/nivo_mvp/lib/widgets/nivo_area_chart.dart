import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';

/// Chart de área con eje Y implícito y etiquetas X. Animado una sola vez.
class NivoAreaChart extends StatefulWidget {
  const NivoAreaChart({
    super.key,
    required this.values,
    required this.xLabels,
    this.height = 200,
    this.lineColor,
    this.fillColor,
  });

  final List<double> values;
  final List<String> xLabels;
  final double height;
  final Color? lineColor;
  final Color? fillColor;

  @override
  State<NivoAreaChart> createState() => _NivoAreaChartState();
}

class _NivoAreaChartState extends State<NivoAreaChart>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..forward();
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final line = widget.lineColor ?? NivoColors.forest;
    return SizedBox(
      height: widget.height,
      width: double.infinity,
      child: AnimatedBuilder(
        animation: _c,
        builder: (_, __) => CustomPaint(
          painter: _AreaPainter(
            values: widget.values,
            xLabels: widget.xLabels,
            progress: Curves.easeOutCubic.transform(_c.value),
            line: line,
            fill: widget.fillColor ?? line.withValues(alpha: 0.14),
          ),
        ),
      ),
    );
  }
}

class _AreaPainter extends CustomPainter {
  _AreaPainter({
    required this.values,
    required this.xLabels,
    required this.progress,
    required this.line,
    required this.fill,
  });

  final List<double> values;
  final List<String> xLabels;
  final double progress;
  final Color line;
  final Color fill;

  @override
  void paint(Canvas canvas, Size size) {
    if (values.length < 2) return;

    final minV = values.reduce(math.min);
    final maxV = values.reduce(math.max);
    final range = (maxV - minV).abs() < 1e-6 ? 1.0 : maxV - minV;

    const padTop = 16.0;
    const padBottom = 26.0;
    const padX = 4.0;
    final plotW = size.width - padX * 2;
    final plotH = size.height - padTop - padBottom;

    final gridPaint = Paint()
      ..color = NivoColors.line.withValues(alpha: 0.55)
      ..strokeWidth = 0.6;
    for (int i = 0; i <= 3; i++) {
      final y = padTop + plotH * (i / 3);
      _dashLine(canvas, Offset(0, y), Offset(size.width, y), gridPaint);
    }

    final points = <Offset>[];
    for (int i = 0; i < values.length; i++) {
      final dx = padX + plotW * (i / (values.length - 1));
      final t = (values[i] - minV) / range;
      final dy = padTop + plotH * (1 - t);
      points.add(Offset(dx, dy));
    }

    final revealed =
        (points.length * progress).clamp(1.0, points.length.toDouble()).floor();
    final sub = points.sublist(0, math.max(1, revealed));

    final path = Path()..moveTo(sub.first.dx, sub.first.dy);
    for (int i = 1; i < sub.length; i++) {
      final p0 = sub[i - 1];
      final p1 = sub[i];
      final mid = Offset((p0.dx + p1.dx) / 2, (p0.dy + p1.dy) / 2);
      path.quadraticBezierTo(p0.dx, p0.dy, mid.dx, mid.dy);
    }
    path.lineTo(sub.last.dx, sub.last.dy);

    final areaPath = Path.from(path)
      ..lineTo(sub.last.dx, padTop + plotH)
      ..lineTo(sub.first.dx, padTop + plotH)
      ..close();
    final areaPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [fill, fill.withValues(alpha: 0)],
      ).createShader(Rect.fromLTWH(0, padTop, size.width, plotH));
    canvas.drawPath(areaPath, areaPaint);

    canvas.drawPath(
      path,
      Paint()
        ..color = line
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );

    // Marcador final
    final last = sub.last;
    canvas.drawCircle(last, 5, Paint()..color = NivoColors.paper);
    canvas.drawCircle(
      last,
      5,
      Paint()
        ..color = line
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );
    canvas.drawCircle(last, 2.2, Paint()..color = line);

    // X labels
    final textStyle = GoogleFonts.jetBrainsMono(
      fontSize: 9,
      letterSpacing: 1.2,
      color: NivoColors.mist,
      fontWeight: FontWeight.w500,
    );
    if (xLabels.isEmpty) return;
    final count = xLabels.length;
    for (int i = 0; i < count; i++) {
      final fx = i / (count - 1);
      final x = padX + plotW * fx;
      final tp = TextPainter(
        text: TextSpan(text: xLabels[i], style: textStyle),
        textDirection: TextDirection.ltr,
      )..layout();
      double dx = x - tp.width / 2;
      if (i == 0) dx = x;
      if (i == count - 1) dx = x - tp.width;
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
      final s = p1 + dir * covered;
      final e = p1 + dir * math.min(covered + dash, total);
      canvas.drawLine(s, e, paint);
      covered += dash + gap;
    }
  }

  @override
  bool shouldRepaint(covariant _AreaPainter old) =>
      old.progress != progress || old.values != values;
}
