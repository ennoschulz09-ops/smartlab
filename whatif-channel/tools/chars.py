"""Figuren-Rig mit Schattierung: runder Kopf (Kugel-Licht), Hoodie/Anzug, grosse Handschuhe, ausdrucksstarkes Gesicht.
Koordinaten: Ursprung = Hueftmitte, y nach unten. Pose-Winkel: 0 = nach unten haengend, positiv = nach vorn."""
import math
import skia
from gfx import C, paint, lin, rad, lerp

R = 78  # Kopfradius

PIP = dict(
    head=[C(255, 252, 246), C(249, 228, 208), C(206, 160, 138)],
    hoodie=[C(255, 178, 80), C(240, 128, 42), C(196, 86, 24)],
    hoodie_dark=C(176, 70, 18), hoodie_light=C(255, 205, 140),
    pants=[C(70, 82, 130), C(44, 52, 92)], shoe=C(250, 250, 252), sole=C(80, 200, 190),
    glove=[C(255, 255, 255), C(236, 226, 220)], style="hoodie", hair=C(92, 56, 40), eye=C(58, 32, 88),
)
SALES = dict(
    head=[C(255, 226, 196), C(240, 190, 152), C(190, 134, 104)],
    hoodie=[C(60, 74, 130), C(38, 48, 94), C(24, 30, 64)],
    hoodie_dark=C(18, 22, 50), hoodie_light=C(120, 138, 200),
    pants=[C(50, 58, 100), C(30, 36, 70)], shoe=C(40, 34, 36), sole=C(20, 18, 20),
    glove=[C(255, 226, 196), C(235, 185, 150)], style="suit", hair=C(70, 70, 82), eye=C(40, 28, 30),
)


def _limb(g, p0, ang0, l0, ang1, l1, width0, width1, shader_colors, edge):
    x1 = p0[0] + l0 * math.sin(math.radians(ang0))
    y1 = p0[1] + l0 * math.cos(math.radians(ang0))
    a = ang0 + ang1
    x2 = x1 + l1 * math.sin(math.radians(a))
    y2 = y1 + l1 * math.cos(math.radians(a))
    mid = shader_colors[1]
    g.line(p0[0], p0[1], x1, y1, stroke=edge, width=width0 + 3)
    g.line(x1, y1, x2, y2, stroke=edge, width=width1 + 3)
    g.line(p0[0], p0[1], x1, y1, stroke=mid, width=width0)
    g.line(x1, y1, x2, y2, stroke=mid, width=width1)
    # Lichtkante
    g.line(p0[0] - 4, p0[1] - 2, x1 - 4, y1 - 2, stroke=shader_colors[0], width=max(3, width0 * 0.25), alpha=0.8)
    g.circle(x1, y1, width0 * 0.5, fill=mid)
    return (x1, y1), (x2, y2), a


def _glove(g, pos, ang, cfg, size=1.0):
    x, y = pos
    g.c.save()
    g.c.translate(x, y)
    g.c.rotate(-ang + 180 if False else -ang)
    g.oval(2, 3, 17 * size, 15 * size, fill=C(0, 0, 0, 40), blur=3)
    g.oval(0, 8 * size, 18 * size, 17 * size, shader=rad((-5, 2), 30, cfg["glove"]))
    g.oval(12 * size, 2 * size, 8 * size, 5.5 * size, shader=rad((10, 0), 14, cfg["glove"]))
    g.c.restore()


def _eye_lid(g, cx, cy, lid, headc):
    if lid <= 0.02:
        return
    g.c.save()
    clip = skia.Path()
    clip.addOval(skia.Rect.MakeLTRB(cx - 11, cy - 14, cx + 11, cy + 14))
    g.c.clipPath(clip, skia.ClipOp.kIntersect, True)
    g.rect(cx - 14, cy - 18, cx + 14, cy - 14 + 28 * lid, fill=headc)
    g.line(cx - 12, cy - 14 + 28 * lid, cx + 12, cy - 14 + 28 * lid, stroke=C(70, 45, 80, 140), width=1.6)
    g.c.restore()


def mouth(g, kind, open_=0.0, teeth=False, col=C(70, 38, 70)):
    if kind == "smile":
        p = skia.Path(); p.moveTo(-15, 0); p.quadTo(0, 15, 15, 0)
        g.path(p, stroke=col, width=4)
    elif kind == "smirk":
        p = skia.Path(); p.moveTo(-12, 3); p.quadTo(4, 11, 17, -5)
        g.path(p, stroke=col, width=4)
    elif kind == "flat":
        g.line(-12, 2, 12, 2, stroke=col, width=4)
    elif kind == "frown":
        p = skia.Path(); p.moveTo(-14, 8); p.quadTo(0, -4, 14, 8)
        g.path(p, stroke=col, width=4)
    elif kind in ("open", "talk"):
        h = 6 + 30 * open_ if kind == "talk" else 28
        wd = 17 + 4 * open_ if kind == "talk" else 21
        p = skia.Path(); p.moveTo(-wd, 0); p.quadTo(0, -2, wd, 0); p.quadTo(0, h * 1.25, -wd, 0); p.close()
        g.path(p, fill=C(110, 24, 40))
        g.c.save(); g.c.clipPath(p, skia.ClipOp.kIntersect, True)
        if teeth:
            g.rect(-wd, -2, wd, 7, fill=C(255, 255, 255))
        g.oval(0, h * 0.85, wd * 0.6, h * 0.35, fill=C(236, 100, 112))
        g.c.restore()
        g.path(p, stroke=col, width=2.5)
    elif kind == "o":
        g.oval(0, 6, 8, 10, fill=C(110, 24, 40)); g.oval(0, 6, 8, 10, stroke=col, width=2.5)
    elif kind == "grit":
        g.rrect(-17, -3, 17, 11, 5, fill=C(255, 255, 255)); g.rrect(-17, -3, 17, 11, 5, stroke=col, width=2.5)
        for x in (-8, 0, 8):
            g.line(x, -3, x, 11, stroke=col, width=1.5)


def person(g, x, y, cfg, scale=1.0, flip=False, lean=0, head_rot=0, head_off=(0, 0), arm_l=(10, 10), arm_r=(-10, 10),
           leg_l=(0, 0), leg_r=(0, 0), look=(0, 0), lid=0.0, brow_l=(0, 0), brow_r=(0, 0), mouth_kind="smile",
           open_=0.0, teeth=False, sweat=0.0, shadow=True, blush=0.5, bob=0.0, glove_big=1.0):
    """Zeichnet eine Figur. brow_*: (Winkel in Grad, Hub in px); Winkel > 0 = Innenseite nach unten (streng)."""
    c = g.c
    c.save()
    c.translate(x, y + bob)
    if flip:
        c.scale(-1, 1)
    c.scale(scale, scale)
    if shadow:
        g.oval(0, 156, 74, 12, fill=C(0, 0, 0, 70), blur=7)
    c.save()
    c.rotate(lean)
    hx, hy = head_off[0], -192 + head_off[1]
    edge = lambda col: C(0, 0, 0, 0)
    # --- Beine ------------------------------------------------------------------
    pc = cfg["pants"]
    for side, lg in ((-1, leg_l), (1, leg_r)):
        hip = (side * 22, 6)
        k, ft, a2 = _limb(g, hip, lg[0], 66, lg[1], 62, 30, 27, [pc[0], pc[1]], C(0, 0, 0, 50))
        sx, sy = ft
        g.oval(sx + 12, sy + 8, 33, 17, fill=C(0, 0, 0, 40), blur=3)
        g.oval(sx + 10, sy + 6, 33, 18, shader=lin((sx, sy - 12), (sx, sy + 24), [cfg["shoe"], C(205, 208, 220)]))
        g.oval(sx + 10, sy + 17, 32, 7, fill=cfg["sole"])
    # --- Hood hinten ---------------------------------------------------------------
    hc = cfg["hoodie"]
    if cfg["style"] == "hoodie":
        g.oval(hx * 0.4, -112, 62, 30, shader=lin((0, -140), (0, -84), [hc[1], hc[2]]))
    # --- Arm hinten (ferne Seite) -------------------------------------------------------
    def arm(side, ar):
        sh = (side * 54, -100)
        e, hnd, a2 = _limb(g, sh, ar[0], 56, ar[1], 54, 30, 25, [cfg["hoodie_light"], hc[1]], C(0, 0, 0, 50))
        if cfg["style"] == "suit":
            g.circle(hnd[0], hnd[1], 15, fill=cfg["glove"][1])
        else:
            _glove(g, hnd, a2, cfg, glove_big)
    arm(-1, arm_l)
    # --- Torso --------------------------------------------------------------------------
    t = skia.Path()
    t.moveTo(-56, -104); t.cubicTo(-70, -60, -62, -10, -52, 14)
    t.quadTo(0, 30, 52, 14); t.cubicTo(62, -10, 70, -60, 56, -104)
    t.quadTo(0, -122, -56, -104); t.close()
    g.path(t, shader=lin((-60, -100), (62, 10), [hc[0], hc[1], hc[2]], [0, 0.5, 1]))
    g.path(t, stroke=C(0, 0, 0, 50), width=2.5)
    if cfg["style"] == "hoodie":
        g.rrect(-32, -40, 32, -2, 14, shader=lin((0, -40), (0, 0), [hc[1], hc[2]]))
        g.rrect(-32, -40, 32, -2, 14, stroke=C(0, 0, 0, 55), width=2)
        for sx_ in (-12, 12):
            g.line(sx_, -108, sx_ * 1.1, -66, stroke=C(255, 255, 255, 230), width=3.5)
            g.circle(sx_ * 1.1, -64, 4.5, fill=C(255, 255, 255))
        for a0, b0, c0, d0 in ((-44, -70, -36, -50), (46, -66, 38, -46), (-6, -24, -14, 8), (10, -22, 18, 6)):
            p = skia.Path(); p.moveTo(a0, b0); p.quadTo((a0 + c0) / 2 + 6, (b0 + d0) / 2, c0, d0)
            g.path(p, stroke=cfg["hoodie_dark"], width=2.4, alpha=0.55)
        g.line(-50, -88, -54, -30, stroke=cfg["hoodie_light"], width=4, alpha=0.7)
    else:  # Anzug
        g.path(_tri((-18, -108), (18, -108), (0, -40)), fill=C(250, 250, 252))
        g.path(_tri((-18, -108), (-2, -108), (-34, -34)), fill=cfg["hoodie_light"], alpha=0.8)
        g.path(_tri((18, -108), (2, -108), (34, -34)), fill=cfg["hoodie_light"], alpha=0.8)
        tie = skia.Path(); tie.moveTo(-7, -104); tie.lineTo(7, -104); tie.lineTo(11, -50); tie.lineTo(0, -34); tie.lineTo(-11, -50); tie.close()
        g.path(tie, shader=lin((-10, -100), (10, -40), [C(250, 90, 80), C(190, 30, 40)]))
    # Hals
    g.rrect(-15, -126, 15, -100, 8, fill=cfg["head"][2])
    # --- vordere Arm -----------------------------------------------------------------
    arm(1, arm_r)
    # --- Kopf -----------------------------------------------------------------------
    c.save()
    c.translate(hx, hy)
    c.rotate(head_rot)
    hd = cfg["head"]
    g.circle(2, 6, R, fill=C(0, 0, 0, 35), blur=6)
    g.circle(0, 0, R, shader=rad((-R * 0.32, -R * 0.38), R * 1.7, [hd[0], hd[1], hd[2]], [0, 0.55, 1.0]))
    g.c.save()
    cp = skia.Path(); cp.addCircle(0, 0, R)
    c.clipPath(cp, skia.ClipOp.kIntersect, True)
    g.oval(0, R * 0.95, R * 0.95, R * 0.4, fill=C(60, 30, 40, 60), blur=10)  # Schatten unten
    g.oval(-R * 0.4, -R * 0.55, R * 0.28, R * 0.16, fill=C(255, 255, 255, 190), blur=6)  # Glanz
    g.circle(0, 0, R - 1.5, stroke=C(255, 255, 255, 60), width=3, blur=2)
    c.restore()
    g.circle(0, 0, R, stroke=C(0, 0, 0, 38), width=2)
    # Haare
    if cfg["style"] == "hoodie":
        for dx, h_, w_ in ((-8, 17, 7), (2, 23, 8), (12, 15, 6)):
            p = skia.Path(); p.moveTo(dx - w_, -R + 6); p.quadTo(dx - 2, -R - h_ * 0.5, dx + 6, -R - h_); p.quadTo(dx + w_ * 0.8, -R - 6, dx + w_, -R + 8); p.close()
            g.path(p, fill=cfg["hair"])
    else:
        p = skia.Path(); p.moveTo(-R + 4, -14); p.cubicTo(-R - 6, -R * 0.9, -20, -R - 16, 24, -R - 10); p.cubicTo(R - 2, -R * 0.7, R + 2, -26, R - 4, -10)
        p.cubicTo(R * 0.6, -R * 0.55, -R * 0.4, -R * 0.62, -R + 4, -14); p.close()
        g.path(p, shader=lin((-R, -R), (R, -20), [C(110, 110, 124), cfg["hair"]]))
        for sd in (-1, 1):
            g.oval(sd * (R - 2), 6, 11, 15, fill=hd[1]); g.oval(sd * (R - 2), 6, 11, 15, stroke=C(0, 0, 0, 40), width=1.5)
    # Gesicht
    ex_look = (look[0] * 5, look[1] * 4)
    for side, br in ((-1, brow_l), (1, brow_r)):
        ex, ey = side * 27, 8
        g.oval(ex, ey, 10.5, 13, fill=C(255, 255, 255)) if cfg["style"] == "suit" else None
        g.oval(ex + ex_look[0], ey + ex_look[1], 8.5 if cfg["style"] != "suit" else 5.5, 11 if cfg["style"] != "suit" else 7, fill=cfg["eye"])
        g.circle(ex + ex_look[0] - 2.5, ey + ex_look[1] - 4, 2.6, fill=C(255, 255, 255, 230))
        _eye_lid(g, ex, ey, lid, hd[1])
        ang, rise = br
        by = ey - 24 - rise
        g.c.save(); g.c.translate(ex, by); g.c.rotate(-side * ang * -1 if False else side * -ang)
        g.line(-15, 0, 15, 0, stroke=cfg["eye"] if cfg["style"] == "hoodie" else cfg["hair"], width=8)
        g.c.restore()
        if blush > 0:
            g.oval(side * 44, 30, 13, 7.5, fill=C(255, 110, 110, int(95 * blush)), blur=3)
    c.save(); c.translate(0, 40)
    mouth(g, mouth_kind, open_, teeth)
    c.restore()
    if sweat > 0:
        for i, (dx, dy) in enumerate(((-R + 4, -26), (R - 8, -34), (-R + 24, -60))):
            yy = dy + sweat * (14 + i * 10)
            p = skia.Path(); p.moveTo(dx, yy - 14); p.quadTo(dx + 9, yy + 2, dx, yy + 7); p.quadTo(dx - 9, yy + 2, dx, yy - 14)
            g.path(p, shader=lin((dx, yy - 14), (dx, yy + 7), [C(190, 230, 255), C(70, 150, 240)]), alpha=min(1, sweat * 2))
    c.restore()  # Kopf
    c.restore()  # lean
    c.restore()


def _tri(a, b, cc):
    p = skia.Path(); p.moveTo(*a); p.lineTo(*b); p.lineTo(*cc); p.close(); return p


def ik(shoulder, target, l1, l2, bend=1):
    """Zwei-Gelenk-IK: liefert (winkel_oberarm, relativer_winkel_unterarm) in Grad (0 = nach unten, + = nach vorn)."""
    sx, sy = shoulder
    dx, dy = target[0] - sx, target[1] - sy
    d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 1e-3))
    base = math.atan2(dx, dy)
    inner = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    a0 = base - bend * inner
    ex, ey = sx + l1 * math.sin(a0), sy + l1 * math.cos(a0)
    fore = math.atan2(target[0] - ex, target[1] - ey)
    return math.degrees(a0), math.degrees(fore - a0)
