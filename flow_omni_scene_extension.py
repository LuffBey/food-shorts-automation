"""Fail-closed Gemini Omni 1.1 Flash scene-extension pipeline.

This is the active production path. It never invokes independent 3x10s,
continuation-frame, or match-cut fallback code. A parent can be extended only
when its state is ACCEPTED_PARENT and Flow exposes an Omni-compatible,
video-context continuation action.
"""

import base64
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from inspect_flow_agent import FlowClient

WORKDIR = Path("/root/hermes-projects/food-discovery-automation")
FLOW_PROJECT_ID = "0bd8a011-4555-49c2-adc8-ba87b68466a9"
CREATOR_ID = "b068cab7-76d4-49ec-9066-9259c139d46a"
CREATOR_NAME = "Creator"
MAX_ATTEMPTS_PER_STAGE = 3

BASE_PROMPT = """Create a 10-second vertical 9:16 photorealistic premium food-commercial video using the bound @Creator and approved brand/food references. Preserve the exact approved Creator identity, matte black crew-neck shirt, seamless burnt-orange studio background, medium-dark walnut table, single plate, and shallow glossy white sauce bowl. The extra-crispy golden fried chicken tender is visible in the first frame. Creator holds one whole unbitten tender in the right hand above the plate, slowly dips only its lower quarter into thick glossy dark amber-red barbecue sauce, then lifts it. End with the same unbitten tender, lower quarter sauced, held 20–25 cm from the mouth; face, plate and bowl visible. No speech, human vocalization, speech-like lips, text, subtitles, logo, music, cut, second food piece or bite."""

EXT1_PROMPT = """Continue directly from the accepted preceding video in the same scene and shot family. Preserve every visible identity, wardrobe, background, table, camera, lighting, prop, right-hand grip, plate and bowl position exactly. Preserve the same single chicken tender with its lower quarter sauced. Creator lifts that same tender, takes exactly one medium bite from the upper end with one realistic crunch, then performs two or three brief closed-mouth chewing movements. End with the same one-bitten tender in the right hand and its crisp golden crust and juicy fibrous white interior cross-section facing camera. Plate and bowl remain visible and unchanged. No fresh scene, cut, second bite, food repair, prop movement/removal, dialogue, vocal reaction, speech-like lips, text, logo or music."""

EXT2_PROMPT = """Continue directly from the accepted preceding video. Preserve the exact same Creator, face, hair, facial hair, black shirt, burnt-orange background, walnut table, plate, white sauce bowl, camera, lens, lighting and color grade. Preserve the same one-bitten chicken tender with identical sauce coverage in the same right hand. Without another bite, slowly rotate the same tender to reveal its crisp golden crust and juicy fibrous white interior. End with a subtle closed-mouth smile and one small natural nod in a clean hero composition; plate and bowl stationary and visible. No second bite, food regrowth, duplication, hand switch, prop change, background change, dialogue, vocalization, speech-like lips, text, subtitle, logo or music."""


class PipelineBlocked(RuntimeError):
    """Raised for unsupported or unavailable Flow capabilities."""


class OmniSceneExtensionPipeline:
    def __init__(self, client=None, workdir=WORKDIR):
        self.client = client or FlowClient()
        self.workdir = Path(workdir)
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.evidence_dir = self.workdir / "runtime_evidence" / self.run_id
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.lineage = {
            "run_id": self.run_id,
            "project_id": FLOW_PROJECT_ID,
            "creator_id": CREATOR_ID,
            "model_required": "Gemini Omni 1.1 Flash",
            "started_at": self.now(),
            "stages": {name: self.empty_stage(name) for name in ("base", "ext1", "ext2")},
            "blockers": [],
        }

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def empty_stage(name):
        return {
            "name": name, "state": "PENDING", "asset_id": None, "parent_id": None,
            "media_url": None, "file_path": None, "duration": None, "resolution": None,
            "fps": None, "retry_count": 0, "transitions": [], "qc": None,
        }

    def transition(self, name, state, reason=None):
        if state not in {"PENDING", "GENERATING", "GENERATED", "QC_PASS", "QC_FAIL", "ACCEPTED_PARENT", "DISCARDED_CHILD", "BLOCKED"}:
            raise ValueError(f"invalid stage state: {state}")
        stage = self.lineage["stages"][name]
        stage["state"] = state
        stage["transitions"].append({"at": self.now(), "state": state, "reason": reason})
        self.persist_ledger()

    def persist_ledger(self):
        (self.evidence_dir / "lineage.json").write_text(json.dumps(self.lineage, indent=2), encoding="utf-8")

    def visible_ui_snapshot(self):
        return self.client.eval("""
        (() => ({
          title: document.title,
          url: location.href,
          buttons: Array.from(document.querySelectorAll('button,[role=button]')).map(b => ({
            text:(b.innerText||'').trim().replace(/\\n+/g,' '),
            aria:b.getAttribute('aria-label')||'', title:b.title||'',
            visible:!!(b.offsetWidth||b.offsetHeight)
          })).filter(x => x.visible && (x.text||x.aria||x.title)),
          videos: Array.from(document.querySelectorAll('video')).map(v => v.currentSrc||v.src).filter(Boolean)
        }))()
        """)

    def verify_ui_scene_extension_capability(self):
        """Require a visible Omni-compatible video-context control; never assume it."""
        ui = self.visible_ui_snapshot()
        (self.evidence_dir / "flow_ui_capability.json").write_text(json.dumps(ui, indent=2), encoding="utf-8")
        self.client.screenshot(str(self.evidence_dir / "flow_ui_capability.png"))
        text = " ".join((b["text"] + " " + b["aria"] + " " + b["title"]).lower() for b in ui["buttons"])
        legacy_only = "uzat (veo" in text or "extend (veo" in text
        omni_context = ("add to prompt" in text or "isteme ekle" in text) and ("omni" in text or "scene extension" in text)
        if legacy_only and not omni_context:
            reason = "Visible Flow UI exposes only legacy 'Uzat (Veo 3.1 - Lite)' continuation; no Omni 1.1 Flash video-context Scene Extension control is visible."
            self.lineage["blockers"].append({"at": self.now(), "reason": reason, "evidence": str(self.evidence_dir / "flow_ui_capability.json")})
            self.persist_ledger()
            return False
        if not omni_context:
            reason = "No visible Omni Scene Extension/Add-to-prompt video-context control was detected."
            self.lineage["blockers"].append({"at": self.now(), "reason": reason, "evidence": str(self.evidence_dir / "flow_ui_capability.json")})
            self.persist_ledger()
            return False
        return True

    def verify_creator_chip(self):
        """Verify an actual Creator entity element is present; plain prompt text is rejected."""
        result = self.client.eval("""
        (() => {
          const exact = Array.from(document.querySelectorAll('*')).filter(e =>
            e.children.length === 0 && e.textContent.trim() === 'Creator' &&
            (e.offsetWidth || e.offsetHeight));
          return {count: exact.length, elements: exact.map(e => ({tag:e.tagName, cls:e.className}))};
        })()
        """)
        if not result or not result.get("count"):
            raise PipelineBlocked("Tokenized @Creator entity chip was not visibly verified.")
        return result

    def collect_video_urls(self):
        return self.client.eval("""
        (() => Array.from(new Set(Array.from(document.querySelectorAll('video')).map(v => v.currentSrc||v.src).filter(Boolean))))()
        """) or []

    def submit_agent_prompt(self, prompt):
        before = set(self.collect_video_urls())
        ok = self.client.eval(f"""
        (() => {{
          const editor=document.querySelector('div[contenteditable=true]');
          const buttons=Array.from(document.querySelectorAll('button'));
          const send=buttons.find(b => (b.innerText||'').includes('arrow_forward'));
          if(!editor || !send) return false;
          editor.focus(); const r=document.createRange(); r.selectNodeContents(editor); r.collapse(false);
          const s=window.getSelection(); s.removeAllRanges(); s.addRange(r);
          document.execCommand('selectAll',false,null); document.execCommand('delete',false,null);
          document.execCommand('insertText',false,{json.dumps(prompt)}); send.click(); return true;
        }})()
        """)
        if not ok:
            raise RuntimeError("Agent composer or arrow_forward submit control was unavailable.")
        return before

    def wait_for_new_video(self, before, timeout=360):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            time.sleep(5)
            body = self.client.eval("document.body.innerText") or ""
            if any(x in body for x in ("Başarısız", "Failed", "Hata")):
                raise RuntimeError("Flow reported a generation failure.")
            current = self.collect_video_urls()
            fresh = [u for u in current if u not in before]
            if fresh:
                return fresh[0]
        raise TimeoutError("No new generated video appeared before timeout.")

    @staticmethod
    def asset_id_from_url(url):
        return url.split("name=")[-1].split("&")[0]

    def probe_video(self, path):
        raw = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-show_entries", "format=duration,size", "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
        data = json.loads(raw); stream = data["streams"][0]; fmt = data["format"]
        num, den = stream["r_frame_rate"].split("/")
        return {"duration": round(float(fmt["duration"]), 3), "resolution": f"{stream['width']}x{stream['height']}", "fps": round(int(num)/int(den), 3), "size_bytes": int(fmt["size"])}

    def download_video(self, media_url, stage_name):
        # Browser fetch preserves authenticated flow session and writes base64 to disk without cookies in reports.
        encoded = self.client.eval(f"""
        (async()=>{{const r=await fetch({json.dumps(media_url)}); if(!r.ok) return null; const b=await r.blob(); return await new Promise((ok,no)=>{{const fr=new FileReader();fr.onload=()=>ok(fr.result);fr.onerror=no;fr.readAsDataURL(b)}})}})()
        """)
        if not encoded or "," not in encoded:
            raise RuntimeError("Authenticated Flow media download failed.")
        path = self.evidence_dir / f"{stage_name}_{self.asset_id_from_url(media_url)}.mp4"
        path.write_bytes(base64.b64decode(encoded.split(",", 1)[1]))
        return path

    def run_base_generation(self):
        stage = self.lineage["stages"]["base"]
        self.verify_creator_chip()
        self.transition("base", "GENERATING")
        before = self.submit_agent_prompt(BASE_PROMPT)
        url = self.wait_for_new_video(before)
        path = self.download_video(url, "base")
        metrics = self.probe_video(path)
        stage.update({"asset_id": self.asset_id_from_url(url), "media_url": url, "file_path": str(path), **metrics})
        self.transition("base", "GENERATED")
        return stage

    def attach_accepted_video_to_prompt(self, parent_name):
        parent = self.lineage["stages"][parent_name]
        if parent["state"] != "ACCEPTED_PARENT":
            raise PipelineBlocked(f"{parent_name} is {parent['state']}, not ACCEPTED_PARENT; it cannot be extended.")
        # The exact action must be visible and must attach a video, not a filename/still.
        ui = self.visible_ui_snapshot()
        if not any("add to prompt" in (b["text"] + b["aria"]).lower() or "isteme ekle" in (b["text"] + b["aria"]).lower() for b in ui["buttons"]):
            raise PipelineBlocked("Accepted parent has no visible Add to prompt/video-context action.")
        # Human-supported UI click is intentionally not guessed: selectors are verified at run time.
        raise PipelineBlocked("Visible Add to prompt control found, but no verified Omni 1.1 video-context attachment state was exposed by this UI build.")

    def run_scene_extension(self, parent_name, stage_name, prompt):
        self.attach_accepted_video_to_prompt(parent_name)
        # Only reachable after a verified video context attachment.
        stage = self.lineage["stages"][stage_name]
        parent = self.lineage["stages"][parent_name]
        stage["parent_id"] = parent["asset_id"]
        self.transition(stage_name, "GENERATING")
        before = self.submit_agent_prompt(prompt)
        url = self.wait_for_new_video(before)
        path = self.download_video(url, stage_name)
        metrics = self.probe_video(path)
        stage.update({"asset_id": self.asset_id_from_url(url), "media_url": url, "file_path": str(path), **metrics})
        self.transition(stage_name, "GENERATED")
        return stage

    def execute_qc_gate(self, stage_name):
        """Extract mandated 0.5-second evidence. Semantic approval is deliberately fail-closed until assessed."""
        stage = self.lineage["stages"][stage_name]
        if stage["state"] != "GENERATED" or not stage["file_path"]:
            raise RuntimeError(f"QC cannot run for {stage_name}: no generated video asset.")
        duration = stage["duration"]
        samples = []
        t = 0.0
        frames_dir = self.evidence_dir / f"qc_{stage_name}"
        frames_dir.mkdir(exist_ok=True)
        while t < duration - 0.05:
            frame = frames_dir / f"{t:.1f}s.jpg"
            subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", stage["file_path"], "-frames:v", "1", "-q:v", "2", str(frame)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            samples.append({"timestamp_s": round(t, 1), "frame_path": str(frame), "checks_required": ["Creator", "background", "table", "plate", "bowl", "food_state", "hand", "bite_count", "speech_lips", "text"]})
            t += 0.5
        stage["qc"] = {"sample_interval_s": 0.5, "sample_count": len(samples), "samples": samples, "decision": "PENDING_HUMAN_OR_VISION_REVIEW"}
        self.persist_ledger()
        return stage["qc"]

    def run(self):
        if not self.verify_ui_scene_extension_capability():
            for name in ("base", "ext1", "ext2"):
                self.transition(name, "BLOCKED", "Omni Scene Extension capability unavailable; no fallback permitted.")
            raise PipelineBlocked(self.lineage["blockers"][-1]["reason"])
        self.run_base_generation()
        self.execute_qc_gate("base")
        # Acceptance is intentionally not inferred from extraction. This guard stops unsafe extension.
        raise PipelineBlocked("Base QC evidence created but no semantic QC approver is attached; base remains GENERATED and cannot become ACCEPTED_PARENT.")


def main():
    pipeline = OmniSceneExtensionPipeline()
    try:
        pipeline.run()
    except PipelineBlocked as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    except Exception as error:
        print(f"FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
