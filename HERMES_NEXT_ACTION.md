# Hermes — Next Action: Run the v6 Identity-Stable Flow Pipeline

Branch: `fix/character-consistency`
Required commit: `126b3c5e4721e81f54098d48510ccc12bc0c9ffe`

## Goal

Run one real 3x10s Google Flow / Omni 1.1 Flash test using the updated Ingredients/References pipeline.

The previous Character-creation workflow is no longer the primary path. Do **not** block on creating a Flow Character asset first.

## What changed

- Use **Video > Ingredients/References** with Omni Flash 1.1.
- Every clip receives the same canonical face image as ingredient #1.
- Clip 1 receives the initial/base scene image as ingredient #2 when available.
- Clip 2 receives clip 1's final frame as ingredient #2.
- Clip 3 receives clip 2's final frame as ingredient #2.
- File uploads now dispatch real `input` and `change` events after CDP file assignment.
- If Flow still does not ingest the file, the engine falls back to a synthetic drag/drop upload onto the prompt area.
- Generation fails fast if the Flow application does not visibly accept the ingredient. Do not continue with text-only generation.

## Run procedure

1. Pull the branch and verify HEAD is:
   `126b3c5e4721e81f54098d48510ccc12bc0c9ffe`

2. Keep the existing authenticated Chromium / Flow session running on CDP port 9222.

3. Ensure a valid face reference exists. Preferred path:
   `/root/hermes-projects/food-discovery-automation/creator_face_ref.jpg`

   If the dedicated file is absent, the pipeline can fall back to the supplied base image, but a clean close/medium character reference is strongly preferred.

4. Run a single 3x10s smoke test. Use the same performer in all three clips.

5. Watch the logs for these success messages for **every** ingredient:
   - `Flow application attachment accepted`
   or
   - `Drag/drop attachment accepted`

   A log that only says `File input events dispatched` is NOT sufficient proof of ingestion.

6. Confirm Omni Flash 1.1, Ingredients/References, 9:16, x1, 10s are active before generation.

7. Do not merge PR #1 yet.

## If it fails

Write/update `HERMES_TEST_REPORT.md` with:

- exact UI text around the model/mode controls
- all visible buttons and aria-labels around the prompt box
- all `input[type=file]` metadata
- whether direct input ingestion succeeded
- whether drag/drop ingestion succeeded
- exact exception/stack trace
- screenshot paths (do not commit generated media)

If ingredient upload succeeds but Generate fails, capture the visible prompt-area DOM text and generate button label/state.

If all 3 clips generate, report:

- Clip 1→2 same identity? yes/no/uncertain
- Clip 2→3 same identity? yes/no/uncertain
- face drift
- hairstyle drift
- wardrobe drift
- background/table drift
- final output path

Commit only code/report changes; do not commit generated videos or reference images.
