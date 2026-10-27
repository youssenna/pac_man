"""Rescale every frame of a folder tree, keeping the folder structure.
    python tools/resize_pack.py maze maze_custom 0.5      # 128px tiles -> 64px
Any scale works (e.g. 0.352 gives 45px tiles for a 45px grid)."""
import os, sys
from PIL import Image
src, dst, k = sys.argv[1], sys.argv[2], float(sys.argv[3])
for dp, _, files in os.walk(src):
    for f in files:
        if f.endswith(".png"):
            out = os.path.join(dst, os.path.relpath(dp, src)); os.makedirs(out, exist_ok=True)
            im = Image.open(os.path.join(dp, f))
            im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS).save(os.path.join(out, f), optimize=True)
