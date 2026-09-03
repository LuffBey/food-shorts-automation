# Google Flow Agent — Editorial 3-Shot Food Shorts Prompt

Google Flow Agent ile global YouTube Shorts, Instagram Reels ve TikTok kullanımı için 3 x 10 saniyelik, toplam yaklaşık 30 saniye süren fotogerçekçi bir premium food-ASMR videosu üret.

Bu çalışma kesintisiz tek çekim taklidi yapmayacak. Üç klip, profesyonel bir yemek reklamındaki gibi bilinçli ve işlevsel üç ayrı plan olacak. Klipler arasında piksel düzeyinde hareket devamlılığı bekleme; bunun yerine aynı kanal kimliğini, aynı Creator'ı, aynı seti, aynı renk paletini ve aynı yiyecek türünü koru. Geçişleri yiyecek dokusunun kadrajı doldurduğu motive edilmiş match-cut noktalarında yap.

Flow'un desteklenen normal Agent, Ingredients/References ve Frames özelliklerini kullan. Güvenlik, kota veya otomasyon kontrollerini aşmaya çalışma.

## 1. İçerik değişkenleri

Her yeni video için aşağıdaki alanları doldur:

- `FOOD`: gösterilecek ana yiyecek
- `SAUCE`: yiyecekle renk ve tat bakımından uyumlu sos
- `HERO_TEXTURE`: izleyiciyi iştahlandıracak ana doku; örneğin çıtır kaplama, sulu iç kısım, peynir uzaması veya parlak glaze
- `PRIMARY_ACTION`: dip, kesme, kırma, çekme, dökme veya kaşıklama
- `TEXTURE_SOUND`: crunch, crackle, sizzle, snap veya benzeri doğal yiyecek sesi
- `PAYOFF`: videonun en güçlü duyusal ödülü

Bu test için:

- `FOOD = extra-crispy golden fried chicken tender`
- `SAUCE = thick glossy dark amber-red barbecue sauce`
- `HERO_TEXTURE = crisp golden crust and juicy fibrous white interior`
- `PRIMARY_ACTION = slow dip and lift`
- `TEXTURE_SOUND = one clean realistic crunch`
- `PAYOFF = bitten cross-section shown close to camera`

## 2. Değişmez kanal kimliği

Önce tek bir onaylı `@BrandSet_Master` görseli oluştur ve üç klipte de yeniden kullan.

`@BrandSet_Master` şu özelliklere sahip olmalı:

- Aynı lisanslı `@Creator`.
- Desensiz, logosuz, mat siyah bisiklet yaka tişört.
- Düz, kesintisiz, mat yanık-turuncu stüdyo fonu.
- Ana fon tonu yaklaşık `#D9682E`.
- Creator'ın arkasında çok hafif `#E98745` merkez aydınlığı.
- Mutfak, dolap, raf, pencere, lamba, bitki, tablo, logo veya dekor yok.
- Orta-koyu ceviz tonunda, uzun doğal damarlı ahşap masa; kareli kasap bloğu deseni yok.
- Tek bir küçük, sığ, parlak beyaz seramik sos kasesi.
- Kamera-solundan yumuşak ana ışık; doğal ten ve yiyecek renkleri.
- Siyah tişört, beyaz kase ve koyu sos sayesinde turuncu fonla net kontrast.

Renk kodlarını yalnız master seti oluştururken kullan. Video kliplerinde seti yeniden tarif ederek yeniden tasarlama; her klipte aynı onaylı `@BrandSet_Master` referansını kullan.

Her klipte ayrıca:

- gerçek `@Creator` entity/chip,
- onaylı `@BrandSet_Master`,
- yiyeceğin onaylı `@FoodProp_Master`

referanslarını yeniden ekle ve Flow arayüzünde gerçekten bağlandıklarını doğrula. Düz metin olarak `@Creator` yazılmış olması yeterli değildir.

## 3. Global ve dile bağımsız format

Creator hiçbir klipte konuşmayacak.

- Sözcük, selamlama, yorum, fısıltı, mırıldanma, ünlem veya anlaşılabilir insan sesi yok.
- `Mmm`, kahkaha, inilti, sesli memnuniyet tepkisi veya abartılı yutkunma yok.
- Voice-over, anlatıcı, off-camera speech ve arka plan konuşması yok.
- Konuşma taklidi yapan dudak hareketi ve lip-sync yok.
- Ağız hareketleri yalnız tek ısırık ve kısa, doğal, ağız kapalı çiğneme için kullanılabilir.
- Ekran yazısı, altyazı, konuşma balonu, renk kodu, logo veya watermark üretme.
- Creator'ın reaksiyonu yalnız gözler, hafif kapalı-ağız gülümsemesi, küçük baş hareketi ve kontrollü el jestiyle verilmeli.

Herhangi bir dilde konuşma, konuşma benzeri dudak hareketi veya ekranda yazı oluşursa klibi reddet.

## 4. Yaratıcı yönetmenlik ilkeleri

- İlk karede yiyecek zaten görünür ve hareket hâlinde olmalı; selamlama veya boş bekleme yok.
- Creator videonun kişilik taşıyıcısıdır, fakat yiyecek görsel ilginin merkezidir.
- Doku gerçekçi görünmeli: küçük düzensizlikler, belirgin çıtır yüzey, kontrollü parlaklık ve doğal iç lifler.
- Sos kalın, parlak ve ağır akmalı; su gibi sıçramamalı.
- Tek seferde bir ana hareket göster. Aynı klibe çok fazla eylem sıkıştırma.
- Reaksiyon doğal ve güvenilir olmalı; göz büyütme, yapay şaşkınlık veya grotesk çiğneme yok.
- Kamera hareketleri minimal ve amaçlı olmalı. Rastgele zoom, açı sıçraması veya sinematik cutaway yok.
- Yiyecek elde erimemeli, büyümemeli, çoğalmamalı veya başka ürüne dönüşmemeli.
- Eller anatomik olarak doğru görünmeli; parmak sayısı ve tutuş klip içinde değişmemeli.
- Buhar, kırıntı ve sos damlası yalnız fiziksel olarak makul miktarda kullanılmalı.

## 5. Üç planlı kurgu

### Clip 1 — Crave Hook / Dip and Gloss

Amaç: İlk saniyede izleyiciyi durdurmak ve sos beklentisi yaratmak.

Plan:

- Sabit ön-üç-çeyrek orta yakın plan.
- İlk karede Creator görünür; bütün ve ısırılmamış `FOOD` kameraya yakın ön plandadır.
- Creator konuşmadan yiyeceği kısa süre gösterir.
- Yiyeceği aynı eliyle tek, yavaş ve kontrollü hareketle `SAUCE` içine batırır.
- Yiyecek kaldırılırken kalın sos yüzeyde tutunur ve tek kısa damla oluşturur.
- Creator'ın yüzü, siyah tişört, beyaz kase, ceviz masa ve turuncu fon görünmeye devam eder.

Geçiş çıkışı:

- Son 0.7–1.0 saniyede soslu çıtır yüzey kontrollü biçimde lense yaklaşır.
- Son karede yiyecek dokusu kadrajın en az yüzde 80'ini doldurur.
- Kare sıcak altın-kahverengi/koyu amber doku ile dolar; yüz ve set büyük ölçüde örtülür.
- Bu bir hata gizleme hareketi değil, bilinçli ürün match-cut'ı gibi görünmelidir.

Ses:

- Hafif çıtır yüzey sesi,
- yoğun sos dip sesi,
- çok düşük ve sabit oda ambiyansı,
- insan sesi yok.

### Clip 2 — Crunch Payoff / Single Bite

Amaç: Videonun temel duyusal ödülünü vermek.

Plan:

- İlk karede aynı tür soslu çıtır yüzey kadrajın en az yüzde 80'ini doldurur.
- Yiyecek lensten geriye çekildiğinde aynı Creator ve aynı marka seti görünür.
- Bu klip kontrollü biçimde Clip 1'den daha yakın kadrajlanabilir; bu fark bilinçli reklam kurgusu olarak görünmelidir.
- Creator yiyeceğin üst ucundan yalnız bir orta boy ısırık alır.
- Tek, net ve gerçekçi `TEXTURE_SOUND` duyulur.
- İçteki sulu beyaz lifler kısa süre görünür.
- Creator iki–üç kısa, doğal ve ağız kapalı çiğneme hareketi yapar.

Geçiş çıkışı:

- Son 0.7–1.0 saniyede Creator tek-ısırıklı kesiti kameraya yaklaştırır.
- Son karede iç doku ve çıtır kenarlar kadrajın en az yüzde 80'ini doldurur.
- Creator'ın ağzı kapalıdır; konuşma veya ikinci ısırık yoktur.

Ses:

- Tek güçlü crunch,
- çok hafif kaplama crackle,
- Clip 1 ile aynı düşük oda ambiyansı,
- insan sesi yok.

### Clip 3 — Texture Reveal / Silent Signature

Amaç: İç dokuyu göstererek tatmin sağlamak ve kanalın tanınabilir kapanışını yapmak.

Plan:

- İlk karede tek-ısırıklı kesitin sulu iç dokusu kadrajın en az yüzde 80'ini doldurur.
- Yiyecek yavaşça geriye çekildiğinde aynı Creator ve aynı turuncu marka seti görünür.
- Creator ikinci bir ısırık almaz.
- Yiyeceği hafifçe çevirerek `HERO_TEXTURE` detayını gösterir.
- Creator kapalı ağızla küçük, doğal bir memnuniyet gülümsemesi ve tek, kısa başparmak işareti verir.
- Final karede Creator, tek-ısırıklı yiyecek, beyaz kase, ceviz masa ve turuncu fon temiz bir hero composition oluşturur.

Ses:

- Hafif kaplama crackle,
- aynı düşük oda ambiyansı,
- konuşma, müzik veya insan sesi yok.

## 6. Geçiş ve post-prodüksiyon kuralları

- Clip 1→2 kesmesini, her iki klipte yiyecek dokusunun kadrajı en çok doldurduğu karelerde yap.
- Clip 2→3 kesmesini, her iki klipte ısırılmış iç dokunun kadrajı en çok doldurduğu karelerde yap.
- Kesintisiz hareket yanılsaması zorlaması yapma. Plan değişimi izleyiciye bilinçli editoryal tercih olarak görünmeli.
- Varsayılan olarak kısa hard match-cut kullan. Uzun crossfade kullanma; yiyeceği eriyormuş gibi gösterebilir.
- Gerekirse en fazla 2–3 karelik çok kısa motion-blur geçişi kullanılabilir.
- Üç klibin oda ambiyansını post-prodüksiyonda tek, kesintisiz düşük seviye altında birleştir.
- Crunch sesini yalnız gerçek ısırık karesine hizala.
- Ses seviyelerinde klip sınırında ani sıçrama oluşturma.
- Final videoda konuşma tespit edilirse yalnız sesi kapatmakla yetinme; konuşma benzeri dudak hareketi de varsa klibi reddet.

## 7. Kalite kontrol ve seçim

Her klibi concat öncesinde ayrı değerlendir.

Zorunlu marka kontrolleri:

- Aynı Creator kimliği
- Aynı siyah tişört
- Aynı yanık-turuncu fon ailesi
- Aynı ceviz masa ailesi
- Aynı beyaz kase tasarımı
- Aynı ışık yönü ve genel renk düzeni
- Mutfak/dekor/yazı bulunmaması

Zorunlu içerik kontrolleri:

- Yiyecek ilk saniyede görünür
- Sos ve doku iştah açıcı, fiziksel olarak makul
- Tek ısırık kuralı korunmuş
- İkinci ısırık veya yiyeceğin geri büyümesi yok
- El/parmak deformasyonu yok
- Abartılı veya rahatsız edici çiğneme yok
- Konuşma, insan sesi, lip-sync veya ekran yazısı yok

Geçiş kontrolleri:

- Clip 1 sonu ve Clip 2 başında kadrajı aynı doku ailesi dolduruyor
- Clip 2 sonu ve Clip 3 başında aynı tür kesit dokusu kadrajı dolduruyor
- Kesme, izleyiciye kazara continuity hatası değil bilinçli match-cut gibi görünüyor
- Ses ambiyansı kesme boyunca devam ediyor

Bir klip marka kimliğini veya kendi iç fiziğini bozuyorsa yalnız o klibi yeniden üret. Bağımsız planlar arasında tender üzerindeki her kırıntının birebir aynı olmasını şart koşma; izleyicinin açıkça fark edeceği kategori, sos, ısırık sayısı veya renk değişikliklerini ise reddet.

## 8. Özgünlük kuralı

Kanal kimliği sabit kalmalı; fakat her video yalnız yemek adı değiştirilmiş aynı şablon gibi görünmemeli.

Her yeni videoda en az iki unsur anlamlı biçimde değişmeli:

- ana duyusal eylem,
- kamera ritmi,
- texture payoff,
- sos davranışı,
- izleyicide oluşturulan merak,
- final hero presentation.

Creator, turuncu fon, ceviz masa, siyah tişört, beyaz kase ve sessiz reaksiyon kanal imzası olarak sabit kalabilir. Hikâye ve duyusal ödül yiyeceğe özgü olmalıdır.

## 9. Teknik üretim ayarları

- Orientation: 9:16
- Resolution: 720 x 1280 veya daha yüksek dikey çıktı
- Duration: her klip 10 saniye
- Output count: 1
- Style: photorealistic premium food commercial
- Dialogue: none
- Voice: none
- Music: none
- Text/subtitles: none

## 10. Teslim ve rapor

Üç klip kabul edilmeden FFmpeg concat veya YouTube upload yapma.

Final raporda şunları ver:

- kullanılan `FOOD`, `SAUCE`, `HERO_TEXTURE`, `PRIMARY_ACTION`, `TEXTURE_SOUND` ve `PAYOFF`,
- her klibin çözünürlük, fps ve gerçek süresi,
- Creator ve marka seti continuity sonucu,
- konuşma/lip-sync/ekran yazısı kontrolü,
- iki match-cut için kullanılan kesin zaman damgaları,
- ses köprüsü ve crunch hizalama sonucu,
- her klip için PASS/FAIL ve gerekçesi,
- final concat yolu, süre ve dosya boyutu,
- varsa blocker.

Üretilen video, geçici frame veya test görsellerini Git'e commit etme. Git'e yalnız prompt, kod ve metin raporlarını ekle.

Fotogerçekçi AI içerik YouTube'a yüklenecekse yükleme aşamasında uygun altered/synthetic content açıklamasını uygula.
