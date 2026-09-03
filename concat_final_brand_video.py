import subprocess
import os
import json

WORKDIR = "/root/hermes-projects/food-discovery-automation"

c1 = os.path.join(WORKDIR, "brand_clip_1.mp4")
c2 = os.path.join(WORKDIR, "brand_clip_2.mp4")
c3 = os.path.join(WORKDIR, "brand_clip_3.mp4")

concat_list = os.path.join(WORKDIR, "brand_concat_list.txt")
with open(concat_list, "w") as f:
    f.write(f"file '{c1}'\n")
    f.write(f"file '{c2}'\n")
    f.write(f"file '{c3}'\n")

final_output = os.path.join(WORKDIR, "brand_channel_identity_shorts_30s.mp4")

subprocess.run([
    'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
    '-i', concat_list, '-c', 'copy', final_output
], check=True)

print(f"Final 30s Video Concat successfully created: {final_output}")

# Run ffprobe
probe = subprocess.run([
    'ffprobe', '-v', 'error', '-show_entries', 'stream=width,height,r_frame_rate,duration,nb_frames',
    '-show_entries', 'format=duration,size', '-of', 'json', final_output
], capture_output=True, text=True)

print("FFprobe summary:")
print(probe.stdout)
