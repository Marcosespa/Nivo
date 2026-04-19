import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../data/app_preview_content.dart';
import '../data/landing_content.dart';
import '../navigation/app_navigator.dart';
import '../theme/nivo_colors.dart';
import '../widgets/fade_in_up.dart';
import '../widgets/nivo_charts.dart';
import '../widgets/nivo_logo.dart';
import '../widgets/rotating_phrase.dart';

class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen> {
  final _scroll = ScrollController();
  final _whyKey = GlobalKey();

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  void _scrollToWhy() {
    final ctx = _whyKey.currentContext;
    if (ctx != null) {
      Scrollable.ensureVisible(
        ctx,
        duration: const Duration(milliseconds: 520),
        curve: Curves.easeOutCubic,
        alignment: 0.08,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        controller: _scroll,
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverAppBar(
            floating: true,
            snap: true,
            elevation: 0,
            backgroundColor: NivoColors.paper.withValues(alpha: 0.94),
            title: const NivoLogo(size: 32),
            actions: [
              TextButton(
                onPressed: () => AppNavigator.goLogin(context),
                child: Text(
                  'Entrar',
                  style: GoogleFonts.inter(
                    fontWeight: FontWeight.w600,
                    color: NivoColors.ink,
                  ),
                ),
              ),
              const SizedBox(width: 4),
            ],
          ),
          SliverToBoxAdapter(
            child: FadeInUp(
              child: _HeroBlock(
                onRegister: () => AppNavigator.goRegister(context),
                onLogin: () => AppNavigator.goLogin(context),
                onWhyQuantum: _scrollToWhy,
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: FadeInUp(
              delay: const Duration(milliseconds: 80),
              child: _TrustStrip(),
            ),
          ),
          SliverToBoxAdapter(
            child: FadeInUp(
              delay: const Duration(milliseconds: 140),
              child: _WhyQuantumSection(key: _whyKey),
            ),
          ),
          const SliverToBoxAdapter(
            child: FadeInUp(
              delay: Duration(milliseconds: 200),
              child: _ShieldSection(),
            ),
          ),
          SliverToBoxAdapter(
            child: FadeInUp(
              delay: const Duration(milliseconds: 260),
              child: _CtaSection(
                onRegister: () => AppNavigator.goRegister(context),
              ),
            ),
          ),
          const SliverToBoxAdapter(child: SizedBox(height: 48)),
        ],
      ),
    );
  }
}

class _HeroBlock extends StatelessWidget {
  const _HeroBlock({
    required this.onRegister,
    required this.onLogin,
    required this.onWhyQuantum,
  });

  final VoidCallback onRegister;
  final VoidCallback onLogin;
  final VoidCallback onWhyQuantum;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            LandingContent.heroKicker.toUpperCase(),
            style: GoogleFonts.jetBrainsMono(
              fontSize: 10,
              letterSpacing: 2.8,
              color: NivoColors.mist,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 20),
          Wrap(
            crossAxisAlignment: WrapCrossAlignment.end,
            spacing: 6,
            runSpacing: 8,
            children: [
              Text(
                LandingContent.heroTitleLead,
                style: GoogleFonts.inter(
                  fontSize: 32,
                  fontWeight: FontWeight.w600,
                  height: 1.05,
                  letterSpacing: -1.2,
                  color: NivoColors.ink,
                ),
              ),
              const RotatingPhrase(phrases: LandingContent.heroRotating),
            ],
          ),
          const SizedBox(height: 20),
          Text(
            LandingContent.heroBody,
            style: GoogleFonts.inter(
              fontSize: 17,
              height: 1.55,
              color: NivoColors.stone,
            ),
          ),
          const SizedBox(height: 28),
          Row(
            children: [
              Expanded(
                child: FilledButton(
                  onPressed: onRegister,
                  child: const Text('Registrarme'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          OutlinedButton(
            onPressed: onWhyQuantum,
            child: const Text('Saber más: por qué cuántica'),
          ),
          const SizedBox(height: 8),
          Center(
            child: TextButton(
              onPressed: onLogin,
              child: Text(
                'Ya tengo cuenta · Entrar',
                style: GoogleFonts.inter(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: NivoColors.forest,
                ),
              ),
            ),
          ),
          const SizedBox(height: 28),
          const _PhonePreviewMock(),
        ],
      ),
    );
  }
}

class _PhonePreviewMock extends StatelessWidget {
  const _PhonePreviewMock();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        width: 284,
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: NivoColors.ink,
          borderRadius: BorderRadius.circular(34),
          boxShadow: [
            BoxShadow(
              color: NivoColors.ink.withValues(alpha: 0.12),
              blurRadius: 32,
              offset: const Offset(0, 20),
            ),
          ],
        ),
        child: Container(
          padding: const EdgeInsets.fromLTRB(16, 18, 16, 18),
          decoration: BoxDecoration(
            color: NivoColors.paper,
            borderRadius: BorderRadius.circular(26),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    'Inicio',
                    style: GoogleFonts.inter(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: NivoColors.ink,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                    decoration: BoxDecoration(
                      color: NivoColors.cloudSoft,
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(color: NivoColors.line),
                    ),
                    child: Text(
                      'PQC',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 8,
                        letterSpacing: 1.4,
                        color: NivoColors.forest,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: NivoColors.ink,
                  borderRadius: BorderRadius.circular(22),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Saldo disponible',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 8,
                        letterSpacing: 1.6,
                        color: NivoColors.paper.withValues(alpha: 0.6),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      AppPreviewContent.balanceLabel,
                      style: GoogleFonts.inter(
                        fontSize: 24,
                        fontWeight: FontWeight.w600,
                        letterSpacing: -0.8,
                        color: NivoColors.paper,
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      height: 56,
                      child: NivoSparkline(
                        points: AppPreviewContent.balanceTrend,
                        lineColor: NivoColors.forest,
                        fillColor: NivoColors.paper.withValues(alpha: 0.08),
                        strokeWidth: 2,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              Row(
                children: AppPreviewContent.quickActions.take(3).map((action) {
                  final isLast =
                      action == AppPreviewContent.quickActions.take(3).last;
                  return Expanded(
                    child: Padding(
                      padding: EdgeInsets.only(right: isLast ? 0 : 8),
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        decoration: BoxDecoration(
                          color: NivoColors.cloudSoft,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: NivoColors.line),
                        ),
                        child: Column(
                          children: [
                            Icon(action.icon, size: 16, color: NivoColors.ink),
                            const SizedBox(height: 6),
                            Text(
                              action.label,
                              style: GoogleFonts.inter(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: NivoColors.ink,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 14),
              ...AppPreviewContent.activities.take(2).map(
                    (item) => Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Row(
                        children: [
                          Container(
                            width: 32,
                            height: 32,
                            decoration: BoxDecoration(
                              color: NivoColors.cloudSoft,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(item.icon,
                                size: 15, color: NivoColors.ink),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  item.title,
                                  style: GoogleFonts.inter(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: NivoColors.ink,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  item.meta,
                                  style: GoogleFonts.inter(
                                    fontSize: 10,
                                    color: NivoColors.stoneSoft,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            item.amount,
                            style: GoogleFonts.inter(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: item.positive
                                  ? NivoColors.forest
                                  : NivoColors.ink,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TrustStrip extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 20),
      decoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: NivoColors.line),
          bottom: BorderSide(color: NivoColors.line),
        ),
      ),
      child: Column(
        children: [
          Text(
            'CONFIANZA RESPALDADA, NO PROMETIDA',
            textAlign: TextAlign.center,
            style: GoogleFonts.jetBrainsMono(
              fontSize: 10,
              letterSpacing: 2.4,
              color: NivoColors.mist,
            ),
          ),
          const SizedBox(height: 20),
          ...LandingContent.trustPoints.map(
            (e) => Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 6,
                    height: 6,
                    margin: const EdgeInsets.only(top: 7, right: 12),
                    decoration: const BoxDecoration(
                      color: NivoColors.forest,
                      shape: BoxShape.circle,
                    ),
                  ),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          e.title,
                          style: GoogleFonts.inter(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            letterSpacing: -0.3,
                            color: NivoColors.ink,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          e.subtitle,
                          style: GoogleFonts.inter(
                            fontSize: 13,
                            height: 1.45,
                            color: NivoColors.stoneSoft,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _WhyQuantumSection extends StatelessWidget {
  const _WhyQuantumSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: NivoColors.cloudSoft,
      padding: const EdgeInsets.fromLTRB(20, 36, 20, 40),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _OutlineBadge(LandingContent.whyBadge),
          const SizedBox(height: 14),
          Text(
            LandingContent.whyTitle,
            style: GoogleFonts.inter(
              fontSize: 32,
              fontWeight: FontWeight.w600,
              height: 1.08,
              letterSpacing: -1.1,
              color: NivoColors.ink,
            ),
          ),
          const SizedBox(height: 14),
          Text(
            LandingContent.whyLead,
            style: GoogleFonts.inter(
              fontSize: 17,
              height: 1.55,
              color: NivoColors.stone,
            ),
          ),
          const SizedBox(height: 24),
          ...LandingContent.whyPillars.map((p) => _PillarCard(
                kicker: p.kicker,
                title: p.title,
                body: p.body,
              )),
        ],
      ),
    );
  }
}

class _ShieldSection extends StatelessWidget {
  const _ShieldSection();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 40, 20, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _OutlineBadge(LandingContent.shieldBadge),
          const SizedBox(height: 14),
          Text(
            LandingContent.shieldTitle,
            style: GoogleFonts.inter(
              fontSize: 34,
              fontWeight: FontWeight.w600,
              height: 1.05,
              letterSpacing: -1.2,
              color: NivoColors.ink,
            ),
          ),
          const SizedBox(height: 14),
          Text(
            LandingContent.shieldLead,
            style: GoogleFonts.inter(
              fontSize: 17,
              height: 1.55,
              color: NivoColors.stone,
            ),
          ),
          const SizedBox(height: 22),
          ...LandingContent.shieldSteps.map(
            (s) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'PASO ${s.step}',
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 10,
                          letterSpacing: 2.4,
                          color: NivoColors.mist,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        s.title,
                        style: GoogleFonts.inter(
                          fontSize: 19,
                          fontWeight: FontWeight.w600,
                          letterSpacing: -0.4,
                          color: NivoColors.ink,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        s.body,
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          height: 1.5,
                          color: NivoColors.stone,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _CtaSection extends StatelessWidget {
  const _CtaSection({required this.onRegister});

  final VoidCallback onRegister;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Card(
        color: NivoColors.paper,
        child: Padding(
          padding: const EdgeInsets.all(22),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                LandingContent.ctaTitle,
                style: GoogleFonts.inter(
                  fontSize: 22,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.5,
                  color: NivoColors.ink,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                LandingContent.ctaBody,
                style: GoogleFonts.inter(
                  fontSize: 15,
                  height: 1.5,
                  color: NivoColors.stone,
                ),
              ),
              const SizedBox(height: 18),
              FilledButton(
                onPressed: onRegister,
                child: const Text('Quiero la beta'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OutlineBadge extends StatelessWidget {
  const _OutlineBadge(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: NivoColors.line),
      ),
      child: Text(
        text.toUpperCase(),
        style: GoogleFonts.jetBrainsMono(
          fontSize: 9,
          letterSpacing: 1.8,
          color: NivoColors.stone,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}

class _PillarCard extends StatelessWidget {
  const _PillarCard({
    required this.kicker,
    required this.title,
    required this.body,
  });

  final String kicker;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Card(
        color: NivoColors.paper,
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                kicker.toUpperCase(),
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 9,
                  letterSpacing: 2.2,
                  color: NivoColors.forest,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                title,
                style: GoogleFonts.inter(
                  fontSize: 19,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.4,
                  color: NivoColors.ink,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                body,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  height: 1.55,
                  color: NivoColors.stone,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
