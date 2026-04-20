import 'package:flutter/material.dart';

import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/landing_screen.dart';
import '../screens/post_auth_home_screen.dart';
import 'nivo_transitions.dart';

/// Rutas disponibles para demo: landing narrativo, auth visual y shell fintech.
abstract final class AppNavigator {
  static const String landing = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String home = '/home';

  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case landing:
        return NivoTransitions.slideFade(const LandingScreen());
      case login:
        return NivoTransitions.slideFade(const LoginScreen());
      case register:
        return NivoTransitions.slideFade(const RegisterScreen());
      case home:
        return NivoTransitions.fadeThrough(const PostAuthHomeScreen());
      default:
        return NivoTransitions.slideFade(const LandingScreen());
    }
  }

  static void goLogin(BuildContext context) {
    Navigator.of(context).pushNamed(login);
  }

  static void goRegister(BuildContext context) {
    Navigator.of(context).pushNamed(register);
  }

  static void goHomeAuthenticated(BuildContext context) {
    Navigator.of(context).pushNamedAndRemoveUntil(home, (r) => false);
  }
}
