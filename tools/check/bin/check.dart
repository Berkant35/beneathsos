import 'dart:convert';
import 'dart:io';

import 'package:beneathsos_check/check.dart';

/// Runs every hub check against the repositories under [args.first] (the hub folder).
void main(List<String> args) {
  final hub = Directory(args.isEmpty ? '.' : args.first);
  final problems = <String>[];
  for (final parent in ['packages', 'apps']) {
    final dir = Directory('${hub.path}/$parent');
    if (!dir.existsSync()) continue;
    for (final repo in dir.listSync().whereType<Directory>()) {
      final pubspec = File('${repo.path}/pubspec.yaml');
      if (!pubspec.existsSync()) continue;
      final (:name, :dependencies) = readPubspec(pubspec.readAsStringSync());
      problems.addAll(dependencyViolations(name, dependencies));
    }
  }
  final l10n = '${hub.path}/apps/beneathsos_app/lib/l10n';
  if (File('$l10n/app_en.arb').existsSync()) {
    Map<String, Object?> arb(String locale) =>
        jsonDecode(File('$l10n/app_$locale.arb').readAsStringSync())
            as Map<String, Object?>;
    problems.addAll(l10nViolations(arb('en'), arb('tr')));
  }
  problems.forEach(stderr.writeln);
  stdout.writeln(
    problems.isEmpty
        ? 'check: all rules hold'
        : 'check: ${problems.length} problem(s)',
  );
  exitCode = problems.isEmpty ? 0 : 1;
}
