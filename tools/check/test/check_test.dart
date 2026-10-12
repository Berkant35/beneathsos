import 'package:beneathsos_check/check.dart';
import 'package:test/test.dart';

void main() {
  group('dependency rules', () {
    test('rubble_core may use only meta and collection', () {
      expect(
        dependencyViolations('rubble_core', ['meta', 'collection']),
        isEmpty,
      );
      expect(dependencyViolations('rubble_core', ['meta', 'flutter']), [
        'rubble_core must not depend on flutter',
      ]);
    });

    test('locator_engine may add rubble_core but not Flutter', () {
      expect(dependencyViolations('locator_engine', ['rubble_core']), isEmpty);
      expect(
        dependencyViolations('locator_engine', ['ble_scanner']),
        hasLength(1),
      );
    });

    test('Flutter packages are checked against their forbidden list', () {
      expect(dependencyViolations('ble_scanner', ['flutter']), isEmpty);
      expect(dependencyViolations('ble_scanner', ['flutter', 'rubble_core']), [
        'ble_scanner must not depend on rubble_core',
      ]);
      expect(
        dependencyViolations('rubble_canvas', ['flutter', 'flutter_riverpod']),
        ['rubble_canvas must not depend on flutter_riverpod'],
      );
      expect(
        dependencyViolations('beneathsos_ui', [
          'flutter',
          'go_router',
          'rubble_core',
        ]),
        [
          'beneathsos_ui must not depend on go_router',
          'beneathsos_ui must not depend on rubble_core',
        ],
      );
    });

    test('the app may depend on everything', () {
      expect(
        dependencyViolations('beneathsos_app', [
          'rubble_core',
          'ble_scanner',
          'flutter',
        ]),
        isEmpty,
      );
    });

    test('an unknown repository is a violation, so a new one gets a rule', () {
      expect(dependencyViolations('mystery', []), [
        'mystery has no dependency rule',
      ]);
    });
  });

  test('direct dependencies are read from a pubspec', () {
    const pubspec = '''
name: beneathsos_ui
dependencies:
  flutter:
    sdk: flutter
  go_router: ^17.0.0
dev_dependencies:
  rubble_core: any
''';
    final read = readPubspec(pubspec);
    expect(read.name, 'beneathsos_ui');
    expect(read.dependencies, ['flutter', 'go_router']);
  });

  group('l10n completeness', () {
    test('keys must match both ways; metadata is ignored', () {
      final en = {
        '@@locale': 'en',
        'a': 'A',
        '@a': <String, Object?>{},
        'b': 'B',
      };
      final tr = {'@@locale': 'tr', 'a': 'A', 'c': 'C'};
      expect(l10nViolations(en, tr), [
        'app_tr.arb is missing "b"',
        'app_en.arb is missing "c"',
      ]);
    });

    test('an empty translation is a violation', () {
      expect(l10nViolations({'a': 'A'}, {'a': ' '}), [
        'app_tr.arb has an empty "a"',
      ]);
    });
  });
}
