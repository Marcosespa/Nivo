import 'package:flutter/material.dart';

abstract final class AppPreviewContent {
  static const String userName = 'Marcos';
  static const String balanceLabel = 'COP 18.450.000';
  static const String balanceDelta = '+12.4% este mes';
  static const String balanceCaption =
      'Cuenta principal · movimientos firmados · Bogotá, CO';

  static const List<double> balanceTrend = [
    0.34,
    0.38,
    0.42,
    0.41,
    0.47,
    0.51,
    0.56,
    0.58,
    0.63,
    0.69,
    0.76,
    0.84,
  ];

  static const List<QuickActionItem> quickActions = [
    QuickActionItem(
      label: 'Enviar',
      subtitle: 'Transferir',
      icon: Icons.arrow_upward_rounded,
    ),
    QuickActionItem(
      label: 'Recibir',
      subtitle: 'Tu llave',
      icon: Icons.arrow_downward_rounded,
    ),
    QuickActionItem(
      label: 'Tarjeta',
      subtitle: 'Virtual',
      icon: Icons.credit_card_rounded,
    ),
    QuickActionItem(
      label: 'Cambiar',
      subtitle: 'USD / EUR',
      icon: Icons.currency_exchange_rounded,
    ),
  ];

  static const List<PocketPreview> pockets = [
    PocketPreview(
      label: 'COP',
      title: 'Disponible',
      amount: '18.450.000',
      delta: '+2.8%',
      note: 'Operación diaria',
    ),
    PocketPreview(
      label: 'USD',
      title: 'Cobros globales',
      amount: '4,280',
      delta: '+640',
      note: 'Freelance y partners',
    ),
    PocketPreview(
      label: 'EUR',
      title: 'Reserva viaje',
      amount: '1,140',
      delta: '+4.3%',
      note: 'Liquidez separada',
    ),
  ];

  static const List<ActivityPreview> activities = [
    ActivityPreview(
      title: 'Transferencia recibida',
      subtitle: 'Laura Gomez · llave segura',
      amount: '+ COP 850.000',
      meta: 'Recibo firmado · hace 4 min',
      positive: true,
      icon: Icons.south_west_rounded,
    ),
    ActivityPreview(
      title: 'Pago PSE',
      subtitle: 'Wompi · utilidad operativa',
      amount: '- COP 128.400',
      meta: 'Verificado · hoy 08:42',
      positive: false,
      icon: Icons.north_east_rounded,
    ),
    ActivityPreview(
      title: 'Compra internacional',
      subtitle: 'Stripe Atlas · tarjeta virtual',
      amount: '- USD 42.00',
      meta: 'Tokenizada · ayer',
      positive: false,
      icon: Icons.credit_card_rounded,
    ),
  ];

  static const List<TransferDraft> transferDrafts = [
    TransferDraft(
      title: 'Nómina producto',
      subtitle: 'Viernes · 9:00 AM',
      amount: 'COP 4.200.000',
      route: 'Bancolombia Empresas',
    ),
    TransferDraft(
      title: 'Tesorería USD',
      subtitle: 'Automático · cada lunes',
      amount: 'USD 1,800',
      route: 'Pocket global',
    ),
  ];

  static const List<CategorySpend> spendCategories = [
    CategorySpend(label: 'Operación', amount: 'COP 3.2M', progress: 0.82),
    CategorySpend(label: 'Equipo', amount: 'COP 2.4M', progress: 0.64),
    CategorySpend(label: 'Viajes', amount: 'COP 1.1M', progress: 0.29),
    CategorySpend(label: 'Software', amount: 'COP 860K', progress: 0.22),
  ];

  static const List<ShieldSignal> shieldSignals = [
    ShieldSignal(
      label: 'Estándares',
      value: 'FIPS 203 / 204',
      caption: 'Llaves y firmas listas para transición',
      icon: Icons.verified_outlined,
    ),
    ShieldSignal(
      label: 'Recibos',
      value: '128',
      caption: 'Documentos firmados en los últimos 30 días',
      icon: Icons.receipt_long_outlined,
    ),
    ShieldSignal(
      label: 'Dispositivos',
      value: '2 activos',
      caption: 'iPhone principal + backup auditado',
      icon: Icons.devices_outlined,
    ),
    ShieldSignal(
      label: 'Recuperación',
      value: '2 de 3',
      caption: 'Split seguro para acceso de emergencia',
      icon: Icons.key_outlined,
    ),
  ];

  static const List<AuditEntry> auditTrail = [
    AuditEntry(
      title: 'Llave híbrida renovada',
      subtitle: 'Actualización programada completada',
      timestamp: 'Hoy · 07:14',
    ),
    AuditEntry(
      title: 'Nuevo recibo firmado',
      subtitle: 'Transferencia a partner de pagos',
      timestamp: 'Ayer · 19:06',
    ),
    AuditEntry(
      title: 'Chequeo de dispositivo',
      subtitle: 'Face ID y sesión protegida verificados',
      timestamp: 'Ayer · 08:20',
    ),
  ];

  static const List<ProfileAction> profileActions = [
    ProfileAction(
      title: 'Cuenta y límites',
      subtitle: 'Topes, bolsillos y perfiles de uso',
      icon: Icons.tune_rounded,
    ),
    ProfileAction(
      title: 'Soporte y partners',
      subtitle: 'Hablar con Nivo o escalar un recibo',
      icon: Icons.support_agent_rounded,
    ),
    ProfileAction(
      title: 'Documentos',
      subtitle: 'Términos, privacidad y disclosures',
      icon: Icons.description_outlined,
    ),
    ProfileAction(
      title: 'Seguridad',
      subtitle: 'Biometría, recuperación y sesiones',
      icon: Icons.lock_outline_rounded,
    ),
  ];
}

class QuickActionItem {
  const QuickActionItem({
    required this.label,
    required this.subtitle,
    required this.icon,
  });

  final String label;
  final String subtitle;
  final IconData icon;
}

class PocketPreview {
  const PocketPreview({
    required this.label,
    required this.title,
    required this.amount,
    required this.delta,
    required this.note,
  });

  final String label;
  final String title;
  final String amount;
  final String delta;
  final String note;
}

class ActivityPreview {
  const ActivityPreview({
    required this.title,
    required this.subtitle,
    required this.amount,
    required this.meta,
    required this.positive,
    required this.icon,
  });

  final String title;
  final String subtitle;
  final String amount;
  final String meta;
  final bool positive;
  final IconData icon;
}

class TransferDraft {
  const TransferDraft({
    required this.title,
    required this.subtitle,
    required this.amount,
    required this.route,
  });

  final String title;
  final String subtitle;
  final String amount;
  final String route;
}

class CategorySpend {
  const CategorySpend({
    required this.label,
    required this.amount,
    required this.progress,
  });

  final String label;
  final String amount;
  final double progress;
}

class ShieldSignal {
  const ShieldSignal({
    required this.label,
    required this.value,
    required this.caption,
    required this.icon,
  });

  final String label;
  final String value;
  final String caption;
  final IconData icon;
}

class AuditEntry {
  const AuditEntry({
    required this.title,
    required this.subtitle,
    required this.timestamp,
  });

  final String title;
  final String subtitle;
  final String timestamp;
}

class ProfileAction {
  const ProfileAction({
    required this.title,
    required this.subtitle,
    required this.icon,
  });

  final String title;
  final String subtitle;
  final IconData icon;
}
