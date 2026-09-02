# Hermes — Next Action: Generate via Standard Keyboard UI Activation

Branch: `fix/character-consistency`

## Exact Flow target

- Project ID: `0bd8a011-4555-49c2-adc8-ba87b68466a9`
- Character ID: `b068cab7-76d4-49ec-9066-9259c139d46a`
- Character name: `Creator`

## Current proven state

- Exact project and `Creator` asset work.
- Real tokenized `@Creator` chip works.
- Human noVNC click on **Oluştur** generates successfully.
- Direct CDP Generate activation was rejected as unusual activity.
- Programmatic XTEST and direct RFB pointer activation produced trusted DOM click chains but failed to produce a playable output.

Do not keep changing mouse paths. The next diagnostic is the standard keyboard-accessibility activation path.

## Goal

Prepare one normal Clip 1 request exactly as before, then activate the focused visible **Oluştur** control with ordinary OS/VNC keyboard events rather than mouse events or DOM/CDP activation.

This is a normal UI/accessibility interaction test. Do not attempt stealth, fingerprint spoofing, proxy/VPN changes, CAPTCHA handling, timing randomization, or any security-control bypass.

## Required procedure

1. Pull the latest `fix/character-consistency` branch.
2. Use the existing authenticated remote Chromium/noVNC session and exact Flow project.
3. Prepare the same simple Clip 1 test prompt with the real tokenized `Creator` entity chip.
4. Verify the visible **Oluştur** control is enabled (`disabled=false`, `aria-disabled` not true).
5. Do NOT call `.focus()` from JavaScript and do NOT use CDP `Runtime.evaluate`/DOM activation on the Generate control.
6. Use the normal desktop keyboard navigation path to move focus to **Oluştur**. Prefer RFB/VNC KeyEvent or ordinary OS-level keyboard input through the visible session.
7. After each Tab/Shift+Tab step, DOM inspection may be used only to READ `document.activeElement` and verify which visible control owns focus. Do not mutate focus from JS.
8. Stop navigation as soon as the active element is the actual Generate/Oluştur control.
9. Record:
   - active element tag/text/aria-label
   - whether focus-visible styling appears
   - enabled/disabled state
10. Send exactly ONE standard activation:
   - first choice: Enter key down/up
   - if the control is semantically a button and Enter is not its documented activation key, use Space down/up instead
   - do not test both in the same prepared run
11. Do not send a mouse click afterward and do not retry.
12. Observe Flow for up to 120 seconds.

## Instrumentation

Keep the existing event logger active and record relevant events around the Generate control:
- keydown
- keyup
- focus
- blur
- click (if keyboard activation synthesizes one)
- `event.isTrusted`
- key/code
- target
- activeElement

Also record Flow outcome:
- generation progress appeared?
- unusual-activity error?
- generic failed card?
- new playable video?
- if playable: resolution/FPS/duration

## Success criterion

Success means the keyboard UI path produces one new playable Clip 1 without a manual noVNC mouse click.

If successful, STOP after Clip 1. Do not proceed to Clip 2/3 in this diagnostic run.

If unsuccessful, report the exact browser event chain and Flow result. Do not try to imitate human timing/trajectory or otherwise evade platform controls.

## Reporting

Update and push:
- `HERMES_TEST_REPORT.md`
- `HERMES_STATUS.md`
- `GENERATE_EVENT_COMPARISON.md` if present

Do not commit videos, screenshots, cookies, secrets, caches, or generated media.
Do not merge `main` or PR #1.
