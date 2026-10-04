# ROOT8105 Census 1.0.0 — P0/P1

Freigegeben: historische F-Breiten für alle 8105 Roots und 83 Ziele,
Betriebskontrollen sowie getrennte Entwicklung/Prüfung von LD und C(S).
Kein automatischer P2/P3-Start. Kein Vollbaum, kein Conway99-Fund,
keine formale DP-Zertifizierung. Historische Pakete bleiben unverändert.

## Inhalt und Modell

- `kernel.py`: ausschließlich Tiefe-1-Zählung des historischen F;
  kontrollierter NumPy-int64-Kantenzähler sowie unabhängiger
  Python-Ganzzahl-Vertexzähler mit exaktem Unranking/Uniformsampling.
- `historical_core.py`: byteidentischer Pilot-Encoder als Prüfvergleich.
  Seine historische Enumeration mit Zeitabbruch wird **nirgends verwendet**.
- `filters.py`: neue Modellkennung `F+LD+CAP-v1-per-state`;
  notwendige Prüfungen an konkreten Zuständen, kein verschärfter Breitenzähler.
- `census.py`, `worker.py`, `runtime.py`: produktiver Zensuscontroller.
- `validate.py`, `operations_test.py`, `preflight.py`: Kontrollen.
- `host_clock.ps1`: unabhängige Windows-Stopwatch-Messung bei WSL.

Alle Pfade werden vom Paketstandort abgeleitet. Python >=3.10, Linux/WSL,
separate venv; Abhängigkeiten in `requirements.txt`. Keine Verbindung zum
Ryzen aus der Cloud. Die Zielhardwarekontrollen werden von Ralph gestartet.

## Vorbereitung und Start: jeweils einzeln ausführen

Die folgenden Schritte sind Referenz; im Chat wird jeweils **nur ein Schritt**
gegeben und dessen Ergebnis abgewartet. Beispielverzeichnisse sind neu und
berühren Pilot, Recovery, C2 sowie andere laufende Berechnungen nicht.

1. ZIP in Windows Downloads speichern und in ein neues Verzeichnis
   `Conway99_ROOT8105_Census_1.0.0` unter `~/conway99_workspace` entpacken.
2. In WSL im Paketverzeichnis `python3 setup.py` ausführen.
3. `.venv/bin/python census.py init ../ROOT8105_Census_1.0.0_run_20261004`
4. `.venv/bin/python preflight.py ../ROOT8105_Census_1.0.0_run_20261004`
5. `.venv/bin/python census.py run ../ROOT8105_Census_1.0.0_run_20261004 --phase calibrate`
6. Kalibrierung auswerten; danach im Hintergrund vollständigen Zensus starten:
   `nohup .venv/bin/python census.py run ../ROOT8105_Census_1.0.0_run_20261004 --phase census > ../ROOT8105_Census_1.0.0_run_20261004/controller.log 2>&1 < /dev/null &`

Schritt5 berechnet 66 deterministisch ausgewählte Roots (22 je Typ, Seed
810520261004) mit allen83 Zielen. Das sind fertige Zensusaufgaben; sie werden
in Schritt6 nicht nochmals berechnet. Kalibrierung endet nach ihrem festgelegten
Aufgabenumfang, **nicht** an einem Zeitlimit. P1 bleibt bis zu8105 Roots offen.

11 Worker, höchstens ein aktiver Prozess je Root. Jeder Worker ist einthreadig.
Kontrollpunkte spätestens nach5s zwischen Zielzählungen; bei SIGTERM/SIGINT
nach Ende der gerade laufenden Zielzählung. Kein untergeordnetes CPU-/Walllimit.
Aktuelle RAM-/Diskwerte stehen in Preflight und Status. Unter2GiB freiem RAM
oder1GiB freiem Diskraum: kontrollierter Ressourcenstopp, keine UNKNOWN→UNSAT-
Umdeutung. Vorabkontrolle fordert4GiB RAM und2GiB Disk. Der C2-Prozess wird
weder gesucht noch signalisiert oder umkonfiguriert.

## Budgetentscheidung GC-19

48*3600 **aggregierte CPU-Sekunden** sind die anfängliche Meldeschwelle des
P0/P1-Laufs einschließlich erfasster Hilfsarbeit. Kein automatischer Zeitstopp.
Es gibt kein verstecktes übergeordnetes Zeitlimit.

`time limit reached. ETA HH:MM. Extend [seconds] ?`

Vor dem Prompt stehen Lauf-ID, Geltungsbereich und Verbrauch. `ETA unknown`
bedeutet fehlende belastbare Messgrundlage. Ohne Antwort, bei EOF und ungültiger
Antwort läuft die normale Aufgabenplanung weiter. Eine offene Anfrage pro
Schwelle; Speicherung in SQLite und `time_request.json`; keine Promptflut.
Antwort im zweiten WSL-Terminal, **mit den angezeigten IDs**:

`.venv/bin/python census.py answer RUN_DIR RUN_ID REQUEST_ID SECONDS`

Positive ganze Sekunden werden zum bisherigen CPU-Budget addiert. Wiederholung
mit derselben Anfrage-ID wirkt nicht nochmals. Ist auch das neue Budget bereits
verbraucht, folgt eine neue Anfrage. `0` beendet **den gesamten benannten
P0/P1-Zensuslauf** kontrolliert. Fertige und partielle Counts sowie alle CPU-
Belege bleiben erhalten. Bei normalem Gesamtabschluss schließt die Anfrage.
Statusausgaben/Antwortdatei sind Momentaufnahmen; die Datenbank entscheidet.

Nach einer ausdrücklichen0 ist ein erneuter Start ein neuer Nutzerentscheid:
`census.py resume-after-stop RUN_DIR` löst nur die Stopmarke, verändert kein
Budget und löscht keine Ergebnisse. Danach regulär `run`; bei überschrittener
Schwelle erscheint erneut eine Anfrage. SIGTERM/SIGINT ist eine kontrollierte
Pause; ein anschließendes `run` setzt ohne Sonderargument fort.

## Abrechnung, Wiederaufnahme und Grenzen

Je Versuch erfasst der Controller am Prozessende `wait4`-CPU (inklusive Import/
Nachlauf). Die Summe der einzelnen Zielmessungen wird **nicht hinzuaddiert**.
Laufende `/proc`-Werte sind vorläufig; Endbelege ersetzen sie. Supervisorzeiten
sind gemessene Prozess-CPU bis zum Abschlussbeleg, inklusive erfasster Helfer-
prozesse. Windows-Stopwatch-Helfer meldet seine eigene Windows-Prozess-CPU;
WSL-Interop-CPU wird separat als Linux-Hilfsarbeit erfasst. Preflight verbucht
seine Prozess- und `wait4`-Kinderzeiten; Installation und externe Statusabfragen
sind Vorbereitung/Bedienung außerhalb des Experimentkontos. Unvermeidlicher
Interpreter-Shutdown nach dem letzten eigenen CPU-Snapshot ist nicht gemessen.
Keine Aussage millisekundengenauer Gesamtenergie-/Host-CPU-Erfassung.

Ergebnisse werden erst zusammen mit dem `wait4`-Endbeleg transaktional als
fertig markiert. Ein Primärschlüssel je Root verhindert doppelte Ergebnisse.
Resume prüft Code-/Modell-/Rootfingerprints und alle Ergebnisdigests. Fehler
werden einzeln als ERROR gespeichert; gesunde Aufgaben laufen weiter.
`run --retry-errors` wiederholt ausdrücklich nur Fehleraufgaben und erhält
bereits gesicherte Zielzählungen. Die CPU aller Fehlversuche bleibt verbucht.

**Harter Prozess-/WSL-Absturz:** Offene Sitzungen sind kein Endbeleg.
Automatisches Weiterrechnen wird bei ungeklärter Abrechnung verweigert.
`census.py inspect-crash RUN_DIR` zeigt Sitzungen, Versuche und CPU-Untergrenzen;
die gespeicherten Dateien bleiben unangetastet. Anschließend kontierte Recovery
planen, fehlende CPU niemals als0 ausgeben. Die Version verspricht keinen
verlustfreien OS-Crash-Endbeleg. Reguläres Pause/Resume ist geprüft.

Heartbeat: eine Sekunde, Statusatomik und Datenbankabfragen; keine rekursiven
Verzeichnis-/Größenscans. Konsole ca.alle10min, zusätzlich bei Phasenabschluss.
`status.json` ist ausdrücklich eine datierte Momentaufnahme. ETA aus gemessenen
CPU-Mitteln je Roottyp und beobachtetem Parallelitätsgrad, frühestens nach60s
und mindestens3 fertigen Roots je verbleibendem Typ. Grobe Schätzung, keine
Schranke. WSL-ETA nur bei frischer, konsistenter Windows-Stopwatch-Messung;
Clock-Helferfehler blockieren keine Zählung, ETA bleibt unknown.

## Datenexport

`census.py export RUN_DIR` schreibt `census.jsonl` und `summary.json`.
Je Root:83 exakte Integer, Minimum, sämtliche minimierenden Ziele, Typ,
Stabilisator, Orbit, Root-/Modell-/Codehash. Das vollständige Ergebnis sind
672715 Counts. Summe der minimalen ersten Breiten ist **keine Vollbaumgröße**.
Archiv für Rückgabe: gesamtes RUN_DIR einschließlich SQLite, Belegen,
Kontrollpunkten, Logs und Preflight. Bei laufendem Prozess nicht einfach eine
SQLite-WAL-Datei isoliert kopieren; kontrolliert pausieren oder SQLite-Backup
verwenden. Alle abgeschlossenen Aufgaben und historischen Versuche erhalten.

## Wissenschaftliche Kontrollen

`validate.py OUTPUT.json` zählt endliche kleine SAT-Projektionen vollständig,
vergleicht sie mit zwei verschiedenen DP-Verfahren und prüft exhaustive
Rangbijektionen. Drei m7-Roots werden mit je83 historischen Reviewerwerten
verglichen; zusätzlich drei unabhängige Vertexzahlen und24 konkrete m7-Zeilen
gegen historische F-SAT. BvLS wird als voller243er-Graph rekonstruiert und über
alle Paarzahlen geprüft;12 Präfixe testen beide Filter. Das ist kein99er-Fund
und keine freie BvLS-Completion-Messung.

`operations_test.py OUTPUT.json` prüft echte parallele Prozesse mit separatem
Testmodell: Weiterarbeit/Planung bei offener Anfrage, EOF, ungültige Antwort,
positive Verlängerung genau einmal, erneute Schwelle,0, Pause/Resume,
Anfragefortbestand beim Neustart, lokaler Workerfehler und Crash-Abrechnungssperre.
Synthetische Counts können wegen eigener Modellkennung und Paketmanifest nicht
als produktiver Zensus fortgesetzt werden.
