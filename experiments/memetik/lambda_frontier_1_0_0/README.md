# Lambda Frontier 1.0.0 — 32 CPU-Stunden, acht unabhängige Zufallsseeds

Vom Benutzer freigegebene Folgeetappe: zwei konkrete Startpopulationen mit
Bestwerten W=2096 und W=2101, je vier frische Wiederholungen à 14400 CPU-s.
Keine Migration, keine neuen Operatoren, keine Änderung der 16er-Selektion.

## Feste Hypothese und Entscheidung

Frage: Erzeugen die beiden jüngsten Frontier-Populationen weitere W-Rekorde?
Primärer Erfolg eines Jobs: adoptiertes best.W < 2096, unabhängig nachgerechnet.

- 0 erfolgreiche Jobs: weitere reine W-Frontier-Fortsetzung vorerst pausieren.
- 1 erfolgreicher Job: Einzelsignal dokumentieren, keine automatische größere Investition.
- Mindestens 2 erfolgreiche Jobs: wiederholtes Fortsetzungssignal; nächste Etappe erst bewerten.

Alle erfolgreichen Endbestwerte werden nach beschrifteter Identität und
Isomorphieklasse gruppiert. Wiederfinden derselben Klasse beweist keine Vielfalt.
Andere Normrekorde werden bewahrt, ersetzen aber nicht nachträglich das W-Kriterium.
Keine automatische Verlängerung. Eine exakt verifizierte Lösung stoppt die Kampagne
und wird doppelt gespeichert. Negative Ergebnisse sind kein Erschöpfungsbeweis.

## Startdaten

Quellarchiv: ryzen_lambda_decision_100_20260924_verified.tar.gz,
SHA256 4b8c28b75241b6490388127b532351833fcb6fb5f07adb1ec8cd8413bb5dc4a4.

| Bank | Quelljob | Bestwert (W,L1,F) | W-Spanne | Seeds |
| --- | --- | --- | --- | --- |
| 2096 | V2-W2102-0 | (2096,2480,3272) | 2096–2225 | 2026092700–2026092703 |
| 2101 | V2-W2108-1 | (2101,2450,3172) | 2101–2154 | 2026092704–2026092707 |

Auswahl: Bestgraph plus Endpopulation, Deduplikation nach gespeicherter Klasse,
Sortierung (W,L1,state), erste 16. Die Klassen werden beim Start neu nachgerechnet.
Je Bank genau 16 Isomorphieklassen, alle HoG-abstämmig; fünf Klassen gemeinsam.
Keine künstliche Angleichung der unterschiedlichen Fitnessverteilungen.
Vergleich konkreter Populationen, kein isolierter Vergleich zweier Gründer,
kein Nachweis unabhängiger Suchbecken. Alle vier Wiederholungen einer Bank erhalten
identische Anfangsindividuen und unterschiedliche neue Seeds; keine Checkpoint-Fortsetzung.
FRONTIER_BANKS.json enthält vollständige Kandidaten samt Hash der Quellresultate.
Das ZIP enthält alle benötigten Graphen und benötigt keine alten Laufverzeichnisse.

## Suche und Budget

P: vorhandene Apex-/Pivot-Perturbation, Längen 2–4 / 5–12 / 13–32 mit bisherigen
Gewichten 4:3:2, danach bisheriger lokaler Abstieg. Zielfunktion lexikographisch
(W,L1). Population, Elternwahl, Selektion und Operatorimplementierung unverändert.
Kein PCesc im produktiven Plan, kein Crossover, keine Sprungmutation, keine Migration.
L1/F/Linf-Normrekorde und Nmax werden wie bisher gespeichert.

Messpunkte: 3600, 7200, 14400 CPU-s. Kein Plateau-Abbruch dazwischen.
32 Such-CPU-h plus höchstens 1 Hilfs-CPU-h: clocks 540 s, controls 1260 s,
infrastructure 1800 s. Darin kurze Hostproben mit 1 und 8 Workern à 60 CPU-s.
Acht gleichzeitige Suchworker, jeweils 1 GiB Adressraumlimit, vorhandene RAM-/Disk-
und CPU-Host-Schutzmaßnahmen. Fünf CPU-s Schlussreserve je Job zählen zum Budget;
ein kleiner Teil bleibt dadurch ungenutzt. Kein stilles Wiedervergeben geschlossener Reserven.

Erwartung: etwa 4–5 Stunden reale Laufzeit plus kurze Prüfungen, keine Erfolgszeitgarantie.
Status alle 10 Minuten, Hostzeit aus persistentem Windows-Monotonzähler.
Wiederaufnehmbare Checkpoints. Diagnosepflicht bei technischen Störungen.

## Start und Daten

ZIP lambda_frontier_1_0_0.zip unter ~/conway99_workspace entpacken.
start.py mit ~/conway99_workspace/venvs/memetik/bin/python ausführen:
prepare → check → launch. Keine Überschreibung bereits vorhandener Verzeichnisse.
Neuer Lauf: ~/conway99_workspace/ryzen_lambda_frontier_100_20260924.
CLI: status, pause, launch (Wiederaufnahme), evaluate, export.
Die Endauswertung nennt Start-/Enddifferenzen, Rekordzeiten, Klassen, Normrekorde,
CPU-Verbrauch und die vorher festgelegte Budgetentscheidung.

## Tests

TEST_RESULTS.json enthält reale kurze Suchworker: Pause, Wiederaufnahme,
Budgetverlängerung im Test, Manipulationsnegative und Lösungssicherung.
Ein separater Acht-Job-Test prüft Banken, Seedzuordnung, gleichzeitigen Start,
Endauswertung, Entscheidungskategorien und Ablehnung veränderter Budgets.
Windows-Host und Ressourcen sind in den lokalen Tests ausdrücklich Fixtures;
der echte Hosttest wird beim Start auf dem Ryzen durchgeführt.
