"""30-Sekunden-Anfang (Folge 1), Sprite-Puppen aus der Drehansicht in der 3D-Szene (Hintergrund aus three.js).
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
import puppets as PU
from PIL import ImageFilter
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
CUTS = [("follow_walk", 0.0), ("two_shot", B["n2"][0] - 0.05), ("sales_mcu", B["s1"][0] - 0.2), ("pip_react", BONGS[0]["t"] - 0.03),
        ("two_shot", B["p2"][0] - 0.05), ("ots_sales", B["s2"][0] - 0.05), ("pip_slow", B["n3"][0] - 0.05), ("paper_pull", B["p3"][0] - 0.1),
        ("sales_typo", B["s3"][0] - 0.05), ("two_shot2", B["p4"][0] - 0.05), ("sales_truth", B["s5"][0] - 0.05), ("pip_listen", B["s5"][0] + 1.1),
        ("deal", B["p5"][0] - 0.15), ("wide_title", B["n5"][0] - 0.05), ("pip_teaser", B["n6"][0] - 0.05)]
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
def tinnitus(dur=2.0, gain=0.07):
    tt = np.arange(int(SR * dur)) / SR; y = (np.sin(2 * np.pi * 3900 * tt) + 0.6 * np.sin(2 * np.pi * 4700 * tt)) * np.exp(-tt * 1.4)
    return (y * gain * np.minimum(1, tt / 0.02)).astype(np.float32)
mix.add_sfx(tinnitus(2.4, 0.07), BONGS[0]["t"] + 0.1); mix.add_sfx(tinnitus(3.0, 0.08), BONGS[-1]["t"] + 0.1)
mix.add_sfx(audio.stamp_hit(0.6), B["s1"][0] + 0.85)
mix.add_sfx(audio.pop(0.35), B["p3"][0] - 0.05); mix.add_sfx(audio.whoosh(0.2, 1500, 6000, 0.25, seed=21), B["p3"][0] - 0.15)
mix.add_sfx(audio.stamp_hit(0.7), B["p5"][0] + 0.25); mix.add_sfx(audio.coin_down(0.5) if hasattr(audio, "coin_down") else audio.pop(0.4), B["p5"][0] + 0.45)
for k in range(6):
    mix.add_sfx(audio.step(0.28, seed=k + 1), 0.2 + k * 0.52)
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


# ---------------------------------------------------------------- Inszenierung (Welt-Meter, Boden z = 1.9)
FIG_H = 3.3; GZ = 1.9
def sm(x): x = min(1.0, max(0.0, x)); return x * x * x * (x * (x * 6 - 15) + 10)
def U(t, a, b): return sm((t - a) / max(1e-6, b - a))
def EB(p, k=1.7): p = min(1, max(0, p)); return 1 + (k + 1) * (p - 1) ** 3 + k * (p - 1) ** 2
def decay(a, tau): return math.exp(-a / tau) if a >= 0 else 0.0
BT = [b["t"] for b in BONGS]; BW = [b["who"] for b in BONGS]


def hit(t, t0, who):
    """Rueckstoss-Antwort der Figur auf einen Glockenschlag: (Versatz, Neigung, Stauchung, Zittern)"""
    a = t - t0
    if a < 0: return 0, 0, 0, 0
    r = min(1.0, a / 0.07) * decay(max(0, a - 0.07), 0.55 if who == "pip" else 0.4)
    return r, r, r, math.sin(a * 58) * decay(a, 0.45)


def actors(t):
    P = dict(x=0, z=GZ, psi=90, hop=0, sx=1, sy=1, tilt=0, dx=0); S = dict(x=0, z=GZ, psi=180, hop=0, sx=1, sy=1, tilt=0, dx=0)
    # ---- Pip
    x_walk = max(5.6, 13.0 - 2.3 * t); walking = x_walk > 5.62
    px = x_walk; stop = U(t, 3.15, 3.35)
    px += -1.0 * U(t, B["s1"][0] + 0.2, B["s1"][0] + 1.0) + 0.0
    px += -0.5 * U(t, B["p3"][0], B["p3"][0] + 0.4) - 0.5 * U(t, B["p4"][0], B["p4"][0] + 0.35) - 0.7 * U(t, B["p5"][0] - 0.1, B["p5"][0] + 0.3)
    hp = hs = 0
    for (t0, who) in zip(BT, BW):
        h = hit(t, t0, "pip" if who == "pip" else "sales"); kk = 1.0 if (who == "pip" or t0 == BT[0]) else 0.6
        px += 0.55 * kk * h[0]; P["tilt"] += 0.30 * kk * h[1]; P["sy"] -= 0.11 * kk * h[2]; P["sx"] += 0.07 * kk * h[2]; P["dx"] += 0.05 * kk * h[3] * 1.0
    if walking:
        ph = px * 2.6; P["hop"] += abs(math.sin(ph)) * 0.14; P["tilt"] += 0.035 * math.sin(ph); P["sy"] += 0.01 * math.sin(ph * 2)
    if 3.0 < t < 3.9:   # Bremsen: federn
        a = t - 3.2; P["sy"] -= 0.09 * math.exp(-a * 3) * (1 if a > 0 else 0) * math.cos(a * 14); P["tilt"] += 0.05 * math.exp(-max(a, 0) * 2.5) * (1 if a > 0 else 0)
    # Freude bei "Today, that changes": zwei kleine Huepfer
    if B["n2"][0] + 0.35 < t < B["n2"][0] + 1.3:
        a = t - (B["n2"][0] + 0.35); P["hop"] += 0.25 * abs(math.sin(a * 6.5)) * (1 - U(a, 0.5, 0.95))
    # Reaktionen mit Sprechen
    lp = lip("P", t); P["hop"] += 0.05 * lp; P["sy"] += 0.012 * lp
    if B["p3"][0] - 0.2 < t < B["p3"][0] + 0.5:
        a = t - (B["p3"][0] - 0.2); P["tilt"] += -0.1 * math.sin(min(1, a / 0.7) * math.pi)      # beugt sich vor
    # Blickrichtung: laeuft nach links, dreht sich fuer die Kamera ein Stueck heraus, schaut zum Verkaeufer
    psi = 90.0
    psi -= 38 * U(t, B["n2"][0] + 0.1, B["n2"][0] + 0.7)               # zur Kamera
    psi += 38 * U(t, B["s1"][0] - 0.1, B["s1"][0] + 0.3)
    psi -= 25 * U(t, B["p2"][0], B["p2"][0] + 0.4) - 25 * U(t, B["s2"][0], B["s2"][0] + 0.4)
    psi -= 45 * U(t, B["n5"][0], B["n5"][0] + 0.6) if t > B["p5"][0] + 0.6 else 0
    P["psi"] = psi; P["x"] = px
    # ---- Verkaeufer
    sx0 = 1.6; sxp = sx0 + 0.3 * U(t, B["s1"][0] - 0.1, B["s1"][0] + 0.5) - 0.4 * U(t, B["p4"][0] - 0.1, B["p4"][0] + 0.4) + 0.5 * U(t, B["p5"][0] - 0.1, B["p5"][0] + 0.3)
    polish = 1 - U(t, B["s1"][0] - 0.5, B["s1"][0] - 0.05)
    S["psi"] = 180.0; S["dx"] += 0.14 * math.sin(t * 8.0) * polish; S["tilt"] += 0.06 * math.sin(t * 8.0 + 0.5) * polish; S["hop"] += 0.03 * abs(math.sin(t * 8)) * polish
    sp0 = B["s1"][0] - 0.4; spin = EB(U(t, sp0, sp0 + 0.5), 1.5)
    face_pip = -78.0   # nach rechts (zu Pip)
    psi_s = 180.0 + (360.0 + face_pip - 180.0) * spin if t >= sp0 else 180.0       # 180 -> 282 (= -78): dreht ueber die Kamera-Seite ein
    S["psi"] = psi_s if t < sp0 + 0.55 else face_pip
    if sp0 < t < sp0 + 0.7: S["hop"] += 0.28 * math.sin(U(t, sp0, sp0 + 0.55) * math.pi); S["sy"] -= 0.12 * (math.exp(-(t - sp0 - 0.55) * 8) if t > sp0 + 0.55 else 0)
    lsl = lip("S", t); S["hop"] += 0.07 * lsl; S["sy"] += 0.018 * lsl; S["tilt"] += -0.02 * lsl * math.sin(t * 17)
    for (t0, who) in zip(BT, BW):
        if who == "sales":   # nach dem Schlag bleibt er einen Moment starr, dann zuckt er
            a = t - t0
            if 0 <= a < 0.9: S["dx"] += 0.05 * math.sin(a * 45) * decay(a, 0.35); S["sy"] -= 0.03 * decay(a, 0.3)
    if B["s2"][0] < t < B["n3"][0]: S["dx"] += 0.06 * math.sin(t * 38); S["tilt"] += 0.05 * math.sin(t * 34); S["hop"] += 0.06 * abs(math.sin(t * 17))       # nervoses Lachen
    if B["s3"][0] - 0.1 < t < B["p4"][0] + 0.3: S["psi"] = -78 + (-70 - -78 + 0) * U(t, B["s3"][0] - 0.1, B["s3"][0] + 0.25) * 0 - 60 * U(t, B["s3"][0], B["s3"][0] + 0.3) * (1 - U(t, B["p4"][0], B["p4"][0] + 0.3))       # Blick weg
    dbl = U(t, B["s4"][0], B["s4"][0] + 0.3) * (1 - U(t, B["s5"][0] - 0.1, B["s5"][0] + 0.15)); S["sy"] -= 0.17 * dbl; S["tilt"] += -0.1 * dbl
    if B["s5"][0] < t < B["p5"][0] - 0.2: S["hop"] += 0.18 * abs(math.sin((t - B["s5"][0]) * 5.5)); S["dx"] += 0.04 * math.sin(t * 30)
    S["x"] = sxp
    # ---- Abschluss: Handschlag-Ersatz, beide hopsen zusammen
    if B["p5"][0] + 0.1 < t < B["p5"][0] + 1.1:
        a = t - (B["p5"][0] + 0.1); hh = 0.3 * abs(math.sin(a * 7)) * (1 - U(a, 0.5, 1.0)); P["hop"] += hh; S["hop"] += hh
        P["psi"] = 90; S["psi"] = -90
    return P, S


WALK = [dict(x0=-14, v=1.1, z=-4.4, tint=dict(hoodie=(0.62, 0.78, 1.0), pants=None), h=3.0), dict(x0=17, v=-0.9, z=-5.3, tint=dict(hoodie=(1.0, 0.62, 0.74), pants=None), h=3.0),
        dict(x0=-2, v=1.3, z=-6.0, tint=dict(hoodie=(0.7, 1.0, 0.76), pants=None), h=3.0)]
SETS = dict(pip=PU.tinted(None), sales=PU.tinted(dict(hoodie=(1.0, 0.72, 0.2), pants=(40, 24, 10))), walk=[PU.tinted(w["tint"]) for w in WALK])


def walker(w, t):
    L = 52.0; x = ((w["x0"] + 26 + w["v"] * t) % L + L) % L - 26; ph = x * 2.2
    return dict(x=x, z=w["z"], psi=90 if w["v"] > 0 else -90, hop=abs(math.sin(ph)) * 0.10, sx=1, sy=1, tilt=0.03 * math.sin(ph), dx=0)


# ---------------------------------------------------------------- Kamera
def shot_cam(name, t, lt, P, S):
    def mk(lx, ly, dist, h, lat, fov=36.0): return dict(look=[lx, ly, GZ], pos=[lx + lat, h, GZ + dist], fov=fov)
    mid = (P["x"] + S["x"]) / 2
    if name == "follow_walk": c = mk(P["x"] - 1.0, 1.75, 9.4, 2.0, 2.4 - 0.4 * lt)
    elif name == "two_shot": c = mk(mid, 1.7, 10.6 - 0.35 * lt, 2.0, 0.6)
    elif name == "two_shot2": c = mk(mid, 1.7, 9.6 - 0.35 * lt, 1.9, -0.8)
    elif name == "sales_mcu": c = mk(S["x"], 1.8, 6.6 - 0.25 * lt, 1.2, -0.9)
    elif name == "pip_react": c = mk(P["x"], 1.8, 6.4 - 0.2 * lt, 1.6, 0.9)
    elif name == "ots_sales": c = mk(S["x"] + 0.3, 1.8, 7.4 - 0.3 * lt, 1.9, 2.3)
    elif name == "pip_slow": c = mk(P["x"], 1.9, 8.0 - 1.6 * min(1, lt / 1.5), 1.7, 0.4)
    elif name == "paper_pull": c = mk(P["x"] - 0.6, 1.8, 7.6, 1.8, 0.8 - 0.8 * lt)
    elif name == "sales_typo": c = mk(S["x"], 1.8, 6.4 - 0.3 * lt, 1.4, -0.6)
    elif name == "sales_truth": c = mk(S["x"], 1.7, 6.2 - 0.3 * lt, 1.3, -0.4)
    elif name == "pip_listen": c = mk(P["x"], 1.9, 6.6 - 0.5 * lt, 1.7, 0.7)
    elif name == "deal": c = mk(mid, 1.8, 8.4 - 0.5 * lt, 1.7, 0.0)
    elif name == "wide_title": c = mk(mid + 1.0, 2.4, 13.5 + 1.2 * lt, 2.6, 0.5, 36.0)
    else: c = mk(P["x"], 2.0, 6.8 - 0.6 * lt, 1.6, 0.7)    # pip_teaser
    # Kamerastoss bei jedem Schlag: Wackeln + kurzes Hineinzoomen
    for t0 in BT:
        a = t - t0
        if 0 <= a < 0.7:
            k = math.exp(-a * 5.5); c["pos"][0] += 0.16 * k * math.sin(a * 62); c["pos"][1] += 0.12 * k * math.cos(a * 71); c["fov"] -= 4.0 * k
    return c


def cut_at(t):
    c = [x for x in CUTS if x[1] <= t] or [CUTS[0]]; return c[-1]


nframes = int(TOTAL * FPS)
specs = []
for i in range(nframes):
    tt = i / FPS; nm, c0 = cut_at(tt); P, S = actors(tt); W_ = [walker(w, tt) for w in WALK]
    cam = shot_cam(nm, tt, tt - c0, P, S)
    pts = [[P["x"], P["z"], FIG_H], [S["x"], S["z"], FIG_H]] + [[w["x"], w["z"], WALK[k]["h"]] for k, w in enumerate(W_)]
    specs.append(dict(i=i, t=tt, cam=cam, pts=pts, cut=nm))
TLJ = os.path.join(WORK, "timeline.json")
json.dump(dict(frames=specs, meta=dict(B=B, bongs=BONGS)), open(os.path.join(WORK, "specs.json"), "w")); os.makedirs(FRAMES, exist_ok=True)
if not REUSE:
    t0 = time.time(); env = dict(os.environ, RENDER_W=str(RW), RENDER_H=str(RH))
    subprocess.run(["node", os.path.join(HERE, "render.cjs"), os.path.join(WORK, "specs.json"), FRAMES, "world_bg2.html"], check=True, env=env)
    print(f"Hintergrund fertig in {time.time() - t0:.0f} s ({nframes} Bilder)", flush=True)
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


def to_skia(im):
    a = np.array(im.convert("RGB")); return skia.Image.fromarray(np.dstack([a, np.full(a.shape[:2], 255, np.uint8)]), colorType=skia.kRGBA_8888_ColorType)


def clampx(v, lo=120, hi=W - 120):
    return max(lo, min(hi, v))


def stage(i, t):
    """Bild i: Hintergrund + Puppen. Gibt PIL-Bild und Kopfpositionen zurueck."""
    sp = specs[i]; inf = INFO[str(i)]["pts"]; cam = sp["cam"]
    bg = Image.open(os.path.join(FRAMES, f"{i:05d}.jpg")).convert("RGB")
    if bg.size != (W, H): bg = bg.resize((W, H), Image.BICUBIC)
    canvas = Image.fromarray(grade_np(np.array(bg))).convert("RGBA")
    P, S = actors(t); Wk = [walker(w, t) for w in WALK]
    items = [("walk", k, w) for k, w in enumerate(Wk)] + ([("sales", 0, S)] if t < B["n6"][0] - 0.1 else []) + [("pip", 0, P)]
    idx = {"pip": 0, "sales": 1}; heads = {}
    order = sorted(items, key=lambda it: -inf[(2 + it[1]) if it[0] == "walk" else idx[it[0]]]["d"])
    for kind, k, st in order:
        pi = (2 + k) if kind == "walk" else idx[kind]; pr = inf[pi]
        foot = pr["foot"]; ph = abs(pr["head"][1] - pr["foot"][1]); fig = WALK[k]["h"] if kind == "walk" else FIG_H; ppx = ph / fig
        cxz = (cam["pos"][0] - st["x"], cam["pos"][2] - st["z"]); n = math.hypot(*cxz); cxz = (cxz[0] / n, cxz[1] / n)
        r = math.radians(st["psi"]); fv = (-math.sin(r), math.cos(r))
        sset = SETS["walk"][k] if kind == "walk" else SETS[kind]
        res = PU.draw(canvas, sset, foot, ppx, fv, cxz, hop=st["hop"], sx=st["sx"], sy=st["sy"], tilt=st["tilt"], dx=st["dx"] * ppx, fig_h=fig, shadow=0.5 if kind != "walk" else 0.3)
        if kind != "walk": heads[kind] = res
    heads.setdefault("sales", dict(head=(-999, -999), foot=(-999, -999), ph=1))
    return canvas, heads, P, S


def paper(g, x, y, k, rot):
    g.c.save(); g.c.translate(x, y); g.c.rotate(rot); g.c.scale(k, k)
    g.rrect(-70, -92, 70, 92, 8, fill=C(250, 250, 246), stroke=C(60, 70, 100), width=3)
    g.text("VEHICLE", 0, -62, 22, fill=C(60, 70, 100)); g.text("REPORT", 0, -38, 22, fill=C(60, 70, 100))
    for j in range(3): g.rrect(-48, -8 + j * 18, 40 + 22 * (j % 2), 2 + j * 18 + 4 + 0, 3, fill=C(200, 204, 216))
    g.rrect(-52, 46, 52, 82, 6, fill=C(255, 235, 235), stroke=C(214, 40, 56), width=3); g.text("4 OWNERS", 0, 64, 20, fill=C(214, 40, 56))
    g.c.restore()


def compose(g, i, t):
    sp = specs[i]; canvas, heads, P, S = stage(i, t); g.clear(C(0, 0, 0)); g.c.drawImage(to_skia(canvas), 0, 0)
    hh, sh = heads["pip"]["head"], heads["sales"]["head"]
    ph_p, ph_s = heads["pip"]["ph"], heads["sales"]["ph"]
    in_title = TITLE[0] <= t < TITLE[1] or (B["n5"][0] <= t < TITLE[0] + 0.001)
    if not in_title:
        X.hud(g, t, BT)
    for b in BONGS:
        a = t - b["t"]
        if 0 <= a < 0.08: g.rect(0, 0, W, H, fill=C(255, 250, 235, int(150 * (1 - a / 0.08))))
        if b["who"] == "sales":
            if 0 <= a < 1.1 and 60 < sh[0] < W - 60:
                X.bell_icon(g, sh[0], max(70, sh[1] - ph_s * 0.25), 0.42 * max(0.01, overshoot(a / 0.2)) * (1 if a < 0.9 else max(0.01, 1 - (a - 0.9) / 0.2)), glow=max(0, 1 - a / 0.7), swing=16 * math.sin(a * 24) * math.exp(-a * 3.2))
                if 0.04 <= a < 1.0 and 60 < sh[0] < W - 60:
                    X.pill(g, clampx(sh[0] + 175, 150), max(60, sh[1] - ph_s * 0.55), "LIE", 38, fill=C(220, 44, 60, 248), k=overshoot((a - 0.04) / 0.25) * (1 if a < 0.8 else max(0.01, 1 - (a - 0.8) / 0.2)))
            for k in range(3):   # Wellen laufen zu Pip
                aa = a - k * 0.12
                if 0 <= aa < 0.9:
                    g.circle(sh[0], sh[1] + ph_s * 0.1, 40 + aa * 460, stroke=C(255, 215, 110, int(200 * (1 - aa / 0.9))), width=5)
        if b["who"] == "pip" and 0 <= a < 2.2:
            for side in (-1, 1):
                for k in range(3):
                    aa = a - k * 0.18
                    if 0 <= aa < 1.2:
                        g.circle(hh[0] + side * ph_p * 0.25, hh[1] + ph_p * 0.08, 60 + aa * 100, stroke=C(160, 220, 255, int(115 * (1 - aa / 1.2))), width=5)
    # Pips Reaktion nach Schlag: Sternchen/Klingeln um den Kopf
    for (t0, who) in zip(BT, BW):
        a = t - t0
        if who == "sales" and 0.03 <= a < 0.8 and (t0 == BT[0]):
            for k in range(5):
                ang = k * 1.26 + a * 6; r = ph_p * (0.17 + 0.05 * math.sin(a * 20 + k))
                g.text("*", hh[0] + math.cos(ang) * r * 1.2, hh[1] - ph_p * 0.02 + math.sin(ang) * r * 0.6, 44, fill=C(255, 236, 120), stroke=C(70, 40, 10), stroke_w=3)
    if B["p2"][0] <= t < B["s2"][0] + 0.3:   # Fragezeichen
        a = t - B["p2"][0]; g.text("?", hh[0] + ph_p * 0.18, hh[1] - ph_p * 0.14, 80, fill=C(255, 255, 255), stroke=C(52, 24, 90), stroke_w=8, scale=max(0.01, overshoot(a / 0.3)) * (1 - U(t, B["s2"][1] - 0.2, B["s2"][1] + 0.3)))
    if B["s2"][0] + 0.3 <= t < B["p5"][0] - 0.1:   # Schweiss
        a = t - (B["s2"][0] + 0.3); k = min(1, a / 0.6)
        for j in range(3):
            yy = sh[1] + ph_s * (0.04 + 0.08 * ((a * 1.2 + j * 0.34) % 1.0)); g.oval(sh[0] + (j - 1) * ph_s * 0.16 + ph_s * 0.2, yy, 7 * k, 11 * k, fill=C(140, 200, 255, 235), stroke=C(60, 110, 200), width=2)
    if B["p3"][0] - 0.05 <= t < B["s5"][0] + 0.5:   # Fahrzeugbericht
        a = t - (B["p3"][0] - 0.05); k = max(0.01, overshoot(a / 0.35)) * (1 - U(t, B["s5"][0] - 0.1, B["s5"][0] + 0.5))
        jab = U(t, B["p4"][0], B["p4"][0] + 0.2) * (1 - U(t, B["p4"][0] + 0.4, B["p4"][0] + 0.8))
        paper(g, hh[0] - ph_p * 0.32 - ph_p * 0.22 * jab, hh[1] + ph_p * 0.42, 1.25 * (ph_p / 470) * k * (1 + 0.15 * jab), -0.12 + 0.2 * math.sin(a * 5) * decay(a, 0.6))
    if B["p5"][0] + 0.2 <= t < B["n5"][0] + 0.3:   # SOLD-Stempel
        a = t - (B["p5"][0] + 0.2); k = max(0.01, overshoot(a / 0.2, 2.6))
        mid = ((hh[0] + sh[0]) / 2, (hh[1] + sh[1]) / 2 - 20); g.c.save(); g.c.translate(*mid); g.c.rotate(-0.14); g.c.scale(k, k)
        g.rrect(-150, -48, 150, 48, 10, stroke=C(220, 44, 60), width=9); g.text("SOLD!", 0, 0, 78, fill=C(220, 44, 60), stroke=C(255, 255, 255, 0), stroke_w=0); g.c.restore()
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
ff.stdin.close(); ff.wait(); print("fertig:", OUT, f"{TOTAL:.1f} s", flush=True)
