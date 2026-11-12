"""30-Sekunden-Anfang (Folge 1): eine durchgehende Szene, drei Stimmen, Aktionen mit Anlauf/Nachschwingen, Schnitt auf die Aktion.
  KOKORO_V1_DIR=... python3 make_story.py ausgabe.mp4            voller Lauf (1280x720, 24 fps)
  PREVIEW=1 ... python3 make_story.py vorschau.mp4               schnelle Vorschau (3D in 640x360, 12 fps)
  ... --reuse   3D-Bilder weiterverwenden (nur bei gleichem Zeitplan; sonst Abbruch)
"""
import json, math, os, subprocess, sys, time
import numpy as np
import skia
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from gfx import C, W, H, Gfx, overshoot
import audio
import explainer as X
from audio import SR

argv = [a for a in sys.argv[1:]]
REUSE = "--reuse" in argv; argv = [a for a in argv if a != "--reuse"]
OUT = argv[0] if argv else "folge1_anfang.mp4"
PREVIEW = os.environ.get("PREVIEW") == "1"
FPS = 12 if PREVIEW else 24
RW, RH = (640, 360) if PREVIEW else (1280, 720)
WORK = os.environ.get("WORK", os.path.join(HERE, "work")); os.makedirs(WORK, exist_ok=True)
FRAMES = os.path.join(WORK, "frames3d")
audio.VOICES.update({"am_eric": 13, "am_puck": 18, "bm_george": 26, "bm_fable": 25, "am_michael": 16})
VOICE = dict(N=os.environ.get("V_NARR", "am_puck"), P=os.environ.get("V_PIP", "am_eric"), S=os.environ.get("V_SALES", "bm_george"))

LINES = [  # id, Sprecher, Text, Pause danach
    ("n1", "N", "You have six hundred dollars and no car.", 0.15),
    ("n2", "N", "Today, that changes.", 0.30),
    ("s1", "S", "Great news, buddy! One owner. Never been in an accident.", 0.25),
    ("p1", "P", "Ow!", 0.10),
    ("p2", "P", "Is that... a bell?", 0.25),
    ("s2", "S", "A what? Ha! Nope. Just, uh, wind chimes.", 0.30),
    ("n3", "N", "And slowly, you understand.", 0.25),
    ("p3", "P", "The report says four owners.", 0.20),
    ("s3", "S", "Typo.", 0.20),
    ("p4", "P", "And two accidents.", 0.15),
    ("s4", "S", "Double typo.", 0.30),
    ("s5", "S", "Okay, okay. Three hundred. Final.", 0.25),
    ("p5", "P", "Sold.", 0.40),
    ("n5", "N", "So, what if you could hear every lie?", 0.15),
    ("tt", None, None, 2.4),   # Titelkarte
    ("n6", "N", "Everyone says they'd love it. Until the first bell.", 2.1),
]
SPEED = dict(P=1.08, S=1.12)
TARGET_WPM = 185.0


def synth(sp, text, speed):
    return audio.speak(text, VOICE[sp], speed)


nar = [(i, sp, tx) for i, sp, tx, _ in LINES if sp == "N"]
words = sum(len(tx.split()) for _, _, tx in nar); d1 = sum(len(synth("N", tx, 1.0)) / SR for _, _, tx in nar)
SPEED["N"] = float(np.clip(TARGET_WPM / (words / d1 * 60), 0.78, 1.15))
print(f"Erzaehler {VOICE['N']} Tempo {SPEED['N']:.2f}, Pip {VOICE['P']}, Verkaeufer {VOICE['S']}", flush=True)

tl, B, t = [], {}, 0.5
for lid, sp, tx, pause in LINES:
    if sp is None:
        B[lid] = [t, t + pause]; t += pause; continue
    x = synth(sp, tx, SPEED[sp]); t1 = t + len(x) / SR
    B[lid] = [t, t1]; tl.append(dict(id=lid, sp=sp, text=tx, t0=t, t1=t1, x=x)); t = t1 + pause
TOTAL = t
fr = lambda lid, f: B[lid][0] + (B[lid][1] - B[lid][0]) * f
BONGS = [dict(t=fr("s1", 0.52), who="sales"), dict(t=B["s1"][1] - 0.05, who="sales"), dict(t=B["s2"][1] - 0.05, who="sales"),
         dict(t=B["s3"][1] - 0.02, who="sales"), dict(t=B["s4"][1] - 0.02, who="sales"), dict(t=B["n6"][1] + 0.25, who="pip")]
CUTS = [("follow_walk", 0.0), ("two_shot", B["n2"][0] - 0.05), ("sales_mcu", B["s1"][0] - 0.15), ("pip_ears", BONGS[0]["t"] - 0.03),
        ("two_shot", B["p2"][0] - 0.05), ("ots_sales", B["s2"][0] - 0.05), ("pip_slow", B["n3"][0] - 0.05), ("paper_pull", B["p3"][0] - 0.1),
        ("sales_typo", B["s3"][0] - 0.05), ("two_shot2", B["p4"][0] - 0.05), ("sales_truth", B["s5"][0] - 0.05), ("pip_listen", B["s5"][0] + 1.1),
        ("handshake", B["p5"][0] - 0.15), ("wide_title", B["n5"][0] - 0.05), ("pip_teaser", B["n6"][0] - 0.05)]
TITLE = B["tt"]
spoken = sum(l["t1"] - l["t0"] for l in tl); wd = sum(len(l["text"].split()) for l in tl)
print(f"Dauer {TOTAL:.1f} s, {wd} Woerter, Sprechtempo {wd / spoken * 60:.0f}/Min.", flush=True)

# ---------------------------------------------------------------- Ton
mix = audio.Mix(TOTAL)
for l in tl:
    mix.add_voice(l["x"], l["t0"], 1.0 if l["sp"] == "N" else 0.95)
mix.set_music(audio.music(TOTAL, "dark", 100), 1.0)
for i, (nm, ct) in enumerate(CUTS):
    if i > 0 and nm not in ("two_shot",):
        mix.add_sfx(audio.whoosh(0.28, 300, 4200, 0.28, seed=i), ct - 0.18)
for k, b in enumerate(BONGS):
    mix.add_sfx(audio.bell(130 if b["who"] == "sales" else 98, 3.0, 0.75 if k == 0 or b["who"] == "pip" else 0.6), b["t"])
    mix.add_sfx(audio.stamp_hit(0.5), b["t"] + 0.02)
import numpy as _np
def tinnitus(dur=2.0, gain=0.07):
    tt = _np.arange(int(SR * dur)) / SR; y = (_np.sin(2 * _np.pi * 3900 * tt) + 0.6 * _np.sin(2 * _np.pi * 4700 * tt)) * _np.exp(-tt * 1.4)
    return (y * gain * _np.minimum(1, tt / 0.02)).astype(_np.float32)
mix.add_sfx(tinnitus(2.4, 0.07), BONGS[0]["t"] + 0.1); mix.add_sfx(tinnitus(3.0, 0.08), BONGS[-1]["t"] + 0.1)
mix.add_sfx(audio.stamp_hit(0.6), B["s1"][0] + 0.85)      # Klatschen
mix.add_sfx(audio.pop(0.35), B["p3"][0] - 0.05)           # Papier
mix.add_sfx(audio.whoosh(0.2, 1500, 6000, 0.25, seed=21), B["p3"][0] - 0.15)
mix.add_sfx(audio.pop(0.4), B["p5"][0] + 0.2)             # Handschlag
for k in range(7):
    mix.add_sfx(audio.step(0.28, seed=k + 1), 0.15 + k * 0.42)
mix.add_sfx(audio.riser(1.1, 0.3), TITLE[0] - 0.7); mix.add_sfx(audio.impact(0.7), TITLE[0])
final = mix.render()
import scipy.io.wavfile as wf
wf.write(os.path.join(WORK, "audio.wav"), SR, (final * 32767).astype(np.int16))

ENV = {}
for l in tl:
    if l["sp"] != "N":
        e = audio.envelope(l["x"], 0.05); ENV[l["id"]] = e / (np.percentile(e, 95) + 1e-6)


def lip(spk, t):
    for l in tl:
        if l["sp"] == spk and l["t0"] - 0.02 <= t <= l["t1"] + 0.04:
            e = ENV[l["id"]]; i = int((t - l["t0"]) * SR)
            return float(np.clip(e[i] if 0 <= i < len(e) else 0, 0, 1)) ** 0.8
    return 0.0


def cut_at(t):
    c = [x for x in CUTS if x[1] <= t] or [CUTS[0]]; return c[-1]


nframes = int(TOTAL * FPS)
specs = []
for i in range(nframes):
    tt = i / FPS; nm, c0 = cut_at(tt)
    specs.append(dict(i=i, t=tt, cut=nm, lt=tt - c0, sp=dict(hero=lip("P", tt), sales=lip("S", tt))))
meta = dict(B=B, bongs=BONGS)
TLJ = os.path.join(WORK, "timeline.json"); now = dict(total=TOTAL, nframes=nframes, cuts=[(n, round(c, 3)) for n, c in CUTS], bongs=[round(b["t"], 3) for b in BONGS], fps=FPS)
if REUSE:
    old = json.load(open(TLJ)) if os.path.exists(TLJ) else None
    if old is None or old["nframes"] != nframes or old["fps"] != FPS or any(abs(a[1] - b[1]) > 0.06 for a, b in zip(old["cuts"], now["cuts"])) or any(abs(a - b) > 0.06 for a, b in zip(old["bongs"], now["bongs"])):
        sys.exit("FEHLER: Zeitplan weicht ab (andere Stimme/Tempo/Vorschau). Bitte ohne --reuse neu rendern.")
else:
    json.dump(now, open(TLJ, "w"))
    json.dump(dict(frames=specs, meta=meta), open(os.path.join(WORK, "specs.json"), "w")); os.makedirs(FRAMES, exist_ok=True)
    t0 = time.time(); env = dict(os.environ, RENDER_W=str(RW), RENDER_H=str(RH))
    subprocess.run(["node", os.path.join(HERE, "render.cjs"), os.path.join(WORK, "specs.json"), FRAMES, "world.html"], check=True, env=env)
    print(f"3D fertig in {time.time() - t0:.0f} s ({nframes} Bilder)", flush=True)
INFO = json.load(open(os.path.join(FRAMES, "info.json")))

_vig = None


def grade_np(a):
    global _vig
    x = a.astype(np.float32) / 255.0
    l = (x * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    sh = np.clip(1.0 - np.clip(l / 0.6, 0, 1), 0, 1) ** 1.6
    x = x * (1 - sh * 0.55) + (x * np.array([0.86, 0.78, 1.14], np.float32) + np.array([0.02, 0.012, 0.05], np.float32)) * (sh * 0.55)
    x = np.clip(x, 0, 1) ** 1.3
    l2 = (x * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    x = np.clip(l2 + (x - l2) * 1.28, 0, 1)
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.41
        _vig = (1.0 - 0.42 * np.clip((d - 0.35) / 0.65, 0, 1) ** 1.5)[..., None]
    return (np.clip(x * _vig * 1.18, 0, 1) * 255).astype(np.uint8)


def to_img(path):
    im = Image.open(path).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.BICUBIC)
    a = grade_np(np.array(im)); return skia.Image.fromarray(np.dstack([a, np.full(a.shape[:2], 255, np.uint8)]), colorType=skia.kRGBA_8888_ColorType)


def clampx(v, lo=120, hi=W - 120):
    return max(lo, min(hi, v))


def compose(g, i, t):
    sp = specs[i]; g.clear(C(0, 0, 0)); g.c.drawImage(to_img(os.path.join(FRAMES, f"{i:05d}.jpg")), 0, 0)
    inf = INFO[str(i)]; hh, sh, tg = inf["hero"], inf["sales"], inf.get("tag")
    in_title = TITLE[0] <= t < TITLE[1] or (B["n5"][0] <= t < TITLE[0] + 0.001)
    if not in_title:
        X.hud(g, t, [b["t"] for b in BONGS])
    for b in BONGS:
        a = t - b["t"]
        if b["who"] == "sales" and tg and 0 <= a < 1.0 and 60 < tg[0] < W - 60 and 40 < tg[1] < H - 60:
            X.pill(g, clampx(tg[0] + 200, 150), max(70, tg[1] + 15), "LIE", 40, fill=C(220, 44, 60, 248), k=overshoot(a / 0.25) * (1 if a < 0.8 else max(0.01, 1 - (a - 0.8) / 0.2)))
        if b["who"] == "pip" and 0 <= a < 2.2:  # Klingeln in den Ohren
            for side in (-1, 1):
                for k in range(3):
                    aa = a - k * 0.18
                    if 0 <= aa < 1.2:
                        r = 70 + aa * 110; al = int(230 * (1 - aa / 1.2))
                        g.circle(hh[0] + side * 170, hh[1] + 10, r, stroke=C(160, 220, 255, int(al * 0.5)), width=5)
    if t >= TITLE[0] - 1.5 and t < TITLE[1] + 0.2 and B["n5"][0] <= t:
        lt = t - B["n5"][0]
        g.text("WHAT IF YOU COULD", 640, 150, 66, fill=C(255, 255, 255), stroke=C(52, 24, 90), stroke_w=11, shadow=(0, 8, C(0, 0, 0, 110), 6), scale=max(0.01, overshoot((lt - 0.1) / 0.4)))
        g.text("HEAR EVERY LIE?", 640, 262, 116, fill=C(255, 224, 40), stroke=C(52, 24, 90), stroke_w=20, shadow=(0, 12, C(0, 0, 0, 130), 8), scale=max(0.01, overshoot((lt - 0.4) / 0.5)))
    if t > TOTAL - 0.9:
        g.rect(0, 0, W, H, fill=C(0, 0, 0, int(255 * min(1, (t - (TOTAL - 0.9)) / 0.8))))


g = Gfx()
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", os.path.join(WORK, "audio.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium" if not PREVIEW else "veryfast",
                       "-crf", "18" if not PREVIEW else "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
for i in range(nframes):
    compose(g, i, i / FPS); ff.stdin.write(g.to_rgb().tobytes())
ff.stdin.close(); ff.wait()
print("fertig:", OUT, round(TOTAL, 1), "s")
print("Zeitplan:", {k: [round(a, 2), round(b, 2)] for k, (a, b) in B.items()})
