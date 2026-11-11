# 3D- und Erklär-Video (kostenlos)

Ziel: Die Bildsprache des Vorbilds nachbauen: 3D-Szenen mit Kugelkopf-Figuren, Stimmungslicht und Tiefenunschärfe, dazu 2D-Erklärgrafik mit Pillen und Zählern.
Alles läuft ohne Abo: three.js im vorinstallierten Chromium (ohne Grafikkarte), Skia, ffmpeg, Kokoro-Stimme.

## Dateien

| Datei | Aufgabe |
|---|---|
| `buddy.js` | Figur: Kugelkopf, Gesicht als Zeichenfläche (Lider, Brauen, Mund, Blick, Schweiß, Lippenbewegung), Hoodie, Arme mit Gelenken, Mütze/Haare/Krawatte |
| `world.html` | 3D-Welt: Glocken-Bühne, Autohof (Autos, Gebäude, Lichterkette), Papier-Requisit, 5 Einstellungen, Licht, Tiefenunschärfe, Bloom, Farbkorrektur |
| `render.cjs` | Rendert die 3D-Bilder einzeln (Chromium) und gibt Kopf-Positionen auf dem Bild zurück |
| `explainer.py` | 2D-Erklärgrafik (Gitter, Regeln, Pillen, Sprechblasen, Zifferblatt-Symbol, Schlusskarte mit Abonnieren-Knopf) |
| `make_video.py` | (alt) erstes Beispiel mit mehreren Stimmen |
| `make_pilot.py` | **Pilot**: nur Erzählerstimme, Zeitplan, goldene Stunde, Sprechblasen, Beschriftungen, Titelkarte, Musik, Effekte, Nachgrading, Export |

## Einrichtung

```bash
# einmalig, siehe ../tools/README.md: sherpa-onnx<2.0 numpy scipy pillow skia-python font-fredoka-one, ffmpeg, Kokoro v1.0
npm install three@0.160.0            # im Ordner tools3d
npm install -g playwright            # oder vorinstalliertes Playwright mit Chromium
KOKORO_V1_DIR=/pfad/kokoro-multi-lang-v1_0 python3 make_video.py beispiel.mp4 am_michael am_onyx am_puck
# nur Einzelbilder prüfen:    ... make_video.py x.mp4 --stills 1.2,5.9,15.3
# (make_video.py: --reuse nur bei unverändertem Zeitplan)
```

## Messwerte (4 Kerne, 1280x720, 24 Bilder pro Sekunde)

- Beispielvideo 27,6 s: 3D-Teil (284 Bilder) 228 s, Rest (Stimme, 2D-Grafik, Export) ca. 90 s.
- Etwa 0,8 s pro 3D-Bild. Ein 10-Minuten-Video mit etwa der Hälfte 3D-Szenen: grob 1,5 bis 2,5 Stunden Rechenzeit.
- Lautheit des Beispiels: -15,9 LUFS, Spitze -1,5 dBFS.

## Grenzen

- Die Stimme (Kokoro) und die Musik habe ich nicht gehört, nur gemessen.
- Es gibt erst 5 Einstellungen und 1 Figurenpaar. Die Bibliothek (Orte, Requisiten, Posen) wächst mit jedem Video.
- Das Kameraspiel ist einfach (langsame Fahrten), keine Handkamera-Schnitte wie beim Vorbild.


## Pilot (Stand v4)

```bash
KOKORO_V1_DIR=/pfad/kokoro-multi-lang-v1_0 python3 make_pilot.py pilot.mp4 am_eric
# optional jugendlicher: PITCH_SHIFT=2 ...   (Halbtöne höher)
# nur Beschriftung/Grading/Ton neu bei GLEICHER Stimme und gleichem Tempo:   ... --reuse   (gleiches WORK-Verzeichnis)
# Andere Stimme = anderer Zeitplan = voller Lauf (ca. 15 Minuten). --reuse bricht dann mit einer Fehlermeldung ab.
```

- Shotliste: `../06-shotliste-pilot.md`. Pip ist in jedem Bild.
- Stimme per Parameter wählbar (gewählt: Stimme 4 = `am_puck`), Hörprobe: `../tools/voices_sampler2.py`. Tempo-Kalibrierung auf ca. 185 Wörter/Min. reine Sprechgeschwindigkeit.
- Messwerte: 3D 638 Bilder in ca. 616 s, Rest ca. 2 Minuten.
