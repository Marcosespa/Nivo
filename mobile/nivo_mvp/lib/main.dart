import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'navigation/app_navigator.dart';
import 'theme/nivo_colors.dart';
import 'theme/nivo_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const NivoMvpApp());
}

class NivoMvpApp extends StatelessWidget {
  const NivoMvpApp({super.key});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: NivoThemeController.instance,
      builder: (context, _) {
        final dark = NivoThemeController.instance.isDark;

        SystemChrome.setSystemUIOverlayStyle(
          SystemUiOverlayStyle(
            statusBarBrightness: dark ? Brightness.dark : Brightness.light,
            statusBarIconBrightness: dark ? Brightness.light : Brightness.dark,
            systemNavigationBarColor: NivoColors.paper,
            systemNavigationBarIconBrightness:
                dark ? Brightness.light : Brightness.dark,
          ),
        );

        return MaterialApp(
          title: 'Nivo',
          debugShowCheckedModeBanner: false,
          theme: NivoTheme.fromController(),
          initialRoute: AppNavigator.landing,
          onGenerateRoute: AppNavigator.onGenerateRoute,
        );
      },
    );
  }
}
