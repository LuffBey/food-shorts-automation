import os
import time
import subprocess
from inspect_flow_agent import FlowClient
from flow_pipeline_v5 import prepare_clean_flow, run_agent_generation, download_video_blob

WORKDIR = "/root/hermes-projects/food-discovery-automation"

# Strict Master Anchors
# Scene Anchor: Fixed medium shot (waist-up/chest-up), same Creator, solid plain black crew-neck shirt, warm cozy wooden butcher-block table, white small ceramic sauce bowl with glossy dark BBQ sauce, warm indoor lighting, fixed camera height, identical lens and framing across all clips.
# Food Anchor: Exactly one single golden-brown extra-crispy fried chicken tender with thick crunchy panko/flaky batter.

PROMPT_CLIP_1 = (
    "Using @Creator, create a 10-second vertical 9:16 video. Fixed medium shot (chest-up), no camera motion. "
    "Creator sitting centered at a warm wooden table wearing a solid plain black crew-neck t-shirt. "
    "In front on the table sits a small white ceramic dipping bowl with glossy BBQ sauce. "
    "He holds a single golden-brown crispy fried chicken tender in his right hand, slowly dips the bottom into the sauce, "
    "then holds it up near chest level facing camera. For the final 1.5 seconds, freeze movement: face with natural smile, "
    "both hands, white bowl on table, and dipped unbitten crispy tender all clearly visible in frame. "
    "Warm studio lighting, zero steam, identical creator identity, 9:16."
)

PROMPT_CLIP_2 = (
    "Using @Creator, seamlessly continuing from the exact start frame, create a 10-second vertical 9:16 video. "
    "Exact same fixed medium shot, same Creator in plain black crew-neck shirt, same wooden table and white sauce bowl. "
    "He brings the exact same sauce-dipped fried chicken tender to his mouth and takes a clean single crunchy bite, "
    "showing golden crispy coating and juicy white meat. He chews with genuine satisfied enjoyment, eyes closed in delight. "
    "For the final 1.5 seconds, hold steady: single-bitten tender held in right hand, white bowl on table, face smiling, "
    "both hands visible. Exact same lighting, framing, and identity continuity, 9:16."
)

PROMPT_CLIP_3 = (
    "Using @Creator, seamlessly continuing from the exact start frame, create a 10-second vertical 9:16 video. "
    "Exact same fixed medium shot, same Creator in plain black crew-neck shirt, same wooden table and white sauce bowl. "
    "Holding the exact same single-bitten chicken tender, he dips the exposed bite back into the white sauce bowl for a rich glaze, "
    "takes the final savoring bite, and nods in authentic culinary approval with a relaxed, happy smile directly to camera. "
    "For the final 1.5 seconds, hold static closing satisfaction pose. Exact same identity, lighting, camera height, 9:16."
)

def extract_exact_end_frame(video_path, out_frame_path):
    subprocess.run([
        'ffmpeg', '-y', '-sseof', '-0.5', '-i', video_path,
        '-vframes', '1', '-q:v', '2', out_frame_path
    ], check=True)
    print(f"Extracted strict end frame: {out_frame_path}")

def extract_exact_start_frame(video_path, out_frame_path):
    subprocess.run([
        'ffmpeg', '-y', '-i', video_path,
        '-vf', 'select=eq(n\\,0)', '-vframes', '1', '-q:v', '2', out_frame_path
    ], check=True)
    print(f"Extracted strict start frame: {out_frame_path}")

def main():
    c = FlowClient()
    prepare_clean_flow(c)
    
    # ------------------ CLIP 1 ------------------
    print("\n>>> PRODUCING STRICT CLIP 1 <<<")
    clip1_url = run_agent_generation(c, PROMPT_CLIP_1, start_frame_path=None)
    clip1_path = os.path.join(WORKDIR, "strict_agent_c1.mp4")
    download_video_blob(c, clip1_url, clip1_path)
    
    clip1_end_frame = os.path.join(WORKDIR, "strict_c1_end.jpg")
    extract_exact_end_frame(clip1_path, clip1_end_frame)
    
    # ------------------ CLIP 2 ------------------
    print("\n>>> PRODUCING STRICT CLIP 2 WITH C1 END-FRAME <<<")
    clip2_url = run_agent_generation(c, PROMPT_CLIP_2, start_frame_path=clip1_end_frame)
    clip2_path = os.path.join(WORKDIR, "strict_agent_c2.mp4")
    download_video_blob(c, clip2_url, clip2_path)
    
    clip2_start_frame = os.path.join(WORKDIR, "strict_c2_start.jpg")
    clip2_end_frame = os.path.join(WORKDIR, "strict_c2_end.jpg")
    extract_exact_start_frame(clip2_path, clip2_start_frame)
    extract_exact_end_frame(clip2_path, clip2_end_frame)
    
    # ------------------ CLIP 3 ------------------
    print("\n>>> PRODUCING STRICT CLIP 3 WITH C2 END-FRAME <<<")
    clip3_url = run_agent_generation(c, PROMPT_CLIP_3, start_frame_path=clip2_end_frame)
    clip3_path = os.path.join(WORKDIR, "strict_agent_c3.mp4")
    download_video_blob(c, clip3_url, clip3_path)
    
    clip3_start_frame = os.path.join(WORKDIR, "strict_c3_start.jpg")
    clip3_end_frame = os.path.join(WORKDIR, "strict_c3_end.jpg")
    extract_exact_start_frame(clip3_path, clip3_start_frame)
    extract_exact_end_frame(clip3_path, clip3_end_frame)
    
    # ------------------ CONCAT ------------------
    concat_txt = os.path.join(WORKDIR, "strict_concat_list.txt")
    with open(concat_txt, "w") as f:
        f.write(f"file '{clip1_path}'\n")
        f.write(f"file '{clip2_path}'\n")
        f.write(f"file '{clip3_path}'\n")
        
    final_output = os.path.join(WORKDIR, "strict_flow_agent_30s_final.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_txt, '-c', 'copy', final_output
    ], check=True)
    print(f"\nConcat successful: {final_output}")

if __name__ == '__main__':
    main()
