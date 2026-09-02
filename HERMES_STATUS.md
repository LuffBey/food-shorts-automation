# Current Status

**Branch:** `fix/character-consistency`
**Exact Flow project:** `0bd8a011-4555-49c2-adc8-ba87b68466a9`
**Exact Creator character:** `b068cab7-76d4-49ec-9066-9259c139d46a` (`Creator`)

## Completed live checks

- Connected to the authenticated Flow session via CDP port `9222`.
- Opened and verified the user-created character at the exact project/character URL.
- Entered the same project composer.
- Typed `@Creator` using real CDP keystrokes, opened the Flow entity/media panel, and selected its `Creator` → `İsteme ekle` action.
- Verified the composer contains a real Slate inline/void, `contenteditable=false` character entity node (`Male food content creator portrait`), not just plain `@Creator` text.

## Generation result

Clip 1 was submitted with the real Creator entity and the required chicken-tender deep-dip ASMR hook. Flow rejected the generation immediately with:

> Başarısız — Olağan dışı etkinlikler tespit ettik. Daha fazla bilgi için lütfen Yardım Merkezi'ni ziyaret edin; üretme işlemi için kredi kullanmadınız.

No Clip 1 media was generated, therefore Clips 2–3, continuation frames, visual identity comparison, concat output, and drift assessment could not be performed. Ingredients/reference fallback was not used.

## Manuel UI Başarı Güncellemesi (2026-09-03)

Önceki otomatik Generate denemesi Flow tarafından "olağan dışı etkinlik" olarak reddedilmişti. Aynı exact proje, gerçek `Creator` chip'i ve aynı prompt ile görünür Chromium/noVNC üzerinden kullanıcı manuel **Oluştur** tıklaması yaptıktan sonra video başarıyla üretildi.

- Doğrulanan Flow projesi: `0bd8a011-4555-49c2-adc8-ba87b68466a9`
- Doğrulanan gerçek karakter entity: `Creator` (`b068cab7-76d4-49ec-9066-9259c139d46a`)
- Gerçek Slate chip: `data-slate-inline=true`, `data-slate-void=true`, `contenteditable=false`
- Klip 1 çıktısı: 720×1280, 9:16, 24 fps, 10.005 sn
- Tutarlılık gözlemi: yüz, kısa koyu saç/sakal, siyah tişört ve sıcak food sahnesi test klibinde tutarlı.
- Clip 2/3 üretimi bu yatay/dikey ve manuel tetikleme testinden sonra kullanıcı isteğiyle durduruldu; tam 3 kliplik üretim henüz tamamlanmadı.

Detaylı Codex handover notu: `CODEX_HANDOVER.md`; canlı test kanıtı: `HERMES_TEST_REPORT.md`.

## OS-level visible UI diagnostic (single click)

A one-shot diagnostic was run without modifying the existing Creator/project/prompt preparation flow. The helper `click_generate_visible_ui.py` uses X11 focus, pointer movement, and one normal XTEST left-button press/release on visible Chromium/noVNC; it does not use CDP mouse input, stealth, spoofing, proxy/VPN, CAPTCHA handling, or retries.

- Exact project and a real tokenized `Creator` chip were freshly prepared.
- Visible Chromium window: `0x200003`, `1050×780` at `(10,10)`.
- Generate button viewport rect: `(785,586,32,32)`; calculated X11 root target: `(811,612)`; browser viewport `1050×659`, DPR `1`.
- One OS-level click was sent, then the page was observed for 120 seconds.
- No new video appeared; Flow showed neither a generation-progress state nor `Olağan dışı etkinlik`; editor/chip remained unchanged and the video count stayed at two pre-existing videos.
- Post-test X11 pointer inspection showed `(1279,20)`, so the initial helper's pointer-warp call was malformed and the event cannot be confirmed as landing on Generate. The helper has been corrected, but **no retry was sent** per test constraint.

**Result:** inconclusive. This was not a confirmed successful visible-UI click, and it did not produce an unusual-activity refusal either. A future run may use the corrected helper for exactly one new click after explicitly authorizing a fresh test.

## Corrected OS-level Generate test

A fresh Clip 1 test was prepared with the same real `Creator` chip and unchanged vertical 9:16 deep-dip prompt. Before clicking, the X11 pointer was `(1279,20)` and the mapped visible Chromium window `0x200003` had a computed Generate target `(811,612)` inside the button's `(785,586,32,32)` viewport rectangle. The corrected helper then sent exactly one normal X11 pointer move plus one primary-button press/release.

- **Pointer target verified:** yes. Post-click X11 pointer was `(811,612)`, exactly matching target.
- **Click reached calculated Generate coordinate:** yes; no CDP/DOM click was used.
- **Generation started:** no visible or DOM progress state in 120 seconds.
- **Olağan dışı etkinlik:** no.
- **New video:** no; video count remained two pre-existing videos.
- **New video resolution/FPS/duration:** N/A.
- **Clip 2/3:** not attempted.

This is a clean, non-stealth, non-retried OS-level test. The remaining issue is now that Flow does not react to the synthetic X11 event even when pointer placement is confirmed; it differs from an actual human noVNC click, which did generate Clip 1 successfully.

## Corrected web-content-coordinate XTEST test

The coordinate conversion was corrected without changing the existing Creator/project/prompt preparation logic. Fresh CDP values immediately before the click were `screen=(10,10)`, `outer=1050×780`, `inner=1050×659`, `DPR=1`, and Generate DOM rect `(785,586,32,32)`. The helper derived (rather than hard-coded) vertical chrome `121` and used content origin `(10,131)`, so the corrected Generate root target was **`(811,733)`**.

The helper now explicitly declares ctypes signatures for `XTestFakeMotionEvent`, `XTestFakeButtonEvent`, `XSync`, and `XQueryPointer`; it focuses/syncs Chromium, uses official XTEST motion, synchronizes, maps the actual root pointer back to viewport coordinates, fails closed if outside the Generate DOM rect, then sends exactly one normal primary press/release.

- Pointer before: `(811,612)`.
- Pointer after XTEST motion: `(811,733)`.
- Converted back to viewport: `(801,602)`, inside the Generate rect: **yes**.
- Exactly one OS-level click was sent; no CDP/DOM click, stealth/fingerprint, proxy/VPN, CAPTCHA handling, or retry was used.
- During 120 seconds: no generation progress, no `Olağan dışı etkinlik`, no other failure, and no new video (two pre-existing videos remained). Clip 2/3 were not attempted.

**Conclusion:** the previous browser-chrome coordinate error is eliminated. Even a verified XTEST click inside the live Generate rectangle caused no Flow state transition, unlike an actual human click through noVNC.

## Generate browser event-chain comparison

A temporary in-page logger observed the live Generate button, parents, and document during one human noVNC click and one corrected XTEST click. It was browser-only instrumentation; existing Creator/project/prompt preparation code remained unchanged. Raw captures are local only: `/tmp/flow_human_generate_events.json` and `/tmp/flow_xtest_generate_events.json`.

| Aspect | Human noVNC | Corrected XTEST |
|---|---|---|
| Creator chip / prompt | Fresh real tokenized chip; same Clip 1 prompt | Fresh real tokenized chip; same Clip 1 prompt |
| Core button chain | `pointerdown → mousedown → focus → pointerup → mouseup → click` | Same |
| `isTrusted` | `true` | `true` |
| Pointer type / button | `mouse`, button 0; buttons 1 at down | Same |
| Arrival path | Multiple small pointer moves over ~0.8s | One synthetic arrival/move |
| Flow result | Third video element appeared; authenticated media HEAD `200` / 3,448,172 bytes | Failed media card at 32%; no fourth playable video |
| `Olağan dışı etkinlik` | No | No (a generic `Başarısız` card appeared instead) |

**Finding:** the captured browser DOM activation sequence is materially equivalent and trusted in both cases. No missing `mousedown`, focus, `mouseup`, or `click` explains the different outcome. The remaining difference is outside the DOM logger—likely lower-level input provenance, browser/renderer handling, or Flow backend policy. No stealth/bypass was used. A human noVNC click is still the only confirmed reliable Generate trigger.

## Programmatic VNC/RFB PointerEvent test

A direct shared **RFB 3.8** session to `127.0.0.1:5900` was used—the same running `x11vnc` server behind noVNC's `websockify:6080 → x11vnc:5900 → X11 :99` path. The helper `vnc_rfb_pointer_event.py` used standard RFB `None` authentication and exactly one sequence: `MOVE buttonMask=0` at dynamically calculated `(811,733)`, 120ms wait, left-down `buttonMask=1`, 120ms wait, left-up `buttonMask=0`.

- No CDP mouse/DOM event, XTEST, stealth/fingerprint, proxy/VPN, CAPTCHA handling, or retry was used.
- Fresh Creator chip and unchanged Clip 1 prompt were prepared first.
- Browser logger recorded a complete trusted chain: `pointerover → pointerenter → mouseover → mouseenter → pointermove → mousemove → pointerdown → mousedown → focus → pointerup → mouseup → click`.
- All captured events had `isTrusted=true`; PointerEvents had `pointerType="mouse"`; button 0 and correct `buttons` down/up state.
- Flow immediately created a generic failed media card: visible `Başarısız`, observed 10% card progress. No `Olağan dışı etkinlik`; no new playable video; Clips 2/3 not attempted.

| Route | Result |
|---|---|
| Human noVNC (`browser → websockify → x11vnc → X11`) | Playable video generated |
| Programmatic XTEST → X11 | Generic failed card / no playable video |
| Programmatic RFB → **same x11vnc** → X11 | Generic failed card / no playable video |

**Conclusion:** simply using the same VNC server/input pipeline is insufficient to reproduce a human noVNC success. At DOM level, all paths produce trusted and complete activation sequences. The remaining difference is outside the logged DOM chain—likely actual noVNC/browser remote-user interaction behavior, input provenance/timing, or Flow backend policy. No bypass was attempted.

## Keyboard accessibility activation test

The branch was reset to requested base `bee55e0e6b0f640653e0b0aea01e16bac978afee` before this test. The exact project and fresh real tokenized `Creator` chip were prepared with the unchanged Clip 1 prompt. No mouse, CDP/DOM click, XTEST mouse/pointer event, VNC/RFB pointer event, stealth/fingerprint spoofing, proxy/VPN, CAPTCHA/security bypass, retry loop, merge, or media commit was used.

Visible Tab navigation reached Generate in four verified focus steps: `add_2/Oluştur` → `Ajan` → `Video 720p 10s` → `arrow_forward/Oluştur`. At step 4, `document.activeElement === Generate button`; it was enabled. After clearing the logger, one normal visible **Enter** keydown/keyup was sent (Space was not also sent, avoiding a second activation).

Captured on the actual focused Generate button:

```text
keydown(Enter) → keypress(Enter) → click → keyup(Enter)
```

Every event had `isTrusted=true`; Enter had `repeat=false`, and Chromium synthesized the click with `button=0`, `buttons=0`, `detail=0`.

**Flow result:** generic `Başarısız` was immediate; no `Olağan dışı etkinlik`, no positive progress state, and no playable new video. Flow added a failed media shell (element count rose to 5), so no resolution/FPS/duration exists. Clip 2/3 were not attempted.

**Conclusion:** Tab focus and keyboard accessibility activation are browser-correct and trusted, but Flow returns the same generic failure behavior as programmatic pointer routes. Human noVNC mouse click remains the only confirmed playable-generation path in this session.

## Otomasyon için kalan mesele

`Creator` asset, gerçek chip, prompt ve Flow video modelinin çalıştığı kanıtlandı. Kalan mesele yalnızca CDP ile doğrudan Generate tıklamasının Flow tarafından "olağan dışı etkinlik" olarak reddedilmesi. Üretim tetikleme adımı insan-onaylı görünür Chromium/noVNC tıklaması olarak bırakılırsa akış çalışıyor.

## Resume condition

Once the Flow account can generate again, rerun the exact project test: generate Clip 1; inspect and select a clean 8–9s frame; insert the verified Creator chip again for Clip 2; repeat for Clip 3; visually reject any face, hair, wardrobe, or scene drift before concatenation.

Detailed live evidence and the complete result matrix are in `HERMES_TEST_REPORT.md`.
