import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../utils/nivo_formatters.dart';

/// Saldo animado estilo "flip counter": al cambiar [value] anima suavemente
/// desde el valor anterior al nuevo, formateado como moneda.
///
/// Pensado para el hero del Home, el pill del top bar y la vista expandida
/// del dashboard. En el MVP el valor viene hardcoded, pero los switches de
/// estado y los toggles de modo disparan rebuilds que activan la animación.
class NivoAnimatedBalance extends StatefulWidget {
  const NivoAnimatedBalance({
    super.key,
    required this.value,
    required this.style,
    this.symbol = '€',
    this.decimals = 2,
    this.duration = const Duration(milliseconds: 900),
    this.curve = Curves.easeOutCubic,
    this.textAlign,
    this.initialFromZero = true,
  });

  final double value;
  final TextStyle style;
  final String symbol;
  final int decimals;
  final Duration duration;
  final Curve curve;
  final TextAlign? textAlign;

  /// Si es `true` (default) el primer mount arranca desde 0 para darle un
  /// efecto de "wake up" al abrir la pantalla.
  final bool initialFromZero;

  @override
  State<NivoAnimatedBalance> createState() => _NivoAnimatedBalanceState();
}

class _NivoAnimatedBalanceState extends State<NivoAnimatedBalance> {
  late double _previous;

  @override
  void initState() {
    super.initState();
    _previous = widget.initialFromZero ? 0 : widget.value;
  }

  @override
  void didUpdateWidget(covariant NivoAnimatedBalance oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.value != widget.value) {
      _previous = oldWidget.value;
    }
  }

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: _previous, end: widget.value),
      duration: widget.duration,
      curve: widget.curve,
      builder: (context, value, _) {
        return Text(
          formatMoney(
            value,
            symbol: widget.symbol,
            decimals: widget.decimals,
          ),
          textAlign: widget.textAlign,
          style: widget.style,
        );
      },
    );
  }
}

/// Variante compacta para el top bar: usa el mismo mecanismo pero expone un
/// wrapper con la tipografía ya resuelta para ese slot.
class NivoTopBarBalance extends StatelessWidget {
  const NivoTopBarBalance({
    super.key,
    required this.value,
    required this.color,
  });

  final double value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return NivoAnimatedBalance(
      value: value,
      duration: const Duration(milliseconds: 700),
      style: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.3,
        color: color,
      ),
    );
  }
}
