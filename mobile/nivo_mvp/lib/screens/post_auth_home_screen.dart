import 'package:flutter/material.dart';

import '../data/fintech_mvp_content.dart';
import '../utils/nivo_formatters.dart';
import '../widgets/demo_preview.dart';
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

  @override
  Widget build(BuildContext context) {
    final tabs = [
      HomeTab(state: _tabStates[0]),
      TransactionsTab(state: _tabStates[1]),
      CurrenciesTab(state: _tabStates[2]),
      TradingTab(state: _tabStates[3]),
      CryptoTab(state: _tabStates[4]),
    ];

    return Scaffold(
      backgroundColor: Colors.white,
      bottomNavigationBar: NivoBottomTabBar(
        currentIndex: _currentIndex,
        items: _items,
        onChanged: (value) => setState(() => _currentIndex = value),
      ),
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            NivoTopBar(
              totalBalance: formatMoney(FintechMvpContent.totalBalance),
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
