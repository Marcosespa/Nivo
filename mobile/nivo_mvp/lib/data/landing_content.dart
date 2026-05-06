/// Copy alineado con la landing web (hero, por qué cuántica, escudo).
abstract final class LandingContent {
  static const String appName = 'Nivo';

  static const String heroKicker =
      'Seguridad post-cuántica · alineada con NIST FIPS 203';

  static const String heroTitleLead = 'Tu dinero, blindado contra';

  static const List<String> heroRotating = [
    'el futuro.',
    'la era cuántica.',
    'lo que viene.',
    'el estándar NIST.',
  ];

  static const String heroBody =
      'Billetera digital colombiana con criptografía post-cuántica integrada '
      'desde el diseño: protege hoy lo que seguirá siendo sensible cuando '
      'madure el riesgo cuántico.';

  static const List<TrustPoint> trustPoints = [
    TrustPoint(
      title: 'Ruta regulatoria en Colombia',
      subtitle: 'Aliados alineados con operación local',
    ),
    TrustPoint(
      title: 'NIST FIPS 203 / 204',
      subtitle: 'Estándares de transición post-cuántica',
    ),
    TrustPoint(
      title: 'Pagos en Colombia',
      subtitle: 'Infraestructura tipo Wompi · ACH · PSE',
    ),
    TrustPoint(
      title: 'Controles auditables',
      subtitle: 'ISO 27001 · SOC 2 (objetivo operativo)',
    ),
  ];

  static const String whyBadge = 'Por qué la cuántica importa';
  static const String whyTitle = '¿Qué es lo “cuántico” y por qué Nivo?';
  static const String whyLead =
      'No hace falta entender la física. Conviene saber que la siguiente '
      'generación de máquinas puede dejar cortos métodos que hoy dan por '
      'cerrados bancos y apps. Nivo integra estándares post-cuánticos desde el diseño.';

  static const List<WhyPillar> whyPillars = [
    WhyPillar(
      kicker: 'Qué es, sin física',
      title: 'Una computadora distinta',
      body:
          'La computación cuántica resuelve algunos problemas mucho más rápido que un PC. '
          'En criptografía eso puede afectar candados diseñados hace años.',
    ),
    WhyPillar(
      kicker: 'Por qué te importa',
      title: 'Guardar hoy, leer mañana',
      body:
          'El riesgo es que alguien archive datos cifrados hoy y los abra dentro de años. '
          'Lo que firmas ahora puede seguir siendo sensible mucho tiempo.',
    ),
    WhyPillar(
      kicker: 'Qué ganas con Nivo',
      title: 'Misma app, candado del futuro',
      body:
          'Criptografía post-cuántica alineada con el NIST donde más duele si falla: '
          'identidad, recibos y acuerdos de largo plazo.',
    ),
  ];

  static const String shieldBadge = 'Así lo hacemos contigo';
  static const String shieldTitle = 'Tu dinero,\nblindado para 2045.';
  static const String shieldLead =
      'Tres capas para que identidad, datos y recibos sigan siendo tuyos cuando '
      'la industria termine de migrar. Sin jerga de más.';

  static const List<ShieldStep> shieldSteps = [
    ShieldStep(
      step: '01',
      title: 'Identidad bajo doble candado',
      body:
          'Llaves pensadas para resistir cuando la computación cuántica deje obsoletos métodos actuales.',
    ),
    ShieldStep(
      step: '02',
      title: 'Estándar NIST',
      body:
          'Alineados con FIPS 203/204 que gobiernos y banca global adoptan en la transición.',
    ),
    ShieldStep(
      step: '03',
      title: 'Pagos firmados',
      body:
          'Cada transacción con firma verificable; alterar un recibo se detecta.',
    ),
  ];

  static const String ctaTitle = 'Beta Nivo';
  static const String ctaBody =
      'Deja tu correo en la web o escríbenos para una demo orientada a inversores o partners.';
}

class TrustPoint {
  const TrustPoint({required this.title, required this.subtitle});

  final String title;
  final String subtitle;
}

class WhyPillar {
  const WhyPillar({
    required this.kicker,
    required this.title,
    required this.body,
  });

  final String kicker;
  final String title;
  final String body;
}

class ShieldStep {
  const ShieldStep({
    required this.step,
    required this.title,
    required this.body,
  });

  final String step;
  final String title;
  final String body;
}
