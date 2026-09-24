# Lambda decision 1.0.0 — V2 und unveränderte V3-Fortsetzung

Freigegeben am 24.09.2026 nach Review des verworfenen 864-CPU-h-Hauptlaufs.
Kein neuer Hauptlauf, keine Sprungmutation, kein Crossover, keine geänderte Selektion.

## Vorab festgelegte Aufgaben und Entscheidung

- V2: W=2102 / 2107 / 2108, je zwei neue Seeds, je 7200 CPU-s: 12 CPU-h.
- V3: alle acht bestehenden P-Jobs von 7200 auf 28800 CPU-s: 48 zusätzliche CPU-h.
- 14 Worker starten gleichzeitig. Nach V2 verbleiben acht V3-Worker.
- V2 positiv: mindestens ein adoptiertes best.W < 2102. Alle sechs Start-/Enddifferenzen und Median werden berichtet.
- V3 positiv: mindestens ein adoptiertes best.W < 2150. Alle acht Endpunkte und Kurven werden berichtet.
- Beide negativ: aktuelle Strategie pausieren. Positiv: Signal bewerten, KEIN automatischer Folgelauf.
- Einzelne Treffer beweisen keine Überlegenheit; negative Ergebnisse keine Erschöpfung oder Nichtexistenz.
- V2 besitzt keine gleichzeitige Gründerkontrolle: Test der Frontier-Produktivität, kein kausaler Seeding-Vergleich.

## Exakte V2-Bank

Für 2102/2107/2108 werden R-P--W-02 / R-P--W-00 / R-P--W-01 aus dem
Folgelauf vom 22.09.2026 verwendet. Jeweils Bestgraph plus Endpopulation,
Deduplikation nach Isomorphieklasse, Sortierung (W,L1,state), erste 16.
Die Bestmarke ist damit tatsächlich enthalten. Alle 48 Bankplätze sind HoG-abstämmig;
16 Klassen pro Bank, keine Behauptung globaler Unabhängigkeit zwischen Banken.
Beide Wiederholungen verwenden dieselbe Bank, Seeds 2026092600 bis 2026092605.
FRONTIER_BANKS.json enthält vollständige Graphen, Herkunft und Quellresultat-Hashes.
Population 16, Ziel W mit bestehendem L1-Tiebreaker, exakt bisheriger P-Operator.

## Echte V3-Fortsetzung

Quelllauf: ~/conway99_workspace/ryzen_lambda_prechecks_100_20260924.
Archiv SHA256: 6a251f5f63eb56dde7b77e8b0460cee5d7aee3eee8c8a5035df09d9bb1928abd.
Die Quelle wird nur gelesen und muss abgeschlossen sein. Fingerprint und die fünf
zentralen Dateien jedes V3-Jobs werden gegen SOURCE_RUN.json geprüft.
Aufgaben, Receipts, Populationen, Archive, RNG, teilweise enumerierte Kataloge und
laufende Episoden werden kopiert. Keine Umsaat, keine Auswahl erfolgreicher Replikate.
Historische Checkpoints/Resultate/Receipts werden zusätzlich unveränderlich archiviert.

worker.py unterscheidet sich vom getesteten Vorprüfungsworker in genau einer
Anweisung: auch isolierte Jobs lesen ihre Laufzeitgrenze aus der externen budget.json.
Dadurch bleiben task.json und Suchcheckpoint byteidentisch; nur das externe Budget
steigt. Bereits geschlossene Reserven werden nicht neu vergeben. Alte Kurven,
Messpunkte und CPU-Sitzungen müssen in der Abschlussprüfung unverändert enthalten sein.

## Ressourcen und Start

60 zusätzliche Such-CPU-h, maximal 2 CPU-h für notwendige Uhr-/Eingangsprüfungen
und Infrastruktur. Kein Mehrverbrauch durch automatische Verlängerung.
Bewährte Windows-Host-Uhr; kurze 1-/18-Worker-Proben vor dem Lauf.
Eigentliche Suche: 14 Worker, später 8; 1 GiB Adressraumlimit pro Worker.
Speicher-/Host-Disk-/CPU-Uhrfehler pausieren nur eigene Prozesse.
Mindestens sechs Stunden Such-Walltime, vorsichtig etwa 6–8 Stunden plus Vorprüfung.
Status alle 10 Minuten. ETA aus längstem Restjob und zuletzt gemessener Worker-Effizienz.
Keine Erfolgszeitprognose. Keine Plateau-Abbrüche vor den festgelegten Endpunkten.
Verifizierte exakte Lösung stoppt die Kampagne und wird doppelt gesichert.

ZIP unter ~/conway99_workspace entpacken und start.py mit dem bestehenden
venvs/memetik/bin/python aufrufen. start.py: prepare → check → launch.
Neuer Lauf: ~/conway99_workspace/ryzen_lambda_decision_100_20260924.
Kein Überschreiben vorhandener Läufe. CLI: status, pause, launch (Wiederaufnahme),
evaluate, export. Nach technischer Störung zuerst Diagnose, kein blindes Restart.

## Validierung

TEST_RESULTS.json: echte kurze Worker mit Pause/Resume/Budgetverlängerung,
Manipulationsnegative, CPU-Receipts und Lösungshandhabung. Zusätzlich alle acht
hochgeladenen realen V3-Checkpoints plus sechs neue V2-Jobs mit kurzen Testbudgets;
alle Zustände fortgeschritten, gleichzeitiger Start, Kurvenpräfixe erhalten,
Quelldateien unverändert. Tests benutzen ausdrücklich markierte Windows-/Versions-
Fixtures; die echte Ryzen-Host-Prüfung wird dadurch nicht ersetzt.
Die Operatoren selbst sind unverändert und werden nicht nochmals lang getestet.
