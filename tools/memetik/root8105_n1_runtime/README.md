# N1-Laufsteuerung: Cloud-Prototyp 0.1.0

Basis/Vertrag: 34c51bd80e040bb705fdb68ae13b1074f9a3c8b5, docs/augmentation/root8105_n1_contract_20261007/VERTRAG.md.
Status: 16 synthetische Linux-Cloudtests bestanden. KEINE N1-/RYZEN-PRODUKTIONSFREIGABE.

## Enthalten

- worker.cpp: nativer CaDiCaL-2.2.1-Worker, streng gelesene DIMACS-CNF, unmittelbare binäre DRAT-Ausgabe ohne stdio-Puffer, kooperatives Stopflag mit terminate(), fsync und Abschlussmetadaten. Ungenutzte deklarierte Variablen werden reserviert.
- runtime.py: genau eine CNF und ein Kindprozess zur Zeit; eigener dauerhafter Supervisor, unabhängige Bedien-CLI, fcntl-Besitzsperre, /proc-Live-CPU und wait4-Endkonten, atomare gehashte Zustände und Antwortquittungen, versiegelte Versuche. Budgetumfang ausdrücklich native Kinder (Suche + Prüfer); Supervisor-CPU separat, noch kein vollständiges Gesamtkampagnenkonto.
- test_runtime.py: 16 echte Prozess-/Integritätsprüfungen, darunter SAT, UNSAT/DRAT, synthetisches Schubfachproblem für Abbruch und Fortsetzung. Keine N1-Klasse.
- build.py: reproduzierbarer Build in neuem Verzeichnis; Quellcommits festgelegt, keine Solver-/Prüferänderung, kein harter Timeout.
- Testbelege und Fehlerdokumentation: docs/augmentation/root8105_n1_runtime_20261007.

## Semantik und Bedienoberfläche

Linux-Python-CLI: init richtet ein neues Runverzeichnis mit --cnf, --worker, --checker und --budget ein. run bleibt als Supervisor aktiv. status liest nur. reply benötigt --request, --seconds und optional --answer-id. Negative oder nicht ganzzahlige CLI-Werte sind ungültig. resume erlaubt ausdrücklich einen neuen Versuch nach STOPPED_UNRESOLVED; fertige geprüfte Ergebnisse werden vor Wiederverwendung auf Dateiänderungen geprüft.

Budgetart ist native_children_cpu_seconds, nicht Walltime. EOF beendet keinen Lauf. Antwort 0 erzeugt bei Suche eine STOP-Datei für den nativen Worker; der Supervisor bleibt bis wait4 und Versiegelung aktiv. Beim Prüfer wird dessen eigener Prozess mit SIGTERM beendet; unveränderte Eingaben bleiben erhalten. Das ist keine Solver-Kill-Eskalation. Keine automatische Frist für Nachlauf. Verschobene/replizierte Antworten werden über IDs und atomare Buchung dedupliziert. Reconnect bedeutet status/reply zum bestehenden Supervisor; ein zweiter run wird abgewiesen.

Für synthetische Tests aus dem Repositorywurzelverzeichnis ist der reproduzierbare Einstieg:
`python tools/memetik/root8105_n1_runtime/build.py <neues-buildverzeichnis>`
Danach:
`python tools/memetik/root8105_n1_runtime/test_runtime.py --output <neues-testverzeichnis> --worker <absoluter-pfad-zum-n1-worker> --checker <absoluter-pfad-zu-drat-trim>`
Dies dokumentiert die Reproduktion, erteilt keine Startfreigabe für Nutzerhardware oder Forschungsinstanzen.

## Offen vor Produktion

Dieser Prototyp setzt den Vertrag noch nicht vollständig um. Insbesondere:

1. SAT_CNF_VERIFIED bedeutet nur vollständige Klauselprüfung. N1-Dekodierung und unabhängige Modellprüfung sind noch nicht integriert; niemals SAT_N1_VERIFIED behaupten.
2. Nach unterbrochenem Checker bleibt UNSAT_UNCERTIFIED erhalten; resume unterstützt diesen Status bewusst noch nicht. Die Wiederaufnahme allein der Prüferphase aus versiegeltem vollständigem Beweis fehlt.
3. Nach Supervisor-/Hostcrash wird ein ungeschlossener Zustand abgewiesen. Es gibt noch kein geprüftes Recoverywerkzeug, keine automatische Prozessadoption, keine Crash-Endabrechnung und kein getestetes Hardwaresicherungskonzept. Letzte Liveprobe ist keine Endabrechnung. Alte Zustände werden nicht automatisch repariert.
4. Atomare aktuelle Statusdatei und geschlossene Versuche sind gesichert; rotierende Generationen/letzter gültiger Vorgänger, Fehlerbehandlung während Speicherung und vollständige Reconciliation sind noch zu implementieren. Defekte Datei wird abgewiesen, nicht still ersetzt.
5. Keine Host-Stopwatch, kein Hosthelfer, keine Gesamtbudgets/mehreren Scopes, keine N1-Manifest-/Abdeckungsintegration, kein Mehrworkerplaner und keine RAM-/Platten-Notfallsteuerung.
6. Worker-/Prüferabbruch bei jeder möglichen Phasengrenze, verzögerter Prüferschluss nach VERIFIED, injizierter Strom-/Controllerverlust, konkurrierende verschiedene Antworten und Dateisystemfehler sind noch nicht vollständig abgenommen.
7. Die Tests belegen atomare Deduplizierung im normalen Betrieb und erneute Zustellung, keinen tatsächlich injizierten Crash zwischen Buchung und ACK.
8. Buildwarnung des unveränderten drat-trim: implizite getc_unlocked-Deklaration bei -std=c99. Echter Prüferlauf und Negativkontrolle bestanden. Abhängigkeiten und Compiler dokumentiert, keine Leistungsprognose.
9. Status/Endreceipt weist Supervisor-CPU separat aus, jedoch noch nicht alle Start-/Abschlusskosten lückenlos. native Kinder werden durch wait4 exakt abgerechnet; Produktionsgesamtabrechnung bleibt offen.

Nicht als allgemeine Behebung der früheren Speicher-/Uhrenprobleme ausgeben. Keine Forschungsrechnung, kein Rootausschluss, keine Ryzen-Anweisung. Historische CPU-Lücke der 960er-Diagnose unverändert.

Nächstes abgegrenztes Paket: Recovery der Prüferphase und des Supervisorzustands ergänzen und mit gezielt injizierten Prozess-/Speicherfehlern prüfen. Danach bleiben N1-Integration und Zielhardwareabnahme gesondert.
