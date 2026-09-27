# Fortsetzung: Conway99 — λ-Reparaturpilot auf dem Ryzen

Setze unser Conway99-Projekt **ausschließlich im Zweig λ-Memetik auf dem
Ryzen** fort. Ziel bleibt ein srg(99,14,1,2), also W=0. Der freigegebene
nächste Versuch ist gemeinsame Kantenreparatur mit einem exakten Solver.
Der Pilot ist implementiert, geprüft und veröffentlicht. **Er wurde im
vorigen Chat noch nicht auf dem Ryzen gestartet.**

Ich habe dem Piloten zugestimmt und ausdrücklich eine ausreichend breite
Startbank sowie großzügige Nutzung des Ryzen verlangt. Der erweiterte
Plan mit bis zu 156 CPU-Stunden ist die maßgebliche Ausführungsvorgabe.
Erstelle keinen weiteren allgemeinen Plan und implementiere keinen
zusätzlichen Suchmechanismus. Betreue zunächst dieses fertige Paket.

## Zuerst lesen und prüfen

Repository `ibenarb/conway99-research`, Arbeitsbranch `memetik`.
Vor Git-Aktionen `AGENTS.md` und `docs/CONWAY99_COLLABORATION.md` lesen.
Allgemeine projektbezogene Veröffentlichungserlaubnis besteht.

**Festes Release:** Commit
`71d06c2fbfd7866bf42bca16a2295517a9cdd965`.

1. [Implementierung, ausgeführte Prüfungen und Grenzen](https://github.com/ibenarb/conway99-research/blob/71d06c2fbfd7866bf42bca16a2295517a9cdd965/docs/memetik/lambda_repair_pilot_20260927/IMPLEMENTIERUNG_UND_PRUEFUNG.md)
2. [Paket-README](https://github.com/ibenarb/conway99-research/blob/71d06c2fbfd7866bf42bca16a2295517a9cdd965/experiments/memetik/lambda_repair_1_0_0/README.md)
3. [Erweiterter Pilotplan V2](https://github.com/ibenarb/conway99-research/blob/f67039295f658380f5795d95b72ad9a32769a9d8/docs/memetik/lambda_repair_pilot_20260927/PLAN_V2.md)
4. [Quellen, Paketmanifest und maschinenlesbare Tests](https://github.com/ibenarb/conway99-research/tree/71d06c2fbfd7866bf42bca16a2295517a9cdd965/experiments/memetik/lambda_repair_1_0_0)

**Direkter ZIP-Download:**

https://raw.githubusercontent.com/ibenarb/conway99-research/71d06c2fbfd7866bf42bca16a2295517a9cdd965/releases/memetik/lambda_repair_1_0_0.zip

**SHA256:**

`3500d0129770139392f151dd96f01e0ab26c4a1609b3cb453bf0739c38903f38`

ZIP-Größe 74872 Bytes; oberster Ordner `lambda_repair_1_0_0`.
Das ZIP enthält 23 Dateien, einschließlich des Paketmanifests. Es ist
selbstständig; für den Start werden keine früheren Roharchive benötigt.
Die erste Installation lädt zusätzlich ungefähr 58 MB exakt festgelegte
Python-Wheels. Versionen und SHA256s sind vollständig im Paket enthalten.

## Dein erster praktischer Auftrag

Prüfe die oben fixierten Quellen und den ZIP-Hash. Gib mir anschließend
**genau einen Bash-Einzeiler für die WSL-Ubuntu-Konsole auf dem Ryzen**, der
unter `$HOME/conway99_workspace` das Paket herunterlädt, den Hash prüft,
einen bereits vorhandenen gleichnamigen Paketordner nicht überschreibt,
entpackt und `lambda_repair_1_0_0/start.py` mit dem vorhandenen Python
`$HOME/conway99_workspace/venvs/memetik/bin/python` ausführt.

`start.py` erzeugt eine **neue** Solverumgebung und startet danach den
Piloten autonom. Keine zusätzliche Installation in der vorhandenen
memetik-Umgebung. Keine erneute allgemeine Freigabe erfragen. Falls ich
inzwischen einen Start gemeldet habe, stattdessen den existierenden Lauf
betreuen; niemals einen zweiten starten.

Für meine Softwarehandlungen immer nur **ein Schritt pro Antwort**, dann
meine Ausgabe abwarten. Befehle als Einzeiler ohne Fortsetzungszeichen.
Deutsch, präzise, leicht formell; jede Antwort mit lokalem Datum und
Uhrzeit im Format `yy.mm.dd HH.MM.SS` beginnen.

## Feste Umgebung und Bedienung

- Ryzen, WSL2 Ubuntu, Python3.12, Linux x86_64; bis zwölf Solverprozesse.
- Neue Umgebung: `$HOME/conway99_workspace/venvs/lambda-repair-1.0.0`.
- Laufverzeichnis: `$HOME/conway99_workspace/ryzen_lambda_repair_100_20260927`.
- Eingefrorenes Bedienprogramm: `RUN/program/run.py`.
- Aktionen: `status`, `pause`, `launch` für saubere Wiederaufnahme,
  `verify`, `export`; jeweils mit dem vollständigen RUN-Pfad als Argument.
- Bedienaktionen mit dem Python der **neuen** Solverumgebung ausführen.
- `controller.log`, `status.json`, `ledger.json`, `RESULT.json`,
  Einzelaufgaben, unveränderliche Receipt-Snapshots und Kontrollberichte.
- Status im Log alle zehn Minuten mit ETA. Er erscheint nicht fortlaufend
  im ursprünglichen Terminal, weil der Controller im Hintergrund läuft.
- Aktive Walltime über Windows-Stopwatch, CPU-Abrechnung über `wait4`.
  Die WSL-Monotonzeit driftet und darf nicht als Kampagnenuhr dienen.
- Vor produktiver Arbeit werden reale Host-Uhr/VHDX-Zuordnung sowie
  Prozess-ID/procfs-Übereinstimmung geprüft. Kein stiller Fallback.

Bei Fehlern zuerst vorhandene Ausgabe auswerten und den nächsten einzelnen
Diagnoseschritt angeben. Laufende oder eingefrorene Verzeichnisse nicht
verändern. Insbesondere keine Ledger-/Session-Dateien löschen, um eine
Wiederaufnahme zu erzwingen. Nach hartem Absturz ist die CPU-Abrechnung
unter Umständen ungeklärt. Eine saubere USER_PAUSE kann dagegen mit
`launch` und denselben verbleibenden Budgets fortgesetzt werden.

Wiederaufnahme erhält den besten gespeicherten Graphen, CPU-Verbrauch
und aktive Hostzeit. CP-SAT wird neu aufgebaut: interner Suchbaum und
Klauseln werden nicht gespeichert. Der erneute Aufbau zählt zum Budget.

## Versuchsdefinition

λ-Kandidaten haben 99 Knoten, Grad14, jede Kante genau einen gemeinsamen
Nachbarn. Für ungeordnete Paare ist
`r_uv = |N(u)∩N(v)| + A_uv - 2`.
W zählt von null verschiedene Residuen, L1 summiert Beträge, F Quadrate;
Linf ist der maximale Betrag und Nmax seine Häufigkeit.

24 paarweise nichtisomorphe Startklassen, zwölf je beobachteter Herkunft
A/B. Je sechs beste nach (W,L1,state), sechs zusätzliche nach festen
invarianten Fehlermerkmalen innerhalb W≤Original-W+100. Diese Auswahl ist
bereits erfolgt; unterschiedliche Klassen sind keine bewiesenen getrennten
Suchbecken. Die Herkunftslinien sind keine randomisierten Familienarme.

24 Starts × Fenstergrößen 24/40/60 × zwei Auswahlregeln ergeben 144
festgelegte Aufgaben. Auswahlregeln: hoher Fehlergrad bzw. feste
Pseudozufallsrangfolge, beide wachsen entlang bestehender Kanten.
Alle Knotenlisten und Seeds stehen unveränderlich in MANIFEST.json.
Keine adaptive Nachselektion, kein Crossover, keine Migration und keine
neuen Aufgaben aus während des Piloten gefundenen Graphen.

Nur Kanten mit beiden Endpunkten im Fenster sind variabel. Grad14 und
Kanten-λ=1 bleiben harte globale Bedingungen. Zielfunktion ist global
lexikographisch (W,L1), kodiert als `50000*W+L1`. Auch Fenster-Außen-Paare
müssen berücksichtigt werden; reine Außen-Außen-Paare bleiben konstant.
Interne Solverbelegungen müssen keine Folge zulässiger AP-Züge bilden.
Jeder ausgegebene Kandidat wird unabhängig vollständig nachgerechnet.

Fünf der 48 Fenster mit 24 Knoten sind schon durch notwendige
Randbedingungen vollständig starr. Das Paket reproduziert dies getrennt
und speichert Propagationstraces. Diese Aufgaben benötigen keine volle
Solverstunde. Bei den anderen Fenstern bedeutet eine verbleibende freie
Variable noch nicht, dass eine alternative zulässige Belegung existiert.

## Budget und autonome Phasen

- Bis 3600 CPU-Sekunden je Aufgabe, inklusive Modellaufbau/Initialisierung.
- Bis zwölf zusätzliche CPU-Stunden für Einrichtung, Kontrollen,
  Koordination und Nachprüfung: insgesamt höchstens 156 CPU-Stunden.
- Keine automatische Übertragung ungenutzter Einzelbudgets.
- Höchstens 24 Stunden aktive Windows-Host-Walltime.
- Bis zwölf Single-Thread-Worker; Kalibrierung und konkurrierende Last
  können die Parallelität verringern.
- 24 GiB Gruppen-RAM. Unter 6 GiB freiem RAM keine neuen Aufgaben;
  bei kritischer Unterschreitung von 2 GiB oder Gruppenüberschreitung
  kontrollierter Abbruch. Mindestens 25 GiB freie logische und Host-Disk.
- Reihenfolge: Uhrkontrolle, mathematische Kontrollen, drei kurze
  Größenkalibrierungen, produktive Aufgaben. Kalibrierungen zählen zu
  den ursprünglichen Aufgabenbudgets; sie sind keine zusätzlichen Arme.

Vorläufig erwartete Walltime bei freiem Ryzen: **14–20 Stunden**.
Das ist keine gemessene Zusage. Bei wenig Parallelität kann die 24-h-Grenze
vor der Abarbeitung aller Aufgaben erreicht werden.

## Befunde vor diesem Piloten

Original A: **W=2076, L1=2488, F=3352, Linf=3, Nmax=20**.
Original B: **W=2077, L1=2436, F=3180, Linf=3, Nmax=13**.
Der nahe Kontrollgraph N hat W=2077, L1=2488 und ist nicht B.
Sein bekannter Zwei-Pivot-Rückweg führt nach A; Trägerknoten
`3, 26, 31, 33, 42, 66, 71, 72`.

Der Radiusversuch fand aus A und B keine bessere (W,L1)-Lösung in höchstens
vier Zügen des eingefrorenen Apex/Pivot-Katalogs. Das ist kein globaler
Ausschluss und keine Aussage über alle denkbaren Reparaturen.

Das anschließende feste Kick-/P-Abstiegsprofil endete budgetbedingt bei
5685 von 6000 Episoden ohne Verbesserung. Kurze Kicks kehrten meist
zurück; lange erzeugten viele deutlich schlechtere Endpunkte.
Die unveränderte P-Linie pausiert. Der jetzige Pilot testet einen anderen
Änderungsmechanismus, keine bloße Verlängerung dieses Profilversuchs.

Beim Rekord verletzen 2076 der 4158 Nichtkanten ihre Zielbedingung;
Fehler betreffen alle Knoten. W ist kein kalibrierter Abstand zu einer
Lösung. Weder Vielfalt noch Flucht noch ein kleiner W-Rekord beweisen
Konvergenz zu W=0. Keine zusätzliche polyedrische/geometrische Annahme
als notwendige SRG-Bedingung einführen.

## Prüfstand und Interpretation

Die veröffentlichten Cloud-Prüfungen bestehen: vollständige kleine
Lösungsmengen, alle 144 Randbedingungen-Zahlen, bekannte N→A-Reparatur,
separate hashgebundene Installation, Pause/Wiederaufnahme, CPU-Audit,
Quellkorruptions-/ungeklärte-CPU-Sperren und geprüfter Ergebnisexport.
Die Cloud-Laufsteuerungsprüfung verwendet ausdrücklich FakeHost; die
echte Windows-Uhr wird erst auf dem Ryzen geprüft.

Primärer Erfolg: unabhängig bestätigtes **W<2076**. Sekundäre
Verbesserungen relativ zum jeweiligen Gründer gesondert ausweisen.
Der erste Rekord stoppt die übrigen Aufgaben nicht automatisch;
W=0 beendet nach unabhängiger Prüfung den Piloten.

`OPTIMAL_UNCERTIFIED` ist eine CP-SAT-Meldung ohne unabhängig geprüftes
Ausschlusszertifikat. Nicht als zertifizierten Fenster- oder globalen
Ausschluss ausgeben. `COMPLETED_BUDGETED_PILOT` bedeutet, dass alle
Aufgaben gemäß ihren Regeln beendet sind, nicht dass sie sämtlich optimal
bewiesen wurden. Zeit-/CPU-Abbruch bleibt UNKNOWN.

Ein Pilot ohne neuen Rekord und mit vielen ungelösten Aufgaben beweist
keine Erschöpfung der Reparaturmethode oder der λ-Suche. Kein automatischer
Folgelauf und keine stillschweigende Budgeterhöhung. Nach Abschluss erst
Export, unabhängiger Audit, Veröffentlichung und dann Fortsetzungsentscheidung.

Für Cloud-Audits `tools/memetik/audit_python.py` verwenden. Neue Ergebnis-
klassen dort mit dem isolierten pynauty prüfen; eine zufällige globale
Benutzerinstallation ist keine Prüfgrundlage. Fehlende lokale Dateien bei
Bedarf aus den fixierten Git-Quellen rekonstruieren. Große frühere
Roharchive nur bei einem konkreten zusätzlichen Prüfbedarf anfordern.
