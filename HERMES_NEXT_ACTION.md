# Hermes — Next Action: Use the User-Created Creator Asset

Branch: `fix/character-consistency`

## Exact Flow target

The user manually created the reusable character asset in this exact Flow project:

- Project ID: `0bd8a011-4555-49c2-adc8-ba87b68466a9`
- Character ID: `b068cab7-76d4-49ec-9066-9259c139d46a`
- Character name: `Creator`
- Character URL: `https://labs.google/fx/tr/tools/flow/project/0bd8a011-4555-49c2-adc8-ba87b68466a9/character/b068cab7-76d4-49ec-9066-9259c139d46a`

Do NOT use the old project `01d7d238-5897-4495-bf29-3c43dea8ce9f` for this test.

## Goal

Open the exact project above in the authenticated remote Chromium session, verify the existing `Creator` asset, insert a real `@Creator` entity chip, then run the 3x10s identity-stable food-ASMR pipeline.

## Required procedure

1. Pull the latest `fix/character-consistency` branch.
2. Connect to the existing authenticated Chromium session on CDP port 9222.
3. Navigate the remote browser to:
   `https://labs.google/fx/tr/tools/flow/project/0bd8a011-4555-49c2-adc8-ba87b68466a9/character/b068cab7-76d4-49ec-9066-9259c139d46a`
4. Verify that the active project ID is exactly `0bd8a011-4555-49c2-adc8-ba87b68466a9`.
5. Verify that the character with ID `b068cab7-76d4-49ec-9066-9259c139d46a` exists and is named `Creator`.
6. Navigate to the generation/composer view for THIS SAME project.
7. Type `@Creator` and select the real autocomplete/entity suggestion.
8. Verify that a real tokenized `Creator` chip/entity is present. Plain text `@Creator` is not sufficient.
9. If the character URL opens but the remote session is logged into the wrong Google account or lacks access, STOP and report `account/session mismatch` explicitly. Do not fall back to the old project.

## Generation test

Only after the real `@Creator` chip is verified:

### Clip 1
- `@Creator`
- crispy fried chicken tender hook
- pick up food + deep glossy sauce dip
- natural eager expression, subtle smile

### Clip 2
- same `@Creator`
- Start Frame = clean 8–9s frame from Clip 1
- bite + crunchy texture reveal + subtle satisfied reaction

### Clip 3
- same `@Creator`
- Start Frame = clean 8–9s frame from Clip 2
- glaze/final bite + small approving smile/nod

Every clip must preserve:
- same face/facial geometry
- same hairstyle/facial hair
- same age/skin tone
- same simple dark wardrobe
- same table/plate/background/lighting/camera distance

If a clip visibly drifts in identity, reject/regenerate that clip and do not use its continuation frame.

## Fallback policy

Primary path is the real `Creator` Character Asset.

Do not use Ingredients fallback unless the character exists but Flow temporarily cannot insert the entity chip after you have diagnosed the exact UI/tokenization failure. If fallback is used, clearly state it in the report.

## Reporting

Update and push:
- `HERMES_TEST_REPORT.md`
- `HERMES_STATUS.md`

Report:
- active Flow project ID
- detected Character ID/name
- whether Creator asset was accessible
- whether real `@Creator` chip was inserted for Clip 1/2/3
- whether Clip 1/2/3 generated
- Clip 1→2 identity result
- Clip 2→3 identity result
- face/hair/wardrobe/scene drift
- any regeneration attempts
- fallback usage
- final output path
- exact blocker if unsuccessful

Commit/push only code and markdown reports to `fix/character-consistency`.
Do not commit videos, images, screenshots, cookies, secrets, or caches.
Do not merge `main` or PR #1.
