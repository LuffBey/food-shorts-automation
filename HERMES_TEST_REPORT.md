# HERMES_TEST_REPORT — Flow Character Consistency

**Date:** 2026-09-03
**Branch:** `fix/character-consistency`
**Base commit under test:** `4e7e60b` (`docs: run pipeline bootstrapped Creator asset`)

## Requested test

Run a real 3 × 10-second Google Flow food-ASMR sequence using a reusable `Creator` character asset and a verified, real `@Creator` entity chip in every clip:

1. crispy chicken tender hook and deep dip;
2. same creator, continuation frame, bite/texture reaction;
3. same creator, continuation frame, glaze/final bite/subtle approval.

No Ingredients/reference fallback was permitted for this run because the requested primary mechanism was the real `@Creator` chip.

## Live Flow session evidence

- Connected to the authenticated Chromium CDP session on port `9222`.
- Current live project: `01d7d238-5897-4495-bf29-3c43dea8ce9f`.
- Project generation view and Characters view both loaded successfully after a browser reload.
- The Characters view showed the new-character form (`Yeni karakter`) but no visible `Creator` asset.
- Project initial data was fetched from Flow's authenticated `flow.projectInitialData` endpoint. Its serialized response contained no project character named `Creator`.

## Real `@Creator` chip verification

On the live project generation editor:

- Literal `@Creator` text was entered into the real Flow prompt editor.
- No autocomplete/menu/entity candidate named `Creator` appeared after waiting for UI update.
- Therefore no selectable real entity chip existed and the editor could not be verified as containing a tokenized `@Creator` chip.
- Literal text was deliberately **not** treated as identity lock.

## Result matrix

| Requirement | Result |
|---|---|
| `Creator` asset detected in current live project | **No** |
| Real `@Creator` chip inserted — Clip 1 | **No** |
| Real `@Creator` chip inserted — Clip 2 | **No** |
| Real `@Creator` chip inserted — Clip 3 | **No** |
| Clip 1 generated | **No** |
| Clip 2 generated | **No** |
| Clip 3 generated | **No** |
| Clip 1 → 2 same identity | **Uncertain / not evaluable** |
| Clip 2 → 3 same identity | **Uncertain / not evaluable** |
| Face, hairstyle, wardrobe, or scene drift | **Not evaluable: no new clips** |
| Clip regenerated due to identity failure | **No: generation never began** |
| Ingredients fallback used | **No** |
| Final output path | **None** |

## Exact blocker

The manually created `Creator` asset is not available in the current authenticated Flow project (`01d7d238-5897-4495-bf29-3c43dea8ce9f`). Live DOM and authenticated project data both lack it, and Flow offers no `Creator` autocomplete candidate. This is a project/session scope mismatch rather than a plain-text insertion issue.

The automation correctly stopped before any video generation to avoid falsely claiming an identity lock. To run the requested 3×10s test, open the Flow project where the manually created asset is actually present, or create/reuse `Creator` in the current project and then rerun.

## Code verification

- `python3 -m py_compile food_discovery_engine.py` passed before live verification.
- No generated videos, frames, screenshots, references, cookies, or secrets were staged or committed.
