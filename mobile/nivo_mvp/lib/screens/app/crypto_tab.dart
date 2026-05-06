import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../data/fintech_mvp_content.dart';
import '../../theme/nivo_colors.dart';
import '../../utils/nivo_formatters.dart';
import '../../widgets/demo_preview.dart';
import '../../widgets/nivo_animated_balance.dart';
import '../../widgets/nivo_app_chrome.dart';
import '../../widgets/nivo_charts.dart';

class CryptoTab extends StatefulWidget {
  const CryptoTab({super.key, required this.state});

  final DemoViewState state;

  @override
  State<CryptoTab> createState() => _CryptoTabState();
}

class _CryptoTabState extends State<CryptoTab> {
  String _selectedSymbol = 'BTC';

  CryptoAsset get _selectedAsset => FintechMvpContent.cryptoAssets
      .firstWhere((asset) => asset.symbol == _selectedSymbol);

  double get _portfolioTotal => FintechMvpContent.cryptoAssets.fold(
        0,
        (sum, asset) => sum + (asset.price * asset.quantity),
      );

  Future<void> _handleRefresh() async {
    HapticFeedback.lightImpact();
    await Future<void>.delayed(const Duration(milliseconds: 1200));
    if (!mounted) return;
    setState(() {}); // Re-fetch simulado: re-renderiza tarjetas y gráfico.
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        const SnackBar(
          content: Text('Crypto actualizada · precios refrescados'),
          duration: Duration(seconds: 2),
        ),
      );
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      color: NivoColors.forest,
      backgroundColor: NivoColors.paper,
      onRefresh: _handleRefresh,
      child: CustomScrollView(
        physics: const AlwaysScrollableScrollPhysics(
          parent: BouncingScrollPhysics(),
        ),
        slivers: [
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 120),
            sliver: SliverToBoxAdapter(
              child: switch (widget.state) {
                DemoViewState.loading => const _CryptoLoadingState(),
                DemoViewState.empty => const _CryptoEmptyState(),
                DemoViewState.error => const _CryptoErrorState(),
                DemoViewState.success => _CryptoSuccessState(
                    portfolioTotal: _portfolioTotal,
                    selectedAsset: _selectedAsset,
                    assets: FintechMvpContent.cryptoAssets,
                    movers: FintechMvpContent.cryptoMovers,
                    onSelectAsset: (symbol) =>
                        setState(() => _selectedSymbol = symbol),
                    onTrade: (side) =>
                        _showTradeSheet(context, side, _selectedAsset),
                  ),
              },
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showTradeSheet(
    BuildContext context,
    String side,
    CryptoAsset asset,
  ) {
    HapticFeedback.mediumImpact();
    return showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          decoration: BoxDecoration(
            color: NivoColors.paper,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
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
                '$side ${asset.symbol}',
                style: GoogleFonts.inter(
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.6,
                  color: NivoColors.ink,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${asset.name} · ${formatMoney(asset.price)}',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: NivoColors.stone,
                ),
              ),
              const SizedBox(height: 18),
              NivoSurface(
                color: NivoColors.cloudSoft,
                child: Text(
                  'Esta acción abre el flujo visual de compra/venta cripto. No hay ejecución real en esta maqueta.',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    height: 1.5,
                    color: NivoColors.stone,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _CryptoSuccessState extends StatelessWidget {
  const _CryptoSuccessState({
    required this.portfolioTotal,
    required this.selectedAsset,
    required this.assets,
    required this.movers,
    required this.onSelectAsset,
    required this.onTrade,
  });

  final double portfolioTotal;
  final CryptoAsset selectedAsset;
  final List<CryptoAsset> assets;
  final List<CryptoMover> movers;
  final ValueChanged<String> onSelectAsset;
  final ValueChanged<String> onTrade;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const NivoSectionHeader(
          kicker: 'Crypto',
          title: 'Tu cartera digital',
          subtitle:
              'Saldo total, precio del activo seleccionado y tendencias del mercado.',
        ),
        const SizedBox(height: 20),
        NivoSurface(
          color: NivoColors.ink,
          radius: 30,
          padding: const EdgeInsets.all(22),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Valor total',
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 10,
                  letterSpacing: 2,
                  color: NivoColors.paper.withValues(alpha: 0.62),
                ),
              ),
              const SizedBox(height: 10),
              NivoAnimatedBalance(
                value: portfolioTotal,
                style: GoogleFonts.inter(
                  fontSize: 34,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -1.1,
                  color: NivoColors.paper,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${assets.length} activos · vista inspirada en exchange moderno, más limpia',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: NivoColors.paper.withValues(alpha: 0.72),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 22),
        NivoSurface(
          color: NivoColors.cloudSoft,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${selectedAsset.symbol} · ${selectedAsset.name}',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: GoogleFonts.inter(
                  fontSize: 22,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.6,
                  color: NivoColors.ink,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                '${formatMoney(selectedAsset.price)} · ${formatPercent(selectedAsset.changePct)}',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: selectedAsset.changePct >= 0
                      ? NivoColors.forest
                      : NivoColors.ink,
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                height: 120,
                child: NivoSparkline(points: selectedAsset.points),
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
          kicker: 'Tus cryptos',
          title: 'Holdings',
          subtitle:
              'Selecciona un activo para actualizar el gráfico y las acciones rápidas.',
        ),
        const SizedBox(height: 14),
        NivoSurface(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
          child: Column(
            children: assets.map((asset) {
              final active = asset.symbol == selectedAsset.symbol;
              final positionValue = asset.price * asset.quantity;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 10),
                child: InkWell(
                  onTap: () => onSelectAsset(asset.symbol),
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
                            asset.symbol.substring(0, 2),
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
                              asset.symbol,
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
                              '${asset.name} · ${formatUnits(asset.quantity)}',
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
                      const SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            formatMoney(positionValue),
                            style: GoogleFonts.inter(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: NivoColors.ink,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            formatPercent(asset.changePct),
                            style: GoogleFonts.inter(
                              fontSize: 11,
                              color: asset.changePct >= 0
                                  ? NivoColors.forest
                                  : NivoColors.ink,
                            ),
                          ),
                        ],
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
          kicker: 'Tendencias',
          title: 'Top movers',
          subtitle:
              'Señales rápidas para abrir exploración sin saturar la vista.',
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: movers
              .map(
                (mover) => Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  decoration: BoxDecoration(
                    color: NivoColors.cloudSoft,
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: NivoColors.line),
                  ),
                  child: Text(
                    '${mover.symbol} ${formatPercent(mover.changePct)}',
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

class _CryptoLoadingState extends StatelessWidget {
  const _CryptoLoadingState();

  @override
  Widget build(BuildContext context) {
    return const Column(
      children: [
        NivoLoadingBlock(height: 24, width: 180),
        SizedBox(height: 10),
        NivoLoadingBlock(height: 16, width: 260),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 160, radius: 28),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 320, radius: 28),
        SizedBox(height: 20),
        NivoLoadingBlock(height: 220, radius: 26),
      ],
    );
  }
}

class _CryptoEmptyState extends StatelessWidget {
  const _CryptoEmptyState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 60),
      child: NivoEmptyState(
        title: 'No tienes crypto todavía',
        description:
            'Cuando compres BTC, ETH o SOL aparecerán aquí tu saldo, el gráfico y las tendencias principales.',
        icon: Icons.currency_bitcoin_rounded,
      ),
    );
  }
}

class _CryptoErrorState extends StatelessWidget {
  const _CryptoErrorState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 60),
      child: NivoErrorState(
        title: 'No pudimos cargar Crypto',
        description:
            'La cartera cripto no respondió a tiempo. Puedes revisar otro estado desde el selector demo.',
      ),
    );
  }
}
