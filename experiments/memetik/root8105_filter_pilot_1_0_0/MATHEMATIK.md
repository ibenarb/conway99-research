# Aussage und Kontrollmodell

Historische Grundmenge F: dieselbe Geometry, constraints und VertexSampler-
Rangordnung wie im eingefrorenen rc3. kernel.py, filters.py, historical_core.py,
roots.tsv und BVLS-Fixture sind byteidentisch übernommen. Die fertige Zählung
B2 = 4846403679 und deren unabhängige Nachzählung werden nicht neu ausgeführt.
Der Aufbau des Samplers erfordert dessen Rekursionsgewichte; nur die 72 für
Unranking benötigten Gesamtsummen werden dabei mit den gespeicherten Census-
Werten verglichen. Das ist kein neuer Vollcensus.

Die 24 Roots/72 Zielpaare/4608 Ränge stammen byteidentisch aus dem vorab
festgelegten Auditmanifest. Die Zielpositionen sind Minimum, Medianrang und
Maximum, bei Sortierung nach (Breite, Label). Es werden weder Roots noch
Ränge nach Sichtung der Filterergebnisse ersetzt. Die vier Filteraufrufe
rotieren in ihrer Reihenfolge deterministisch über die 64 Ränge je Ziel.
Jeder Aufruf beinhaltet F-verify; die Kosten sind daher eigenständige Kosten
je Variante, nicht rein inkrementelle LD-/CAP-Kosten.

LD: Zwei H-Nachbarn v,w einer gebauten Zeile u teilen bereits u als Nachbarn.
Teilen ihre Zweierlabels einen Randknoten, besitzen sie mindestens zwei
verschiedene gemeinsame Nachbarn im Gesamtgraphen. Eine Kante vw wäre mit
lambda=1 unvereinbar. Solche Kanten müssen deshalb 0 sein.

CAP: Für jede offene Zeile werden notwendige Grad-, Randmargen- und
Codegree-Gleichungen betrachtet. Festgelegte Einsen ergeben eine Untergrenze;
alle noch verfügbaren Positionen eine Obergrenze. Ein Zielwert außerhalb
[Untergrenze,Obergrenze] ist unmöglich. Mit LD werden zusätzlich durch LD
verbotene Positionen entfernt. Deshalb kann die Kombination stärker sein
als die Vereinigung der separat gemessenen Ausschlüsse.

SAT-Kontrolle: Zuerst alle Stichproben abschließen. Dann pro (Roottyp,
Ablehnungsgrund) die ersten acht verschiedenen Zustände in lexikographischer
Ordnung (Root,Ziel,Rang), oder alle wenn weniger vorhanden. Jeden gewählten
Zustand unter allen Varianten prüfen, die ihn aus diesem Grund ablehnen.
Keine erneute Auswahl nach SAT-Ergebnis. Auswahl vor Solverstart gespeichert.

sat_control.py rekonstruiert Labels selbst und importiert weder kernel.constraints
noch filters. Für LD werden notwendige Nullkanten/Nullcodegrees kodiert;
für CAP die vollständigen notwendigen Gleichungen der als Widerspruch
benannten offenen Zeile. Diese CNF ist eine notwendige Relaxation, kein
vollständiges SRG-Modell. Glucose-UNSAT wird als UNSAT_UNCERTIFIED gespeichert;
kein formales Zertifikat behauptet. SAT wäre ein Kontrollwiderspruch und
verhindert die Abnahme. UNKNOWN bleibt UNKNOWN und verhindert eine vollständige
mathematische Abnahme. Ein Überleben der billigen Filter ist kein SAT-Zeuge.

Positivkontrollen: vollständiger BVLS-Graph srg(243,22,1,2), unabhängige Prüfung
aller Grade und Codegrees per Matrixidentität; zwölf Präfixe bestehen LD/CAP.
Zusätzlich drei Präfixtiefen in allen vier Varianten mit der vollständigen
bekannten Belegung als SAT-Annahmen. Die leere F-Relaxations-CNF ist allein
kein F-Nachweis; F wird vorher durch die vollständige Matrix und Präfixprüfungen
kontrolliert. Zwei absichtlich ungültige Kleinzustände testen lediglich die
Ablehnungsprädikate. Sie werden nicht als gültige F-Stichproben ausgewiesen.

Auswertung je Roottyp und Zielposition: Ausschlüsse, Ablehnungsgründe,
Schnittmenge der separaten LD-/CAP-Ausschlüsse, zusätzliche reine
Kombinationsausschlüsse und CPU. Keine naive Hochrechnung der absichtlich
überrepräsentierten seltenen Typen; keine exakten gefilterten Breiten,
keine Rootausschlüsse und keine Aussage über die gesamte Suchbaumgröße.
