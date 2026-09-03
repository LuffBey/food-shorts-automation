# Google Flow Agent — Channel Identity and Continuity Prompt

Google Flow Agent ile kanalın sabit görsel kimliğine sahip 3 x 10 saniyelik bir food-ASMR Shorts videosu üret.

## Ana hedef

Önceki test Creator kimliğini başarıyla korudu. Mevcut karakter kilidi talimatlarını aynen koru. Bu çalışmanın yeni hedefi arka plan, masa, kamera, kase, sos ve yiyecek durumunu da aynı kesinlikle sabitlemektir.

Flow'un desteklenen normal Agent, Ingredients/References ve Frames özelliklerini kullan. Güvenlik, kota veya otomasyon kontrollerini aşmaya çalışma.

## Aşama 1 — Master Brand Set

Video üretmeden önce tek bir yüksek kaliteli `BrandSet_Master` görseli hazırla.

Master set tanımı:

- Aynı lisanslı `@Creator` kullanılmalı.
- Creator üzerinde desensiz, logosuz, mat siyah bisiklet yaka tişört bulunmalı.
- Arka plan düz ve mat yanık-turuncu stüdyo fonu olmalı.
- Ana fon rengi yaklaşık `#D9682E` olmalı.
- Creator'ın arkasında çok hafif ve yumuşak `#E98745` merkez aydınlığı bulunmalı.
- Fonda dolap, mutfak, pencere, raf, bitki, lamba, tablo, logo veya başka dekor bulunmamalı.
- Fon düz, kesintisiz ve bütün videolarda aynı olmalı.
- Masa orta-koyu ceviz renginde, uzun ve yatay doğal ahşap damarlarına sahip olmalı.
- Kasap bloğu, kareli parke veya end-grain masa deseni olmamalı.
- Masa yüzeyi yaklaşık `#7A4A2A` tonunda olmalı.
- Masanın ortasının hafif solunda tek bir küçük, sığ, parlak beyaz seramik sos kasesi bulunmalı.
- Kasede koyu amber-kırmızı, parlak ve kıvamlı tek bir sos bulunmalı.
- Beyaz, kremalı veya açık renkli sos kullanılmamalı.
- Creator göğüsten yukarısı görünecek şekilde kadrajlanmalı.
- Yüz, iki el, kase ve çalışma alanı aynı anda kadraja sığmalı.
- Kamera göz seviyesinin çok az altında ve tam karşıda olmalı.
- Sabit 50 mm eşdeğeri doğal perspektif kullanılmalı.
- Kamera yüksekliği, açı, lens, zoom ve subject distance daha sonra değiştirilmemeli.
- Yumuşak ana ışık kamera-solundan gelmeli.
- Turuncu fon Creator'ın tenini veya yiyeceği turuncuya boyamamalı.
- Ten rengi ve yiyeceğin altın-kahverengi kaplaması doğal kalmalı.
- Siyah tişört ve beyaz kase, yiyecek ile fon arasında güçlü görsel ayrım sağlamalı.

Bu görseli üretimden önce incele. Tüm koşulları karşılamıyorsa video üretimine geçme. Başarılı görseli `@BrandSet_Master` olarak kaydet.

Renk kodları yalnız master görseli oluşturmak içindir. Master onaylandıktan sonra her klipte seti metinden yeniden tasarlama; aynı `@BrandSet_Master` görselini referans olarak kullan.

## Aşama 2 — Food Prop

Tek bir `@FoodProp_Master` hazırla:

- Yalnızca bir adet büyük, uzun ve çıtır kızarmış tavuk tender bulunmalı.
- Belirgin, kuru ve altın-kahverengi çıtır kaplamaya sahip olmalı.
- Başlangıçta bütün ve ısırılmamış olmalı.
- Uzunluğu, kalınlığı, konturu ve kaplama deseni sabit olmalı.
- Kemik, tabak, ikinci parça veya ekstra yiyecek bulunmamalı.

Bu nesne bütün kliplerde aynı fiziksel tender olarak kabul edilmeli. Model yeni bir tender oluşturmamalı.

## Aşama 3 — Sınır kareleri

`@Creator`, `@BrandSet_Master` ve `@FoodProp_Master` kullanarak dört sınır karesi hazırla. Bu kareleri birbirinden bağımsız üretme; ilk onaylı master kareyi düzenleyerek türet.

### S0 — Başlangıç

Creator tender'ı sağ elinde tutuyor. Tender bütün, kuru ve ısırılmamış. Sol el masada. Koyu amber-kırmızı sos kasesi sabit yerinde.

### S1 — Clip 1 sonu / Clip 2 başlangıcı

Aynı kare düzeni. Aynı tender'ın yalnızca alt yüzde 25'lik kısmı koyu amber-kırmızı sosla kaplı. Tender hâlâ ısırılmamış. Kase, eller, yüz, masa ve fon aynı.

### S2 — Clip 2 sonu / Clip 3 başlangıcı

Aynı kare düzeni. Tender'ın üst ucunda tek, belirgin bir ısırık izi var. Alt kısmındaki koyu sos aynı. Başka hiçbir şey değişmemiş.

### S3 — Final

Creator aynı tek-ısırıklı tender'ı kameraya biraz daha yakın gösteriyor ve doğal biçimde gülümsüyor. Diğer eli küçük bir başparmak işareti yapıyor. Kase aynı yerde ve kadrajda.

Dört kare arasında şunlar değişmemeli:

- yüz ve saç,
- kıyafet,
- arka plan rengi,
- fon ışık dağılımı,
- masa rengi ve damar deseni,
- kase biçimi, boyutu ve konumu,
- sos rengi,
- kamera ve kadraj,
- tender'ın temel geometrisi.

## Aşama 4 — Video üretimi

Üretim ayarları:

- Model: Gemini Omni Flash 1.1
- Format: 9:16
- Çözünürlük: 720p
- Süre: 10 saniye
- Output: 1
- Görünüm: fotogerçekçi
- Ses: doğal food-ASMR
- Konuşma ve dudak senkronu: yok
- Müzik: yok
- Yalnızca hafif ortam sesi, sos sesi ve tek gerçekçi crunch kullanılmalı.

### Clip 1 — Dip

- Gerçek Start Frame: `S0`
- Gerçek End Frame: `S1`

Creator videonun ilk karesinde tender'ı kameraya hafifçe gösterir. Boş giriş veya selamlama yapmaz. Ardından aynı tender'ı aynı sağ eliyle, aynı yerde duran kaseye bir kez yavaşça batırır ve kaldırır.

Sos koyu amber-kırmızı kalmalı. Sosun rengi beyaza, turuncuya veya başka bir renge dönüşmemeli. Kase hareket etmemeli veya biçim değiştirmemeli.

Son 1 saniye boyunca `S1` düzenine yerleşerek sabit kal.

### Clip 2 — Single Bite

- Gerçek Start Frame: `S1`
- Gerçek End Frame: `S2`

İlk kare Clip 1'in son karesiyle görsel olarak aynı olmalı. Yeni bir sahne kurma.

Creator aynı soslu tender'dan yalnızca bir ısırık alır. Tek, net ve doğal crunch duyulur. Aşırı büyük ısırık, grotesk ağız hareketi veya abartılı çiğneme oluşturma.

Tender yalnızca ısırılan miktar kadar küçülmeli. Sos kaplaması ve çıtır kaplama deseni korunmalı. Kase ve masa hareket etmemeli.

Son 1 saniye boyunca `S2` düzeninde sabit kal.

### Clip 3 — Texture Reveal and Signature Reaction

- Gerçek Start Frame: `S2`
- Gerçek End Frame: `S3`

İlk kare Clip 2'nin son karesiyle aynı olmalı. Mutfak veya yeni arka plan oluşturma.

Creator ikinci bir ısırık almaz. Mevcut tek-ısırıklı tender'ı hafifçe kameraya yaklaştırarak iç dokuyu gösterir. İç kısım doğal, sulu ve lifli görünmeli; yiyecek parçalanmamalı veya başka bir ürüne dönüşmemeli.

Creator kısa, kontrollü ve doğal bir memnuniyet gülümsemesi gösterir. Diğer eliyle küçük bir başparmak işareti yapar. Son kare `S3` ile eşleşir.

## Mutlak sahne kilidi

Her üç klip için:

- Yeni arka plan üretme.
- Stüdyo fonunu mutfağa dönüştürme.
- Fon rengini krem, gri, yeşil veya beyaza değiştirme.
- Dekor, dolap, raf, pencere veya ışık ekleme.
- Masa malzemesini veya damar desenini değiştirme.
- Kaseyi büyütme, küçültme, derinleştirme veya hareket ettirme.
- Kase içeriğini değiştirme.
- Koyu amber-kırmızı sosu beyaz sosa dönüştürme.
- Kamerayı yaklaştırma, uzaklaştırma veya farklı açıya taşıma.
- Creator'ın kadrajdaki kafa ve gövde ölçeğini değiştirme.
- Yeni kişi, yeni el, yeni yemek veya ikinci tender oluşturma.
- Klip içinde cut, cutaway, insert shot, close-up, zoom veya yeniden kadrajlama yapma.
- Yiyeceği geri büyütme.
- Isırık izini kapatma, taşıma veya yeniden şekillendirme.
- Tender'ı bir elden diğerine geçirme.

Kamera tripod üzerinde kilitli, tek çekim gibi davranmalı.

## Zorunlu QC kapıları

Her üretimden sonra yalnız prompta güvenme; videoyu görsel olarak doğrula.

### Clip 1 red kriterleri

- Turuncu master fon eşleşmiyorsa
- Masa deseni değişmişse
- Sos koyu amber-kırmızı değilse
- Kase farklıysa
- Creator veya kamera ölçeği değişmişse

### Clip 2 red kriterleri

- İlk kare Clip 1'in son karesiyle eşleşmiyorsa
- Fon, masa, kase veya sos değişmişse
- Birden fazla ısırık oluşmuşsa
- Tender farklı bir parçaya dönüşmüşse
- Kamera kesmesi varsa

### Clip 3 red kriterleri

- İlk kare Clip 2'nin son karesiyle eşleşmiyorsa
- Arka plan mutfağa veya başka bir sete dönüşmüşse
- İkinci ısırık oluşmuşsa
- Kase kaybolmuş veya büyümüşse
- Kamera açısı değişmişse

Kliplerden biri başarısızsa yalnızca başarısız klibi yeniden üret. Üç klip de onaylanmadan FFmpeg concat veya YouTube upload yapma.

## Sınır karesi raporu

Concat öncesinde şu dört karşılaştırmayı raporla:

- Clip 1 son kare ile `S1`
- Clip 2 ilk kare ile `S1`
- Clip 2 son kare ile `S2`
- Clip 3 ilk kare ile `S2`

Her karşılaştırmada aşağıdaki alanları ayrı ayrı `PASS` veya `FAIL` olarak bildir:

- Creator
- fon rengi
- masa dokusu
- kamera ve kadraj
- kase biçimi ve konumu
- sos rengi
- tender şekli
- ısırık durumu
- tender'ı tutan el

Herhangi bir `FAIL` varsa concat yapma.

## Teslim raporu

Yalnızca bütün QC kapıları geçilirse FFmpeg ile tek bir 30 saniyelik video oluştur. Son raporda şunları ver:

- kullanılan Flow modeli ve ayarlar,
- `BrandSet_Master`, `FoodProp_Master`, `S0`, `S1`, `S2`, `S3` oluşturma ve kullanım durumu,
- her klibin generation sonucu,
- her sınır karşılaştırmasının PASS/FAIL sonucu,
- her klibin çözünürlük, fps ve süresi,
- final concat dosya yolu ve final süre,
- varsa blocker.

Üretilen medya dosyalarını veya geçici frame'leri Git'e commit etme.
