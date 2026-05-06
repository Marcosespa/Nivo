import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../data/fintech_mvp_content.dart';
import '../../theme/nivo_colors.dart';
import '../../utils/nivo_formatters.dart';
import '../../widgets/demo_preview.dart';
import '../../widgets/nivo_app_chrome.dart';

class TransactionsTab extends StatefulWidget {
  const TransactionsTab({super.key, required this.state});

  final DemoViewState state;

  @override
  State<TransactionsTab> createState() => _TransactionsTabState();
}

class _TransactionsTabState extends State<TransactionsTab> {
  final _searchController = TextEditingController();
  int _selectedFilter = 0;
  String _query = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  List<TransactionItem> get _filteredTransactions {
    return FintechMvpContent.transactions.where((item) {
      final matchesFilter = switch (_selectedFilter) {
        1 => item.type == TransactionType.income,
        2 => item.type == TransactionType.expense,
        3 => item.type == TransactionType.transfer,
        _ => true,
      };

      final q = _query.trim().toLowerCase();
      final matchesQuery = q.isEmpty ||
          item.title.toLowerCase().contains(q) ||
          item.subtitle.toLowerCase().contains(q) ||
          item.category.toLowerCase().contains(q);

      return matchesFilter && matchesQuery;
    }).toList();
  }

  Future<void> _handleRefresh() async {
    HapticFeedback.lightImpact();
    await Future<void>.delayed(const Duration(milliseconds: 1100));
    if (!mounted) return;
    setState(() {}); // Re-render simulado para la demo.
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        const SnackBar(
          content: Text('Movimientos actualizados'),
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
                DemoViewState.loading => const _TransactionsLoadingState(),
                DemoViewState.empty => const _TransactionsEmptyState(),
                DemoViewState.error => const _TransactionsErrorState(),
                DemoViewState.success => _TransactionsSuccessState(
                    controller: _searchController,
                    selectedFilter: _selectedFilter,
                    onFilterChanged: (value) =>
                        setState(() => _selectedFilter = value),
                    onQueryChanged: (value) => setState(() => _query = value),
                    items: _filteredTransactions,
                    onOpenItem: (item) => _showTransactionDetails(context, item),
                  ),
              },
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showTransactionDetails(
    BuildContext context,
    TransactionItem item,
  ) {
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
              Row(
                children: [
                  Container(
                    width: 46,
                    height: 46,
                    decoration: BoxDecoration(
                      color: NivoColors.cloudSoft,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Icon(item.icon, size: 20, color: NivoColors.ink),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.title,
                          style: GoogleFonts.inter(
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                            letterSpacing: -0.5,
                            color: NivoColors.ink,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          item.subtitle,
                          style: GoogleFonts.inter(
                            fontSize: 14,
                            color: NivoColors.stone,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 18),
              Text(
                formatMoney(item.amount, signed: true),
                style: GoogleFonts.inter(
                  fontSize: 28,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.8,
                  color: item.amount >= 0 ? NivoColors.forest : NivoColors.ink,
                ),
              ),
              const SizedBox(height: 18),
              NivoSurface(
                color: NivoColors.cloudSoft,
                child: Column(
                  children: [
                    _DetailRow(label: 'Fecha', value: item.dateLabel),
                    Divider(height: 20, color: NivoColors.line),
                    _DetailRow(label: 'Referencia', value: item.reference),
                    Divider(height: 20, color: NivoColors.line),
                    _DetailRow(label: 'Categoría', value: item.category),
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

class _TransactionsSuccessState extends StatelessWidget {
  const _TransactionsSuccessState({
    required this.controller,
    required this.selectedFilter,
    required this.onFilterChanged,
    required this.onQueryChanged,
    required this.items,
    required this.onOpenItem,
  });

  final TextEditingController controller;
  final int selectedFilter;
  final ValueChanged<int> onFilterChanged;
  final ValueChanged<String> onQueryChanged;
  final List<TransactionItem> items;
  final ValueChanged<TransactionItem> onOpenItem;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const NivoSectionHeader(
          kicker: 'Movimientos',
          title: 'Actividad reciente',
          subtitle:
              'Busca, filtra y abre el detalle sin salir de la lista principal.',
        ),
        const SizedBox(height: 20),
        NivoSearchField(
          controller: controller,
          hint: 'Buscar por comercio, categoría o contacto',
          onChanged: onQueryChanged,
        ),
        const SizedBox(height: 14),
        NivoSegmentedControl(
          labels: const ['Todos', 'Ingresos', 'Gastos', 'Transferencias'],
          selectedIndex: selectedFilter,
          onChanged: onFilterChanged,
        ),
        const SizedBox(height: 20),
        if (items.isEmpty)
          const NivoEmptyState(
            title: 'No hay resultados',
            description:
                'Prueba otro filtro o término de búsqueda para encontrar movimientos.',
            icon: Icons.search_off_rounded,
          )
        else
          ..._buildSections(items),
      ],
    );
  }

  List<Widget> _buildSections(List<TransactionItem> items) {
    final sections = <String, List<TransactionItem>>{};
    for (final item in items) {
      sections.putIfAbsent(item.section, () => []).add(item);
    }

    return sections.entries.map((entry) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.only(left: 4, bottom: 8),
              child: Text(
                entry.key.toUpperCase(),
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 10,
                  letterSpacing: 2,
                  color: NivoColors.mist,
                ),
              ),
            ),
            NivoSurface(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
              child: Column(
                children: entry.value
                    .map(
                      (item) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: _TransactionRow(
                          item: item,
                          onTap: () => onOpenItem(item),
                        ),
                      ),
                    )
                    .toList(),
              ),
            ),
          ],
        ),
      );
    }).toList();
  }
}

class _TransactionRow extends StatelessWidget {
  const _TransactionRow({
    required this.item,
    required this.onTap,
  });

  final TransactionItem item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 2, vertical: 4),
          child: Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: NivoColors.cloudSoft,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(item.icon, size: 18, color: NivoColors.ink),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.title,
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
                      item.subtitle,
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
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    formatMoney(item.amount, signed: true),
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color:
                          item.amount >= 0 ? NivoColors.forest : NivoColors.ink,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    item.dateLabel,
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      color: NivoColors.mist,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 13,
              color: NivoColors.stone,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            value,
            textAlign: TextAlign.right,
            style: GoogleFonts.inter(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: NivoColors.ink,
            ),
          ),
        ),
      ],
    );
  }
}

class _TransactionsLoadingState extends StatelessWidget {
  const _TransactionsLoadingState();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const NivoLoadingBlock(height: 24, width: 180),
        const SizedBox(height: 10),
        const NivoLoadingBlock(height: 16, width: 260),
        const SizedBox(height: 20),
        const NivoLoadingBlock(height: 54, radius: 16),
        const SizedBox(height: 14),
        const NivoLoadingBlock(height: 46, radius: 999),
        const SizedBox(height: 20),
        ...List.generate(
          4,
          (_) => const Padding(
            padding: EdgeInsets.only(bottom: 12),
            child: NivoLoadingBlock(height: 78, radius: 22),
          ),
        ),
      ],
    );
  }
}

class _TransactionsEmptyState extends StatelessWidget {
  const _TransactionsEmptyState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 60),
      child: NivoEmptyState(
        title: 'Todavía no hay movimientos',
        description:
            'Cuando empieces a pagar, recibir o transferir, aquí verás toda la actividad con filtros y detalle.',
        icon: Icons.receipt_long_outlined,
      ),
    );
  }
}

class _TransactionsErrorState extends StatelessWidget {
  const _TransactionsErrorState();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 60),
      child: NivoErrorState(
        title: 'No pudimos cargar los movimientos',
        description:
            'La actividad reciente no está disponible ahora mismo. Cambia el estado demo o vuelve a intentarlo más tarde.',
      ),
    );
  }
}
