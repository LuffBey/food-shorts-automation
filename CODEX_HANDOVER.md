# 🚀 Food Discovery AI Video Automation — Codex Devir & Entegrasyon Dokümanı

## 📌 1. Projenin Amacı ve Özeti
Bu proje, **YouTube Shorts, TikTok ve Instagram Reels** için küresel ölçekte (dil bariyeri olmayan, yüksek retention oranına sahip) **ASMR & Food Discovery / Mukbang** videolarını uçtan uca, tam otomatik olarak üretmeyi amaçlar.

Videolar **3x10 saniyelik 3 parçanın (Toplam 30 saniye)** kusursuz bir kurgu (match-cut) ile dikey **9:16 (1080x1920, 30 FPS)** formatında birleştirilmesiyle oluşturulur:
- **Klip 1 (0–10s):** Yiyecek tabağı açılışı, parçayı alma ve sosa derin daldırma (Deep Dip).
- **Klip 2 (10–20s):** Isırık, iç dokunun gösterilmesi, peynir uzaması (Cheese pull) ve çiğneme/tatmin reaksiyonu.
- **Klip 3 (20–30s):** Sos gezdirme (Glaze/Drizzle), son lokma ve kameraya net onay (Thumbs Up).

---

## 🛠️ 2. Mevcut Sistem Mimarisi & Altyapı

1. **Sunucu & Çalışma Alanı:**
   - **OS:** Linux (Debian)
   - **Proje Ana Dizini:** `/root/hermes-projects/food-discovery-automation/`
   - **İkinci Beyin (Obsidian Kasa):** `/root/Documents/Obsidian Vault/Projects/Food Discovery Automation/`

2. **Video Üretim Motoru:**
   - **Platform:** Google Labs — Google Flow (`https://labs.google/fx/tr/tools/flow`)
   - **Model:** `Omni 1.1 Flash` (Video modu, 720p, 10s, 9:16)
   - **Erişim Yöntemi:** Headless Chromium (`--remote-debugging-port=9222`, kullanıcı profili: `/root/.chromium-profile`). Python tabanlı CDP (Chrome DevTools Protocol) websocket köprüsü ile web arayüzü doğrudan sürülmektedir.

3. **Mevcut Python Motoru (`food_discovery_engine.py`):**
   - Arayüz ayarlarını otomatik seçer (Omni 1.1 Flash, Video, 9:16, 10s).
   - Prompt kutusuna (Slate.js rich text editor) gerçek klavye olayları (CDP KeyEvent) ile prompt enjekte eder.
   - Üretilen `media.getMediaUrlRedirect` video stream URL'lerini yakalayıp yerel diske indirir.
   - FFmpeg ile 3 klibi 1080x1920 9:16 formatında, renk doygunluğunu canlandırarak (`eq=saturation=1.12:contrast=1.05`) master video olarak birleştirir.

---

## ⚠️ 3. Çözülmesi Gereken Kritik Sorun: Karakter ve Sahne Tutarlılığı (Identity Drift)

### Problem:
Text-to-Video tabanlı üretimlerde, promptlar ne kadar detaylı yazılırsa yazılsın model her 10 saniyelik klipte tohumu (seed) sıfırlamakta; bu yüzden aktörün yüzü, tabağın şekli ve masa düzeni klipler arasında değişmektedir.

### Tespit Edilen Kök Neden & Google Flow Mekanizması:
1. **Sıradan Görsel Yükleme Yanılgısı:** Flow arayüzüne dosya yüklemek veya promptta karakteri tarif etmek karakteri kilitlemez; model bunu sadece ortam referansı sayar.
2. **Casting Handshake Kuralı:** Google Flow'da karakteri kilitlemenin tek resmi yolu, karakterin **"Karakterler"** kütüphanesine kaydedilip prompt içinde **`@KarakterAdı`** şeklinde çağrılmasıdır (Slate editöründe renkli casting çipi oluşturulması gerekir).

---

## 🎯 4. Codex İçin İhtiyaç Duyulan Görevler & Çözüm Yolları

Codex'in aşağıdaki iki çözüm yolundan birini veya hibritini hayata geçirmesi beklenmektedir:

### Görev A (Google Flow Native Casting Otomasyonu):
1. `/root/hermes-projects/food-discovery-automation/creator_face_ref.jpg` görselini Google Flow Characters kütüphanesine `@Creator` adıyla kaydeden otomasyonu kurmak.
2. Slate.js editörüne metin yazarken `@Creator` casting çipini (React/Slate entity node) otomatik tetiklemek.
3. Klip 1 son karesini (`clip_1_end.jpg`) -> Klip 2'nin **Start Frame**'i; Klip 2 son karesini -> Klip 3'ün **Start Frame**'i olarak besleyen akışı tam otomatize etmek.

### Görev B (Sıfır Sapmalı Post-Process FaceSwap / LivePortrait Katmanı):
- Google Flow üzerinden üretilen yemek videosunun üzerine, sabit karakter görselimizdeki (`creator_face_ref.jpg`) yüzü videodaki aktörün yüzüne birebir, aynı mimik ve ışıkla oturtacak yerel, hafif bir araç (örneğin ReActor / InsightFace / LivePortrait) entegre etmek.

---

## 5. Codex'e Güncel Canlı Test Raporu (2026-09-03)

### Doğrulanan canlı ortam

- **Branch:** `fix/character-consistency`
- **Doğrulanan Flow projesi:** `0bd8a011-4555-49c2-adc8-ba87b68466a9`
- **Doğrulanan karakter:** `Creator`
- **Character ID:** `b068cab7-76d4-49ec-9066-9259c139d46a`
- **Erişim:** CDP port `9222`; gerektiğinde görünür Chromium + noVNC ile kullanıcı manuel kontrolü mümkündür.

### `@Creator` gerçek chip doğrulaması

Bu mekanizma artık yalnızca teorik değil, canlı Flow DOM'unda doğrulandı:

1. Composer'a gerçek CDP klavye olaylarıyla `@Creator` yazıldı.
2. Flow'un entity/media seçicisi açıldı ve doğru `Creator` karakter kartı bulundu.
3. `İsteme ekle` seçildi.
4. Slate editörde düz metin yerine şu özellikleri taşıyan gerçek entity node oluştu:
   - `data-slate-inline="true"`
   - `data-slate-void="true"`
   - `contenteditable="false"`
   - etiket: `Male food content creator portrait`

**Kural:** Düz `@Creator` metni kimlik kilidi sayılmayacak; yukarıdaki token/chip DOM doğrulaması olmadan üretim başlatılmayacak.

### Clip 1 manuel üretim sonucu

Önceki CDP tıklamasında görünen "olağan dışı etkinlik" engelinin otomasyon/etkileşim kaynaklı olduğu test edildi. Aynı hazır prompt ve gerçek `Creator` chip ile kullanıcı görünür Chromium'da **Oluştur** düğmesine manuel bastı ve Flow videoyu başarıyla üretti.

- Oluşan doğru dikey sonuç: **720×1280, 9:16, 24 fps, 10.005 sn**
- İndirilen yerel test dosyası (git dışında): `clip_1_creator_deep_dip.mp4`
- İçerik: Creator'ın çıtır tavuk parçasını sosa daldırdığı hook testi.
- Görsel inceleme: aynı erkek yüzü, kısa koyu saç/sakal, siyah tişört ve sıcak mutfak/food sahnesi klip boyunca tutarlı.
- 5. saniyede dramatik macro yakın plan bulundu; **continuation frame için uygun değil**.
- 8–9 saniye aralığı tekrar orta plana dönüyor; **9. saniye karesi** temiz continuation adayı olarak çıkarıldı: `clip_1_continuation_9s.jpg` (git dışında).

### Önemli teşhis

- `Creator` asset erişimi: **çalışıyor**.
- Gerçek `@Creator` chip ekleme: **çalışıyor**.
- Flow video üretimi: **manuel UI tıklamasıyla çalışıyor**.
- CDP üzerinden doğrudan Generate tıklamasında oluşan "unusual activity" reddi, platformun otomasyon algılama davranışıdır; karakter/prompt/video-model arızası değildir.

### Codex için sonraki uygulama yönü

1. Chip hazırlama, DOM doğrulama, prompt kurma, indirme ve frame extraction otomatik kalabilir.
2. Generate tetikleme yolunu anti-bot reddini azaltacak şekilde gerçek kullanıcı etkileşimine yaklaştırın; bu mümkün değilse human-in-the-loop modunda görünür Chromium/noVNC üzerinde kullanıcıya yalnızca **Oluştur** tıklaması bırakın.
3. Clip 2 ve 3 için her seferinde gerçek `Creator` chip ekleyin; düz metni kabul etmeyin.
4. Clip 2 Start Frame olarak `clip_1_continuation_9s.jpg` kullanılmalı; sonra Clip 2'nin temiz 8–9 sn karesi Clip 3'e aktarılmalı.
5. Her üretim sonrası indirilen videoyu ve seçilen continuation frame'i görsel olarak kontrol edin. Kimlik, saç/sakal, siyah tişört veya sahne kayarsa klibi reddedip yeniden üretin.
6. Üretilen video/frame/reference dosyalarını repoya commit etmeyin. Sadece kod ve Markdown raporları pushlanabilir.

---

## 6. Önemli Dosya Yolları ve Çalışma Ağacı

- **Ana Motor Kodu:** `/root/hermes-projects/food-discovery-automation/food_discovery_engine.py`
- **Karakter Referans Görseli:** `/root/hermes-projects/food-discovery-automation/creator_face_ref.jpg`
- **Örnek Çıktı Videosu:** `/root/hermes-projects/food-discovery-automation/real_nashville_hot_chicken_master.mp4`
- **Detaylı Analiz Notları:** `/root/Documents/Obsidian Vault/Projects/Food Discovery Automation/Character Consistency Root Cause & Fix.md`
- **Sektör Taktikleri Notu:** `/root/Documents/Obsidian Vault/Projects/Food Discovery Automation/Professional Mukbang Tricks & Prompt Rules.md`
