"""Audio-Engine (kostenlos): Stimme (Kokoro v1.0), Soundeffekte und Musik selbst erzeugt, Abmischung mit Ducking."""
import os
import numpy as np
from scipy import signal

SR = 44100
VOICES = {  # sid in kokoro-multi-lang-v1_0
    "af_heart": 3, "af_bella": 2, "af_nova": 7, "af_sky": 10, "am_adam": 11, "am_eric": 13, "am_fenrir": 14,
    "am_liam": 15, "am_michael": 16, "am_onyx": 17, "am_puck": 18, "bf_emma": 21, "bm_daniel": 24, "bm_fable": 25, "bm_george": 26,
}
_tts = None


def _load():
    global _tts
    if _tts is None:
        import sherpa_onnx
        B = os.environ["KOKORO_V1_DIR"].rstrip("/") + "/"
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=B + "model.onnx", voices=B + "voices.bin", tokens=B + "tokens.txt",
                                                           data_dir=B + "espeak-ng-data", lexicon=B + "lexicon-us-en.txt"),
            num_threads=4, provider="cpu"))
        _tts = sherpa_onnx.OfflineTts(cfg)
    return _tts


def speak(text, voice="am_michael", speed=1.12):
    a = _load().generate(text, sid=VOICES[voice], speed=speed)
    x = np.array(a.samples, dtype=np.float32)
    x = signal.resample_poly(x, SR // 300, 24000 // 300)  # 24k -> 44.1k
    return voice_fx(x.astype(np.float32))


def voice_fx(x):
    """Leichte Aufbereitung: Tiefen weg, Praesenz an, sanfte Kompression."""
    sos = signal.butter(2, 85, "highpass", fs=SR, output="sos")
    x = signal.sosfilt(sos, x)
    pres = signal.butter(2, [2500, 5200], "bandpass", fs=SR, output="sos")
    x = x + 0.35 * signal.sosfilt(pres, x)
    # Kompressor (einfach, Huellkurven-basiert)
    env = np.abs(x)
    env = signal.sosfilt(signal.butter(1, 18, "lowpass", fs=SR, output="sos"), env)
    gain = np.where(env > 0.12, (0.12 + (env - 0.12) * 0.45) / np.maximum(env, 1e-6), 1.0)
    x = x * gain
    pk = np.max(np.abs(x)) + 1e-9
    return (x / pk * 0.89).astype(np.float32)


def silence(sec):
    return np.zeros(int(SR * sec), dtype=np.float32)


# ---------------------------------------------------------------- Effekte
def reverb(x, rt60=1.4, wet=0.25, seed=5):
    rnd = np.random.RandomState(seed)
    n = int(SR * rt60)
    t = np.arange(n) / SR
    ir = rnd.randn(n) * np.exp(-6.9 * t / rt60)
    ir = signal.sosfilt(signal.butter(2, 6500, "lowpass", fs=SR, output="sos"), ir)
    ir /= np.sqrt(np.sum(ir ** 2))
    y = signal.fftconvolve(x, ir)[: len(x) + n // 2]
    out = np.zeros(len(y), dtype=np.float32)
    out[: len(x)] += x * (1 - wet)
    return (out + y * wet * 1.6).astype(np.float32)


def bell(f0=110.0, dur=3.4, gain=1.0):
    t = np.arange(int(SR * dur)) / SR
    parts = [(1.0, 1.0, 0.9), (2.0, 0.6, 1.4), (2.76, 0.55, 1.8), (4.07, 0.3, 2.4), (5.4, 0.25, 3.0), (8.9, 0.1, 4.8)]
    y = sum(a * np.sin(2 * np.pi * f0 * m * t + 0.3 * m) * np.exp(-t * d) for m, a, d in parts)
    y *= np.minimum(1, t / 0.004)
    y = y / np.abs(y).max()
    return (reverb(y.astype(np.float32), 2.2, 0.35) * gain).astype(np.float32)


def _noise(dur, seed=1):
    return np.random.RandomState(seed).randn(int(SR * dur)).astype(np.float32)


def whoosh(dur=0.45, f0=250, f1=3800, gain=0.5, seed=2):
    n = _noise(dur, seed)
    out = np.zeros_like(n)
    blk = 512
    zi = None
    for i in range(0, len(n), blk):
        k = i / len(n)
        fc = f0 * (f1 / f0) ** k
        sos = signal.butter(2, [fc * 0.7, min(fc * 1.4, SR / 2 - 100)], "bandpass", fs=SR, output="sos")
        seg, _ = signal.sosfilt(sos, n[i:i + blk], zi=signal.sosfilt_zi(sos) * 0)
        out[i:i + blk] = seg
    t = np.linspace(0, 1, len(out))
    env = np.sin(np.pi * t) ** 1.6
    return (out / (np.abs(out).max() + 1e-9) * env * gain).astype(np.float32)


def pop(gain=0.5, f0=700, f1=180, dur=0.12):
    t = np.arange(int(SR * dur)) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 40)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 32) * gain).astype(np.float32)


def impact(gain=0.9, dur=1.1):
    t = np.arange(int(SR * dur)) / SR
    f = 48 + 90 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5)
    nz = signal.sosfilt(signal.butter(2, 1800, "lowpass", fs=SR, output="sos"), _noise(dur, 9)) * np.exp(-t * 20) * 0.5
    y = boom + nz
    return (reverb(y.astype(np.float32), 0.8, 0.2) * gain / np.abs(y).max()).astype(np.float32)


def stamp_hit(gain=0.8):
    t = np.arange(int(SR * 0.5)) / SR
    thump = np.sin(2 * np.pi * (70 + 120 * np.exp(-t * 30)) * t) * np.exp(-t * 11)
    click = signal.sosfilt(signal.butter(2, [2000, 6000], "bandpass", fs=SR, output="sos"), _noise(0.5, 4)) * np.exp(-t * 90) * 0.6
    y = thump + click
    return (y / np.abs(y).max() * gain).astype(np.float32)


def riser(dur=1.5, gain=0.35):
    n = _noise(dur, 6)
    t = np.linspace(0, 1, len(n))
    out = np.zeros_like(n)
    blk = 1024
    for i in range(0, len(n), blk):
        fc = 300 * (9000 / 300) ** (i / len(n))
        sos = signal.butter(2, [fc * 0.6, min(fc * 1.5, SR / 2 - 100)], "bandpass", fs=SR, output="sos")
        out[i:i + blk] = signal.sosfilt(sos, n[i:i + blk])
    return (out / (np.abs(out).max() + 1e-9) * t ** 2 * gain).astype(np.float32)


def gulp(gain=0.5):
    t = np.arange(int(SR * 0.28)) / SR
    f = 260 - 140 * t / 0.28 + 40 * np.sin(2 * np.pi * 14 * t)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * np.minimum(1, t / 0.01) * gain).astype(np.float32)


def step(gain=0.35, seed=3):
    """Weicher Schritt: kurzer, tiefpassgefilterter Aufprall."""
    n = int(SR * 0.11); t = np.arange(n) / SR
    y = signal.sosfilt(signal.butter(2, 700, "lowpass", fs=SR, output="sos"), _noise(0.11, seed)) * np.exp(-t * 38)
    y += np.sin(2 * np.pi * 95 * t) * np.exp(-t * 30) * 0.8
    return (y / (np.abs(y).max() + 1e-9) * gain).astype(np.float32)


def coin_down(gain=0.45):
    """Fallender Preis: abwaerts laufende Toene."""
    out = np.zeros(int(SR * 0.7), dtype=np.float32)
    for i, f in enumerate((880, 740, 622, 523)):
        t = np.arange(int(SR * 0.22)) / SR
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 14) * gain
        o = int(i * 0.1 * SR)
        out[o:o + len(s)] += s[: len(out) - o]
    return out


# ---------------------------------------------------------------- Musik
def _note(f, dur, kind="pad", amp=1.0):
    t = np.arange(int(SR * dur)) / SR
    if kind == "pad":
        y = sum(np.sin(2 * np.pi * f * (1 + c) * t + ph) + 0.5 * np.sin(2 * np.pi * 2 * f * (1 + c) * t) for c, ph in ((0, 0), (0.004, 1.3), (-0.004, 2.1)))
        env = np.minimum(1, t / 0.5) * np.minimum(1, (dur - t) / 0.6)
    elif kind == "pluck":
        y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 14)
        env = np.exp(-t * 6.5) * np.minimum(1, t / 0.004)
    else:  # bass
        y = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
        env = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.12)
    return (y * env * amp).astype(np.float32)


def _put(out, n, t):
    i0 = int(t * SR)
    if i0 >= len(out):
        return
    m = min(len(n), len(out) - i0)
    out[i0:i0 + m] += n[:m]


def music(dur, mood="dark", bpm=92, seed=0):
    """Hintergrundmusik (Am-F-C-G). mood: dark = ruhig/sphaerisch, tense = mit Puls."""
    beat = 60.0 / bpm
    bar = 4 * beat
    out = np.zeros(int(SR * (dur + 2)), dtype=np.float32)
    A = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    chords = [(57, (0, 3, 7)), (53, (0, 4, 7)), (60, (0, 4, 7)), (55, (0, 4, 7))]  # Am F C G (Grundton MIDI)
    rnd = np.random.RandomState(seed)
    nbars = int(dur / bar) + 2
    for b_ in range(nbars):
        root, iv = chords[b_ % 4]
        t0 = b_ * bar
        for k in iv:
            n = _note(A(root + 12 + k), bar * 1.05, "pad", 0.16)
            _put(out, n, t0)
        for h in (0, 2):
            n = _note(A(root - 12), beat * 1.9, "bass", 0.5)
            _put(out, n, t0 + h * beat)
        steps = 8 if mood == "dark" else 16
        for s_ in range(steps):
            if mood == "dark" and rnd.rand() < 0.35:
                continue
            k = iv[(s_ * 2 + b_) % 3]
            n = _note(A(root + 24 + k + (12 if s_ % 4 == 3 else 0)), 0.5, "pluck", 0.22 if mood == "dark" else 0.16)
            _put(out, n, t0 + s_ * bar / steps)
        if mood == "tense":
            for s_ in range(8):
                n = _note(A(root - 12), beat * 0.45, "bass", 0.35)
                _put(out, n, t0 + s_ * beat / 2)
    out = out[: int(SR * dur)]
    sos = signal.butter(2, 5200, "lowpass", fs=SR, output="sos")
    out = signal.sosfilt(sos, out)
    out = reverb(out.astype(np.float32), 1.8, 0.3)[: int(SR * dur)]
    fade = np.minimum(1, np.minimum(np.arange(len(out)) / (SR * 1.2), (len(out) - np.arange(len(out))) / (SR * 1.5)))
    return (out / (np.max(np.abs(out)) + 1e-9) * fade).astype(np.float32)


def envelope(x, win=0.06):
    e = np.abs(x)
    n = max(1, int(SR * win))
    return np.convolve(e, np.ones(n) / n, mode="same")


class Mix:
    """Sammelt Stimme, Effekte, Musik und mischt mit Ducking."""

    def __init__(self, total):
        self.n = int(SR * total)
        self.voice = np.zeros(self.n, dtype=np.float32)
        self.sfx = np.zeros(self.n, dtype=np.float32)
        self.bg = np.zeros(self.n, dtype=np.float32)

    @staticmethod
    def _add(buf, x, t, g=1.0):
        i = int(t * SR)
        if i >= len(buf):
            return
        seg = x[: len(buf) - i] * g
        buf[i:i + len(seg)] += seg

    def add_voice(self, x, t, g=1.0):
        self._add(self.voice, x, t, g)

    def add_sfx(self, x, t, g=1.0):
        self._add(self.sfx, x, t, g)

    def set_music(self, m, g=0.5):
        n = min(len(m), self.n)
        self.bg[:n] = m[:n] * g

    def render(self):
        env = envelope(self.voice, 0.15)
        duck = 1.0 - 0.62 * np.clip(env / 0.12, 0, 1)
        duck = signal.sosfilt(signal.butter(1, 4, "lowpass", fs=SR, output="sos"), duck).astype(np.float32)
        y = self.voice * 1.0 + self.sfx * 0.9 + self.bg * (0.26 * duck)
        pk = np.max(np.abs(y)) + 1e-9
        if pk > 0.97:
            y = y / pk * 0.97
        return y.astype(np.float32)
