import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../data/fintech_mvp_content.dart';
import '../theme/nivo_colors.dart';

class NivoSparkline extends StatelessWidget {
  const NivoSparkline({
    super.key,
    required this.points,
    this.lineColor = NivoColors.forest,
    this.fillColor,
    this.strokeWidth = 2.4,
  });

  final List<double> points;
  final Color lineColor;
  final Color? fillColor;
  final double strokeWidth;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _SparklinePainter(
        points: points,
        lineColor: lineColor,
        fillColor: fillColor ?? lineColor.withValues(alpha: 0.08),
        strokeWidth: strokeWidth,
      ),
      child: const SizedBox.expand(),
    );
  }
}

class _SparklinePainter extends CustomPainter {
  _SparklinePainter({
    required this.points,
    required this.lineColor,
    required this.fillColor,
    required this.strokeWidth,
  });

  final List<double> points;
  final Color lineColor;
  final Color fillColor;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    if (points.length < 2) return;

    final minValue = points.reduce(math.min);
    final maxValue = points.reduce(math.max);
    final range =
        (maxValue - minValue).abs() < 0.0001 ? 1.0 : maxValue - minValue;

    Offset mapPoint(int index) {
      final x = size.width * index / (points.length - 1);
      final normalized = (points[index] - minValue) / range;
      final y = size.height - (normalized * size.height);
      return Offset(x, y.clamp(0, size.height));
    }

    final linePath = Path()..moveTo(mapPoint(0).dx, mapPoint(0).dy);
    for (var i = 1; i < points.length; i++) {
      final point = mapPoint(i);
      linePath.lineTo(point.dx, point.dy);
    }

    final fillPath = Path.from(linePath)
      ..lineTo(size.width, size.height)
      ..lineTo(0, size.height)
      ..close();

    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.fill;
    canvas.drawPath(fillPath, fillPaint);

    final strokePaint = Paint()
      ..color = lineColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    canvas.drawPath(linePath, strokePaint);
  }

  @override
  bool shouldRepaint(covariant _SparklinePainter oldDelegate) {
    return oldDelegate.points != points ||
        oldDelegate.lineColor != lineColor ||
        oldDelegate.fillColor != fillColor ||
        oldDelegate.strokeWidth != strokeWidth;
  }
}

class NivoScoreRing extends StatelessWidget {
  const NivoScoreRing({
    super.key,
    required this.value,
    this.size = 112,
    this.thickness = 10,
    this.color = NivoColors.forest,
    this.backgroundColor = NivoColors.cloud,
    this.child,
  });

  final double value;
  final double size;
  final double thickness;
  final Color color;
  final Color backgroundColor;
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    final clampedValue = value.clamp(0, 1).toDouble();

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          CustomPaint(
            size: Size.square(size),
            painter: _ScoreRingPainter(
              value: clampedValue,
              thickness: thickness,
              color: color,
              backgroundColor: backgroundColor,
            ),
          ),
          if (child != null) child!,
        ],
      ),
    );
  }
}

class NivoCandlestickChart extends StatelessWidget {
  const NivoCandlestickChart({
    super.key,
    required this.candles,
  });

  final List<CandlePoint> candles;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _CandlestickPainter(candles: candles),
      child: const SizedBox.expand(),
    );
  }
}

class _CandlestickPainter extends CustomPainter {
  _CandlestickPainter({required this.candles});

  final List<CandlePoint> candles;

  @override
  void paint(Canvas canvas, Size size) {
    if (candles.isEmpty) return;

    final maxValue = candles
        .map((candle) => candle.high)
        .reduce((value, element) => math.max(value, element));
    final minValue = candles
        .map((candle) => candle.low)
        .reduce((value, element) => math.min(value, element));
    final range =
        (maxValue - minValue).abs() < 0.001 ? 1.0 : maxValue - minValue;

    double normalize(double value) {
      final mapped = (value - minValue) / range;
      return size.height - (mapped * size.height);
    }

    final slotWidth = size.width / candles.length;
    final candleWidth = slotWidth * 0.42;

    final gridPaint = Paint()
      ..color = NivoColors.line
      ..strokeWidth = 1;

    for (var i = 1; i < 4; i++) {
      final y = size.height * (i / 4);
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    for (var i = 0; i < candles.length; i++) {
      final candle = candles[i];
      final centerX = slotWidth * i + slotWidth / 2;
      final isUp = candle.close >= candle.open;
      final color = isUp ? NivoColors.forest : NivoColors.ink;

      final wickPaint = Paint()
        ..color = color
        ..strokeWidth = 1.3;

      canvas.drawLine(
        Offset(centerX, normalize(candle.high)),
        Offset(centerX, normalize(candle.low)),
        wickPaint,
      );

      final openY = normalize(candle.open);
      final closeY = normalize(candle.close);
      final top = math.min(openY, closeY);
      final bottom = math.max(openY, closeY);

      final bodyRect = Rect.fromLTWH(
        centerX - candleWidth / 2,
        top,
        candleWidth,
        math.max(2, bottom - top),
      );

      final bodyPaint = Paint()
        ..color = isUp ? NivoColors.forest : NivoColors.ink
        ..style = isUp ? PaintingStyle.stroke : PaintingStyle.fill
        ..strokeWidth = 1.4;

      if (isUp) {
        canvas.drawRect(bodyRect, bodyPaint);
      } else {
        canvas.drawRect(bodyRect, bodyPaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _CandlestickPainter oldDelegate) {
    return oldDelegate.candles != candles;
  }
}

class _ScoreRingPainter extends CustomPainter {
  _ScoreRingPainter({
    required this.value,
    required this.thickness,
    required this.color,
    required this.backgroundColor,
  });

  final double value;
  final double thickness;
  final Color color;
  final Color backgroundColor;

  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final radius = (size.shortestSide - thickness) / 2;
    final rect = Rect.fromCircle(center: center, radius: radius);

    final trackPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = thickness
      ..strokeCap = StrokeCap.round;

    final progressPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = thickness
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(rect, -math.pi / 2, math.pi * 2, false, trackPaint);
    canvas.drawArc(
        rect, -math.pi / 2, math.pi * 2 * value, false, progressPaint);
  }

  @override
  bool shouldRepaint(covariant _ScoreRingPainter oldDelegate) {
    return oldDelegate.value != value ||
        oldDelegate.thickness != thickness ||
        oldDelegate.color != color ||
        oldDelegate.backgroundColor != backgroundColor;
  }
}
