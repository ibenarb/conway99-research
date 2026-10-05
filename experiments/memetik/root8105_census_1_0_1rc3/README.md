# ROOT8105 Census 1.0.1-rc3 — P0/P1 (Korrekturkandidat)

Korrekturen gegenüber 1.0.0 nach externem Crosscheck vom 04.10.2026 (K1–K7):
Windows-Zeitmesserfehler blockieren nie die Zählung und hinterlassen keine offene
Sitzung (K1–K3); `reconcile-crash` als kontierter Wiederanlauf nach hartem
Absturz (K4, GC-15); zusätzliche Audit-Invarianten und Endstatus
`PHASE_INCOMPLETE` mit Exitcode 3 (K5); Worker stoppen auch bei Controllertod
während ihres Starts (K6); RUN_DIR-Dateisystemprüfung und Zeitmesser-Probe im
Preflight (K7). Mathematischer Kern (`kernel.py`, Modell, Roots) unverändert.
Neuer Code-Fingerprint: 1.0.0-Laufverzeichnisse sind damit nicht fortsetzbar.
`VALIDATION.json`/`MATHEMATICAL_CHECKS.json` sind neu für diesen Kandidaten erzeugt
(Review-Sandbox, nicht Zielhardware); Status ausdrücklich NOT_RELEASED.

Freigegeben: historische F-Breiten für alle 8105 Roots und 83 Ziele,
Betriebskontrollen sowie getrennte Entwicklung/Prüfung von LD und C(S).
Kein automatischer P2/P3-Start. Kein Vollbaum, kein Conway99-Fund,
keine formale DP-Zertifizierung. Historische Pakete bleiben unverändert.

## Korrektur rc3: Testisolierung auf WSL

rc2 fand im simulierten Fall clock-missing die tatsächlich installierte
Windows-PowerShell aus dem geerbten PATH. Das war ein Fehler des Tests.
rc3 verwendet für alle vier simulierten Uhrenszenarien ausschließlich den
jeweiligen Testpfad. Zusätzliche Regression: Eine weitere powershell.exe im
geerbten Suchpfad bleibt unerreichbar und wird nicht gestartet.

Nur operations_test.py wurde funktional geändert. Produktionscontroller,
Worker, Recovery, Hostuhrskript und Mathematik bleiben byteidentisch zu rc2.
Der neue Test verändert trotzdem den Paketfingerprint: neuen Lauf anlegen;
rc2-Verzeichnisse und den fehlgeschlagenen Preflight unverändert erhalten.
Die alten Kosten nicht als null ausgeben; vor allem enthält der fehlerhafte
Hostuhrtest keinen verlässlichen Windows-CPU-Endbeleg. Es wurden noch keine
produktiven Zensusroots auf Ryzen berechnet.

Aktuelle Belege stehen in VALIDATION.json und validation/rc3_evidence.tar.gz.
Die früheren66-Root- und Crashkontrollen gelten als rc2-Basisbelege, unter
validation/rc2_basis eindeutig getrennt; für diese reine Testkorrektur nicht
erneut als neue rc3-Rechnung ausgegeben. Reale WSL-Abnahme weiterhin offen.

## Übernommene Ergänzungen aus rc2 (05.10.2026)

- Recovery prüft Manifest, Code, Modell, Roots, Kontenverknüpfungen und CPU-Werte
  vor dem Schreiben; Trockenlauf öffnet die Datenbank nur lesend. Auch bei
  abgewiesener Recovery werden Verbindung und Controllersperre freigegeben.
- Eine RUNNING-Wurzel ohne genau einen offenen Versuch ist ein inkonsistenter
  Datenbestand: NEW_RUN_REQUIRED. Nicht durch manuelles Ändern der Datenbank
  oder reconcile-crash scheinbar reparieren. Gesamten stillgelegten Bestand
  erhalten und init mit einem anderen, noch nicht existierenden Laufverzeichnis
  ausführen. Neue Kennung und Konten; keine Übernahme ungesicherter Counts.
- Ungültige Worker-CPU (negativ, unendlich, NaN, bool oder Text) wird verworfen;
  fehlende Endabrechnung bleibt ausdrücklich eine Untergrenze.
- Worker prüfen sowohl Controller-PID als auch die Prozess-Startidentität.
- recovery_test.py ergänzt sieben Prüfgruppen und läuft auch im Preflight.

Status: Kandidat für Zielhardware-Abnahme. Weder rc1- noch 1.0.0-Läufe können
mit diesem neuen Code-Fingerprint fortgesetzt werden. Der mathematische Kern
und die Rootdaten sind gegenüber rc1 unverändert.

Die Cloud-Belege stehen in VALIDATION.json und PRUEFBERICHT.md. Sie ersetzen
keine reale PowerShell-/WSL-Abnahme. C2 nicht verändern; insbesondere kein
wsl --shutdown während C2 in derselben Umgebung läuft. Gezielte SIGKILL-Tests
betreffen ausschließlich einen eigens gestarteten wegwerfbaren Testcontroller.

## Inhalt und Modell

- `kernel.py`: ausschließlich Tiefe-1-Zählung des historischen F;
  kontrollierter NumPy-int64-Kantenzähler sowie unabhängiger
  Python-Ganzzahl-Vertexzähler mit exaktem Unranking/Uniformsampling.
- `historical_core.py`: byteidentischer Pilot-Encoder als Prüfvergleich.
  Seine historische Enumeration mit Zeitabbruch wird **nirgends verwendet**.
- `filters.py`: neue Modellkennung `F+LD+CAP-v1-per-state`;
  notwendige Prüfungen an konkreten Zuständen, kein verschärfter Breitenzähler.
- `census.py`, `worker.py`, `runtime.py`: produktiver Zensuscontroller.
- `validate.py`, `operations_test.py`, `recovery_test.py`, `preflight.py`: Kontrollen.
- `host_clock.ps1`: unabhängige Windows-Stopwatch-Messung bei WSL.

Alle Pfade werden vom Paketstandort abgeleitet. Python >=3.10, Linux/WSL,
separate venv; Abhängigkeiten in `requirements.txt`. Keine Verbindung zum
Ryzen aus der Cloud. Die Zielhardwarekontrollen werden von Ralph gestartet.

## Vorbereitung und Start: jeweils einzeln ausführen

Die folgenden Schritte sind Referenz; im Chat wird jeweils **nur ein Schritt**
gegeben und dessen Ergebnis abgewartet. Beispielverzeichnisse sind neu und
berühren Pilot, Recovery, C2 sowie andere laufende Berechnungen nicht.

1. ZIP in Windows Downloads speichern und in ein neues Verzeichnis
   `Conway99_ROOT8105_Census_1.0.1rc3` unter `~/conway99_workspace` entpacken.
2. In WSL im Paketverzeichnis `python3 setup.py` ausführen.
3. `.venv/bin/python census.py init ../ROOT8105_Census_1.0.1rc3_run_YYYYMMDD`
4. `.venv/bin/python preflight.py ../ROOT8105_Census_1.0.1rc3_run_YYYYMMDD`
   Preflight prüft zusätzlich Dateisystemtyp und startet unter WSL den Windows-
   Zeitmesser 12s probeweise (`host_clock_probe` in `preflight.json`;
   bei `DEGRADED`/`UNAVAILABLE` Warnung, ETA später unknown, Zählung unberührt).
5. `.venv/bin/python census.py run ../ROOT8105_Census_1.0.1rc3_run_YYYYMMDD --phase calibrate`
6. Kalibrierung auswerten; danach im Hintergrund vollständigen Zensus starten:
   `nohup .venv/bin/python census.py run ../ROOT8105_Census_1.0.1rc3_run_YYYYMMDD --phase census > ../ROOT8105_Census_1.0.1rc3_run_YYYYMMDD/controller.log 2>&1 < /dev/null &`

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
Ablauf, jeweils einzeln:
1. `census.py reconcile-crash RUN_DIR` (Trockenlauf, ändert nichts): zeigt
   offene Sitzungen/Versuche, CPU-Untergrenzen aus `/proc`-Livewert und
   Worker-Selbstmeldung sowie gerettete Teilzählungen. Verweigert, solange
   Controller-Lock gehalten wird oder ein Worker derselben Boot-ID noch lebt.
2. `census.py reconcile-crash RUN_DIR --apply`: offene Versuche werden als
   `CRASH_LOWER_BOUND` (cpu_exact=0) geschlossen, Sitzung als
   `CRASHED_RECONCILED` mit letzter Statuszeit; Roots zurück auf PENDING mit
   letztem Datenbank-Kontrollpunkt. Gerettete Worker-Ausgaben werden getrennt
   als `salvage_*` gespeichert und **nicht** übernommen. Der gesamte Lauf trägt
   danach `cpu_is_lower_bound=true` im Statusbefehl, Abschlussreport und Summary.
   Laufende status.json-Snapshots enthalten dieses Kennzeichen noch nicht;
   die Untergrenzenklassifikation bleibt dauerhaft in der Datenbank erhalten.
3. Danach reguläres `run`. Nichts wird gelöscht; fehlende CPU nie als 0.
Die Version verspricht keinen verlustfreien OS-Crash-Endbeleg.

**Betriebsregeln:** RUN_DIR liegt im WSL-Linux-Dateisystem (ext4 unter `~`);
`run` und Preflight verweigern 9p/drvfs/Netzwerk/FUSE. `run.sqlite` niemals von
Windows aus öffnen, kopieren, sichern oder synchronisieren (Explorer, DB-Browser,
Backup, OneDrive, Virenscanner auf `\\wsl.localhost`): SQLite-WAL braucht
gemeinsamen Speicher und erzeugt sonst veraltete oder gemischte Zustände. Status
nur über `census.py status RUN_DIR`. Externe Schreibsperren über 30s brechen den
Controller kontrolliert ab. Ein Ende mit `PHASE_INCOMPLETE` (Exitcode 3) heißt:
offene Roots vorhanden, erneut `run` starten. Zeitmesserfehler stehen als
`HOST_CLOCK_*` im Log und unter `warnings_<session>` in der Datenbank.

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
