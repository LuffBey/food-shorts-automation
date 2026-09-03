# Food Discovery AI Video Automation

Google Flow / Gemini Omni 1.1 Flash based pipeline for language-independent food Shorts, Reels and TikTok videos.

## Active architecture

The production path is now **one 10-second base clip plus two contextual scene extensions**. Independent 3×10-second generations and extracted continuation frames are legacy experiments, not the default pipeline.

```text
approved references
  -> 10s Omni 1.1 base clip
  -> QC
  -> scene extension 1 from accepted video
  -> QC
  -> scene extension 2 from accepted chain
  -> QC
  -> duration/audio normalization
  -> final 9:16 master
```

Read in this order:

1. `ARCHITECTURE.md` — system design and quality gates.
2. `FLOW_AGENT_OMNI_SCENE_EXTENSION_PROMPT.md` — executable Hermes instruction.
3. `HERMES_NEXT_ACTION.md` — immediate implementation/test assignment.
4. `CODEX_HANDOVER.md` — environment and migration notes.

## Non-negotiable output rules

- Same licensed Creator, burnt-orange set, walnut table, white bowl and food-state lineage.
- No dialogue, voice-over, intelligible vocalization or speech-like lip movement in any language.
- Never extend a failed generation.
- Never conceal identity, prop or food-state drift in post-production.
- Do not silently fall back to independent clip generation.
- Use only supported Flow controls; do not bypass service safeguards.

## Legacy files

Scripts and documents named `3x10s`, `continuation`, `frame`, `concat` or `editorial` describe earlier experiments. They remain for traceability until Hermes implements and validates the Omni scene-extension path. They must not be treated as active production instructions.

Generated videos, screenshots, extracted frames, browser profiles, cookies and credentials are not committed.
