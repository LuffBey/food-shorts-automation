import json
import time
import base64
import os
import subprocess
from inspect_flow_agent import FlowClient

WORKDIR = "/root/hermes-projects/food-discovery-automation"

# 1. Base Anchors Definition
# Scene & Food Anchor: Single crispy fried chicken tender, white ceramic sauce bowl with glossy BBQ sauce, warm wooden butcher-block table, plain black crewneck shirt, warm cozy studio lighting, fixed medium shot (waist-up / chest-up).

def prepare_clean_flow(client):
    # Ensure Agent mode is selected and confirm-before-generating is Never, 9:16, 10s, x1, Omni 1.1 Flash
    print("Verifying Flow settings...")
    client.eval("""
    (() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const ajanBtn = btns.find(b => b.innerText && b.innerText.trim() === 'Ajan');
        if (ajanBtn) ajanBtn.click();
    })()
    """)
    time.sleep(1)

def run_agent_generation(client, prompt_text, start_frame_path=None):
    print(f"\n--- Submitting to Flow Agent ---")
    print(f"Prompt: {prompt_text[:140]}...")
    if start_frame_path:
        print(f"Loading Start Frame: {start_frame_path}")
        doc = client.cdp('DOM.getDocument', {'depth': -1})
        root_node_id = doc['result']['root']['nodeId']
        node_info = client.cdp('DOM.querySelector', {'nodeId': root_node_id, 'selector': 'input[type="file"]'})
        if node_info and 'result' in node_info and 'nodeId' in node_info['result']:
            file_node_id = node_info['result']['nodeId']
            client.cdp('DOM.setFileInputFiles', {'files': [start_frame_path], 'nodeId': file_node_id})
            time.sleep(2)
            print("Start Frame successfully attached to input.")

    # Focus & clear editor
    client.eval("""
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
    client.cdp('Input.insertText', {'text': prompt_text})
    time.sleep(1)

    # Click Agent arrow_forward button
    client.eval("""
    (() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const sendBtn = btns.find(b => b.innerText && b.innerText.includes('arrow_forward'));
        if (sendBtn) sendBtn.click();
    })()
    """)
    print("Submitted. Waiting for generation...")
    time.sleep(8)
    
    start_t = time.time()
    while time.time() - start_t < 360:
        time.sleep(5)
        status = client.eval("""
        (() => {
            const body = document.body.innerText;
            const percent = (body.match(/\\d+%/g) || [])[0];
            const hasFailed = body.includes('Başarısız') || body.includes('Olağan dışı');
            const vids = Array.from(document.querySelectorAll('video')).map(v => v.src || v.currentSrc);
            return {
                percent,
                hasFailed,
                topVideo: vids[0] || null
            };
        })()
        """)
        print(f"[{int(time.time() - start_t)}s] Progress: {status.get('percent')} | Failed: {status.get('hasFailed')}")
        if not status.get('percent') and status.get('topVideo'):
            return status.get('topVideo')
        if status.get('hasFailed') and not status.get('percent'):
            raise RuntimeError("Generation failed on Flow.")
            
    raise TimeoutError("Flow generation timed out.")

def download_video_blob(client, media_url, out_path):
    res = client.eval(f"""
    (async () => {{
        try {{
            const resp = await fetch({json.dumps(media_url)});
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
    print(f"Downloaded video -> {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    c = FlowClient()
    prepare_clean_flow(c)
