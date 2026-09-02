# HERMES_TEST_REPORT — Flow Character Consistency

**Date:** 2026-09-02
**Branch:** `fix/character-consistency`
**Base commit under test:** `0a999e1ff949a2a6a1a782b010138ea98ef07bf4` (`fix: preserve character identity across 10s Flow clips`)

## Scope

Validate the character-reference and continuity upload path against a real Google Flow session, then produce three 10-second clips only if the Flow UI accepts the reference and generation can be verified.

## Environment and access evidence

- A real authenticated Google Flow page was opened at `https://labs.google/fx/tr/tools/flow` through Chromium CDP on port `9222`.
- A new Flow project was created: `01d7d238-5897-4495-bf29-3c43dea8ce9f`.
- The Flow **Characters → New character** screen was reached and exposed one live `input[type=file]` with `accept="image/*"`, `multiple=true`, and `disabled=false`.
- `v4_frame_1.jpg` was copied locally as `creator_face_ref.jpg` solely as an uncommitted test fixture. Visual review confirms it is a close facial reference (short dark hair, trimmed stubble, dark crew-neck), but it is not committed to this repository.

## Live upload probe

The CDP call `DOM.setFileInputFiles` assigned `creator_face_ref.jpg` to the live Flow file input. The browser-side state immediately verified:

```text
input.files = [{ name: "creator_face_ref.jpg", size: 127320, type: "image/jpeg" }]
```

However, the Flow UI did **not** render a media attachment/preview or filename, and `document.body.innerText` did not contain `creator_face_ref.jpg`. The UI’s visible submit/create button remained enabled but did not initiate a character-generation job after both CDP mouse and DOM `.click()` attempts. No user-visible policy rejection, explicit validation error, or loading/progress state was present.

**Result:** CDP-level file assignment passed; Flow application-level attachment ingestion was not verified.

## Code fixes made during the live probe

Two small reliability fixes were made in `food_discovery_engine.py`:

1. `_verify_upload()` now checks `input.files` in addition to filename/preview DOM text. This correctly distinguishes a successful CDP assignment from a rendered Flow attachment.
2. `set_prompt()` now programmatically focuses the Slate editor and uses `Input.insertText`; it also sends a complete raw Ctrl+A / Backspace sequence. The original coordinate-click/key-event path left the Slate editor unfocused in this headless Flow session, so prompts were not reliably replaced.

Validation run:

```text
python3 -m py_compile food_discovery_engine.py  # passed
git diff --check                               # passed
```

## Three-clip test status

| Clip | Intended action | Flow generation | Output file | Face comparison |
|---|---|---:|---|---|
| 1 | Pre-bite/deep dip from anchored character | Not run | None | Not assessable |
| 2 | Post-bite/reaction using prior end frame | Not run | None | Not assessable |
| 3 | Glaze/drizzle finale using prior end frame | Not run | None | Not assessable |

No 10-second clips, end frames, or final concatenated video were produced in this run. It would be misleading to claim face consistency or a numerical face-match score without generated output frames.

## Blocking condition

The current automation assumes a semantic, role-specific upload control exists in the active generation UI. In the real Flow Character screen, the only observed input is a generic project-level media uploader; setting its files via CDP does not cause the React application to ingest/render the reference asset. The live UI therefore requires a Flow-specific attachment workflow (likely a user-gesture-mediated upload or a different, rendered attachment component) before character creation and the subsequent three-clip pipeline can be verified.

## Evidence artifacts (intentionally untracked)

- `flow_character_ui.png` — initial live Character creation UI capture.
- `flow_character_attachment_attempt.png` — UI capture after the direct attachment attempt.
- `creator_face_ref.jpg` — local test fixture copied from existing untracked `v4_frame_1.jpg`.

These artifacts are intentionally excluded from the commit, along with all pre-existing untracked videos/images/scripts in the repository root.

## Conclusion

- **Automation code:** syntax and diff checks pass; prompt focus and low-level upload verification were improved and tested against the live DOM.
- **Reference upload:** file was assigned at CDP level, but not accepted/rendered by Flow’s application UI.
- **Face consistency across three clips:** **not assessed** because zero Flow clips were generated.
