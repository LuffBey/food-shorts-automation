# HERMES_TEST_REPORT — Flow Character Consistency

**Date:** 2026-09-03
**Branch:** `fix/character-consistency`
**Commit under test:** pending commit for this implementation

## Scope

Implemented and smoke-tested the Character Asset-first architecture for the Food Discovery three-clip (3 × 10 second) ASMR Flow pipeline. The target concept is crispy fried chicken tenders with glossy dipping sauce.

## Code changes

- Replaced `food_discovery_engine.py` with a maintainable CDP implementation.
- Added `CharacterAssetManager` that opens Flow Characters, searches for a reusable `Creator` asset, reuses it if found, and otherwise attempts character creation using up to two local reference images.
- Added a reactive upload path: `DOM.setFileInputFiles`, followed by bubbling `input`, `change`, `dragenter`, `dragover`, and `drop` events.
- Added verified `@Creator` insertion: it opens autocomplete, selects a visible Creator candidate, and requires a non-plain-text token/chip node. It does **not** silently claim identity lock when only literal text exists.
- Added all three persistent locks to every clip prompt: identity, scene, and negative constraints.
- Added per-clip failure stopping, start-frame attachment checks, and `8s`/`9s` continuation-frame extraction so a failed clip cannot be propagated into the chain.
- Preserved CDP Flow connection, browser-side video download, FFmpeg continuity-frame extraction, normalization, and concat output path conventions.

## Live Flow evidence

A real authenticated Flow project was connected through Chromium CDP port 9222:

`https://labs.google/fx/tr/tools/flow/project/01d7d238-5897-4495-bf29-3c43dea8ce9f/characters`

Character Asset creation was attempted in the live **Yeni karakter** screen using:

`/root/hermes-projects/food-discovery-automation/creator_face_ref.jpg`

### Character Asset creation

**Result: not successful.**

- CDP attachment did assign the file: `input.files = ['creator_face_ref.jpg']`.
- The Flow application did not render a visible attachment name or preview after the reactive event dispatch.
- The manager therefore returned `blocked-upload-not-ingested` rather than submitting a character generation with unverified input.
- No reusable `Creator` asset was found in the project during the check.

### `@Creator` chip insertion

**Result: not successful / not attempted past asset gate.**

Because no reusable `Creator` asset existed and Flow did not ingest the creation upload, there was no valid autocomplete candidate to select. The implementation intentionally fails the chip verification rather than treating plain `@Creator` text as a character token.

### Three-clip production test

**Result: not run to generation.**

The workflow was stopped before Clip 1 because the required primary identity-lock asset could not be created or reused. No generated videos, screenshots, extracted frames, cache, secrets, or temporary media were committed.

### Face stability

**Result: not evaluable.**

No new three-clip sequence was produced in this run, so Clip 1→2 and Clip 2→3 face stability cannot be truthfully asserted.

## Verification performed

- `python3 -m py_compile food_discovery_engine.py` — passed.
- Live CDP connection to authenticated Google Flow Characters page — passed.
- Live attachment-state inspection (`input.files`) — passed at browser DOM level.
- Live Flow application ingestion / preview verification — failed, correctly blocking creation.
- Prompt and continuation-frame structural smoke test — passed.

## Exact diagnosis

The remaining blocker is Flow application-level ingestion of the reference image in the Character creation UI. CDP has set the native file input, but Flow has not accepted it into its React/application state. This is distinct from a missing authentication or missing file-input issue.
