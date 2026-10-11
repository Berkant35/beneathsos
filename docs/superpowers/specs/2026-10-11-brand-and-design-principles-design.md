# Brand and design principles — design (roadmap phase 1.1)

- Status: Approved in conversation 2026-10-11, pending written-spec review
- Scope: roadmap phase 1.1. Tokens, fonts and components are phase 1.2 (`beneathsos_ui`).

## 1. Purpose

> **A very usable, readable interface for people at a collapsed building in an emergency.**

Every design decision is tested against this sentence. Primary user: an untrained volunteer under
stress, outdoors (sun, dust, night), one hand, possibly gloves. Victim-mode user: a trapped person in
the dark, panicking, with a draining battery. Secondary audience of the brand: AFAD, NGOs,
contributors and supporters — it must look trustworthy, not like a hobby project.

## 2. Decisions

| Topic | Decision |
|---|---|
| Feeling | Calm body + high-visibility accent for actions and attention |
| Theme | Follow the phone's light/dark setting everywhere, including victim mode |
| Typeface | Atkinson Hyperlegible Next (variable 200–800, 115 KB, SIL OFL 1.1); tabular figures (`tnum`) for changing numbers |
| Icons | Material Symbols Rounded (Apache-2.0) + 5–6 custom domain icons drawn on the same grid and weight |
| Palette | Ink navy + safety orange + separate error red (§4) |
| Logo | "Signal exit": straight rubble line, phone dot below, three arcs rising and fading (§6) |
| Voice | Short, calm, directive; formal "siz" in Turkish; imperative in English (§7) |
| Accessibility | WCAG 2.2 AA + field ergonomics (§8) |
| Source of truth | Code first: tokens in `beneathsos_ui` (1.2), visual reference in Widgetbook (1.3), brand SVGs in `docs/brand/` |

Verified on 2026-10-11 for the typeface: all Turkish letters present (ı İ ş Ş ğ Ğ ç Ç ö Ö ü Ü),
`tnum` feature present, licence allows embedding and commercial use (ship `OFL.txt`, list it in the
app's licence page).

## 3. Design principles (`docs/design/principles.md`)

1. **Show uncertainty, never hide it.** A location is a region with a confidence level, never a single
   pin. Say "signal exit point", never "the victim is here".
2. **One screen, one primary action.** At most one orange button per screen, in the thumb zone
   (bottom half). Everything else is secondary.
3. **Readable in the worst light.** High contrast, Atkinson, body text ≥ 17 pt, tabular numbers;
   layouts survive 200 % system text size.
4. **Say what happened, then what to do.** Every status and error has two parts ("Bluetooth is off.
   Tap to turn it on."). Never blame the user. Red means "blocked" only.
5. **Don't rely on eyes alone.** Critical events (measurement done, target lost, identity rotating)
   also vibrate and sound. No information is carried by colour alone.
6. **Calm under pressure.** No decorative motion. Motion only explains time or state (countdown,
   scanning) and follows the system "reduce motion" setting.
7. **Respect the person and the battery.** Victim mode is the simplest screen: large text, few
   elements, no animation, dimmed screen.

## 4. Colour roles

| Role | Light | Dark | Use |
|---|---|---|---|
| Primary (calm body) | `#1B2A4E` | `#9DB2E0` | Titles, secondary buttons, navigation |
| Accent (action / attention) | `#FF7900` | `#FF8C2E` | The primary button, identity-rotation warning |
| On accent | `#1A0D00` | `#1A0D00` | Text and icons on accent — **white on orange is forbidden** |
| Error (blocked) | `#B3261E` | `#FFB4AB` | Bluetooth off, permission missing |
| Background / text | `#F5F6F9` / `#121A2B` | `#0C111D` / `#E8ECF5` | |
| Secondary surface (dark) | — | `#22324F` | Secondary buttons in dark theme |

Measured WCAG contrast (AA needs 4.5 for normal text):

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
| White on `#FF7900` (forbidden) | 2.6 |

The probability-map heat scale is separate from these roles: perceptually uniform and
colour-blind safe, chosen in roadmap phase 9.

**Not an official app.** Navy and orange are also AFAD's colours. Mitigations: ink navy and ANSI
safety orange tones distinct from AFAD's; own logo and typography; the statement
"BeneathSOS is an independent open-source project and is not affiliated with AFAD or any government
agency" (TR: "BeneathSOS bağımsız bir açık kaynak projedir; AFAD veya herhangi bir kamu kurumuyla
bağlantısı yoktur.") in onboarding (phase 4), the About screen and store listings. The Red Cross /
Red Crescent emblems are protected by law and are never used.

## 5. Typography and icons

- Roles: title, body, label, **numeric** (tabular, bold — dBm, countdowns, metres). The size scale is
  defined as tokens in phase 1.2; body ≥ 17 pt.
- Icons: Material Symbols Rounded with weight matched to Atkinson. Custom icons planned: rubble site,
  measurement point (heard), measurement point (not heard), signal exit point, probability region,
  Find My target. Same 48-unit grid and stroke as the logo.

## 6. Logo and app icon (`docs/brand/`)

Geometry on a 48 × 48 grid, round caps, one stroke width (3.6):

- Rubble line: `M6 30 H42`, primary colour.
- Phone dot: circle at (24, 38), r 3.4, accent.
- Arcs, accent, opacity 1 / 0.75 / 0.5 from inner to outer: radii 7.5, 14.5, 21.5, centred above the
  dot, opening upwards.

Assets: symbol, wordmark ("Beneath" primary + "SOS" accent, Atkinson Hyperlegible Next ExtraBold),
horizontal lock-up, versions for light and dark backgrounds, one-colour version, app-icon master
(1024 px). Minimum size 16 px; clear space ¼ of the symbol height. Misuse examples in
`docs/brand/README.md`.

App icon: navy background with orange signal (dark system appearance: `#0C111D` background,
`#9DB2E0` line, `#FF8C2E` signal); iOS dark and tinted variants; Android adaptive icon (foreground +
background layers) and Android 13 monochrome themed icon.

Launch screen: background `#F5F6F9` (light) / `#0C111D` (dark), centred symbol, **no text**; Android 12
splash rules respected.

Tooling: PNGs are generated from the SVG masters by a script (no hand-copied files);
`flutter_launcher_icons` and `flutter_native_splash` as dev dependencies only.

## 7. Voice and tone (`docs/design/voice-and-tone.md`)

- Short, calm, directive. One action per sentence. Numbers with units. No blame, no promises.
- Turkish: formal "siz" ("Telefonu sabit tutun."). English: imperative ("Hold the phone still.").
- Errors: what happened, then what to do.
- Never claim a location ("most likely area", "signal exit point").
- Translations carry the same meaning, not word-for-word.

Examples:

| Do | Don't |
|---|---|
| "Telefonu sabit tutun. 12 sn kaldı." / "Hold the phone still. 12 s left." | "Harika gidiyorsun! Biraz daha sabit tutar mısın?" |
| "Bu noktada sinyal yok. Bu da bir bilgi; haritayı güncelledik." | "Ölçüm başarısız." |
| "En olası bölge" / "Most likely area" | "Kurban burada" / "Victim found" |

The glossary in `voice-and-tone.md` fixes the TR/EN terms: probability region, most likely area,
signal exit point, measurement point, target, identity rotation, relink, ambient scan, victim mode,
rescuer.

## 8. Accessibility (`docs/design/accessibility.md`)

Target: WCAG 2.2 AA plus field ergonomics:

- Touch targets ≥ 56 px; the primary action is 64 px tall and sits in the bottom half.
- Body text ≥ 17 pt; layouts tested at 200 % system text size.
- Critical events also signalled by vibration and sound.
- "Reduce motion": animations shortened; information-carrying animations (countdown) become a
  simple indicator.
- Colour never carries information alone (icon or text too).

The document ends with a **PR checklist** used for every UI change.

## 9. Deliverables

Hub (`beneathsos`):
- `docs/design/principles.md`, `docs/design/voice-and-tone.md`, `docs/design/accessibility.md`
- `docs/brand/` (SVG masters + README) and the PNG generation script
- `docs/adr/0017-visual-identity.md`

App (`beneathsos_app`):
- App icon (iOS incl. dark/tinted, Android adaptive + monochrome), launch screen (light/dark)
- Dev dependencies `flutter_launcher_icons`, `flutter_native_splash`

## 10. Verification

- Contrast ratios in §4 recomputed by script from the final hex values.
- Logo renders correctly at 16, 24, 32, 48 px and in one colour.
- Simulator screenshots of the home-screen icon and launch screen in light and dark mode; Android
  build passes.
- App analyze and tests pass; a new TestFlight build shows the new icon.

## 11. Out of scope

Font embedding, colour/spacing/type tokens, components (phase 1.2); Widgetbook (1.3); flow mockups
(1.4); in-app "not affiliated" statement (phase 4); probability heat scale (phase 9).
