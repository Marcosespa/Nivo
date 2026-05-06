String formatMoney(
  double value, {
  String symbol = '€',
  int decimals = 2,
  bool signed = false,
}) {
  final isNegative = value < 0;
  final absolute = value.abs().toStringAsFixed(decimals);
  final parts = absolute.split('.');
  final whole = parts.first;
  final decimal = parts.length > 1 ? parts.last : '';
  final buffer = StringBuffer();

  for (var i = 0; i < whole.length; i++) {
    final reverseIndex = whole.length - i;
    buffer.write(whole[i]);
    if (reverseIndex > 1 && reverseIndex % 3 == 1) {
      buffer.write(',');
    }
  }

  final sign = isNegative
      ? '-'
      : signed && value > 0
          ? '+'
          : '';

  return decimals == 0
      ? '$sign$symbol${buffer.toString()}'
      : '$sign$symbol${buffer.toString()}.$decimal';
}

String formatPercent(double value) {
  final sign = value > 0 ? '+' : '';
  return '$sign${value.toStringAsFixed(2)}%';
}

String formatUnits(double value, {int decimals = 4}) {
  return value.toStringAsFixed(decimals);
}
