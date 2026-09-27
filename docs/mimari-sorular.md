# BeneathSOS — Mimari Soruları (2026-09-27)

Cevaplar netleşince `CLAUDE.md` ve mimari dokümanı bu dosyadan üretilecek. Her soruda **Önerim** var; "öneri" yazmak kabul demek.

## A. Ürün kapsamı
1. v1 kapsamı: (a) yalnız kurtarıcı/tarayıcı, (b) tek uygulamada tarayıcı + kurban modu (beacon), (c) iki ayrı uygulama? **Önerim:** tek uygulama, iki mod; kurban modu v1.1.
2. Hedef kullanıcı: sivil gönüllü mü, eğitimli ekip (AFAD/AKUT/itfaiye) mi, ikisi mi? **Önerim:** v1 eğitimli ekip/gönüllü.
3. Platform önceliği: Android ve iOS eşit mi? **Önerim:** kurtarıcı tarafında Android öncelikli; iOS kapsamı testten sonra.
4. Aynı enkazda birden fazla kurtarıcının ölçümleri v1'de birleşsin mi? **Önerim:** v1 tek cihaz, veri modeli çoklu cihaza hazır.
5. İnternet varsayımı ve sunucu: tamamen çevrimdışı mı, Supabase gibi bir backend olacak mı? **Önerim:** v1 %100 çevrimdışı + dosya dışa aktarma; sunucu v2.

## B. Kod organizasyonu
6. Monorepo (pub workspaces + melos). Paketler: `rubble_core` (modeller), `ble_scanner` (plugin), `locator_engine` (olasılık haritası, saf Dart), `rubble_canvas` (çizim/ısı haritası), `app`. **Önerim:** bu 4 paket + app.
7. Paketler monorepo içinde path dependency mi olsun, ayrı repo / pub.dev mi? Açık kaynak planı var mı? **Önerim:** monorepo; motor ve protokol ileride açık kaynak.
8. BLE katmanı: hazır paket (flutter_blue_plus ticari lisans ister, bluetooth_low_energy MIT, flutter_reactive_ble) mi, kendi native plugin'imiz (Kotlin/Swift + Pigeon) mi? **Önerim:** kendi ince plugin'imiz; ham paket, scan mode ve zaman damgası kontrolü bizde olur, lisans riski kalmaz.
9. Olasılık motoru nerede çalışsın: saf Dart + isolate mi, native/FFI mi? **Önerim:** saf Dart + isolate; Python simülasyonu "altın" test verisi üretir.
10. Katmanlama: feature-first + domain/data/presentation? **Önerim:** evet; domain saf Dart ve Flutter'a bağımlı değil.

## C. State ve navigasyon
11. State management: Riverpod 3 (code-gen) mi, Bloc/Cubit mi? Qulo'dakiyle aynı mı olsun? **Önerim:** Riverpod 3; BLE akışları için StreamProvider.
12. Router: go_router + typed routes? Deep link gerekecek mi (ör. paylaşılan saha dosyasını açmak)? **Önerim:** go_router.
13. Uygulama ölçüm sırasında kapanırsa oturum kaldığı yerden devam etsin mi? **Önerim:** evet; her olay anında diske yazılan olay günlüğü (event-sourced).

## D. Veri
14. Yerel veritabanı: Drift (SQLite) mi, Isar/ObjectBox mı? **Önerim:** Drift.
15. Her ham RSSI örneği mi saklansın, yalnız nokta özeti mi? **Önerim:** ham veri; saha kalibrasyonu için çok değerli.
16. Enkaz nasıl çizilecek: metre ölçekli boş tuval mi, uydu/çevrimdışı harita mı, kenar uzunluğu girilerek mi? **Önerim:** v1 ölçekli tuval + kenar uzunluğu girişi.
17. Ölçüm noktasının konumu: haritaya elle dokunarak mı, ARCore/ARKit ile otomatik mi? **Önerim:** v1 elle, AR v2.

## E. Motor ve algoritma
18. Motor parametreleri (α, σ, n, P0) nasıl yönetilsin? **Önerim:** uygulamaya gömülü, versiyonlanmış JSON profiller ("boşluklu", "yoğun"); saha verisiyle güncellenir.
19. Kurtarıcı telefonun RSSI ofsetini kalibre eden 1 m'lik bir adım olsun mu? **Önerim:** isteğe bağlı; tek telefonla ölçümde ortak ofset zaten modelde hesaba katılıyor.
20. v1'de "bir sonraki en iyi ölçüm noktası" önerisi olsun mu (belirsizliği en çok azaltan nokta)? **Önerim:** evet; en güçlü farklılaştırıcı.
21. Aynı enkazda birden fazla hedef: hedef başına ayrı harita, ölçüm turunda tüm hedeflerin RSSI'sı birlikte kaydedilsin mi? **Önerim:** evet.

## F. Edge case kararları
22. Hedefin adresi değişti (~15 dk): otomatik yeniden kilitleme mi, kullanıcıya sorma mı? **Önerim:** otomatik öneri + kullanıcı onayı.
23. Bir noktada sinyal yok: nokta "algılanmadı" olarak kaydedilip haritaya bilgi olarak girsin. Minimum ölçüm süresi ne olsun? **Önerim:** 15 sn, ekranda sayaç.
24. Kurtarıcı ölçüm sırasında hareket ediyorsa ivmeölçerle "telefonu sabit tut" uyarısı verilsin mi? **Önerim:** evet; hareketli örnekler işaretlenir.
25. Çok güçlü (> −50 dBm) ya da hareket eden cihazlar otomatik olarak "yüzey cihazı" diye elensin mi?
26. Sunum dili: "kurban burada" demek yasak; %50/%90 bölgeleri ve güven metni gösterilsin, ilk açılışta yasal uyarı olsun. Onaylıyor musun?

## G. Süreç, kalite, dağıtım
27. Qulo kuralları (ekran ~200 satır, widget logic → mixin, AppScaffold, hardcode string yasak, l10n) buraya da taşınsın mı? Diller TR + EN mi?
28. Test ve CI: motor için altın veri testleri, BLE için sahte tarayıcı, golden testler, GitHub Actions. Bu klasörün kendi git reposu açılsın mı (şu an home repo'ya düşüyor)? Public mi private mı?
29. v1'de araştırma/saha modu olsun mu: gerçek konum girilip hata ölçülsün, ham veri CSV olarak dışa aktarılsın? **Önerim:** evet; saha kampanyası için şart.
30. Lisans ve ticari model: açık kaynak mı (Apache/GPL), kâr amacı var mı (flutter_blue_plus kararını etkiler)? "BeneathSOS" adı kesin mi?
