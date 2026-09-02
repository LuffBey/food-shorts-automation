# Hermes — Next Action: Run the Character-Asset Identity Pipeline

Branch: `fix/character-consistency`

## User bootstrap completed

The user has manually created a reusable Google Flow Character asset named exactly:

`Creator`

Do not attempt to create the character asset again unless it is genuinely missing from the authenticated Flow project.

## Goal

Run one real 3x10s Google Flow food-ASMR test using `@Creator` as the primary identity lock.

The test is successful only if the same creator identity remains stable across all three clips.

## Required flow

1. Pull `fix/character-consistency` and use the current HEAD.
2. Connect to the existing authenticated Flow session on CDP port 9222.
3. Open the generation UI and verify the reusable character asset `Creator` is visible/available.
4. For EVERY clip, insert `@Creator` and select the real autocomplete/entity chip. Plain text `@Creator` is not sufficient.
5. Verify the resulting editor contains a real Creator token/chip before generation.
6. Use the same scene/wardrobe/lighting constraints in all clips.
7. Clip 1: hook + pick up food + deep dip.
8. Clip 2: same `@Creator` + clean continuation frame from Clip 1 + bite/texture reveal/reaction.
9. Clip 3: same `@Creator` + clean continuation frame from Clip 2 + glaze/final bite/subtle approval.
10. Prefer a clean frame around 8–9 seconds if the literal final frame is blurred, occluded, malformed, or off-frame.
11. If a clip visibly changes identity, reject/regenerate that clip and do not propagate its continuation frame.

## Identity requirements

Every clip should preserve:
- same face and facial geometry
- same hair and facial hair
- same apparent age and skin tone
- same black/simple wardrobe
- same body proportions
- same table, plate, background, camera distance and lighting

Character behavior should remain natural: relaxed, genuinely hungry, small natural smiles, subtle approving reactions, no exaggerated acting.

## Fallback

If the real `@Creator` chip cannot be inserted even though the asset exists, diagnose the autocomplete/tokenization UI and fix that code first.

Only if Character asset reuse is temporarily impossible may you test the existing Ingredients/References fallback. Clearly report that fallback was used. Do not silently treat it as equivalent to `@Creator`.

## Test concept

Use a visually strong ASMR food concept such as crispy fried chicken tenders with glossy dipping sauce.

Target output:
- 3 x 10 second clips
- vertical 9:16
- attention-grabbing first 2 seconds
- satisfying food texture and bite moments
- subtle, natural creator reactions
- final concatenated 20–30 second short

## Required report updates

Overwrite/update both:
- `HERMES_TEST_REPORT.md`
- `HERMES_STATUS.md`

Report explicitly:
- current branch and commit SHA
- `Creator` asset detected: yes/no
- real `@Creator` chip inserted for Clip 1/2/3: yes/no
- Clip 1 generated: yes/no
- Clip 2 generated: yes/no
- Clip 3 generated: yes/no
- Clip 1→2 same identity: yes/no/uncertain
- Clip 2→3 same identity: yes/no/uncertain
- face drift
- hairstyle drift
- wardrobe drift
- scene drift
- whether any clip was regenerated due to identity failure
- whether Ingredients fallback was used
- final output path if successful
- exact blocker and DOM/UI evidence if unsuccessful

## Git rules

Commit/push only code and markdown reports to `fix/character-consistency`.
Do not commit generated videos, reference images, screenshots, cache, cookies or secrets.
Do not merge `main`.
Do not merge PR #1.
