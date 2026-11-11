"""Proof of Concept: Thumbnail fuer "What If You Could Hear Every Lie?" (1280x720, kostenlos per Code).
Aufruf: python3 poc_thumbnail.py thumbnail.png"""
import sys
from PIL import Image, ImageDraw
import wi_draw as D
from wi_draw import S, Canvas

out = sys.argv[1] if len(sys.argv) > 1 else "thumbnail.png"
bg = D.gradient((70, 25, 130), (215, 45, 95))
c = Canvas(bg)
# Lichtstrahlen (auf eigener Ebene, damit sie halbtransparent bleiben)
rays = Image.new("RGBA", bg.size, (0, 0, 0, 0))
rd = ImageDraw.Draw(rays)
for i in range(9):
    ang = i * 40
    rd.pieslice([-400 * S, -400 * S, 1700 * S, 1100 * S], ang, ang + 12, fill=(255, 255, 255, 28))
c.overlay(rays)
D.pip(c, 330, 330, 2.5, brow=(-0.8, -0.8), look=(0.8, 0), mouth="open", arm=(505, 300))
lay = D.bell_layer(260, -14)
lay = lay.resize((int(lay.width * 1.7), int(lay.height * 1.7)), Image.LANCZOS)
c.im.alpha_composite(lay, (int(700 * S), int(190 * S)))
c.overlay(D.rings(925, 330, 0.5, (255, 230, 120), n=3, life=1.6, speed=300))
c.text((930, 110), "LIAR?", 200, fill=D.YELLOW, stroke=16)
D.final_frame(c).save(out)
print("fertig:", out)
