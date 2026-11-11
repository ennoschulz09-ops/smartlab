"""Hoerprobe: gleicher Text in mehreren kostenlosen Stimmen. Aufruf: KOKORO_V1_DIR=... python3 voices_sampler.py out.wav"""
import sys
import numpy as np
import scipy.io.wavfile as wf
import audio
from audio import SR

CAND = ["am_michael", "am_fenrir", "am_puck", "am_liam", "am_eric", "am_onyx", "bm_daniel", "bm_george", "af_heart", "af_nova"]
TEXT = "A bell rings. Low. Deep. Like a church bell underwater. One previous owner, says the salesman, patting the hood."
parts = []
for i, v in enumerate(CAND, 1):
    parts += [audio.speak(f"Voice {i}.", "af_sky", 1.0), audio.silence(0.35), audio.speak(TEXT, v, 1.12), audio.silence(1.1)]
x = np.concatenate(parts)
x = x / np.max(np.abs(x)) * 0.9
wf.write(sys.argv[1] if len(sys.argv) > 1 else "stimmen.wav", SR, (x * 32767).astype(np.int16))
print("\n".join(f"Stimme {i}: {v}" for i, v in enumerate(CAND, 1)))
