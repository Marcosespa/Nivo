import 'package:flutter/material.dart';

/// Mock data para la maqueta visual del app NIVO (5 pestañas).
/// Ningún dato proviene del backend. Todo es contenido de demostración.
abstract final class NivoAppContent {
  // ───────── Usuario ─────────
  static const String userName = 'Marcos';
  static const String userInitials = 'ME';
  static const String userEmail = 'marcos@nivo.co';

  // ───────── Saldo global (Home) ─────────
  static const String totalDisplay = '€ 4.872,45';
  static const String totalCurrency = 'EUR';
  static const double totalChangePct = 2.4;

  // ───────── Cuentas del Home ─────────
  static const List<AccountCardData> accountCards = [
    AccountCardData(
      title: 'Cuenta EUR',
      amount: '€ 3.104,12',
      subtitle: 'Principal',
      flag: '🇪🇺',
      positiveDelta: '+€ 82 · 7d',
      isPrimary: true,
    ),
    AccountCardData(
      title: 'Cuenta USD',
      amount: '\$ 1.240,80',
      subtitle: 'Cobros globales',
      flag: '🇺🇸',
      positiveDelta: '+\$ 18 · 7d',
    ),
    AccountCardData(
      title: 'Tarjeta física',
      amount: '€ 420,00',
      subtitle: '•••• 2410',
      flag: '💳',
      positiveDelta: 'Activa',
    ),
    AccountCardData(
      title: 'Crypto',
      amount: '€ 1.107,53',
      subtitle: 'BTC · ETH · SOL',
      flag: '₿',
      positiveDelta: '+4,1% · 24h',
    ),
  ];

  static const List<HomeAction> homeActions = [
    HomeAction(icon: Icons.north_east_rounded, label: 'Enviar'),
    HomeAction(icon: Icons.south_west_rounded, label: 'Recibir'),
    HomeAction(icon: Icons.swap_horiz_rounded, label: 'Cambiar'),
    HomeAction(icon: Icons.insights_rounded, label: 'Invertir'),
  ];

  // Tendencia para el sheet "Ver más" del Home (últimos 30 días)
  static const List<double> totalTrend = [
    3.82, 3.95, 3.71, 3.88, 4.02, 4.11, 4.06,
    4.21, 4.10, 4.32, 4.28, 4.45, 4.52, 4.40,
    4.58, 4.61, 4.72, 4.65, 4.70, 4.78, 4.69,
    4.80, 4.84, 4.81, 4.88, 4.79, 4.85, 4.90,
    4.87, 4.87,
  ];

  static const List<CategorySpendData> monthSpend = [
    CategorySpendData(label: 'Mercado', amount: '€ 320,40', progress: 0.72),
    CategorySpendData(label: 'Transporte', amount: '€ 184,10', progress: 0.54),
    CategorySpendData(label: 'Restaurantes', amount: '€ 138,90', progress: 0.41),
    CategorySpendData(label: 'Suscripciones', amount: '€ 74,99', progress: 0.22),
  ];

  // ───────── Movimientos ─────────
  static const List<MovementGroup> movements = [
    MovementGroup(
      label: 'Hoy',
      items: [
        MovementEntry(
          title: 'Rappi',
          subtitle: 'Mercado',
          amount: '- € 28,40',
          category: MovementKind.expense,
          icon: Icons.shopping_basket_rounded,
          timestamp: '14:08',
          reference: 'NIVO-87F2-QR',
          method: 'Tarjeta virtual · NFC',
        ),
        MovementEntry(
          title: 'Transferencia · Laura',
          subtitle: 'SEPA Instant',
          amount: '+ € 150,00',
          category: MovementKind.income,
          icon: Icons.south_west_rounded,
          timestamp: '10:42',
          reference: 'SEPA-9AC1-2410',
          method: 'SEPA Instant · IBAN',
        ),
        MovementEntry(
          title: 'Nómina · Globant',
          subtitle: 'Salario mensual',
          amount: '+ € 3.850,00',
          category: MovementKind.income,
          icon: Icons.account_balance_wallet_outlined,
          timestamp: '08:01',
          reference: 'WIRE-334D-0919',
          method: 'Transferencia bancaria',
        ),
      ],
    ),
    MovementGroup(
      label: 'Ayer',
      items: [
        MovementEntry(
          title: 'Uber',
          subtitle: 'Transporte',
          amount: '- € 12,30',
          category: MovementKind.expense,
          icon: Icons.local_taxi_rounded,
          timestamp: '22:17',
          reference: 'CARD-8021-UBER',
          method: 'Tarjeta virtual',
        ),
        MovementEntry(
          title: 'Transferencia a Diego',
          subtitle: 'Renta compartida',
          amount: '- € 480,00',
          category: MovementKind.transfer,
          icon: Icons.swap_horiz_rounded,
          timestamp: '20:14',
          reference: 'SEPA-3BB0-REN',
          method: 'Nivo P2P',
        ),
        MovementEntry(
          title: 'Netflix',
          subtitle: 'Suscripción',
          amount: '- € 15,99',
          category: MovementKind.expense,
          icon: Icons.subscriptions_rounded,
          timestamp: '09:00',
          reference: 'SUB-NFLX-04',
          method: 'Recurrente',
        ),
      ],
    ),
    MovementGroup(
      label: 'Esta semana',
      items: [
        MovementEntry(
          title: 'Conversión EUR → USD',
          subtitle: 'Cambio de divisa',
          amount: '- € 500,00',
          category: MovementKind.transfer,
          icon: Icons.currency_exchange_rounded,
          timestamp: 'lun 18:14',
          reference: 'FX-4411-USD',
          method: 'Tasa spot · 1,0742',
        ),
        MovementEntry(
          title: 'Freelance · Partner',
          subtitle: 'Cobro internacional',
          amount: '+ \$ 640,00',
          category: MovementKind.income,
          icon: Icons.work_outline_rounded,
          timestamp: 'lun 11:28',
          reference: 'WIRE-PNR-8821',
          method: 'Wire USD',
        ),
      ],
    ),
  ];

  // ───────── Divisas ─────────
  static const List<CurrencyBalance> currencyBalances = [
    CurrencyBalance(code: 'EUR', flag: '🇪🇺', amount: '3.104,12', subtitle: 'Principal'),
    CurrencyBalance(code: 'USD', flag: '🇺🇸', amount: '1.240,80', subtitle: 'Global'),
    CurrencyBalance(code: 'GBP', flag: '🇬🇧', amount: '518,40', subtitle: 'Viaje'),
    CurrencyBalance(code: 'CZK', flag: '🇨🇿', amount: '4.260,00', subtitle: 'Reserva'),
  ];

  static const List<CurrencyRate> popularRates = [
    CurrencyRate(code: 'USD', flag: '🇺🇸', name: 'Dólar estadounidense', rate: '1,0742', delta: '+0,12%'),
    CurrencyRate(code: 'GBP', flag: '🇬🇧', name: 'Libra esterlina', rate: '0,8548', delta: '-0,04%'),
    CurrencyRate(code: 'CHF', flag: '🇨🇭', name: 'Franco suizo', rate: '0,9461', delta: '+0,08%'),
    CurrencyRate(code: 'JPY', flag: '🇯🇵', name: 'Yen japonés', rate: '162,30', delta: '+0,21%'),
    CurrencyRate(code: 'MXN', flag: '🇲🇽', name: 'Peso mexicano', rate: '18,94', delta: '-0,18%'),
    CurrencyRate(code: 'BRL', flag: '🇧🇷', name: 'Real brasileño', rate: '5,62', delta: '+0,34%'),
  ];

  // Serie sparkline para la tasa EUR→USD (últimos 14 d)
  static const List<double> fxEurUsdTrend = [
    1.070, 1.068, 1.072, 1.074, 1.075, 1.073, 1.071,
    1.069, 1.072, 1.076, 1.078, 1.075, 1.074, 1.0742,
  ];

  // ───────── Trading (Stocks) ─────────
  static const String tradingTotal = '€ 2.148,60';
  static const String tradingDelta = '+ € 42,30 · hoy';

  static const List<StockPosition> stockPositions = [
    StockPosition(
      symbol: 'AAPL',
      name: 'Apple Inc.',
      shares: '4',
      price: '\$ 231,08',
      deltaPct: '+1,24%',
      positive: true,
    ),
    StockPosition(
      symbol: 'TSLA',
      name: 'Tesla',
      shares: '2',
      price: '\$ 248,50',
      deltaPct: '-0,84%',
      positive: false,
    ),
    StockPosition(
      symbol: 'MSFT',
      name: 'Microsoft',
      shares: '3',
      price: '\$ 416,72',
      deltaPct: '+0,52%',
      positive: true,
    ),
  ];

  static const List<StockWatch> stockWatchlist = [
    StockWatch(symbol: 'NVDA', name: 'NVIDIA', price: '\$ 870,14', deltaPct: '+2,18%', positive: true),
    StockWatch(symbol: 'GOOG', name: 'Alphabet', price: '\$ 171,40', deltaPct: '+0,36%', positive: true),
    StockWatch(symbol: 'AMZN', name: 'Amazon', price: '\$ 184,25', deltaPct: '-0,11%', positive: false),
    StockWatch(symbol: 'META', name: 'Meta', price: '\$ 502,91', deltaPct: '+0,94%', positive: true),
  ];

  // 24 velas (open, high, low, close) para AAPL
  static const List<Candle> candlesAapl = [
    Candle(226.1, 227.4, 225.6, 226.8),
    Candle(226.8, 228.2, 226.3, 227.9),
    Candle(227.9, 228.5, 227.0, 227.2),
    Candle(227.2, 228.0, 226.4, 227.6),
    Candle(227.6, 229.0, 227.3, 228.7),
    Candle(228.7, 229.4, 228.1, 228.3),
    Candle(228.3, 228.9, 227.6, 228.0),
    Candle(228.0, 229.2, 227.8, 229.1),
    Candle(229.1, 230.2, 229.0, 230.0),
    Candle(230.0, 230.6, 229.4, 229.7),
    Candle(229.7, 230.1, 229.0, 229.2),
    Candle(229.2, 230.5, 229.1, 230.3),
    Candle(230.3, 231.2, 230.0, 231.0),
    Candle(231.0, 231.4, 230.3, 230.6),
    Candle(230.6, 231.0, 230.0, 230.2),
    Candle(230.2, 230.9, 229.8, 230.8),
    Candle(230.8, 231.6, 230.5, 231.3),
    Candle(231.3, 231.8, 230.9, 230.9),
    Candle(230.9, 231.2, 230.1, 230.4),
    Candle(230.4, 231.0, 230.2, 230.9),
    Candle(230.9, 231.5, 230.6, 231.2),
    Candle(231.2, 231.6, 230.9, 231.4),
    Candle(231.4, 231.8, 231.0, 231.1),
    Candle(231.1, 231.5, 230.8, 231.08),
  ];

  // ───────── Crypto ─────────
  static const String cryptoTotal = '€ 1.107,53';
  static const String cryptoDelta = '+ 4,1% · 24h';

  static const List<CryptoCoin> cryptoHoldings = [
    CryptoCoin(
      symbol: 'BTC',
      name: 'Bitcoin',
      mark: '₿',
      tint: Color(0xFFF7931A),
      price: '€ 64.120,00',
      deltaPct: '+2,8%',
      positive: true,
      holdings: '€ 642,30',
      amount: '0,01002 BTC',
    ),
    CryptoCoin(
      symbol: 'ETH',
      name: 'Ethereum',
      mark: 'Ξ',
      tint: Color(0xFF627EEA),
      price: '€ 3.048,20',
      deltaPct: '+1,6%',
      positive: true,
      holdings: '€ 310,40',
      amount: '0,1018 ETH',
    ),
    CryptoCoin(
      symbol: 'SOL',
      name: 'Solana',
      mark: '◎',
      tint: Color(0xFF14F195),
      price: '€ 148,90',
      deltaPct: '-0,9%',
      positive: false,
      holdings: '€ 92,10',
      amount: '0,6184 SOL',
    ),
    CryptoCoin(
      symbol: 'ADA',
      name: 'Cardano',
      mark: '₳',
      tint: Color(0xFF0033AD),
      price: '€ 0,41',
      deltaPct: '+3,2%',
      positive: true,
      holdings: '€ 62,73',
      amount: '153,00 ADA',
    ),
  ];

  static const List<CryptoMover> cryptoTopMovers = [
    CryptoMover(symbol: 'PEPE', name: 'Pepe', deltaPct: '+18,4%'),
    CryptoMover(symbol: 'AVAX', name: 'Avalanche', deltaPct: '+7,2%'),
    CryptoMover(symbol: 'LINK', name: 'Chainlink', deltaPct: '+5,8%'),
    CryptoMover(symbol: 'DOT', name: 'Polkadot', deltaPct: '-2,1%'),
  ];

  // Serie de precios BTC (24 puntos)
  static const List<double> btcTrend = [
    62.4, 62.8, 62.3, 62.6, 62.9, 63.4, 63.1, 63.6,
    63.9, 63.7, 63.5, 63.8, 64.0, 63.7, 63.9, 64.2,
    64.4, 64.1, 64.3, 64.0, 64.2, 64.5, 64.3, 64.12,
  ];
}

// ═══════════════ Modelos ═══════════════

class AccountCardData {
  const AccountCardData({
    required this.title,
    required this.amount,
    required this.subtitle,
    required this.flag,
    required this.positiveDelta,
    this.isPrimary = false,
  });
  final String title;
  final String amount;
  final String subtitle;
  final String flag;
  final String positiveDelta;
  final bool isPrimary;
}

class HomeAction {
  const HomeAction({required this.icon, required this.label});
  final IconData icon;
  final String label;
}

class CategorySpendData {
  const CategorySpendData({
    required this.label,
    required this.amount,
    required this.progress,
  });
  final String label;
  final String amount;
  final double progress;
}

enum MovementKind { income, expense, transfer }

class MovementGroup {
  const MovementGroup({required this.label, required this.items});
  final String label;
  final List<MovementEntry> items;
}

class MovementEntry {
  const MovementEntry({
    required this.title,
    required this.subtitle,
    required this.amount,
    required this.category,
    required this.icon,
    required this.timestamp,
    required this.reference,
    required this.method,
  });
  final String title;
  final String subtitle;
  final String amount;
  final MovementKind category;
  final IconData icon;
  final String timestamp;
  final String reference;
  final String method;
}

class CurrencyBalance {
  const CurrencyBalance({
    required this.code,
    required this.flag,
    required this.amount,
    required this.subtitle,
  });
  final String code;
  final String flag;
  final String amount;
  final String subtitle;
}

class CurrencyRate {
  const CurrencyRate({
    required this.code,
    required this.flag,
    required this.name,
    required this.rate,
    required this.delta,
  });
  final String code;
  final String flag;
  final String name;
  final String rate;
  final String delta;
}

class StockPosition {
  const StockPosition({
    required this.symbol,
    required this.name,
    required this.shares,
    required this.price,
    required this.deltaPct,
    required this.positive,
  });
  final String symbol;
  final String name;
  final String shares;
  final String price;
  final String deltaPct;
  final bool positive;
}

class StockWatch {
  const StockWatch({
    required this.symbol,
    required this.name,
    required this.price,
    required this.deltaPct,
    required this.positive,
  });
  final String symbol;
  final String name;
  final String price;
  final String deltaPct;
  final bool positive;
}

class Candle {
  const Candle(this.open, this.high, this.low, this.close);
  final double open;
  final double high;
  final double low;
  final double close;
}

class CryptoCoin {
  const CryptoCoin({
    required this.symbol,
    required this.name,
    required this.mark,
    required this.tint,
    required this.price,
    required this.deltaPct,
    required this.positive,
    required this.holdings,
    required this.amount,
  });
  final String symbol;
  final String name;
  final String mark;
  final Color tint;
  final String price;
  final String deltaPct;
  final bool positive;
  final String holdings;
  final String amount;
}

class CryptoMover {
  const CryptoMover({
    required this.symbol,
    required this.name,
    required this.deltaPct,
  });
  final String symbol;
  final String name;
  final String deltaPct;
}
