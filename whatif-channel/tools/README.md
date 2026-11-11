# Kostenlose Produktions-Pipeline (Version 2)

Alles läuft ohne Abo und ohne Credits: Python, Skia (Zeichnen), ffmpeg, offline laufende KI-Stimme, selbst erzeugte Musik und Soundeffekte.

## Dateien

| Datei | Aufgabe |
|---|---|
| `gfx.py` | Zeichen-Grundlagen (Verläufe, Schatten, Glow, Text mit Umrandung, Animationskurven) |
| `chars.py` | Figuren-Rig: Kugel-Licht am Kopf, Hoodie/Anzug mit Falten, Handschuhe, Gesicht (Augenbrauen, Lider, Mund-Formen), IK für Arme |
| `scenes.py` | Hintergründe (Autohaus, Tiefsee), Auto, Glocke, Schallwellen, Preisschild, Stempel, Effekte |
| `audio.py` | Stimme (Kokoro v1.0, 54 Stimmen), Soundeffekte, Musik, Abmischung mit Absenken der Musik unter der Stimme |
| `make_clip.py` | Beispielszene aus Skript 01 (Zeitplan, Einstellungen, Lippenbewegung, Kamerafahrten) |
| `thumb.py` | Thumbnail |
| `voices_sampler.py` | Hörprobe mit mehreren Stimmen |

## Einrichtung

```bash
pip install "sherpa-onnx<2.0" numpy scipy pillow skia-python font-fredoka-one
sudo apt-get install ffmpeg libegl1 libgl1      # nur Linux; Windows/Mac brauchen das nicht
curl -L -o kokoro.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2
tar xjf kokoro.tar.bz2                          # ca. 350 MB, einmalig
export KOKORO_V1_DIR=$PWD/kokoro-multi-lang-v1_0

python3 voices_sampler.py stimmen.wav           # Hörprobe, um Stimmen zu vergleichen
python3 thumb.py thumbnail.png
python3 make_clip.py clip.mp4 am_michael am_onyx am_puck   # Erzähler, Verkäufer, Pip
```

`sherpa-onnx` muss unter Version 2.0 bleiben, sonst fehlt der eingebaute Aussprache-Teil.

## Messwerte (4 CPU-Kerne)

- Die 19,4-Sekunden-Szene (Stimme, Musik, Effekte, 466 Bilder) brauchte 41 Sekunden: etwa 2-fache Echtzeit. Ein 10-Minuten-Video wären ca. 20 bis 25 Minuten.
- Erzähltempo: ca. 170 bis 180 Wörter pro Minute (Vorbild: ca. 173).
- Lautheit des Beispielclips: ca. -16 LUFS, Spitzenpegel -1,3 dBFS.

## Grenzen

- Ich kann die Tonqualität nicht hören, nur messen. Die Stimmwahl muss ein Mensch treffen.
- Kokoro ist eine gute freie Stimme, aber weniger ausdrucksstark als bezahlte Dienste.
- Die Bild-Bibliothek (Figuren-Posen, Orte, Requisiten) wächst mit jedem Video. Das ist der Hauptaufwand.
- Lizenzen (Kokoro, sherpa-onnx, Fredoka One) vor der Monetarisierung auf den Projektseiten prüfen.
