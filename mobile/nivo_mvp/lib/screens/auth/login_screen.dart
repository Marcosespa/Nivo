import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../navigation/app_navigator.dart';
import '../../navigation/nivo_transitions.dart';
import '../../theme/nivo_colors.dart';
import '../../widgets/auth_scaffold.dart';
import '../../widgets/nivo_text_field.dart';
import 'register_screen.dart';

/// Maqueta visual: sin validación, sin red, sin almacenamiento.
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _obscure = true;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  void _continuePreview() {
    AppNavigator.goHomeAuthenticated(context);
  }

  void _goRegister() {
    Navigator.of(context).pushReplacement(
      NivoTransitions.authSwap(
        const RegisterScreen(),
        registerForward: true,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AuthScaffold(
      title: 'Entrar a Nivo',
      subtitle:
          'Vista previa del acceso móvil con la misma línea visual de la landing. Puedes escribir para probar el layout; no hay autenticación real.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          NivoTextField(
            label: 'Correo',
            hint: 'ejemplo@correo.com',
            controller: _email,
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.next,
            autocorrect: false,
          ),
          const SizedBox(height: 20),
          NivoTextField(
            label: 'Contraseña',
            hint: '••••••••',
            controller: _password,
            obscure: _obscure,
            textInputAction: TextInputAction.done,
            autocorrect: false,
            onSubmitted: (_) => _continuePreview(),
            suffix: IconButton(
              onPressed: () => setState(() => _obscure = !_obscure),
              icon: Icon(
                _obscure
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
                color: NivoColors.stoneSoft,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Recuperación de cuenta y validación real quedan para la siguiente fase del MVP.',
            style: GoogleFonts.inter(
              fontSize: 12,
              height: 1.4,
              color: NivoColors.mist,
            ),
          ),
          const SizedBox(height: 20),
          FilledButton(
            onPressed: _continuePreview,
            child: const Text('Continuar a la app'),
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                '¿No tienes cuenta? ',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: NivoColors.stone,
                ),
              ),
              TextButton(
                onPressed: _goRegister,
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Text(
                  'Registrarse',
                  style: GoogleFonts.inter(
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                    color: NivoColors.forest,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
