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

## Manual UI generation validation (2026-09-03)

The prior direct-CDP Generate attempt was rejected with Flow's "unusual activity" message. The same exact project, verified real `Creator` entity chip, and prepared Clip 1 prompt were then submitted by the user through the visible Chromium/noVNC Flow UI. Flow generated the video successfully.

- Generated test clip: **720×1280 (9:16), 24 fps, 10.005 seconds**.
- Local non-versioned test download: `clip_1_creator_deep_dip.mp4`.
- Visual review: the creator's face, short dark hair/stubble, plain black crew-neck shirt, and warm food scene stayed consistent within the test clip.
- The dramatic 5s macro close-up is unsuitable as a chain frame; the 9s medium-shot frame was extracted as `clip_1_continuation_9s.jpg` for potential Clip 2 chaining.
- The user stopped the run after this manual trigger/orientation test. Clips 2 and 3 were **not** generated, and the 3×10s final concat/identity comparison is therefore still incomplete.

This changes the diagnosis: `Creator` asset access, real chip insertion, prompt setup, and Flow video generation are all working. The remaining automation issue is specifically the direct CDP Generate interaction; a human-in-the-loop visible UI click is a functional fallback.

## OS-Level Visible UI Click Diagnostic (2026-09-03)

A dedicated, transparent helper, `click_generate_visible_ui.py`, was added for this diagnostic only. It uses X11 on the existing `:99` visible Chromium/noVNC display: it raises/focuses the existing Chromium X11 window, moves the real X11 pointer, and emits one XTEST primary-button press/release. It contains no CDP mouse event, stealth/fingerprint change, proxy/VPN change, CAPTCHA handling, or retry loop.

### Pre-click preparation

- Exact project: `0bd8a011-4555-49c2-adc8-ba87b68466a9`.
- Real tokenized `Creator` chip was freshly inserted and DOM-verified before the click.
- Prepared prompt: the same simple Clip 1 vertical 9:16 chicken-tender deep-dip prompt.
- Visible Chromium X11 window: ID `0x200003`, bounds `left=10`, `top=10`, `width=1050`, `height=780`.
- Generate button viewport rectangle: `left=785`, `top=586`, `width=32`, `height=32`; centre `(801, 602)`.
- Browser viewport: `1050×659`, `devicePixelRatio=1`; root-screen target coordinate calculated as `(811, 612)`.

### One-click outcome

- Interaction method: one OS-level X11 pointer move + one left-button press/release aimed at root coordinate **(811, 612)** on visible Chromium window `0x200003`.
- Flow's visible result: **no visible state transition** during the 120-second observation window.
- DOM observation after the click: editor content and `Creator` chip remained present; no generation-progress text; no `Olağan dışı etkinlik` error; video count stayed at the pre-existing **2** videos.
- Resolution/fps/duration: **not applicable**—this click did not produce a new video.

Post-test pointer inspection found the X11 pointer still at `(1279, 20)`, proving the original helper's `XWarpPointer` call was malformed and did not move the pointer to the intended Generate coordinate. The helper has been corrected for the X11 function signature, but **no second Generate click was sent**, as required. Therefore the honest test status is: **inconclusive — the one sent event was not confirmed to land on the button; neither `unusual activity` nor a new video was observed.**

## Exact blocker and next action

The identity-lock precondition is proven in the exact user-created Flow project: the `Creator` asset is accessible, the real tokenized entity chip can be inserted, and Flow can generate when the user clicks **Oluştur** in visible Chromium/noVNC. The remaining blocker is only direct-CDP generation triggering Flow's automated-activity detection.

To complete the production test, retain the automated preparation, download, frame extraction, and visual QA; require one visible human **Oluştur** click per clip. Generate Clip 2 with the selected 9s Clip 1 continuation frame, inspect it, then generate Clip 3 with a clean 8–9s Clip 2 frame. No generated media, screenshots, reference images, cookies, or secrets are committed.
