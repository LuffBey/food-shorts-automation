# HERMES_TEST_REPORT — Exact Creator Character 3×10s Test

**Date:** 2026-09-03
**Branch:** `fix/character-consistency`
**Base commit under test:** `0acfb3e` (`docs: target exact user-created Flow Creator asset`)

## Exact authenticated Flow target

- **Project ID:** `0bd8a011-4555-49c2-adc8-ba87b68466a9`
- **Character ID:** `b068cab7-76d4-49ec-9066-9259c139d46a`
- **Character name:** `Creator`
- **Character URL:** `https://labs.google/fx/tr/tools/flow/project/0bd8a011-4555-49c2-adc8-ba87b68466a9/character/b068cab7-76d4-49ec-9066-9259c139d46a`

## Live verification

Connected to the existing authenticated Chromium session through CDP port `9222`, navigated to the exact character URL, and reloaded once after the initial client-side page exception.

The reloaded character page showed all required identity evidence:

- page title/content showed `Creator`;
- exact project and character IDs remained in the live URL;
- character portrait was named **Male food content creator portrait**;
- character editor showed the black crew-neck food-creator specification.

After selecting **Bitti**, the same project composer loaded and its media panel visibly showed a tile with:

- `id="fe_id_b068cab7-76d4-49ec-9066-9259c139d46a"`
- tile title `Creator`
- type `Karakter`
- action `İsteme ekle`.

## Real `@Creator` entity chip verification

This test did verify a real Flow entity—not literal prompt text only:

1. `@Creator` was typed through real CDP key events, which opened Flow's media/entity panel.
2. The exact `Creator` character tile was shown in that panel.
3. `İsteme ekle` was clicked.
4. The Slate composer DOM then contained an inline, void, `contenteditable="false"` entity node, rather than only a Slate text span:

```html
<span data-slate-node="element" data-slate-inline="true"
      data-slate-void="true" contenteditable="false" ...>
  Male food content creator portrait
</span>
```

Therefore the real `Creator` chip was inserted successfully for **Clip 1**.

## Generation attempt

Clip 1 was composed with the verified Creator entity plus the required vertical 9:16 chicken-tender deep-dip hook, stable black wardrobe, same warm table/background/lighting/camera constraints, and anti-drift constraints.

The real Flow **Oluştur** action was clicked. Flow immediately returned this visible error:

> **Başarısız — Olağan dışı etkinlikler tespit ettik. Daha fazla bilgi için lütfen Yardım Merkezi'ni ziyaret edin; üretme işlemi için kredi kullanmadınız.**

No video element, generated media URL, or downloadable Clip 1 appeared. This is a Flow account/platform generation restriction after successful character/chip verification—not an asset lookup, tokenization, prompt, or video-download failure.

## Result matrix

| Requirement | Result |
|---|---|
| Active Flow project | `0bd8a011-4555-49c2-adc8-ba87b68466a9` |
| Exact Creator ID/name detected | **Yes** — `b068cab7-76d4-49ec-9066-9259c139d46a` / `Creator` |
| Creator asset accessible | **Yes** |
| Real `@Creator` chip inserted — Clip 1 | **Yes** |
| Real `@Creator` chip inserted — Clip 2 | **No — Clip 2 was not reachable** |
| Real `@Creator` chip inserted — Clip 3 | **No — Clip 3 was not reachable** |
| Clip 1 generated | **No — Flow blocked generation** |
| Clip 2 generated | **No** |
| Clip 3 generated | **No** |
| Clip 1 → 2 identity result | **Uncertain / not evaluable** |
| Clip 2 → 3 identity result | **Uncertain / not evaluable** |
| Face/hair/wardrobe/scene drift | **Not evaluable: no generated clips** |
| Regeneration attempts | **None** — retrying platform restriction would not test identity continuity |
| Ingredients fallback used | **No** |
| Final output path | **None** |

## Exact blocker and next action

The identity-lock precondition is now proven in the exact user-created Flow project: the `Creator` asset is accessible and the real tokenized entity chip can be inserted. The sole blocker is Flow's visible **unusual activity** generation refusal. Resolve that restriction in the authenticated Google Flow account/session, then rerun Clip 1 and continue with clean 8–9 second continuation frames for Clips 2 and 3. No fallback was used and no generated media, screenshots, reference images, cookies, or secrets are committed.
