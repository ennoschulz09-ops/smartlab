"""Proof of Concept: 15-Sekunden-Szene aus Skript 01, komplett kostenlos erzeugt.
Aufruf:  KOKORO_DIR=/pfad/kokoro-en-v0_19 python3 poc_video.py ausgabe.mp4
"""
import math, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw
import wi_draw as D
from wi_draw import S, W, H, Canvas
import wi_tts

OUT = sys.argv[1] if len(sys.argv) > 1 else "poc.mp4"
FPS, SR = 24, 24000

# (Szene, Text, Pause danach)
LINES = [
    ("bell", "A bell rings.", 0.35),
    ("bell", "Low. Deep.", 0.3),
    ("bell", "Like a church bell underwater.", 0.6),
    ("lot", "\"One previous owner,\" says the salesman, patting the hood.", 0.7),
    ("pip", "You smile.", 0.35),
    ("pip", "Funny. The report says four.", 0.8),
]


def bell_sound(f0=110.0, dur=3.2, gain=1.0):
    t = np.arange(int(SR * dur)) / SR
    parts = [(1.0, 1.0, 1.1), (2.0, 0.6, 1.7), (2.76, 0.5, 2.1), (5.4, 0.25, 3.4), (8.9, 0.12, 5.0)]
    y = sum(a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-t * dec) for m, a, dec in parts)
    y *= np.minimum(1, t / 0.006)
    return (y / np.abs(y).max() * gain).astype(np.float32)


# --- Stimme erzeugen und Zeitplan berechnen --------------------------------
timeline, audio, cur = [], [np.zeros(int(SR * 0.4), dtype=np.float32)], 0.4
for scene, text, pause in LINES:
    s, sr = wi_tts.synthesize(text, sid=6, speed=0.95)
    assert sr == SR
    timeline.append(dict(scene=scene, text=text, t0=cur, t1=cur + len(s) / SR))
    audio += [s, np.zeros(int(SR * pause), dtype=np.float32)]
    cur += len(s) / SR + pause
TOTAL = cur + 0.5
voice = np.concatenate(audio)
mix = np.zeros(int(SR * TOTAL), dtype=np.float32)
mix[: len(voice)] += voice

# Glocken-Schläge (Zeit, Grundton, Lautstärke, Ringfarbe)
BONGS = [
    (timeline[0]["t0"] + 0.15, 130.0, 0.5, (255, 210, 80)),
    (timeline[2]["t0"] + 0.0, 82.0, 0.45, (120, 180, 255)),
    (timeline[3]["t0"] + 1.85, 110.0, 0.55, (255, 70, 70)),
    (timeline[5]["t0"] + 0.9, 110.0, 0.0, (255, 70, 70)),  # stiller Wiederhol-Effekt (nur Bild)
]
for t, f0, g, _ in BONGS:
    if g > 0:
        b = bell_sound(f0, gain=g)
        i = int(t * SR)
        mix[i : i + len(b)] += b[: len(mix) - i]
mix = np.clip(mix * 0.9, -1, 1)
with wave.open("audio.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

# --- Hintergründe ------------------------------------------------------------
BG_BELL = D.gradient((8, 20, 50), (30, 75, 140))
BG_LOT = D.gradient((120, 195, 255), (215, 240, 255))
d = ImageDraw.Draw(BG_LOT)
d.rectangle([0, 500 * S, W * S, H * S], fill=(74, 79, 92, 255))
d.rectangle([0, 500 * S, W * S, 508 * S], fill=(110, 116, 130, 255))
for x in range(0, W, 120):
    d.rectangle([x * S, 640 * S, (x + 60) * S, 648 * S], fill=(230, 230, 235, 255))
for i in range(11):  # Wimpelkette
    x = 40 + i * 118
    d.polygon([(x * S, 70 * S), ((x + 40) * S, 70 * S), ((x + 20) * S, 118 * S)], fill=[(225, 60, 60, 255), (255, 210, 60, 255), (60, 170, 120, 255)][i % 3])
d.line([(0, 70 * S), (W * S, 70 * S)], fill=(60, 60, 70, 255), width=3 * S)


def scene_bell(c, t, lt):
    for i in range(14):  # aufsteigende Blasen
        bx = (i * 97 + 40) % W
        by = H - ((t * 40 + i * 83) % (H + 60))
        c.ell(bx, by, 6 + (i % 3) * 3, 6 + (i % 3) * 3, outline=(160, 200, 255, 110), w=2)
    ang = 17 * math.sin(lt * 5.5) * math.exp(-lt * 0.55)
    c.paste(D.bell_layer(260, ang), 640 - 130, 150)


def scene_lot(c, t, lt, dur):
    D.car(c, 560, 330, 1.35, flip=True)  # Motorhaube zeigt nach links zum Verkäufer
    pat = abs(math.sin(lt * 7)) * 14
    D.salesman(c, 420, 300, 1.25, hand=(590, 470 - pat), grin=True)
    c.rect(150, 140, 520, 215, fill=D.WHITE, r=22, outline=D.BLACK, w=4)
    c.poly([(380, 213), (420, 213), (418, 245)], fill=D.WHITE)
    c.text((335, 178), "One previous owner.", 34, fill=D.BLACK)
    if lt > 1.85:  # Lüge erkannt
        k = min(1, (lt - 1.85) / 0.15)
        c.rect(150, 140, 520, 215, outline=D.RED, r=22, w=8)
        c.text((860, 170), "LIE", 120 * (0.8 + 0.2 * k), fill=D.RED, stroke=7, stroke_fill=D.WHITE)


def scene_pip(c, t, lt, idx):
    D.car(c, 800, 400, 1.0, flip=True)
    sweat = 0.0 if idx == 4 else min(1, (lt) / 1.2)
    D.salesman(c, 1010, 330, 1.05, sweat=sweat, grin=(idx == 4))
    if idx == 4:
        D.pip(c, 330, 300, 1.55, brow=(0, 0), look=(0.8, 0), mouth="smile")
    else:
        D.pip(c, 330, 300, 1.55, brow=(0.6, -0.5), look=(0.8, 0), mouth="smirk", arm=(540, 430))
        c.rect(520, 345, 650, 470, fill=D.WHITE, r=8, outline=D.BLACK, w=3)
        c.text((585, 385), "REPORT", 20, fill=D.BLACK)
        c.text((585, 430), "4 OWNERS", 19, fill=D.RED)


nframes = int(TOTAL * FPS)
ff = subprocess.Popen(
    ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-i", "audio.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT],
    stdin=subprocess.PIPE)

for fi in range(nframes):
    t = fi / FPS
    cur_i = max([i for i, L in enumerate(timeline) if L["t0"] - 0.15 <= t] or [0])
    L = timeline[cur_i]
    scene_start = min(x["t0"] for x in timeline if x["scene"] == L["scene"])
    lt = t - scene_start
    c = Canvas({"bell": BG_BELL, "lot": BG_LOT, "pip": BG_LOT}[L["scene"]])
    if L["scene"] == "bell":
        scene_bell(c, t, lt)
    elif L["scene"] == "lot":
        scene_lot(c, t, lt, L["t1"] - L["t0"])
    else:
        scene_pip(c, t, t - L["t0"], cur_i)
    for bt, _, g, col in BONGS:  # Schallwellen
        if 0 <= t - bt < 1.6:
            cxr, cyr = (640, 260) if L["scene"] == "bell" else ((420, 300) if L["scene"] == "lot" else (1010, 330))
            c.overlay(D.rings(cxr, cyr, t - bt, col))
    if t >= L["t0"] - 0.05 and t <= L["t1"] + 0.25:  # Untertitel
        c.wrapped((W / 2, 640), L["text"], 52, 1100, fill=D.WHITE, stroke=7)
    zoom = 1.0 + 0.045 * min(1, lt / 4.0)
    ff.stdin.write(D.final_frame(c, zoom).tobytes())
ff.stdin.close(); ff.wait()
print("fertig:", OUT, round(TOTAL, 1), "s,", nframes, "Frames")
