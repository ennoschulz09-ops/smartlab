"""2D-Erklaergrafik (dunkelviolettes Gitter, leuchtende Elemente, Pillen) und Overlays fuer die 3D-Szenen. Skia, kostenlos."""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import skia
from gfx import C, W, H, Gfx, lin, rad, paint, ease_out, ease_inout, overshoot, lerp

INTER = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
_uf = {}
GOLD = (255, 205, 90)
LAV = (190, 170, 255)


def ufont(sz):
    k = int(sz)
    if k not in _uf:
        _uf[k] = skia.Font(skia.Typeface.MakeFromFile(INTER), sz)
    return _uf[k]


def utext(g, s, x, y, size, fill=C(255, 255, 255), spacing=0.0, anchor="center"):
    f = ufont(size)
    if spacing:
        w = sum(f.measureText(ch) for ch in s) + spacing * (len(s) - 1)
        cx = x - w / 2 if anchor == "center" else x
        for ch in s:
            g.c.drawString(ch, cx, y, f, paint(fill=fill)); cx += f.measureText(ch) + spacing
    else:
        w = f.measureText(s)
        g.c.drawString(s, x - w / 2 if anchor == "center" else x, y, f, paint(fill=fill))
    return f.measureText(s)


def pill(g, x, y, text, size=26, fill=C(22, 12, 40, 236), color=C(255, 255, 255), k=1.0, border=C(255, 255, 255, 46), icon=None, alpha=1.0):
    if k <= 0.01:
        return
    f = ufont(size); w = f.measureText(text) + size * 1.5 + (size * 1.2 if icon else 0); h = size * 1.9
    g.c.save(); g.c.translate(x, y); g.c.scale(k, k)
    if alpha < 1:
        g.c.saveLayerAlpha(None, int(255 * alpha))
    g.rrect(-w / 2 + 2, -h / 2 + 6, w / 2 + 2, h / 2 + 6, h / 2, fill=C(0, 0, 0, 70), blur=8)
    g.rrect(-w / 2, -h / 2, w / 2, h / 2, h / 2, fill=fill)
    g.rrect(-w / 2, -h / 2, w / 2, h / 2, h / 2, stroke=border, width=1.6)
    off = size * 0.6 if icon else 0
    if icon == "check":
        g.circle(-w / 2 + size * 1.0, 0, size * 0.5, fill=C(70, 200, 120)); g.path(_pl([(-w / 2 + size * 0.78, 0), (-w / 2 + size * 0.95, size * 0.2), (-w / 2 + size * 1.25, -size * 0.18)]), stroke=C(255, 255, 255), width=size * 0.14)
    utext(g, text, off, size * 0.34, size, color)
    if alpha < 1:
        g.c.restore()
    g.c.restore()


def _pl(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def bubble(g, x, y, text, size=26, tail=(0, 40), k=1.0, fill=C(255, 255, 255), color=C(40, 24, 64)):
    if k <= 0.01:
        return
    f = ufont(size); w = f.measureText(text) + size * 1.6; h = size * 2.0
    g.c.save(); g.c.translate(x, y); g.c.scale(k, k)
    g.rrect(-w / 2 + 3, -h / 2 + 6, w / 2 + 3, h / 2 + 6, h * 0.42, fill=C(0, 0, 0, 60), blur=8)
    g.rrect(-w / 2, -h / 2, w / 2, h / 2, h * 0.42, fill=fill)
    tx, ty = tail
    g.path(_pl([(-12 + tx * 0.2, h / 2 - 2), (14 + tx * 0.2, h / 2 - 2), (tx, h / 2 + ty)]), fill=fill)
    utext(g, text, 0, size * 0.34, size, color)
    g.c.restore()


def bell_icon(g, x, y, s=1.0, glow=0.0, gray=False, ring_age=-1, ring_col=GOLD, swing=0.0):
    c = g.c
    if glow > 0 and not gray:
        g.circle(x, y, 150 * s, shader=rad((x, y), 150 * s, [C(*GOLD, int(170 * glow)), C(*GOLD, 0)]))
    if ring_age >= 0:
        for k in range(3):
            a = ring_age - k * 0.2
            if 0 <= a < 1.4:
                r = (40 + a * 150) * s; al = int(255 * (1 - a / 1.4) ** 1.4)
                g.circle(x, y, r, stroke=C(*ring_col, int(al * 0.5)), width=8 * s, blur=6); g.circle(x, y, r, stroke=C(*ring_col, al), width=3.4 * s)
    c.save(); c.translate(x, y - 40 * s); c.rotate(swing); c.scale(s, s); c.translate(0, 40)
    b = skia.Path(); b.moveTo(-46, 40); b.cubicTo(-48, -22, -28, -46, 0, -46); b.cubicTo(28, -46, 48, -22, 46, 40); b.lineTo(66, 68); b.quadTo(0, 80, -66, 68); b.close()
    cols = [C(200, 190, 215), C(150, 142, 170), C(110, 104, 130)] if gray else [C(255, 236, 150), C(255, 196, 58), C(190, 124, 24)]
    g.path(b, shader=lin((-60, -40), (60, 70), cols, [0, 0.5, 1]))
    g.path(b, stroke=C(70, 40, 10, 120), width=2.4)
    g.circle(0, -52, 9, stroke=C(150, 150, 170) if gray else C(210, 150, 40), width=5)
    g.circle(0, 82, 11, fill=C(120, 114, 140) if gray else C(210, 150, 40))
    if not gray:
        g.path(_pl([(-34, 20), (-26, -22), (-20, -34), (-16, -34), (-22, 14), (-28, 50)]), fill=C(255, 255, 255, 110))
    c.restore()


def grid_bg(g, t):
    g.rect(0, 0, W, H, shader=rad((W / 2, H * 0.45), W * 0.8, [C(58, 30, 104), C(30, 16, 62), C(14, 8, 32)], [0, 0.55, 1]))
    for x in range(0, W + 1, 56):
        g.line(x, 0, x, H, stroke=C(190, 160, 255, 14), width=1)
    for y in range(0, H + 1, 56):
        g.line(0, y, W, y, stroke=C(190, 160, 255, 14), width=1)
    rnd = random.Random(7)
    for i in range(26):
        x = rnd.random() * W; y = (rnd.random() * H - t * rnd.uniform(6, 22)) % H
        g.circle(x, y, rnd.uniform(1.2, 2.8), fill=C(220, 200, 255, int(rnd.uniform(40, 110))))
    g.line(0, 640, W, 640, stroke=C(200, 170, 255, 40), width=1.5)


def mini(g, x, y, s=1.0, hood=(255, 159, 67), head=(255, 241, 230), beanie=None, hair=None, tie=False, lid=0.55, mood="smirk", look=0.0, arms=(0.0, 0.0), bob=0.0):
    """Kleine 2D-Figur (Kugelkopf, minimales Gesicht). (x, y) = Boden, Hoehe ca. 230*s."""
    y = y + bob
    g.oval(x, y + 2, 52 * s, 9 * s, fill=C(0, 0, 0, 80), blur=5)
    for sd in (-1, 1):
        g.line(x + sd * 11 * s, y - 62 * s, x + sd * 11 * s, y - 8 * s, stroke=C(86, 96, 160), width=11 * s)
        g.oval(x + sd * 12 * s, y - 4 * s, 15 * s, 8 * s, fill=C(246, 242, 255))
    g.rrect(x - 30 * s, y - 128 * s, x + 30 * s, y - 56 * s, 22 * s, shader=lin((x - 30 * s, y - 128 * s), (x + 30 * s, y - 56 * s), [C(*[min(255, int(v * 1.12)) for v in hood]), C(*hood), C(*[int(v * 0.78) for v in hood])]))
    for sd, ar in ((-1, arms[0]), (1, arms[1])):
        sx, sy = x + sd * 30 * s, y - 118 * s
        hx, hy = sx + sd * (10 + 22 * ar) * s, sy + (52 - 34 * ar) * s
        g.line(sx, sy, hx, hy, stroke=C(*hood), width=12 * s)
        g.circle(hx, hy, 11 * s, fill=C(248, 244, 255))
    if tie:
        g.path(_pl([(x - 5 * s, y - 126 * s), (x + 5 * s, y - 126 * s), (x + 7 * s, y - 92 * s), (x, y - 84 * s), (x - 7 * s, y - 92 * s)]), fill=C(224, 56, 74))
    else:
        for sd in (-1, 1):
            g.line(x + sd * 6 * s, y - 118 * s, x + sd * 6 * s, y - 92 * s, stroke=C(255, 220, 235), width=2.6 * s)
    g.rrect(x - 5 * s, y - 150 * s, x + 5 * s, y - 126 * s, 4 * s, fill=C(244, 214, 232))
    hy = y - 192 * s; R = 48 * s
    g.circle(x, hy, R, shader=rad((x - R * 0.3, hy - R * 0.4), R * 1.8, [C(*[min(255, v + 6) for v in head]), C(*head), C(*[int(v * 0.8) for v in head])], [0, 0.5, 1]))
    if beanie:
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - R, hy - R, x + R, hy + R), 188, 164); p.close()
        g.path(p, fill=C(*beanie)); g.rrect(x - R * 0.98, hy - R * 0.52, x + R * 0.98, hy - R * 0.3, 7 * s, fill=C(244, 236, 255)); g.circle(x, hy - R - 6 * s, 9 * s, fill=C(244, 236, 255))
    if hair:
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - R, hy - R, x + R, hy + R), 190, 160); p.close(); g.path(p, fill=C(*hair))
    ink = C(42, 24, 64)
    for sd in (-1, 1):
        ex = x + sd * 17 * s + look * 3 * s; ey = hy + 4 * s
        g.oval(ex, ey + 4 * s, 4.5 * s, 6.5 * s * (1 - lid * 0.5), fill=ink)
        g.line(ex - 12 * s, ey - 3 * s, ex + 12 * s, ey - 4 * s, stroke=ink, width=4.4 * s)
        g.line(ex - 11 * s, ey - 19 * s - (4 * s if sd > 0 and mood == "smirk" else 0), ex + 11 * s, ey - 19 * s, stroke=ink, width=5 * s)
    p = skia.Path()
    if mood == "smirk":
        p.moveTo(x - 11 * s, hy + 28 * s); p.quadTo(x + 4 * s, hy + 34 * s, x + 14 * s, hy + 24 * s)
    elif mood == "flat":
        p.moveTo(x - 10 * s, hy + 28 * s); p.lineTo(x + 10 * s, hy + 28 * s)
    else:
        p.moveTo(x - 12 * s, hy + 26 * s); p.quadTo(x, hy + 38 * s, x + 12 * s, hy + 26 * s)
    g.path(p, stroke=ink, width=4 * s)


# ---------------------------------------------------------------- Erklaerszene
def title_block(g, label, title, k):
    if k <= 0:
        return
    a = min(1, k)
    utext(g, label, 640, 78, 22, C(*LAV, int(190 * a)), spacing=7)
    g.text(title, 640, 150 + (1 - ease_out(k)) * 20, 70, fill=C(255, 236, 190, int(255 * a)), shadow=(0, 6, C(0, 0, 0, 120), 6))


def explainer(g, t, B):
    grid_bg(g, t)
    lt = lambda n: t - B[n]
    on = lambda n: t >= B[n]
    # --- Titel
    if on("title") and t < B["r1a"]:
        k = overshoot(lt("title") / 0.4)
        pill(g, 640, 205, "THE BELL", 26, k=k)
        g.text("3 RULES", 640, 360, 150, fill=C(255, 236, 190), shadow=(0, 10, C(0, 0, 0, 130), 8), scale=max(0.01, k))
        bell_icon(g, 640, 500, 0.9 * k, glow=0.8, ring_age=(lt("title") % 1.6), swing=10 * math.sin(lt("title") * 7) * math.exp(-lt("title") * 0.5))
    # --- Regel 1
    if on("r1a") and t < B["r2"]:
        title_block(g, "RULE 1", "ONLY LIES", ease_out(lt("r1a") / 0.35))
        g.line(640, 220, 640, 620, stroke=C(200, 170, 255, 36), width=2)
        # Luege (rechts)
        ka = overshoot(lt("r1a") / 0.45)
        mini(g, 900, 585, 1.3 * max(0.01, ka), hood=(43, 53, 102), head=(255, 233, 220), hair=(58, 58, 72), tie=True, lid=0.1, mood="smile", bob=2 * math.sin(t * 2))
        bubble(g, 900, 218, "Only one owner.", 28, tail=(0, 36), k=overshoot((lt("r1a") - 0.25) / 0.35))
        la = lt("r1a") - 0.9
        if la >= 0:
            bell_icon(g, 1090, 440, 0.9, glow=1.0, ring_age=la, ring_col=(255, 205, 90), swing=14 * math.sin(la * 9) * math.exp(-la * 1.2))
            pill(g, 1090, 560, "LIE", 30, fill=C(220, 44, 60, 245), k=overshoot((la - 0.1) / 0.3))
        # Irrtum (links)
        if on("r1b"):
            kb = overshoot(lt("r1b") / 0.45)
            mini(g, 330, 585, 1.3 * max(0.01, kb), lid=0.35, mood="flat", look=0.6, bob=2 * math.sin(t * 2 + 1))
            bubble(g, 330, 218, "Maybe three?", 28, tail=(0, 36), k=overshoot((lt("r1b") - 0.25) / 0.35))
            lb = lt("r1b") - 0.7
            if lb >= 0:
                bell_icon(g, 520, 440, 0.9 * overshoot(lb / 0.3), gray=True)
                pill(g, 520, 560, "MISTAKE · NO BELL", 22, k=overshoot((lb - 0.15) / 0.3))
        cnt = 1 if lt("r1a") > 0.95 else 0
        pill(g, 640, 668, f"BELLS TODAY   {cnt}", 28, k=ease_out(lt("r1a") / 0.4))
    # --- Regel 2
    if on("r2") and t < B["r3"]:
        title_block(g, "RULE 2", "TEN METERS", ease_out(lt("r2") / 0.35))
        r = ease_out(lt("r2") / 1.0) * 250
        g.circle(640, 450, r, fill=C(255, 205, 90, 22)); g.circle(640, 450, r, stroke=C(255, 205, 90, 210), width=4)
        mini(g, 640, 600, 1.3, hood=(255, 159, 67), beanie=(47, 196, 184), lid=0.4, bob=2 * math.sin(t * 2))
        for (px, py, inside) in ((470, 520, True), (810, 540, True), (1060, 520, False)):
            kk = overshoot((lt("r2") - 0.5) / 0.4)
            mini(g, px, py + 60, 0.7 * max(0.01, kk), hood=(120, 200, 160) if inside else (180, 180, 200), lid=0.5, mood="smile", bob=1.5 * math.sin(t * 2 + px))
            if lt("r2") > 1.0:
                if inside:
                    bell_icon(g, px, py - 130, 0.4, glow=0.8, ring_age=(lt("r2") - 1.0) % 1.5)
                else:
                    pill(g, px, py - 120, "...", 24, k=1.0)
        pill(g, 905, 255, "10 m", 34, k=overshoot((lt("r2") - 0.7) / 0.35), fill=C(255, 205, 90, 245), color=C(40, 24, 10))
    # --- Regel 3
    if on("r3") and t < B["end"]:
        title_block(g, "RULE 3", "NEVER THE TRUTH", ease_out(lt("r3") / 0.35))
        bell_icon(g, 330, 440, 1.2 * overshoot(lt("r3") / 0.4), glow=1.0, ring_age=lt("r3") % 1.7, swing=12 * math.sin(lt("r3") * 8) * math.exp(-(lt("r3") % 1.7) * 1.3))
        pill(g, 560, 440, "LIE", 36, fill=C(220, 44, 60, 245), k=overshoot((lt("r3") - 0.6) / 0.3))
        g.line(620, 440, 760, 440, stroke=C(200, 170, 255, int(180 * min(1, max(0, (lt("r3") - 0.9) / 0.3)))), width=5)
        kq = overshoot((lt("r3") - 1.3) / 0.45)
        g.circle(900, 440, 120 * max(0.01, kq), shader=rad((900, 440), 120, [C(255, 255, 255, 50), C(255, 255, 255, 6)]))
        g.text("?", 900, 500, 190, fill=C(255, 236, 190), scale=max(0.01, kq) * (1 + 0.05 * math.sin(t * 5)))
        pill(g, 900, 610, "WHAT IS TRUE?", 28, k=overshoot((lt("r3") - 1.6) / 0.35))


def endcard(g, t, t0):
    lt = t - t0
    g.rect(0, 0, W, H, shader=lin((0, 0), (0, H), [C(8, 22, 52), C(18, 70, 110), C(28, 110, 140)], [0, 0.6, 1]))
    for x, w_ in ((180, 90), (520, 130), (980, 110)):
        p = _pl([(x - w_ * 0.4, 0), (x + w_ * 0.4, 0), (x + w_ * 1.6 + 50, H), (x - w_ * 1.2 + 50, H)])
        g.path(p, shader=lin((0, 0), (0, H), [C(150, 220, 255, 52), C(150, 220, 255, 0)]), blur=14)
    rnd = random.Random(3)
    for i in range(22):
        x = rnd.random() * W; y = H - ((t * rnd.uniform(14, 50) + rnd.random() * H) % H); r = rnd.uniform(3, 11)
        g.circle(x, y, r, stroke=C(190, 230, 255, 110), width=1.6)
    k = overshoot(lt / 0.5)
    bell_icon(g, 330, 360, 2.5 * max(0.01, k), glow=1.0, ring_age=lt % 1.8, swing=14 * math.sin(lt * 7) * math.exp(-(lt % 1.8) * 1.2))
    g.text("WOULD YOU WANT TO", 835, 300, 54, fill=C(255, 255, 255), stroke=C(20, 20, 70), stroke_w=10, shadow=(0, 8, C(0, 0, 0, 120), 6), scale=max(0.01, overshoot((lt - 0.15) / 0.4)))
    g.text("HEAR EVERY LIE?", 835, 405, 84, fill=C(255, 224, 40), stroke=C(30, 20, 90), stroke_w=18, shadow=(0, 12, C(0, 0, 0, 140), 8), scale=max(0.01, overshoot((lt - 0.35) / 0.45)))
    sub = lt - 1.2
    pill(g, 835, 515, "TELL US BELOW", 28, k=overshoot((sub - 0.1) / 0.35))
    # Abonnieren-Knopf (rot -> grau mit Haken)
    bt = lt - 1.9
    if bt > 0:
        done = bt > 0.9
        kk = overshoot(bt / 0.35)
        pill(g, 1090, 640, "SUBSCRIBED" if done else "SUBSCRIBE", 24, fill=C(120, 120, 134, 240) if done else C(222, 40, 52, 245), k=kk, icon="check" if done else None)
        if 0.85 < bt < 1.3:
            a = (bt - 0.85) / 0.45
            g.circle(1090, 640, 30 + 60 * a, stroke=C(255, 255, 255, int(200 * (1 - a))), width=3)


# ---------------------------------------------------------------- Overlays ueber 3D
def hud(g, t, bongs):
    x, y = 1218, 62
    g.circle(x, y, 40, fill=C(22, 12, 40, 225)); g.circle(x, y, 40, stroke=C(*GOLD, 200), width=2.5)
    age = min([t - b for b in bongs if t >= b] or [9])
    bell_icon(g, x, y + 4, 0.34, glow=0.0, swing=10 * math.sin(age * 9) * math.exp(-age * 1.4) if age < 3 else 0)
    if age < 1.4:
        a = age / 1.4
        g.circle(x, y, 40 + 26 * a, stroke=C(*GOLD, int(220 * (1 - a))), width=3)
