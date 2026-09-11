# Conway 99 – memetischer Office-Pilot 0.1.0

Stand: 11. September 2026. Ausgangscommit: `15f6ce2550423ecfaf75847cfba824deecd563f3`.
Branch: `memetic/office-v0.1.0-20260911`.

## Verbindliche Grundlage

Die unveränderten Referenztexte liegen in `docs/memetic/reference/`: dritter Reviewer-Pong,
anschließende Synthese und die danach vereinbarte konkrete Parameterantwort. Bei Unterschieden
ist die spätere Synthese bzw. der nachfolgende Parameterkonsens maßgeblich, nicht eine vom
Reviewer inzwischen zurückgenommene Behauptung. Die jetzige Office-Skalierung ändert vier
Worker in drei. Population und Versuchskontingente bleiben unverändert.

Zwei getrennte Arme:

- **Omega/H84:** binär, symmetrisch, Nulldiagonale, feste Rahmenkonvention,
  H-Zeilengrad 12 und `P H = 2 J - (C + I) P`.
- **Lambda:** einfacher 14-regulärer 99-Graph, jede Kante mit genau einem gemeinsamen Nachbarn.

Beide minimieren `F = sum_{i<j} (common(i,j) + A[i,j] - 2)^2`.
Zusätzlich werden W, Residuenhistogramm, Defektgradprofil, Dreiecke und Vierzyklen gemeldet.
Ein Treffer erfordert F=0 UND eine unabhängige vollständige Prüfung sämtlicher Bedingungen.

HoG #57338 ist ein Kontrollstart des Lambda-Arms. Es wird nicht als Omega-Start ausgegeben.
Die belegte Tiefe-2-Apex-Barriere ist operatorspezifisch; drei Schritte sind notwendig,
aber ihre Hinreichendheit ist offen. Die Neunerknotenrotation ist eine zusammengesetzte
Bewegung, keine bewiesene unabhängige Erreichbarkeitsgarantie. Produktfamilien sind keine
Vollständigkeitsbehauptung über alle Omega-Trades. Ein Prisma-Defektprofil wäre ein Anlass
für weitere Prüfung, kein Lösungszertifikat; Version 0.1.0 enthält keinen Sonderdetektor dafür.

## Population und Suchvertrag

Ziel: 32 Kandidaten je Arm, vier Herkunftsgruppen mit je acht Plätzen. Herkunftsgruppen:
randomisierte exakte Konstruktion, randomisierte Konstruktion mit exakter Reparatur,
algebraische/symmetrische Konstruktion, Projektimporte und deren zulässige Ausflüge.
HoG und seine Abstammungsfamilie belegen höchstens vier Plätze. Gruppenquoten werden nicht
mit Relabelings, Familienumbenennungen oder vermeintlich verschiedenen Zufallsseeds aufgefüllt.
Pro Gruppe werden zunächst bis zu vier gute und anschließend bis zu vier strukturell
verschiedene zulässige Vertreter ausgewählt. Fehlende Starts bleiben als fehlend ausgewiesen.

Die Starterzeugung versucht pro Methode und Arm 16 vollständige endliche Aufgaben. Dazu
kommen acht zulässige Ausflüge je Referenzgraph: insgesamt 128 Aufgaben. Jede erhält ein
Budget von 30 CPU-Sekunden. Nach spätestens 45 Minuten aktiver Vorbereitungszeit werden
keine weiteren Starteraufgaben gestartet; bereits aktive Aufgaben enden geordnet.
Die Starterzeugung darf schlechtere, aber zulässige Graphen liefern: Hier bestehen noch
keine monoton fortgeführten Elternlinien.

Omega-Konstruktion löst sämtliche P-Margins als binäres CP-SAT-Modell. Reparatur verwendet
eine frisch erzeugte Bernoulli-Matrix als Präferenz, erfüllt bei Rückgabe aber alle harten
Bedingungen. Algebraische Versuche verlangen zusätzlich Rahmentranslation um 1, 2 oder 7.
Lambda-Konstruktion verwendet Gradgleichungen und fügt verletzte Lambda-Bedingungen exakt
hinzu. Eine Rückgabe erfolgt erst nach vollständiger Lambda-Prüfung. Die Reparatur beginnt
mit einer zufällig beschrifteten regulären Vorschlagsmatrix; die algebraische Variante
testet Translation um 33 auf Z99. Für diese Familien wird weder Lösbarkeit noch schnelle
Ausbeute zugesagt. UNKNOWN/Budgetende bedeutet lediglich: kein Start in dieser Aufgabe.

Pro Elternzustand und Generation acht Versuche:

| Typ | Anzahl | Störlänge |
|---|---:|---|
| kurze zufällige Störung | 3 | gleichverteilt 2–4 |
| mittlere zufällige Störung | 2 | gleichverteilt 5–12 |
| lange zufällige Störung | 1 | gleichverteilt 13–32 |
| elterngerichtete Störung | 1 | gleichverteilt 8–16 |
| Omega-Crossover / zweiter gerichteter Lambda-Versuch | 1 | Crossover bzw. 8–16 |

Bei voller Population sind dies 512 Versuche pro Generation, davon im Erwartungswert
3104 rein zufällige Störzüge vor dem Abstieg. 512 Versuche bedeuten nicht 512 erfolgreiche Kinder.
Jeder vollständige Versuch endet bei spätestens 256 F-Bewertungen, 32 angenommenen
Abstiegszügen oder 30 CPU-Sekunden. Die Grenzen betreffen die Aufgabe, nicht den Gesamtlauf.
Zugerzeugung, Ausrichtung und Solverarbeit werden zur CPU-Zeit gezählt. Eine C-Bibliothek
kann geringfügig über das Restbudget hinaus zurückkehren; überwacht werden zusätzlich RSS
und ein 600-Sekunden-Watchdog für einen festhängenden Worker.

Die letzten acht besuchten beschrifteten Zustände und die direkte Umkehrung sind tabu.
Die Störung darf F erhöhen. Der anschließende Abstieg wählt eine strikte Verbesserung
unter bis zu acht generierten zulässigen Nachbarn. Kein Befund aus dieser endlichen
Stichprobe wird als bewiesenes lokales Minimum bezeichnet. Vollständige Nachbarschaftsleere
und Budgetende werden unterschiedlich protokolliert. Der beste tatsächlich übernommene,
zulässige, nicht zum Elter isomorphe Zwischenstand bleibt erhalten.

Nach zehn unveränderten Generationen verwendet eine seit fünf Generationen nicht strikt
verbesserte Linie zwei kurze, zwei mittlere und zwei lange Zufallsversuche; der lange Bereich
wird auf 13–64 erweitert. Eine strikte Verbesserung stellt die ursprüngliche Verteilung wieder her.

Omega-Einzelzüge: 70 % 4×4, 20 % 4×6, 10 % 6×6. Lambda: 90 % Apex, 10 % geprüfte Rotation.
Vollständig erschöpfte Familien werden aus der Auswahl entfernt und die übrigen Gewichte
renormiert. Endet die Erzeugung vorher am Aufgabenbudget, wird die Familie nicht als leer
erklärt. Innerhalb einer Familie wird die Durchlaufreihenfolge zufällig variiert; eine uniforme
Verteilung über sämtliche zulässigen Züge wird nicht behauptet. Die 250600 Sechservektoren
werden modulo Vorzeichen lazily erzeugt; ihre quadratische Paartabelle wird nie gespeichert.

Crossover erfolgt nur zwischen Omega-Eltern im selben Rahmen: `Delta_ij in {0,D_ij}`,
`P Delta = 0`, Symmetrie und vollständige harte Bedingungen. 25/50/75 Prozent sind weiche
Zielanteile, bezogen auf unterschiedliche ungerichtete Paare. Ganze Eltern und isomorphe
Elternkopien sind ausgeschlossen. Solverzustände mit gültigem Kind werden unabhängig geprüft.

Gerichtete Mutation wählt möglichst eine andere Herkunft im selben Arm. Im Omega-Arm
werden 64 erlaubte zufällige Rahmenumbenennungen verglichen; im Lambda-Arm wird eine endliche
lokale Beschriftungsverbesserung verwendet. Das ist eine Heuristik, kein minimaler Editabstand.
Pro Schritt werden bis zu acht zulässige Züge bewertet, mit Wahrscheinlichkeit 0,8 wird der
Zug mit geringstem beschriftetem Abstand zum zweiten Elter gewählt, sonst zufällig.
Kanten außerhalb beider Elternmengen sind dabei erlaubt.

Alle Aufgaben einer Runde beziehen sich auf dieselbe Elternpopulation. Der beste geeignete
Nachfahre ersetzt seinen eigenen Elter. Populationsduplikate werden abgelehnt, auch bei
strikter Verbesserung. Bei F-Gleichstand wird kanonische Neuheit verlangt und größerer
Deskriptorabstand zur übrigen Population bevorzugt. Auswertung und Kollisionsauflösung erfolgen
in fester Linienreihenfolge, unabhängig von der Fertigstellungsreihenfolge der Worker.
Archive verschiedener Merkmalszellen ergänzen ein unverlierbares globales Bestniveau je Arm.
Ein schlechterer Neustart ersetzt keine laufende Elternlinie.

## Sprache und erforderliche Abhängigkeiten

Python 3.12, `ortools==9.15.6755`, `pynauty==2.8.8.1`. NumPy und weitere Pakete werden als
Abhängigkeiten von OR-Tools installiert, nicht vorsorglich als separate Werkzeugausstattung.
Der Laufkern verwendet ganzzahlige Bitmasken; der unabhängige Prüfer nur Python-Standardbibliothek
und Nachbarmengen. Die Isomorphieprüfung verwendet nauty-Zertifikate, im Omega-Arm zusätzlich
eine gewurzelte/gefärbte Form. Graph6 oder Deskriptor-Hashes ersetzen diese Prüfung nicht.

Für CPython 3.12, Linux x86-64 und glibc 2.39 liegen passende Binärpakete vor:
[Pynauty](https://pypi.org/project/pynauty/2.8.8.1/),
[OR-Tools](https://pypi.org/project/ortools/9.15.6755/).
Die Installation erzwingt `--only-binary=:all:`. Es wird nicht heimlich auf einen Quellbuild
gewechselt. Compiler, CMake, Ninja und historische SAT/LRAT-Werkzeuge werden nicht benötigt.
Falls Ubuntu das Venv-Modul noch nicht vollständig installiert hat, wird ausschließlich
`python3-venv` nachinstalliert. Sämtliche tatsächlich installierten Paketversionen werden
mit `pip freeze --all` festgehalten.

## Office-Ressourcen und Laufzeit

Die folgende Tabelle enthält Planungswerte. Gemessene Solver-Spitzen auf dem Office-Rechner
stehen erst nach dessen vollständiger Kontrolle und Kalibrierung zur Verfügung.

| Größe | Auslegung 0.1.0 |
|---|---|
| Physische/logische CPU | vier/acht; drei einzelne Suchprozesse |
| Priorität | Coordinator nice +5; Worker zusätzlich +10 |
| Numerische/CP-SAT-Threads | jeweils einer |
| Erwarteter Experimentspeicher | ungefähr 1–2,5 GiB RSS; noch nicht Office-gemessen |
| Gemessene RSS-Schranken | 1100 MiB je Worker, 3072 MiB einschließlich Coordinator |
| Virtueller Adressraum | 1536 MiB je Worker; zusätzliche Schranke, kein RSS-Ersatz |
| WSL-Speicherreserve | unter 768 MiB MemAvailable keine neuen Aufgaben; unter 384 MiB geordneter Stopp |
| Swap | keine eingeplante Kapazität; Nutzung wird berichtet |
| Freier Plattenplatz | 10 GiB Reserve, sowohl Linux-Laufpfad als auch Windows C: |
| Installation und erste Daten | voraussichtlich unter 2 GiB |
| Checkpoints | drei rollierende gzip/JSON-Stände; erwartet unter 10 MiB je Stand |
| Kompakte Logs | erwartet unter 100 MiB täglich; Detail-Logs rotieren je 25 MiB |
| Vollständige Seedliste | append-only `task_seeds.tsv`; wächst separat, keine Rotation |
| Vorbereitung | ungefähr 30–60 Minuten eingeplant, automatische Startergrenze 45 Minuten |
| Pilot | 24 Stunden aktive Coordinator-Laufzeit; Ausfallzeit bei ausgeschaltetem Rechner zählt nicht |

Für eine volle Generation beträgt die Summe der Aufgabenbudgets 15360 CPU-Sekunden.
Bei drei Workern entspricht dies 85,3 Minuten reiner Aufgaben-CPU bei voller Parallelität,
zuzüglich Start-, Koordinations-, Prüf- und Betriebssystemkosten. Das ist keine gemessene
Generationsdauer und keine strenge Wanduhrschranke. Früher endende Versuche und kleinere
Populationen verkürzen die Runden. Statusberichte liefern nach mindestens acht Aufgaben
eine gemessene Batch-ETA. Eine ETA bis F=0 wird nie ausgegeben.

## Dateien und Wiederaufnahme

Im Repository:

- `src/memetic/`: Kern, Operatoren, Modelle, Worker, Coordinator, Laufbetrieb, unabhängiger
  Prüfer, gebündelte Kontrollen und Auslieferung.
- `configs/memetic/office-0.1.0.json`: sämtliche Betriebsparameter.
- `data/memetic/reference/`: vier kleine graph6-Referenzen und Dateibyte-Prüfsummen.
- `docs/memetic/`: Vertrag und unveränderte Reviewgrundlagen.
- `results/memetic/`: kleine lokale Kernprüfergebnisse und nachgerechnete Planungswerte;
  die Auslieferung ergänzt nach Erfolg den vollständigen Office-Prüfbericht.
- `manifests/memetic/`: nach erfolgreicher Office-Prüfung die reproduzierbare Paket-
  und Versionsinformation der dort tatsächlich installierten Umgebung.

Außerhalb des Repositorys, unter `/home/rb/conway99_workspace/conway99_memetic_office_0.1.0/`:

- `environment/`: isolierte Python-Umgebung;
- `audits/`: vollständige Validierung, installierte Versionen, Status und kompletter Diff vor Commit;
- `runs/pilot-001/`: Config, Provenienz, Starterbericht, Kalibrierung, Population, Bestarchiv,
  Seedliste, Status, Logs, atomare Checkpoints, temporäre Workeraufgaben und separat geprüfte Treffer.

Checkpoints sind ein gzip-komprimierter JSON-Umschlag mit Schema, Sequenznummer und SHA-256
über eine kanonische JSON-Nutzlast. Darin stehen Konfiguration, Population, Archive,
Rundensnapshot, abgeschlossene Ergebnisse, Aufgabenseeds, Zähler und aktive Laufzeit.
Drei Slots werden atomar ersetzt, jeweils mit Dateisystem-fsync. Nach einem beschädigten
neuesten Slot wird der neueste ältere gültige Stand geladen; wenn keiner gültig ist, gibt
es keinen stillen Neustart. Ein flock verhindert zwei Coordinator für denselben Lauf. Worker erhalten ein Linux-
Elternprozess-Todessignal, damit ein unerwartet beendeter Coordinator keine verwaisten
Suchprozesse hinterlässt.

Jede Aufgabe hat einen aus Masterseed und Aufgabenkennung abgeleiteten Zufallsstrom.
Abgeschlossene Ergebnisse werden vor Bereinigung der temporären Dateien dauerhaft gesichert.
Unvollständige Aufgaben werden beim Resume aus ihrem unveränderten Input und Seed wiederholt.
CPU-/Solverzeitbudgets können auf verschieden belasteten Rechnern unterschiedliche Endpunkte
erzeugen. Gesicherte Ergebnisse sind verbindlich; bitgleiche Wiederholung zeitbegrenzter
Aufgaben wird nicht versprochen. Änderungen von Code, Referenzen, Konfiguration, Python
oder wesentlichen Paketversionen verhindern eine stille Wiederaufnahme unter anderer Semantik.

Der gleiche Auslieferungsaufruf startet einen unterbrochenen Lauf erneut. Nach einem
Windows-Neustart muss Ubuntu gestartet und dieser Aufruf wiederholt werden. Es wird kein
Windows-Autostart und keine geplante Aufgabe eingerichtet. Ein bereits aktiver Lauf wird
nicht doppelt gestartet. Ein vollständig beendeter Pilot wird nicht automatisch verlängert.

## Auslieferungs- und Validierungsschranke

Die Arbeitsumgebung konnte die externen Pakete wegen einer abgebrochenen Netzfreigabe
nicht installieren. Hier ausgeführt: unabhängige Referenzprüfungen, vollständige unmittelbare
HoG-Apex-Nachbarschaft, Omega-Produktkontrolle, alle Support-4/6-Kernvektoren, Rook/BvLS-
Positivkontrollen einschließlich Rotation, Checkpoint-Rückfall und exklusive Laufsperre.
Die Details stehen in `results/memetic/core_validation_0.1.0.json`.

Noch nicht als bestanden behauptet werden: nauty-Kanonisierung, tatsächliche CP-SAT-Modelle,
paralleler Betrieb mit diesen Paketen und echte Runner-Wiederaufnahme. Vor erstem Commit,
Push und Suchstart führt die Auslieferung automatisch genau eine volle Kontrollserie aus:
zusätzlich Beschriftungsinvarianz, negatives UND positives Crossover-Modell sowie hartes Beenden per SIGKILL
und Wiederaufnehmen eines kurzen echten Coordinator-Laufs. Sie stoppt bei jedem Fehler.
Eine unveränderte, bereits vollständig validierte Version verwendet beim nächsten Aufruf
den gespeicherten Validierungsnachweis statt dieselben Tests erneut auszuführen.

Ein erfolgloser Pilot ist weder UNSAT noch eine Widerlegung von Conway 99. Wenn die Zielpopulation
nicht erreicht wurde, wird ausdrücklich der tatsächlich untersuchte kleinere Bestand berichtet.


## Auslieferungsrevision r2 – Checkpoint-Korrektur

Die volle Office-Kontrolle der Erstlieferung erreichte die Runner-Wiederaufnahme,
brach dort aber wegen ungültiger Prüfsummen ab. Ursache war die Sortierung numerischer
Schlüssel des Residuenhistogramms: vor dem JSON-Schreiben numerisch, nach dem Einlesen
als Zeichenketten. Revision r2 normalisiert JSON-Schlüssel vor der kanonischen Sortierung.
Die Regression enthält nun ein verschachteltes Histogramm mit negativen und mehrstelligen
Schlüsseln und prüft die vollständige Schreib-/Lese-Rundreise.

Auf dem Office-Rechner sind die benötigten Pakete bereits installiert; Isomorphie-
und Crossover-Kontrollen wurden vor dem Wiederaufnahmefehler durchlaufen. Die erneute
volle Kontrollserie bleibt vor Commit, Push und Pilotstart erforderlich. Der r2-Installer
ersetzt ausschließlich anhand ihrer ursprünglichen SHA-256-Werte erkannte Dateien der
Erstlieferung. Vorhandene Pilot-Checkpoints werden nicht automatisch migriert.
