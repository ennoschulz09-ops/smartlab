"""Bildfolge (Filmstreifen) aus einem Video, um Bewegung zu pruefen.  python3 strip.py video.mp4 t0 t1 anzahl out.png [breite]"""
import subprocess, sys, tempfile, os
from PIL import Image, ImageDraw
v, t0, t1, n, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
w = int(sys.argv[6]) if len(sys.argv) > 6 else 426
tmp = tempfile.mkdtemp(); ims = []
for k in range(n):
    t = t0 + (t1 - t0) * k / max(1, n - 1)
    f = os.path.join(tmp, f"{k}.png"); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", v, "-frames:v", "1", f], check=True)
    im = Image.open(f).convert("RGB"); im = im.resize((w, int(w * im.height / im.width))); d = ImageDraw.Draw(im); d.rectangle([0, 0, 62, 18], fill=(0, 0, 0)); d.text((3, 3), f"{t:.2f}s", fill=(255, 255, 0)); ims.append(im)
cols = 3; rows = (n + cols - 1) // cols
s = Image.new("RGB", (cols * w, rows * ims[0].height))
for k, im in enumerate(ims):
    s.paste(im, ((k % cols) * w, (k // cols) * ims[0].height))
s.save(out); print(out, s.size)
