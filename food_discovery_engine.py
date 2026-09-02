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
        if not head: return None
        length = head[1] & 0x7F
        if length == 126:
            length = int.from_bytes(self.s.recv(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.s.recv(8), 'big')
        data = bytearray()
        while len(data) < length:
            chunk = self.s.recv(length - len(data))
            if not chunk: break
            data.extend(chunk)
        return data.decode('utf-8', errors='ignore')

    def cdp(self, method, params=None):
        self.msg_id += 1
        curr_id = self.msg_id
        payload = {'id': curr_id, 'method': method}
        if params: payload['params'] = params
        self._send(json.dumps(payload))
        while True:
            res_str = self._recv()
            if not res_str: break
            try:
                res = json.loads(res_str)
                if res.get('id') == curr_id:
                    return res
            except:
                pass
        return None

    def eval(self, expr):
        res = self.cdp('Runtime.evaluate', {'expression': expr, 'returnByValue': True, 'awaitPromise': True})
        return res.get('result', {}).get('result', {}).get('value')

    def click_el(self, js_find):
        box = self.eval(f"""
        (() => {{
            const btns = Array.from(document.querySelectorAll('button, div[role="button"], span[role="button"], div[contenteditable="true"]'));
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
        self.cdp('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
        self.cdp('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
        return True

    def set_start_frame(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Start frame dosyası bulunamadı: {image_path}")
        
        # DOM.getDocument with depth to ensure subframes/inputs exist
        doc = self.cdp('DOM.getDocument', {'depth': -1})
        root_node_id = doc['result']['root']['nodeId']
        node_info = self.cdp('DOM.querySelector', {'nodeId': root_node_id, 'selector': 'input[type="file"]'})
        if not node_info or 'result' not in node_info or 'nodeId' not in node_info['result'] or node_info['result']['nodeId'] == 0:
            print("Warning: querySelector nodeId 0, trying direct element focus...")
            return False
        file_node_id = node_info['result']['nodeId']
        self.cdp('DOM.setFileInputFiles', {'files': [image_path], 'nodeId': file_node_id})
        time.sleep(2)
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
            self.cdp('Input.dispatchKeyEvent', {'type': 'keyDown', 'text': char, 'unmodifiedText': char})
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
        
        self.negative_rules = (
            "Exclude: extra fingers, fused fingers, distorted teeth, mouth morphing, "
            "food sticking to facial skin, floating objects, camera drifting, background shifts, "
            "steam, smoke, vapor, blurry sauce, cartoonish artifacts. Silent, hyper-realistic, 4k."
        )

    def ensure_video_settings(self):
        print("Flow Video Ayarları Yapılandırılıyor (Omni 1.1 Flash, 9:16, 10s)...")
        # Ensure 9:16 is active
        self.client.click_el("b => b.innerText && (b.innerText.includes('Banana') || b.innerText.includes('Omni') || b.innerText.includes('Veo') || b.innerText.includes('Video'))")
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

    def build_clip_prompt(self, delta_action):
        return f"{delta_action} {self.negative_rules}"

    def generate_single_clip(self, full_prompt, start_frame_path, out_mp4, out_end_frame):
        # 1. Start Frame Beslemesi
        if start_frame_path and os.path.exists(start_frame_path):
            print(f"-> Keyframe / Start Frame besleniyor: {start_frame_path}")
            self.client.set_start_frame(start_frame_path)

        # 2. Bounded Action Delta Prompt Girişi
        print(f"-> Güçlendirilmiş Prompt: {full_prompt[:120]}...")
        self.client.set_prompt(full_prompt)

        # 3. Tetikle
        existing_vids = set(self.client.eval("Array.from(document.querySelectorAll('video, a[href*=\"media.getMediaUrlRedirect\"]')).map(el => el.src || el.href).filter(Boolean)") or [])
        self.client.click_el("b => b.innerText && b.innerText.includes('arrow_forward')")

        # 4. Doğrula & İndir
        for i in range(55):
            time.sleep(3)
            curr_vids = self.client.eval("Array.from(document.querySelectorAll('video, a[href*=\"media.getMediaUrlRedirect\"]')).map(el => el.src || el.href).filter(Boolean)") or []
            new_vids = [v for v in curr_vids if v not in existing_vids and 'media.getMediaUrlRedirect' in v and 'MEDIA_URL_TYPE_THUMBNAIL' not in v]
            if new_vids:
                vid_url = new_vids[-1]
                ok = self.client.download_video_by_url(vid_url, out_mp4)
                if ok:
                    subprocess.run(['ffmpeg', '-sseof', '-0.1', '-i', out_mp4, '-update', '1', '-q:v', '1', out_end_frame, '-y'], check=True)
                    print(f"-> Klip kaydedildi: {out_mp4}")
                    print(f"-> Son kare referansı hazır: {out_end_frame}")
                    return True
            print(f"[{i*3}s] Google Flow render alıyor...")
        raise RuntimeError(f"Klip üretimi zaman aşımına uğradı: {out_mp4}")

    def produce_3x10s_shorts(self, base_image_path, food_name, action_clip1_prebite, action_clip2_postbite, action_clip3_finale, output_mp4):
        print(f"\n=======================================================")
        print(f"🚀 PROFESYONEL AI MUKBANG ÜRETİMİ: {food_name.upper()}")
        print(f"=======================================================")

        c1_mp4 = f"{self.workdir}/prod_c1.mp4"
        c1_end = f"{self.workdir}/prod_c1_end.jpg"
        c2_mp4 = f"{self.workdir}/prod_c2.mp4"
        c2_end = f"{self.workdir}/prod_c2_end.jpg"
        c3_mp4 = f"{self.workdir}/prod_c3.mp4"
        c3_end = f"{self.workdir}/prod_c3_end.jpg"

        # KLIP 1: Pre-Bite / Deep Dip
        p1 = self.build_clip_prompt(action_clip1_prebite)
        print("\n[ADIM 1/3] Klip 1 (Pre-Bite / Deep Dip) üretiliyor...")
        self.generate_single_clip(p1, base_image_path, c1_mp4, c1_end)
        time.sleep(3)

        # KLIP 2: Post-Bite / Reaction
        p2 = self.build_clip_prompt(action_clip2_postbite)
        print("\n[ADIM 2/3] Klip 2 (Post-Bite / Reaction) üretiliyor...")
        self.generate_single_clip(p2, c1_end, c2_mp4, c2_end)
        time.sleep(3)

        # KLIP 3: Finale / Thumbs Up
        p3 = self.build_clip_prompt(action_clip3_finale)
        print("\n[ADIM 3/3] Klip 3 (Glaze & Thumbs Up Finale) üretiliyor...")
        self.generate_single_clip(p3, c2_end, c3_mp4, c3_end)

        # POST-PRODÜKSİYON
        print("\n[KURGU] Renk Doygunluğu (+12% Vibrance) ve 9:16 Master Render yapılıyor...")
        converted = []
        for i, f in enumerate([c1_mp4, c2_mp4, c3_mp4]):
            out = f"{self.workdir}/prod_norm_{i+1}.mp4"
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

        subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_txt, '-c:v', 'copy', output_mp4, '-y'], check=True)
        print(f"\n✨ PROFESYONEL MUKBANG SHORTS TAMAMLANDI: {output_mp4}")
        return output_mp4

if __name__ == '__main__':
    print("ProfessionalMukbangPipeline v4.1 Güncellendi.")
