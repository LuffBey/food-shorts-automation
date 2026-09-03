import json
import base64
import os
import subprocess
from inspect_flow_agent import FlowClient

WORKDIR = "/root/hermes-projects/food-discovery-automation"
c = FlowClient()

# Get top video / media generated
top_media = c.eval("""
(() => {
    const vids = Array.from(document.querySelectorAll('video')).map(v => v.src || v.currentSrc);
    return vids[0] || null;
})()
""")

print("Top media URL:", top_media)
if top_media:
    out_path = os.path.join(WORKDIR, "brandset_raw.mp4")
    res = c.eval(f"""
    (async () => {{
        try {{
            const resp = await fetch({json.dumps(top_media)});
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

    # Extract first frame as BrandSet_Master
    master_frame = os.path.join(WORKDIR, "BrandSet_Master.jpg")
    subprocess.run([
        'ffmpeg', '-y', '-i', out_path,
        '-vf', 'select=eq(n\\,0)', '-vframes', '1', '-q:v', '2', master_frame
    ], check=True)
    print(f"Extracted BrandSet_Master.jpg: {master_frame}")
