"""Hoerprobe v2: jugendlichere Kandidaten mit den echten Einstiegszeilen, natuerliches Tempo, kaum kuenstliche Pausen.
Aufruf: KOKORO_V1_DIR=... python3 voices_sampler2.py out.wav"""
import sys, numpy as np, librosa
import scipy.io.wavfile as wf
import audio
from audio import SR

audio.VOICES.update({"am_eric": 13, "am_fenrir": 14, "am_liam": 15, "am_puck": 18, "af_sarah": 9, "af_jessica": 4, "af_kore": 5, "af_nova": 7})
TEXT = ["Today, you can hear every lie.", "A bell rings. Only for lies.", "You're buying your first car.", "The salesman loves it already.", "One previous owner, he says.", "A lie."]
CAND = [("am_eric", 0.0), ("am_fenrir", 0.0), ("am_liam", 0.0), ("am_puck", 0.0), ("af_sarah", 0.0), ("af_kore", 0.0), ("am_eric", 2.0), ("am_fenrir", 2.0)]
SPEED = 0.90
parts = []
for i, (v, st) in enumerate(CAND, 1):
    parts += [audio.speak(f"Voice {i}.", "af_sky", 0.95), audio.silence(0.3)]
    for ln in TEXT:
        x = audio.speak(ln, v, SPEED)
        if st:
            x = librosa.effects.pitch_shift(x, sr=SR, n_steps=st).astype(np.float32)
        parts += [x, audio.silence(0.16)]
    parts += [audio.silence(0.9)]
x = np.concatenate(parts); x = x / np.max(np.abs(x)) * 0.9
wf.write(sys.argv[1] if len(sys.argv) > 1 else "stimmen2.wav", SR, (x * 32767).astype(np.int16))
for i, (v, st) in enumerate(CAND, 1):
    print(f"Stimme {i}: {v}" + (f" (+{st:g} Halbtoene hoeher)" if st else ""))
