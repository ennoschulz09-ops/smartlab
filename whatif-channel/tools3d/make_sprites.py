"""Sprites aus den freigestellten Drehansicht-Bildern: Mauszeiger entfernen, zuschneiden, auf gleiche Hoehe bringen.
   python3 make_sprites.py ../referenz/sprites/all ../referenz/sprites/pip"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi, signal

SRC, DST = sys.argv[1], sys.argv[2]; os.makedirs(DST, exist_ok=True)
PICK = {"0": "029", "45": "074", "90": "025", "135": "022", "180": "008"}   # Blick nach links: Winkel von vorn (0) bis Ruecken (180)

# Mauszeiger-Vorlage aus einem Bild, in dem er ueber dem dunklen Hintergrund steht
ref = np.array(Image.open(os.path.join(SRC, "..", "..", "sprites", "cursor_src.png")).convert("RGB")).astype(np.float32) if os.path.exists(os.path.join(SRC, "..", "cursor_src.png")) else None


def cursor_mask(im, tpl):
    g = im.mean(-1); t = tpl.mean(-1)
    g0, t0 = g - g.mean(), t - t.mean()
    cc = signal.fftconvolve(g0, t0[::-1, ::-1], mode="same")
    norm = np.sqrt(signal.fftconvolve(g0 ** 2, np.ones_like(t0), mode="same") * (t0 ** 2).sum() + 1e-6)
    return cc / norm


idx = json.load(open(os.path.join(SRC, "index.json"))); meta = {}
for ang, k in PICK.items():
    f = f"s_{k}.png"; im = np.array(Image.open(os.path.join(SRC, f))).astype(np.float32); rgb, a = im[..., :3], im[..., 3] / 255
    b = idx[f]["box"]; rgb = rgb[b[1]:b[3] + 1, b[0]:b[2] + 1]; a = a[b[1]:b[3] + 1, b[0]:b[2] + 1]
    # Mauszeiger: weisse Pfeilspitze mit schwarzem Rand = sehr helle, kleine, scharf begrenzte Struktur -> ueber manuelle Liste entfernen
    cur = json.load(open(os.path.join(SRC, "cursors.json"))).get(k) if os.path.exists(os.path.join(SRC, "cursors.json")) else None
    if cur:
        x0, y0, x1, y1 = [c - o for c, o in zip(cur, (b[0], b[1], b[0], b[1]))]
        m = np.zeros(a.shape, bool); m[max(0, y0):y1, max(0, x0):x1] = True
        w = (~m).astype(np.float32)
        for c in range(3):
            num = ndi.gaussian_filter(rgb[..., c] * w, 6); den = ndi.gaussian_filter(w, 6) + 1e-4; rgb[..., c] = np.where(m, num / den, rgb[..., c])
    h = rgb.shape[0]; H = 700; s = H / h
    out = Image.fromarray(np.dstack([rgb.astype(np.uint8), (a * 255).astype(np.uint8)])).resize((int(rgb.shape[1] * s), H), Image.LANCZOS)
    arr = np.array(out); ys, xs = np.where(arr[..., 3] > 128); lowrows = ys > ys.max() - 25
    ax = int(xs[lowrows].mean()); meta[ang] = dict(file=f"a{ang}.png", w=out.width, h=out.height, anchor_x=ax)
    out.save(os.path.join(DST, f"a{ang}.png"))
json.dump(meta, open(os.path.join(DST, "meta.json"), "w"), indent=1); print(meta)
