"""Pilot (ca. 30 s): "Today, you can hear every lie." Nur Erzaehlerstimme, 3D-Szenen, Beschriftungen, Musik, Effekte. Kostenlos.
Aufruf:
  KOKORO_V1_DIR=/pfad/kokoro-multi-lang-v1_0 python3 make_pilot.py ausgabe.mp4 [stimme]     (Standard: am_eric)
  ... --reuse   3D-Bilder aus vorherigem Lauf (gleiches WORK) weiterverwenden, nur Ton/Beschriftung neu
  ... --stills 1.0,5.0   nur Einzelbilder
"""
import json, math, os, subprocess, sys, time
import numpy as np
import skia
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from gfx import C, W, H, Gfx, overshoot, ease_out, ease_inout
import audio
import explainer as X
from audio import SR

argv = [a for a in sys.argv[1:] if a != "--timeline-only"]
STILLS = None
if "--stills" in argv:
    k = argv.index("--stills"); STILLS = [float(v) for v in argv[k + 1].split(",")]; argv = argv[:k] + argv[k + 2:]
REUSE = "--reuse" in argv; argv = [a for a in argv if a != "--reuse"]
OUT = argv[0] if argv else "pilot.mp4"
VOICE = argv[1] if len(argv) > 1 else "am_eric"
audio.VOICES.update({"am_eric": 13, "am_fenrir": 14, "am_liam": 15, "am_puck": 18, "af_sarah": 9, "af_kore": 5, "af_jessica": 4})
SHIFT = float(os.environ.get("PITCH_SHIFT", "0"))   # optional: Halbtoene hoeher (jugendlicher)
FPS = 24
WORK = os.environ.get("WORK", os.path.join(HERE, "work")); os.makedirs(WORK, exist_ok=True)
FRAMES = os.path.join(WORK, "frames3d")

LINES = [  # (Text, Einstellung, Pause danach)
    ("Today, you can hear every lie.", "pip_hook", 0.20),
    ("A bell rings. Only for lies.", "demo_two", 0.20),
    ("You're buying your first car.", "walk_wide", 0.18),
    ("The salesman loves it already.", "pat_hood", 0.18),
    ("One previous owner, he says.", "ots_pitch", 0.20),
    ("A lie.", "bell_lie", 0.30),
    ("You smile. The report says four.", "pip_report", 0.18),
    ("His smile cracks.", "sales_crack", 0.18),
    ("The price falls with it.", "price_drop", 0.15),
    ("Two thousand dollars, gone in ten seconds.", "price_drop", 0.34),
    ("And you're just getting started.", "hero_end", 0.55),
    (None, "title_card", 3.4),
    ("But every lie you hear... costs you something.", "tease", 2.2),
]
TARGET_WPM = 185.0   # reine Sprechgeschwindigkeit; mit Pausen ca. 170 bis 175 (Vorbild: 173)


def synth(text, speed):
    x = audio.speak(text, VOICE, speed)
    if SHIFT:
        import librosa
        x = librosa.effects.pitch_shift(x, sr=SR, n_steps=SHIFT).astype(np.float32)
    return x


# Tempo kalibrieren (ein Probelauf bei 1.0)
words = sum(len(t.split()) for t, _, _ in LINES if t)
dur1 = sum(len(synth(t, 1.0)) / SR for t, _, _ in LINES if t)
speed = float(np.clip(TARGET_WPM / (words / dur1 * 60), 0.78, 1.15))  # Dauer ~ 1/Tempo: schneller sprechen, wenn die Stimme zu langsam ist
print(f"Stimme {VOICE}: Tempo-Faktor {speed:.2f}", flush=True)

tl, t = [], 0.45
for text, shot, pause in LINES:
    if text is None:
        tl.append(dict(text=None, shot=shot, t0=t, t1=t + pause, x=None)); t += pause; continue
    x = synth(text, speed)
    tl.append(dict(text=text, shot=shot, t0=t, t1=t + len(x) / SR, x=x))
    t += len(x) / SR + pause
TOTAL = t + 0.2
spoken = sum(l["t1"] - l["t0"] for l in tl if l["x"] is not None)
print(f"Dauer {TOTAL:.1f} s, Sprechtempo {words / spoken * 60:.0f} Woerter/Min., mit Pausen {words / (TOTAL - 0.65 - 3.4 - 2.2) * 60:.0f}", flush=True)
shots = []
for L in tl:
    shots.append(dict(name=L["shot"], t0=0.0 if not shots else L["t0"] - 0.05))
for i, s in enumerate(shots):
    s["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else TOTAL
LI = {}
for l in tl:
    LI.setdefault(l["shot"], l)  # erste Zeile je Einstellung
PD = [l for l in tl if l["shot"] == "price_drop"]
EV = dict(hear=LI["pip_hook"]["t0"] + 1.5, demo=LI["demo_two"]["t0"] + 0.8, lie=LI["bell_lie"]["t0"] + 0.02,
          price=LI["price_drop"]["t0"] + 0.9, loss=PD[-1]["t0"] + 0.15, title=LI["title_card"]["t0"], tease=LI["tease"]["t0"] + 0.35)

# ---------------------------------------------------------------- Ton
mix = audio.Mix(TOTAL)
for l in tl:
    if l["x"] is not None:
        mix.add_voice(l["x"], l["t0"], 1.0)
mix.set_music(audio.music(TOTAL, "dark", 100), 1.0)
for i, s in enumerate(shots):
    if i > 0 and s["name"] != "title_card":
        mix.add_sfx(audio.whoosh(0.32, 300, 4200, 0.34, seed=i), s["t0"] - 0.2)
mix.add_sfx(audio.bell(130, 2.6, 0.35), EV["hear"])
mix.add_sfx(audio.bell(110, 3.0, 0.6), EV["demo"]); mix.add_sfx(audio.pop(0.35), EV["demo"] + 0.15)
mix.add_sfx(audio.bell(110, 3.0, 0.7), EV["lie"]); mix.add_sfx(audio.stamp_hit(0.8), EV["lie"] + 0.1); mix.add_sfx(audio.pop(0.4), EV["lie"] + 0.1)
mix.add_sfx(audio.coin_down(0.35), EV["price"] + 0.1); mix.add_sfx(audio.pop(0.35), EV["price"])
w0 = LI["walk_wide"]["t0"]
for k in range(5):
    mix.add_sfx(audio.step(0.3, seed=k + 1), w0 + 0.25 + k * 0.46)
mix.add_sfx(audio.riser(1.2, 0.3), EV["title"] - 1.1); mix.add_sfx(audio.impact(0.7), EV["title"])
mix.add_sfx(audio.bell(98, 3.6, 0.65), EV["tease"])
final = mix.render()
import scipy.io.wavfile as wf
wf.write(os.path.join(WORK, "audio.wav"), SR, (final * 32767).astype(np.int16))


def shot_at(t):
    return ([s for s in shots if s["t0"] <= t] or [shots[0]])[-1]


def spec(i, t):
    s = shot_at(t); age = lambda b: (t - b) if t >= b else -1
    return dict(i=i, shot=s["name"], t=t, lt=t - s["t0"], ev=dict(demo=age(EV["demo"]), lie=age(EV["lie"]), price=age(EV["price"])))


nframes = int(TOTAL * FPS)
TLJ = os.path.join(WORK, "timeline.json")
now_tl = dict(total=TOTAL, nframes=nframes, shots=[(x["name"], round(x["t0"], 3)) for x in shots], ev={k: round(v, 3) for k, v in EV.items()})
if "--timeline-only" in sys.argv:
    json.dump(now_tl, open(TLJ, "w")); print("Zeitplan gespeichert"); sys.exit(0)
if REUSE:
    # Schutz: die 3D-Bilder passen nur zum Zeitplan des vollen Laufs. Andere Stimme/Tempo = neuer voller Lauf noetig.
    if not os.path.exists(TLJ):
        sys.exit("FEHLER: kein gespeicherter Zeitplan (timeline.json). Erst einen vollen Lauf machen.")
    old = json.load(open(TLJ))
    bad = old["nframes"] != nframes or any(abs(a[1] - b[1]) > 0.06 for a, b in zip(old["shots"], now_tl["shots"])) or any(abs(old["ev"][k] - now_tl["ev"][k]) > 0.06 for k in old["ev"])
    if bad:
        sys.exit("FEHLER: Der Zeitplan weicht vom gespeicherten Lauf ab (andere Stimme oder anderes Tempo). "
                 "Die 3D-Bilder passen dann nicht mehr: bitte ohne --reuse neu rendern (ca. 15 Minuten).")
else:
    json.dump(now_tl, open(TLJ, "w"))
times = STILLS if STILLS else [i / FPS for i in range(nframes)]
specs = [spec(i, times[i]) for i in range(len(times))]
print(f"{len(times)} Bilder", flush=True)
if not (REUSE and os.path.exists(os.path.join(FRAMES, "info.json"))):
    sp_json = os.path.join(WORK, "specs.json"); json.dump(specs, open(sp_json, "w")); os.makedirs(FRAMES, exist_ok=True)
    t0 = time.time(); subprocess.run(["node", os.path.join(HERE, "render.cjs"), sp_json, FRAMES, "world_pilot.html"], check=True); print(f"3D fertig in {time.time() - t0:.0f} s", flush=True)
INFO = json.load(open(os.path.join(FRAMES, "info.json")))


_vig = None


def grade_np(a):
    """Nachgrading wie beim Vorbild: tiefere Schatten (violett), kraeftigere Farben, mehr Kontrast, Vignette."""
    global _vig
    x = a.astype(np.float32) / 255.0
    l = (x * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    sh = 1.0 - np.clip((l - 0.0) / 0.6, 0, 1) ** 2 * (3 - 2 * np.clip(l / 0.6, 0, 1))
    sh = np.clip(1.0 - np.clip(l / 0.6, 0, 1), 0, 1) ** 1.6
    x = x * (1 - sh * 0.55) + (x * np.array([0.86, 0.78, 1.14], np.float32) + np.array([0.02, 0.012, 0.05], np.float32)) * (sh * 0.55)
    x = np.clip(x, 0, 1) ** 1.3
    l2 = (x * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    x = np.clip(l2 + (x - l2) * 1.28, 0, 1)
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.41
        _vig = (1.0 - 0.42 * np.clip((d - 0.35) / 0.65, 0, 1) ** 1.5)[..., None]
    x = x * _vig * 1.18
    return (np.clip(x, 0, 1) * 255).astype(np.uint8)


def to_img(path):
    a = grade_np(np.array(Image.open(path).convert("RGB"))); return skia.Image.fromarray(np.dstack([a, np.full(a.shape[:2], 255, np.uint8)]), colorType=skia.kRGBA_8888_ColorType)


def clampx(v, lo=90, hi=W - 90):
    return max(lo, min(hi, v))


def compose(g, i, t):
    s = shot_at(t); g.clear(C(0, 0, 0))
    g.c.drawImage(to_img(os.path.join(FRAMES, f"{i:05d}.jpg")), 0, 0)
    inf = INFO[str(i)]; hh, sh, tg = inf["hero"], inf["sales"], inf.get("tag")
    n = s["name"]
    if n != "title_card":
        X.hud(g, t, [EV["hear"], EV["demo"], EV["lie"], EV["tease"]])
    if n == "pip_hook":
        a = t - EV["hear"]
        for k in range(3):
            aa = a - k * 0.22
            if 0 <= aa < 1.4:
                r = 110 + aa * 300; al = int(230 * (1 - aa / 1.4) ** 1.4)
                g.circle(hh[0], hh[1], r, stroke=C(255, 215, 110, int(al * 0.4)), width=14, blur=9); g.circle(hh[0], hh[1], r, stroke=C(255, 220, 130, al), width=3.5)
        if a > 0.15:
            X.pill(g, 640, 640, "YOU HEAR EVERY LIE", 26, k=overshoot((a - 0.15) / 0.3))
    if n == "demo_two":
        bx = clampx(sh[0] - 250, 260); X.bubble(g, bx, max(120, sh[1] - 170), "Great to see you!", 30, tail=(150, 60), k=overshoot((t - (shot_at(t)["t0"] + 0.25)) / 0.3))
        if tg and t >= EV["demo"]:
            X.pill(g, clampx(tg[0] + 190, 150), max(70, tg[1] + 10), "LIE", 38, fill=C(220, 44, 60, 248), k=overshoot((t - EV["demo"] - 0.1) / 0.3))
    if n == "ots_pitch":
        X.bubble(g, clampx(sh[0] + 260, 260, W - 260), max(110, sh[1] - 175), "One previous owner.", 32, tail=(-160, 60), k=overshoot((t - s["t0"] - 0.2) / 0.3))
    if n == "bell_lie" and tg and t >= EV["lie"]:
        X.pill(g, clampx(tg[0] + 230, 150), max(70, tg[1] + 20), "LIE", 52, fill=C(220, 44, 60, 248), k=overshoot((t - EV["lie"] - 0.1) / 0.3))
    if n == "price_drop" and t >= EV["loss"]:
        g.text("-$2,000", 640, 130, 108, fill=C(255, 90, 90), stroke=C(255, 255, 255), stroke_w=12, rot=-5, scale=max(0.01, overshoot((t - EV["loss"]) / 0.25)), shadow=(5, 8, C(0, 0, 0, 110), 6))
    if n == "title_card":
        lt = t - EV["title"]
        g.text("WHAT IF YOU COULD", 640, 150, 66, fill=C(255, 255, 255), stroke=C(52, 24, 90), stroke_w=11, shadow=(0, 8, C(0, 0, 0, 110), 6), scale=max(0.01, overshoot((lt - 0.1) / 0.4)))
        g.text("HEAR EVERY LIE?", 640, 262, 116, fill=C(255, 224, 40), stroke=C(52, 24, 90), stroke_w=20, shadow=(0, 12, C(0, 0, 0, 130), 8), scale=max(0.01, overshoot((lt - 0.3) / 0.5)))
        X.pill(g, 640, 345, "PART 1", 26, k=overshoot((lt - 0.9) / 0.3))
    if t > TOTAL - 1.0:
        g.rect(0, 0, W, H, fill=C(0, 0, 0, int(255 * min(1, (t - (TOTAL - 1.0)) / 0.9))))


g = Gfx()
if STILLS:
    for i, tt in enumerate(times):
        fi = int(round(tt * FPS)) if REUSE else i
        compose(g, fi, tt); Image.fromarray(g.to_rgb()).save(os.path.join(WORK, f"still_{tt:.2f}.png"))
    print("Einzelbilder fertig"); sys.exit(0)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", os.path.join(WORK, "audio.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
for i, tt in enumerate(times):
    compose(g, i, tt); ff.stdin.write(g.to_rgb().tobytes())
ff.stdin.close(); ff.wait()
print("fertig:", OUT, round(TOTAL, 1), "s")
print("Zeitplan:", [(l["text"] or "[Titel]", round(l["t0"], 2), round(l["t1"], 2)) for l in tl])
