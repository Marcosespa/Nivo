import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'navigation/app_navigator.dart';
import 'theme/nivo_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarBrightness: Brightness.light,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Color(0xFFFFFFFF),
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );
  runApp(const NivoMvpApp());
}

class NivoMvpApp extends StatelessWidget {
  const NivoMvpApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nivo',
      debugShowCheckedModeBanner: false,
      theme: NivoTheme.light(),
      initialRoute: AppNavigator.landing,
      onGenerateRoute: AppNavigator.onGenerateRoute,
    );
  }
}
