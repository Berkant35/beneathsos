# BeneathSOS — Fizibilite Değerlendirmesi (2026-09-27)

**Soru:** Enkaz etrafına 4 telefon koyup (GPS lat/long ile dörtgen), enkaz altındaki cihazın BLE RSSI değerleriyle yatay konumunu, derinliğini, katman sayısını ve malzemesini çıkarabilir miyiz?

**Yöntem:** 6 boyutta paralel web araştırması (RF fiziği, konum kestirimi, iOS/Android, alternatif teknolojiler, önceki çalışmalar, operasyon/hukuk) + Monte Carlo simülasyonu (60 senaryo × 500 deneme, `research/sim/rssi_sim.py`) + 43 karar belirleyici iddianın bağımsız kaynaklarla çürütülmeye çalışıldığı doğrulama turu (20 teyit, 23 kısmen doğru/düzeltildi, 0 tamamen çürütüldü) + eksik konular turu.
Tüm bulgular ve kaynaklar: `research/ek-bulgular-2026-09-27.md`, ham veri: `research/fizibilite-ham-2026-09-27.json`.

## Hüküm

| Hedef | Durum | Neden |
|---|---|---|
| Enkaz altında sinyal veren cihaz **var mı?** | ✅ Mümkün (sığ/boşluklu enkazda) | BLE link bütçesi ~45–55 dB; tek döşeme 13–40 dB |
| 4 GPS köşesi + RSSI ile **yatay konum** | ❌ Çalışmıyor | Simülasyonda "karenin ortası" tahmininden iyi değil; GPS hatası 5–13 m |
| RSSI ile **derinlik** | ❌ Tanımlanamaz | Bilinmeyen malzeme kaybı = mesafe; kare köşeleri eş-çembersel → Fisher matrisi tekil |
| **Katman sayısı / malzeme** | ❌ Bilimsel olarak savunulamaz | Bayes-optimal doğruluk %47,1 = çoğunluk tahmini (%47,1) |
| Tek telefonla **yürüyerek tarama** (AR konumlu) | ✅ Sığ kurbanda umut verici | d=1 m: medyan 0,8–1,0 m, p90 ~2 m; d=3 m: 2–4 m, denemelerin ~yarısında sinyal yetersiz |
| **Uygulamasız** tespit (OS beacon'ları) | ⚠️ Büyük fırsat, ciddi uyarılar | İnternetsiz iPhone 2 sn'de bir Find My yayını yapar; iOS kurtarıcı bunu göremez |

## Ana engeller

1. **Duyabilmek:** NIST yıkım deneylerinde enkaz 60–80+ dB ek kayıp (1,8 GHz altında ölçüldü; 2,4 GHz için gerçek enkaz ölçümü literatürde YOK). Simülasyon: d=3 m'de 4 linkin hepsi %2–13, d=6 m'de %0.
2. **Tanımlanamazlık:** RSSI mesafe + malzeme + vücut (0–20 dB) + cihaz ofseti (±10–15 dB) + kanal farkı (15 dB) toplamı. Gürültü σ 6–14 dB; derinlik bilgisi taşıyan sinyal ~3 dB.
3. **Debris radiator:** Sinyal boru/kablo/boşluktan sızar; RSSI tepesi kurbanın üstünde olmayabilir → "sinyal çıkış noktası + olasılık bölgesi" gösterilmeli, "kurban burada" değil.
4. **iOS kurban tarafı:** Arka planda manufacturer data yok, UUID overflow alanında; force-quit sonrası yeniden başlamaz.
5. **iOS kurtarıcı tarafı:** Apple 0x004C verisi CoreBluetooth'tan gizli → OS beacon taraması için Android ya da harici alıcı şart.
6. **Benimsenme:** HAYAT 112 4 ayda ~933 bin indirme (~%1). Uygulama gerektiren katman ancak kurumsal dağıtımla ölçeklenir.
7. **Yanlış pozitif:** Şebeke çöktüğünde yüzeydeki herkesin iPhone'u da Find My yayını yapar; ölmüş kişinin telefonu da yayın yapar.
8. **Kurumsal alan:** AFAD tek yetkili (TAMP); HAYAT 112 ("Enkaz Altındayım", ultrasonik alarm, Mors) ve TÜBİTAK BİLGEM ATEAS (Akıllı Telefon Enkaz Arama Sistemi) mevcut.
9. **Hukuk/mağaza:** Hücresel (sahte baz istasyonu) BTK izni olmadan yasa dışı; Apple 1.4.1 doğrulanamayan ölçüm iddialarını reddeder.
10. **Flutter:** flutter_blue_plus yalnız central + kâr amaçlı kuruluşa ticari lisans; `bluetooth_low_energy` (MIT) alternatif, arka plan için native kod gerekir.

## Önerilen yeniden çerçeve

1. **Pasif katman (uygulamasız):** Android kurtarıcı Find My / Nearby / Find Hub yayınlarını tarar → "bu enkazda N sabit, gömülü görünen cihaz" → bina triyajı (INSARAG ASR-2 desteği).
2. **Aktif katman (kurban uygulaması):** canlılık kalp atışı (son dokunuş/hareket), pil, kat, kişi sayısı; iki yönlü kısa mesaj; kurtarıcı tetikleyince hoparlörden SOS bip.
3. **Kurtarıcı:** tek telefonla yürüyerek tarama + ARKit/ARCore konum + Bayes ısı haritası + belirsizlik bölgesi; çoklu kurtarıcı birleştirme.
4. **Son metreler:** akustik (bip + sessizlik penceresinde dinleme, Delsar mantığı).
5. **Çıkarılacaklar:** metre cinsinden derinlik, katman, malzeme. En fazla "sığ/derin" sınıfı.

## İlk go/no-go kapısı

2,4 GHz gerçek enkaz zayıflaması bilinmiyor → **saha ölçüm kampanyası**: AFAD/AKUT/itfaiye eğitim enkazı, bilinen derinlikte telefonlar (iPhone uçak modu = Find My yayını, Android beacon), BLE 1M/Coded PHY. Hem go/no-go hem literatürde boş olan açık veri seti.

## Güncelleme — Kullanıcının kurgusu: elle işaretlenmiş noktalar + çember kesişimi, olasılık odaklı

Simülasyon: `research/sim/circle_prob_sim.py`, çıktı `research/sim/circle_prob_output.txt`. Senaryo: 12×10 m taban, 4-5 katlı pankek sonrası 3-5 m enkaz, tek telefon, noktalar haritada ±0,5 m hatayla işaretleniyor, σ=6 dB, eşik −100 dBm, 250 deneme.

| Senaryo | ≥3 noktada sinyal | Serbest uzay çemberi | Olasılık haritası hatası (medyan) | %90 bölge / bina | En olası %25'lik alanda kurban |
|---|---|---|---|---|---|
| Boşluklu, 4 köşe | %6 | 8,2 m | 2,4 m | %29 | %80 |
| Boşluklu, 8 çevre noktası | %54 | 9,6 m | 1,4 m | %14 | %98 |
| Boşluklu, 12 çevre noktası | %81 | 9,9 m | 1,4 m | %10 | %99 |
| Boşluklu, 4 köşe + 5 enkaz üstü noktası | %79 | 9,0 m | 1,2 m | %11 | %98 |
| Yoğun, 4 köşe | %0 | — | 3,0 m | %67 | %57 |
| Yoğun, 12 çevre noktası | %26 | 11,0 m | 1,5 m | %18 | %88 |

Karşılaştırma için: hep bina merkezini söylemek medyan ~3,95 m hata verir; şans %25.

Sonuç: Serbest uzay formülüyle RSSI'dan hesaplanan çember yarıçapları sistematik olarak çok büyük çıkıyor (8-11 m hata). Olasılık haritası ise (malzeme kaybı, n ve ofset bilinmiyor; sinyal alınamayan noktalar da "burada değil" bilgisi taşıyor) boşluklu enkazda anlamlı bir önceliklendirme sağlıyor.

Uyarı: Olasılık modeli simülatörle aynı model ailesini kullanıyor ve malzeme kaybının α aralığı veriliyor. Bu yüzden sonuçlar iyimser; gerçek α ve σ ancak saha ölçümüyle öğrenilir. Önceki "merkezden iyi değil" sonucu önsel bilgi kullanmayan ML kestiricisine aitti; olasılık çerçevesi bu sonucu değiştiriyor.
