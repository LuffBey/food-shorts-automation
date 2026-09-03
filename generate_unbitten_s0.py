import json
import time
import base64
import os
import subprocess
from inspect_flow_agent import FlowClient

WORKDIR = "/root/hermes-projects/food-discovery-automation"
c = FlowClient()

# Generate S0 frame: holding a 100% UNBITTEN, WHOLE, intact crispy fried chicken tender, exactly on this approved burnt orange background and dark walnut table
prompt_s0 = (
    "Using @Creator, generate a 9:16 vertical photorealistic image. "
    "Creator in plain black crew-neck shirt seated at the smooth dark walnut wooden table (#7A4A2A) with horizontal grain. "
    "Solid matte burnt-orange studio wall background (#D9682E) with soft warm center. "
    "Small white ceramic bowl filled with glossy dark amber-red BBQ sauce on the table slightly to the left. "
    "He holds a completely UNBITTEN, 100% whole, intact golden-brown crispy fried chicken tender in his right hand. "
    "No bites, no white meat exposed, fully breaded and unbitten. Left hand on table. Natural closed-mouth smile directly to camera. "
    "50mm eye-level perspective, clean studio lighting."
)

# Focus editor and clear
c.eval("""
(() => {
    const editor = document.querySelector('div[contenteditable="true"]');
    if (editor) {
        editor.focus();
        const range = document.createRange();
        range.selectNodeContents(editor);
        range.collapse(false);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    }
})()
""")
time.sleep(0.3)
c.cdp('Input.insertText', {'text': prompt_s0})
time.sleep(1)

# Click Agent arrow_forward button
c.eval("""
(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const sendBtn = btns.find(b => b.innerText && b.innerText.includes('arrow_forward'));
    if (sendBtn) sendBtn.click();
})()
""")
print("Submitted unbitten S0 prompt. Waiting for generation...")
time.sleep(10)

start_t = time.time()
while time.time() - start_t < 180:
    time.sleep(4)
    info = c.eval("""
    (() => {
        const body = document.body.innerText;
        const percent = (body.match(/\\d+%/g) || [])[0];
        const vids = Array.from(document.querySelectorAll('video')).map(v => v.src || v.currentSrc);
        return { percent, topVid: vids[0] || null };
    })()
    """)
    print(f"[{int(time.time() - start_t)}s] Progress: {info.get('percent')}")
    if not info.get('percent') and info.get('topVid'):
        break

# Download
out_path = os.path.join(WORKDIR, "brandset_s0_raw.mp4")
res = c.eval(f"""
(async () => {{
    try {{
        const resp = await fetch({json.dumps(info['topVid'])});
        const blob = await resp.blob();
        return new Promise((resolve) => {{
            const reader = new FileReader();
            reader.onloadend = () => resolve({{ dataUrl: reader.result }});
            reader.onerror = () => resolve({{ error: 'reader error' }});
            reader.readAsDataURL(blob);
        }});
    }} catch(e) {{
        return {{ error: e.toString() }};
    }}
}})()
""")
b64 = res['dataUrl'].split(',')[1]
with open(out_path, 'wb') as f:
    f.write(base64.b64decode(b64))

s0_frame = os.path.join(WORKDIR, "S0_Master.jpg")
subprocess.run([
    'ffmpeg', '-y', '-i', out_path,
    '-vf', 'select=eq(n\\,0)', '-vframes', '1', '-q:v', '2', s0_frame
], check=True)
print(f"Extracted S0_Master.jpg: {s0_frame}")
