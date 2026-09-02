import socket
import json
import base64
import mimetypes
import os
import time
import urllib.request
import subprocess


class FlowClient:
    def __init__(self, port=9222):
        self.port = port
        self.connect()

    def connect(self):
        pages = json.loads(
            urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/list').read().decode()
        )
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
        else:
            frame.append(0x80 | 127)
            frame.extend(length.to_bytes(8, 'big'))
        mask = os.urandom(4)
        frame.extend(mask)
        frame.extend(bytearray(b ^ mask[i % 4] for i, b in enumerate(data)))
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
        }) or {}
        return res.get('result', {}).get('result', {}).get('value')

    def click_el(self, js_find):
        box = self.eval(f"""
        (() => {{
            const items = Array.from(document.querySelectorAll(
                'button, [role="button"], [role="menuitem"], [role="option"], div[contenteditable="true"]'
            ));
            const el = items.find({js_find});
            if (!el) return null;
            const rect = el.getBoundingClientRect();
            if (!rect.width || !rect.height) return null;
            el.scrollIntoView({{block: 'center', inline: 'center'}});
            return {{x: rect.left + rect.width / 2, y: rect.top + rect.height / 2}};
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

    def click_text(self, terms):
        terms = [t.lower() for t in terms]
        return self.click_el(
            "el => {"
            "const text=((el.innerText||'')+' '+(el.getAttribute('aria-label')||'')+' '+"
            "(el.getAttribute('title')||'')).toLowerCase();"
            f"return {json.dumps(terms)}.some(t => text.includes(t));"
            "}"
        )

    def _file_inputs(self):
        return self.eval("""
        (() => Array.from(document.querySelectorAll('input[type="file"]')).map((el, index) => {
            let node = el;
            let text = '';
            for (let depth = 0; depth < 7 && node; depth++, node = node.parentElement) {
                text += ' ' + (node.innerText || '') + ' ' +
                        (node.getAttribute?.('aria-label') || '') + ' ' +
                        (node.getAttribute?.('title') || '');
            }
            return {
                index,
                accept: el.accept || '',
                multiple: !!el.multiple,
                disabled: !!el.disabled,
                text: text.replace(/\\s+/g, ' ').trim().slice(0, 1200)
            };
        }))()
        """) or []

    def _choose_image_input_index(self):
        inputs = self._file_inputs()
        candidates = []
        for item in inputs:
            if item.get('disabled'):
                continue
            accept = (item.get('accept') or '').lower()
            if not accept or 'image' in accept or '.jpg' in accept or '.png' in accept:
                candidates.append(item)
        if not candidates:
            return None

        def score(item):
            text = (item.get('text') or '').lower()
            value = 0
            for kw in (
                'ingredient', 'reference', 'add image', 'upload', 'media',
                'içerik', 'referans', 'görsel', 'resim', 'yükle', 'medya'
            ):
                if kw in text:
                    value += 5
            if 'character' in text or 'karakter' in text:
                value += 2
            if 'video' in (item.get('accept') or '').lower():
                value -= 2
            return value

        best = sorted(candidates, key=score, reverse=True)[0]
        print(
            f"-> Image upload input seçildi: index={best['index']} "
            f"accept={best.get('accept', '')} context={best.get('text', '')[:180]}"
        )
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

        event_result = self.eval(f"""
        (() => {{
            const input = document.querySelectorAll('input[type="file"]')[{int(index)}];
            if (!input) return false;
            input.dispatchEvent(new Event('input', {{bubbles: true, composed: true}}));
            input.dispatchEvent(new Event('change', {{bubbles: true, composed: true}}));
            return Array.from(input.files || []).map(f => f.name);
        }})()
        """)
        print(f"-> File input events dispatched: {event_result}")
        time.sleep(1.5)
        return True

    def _prompt_attachment_snapshot(self):
        return self.eval("""
        (() => {
            const editor = document.querySelector('[data-slate-editor="true"]');
            const root = editor?.closest('form') || editor?.parentElement?.parentElement?.parentElement ||
                         document.body;
            const imgs = Array.from(root.querySelectorAll('img')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.width >= 24 && r.height >= 24;
            });
            const removeButtons = Array.from(root.querySelectorAll('button,[role="button"]')).filter(el => {
                const t = ((el.getAttribute('aria-label') || '') + ' ' +
                           (el.getAttribute('title') || '') + ' ' +
                           (el.innerText || '')).toLowerCase();
                return ['remove', 'delete', 'close', 'kaldır', 'sil'].some(x => t.includes(x));
            });
            return {
                imageCount: imgs.length,
                removeCount: removeButtons.length,
                bodyText: (root.innerText || '').slice(0, 1500)
            };
        })()
        """) or {}

    def _attachment_changed(self, before):
        after = self._prompt_attachment_snapshot()
        return (
            after.get('imageCount', 0) > before.get('imageCount', 0)
            or after.get('removeCount', 0) > before.get('removeCount', 0)
        )

    def _drag_file_to_prompt(self, image_path):
        mime = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
        with open(image_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('ascii')
        filename = os.path.basename(image_path)
        return bool(self.eval(f"""
        (() => {{
            const editor = document.querySelector('[data-slate-editor="true"]');
            if (!editor) return false;
            const target = editor.closest('form') || editor.parentElement?.parentElement || editor;
            const bytes = Uint8Array.from(atob({json.dumps(encoded)}), c => c.charCodeAt(0));
            const file = new File([bytes], {json.dumps(filename)}, {{type: {json.dumps(mime)}}});
            const dt = new DataTransfer();
            dt.items.add(file);
            for (const type of ['dragenter', 'dragover', 'drop']) {{
                target.dispatchEvent(new DragEvent(type, {{
                    bubbles: true,
                    cancelable: true,
                    composed: true,
                    dataTransfer: dt
                }}));
            }}
            return true;
        }})()
        """))

    def _open_add_image_uploader(self):
        clicked = self.click_text([
            'add image', 'add media', 'görsel ekle', 'resim ekle',
            'medya ekle', 'add_photo', 'add photo'
        ])
        if clicked:
            time.sleep(0.7)
            self.click_text(['upload', 'media', 'yükle', 'medya'])
            time.sleep(0.7)
        return clicked

    def attach_ingredient(self, image_path, label='ingredient'):
        if not image_path or not os.path.exists(image_path):
            raise FileNotFoundError(f"{label} bulunamadı: {image_path}")

        before = self._prompt_attachment_snapshot()
        self._open_add_image_uploader()

        index = self._choose_image_input_index()
        if index is not None and self._set_file_input_by_index(index, image_path):
            for _ in range(12):
                time.sleep(0.5)
                if self._attachment_changed(before):
                    print(f"-> Flow application attachment accepted: {label}")
                    return True

        print(f"-> Direct input ingestion görünmedi; drag/drop fallback deneniyor: {label}")
        before_drag = self._prompt_attachment_snapshot()
        if self._drag_file_to_prompt(image_path):
            for _ in range(16):
                time.sleep(0.5)
                if self._attachment_changed(before_drag):
                    print(f"-> Drag/drop attachment accepted: {label}")
                    return True

        raise RuntimeError(
            f"Flow {label} dosyasını uygulama seviyesinde kabul etmedi: {image_path}. "
            "Dosya input.files içine girmiş olsa bile generation başlatılmayacak."
        )

    def clear_prompt_attachments(self):
        removed = self.eval("""
        (() => {
            const editor = document.querySelector('[data-slate-editor="true"]');
            const root = editor?.closest('form') || editor?.parentElement?.parentElement?.parentElement;
            if (!root) return 0;
            let count = 0;
            for (const el of Array.from(root.querySelectorAll('button,[role="button"]'))) {
                const t = ((el.getAttribute('aria-label') || '') + ' ' +
                           (el.getAttribute('title') || '')).toLowerCase();
                if (['remove image', 'remove attachment', 'delete image',
                     'görseli kaldır', 'resmi kaldır', 'eki kaldır'].some(x => t.includes(x))) {
                    el.click();
                    count += 1;
                }
            }
            return count;
        })()
        """) or 0
        if removed:
            print(f"-> Önceki prompt attachment'ları temizlendi: {removed}")
            time.sleep(0.8)
        return removed

    def ensure_ingredients_mode(self):
        print("Flow Ingredients/References modu yapılandırılıyor (Omni Flash 1.1, 9:16, 10s)...")

        if not self.click_text(['nano banana', 'omni', 'veo', 'model']):
            self.click_text(['video settings', 'generation settings', 'ayarlar'])
        time.sleep(0.6)

        self.click_text(['video', 'videocam'])
        time.sleep(0.5)

        ingredients_clicked = self.click_text([
            'ingredients', 'references', 'ingredient', 'reference',
            'malzemeler', 'referanslar', 'referans'
        ])
        if not ingredients_clicked:
            raise RuntimeError(
                "Flow Video > Ingredients/References modu bulunamadı. "
                "Omni 1.1 Flash için reference mode aktif olmadan üretim yapılmayacak."
            )
        time.sleep(0.6)

        self.click_text(['omni 1.1 flash', 'omni flash', 'omni'])
        time.sleep(0.4)
        self.click_text(['9:16', 'crop_9_16'])
        time.sleep(0.3)
        self.click_text(['x1', '1 output', '1 sonuç'])
        time.sleep(0.3)
        self.click_text(['10s', '10 s', '10 sn', '10 saniye'])
        time.sleep(0.4)
        return True

    def set_prompt(self, text):
        focused = self.eval("""
        (() => {
            const el = document.querySelector('[data-slate-editor="true"]');
            if (!el) return false;
            el.focus();
            const range = document.createRange();
            range.selectNodeContents(el);
            range.collapse(false);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            return document.activeElement === el;
        })()
        """)
        if not focused:
            raise RuntimeError("Flow prompt editor could not receive focus")

        self.cdp('Input.dispatchKeyEvent', {
            'type': 'rawKeyDown', 'key': 'Control', 'code': 'ControlLeft',
            'windowsVirtualKeyCode': 17, 'nativeVirtualKeyCode': 17, 'modifiers': 2,
        })
        self.cdp('Input.dispatchKeyEvent', {
            'type': 'rawKeyDown', 'key': 'a', 'code': 'KeyA',
            'windowsVirtualKeyCode': 65, 'nativeVirtualKeyCode': 65, 'modifiers': 2,
        })
        self.cdp('Input.dispatchKeyEvent', {
            'type': 'keyUp', 'key': 'a', 'code': 'KeyA',
            'windowsVirtualKeyCode': 65, 'nativeVirtualKeyCode': 65, 'modifiers': 2,
        })
        self.cdp('Input.dispatchKeyEvent', {
            'type': 'keyUp', 'key': 'Control', 'code': 'ControlLeft',
            'windowsVirtualKeyCode': 17, 'nativeVirtualKeyCode': 17,
        })
        self.cdp('Input.dispatchKeyEvent', {
            'type': 'keyDown', 'key': 'Backspace', 'code': 'Backspace',
            'windowsVirtualKeyCode': 8, 'nativeVirtualKeyCode': 8,
        })
        self.cdp('Input.dispatchKeyEvent', {
            'type': 'keyUp', 'key': 'Backspace', 'code': 'Backspace',
            'windowsVirtualKeyCode': 8, 'nativeVirtualKeyCode': 8,
        })
        self.cdp('Input.insertText', {'text': text})
        time.sleep(0.3)

    def click_generate(self):
        if self.click_text(['generate', 'oluştur', 'üret', 'arrow_forward']):
            return True
        raise RuntimeError("Flow Generate button bulunamadı.")

    def download_video_by_url(self, vid_url, out_path):
        res = self.eval(f"""
        (async () => {{
            const resp = await fetch({json.dumps(vid_url)});
            const blob = await resp.blob();
            return new Promise((resolve, reject) => {{
                const reader = new FileReader();
                reader.onloadend = () => resolve({{size: blob.size, dataUrl: reader.result}});
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
            "REFERENCE ROLE 1 — CANONICAL PERSON: Use the first supplied ingredient as the exact "
            "identity source for the main performer. Preserve the same facial identity, facial geometry, "
            "eyes, nose, jawline, hairstyle, hair color, skin tone, apparent age and body proportions. "
            "Never replace, redesign, reinterpret or age-shift this person. "
        )
        self.scene_lock = (
            "REFERENCE ROLE 2 — CONTINUITY STATE: When a second ingredient is supplied, use it as the "
            "visual continuation state from the previous clip. Preserve the same wardrobe, table, plate, "
            "food styling, background, lighting, lens, camera height and color grade. Continue naturally "
            "from that state without introducing another person. "
        )
        self.negative_rules = (
            "One main performer only. No duplicate person, face swap, identity drift, hairstyle change, "
            "wardrobe change, mouth morphing, distorted teeth, extra fingers, fused fingers, floating "
            "objects, background replacement, camera teleport, smoke, vapor or cartoon artifacts. "
            "Photorealistic food-commercial cinematography."
        )

    def ensure_video_settings(self):
        return self.client.ensure_ingredients_mode()

    def build_clip_prompt(self, delta_action, has_continuity_reference=True):
        continuity = self.scene_lock if has_continuity_reference else ''
        return (
            f"{self.identity_lock}{continuity}"
            f"ACTION FOR THIS CLIP ONLY: {delta_action} "
            f"{self.negative_rules}"
        )

    def _resolve_character_reference(self, requested_path, base_image_path):
        for path in [requested_path, self.character_reference, base_image_path]:
            if path and os.path.exists(path):
                return path
        raise FileNotFoundError(
            "Karakter tutarlılığı için bir master görsel gerekli. "
            f"Beklenen: {self.character_reference} veya geçerli base_image_path."
        )

    def generate_single_clip(
        self,
        full_prompt,
        continuity_image_path,
        out_mp4,
        out_end_frame,
        character_reference_path,
    ):
        self.client.ensure_ingredients_mode()
        self.client.clear_prompt_attachments()

        print(f"-> Canonical character ingredient: {character_reference_path}")
        self.client.attach_ingredient(character_reference_path, 'canonical character reference')

        if continuity_image_path and os.path.exists(continuity_image_path):
            print(f"-> Continuity ingredient: {continuity_image_path}")
            self.client.attach_ingredient(continuity_image_path, 'previous-scene continuity reference')

        print(f"-> Prompt: {full_prompt[:220]}...")
        self.client.set_prompt(full_prompt)

        existing_vids = set(self.client.eval(
            """Array.from(document.querySelectorAll(
                'video, a[href*="media.getMediaUrlRedirect"]'
            )).map(el => el.src || el.href).filter(Boolean)"""
        ) or [])

        self.client.click_generate()

        for i in range(70):
            time.sleep(3)
            curr_vids = self.client.eval(
                """Array.from(document.querySelectorAll(
                    'video, a[href*="media.getMediaUrlRedirect"]'
                )).map(el => el.src || el.href).filter(Boolean)"""
            ) or []
            new_vids = [
                v for v in curr_vids
                if v not in existing_vids
                and 'media.getMediaUrlRedirect' in v
                and 'MEDIA_URL_TYPE_THUMBNAIL' not in v
            ]
            if new_vids:
                vid_url = new_vids[-1]
                if self.client.download_video_by_url(vid_url, out_mp4):
                    subprocess.run([
                        'ffmpeg', '-sseof', '-0.25', '-i', out_mp4,
                        '-frames:v', '1', '-q:v', '1', out_end_frame, '-y'
                    ], check=True)
                    print(f"-> Klip kaydedildi: {out_mp4}")
                    print(f"-> Continuity frame hazır: {out_end_frame}")
                    return True
            print(f"[{i * 3}s] Google Flow render bekleniyor...")

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

        character_reference_path = self._resolve_character_reference(
            character_reference_path, base_image_path
        )

        c1_mp4 = f"{self.workdir}/prod_c1.mp4"
        c1_end = f"{self.workdir}/prod_c1_end.jpg"
        c2_mp4 = f"{self.workdir}/prod_c2.mp4"
        c2_end = f"{self.workdir}/prod_c2_end.jpg"
        c3_mp4 = f"{self.workdir}/prod_c3.mp4"
        c3_end = f"{self.workdir}/prod_c3_end.jpg"

        p1 = self.build_clip_prompt(
            action_clip1_prebite,
            has_continuity_reference=bool(base_image_path and os.path.exists(base_image_path)),
        )
        print("\n[ADIM 1/3] Klip 1 üretiliyor...")
        self.generate_single_clip(
            p1,
            base_image_path if base_image_path and os.path.exists(base_image_path) else None,
            c1_mp4,
            c1_end,
            character_reference_path,
        )
        time.sleep(2)

        p2 = self.build_clip_prompt(action_clip2_postbite, has_continuity_reference=True)
        print("\n[ADIM 2/3] Klip 2 üretiliyor...")
        self.generate_single_clip(
            p2, c1_end, c2_mp4, c2_end, character_reference_path
        )
        time.sleep(2)

        p3 = self.build_clip_prompt(action_clip3_finale, has_continuity_reference=True)
        print("\n[ADIM 3/3] Klip 3 üretiliyor...")
        self.generate_single_clip(
            p3, c2_end, c3_mp4, c3_end, character_reference_path
        )

        print("\n[KURGU] 3 klip normalize edilip birleştiriliyor...")
        converted = []
        for i, src in enumerate([c1_mp4, c2_mp4, c3_mp4]):
            out = f"{self.workdir}/prod_norm_{i + 1}.mp4"
            subprocess.run([
                'ffmpeg', '-i', src,
                '-vf',
                'crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920,fps=30,'
                'eq=saturation=1.12:contrast=1.05',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-preset', 'fast', '-crf', '18', '-an', out, '-y'
            ], check=True)
            converted.append(out)

        concat_txt = f"{self.workdir}/prod_final_concat.txt"
        with open(concat_txt, 'w') as f:
            for clip in converted:
                f.write(f"file '{clip}'\n")

        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_txt,
            '-c:v', 'copy', output_mp4, '-y'
        ], check=True)

        print(f"\n✨ SHORTS TAMAMLANDI: {output_mp4}")
        return output_mp4


if __name__ == '__main__':
    print(
        "ProfessionalMukbangPipeline v6.0 — Omni 1.1 Ingredients identity lock "
        "+ React-aware upload + drag/drop fallback."
    )
