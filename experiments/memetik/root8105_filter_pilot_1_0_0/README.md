# ROOT8105 Filterpilot 1.0.0

Eigenes Paket; rc3 und laufende Ryzen-/C2-Prozesse bleiben unverändert.
Wissenschaftlicher Umfang: MATHEMATIK.md. Laufstatus und lokale Ergebnisse
stehen im mitgelieferten Bericht; dieser Text allein ist keine Startfreigabe
für eine neue Großkampagne.

## Betrieb

Python >=3.10, Linux/WSL; lokale Linux-Partition für SQLite-WAL.
setup.py erzeugt ausschließlich eine neue .venv dieses Pakets und prüft
SHA256.json. Vorhandene Umgebungen werden nicht verändert.
run.py init RUN erzeugt eine neue Laufkennung mit 14400 aggregierten
CPU-Sekunden als Meldeschwelle und höchstens elf Workern. --workers erlaubt
1..11, --budget-cpu-seconds setzt die ausdrücklich gewünschte Meldeschwelle.
Eigene Initialisierung, Preflight, Worker-wait4, Supervisor und Hosthelfer
werden separat verbucht. Zeitangaben innerhalb der Filter sind Teilmengen,
keine zusätzlich zur wait4-Abrechnung zu addierenden Konten.

preflight.py RUN prüft neue mathematische Kontrollen, Betriebs- und Recovery-
Regressionen. Unter WSL folgt eine 180-Gastsekunden-Lastprüfung mit zwei
Hilfsprozessen und realer Windows-Stopwatch. Diese Diagnosezeit ist kein
Suchzeitlimit. Bei Uhrenabweichungen bleibt ETA unknown; Anker, Deltas,
Frische und Fehlergrund stehen in preflight_clock_diagnostics.json.
Die Linux-/Cloudtests ersetzen diesen Windows-/WSL-Test nicht.

run.py run RUN --phase calibrate bearbeitet drei vorgewählte Roots (je Typ
einen, insgesamt neun Sampler/576 Zustände) auf dem echten Produktionspfad.
run.py run RUN --phase pilot übernimmt fertige Kalibrierungsaufgaben und
bearbeitet den Rest sowie die deterministischen SAT-Kontrollen. 24 Samplejobs
plus ein Kontrolljob; die historische interne Tabelle heißt weiterhin roots,
enthält also 25 Jobs. Der Kontrolljob mit ID0 ist kein zusätzlicher Root.
Status und Log alle etwa zehn Gastminuten; status.json wird laufend ersetzt.
Clock-Diagnostik alle etwa 30 Gastsekunden; immer als datierte Momentaufnahme.
Derzeit wird keine Gesamt-ETA aus den wenigen Kalibrierungsroots errechnet.

Budgetende: time limit reached. ETA unknown. Extend [seconds] ?
Ohne Antwort/bei EOF unverändert weiterarbeiten. Antwort über
run.py answer RUN RUN_ID REQUEST_ID SECONDS. IDs stehen in time_request.json.
Positive ganze Sekunden auf das bisherige aggregierte CPU-Budget addieren;
0 bewirkt einen kontrollierten Stopp. Falsche IDs/ungültige Antworten verändern
kein Budget. Antworten werden genau einmal verarbeitet. DB und atomarer
Dateispiegel werden beim Antworten, Abschluss und Neustart synchronisiert.

Nach kontrolliertem 0-Stopp ist run.py resume-after-stop RUN ausdrücklich
nötig; anschließend run.py run RUN. Nach Signalstopp reicht run.py run RUN.
Fertige Zielpaare werden nicht wiederholt; ein unterbrochenes, noch nicht
abgeschlossenes Zielpaar wird vollständig neu bearbeitet und seine frühere
CPU bleibt verbucht. Kein Löschen von Checkpoints zur Laufzeitverkürzung.
Harte/ungeklärte Abstürze erfordern inspect-crash/reconcile-crash. Gerettete
CPU-Untergrenzen werden nicht zu exakten Endkonten erklärt.

RAM-Sicherheit: unter 2 GiB freiem RAM kontrollierter Stopp; Disk unter 1 GiB.
Preflight verlangt 4 GiB RAM/2 GiB Disk. Kein globaler WSL-Neustart, kein Eingriff
in andere Prozesse. Die Zahl verfügbarer Kerne allein ist keine Zusicherung,
dass parallele C2-Arbeit elf zusätzliche Worker erlaubt.

run.py status RUN liest die Konten. run.py export RUN erstellt summary.json.
Diese enthält getrennte Sampler-/Unranking-/Filterkosten und Strata sowie
Kontrollresultate. Geschlossene Konten und PASS-Kontrollen sind erforderlich,
um von einem abgenommenen Pilot zu sprechen. Windows-Hostkonten mit fehlendem
Endwert werden ausdrücklich als Untergrenze markiert.

Regelbasis: Commit 40c0050af19353fd9c9d1a203e58f5df07636229;
GC-01/02/08/10/11/15/16/18/19/20/21. Es existiert keine Laufzeitgarantie.
