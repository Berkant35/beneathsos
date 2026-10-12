/// Hub checks for BeneathSOS: dependency rules between repositories (`CLAUDE.md` §2) and l10n
/// completeness of the app's ARB files.
library;

import 'package:yaml/yaml.dart';

/// Our own repositories.
const _ours = {
  'rubble_core',
  'locator_engine',
  'ble_scanner',
  'beneathsos_ui',
  'rubble_canvas',
  'beneathsos_app',
};

const _riverpod = {'riverpod', 'flutter_riverpod', 'riverpod_annotation'};

/// What a repository may depend on: an allow list (pure Dart) or a deny list (Flutter).
typedef _Rule = ({Set<String>? allowed, Set<String> forbidden});

final Map<String, _Rule> _rules = {
  'rubble_core': (allowed: {'meta', 'collection'}, forbidden: const {}),
  'locator_engine': (
    allowed: {'meta', 'collection', 'rubble_core'},
    forbidden: const {},
  ),
  'ble_scanner': (allowed: null, forbidden: _ours),
  'rubble_canvas': (
    allowed: null,
    forbidden: {
      ..._ours.difference({'rubble_core'}),
      ..._riverpod,
    },
  ),
  'beneathsos_ui': (
    allowed: null,
    forbidden: {..._ours, ..._riverpod, 'go_router'},
  ),
  'beneathsos_app': (allowed: null, forbidden: const {}),
};

/// Direct (non-dev) dependencies of [package] that break its rule, as messages.
List<String> dependencyViolations(String package, Iterable<String> deps) {
  final rule = _rules[package];
  if (rule == null) return ['$package has no dependency rule'];
  return [
    for (final dep in deps)
      if (dep != package &&
          (rule.forbidden.contains(dep) ||
              (rule.allowed != null && !rule.allowed!.contains(dep))))
        '$package must not depend on $dep',
  ];
}

/// The package name and its direct (non-dev) dependencies.
({String name, List<String> dependencies}) readPubspec(String yaml) {
  final doc = loadYaml(yaml) as YamlMap;
  final deps = doc['dependencies'] as YamlMap?;
  return (
    name: doc['name'] as String,
    dependencies: [...?deps?.keys.cast<String>()],
  );
}

/// Keys missing or empty between the English and Turkish ARB files, as messages.
List<String> l10nViolations(Map<String, Object?> en, Map<String, Object?> tr) {
  Set<String> keys(Map<String, Object?> arb) => {
    ...arb.keys.where((k) => !k.startsWith('@')),
  };
  final (enKeys, trKeys) = (keys(en), keys(tr));
  return [
    for (final k in enKeys.difference(trKeys)) 'app_tr.arb is missing "$k"',
    for (final k in trKeys.difference(enKeys)) 'app_en.arb is missing "$k"',
    for (final k in enKeys.intersection(trKeys))
      if ('${en[k]}'.trim().isEmpty) 'app_en.arb has an empty "$k"',
    for (final k in enKeys.intersection(trKeys))
      if ('${tr[k]}'.trim().isEmpty) 'app_tr.arb has an empty "$k"',
  ];
}
