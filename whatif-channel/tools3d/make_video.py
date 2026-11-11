"""Kurzes Beispielvideo (3D-Szenen + 2D-Erklaergrafik + Ton), komplett kostenlos.
Aufruf:
  KOKORO_V1_DIR=/pfad/kokoro-multi-lang-v1_0 python3 make_video.py ausgabe.mp4 [narr_voice sales_voice hero_voice]
  ... --stills 1.0,5.0,12.0   (nur Einzelbilder als PNG, zum Pruefen)
"""
import json, math, os, subprocess, sys, time
import numpy as np
import skia
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from gfx import C, W, H, Gfx
import audio
import explainer as X
from audio import SR

args = [a for a in sys.argv[1:] if not a.startswith("--")]
STILLS = None
if "--stills" in sys.argv:
    STILLS = [float(v) for v in sys.argv[sys.argv.index("--stills") + 1].split(",")]
    args = [a for a in args if a != sys.argv[sys.argv.index("--stills") + 1]]
OUT = args[0] if args else "beispiel.mp4"
V = dict(narr=args[1] if len(args) > 1 else "am_michael", sales=args[2] if len(args) > 2 else "am_onyx", hero=args[3] if len(args) > 3 else "am_puck")
FPS = 24
WORK = os.environ.get("WORK", os.path.join(HERE, "work")); os.makedirs(WORK, exist_ok=True)
FRAMES = os.path.join(WORK, "frames3d")

# (Sprecher, Text, Einstellung, Pause danach, Tempo)
LINES = [
    ("narr", "A bell rings.", "bell_wide", 0.30, 1.10),
    ("narr", "Low. Deep. Like a church bell underwater.", "bell_close", 0.55, 1.10),
    ("sales", "One previous owner.", "lot_two", 1.00, 1.05),
    ("hero", "Funny.", "hero_close", 0.22, 1.00),
    ("hero", "The report says four.", "hero_close", 0.50, 1.08),
    ("narr", "His face falls.", "sales_close", 0.55, 1.08),
    ("narr", "Three rules.", "explainer", 0.25, 1.08),
    ("narr", "One. Only lies ring the bell.", "explainer", 0.30, 1.10),
    ("narr", "Honest mistakes stay silent.", "explainer", 0.40, 1.10),
    ("narr", "Two. Ten meters, no more.", "explainer", 0.40, 1.10),
    ("narr", "Three. It never tells you the truth.", "explainer", 0.80, 1.10),
    ("narr", "Would you want to hear every lie?", "endcard", 2.60, 1.00),
]
SHOTS3D = {"bell_wide", "bell_close", "lot_two", "hero_close", "sales_close"}

# ---------------------------------------------------------------- Zeitplan und Stimmen
tl, t = [], 0.55
for sp, text, shot, pause, spd in LINES:
    x = audio.speak(text, V[sp], spd)
    tl.append(dict(sp=sp, text=text, shot=shot, t0=t, t1=t + len(x) / SR, x=x))
    t += len(x) / SR + pause
TOTAL = t + 0.2
shots = []
for L in tl:
    if not shots or shots[-1]["name"] != L["shot"]:
        shots.append(dict(name=L["shot"], t0=0.0 if not shots else L["t0"] - 0.06))
for i, s in enumerate(shots):
    s["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else TOTAL
B = dict(title=tl[6]["t0"] - 0.05, r1a=tl[7]["t0"] - 0.05, r1b=tl[8]["t0"] - 0.05, r2=tl[9]["t0"] - 0.05, r3=tl[10]["t0"] - 0.05, end=[s for s in shots if s["name"] == "endcard"][0]["t0"])
EV = dict(bong1=tl[0]["t0"] + 0.2, bong2=tl[1]["t0"] + 0.1, lie=tl[2]["t1"] + 0.05, gulp=tl[5]["t0"] + 0.15)

# ---------------------------------------------------------------- Ton
mix = audio.Mix(TOTAL)
for L in tl:
    mix.add_voice(L["x"], L["t0"], 1.0 if L["sp"] == "narr" else 0.95)
mix.set_music(audio.music(TOTAL, "dark", 92), 1.0)
for i, s in enumerate(shots):
    if i > 0:
        mix.add_sfx(audio.whoosh(0.35, 300, 4200, 0.42, seed=i), s["t0"] - 0.22)
mix.add_sfx(audio.bell(130, 3.2, 0.55), EV["bong1"])
mix.add_sfx(audio.bell(82, 3.6, 0.5), EV["bong2"])
mix.add_sfx(audio.bell(110, 3.0, 0.6), EV["lie"])
mix.add_sfx(audio.stamp_hit(0.9), EV["lie"] + 0.12)
mix.add_sfx(audio.pop(0.45), EV["lie"] + 0.12)
mix.add_sfx(audio.gulp(0.5), EV["gulp"])
mix.add_sfx(audio.pop(0.4), B["title"] + 0.1)
mix.add_sfx(audio.bell(110, 2.4, 0.4), B["r1a"] + 0.9)
mix.add_sfx(audio.pop(0.4), B["r1a"] + 1.0)
mix.add_sfx(audio.pop(0.3), B["r1b"] + 0.7)
mix.add_sfx(audio.whoosh(0.5, 200, 2600, 0.35, seed=11), B["r2"] + 0.05)
mix.add_sfx(audio.pop(0.35), B["r2"] + 0.7)
mix.add_sfx(audio.bell(130, 2.4, 0.4), B["r3"] + 0.05)
mix.add_sfx(audio.pop(0.4), B["r3"] + 0.6)
mix.add_sfx(audio.riser(1.1, 0.3), B["r3"] + 0.25)
mix.add_sfx(audio.pop(0.45), B["r3"] + 1.3)
mix.add_sfx(audio.riser(0.8, 0.28), B["end"] - 0.7)
mix.add_sfx(audio.bell(98, 3.4, 0.5), B["end"] + 0.1)
mix.add_sfx(audio.pop(0.5), B["end"] + 1.9)
mix.add_sfx(audio.coin_down(0.35), B["end"] + 2.8)
final = mix.render()
import scipy.io.wavfile as wf
wf.write(os.path.join(WORK, "audio.wav"), SR, (final * 32767).astype(np.int16))

ENV = {}
for L in tl:
    if L["sp"] != "narr":
        e = audio.envelope(L["x"], 0.05); ENV[id(L)] = e / (np.percentile(e, 95) + 1e-6)


def active(sp, t):
    for L in tl:
        if L["sp"] == sp and L["t0"] - 0.02 <= t <= L["t1"] + 0.05:
            return L
    return None


def lip(sp, t):
    L = active(sp, t)
    if not L:
        return 0.0
    e = ENV[id(L)]; i = int((t - L["t0"]) * SR)
    return float(np.clip(e[i] if 0 <= i < len(e) else 0, 0, 1)) ** 0.8


def shot_at(t):
    return ([s for s in shots if s["t0"] <= t] or [shots[0]])[-1]


def spec(i, t):
    s = shot_at(t); age = lambda b: (t - b) if t >= b else -1
    st2 = tl[4]["t0"] - 0.15
    return dict(i=i, shot=s["name"], t=t, lt=t - s["t0"], shake=(0.1 * math.exp(-(t - EV["lie"]) * 8) if t >= EV["lie"] else 0), gulp=t >= EV["gulp"],
                sp=dict(sales=lip("sales", t), hero=lip("hero", t), stage=2 if t >= st2 else 1, paperT=(t - st2) / 0.45),
                ev=dict(bong1=age(EV["bong1"]), bong2=age(EV["bong2"]), lie=age(EV["lie"])))


nframes = int(TOTAL * FPS)
times = STILLS if STILLS else [i / FPS for i in range(nframes)]
idx = list(range(len(times)))
specs = [spec(i, times[i]) for i in idx if shot_at(times[i])["name"] in SHOTS3D]
print(f"Dauer {TOTAL:.1f} s, {len(times)} Bilder, davon 3D: {len(specs)}", flush=True)
REUSE = "--reuse" in sys.argv and os.path.exists(os.path.join(FRAMES, "info.json"))
if specs and not REUSE:
    sp_json = os.path.join(WORK, "specs.json"); json.dump(specs, open(sp_json, "w"))
    os.makedirs(FRAMES, exist_ok=True)
    t0 = time.time()
    subprocess.run(["node", os.path.join(HERE, "render.cjs"), sp_json, FRAMES], check=True)
    print(f"3D fertig in {time.time() - t0:.0f} s", flush=True)
if "--reuse" in sys.argv:
    args = [a for a in args if a != "--reuse"]
INFO = json.load(open(os.path.join(FRAMES, "info.json"))) if specs else {}


def to_img(path):
    a = np.array(Image.open(path).convert("RGB")); return skia.Image.fromarray(np.dstack([a, np.full(a.shape[:2], 255, np.uint8)]), colorType=skia.kRGBA_8888_ColorType)


def compose(g, i, t):
    s = shot_at(t); g.clear(C(0, 0, 0))
    if s["name"] in SHOTS3D:
        g.c.drawImage(to_img(os.path.join(FRAMES, f"{i:05d}.jpg")), 0, 0)
        inf = INFO[str(i)]; sh, hh = inf["sales"], inf["hero"]
        X.hud(g, t, [EV["bong1"], EV["bong2"], EV["lie"]])
        if s["name"] == "lot_two":
            if active("sales", t) or t - EV["lie"] < 0.9:
                X.bubble(g, sh[0] + 60, max(100, sh[1] - 190), "One previous owner.", 30, tail=(-40, 70), k=X.overshoot((t - (tl[2]["t0"] + 0.02)) / 0.3) if t < EV["lie"] + 0.6 else max(0.01, 1 - (t - EV["lie"] - 0.6) / 0.2))
            if t >= EV["lie"]:
                X.pill(g, sh[0] + 330, sh[1] - 20, "LIE", 46, fill=C(220, 44, 60, 248), k=X.overshoot((t - EV["lie"]) / 0.3))
        if s["name"] == "hero_close":
            L = active("hero", t)
            if L:
                x = hh[0] + (340 if hh[0] < 640 else -340)
                X.bubble(g, x, max(100, hh[1] - 200), L["text"], 32, tail=(-90 if hh[0] < 640 else 90, 70), k=X.overshoot((t - L["t0"] + 0.02) / 0.3))
    elif s["name"] == "explainer":
        X.explainer(g, t, B)
    else:
        X.endcard(g, t, B["end"])


g = Gfx()
if STILLS:
    for i, tt in zip(idx, times):
        compose(g, i, tt); Image.fromarray(g.to_rgb()).save(os.path.join(WORK, f"still_{tt:.2f}.png"))
    print("Einzelbilder fertig")
    sys.exit(0)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", os.path.join(WORK, "audio.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
for i, tt in zip(idx, times):
    compose(g, i, tt); ff.stdin.write(g.to_rgb().tobytes())
ff.stdin.close(); ff.wait()
print("fertig:", OUT, round(TOTAL, 1), "s")
print("Zeitplan:", [(L["sp"], round(L["t0"], 2), round(L["t1"], 2)) for L in tl])
print("Einstellungen:", [(s["name"], round(s["t0"], 2), round(s["t1"], 2)) for s in shots])
