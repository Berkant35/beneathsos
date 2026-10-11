# 0007. Own BLE plugin (Pigeon) instead of a third-party BLE package

- Status: Accepted
- Date: 2026-09-27

## Context

The product depends on details that general BLE packages hide or do not handle:

- raw manufacturer data with the company id, to recognise an app-less iPhone's Find My beacon
  (Apple `0x004C`, payload type `0x12`);
- a monotonic receive timestamp per advertisement;
- high-rate scanning without flooding the platform channel;
- Android refuses apps that start more than 5 scans in 30 s — the scanner must keep one long scan and
  delay restarts instead of failing;
- later, advertising from the victim's phone.

`flutter_blue_plus`, the most popular package, requires a commercial licence for for-profit
organisations (including during development) and only supports the central role.

## Decision

Write `ble_scanner`, a small plugin in its own repository:

- Pigeon contract (`pigeons/messages.dart`) generating type-safe Dart, Kotlin and Swift;
- Android: one long-running `BluetoothLeScanner` scan, throttle-safe restarts, coroutine-based
  delivery; iOS: CoreBluetooth with `allowDuplicates`;
- samples buffered natively and delivered in batches (default 250 ms);
- no BeneathSOS domain types, so other projects can reuse it.

## Alternatives

- **flutter_blue_plus** — licence and central-only limits.
- **flutter_reactive_ble, bluetooth_low_energy, universal_ble** — usable, but each hides or reshapes
  some of the fields above, and adding victim-mode advertising would mean a second dependency.

## Consequences

- We own native code on two platforms. Platform behaviour is ours to discover: e.g. iOS reports the
  adapter as `unknown` until CoreBluetooth is ready (caught in the simulator, handled in
  `BleService`).
- The plugin is reusable and independently versioned (`v0.1.0`).
- Apache-2.0 end to end; no commercial licence question.

## References

- Repository `Berkant35/ble_scanner`; `docs/research/field-test-01.md`.
