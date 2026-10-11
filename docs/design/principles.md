# Design principles

> **A very usable, readable interface for people at a collapsed building in an emergency.**

Every design decision is tested against this sentence.

**Who we design for.** The primary user is an untrained volunteer under stress, outdoors — in
sunlight, dust or at night — using one hand, possibly with gloves. The victim-mode user is a trapped
person in the dark, panicking, with a draining battery. The brand also speaks to AFAD, NGOs,
contributors and supporters: it must look trustworthy, not like a hobby project.

## The seven principles

1. **Show uncertainty, never hide it.** A location is a region with a confidence level, never a single
   pin. Say "signal exit point", never "the victim is here".
2. **One screen, one primary action.** At most one orange button per screen, in the thumb zone
   (bottom half). Everything else is secondary.
3. **Readable in the worst light.** High contrast, Atkinson Hyperlegible, body text ≥ 17 pt, tabular
   numbers; layouts survive 200 % system text size.
4. **Say what happened, then what to do.** Every status and error has two parts ("Bluetooth is off.
   Tap to turn it on."). Never blame the user. Red means "blocked" only.
5. **Don't rely on eyes alone.** Critical events (measurement done, target lost, identity rotating)
   also vibrate and sound. No information is carried by colour alone.
6. **Calm under pressure.** No decorative motion. Motion only explains time or state (countdown,
   scanning) and follows the system "reduce motion" setting.
7. **Respect the person and the battery.** Victim mode is the simplest screen: large text, few
   elements, no animation, dimmed screen.

## Colour roles

The app follows the phone's light/dark setting everywhere, including victim mode.

| Role | Light | Dark | Use |
|---|---|---|---|
| Primary (calm body) | `#1B2A4E` | `#9DB2E0` | Titles, secondary buttons, navigation |
| Accent (action / attention) | `#FF7900` | `#FF8C2E` | The primary button, identity-rotation warning — in light theme as a fill behind dark content only |
| On accent | `#1A0D00` | `#1A0D00` | Text and icons on accent — **white on orange is forbidden** |
| Error (blocked) | `#B3261E` | `#FFB4AB` | Bluetooth off, permission missing |
| Background / text | `#F5F6F9` / `#121A2B` | `#0C111D` / `#E8ECF5` | |
| Secondary surface (dark) | — | `#22324F` | Secondary buttons in dark theme |

Measured WCAG contrast (AA needs 4.5 for normal text, 3 for meaningful icons). These values are pinned by
`tools/brand/tests/test_contrast.py`:

| Pair | Ratio |
|---|---|
| White on `#1B2A4E` | 14.1 |
| `#121A2B` on `#F5F6F9` | 16.1 |
| `#1A0D00` on `#FF7900` | 7.3 |
| `#1A0D00` on `#FF8C2E` | 8.2 |
| `#B3261E` on white | 6.5 |
| `#9DB2E0` on `#0C111D` | 8.9 |
| `#E8ECF5` on `#0C111D` | 15.9 |
| `#E8ECF5` on `#22324F` | 10.8 |
| `#FF8C2E` on `#0C111D` (orange text and icons, dark theme) | 8.1 |
| White on `#FF7900` (forbidden) | 2.6 |
| `#FF7900` on `#F5F6F9` (forbidden for text and icons) | 2.4 |

The probability-map heat scale is separate from these roles: perceptually uniform and colour-blind
safe, chosen in roadmap phase 9.

## Typography

- Typeface: **Atkinson Hyperlegible Next** (variable weight 200–800), bundled with the app — the app
  works offline, so fonts are never downloaded.
- Roles: **title**, **body**, **label** and **numeric**. Numeric text (dBm, countdowns, metres) uses
  tabular figures and a bold weight so changing numbers do not jump.
- Body text ≥ 17 pt. The full size scale is defined as tokens in `beneathsos_ui` (roadmap phase 1.2).

## Icons

- **Material Symbols Rounded**, weight matched to Atkinson.
- Custom icons, drawn on the logo's 48-unit grid and stroke: rubble site, measurement point (heard),
  measurement point (not heard), signal exit point, probability region, Find My target.
- Icons that carry meaning always have a text label or an accessibility label.

## Related

- [Voice and tone](voice-and-tone.md)
- [Accessibility](accessibility.md)
- [Brand: logo, colours, typeface](../brand/README.md)
- [ADR 0017 — visual identity](../adr/0017-visual-identity.md)
