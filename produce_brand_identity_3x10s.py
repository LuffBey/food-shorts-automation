import os
import time
import subprocess
import json
import base64
from inspect_flow_agent import FlowClient

WORKDIR = "/root/hermes-projects/food-discovery-automation"
S0_PATH = os.path.join(WORKDIR, "S0_Master.jpg")

# PROMPT 1: S0 -> S1 (Dip into dark amber-red BBQ sauce, no mouth opening, no lip movement, mouth closed natural smile)
PROMPT_CLIP_1 = (
    "Using @Creator, seamlessly starting from the exact attached start frame S0, create a 10-second vertical 9:16 photorealistic video. "
    "Fixed locked tripod camera (50mm eye-level). "
    "Creator remains seated centered at the dark walnut wooden table (#7A4A2A) against the seamless solid matte burnt-orange studio background (#D9682E). "
    "He wears the solid plain black crew-neck t-shirt. White ceramic dipping bowl filled with dark amber-red BBQ sauce stays stationary on table. "
    "Action: He holds the intact crispy golden fried chicken tender, brings it down to the white bowl, slowly dips the bottom 25% into the dark amber-red BBQ sauce, "
    "then raises the sauce-dipped unbitten tender to chest level facing camera. "
    "STRICT NO SPEECH LOCK: Creator's mouth remains completely closed at all times. Zero speaking, zero whispering, zero lip movement, zero lip sync. Natural subtle smile with closed lips. "
    "For the final 1.5 seconds, hold completely steady: face, black shirt, dark amber-red dipped unbitten tender, white bowl, and burnt orange background locked in place. "
    "Audio: only realistic food ASMR sauce dipping and subtle room tone, zero speech, zero voices."
)

# PROMPT 2: S1 -> S2 (Single bite, natural short chewing, mouth closed, no talking)
PROMPT_CLIP_2 = (
    "Using @Creator, seamlessly continuing from the exact attached start frame S1, create a 10-second vertical 9:16 photorealistic video. "
    "Exact same fixed locked tripod camera, same solid matte burnt-orange background (#D9682E), same dark walnut table, same white bowl with dark amber-red BBQ sauce, same plain black shirt. "
    "Action: Creator brings the sauce-dipped crispy chicken tender to his mouth, takes exactly ONE single clean crunchy bite from the top end, revealing juicy white meat inside. "
    "He chews naturally and briefly with mouth closed, savoring the flavor with closed eyes in quiet culinary enjoyment. "
    "STRICT NO SPEECH LOCK: After the single bite, his mouth remains closed while chewing. Absolutely zero talking, zero lip flapping, zero mouthing words, zero speaking to camera. "
    "For the final 1.5 seconds, hold static pose: single-bitten tender held in hand, mouth closed in relaxed smile, white bowl and orange background steady. "
    "Audio: single crisp ASMR crunch sound, zero talking, zero voices, zero vocalizations."
)

# PROMPT 3: S2 -> S3 (Texture reveal & signature reaction: thumb up, closed mouth smile, no talking)
PROMPT_CLIP_3 = (
    "Using @Creator, seamlessly continuing from the exact attached start frame S2, create a 10-second vertical 9:16 photorealistic video. "
    "Exact same fixed locked tripod camera, same solid matte burnt-orange background (#D9682E), same dark walnut table, same white bowl, same plain black shirt. "
    "Action: Creator does NOT take any second bite. He gently tilts the single-bitten chicken tender forward to showcase the juicy, flaky interior texture to camera. "
    "With his other hand resting on the table, he gives a subtle small thumbs-up gesture while nodding gently with a closed-mouth smile of authentic approval. "
    "STRICT NO SPEECH LOCK: Mouth remains firmly closed throughout the entire video. Zero speech, zero talking, zero mouthing words, zero lip movement. Pure silent visual reaction. "
    "For the final 1.5 seconds, hold the static approved signature pose: single-bitten tender, small thumbs up, closed mouth smile, white bowl, orange background. "
    "Audio: subtle ambient room tone, zero voices, zero speech, zero music."
)

def run_agent_video(client, prompt_text, start_frame_path):
    print(f"\n--- Submitting Video Prompt to Flow Agent ---")
    print(f"Start Frame: {start_frame_path}")
    print(f"Prompt: {prompt_text[:120]}...")
    
    # Upload start frame
    doc = client.cdp('DOM.getDocument', {'depth': -1})
    root_node_id = doc['result']['root']['nodeId']
    node_info = client.cdp('DOM.querySelector', {'nodeId': root_node_id, 'selector': 'input[type="file"]'})
    if node_info and 'result' in node_info and 'nodeId' in node_info['result']:
        file_node_id = node_info['result']['nodeId']
        client.cdp('DOM.setFileInputFiles', {'files': [start_frame_path], 'nodeId': file_node_id})
        time.sleep(2)
        print("Start frame attached.")

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

def download_video(client, media_url, out_path):
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
    print(f"Saved {out_path} ({os.path.getsize(out_path)} bytes)")

def extract_frame(video_path, time_offset, out_path):
    subprocess.run([
        'ffmpeg', '-y', '-ss', str(time_offset), '-i', video_path,
        '-vframes', '1', '-q:v', '2', out_path
    ], check=True)
    print(f"Extracted {out_path}")

def main():
    c = FlowClient()
    
    # 1. Produce Clip 1 (S0 -> S1)
    print("\n==========================================")
    print("  PRODUCING CLIP 1 (Dip & Hold S1)")
    print("==========================================")
    c1_url = run_agent_video(c, PROMPT_CLIP_1, S0_PATH)
    c1_path = os.path.join(WORKDIR, "brand_clip_1.mp4")
    download_video(c, c1_url, c1_path)
    
    # Extract S1 (end frame of clip 1 at 9.5s) and start frame
    s1_path = os.path.join(WORKDIR, "S1_Frame.jpg")
    c1_start_path = os.path.join(WORKDIR, "C1_Start.jpg")
    c1_mid_path = os.path.join(WORKDIR, "C1_Mid.jpg")
    extract_frame(c1_path, "00:00:00.000", c1_start_path)
    extract_frame(c1_path, "00:00:05.000", c1_mid_path)
    extract_frame(c1_path, "00:00:09.500", s1_path)
    
    # 2. Produce Clip 2 (S1 -> S2)
    print("\n==========================================")
    print("  PRODUCING CLIP 2 (Single Bite & S2)")
    print("==========================================")
    c2_url = run_agent_video(c, PROMPT_CLIP_2, s1_path)
    c2_path = os.path.join(WORKDIR, "brand_clip_2.mp4")
    download_video(c, c2_url, c2_path)
    
    s2_path = os.path.join(WORKDIR, "S2_Frame.jpg")
    c2_start_path = os.path.join(WORKDIR, "C2_Start.jpg")
    c2_mid_path = os.path.join(WORKDIR, "C2_Mid.jpg")
    extract_frame(c2_path, "00:00:00.000", c2_start_path)
    extract_frame(c2_path, "00:00:05.000", c2_mid_path)
    extract_frame(c2_path, "00:00:09.500", s2_path)
    
    # 3. Produce Clip 3 (S2 -> S3)
    print("\n==========================================")
    print("  PRODUCING CLIP 3 (Texture Reveal & S3 Reaction)")
    print("==========================================")
    c3_url = run_agent_video(c, PROMPT_CLIP_3, s2_path)
    c3_path = os.path.join(WORKDIR, "brand_clip_3.mp4")
    download_video(c, c3_url, c3_path)
    
    s3_path = os.path.join(WORKDIR, "S3_Frame.jpg")
    c3_start_path = os.path.join(WORKDIR, "C3_Start.jpg")
    c3_mid_path = os.path.join(WORKDIR, "C3_Mid.jpg")
    extract_frame(c3_path, "00:00:00.000", c3_start_path)
    extract_frame(c3_path, "00:00:05.000", c3_mid_path)
    extract_frame(c3_path, "00:00:09.500", s3_path)
    
    print("\nAll 3 clips successfully generated on disk.")

if __name__ == '__main__':
    main()
