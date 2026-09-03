import json
import time
import base64
import os
import subprocess
from inspect_flow_agent import FlowClient

WORKDIR = "/root/hermes-projects/food-discovery-automation"

def run_pipeline():
    c = FlowClient()
    
    # Define 3 prompts maintaining character, scene, wardrobe continuity
    # Clip 1: Food hook + showcase product + first slow deep dip into glossy sauce
    prompt_clip1 = (
        "Using @Creator, create a 10-second vertical 9:16 video. "
        "Male creator in plain black crew-neck shirt sitting at a warm wooden table. "
        "Powerful food hook: holding a golden-brown extra-crispy fried chicken tender, "
        "slowly dipping it into a small bowl of thick glossy barbecue sauce, subtle smiling eye contact, "
        "warm studio lighting, appetizing crunchy texture, cinematic ASMR, same creator identity."
    )
    
    # Clip 2: Continuation from Clip 1 -> raising dipped chicken, taking a big crispy bite, crunch texture & natural delighted reaction
    prompt_clip2 = (
        "Using @Creator, continuing seamlessly from previous frame, create a 10-second vertical 9:16 video. "
        "Male creator in plain black crew-neck shirt sitting at the same warm wooden table. "
        "He lifts the sauce-dipped crispy fried chicken tender to his mouth, takes a huge crunchy bite, "
        "visible flaky breading crunch, authentic mouthwatering food reaction, chewing happily, "
        "warm studio lighting, exact same creator identity, no cuts, no wardrobe change."
    )
    
    # Clip 3: Continuation from Clip 2 -> final glazed bite, showing remaining juicy tender, nodding in delicious approval, closing reaction
    prompt_clip3 = (
        "Using @Creator, continuing seamlessly from previous frame, create a 10-second vertical 9:16 video. "
        "Male creator in plain black crew-neck shirt sitting at the same warm wooden table. "
        "He shows the juicy interior of the crispy fried chicken tender, takes a final savory bite with glossy glaze, "
        "nods head in genuine culinary satisfaction, relaxed pleasant smile to camera, warm studio lighting, "
        "exact same creator identity, perfect ending reaction."
    )

    prompts = [
        ("clip_1", prompt_clip1),
        ("clip_2", prompt_clip2),
        ("clip_3", prompt_clip3)
    ]
    
    video_files = []
    
    for idx, (clip_name, prompt) in enumerate(prompts, start=1):
        print(f"\n==========================================")
        print(f"  STARTING {clip_name.upper()} (Step {idx}/3)")
        print(f"==========================================")
        
        # If clip 2 or clip 3, we can upload the continuation frame from previous clip if needed
        if idx > 1:
            prev_video = video_files[idx - 2]
            cont_frame = os.path.join(WORKDIR, f"{clip_name}_cont_start.jpg")
            subprocess.run([
                'ffmpeg', '-y', '-ss', '00:00:09.500', '-i', prev_video,
                '-vframes', '1', '-q:v', '2', cont_frame
            ], check=True)
            print(f"Extracted continuation start frame: {cont_frame}")
            
            # Upload continuation frame into flow input
            doc = c.cdp('DOM.getDocument', {'depth': -1})
            root_node_id = doc['result']['root']['nodeId']
            node_info = c.cdp('DOM.querySelector', {'nodeId': root_node_id, 'selector': 'input[type="file"]'})
            if node_info and 'result' in node_info and 'nodeId' in node_info['result']:
                file_node_id = node_info['result']['nodeId']
                c.cdp('DOM.setFileInputFiles', {'files': [cont_frame], 'nodeId': file_node_id})
                time.sleep(2)
                print(f"Continuation frame loaded into composer.")

        # Focus & clean editor
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
        c.cdp('Input.insertText', {'text': prompt})
        time.sleep(1)
        
        # Submit via Agent arrow_forward button
        c.eval("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const sendBtn = btns.find(b => b.innerText && b.innerText.includes('arrow_forward'));
            if (sendBtn) sendBtn.click();
        })()
        """)
        print(f"Prompt submitted for {clip_name}. Monitoring generation...")
        
        # Wait for generation to start and finish
        time.sleep(8)
        start_t = time.time()
        completed_media_url = None
        
        while time.time() - start_t < 360:
            time.sleep(5)
            status = c.eval("""
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
            
            print(f"[{int(time.time() - start_t)}s] {clip_name} Status: Progress={status.get('percent')} | Failed={status.get('hasFailed')}")
            
            if not status.get('percent') and status.get('topVideo'):
                completed_media_url = status.get('topVideo')
                break
                
            if status.get('hasFailed') and not status.get('percent'):
                raise RuntimeError(f"{clip_name} generation failed on Flow platform.")
        
        if not completed_media_url:
            raise TimeoutError(f"{clip_name} timed out.")
            
        out_vid_path = os.path.join(WORKDIR, f"flow_agent_{clip_name}.mp4")
        
        # Download video blob
        res = c.eval(f"""
        (async () => {{
            try {{
                const resp = await fetch({json.dumps(completed_media_url)});
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
        with open(out_vid_path, 'wb') as f:
            f.write(base64.b64decode(b64))
            
        print(f"Successfully saved {clip_name} to {out_vid_path} ({os.path.getsize(out_vid_path)} bytes)")
        video_files.append(out_vid_path)
        time.sleep(3)

    # Concat the 3 clips into a single 30s Shorts video
    concat_list_path = os.path.join(WORKDIR, "concat_agent_3x10s.txt")
    with open(concat_list_path, "w") as f:
        for vf in video_files:
            f.write(f"file '{vf}'\n")
            
    final_output_path = os.path.join(WORKDIR, "flow_agent_shorts_30s_final.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_list_path, '-c', 'copy', final_output_path
    ], check=True)
    
    print(f"\n==========================================")
    print(f"  ALL 3 CLIPS GENERATED & CONCATENATED!")
    print(f"  Final video: {final_output_path}")
    print(f"==========================================")

if __name__ == '__main__':
    run_pipeline()
