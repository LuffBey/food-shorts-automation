import json
import time
import base64
import os
import subprocess
from inspect_flow_agent import FlowClient

WORKDIR = "/root/hermes-projects/food-discovery-automation"

# 1. Flow image generation for BrandSet_Master
# In Agent mode, we can generate an image by asking the Agent or setting image mode.
# Let's inspect how Flow Agent generates image or if Nano Banana 2 is configured for image defaults.

def generate_master_image(client):
    prompt_master = (
        "Using @Creator, generate a high quality photorealistic reference portrait image (9:16 vertical). "
        "Male food creator with short dark buzzcut hair and neat light stubble, smiling with closed mouth directly at camera. "
        "Wearing a solid plain black crew-neck t-shirt. "
        "Seated centered at a smooth dark walnut wooden table (#7A4A2A) with long horizontal wood grain (no checkerboard, no butcher block). "
        "Directly on the table slightly to the left sits a single small shallow bright white ceramic sauce bowl containing thick glossy dark amber-red BBQ sauce (#8B1E0F). "
        "In his right hand he holds a single large crispy golden-brown fried chicken tender, completely unbitten and dry. Left hand resting naturally on the wooden table. "
        "Background is a seamless solid matte burnt-orange studio wall (#D9682E) with very subtle soft center ambient warmth (#E98745), zero kitchens, zero cabinets, zero decor, zero lamps, zero text. "
        "Clean 50mm eye-level perspective, crisp natural lighting from camera-left, sharp focus on creator, food and sauce bowl, vertical 9:16."
    )
    
    # Focus editor and clear
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
    client.cdp('Input.insertText', {'text': prompt_master})
    time.sleep(1)
    
    # Click Agent arrow_forward button
    client.eval("""
    (() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const sendBtn = btns.find(b => b.innerText && b.innerText.includes('arrow_forward'));
        if (sendBtn) sendBtn.click();
    })()
    """)
    print("Submitted Master BrandSet prompt to Flow Agent. Waiting...")
    time.sleep(10)
    
    # Monitor for new image / video in gallery
    start_t = time.time()
    while time.time() - start_t < 180:
        time.sleep(4)
        info = client.eval("""
        (() => {
            const body = document.body.innerText;
            const percent = (body.match(/\\d+%/g) || [])[0];
            const imgs = Array.from(document.querySelectorAll('img[src*="media"], img[src*="blob"], img[src*="googleusercontent"]'))
                .map(i => i.src);
            const vids = Array.from(document.querySelectorAll('video')).map(v => v.src || v.currentSrc);
            return {
                percent,
                imgs: imgs.slice(0, 5),
                vids: vids.slice(0, 5)
            };
        })()
        """)
        print(f"[{int(time.time() - start_t)}s] Progress: {info.get('percent')} | Vids: {len(info.get('vids', []))}")
        if not info.get('percent'):
            break

if __name__ == '__main__':
    c = FlowClient()
    generate_master_image(c)
