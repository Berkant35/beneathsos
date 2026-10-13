# Privacy — BeneathSOS

*Last updated 2026-10-13. Türkçesi aşağıda.*

**BeneathSOS collects nothing.** It has no account, no server, no analytics and no advertising. It never
connects to the internet by itself.

## What stays on your phone
- **Searches** you create: the site name you type, the rubble outline you draw, the targets you choose,
  every measurement point and its readings — stored in the app's own database on your phone.
- **Raw Bluetooth readings** heard while measuring: signal strength and the temporary Bluetooth identity
  of nearby devices (these identities change every few minutes on phones). No names and no message
  contents are stored.
- Deleting the app deletes all of it.

## Bluetooth
- *Searching* listens to Bluetooth advertisements nearby to estimate where a phone may be. On Android the
  system calls this "location" access; BeneathSOS never reads GPS or your position.
- *"I am trapped"* makes your phone send a Bluetooth help signal: a fixed BeneathSOS identifier, a random
  number chosen each time you start, the battery level and how many minutes ago the phone was touched or
  moved (Android). Anyone nearby with BeneathSOS can see it. It stops when you leave the screen.

## Exports
Only when you tap **Export this search**, the app writes two files and opens your phone's share sheet;
you choose where they go. The files carry the disclaimer. The Bluetooth identities of phones that are not
your search targets are replaced by codes that cannot be traced back and differ in every export.

## Contact
Open source: <https://github.com/Berkant35/beneathsos>. Security issues: the repository's private
vulnerability reporting.

---

# Gizlilik — BeneathSOS

**BeneathSOS hiçbir veri toplamaz.** Hesap, sunucu, analiz ya da reklam yoktur. Uygulama kendiliğinden
internete bağlanmaz.

## Telefonunuzda kalanlar
- Oluşturduğunuz **aramalar**: yazdığınız alan adı, çizdiğiniz enkaz sınırı, seçtiğiniz hedefler, her
  ölçüm noktası ve ölçümleri — telefonunuzdaki uygulama veritabanında.
- Ölçüm sırasında duyulan **ham Bluetooth ölçümleri**: sinyal gücü ve yakındaki cihazların geçici
  Bluetooth kimlikleri (telefonlarda birkaç dakikada bir değişir). Ad ya da mesaj içeriği saklanmaz.
- Uygulamayı silmek hepsini siler.

## Bluetooth
- *Arama*, bir telefonun nerede olabileceğini tahmin etmek için çevredeki Bluetooth yayınlarını dinler.
  Android buna "konum" izni der; BeneathSOS GPS'i ya da konumunuzu hiç okumaz.
- *"Enkaz altındayım"*, telefonunuzun Bluetooth yardım sinyali göndermesini sağlar: sabit bir BeneathSOS
  tanımlayıcısı, her başlatışta seçilen rastgele bir sayı, pil düzeyi ve telefona kaç dakika önce
  dokunulduğu ya da kıpırdatıldığı (Android). Yakındaki BeneathSOS'lu herkes görebilir. Ekrandan
  çıkınca durur.

## Dışa aktarma
Yalnızca **Bu aramayı dışa aktar**'a dokunduğunuzda uygulama iki dosya yazar ve telefonun paylaşım
menüsünü açar; dosyaların nereye gideceğini siz seçersiniz. Dosyalar uyarı metnini içerir. Arama hedefiniz
olmayan telefonların Bluetooth kimlikleri, geri izlenemeyen ve her dışa aktarmada değişen kodlarla
değiştirilir.
