import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../data/fintech_mvp_content.dart';
import '../../theme/nivo_colors.dart';
import '../../utils/nivo_formatters.dart';
import '../../widgets/demo_preview.dart';
import '../../widgets/nivo_app_chrome.dart';
import '../../widgets/nivo_charts.dart';

class TradingTab extends StatefulWidget {
  const TradingTab({super.key, required this.state});

  final DemoViewState state;

  @override
  State<TradingTab> createState() => _TradingTabState();
}

class _TradingTabState extends State<TradingTab> {
  final _searchController = TextEditingController();
  String _selectedSymbol = 'AAPL';
  String _query = '';
  late Set<String> _watchlist;

  @override
  void initState() {
    super.initState();
    _watchlist = FintechMvpContent.initialWatchlist.toSet();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  StockQuote get _selectedQuote => FintechMvpContent.stocks
      .firstWhere((stock) => stock.symbol == _selectedSymbol);

  List<StockQuote> get _filteredStocks {
    final q = _query.trim().toLowerCase();
    if (q.isEmpty) return FintechMvpContent.stocks;
    return FintechMvpContent.stocks.where((stock) {
      return stock.symbol.toLowerCase().contains(q) ||
          stock.name.toLowerCase().contains(q);
    }).toList();
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
              DemoViewState.loading => const _TradingLoadingState(),
              DemoViewState.empty => const _TradingEmptyState(),
              DemoViewState.error => const _TradingErrorState(),
              DemoViewState.success => _TradingSuccessState(
                  controller: _searchController,
                  selectedQuote: _selectedQuote,
                  positions: FintechMvpContent.positions,
                  stocks: _filteredStocks,
                  watchlist: _watchlist,
                  onSearchChanged: (value) => setState(() => _query = value),
                  onSelectStock: (symbol) =>
                      setState(() => _selectedSymbol = symbol),
                  onToggleWatchlist: (symbol) => setState(() {
                    if (_watchlist.contains(symbol)) {
                      _watchlist.remove(symbol);
                    } else {
                      _watchlist.add(symbol);
                    }
                  }),
                  onTrade: (side) =>
                      _showTradeSheet(context, side, _selectedQuote),
                ),
            },
          ),
        ),
      ],
    );
  }

  Future<void> _showTradeSheet(
    BuildContext context,
    String side,
    StockQuote quote,
  ) {
    return showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          decoration: const BoxDecoration(
            color: NivoColors.paper,
            borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
          ),
          padding: const EdgeInsets.fromLTRB(24, 14, 24, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 42,
                  height: 4,
                  decoration: BoxDecoration(
                    color: NivoColors.line,
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              ),
              const SizedBox(height: 18),
              Text(
                '$side ${quote.symbol}',
                style: GoogleFonts.inter(
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.7,
                  color: NivoColors.ink,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${quote.name} · ${formatMoney(quote.price)}',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: NivoColors.stone,
                ),
              ),
              const SizedBox(height: 18),
              NivoSurface(
                color: NivoColors.cloudSoft,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Vista previa del trade',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 10,
                        letterSpacing: 1.8,
                        color: NivoColors.mist,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      '1.0 acción · ${formatMoney(quote.price)}',
                      style: GoogleFonts.inter(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: NivoColors.ink,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Este modal confirma el flujo y el tono visual; no ejecuta órdenes reales.',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        height: 1.5,
                        color: NivoColors.stone,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _TradingSuccessState extends StatelessWidget {
  const _TradingSuccessState({
    required this.controller,
    required this.selectedQuote,
    required this.positions,
    required this.stocks,
    required this.watchlist,
    required this.onSearchChanged,
    required this.onSelectStock,
    required this.onToggleWatchlist,
    required this.onTrade,
  });

  final TextEditingController controller;
  final StockQuote selectedQuote;
  final List<StockPosition> positions;
  final List<StockQuote> stocks;
  final Set<String> watchlist;
  final ValueChanged<String> onSearchChanged;
  final ValueChanged<String> onSelectStock;
  final ValueChanged<String> onToggleWatchlist;
  final ValueChanged<String> onTrade;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const NivoSectionHeader(
          kicker: 'Trading',
          title: 'Acciones y mercados',
          subtitle:
              'Busca tickers, revisa posiciones y abre compra o venta desde la misma vista.',
        ),
        const SizedBox(height: 20),
        NivoSearchField(
          controller: controller,
          hint: 'Buscar AAPL, TSLA, NVDA...',
          onChanged: onSearchChanged,
        ),
        const SizedBox(height: 18),
        NivoSurface(
          color: NivoColors.cloudSoft,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Mercado seleccionado',
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 10,
                  letterSpacing: 2,
                  color: NivoColors.mist,
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${selectedQuote.symbol} · ${selectedQuote.name}',
                          style: GoogleFonts.inter(
                            fontSize: 22,
                            fontWeight: FontWeight.w600,
                            letterSpacing: -0.6,
                            color: NivoColors.ink,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          '${formatMoney(selectedQuote.price)} · ${formatPercent(selectedQuote.changePct)}',
                          style: GoogleFonts.inter(
                            fontSize: 14,
                            color: selectedQuote.changePct >= 0
                                ? NivoColors.forest
                                : NivoColors.ink,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => onToggleWatchlist(selectedQuote.symbol),
                    icon: Icon(
                      watchlist.contains(selectedQuote.symbol)
                          ? Icons.star_rounded
                          : Icons.star_border_rounded,
                      color: watchlist.contains(selectedQuote.symbol)
                          ? NivoColors.forest
                          : NivoColors.mist,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 18),
              SizedBox(
                height: 180,
                child: NivoCandlestickChart(candles: selectedQuote.candles),
              ),
              const SizedBox(height: 18),
              Row(
                children: [
                  Expanded(
                    child: FilledButton(
                      onPressed: () => onTrade('Comprar'),
                      child: const Text('Comprar'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => onTrade('Vender'),
                      child: const Text('Vender'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 22),
        const NivoSectionHeader(
          kicker: 'Posiciones',
          title: 'Abiertas',
          subtitle: 'Tu cartera actual con ganancia o pérdida estimada.',
        ),
        const SizedBox(height: 14),
        NivoSurface(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
          child: Column(
            children: positions.map((position) {
              final pnlPct = ((position.currentPrice - position.averagePrice) /
                      position.averagePrice) *
                  100;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 10),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            position.symbol,
                            style: GoogleFonts.inter(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: NivoColors.ink,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${formatUnits(position.shares, decimals: 2)} acc · avg ${formatMoney(position.averagePrice)}',
                            style: GoogleFonts.inter(
                              fontSize: 12,
                              color: NivoColors.stone,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      formatPercent(pnlPct),
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: pnlPct >= 0 ? NivoColors.forest : NivoColors.ink,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 22),
        const NivoSectionHeader(
          kicker: 'Mercados',
          title: 'Listado',
          subtitle: 'Busca, selecciona y añade tickers a tu watchlist.',
        ),
        const SizedBox(height: 14),
        NivoSurface(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
          child: Column(
            children: stocks.map((stock) {
              final active = stock.symbol == selectedQuote.symbol;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 10),
                child: InkWell(
                  onTap: () => onSelectStock(stock.symbol),
                  borderRadius: BorderRadius.circular(18),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: active ? NivoColors.ink : NivoColors.cloudSoft,
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Center(
                          child: Text(
                            stock.symbol.substring(0, 2),
                            style: GoogleFonts.inter(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: active ? NivoColors.paper : NivoColors.ink,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              stock.symbol,
                              style: GoogleFonts.inter(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: NivoColors.ink,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              stock.name,
                              style: GoogleFonts.inter(
                                fontSize: 12,
                                color: NivoColors.stone,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            formatMoney(stock.price),
                            style: GoogleFonts.inter(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: NivoColors.ink,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            formatPercent(stock.changePct),
                            style: GoogleFonts.inter(
                              fontSize: 11,
                              color: stock.changePct >= 0
                                  ? NivoColors.forest
                                  : NivoColors.ink,
                            ),
                          ),
                        ],
                      ),
                      IconButton(
                        onPressed: () => onToggleWatchlist(stock.symbol),
                        icon: Icon(
                          watchlist.contains(stock.symbol)
                              ? Icons.star_rounded
                              : Icons.star_border_rounded,
                          size: 18,
                          color: watchlist.contains(stock.symbol)
                              ? NivoColors.forest
                              : NivoColors.mist,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 22),
        const NivoSectionHeader(
          kicker: 'Watchlist',
          title: 'Personalizable',
          subtitle:
              'Los símbolos marcados quedan accesibles para revisión rápida.',
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: watchlist
              .map(
                (symbol) => Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: NivoColors.cloudSoft,
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: NivoColors.line),
                  ),
                  child: Text(
                    symbol,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: NivoColors.ink,
                    ),
                  ),
                ),
              )
              .toList(),
        ),
      ],
    );
  }
}

class _TradingLoadingState extends StatelessWidget {
  const _TradingLoadingState();

  @override
  Widget build(BuildContext context) {
    return const Column(
      children: [
        NivoLoadingBlock(height: 24, width: 180),
        SizedBox(height: 10),
        NivoLoadingBlock(height: 16, width: 260),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 54, radius: 16),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 340, radius: 28),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 220, radius: 26),
      ],
    );
  }
}

class _TradingEmptyState extends StatelessWidget {
  const _TradingEmptyState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 60),
      child: NivoEmptyState(
        title: 'Aún no tienes posiciones abiertas',
        description:
            'Cuando compres acciones, aquí verás tus posiciones, watchlist y el gráfico del activo seleccionado.',
        icon: Icons.show_chart_rounded,
      ),
    );
  }
}

class _TradingErrorState extends StatelessWidget {
  const _TradingErrorState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 60),
      child: NivoErrorState(
        title: 'No pudimos cargar Trading',
        description:
            'La vista de mercados no está disponible en este momento dentro de la demo.',
      ),
    );
  }
}
