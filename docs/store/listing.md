# Store listing (draft for the maintainer)

## English
- **Name:** BeneathSOS
- **Subtitle (30):** Find phones under rubble
- **Promotional text:** Offline Bluetooth search aid for earthquake volunteers. Supports — never replaces —
  professional search and rescue.
- **Description:**
  BeneathSOS helps volunteers narrow down where a phone trapped under earthquake rubble may be. Draw the
  rubble, measure the phone's Bluetooth signal at a few points around it, and the app shows the most
  likely area (50 % and 90 % regions) and where to measure next. It never claims an exact spot: Bluetooth
  signal cannot tell distance from obstruction.

  • Works fully offline — no account, no server, no data collected
  • A point with no signal counts too
  • "I am trapped": a trapped person's phone sends a Bluetooth help signal rescuers' phones recognise,
    with battery and a sign of life
  • Export a search for field research; bystanders' devices are never identifiable

  BeneathSOS is an independent open-source project, not affiliated with AFAD or any agency. In an
  emergency call 112 and follow the rescue teams on site.
- **Keywords (100):** earthquake,rescue,rubble,bluetooth,search,sos,trapped,volunteer,afad,deprem
- **Category:** Utilities (secondary: Navigation)
- **Privacy:** Data Not Collected. Policy URL: https://github.com/Berkant35/beneathsos/blob/main/docs/privacy.md

## Türkçe
- **Ad:** BeneathSOS
- **Alt başlık:** Enkaz altındaki telefonu bulun
- **Tanıtım metni:** Deprem gönüllüleri için çevrimdışı Bluetooth arama yardımcısı. Profesyonel arama
  kurtarmayı destekler, onun yerini asla almaz.
- **Açıklama:**
  BeneathSOS, gönüllülerin deprem enkazı altında kalmış bir telefonun nerede olabileceğini daraltmasına
  yardım eder. Enkazı çizin, telefonun Bluetooth sinyalini çevresinde birkaç noktada ölçün; uygulama en
  olası alanı (%50 ve %90 bölgeleri) ve bir sonraki ölçüm yerini gösterir. Asla kesin bir nokta iddia
  etmez: Bluetooth sinyali uzaklığı engelden ayıramaz.

  • Tamamen çevrimdışı — hesap yok, sunucu yok, veri toplanmaz
  • Sinyal alınamayan nokta da bilgidir
  • "Enkaz altındayım": enkaz altındaki kişinin telefonu, kurtarıcıların telefonlarının tanıdığı bir
    Bluetooth yardım sinyali gönderir; pil ve yaşam belirtisiyle
  • Saha araştırması için dışa aktarma; çevredeki cihazlar asla tanınamaz

  BeneathSOS bağımsız, açık kaynaklı bir projedir; AFAD ya da herhangi bir kurumla bağlantılı değildir.
  Acil durumda 112'yi arayın ve sahadaki kurtarma ekiplerini izleyin.
- **Anahtar kelimeler:** deprem,enkaz,kurtarma,bluetooth,arama,sos,afad,gönüllü,yardım

## App Review notes
- Bluetooth is the whole product: rescuers measure Bluetooth signal strength around rubble; nothing is
  sent anywhere.
- `bluetooth-peripheral` background mode: "I am trapped" keeps advertising a help signal if a trapped
  person's screen locks or the app is backgrounded; it stops when the person leaves the screen.
- To try: Start a search → Practice with sample data walks through every screen without hardware.
- No login. Export uses the system share sheet only.
