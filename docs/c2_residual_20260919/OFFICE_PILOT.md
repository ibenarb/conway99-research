# Office: technische Pilotvorbereitung, 19. September 2026

Fortsetzung nach Commit 6701297836e81038cf8754741248a5fdba0ab4ad.
Die untenstehenden Office-Ergebnisse stammen aus den vom Nutzer übermittelten
Konsolenausgaben. Sie sind keine hier ausgeführten Fernrechnungen auf seinem PC.

## Eingegangener Stand

- Host rb-PC, WSL Ubuntu 24.04.5, acht logische CPUs; zuletzt 4,3 GiB MemAvailable.
- Windows C: 286,6 GiB frei laut nativer PowerShell-Abfrage; virtuelle Linux-
  Freiplatzangaben werden dafür nicht verwendet. Ressourcenwerte sind Momentaufnahmen.
- Paket 1.0.0 per SHA256 geprüft; 2140 Lex-, 448 Bahnminimum- und 16 Rook-Prüfungen
  auf Office bestanden. Vier Varianten von Matchingtyp 6 mit geprüftem Basishash erzeugt.
- C++-Propagator lokal gebaut; 400 Prüferkontrollen und 20 UP-Abfragen bestanden.
- Für Cube [12] fixiert Totalizer 88, Lex 93 Primärbits. Ohne Annahmen jeweils 66,
  für [-12] jeweils 67, für [1722,1721] und [1721,859] jeweils 69.
  Dreierklauseln verändern hier keinen Primärabschluss. Kein UP-Konflikt.
- CaDiCaL aus rel-2.2.1 / Commit 4198d817d0dcde5b1240eefbff70b555b7df2af9
  lokal auf Office gebaut, Ausgabe 2.2.1. SAT-/UNSAT-Kontrollen liefern 10 bzw. 20.
- Office-Binärhash: 82c88e3027d35e7c60293ea9440fc97576e1161ee9e103785bdb6962748ba996.

## Neuer Starter office_pilot.py, Version 1.0.0

Er benutzt die bereits vorhandenen Office-CNFs und speichert Resultate unter
`office_pilot_runs/pilot_<UTC-Zeit>` im installierten Paket. Keine Änderungen
an alten Läufen oder an Memetikprozessen. Genau ein eigener Solverprozess
läuft gleichzeitig, mit nice=10. Reihenfolge vorab: Totalizer, beides, Lex,
Dreierklauseln. Jeweils Seed 0. Nur Typ 6, kein Cubing und keine Proof-Dateien.

Dies ist zunächst ein technischer Pilot mit vier kurzen Versuchen, kein
statistisch belastbarer Variantenbenchmark und keine Ausschlusszertifizierung.

### Grenzen

- CaDiCaL `-t 55`: 55 Sekunden Wandzeit nach seiner internen Aktivierung.
  Im gepinnten `src/cadical.cpp` ist -t ausdrücklich ein wall-clock limit.
- Zusätzlich Unix RLIMIT_CPU hart 60 CPU-Sekunden für den gesamten Kindprozess.
- Wrapper-Wandzeitgrenze 75 Sekunden; bei Abbruch SIGTERM an die eigene
  Prozessgruppe, nach zwei Sekunden nötigenfalls SIGKILL.
- 1536 MiB maximaler virtueller Adressraum per RLIMIT_AS; Swap ist kein Zusatzbudget.
- Pro Logdatei hart 16 MiB per RLIMIT_FSIZE, insgesamt höchstens 64 MiB Solverlogs;
  Core-Dumps aus. Keine Proof-Datei wird angefordert.
- Vor jedem Job mindestens 3 GiB MemAvailable, 2 GiB Linux-Freiraum und
  20 GiB tatsächlicher Windows-C:-Freiraum. Windows-Abfrage mit acht Sekunden
  Timeout; bei Fehler kein nächster Solverstart. Keine stille Ersatzmessung.
- Vor jedem Job wird bei anderen erkennbaren Python-/SAT-Prozessen abgebrochen.
  Diese vorsichtige Prüfung kann auch fremde harmlose Pythonprozesse erkennen.
  Niemand wird beendet; bei Bedarf erst gezielt klären.
- Während eines Jobs Abbruch bei unter 1 GiB MemAvailable bzw. 2 GiB
  Linux-Freiraum. Der Windows-Wert wird zwischen Jobs erneut gelesen; die
  zusätzliche Schreiblast innerhalb eines Jobs ist hart begrenzt.

Der Starter pinnt Solver, alle vier CNFs und die Primärkarte. Die vorhandenen
Office-Prüfberichte müssen PASS melden. CPU-Zeit und Spitzen-RSS kommen aus
wait4 für genau den gestarteten Prozess, nicht aus kumulierten Kindprozesswerten.
Kommandozeilen, Hashes, Ressourcenmessungen und vollständige Logs werden erhalten.

CaDiCaL 2.2.1 meldet reguläres Unknown als `c UNKNOWN` bei Rückgabecode 0;
das wird ausdrücklich berücksichtigt. Ein Ressourcenausfall wird nicht als
UNSAT interpretiert. Bei SAT wird nur SAT_UNVERIFIED, bei UNSAT nur
UNSAT_UNCERTIFIED gemeldet und zur Prüfung angehalten. Timeouts/CPU-Grenzen
bleiben offen. Falls der Pilot nur offene Ergebnisse liefert, folgt daraus
kein Laufzeitranking. Der harte CPU-Abbruch kann ein unvollständiges Schlusslog
hinterlassen; wait4-Ressourcenwerte bleiben dennoch verfügbar.

## Kontrolle des Starters

Die hier ausgeführten Kontrollen verwenden ausschließlich kurzlebige Testprozesse,
keinen C99-Solverlauf. Geprüft wurden SAT-/UNSAT-/Unknown-Klassifikation,
widersprüchliche Rückgabecodes, fehlende Statusmeldung, Wandzeitabbruch,
Ressourcenabbruch, Schutz vorhandener Logs, harte Ausgabegrenze sowie
fehlerhafte/zu kleine/zeitüberschreitende Windows-Messungen.
Ergebnisse: results/c2_residual_20260919/pilot_controller_controls.json.
Diese Testprozesse sind keine Office-Messungen. Der echte Office-Pilot ist
zum Veröffentlichungszeitpunkt noch NICHT gestartet.

## Ausführung

Der neue Starter wird als vollständige zusätzliche Datei mit SHA256 geliefert.
Nach Installation ist ein einzelner Aufruf von `office_pilot.py` im bestehenden
Paket ausreichend. Er startet vier aufeinanderfolgende Kurzläufe, sofern alle
Kontrollen grün sind. Zeitbedarf ungefähr vier bis fünf Minuten bei freier CPU.
Keine Wiederholung der bereits bestandenen großen Encoderkontrollen nötig.
