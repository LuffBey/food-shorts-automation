# Hermes — Implement and Validate Omni 1.1 Scene Extension

Branch: `fix/character-consistency`

## Read first

1. `ARCHITECTURE.md`
2. `FLOW_AGENT_OMNI_SCENE_EXTENSION_PROMPT.md`
3. `CODEX_HANDOVER.md`

These are the active instructions. The old independent 3×10, continuation-frame and concat workflows are historical fallbacks only.

## Goal

Replace the current independent-generation pipeline with:

1. one approved 10-second Gemini Omni 1.1 Flash base clip;
2. scene extension 1 using the accepted video itself as context;
3. scene extension 2 continuing the accepted parent chain;
4. QC after every stage;
5. final assembly determined by whether Flow returns cumulative or delta segments.

## Existing Flow target

- Project ID: `0bd8a011-4555-49c2-adc8-ba87b68466a9`
- Character ID: `b068cab7-76d4-49ec-9066-9259c139d46a`
- Character name: `Creator`
- Model: Gemini Omni 1.1 Flash
- Format: Video, 9:16, 10 seconds, one output

Confirm these in the live UI; do not assume stale selectors or labels.

## Implementation requirements

1. Preserve existing working support for real tokenized `@Creator` insertion and verification.
2. Add a scene-extension operation that uses the accepted generated video’s visible `Add to prompt`/continuation control.
3. Before submitting, verify that a video reference/entity is actually present in the composer. A still frame, filename or plain text mention is insufficient.
4. Record stage lineage: `base -> ext1 -> ext2`, including asset IDs/URLs or stable UI identifiers when available.
5. Introduce explicit stage states: `GENERATED`, `QC_PASS`, `QC_FAIL`, `ACCEPTED_PARENT`, `DISCARDED_CHILD`.
6. Only an `ACCEPTED_PARENT` may be extended.
7. Determine whether each result is cumulative or continuation-only by measuring its real duration and inspecting its opening frames.
8. Add QC sampling at 0.5-second intervals, with denser checks around extension boundaries.
9. Apply the retry policy from `ARCHITECTURE.md`; maximum three attempts from the same accepted parent.
10. Do not automatically invoke legacy `execute_3x10s_flow.py`, continuation-frame generation or match-cut concat when Omni extension is unavailable. Stop and report the blocker.

## Safe interaction requirement

Use normal supported Flow UI behavior. Do not attempt stealth, fingerprint changes, proxy/VPN tricks, CAPTCHA handling, anti-bot evasion or security-control bypass. A normal human-in-the-loop Generate/Continue click is acceptable when required; report it honestly.

## Validation run

Use the default fried-chicken episode in `FLOW_AGENT_OMNI_SCENE_EXTENSION_PROMPT.md`.

Stop after the first complete base→ext1→ext2 validation chain. Do not upload to YouTube.

For each stage verify:

- same Creator face, hair and facial hair;
- same black shirt and burnt-orange background;
- same walnut table, plate and white bowl;
- correct food count, sauce state and bite count;
- same active hand and plausible grip;
- no dialogue, voice, speech-like lip movement or text;
- actual resolution, FPS and duration.

## Deliverables

- implementation changes for the new pipeline;
- `HERMES_TEST_REPORT.md` updated with timestamped evidence;
- `HERMES_STATUS.md` updated with current state;
- any new selector/UI findings documented without secrets;
- committed and pushed changes on `fix/character-consistency`.

Do not commit generated media, frames, screenshots, cookies, tokens or browser-profile data. Do not merge `main` or upload/publish content.
