# K1: verknüpfter Wiederanlauf nach WSL-Unterbrechung, 01.10.2026

Ralph hat die Fortsetzung am 01.10.2026 09:06 MESZ autorisiert. Der ursprüngliche
Lauf wird nicht verändert oder als sauber beendet ausgegeben. Diagnosearchiv:
`ryzen_lambda_k1_100_20260929_diagnose_20261001.tar.gz`, SHA256
`21faeaa0b70db1fd6db9f1759ec32df4ea5484ec0a53d4198c68de2658f746cd`.

336 Aufgaben abgeschlossen: A64, B200, C1 48, C2 24. Zwölf weitere B-Aufgaben
unterbrochen, 172 unbegonnen. Es fehlen zwölf wait4-Endbelege und die endgültige
Controller-/Hosthelfer-Abrechnung. Letzte Ledger-Hostdauer 104732.523999 s;
WSL am 01.10. um08:20:45 neu gestartet. Kein belegter Windows-Neustart, keine
belegte Absturzursache. Die alten Kernelmeldungen sind nicht verfügbar.

## Wissenschaftlicher Vertrag

Neuer Ordner `ryzen_lambda_k1_100_20260929_recovery_101`; 184 Aufgaben mit exakt
identischen Taskobjekten, Gründern, Budgets, Seeds, LP-/Radiusparametern wie zuvor.
Zwölf neue Vollversuche ersetzen für den Hauptvergleich die unterbrochenen
Versuche; deren Beobachtungen bleiben separat. Keine geretteten Incumbents als
neue Hints: alle184 starten vom ursprünglichen Gründer. Die ausgewählten Aufgaben
bilden46 vollständige Vierer-Vergleichszellen. Modell, Solver und Ziel bleiben gleich.
Die336 Abschlüsse bleiben ausschließlich im byteidentisch eingebetteten
Vorgängerarchiv und in der Zuordnung erhalten; keine neue Buchung ihrer CPU.

Neue Suche184CPUh, neue harte Abschnittsgrenze216CPUh inklusive24CPUh Hilfskonto
und Nachlauf; neue aktive Hostgrenze48h. Zwölf Worker; RAM-/Plattenreserven und
weiche Nachlauftoleranzen unverändert. Erwartete Dauer bei bisherigem Durchsatz
ungefähr16h, keine Abschlussgarantie. Keine automatische Budgetübertragung.

Alte verbuchte CPU344.1138166822222h; unverbuchter Rest bleibt ausdrücklich
unbekannt. Die zwölf alten Worker hatten zusammen12.1CPUh Reservierungen, und
der gesamte alte Hilfsetat war24CPUh. Bekannte alte Aufgaben-CPU plus diese
Planungsreserven plus216CPUh neuer Abschnitt bleiben unter der ursprünglichen
672CPUh-Freigabe. Diese Rechnung ist eine Budgetvorsorge und kein Messbeleg
für die tatsächliche alte Gesamtnutzung. Weder alte Gesamt-CPU noch alte
Gesamt-Walltime werden nachträglich als exakt zertifiziert ausgegeben.

## Integrität und Wiederanlauf

Starter prüft den archivierten SHA, alle wissenschaftlichen Originaldateien
samt Logs/Ledger/Receipts, Prozessfreiheit und Original-Lock. Bytecode und
Lockdateiinhalt sind vom Dateiinventar ausgenommen. Neue Dateien oder Änderungen
am Original führen zum Diagnoseabbruch. Bestehendes Ziel wird nie überschrieben.
Das Originalarchiv wird ins neue Ergebnisverzeichnis kopiert und bei Launch,
Audit und Export erneut gehasht. Status weist184 Abschnittsaufgaben und520
Gesamtaufgaben getrennt aus. Die alte unbekannte CPU bleibt `null`.

Alle mathematischen Kontrollen sowie der reale Windows-/WSL-Uhren- und
Zwölfworker-Test laufen vor neuer Produktion. Ein neuer atomarer Heartbeat
speichert alle30Hostsekunden Boot-ID, UTC, live Worker-CPU und Controller-/
Hosthelfer-CPU. Er ersetzt keine wait4-Endbelege und bewirkt keine automatische
Wiederaufnahme. Regeln GC-01/02/06/09/10/14/15.

## Aussageumfang der bisherigen Prüfung

Originalpaketprüfsummen und Ergebnis-Hashes stimmen.350 vorhandene CPU-Receipts
stimmen mit dem Ledger einschließlich70s CLI-Reservierungen überein.647 aktuelle
Best-/Kandidatendateien sowie8192 Katalogeinträge und sekundäre λ-Incumbents
wurden auf gespeicherte Graph-/Scorebedingungen geprüft. Beste W-Werte in A/B/C1
2076, beste Packing-Kantenzahl546. Kein kompletter Sitzungsaudit, keine
kanonische Auswertung, keine zertifizierten Solver-Ausschlüsse.
