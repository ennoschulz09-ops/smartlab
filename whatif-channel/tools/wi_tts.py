"""Kostenlose, offline laufende KI-Stimme (Kokoro via sherpa-onnx).

Einmalig (ca. 320 MB, kostenlos):
  pip install "sherpa-onnx<2.0" numpy
  curl -L -o kokoro.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-en-v0_19.tar.bz2
  tar xjf kokoro.tar.bz2     # -> Ordner kokoro-en-v0_19
  export KOKORO_DIR=/pfad/zu/kokoro-en-v0_19

Stimmen (sid): 0 af, 1 af_bella, 2 af_nicole, 3 af_sarah, 4 af_sky, 5 am_adam,
               6 am_michael, 7 bf_emma, 8 bf_isabella, 9 bm_george, 10 bm_lewis
"""
import os
import numpy as np
import sherpa_onnx

_tts = None


def _load():
    global _tts
    if _tts is None:
        base = os.environ["KOKORO_DIR"].rstrip("/") + "/"
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                    model=base + "model.onnx",
                    voices=base + "voices.bin",
                    tokens=base + "tokens.txt",
                    data_dir=base + "espeak-ng-data",
                ),
                num_threads=4,
                provider="cpu",
            )
        )
        _tts = sherpa_onnx.OfflineTts(cfg)
    return _tts


def synthesize(text, sid=6, speed=0.95):
    """Gibt (samples float32 [-1,1], sample_rate) zurueck."""
    audio = _load().generate(text, sid=sid, speed=speed)
    return np.array(audio.samples, dtype=np.float32), audio.sample_rate
