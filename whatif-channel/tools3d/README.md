# 3D-Rendering im Browser (kostenlos)

Ziel: Die 3D-Bildsprache des Vorbilds nachbauen (Kugelkopf-Figuren, Stimmungslicht, Tiefenunschärfe). three.js läuft im vorinstallierten Chromium ohne Grafikkarte (SwiftShader), jedes Bild wird einzeln gerendert.

## Dateien

| Datei | Aufgabe |
|---|---|
| `buddy.js` | Figur: iridisierende Kugel, Gesicht auf einer Zeichenfläche (Brauen, Lider, Mund, Blickrichtung, steuerbar pro Bild), Hals, Hoodie, Arme mit Gelenken, Kugelhände, Beine, Mütze |
| `scene_demo.html` | Beispielszene (Casino): Licht, Tisch, Roulette, Chips, drei Figuren, Tiefenunschärfe, Farbkorrektur, Vignette |
| `render.cjs` | Rendert Bilder: `node render.cjs scene_demo.html 0,1.5` erzeugt `shot_0.png`, `shot_1.5.png` |

## Einrichtung

```bash
npm install three@0.160.0
npm install -g playwright   # oder vorinstalliertes Playwright mit Chromium nutzen
node render.cjs scene_demo.html 0,1.5
```

## Messwerte (4 Kerne, 1280x720)

- Erstes Bild ca. 1,9 s (Shader werden übersetzt), danach ca. 0,8 s pro Bild mit Schatten und Tiefenunschärfe.
- Ein 10-Minuten-Video mit 24 Bildern pro Sekunde hätte 14.400 Bilder. Statische Einstellungen brauchen nur wenige Bilder plus Kamerafahrt. Realistisch sind einige Stunden Rechenzeit pro Video.

## Offen (nächste Schritte)

- Szenen-Bibliothek (Casino, Spind, Arena, Straße ...), Requisiten, Figuren-Posen, Kamerafahrten.
- Zusammenspiel mit der 2D-Erklärgrafik (`../tools/`) und den Beschriftungen (Pillen, Zähler, Sprechblasen).
- Tonspur aus `../tools/audio.py`.
