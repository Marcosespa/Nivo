import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../data/fintech_mvp_content.dart';
import '../theme/nivo_colors.dart';
import '../widgets/demo_preview.dart';
import '../widgets/nivo_animated_balance.dart';
import '../widgets/nivo_app_chrome.dart';
import 'app/crypto_tab.dart';
import 'app/currencies_tab.dart';
import 'app/home_tab.dart';
import 'app/trading_tab.dart';
import 'app/transactions_tab.dart';

class PostAuthHomeScreen extends StatefulWidget {
  const PostAuthHomeScreen({super.key});

  @override
  State<PostAuthHomeScreen> createState() => _PostAuthHomeScreenState();
}

class _PostAuthHomeScreenState extends State<PostAuthHomeScreen> {
  int _currentIndex = 0;
  late final List<DemoViewState> _tabStates =
      List<DemoViewState>.filled(_items.length, DemoViewState.success);

  static const List<NivoTabItem> _items = [
    NivoTabItem(label: 'Home', icon: Icons.home_rounded),
    NivoTabItem(label: 'Movs', icon: Icons.receipt_long_rounded),
    NivoTabItem(label: 'FX', icon: Icons.currency_exchange_rounded),
    NivoTabItem(label: 'Trading', icon: Icons.show_chart_rounded),
    NivoTabItem(label: 'Crypto', icon: Icons.currency_bitcoin_rounded),
  ];

  static const List<String> _labels = [
    'Home',
    'Movimientos',
    'Divisas',
    'Trading',
    'Crypto',
  ];

  void _handleTabChange(int value) {
    if (value == _currentIndex) return;
    HapticFeedback.selectionClick();
    setState(() => _currentIndex = value);
  }

  void _handleThemeToggle() {
    HapticFeedback.lightImpact();
    NivoThemeController.instance.toggle();
  }

  @override
  Widget build(BuildContext context) {
    final tabs = [
      HomeTab(
        state: _tabStates[0],
        onNavigateTab: _handleTabChange,
      ),
      TransactionsTab(state: _tabStates[1]),
      CurrenciesTab(state: _tabStates[2]),
      TradingTab(state: _tabStates[3]),
      CryptoTab(state: _tabStates[4]),
    ];

    final isDark = NivoThemeController.instance.isDark;

    return Scaffold(
      backgroundColor: NivoColors.paper,
      bottomNavigationBar: NivoBottomTabBar(
        currentIndex: _currentIndex,
        items: _items,
        onChanged: _handleTabChange,
      ),
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            _HomeTopBar(
              balance: FintechMvpContent.totalBalance,
              isDark: isDark,
              onToggleTheme: _handleThemeToggle,
              onAvatarTap: () => showDemoStateSheet(
                context: context,
                tabLabel: _labels[_currentIndex],
                currentState: _tabStates[_currentIndex],
                onChanged: (state) =>
                    setState(() => _tabStates[_currentIndex] = state),
              ),
            ),
            Expanded(
              child: IndexedStack(
                index: _currentIndex,
                children: tabs,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Top bar del shell fintech con saldo animado + toggle de tema + avatar demo.
class _HomeTopBar extends StatelessWidget {
  const _HomeTopBar({
    required this.balance,
    required this.isDark,
    required this.onToggleTheme,
    required this.onAvatarTap,
  });

  final double balance;
  final bool isDark;
  final VoidCallback onToggleTheme;
  final VoidCallback onAvatarTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 6),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Align(
              alignment: Alignment.centerLeft,
              child: _BrandPill(),
            ),
          ),
          Expanded(
            flex: 3,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: NivoColors.cloudSoft,
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: NivoColors.line),
                ),
                child: NivoTopBarBalance(
                  value: balance,
                  color: NivoColors.ink,
                ),
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                _RoundIconButton(
                  onTap: onToggleTheme,
                  icon: isDark
                      ? Icons.light_mode_rounded
                      : Icons.dark_mode_rounded,
                  tooltip:
                      isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro',
                ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: onAvatarTap,
                  child: Container(
                    width: 38,
                    height: 38,
                    decoration: BoxDecoration(
                      color: NivoColors.ink,
                      borderRadius: BorderRadius.circular(14),
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      'ME',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: NivoColors.paper,
                        letterSpacing: 0.4,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _BrandPill extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: NivoColors.ink,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        'NIVO',
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w800,
          letterSpacing: 2,
          color: NivoColors.paper,
        ),
      ),
    );
  }
}

class _RoundIconButton extends StatelessWidget {
  const _RoundIconButton({
    required this.icon,
    required this.onTap,
    this.tooltip,
  });

  final IconData icon;
  final VoidCallback onTap;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    final button = Material(
      color: NivoColors.cloudSoft,
      shape: CircleBorder(side: BorderSide(color: NivoColors.line)),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(9),
          child: Icon(icon, size: 18, color: NivoColors.ink),
        ),
      ),
    );
    if (tooltip == null) return button;
    return Tooltip(message: tooltip!, child: button);
  }
}
