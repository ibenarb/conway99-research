# Vollständiges Radiusreview: Abgleich und revidierter Plan

27.09.2026. **Dieser Plan ersetzt den vorläufigen 12-CPU-h-Längenmischungsvergleich. Kein neuer Suchlauf ist implementiert oder gestartet.**

## Empfehlung

Den Kern des Reviewervorschlags übernehmen: an den beiden fixierten Rekordgraphen ein Profil der Rückkehr und Verbesserung nach **einzelnen Perturbationsweglängen**, jeweils gefolgt vom unveränderten P-Steilstabstieg. Dabei die ungültigen Kontrollannahmen, den geänderten Gleichstandsentscheid und die Vermischung von BFS-Schichten mit Zufallswegen korrigieren. Kein Tiefe-5-Kalibrierungsblock. W2079 als festes positives Kontrollbeispiel, nicht als dritter vollwertiger Sucharm.

Ziel: 300 unabhängige geseedete Wege je Kombination aus zwei Starts und zehn Weglängen, insgesamt 6000 Episoden. Harte Grenze 20 Such-CPU-h plus 2 Hilfs-CPU-h. Bei durchschnittlich 6 CPU-s/Episode wären etwa 10 Such-CPU-h nötig; das ist eine vorläufige Schätzung. Keine automatische Fortsetzung.

## Vollständiger Eingang

Der nachgereichte Bildschirmtext ist 33575 Bytes lang, SHA256
`1f095c2e297c9dd25bfe52e628b0eb299de75e8509fe943d1f0d627bf01c83e8`.
Er enthält das strategische Review und spätere Fortschrittsantworten. Die endgültigen Tiefe-3-Zahlen im bereits geprüften ZIP ersetzen die früheren Zwischenstände; diese sind keine widersprüchlichen Endergebnisse.

[Unverändertes Original mit ZIP und Nachtragsmetadaten](https://github.com/ibenarb/conway99-research/tree/06cdb5f4175aced5c30f6f9fe8245873211ebc09/docs/reviews/20260927_lambda_radius), Zweig `reviews/20260927-lambda-radius`.

Mein erster Abgleich beschrieb korrekt den damals gelieferten ZIP-Inhalt, aber noch nicht die Gesamtposition des Reviewers. Diese Lücke ist jetzt geschlossen. Die dortigen kleinen Prüfergebnisse bleiben gültig; der dortige Versuchsplan wird durch diesen Plan ersetzt.

## Übereinstimmung und sinnvolle Änderung meines Vorschlags

Wir stimmen in der Entscheidung überein: kein automatischer Radius 5, kein unbegründeter F-Wechsel, kein großer unveränderter P-Lauf; stattdessen eine begrenzte Diagnose der Perturbation mit anschließendem Abstieg. Die externe Tiefe-3-Nachzählung stärkt die Rechnung, ersetzt aber weiterhin keine unabhängige vollständige Tiefe-4-Enumeration und verwendet gemeinsamen Katalogcode.

Mein vorläufiger Versuch verglich drei Mischungen der bestehenden Längenintervalle. Das beantwortet eine unmittelbare Methodenwahl, verdeckt jedoch, bei welchen konkreten Längen der Effekt entsteht. Der Reviewer stellt die diagnostisch präzisere Frage nach dem Profil R(k), E(k). **Deshalb ändere ich meinen Plan zugunsten einzelner Weglängen.** Die größeren harten Reserven finanzieren die getrennten Zellen; sie sind keine Aufforderung, ungenutztes Budget aufzubrauchen.

## Nötige Korrekturen am Review

1. **Radius 4 erzwingt keine Rückkehrrate nahe eins für k=1 oder 2.** Perturbation plus Abstieg kann insgesamt länger als vier Züge sein und in einem schlechteren lokalen Minimum enden. Auch eine Verbesserung nach kurzem Stoß wäre vereinbar, falls der gesamte Weg mindestens fünf Züge hat. Die vorgeschlagene Kontrolle (b) ist daher zu streichen. Prüffähig ist stattdessen: ein reproduzierter strikt besserer Zustand nach insgesamt höchstens vier Apex/Pivot-Zügen wäre ein Widerspruch zum Radiusbefund.
2. **Erreichbarkeit beweist keinen bestimmten Steilstabstieg.** Der bekannte Vier-Zug-Pfad allein begründet Kontrolle (a) nicht. Für dieses konkrete Beispiel habe ich sie jetzt geprüft: vom gespeicherten Mittelpunkt (2121,2544) führt der unveränderte kataloggeordnete P-Abstieg über (2098,2518) zum exakten W2076/L1=2488-Graphen. Beide gewählten Schritte wurden unabhängig nachbewertet und auf λ geprüft; der Endzustand ist ein lokales Minimum. Das macht diesen spezifischen Kontrollfall brauchbar. Er muss gezielt eingespeist werden, nicht zufällig unter 300 Wegen auftreten.
3. **P entscheidet Gleichstände nach Katalogreihenfolge.** `Engine.step_episode` wählt das erste Minimum nach (W,L1) aus der Katalogliste. Ein zusätzlicher Tie-Break nach sortiertem Zugtupel wäre eine Methodenänderung. Wir behalten den alten Entscheid exakt bei.
4. **Weglänge ist nicht kürzester Abstand.** Ein Zufallsweg von k Zügen kann zurücklaufen und in einer niedrigeren BFS-Schicht enden. Gleichgewichtete verschiedene Zustände einer Schicht sind zudem anders verteilt als Endpunkte uniformer Zufallszüge. Deshalb keine Zusammenfassung beider Stichprobenarten zu einem vermeintlich einheitlichen Tiefenprofil. Unser Pilot verwendet überall das gleiche Wegmodell und nennt den Parameter k.
5. **Die Rückkehrquote misst keine Erkundung der Region Abstand ≥5.** Ein zurückkehrender Weg kann diese Region besuchen, ein anderer Endpunkt muss nicht darin liegen. „Erkundung um Faktor fünf überschätzt“ folgt aus den Rückkehrzahlen nicht. Auch ein CPU-Verlust von 79 % ist damit nicht belegt. Unsere zuvor berechneten unteren Rückkehrgrenzen bei Länge ≥5 (58,53 % F; 62,10 % O) bleiben gültig.
6. **Nahe W-Werte sind kein Plateau von Endminima.** Der W2077-Zustand im Radius 2 um W2076 ist zunächst nur ein Zustand. Seine Existenz belegt weder ein weiteres lokales Minimum noch Neutralzug-Verbindungen. Die Schwelle W≤W(Start)+2 erlaubt außerdem Verschlechterung. „W2077 ist isolierter“ ist nur relativ zu dieser W-Schwelle und den geprüften Schichten belegt, nicht als Aussage über alle Abstiegsbecken oder Fluchtwahrscheinlichkeiten. Auch „ab Tiefe 3 steigt die Landschaft“ beschreibt die ersten Schichtminima, keine monotone Entwicklung aller weiteren Schichten.
7. **Die Tiefe-5-Rechnung vermischt Größenordnungen.** 7,4 Mio. ×1287 Bytes sind rund 9,52 GB = 8,87 GiB, nicht allein schon mehr als 10 GiB; SQLite-Indizes, Pfade und weitere Daten können den Rahmen dennoch sprengen. Faktor 37 auf 18,17643 h ergibt für den ersten Arm rund 673 CPU-h; auf beide Arme rund 1249 h. 1300 h passt eher zur groben Summe, nicht zu dem einzeln hergeleiteten Arm. Die Deduplikationsannahme bleibt spekulativ. 5000 Tiefe-3-Eltern zur Kalibrierung dieser ungewählten Option expandieren wir nicht.
8. **0/300 und „95 %“ benötigen eine Modellannahme.** Bei unabhängigen gleichverteilten Episoden mit festem Start/Abstieg ist die einseitige exakte Obergrenze 1−0,05^(1/300)=0,9936 %, je Zelle. Das ist keine simultane Aussage über alle Längen. Für 20 Zellen ergibt die einfache Bonferroni-Grenze etwa 1,98 % je Nullzelle. Historische O-Episoden sind wegen wechselnder Eltern und Auswahl nicht ohne Weiteres zusätzliche Bernoulli-Versuche; rund 4000 Episoden waren jeweils Gesamtzahlen, nicht die Zahl nach 4,75 h. Ein Nullpilot bleibt eine Budgetentscheidung, kein Erschöpfungsbeweis.
9. **Umfang und Aufwand des Reviewerplans sind nicht vollständig festgelegt.** Die anfängliche Formulierung „d=1…3 exakt“ wird später für Schicht 3 zur ID-Stichprobe korrigiert; für den dritten Start W2079 fehlen im Radiuspaket entsprechend vorbereitete SQLite-Schichten und Stichprobenregeln. Periodische ID-Auswahl ist keine Zufallsstichprobe. 12/12/6 h plus 2 Hilfsstunden ergeben 32 h; „höchstens 30 insgesamt“ wäre anders zu definieren. Unser Plan legt alle Zellen und Reserven ausdrücklich fest.

Kleine Formalie: Der Begleittext spricht von SHA256SUMS über 20 andere Dateien; tatsächlich enthält das ZIP 20 Dateien insgesamt und das Manifest 19 Einträge. Alle passen. Die Aussage „ohne B wäre ein F-/Operatorversuch nicht interpretierbar“ ist ebenfalls zu stark: Solche Versuche wären mit geeigneten Kontrollen interpretierbar; B ist hier eine Prioritätsentscheidung, keine logische Voraussetzung.

## Revidierter Versuch, vollständig vorab festgelegt

**Starts:** Exakte Graphen aus `STARTS.json` im Commit `8ec085cdb8402a6e33dc186ae0302fea4dd542ec`:

- A: W2076/L1=2488, state `8169eba8e1f2bf78eb655d99b94844a1eb5056df828e8c610a3778d537a7d0fe`.
- B: W2077/L1=2436, state `136bad89e063ba84bbc4201cfa5be21db6d511852602ad861a4d2c0e0ef8e49c`.

**Weglängen:** k∈{1,2,3,4,6,8,12,16,24,32}. Eine Episode startet immer neu am jeweiligen Originalgraphen. Uniforme Wahl aus dem vollständigen eingefrorenen Apex/Pivot-Katalog in jedem Perturbationsschritt; Rückzüge zulässig. Danach exakter P-Steilstabstieg mit alter Katalogreihenfolge und unveränderter strikter Zielfunktion (W,L1). Alle Zwischenzustände bleiben im λ-Raum. Keine Selektion, Populationserneuerung, Migration, Taburegel, Neutralzüge, cycle3 oder sonstige Methodenänderung.

**Stichprobe:** Je Start und k genau 300 vorab indizierte Wege, gruppiert in drei Blöcke zu 100; insgesamt 20 Zellen und 6000 Episoden. Seed für jede Episode: SHA256 von `lambda-profile-v2|state|k|index`, UTF-8, als unsigned Big-Endian-Integer; index=0,…,299. Keine nachträgliche Auswahl von Seeds. Wiederholte Zustände bleiben Beobachtungen für die Rückkehrquote, zählen aber nicht mehrfach zur Klassenvielfalt. Geseedete Wege sind reproduzierbar; das Profil ist keine exhaustive oder rein deterministische Basinvermessung. Die statistische Interpretation nutzt das übliche Modell unabhängiger Zufallsströme.

**Kontrolle:** W2079 ist kein dritter Sucharm. Sein gespeicherter Vier-Zug-Zeuge und der jetzt überprüfte zweischrittige Abstieg ab dessen Mittelpunkt sind feste positive Kontrollen. Root-Scores und λ unabhängig prüfen; Steilstabstieg gegen die bestehende P-Implementierung und ihre Gleichstandsbehandlung testen. Keine Forderung nach Rückkehrquote≈1.

**Kalibrierung:** Zuerst je 10 Episoden bei k=8 und 32 für beide Starts. Diese 40 Episoden sind die ersten vorab indizierten Beobachtungen der betreffenden Zellen, werden im Suchbudget verbucht und bleiben in der Auswertung. Gemessene Kosten, auch längere Abstiege, dienen der ETA. N wird nach Sichtung der Ergebnisse nicht geändert; eine erkennbare Budgetunzulänglichkeit führt zu `INCOMPLETE` statt stiller Stichprobenverkürzung.

**Budget:** Höchstens 1 CPU-h je Zelle, also 20 Such-CPU-h; keine Übertragung. Vorbereitung, Kontrollen, Auswertung und Programmstart zusammen höchstens 2 Hilfs-CPU-h. Gesamt maximal22 CPU-h. Jede Zelle endet nach 300 vollständigen Episoden oder ihrem Limit. Verifikation, Kanonisierung und Protokollierung während einer Episode zählen zum Suchbudget. Eine bei Limit unterbrochene Episode bleibt als zensiert samt Kosten und Checkpoint erhalten; sie zählt nicht als fertiger Endpunkt. Teilprofile mit N<300 werden explizit so berichtet; keine 0/300-Aussage dazu.

**Ausführung:** Höchstens 12 freie Ryzen-Worker, keine Verdrängung anderer Projektprozesse. Vorab festgelegte gemischte Rundfolge über alle 20 Zellen, beispielsweise Arbeitspakete zu 10 Episoden, damit lange Weglängen nicht erst nach Verbrauch aller Ressourcen an die Reihe kommen. Je Zelle nur ein aktives Paket; eindeutige Indizes, CPU-Ledger und Wiederaufnahme ohne Doppelerfassung. WSL-Drift berücksichtigen: Windows-Host-Monotonzeit, wait4-Abrechnung und Meldung alle zehn Minuten mit ETA.

**RAM/Disk/Walltime:** 8 GiB Prozessgruppen-RAM, 10 GiB neue Ausgaben; Pause unter 6 GiB verfügbarem RAM oder 25 GiB freiem Linux-/Windows-Datenträgerplatz. Keine großen alten SQLite-Dateien erforderlich. Bei 6 CPU-s/Episode etwa 10 Such-CPU-h, theoretisch 50 Minuten auf 12 voll nutzbaren Kernen; für Planung einschließlich Kontrollen und I/O etwa 2–3 Hoststunden. Diese Schätzung wird durch die Kalibrierung ersetzt. Harte zusätzliche Grenze 4 Hoststunden; bei Konkurrenz um Ressourcen keine Laufzeitgarantie.

**Aufzeichnung:** Je Episode vollständiger Perturbations- und Abstiegspfad, Start/Ende graph6-state/Klasse, k Soll/Ist, Anzahl Abstiegsschritte, getrennte und gesamte CPU-Kosten, fünf Scores, Rückkehr exakt/isomorph, Stopgrund, maximale W/L1/F-Werte entlang des realisierten Weges. Letztere sind beobachtete Wegmaxima, keine minimale notwendige Barriere. Endpunkte unabhängig voll bewerten und kanonisieren. Alle Verbesserungszeugen unabhängig replayen. Den aktuellen Weg und bereits verbuchte Kosten auch bei Zensierung erhalten.

**Auswertung je Start und k:** R(k) exakt und isomorph; E(k) für strikt (W,L1)-bessere vollständige Endpunkte; globale Rekorde W<2076 separat; Zahl verschiedener besserer Klassen, Endwertverteilung, CPU pro vollständiger Episode und pro Treffer, Anteil der CPU in Rückkehrepisoden. Ergänzend Zahl vom Start verschiedener Endklassen mit W≤W(Start)+2 als beschreibende Qualitätsgruppe, ausdrücklich kein Neutralplateau-Nachweis. Zwischenzeitliche bessere Zustände separat melden; sie mit vollständigen Endpunkten nicht vermischen. Bei ungleichen Kosten Wahrscheinlichkeiten pro Episode und Nutzen pro CPU getrennt berichten.

## Entscheidungen nach dem Pilot

- Jeder geprüfte bessere Zustand ist ein lokaler Fund; W<2076 ist separat ein globaler Rekord. Nicht beim ersten Treffer abbrechen, sondern das vorab festgelegte Profil innerhalb der Limits fertigstellen. Nur eine vollständig bestätigte SRG-Lösung beendet den Versuch als gelöst.
- Ein Treffer führt zunächst zu Zeugen- und Pfadanalyse. Treffer einer Zelle in mindestens zwei der drei festen 100er-Blöcke begründen die Auswahl dieser Länge für einen **neuen** Bestätigungsplan; das ist eine pragmatische Vorabregel, keine behauptete Methodenüberlegenheit. Wiederholung derselben Klasse zeigt Reproduzierbarkeit, keine Vielfalt. Vergleich mit der alten Längenmischung und adaptiven 16er-Population wäre erst Gegenstand dieses Folgeplans.
- Kein lokaler Treffer nach vollständiger Stichprobe: weitere unveränderte W-Frontier-Suche pausieren. Kleine E(k) sind nicht ausgeschlossen; nur der jetzt vereinbarte Ansatz rechtfertigt dann kein weiteres automatisches Budget.
- Viele andere oder nahe Endminima, aber keine Verbesserung: Profile archivieren. Kein automatischer Plateauwalk; dafür müsste eine konkrete Verbindungs-/Akzeptanzhypothese begründet werden. Eine niedrigere Rückkehrquote allein reicht nicht.
- Budget-/Ressourcenende vor N=300: jeweilige Zelle `INCOMPLETE`; kein globales negatives Urteil aus unvollständigen Zellen. Score-, λ-, Replay-, Katalog- oder Buchungsfehler: eigene Prozesse stoppen und `DIAGNOSIS_REQUIRED`. Fremde Prozesse bleiben unberührt. Keine automatische Verlängerung.

## Prüfartefakte dieses Nachtrags

`supplement/check_controls.py` und `supplement/CONTROLS.json`: konkreter positiver Abstieg ab dem bereits gespeicherten Mittelpunkt, unabhängige Score-/λ-Prüfung seiner Schritte und die genannten arithmetischen Nachrechnungen. Ausgeführt über den isolierten Audit-Helfer. Keine neue große Enumeration, keine neue Suchkampagne und keine Änderung an eingefrorenem Ryzen-Code.
