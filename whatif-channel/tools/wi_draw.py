"""Kleine Zeichen-Bibliothek: eigene Figur "Pip", Verkaeufer, Auto, Glocke.
Alles wird in 2-facher Aufloesung gezeichnet und spaeter runterskaliert (glatte Kanten)."""
import math
from PIL import Image, ImageDraw, ImageFont

W, H, S = 1280, 720, 2
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

ORANGE = (255, 170, 60, 255)
TEAL = (30, 170, 160, 255)
TEAL_D = (20, 130, 125, 255)
PURPLE = (120, 80, 200, 255)
PURPLE_L = (240, 220, 255, 255)
SKIN = (242, 194, 155, 255)
NAVY = (30, 40, 80, 255)
RED = (225, 60, 60, 255)
WHITE = (255, 255, 255, 255)
BLACK = (15, 15, 25, 255)
GOLD = (255, 200, 60, 255)
GOLD_D = (210, 150, 30, 255)
YELLOW = (255, 225, 40, 255)
WIN = (170, 220, 250, 255)
DARK = (40, 42, 55, 255)
GREY = (170, 175, 185, 255)


def font(size):
    return ImageFont.truetype(FONT, int(size * S))


def gradient(top, bottom):
    img = Image.new("RGBA", (W * S, H * S))
    d = ImageDraw.Draw(img)
    for y in range(H * S):
        k = y / (H * S - 1)
        d.line([(0, y), (W * S, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)) + (255,))
    return img


class Canvas:
    def __init__(self, bg):
        self.im = bg.copy()
        self.d = ImageDraw.Draw(self.im)

    def ell(self, cx, cy, rx, ry, fill=None, outline=None, w=0):
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill, outline=outline, width=int(w * S))

    def rect(self, x0, y0, x1, y1, fill=None, r=0, outline=None, w=0):
        self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=fill, outline=outline, width=int(w * S))

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def line(self, pts, fill, w):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(w * S), joint="curve")

    def arc(self, cx, cy, rx, ry, a0, a1, fill, w):
        self.d.arc([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], a0, a1, fill=fill, width=int(w * S))

    def paste(self, layer, x, y):
        self.im.alpha_composite(layer, (int(x * S), int(y * S)))
        self.d = ImageDraw.Draw(self.im)

    def overlay(self, layer):
        self.im.alpha_composite(layer)
        self.d = ImageDraw.Draw(self.im)

    def text(self, xy, s, size, fill=WHITE, stroke=0, stroke_fill=BLACK, anchor="mm"):
        self.d.text((xy[0] * S, xy[1] * S), s, font=font(size), fill=fill, anchor=anchor,
                    stroke_width=int(stroke * S), stroke_fill=stroke_fill)

    def wrapped(self, xy, s, size, max_w, **kw):
        words, lines, cur = s.split(), [], ""
        f = font(size)
        for w_ in words:
            t = (cur + " " + w_).strip()
            if self.d.textlength(t, font=f) / S <= max_w:
                cur = t
            else:
                lines.append(cur)
                cur = w_
        lines.append(cur)
        lh = size * 1.18
        y0 = xy[1] - lh * (len(lines) - 1) / 2
        for i, ln in enumerate(lines):
            self.text((xy[0], y0 + i * lh), ln, size, **kw)


def pip(c, cx, cy, sc=1.0, brow=(0, 0), look=(0, 0), mouth="smirk", arm=None, eyes_open=1.0):
    """Eigene Hauptfigur: runder oranger Kopf, violette Mütze, türkiser Hoodie."""
    R = 62 * sc
    c.rect(cx - 54 * sc, cy + R - 16 * sc, cx + 54 * sc, cy + R + 130 * sc, fill=TEAL, r=30 * sc)
    c.rect(cx - 30 * sc, cy + R + 78 * sc, cx + 30 * sc, cy + R + 112 * sc, fill=TEAL_D, r=12 * sc)
    if arm:  # Arm zur Hand (hx, hy)
        hx, hy = arm
        c.line([(cx + 46 * sc, cy + R + 14 * sc), (hx, hy)], TEAL, 22 * sc)
        c.ell(hx, hy, 14 * sc, 14 * sc, fill=ORANGE)
    c.ell(cx, cy, R, R * 0.96, fill=ORANGE)
    # Mütze
    c.d.pieslice([(cx - R - 4 * sc) * S, (cy - R - 8 * sc) * S, (cx + R + 4 * sc) * S, (cy + R - 8 * sc) * S], 180, 360, fill=PURPLE)
    c.rect(cx - R - 6 * sc, cy - 26 * sc, cx + R + 6 * sc, cy - 6 * sc, fill=PURPLE_L, r=9 * sc)
    c.ell(cx, cy - R - 10 * sc, 15 * sc, 15 * sc, fill=PURPLE_L)
    # Augen
    for side in (-1, 1):
        ex, ey = cx + side * 24 * sc, cy + 16 * sc
        c.ell(ex, ey, 15 * sc, 18 * sc * eyes_open, fill=WHITE)
        c.ell(ex + look[0] * 5 * sc, ey + look[1] * 5 * sc, 7.5 * sc, 8.5 * sc * eyes_open, fill=BLACK)
        b = brow[0] if side < 0 else brow[1]
        yb = ey - 30 * sc
        xi, xo = ex - side * 14 * sc, ex + side * 14 * sc
        c.line([(xi, yb + b * 9 * sc), (xo, yb - b * 9 * sc)], BLACK, 5.5 * sc)
        c.ell(ex + side * 22 * sc, ey + 26 * sc, 10 * sc, 6 * sc, fill=(255, 130, 110, 160))
    my = cy + 46 * sc
    if mouth == "smirk":
        c.line([(cx - 16 * sc, my + 2 * sc), (cx + 2 * sc, my + 7 * sc), (cx + 19 * sc, my - 5 * sc)], BLACK, 4.5 * sc)
    elif mouth == "smile":
        c.arc(cx, my - 6 * sc, 20 * sc, 14 * sc, 15, 165, BLACK, 4.5 * sc)
    elif mouth == "open":
        c.ell(cx, my + 2 * sc, 11 * sc, 13 * sc, fill=BLACK)
    else:
        c.line([(cx - 13 * sc, my), (cx + 13 * sc, my)], BLACK, 4.5 * sc)


def salesman(c, cx, cy, sc=1.0, hand=None, sweat=0.0, grin=True):
    R = 56 * sc
    c.rect(cx - 62 * sc, cy + R - 14 * sc, cx + 62 * sc, cy + R + 160 * sc, fill=NAVY, r=26 * sc)
    c.poly([(cx - 20 * sc, cy + R - 10 * sc), (cx + 20 * sc, cy + R - 10 * sc), (cx, cy + R + 50 * sc)], fill=WHITE)
    c.poly([(cx - 7 * sc, cy + R + 6 * sc), (cx + 7 * sc, cy + R + 6 * sc), (cx + 10 * sc, cy + R + 60 * sc), (cx, cy + R + 72 * sc), (cx - 10 * sc, cy + R + 60 * sc)], fill=RED)
    if hand:
        c.line([(cx - 54 * sc, cy + R + 20 * sc), hand], NAVY, 24 * sc)
        c.ell(hand[0], hand[1], 15 * sc, 15 * sc, fill=SKIN)
    c.ell(cx, cy, R, R * 1.02, fill=SKIN)
    c.d.pieslice([(cx - R - 2 * sc) * S, (cy - R - 6 * sc) * S, (cx + R + 2 * sc) * S, (cy + R - 6 * sc) * S], 185, 355, fill=(70, 70, 80, 255))
    for side in (-1, 1):
        ex = cx + side * 20 * sc
        c.ell(ex, cy + 4 * sc, 6 * sc, 7 * sc, fill=BLACK)
        c.line([(ex - side * 10 * sc, cy - 14 * sc), (ex + side * 10 * sc, cy - 20 * sc)], (70, 70, 80, 255), 5 * sc)
    if grin:
        c.rect(cx - 24 * sc, cy + 24 * sc, cx + 24 * sc, cy + 42 * sc, fill=WHITE, r=8 * sc, outline=BLACK, w=3 * sc)
    else:
        c.line([(cx - 16 * sc, cy + 36 * sc), (cx + 16 * sc, cy + 32 * sc)], BLACK, 4 * sc)
    if sweat > 0:
        for i, (dx, dy) in enumerate([(-R - 6 * sc, -10 * sc), (R + 4 * sc, 0), (-R + 4 * sc, -R + 6 * sc)]):
            yy = cy + dy + sweat * 22 * sc * (1 + i * 0.3)
            c.poly([(cx + dx, yy - 14 * sc), (cx + dx - 8 * sc, yy + 2 * sc), (cx + dx + 8 * sc, yy + 2 * sc)], fill=(90, 170, 255, 255))
            c.ell(cx + dx, yy + 4 * sc, 8 * sc, 8 * sc, fill=(90, 170, 255, 255))


def car(c, x, y, sc=1.0, color=(60, 130, 230, 255), flip=False):
    """Seitenansicht. Ohne flip zeigt die Motorhaube nach rechts, mit flip nach links."""
    def X(v):
        return x + (360 - v) * sc if flip else x + v * sc

    c.rect(min(X(0), X(360)), y + 50 * sc, max(X(0), X(360)), y + 124 * sc, fill=color, r=28 * sc)
    c.poly([(X(70), y + 54 * sc), (X(112), y), (X(252), y), (X(300), y + 54 * sc)], fill=color)
    c.poly([(X(90), y + 52 * sc), (X(120), y + 12 * sc), (X(172), y + 12 * sc), (X(172), y + 52 * sc)], fill=WIN)
    c.poly([(X(184), y + 52 * sc), (X(184), y + 12 * sc), (X(246), y + 12 * sc), (X(282), y + 52 * sc)], fill=WIN)
    for wx in (X(82), X(282)):
        c.ell(wx, y + 126 * sc, 33 * sc, 33 * sc, fill=DARK)
        c.ell(wx, y + 126 * sc, 14 * sc, 14 * sc, fill=GREY)
    c.ell(X(350), y + 86 * sc, 9 * sc, 12 * sc, fill=YELLOW)


def bell_layer(size=260, angle=0.0):
    """Goldene Glocke, am oberen Aufhaengepunkt gedreht."""
    s = size
    lay = Image.new("RGBA", (s * S, s * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx = s / 2
    d.ellipse([(cx - 14) * S, 4 * S, (cx + 14) * S, 32 * S], outline=GOLD_D, width=7 * S)
    d.pieslice([(cx - 80) * S, 30 * S, (cx + 80) * S, 200 * S], 180, 360, fill=GOLD)
    d.polygon([((cx - 80) * S, 115 * S), ((cx + 80) * S, 115 * S), ((cx + 112) * S, 188 * S), ((cx - 112) * S, 188 * S)], fill=GOLD)
    d.rounded_rectangle([(cx - 116) * S, 182 * S, (cx + 116) * S, 204 * S], radius=11 * S, fill=GOLD_D)
    d.ellipse([(cx - 22) * S, 200 * S, (cx + 22) * S, 244 * S], fill=GOLD_D)
    d.ellipse([(cx - 58) * S, 62 * S, (cx - 30) * S, 118 * S], fill=(255, 235, 150, 200))
    return lay.rotate(angle, center=(cx * S, 18 * S), resample=Image.BICUBIC)


def rings(cx, cy, age, color, n=3, life=1.5, speed=430):
    """Schallwellen als halbtransparenter Overlay."""
    lay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(n):
        a = age - k * 0.2
        if a < 0 or a > life:
            continue
        r = (50 + a * speed) * S
        alpha = int(255 * (1 - a / life))
        d.ellipse([cx * S - r, cy * S - r, cx * S + r, cy * S + r], outline=color[:3] + (alpha,), width=int((12 * (1 - a / life) + 2) * S))
    return lay


def final_frame(c, zoom=1.0, cx=0.5, cy=0.5):
    """Kamerafahrt: zuschneiden und auf 1280x720 skalieren."""
    w, h = W * S / zoom, H * S / zoom
    x0 = (W * S - w) * cx
    y0 = (H * S - h) * cy
    return c.im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.LANCZOS).convert("RGB")
