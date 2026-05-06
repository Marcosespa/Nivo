import 'package:flutter_test/flutter_test.dart';
import 'package:nivo_mvp/main.dart';

void main() {
  testWidgets('App arranca', (tester) async {
    await tester.pumpWidget(const NivoMvpApp());
    await tester.pumpAndSettle(const Duration(seconds: 2));
    expect(find.text('Nivo'), findsWidgets);
  });
}
