# Conway99 λ – Ryzen-Folgeprogramm 1.0.0

Dieses vollständige Quellpaket setzt den am 22.09.2026 akzeptierten Vorschlag um.
Es startet beim Herunterladen oder Entpacken keine Berechnung.

## Festes Experiment

| Gruppe | Jobs | Neues Suchbudget |
|---|---:|---:|
| Pext/W: vorhandene Zustände 1 → 4 CPU-h | 12 | 36 CPU-h |
| PC/W: neue Starts mit ursprünglichen 16 Gründern | 12 | 48 CPU-h |
| TCx/W: vorhandene Seeds 00–02, 1 → 4 CPU-h | 3 | 9 CPU-h |
| Rekord W: drei gepaarte P/PC-Seeds ab W=2114 | 6 | 12 CPU-h |
| Rekord Linf: P ab (2,216,2468) | 4 | 8 CPU-h |
| Rekord L1: P ab 2388 | 2 | 4 CPU-h |
| **Suche** | **39** | **117 CPU-h** |

Weitere Kontingente: 0,95 h Uhrenprobe, 1,05 h Kontrollen, 1 h Archivernte,
1 h Infrastruktur. Insgesamt 121 neue CPU-h. Maximal 18 Worker, keine
automatische Verlängerung. Alte CPU-Zeit wird nicht nochmals als Guthaben benutzt.

PC verwendet P unverändert, außer dass der vollständige Dreierzyklus in
Perturbation und Abstieg verfügbar ist. Die originalen 0.2.0-Quellen werden nicht
editiert. Pext und TCx starten die originalen Worker aus einer geprüften Kopie.
Rekordstarts sind von den Methodenvergleichen getrennt.

## Umgebung

Nur Ryzen/Ubuntu unter WSL2, gleicher Python-/pynauty-Stand wie im Originallauf.
Bekannter Pythonpfad: `/home/rb/conway99_workspace/venvs/memetik/bin/python`.
Bekannter Originallauf:
`/home/rb/conway99_workspace/ryzen_lambda_compare_020_20260921`.

Das ZIP enthält alle benötigten eigenen Pythonquellen, fixierten Originalquellen,
Gründer, Rekordgraphen und Manifeste. pynauty 2.8.8.1 muss wie im Originallauf
installiert sein. Installation von Paketen oder Systemkonfigurationen erfolgt
nicht automatisch.

Die Standardeinstellung liest den Originallauf nur. Sie verlangt dessen ruhenden,
vollständigen Ein-Stunden-Endpunkt und die veröffentlichten Receipt-Hashes.
Abweichende Dateien oder unvollständige CPU-Abrechnungen führen zu einer Diagnose,
nicht zum stillen Neubeginn.

## Bedienung – Aktionen

Einstieg ist `experiments/memetik/lambda_followup_1_0_0/run.py` unter dem
entpackten Hauptverzeichnis. Manuelle Befehle werden Ralph einzeln gegeben.

| Aktion | Wirkung |
|---|---|
| `prepare RUN --source ORIGINAL` | Verifiziert Paket, Umgebung, Originalzustände und Speicherreserven; erzeugt separate Kopien und feste Jobs. Kein Suchstart. |
| `check RUN` | Reale Windows-/WSL-Uhrenprobe mit einem und 18 Workern, mathematische/PC-Kontrollen, 120-CPU-s-Wiederaufnahmeprobe einer Kopie. Ergebnis READY_NOT_STARTED. |
| `launch RUN` | Startet den vorbereiteten Controller im Hintergrund; bleibt unabhängig vom geöffneten Terminal. |
| `status RUN` | Zeigt aktuellen Status und ETA. |
| `pause RUN` | Sendet nur dem eigenen, anhand PID und Startzeit geprüften Controller ein Pausensignal. |
| `launch RUN` nach sauberer Pause | Setzt dieselben Jobs mit Restbudget fort; keine neuen Seeds. |
| `evaluate RUN` | Prüft Endgraphen, CPU-Abrechnungen, Kurven, alte Messpunkte und P/PC-Paarvergleich. |
| `export RUN` | Erstellt nach Prüfung ein vollständiges tar.gz plus SHA256; überschreibt kein vorhandenes Archiv. |

`run RUN` ist der interne Vordergrund-Controller. Für den normalen Start ist
`launch` vorgesehen. Es gibt kein pauschales `extend`, keinen frei wählbaren
Jobhorizont und keine stille Budgeterhöhung.

## Status und erwartete Laufzeit

`controller.log` und `status.json` enthalten alle zehn Minuten Fortschritt,
Bestwerte getrennt nach Suchgruppe und Ziel, neue verbrauchte CPU-Zeit und eine
Budget-ETA. Die Hintergrundausführung schreibt ins Log; sie erzeugt keine
automatischen Chatnachrichten. Diagnosephasen melden zusätzlich ihren Beginn und
Abschluss. Originale Verbesserungs- und Checkpointprotokolle bleiben erhalten.

Die idealisierte Belegung beträgt sieben Stunden Suche. Vor realer Kalibrierung
sind 7–10 Stunden Suche plus Kontrollen, Einrichtung und gegebenenfalls Archivernte
eine vorsichtige Planung, keine Garantie. Der erste Uhren-/Kontrollschritt dürfte
typischerweise etwa 10–20 Minuten benötigen; der eigentliche Rechnerdurchsatz ist
hier nicht gemessen.

## Zeitbasis, CPU und Datenintegrität

Ein fortlaufender Windows-PowerShell-Prozess liefert monotone Hostintervalle,
UTC, eigene Prozess-CPU und die freie Kapazität des tatsächlichen VHDX-Trägervolumens.
Seine native Windows-CPU sowie Linux-Interop-CPU werden dem Infrastrukturledger
zugeordnet. Gastuhren werden parallel protokolliert. Ein positiver lokaler Test
dieses Pakets ersetzt keine echte Prüfung auf Ryzen.

Suchbudgets werden im Worker über getrusage geprüft; nur wait4 beendet und rechnet
Workerprozesse im Controller ab. RNG-Zustände, Katalogpräfixe und Archive bleiben
bei Wiederaufnahme erhalten. Replay kostet reale CPU innerhalb des Budgets.
Geschlossene Abschlussreserven alter Messpunkte werden nicht erneut verwendet.

Die Startbanken bleiben fixiert. Die lesende OBSERVED-Ernte erfolgt nach den
Suchjobs und vor dem abschließenden Export, damit sie deren CPU-/SMT-Vergleich
nicht beeinflusst. Sie verändert keine Starter. Unter ihrem eigenen
Ein-Stunden-Kontingent prüft sie Datensätze, führt strikte zielbezogene Abstiege
aus und untersucht – soweit vollständig möglich – die zehn besten verschiedenen
beschrifteten W-Endpunkte in Tiefe zwei. Unvollständige Arbeit wird ausdrücklich
als INCOMPLETE gemeldet. Suchendpunkte werden schon vor dieser Zusatzdiagnose
in EVALUATION.json gesichert.

An jedem Erfolgspfad werden λ-Gültigkeit und Nullresiduen geprüft und der Zeuge
zweifach gesichert. Globale Lösungserkennung umfasst beide Suchwurzeln sowie die
nachgelagerte Archivernte. Nur eigene Worker werden kontrolliert gestoppt.

## Ressourcen und Fehlerfälle

Schutzwerte: 1 GiB Adressraum je Worker, 36 GiB eigene Prozessgruppe,
6 GiB freier RAM, 20 GiB freie Linux-Platte, 50 GiB frei auf dem real ermittelten
Windows-VHDX-Volume. Vor den Archivkopien wird auch deren Platzbedarf berücksichtigt.

Es gibt keine Löschung alter Daten, keine Veränderung von Office-Prozessen,
keine pauschale Archivverdrängung nach 64 Klassen und keinen Plateau-Stopp.

Ein ungültiger Checkpoint, ein fehlender Receipt, eine Zeitinkonsistenz oder ein
anderer technischer Fehler wird sichtbar gespeichert. Aktive Marker ohne
abschließenden Receipt werden nicht durch bloßes Neustarten entfernt. In solchen
Fällen zuerst den Fehlerbericht auswerten. Erneute verbrauchte Hilfs-CPU wird
weitergezählt; ein Kontingentüberschreiten wird nicht durch Rücksetzen des Ledgers
oder heimliches Übertragen von Suchbudget verdeckt.

## Dateien

- `pc_engine.py`, `pc_worker.py`: schmale PC-Erweiterung.
- `prepare.py`: Paket-/Quellenprüfung und sichere selektive Kopien.
- `coordinator.py`: gemeinsamer Scheduler, Ressourcen, Lösungen und Receipts.
- `host.ps1`, `clock.py`: persistente Hostmessung und Uhrenprobe.
- `checks.py`, `integration_tests.py`, `infrastructure_tests.py`: Kontrollen.
- `harvest.py`, `evaluate.py`: Zusatzdiagnose und Ergebnisauswertung.
- `PACKAGE.json`: SHA256 aller ausgelieferten Nutzdateien.
- `SOURCE_PINS.json`: unveränderte 46 Referenzdateien.
- `docs/memetik/lambda_synthesis_20260922/`: exaktes Manifest und Rekordbank.

Die produktiven Windows-/WSL-Prüfungen und die originale Ryzen-Wiederaufnahmeprobe
sind beim Ausliefern noch nicht durchgeführt. Ohne sie wird kein Suchlauf gestartet.
