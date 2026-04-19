import 'package:flutter/material.dart';

/// Transiciones alineadas a una app financiera: suaves, sin exceso de movimiento.
abstract final class NivoTransitions {
  static const Duration _in = Duration(milliseconds: 420);
  static const Duration _out = Duration(milliseconds: 320);

  /// Pantallas completas (login, registro, post-login).
  static Route<T> slideFade<T extends Object?>(Widget page) {
    return PageRouteBuilder<T>(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: _in,
      reverseTransitionDuration: _out,
      opaque: true,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        final curved = CurvedAnimation(
          parent: animation,
          curve: Curves.easeOutCubic,
          reverseCurve: Curves.easeInCubic,
        );
        return FadeTransition(
          opacity: curved,
          child: SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0.04, 0),
              end: Offset.zero,
            ).animate(curved),
            child: child,
          ),
        );
      },
    );
  }

  /// Entre login ↔ registro (cambio lateral más marcado).
  static Route<T> authSwap<T extends Object?>(
    Widget page, {
    required bool registerForward,
  }) {
    return PageRouteBuilder<T>(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: _in,
      reverseTransitionDuration: _out,
      opaque: true,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        final curved = CurvedAnimation(
          parent: animation,
          curve: Curves.easeOutCubic,
          reverseCurve: Curves.easeInCubic,
        );
        final dx = registerForward ? 0.08 : -0.08;
        return FadeTransition(
          opacity: Tween<double>(begin: 0, end: 1).animate(curved),
          child: SlideTransition(
            position: Tween<Offset>(
              begin: Offset(dx, 0),
              end: Offset.zero,
            ).animate(curved),
            child: child,
          ),
        );
      },
    );
  }

  /// Reemplazo suave al entrar al “home” autenticado.
  static Route<T> fadeThrough<T extends Object?>(Widget page) {
    return PageRouteBuilder<T>(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: _in,
      reverseTransitionDuration: _out,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        final curved = CurvedAnimation(
          parent: animation,
          curve: Curves.easeInOutCubic,
        );
        return FadeTransition(opacity: curved, child: child);
      },
    );
  }
}
