# 🍗 Food Discovery AI Video Automation Engine

Automated, end-to-end AI Food & Mukbang YouTube Shorts / TikTok production pipeline using Google Flow (Gemini Omni 1.1 Flash / Veo 3.1) and CDP (Chrome DevTools Protocol).

## 📌 Architecture & Features
- **3x10s Match-Cut Narrative Flow:** 
  1. *Pre-Bite / Deep Dip (0-10s)*
  2. *Post-Bite / Crunch Reaction (10-20s)*
  3. *Glaze Drizzle & Thumbs Up Finale (20-30s)*
- **Anti-Morphing & Continuity:** Utilizes Start Frame (Keyframe Interpolation) between clips to avoid face and prop drift.
- **Automated Post-Production:** FFmpeg automated color saturation boost (+12% Vibrance), 1080x1920 9:16 vertical crop, 30 FPS lossless muxing.

## 📂 Core Files
- `food_discovery_engine.py`: Main CDP automation client and multi-clip production engine.
- `CODEX_HANDOVER.md`: Detailed integration and task handover guide for Codex.
- `creator_face_ref.jpg`: High-resolution character face reference.
- `real_frame_1.jpg` & `real_frame_2.jpg`: Full table & platter scene references.

## 🚀 How to Run
```bash
python3 food_discovery_engine.py
```
