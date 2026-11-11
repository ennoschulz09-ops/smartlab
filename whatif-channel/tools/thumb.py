"""Thumbnail "LIAR?" (1280x720). Aufruf: python3 thumb.py ausgabe.png"""
import sys, math
import skia
from PIL import Image
from gfx import *
import chars, scenes

out = sys.argv[1] if len(sys.argv) > 1 else "thumbnail.png"
g = Gfx()
g.rect(0, 0, W, H, shader=lin((0, 0), (W, H), [C(80, 46, 210), C(176, 54, 190), C(250, 72, 120)], [0, 0.55, 1]))
g.c.save()
g.c.translate(560, 360)
for i in range(18):  # Strahlen
    g.c.save(); g.c.rotate(i * 20)
    p = skia.Path(); p.moveTo(0, 0); p.lineTo(1500, -70); p.lineTo(1500, 70); p.close()
    g.path(p, fill=C(255, 255, 255, 26))
    g.c.restore()
g.c.restore()
g.circle(560, 400, 560, shader=rad((560, 400), 560, [C(255, 255, 255, 70), C(255, 255, 255, 0)]))
scenes.bell(g, 960, 470, 1.4, -12, 1.0)
scenes.rings(g, 960, 490, 0.40, (255, 230, 120), life=1.8, speed=430, width=16)
sc = 1.95
a0, a1 = chars.ik((54, -100), (96, -198), 56, 54, 1)
chars.person(g, 340, 650, chars.PIP, sc, arm_r=(a0, a1), arm_l=(14, 30), look=(0.9, 0), lid=0, brow_l=(-16, 12), brow_r=(-16, 12),
             mouth_kind="o", head_rot=-5, glove_big=1.1, shadow=False)
g.text("LIAR?", 960, 235, 215, fill=C(255, 224, 40), stroke=C(30, 20, 90), stroke_w=34, shadow=(0, 14, C(0, 0, 0, 150), 8), rot=-4)
vignette(g, 0.35)
Image.fromarray(g.to_rgb()).save(out)
print("fertig:", out)
