# C2 LOW Pilot 1.0.1

Dieses Paket bereitet 72 Aufgaben vor: 32 vollständige R-Fälle, dieselben 32
notwendigen X-Modelle und acht vollständige MIN-Vergleichsfälle. Es ist keine
vollständige Ausschlusskampagne für die 3.152 LOW-Wurzeln.

## Installation und erster Schritt

Der Installer installiert nach ~/conway99_workspace/C2_LOW_Pilot_1.0.1,
prüft Dateihashes, entpackt die festgelegte F0-Basis, erzeugt die 72 Formeln
und führt die Kontrollsuite aus. Er startet keine Pilotaufgaben.
Eine bestehende Installation wird nicht überschrieben.

Voraussetzungen: Linux x86_64, Python 3.10 oder neuer; unter WSL2 Zugriff auf
Windows C und funktionierendes PowerShell/Get-CimInstance. Keine pip-Installation.
Die mitgelieferten nativen Binärdateien stammen aus der bisherigen Werkzeugkette.

Erst nach erfolgreichem LOW_PREFLIGHT_PASS wird der Start besprochen.
Der spätere Befehl `python3 run.py start --stage initial` startet 16 Aufgaben,
je eine R- und X-Aufgabe aus jeder der acht L-Familien. Nach diesem Teilpanel
endet die Freigabe. `--stage all` ist eine gesonderte Freigabe der restlichen Aufgaben.
Keine Aufgabe wird allein wegen einer abgelaufenen Zielzeit beendet.

## Mathematische Reichweite

FULL/R: unveränderte F0-Basis plus 132 lokale Matchingfestlegungen und Regel R.
FULL/MIN: dieselbe F0-Basis plus lokale Festlegungen und die Minimumausgradregel.
R und MIN sind alternative Überdeckungen, keine kumulativen Bedingungen.
F0-SHA256: 7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd.

X: notwendiges Verbindungsmodell mit 720 Primärbits, Nichtkantenmarkierung,
Kreuzblockgleichungen, Ankerinzidenzen und den korrigierten Lemma-K-Ungleichungen.
Globale R-Bedingungen werden darin nicht als bereits projiziert vorausgesetzt.
INTERFACE_VERIFIED_ONLY ist ein verifiziertes Zwischenmodell, kein Conway-99-Graph.
Ein UNSAT_CERTIFIED des X-Modells schließt die entsprechende lokale Struktur
unter dem dokumentierten notwendigen Übergang aus.

Die fehlerhafte unqualifizierte Schmetterlingsklausel aus Review 02 ist nicht enthalten.
Historische F346-Muster werden nicht unzulässig auf F0 übertragen.
Die vollständigen Fälle enthalten absichtlich noch keine weiteren experimentellen
redundanten Klauselschichten. Zunächst wird diese überprüfbare Referenz gemessen.

## Kontrollen

- 4.096 vollständige Wahrheitstabellenbelegungen des Zwölf-Eingangs-Schwellenzählers;
- unabhängige Labeldekodierung aller 3.152 mal 132 Wurzelfestlegungen;
- reale k=4-SAT-Kontrollen beider Regeln mit unabhängig geprüften Graphen;
- bekannte lokale Widersprüche in F0 und X, beide mit LRAT und cake-Prüfung;
- negativer F0-Test ohne Suchentscheidungen/Konfliktbudget;
- Laufzeit-/Pausen-/Verlängerungstests am echten Supervisor;
- kompletter Solver-/Checkerablauf an zwei negativen Kontrollformeln, Wiedereinstieg
  und absichtliche Proof-Veränderung mit erwarteter Zurückweisung.

Eine positive Conway-99-Instanz ist nicht bekannt. Die k=4-X-Kontrolle hat eine
leere Zwischenstruktur; sie ersetzt die algebraische Herleitung für 720 Bits nicht.
Eigene Herleitung und Matrixidentitätskontrollen liegen unter evidence.
Die WSL-Telemetrie wird zusätzlich bei der Installation am Zielsystem geprüft.

## Betrieb

Voreinstellung: zwei Solver, ein Checker. cake erhält 8 GiB Heap plus 512 MiB Stack.
Start-/Laufzeitwächter berücksichtigen freien Linux-RAM, unter WSL zusätzlich
freien physischen Windows-RAM, Linux-Platte und freien Platz auf Windows C.
Reserve: 8 GiB RAM, 30 GiB Platte. Bei Ressourcenmangel werden Kinder pausiert;
bei Erholung fortgesetzt. Keine pauschale Proofgrößen-Abbruch- oder Pausengrenze;
physischer freier Speicher bleibt maßgeblich, große Proofs lösen Informationsmeldungen aus.
Keine CPU-Auslastungssperre und kein Zugriff auf andere bestehende Forschungsprozesse.

Solver-Zielzeit 1.800 CPU-Sekunden, Checker-Zielzeit 3.600: Das sind Meldepunkte,
keine Laufzeitprognose und keine Abbruchgrenze. Ohne Antwort läuft der Job weiter.
`extend JOB SEKUNDEN` verlängert; **0 fordert ausdrücklich das Beenden dieses Jobs an**.
`pause JOB` und `resume JOB` steuern nur die manuelle Pause; Ressourcenwächter bleiben aktiv.
Ein pausenbedingter Dauerstillstand ist im Status mit Ursache sichtbar.

`status` zeigt Aufgaben, aktive Jobs, CPU, Ressourcenpausen und Verlängerungsanfragen.
`start` öffnet automatisch die Liveansicht; `watch` verbindet sie erneut.
Strg+C oder das Schließen des Terminals beendet nur die Ansicht, nicht Controller,
Supervisoren oder den getrennten Beobachter. `start --detach` startet ohne Ansicht.
Von Anfang an erscheint alle 15 Minuten ein Heartbeat, auch ohne neue Ergebnisse.
Er nennt erledigte/offene/aktive Aufgaben, Wand- und CPU-Zeit, Änderungen seit dem
vorherigen Heartbeat, Proofwachstum und gescannte Proofzähler (mit Scanrückstand),
I/O-Aktivität, native Solver-Logzeilen, RAM/RSS, physischen freien Plattenplatz,
Swap, Linux-Speicherdruck, Pausen und veraltete Telemetrie.
Start, Phasenwechsel, SAT vor Prüfung, UNSAT vor Zertifizierung, Prüfstart und
Prüfergebnis, verifizierte Modelle, Fehler sowie Budget- und Pausenänderungen werden
unverzüglich protokolliert und in der Ansicht ausgegeben (typisch binnen 2 Sekunden).
Ereignisse stehen dauerhaft in work/events.jsonl; Heartbeats in work/heartbeat.json.
Der Pilot erzeugt derzeit keine adaptiven Teilbranches. Es werden deshalb keine
fiktiven Branch-Ereignisse gemeldet. Interne SAT-Entscheidungen erscheinen nur in
den nativen zusammengefassten Berichten, soweit der Solver sie ausgibt.
Jeder Heartbeat weist eine unbekannte Abschluss-ETA mit Begründung und dem nächsten
Kontrollzeitpunkt aus. CPU, Proofbytes und Checker-I/O beweisen Aktivität, keine
bekannte Restarbeit. Für die endliche Formelvorbereitung gibt es eine ausdrücklich
grobe Phasenhochrechnung. Eine unbekannte SAT-Laufzeit wird nicht aus den schneller
abgeschlossenen Fällen hochgerechnet.
Eine belastbare Fund- oder Abschluss-ETA wird nicht erfunden.
`export` erzeugt ein Diagnose-ZIP mit Metadaten und Logs, ohne große CNF-/Proofdateien.
Die Originalbeweise und Formeln bleiben lokal erhalten.

Der Controller kann nach einem normalen Controllerabbruch wieder gestartet werden;
bereits laufende getrennte Supervisoren werden wiedergefunden. Ein unklarer oder
abgestürzter Supervisor wird nicht automatisch neu gestartet: Sein Kind bleibt
gegebenenfalls pausiert und die Situation muss geprüft werden. Ein WSL-/Rechnerneustart
kann native Suchzustände verlieren; es gibt keinen erfundenen Solver-Checkpoint.
Ein fehlgeschlagener Checker bleibt als Fehler offen und wird nicht als Ausschluss gezählt.

## Herkunft

Forschung: ibenarb/conway99-research, eigener LOW-Plan 007b73825da7a7dc3c04f332ef6b0cd9d215fc4c.
Private Synthese: ibenarb/conway99-review-exchange, b2901854623a14d4023e352d04ef9546805b4291.
Werkzeuge: CaDiCaL 2.2.1; lrat-trim und cake_lpr aus der bisherigen lokalen Werkzeugkette.
Exakte Binärhashes und Quellcommits: evidence/toolchain.json.
Historische Kosten: evidence/historical_costs.json, ausschließlich protokollierte
abgeschlossene Jobs einschließlich Mehrfachversuchen; keine LOW-Laufzeitprognose.
Konfliktzahlen fehlen in den hier vorhandenen Metadaten, da die entsprechenden
Textlogs nicht mit vorliegen. Fehlende Werte werden nicht geschätzt.

## Änderung 1.0.1

Nur Laufzeitüberwachung und Bedienung wurden erweitert. Alle 72 Formelhashes
müssen mit 1.0.0 übereinstimmen. Keine historischen hohen Typen werden neu gerechnet.
Die verbindlichen Rechenregeln liegen in MONITORING_POLICY.md. Diese Release erfüllt
die dort für 1.0.0 noch als fehlend bezeichneten Punkte. Die Installation erzeugt
einen eigenen Versionsordner; vorhandene Installationen bleiben erhalten.
