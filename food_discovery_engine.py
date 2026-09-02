import socket
import json
import base64
import os
import time
import urllib.request
import subprocess


class FlowClient:
    def __init__(self, port=9222):
        self.port = port
        self.connect()

    def connect(self):
        pages = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/list').read().decode())
        flow_page = next((p for p in pages if 'flow' in p.get('url', '')), None)
        if not flow_page:
            flow_page = pages[0]
        ws_url = flow_page['webSocketDebuggerUrl']
        path = ws_url.split(str(self.port))[1]

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('127.0.0.1', self.port))
        key = base64.b64encode(os.urandom(16)).decode('utf-8')
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.s.sendall(req.encode())
        self.s.recv(4096)
        self.msg_id = 0

    def _send(self, text):
        data = text.encode('utf-8')
        length = len(data)
        frame = bytearray([0x81])
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(length.to_bytes(2, 'big'))
        mask = os.urandom(4)
        frame.extend(mask)
        masked_data = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))
        frame.extend(masked_data)
        self.s.sendall(frame)

    def _recv(self):
        head = self.s.recv(2)
        if not head:
            return None
        length = head[1] & 0x7F
        if length == 126:
            length = int.from_bytes(self.s.recv(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.s.recv(8), 'big')
        data = bytearray()
        while len(data) < length:
            chunk = self.s.recv(length - len(data))
            if not chunk:
                break
            data.extend(chunk)
        return data.decode('utf-8', errors='ignore')

    def cdp(self, method, params=None):
        self.msg_id += 1
        curr_id = self.msg_id
        payload = {'id': curr_id, 'method': method}
        if params:
            payload['params'] = params
        self._send(json.dumps(payload))
        while True:
            res_str = self._recv()
            if not res_str:
                break
            try:
                res = json.loads(res_str)
                if res.get('id') == curr_id:
                    return res
            except Exception:
                pass
        return None

    def eval(self, expr):
        res = self.cdp('Runtime.evaluate', {
            'expression': expr,
            'returnByValue': True,
            'awaitPromise': True,
        })
        return res.get('result', {}).get('result', {}).get('value')

    def click_el(self, js_find):
        box = self.eval(f"""
        (() => {{
            const btns = Array.from(document.querySelectorAll(
                'button, div[role="button"], span[role="button"], div[contenteditable="true"]'
            ));
            const el = btns.find({js_find});
            if (!el) return null;
            const rect = el.getBoundingClientRect();
            return {{ x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 }};
        }})()
        """)
        if not box:
            return False
        x, y = box['x'], box['y']
        self.cdp('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x, 'y': y})
        self.cdp('Input.dispatchMouseEvent', {
            'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1
        })
        self.cdp('Input.dispatchMouseEvent', {
            'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1
        })
        return True

    def _file_inputs(self):
        """Return upload inputs with enough nearby text to distinguish their roles."""
        return self.eval("""
        (() => Array.from(document.querySelectorAll('input[type="file"]')).map((el, index) => {
            let node = el;
            let text = '';
            for (let depth = 0; depth < 6 && node; depth++, node = node.parentElement) {
                text += ' ' + (node.innerText || node.getAttribute?.('aria-label') || '');
            }
            return {
                index,
                accept: el.accept || '',
                multiple: !!el.multiple,
                disabled: !!el.disabled,
                text: text.replace(/\\s+/g, ' ').trim().slice(0, 1000)
            };
        }))()
        """) or []

    def _choose_file_input_index(self, role):
        """
        Pick a Flow upload input by semantic context instead of blindly using
        document.querySelector('input[type=file]').
        """
        inputs = self._file_inputs()
        if not inputs:
            return None

        role_keywords = {
            'start_frame': [
                'start frame', 'starting frame', 'first frame', 'başlangıç', 'ilk kare', 'frame'
            ],
            'character_reference': [
                'character', 'characters', 'ingredient', 'ingredients', 'reference',
                'referans', 'karakter', 'asset'
            ],
        }
        avoid_keywords = {
            'start_frame': ['character', 'ingredient', 'reference', 'karakter', 'referans'],
            'character_reference': ['end frame', 'ending frame', 'last frame', 'son kare'],
        }

        def score(item):
            text = (item.get('text') or '').lower()
            value = 0
            for kw in role_keywords.get(role, []):
                if kw in text:
                    value += 5
            for kw in avoid_keywords.get(role, []):
                if kw in text:
                    value -= 3
            if item.get('disabled'):
                value -= 100
            return value

        ranked = sorted(inputs, key=score, reverse=True)
        best = ranked[0]
        if score(best) <= 0:
            print(f"Warning: '{role}' upload alanı semantik olarak bulunamadı. Inputs={inputs}")
            return None
        print(f"-> {role} upload input seçildi: index={best['index']} context={best.get('text', '')[:180]}")
        return best['index']

    def _set_file_input_by_index(self, index, image_path):
        doc = self.cdp('DOM.getDocument', {'depth': -1})
        root_node_id = doc['result']['root']['nodeId']
        nodes = self.cdp('DOM.querySelectorAll', {
            'nodeId': root_node_id,
            'selector': 'input[type="file"]',
        })
        node_ids = nodes.get('result', {}).get('nodeIds', []) if nodes else []
        if index is None or index >= len(node_ids):
            return False
        self.cdp('DOM.setFileInputFiles', {
            'files': [os.path.abspath(image_path)],
            'nodeId': node_ids[index],
        })
        time.sleep(1.5)
        return True

    def _verify_upload(self, filename):
        filename = os.path.basename(filename)
        return bool(self.eval(f"""
        (() => {{
            const needle = {json.dumps(filename.lower())};
            const bodyText = (document.body.innerText || '').toLowerCase();
            if (bodyText.includes(needle)) return true;
            return Array.from(document.querySelectorAll('img')).some(img =>
                (img.alt || '').toLowerCase().includes(needle) ||
                (img.src || '').toLowerCase().includes(needle)
            );
        }})()
        """))

    def set_start_frame(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Start frame dosyası bulunamadı: {image_path}")
        index = self._choose_file_input_index('start_frame')
        if index is None:
            return False
        ok = self._set_file_input_by_index(index, image_path)
        if not ok:
            return False
        verified = self._verify_upload(image_path)
        if not verified:
            print("Warning: Start Frame upload DOM üzerinden kesin doğrulanamadı; UI state kontrol edilmeli.")
        return True

    def set_character_reference(self, image_path):
        if not image_path or not os.path.exists(image_path):
            raise FileNotFoundError(f"Karakter referansı bulunamadı: {image_path}")
        index = self._choose_file_input_index('character_reference')
        if index is None:
            return False
        ok = self._set_file_input_by_index(index, image_path)
        if not ok:
            return False
        verified = self._verify_upload(image_path)
        if not verified:
            print("Warning: Character Reference upload DOM üzerinden kesin doğrulanamadı; UI state kontrol edilmeli.")
        return True

    def set_prompt(self, text):
        self.click_el("el => el.getAttribute('data-slate-editor') === 'true'")
        time.sleep(0.2)
        self.cdp('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'a', 'modifiers': 2})
        self.cdp('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'a'})
        self.cdp('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'Backspace'})
        self.cdp('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Backspace'})
        time.sleep(0.2)
        for char in text:
            self.cdp('Input.dispatchKeyEvent', {
                'type': 'keyDown', 'text': char, 'unmodifiedText': char
            })
            self.cdp('Input.dispatchKeyEvent', {'type': 'keyUp'})
            time.sleep(0.001)
        time.sleep(0.3)

    def download_video_by_url(self, vid_url, out_path):
        res = self.eval(f"""
        (async () => {{
            const resp = await fetch({json.dumps(vid_url)});
            const blob = await resp.blob();
            return new Promise((resolve, reject) => {{
                const reader = new FileReader();
                reader.onloadend = () => resolve({{ size: blob.size, dataUrl: reader.result }});
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            }});
        }})()
        """)
        if res and 'dataUrl' in res:
            b64 = res['dataUrl'].split(',')[1]
            with open(out_path, 'wb') as f:
                f.write(base64.b64decode(b64))
            return True
        return False


class ProfessionalMukbangPipeline:
    def __init__(self, client: FlowClient):
        self.client = client
        self.workdir = "/root/hermes-projects/food-discovery-automation"
        os.makedirs(self.workdir, exist_ok=True)
        self.character_reference = os.path.join(self.workdir, 'creator_face_ref.jpg')

        self.identity_lock = (
            "IDENTITY LOCK: The main performer must be the exact same person shown in the supplied "
            "character reference image. Preserve the same facial identity, facial geometry, eyes, nose, "
            "jawline, hairstyle, hair color, skin tone, apparent age, body proportions and clothing. "
            "Do not redesign, reinterpret, replace or age-shift the person. "
        )
        self.scene_lock = (
            "CONTINUITY LOCK: Preserve the same table, plate, food styling, background, lighting, lens, "
            "camera height, color grade and wardrobe from the supplied start frame. Treat the start frame "
            "as the exact continuation point of the previous clip. "
        )
        self.negative_rules = (
            "Exclude: extra fingers, fused fingers, distorted teeth, mouth morphing, identity drift, "
            "face replacement, hairstyle changes, wardrobe changes, food sticking to facial skin, floating "
            "objects, camera drifting, background shifts, steam, smoke, vapor, blurry sauce, cartoonish "
            "artifacts. Silent, hyper-realistic, 4k."
        )

    def ensure_video_settings(self):
        print("Flow Video Ayarları Yapılandırılıyor (Omni 1.1 Flash, 9:16, 10s)...")
        self.client.click_el(
            "b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Omni') || "
            "b.innerText.includes('Veo') || b.innerText.includes('Video'))"
        )
        time.sleep(0.5)
        self.client.click_el("b => b.innerText && b.innerText.trim() === 'videocam Video'")
        time.sleep(0.3)
        self.client.click_el("b => b.innerText && (b.innerText.includes('Omni') || b.innerText.includes('Flash'))")
        time.sleep(0.3)
        self.client.click_el("b => b.innerText && (b.innerText.includes('9:16') || b.innerText.trim() === 'crop_9_16 9:16')")
        time.sleep(0.3)
        self.client.click_el("b => b.innerText && b.innerText.trim() === 'x1'")
        time.sleep(0.3)
        self.client.click_el("b => b.innerText && b.innerText.trim() === '10s'")
        time.sleep(0.3)
        self.client.click_el("el => el.getAttribute('data-slate-editor') === 'true'")
        time.sleep(0.5)

    def build_clip_prompt(self, delta_action, has_start_frame=True):
        continuity = self.scene_lock if has_start_frame else ''
        return f"{self.identity_lock}{continuity}ACTION DELTA: {delta_action} {self.negative_rules}"

    def generate_single_clip(
        self,
        full_prompt,
        start_frame_path,
        out_mp4,
        out_end_frame,
        character_reference_path=None,
    ):
        # 1. Persistent character identity reference: every clip gets the SAME image.
        character_reference_path = character_reference_path or self.character_reference
        if character_reference_path and os.path.exists(character_reference_path):
            print(f"-> Kalıcı Character Reference besleniyor: {character_reference_path}")
            if not self.client.set_character_reference(character_reference_path):
                print("Warning: Character Reference alanı bulunamadı. Identity consistency düşebilir.")

        # 2. Temporal continuity reference: previous clip's final clean frame.
        if start_frame_path and os.path.exists(start_frame_path):
            print(f"-> Continuity / Start Frame besleniyor: {start_frame_path}")
            if not self.client.set_start_frame(start_frame_path):
                print("Warning: Start Frame alanı bulunamadı. Match-cut continuity düşebilir.")

        # 3. Prompt = persistent identity lock + scene lock + bounded action delta.
        print(f"-> Güçlendirilmiş Prompt: {full_prompt[:180]}...")
        self.client.set_prompt(full_prompt)

        # 4. Trigger generation and capture only newly-created media.
        existing_vids = set(self.client.eval(
            "Array.from(document.querySelectorAll('video, a[href*=\\\"media.getMediaUrlRedirect\\\"]'))"
            ".map(el => el.src || el.href).filter(Boolean)"
        ) or [])
        self.client.click_el("b => b.innerText && b.innerText.includes('arrow_forward')")

        for i in range(55):
            time.sleep(3)
            curr_vids = self.client.eval(
                "Array.from(document.querySelectorAll('video, a[href*=\\\"media.getMediaUrlRedirect\\\"]'))"
                ".map(el => el.src || el.href).filter(Boolean)"
            ) or []
            new_vids = [
                v for v in curr_vids
                if v not in existing_vids
                and 'media.getMediaUrlRedirect' in v
                and 'MEDIA_URL_TYPE_THUMBNAIL' not in v
            ]
            if new_vids:
                vid_url = new_vids[-1]
                ok = self.client.download_video_by_url(vid_url, out_mp4)
                if ok:
                    subprocess.run([
                        'ffmpeg', '-sseof', '-0.1', '-i', out_mp4,
                        '-update', '1', '-q:v', '1', out_end_frame, '-y'
                    ], check=True)
                    print(f"-> Klip kaydedildi: {out_mp4}")
                    print(f"-> Son kare continuity referansı hazır: {out_end_frame}")
                    return True
            print(f"[{i * 3}s] Google Flow render alıyor...")
        raise RuntimeError(f"Klip üretimi zaman aşımına uğradı: {out_mp4}")

    def produce_3x10s_shorts(
        self,
        base_image_path,
        food_name,
        action_clip1_prebite,
        action_clip2_postbite,
        action_clip3_finale,
        output_mp4,
        character_reference_path=None,
    ):
        print("\n=======================================================")
        print(f"🚀 PROFESYONEL AI MUKBANG ÜRETİMİ: {food_name.upper()}")
        print("=======================================================")

        character_reference_path = character_reference_path or self.character_reference
        if not os.path.exists(character_reference_path):
            raise FileNotFoundError(
                "Karakter tutarlılığı için creator_face_ref.jpg zorunlu. "
                f"Beklenen dosya: {character_reference_path}"
            )

        c1_mp4 = f"{self.workdir}/prod_c1.mp4"
        c1_end = f"{self.workdir}/prod_c1_end.jpg"
        c2_mp4 = f"{self.workdir}/prod_c2.mp4"
        c2_end = f"{self.workdir}/prod_c2_end.jpg"
        c3_mp4 = f"{self.workdir}/prod_c3.mp4"
        c3_end = f"{self.workdir}/prod_c3_end.jpg"

        # CLIP 1: master identity + initial scene frame.
        p1 = self.build_clip_prompt(action_clip1_prebite, has_start_frame=bool(base_image_path))
        print("\n[ADIM 1/3] Klip 1 (Pre-Bite / Deep Dip) üretiliyor...")
        self.generate_single_clip(
            p1, base_image_path, c1_mp4, c1_end, character_reference_path
        )
        time.sleep(3)

        # CLIP 2: SAME character reference + previous final frame.
        p2 = self.build_clip_prompt(action_clip2_postbite, has_start_frame=True)
        print("\n[ADIM 2/3] Klip 2 (Post-Bite / Reaction) üretiliyor...")
        self.generate_single_clip(
            p2, c1_end, c2_mp4, c2_end, character_reference_path
        )
        time.sleep(3)

        # CLIP 3: SAME character reference + previous final frame.
        p3 = self.build_clip_prompt(action_clip3_finale, has_start_frame=True)
        print("\n[ADIM 3/3] Klip 3 (Glaze & Thumbs Up Finale) üretiliyor...")
        self.generate_single_clip(
            p3, c2_end, c3_mp4, c3_end, character_reference_path
        )

        # POST-PRODUCTION
        print("\n[KURGU] Renk Doygunluğu (+12% Vibrance) ve 9:16 Master Render yapılıyor...")
        converted = []
        for i, f in enumerate([c1_mp4, c2_mp4, c3_mp4]):
            out = f"{self.workdir}/prod_norm_{i + 1}.mp4"
            cmd = [
                'ffmpeg', '-i', f,
                '-vf', 'crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920,fps=30,eq=saturation=1.12:contrast=1.05',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '18',
                '-an', out, '-y'
            ]
            subprocess.run(cmd, check=True)
            converted.append(out)

        concat_txt = f"{self.workdir}/prod_final_concat.txt"
        with open(concat_txt, 'w') as f:
            for c in converted:
                f.write(f"file '{c}'\n")

        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_txt,
            '-c:v', 'copy', output_mp4, '-y'
        ], check=True)
        print(f"\n✨ PROFESYONEL MUKBANG SHORTS TAMAMLANDI: {output_mp4}")
        return output_mp4


if __name__ == '__main__':
    print("ProfessionalMukbangPipeline v5.0 — persistent character reference + continuity frame.")
