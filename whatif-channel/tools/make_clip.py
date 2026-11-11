"""Testclip neu: Szene aus Skript 01 (ca. 20 s), alles kostenlos.
Aufruf: KOKORO_V1_DIR=/pfad/kokoro-multi-lang-v1_0 python3 make_clip.py ausgabe.mp4 [narr_voice] [sales_voice] [pip_voice]
"""
import math, subprocess, sys, wave
import numpy as np
import skia
from gfx import *
import chars, scenes, audio
from audio import SR

OUT = sys.argv[1] if len(sys.argv) > 1 else "clip.mp4"
V_NARR = sys.argv[2] if len(sys.argv) > 2 else "am_michael"
V_SALES = sys.argv[3] if len(sys.argv) > 3 else "am_onyx"
V_PIP = sys.argv[4] if len(sys.argv) > 4 else "am_puck"
FPS = 24

# (Sprecher, Text, Einstellung, Pause danach, Tempo)
LINES = [
    ("narr", "A bell rings.", "abyss", 0.30, 1.10),
    ("narr", "Low. Deep.", "abyss", 0.28, 1.05),
    ("narr", "Like a church bell underwater.", "abyss", 0.55, 1.10),
    ("sales", "One previous owner.", "lot_wide", 0.10, 1.05),
    ("narr", "says the salesman, patting the hood.", "lot_wide", 0.80, 1.12),
    ("pip", "Funny.", "pip_close", 0.25, 1.0),
    ("pip", "The report says four.", "pip_close", 0.55, 1.08),
    ("narr", "His face falls.", "sales_close", 0.35, 1.08),
    ("narr", "The price falls with it.", "price", 0.40, 1.10),
    ("narr", "Two thousand dollars, gone in ten seconds.", "price", 1.00, 1.12),
]
VOICE_OF = {"narr": V_NARR, "sales": V_SALES, "pip": V_PIP}

# ---------------------------------------------------------------- Audio vorbereiten
tl, t = [], 0.55
for sp, text, shot, pause, spd in LINES:
    x = audio.speak(text, VOICE_OF[sp], spd)
    tl.append(dict(sp=sp, text=text, shot=shot, t0=t, t1=t + len(x) / SR, x=x))
    t += len(x) / SR + pause
TOTAL = t + 0.4
mix = audio.Mix(TOTAL)
for L in tl:
    mix.add_voice(L["x"], L["t0"], 1.0 if L["sp"] == "narr" else 0.95)
mix.set_music(audio.music(TOTAL, "dark", 92), 1.0)

# Schnitte und Ereignisse
shots, cur = [], None
for L in tl:
    if cur is None or cur["name"] != L["shot"]:
        cur = dict(name=L["shot"], t0=L["t0"] - 0.06, lines=[])
        shots.append(cur)
    cur["lines"].append(L)
for i, s in enumerate(shots):
    s["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else TOTAL
    if i > 0:
        mix.add_sfx(audio.whoosh(0.35, 300, 4200, 0.45, seed=i), s["t0"] - 0.22)
EV = {}
EV["bong1"] = tl[0]["t0"] + 0.2
EV["bong2"] = tl[2]["t0"] + 0.1
EV["lie"] = tl[3]["t1"] - 0.15  # am Ende der Luege
EV["price"] = tl[8]["t0"] + 0.25
EV["gulp"] = tl[7]["t0"] + 0.15
mix.add_sfx(audio.bell(130, 3.2, 0.55), EV["bong1"])
mix.add_sfx(audio.bell(82, 3.6, 0.5), EV["bong2"])
mix.add_sfx(audio.bell(110, 3.0, 0.6), EV["lie"])
mix.add_sfx(audio.stamp_hit(0.9), EV["lie"] + 0.12)
mix.add_sfx(audio.pop(0.45), EV["lie"] + 0.12)
mix.add_sfx(audio.gulp(0.5), EV["gulp"])
mix.add_sfx(audio.coin_down(0.4), EV["price"] + 0.55)
mix.add_sfx(audio.riser(0.9, 0.3), tl[8]["t0"] - 0.85)
final = mix.render()
import scipy.io.wavfile as wf
wf.write("audio.wav", SR, (final * 32767).astype(np.int16))

# Lippenbewegung aus der Lautstaerke
ENV = {}
for L in tl:
    if L["sp"] != "narr":
        e = audio.envelope(L["x"], 0.05)
        ENV[id(L)] = e / (np.percentile(e, 95) + 1e-6)


def lip(L, t):
    e = ENV[id(L)]
    i = int((t - L["t0"]) * SR)
    return float(np.clip(e[i] if 0 <= i < len(e) else 0, 0, 1)) ** 0.8


def speaking(sp, t):
    for L in tl:
        if L["sp"] == sp and L["t0"] <= t <= L["t1"]:
            return L
    return None


def blink(t, ph):
    k = (t + ph) % 3.4
    return 1.0 if k < 0.13 else 0.0


def reach(px, py, sc, flip, side, target, bend=1):
    lx = (target[0] - px) / sc * (-1 if flip else 1)
    ly = (target[1] - py) / sc
    return chars.ik((side * 54, -100), (lx, ly), 56, 54, bend)


# ---------------------------------------------------------------- Einstellungen
def camera(g, z, cx, cy, shake=0.0, t=0.0):
    cx = min(max(cx, W / (2 * z)), W - W / (2 * z))
    cy = min(max(cy, H / (2 * z)), H - H / (2 * z))
    g.c.translate(W / 2, H / 2)
    g.c.scale(z, z)
    g.c.translate(-cx, -cy)
    if shake > 0.1:
        g.c.translate(shake * math.sin(t * 95), shake * math.cos(t * 83))


def bg(g, name):
    g.draw_image(scenes.make_lot() if name == "lot" else scenes.make_abyss(), 0, 0)


_blur_cache = {}


def bg_blur(g):
    if "lotb" not in _blur_cache:
        tmp = Gfx(); tmp.clear(C(0, 0, 0))
        tmp.draw_image(scenes.make_lot(), 0, 0, blur=9)
        _blur_cache["lotb"] = tmp.snapshot()
    g.draw_image(_blur_cache["lotb"], 0, 0)


def shot_abyss(g, t, s):
    lt = t - s["t0"]
    z = 1.0 + 0.16 * ease_inout(lt / (s["t1"] - s["t0"]))
    g.c.save(); camera(g, z, 640, 330)
    bg(g, "abyss")
    scenes.bubbles(g, t)
    ang, pulse = 0.0, 0.0
    for bt in (EV["bong1"], EV["bong2"]):
        if t >= bt:
            d = t - bt
            ang += 17 * math.exp(-d * 0.75) * math.sin(d * 6.4)
            pulse = max(pulse, math.exp(-d * 1.4))
    scenes.bell(g, 640, 280, 1.25, ang, 0.55 + 0.45 * pulse)
    scenes.rings(g, 640, 330, t - EV["bong1"], (255, 220, 120))
    scenes.rings(g, 640, 330, t - EV["bong2"], (110, 190, 255), life=2.2, speed=380)
    if 0 <= t - EV["bong1"] < 0.8:
        k = overshoot((t - EV["bong1"]) / 0.18)
        g.text("BONG", 960, 170, 150, fill=C(255, 226, 120), stroke=C(70, 35, 0), stroke_w=16, rot=8, shadow=(5, 8, C(0, 0, 0, 120), 6), scale=k * (1 - ease_inout((t - EV["bong1"] - 0.55) / 0.25)))
    g.c.restore()


def people_wide(g, t, s):
    GY = 440
    sales = speaking("sales", t)
    pat = abs(math.sin(t * 5.5)) * 14
    tgt = (484, 428 - pat)
    a0, a1 = reach(400, GY, 0.95, False, 1, tgt)
    after = t > EV["lie"]
    chars.person(g, 400, GY, chars.SALES, 0.95, arm_r=(a0, a1), arm_l=(24 + 16 * math.sin(t * 3.1), 46),
                 look=(0.4, 0), lid=blink(t, 0.3), brow_l=(-12, 6), brow_r=(-12, 6), head_rot=2 * math.sin(t * 1.4),
                 mouth_kind="talk" if sales else "smile", open_=lip(sales, t) if sales else 0, teeth=True,
                 sweat=min(1, max(0, (t - EV["lie"] - 0.1) / 0.8)) * 0.7, bob=2 * math.sin(t * 2.2))
    chars.person(g, 1190, GY, chars.PIP, 0.95, flip=True, arm_l=(12, 20), arm_r=(10, 24), look=(-0.8, 0), lid=0.3 + 0.7 * blink(t, 0.9),
                 brow_l=((-6, 3) if not after else (4, 2)), brow_r=((-6, 3) if not after else (4, 14)), head_rot=-2 * math.sin(t * 1.1),
                 mouth_kind="smile" if not after else "smirk", bob=2 * math.sin(t * 2.0 + 1))


def shot_lot_wide(g, t, s):
    lt = t - s["t0"]
    z = 1.0 + 0.06 * ease_inout(lt / (s["t1"] - s["t0"]))
    d = t - EV["lie"]
    g.c.save(); camera(g, z, 700, 380, shake=(7 * math.exp(-d * 9) if d > 0 else 0), t=t)
    bg(g, "lot")
    scenes.car(g, 470, 350, 1.75, (70, 130, 235), flip=True)
    people_wide(g, t, s)
    if d > 0:
        scenes.rings(g, 410, 255, d, (255, 70, 70), life=1.3, speed=600)
        scenes.speed_lines(g, 640, 340, t, n=24, r0=260, col=C(255, 255, 255, int(110 * math.exp(-d * 4))))
        scenes.stamp(g, 760, 205, "LIE", d, 150)
    g.c.restore()


def shot_pip_close(g, t, s):
    lt = t - s["t0"]
    z = 1.0 + 0.05 * ease_inout(lt / (s["t1"] - s["t0"]))
    g.c.save(); camera(g, z, 640, 360)
    bg_blur(g)
    cur = speaking("pip", t)
    second = t >= tl[6]["t0"] - 0.1
    px, py, sc = 800, 640, 1.55
    tgt = (px - 215, py - 255) if second else (px - 90, py - 130)
    a0, a1 = reach(px, py, sc, True, 1, tgt)
    chars.person(g, px, py, chars.PIP, sc, flip=True, arm_r=(a0, a1), arm_l=(12, 30), look=(-0.9, 0.2),
                 lid=0.4 if not second else 0.15, brow_l=(-4, 14) if not second else (8, 2), brow_r=(10, -2) if not second else (8, 2),
                 mouth_kind="talk" if cur else "smirk", open_=lip(cur, t) if cur else 0, head_rot=3 * math.sin(t * 1.6) - 3, bob=2.5 * math.sin(t * 2.1))
    if second:
        k = overshoot((t - tl[6]["t0"] + 0.1) / 0.3)
        scenes.report_paper(g, tgt[0] - 28, tgt[1] - 28, -10, 1.15 * k)
    g.c.restore()


def shot_sales_close(g, t, s):
    lt = t - s["t0"]
    z = 1.0 + 0.07 * ease_inout(lt / (s["t1"] - s["t0"]))
    g.c.save(); camera(g, z, 640, 360)
    bg_blur(g)
    sw = min(1, lt / 0.9)
    gl = t >= EV["gulp"]
    chars.person(g, 520, 650, chars.SALES, 1.55, arm_l=(30, 50), arm_r=(-30, 40), look=(0.9, 0.3), lid=0.0,
                 brow_l=(-22, 10 + 4 * sw), brow_r=(-22, 10 + 4 * sw), mouth_kind="grit" if gl else "frown", sweat=sw,
                 head_rot=-2 + 2 * math.sin(t * 7) * (1 if gl else 0), bob=2 * math.sin(t * 2.0))
    g.c.restore()


def shot_price(g, t, s):
    lt = t - s["t0"]
    z = 1.0 + 0.10 * ease_inout(lt / (s["t1"] - s["t0"]))
    g.c.save(); camera(g, z, 700, 360)
    bg(g, "lot")
    scenes.car(g, 330, 330, 2.0, (70, 130, 235), flip=True)
    scenes.price_board(g, 800, 270, t - (EV["price"] - 0.15))
    chars.person(g, 190, 470, chars.SALES, 0.95, arm_l=(22, 40), arm_r=(-24, 36), look=(0.8, 0.4), lid=0,
                 brow_l=(-20, 10), brow_r=(-20, 10), mouth_kind="grit", sweat=0.9, bob=2 * math.sin(t * 2.2))
    d = t - (EV["price"] + 0.55)
    if d > 0:
        g.text("-$2,000", 640, 130, 120, fill=C(255, 70, 70), stroke=C(255, 255, 255), stroke_w=11,
               rot=-6, scale=overshoot(d / 0.25), shadow=(5, 8, C(0, 0, 0, 120), 6))
    g.c.restore()


SHOTS = dict(abyss=shot_abyss, lot_wide=shot_lot_wide, pip_close=shot_pip_close, sales_close=shot_sales_close, price=shot_price)

# ---------------------------------------------------------------- Rendern
nframes = int(TOTAL * FPS)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", "audio.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
g = Gfx()
only = [float(a) for a in sys.argv[5:]]  # optionale Einzelbild-Zeiten
for fi in range(nframes) if not only else range(len(only)):
    t = fi / FPS if not only else only[fi]
    s = ([x for x in shots if x["t0"] <= t] or [shots[0]])[-1]
    g.clear(C(0, 0, 0))
    SHOTS[s["name"]](g, t, s)
    # Blitz bei der Luege
    if 0 <= t - EV["lie"] < 0.12:
        g.rect(0, 0, W, H, fill=C(255, 255, 255, int(120 * (1 - (t - EV["lie"]) / 0.12))))
    scenes_v = skia.Paint()
    vignette(g, 0.5)
    if only:
        from PIL import Image
        Image.fromarray(g.to_rgb()).save(f"frame_{only[fi]:.2f}.png")
    else:
        ff.stdin.write(g.to_rgb().tobytes())
ff.stdin.close(); ff.wait()
print("fertig:", OUT, round(TOTAL, 1), "s")
print("Zeitplan:", [(L["sp"], round(L["t0"], 2), round(L["t1"], 2)) for L in tl])
