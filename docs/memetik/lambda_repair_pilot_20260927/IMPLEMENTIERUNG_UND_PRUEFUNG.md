# Solverpaket lambda_repair_1_0_0

27.09.2026. Umsetzung des freigegebenen erweiterten Piloten, ausschließlich
λ-Memetik auf dem Ryzen. Kein produktiver Ryzen-Lauf wurde in diesem Chat
begonnen. Der nächste Chat soll den vorbereiteten Piloten betreuen.

## Gelieferter Stand

- Eigenständiges Release `releases/memetik/lambda_repair_1_0_0.zip`.
- Quellen `experiments/memetik/lambda_repair_1_0_0/`.
- Byteidentische Übernahme von Startbank und Fenstern aus
  `f67039295f658380f5795d95b72ad9a32769a9d8`.
- OR-Tools CP-SAT 9.14.6206, elf exakt fixierte Runtime-Abhängigkeiten,
  Wheel-SHA256s und Installation in einer neuen isolierten Umgebung.
- Grad14 und λ=1 hart, globale Zielfunktion `50000*W+L1`, unabhängiger
  mengenbasierter graph6-/Score-/Fensterrand-Prüfer.
- 144 feste Aufgaben mit je einer CPU-Stunde einschließlich Modellbau,
  12 CPU-Stunden Hilfsbudget, 24 Stunden aktive Host-Walltime.
- Bis zwölf Single-Thread-Prozesse, begrenzt durch Kalibrierung, freie
  Ressourcen und Gruppen-RAM. CPU per wait4; Windows-Stopwatch; Status
  im Log alle zehn Minuten mit ausdrücklich grober ETA.
- Frische Uhrkontrolle pro Sitzung, mathematische Kontrollen, danach
  drei Kalibrierungen à höchstens 60 CPU-Sekunden. Diese werden den
  ursprünglichen Aufgabenbudgets belastet und erzeugen keine Zusatzarme.
- Fünf durch Randbedingungen starre Fenster werden mit Propagationstrace
  erledigt, ohne eine nutzlose volle Solverstunde abzuwarten.
- Atomare Kandidatensicherung, einzelne CPU-Receipts und unveränderliche
  Ergebnis-Snapshots. Export mit vorherigem Audit und SHA256.

Das ausführbare Paket und die begründenden Auswertungen sind Git-Artefakte;
eine zweite Ablage des Repositorys ist nicht erforderlich.

## Tatsächlich ausgeführte Kontrollen

1. Kleine Fälle auf sechs Knoten mit Grad2 und λ=0 bzw. λ=1 vollständig
   aufgezählt. Der unabhängige Enumerator findet 60 bzw. zehn beschriftete
   Graphen. Für je drei Fenstergrößen stimmen die gesamten zulässigen
   Lösungsmengen und Zielfunktionsoptima mit CP-SAT überein.
2. Alle 24 Gründer erneut unabhängig auf die λ-Bedingungen und sämtliche
   Kennzahlen geprüft. Bereits vorher unabhängig kanonisierte Startbank
   und Fensterdatei unverändert übernommen.
3. Sämtliche 144 veröffentlichten Randbedingungen-Zahlen mit einem
   getrennten mengenbasierten Prüfer reproduziert; fünf starre Fenster.
4. Die bekannte Rückreparatur N=(2077,2488) nach A=(2076,2488) wird ohne
   Vorgabe der Zielkanten gefunden, und der vollständige Endgraph wird
   unabhängig nachgerechnet.
5. Vollständige Startbelegungen an den drei repräsentativen Größen gegen
   jede erzeugte Modellnebenbedingung geprüft. Jeder produktive Worker
   führt dieselbe vollständige Prüfung vor seinem Solveraufruf aus.
6. Isolierter Integrationstest mit drei verkürzten Aufgaben: SIGTERM-Pause,
   alle Kinder per wait4 abgerechnet, Wiederaufnahme aus erhaltenen
   Kandidaten, Abschluss innerhalb der jeweiligen CPU-Obergrenzen und
   vollständiger Ledger-Audit. Endstatus enthält keine laufende ETA und
   zählt die zuletzt abgeschlossene CPU-Sitzung nicht doppelt.
7. Veränderte eingefrorene Quelle und ungeklärte CPU-Reservierung werden
   zurückgewiesen. Keine automatische Fortsetzung nach unklarem Absturz.
8. Eigenständige Installation mit `--require-hashes` und `pip check`
   erfolgreich; Vorbereitung in einem neuen Testworkspace ohne Laufstart.
9. Ergebnisexport ausgeführt, SHA256 nachgerechnet, Archivinhalt und
   enthaltenen unabhängigen Auditbericht geprüft.

Die maschinenlesbaren Ergebnisse stehen in `TEST_RESULTS.json` im Paket.
Die vollständigen Prüfscripte sind enthalten. Cloud-Integration verwendet
explizit FakeHost; sie ist kein ausgeführter Windows-/WSL-Test.

## Während der Entwicklung korrigierte Fehler

Die vollständige Belegungsprüfung musste die von CP-SAT eingefügten
Konstanten und bool_or-Nebenbedingungen ausdrücklich berücksichtigen.
Ein verkürzter Wiederaufnahmetest zeigte außerdem, dass Modellbau vor
Beginn des Solver-Watchdogs zu viel Restbudget verbrauchen konnte.
CPU- und Pause-Prüfungen greifen nun bereits im Modellbau und in der
Belegungsprüfung; der korrigierte Integrationstest besteht.

In der Cloud stimmen numerische Prozess-IDs nicht zuverlässig mit dem
sichtbaren procfs-Namensraum überein. Das Produktionsprogramm akzeptiert
solche Umgebungen nicht. Der echte Ryzen-Start prüft die Übereinstimmung;
Windows-Uhr und VHDX-Zuordnung müssen dort ebenfalls erfolgreich sein.
Es wird keine stillschweigende Ersatz-Uhr verwendet.

## Genaue Grenzen der Aussagen

`OPTIMAL_UNCERTIFIED` bezeichnet eine Solver-Optimalitätsmeldung ohne
unabhängig geprüftes Beweiszertifikat. Daraus wird kein zertifizierter
Fensterausschluss gemacht. `COMPLETED_BUDGETED_PILOT` bedeutet, dass alle
Aufgaben gemäß Budgetregeln beendet wurden, nicht dass sämtliche Fenster
optimal gelöst wurden. Timeouts bleiben unbekannt.

Wiederaufnahme erhält Graphen, CPU-Konten und aktive Hostzeit. Der interne
CP-SAT-Suchbaum und gelernte Klauseln werden nicht gespeichert. Der
Neustartaufwand zählt erneut zum verbleibenden ursprünglichen Budget.
Nach hartem Prozess-/Hostverlust ist erst Diagnose und Abrechnung nötig.

Die geschätzten 14–20 Stunden auf einem freien Ryzen bleiben eine
Planungsannahme. Gemessene Solver-RAM-Bedarfe oder konkurrierende Last
können die Parallelität verringern; dann kann die harte 24-h-Grenze ein
unvollständiges Ergebnis erzeugen. Keine automatische Budgetverlängerung.

Der nächste wissenschaftliche Entscheidungsmaßstab bleibt ein unabhängig
geprüfter Graph mit W<2076. Sekundäre Gründerverbesserungen, Schranken und
Aufgabenstatus werden vollständig mitberichtet. Keine Behauptung eines
nachgewiesenen Weges nach W=0 und kein globaler Nichtexistenzausschluss.
