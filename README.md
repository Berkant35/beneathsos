# BeneathSOS

**Open-source, offline mobile app that helps volunteers find phones trapped under earthquake rubble —
shown as a probability map, never as a false certainty.**

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![App CI](https://github.com/Berkant35/beneathsos_app/actions/workflows/ci.yml/badge.svg)](https://github.com/Berkant35/beneathsos_app/actions/workflows/ci.yml)
[![ble_scanner CI](https://github.com/Berkant35/ble_scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/Berkant35/ble_scanner/actions/workflows/ci.yml)

> BeneathSOS supports, and never replaces, professional search and rescue. It is under development
> and not ready for use in a real emergency.

## Why

In the first hours after an earthquake, a large share of the people pulled out alive are rescued by neighbours and
volunteers, long before heavy equipment and professional teams arrive. Many of the people trapped
have a phone in their pocket. Even with no network and no app installed, an iPhone that loses its
internet connection keeps broadcasting a Bluetooth "Find My" beacon every few seconds.

BeneathSOS turns any rescuer's phone into a tool to listen for those signals and to answer one
question: **where should we look first?**

## How it works

1. **Draw the rubble** — the footprint of the collapsed building, to scale.
2. **Measure** — walk around (and, where safe, over) the rubble and measure the target phone's
   Bluetooth signal strength for a few seconds at each point. A point where nothing is heard counts
   too.
3. **Read the map** — the app combines all measurements into a probability map with 50 % and 90 %
   regions and suggests the next point that would narrow it down most.

## What it is not

- It never says "the person is here". Bluetooth signal strength through rubble is far too noisy for
  that; the app shows **where it is most likely** and how uncertain that is.
- It does not estimate depth, number of floors or building material from the signal. Our research
  shows this is not possible from signal strength alone
  ([ADR 0002](docs/adr/0002-probability-map-not-a-point.md)).
- It does not use the internet, accounts or analytics. Everything stays on the phone.

## Status

| | |
|---|---|
| ✅ Research | Feasibility study, physics limits, two simulations ([report](docs/fizibilite-2026-09-27.md)) |
| ✅ Field test | An Android phone detects an app-less iPhone in airplane mode by its Find My beacon |
| ✅ Foundations | Bluetooth scanner plugin, scanning and device-tracking logic, 52 tests, CI, TestFlight builds |
| 🔄 Now | Documentation and open-source setup (roadmap phase 0) |
| ⏳ Next | Design system, rubble drawing, measurement, probability engine and map, victim mode |

Full plan: [roadmap](docs/roadmap.md). How it is built: [architecture](docs/architecture.md).
Why it is built this way: [decision records](docs/adr/README.md).

## Repositories

| Repository | What |
|---|---|
| [`beneathsos`](https://github.com/Berkant35/beneathsos) (this one) | Rules, documentation, research, decision records, tools |
| [`beneathsos_app`](https://github.com/Berkant35/beneathsos_app) | The Flutter app (Android, iOS) |
| [`ble_scanner`](https://github.com/Berkant35/ble_scanner) | Flutter plugin: raw Bluetooth LE scanning with RSSI and manufacturer data |

More packages (`rubble_core`, `locator_engine`, `rubble_canvas`) will follow the roadmap.

## Getting started (developers)

```bash
# Flutter is pinned with FVM (https://fvm.app)
git clone https://github.com/Berkant35/beneathsos.git
cd beneathsos
git clone https://github.com/Berkant35/beneathsos_app.git apps/beneathsos_app
git clone https://github.com/Berkant35/ble_scanner.git packages/ble_scanner
tools/link_local.sh                 # use the local packages instead of their git tags
cd apps/beneathsos_app && fvm install && fvm flutter pub get && fvm flutter test
```

Each repository also works on its own; it then resolves sibling packages from GitHub.

## Contributing

Contributions are welcome — code, translations, field measurements, review of the physics.
Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the project rules in [CLAUDE.md](CLAUDE.md)
(they apply to humans and AI assistants alike). Please follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Security issues: see [SECURITY.md](SECURITY.md).

## Licence

[Apache License 2.0](LICENSE) — see [ADR 0011](docs/adr/0011-apache-2-licence.md) for why.
