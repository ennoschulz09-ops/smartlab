"""Figur aus dem Drehansicht-Video freistellen (Hintergrund = glatter dunkler Verlauf).
   python3 cutout.py video.mp4 ausgabeordner [fps]   -> PNG mit Alpha pro Bild + index.json (Boxen)"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def fit_bg(im):
    H, W, _ = im.shape; yy, xx = np.mgrid[0:H, 0:W]
    A = np.stack([np.ones_like(xx), xx, yy, xx * xx, xx * yy, yy * yy], -1).reshape(-1, 6).astype(np.float32)
    A = A / np.array([1, W, H, W * W, W * H, H * H], dtype=np.float32)
    m = ((xx < 70) | (xx > W - 70) | (yy < 10)).reshape(-1); bg = np.zeros_like(im)
    for c in range(3):
        co, *_ = np.linalg.lstsq(A[m], im[..., c].reshape(-1)[m], rcond=None); bg[..., c] = (A @ co).reshape(H, W)
    return bg


def cut(im, thr=9):
    bg = fit_bg(im); d = np.abs(im - bg).max(-1)
    H = d.shape[0]; ramp = np.clip((np.arange(H)[:, None] / H - 0.78) / 0.07, 0, 1)
    mask = d > (thr + 7 * ramp)
    mask = ndi.binary_closing(mask, structure=np.ones((3, 3)), iterations=6); mask = ndi.binary_fill_holes(mask)
    mask = ndi.binary_opening(mask, structure=np.ones((3, 3)), iterations=3)
    lab, n = ndi.label(mask)
    if n == 0: return None
    sizes = ndi.sum(mask, lab, range(1, n + 1)); mask = lab == (1 + int(np.argmax(sizes))); mask = ndi.binary_fill_holes(mask)
    mask = ndi.binary_erosion(mask, structure=np.ones((3, 3)), iterations=1)
    return ndi.gaussian_filter(mask.astype(np.float32), 0.9)


if __name__ == "__main__":
    vid, out = sys.argv[1], sys.argv[2]; fps = float(sys.argv[3]) if len(sys.argv) > 3 else 5
    os.makedirs(out, exist_ok=True); tmp = os.path.join(out, "_raw"); os.makedirs(tmp, exist_ok=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", vid, "-vf", f"fps={fps}", os.path.join(tmp, "r_%03d.png")], check=True)
    idx = {}
    for f in sorted(os.listdir(tmp)):
        im = np.array(Image.open(os.path.join(tmp, f)).convert("RGB")).astype(np.float32); a = cut(im)
        if a is None: continue
        ys, xs = np.where(a > 0.5)
        if len(ys) == 0: continue
        H, W = a.shape; box = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        rgba = np.dstack([im.astype(np.uint8), (a * 255).astype(np.uint8)]); Image.fromarray(rgba).save(os.path.join(out, f.replace("r_", "s_")))
        idx[f.replace("r_", "s_")] = dict(box=box, touches=bool(box[0] <= 2 or box[2] >= W - 3 or box[1] <= 2 or box[3] >= H - 3), h=box[3] - box[1], w=box[2] - box[0])
    json.dump(idx, open(os.path.join(out, "index.json"), "w"), indent=1); print(len(idx), "Bilder")
