# λ-Radius 1.0.0: deterministische lokale Untersuchung auf dem Ryzen

Autorisiert am 26.09.2026: Vorschlag aus
`docs/memetik/lambda_review_20260926/ABGLEICH_UND_VORSCHLAG.md` umsetzen.
Keine neue P-Kampagne, keine Migration, kein Crossover und kein Abstieg nach Fund.

## Ablauf

1. Isoliertes eigenes Laufverzeichnis; Eingaben, Quellen und Python/pynauty-Identität
   einfrieren. Bestehende Suchläufe und ihre Umgebungen bleiben unverändert.
2. Windows-Host-Uhr und wait4/Host-Intervallkontrolle; unabhängige Vollbewertung
   aller 194 direkten Nachbarn beider Rekordgraphen einschließlich Inversenprüfung.
   Bekannte Vier-Zug-Verbindung W2079→W2076 im Meet-in-the-middle neu erzeugen
   und jeden Schritt unabhängig nachrechnen.
3. Vollständige beschriftete Schichten 0, 1, 2 aufbauen. Erwartet: 99/5222 und
   95/4768 Zustände in Schicht 1/2. Keine Isomorphiereduktion.
4. Alle Nachbarn der Tiefe-2-Zustände, aufgeteilt in disjunkte ID-Intervalle,
   bewerten. Erwartete Kindzahlen: 526476 und 459185; keine Verbesserungen.
   Jede Abweichung verhindert den anschließenden Tiefe-4-Start.
5. Deduplizierte Vereinigung der vollständigen Schichten 0..3 in SQLite bilden.
   Ursprüngliche Eingabezustände auf niedrigster Tiefe behalten. Kurze CPU-
   Hochrechnung anzeigen, ohne Vollständigkeit innerhalb des Budgets zu versprechen.
6. Alle Nachbarn aller verschiedenen Zustände genau auf Tiefe 3 prüfen. Zusammen
   mit den bereits geprüften unteren Schichten ist damit Radius ≤4 abgedeckt.
   Die beiden Arme werden verschachtelt eingereiht, mit höchstens zwölf Workern.
7. Beim ersten unabhängig replay-geprüften Verbesserungszeugen endet nur der
   betreffende Arm. Der andere Arm behält sein eigenes Budget. Kein Folgeabstieg.

Startgraphen werden durch vollständige state-Hashes in STARTS.json festgelegt;
W allein ist ausdrücklich kein eindeutiger Bezeichner. Operatorcode aus a4d4396
ist byteidentisch gepinnt; keine Änderung an früheren Quellen.

## Harte Grenzen und Zeit

- Hilfsarbeit insgesamt ≤7200 CPU-s, einschließlich Kontrollen, Schichten bis 3,
  SQLite-Vereinigung, Steuerung und Windows-Helfer. Vorbereitung und Start erhalten
  je eine konservative, dokumentierte 10-s-Reserve innerhalb dieses Budgets.
- Tiefe 4: je Arm ≤72000 CPU-s. Alle Worker-Sitzungen werden über wait4 abgerechnet,
  auch unterbrochene oder fehlgeschlagene. Keine Übertragung zwischen Armen.
- Höchstens zwölf Worker; Threads numerischer Bibliotheken auf eins begrenzt.
- Die Allokationen aktiver Worker werden vor dem Start reserviert. Jeder Worker
  hat kooperative CPU-Grenzen und RLIMIT_CPU; Schlussreserven bleiben ungenutzt.
- Gesamter Lauf ≤8 Windows-Host-Stunden über saubere Wiederaufnahmen summiert.
- Gesamter eigener RSS-Rahmen 8 GiB, Ausgabedatenrahmen 10 GiB; Pause bei weniger
  als 6 GiB verfügbarem RAM oder 25 GiB freier Linux-/Windows-VHDX-Partition.
  Speicher-/Diskgrenzen werden periodisch geprüft, nicht als Kernel-Quota gesetzt.
- Planung 4–6 Stunden bei zwölf freien Ryzen-Kernen; tatsächlicher Durchsatz
  wird ausgewiesen. Ressourcen oder Budget können eine vollständige Antwort verhindern.
- Walltime, Zehn-Minuten-Status und ETA beruhen auf dem persistenten Windows-
  Stopwatch-Helfer. Linux-Monotonzeit wird nur für kurze Poll-Abstände verwendet.
  Ein fehlender Host-Helfer führt nicht zu einem vorgetäuschten erfolgreichen Test.
- Export ist eine separate nachgelagerte Dateioperation, keine Verlängerung der Suche.

## Checkpoints und Ergebnisbedeutung

Jeder vollständig ausgewertete Elternzustand ist eine SQLite-Transaktion.
Unterbrechung während eines Elternzustands rollt diesen zurück; seine CPU-Kosten
bleiben im wait4-Ledger. Beim Fortsetzen wird er neu berechnet. Quell-/Task-
Fingerprints und Receipthashes verhindern stilles Fortsetzen geänderter Daten.
Ein hart abgebrochener Controller hinterlässt bewusst eine ungelöste Sitzung;
vor Wiederaufnahme sind Prozesse und CPU-Abrechnung zu diagnostizieren.
Kein automatisches Zurücksetzen von Budgets oder Löschen solcher Sperren.

`VERIFIED_IMPROVEMENT_DEPTH4`: replay-geprüfter Pfad mit besserem (W,L1),
nicht zwingend neuer globaler W-Rekord. Dieser verlangt W<2076.

`COMPLETE_NO_IMPROVEMENT_DEPTH4`: alle vorgesehenen Arbeitseinheiten abgeschlossen,
exakte Zahl der Tiefe-3-Eltern abgedeckt, untere Schichten zuvor vollständig geprüft.
Aussage ausschließlich über diesen Startgraphen und den fixierten Katalog.

`INCOMPLETE`: Budget-/Ressourcen-/Zeitgrenze oder saubere Benutzerpause; kein
negatives mathematisches Ergebnis. Gesicherte Arbeit bleibt erhalten.

`LOWER_DEPTH_COUNTEREXAMPLE`: unabhängig bestätigte Verbesserung bereits bis
Tiefe 3; Widerspruch zum Review wird gespeichert, Tiefe 4 nicht automatisch gestartet.

`DIAGNOSIS_REQUIRED`: technischer Fehler, Hash-/Abdeckungs-/Scoreabweichung oder
Budgetüberschreitung. Bestehende fremde Prozesse werden nicht angefasst.

## Dateien und Bedienung

Eigenes Laufverzeichnis:
`$HOME/conway99_workspace/ryzen_lambda_radius_100_20260926`.

CLI im eingefrorenen Programm: `run.py`, Aktionen `status`, `pause`, `launch`,
`export`; jeweils mit dem Laufverzeichnis als Argument. `start.py` im ZIP führt
Vorbereitung und Hintergrundstart aus. Eine Wiederaufnahme erweitert keine Limits.

`controller.log` enthält Meldungen bei Phasenwechseln und alle zehn Minuten.
`status.json` enthält den letzten Status, `RESULT.json` den End-/Pausenbericht,
`ledger.json` CPU-Abrechnung, `DEPTH3_VERIFIED.json` die vollständige Vorprüfung,
`CALIBRATION.json` die Laufzeithochrechnung und `WITNESS_*.json` etwaige Zeugen.
Der Startmeldungs-PID allein bestätigt noch nicht bestandene Kontrollen.

Tests: `tests.py` nutzt den vorgeschriebenen Audit-Python und eine ausdrücklich
als Test markierte native Uhr. Mathematische Kontrollen, positiver Tiefe-4-Fall,
Transaktionsabbruch/Resume, Deduplikation, wait4 und Budget-/Crashsperren werden
lokal geprüft. Ein echter WSL-/Windows-Test erfolgt erst auf dem Ryzen.

## Lokale Prüfbilanz vor Veröffentlichung

- TEST_RESULTS.json: 194 direkte Nachbarn unabhängig bewertet und Rückzüge
  geprüft, positiver Vier-Zug-Zeuge, transaktionale Wiederaufnahme, Merge,
  wait4, Budgetende und Sperre nach unklarer Sitzung bestanden.
- INTEGRATION_RESULTS.json: echte Schichten 1/2 beider Arme vollständig
  reproduziert; zusätzlich 582 Kinder aus sechs verteilten Tiefe-2-Zuständen
  unabhängig bewertet, aufgeteilte Zustandsmengen exakt gleich; aktuelle
  Steuerung und Ablehnung manipulierter Ergebnisse bestanden.
- RUNTIME_RESULTS.json: Fund beendet nur den betroffenen Arm; anderer Arm
  läuft zu Ende; Wiederaufnahme erzeugt keine zusätzliche Suche; Abbruch
  nach vier tatsächlichen SQLite-Inserts rollt den Elternzustand vollständig zurück.
- PACKAGE_TEST_RESULTS.json: eigenständige ZIP-Vorbereitung, Schutz bestehender
  Laufverzeichnisse, Ablehnung ohne Windows-Uhr und bei Quellenmanipulation bestanden.
- Vollständige Tiefe 3 und Tiefe 4 sind nicht vorweggenommen; sie sind der
  autorisierte Ryzen-Lauf. Echter WSL-/Windows-Start ist hier nicht ausgeführt.
