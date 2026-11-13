"""Sprite-Puppen aus der Drehansicht: Blickwinkel waehlen/ueberblenden, umfaerben, verformen (Hopsen, Stauchen, Neigen) und platzieren."""
import json, math, os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(HERE, "..", "referenz", "sprites", "pip")
ANGLES = [0, 45, 90, 135, 180]          # Blick nach links, 0 = zur Kamera, 180 = weg von der Kamera
_base = {}


def _load():
    if _base: return
    meta = json.load(open(os.path.join(SPR, "meta.json")))
    for a in ANGLES:
        m = meta[str(a)]; _base[a] = (Image.open(os.path.join(SPR, m["file"])).convert("RGBA"), m["anchor_x"])


def tinted(variant):
    """variant: dict(hoodie=(r,g,b) Multiplikator, pants=(add r,g,b) oder None) -> Dict Winkel -> (Bild, Anker)"""
    _load(); out = {}
    for a, (im, ax) in _base.items():
        arr = np.array(im).astype(np.float32); H = arr.shape[0]
        if variant:
            lum = arr[..., :3].mean(-1); rows = np.arange(H)[:, None] / H
            sat = arr[..., :3].max(-1) - arr[..., :3].min(-1); st = {0: 0.29, 45: 0.31, 90: 0.29, 135: 0.26, 180: 0.27}[a]
            w = np.clip((sat - 7) / 9, 0, 1) * np.clip((lum - 55) / 25, 0, 1) * np.clip((rows - (st - 0.03)) / 0.04, 0, 1) * np.clip((0.66 - rows) / 0.05, 0, 1)
            if variant.get("hoodie") is not None:
                m = np.array(variant["hoodie"], np.float32); arr[..., :3] = arr[..., :3] * (1 + (m - 1) * w[..., None])
            if variant.get("pants") is not None:
                pm = (lum < 70) & (rows > 0.55); add = np.array(variant["pants"], np.float32)
                arr[..., :3] = np.where(pm[..., None], arr[..., :3] * 0.6 + add, arr[..., :3])
        out[a] = (Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), ax)
    return out


def view(set_, alpha_deg, mirror):
    """Bild fuer Blickwinkel alpha_deg (0..180), bei Bedarf ueberblendet; alle auf gemeinsamen Anker (Mitte der Fuesse) gelegt."""
    a = max(0.0, min(180.0, alpha_deg)); k = min(ANGLES, key=lambda x: abs(x - a)); W = 460
    t = Image.new("RGBA", (W, 700), (0, 0, 0, 0)); im0, ax = set_[k]; t.paste(im0, (W // 2 - ax, 0)); im = t
    return im.transpose(Image.FLIP_LEFT_RIGHT) if mirror else im


def draw(canvas, set_, foot, ppx, facing, cam_xz, hop=0.0, sx=1.0, sy=1.0, tilt=0.0, dx=0.0, warm=(1.04, 0.98, 0.93), shadow=0.45, fig_h=3.3, face_vec=None):
    """Zeichnet eine Puppe: foot = Bildpunkt der Fuesse, ppx = Pixel pro Weltmeter auf dieser Tiefe, facing = (fx, fz) Blickrichtung am Boden."""
    fx, fz = facing; n = math.hypot(fx, fz) or 1; fx, fz = fx / n, fz / n
    cx, cz = cam_xz; return_pos = None
    dot = fx * cx + fz * cz; cross = fx * cz - fz * cx
    alpha = math.degrees(math.acos(max(-1, min(1, dot)))); mirror = cross > 0
    img = view(set_, alpha, mirror)
    ph = fig_h * ppx; s = ph / 700.0
    w, h = img.size; img = img.resize((max(2, int(w * s * sx)), max(2, int(h * s * sy))), Image.LANCZOS)
    arr = np.array(img).astype(np.float32); arr[..., 0] *= warm[0]; arr[..., 1] *= warm[1]; arr[..., 2] *= warm[2]; img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    # Schatten
    if shadow > 0:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); from PIL import ImageDraw
        d = ImageDraw.Draw(sh); rw = ph * 0.2 * sx * (1 - min(0.6, hop * 0.15)); rh = rw * 0.28
        d.ellipse((foot[0] - rw + dx, foot[1] - rh, foot[0] + rw + dx, foot[1] + rh), fill=(30, 12, 55, int(255 * shadow * (1 - min(0.7, hop * 0.25)))))
        sh = sh.filter(ImageFilter.GaussianBlur(max(2, ph * 0.012))); canvas.alpha_composite(sh)
    if abs(tilt) > 1e-3:
        pad = img.width // 2 + 10; big = Image.new("RGBA", (img.width + 2 * pad, img.height + 20), (0, 0, 0, 0)); big.paste(img, (pad, 0))
        big = big.rotate(math.degrees(-tilt), resample=Image.BICUBIC, center=(big.width // 2, img.height - 2)); img = big
        ox, oy = img.width // 2, img.height - 20
    else:
        ox, oy = img.width // 2, img.height
    pos = (int(foot[0] + dx - ox), int(foot[1] - hop * ppx - oy + 2)); canvas.alpha_composite(img, (max(pos[0], -img.width + 1) if False else pos[0], pos[1])) if (pos[0] > -img.width and pos[1] > -img.height and pos[0] < canvas.width and pos[1] < canvas.height) else None
    return dict(head=(foot[0] + dx, foot[1] - hop * ppx - ph * sy * 0.93), foot=(foot[0] + dx, foot[1] - hop * ppx), ph=ph * sy)
