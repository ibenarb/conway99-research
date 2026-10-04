## Crosscheck ROOT8105-Census 1.0.0 (Commit 948f252)

**Zugriff:** Die direkte GitHub-Webseite war für mich gesperrt. Den fixierten Commit konnte ich aber vollständig über codeload laden. Die SHA256-Prüfsummen aller Paketdateien stimmen mit `SHA256.json` überein. Gelesen habe ich alle Quellen, die Prüfberichte und beide Rohbelegarchive. Danach habe ich eigene Tests mit echten Prozessen gefahren, ausschließlich im Testmodell bzw. in Kopien. Es wurde keine Produktionskampagne gestartet.

**Grenzen meiner Prüfung:** Die Sandbox hat 1 CPU und kein WSL/Windows. Den Windows-Zeitmesser habe ich mit Attrappen für `wslpath` und `powershell.exe` simuliert. In einer Kopie wurde dafür nur die WSL-Erkennung erzwungen, der übrige Code blieb unverändert. Eine breitere unabhängige Zählerkontrolle habe ich gestartet, ihr Ergebnis aber nicht mehr auswerten können. Ich beanspruche sie daher nicht.

### Kurzurteil

Die Mathematik ist nach meiner Prüfung tragfähig. Gegen die Counts selbst habe ich keinen Befund. Die Schwächen liegen im Betrieb unter Fehlerbedingungen:

- Der WSL-Zeitmesser kann den Lauf abbrechen oder dauerhaft blockieren.
- Nach jedem harten Absturz gibt es keinen Wiederanlaufweg.
- Die Startprüfung erkennt nicht alle inkonsistenten Datenbankzustände.

**Urteil: nach Korrekturen freigeben.**

### Befunde

**H1 – Hoch: Fehlstart des Zeitmessers blockiert den Lauf dauerhaft.**

- *Ort:* `census.py`, `run_campaign`, Z. 177–183. `wslpath` und `Popen(powershell.exe)` laufen *nach* dem Session-INSERT (Z. 165–167), aber *vor* dem `try`.
- *Folge:* Jede Ausnahme hinterlässt eine offene Sitzung. Jedes spätere `run` wird mit `UNCLOSED_SESSION` verweigert.
- *Reproduziert:* PATH ohne `powershell.exe` ergibt `FileNotFoundError` und `open_sessions=1`. Der Neustart wird auch dann verweigert, wenn der Helfer wieder verfügbar ist.
- *Reale Auslöser:* Interop aus, `appendWindowsPath=false`, Gruppenrichtlinie oder Virenscanner.
- Das widerspricht der README-Zusage „Clock-Helferfehler blockieren keine Zählung“.

**H2 – Hoch: Jeder Lesefehler der Zeitmesserdatei bricht den gesamten Lauf ab.**

- *Ort:* `census.py`, Z. 283–290. `exists()`, `read_text()`, `json.loads` und der Schlüsselzugriff stehen ohne eigenes try. Ein Fehler landet im `except BaseException`.
- *Folge:* `CONTROLLER_ERROR`, alle Worker erhalten SIGTERM, kein Export.
- *Reproduziert:* Ein einziger ungültiger JSON-Schreibvorgang führte zu `CONTROLLER_ERROR`. Ein Neustart funktioniert danach.
- *Plausible Auslöser:* Das Überschreiben mit `Move-Item -Force` ist unter Windows PowerShell 5.1 nach meinem Kenntnisstand nicht atomar (auf dem Ryzen verifizieren). Dazu kommen Encoding- oder Locale-Effekte (de-DE).
- Das TOCTOU-Fenster zwischen `exists` und `read` konnte ich in 9143 Lesevorgängen nicht treffen. Es bleibt theoretisch.

**H3 – Mittel/Hoch: `host.wait()` ohne Timeout (Z. 334).**

- *Folge:* Beendet sich der Helfer nicht, hängt der Controller nach getaner Arbeit unbegrenzt. SIGTERM setzt nur ein Flag.
- *Reproduziert:* Alle Roots waren fertig, der Controller lief nach 20 s und nach SIGTERM weiter. Nach kill blieb die Sitzung offen und der Lauf war blockiert.

**H4 – Hoch (Betrieb): Kein Wiederanlaufweg nach hartem Absturz.**

- *Auslöser:* SIGKILL oder OOM des Controllers, `wsl --shutdown`, Windows-Update-Neustart, Stromausfall, sowie H1 und H3.
- *Folge:* Der Lauf bleibt dauerhaft gesperrt. `inspect-crash` listet nur DB-Zeilen und liest weder `output.json` noch `worker_cpu_s` noch die Hostuhr.
- GC-15 verlangt ausdrücklich, neue Konten anzulegen und fertige Aufgaben zu übernehmen. Umgesetzt ist nur die Sperre.
- *Reproduziert:* Die DB-CPU offener Versuche war 0.0, real waren es 0.37 s bzw. 2.58 s laut `output.json`.
- Die 5-s-Kontrollpunkte werden nach einem Absturz von keinem Codepfad genutzt. Bei rund 10 s pro Root ist das unerheblich.

**M1 – Mittel: PDEATHSIG-Startrennen.**

- *Ort:* `worker.py`, `main`, Z. 24–27. `parent = os.getppid()` wird erst beim Start gelesen.
- *Folge:* Stirbt der Controller während des Interpreterstarts eines Workers, ist der Elternprozess schon init. Die Prüfung greift dann nicht.
- *Reproduziert:* Bei Abschuss direkt nach dem Spawn lief der Worker unbeaufsichtigt bis `COMPLETE` (83 Ziele). 2.58 s CPU blieben ungebucht. Bei Abschuss mitten im Root funktioniert der Mechanismus (`STOPPED_PARTIAL` nach 0.1 s).
- *Fix:* Controller-PID und -Identität per spec übergeben und nach `prctl` vergleichen.

**M2 – Mittel: `audit_start` übersieht verwaiste RUNNING-Roots.**

- *Problem:* Ein Root im Zustand RUNNING ohne offenen Versuch passiert die Prüfung. Er wird nie wieder eingeplant, weil nur PENDING in die Warteschlange kommt.
- *Folgefehler:* Die Zensusphase endet mit Exitcode 0 als `CALIBRATION_COMPLETE` (Z. 340–342). Das ist ein Fehllabel.
- *Reproduziert* mit genau dem Rissmuster der fehlgeschlagenen Cloud-DB.
- *Fix:* Invarianten prüfen. RUNNING muss genau einem offenen Versuch entsprechen, DONE einem Ergebnis mit COMPLETE-Beleg, `latest_state` dem Sitzungsstatus. Ein unvollständiger Zensus braucht einen eigenen Endstatus.

**M3 – Mittel: Speicherort und Zugriff von außen sind ungesichert.**

- *Problem:* Nichts prüft, dass RUN_DIR auf lokalem ext4 liegt. WAL mit `-shm` ist über 9P, DrvFs oder Sync-Dateisysteme unsicher.
- Fremdzugriffe von Windows über `\\wsl.localhost` sind ein reales Risiko, etwa DB-Browser, Backup, OneDrive oder Virenscanner.
- *Reproduziert:* Eine externe Schreibsperre von 45 s ließ den Controller nach 30 s mit `database is locked` abbrechen. Er hat sich danach sauber erholt.
- *Fehlerisolation:* Fehler beim Live-Lesen von Worker-Checkpoints (Z. 233–236) sind ebenfalls global fatal statt isoliert. Nicht reproduziert, auf ext4 unwahrscheinlich.

**Niedrig:**

- Der Fatal-Handler übernimmt keine Teilzählungen (Z. 328). Die CPU bleibt aber gebucht.
- Ein Worker, der zwischen `Popen` und dem DB-INSERT verwaist, bleibt unverbucht.
- Der Budget-Prompt wird beim Neustart mit offener Anfrage nicht erneut ausgegeben.
- Die ETA zieht laufenden Fortschritt nicht ab (GC-11). Bei 10-s-Roots ist das irrelevant.
- `filters.MODEL` unterscheidet nicht zwischen LD-only, CAP-only und beiden zusammen.
- `filters.py` gehört zum Zensus-Fingerprint. Filterentwicklung im selben Verzeichnis sperrt das Resume (fail-closed), sollte also in einer Kopie stattfinden.

### 1. CPU-Abrechnung

Doppelzählungen habe ich keine gefunden:

- Worker werden einmal per `wait4` erfasst. Die `/proc`-Livewerte werden am Ende ersetzt.
- Hilfsarbeit wird als `RUSAGE_CHILDREN` minus geerntete Worker-CPU gebucht.
- Die Windows-PowerShell-CPU ist sauber vom Linux-Interop-Shim getrennt.
- Preflight und Export werden je einmal gebucht.
- Die Integrationssumme stimmt: 669.42 + 2.59 + 65.19 = 737.2 s.

Lücken bestehen nur in Fehlerfällen (H4, M1, Popen/INSERT-Fenster) und in den deklarierten Nachläufen. Livewerte sind Untergrenzen, höchstens 1 s alt. Die Interop-Linux-CPU kommt erst am Sitzungsende hinzu.

### 2. GC-19

Die Logik ist korrekt:

- Es gibt keine blockierende Eingabe.
- Pro Schwelle existiert genau eine Anfrage, und die Lesereihenfolge (Anfrage vor Budget) ist rennfest.
- Acht *gleichzeitige* Antworten ergaben genau einmal EXTENDED und siebenmal ALREADY_PROCESSED.
- Die Eingaben `-5`, `+5`, `1e3`, ` 7`, `5.0` und Vollbreiten-`０` werden alle als ungültig abgewiesen, der Lauf geht weiter. Eine falsche Run-ID wird abgewiesen.
- Nach einer Verlängerung entsteht die neue Anfrage korrekt. `0` stoppt an der nächsten Zielgrenze.

Anmerkungen:

- Der Preflight ruft `budget_tick` auf der Produktions-DB auf. Bei 48 h ist das harmlos.
- **Hochrechnung:** Typmittel 10.19 / 11.57 / 8.67 s bei 7418 / 630 / 57 Roots ergeben etwa 23 CPU-h (Cloudtempo). Die Meldeschwelle wird im Produktionslauf also voraussichtlich nie erreicht. GC-19 ist dann nur synthetisch geprüft.

### 3. Persistenz und der Befund 66 → 64

Die atomare Übernahme ist korrekt. Versuchsbeleg, Root=DONE und Ergebnis stehen in einer Transaktion, mit Primärschlüssel und WAL plus `synchronous=FULL`.

**Forensik des fehlgeschlagenen Laufs** (`development_evidence.tar.gz`):

- Die DB enthält `latest_state=CALIBRATION_COMPLETE` und `helper_cpu_<session>`. Beide werden in *derselben* Transaktion geschrieben wie das Sitzungsende (Z. 346–353).
- Trotzdem steht die Sitzung noch auf RUNNING, mit CPU 2.7377 statt 2.7625 am Ende. Die Roots 20 und 36 sind RUNNING, es gibt 64 Ergebnisse.
- `auxiliary_cpu_s` hat bereits den Wert *nach* dem Export, also aus einer noch späteren Transaktion.
- `integrity_check` meldet `ok`. Die Datei ist also strukturell gesund, aber eine Mischung aus Seiten verschiedener Zeitpunkte: die Meta-Seiten 3 und 209 sind neu, Sessions-, Attempts- und Results-Seiten alt.
- Auch `attempts/fe2df7e2…output.json` (Root 36) liegt als veralteter Zwischenstand vor (RUNNING, 73 Ziele). Das später geschriebene `census.jsonl` enthält Root 36 dagegen vollständig.

Weder SQLite noch die Transaktionsgrenzen des Codes können diesen Zustand erzeugen. Die Belege stützen daher stark eine inkohärente Datei-Synchronisation und keinen Controllerfehler. Das ist deutlich mehr als eine bloße „Arbeitshypothese“. Ergänzend gezeigt: Eine Kopie von `run.sqlite` ohne `-wal` während des Laufs zeigte 0 statt 6 Ergebnisse, bei `integrity_check ok`.

**Was der Wiederholungslauf absichert:** Auf lokalem Dateisystem werden 66 Ergebnisse mit exakten `wait4`-Belegen geschrieben, die Sitzung geschlossen, das Audit beim Neuöffnen bestanden, und nichts wird neu berechnet.

**Was er nicht absichert:** Das „Resume“ war ein Neustart *nach* Abschluss; die zweite Sitzung dauerte 1 ms. Nicht geprüft sind:

- Unterbrechung mitten im Root mit echtem Kern
- Absturz
- WSL und der Zeitmesser
- die Zensusphase
- `--retry-errors`
- der Prompt unter Last

**Offene Restrisiken:** Die Ursache ist für jene Umgebung nicht bewiesen. M2 bleibt bestehen. Auf dem Ryzen entsteht das Risiko vor allem durch Zugriff, Kopie oder Backup von Windows aus während des Laufs.

### 4. Mathematik

- **Übereinstimmung mit historischem F:** Die Reduktion in MATHEMATIK.md ist korrekt. In Tiefe 1 sind die beiden Typ-1-Nachbarn isoliert, und die Typ-0-Nachbarn brauchen ein perfektes Matching. Dafür bleiben 10 bzw. 8 Knoten, also immer gerade Anzahl, und es gibt keine weiteren Kopplungen. Für t∈N(u) vom Typ 0 ist die Sterngleichung identisch mit der Paargleichung k=1.
- **Overflowbeweis:** Korrekt. Jede Zelle zählt disjunkte Teilmengen mit höchstens 12 Kanten, also gilt B7 = 134 744 793 483 572 < 2^63−1. Die m11-Sperre greift.
- **Uniformsampler:** Die Bijektion ist strukturell korrekt, `randrange` arbeitet exakt. Bei m7 wurden aber nur 24 Ränge und nur das Ziel (0,8) geprüft. Im Zensus wird der Sampler nicht verwendet.
- **Filter:** LD (aus λ=1) und CAP (lo ≤ Soll ≤ hi) sind korrekt als notwendige Bedingungen begründet. Die Modellkennung ist vom Zensus getrennt, aber nicht nach LD und CAP aufgeschlüsselt.
- **Provenienz:** Die „Reviewerwerte“ stammen aus `width_dp.py`, dem direkten Vorfahren von `kernel.py` (siehe dessen Docstring). Die 249 bzw. 747 Treffer sind daher Regression innerhalb derselben Algorithmusfamilie, keine unabhängige Prüfung.
- **Unabhängige Belege:** Unabhängig sind die SAT-Abgleiche bei m ≤ 5 und die Totale des Vertexzählers. Ich habe `validate.py` vollständig nachgefahren (PASS). Stichprobe Root 1 mit den Zielen 1, 6, 22, 42 und 83: Kern, Vertexzähler und Fixture stimmen überein.
- **Empfehlung:** Eine Stichprobe von ca. 2 % aller Counts mit dem Vertexzähler (rund 0.2 s pro Ziel, etwa 45 CPU-min) nachzählen, als getrenntes Verifikationsmodell.

### Notwendige Korrekturen

Jede Korrektur ändert den Fingerprint. Ein mit 1.0.0 begonnener Lauf ist danach nicht fortsetzbar. Deshalb erst korrigieren, dann kalibrieren.

- **K1:** Den Zeitmesserstart in das try verlegen, Fehler abfangen, ETA dann `unknown`.
- **K2:** Jeden Hostuhr-Lesevorgang absichern und den letzten gültigen Wert behalten.
- **K3:** `host.wait(timeout)`, dann terminate/kill und den CPU-Wert als Untergrenze markieren.
- **K4:** Einen Befehl `reconcile-crash` einführen. Er soll: 
  - prüfen, dass der Lock frei ist bzw. die Boot-ID wechselte,
  - offene Versuche mit `max(DB, output.json)` als Untergrenze schließen,
  - gültige Teilzählungen übernehmen,
  - die Sitzung als CRASHED buchen,
  - alles protokollieren und nichts löschen.
- **K5:** Audit-Invarianten aus M2 und ein eigener Endstatus für einen unvollständigen Zensus.
- **K6:** PDEATHSIG-Identitätsprüfung in `worker.py`.
- **K7:** Preflight prüft den Dateisystemtyp von RUN_DIR und testet den Zeitmesser kurz. Die README verbietet Windows-Zugriffe auf `run.sqlite`.
- **K8 (optional):** Die Niedrig-Punkte.

### Zielhardwaretests (Ryzen/WSL)

- **T1:** `host_clock.ps1` 2–3 min isoliert laufen lassen, unter de-DE. Dabei prüfen: 
  - JSON-Gültigkeit jede Sekunde
  - ob die Zieldatei bei `Move-Item -Force` kurz verschwindet
  - Drift gegenüber der WSL-Uhr
  - Reaktion auf die Stoppdatei
- **T2:** Fehlerinjektion (fehlende PowerShell, korrupte Datei, hängender Helfer) gegen K1–K3.
- **T3:** Wegwerf-Kalibrierung mit SIGTERM nach etwa 30 s, Neustart und Digest-Vergleich mit einem Referenzlauf.
- **T4:** `wsl --shutdown` während eines Wegwerf-Laufs, danach `reconcile-crash` und Fortsetzung.
- **T5:** Prüfen, ob der nohup-Prozess das Schließen des Terminals bzw. das WSL-Leerlaufende überlebt. Schlafmodus und Update-Neustarts für die Laufdauer abschalten.
- **T6:** `validate.py` ohne `--quick` und die Vertex-Stichprobe.
- **T7:** 11 Worker plus C2 laufen lassen und beobachten, ob `MemAvailable` über 2 GiB bleibt.
- **T8:** `stat -f -c %T RUN_DIR` muss ext2/ext3 ergeben.
- **T9:** Wegwerf-Lauf mit etwa 300 s Budget; Prompt, Antwort aus dem zweiten Terminal und `0` testen.

### Abschluss

**Nach Korrekturen freigeben.** Für die Ryzen-Vorabkontrolle sind K1–K5 zwingend, K6–K7 dringend empfohlen. Den Breitenzensus erst nach bestandenen T1–T5 und T8.

Mit dem unveränderten 1.0.0 empfehle ich höchstens T1 als risikolosen Diagnoselauf. Sollte doch mit 1.0.0 gerechnet werden, ist das schlimmste erwartbare Ergebnis ein blockierter oder abgebrochener Lauf, keine falschen Zahlen. Die einzige Ausnahme ist stille Unvollständigkeit nach M2, die nur bei Speicherrissen auftritt.

Weiter

Dachte 8 s nach

Ich setze bei dem offenen Punkt aus der ersten Runde an: der breiteren unabhängigen Zählerkontrolle, deren Ergebnis noch fehlte.

3 Befehle ausgeführt

Zählerkontrolle abgeschlossen: 2.490 Counts, keine Abweichung (siehe unten). Als nächsten Schritt setze ich die Korrekturen K1–K7 als getesteten Patch um, in einer Kopie des Pakets.

20 Befehle ausgeführt · 12 Notizen

## Fortsetzung Crosscheck ROOT8105 1.0.0: unabhängige Kontrolle und Korrekturkandidat

Ich habe die offene Zählerkontrolle abgeschlossen und die Korrekturen K1–K7 als Kandidat 1.0.1-rc1 umgesetzt und getestet. **Noch nicht erledigt ist der Export:** Patchdatei und ZIP habe ich nicht mehr erzeugt, die Änderungen liegen nur in meiner Sandbox. Das hole ich im nächsten Schritt nach, wenn ihr wollt.

### Unabhängige Zählerkontrolle (aus Runde 1 offen)

Insgesamt 2.490 Counts, keine einzige Abweichung, alle drei Roottypen abgedeckt:

- **Kern gegen Vertexzähler:** 6 zufällige Roots außerhalb der Fixture, je 83 Ziele, also 498 Counts.
- **Vertexzähler gegen Reviewer-Fixture:** 24 weitere Fixture-Roots, also 1.992 Counts.

Damit ist die Regression auf den Vorfahren `width_dp.py` durch einen zweiten, unabhängigen Algorithmus breiter abgesichert.

### Korrekturen im Kandidaten

Kern, Modell und Rootliste sind unverändert.

- **`runtime.py`** 
  - K2: robuster Hostuhr-Leser, der nie eine Ausnahme wirft.
  - K7: Dateisystemprüfung über `/proc/self/mountinfo`. Abgelehnt werden 9p, drvfs, Netzwerk- und FUSE-Dateisysteme.
- **`census.py`** 
  - K1: Zeitmesserstart im `try`; ein Fehler ergibt nur `HOST_CLOCK_UNAVAILABLE`.
  - K3: Helfer-Stopp mit Timeout, danach terminate/kill.
  - Fatalpfad: Worker werden ohne `ChildProcessError` geerntet, nicht abgerechnete Versuche wiederholt verbucht, Teilzählungen bleiben erhalten.
  - Fehler beim Live-Lesen sind nicht mehr global fatal.
  - Ein Worker, der zwischen `Popen` und DB-INSERT verwaist, wird sofort beendet und als Hilfs-CPU verbucht.
  - K5: neue Audit-Invarianten und der Endstatus `PHASE_INCOMPLETE` mit Exitcode 3.
  - K4: neuer Befehl `reconcile-crash`, als Trockenlauf oder mit `--apply`. Er verweigert, solange ein Lock gehalten wird oder ein Worker lebt. Abgebrochene Versuche werden als `CRASH_LOWER_BOUND` geschlossen, der Lauf trägt danach `cpu_is_lower_bound`.
  - Gerettete Ausgaben werden nach GC-15 getrennt als `salvage_*` gespeichert und **nicht** übernommen.
- **`worker.py`** 
  - K6: Abgleich mit der Controller-PID aus der spec nach `prctl`.
  - Stopprüfung vor jedem Ziel.
- **`preflight.py`** 
  - K7: Dateisystemprüfung und 12-s-Probe des echten Windows-Zeitmessers auf WSL. Die Probe warnt nur und blockiert die Zählung nicht.
  - Kinder-CPU wird vollständig über `RUSAGE_CHILDREN` erfasst.
- **README und Prüfsummen:** neuer Absatz zu Betriebsregeln und Crash-Ablauf, `SHA256.json` neu erzeugt.

Der Fingerprint ändert sich dadurch. 1.0.0-Laufverzeichnisse sind mit dem Kandidaten absichtlich nicht fortsetzbar.

### Testergebnisse

| Prüfung                                            | Ergebnis                                                                             |
| -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Prozess-Regressionstests (11 alte + 8 neue)        | 19/19 bestanden                                                                      |
| Gegenprobe PDEATHSIG-Test mit `worker.py` 1.0.0    | 3/3 schlagen fehl (Worker läuft bis COMPLETE), mit Korrektur bestanden               |
| Zeitmesser-Probe: gut / fehlt / korrupt / hängt    | PASS / UNAVAILABLE / DEGRADED (10 Lesefehler) / DEGRADED (beendet nach 3 s)          |
| Lebenszyklus mit echtem Zählkern                   | bestanden, siehe unten                                                               |
| Preflight-Durchlauf (Kopie mit 1-GiB-RAM-Schwelle) | lief bis zum Abschlussdatensatz (130,8 s CPU), Statusfeld nicht mehr einzeln gelesen |

Die neuen Prozesstests decken ab: verwaister RUNNING-Root, verwaister Worker beim Start, Absturz → Abgleich → Fortsetzung, extern gestoppter Worker, sowie die vier Zeitmesser-Szenarien.

**Lebenszyklus mit echtem Kern im Detail:**

- Pause per SIGTERM: Root 7602 behielt 65 Teilzählungen und wurde daraus fortgesetzt.
- Harter Absturz per SIGKILL: der Worker stoppte nach PDEATHSIG kontrolliert. `reconcile-crash` setzte die CPU-Untergrenze von 7,05 auf 7,4 s.
- Fortsetzung danach: alle 5 Ergebnisse stimmen mit dem Vertexzähler überein, die 54 geretteten Zählungen sind identisch.

Das deckt die Lücke ab, die der Cloud-Beleg offenließ.

**Einschränkungen der Tests:**

- Für den Kerntest musste ich einen markierten Preflight-Platzhalter in die DB schreiben, weil die Sandbox die 4-GiB-Schwelle nicht erfüllt.
- Echtes WSL und PowerShell konnte ich nicht testen.

### Offen

- Patch und ZIP exportieren.
- `VALIDATION.json` und `MATHEMATICAL_CHECKS.json` neu erzeugen.
- Die Niedrig-Punkte (K8): 
  - Prompt beim Neustart erneut ausgeben
  - ETA nach GC-11
  - getrennte Modellkennungen für LD und CAP
- Auf WSL bleibt ein bekanntes Restrisiko: terminate beendet nur den Interop-Prozess. Eine wirklich hängende Windows-PowerShell kann weiterlaufen; sie wird nur protokolliert.

### Urteil (aktualisiert)

Für 1.0.0 bleibt es bei **nach Korrekturen freigeben**. Für den Kandidaten 1.0.1-rc1 empfehle ich die Ryzen-Vorabkontrolle, sobald ihr den Patch übernommen habt. Danach den Breitenzensus, sobald T1 (Zeitmesser unter de-DE), T4 (`wsl --shutdown`, dann `reconcile-crash`), T5 (WSL-Lebensdauer) und T8 (ext4) auf dem Ryzen bestanden sind.

Weiter

Dachte 14 s nach

Ich arbeite die offenen Punkte der Reihe nach ab: zuerst das Preflight-Ergebnis vollständig lesen, dann die Niedrig-Punkte (K8), dann die Prüfbelege neu erzeugen und schließlich Patch und ZIP exportieren.

Hat einen Befehl ausgeführt

Preflight bestanden: Status PASS, Dateisystem ext4, Probe `NOT_WSL` (hier erwartet), 130,8 s CPU vollständig verbucht. Jetzt die drei Niedrig-Punkte (K8).

14 Befehle ausgeführt, datei erstellt, dateien geteilt · 5 Notizen

Die offenen Punkte sind erledigt: Die drei Niedrig-Punkte sind behoben, die Prüfbelege neu erzeugt, und Patch, ZIP und Bericht liegen vor. Eine Produktionskampagne wurde nicht gestartet.

**Was hinzugekommen ist:**

- **Offene Budgetanfrage:** Ein neu gestarteter Controller zeigt sie mit Lauf- und Anfrage-ID erneut an. Bisher stand sie nach einem Neustart nur noch in `time_request.json`.
- **ETA:** Sie zieht den laufenden Fortschritt ab und beachtet, dass ein Root nur auf einem Worker läuft. Beispiel: Ist nur noch ein Root offen, meldet die alte Formel 16 s, die neue 90 s.
- **Filter:** Jede Kombination von LD und CAP hat jetzt eine eigene Modellkennung.
- **Preflight-Ergebnis:** Status PASS, ext4 erkannt, 130,8 s CPU vollständig verbucht. Ohne WSL meldet die Zeitmesser-Probe `NOT_WSL`, was hier erwartet ist.

**Prüfungen auf dem endgültigen Code:**

- `validate.py` vollständig bestanden.
- 20 von 20 Prozesstests bestanden, davon 9 neue.
- Ein kurzer Lauf mit dem echten Zählkern und Pause per SIGTERM: Audit bestanden, Teilzählungen gesichert, Ergebnisse identisch mit dem unabhängigen Vertexzähler.

**Ablage im Repository:** Der Kandidat liegt als neues Verzeichnis `experiments/memetik/root8105_census_1_0_1rc1`. 1.0.0 bleibt unverändert, gemäß eurer Regel „Historische Pakete bleiben unverändert“. Der Bericht samt Beweisarchiv liegt unter `docs/augmentation/root8105_census_crosscheck_20261004`.

**Gegenprobe des Patches:** Ich habe ihn auf eine frische Kopie von Commit 948f252 angewendet:

- 1.0.0 ist danach byteidentisch zum Commit.
- rc1 ist identisch mit den getesteten Quellen.
- Beide Prüfsummenlisten stimmen.

**Anwenden:**

- Patch im Repository-Wurzelverzeichnis mit `git apply root8105_census_1_0_1rc1.patch`.
- Das ZIP enthält den Ordner `Conway99_ROOT8105_Census_1.0.1rc1/`. `unzip … -d ~/conway99_workspace` legt also genau das Verzeichnis an, das die README nennt.

**Was nur auf dem Ryzen geht:**

- Alles mit echtem WSL und Windows, vor allem die Zeitmesser-Tests T1 und T2.
- Absturztest mit `wsl --shutdown` (T4) und die WSL-Lebensdauer (T5).
- Ein Lauf mit 11 Workern über die 66 Kalibrierungs-Roots mit rc1.

Danach würde ich die Statusmarke in `VALIDATION.json` von `NOT_RELEASED` auf freigegeben setzen.

Dateien:

- ROOT8105_Crosscheck_Bericht_20261004.md
- root8105_census_1_0_1rc1.patch
- Conway99_ROOT8105_Census_1.0.1rc1.zip