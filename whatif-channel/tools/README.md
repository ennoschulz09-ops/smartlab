# Kostenlose Produktions-Pipeline

Alles hier läuft ohne Abo und ohne Credits: Python, Pillow, ffmpeg, eine offline laufende KI-Stimme.

## Bestandteile

| Teil | Datei | Kosten |
|---|---|---|
| Stimme (Kokoro, offline) | `wi_tts.py` | 0 (Modell ca. 320 MB, einmaliger Download) |
| Figuren, Bühne, Glocke, Kamerafahrt | `wi_draw.py` | 0 |
| Beispielszene aus Skript 01 | `poc_video.py` | 0 |
| Thumbnail | `poc_thumbnail.py` | 0 |

## Einrichtung

```bash
pip install "sherpa-onnx<2.0" numpy pillow
sudo apt-get install ffmpeg          # oder ffmpeg.org
curl -L -o kokoro.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-en-v0_19.tar.bz2
tar xjf kokoro.tar.bz2
export KOKORO_DIR=$PWD/kokoro-en-v0_19
python3 poc_thumbnail.py thumbnail.png
python3 poc_video.py szene.mp4
```

Hinweis: `sherpa-onnx` muss unter Version 2.0 bleiben, sonst fehlt der eingebaute Aussprache-Teil für Kokoro.
Als Schrift dient Inter ExtraBold (unter `/usr/share/fonts/opentype/inter/`). Auf anderen Systemen den Pfad `FONT` in `wi_draw.py` anpassen.

## Geschwindigkeit (gemessen, 4 CPU-Kerne)

- Stimme: ca. 0,5-fache Echtzeit (10 Minuten Sprache brauchen etwa 5 Minuten).
- Video: ca. 3,6-fache Echtzeit (die 15,5-Sekunden-Szene brauchte 56 Sekunden, ein 10-Minuten-Video wäre etwa 35 Minuten).

## Grenzen (ehrlich)

- Die Stimme klingt gut verständlich, aber weniger lebendig als bezahlte Dienste. Eigene Aufnahme oder die kostenlosen Stimmen in CapCut sind Alternativen.
- Der größte Aufwand pro Video ist nicht das Rendern, sondern die **Bild-Bibliothek**: Figuren in verschiedenen Posen, Orte, Gegenstände. Sie wächst mit jedem Video und wird danach wiederverwendet.
- Lizenzen der Bestandteile (Kokoro-Modell, sherpa-onnx, Inter) vor der Monetarisierung auf der jeweiligen Projektseite prüfen.
