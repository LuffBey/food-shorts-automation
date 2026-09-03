# Historical Baseline — Google Flow Agent Kanal Görsel Kimliği & 3×10s Shorts Üretim Raporu

> This report predates the Omni 1.1 scene-extension migration. Its PASS result
> applies only to the former independent-clip test and must not be presented as
> validation of the active architecture. See `ARCHITECTURE.md` and
> `HERMES_NEXT_ACTION.md` for the required new validation.

## 1. Görev ve Branch Güncellemesi
- **Hedef Branch:** `fix/character-consistency`
- **Hedef Commit:** `f9c963f5068900eb3096b2ede513bd2200648bc7`
- **Referans Doküman:** `FLOW_AGENT_CHANNEL_IDENTITY_PROMPT.md`

---

## 2. Aşama 1–3: Master Brand Set ve Sınır Kareleri Doğrulaması
1. **Master Brand Set (`BrandSet_Master.jpg` & `S0_Master.jpg`):**
   - **Arka Plan:** Düz mat yanık-turuncu fon (`#D9682E`), sıfır mutfak/dolap/dekor/lamba (`PASS`).
   - **Masa:** Yatay damarlı koyu ceviz ahşap masa (`#7A4A2A`), kasap bloğu/damalı desen yok (`PASS`).
   - **Kase & Sos:** Masada hafif solda beyaz seramik kase, içinde koyu amber-kırmızı parlak BBQ sosu (`PASS`).
   - **Kıyafet & Karakter:** Düz mat siyah bisiklet yaka tişört, `@Creator` kimliği (`PASS`).
   - **Food Prop:** Tek parça, altın-kahverengi çıtır unbitten kızarmış tavuk tender (`PASS`).
2. **Sınır Kareleri (S0 ➔ S1 ➔ S2 ➔ S3):**
   - **S0:** Unbitten kuru tender, ağız kapalı tebessüm (`PASS`).
   - **S1 (Clip 1 Sonu / Clip 2 Başı):** Yalnızca alt %25 kısmı koyu amber-kırmızı sosla kaplı, ısırılmamış, ağız tamamen kapalı (`PASS`).
   - **S2 (Clip 2 Sonu / Clip 3 Başı):** Üst ucunda tek net ısırık izi, alt sos aynı, ağız kapalı çiğneme tebessümü (`PASS`).
   - **S3 (Clip 3 Sonu / Final):** Tek ısırıklı tender dokusu kameraya gösterilmiş, kapalı ağızlı onay gülümsemesi (`PASS`).

---

## 3. Aşama 4: Klip Üretimleri ve QC Kapıları
- **Clip 1 (Dip & Hold S1):**
  - **Dosya:** `/root/hermes-projects/food-discovery-automation/brand_clip_1.mp4`
  - **Süre / Format:** `10.005 s` | `720x1280` (9:16) | `24 fps`
  - **QC:** Turuncu fon, ceviz masa, koyu sos, unbitten tender, ağız kapalı (konuşma/dudak oynatma yok) (`PASS`).
- **Clip 2 (Single Bite & S2):**
  - **Dosya:** `/root/hermes-projects/food-discovery-automation/brand_clip_2.mp4`
  - **Süre / Format:** `10.005 s` | `720x1280` (9:16) | `24 fps`
  - **QC:** S1 başlangıcıyla dikişsiz devam etti, tek net ısırık alındı, ağız kapalı çiğnendi, konuşma yok (`PASS`).
- **Clip 3 (Texture Reveal & S3 Reaction):**
  - **Dosya:** `/root/hermes-projects/food-discovery-automation/brand_clip_3.mp4`
  - **Süre / Format:** `10.005 s` | `720x1280` (9:16) | `24 fps`
  - **QC:** İkinci ısırık alınmadı, doku gösterildi, mutfağa dönüşmedi, konuşma/fısıltı yok, sessiz onay tebessümü (`PASS`).

---

## 4. Final Concat & Çıktı
- **Video Dosyası:** `/root/hermes-projects/food-discovery-automation/brand_channel_identity_shorts_30s.mp4`
- **Toplam Süre:** `30.036 s`
- **Çözünürlük & FPS:** `720x1280` (9:16 dikey) | `24 fps`
- **Boyut:** `9,890,361 bytes`
- **Tüm QC Kapıları:** PASS (Sıfır konuşma, sıfır mutfak kayması, tam sahne/renk/yiyecek kilitleri).
