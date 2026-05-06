import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../data/fintech_mvp_content.dart';
import '../../theme/nivo_colors.dart';
import '../../utils/nivo_formatters.dart';
import '../../widgets/demo_preview.dart';
import '../../widgets/nivo_app_chrome.dart';
import '../../widgets/nivo_charts.dart';

class CurrenciesTab extends StatefulWidget {
  const CurrenciesTab({super.key, required this.state});

  final DemoViewState state;

  @override
  State<CurrenciesTab> createState() => _CurrenciesTabState();
}

class _CurrenciesTabState extends State<CurrenciesTab> {
  String _fromCode = 'EUR';
  String _toCode = 'USD';
  final _amountController = TextEditingController(text: '250');

  @override
  void dispose() {
    _amountController.dispose();
    super.dispose();
  }

  double get _currentRate {
    if (_fromCode == _toCode) return 1;

    if (_fromCode == 'EUR') {
      return _findPairRate('EUR/$_toCode');
    }

    if (_toCode == 'EUR') {
      final pairRate = _findPairRate('EUR/$_fromCode');
      return pairRate == 0 ? 1 : 1 / pairRate;
    }

    final fromToEuro = _findPairRate('EUR/$_fromCode');
    final euroToTarget = _findPairRate('EUR/$_toCode');
    if (fromToEuro == 0 || euroToTarget == 0) return 1;
    return (1 / fromToEuro) * euroToTarget;
  }

  List<double> get _currentSeries {
    if (_fromCode == _toCode) return const [1, 1, 1, 1, 1];
    if (_fromCode == 'EUR') {
      return _findSeries('EUR/$_toCode');
    }
    if (_toCode == 'EUR') {
      return _findSeries('EUR/$_fromCode')
          .map((value) => value == 0 ? 0.0 : (1 / value).toDouble())
          .toList();
    }

    final source = _findSeries('EUR/$_fromCode');
    final target = _findSeries('EUR/$_toCode');
    if (source.isEmpty || target.isEmpty) return const [1, 1, 1, 1, 1];
    return List.generate(
      target.length,
      (index) => ((1 / source[index]) * target[index]).toDouble(),
    );
  }

  double _findPairRate(String pair) {
    final found = FintechMvpContent.fxPairs.where((item) => item.pair == pair);
    return found.isEmpty ? 0 : found.first.rate;
  }

  List<double> _findSeries(String pair) {
    final found = FintechMvpContent.fxPairs.where((item) => item.pair == pair);
    return found.isEmpty ? const [] : found.first.points;
  }

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      physics: const BouncingScrollPhysics(),
      slivers: [
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 120),
          sliver: SliverToBoxAdapter(
            child: switch (widget.state) {
              DemoViewState.loading => const _CurrenciesLoadingState(),
              DemoViewState.empty => const _CurrenciesEmptyState(),
              DemoViewState.error => const _CurrenciesErrorState(),
              DemoViewState.success => _CurrenciesSuccessState(
                  fromCode: _fromCode,
                  toCode: _toCode,
                  amountController: _amountController,
                  currentRate: _currentRate,
                  currentSeries: _currentSeries,
                  onFromChanged: (value) =>
                      setState(() => _fromCode = value ?? _fromCode),
                  onToChanged: (value) =>
                      setState(() => _toCode = value ?? _toCode),
                  onSwap: () => setState(() {
                    final current = _fromCode;
                    _fromCode = _toCode;
                    _toCode = current;
                  }),
                  onConfirm: () => _showConfirmDialog(context),
                ),
            },
          ),
        ),
      ],
    );
  }

  Future<void> _showConfirmDialog(BuildContext context) async {
    final amount = double.tryParse(_amountController.text) ?? 0;
    final converted = amount * _currentRate;

    await showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(
            'Confirmar cambio',
            style: GoogleFonts.inter(fontWeight: FontWeight.w600),
          ),
          content: Text(
            'Cambiar ${formatMoney(amount, symbol: _symbolFor(_fromCode))} a '
            '${formatMoney(converted, symbol: _symbolFor(_toCode))} con tasa '
            '${_currentRate.toStringAsFixed(4)}.',
            style: GoogleFonts.inter(height: 1.5),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancelar'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Confirmar'),
            ),
          ],
        );
      },
    );
  }

  String _symbolFor(String code) {
    return switch (code) {
      'USD' => '\$',
      'GBP' => '£',
      'CZK' => 'Kč ',
      _ => '€',
    };
  }
}

class _CurrenciesSuccessState extends StatelessWidget {
  const _CurrenciesSuccessState({
    required this.fromCode,
    required this.toCode,
    required this.amountController,
    required this.currentRate,
    required this.currentSeries,
    required this.onFromChanged,
    required this.onToChanged,
    required this.onSwap,
    required this.onConfirm,
  });

  final String fromCode;
  final String toCode;
  final TextEditingController amountController;
  final double currentRate;
  final List<double> currentSeries;
  final ValueChanged<String?> onFromChanged;
  final ValueChanged<String?> onToChanged;
  final VoidCallback onSwap;
  final VoidCallback onConfirm;

  @override
  Widget build(BuildContext context) {
    final amount = double.tryParse(amountController.text) ?? 0;
    final converted = amount * currentRate;
    final codes = FintechMvpContent.currencyPockets.map((e) => e.code).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const NivoSectionHeader(
          kicker: 'Divisas',
          title: 'Cuentas multi-currency',
          subtitle:
              'Saldos, conversión y contexto de tipo de cambio en una sola vista.',
        ),
        const SizedBox(height: 20),
        SizedBox(
          height: 116,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            physics: const BouncingScrollPhysics(),
            itemCount: FintechMvpContent.currencyPockets.length,
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              final pocket = FintechMvpContent.currencyPockets[index];
              return SizedBox(
                width: 170,
                child: NivoSurface(
                  color: index == 0 ? NivoColors.ink : NivoColors.paper,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${pocket.flag} ${pocket.code}',
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 10,
                          letterSpacing: 1.6,
                          color: index == 0
                              ? NivoColors.paper.withValues(alpha: 0.7)
                              : NivoColors.mist,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        pocket.name,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: GoogleFonts.inter(
                          fontSize: 13,
                          color:
                              index == 0 ? NivoColors.paper : NivoColors.stone,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        formatMoney(
                          pocket.balance,
                          symbol: pocket.code == 'USD'
                              ? '\$'
                              : pocket.code == 'GBP'
                                  ? '£'
                                  : pocket.code == 'CZK'
                                      ? 'Kč '
                                      : '€',
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: GoogleFonts.inter(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          letterSpacing: -0.5,
                          color: index == 0 ? NivoColors.paper : NivoColors.ink,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 22),
        NivoSurface(
          color: NivoColors.cloudSoft,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const NivoSectionHeader(
                kicker: 'Conversor',
                title: 'Tipo en vivo',
                subtitle:
                    'Selecciona origen, destino y revisa la evolución antes de confirmar.',
              ),
              const SizedBox(height: 18),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: fromCode,
                      items: codes
                          .map(
                            (code) => DropdownMenuItem(
                              value: code,
                              child: Text(code),
                            ),
                          )
                          .toList(),
                      onChanged: onFromChanged,
                      decoration: const InputDecoration(labelText: 'Origen'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  IconButton(
                    onPressed: onSwap,
                    icon: const Icon(Icons.swap_horiz_rounded),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: toCode,
                      items: codes
                          .map(
                            (code) => DropdownMenuItem(
                              value: code,
                              child: Text(code),
                            ),
                          )
                          .toList(),
                      onChanged: onToChanged,
                      decoration: const InputDecoration(labelText: 'Destino'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              TextField(
                controller: amountController,
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Monto',
                  hintText: '250',
                ),
              ),
              const SizedBox(height: 18),
              NivoSurface(
                color: NivoColors.paper,
                radius: 22,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Tasa $fromCode/$toCode',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 10,
                        letterSpacing: 1.8,
                        color: NivoColors.mist,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      currentRate.toStringAsFixed(4),
                      style: GoogleFonts.inter(
                        fontSize: 26,
                        fontWeight: FontWeight.w600,
                        letterSpacing: -0.8,
                        color: NivoColors.ink,
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      height: 78,
                      child: NivoSparkline(points: currentSeries),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Recibirías ${converted.toStringAsFixed(2)} $toCode',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        color: NivoColors.stone,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),
              FilledButton(
                onPressed: onConfirm,
                child: const Text('Cambiar ahora'),
              ),
            ],
          ),
        ),
        const SizedBox(height: 22),
        const NivoSectionHeader(
          kicker: 'Populares',
          title: 'Monedas seguidas',
          subtitle: 'Referencias rápidas con banderas y cruces frecuentes.',
        ),
        const SizedBox(height: 14),
        NivoSurface(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
          child: Column(
            children: FintechMvpContent.popularCurrencies
                .map(
                  (item) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    child: Row(
                      children: [
                        Text(item.flag, style: const TextStyle(fontSize: 20)),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '${item.code} · ${item.name}',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: GoogleFonts.inter(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: NivoColors.ink,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                item.rateLabel,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: GoogleFonts.inter(
                                  fontSize: 12,
                                  color: NivoColors.stone,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                )
                .toList(),
          ),
        ),
      ],
    );
  }
}

class _CurrenciesLoadingState extends StatelessWidget {
  const _CurrenciesLoadingState();

  @override
  Widget build(BuildContext context) {
    return const Column(
      children: [
        NivoLoadingBlock(height: 24, width: 180),
        SizedBox(height: 10),
        NivoLoadingBlock(height: 16, width: 260),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 116, radius: 24),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 360, radius: 28),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 220, radius: 26),
      ],
    );
  }
}

class _CurrenciesEmptyState extends StatelessWidget {
  const _CurrenciesEmptyState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 60),
      child: NivoEmptyState(
        title: 'Aún no tienes bolsillos en divisas',
        description:
            'Cuando abras tus cuentas multi-currency verás EUR, USD, GBP, CZK y el conversor listo para usar.',
        icon: Icons.language_rounded,
      ),
    );
  }
}

class _CurrenciesErrorState extends StatelessWidget {
  const _CurrenciesErrorState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 60),
      child: NivoErrorState(
        title: 'No pudimos cargar las divisas',
        description:
            'Los saldos o la tasa de cambio no están disponibles ahora mismo dentro de esta vista demo.',
      ),
    );
  }
}
