# Voice and tone

How BeneathSOS talks. Every string in the app (buttons, warnings, instructions, errors) follows these
rules, in English and Turkish.

## Rules

- **Short, calm, directive.** One action per sentence. No filler.
- **Numbers with units.** "12 s left", "−71 dBm", "3 m".
- **No blame, no promises.** The situation is hard enough; never imply the user did something wrong,
  never promise an outcome.
- **Errors: what happened, then what to do.** "Bluetooth is off. Tap to turn it on."
- **Never claim a location.** Use "most likely area" and "signal exit point" — never "the victim is
  here" or "victim found".
- **Turkish uses the formal "siz"** ("Telefonu sabit tutun."), the standard of emergency and public
  services, respectful to every age. **English uses the imperative** ("Hold the phone still.").
- **Translations carry the same meaning, not the same words.** Write each language naturally.

## Examples

| Do | Don't |
|---|---|
| "Telefonu sabit tutun. 12 sn kaldı." / "Hold the phone still. 12 s left." | "Harika gidiyorsun! Biraz daha sabit tutar mısın?" |
| "Bu noktada sinyal yok. Bu da bir bilgi; haritayı güncelledik." / "No signal at this point. That is information too; the map is updated." | "Ölçüm başarısız." / "Measurement failed." |
| "En olası bölge" / "Most likely area" | "Kurban burada" / "Victim found" |
| "Bluetooth kapalı. Açmak için dokunun." / "Bluetooth is off. Tap to turn it on." | "Hata: Bluetooth kullanılamıyor." / "Error: Bluetooth unavailable." |

## Glossary

Use exactly these terms in the app, the documentation and translations.

| English | Türkçe | Notes |
|---|---|---|
| probability region | olasılık bölgesi | Never "location" alone |
| most likely area | en olası bölge | The 50 % region |
| signal exit point | sinyal çıkış noktası | Where the signal leaves the rubble — not the person |
| measurement point | ölçüm noktası | |
| signal heard / no signal | sinyal var / sinyal yok | "No signal" is information, not failure |
| target | hedef | The device being searched for |
| identity rotation | kimlik değişimi | Phones change their Bluetooth identity ~ every 15 min |
| relink | yeniden bağla | Confirming the new identity of the target |
| ambient scan | ortam taraması | 30 s scan to blacklist surface devices |
| rubble site | enkaz alanı | |
| rescuer | kurtarıcı | |
| I am trapped (victim mode) | Enkaz altındayım | UI label; "victim mode" is internal only |

## Related

- [Design principles](principles.md)
- [Accessibility](accessibility.md)
- ARB files: `apps/beneathsos_app/lib/l10n/app_en.arb`, `app_tr.arb` in the
  [app repository](https://github.com/Berkant35/beneathsos_app)
