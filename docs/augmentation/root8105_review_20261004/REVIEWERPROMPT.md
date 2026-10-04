# Unabhängiger Reviewauftrag: Fortsetzung des ROOT8105-Autopiloten

Bitte analysiere selbständig den abgeschlossenen ROOT8105-Piloten und die drei neuen memetischen H-Faser-Berichte. Entwickle eigene Schlussfolgerungen und einen konkreten Fortsetzungsplan. Du sollst keinen bereits vorgeschlagenen Plan bestätigen. Ralph wird Deine Antwort hier hochladen; erst nach Abgleich fällt die Entscheidung über den nächsten Lauf. Keine Ausführung eines neuen Großexperiments und keine Kontaktaufnahme mit Dritten erforderlich.

## Ziel

Wir suchen einen SRG(99,14,1,2) oder eine nachvollziehbare vollständige Ausschlussstrategie im ROOT8105-Modell. Die unmittelbare Pilotfrage war: Wie breit wachsen die Suchbäume, lässt sich vollständige Augmentation zertifizieren und passt der Aufwand auf den verfügbaren Ryzen? Unterscheide mathematische Evidenz, empirische Suchleistung, technische Korrektheit und offene Fragen.

## Quellen und empfohlene Lesereihenfolge

Beginne mit den Rohdaten und Quellständen. Formuliere einen eigenen vorläufigen Befund, bevor Du die Codex-Synthese und den Plan liest.

1. Im selben fixierten Commit/Verzeichnis wie dieser Prompt:
   - `raw/summary.json`, `raw/growth_by_depth.csv`, `raw/roots_summary.csv`;
   - `raw/receipts.json`, `raw/aux_ledger.json`;
   - originaler Nutzerexport `ROOT8105_Abschlussberichte.tar.gz`;
   - `audit_results.py` und `DERIVED_METRICS.json` zur reproduzierbaren Nachrechnung. Dieses Audit ist kein Proofchecker.
2. Pilotquellen (fixiert): https://github.com/ibenarb/conway99-research/tree/7c664ebdbf94254179b74eaa523c5bc2150054f5/experiments/memetik/root8105_pilot_1_0_1
   Besonders `core.py`, `worker.py`, `proof.py`, `completion.py`, `report.py`, Konfiguration/README und Root-/Kontrollprüfungen. Keine Gleichsetzung des Paketnamens mit einer bereits bewiesenen vollständigen Canonical-Augmentation.
3. Recovery (fixiert): https://github.com/ibenarb/conway99-research/tree/036c108dd7176909cd7f9544d48a4daa1f8da1a2/experiments/memetik/root8105_recovery_1_0_2
4. Die drei Parallelcommits vollständig lesen:
   - https://github.com/ibenarb/conway99-research/commit/efe29fd5aee3a79608f920e498a5279c6b7f4cc7
   - https://github.com/ibenarb/conway99-research/commit/01e695903f6b6d1fa400e1e73ee16611cba7a500
   - https://github.com/ibenarb/conway99-research/commit/34c3dbebf0d3748420e43abd3930f72df044e9b5
   Vollständige Dateien: `docs/memetik/H_FIBRE_INVESTIGATION_2026-10-04.md`, `results/memetik/H_FIBRE_INVESTIGATION_20261004.json`, `docs/augmentation/AUGMENTATION_PILOT_MEMETIK_HANDOFF_2026-10-04.md` am letzten dieser Commits.
5. Verbindliche Regeln (fixiert): https://github.com/ibenarb/conway99-research/blob/611be0b0bc14acf7e0dfd4dfe40db13b27487271/docs/EXPERIMENT_RULES.md und `docs/operations/GLOBAL_CONCLUSIONS.md` desselben Commits.
6. Erst nach Deiner eigenen Erstdiagnose: `ERGEBNISSE_UND_ABGLEICH.md` und `FORTSETZUNGSPLAN.md` in diesem Verzeichnis. Kritisiere sie ausdrücklich; Alternativen sind erwünscht.

Die Herkunft und genaue Dateizuordnung stehen zusätzlich in `SOURCE_INDEX.json`. Die drei memetischen Commits sind aufeinanderfolgende Dokumentationsschritte; dort berichtete Prüfungen sind keine von Dir ausgeführten Reproduktionen. Fehlende H-Zeugen/Prüfprogramme oder DRAT-Rohartefakte als fehlend benennen und konkret anfordern, nicht imaginär voraussetzen.

## Aufgaben

1. Rechne die wesentlichen Pilotkennzahlen nach. Was misst der gepaarte ordered/dynamic-Vergleich wirklich? Welche Breiten sind exakt, welche nur Untergrenzen, welche Zähler enthalten Wiederholungen? Wie repräsentativ sind Root- und Proofauswahl?
2. Rekonstruiere die mathematischen Modelle aus den Quellen. Welche Bedingungen erfüllen die memetischen H-Zeugen, welche verlangt der Augmentation-Encoder, welche erst ein vollständiger SRG? Prüfe die Übertragbarkeit der vorgeschlagenen planted controls. Gib für jeden Kontrolltyp exakt an, was garantiert positiv ist und was nicht.
3. Prüfe den Aussageumfang der lokalen DRAT-Zertifikate und die noch fehlenden Schritte bis zu einer zertifizierten Schicht oder einem Root-Ausschluss. Welche Symmetrie- und Coverage-Nachweise wären nötig? Muss echte Canonical-Augmentation implementiert werden, oder wäre eine andere vollständige Methode günstiger?
4. Welche Folgerungen aus minimalen H-Moves und lokalen Distanzlücken sind für ROOT8105 zulässig? Welche vermeintlichen Zusammenhänge wären unbelegt? Beachte unterschiedliche Zustandsräume und Maße.
5. Entscheide unabhängig, wo der nächste Erkenntnisgewinn zu erwarten ist: exakte frühe Breitenmessung, direkte SAT-/Cube-Zerlegung, stärkere notwendige Bedingungen, Completion-Kalibrierung, heuristische Tiefensuche oder ein begründet anderer Ansatz. Vergleiche mindestens die ernsthaft konkurrierenden Optionen; eine eigene Priorisierung ist erforderlich.
6. Entwickle einen ausführbaren Plan: Rootauswahl, Kontrollen, Zustandsdarstellung, Erweiterungs-/Pruningregeln, Vollständigkeit, Fortsetzbarkeit, Zertifikate, Messgrößen, Parallelisierung, Speicher-/Plattenbedarf, CPU-Meldeschwellen und Entscheidungskriterien. Trenne vorbereitende Entwicklung und echten Zielhardwaretest vom Forschungsversuch. Begründe großzügige, aber nicht blind große Ressourcen.
7. Gib erwarteten Erkenntnisgewinn, wesentliche Risiken und Änderungen am Codex-Plan an. Wo ist keine belastbare ETA möglich? Welche fehlenden Daten sind entscheidungsrelevant? Muss Nearest-H abgewartet werden, oder lassen sich unabhängige Schritte schon vorbereiten?

## Ressourcen und zwingende Nutzerregel

Ryzen, 12 physische Kerne/24 logische, bis elf Kerne für diesen Zweig; ein separater C2-Checker bleibt unangetastet. In den letzten Momentaufnahmen etwa 29–30 GB verfügbarer RAM, vor Start neu messen. Kein Hardwarekauf vorausgesetzt. Ralph bevorzugt ausreichend breite Kontrollen und großzügige Rechenbudgets.

Zeitbudgets sind Melde-/Entscheidungsschwellen, keine automatischen Abbruchgründe. Bei Erreichen:

    time limit reached. ETA HH:MM. Extend [seconds] ?

Bis zur Antwort weiterrechnen, auch bei EOF; Verbrauch vollständig buchen. 0 beendet den bezeichneten Auftrag kontrolliert, positive Sekunden verlängern dessen bisheriges Budget. ETA unknown, wenn keine belastbare Restzeit vorliegt. Hintergrundläufe brauchen einen funktionierenden dauerhaften Antwortkanal. Native Solverlimits, Watchdogs und RLIMIT_CPU dürfen die Regel nicht umgehen. Echte RAM-/Platten-/Integritätsgefahren bleiben gesondert zu behandeln. Die historische 1.0.1/Recovery bleibt als historischer Beleg unverändert.

Offene technische Prüfungen: Gültigkeit der konkreten Zeugen und Modellabbildungen, vollständige Enumeration mit Resume, geprüfte Cube-/Symmetrie-Coverage, Kosten vollständiger früher Proofs, GC-19-Implementierung samt realem WSL-/Hosttest, Skalierung des Dateibestands. Relevante GC-IDs: 01,05,08,10,11,14–19 sowie die neu vorgeschriebene GC-20-Modellkontrollregel im Commit dieses Reviewpakets.

## Gewünschte Antwort

- Eigenständiger Befund mit klarer Trennung gesichert/berichtet/vermutet/offen.
- Modell- und Beweiskettenprüfung samt konkreten Korrekturen.
- Priorisierter eigener Fortsetzungsplan mit Ressourcen und überprüfbaren Entscheidungspunkten.
- Abschließender Vergleich mit Codex: Zustimmung, Widerspruch und notwendige Änderungen, jeweils begründet.
- Liste fehlender Artefakte und tatsächlich von Dir ausgeführter Prüfungen. Kein behauptetes Rechnen ohne Ausführung.

Dein Vorschlag bleibt eine Empfehlung. Ralph und Codex entscheiden nach Rückgabe gemeinsam über Umsetzung und Laufstart.
