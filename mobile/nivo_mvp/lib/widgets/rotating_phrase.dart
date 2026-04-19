import 'dart:async';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/nivo_colors.dart';

class RotatingPhrase extends StatefulWidget {
  const RotatingPhrase({
    super.key,
    required this.phrases,
    this.interval = const Duration(milliseconds: 2200),
  });

  final List<String> phrases;
  final Duration interval;

  @override
  State<RotatingPhrase> createState() => _RotatingPhraseState();
}

class _RotatingPhraseState extends State<RotatingPhrase> {
  int _i = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(widget.interval, (_) {
      if (!mounted) return;
      setState(() {
        _i = (_i + 1) % widget.phrases.length;
      });
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final text = widget.phrases[_i];
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 320),
      switchInCurve: Curves.easeOutCubic,
      switchOutCurve: Curves.easeInCubic,
      transitionBuilder: (child, anim) {
        return ClipRect(
          child: SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0, 0.12),
              end: Offset.zero,
            ).animate(anim),
            child: FadeTransition(opacity: anim, child: child),
          ),
        );
      },
      child: Container(
        key: ValueKey(text),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: NivoColors.forest,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Text(
          text,
          style: GoogleFonts.inter(
            fontSize: 22,
            fontWeight: FontWeight.w500,
            letterSpacing: -0.6,
            color: Colors.white,
            height: 1.15,
          ),
        ),
      ),
    );
  }
}
