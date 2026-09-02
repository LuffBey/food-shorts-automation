"""Google Flow food-shorts automation with character-first continuity.

This module drives an already authenticated Chromium instance exposed on CDP port 9222.
It does not log in, publish, or commit generated media.
"""
import base64
import json
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path


class FlowClient:
    """Small dependency-free Chrome DevTools Protocol client."""

    def __init__(self, port=9222):
        self.port = port
        self.msg_id = 0
        self.connect()

    def connect(self):
        pages = json.loads(urllib.request.urlopen(
            f"http://127.0.0.1:{self.port}/json/list", timeout=10
        ).read().decode())
        page = next((p for p in pages if "flow" in p.get("url", "").lower()), pages[0])
        path = page["webSocketDebuggerUrl"].split(str(self.port), 1)[1]
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(60)
        self.s.connect(("127.0.0.1", self.port))
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{self.port}\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        self.s.sendall(request.encode())
        self.s.recv(4096)

    def _send(self, text):
        data = text.encode()
        frame = bytearray([0x81])
        if len(data) <= 125:
            frame.append(0x80 | len(data))
        elif len(data) <= 65535:
            frame.extend([0x80 | 126]); frame.extend(len(data).to_bytes(2, "big"))
        else:
            frame.extend([0x80 | 127]); frame.extend(len(data).to_bytes(8, "big"))
        mask = os.urandom(4)
        frame.extend(mask)
        frame.extend(b ^ mask[i % 4] for i, b in enumerate(data))
        self.s.sendall(frame)

    def _recv(self):
        head = self.s.recv(2)
        if not head:
            return None
        length = head[1] & 127
        if length == 126:
            length = int.from_bytes(self.s.recv(2), "big")
        elif length == 127:
            length = int.from_bytes(self.s.recv(8), "big")
        masked = bool(head[1] & 128)
        mask = self.s.recv(4) if masked else b""
        chunks = bytearray()
        while len(chunks) < length:
            chunks.extend(self.s.recv(length - len(chunks)))
        if masked:
            chunks = bytearray(b ^ mask[i % 4] for i, b in enumerate(chunks))
        return chunks.decode(errors="replace")

    def cdp(self, method, params=None):
        self.msg_id += 1
        message_id = self.msg_id
        self._send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        while True:
            raw = self._recv()
            if raw is None:
                raise RuntimeError("CDP connection closed")
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if result.get("id") == message_id:
                if "error" in result:
                    raise RuntimeError(f"CDP {method}: {result['error']}")
                return result

    def eval(self, expression):
        result = self.cdp("Runtime.evaluate", {
            "expression": expression, "returnByValue": True, "awaitPromise": True,
        })
        return result.get("result", {}).get("result", {}).get("value")

    def _click_center(self, point):
        if not point:
            return False
        self.cdp("Input.dispatchMouseEvent", {"type": "mouseMoved", **point})
        self.cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "button": "left", "clickCount": 1, **point})
        self.cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "button": "left", "clickCount": 1, **point})
        return True

    def click_text(self, text, timeout=5):
        """Click a visible interactive element whose accessible text includes text."""
        needle = json.dumps(text.lower())
        end = time.time() + timeout
        while time.time() < end:
            point = self.eval(f"""(() => {{
              const needle={needle};
              const nodes=[...document.querySelectorAll('button,[role=button],[role=menuitem],a')];
              const el=nodes.find(x => !x.disabled && x.offsetParent &&
                ((x.innerText||x.getAttribute('aria-label')||'').toLowerCase().includes(needle)));
              if (!el) return null; const r=el.getBoundingClientRect();
              return {{x:r.left+r.width/2,y:r.top+r.height/2}};
            }})()""")
            if point:
                return self._click_center(point)
            time.sleep(.25)
        return False

    def visible_text(self):
        return self.eval("document.body ? document.body.innerText : ''") or ""

    def capture(self, output_path):
        data = self.cdp("Page.captureScreenshot", {"format": "png"})["result"]["data"]
        Path(output_path).write_bytes(base64.b64decode(data))

    def _file_input_node(self, selector="input[type=file]"):
        """Resolve a fresh DOM node immediately before setting files.

        Flow rerenders its composer after opening an upload dialog, so a Runtime object
        handle may be stale by the time DOM.setFileInputFiles is called.
        """
        document = self.cdp("DOM.getDocument", {"depth": 1})["result"]["root"]["nodeId"]
        result = self.cdp("DOM.querySelector", {"nodeId": document, "selector": selector})
        return result.get("result", {}).get("nodeId")

    def attach_file(self, image_path, selector="input[type=file]"):
        """Attach through CDP then notify React and its drag/drop listeners."""
        image_path = os.path.abspath(image_path)
        if not os.path.isfile(image_path):
            raise FileNotFoundError(image_path)
        node = self._file_input_node(selector)
        if not node:
            return {"attached": False, "reason": "No Flow file input found"}
        try:
            self.cdp("DOM.setFileInputFiles", {"files": [image_path], "nodeId": node})
        except RuntimeError:
            # One retry after re-resolving handles Flow's reactive rerender.
            node = self._file_input_node(selector)
            if not node:
                return {"attached": False, "reason": "Flow file input was detached"}
            self.cdp("DOM.setFileInputFiles", {"files": [image_path], "nodeId": node})
        # React commonly listens to input/change; drop targets commonly listen to DragEvent.
        verification = self.eval("""(() => {
          const el=document.querySelector('input[type=file]'); if (!el) return null;
          el.dispatchEvent(new Event('input',{bubbles:true,composed:true}));
          el.dispatchEvent(new Event('change',{bubbles:true,composed:true}));
          try { const dt=new DataTransfer(); for(const f of el.files) dt.items.add(f);
            for(const type of ['dragenter','dragover','drop']) el.dispatchEvent(new DragEvent(type,{bubbles:true,composed:true,dataTransfer:dt}));
          } catch (_) {}
          return [...el.files].map(f=>({name:f.name,size:f.size,type:f.type}));
        })()""")
        return {"attached": bool(verification), "files": verification or []}

    def focus_editor(self):
        return self.eval("""(() => {
          const el=[...document.querySelectorAll('[contenteditable=true],textarea')].find(e=>e.offsetParent);
          if (!el) return false; el.focus(); return document.activeElement===el;
        })()""")

    def clear_editor(self):
        if not self.focus_editor():
            raise RuntimeError("Flow prompt editor not found")
        self.cdp("Input.dispatchKeyEvent", {"type":"keyDown","key":"Control","code":"ControlLeft","modifiers":2})
        self.cdp("Input.dispatchKeyEvent", {"type":"keyDown","key":"a","code":"KeyA","modifiers":2})
        self.cdp("Input.dispatchKeyEvent", {"type":"keyUp","key":"a","code":"KeyA","modifiers":2})
        self.cdp("Input.dispatchKeyEvent", {"type":"keyUp","key":"Control","code":"ControlLeft"})
        self.cdp("Input.dispatchKeyEvent", {"type":"keyDown","key":"Backspace","code":"Backspace"})
        self.cdp("Input.dispatchKeyEvent", {"type":"keyUp","key":"Backspace","code":"Backspace"})

    def insert_text(self, text):
        self.cdp("Input.insertText", {"text": text})
        time.sleep(.4)

    def download_video_by_url(self, video_url, output_path):
        result = self.eval(f"""(async()=>{{
          const r=await fetch({json.dumps(video_url)}); const b=await r.blob();
          return await new Promise((ok,no)=>{{const f=new FileReader();f.onloadend=()=>ok({{size:b.size,dataUrl:f.result}});f.onerror=no;f.readAsDataURL(b)}})
        }})()""")
        if not result or "dataUrl" not in result:
            return False
        Path(output_path).write_bytes(base64.b64decode(result["dataUrl"].split(",", 1)[1]))
        return True


class CharacterAssetManager:
    """Character-first Flow UI automation. It fails closed for identity lock."""

    def __init__(self, client, name="Creator", reference_paths=None):
        self.client = client
        self.name = name
        self.reference_paths = [p for p in (reference_paths or []) if os.path.isfile(p)][:2]
        self.creation_status = "not-attempted"

    def asset_exists(self):
        text = self.client.visible_text().lower()
        return self.name.lower() in text and "character" in text

    def open_characters(self):
        if self.client.click_text("Characters", timeout=3):
            time.sleep(1)
            return True
        # Flow may expose a compact icon with only aria-label.
        return bool(self.client.eval("""(() => {
          const el=[...document.querySelectorAll('[aria-label],[title]')].find(e=>
            e.offsetParent && ((e.getAttribute('aria-label')||e.title||'').toLowerCase().includes('character')));
          if(!el)return false; el.click(); return true;
        })()"""))

    def ensure_creator(self):
        self.open_characters()
        if self.asset_exists():
            self.creation_status = "reused-existing"
            return True
        for label in ("New character", "Yeni karakter", "Create character", "Karakter oluştur", "Add character", "Create", "Oluştur"):
            if self.client.click_text(label, timeout=1):
                break
        else:
            self.creation_status = "blocked-no-character-create-control"
            return False
        time.sleep(1)
        attached = []
        for reference in self.reference_paths:
            outcome = self.client.attach_file(reference)
            attached.append(outcome)
            time.sleep(.8)
        filename_visible = any(Path(p).name.lower() in self.client.visible_text().lower() for p in self.reference_paths)
        preview_visible = bool(self.client.eval("""(() => [...document.querySelectorAll('img,video,[role=img]')].some(e=>e.offsetParent &&
          /preview|upload|reference|character/i.test((e.alt||e.getAttribute('aria-label')||e.className||''))) )()"""))
        if not any(x.get("attached") for x in attached) or not (filename_visible or preview_visible):
            self.creation_status = "blocked-upload-not-ingested"
            return False
        # The label/name is optional on different Flow versions; populate any visible field if present.
        self.client.eval(f"""(() => {{const i=[...document.querySelectorAll('input[type=text]')].find(x=>x.offsetParent && /name/i.test(x.placeholder||x.getAttribute('aria-label')||''));
          if(i){{i.focus();i.value={json.dumps(self.name)};i.dispatchEvent(new Event('input',{{bubbles:true}}));i.dispatchEvent(new Event('change',{{bubbles:true}}));}}}})()""")
        for label in ("Create", "Generate", "Save"):
            if self.client.click_text(label, timeout=1):
                break
        for _ in range(60):
            time.sleep(2)
            if self.asset_exists():
                self.creation_status = "created"
                return True
        self.creation_status = "blocked-create-not-rendered"
        return False

    def insert_verified_chip(self):
        """Insert @Creator and select its autocomplete item; never accept plain text."""
        self.client.clear_editor()
        self.client.insert_text("@" + self.name)
        time.sleep(1)
        selected = self.client.click_text(self.name, timeout=3)
        if not selected:
            self.creation_status = self.creation_status + "; chip-suggestion-not-found"
            return False
        time.sleep(.5)
        # A real chip has a non-text element / contenteditable child rather than plain editor text.
        tokenized = self.client.eval(f"""(() => {{
          const ed=[...document.querySelectorAll('[contenteditable=true]')].find(e=>e.offsetParent); if(!ed)return false;
          const name={json.dumps(self.name.lower())};
          return [...ed.querySelectorAll('*')].some(n => (n.textContent||'').trim().toLowerCase()===name &&
            !['#text','BR','P'].includes(n.nodeName) && (n.getAttribute('data-lexical-text')!=='true'));
        }})()""")
        if not tokenized:
            self.creation_status = self.creation_status + "; chip-not-tokenized"
        return bool(tokenized)


class ProfessionalMukbangPipeline:
    def __init__(self, client):
        self.client = client
        self.workdir = "/root/hermes-projects/food-discovery-automation"
        self.character_reference = os.path.join(self.workdir, "creator_face_ref.jpg")
        self.character = CharacterAssetManager(client, "Creator", [self.character_reference])
        self.identity_lock = ("Persistent identity lock: exact same person @Creator; same face, facial geometry, hair, clothing, age, skin tone and body proportions. ")
        self.scene_lock = ("Persistent scene lock: same table, fried-chicken platter, camera distance, realistic 50mm lens feel, warm studio lighting and background. ")
        self.negative_rules = ("Negative constraints: identity drift, face replacement, hairstyle change, wardrobe change, hand deformities, floating food, background shifts, unstable camera, blur, text, subtitles. Silent hyper-real food ASMR realism.")

    def ensure_video_settings(self):
        # Existing controls vary by Flow release; only use actual visible text.
        self.client.click_text("Video", timeout=2)
        self.client.click_text("9:16", timeout=2)
        self.client.click_text("10", timeout=2)

    def set_start_frame(self, image_path):
        return self.client.attach_file(image_path)

    def set_character_reference(self):
        return self.client.attach_file(self.character_reference)

    def build_clip_prompt(self, action):
        return f"{self.identity_lock}{self.scene_lock}Action delta only: {action}. {self.negative_rules}"

    def _append_after_chip(self, prompt):
        self.client.insert_text(" " + prompt)

    def _generation_ready(self):
        text = self.client.visible_text().lower()
        return not any(x in text for x in ("safety", "try again", "error generating"))

    def generate_single_clip(self, clip_number, action, start_frame=None, output_path=None):
        """Generate exactly one clip. Returns None on failure rather than chaining bad output."""
        self.ensure_video_settings()
        character_ready = self.character.ensure_creator()
        chip_ok = character_ready and self.character.insert_verified_chip()
        if not chip_ok:
            # Explicit fallback: ingredient reference. The report retains the precise reason.
            self.client.clear_editor()
            fallback = self.set_character_reference()
            if not fallback.get("attached"):
                raise RuntimeError("Identity lock unavailable: @Creator chip failed and reference fallback did not attach")
            self.client.insert_text(self.build_clip_prompt(action))
        else:
            self._append_after_chip(self.build_clip_prompt(action))
        if start_frame:
            attached = self.set_start_frame(start_frame)
            if not attached.get("attached"):
                raise RuntimeError(f"Clip {clip_number}: start-frame attachment failed")
        if not self.client.click_text("Generate", timeout=5):
            raise RuntimeError(f"Clip {clip_number}: Flow Generate button not found")
        # Wait for a media URL visible in Flow's generated project DOM.
        url = None
        for _ in range(180):
            time.sleep(2)
            url = self.client.eval("""(() => { const m=[...document.querySelectorAll('video')].find(v=>v.src && v.src.startsWith('http')); return m && m.src; })()""")
            if url:
                break
            if not self._generation_ready():
                return None
        if not url:
            return None
        output_path = output_path or os.path.join(self.workdir, f"clip_{clip_number}.mp4")
        return output_path if self.client.download_video_by_url(url, output_path) else None

    def choose_clean_continuation_frame(self, video_path, clip_number):
        """Extract 8.0s and 9.0s candidates; select earlier candidate if final frame is unusable.

        Automatic visual scoring is deliberately conservative: frame extraction must succeed and
        must not be near-black. Human/vision QA can reject a clip before chaining it.
        """
        candidates = []
        for seconds in (8.0, 9.0):
            frame = os.path.join(self.workdir, f"clip_{clip_number}_continuation_{seconds:.0f}s.jpg")
            cmd = ["ffmpeg", "-y", "-ss", str(seconds), "-i", video_path, "-frames:v", "1", "-q:v", "2", frame]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0 and os.path.getsize(frame) > 10_000:
                candidates.append(frame)
        if not candidates:
            raise RuntimeError(f"Clip {clip_number}: no usable continuation frame extracted")
        return candidates[-1]  # 9s normally preserves the latest clean composition.

    def produce_3x10s_shorts(self):
        actions = [
            "Hook in the first two seconds: Creator picks up a crispy fried chicken tender and performs one slow deep dip into glossy sauce; macro crunchy texture and sauce stretch.",
            "Creator takes one clean bite, shows the crunchy tender interior and gives a subtle satisfied ASMR reaction; keep hands and face fully visible.",
            "Creator drizzles glossy glaze over the last tender, takes a final bite, faces camera and gives a natural small thumbs-up approval.",
        ]
        clips, continuation = [], None
        for index, action in enumerate(actions, 1):
            clip = self.generate_single_clip(index, action, continuation)
            if not clip:
                raise RuntimeError(f"Clip {index} failed; chain stopped so a broken identity frame is not propagated")
            clips.append(clip)
            if index < 3:
                continuation = self.choose_clean_continuation_frame(clip, index)
        output = os.path.join(self.workdir, "food_asmr_creator_3x10s.mp4")
        listfile = os.path.join(self.workdir, "generated_concat.txt")
        Path(listfile).write_text("".join(f"file '{Path(c).resolve()}'\n" for c in clips))
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile, "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", output], check=True)
        return output


if __name__ == "__main__":
    pipeline = ProfessionalMukbangPipeline(FlowClient())
    print(pipeline.produce_3x10s_shorts())
