import 'package:flutter/material.dart';

class FintechMvpContent {
  static const double totalBalance = 4872.45;
  static const List<double> totalBalanceTrend = [
    4.12,
    4.18,
    4.21,
    4.16,
    4.28,
    4.35,
    4.41,
    4.47,
    4.59,
    4.63,
    4.71,
    4.87,
  ];

  static const List<HomeQuickCard> homeQuickCards = [
    HomeQuickCard(
      title: 'Cuenta EUR',
      subtitle: 'Principal',
      value: '€3,120.40',
      icon: Icons.account_balance_wallet_outlined,
    ),
    HomeQuickCard(
      title: 'Cuenta USD',
      subtitle: 'Disponible',
      value: '\$1,220.00',
      icon: Icons.attach_money_rounded,
    ),
    HomeQuickCard(
      title: 'Tarjeta física',
      subtitle: 'Terminada en 2410',
      value: 'Activa',
      icon: Icons.credit_card_rounded,
    ),
    HomeQuickCard(
      title: 'Crypto',
      subtitle: 'Valor total',
      value: '€532.05',
      icon: Icons.currency_bitcoin_rounded,
    ),
  ];

  static const List<QuickAction> homeActions = [
    QuickAction(label: 'Enviar', icon: Icons.arrow_upward_rounded),
    QuickAction(label: 'Recibir', icon: Icons.arrow_downward_rounded),
    QuickAction(label: 'Cambiar', icon: Icons.currency_exchange_rounded),
    QuickAction(label: 'Invertir', icon: Icons.show_chart_rounded),
  ];

  static const List<DashboardMetric> dashboardMetrics = [
    DashboardMetric(label: 'Cash', value: '64%', caption: 'EUR + USD'),
    DashboardMetric(label: 'Stocks', value: '21%', caption: '3 posiciones'),
    DashboardMetric(label: 'Crypto', value: '15%', caption: 'BTC · ETH · SOL'),
  ];

  static const List<TransactionItem> transactions = [
    TransactionItem(
      section: 'Hoy',
      title: 'Apple Store',
      subtitle: 'Suscripción iCloud',
      amount: -2.99,
      category: 'Suscripciones',
      reference: 'TXN-09281-APL',
      dateLabel: 'Hoy · 09:12',
      icon: Icons.cloud_outlined,
      type: TransactionType.expense,
    ),
    TransactionItem(
      section: 'Hoy',
      title: 'Transferencia recibida',
      subtitle: 'Laura Gómez',
      amount: 240.00,
      category: 'Transferencia',
      reference: 'TRF-IN-240-001',
      dateLabel: 'Hoy · 08:44',
      icon: Icons.south_west_rounded,
      type: TransactionType.income,
    ),
    TransactionItem(
      section: 'Ayer',
      title: 'Uber',
      subtitle: 'Madrid',
      amount: -18.40,
      category: 'Movilidad',
      reference: 'UBR-88271-MAD',
      dateLabel: 'Ayer · 22:18',
      icon: Icons.local_taxi_outlined,
      type: TransactionType.expense,
    ),
    TransactionItem(
      section: 'Ayer',
      title: 'Cambio EUR → USD',
      subtitle: 'FX instantáneo',
      amount: -300.00,
      category: 'Cambio',
      reference: 'FX-300-EURUSD',
      dateLabel: 'Ayer · 16:05',
      icon: Icons.currency_exchange_rounded,
      type: TransactionType.transfer,
    ),
    TransactionItem(
      section: 'Esta semana',
      title: 'Tesla',
      subtitle: 'Compra fraccionada',
      amount: -120.00,
      category: 'Trading',
      reference: 'STK-TSLA-0102',
      dateLabel: 'Mar · 15:20',
      icon: Icons.show_chart_rounded,
      type: TransactionType.transfer,
    ),
    TransactionItem(
      section: 'Esta semana',
      title: 'Nómina',
      subtitle: 'Remote payroll',
      amount: 2400.00,
      category: 'Ingreso',
      reference: 'PAY-APR-2026',
      dateLabel: 'Lun · 08:00',
      icon: Icons.account_balance_outlined,
      type: TransactionType.income,
    ),
    TransactionItem(
      section: 'Esta semana',
      title: 'Binance Transfer',
      subtitle: 'Compra BTC',
      amount: -210.50,
      category: 'Crypto',
      reference: 'CRY-BTC-8831',
      dateLabel: 'Dom · 18:31',
      icon: Icons.currency_bitcoin_rounded,
      type: TransactionType.transfer,
    ),
  ];

  static const List<CurrencyPocket> currencyPockets = [
    CurrencyPocket(code: 'EUR', name: 'Euro', flag: '🇪🇺', balance: 3120.40),
    CurrencyPocket(
        code: 'USD', name: 'US Dollar', flag: '🇺🇸', balance: 1318.10),
    CurrencyPocket(
        code: 'GBP', name: 'Pound Sterling', flag: '🇬🇧', balance: 582.24),
    CurrencyPocket(
        code: 'CZK', name: 'Czech Koruna', flag: '🇨🇿', balance: 12840.00),
  ];

  static const List<FxRateSeries> fxPairs = [
    FxRateSeries(
      pair: 'EUR/USD',
      rate: 1.0874,
      changePct: 0.42,
      points: [1.06, 1.061, 1.065, 1.07, 1.074, 1.079, 1.087],
    ),
    FxRateSeries(
      pair: 'EUR/GBP',
      rate: 0.8521,
      changePct: -0.18,
      points: [0.861, 0.859, 0.857, 0.856, 0.854, 0.853, 0.852],
    ),
    FxRateSeries(
      pair: 'EUR/CZK',
      rate: 25.2400,
      changePct: 0.24,
      points: [25.11, 25.13, 25.18, 25.2, 25.22, 25.23, 25.24],
    ),
  ];

  static const List<PopularCurrency> popularCurrencies = [
    PopularCurrency(
        flag: '🇺🇸',
        code: 'USD',
        name: 'US Dollar',
        rateLabel: '1 EUR = 1.0874 USD'),
    PopularCurrency(
        flag: '🇬🇧',
        code: 'GBP',
        name: 'British Pound',
        rateLabel: '1 EUR = 0.8521 GBP'),
    PopularCurrency(
        flag: '🇨🇿',
        code: 'CZK',
        name: 'Czech Koruna',
        rateLabel: '1 EUR = 25.24 CZK'),
    PopularCurrency(
        flag: '🇨🇭',
        code: 'CHF',
        name: 'Swiss Franc',
        rateLabel: '1 EUR = 0.9780 CHF'),
  ];

  static const List<StockQuote> stocks = [
    StockQuote(
      symbol: 'AAPL',
      name: 'Apple',
      price: 214.32,
      changePct: 1.82,
      candles: [
        CandlePoint(open: 208, high: 212, low: 206, close: 210),
        CandlePoint(open: 210, high: 214, low: 209, close: 213),
        CandlePoint(open: 213, high: 216, low: 211, close: 214),
        CandlePoint(open: 214, high: 217, low: 212, close: 216),
        CandlePoint(open: 216, high: 218, low: 213, close: 214),
        CandlePoint(open: 214, high: 215, low: 211, close: 212),
        CandlePoint(open: 212, high: 214, low: 210, close: 213),
        CandlePoint(open: 213, high: 216, low: 212, close: 214),
      ],
    ),
    StockQuote(
      symbol: 'TSLA',
      name: 'Tesla',
      price: 173.86,
      changePct: -0.94,
      candles: [
        CandlePoint(open: 182, high: 184, low: 178, close: 180),
        CandlePoint(open: 180, high: 181, low: 176, close: 177),
        CandlePoint(open: 177, high: 179, low: 172, close: 174),
        CandlePoint(open: 174, high: 176, low: 171, close: 173),
        CandlePoint(open: 173, high: 175, low: 170, close: 174),
        CandlePoint(open: 174, high: 176, low: 172, close: 173),
      ],
    ),
    StockQuote(
      symbol: 'NVDA',
      name: 'NVIDIA',
      price: 942.50,
      changePct: 2.64,
      candles: [
        CandlePoint(open: 910, high: 928, low: 902, close: 920),
        CandlePoint(open: 920, high: 936, low: 915, close: 934),
        CandlePoint(open: 934, high: 948, low: 930, close: 942),
        CandlePoint(open: 942, high: 950, low: 938, close: 947),
      ],
    ),
    StockQuote(
      symbol: 'MSFT',
      name: 'Microsoft',
      price: 428.11,
      changePct: 0.61,
      candles: [
        CandlePoint(open: 419, high: 423, low: 418, close: 421),
        CandlePoint(open: 421, high: 426, low: 420, close: 425),
        CandlePoint(open: 425, high: 429, low: 424, close: 428),
      ],
    ),
  ];

  static const List<StockPosition> positions = [
    StockPosition(
        symbol: 'AAPL',
        shares: 4.2,
        averagePrice: 198.10,
        currentPrice: 214.32),
    StockPosition(
        symbol: 'NVDA',
        shares: 0.85,
        averagePrice: 958.40,
        currentPrice: 942.50),
    StockPosition(
        symbol: 'MSFT',
        shares: 2.0,
        averagePrice: 402.35,
        currentPrice: 428.11),
  ];

  static const List<String> initialWatchlist = ['AAPL', 'TSLA', 'NVDA'];

  static const List<CryptoAsset> cryptoAssets = [
    CryptoAsset(
      symbol: 'BTC',
      name: 'Bitcoin',
      price: 64280.00,
      changePct: 3.42,
      quantity: 0.0048,
      points: [60200, 61100, 62050, 62500, 63120, 63950, 64280],
    ),
    CryptoAsset(
      symbol: 'ETH',
      name: 'Ethereum',
      price: 3180.50,
      changePct: 1.16,
      quantity: 0.38,
      points: [2990, 3025, 3070, 3100, 3120, 3158, 3180],
    ),
    CryptoAsset(
      symbol: 'SOL',
      name: 'Solana',
      price: 144.30,
      changePct: -2.10,
      quantity: 6.2,
      points: [150, 148, 146, 149, 147, 145, 144.3],
    ),
  ];

  static const List<CryptoMover> cryptoMovers = [
    CryptoMover(symbol: 'DOGE', changePct: 8.14),
    CryptoMover(symbol: 'TON', changePct: 5.82),
    CryptoMover(symbol: 'AVAX', changePct: 4.91),
  ];
}

class HomeQuickCard {
  const HomeQuickCard({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.icon,
  });

  final String title;
  final String subtitle;
  final String value;
  final IconData icon;
}

class QuickAction {
  const QuickAction({
    required this.label,
    required this.icon,
  });

  final String label;
  final IconData icon;
}

class DashboardMetric {
  const DashboardMetric({
    required this.label,
    required this.value,
    required this.caption,
  });

  final String label;
  final String value;
  final String caption;
}

enum TransactionType {
  income,
  expense,
  transfer,
}

class TransactionItem {
  const TransactionItem({
    required this.section,
    required this.title,
    required this.subtitle,
    required this.amount,
    required this.category,
    required this.reference,
    required this.dateLabel,
    required this.icon,
    required this.type,
  });

  final String section;
  final String title;
  final String subtitle;
  final double amount;
  final String category;
  final String reference;
  final String dateLabel;
  final IconData icon;
  final TransactionType type;
}

class CurrencyPocket {
  const CurrencyPocket({
    required this.code,
    required this.name,
    required this.flag,
    required this.balance,
  });

  final String code;
  final String name;
  final String flag;
  final double balance;
}

class FxRateSeries {
  const FxRateSeries({
    required this.pair,
    required this.rate,
    required this.changePct,
    required this.points,
  });

  final String pair;
  final double rate;
  final double changePct;
  final List<double> points;
}

class PopularCurrency {
  const PopularCurrency({
    required this.flag,
    required this.code,
    required this.name,
    required this.rateLabel,
  });

  final String flag;
  final String code;
  final String name;
  final String rateLabel;
}

class StockQuote {
  const StockQuote({
    required this.symbol,
    required this.name,
    required this.price,
    required this.changePct,
    required this.candles,
  });

  final String symbol;
  final String name;
  final double price;
  final double changePct;
  final List<CandlePoint> candles;
}

class StockPosition {
  const StockPosition({
    required this.symbol,
    required this.shares,
    required this.averagePrice,
    required this.currentPrice,
  });

  final String symbol;
  final double shares;
  final double averagePrice;
  final double currentPrice;
}

class CandlePoint {
  const CandlePoint({
    required this.open,
    required this.high,
    required this.low,
    required this.close,
  });

  final double open;
  final double high;
  final double low;
  final double close;
}

class CryptoAsset {
  const CryptoAsset({
    required this.symbol,
    required this.name,
    required this.price,
    required this.changePct,
    required this.quantity,
    required this.points,
  });

  final String symbol;
  final String name;
  final double price;
  final double changePct;
  final double quantity;
  final List<double> points;
}

class CryptoMover {
  const CryptoMover({
    required this.symbol,
    required this.changePct,
  });

  final String symbol;
  final double changePct;
}
