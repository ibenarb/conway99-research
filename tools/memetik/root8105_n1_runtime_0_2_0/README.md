# N1-Runtime 0.2.0 – explizite Recovery

Basis: 9a4637f67207f6bc17ab028c93210af5a35ad772.
Vertrag: 34c51bd80e040bb705fdb68ae13b1074f9a3c8b5.
Eigenes Versionsverzeichnis; 0.1.0 und seine Archive bleiben unverändert.
Status: CLOUD_PROTOTYPE, KEINE PRODUKTIONS-/RYZEN-FREIGABE.

## Dieses Paket

runtime.py verwaltet unveränderliche, gehashte Zustandsgenerationen im Verzeichnis states. state.json ist nur eine nachgeschriebene Komfortkopie. Statusabfragen lesen die höchste vollständig veröffentlichte Generation; temporäre Dateien zählen nicht. Der atomare Commit einer Antwort enthält Budgetänderung und Antwort-ID zusammen. Ein Generationenname wird niemals überschrieben; Schreiben aus einem alten Snapshot schlägt fehl.

recovery.py ergänzt recover (lesender Plan) und recover --apply (ausdrückliche Wiederherstellung). Beide benötigen die exklusive Supervisorsperre. Apply erhält die alten Cachebytes im Verzeichnis recovery und schreibt Bericht sowie neue Generation. Es werden keine ursprünglichen Versuchsdateien repariert oder gelöscht.

Jeder Kindprozess erhält vor Start einen Launch-Intent, nach Start seine Identität und nach wait4 einen phasenbezogenen Endbeleg mit CPU und Ausgabedateihashes. Such-/Prüferkonten werden aus diesen disjunkten Endbelegen rekonstruiert, nicht aus einer möglicherweise veralteten Gesamtsumme. Ein gültiger Phasenbeleg darf auch dann übernommen werden, wenn der anschließende Supervisorstatus oder der komplette Versuchsabschluss fehlt.

Ein beendeter erfolgreicher UNSAT-Suchprozess liefert einen versiegelten Proof-Quellversuch. Bei UNSAT_UNCERTIFIED startet resume ausschließlich den externen Prüfer in einem neuen Versuch. Der Verweis auf den alten Beweis bindet Quellversuch, Original-CNF und Proofhash. Keine erneute Suche, kein Anhängen an einen Teilbeweis. Auch nach einem realen Supervisorabsturz zwischen Phasenbeleg und Statuscommit funktioniert dieser Pfad. Bereits zertifizierte Fälle werden ohne Neuberechnung übernommen.

## Bewusste Sperren

- Lebender verwaister Prozess: keine Adoption, kein Signal durch recover, kein Doppelstart.
- Startfenster ohne gespeicherte Kindidentität: manuelle Reconciliation erforderlich; keine Behauptung, es sei kein Kind gestartet.
- Fehlender wait4-Endbeleg: cpu_s=null, letzte gemessene Untergrenze getrennt, accounting_complete=false. ACCOUNTING_INCOMPLETE sperrt resume. Der fehlende Endverbrauch wird weder als null Sekunden noch als rekonstruierbar behauptet.
- Beschädigte maßgebliche Zustandsgeneration: keine stille Rückkehr zu einem älteren Budget-/Antwortstand. Gültige Vorgänger bleiben erhalten, automatische Recovery bleibt gesperrt.
- Beschädigte versiegelte Eingaben, Quellen, Proofs, Endbelege oder SAT-Zeugen: Abweisung.
- Tool- und Versionswechsel: keine automatische Migration alter Runverzeichnisse. Nur in diesem Versionsverzeichnis neu initialisierte Kontrollläufe wurden abgenommen.

## Tests und Grenzen

11/11 neue Recoverytests und 16/16 bestehende Funktionsprüfungen bestanden; Belege unter docs/augmentation/root8105_n1_recovery_20261007. Tests verwenden echten CaDiCaL-Worker und echten drat-trim. Ein als solcher archivierter Prüfadapter führt den echten Prüfer aus und verzögert danach den eigenen Abschluss, um VERIFIED-vor-Prozessende und 0-Abbruch zu prüfen. Er ist kein Produktionsprüfer.

Gezielte Prozessabbrüche verwenden os._exit(91) ausschließlich bei gleichzeitig gesetztem N1_TEST_FAULT und vorhandener ALLOW_TEST_FAULTS-Datei im Testlauf. Fehler vor Dateiersetzung benötigen N1_TEST_WRITE_FAIL und denselben Testmarker. Diese Injektionen sind keine Laufzeitlimits. Nach einem simulierten Supervisorverlust wird ein noch lebender synthetischer Solver nur im Test durch seinen eigenen STOP-Kanal kontrolliert beendet. Fehlende Schlusskonten bleiben danach sichtbar.

Quellen der drei fehlgeschlagenen Zwischenstände sind aus den lokalen Bearbeitungsschritten rekonstruiert und gegen die zur Ausführung gespeicherten runtime_sha256-Werte geprüft worden. Auch ihre Belege bleiben erhalten. Historische Forschungsdaten und laufende Nutzerprozesse unberührt.

Noch offen: N1-Dekodierung/Modellprüfung, Host-Stopwatch/Windows-WSL, gesamte Supervisor-/Host-Endabrechnung, Kampagnengesamtbudgets, Ressourcen-Notfallsteuerung. Die Kindes-CPU-Konten sind exakt, soweit wait4-Belege vorliegen; das ist keine lückenlose Gesamtkampagnenabrechnung. Keine echten Stromausfall-/Datenträgertests. Die Speicherung aller Generationen ist für diesen kleinen Prototyp ausgelegt; Skalierung/Archivierung ist vor langen Produktionsläufen gesondert nötig. Keine nicht geprüfte beliebige Crash-/Speicherfehlertoleranz behaupten.

## Reproduktion und nächste Grenze

build.py baut die unveränderten fixierten nativen Abhängigkeiten wie in 0.1.0. worker.cpp ist byteidentisch zu 0.1.0; der bereits daraus gebaute Worker wurde verwendet. Die beiden Tests sind Python-Einstiege test_runtime.py und test_recovery.py, jeweils mit --output (neues Verzeichnis), --worker und --checker (absolute Binärpfade). Kein automatischer Produktionsstart.

Nächstes abgegrenztes Paket: N1-Inputbindung und unabhängige dekodierte SAT-Zeugenprüfung integrieren und mit kleinen positiven/negativen Kontrollen testen. Danach bleibt die Zielhardwarefreigabe ein eigener Schritt.
