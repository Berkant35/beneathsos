# Accessibility

BeneathSOS targets **WCAG 2.2 AA plus field ergonomics**: the people using it are under stress,
outdoors, often with one hand or gloves, and some are older or have low vision.

## Targets

- **Touch targets ≥ 56 px**; the primary action is **64 px** tall and sits in the bottom half of the
  screen (thumb zone).
- **Body text ≥ 17 pt**; every layout is checked at **200 %** system text size.
- **Critical events also vibrate and sound** — measurement done, target lost, identity rotating. The
  user may not be looking at the screen.
- **Reduce motion:** when the system setting is on, animations are shortened, and animations that
  carry information (a countdown) become a simple indicator.
- **Colour never carries information alone** — always an icon or text as well.
- Contrast: text ≥ 4.5 (large text ≥ 3); icons and graphics that carry meaning ≥ 3 (WCAG 1.4.11).
  The palette's measured ratios are in [principles.md](principles.md#colour-roles).
- **In light theme, orange is a fill only** — behind dark text or icons. Never orange text or orange
  icons on the light background (2.4). In dark theme, orange text and icons are fine (8.1).

## Pull request checklist (UI changes)

- [ ] Text contrast ≥ 4.5 (large text ≥ 3); no white text on orange
- [ ] Icons and graphics that carry meaning ≥ 3; no orange text or icons on the light background
- [ ] Touch targets ≥ 56 px; the primary action is ≥ 64 px tall and in the bottom half
- [ ] Body text ≥ 17 pt; checked at 200 % system text size with no clipped or overlapping text
- [ ] No information by colour alone (icon or text too)
- [ ] Critical events also vibrate and sound
- [ ] Works with "reduce motion"; no decorative animation
- [ ] Every string from ARB in English and Turkish, using the [glossary](voice-and-tone.md#glossary) terms
- [ ] Screen readers: meaningful labels on icons and controls
- [ ] Checked in light and dark mode

## Related

- [Design principles](principles.md)
- [Voice and tone](voice-and-tone.md)
- [ADR 0017 — visual identity](../adr/0017-visual-identity.md)
