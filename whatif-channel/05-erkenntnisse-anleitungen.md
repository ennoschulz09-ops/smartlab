# Erkenntnisse aus Anleitungen (Stand 11.11.2026)

Gelesen (komplette Transkripte und Beschreibungen):
1. "How to Make Viral 3D 'What If' Videos Using Claude (FREE Skill)" (Saidox AI Flow): Nachbau eines What-If-Kanals mit 6,1 Mio. Views.
2. "I Made VIRAL Animation Videos Using Claude Code (FREE Plugin)" (Grow With Kaz, 335K Views): three.js + Remotion + ElevenLabs.
3. "How to Make Viral Animated Shorts Using Claude (Full Workflow)" (Mr omi, 959K Views) plus sein **frei nutzbarer Skill (MIT-Lizenz)**: github.com/mromidev/claude-animated-shorts.

## 1. Bestätigt: Der Weg ist richtig

- Die erfolgreichen Kanäle dieser Art werden **mit 3D aus Code** gebaut (three.js, Remotion), ohne KI-Videogenerator.
- Der Unterschied zwischen "billig" und "premium" liegt im **Handwerk**, nicht im Werkzeug.

## 2. Warum erste Versionen billig aussehen (aus allen drei Quellen)

| Problem | Lösung |
|---|---|
| Flaches Licht | Tiefe, goldene Sonne mit langen Schatten, Schatten **violett-blau statt braun oder schwarz** |
| Keine Luft | Dunst/Nebel in Horizontfarbe, Hintergründe unscharf, Fokus auf den Augen |
| Kisten statt Dinge | Freie 3D-Modelle (z. B. Kenney, CC0) umgefärbt, gemalte Texturen mit dunklen Fugen |
| Ruckelnde Kamera | Kamerafahrten über 18 bis 40 Bilder mit weichem Ein- und Auslauf, bei Halten immer ein leichtes Hineinschieben, Stöße bei Einschlägen |
| Falsche Proportionen | Messen statt schätzen (Kopfhöhen, Gliedmaßen-Dicke) |
| Raten | **Referenz messen**: Helligkeit, Sättigung, Unschärfe, Kamerabewegung pro Bild, dann Seite-an-Seite-Vergleich mit Punktzahl pro Bereich |

## 3. Arbeitsweise, die funktioniert

1. Referenz Bild für Bild messen (Zahlen, keine Meinungen), Ergebnisse als Regelwerk speichern.
2. Erst **Standbilder** jeder Einstellung prüfen, dann rendern.
3. Bereiche trennen: Kamera, Welt/Licht, Materialien, Figuren, Nachbearbeitung. Jeder Bereich wird einzeln verbessert.
4. Prüfrunden mit Seite-an-Seite-Bildern und Punkten pro Bereich (beim Vorbild-Skill: von 4-5/10 auf 6-7/10 in 4 Runden).
5. Jede Bildreaktion landet 0 bis 3 Bilder **vor** dem passenden Wort.

## 4. Skript-Regeln (gemessen an 20 erfolgreichen Videos)

- Satz 1 ist der Haken: ein Paradox als Tatsache, ohne Einleitung.
- Kein Bild beschreibt, was man ohnehin sieht.
- Schnell und ohne Pausen erzählt (ca. 3,7 Wörter pro Sekunde bei Shorts).
- Wendepunkt mit "You see," zur echten Erklärung, Alltagsvergleich, ironisches Ende.

## 5. Stimme

- Alle drei nutzen **ElevenLabs**. **Der Gratis-Tarif von ElevenLabs erlaubt keine kommerzielle Nutzung** (laut ElevenLabs-Hilfe), also nicht für einen monetarisierten Kanal.
- Ein Erfolgsformat ("Minute Zero", 6,1 Mio. Views) kommt **ganz ohne Stimme** aus: Ich-Perspektive, eine wachsende Zahl, kurze Textzeile, Klang aus Code.
- Kostenlose Optionen: eigene Stimme (einzigartig), freie Modelle wie Kokoro (Apache-2.0, aber hörbar schwächer), oder Format ohne Stimme.

## 6. Hauptfigur

- Beim Vorbild ist "du" immer dieselbe Figur (hellblauer Hoodie) und steht in fast jeder Einstellung im Mittelpunkt. Nebenfiguren sind farblich zurückgenommen.
- Unser Beispiel hatte den Verkäufer im Fokus und keine durchgehende Geschichte. Das war ein Fehler.

## 7. Wichtig

- **Der Name "What If Lab" ist schon vergeben** (ein Kanal startete vor ca. 4 Wochen). Unser Arbeitstitel muss geändert werden.
- Referenzmaterial nur zum Studieren, nie hochladen. Eigene Geschichten, Figuren und Stimme.
- Remotion-Lizenz vor dem Einsatz prüfen (für Einzelpersonen laut Remotion kostenlos, Bedingungen ändern sich).
