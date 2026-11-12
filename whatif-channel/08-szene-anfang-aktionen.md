# Folge 1, Anfang (ca. 36 s): eine durchgehende Szene, Aktionen statt Standbilder

Ort: Autohof im goldenen Abendlicht. Eigene Geschichte, nichts aus dem Beispielvideo übernommen. Drei Stimmen: Erzähler (Stimme 4), Pip, Verkäufer.

Prinzip pro Zeile: **Anlauf, Bewegung, Nachschwingen, Reaktion der anderen Figur, Schnitt auf die Aktion.**

| Zeile | Sprecher | Aktion (Anlauf, Bewegung, Nachschwingen) | Reaktion / Detail | Schnitt |
|---|---|---|---|---|
| "You have six hundred dollars and no car." | Erzähler | Pip geht von rechts ins Bild (Gehzyklus: Beine, Armschwung, Körperwippen) | Verkäufer poliert mit dem Rücken zur Kamera ein Auto | Seitliche Fahrt, folgt Pip |
| "Today, that changes." | Erzähler | Pip bremst, plant die Füße, reibt die Hände (Vorfreude), dreht sich zum Verkäufer | | Zwei-Einstellung |
| "Great news, buddy! One owner. Never been in an accident." | Verkäufer | Wirbelt herum (Überschwingen), Arme weit, **Klatschen** | **Schlag 1** nach "One owner", **Schlag 2** am Ende | Untersicht auf den Verkäufer |
| (Schlag 1) | | Pip: Kopf zuckt zurück, Körper staucht, **Hände an die Ohren**, Pom-Pom federt nach, Zähne zusammen, Tinnitus-Pfeifen | "LIE"-Schild über dem Verkäufer | Schnitt genau auf den Schlag: Pip nah |
| "Ow!" / "Is that... a bell?" | Pip | Hände bleiben an den Ohren, Gesicht wechselt zu "Autsch" | | Zwei-Einstellung |
| "A what? Ha! Nope. Just, uh, wind chimes." | Verkäufer | **Nervöses Lachen**: Schultern zittern, Hände wehren ab | **Schlag 3**, Schweißtropfen | Über Pips Schulter |
| "And slowly, you understand." | Erzähler | Pip lässt die Hände langsam sinken, Augen verengen sich | | Langsame Fahrt auf Pip |
| "The report says four owners." | Pip | **Papier ziehen**: Arm zurück (Anlauf), vorschnellen, Papier klappt auf mit Überschwingen | Verkäufer erstarrt | Halbtotale |
| "Typo." | Verkäufer | Erstarrt, Kopf wendet sich ab, Zittern | **Schlag 4** | Nah auf den Verkäufer |
| "And two accidents." | Pip | Macht einen Schritt vor und stößt mit dem Papier nach | Verkäufer weicht einen Schritt zurück | Zwei-Einstellung |
| "Double typo." | Verkäufer | **Sackt zusammen** (Körper staucht, Kopf sinkt) | **Schlag 5** | |
| "Okay, okay. Three hundred. Final." | Verkäufer | Hände hoch (Aufgeben, mit Überschwingen) | **Kein Schlag: die Wahrheit.** | Nah auf Verkäufer |
| (Stille) | | Pip hört zu, neigt den Kopf, Braue geht hoch, lächelt | | Schnitt auf Pip |
| "Sold." | Pip | Schlägt ein: beide drehen sich ins Profil, **Handschlag mit Pumpen** (Hände werden aufeinander ausgerichtet) | Detail aufgelöst: 600 Dollar, bezahlt 300 | Seitenansicht |
| "So, what if you could hear every lie?" | Erzähler | Totale, Kamera zieht zurück | Titel "WHAT IF YOU COULD HEAR EVERY LIE?" | Titelkarte |
| "Everyone says they'd love it. Until the first bell." | Erzähler | Pip allein, **Schlag in seinen Ohren**, Hände an die Ohren, Bild blendet ab | Klingeln beidseitig | Nah auf Pip |

Messbar: 15 Schnitte in ca. 36 s (etwa alle 2,4 s), 6 Glockenschläge, 3 Stimmen.

## Arbeitsweise (neu)

- Bewegung wird an **Bildfolgen** geprüft (`tools3d/strip.py`), nicht an Einzelbildern.
- Schnelle Vorschau mit `PREVIEW=1` (3D in 640x360, 12 Bilder pro Sekunde, ca. 3 bis 4 Minuten), voller Lauf nur einmal.

## Noch nicht gesehen

Wie die Figuren im Beispielvideo tatsächlich animiert sind. Dafür brauche ich die Bildschirmaufnahme.
