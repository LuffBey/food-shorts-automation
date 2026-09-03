# Food Shorts Automation — Omni 1.1 Scene-Extension Architecture

Status: active architecture as of 2026-09-03.

This document supersedes the independent `3 x 10s + continuation-frame + concat` design.

## 1. Product goal

Produce a genuinely appetizing, globally understandable 24–30 second vertical food short with:

- one stable Creator identity;
- one recognizable channel set;
- physically coherent food and props;
- no spoken language or speech-like lip movement;
- a clear sensory arc: hook, bite/payoff, texture/final reaction;
- safe, normal use of Google Flow and its supported controls.

The system must prefer a shorter clean result over a longer visibly broken result.

## 2. Core architectural decision

Generate one approved 10-second base clip with Gemini Omni 1.1 Flash, then continue that accepted video twice through Omni scene extension. Do not generate clips 2 and 3 as fresh text-to-video requests.

```text
Content brief + channel bible
             |
             v
Brand/Creator/food references
             |
             v
Omni 1.1 Flash base clip (0–10s)
             |
        QC gate A -- FAIL --> regenerate from same references
             |
             v
Add accepted video to prompt / preserve interaction context
             |
             v
Scene extension 1 (10–20s)
             |
        QC gate B -- FAIL --> discard child; retry from base clip
             |
             v
Add accepted extended result to prompt / continue same chain
             |
             v
Scene extension 2 (20–30s)
             |
        QC gate C -- FAIL --> discard child; retry from extension 1
             |
             v
Duration normalization + audio finishing + final QC
             |
             v
YouTube upload (separate publish stage)
```

Never extend a failed result. The parent of every generation must be the most recent accepted result.

## 3. Why this replaces the old design

Independent generations reset too much hidden scene state. A saved last frame can constrain one instant, but it does not reliably carry the preceding motion, object history, hand usage, bite count, or narrative intent.

Omni 1.1 scene extension is intended to retain prior interaction/video context and can extend a scene up to 40 seconds. Official references:

- https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/
- https://blog.google/innovation-and-ai/models-and-research/google-labs/new-creative-controls-google-flow/
- https://support.google.com/flow/answer/16352836?hl=en

The old editorial three-shot workflow remains a manually selected fallback only. Hermes must not silently fall back to it when scene extension is missing or blocked.

## 4. Fixed channel identity

These attributes are immutable across every episode and every extension:

- the licensed `@Creator` entity/chip;
- plain matte black crew-neck shirt, no logo or pattern;
- seamless matte burnt-orange background near `#D9682E`;
- subtle center glow near `#E98745`;
- medium-dark walnut table with long natural grain;
- one shallow glossy white ceramic sauce bowl;
- soft key light from camera-left;
- natural skin and food color, premium photorealistic food-commercial look;
- no kitchen, cabinets, shelves, windows, plants, wall art, signage or decorative clutter.

Color codes are used to create/approve the master set. Extension prompts must preserve the existing set, not ask the model to redesign it.

## 5. Per-video continuity ledger

Before generation, Hermes must create a machine-readable and human-readable ledger containing:

- Creator identity, wardrobe and seat/body position;
- camera height, angle, lens feel, crop and movement allowance;
- background, table, bowl and plate descriptions and positions;
- food type, number of pieces and exact food state;
- active hand and grip;
- sauce level and coverage;
- bite count;
- crumbs, drips and other irreversible changes;
- permitted action for the next segment;
- forbidden changes.

Example state progression:

| State | Food | Hand/position | Bite count | Required visible props |
|---|---|---|---:|---|
| S0 | whole, dry tender | right hand above plate | 0 | plate + bowl |
| S1 | same tender, lower 25% sauced | right hand, 20–25 cm from mouth | 0 | plate + bowl |
| S2 | same tender with one top bite | right hand, cross-section toward camera | 1 | plate + bowl |
| S3 | same one-bitten tender rotated slightly | right hand, final hero pose | 1 | plate + bowl |

The next prompt may advance state only from S0→S1→S2→S3. It may never reverse a bite, refill sauce, switch hands without showing it, duplicate food, move the plate or remove a prop.

## 6. Narrative structure

### Base clip, 0–10 seconds — crave hook

- Food is already visible and moving in the first frame.
- Show the whole unbitten food briefly.
- Perform one slow dip and lift.
- End in a low-motion, readable S1 pose with face, hand, plate and bowl visible.
- Do not end during a bite, whip-pan, occlusion or with the plate outside frame.

### Extension 1, 10–20 seconds — sensory payoff

- Continue directly from S1.
- Lift the same piece to the mouth and take exactly one medium bite.
- Use one clean, realistic crunch.
- Chew briefly with closed mouth.
- End in S2 with the one-bitten cross-section visible and all anchor props still present.

### Extension 2, 20–30 seconds — texture reveal and signature

- Continue directly from S2.
- No second bite.
- Rotate the same piece slightly to reveal texture, juice or cheese pull appropriate to the food.
- Finish with a subtle closed-mouth smile or small nod; thumbs-up is optional, not mandatory.
- End in S3 with a clean hero composition.

This is one continuity chain, but the visual rhythm may include model-generated motivated reframing. Do not demand an elaborate 30-second unbroken camera move.

## 7. Prompt layering

Every request has three layers:

1. `IMMUTABLE CONTINUITY CONTRACT`: identity, wardrobe, set, camera family, props, current food state, silence.
2. `ONE NEW ACTION`: only the action allowed in the next segment.
3. `END STATE`: an explicit stable pose used as the next QC boundary.

Extension prompts must be shorter than the base prompt. Re-describing the entire scene with new adjectives increases the chance of redesign. Use preservation language and describe only the state delta.

## 8. Global audio/language contract

- No dialogue, narration, whispering, humming, words, exclamations or intelligible human voice in any language.
- No speech-like lip movement or lip-sync.
- Mouth motion is allowed only for the single bite and brief closed-mouth chewing.
- No subtitles, captions, labels, logos, watermarks or generated screen text.
- Allowed audio: natural dip, sizzle, crackle, one crunch and stable room tone.
- If unwanted voice exists without speech-like mouth movement, replace the generated audio in post.
- If speech-like mouth movement exists, reject the video; muting alone is not sufficient.

## 9. Flow execution contract

Hermes must use normal supported Flow controls:

1. Open the approved Flow project.
2. Select Video, Gemini Omni 1.1 Flash, 9:16, 10 seconds, one output. Draft at 360p when available; render accepted generations at 720p or upscale through supported controls.
3. Bind the real tokenized `@Creator` entity and approved references. Plain text `@Creator` is not sufficient.
4. Generate the base clip.
5. After QC PASS, use the accepted video’s visible `Add to prompt`/scene-continuation control. The video itself must be present as context before submitting the continuation instruction.
6. Generate extension 1 from the accepted base.
7. After QC PASS, continue from the accepted extension result/same interaction chain and generate extension 2.
8. Record parent/child asset IDs or stable UI identifiers where available.

Do not use the legacy Veo-only Extend path when the intended operation is Omni 1.1 contextual scene extension. Do not bypass sign-in, quotas, anti-abuse controls, CAPTCHA or other platform safeguards. If a normal UI operation requires a human click, pause at that step and report it.

## 10. Output-shape detection

Flow interfaces may expose an extension either as a cumulative video or as a new continuation segment. Hermes must inspect durations instead of assuming:

- If the final accepted asset is approximately 30 seconds and contains the full sequence, use it directly.
- If Flow returns three approximately 10-second segments, concatenate only the accepted parent-chain segments in order.
- Detect and trim any duplicated boundary frames/audio; do not hide a semantic jump with a long crossfade.
- Normalize to 24–30 seconds only after content QC.
- Do not apply a blind saturation boost. Use one restrained final grade only if scopes/visual comparison show it is needed.

## 11. QC gates

Inspect at least every 0.5 seconds and more densely within ±1 second of each extension boundary.

Hard-fail conditions:

- Creator face/age/hair/facial-hair drift;
- wardrobe change;
- orange background, table, plate or bowl changes/disappears;
- food changes category, size, count, color or returns to an earlier bite state;
- hand/grip teleportation, extra fingers or impossible contact;
- unexplained camera/location cut;
- speech, speech-like lips or generated text;
- more than one bite;
- unappetizing anatomy, chewing or food physics.

Soft issues may be repaired only in post when they do not alter story state: minor exposure, audio level or a few duplicated boundary frames.

Retry policy:

- maximum three attempts per stage by default;
- retry from the same accepted parent;
- never extend the failed child;
- do not change multiple variables at once;
- after three failures, stop and report the exact recurring error with timestamps.

## 12. Post-production and publishing boundary

Post-production may:

- trim start/end dead time;
- remove duplicated extension overlap;
- normalize resolution/FPS/audio;
- add a continuous licensed/original room-tone bed;
- align one crunch to the visible bite;
- create the final 9:16 deliverable.

Post-production must not be used to conceal identity, prop or food-state drift.

YouTube upload remains a separate stage and begins only after final QC PASS. Apply the platform’s appropriate altered/synthetic-content disclosure. Generated video, frames, cookies, tokens and temporary media stay out of Git.

## 13. Required run report

For each run record:

- model, aspect ratio, requested and actual duration, resolution and FPS;
- base/extension parentage;
- retry count and prompt revision per stage;
- S0/S1/S2/S3 ledger values;
- timestamped identity, set, prop, food-state, hand and speech checks;
- whether the final asset was cumulative or segment-based;
- any boundary trim and audio replacement;
- PASS/FAIL decision for each gate;
- final path, duration and file size;
- blocker, if any.

