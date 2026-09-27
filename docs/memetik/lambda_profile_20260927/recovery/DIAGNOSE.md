# λ-Profil: Diagnose und Wiederaufnahme 1.0.1, 27.09.2026

Originalpaket: c8df6bbed25770479f49dd68fc5aab40e61b6bf6.
Eingangsarchiv: ryzen_lambda_profile_100_20260927_results.tar.gz,
SHA256 8a95e0a04416dd15acf620b7f54e5ea4389434ce0031fe2b266c700bd8b0d7fb.

## Ursache und Prüfung

Der Controller brach nach 3087,7683315 Windows-Hostsekunden in seiner
Speicherplatzmessung ab. Zwischen `is_file()` und `stat()` verschwand
`jobs/2076_k32/work.sqlite-journal`. Reguläres SQLite-Verhalten traf auf
einen unbehandelten Wettlauf im Controller. Der finally-Pfad beendete und
verbuchte alle Worker; keine offenen Sitzungen oder CPU-Reservierungen.

Archivhash, eingefrorene Paketdateien, alle Task-/Resultat-/Checkpoint-Receipts,
20 SQLite-Integritätsprüfungen, lückenlose Episodenindizes, Seedbindung und
CPU-Abrechnung geprüft. 5099 Episoden, zwölf vollständige Zellen, acht
angefangene Episoden. 617 unterschiedliche Endgraphen mit vorhandenem
unabhängigem Verifier und pynauty 2.8.8.1 erneut nachgerechnet: alle Kennzahlen,
λ-Bedingungen und Isomorphieklassen stimmen. Kein besserer Endpunkt nach
(W,L1). Nicht alle Pfade und Minima erneut exhaustiv geprüft.

Such-CPU und Belege stimmen bis Rundungsfehler überein. Aux-Belege liegen
6 Mikrosekunden über dem Ledger: `close()` fragt `own_cpu()` für Verbuchung
und Sitzungsbeleg zweimal ab. Audit-Toleranz hierfür 1 Millisekunde; keine
Budgetüberschreitung. Insgesamt rund 8,35 verbuchte CPU-Stunden.

## Wiederaufnahme

Separates Verzeichnis `ryzen_lambda_profile_100_20260927_recovery_101`.
Originalverzeichnis und ursprünglicher Programmbaum bleiben unverändert.
Ein vollständiger Controller und Kampagnentreiber werden separat unter
`recovery/` eingefroren. Worker, Suche, RNG, Zielfunktion und Taskdefinitionen
sind unverändert. Dateiüberwachung verwendet einen einzigen `stat` pro Datei,
behandelt ausschließlich `FileNotFoundError` als normalen Dateiverschwund
und reicht andere Fehler weiter.

Die Wiederaufnahme akzeptiert nur den anhand INPUTS.json fixierten,
geprüften Snapshot, prüft Receipts/SQLite erneut, hält den Originallock und
verweigert bestehende Zielverzeichnisse. Alte CPU-Zähler und aktive
Hostlaufzeit werden übernommen; 30 CPU-Sekunden zusätzlich für Vorbereitung
und Start reserviert. Neues Clock-Probe-Job vermeidet die Wiederverwendung
des abgeschlossenen Probes für die CPU-Verfügbarkeitsmessung. Alte Kontrollen
und Kalibrierung bleiben erhalten. Das alte Diagnoseergebnis wird in der
Kopie als PRE_RECOVERY_RESULT.json archiviert.

Limits bleiben 3600 CPU-Sekunden je Zelle, 7200 Aux-Sekunden und vier aktive
Hoststunden kumuliert. Insbesondere lange k-Zellen werden voraussichtlich
vor 300 Episoden ihr Budget erreichen. Das ist ein unvollständiges Profil,
kein erneuter Programmfehler und kein Erschöpfungsnachweis.

## Tests und Grenzen

- Simulierter Journal-Dateiverschwund behandelt; PermissionError bleibt Fehler.
- Echte gespeicherte k12-Episode auf Cloud-Kopie fortgesetzt: alter Pfadpräfix
  erhalten, alte Episoden byteidentisch, CPU-Zähler und andere Zellbudgets erhalten.
- Originalsnapshot nach Test hashidentisch; Zielüberschreiben verweigert.
- Reduzierte vollständige Kampagne mit zwei Zellen: COMPLETE, frischer Clock-Probe.
- Cloud-Tests nutzen FakeHost, nicht die reale Windows-Uhr. Die unveränderte
  Host-Anbindung muss beim Ryzen-Start wieder erfolgreich sein.

Die erste Cloud-Entpackung scheiterte nur beim Übernehmen von UID/GID 1000;
mit --no-same-owner erfolgreich wiederholt. Ein erster CPU-Audit mit
1-Mikrosekunden-Toleranz meldete die oben erklärte 6-Mikrosekunden-Differenz;
anschließend mit expliziter 1-Millisekunden-Toleranz wiederholt.

Reproduktion: Audit mit `tools/memetik/audit_python.py --` und
`experiments/memetik/lambda_profile_recovery_1_0_1/audit.py ARCHIVVERZEICHNIS`.
Tests analog mit `tests.py ARCHIVVERZEICHNIS`. Lokale Testdaten werden nur
in temporären Kopien verändert. README im Wiederaufnahmepaket beachten.
