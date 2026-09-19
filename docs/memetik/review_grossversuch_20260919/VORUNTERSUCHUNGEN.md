# Vorbereitung des nächsten Memetik-Großversuchs
Stand 19.09.2026. Vorschläge, keine bereits ausgeführten Experimente. Ergebnisgrundlage: BERICHT.md im selben Verzeichnis.

## 1. Was wir vor dem Start wissen müssen
Die eigentliche Entscheidung lautet nicht „Wie viele Matrizen können wir erzeugen?“, sondern: Welche Kombination aus Gründern, lokalen Operatoren und Fluchtsteuerung findet bei gleichem Aufwand neue, bessere Strukturen?

Begriffe getrennt führen:
- Konstruktionsfamilie: nachvollziehbares mathematisches Erzeugungsprinzip, nicht KI-Anbieter oder Seed.
- Graphstruktur: Isomorphieklasse des vollständigen Graphen.
- Arbeitszustand: Graph plus zulässiger Rahmen, relevant insbesondere bei Ω.
- Empirisches Einzugsgebiet: beobachtete Endpunktverteilung unter einem festgelegten Ziel und Algorithmus; kein intrinsisches oder vollständig bekanntes Objekt.
- Plateau für ein Ziel: zusammenhängende Komponente gleicher Zielwerte unter dem festgelegten Katalog. Für Linf heißt neutral: gleiches vollständiges Tupel (Linf,Nmax,L1), nicht nur gleiches Linf.
- Lokales Minimum im hier verwendeten Sinn: kein strikt besserer direkter Nachbar. Davon ein striktes Minimum (alle Nachbarn schlechter) und einen bloß budgetbeendeten Endpunkt unterscheiden.

## 2. Priorisierte Voruntersuchungen
| Priorität | Untersuchung | Messung und Entscheidung |
|---|---|---|
| P0 | Gemeinsames Gründerregister aus Altbestand, 14 aufgenommenen KI-Kandidaten und geprüften Nachfahren | Arm, Generator, Abstammung, graph6/Hash, vollständiger Score, Isomorphieklasse und Automorphismen; Lücken schließen, vorhandene Abnahmen verwenden |
| P0 | B ab W=2080 fertig untersuchen | Ein W-Abstieg mit abschließendem Katalogzensus; zusätzlich L1/F/Linf-Abstiege dieses neuen Starts im gemeinsamen Vorbereitungstest. Neue Nachfahren separat speichern |
| P0 | Kleine randomisierte Abstiegsserie je zugelassenem strukturellem Vertreter und vorgesehenem Selektionsziel | Startvorschlag vier Zufallsseeds, gleiche CPU-Obergrenze je Aufgabe; Verbesserung, Kosten und exakte Endpunktisomorphien. Bestehende deterministische Läufe als Referenz verwenden, nicht pauschal wiederholen |
| P0 | Kontrollvergleich strikter Abstieg gegen Plateau-/Escape-Steuerung | Erfolgsrate, Verbesserung pro CPU-Zeit, Anzahl neuer Endpunktklassen, Familienverlust und Wiederkehr zum gleichen Endpunkt |
| P1 | C08-Plateau und repräsentative neue Endpunkte | Begrenzte neutrale Exploration: Zahl verschiedener Zustände/Klassen, besuchte neutrale Kanten und gefundene Ausgangszeugen. Bei unvollständiger Exploration keine globale Ausgangsdichte oder Mischzeit behaupten |
| P1 | Kleine, armverträgliche Reparatur-/Makrooperatoren | Anteil zulässiger, nichtisomorph neuer Kinder; Kosten einschließlich Fehlversuchen und Reparaturen; Verbesserung nach gleichem Abstieg |
| P1 | Rekombinationsprobe | Kinder mit eigenständigem Strukturbeitrag und anschließendem Nutzen gegenüber budgetgleicher Mutation; bloße Rückgabe eines Elternteils zählt nicht als Erfolg |
| P2 | HoG-Vertiefung, komplette C08-Komponente, lokale A-Flucht und vollständige HoG-Zertifizierung | Eigene Forschungsfragen; keine allgemeine Startbedingung des Populationsversuchs |

Für A keinen weiteren Lauf im bekannten Achtzustandskatalog ansetzen. Ohne wirksame Erweiterung bleibt A als Referenz im Archiv, beansprucht aber nicht laufend viele aktive Plätze. HoG als hochwertigen Gründer bewahren, nicht allein wegen der großen Barriere aussortieren.

CPU-bedingte Abbruchendpunkte gesondert zählen. Die Rückkehrrate zu gleichen Klassen nur mit Ziel, Tie-Breaking und Budget berichten. Konfidenzintervalle bzw. Streuung über unabhängige Läufe zeigen; vier Seeds sind eine Vorauswahl, keine belastbare Wirksamkeitsstudie.

## 3. Diversität messen und neue Familien auswählen
Exakte Isomorphieprüfung für Gründer und ausgewählte Endpunkte ist überschaubar und vorrangig. Zusätzlich Residuenhistogramm, Defektgradprofil und Automorphismengruppe speichern. Diese Merkmale sind keine vollständigen Isomorphietests. Für gemeinsame Ω-Beschriftung ist Kantenabstand diagnostisch brauchbar; zwischen beliebigen Nummerierungen ist er kein strukturinvarianter Abstand.

Ungefärbte Isomorphie darf Ω-Arbeitszustände nicht automatisch aus der Suche entfernen: verschiedene Rahmen können unterschiedliche Operatornachbarschaften bedeuten. Zunächst Analyse und Diversitätskontrolle; eine Quotientensuche erst nach Nachweis, dass die zugelassenen Isomorphismen Nachbarschaften und Wegzeugen korrekt transportieren.

Aus dem Bestand drei bis vier zusätzliche, tatsächlich unterschiedliche Erzeugungsprinzipien anstreben. Prüfkandidaten für Entwicklungsarbeit:
1. Ω direkt aus den Inzidenz-/Marginalbedingungen, mit randomisierten Kosten und Beschränkung der Nähe zu vorhandenen Gründern; keine globale srg-Bedingung als Aufnahmehürde.
2. Ω durch größere zulässige Kerneländerungen von H: D symmetrisch, Nulldiagonale, PD=0, Gradbedingung und Binärität von H+D explizit prüfen. D≠0 garantiert weder neue Isomorphieklasse noch brauchbare lokale Flucht.
3. λ über eine lineare 3-uniforme Hypergraphstruktur: 99 Punkte, jeder in sieben Tripeln, 231 Tripel insgesamt. Paare höchstens einmal und keine Berge-Dreiecke sicherstellen, damit der Schatten einfach, 14-regulär ist und jede Kante genau ein Dreieck trägt. Existenz, Erzeugungsrate und Diversität sind zu testen, nicht behauptet.
4. Strukturvorgaben schrittweise lockern oder zwischen zulässigen Eltern reparieren; feste Symmetrie höchstens als Erzeugungshilfe, nicht dauerhaftes Selektionskriterium. Neue Familie nur bei anderem Prinzip oder nachgewiesen anderem Suchverhalten anerkennen.

Diese Skizzen sind keine Literatur-Neuheitsbehauptungen und kein Ersatz für die bereits eingesammelten Kandidaten. Ihre Originalität und praktische Erzeugbarkeit gehören in den Review. Für die aktuelle Planung keine neuen Symmetrieausschlüsse oder fremden Zweige übernehmen.

## 4. Drei Strategien zur Wahl
### A — Früher Start mit konservativer Steuerung
Strukturell geprüfte größere Gründerbasis, L1/F/Linf-Inseln, strikter Abstieg, kurze neutrale Spaziergänge mit Besuchsspeicher und gelegentliche zulässige Mutation/Neustart. Gründerfamilien zunächst durch Mindestvertretung schützen.
Vorteil: kleiner Implementierungsaufwand und klarer Vergleich zum alten Pilot. Risiko: echte Barrieren wie B werden nur zufällig überwunden.

### B — Adaptive Plateau- und Fluchtsteuerung (bevorzugt)
Wie A, ergänzt um begrenzte Escape-Episoden nach Stagnation: neutrale Exploration, dann kleine Minimax- oder Schwellenepisoden bzw. stärkere Mutation. Rohbarrieren in W, L1 und F nicht gemeinsam kalibrieren; pro Ziel und Familie aus beobachteten Trade-Kosten und Ausbeute ableiten. Für Linf lexikographische Ordnung verwenden, keine willkürliche skalare Gewichtung.
Zuweisung zusätzlicher Arbeit an Mechanismen mit beobachtetem Erfolg, mit einem fest reservierten Explorationsanteil für bislang erfolglose Familien. Minimax-Datenbanken bleiben lokale Diagnoseinstrumente; keine unbeschränkte Datenbank pro Individuum.
Vorteil: reagiert auf die drei beobachteten Hindernistypen. Risiko: Verwaltungsaufwand und Überanpassung an A/B/C08/HoG. Deshalb an zusätzlichen, nicht zur Parametrierung verwendeten Gründern prüfen.

### C — Größere Variation und Rekombination
Wie B, ergänzt um armverträgliche Makrotrades/Fensterreparatur und echte Rekombination. Nur Eltern desselben Arms, mit geprüftem Arbeitsrahmen. Erzeugung plus Reparatur plus lokaler Abstieg gemeinsam budgetieren. Gegen Mutation aus denselben Eltern vergleichen.
Vorteil: möglicher Wechsel zwischen bisher getrennten Bereichen. Risiko: teure Reparaturen, Klone und Verletzung harter Gleichungen. Ohne messbaren Zusatznutzen kein Pflichtbestandteil des Großversuchs; eine Crossoverquote von 20 % ist eine zu prüfende Hypothese, keine begründete Konstante.

## 5. Konkreter Vergleich vor der Skalierung
Zuerst drei Varianten bei gleicher Population und gleichem CPU-Gesamtbudget vergleichen: A0 strikter Abstieg/Mutation; A1 zusätzlich neutraler Besuchsspeicher; A2 zusätzlich begrenzte Escape-Episoden. L1, F und Linf getrennt in beiden Armen auswerten. Mindestens drei unabhängige Wiederholungen pro Konfiguration als Screening; gepaarte Gründerbestände und dokumentierte Seeds, nicht einzelne Generationen als unabhängige Stichproben behandeln.

Primär: Verlauf des jeweils selektierten Ziels über CPU-Zeit und Zahl verbesserter, nichtisomorpher Endpunkte. Sekundär: alle weiteren Scores, Familienanteile, Duplikatrate, Kosten pro zulässigem Kind, Rückkehrquote, Speicherbedarf. W bleibt Diagnose. Rohgewinne verschiedener Normen nicht zu einer Gesamtrangliste addieren.

Anschließend nur die zwei überzeugendsten Varianten mit längeren Läufen vergleichen. Makrooperatoren/Crossover einzeln ergänzen, damit ihr Nutzen zugeordnet werden kann. Zusätzliche Familien und zusätzliche Rechenzeit nicht gleichzeitig verändern und dann den Gewinn allein „Diversität“ zuschreiben.

## 6. Startfreigabe und Population
Keine vollständige Plateau- oder Barrierentheorie abwarten. Startbereit ist der neue Versuch, wenn:
- alle verwendeten Gründer gültig, reproduzierbar und mit Herkunft/Klassen versehen sind;
- zusätzliche Plätze nicht nur Umnummerierungen oder blind kopierte Nachfahren enthalten;
- ein begrenzter Vergleich die gewählte Steuerung gegenüber der einfachen Referenz rechtfertigt, sonst startet die Referenz;
- harte Armverträge bei Nachkommen geprüft werden, Checkpoints konsistent sind und Status/Budget nachvollziehbar bleiben.

Planungsgröße: zunächst 32 aktive Individuen je Arm und Selektionsziel, dann 64 nach Ressourcen- und Diversitätsprüfung. Das wären bei zwei Armen und drei Zielen 192 bzw. 384 aktive Plätze, nicht ebenso viele unabhängige Familien. Population nicht künstlich mit „neuen Familien“ auffüllen; reichen strukturell verschiedene gültige Gründer nicht, kleiner beginnen und laufend ergänzen. Familienquoten anfangs schützen, später anhand der gemessenen Ausbeute lockern; schwächere neue Strukturen im getrennten Archiv behalten.

Vorbereitung auf einen festen Anteil des Gesamtbudgets begrenzen, z.B. höchstens 10–15 % als Planungsregel, keine gemessene optimale Quote. Neue Vorfragen nur aufnehmen, wenn sie eine konkrete Startentscheidung ändern. Vollständige HoG-Rezertifizierung kann parallel zur methodischen Forschung geplant werden.

Office-Zahlen beziehen sich auf rb-PC mit vier Kernen/acht Threads und rund 4,8 GiB WSL-RAM. Ein möglicher künftiger Großlauf auf Ryzen benötigt ein eigenes gemessenes Ressourcenprofil; keine Office-Speicherlimits ungeprüft vervielfachen. In dieser Vorlage wird kein Rechner umbelegt und kein Lauf gestartet.
