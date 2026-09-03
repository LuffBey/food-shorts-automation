# Hermes Master Instruction — Omni 1.1 Food Shorts Scene Extension

Read `ARCHITECTURE.md` completely and treat it as the active system design. `FLOW_AGENT_EDITORIAL_3SHOT_PROMPT.md`, continuation-frame scripts and historical test reports are reference material only; they do not override this instruction.

## Mission

Using Google Flow Agent and Gemini Omni 1.1 Flash, produce one globally understandable, photorealistic, appetizing vertical food short of approximately 30 seconds.

Create one approved 10-second base video, then use the accepted video itself as context and continue the same scene twice with Omni 1.1 scene extension. Do not create clips 2 and 3 as independent text-to-video generations. Do not use extracted still frames as the primary continuity mechanism.

Use only normal, supported Google Flow controls. Do not bypass safety, authentication, quota, anti-abuse or automation controls.

## Episode variables

Fill these before starting:

- `FOOD`
- `SAUCE`
- `HERO_TEXTURE`
- `PRIMARY_ACTION`
- `TEXTURE_SOUND`
- `PAYOFF`

Default validation episode:

- `FOOD = extra-crispy golden fried chicken tender`
- `SAUCE = thick glossy dark amber-red barbecue sauce`
- `HERO_TEXTURE = crisp golden crust and juicy fibrous white interior`
- `PRIMARY_ACTION = slow dip and lift`
- `TEXTURE_SOUND = one clean realistic crunch`
- `PAYOFF = one-bitten cross-section presented close to camera`

## Immutable continuity contract

Preserve throughout the complete chain:

- the exact same licensed `@Creator` identity and real tokenized entity chip;
- the exact same face, age, hair, facial hair and body proportions;
- plain matte black crew-neck shirt;
- seamless matte burnt-orange studio background;
- medium-dark walnut table with long natural grain;
- the same plate, the same shallow glossy white ceramic sauce bowl and the same food piece;
- the same camera side, lens family, lighting direction and color grade;
- physically correct hands, grip, food state, sauce state, crumbs and bite count.

No kitchen, décor, signage, text, logos, subtitles, new props, prop removal, plate movement, food duplication, hand teleportation, wardrobe change, location change or unexplained cut.

Creator never speaks. No dialogue, voice-over, whisper, humming, intelligible vocalization, speech-like lip movement or lip-sync in any language. No “mmm.” Reaction is conveyed only with the eyes, a subtle closed-mouth smile or a small nod. Allowed sound is food ASMR and stable room tone.

## Before generation

1. Confirm Video mode, Gemini Omni 1.1 Flash, 9:16, 10 seconds and one output.
2. Create or select the approved `@BrandSet_Master` and food reference.
3. Bind the actual `@Creator` entity/chip and verify the Slate/entity node; plain text is not accepted.
4. Write a continuity ledger for S0–S3 as specified in `ARCHITECTURE.md`.
5. Confirm the plate, bowl and full food piece are visible in S0.

## Base generation — 0–10 seconds

Use this structure, substituting the episode variables:

```text
Create a 10-second vertical 9:16 photorealistic premium food-commercial video using the bound @Creator and approved brand/food references.

Preserve the exact approved Creator identity, matte black crew-neck shirt, seamless burnt-orange studio background, medium-dark walnut table, single plate, single shallow glossy white sauce bowl, camera-left soft key light and fixed front three-quarter medium close framing.

The FOOD is already clearly visible in the first frame. The Creator holds the one whole unbitten FOOD in the right hand above the plate, slowly dips only its lower quarter into the SAUCE, then lifts it. The sauce is thick, glossy and physically plausible. End in a calm readable pose: the same unbitten FOOD remains in the right hand 20–25 cm from the mouth, lower quarter sauced, while the face, plate and bowl remain visible.

No speech, human vocalization, speech-like lip movement, text, subtitles, logo, music, camera cut, location change, new object, disappearing object, second food piece or bite. Natural dip/crackle sound and quiet stable room tone only.
```

Run QC gate A. If it fails, regenerate from the same references. Do not proceed.

## Scene extension 1 — 10–20 seconds

Use the accepted base video’s visible `Add to prompt`/scene-continuation action. Verify that the video, not merely a still image or filename, is attached as context. Then use:

```text
Continue directly from the accepted preceding video in the same scene and same shot family. Preserve every visible identity, wardrobe, background, table, camera, lighting and prop detail exactly. Preserve the same right-hand grip, the same plate and bowl positions, and the same single FOOD with only its lower quarter covered in the same SAUCE.

The Creator smoothly lifts that same FOOD from its current position, takes exactly one medium bite from the upper end, makes one clean realistic crunch, then performs two or three brief natural closed-mouth chewing movements. End in a calm readable pose with the same one-bitten FOOD still in the right hand and its HERO_TEXTURE cross-section facing the camera. The plate and bowl remain visible and unchanged.

No fresh scene, cut, time jump, camera-side change, new food, repaired bite, second bite, prop movement/removal, speech, “mmm,” vocal reaction, speech-like lips, text, subtitles, logo or music.
```

Run QC gate B, concentrating on the first second, bite moment and final second. If it fails, discard it and retry from the accepted base video. Never use the failed extension as a parent.

## Scene extension 2 — 20–30 seconds

Continue from the accepted extension-1 result in the same interaction/parent chain. Use:

```text
Continue directly from the accepted preceding video. Preserve the exact same Creator, face, hair, facial hair, black shirt, burnt-orange background, walnut table, plate, white sauce bowl, camera, lens, lighting and color grade. Preserve the same single FOOD with exactly one existing bite and the same sauce coverage, held in the same right hand.

Without taking another bite, the Creator slowly rotates the same one-bitten FOOD just enough to reveal the HERO_TEXTURE and PAYOFF clearly. Finish with a subtle closed-mouth smile and one small natural nod while holding the food in a clean hero composition. The plate and bowl stay visible and stationary through the final frame.

No second bite, food regrowth, duplication, hand switch, new or disappearing prop, background change, camera jump, dialogue, vocalization, speech-like lips, text, subtitle, logo or music.
```

Run QC gate C. If it fails, discard it and retry from the accepted extension-1 parent.

## Assembly

Inspect actual output durations:

- If Flow returns one cumulative approximately 30-second asset, use that accepted asset.
- If Flow returns continuation segments, assemble only the accepted base → extension 1 → extension 2 lineage.
- Remove only genuine duplicated boundary frames/audio.
- Do not use crossfades to hide a visual continuity failure.
- Normalize to a clean 24–30 seconds, vertical 9:16. Preserve the native look unless a restrained global correction is demonstrably needed.

## Mandatory rejection rules

Reject any stage containing identity drift, wardrobe drift, background change, missing/moved plate or bowl, changed food count/category, impossible bite state, incorrect hand/grip, malformed anatomy, more than one bite, dialogue, speech-like lips, generated text or unappetizing food physics.

Use at most three attempts per stage. After three failures, stop and report the repeated defect with timestamps. Do not silently switch to the old independent 3×10 workflow.

## Required report

Update `HERMES_STATUS.md` and create/update the run report with:

- Flow project, model and settings;
- base and extension asset lineage;
- continuity ledger S0–S3;
- actual resolution, FPS and duration;
- frame-based checks at least every 0.5 seconds and within ±1 second of boundaries;
- timestamped Creator, background, table, plate, bowl, food, bite, hand, speech/lips and text results;
- retries and exact rejection reasons;
- cumulative-versus-segment output behavior;
- final path, duration, size and PASS/FAIL.

Do not commit generated video, screenshots, extracted frames, cookies, credentials or temporary media. Commit only prompt, architecture, implementation code and text reports. Do not upload to YouTube until final QC passes and publishing is separately requested.

