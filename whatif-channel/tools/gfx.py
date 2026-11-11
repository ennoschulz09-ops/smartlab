"""Zeichen-Grundlagen auf Basis von Skia (kostenlos): Verlaeufe, Schatten, Glow, Text mit Umrandung."""
import math
import numpy as np
import skia

W, H = 1280, 720
try:  # runde, dicke Schrift wie beim Vorbild (pip install font-fredoka-one)
    import font_fredoka_one
    FONT_PATH = font_fredoka_one.FredokaOne
except Exception:
    FONT_PATH = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
_fonts = {}


def C(r, g, b, a=255):
    return skia.Color(int(r), int(g), int(b), int(a))


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_inout(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def overshoot(t, k=1.9):
    """Federnder Einlauf 0->1 mit leichtem Ueberschwingen."""
    t = max(0.0, min(1.0, t))
    return 1 + (k + 1) * (t - 1) ** 3 + k * (t - 1) ** 2


def lin(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear([p0, p1], colors, pos)


def rad(c, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(c, r, colors, pos)


def paint(fill=None, shader=None, stroke=None, width=0, blur=0, alpha=None, cap="round"):
    p = skia.Paint(AntiAlias=True)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(width)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        p.setColor(stroke)
    if fill is not None:
        p.setColor(fill)
    if shader is not None:
        p.setShader(shader)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if alpha is not None:
        p.setAlphaf(alpha)
    return p


def font(size):
    key = int(size)
    if key not in _fonts:
        _fonts[key] = skia.Font(skia.Typeface.MakeFromFile(FONT_PATH), size)
    return _fonts[key]


class Gfx:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.surface = skia.Surface(w, h)
        self.c = self.surface.getCanvas()

    def clear(self, color=None):
        self.c.clear(color if color is not None else C(0, 0, 0))

    # --- Formen -------------------------------------------------------------
    def circle(self, x, y, r, **kw):
        self.c.drawCircle(x, y, r, paint(**kw))

    def oval(self, x, y, rx, ry, **kw):
        self.c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), paint(**kw))

    def rrect(self, x0, y0, x1, y1, r, **kw):
        self.c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), r, r), paint(**kw))

    def rect(self, x0, y0, x1, y1, **kw):
        self.c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(**kw))

    def line(self, x0, y0, x1, y1, **kw):
        self.c.drawLine(x0, y0, x1, y1, paint(**kw))

    def path(self, p, **kw):
        self.c.drawPath(p, paint(**kw))

    # --- Text ------------------------------------------------------------------
    def text(self, s, x, y, size, fill=C(255, 255, 255), stroke=None, stroke_w=0, shadow=None, anchor="center", rot=0, scale=1.0):
        f = font(size)
        w = f.measureText(s)
        ox = -w / 2 if anchor == "center" else 0
        self.c.save()
        self.c.translate(x, y)
        self.c.rotate(rot)
        self.c.scale(scale, scale)
        if shadow:
            sp = paint(stroke=shadow[2], width=stroke_w + 2, blur=shadow[3] if len(shadow) > 3 else 0)
            self.c.drawString(s, ox + shadow[0], shadow[1], f, sp)
        if stroke is not None and stroke_w > 0:
            self.c.drawString(s, ox, 0, f, paint(stroke=stroke, width=stroke_w))
        self.c.drawString(s, ox, 0, f, paint(fill=fill))
        self.c.restore()

    # --- Ausgabe ---------------------------------------------------------------
    def to_rgb(self):
        a = self.surface.makeImageSnapshot().toarray()  # RGBA
        return np.ascontiguousarray(a[:, :, [2, 1, 0]])  # Skia liefert BGRA

    def snapshot(self):
        return self.surface.makeImageSnapshot()

    def draw_image(self, img, x=0, y=0, blur=0, alpha=1.0):
        p = skia.Paint(AntiAlias=True)
        if blur:
            p.setImageFilter(skia.ImageFilters.Blur(blur, blur))
        p.setAlphaf(alpha)
        self.c.drawImage(img, x, y, skia.SamplingOptions(skia.FilterMode.kLinear), p)


def vignette(g, strength=0.55):
    g.c.drawRect(skia.Rect.MakeWH(g.w, g.h), paint(shader=rad((g.w / 2, g.h / 2), g.w * 0.75,
                                                              [C(0, 0, 0, 0), C(0, 0, 0, 0), C(0, 0, 0, int(255 * strength))], [0, 0.55, 1])))
