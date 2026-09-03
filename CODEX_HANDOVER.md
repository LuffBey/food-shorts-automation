# Food Shorts Automation — Current Handover

Updated: 2026-09-03

## Current decision

The project has migrated from independent `3 x 10s` generation to a parent-preserving Gemini Omni 1.1 Flash scene-extension chain.

The old method improved presentation through match cuts but could not reliably preserve identity, set geometry, plate/bowl state, hand state or bite history. Extracting a last frame carried appearance at one instant but not the complete temporal context.

The active design is defined in `ARCHITECTURE.md`. The exact instruction for Hermes is `FLOW_AGENT_OMNI_SCENE_EXTENSION_PROMPT.md`.

## Production path

```text
Creator + BrandSet + FoodProp references
  -> Base 10s generation
  -> QC and accept/reject
  -> Add accepted video to prompt / scene extension
  -> Extension 1
  -> QC and accept/reject
  -> Continue accepted parent chain
  -> Extension 2
  -> QC and accept/reject
  -> cumulative-output selection or segment assembly
  -> audio/duration normalization
  -> final QC
```

## Live environment known from prior tests

- Remote working directory: `/root/hermes-projects/food-discovery-automation/`
- Branch: `fix/character-consistency`
- Flow project: `0bd8a011-4555-49c2-adc8-ba87b68466a9`
- Creator ID: `b068cab7-76d4-49ec-9066-9259c139d46a`
- Creator name: `Creator`
- Authenticated Chromium/CDP port: `9222`
- Proven base settings: Gemini Omni 1.1 Flash, 720×1280, 9:16, 10 seconds, one output

Treat all UI selectors and entitlement state as time-sensitive and verify them visibly.

## Proven components that should be retained

- opening the existing authenticated Flow project;
- selecting Omni 1.1 Flash video settings;
- inserting and verifying the real tokenized `@Creator` entity;
- detecting generated media and downloading accepted output;
- measuring output with FFmpeg/ffprobe;
- human-in-the-loop Generate activation when normal automation is rejected;
- keeping generated media and secrets outside Git.

## Components now considered legacy

- generating clips 2 and 3 from fresh text prompts;
- treating a final extracted JPEG as the primary continuity carrier;
- claiming “seamless” continuity from independently generated clips;
- automatically concatenating three clips before semantic QC;
- blind `saturation=1.12`/`contrast=1.05` enhancement;
- using face swap as the default continuity repair.

Do not delete legacy files yet; they are useful for regression comparison. Mark new implementation paths clearly and prevent accidental invocation as production defaults.

## New implementation responsibilities

Hermes must discover and verify the current Omni scene-extension UI in the existing project. In the observed Flow workflow, an accepted generated video is added back to the prompt through its visible `Add to prompt`/continuation action and the next action is requested in the same context.

The automation must fail closed if:

- the selected model is not Omni 1.1 Flash;
- the source video is not present as prompt context;
- asset lineage cannot be determined;
- a failed child would otherwise become a parent;
- Flow offers only an incompatible legacy path;
- a platform safeguard requests user action.

No attempt may bypass authentication, quota, safety or anti-abuse controls.

## Quality philosophy

Continuity is state management, not adjective repetition. Maintain an explicit ledger for Creator, wardrobe, set, camera, every prop, hand/grip, sauce coverage, bite count and irreversible food changes.

Each segment introduces only one main action and ends in a low-motion, readable state. A failed result is discarded and regenerated from its last accepted parent.

The video is global and language-independent: no dialogue, narration, “mmm,” whisper, intelligible voice, speech-like lips, subtitles or generated text. Food ASMR and stable room tone are allowed.

## Source basis

- Gemini Omni 1.1 Flash scene extension and API interaction chaining: https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/
- Flow creative-control release: https://blog.google/innovation-and-ai/models-and-research/google-labs/new-creative-controls-google-flow/
- Current Flow model feature matrix: https://support.google.com/flow/answer/16352836?hl=en
- Flow editing help: https://support.google.com/flow/answer/16935718?hl=en

The feature is newly released, so help pages and UI labels may not update in lockstep. Trust the verified account UI for availability, while following the official supported workflow.
