"""Hintergruende, Requisiten und Effekte."""
import math, random
import skia
from gfx import *

_cache = {}


def cloud(g, x, y, s, a=235):
    for dx, dy, r in ((0, 0, 50), (46, -10, 40), (-44, 6, 36), (90, 8, 34), (-86, 12, 28)):
        g.circle(x + dx * s, y + dy * s, r * s, fill=C(255, 255, 255, a), blur=2)


def car(g, x, y, s=1.0, color=(70, 130, 235), flip=False, light=0.0):
    """Auto in Seitenansicht. (x, y) = linke obere Ecke der Huelle bei flip=False. Breite ca. 360*s."""
    c = g.c
    c.save()
    c.translate(x, y)
    if flip:
        c.translate(360 * s, 0)
        c.scale(-1, 1)
    c.scale(s, s)
    r, gg, b = color
    top, mid, bot = C(min(255, r + 70), min(255, gg + 70), min(255, b + 50)), C(r, gg, b), C(r * 0.55, gg * 0.55, b * 0.6)
    g.oval(180, 142, 190, 16, fill=C(0, 0, 0, 90), blur=8)
    body = skia.Path()
    body.moveTo(6, 100); body.cubicTo(-4, 70, 6, 56, 40, 52); body.lineTo(70, 50)
    body.cubicTo(92, 22, 114, 4, 150, 2); body.lineTo(232, 2)
    body.cubicTo(262, 4, 286, 28, 302, 50); body.cubicTo(336, 54, 358, 62, 358, 90)
    body.lineTo(356, 104); body.lineTo(8, 104); body.close()
    g.path(body, shader=lin((0, 0), (0, 110), [top, mid, bot], [0, 0.45, 1]))
    g.path(body, stroke=C(0, 0, 0, 60), width=2.5)
    # Fenster
    w1 = skia.Path(); w1.moveTo(88, 50); w1.cubicTo(104, 26, 120, 12, 150, 10); w1.lineTo(172, 10); w1.lineTo(172, 50); w1.close()
    w2 = skia.Path(); w2.moveTo(184, 50); w2.lineTo(184, 10); w2.lineTo(232, 10); w2.cubicTo(254, 12, 272, 30, 286, 50); w2.close()
    for w in (w1, w2):
        g.path(w, shader=lin((0, 8), (0, 52), [C(190, 232, 255), C(80, 140, 205)]))
        g.c.save(); g.c.clipPath(w, skia.ClipOp.kIntersect, True)
        g.path(_poly([(120, 0), (150, 0), (110, 60), (84, 60)]), fill=C(255, 255, 255, 90))
        g.path(_poly([(216, 0), (232, 0), (192, 60), (176, 60)]), fill=C(255, 255, 255, 60))
        g.c.restore()
        g.path(w, stroke=C(0, 0, 0, 70), width=2)
    g.path(_line([(10, 78), (350, 78)]), stroke=C(255, 255, 255, 60), width=3)  # Zierlinie
    g.line(14, 60, 330, 56, stroke=C(255, 255, 255, 80), width=3)  # Glanz
    g.rrect(214, 62, 232, 68, 3, fill=C(255, 255, 255, 160))  # Tuergriff
    g.line(180, 52, 180, 100, stroke=C(0, 0, 0, 60), width=2)
    g.rrect(344, 92, 366, 104, 4, fill=C(210, 214, 222))  # Stossstange
    g.oval(346, 70, 10, 13, fill=C(255, 244, 170))
    if light > 0:
        g.oval(360, 70, 70 * light, 40 * light, fill=C(255, 244, 170, int(90 * light)), blur=14)
    g.oval(6, 74, 5, 11, fill=C(230, 50, 50))
    for wx in (82, 282):
        g.circle(wx, 104, 33, fill=C(28, 30, 38))
        g.circle(wx, 104, 20, shader=rad((wx - 5, 99), 28, [C(245, 248, 255), C(120, 128, 142)]))
        for k in range(5):
            a = k * 72 + 10
            g.line(wx, 104, wx + 19 * math.cos(math.radians(a)), 104 + 19 * math.sin(math.radians(a)), stroke=C(90, 96, 110), width=3)
        g.circle(wx, 104, 6, fill=C(60, 66, 80))
    c.restore()


def _poly(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close(); return p


def _line(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def bell(g, cx, cy, s=1.0, angle=0.0, glow=1.0):
    c = g.c
    if glow > 0:
        g.circle(cx, cy + 20 * s, 230 * s, shader=rad((cx, cy + 20 * s), 230 * s, [C(255, 210, 90, int(150 * glow)), C(255, 190, 60, 0)]))
    c.save(); c.translate(cx, cy - 80 * s); c.rotate(angle); c.scale(s, s); c.translate(0, 80)
    g.oval(0, 190, 70, 10, fill=C(0, 0, 0, 0))
    g.circle(0, -80, 17, stroke=C(190, 130, 30), width=8)
    b = skia.Path()
    b.moveTo(-72, 56); b.cubicTo(-76, -34, -44, -72, 0, -72); b.cubicTo(44, -72, 76, -34, 72, 56)
    b.lineTo(104, 108); b.quadTo(0, 126, -104, 108); b.close()
    g.path(b, shader=lin((-104, 0), (104, 0), [C(255, 240, 160), C(255, 200, 60), C(205, 135, 25), C(150, 90, 15)], [0, 0.35, 0.75, 1]))
    g.path(b, stroke=C(120, 70, 10, 120), width=3)
    g.path(_poly([(-60, 30), (-46, -30), (-38, -52), (-30, -52), (-40, 20), (-48, 80)]), fill=C(255, 255, 255, 110))
    g.rrect(-110, 104, 110, 126, 11, shader=lin((0, 104), (0, 126), [C(230, 160, 40), C(160, 100, 18)]))
    g.circle(0, 138, 19, shader=rad((-5, 132), 26, [C(255, 225, 120), C(180, 115, 20)]))
    c.restore()


def rings(g, cx, cy, age, color=(255, 220, 120), life=1.6, n=3, speed=520, width=14):
    for k in range(n):
        a = age - k * 0.18
        if a < 0 or a > life:
            continue
        r = 40 + a * speed * (1 - 0.35 * a / life)
        al = int(255 * (1 - a / life) ** 1.4)
        w = width * (1 - a / life) + 2
        g.circle(cx, cy, r, stroke=C(*color, int(al * 0.55)), width=w * 2.4, blur=10)
        g.circle(cx, cy, r, stroke=C(*color, al), width=w)


def speed_lines(g, cx, cy, t, n=34, r0=140, r1=900, col=C(255, 255, 255, 120), seed=3):
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.random() * math.tau
        w = rnd.uniform(1.5, 5)
        rr0 = r0 + rnd.random() * 220
        g.line(cx + rr0 * math.cos(a), cy + rr0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a), stroke=col, width=w)


def make_abyss():
    if "abyss" in _cache:
        return _cache["abyss"]
    g = Gfx()
    g.rect(0, 0, W, H, shader=lin((0, 0), (0, H), [C(5, 14, 40), C(10, 52, 96), C(16, 96, 130)], [0, 0.6, 1]))
    for x, w_, a in ((180, 70, 70), (470, 110, 60), (760, 80, 66), (1010, 120, 54), (1230, 60, 60)):
        p = _poly([(x - w_ * 0.4, 0), (x + w_ * 0.4, 0), (x + w_ * 1.6 + 60, H), (x - w_ * 1.2 + 60, H)])
        g.path(p, shader=lin((0, 0), (0, H), [C(150, 220, 255, a), C(150, 220, 255, 0)]), blur=14)
    _cache["abyss"] = g.snapshot()
    return _cache["abyss"]


def make_lot():
    if "lot" in _cache:
        return _cache["lot"]
    far = Gfx(); far.clear(C(0, 0, 0, 0))
    g = Gfx()
    g.rect(0, 0, W, 470, shader=lin((0, 0), (0, 470), [C(88, 168, 250), C(190, 225, 255), C(236, 246, 255)], [0, 0.7, 1]))
    g.circle(1020, 110, 300, shader=rad((1020, 110), 300, [C(255, 252, 215, 230), C(255, 250, 220, 0)]))
    for x, y, s in ((200, 120, 1.1), (620, 70, 0.8), (900, 170, 1.0), (1150, 80, 0.7)):
        cloud(g, x, y, s)
    # ferne Ebene (wird weichgezeichnet)
    far.rect(40, 250, 640, 430, shader=lin((0, 250), (0, 430), [C(235, 238, 246), C(190, 198, 214)]))
    far.rect(40, 232, 640, 262, fill=C(215, 55, 60))
    far.text("AUTO  SALES", 340, 258, 24, fill=C(255, 255, 255))
    for i in range(6):
        far.rrect(70 + i * 95, 290, 150 + i * 95, 410, 6, shader=lin((0, 290), (0, 410), [C(120, 180, 225), C(60, 110, 170)]))
    for x, r in ((730, 70), (800, 90), (880, 64), (1010, 84), (1120, 70), (1230, 92)):
        far.circle(x, 400 - r * 0.3, r, shader=rad((x - 10, 360), r * 1.2, [C(92, 175, 110), C(40, 110, 70)]))
    far.rect(0, 420, W, 470, fill=C(98, 150, 98))
    g.draw_image(far.snapshot(), 0, 0, blur=2.6)
    g.rect(0, 430, W, H, shader=lin((0, 430), (0, H), [C(138, 144, 158), C(92, 98, 112), C(60, 65, 78)], [0, 0.4, 1]))
    g.rect(0, 430, W, 440, fill=C(176, 182, 194))
    for k in range(-5, 12):  # Parkmarkierungen mit Perspektive
        x0 = 640 + (k - 3) * 40
        x1 = 640 + (k - 3) * 330
        g.path(_poly([(x0 - 2, 446), (x0 + 2, 446), (x1 + 14, H), (x1 - 14, H)]), fill=C(238, 240, 246, 150))
    # Wimpelkette
    p = skia.Path(); p.moveTo(-20, 38); p.quadTo(640, 112, 1300, 38)
    g.path(p, stroke=C(70, 70, 82), width=3)
    pm = skia.PathMeasure(p, False)
    cols = [C(236, 64, 64), C(255, 208, 60), C(70, 190, 130), C(80, 150, 240)]
    n = 16
    for i in range(n):
        pos = pm.getPosTan(pm.getLength() * (i + 0.5) / n)
        x, y = pos[0].x(), pos[0].y()
        g.path(_poly([(x - 20, y), (x + 20, y), (x, y + 46)]), fill=cols[i % 4])
    for x, y, col in ((70, 250, C(236, 64, 64)), (110, 205, C(255, 208, 60)), (36, 215, C(80, 150, 240))):
        g.line(x, y + 40, x - 6, 440, stroke=C(255, 255, 255, 120), width=1.5)
        g.oval(x, y, 24, 30, shader=rad((x - 8, y - 10), 40, [C(255, 255, 255), col]))
    _cache["lot"] = g.snapshot()
    return _cache["lot"]


def price_board(g, x, y, t):
    """Schild mit durchgestrichenem Preis; t = Sekunden seit Einblendung."""
    k = overshoot(t / 0.35)
    g.c.save(); g.c.translate(x, y); g.c.scale(k, k)
    g.rrect(-120, -64, 120, 64, 16, fill=C(0, 0, 0, 70), blur=8)
    g.rrect(-120, -66, 120, 62, 16, shader=lin((0, -66), (0, 62), [C(255, 236, 120), C(255, 196, 40)]))
    g.rrect(-120, -66, 120, 62, 16, stroke=C(150, 100, 10), width=4)
    g.text("$8,500", 0, -8, 52, fill=C(130, 90, 20))
    g.line(-92, -26, 92, -26, stroke=C(220, 40, 40), width=7)
    nt = ease_out((t - 0.5) / 0.4)
    g.text("$6,500", 0, 40 - (1 - nt) * 30, 44, fill=C(200, 30, 40), stroke=C(255, 255, 255), stroke_w=3) if nt > 0 else None
    g.c.restore()


def report_paper(g, x, y, rot=-8, s=1.0, hl=0.0):
    g.c.save(); g.c.translate(x, y); g.c.rotate(rot); g.c.scale(s, s)
    g.rrect(-62, -80, 64, 82, 6, fill=C(0, 0, 0, 60), blur=6)
    g.rrect(-64, -84, 62, 78, 6, fill=C(252, 252, 250))
    g.path(_poly([(30, -84), (62, -84), (62, -52)]), fill=C(215, 218, 226))
    g.text("VEHICLE", -2, -50, 17, fill=C(80, 86, 100))
    g.text("REPORT", -2, -30, 17, fill=C(80, 86, 100))
    for i in range(3):
        g.rrect(-46, -10 + i * 14, 40 + (i % 2) * 8, -4 + i * 14, 3, fill=C(190, 196, 208))
    g.c.save(); g.c.translate(-2, 46); g.c.rotate(-6)
    g.rrect(-52, -20, 52, 20, 6, stroke=C(220, 40, 50), width=4)
    g.text("4 OWNERS", 0, 8, 19, fill=C(220, 40, 50))
    g.c.restore()
    g.c.restore()


def stamp(g, x, y, text, t, size=130, col=C(235, 45, 55), rot=-9):
    k = overshoot(t / 0.22, 2.4)
    if t < 0:
        return
    g.text(text, x, y, size, fill=col, stroke=C(255, 255, 255), stroke_w=size * 0.12, shadow=(5, 8, C(0, 0, 0, 120), 6), rot=rot, scale=k)


def bubbles(g, t, n=26, seed=1):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.random() * W + math.sin(t * 0.8 + i) * 14
        sp = rnd.uniform(18, 60)
        y = H - ((t * sp + rnd.random() * (H + 80)) % (H + 80)) + 40
        r = rnd.uniform(3, 13)
        g.circle(x, y, r, stroke=C(190, 230, 255, 120), width=1.6)
        g.circle(x - r * 0.3, y - r * 0.3, r * 0.22, fill=C(255, 255, 255, 150))
