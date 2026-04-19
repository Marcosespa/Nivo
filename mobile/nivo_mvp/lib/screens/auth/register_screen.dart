import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../navigation/app_navigator.dart';
import '../../navigation/nivo_transitions.dart';
import '../../theme/nivo_colors.dart';
import '../../widgets/auth_scaffold.dart';
import '../../widgets/nivo_text_field.dart';
import 'login_screen.dart';

/// Maqueta visual: sin validación ni envío de datos.
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _accept = true;
  bool _obscure = true;

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  void _continuePreview() {
    AppNavigator.goHomeAuthenticated(context);
  }

  void _goLogin() {
    Navigator.of(context).pushReplacement(
      NivoTransitions.authSwap(
        const LoginScreen(),
        registerForward: false,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AuthScaffold(
      title: 'Crear tu cuenta',
      subtitle:
          'Onboarding de presentación para mostrar cómo se vería el alta dentro del producto móvil de Nivo.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          NivoTextField(
            label: 'Nombre',
            hint: 'Nombre de ejemplo',
            controller: _name,
            textInputAction: TextInputAction.next,
          ),
          const SizedBox(height: 20),
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
            hint: 'Texto de muestra',
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
          const SizedBox(height: 22),
          InkWell(
            onTap: () => setState(() => _accept = !_accept),
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Checkbox(
                    value: _accept,
                    onChanged: (v) => setState(() => _accept = v ?? false),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Acepto términos y privacidad (solo maqueta, sin efecto legal).',
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        height: 1.45,
                        color: NivoColors.stone,
                      ),
                    ),
                  ),
                ],
              ),
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
                '¿Ya tienes cuenta? ',
                style: GoogleFonts.inter(fontSize: 14, color: NivoColors.stone),
              ),
              TextButton(
                onPressed: _goLogin,
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Text(
                  'Entrar',
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
