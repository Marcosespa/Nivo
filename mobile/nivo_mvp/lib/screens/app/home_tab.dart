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

/// Mapa de quick cards → índice de pestaña destino.
/// EUR / USD → FX (2) · Tarjeta → Movimientos (1) · Crypto → Crypto (4).
const Map<String, int> _quickCardTabRouting = {
  'Cuenta EUR': 2,
  'Cuenta USD': 2,
  'Tarjeta física': 1,
  'Crypto': 4,
};

class HomeTab extends StatelessWidget {
  const HomeTab({
    super.key,
    required this.state,
    required this.onNavigateTab,
  });

  final DemoViewState state;
  final ValueChanged<int> onNavigateTab;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [NivoColors.paper, NivoColors.cloudSoft],
        ),
      ),
      child: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 120),
            sliver: SliverToBoxAdapter(
              child: switch (state) {
                DemoViewState.loading => const _HomeLoadingState(),
                DemoViewState.empty => _HomeEmptyState(
                    onTap: () => _showDashboardSheet(context),
                  ),
                DemoViewState.error => const _HomeErrorState(),
                DemoViewState.success => _HomeSuccessState(
                    onExpand: () => _showDashboardSheet(context),
                    onQuickCardTap: (card) {
                      final idx = _quickCardTabRouting[card.title];
                      if (idx != null) {
                        HapticFeedback.selectionClick();
                        onNavigateTab(idx);
                      }
                    },
                    onActionTap: _handleActionTap,
                  ),
              },
            ),
          ),
        ],
      ),
    );
  }

  void _handleActionTap(String label) {
    // Mapeo de acciones rápidas → pestañas relevantes.
    HapticFeedback.selectionClick();
    switch (label) {
      case 'Enviar':
      case 'Recibir':
        onNavigateTab(1); // Movimientos
        break;
      case 'Cambiar':
        onNavigateTab(2); // Divisas
        break;
      case 'Invertir':
        onNavigateTab(3); // Trading
        break;
    }
  }

  Future<void> _showDashboardSheet(BuildContext context) {
    return showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.82,
        minChildSize: 0.62,
        maxChildSize: 0.96,
        expand: false,
        builder: (context, controller) {
          return Container(
            decoration: BoxDecoration(
              color: NivoColors.paper,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(32),
              ),
            ),
            child: CustomScrollView(
              controller: controller,
              physics: const BouncingScrollPhysics(),
              slivers: [
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 14, 24, 24),
                    child: Column(
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
                        const NivoSectionHeader(
                          kicker: 'Dashboard',
                          title: 'Vista expandida',
                          subtitle:
                              'Todo el detalle queda aquí, no en el primer fold del home.',
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
                                'Balance total',
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 10,
                                  letterSpacing: 2,
                                  color:
                                      NivoColors.paper.withValues(alpha: 0.62),
                                ),
                              ),
                              const SizedBox(height: 10),
                              NivoAnimatedBalance(
                                value: FintechMvpContent.totalBalance,
                                style: GoogleFonts.inter(
                                  fontSize: 34,
                                  fontWeight: FontWeight.w600,
                                  letterSpacing: -1.1,
                                  color: NivoColors.paper,
                                ),
                              ),
                              const SizedBox(height: 18),
                              SizedBox(
                                height: 110,
                                child: NivoSparkline(
                                  points: FintechMvpContent.totalBalanceTrend,
                                  lineColor: NivoColors.forest,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 20),
                        Row(
                          children: FintechMvpContent.dashboardMetrics
                              .map(
                                (metric) => Expanded(
                                  child: Padding(
                                    padding: EdgeInsets.only(
                                      right: metric ==
                                              FintechMvpContent
                                                  .dashboardMetrics.last
                                          ? 0
                                          : 10,
                                    ),
                                    child: NivoSurface(
                                      color: NivoColors.cloudSoft,
                                      padding: const EdgeInsets.all(16),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            metric.label,
                                            style: GoogleFonts.jetBrainsMono(
                                              fontSize: 9,
                                              letterSpacing: 1.6,
                                              color: NivoColors.mist,
                                            ),
                                          ),
                                          const SizedBox(height: 8),
                                          Text(
                                            metric.value,
                                            style: GoogleFonts.inter(
                                              fontSize: 20,
                                              fontWeight: FontWeight.w600,
                                              color: NivoColors.ink,
                                            ),
                                          ),
                                          const SizedBox(height: 4),
                                          Text(
                                            metric.caption,
                                            style: GoogleFonts.inter(
                                              fontSize: 12,
                                              color: NivoColors.stone,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                              )
                              .toList(),
                        ),
                        const SizedBox(height: 20),
                        const NivoSectionHeader(
                          kicker: 'Actividad',
                          title: 'Últimos movimientos',
                          subtitle:
                              'Resumen rápido de lo más reciente sin abrir la pestaña completa.',
                        ),
                        const SizedBox(height: 14),
                        NivoSurface(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 18,
                            vertical: 8,
                          ),
                          child: Column(
                            children: FintechMvpContent.transactions
                                .take(4)
                                .map(
                                  (tx) => Padding(
                                    padding: const EdgeInsets.symmetric(
                                      vertical: 10,
                                    ),
                                    child: Row(
                                      children: [
                                        Container(
                                          width: 40,
                                          height: 40,
                                          decoration: BoxDecoration(
                                            color: NivoColors.cloudSoft,
                                            borderRadius:
                                                BorderRadius.circular(14),
                                          ),
                                          child: Icon(
                                            tx.icon,
                                            size: 18,
                                            color: NivoColors.ink,
                                          ),
                                        ),
                                        const SizedBox(width: 12),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                tx.title,
                                                style: GoogleFonts.inter(
                                                  fontSize: 14,
                                                  fontWeight: FontWeight.w600,
                                                  color: NivoColors.ink,
                                                ),
                                              ),
                                              const SizedBox(height: 4),
                                              Text(
                                                tx.dateLabel,
                                                style: GoogleFonts.inter(
                                                  fontSize: 12,
                                                  color: NivoColors.stone,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          formatMoney(
                                            tx.amount,
                                            symbol: tx.amount.abs() >= 1000
                                                ? '€'
                                                : '€',
                                            signed: true,
                                          ),
                                          style: GoogleFonts.inter(
                                            fontSize: 13,
                                            fontWeight: FontWeight.w600,
                                            color: tx.amount >= 0
                                                ? NivoColors.forest
                                                : NivoColors.ink,
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
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _HomeSuccessState extends StatelessWidget {
  const _HomeSuccessState({
    required this.onExpand,
    required this.onQuickCardTap,
    required this.onActionTap,
  });

  final VoidCallback onExpand;
  final ValueChanged<HomeQuickCard> onQuickCardTap;
  final ValueChanged<String> onActionTap;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: 18),
        NivoAnimatedBalance(
          value: FintechMvpContent.totalBalance,
          textAlign: TextAlign.center,
          style: GoogleFonts.inter(
            fontSize: 42,
            fontWeight: FontWeight.w600,
            letterSpacing: -1.4,
            color: NivoColors.ink,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Saldo total · listo para mover, cambiar e invertir',
          textAlign: TextAlign.center,
          style: GoogleFonts.inter(
            fontSize: 15,
            height: 1.5,
            color: NivoColors.stone,
          ),
        ),
        const SizedBox(height: 28),
        SizedBox(
          height: 172,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            physics: const BouncingScrollPhysics(),
            itemCount: FintechMvpContent.homeQuickCards.length,
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              final card = FintechMvpContent.homeQuickCards[index];
              final hasRoute = _quickCardTabRouting.containsKey(card.title);
              return SizedBox(
                width: 180,
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: hasRoute ? () => onQuickCardTap(card) : null,
                    borderRadius: BorderRadius.circular(26),
                    child: NivoSurface(
                      color: NivoColors.paper,
                      padding: const EdgeInsets.all(14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(card.icon,
                                  size: 20, color: NivoColors.ink),
                              const Spacer(),
                              if (hasRoute)
                                Icon(
                                  Icons.arrow_outward_rounded,
                                  size: 14,
                                  color: NivoColors.mist,
                                ),
                            ],
                          ),
                          const Spacer(),
                          Text(
                            card.title,
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
                            card.subtitle,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: GoogleFonts.inter(
                              fontSize: 12,
                              color: NivoColors.stone,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            card.value,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: GoogleFonts.inter(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              letterSpacing: -0.4,
                              color: NivoColors.ink,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 28),
        GridView.builder(
          itemCount: FintechMvpContent.homeActions.length,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.7,
          ),
          itemBuilder: (context, index) {
            final action = FintechMvpContent.homeActions[index];
            return Material(
              color: index == 0 ? NivoColors.ink : NivoColors.cloudSoft,
              borderRadius: BorderRadius.circular(24),
              child: InkWell(
                onTap: () => onActionTap(action.label),
                borderRadius: BorderRadius.circular(24),
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Row(
                    children: [
                      Icon(
                        action.icon,
                        size: 20,
                        color: index == 0 ? NivoColors.paper : NivoColors.ink,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          action.label,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: GoogleFonts.inter(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color:
                                index == 0 ? NivoColors.paper : NivoColors.ink,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 24),
        NivoSurface(
          color: NivoColors.cloudSoft,
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ver más',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 10,
                        letterSpacing: 2,
                        color: NivoColors.mist,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Ver todo el dashboard',
                      style: GoogleFonts.inter(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        letterSpacing: -0.5,
                        color: NivoColors.ink,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Gráficos, asignación y detalle reciente fuera de la vista principal.',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        height: 1.5,
                        color: NivoColors.stone,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              FilledButton(
                onPressed: onExpand,
                child: const Text('Abrir'),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _HomeLoadingState extends StatelessWidget {
  const _HomeLoadingState();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const NivoLoadingBlock(height: 46, width: 220, radius: 18),
        const SizedBox(height: 10),
        const NivoLoadingBlock(height: 16, width: 240),
        const SizedBox(height: 28),
        SizedBox(
          height: 128,
          child: Row(
            children: List.generate(
              2,
              (index) => Expanded(
                child: Padding(
                  padding: EdgeInsets.only(right: index == 1 ? 0 : 12),
                  child: const NivoLoadingBlock(
                    height: 128,
                    radius: 24,
                  ),
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 28),
        GridView.count(
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.7,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          children: List.generate(
            4,
            (_) => const NivoLoadingBlock(height: 100, radius: 24),
          ),
        ),
        const SizedBox(height: 24),
        const NivoLoadingBlock(height: 110, radius: 26),
      ],
    );
  }
}

class _HomeEmptyState extends StatelessWidget {
  const _HomeEmptyState({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: 40),
        NivoEmptyState(
          title: 'Tu home todavía está vacío',
          description:
              'Activa una cuenta, añade una tarjeta o recibe tu primera transferencia para empezar a ver saldos y acciones rápidas.',
          icon: Icons.account_balance_wallet_outlined,
          ctaLabel: 'Ver cómo se vería',
          onTap: onTap,
        ),
      ],
    );
  }
}

class _HomeErrorState extends StatelessWidget {
  const _HomeErrorState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 40),
      child: NivoErrorState(
        title: 'No pudimos cargar el home',
        description:
            'La vista principal no respondió a tiempo. Revisa red o vuelve a intentar desde el selector demo.',
      ),
    );
  }
}
