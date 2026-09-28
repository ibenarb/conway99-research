# Diagnose und Wiederaufnahme λ-Reparaturpilot — 28.09.2026

## Ergebnis des unterbrochenen Laufs

Start 27.09.2026 gegen 16:46 Uhr; Ende 17:47:30 MESZ.
Aktive Hostzeit: 3684,4482012 s. Abgerechnet: 42833,936141 CPU-s
(11,8983155947 CPU-h). 39 CPU-Receipts, keine offenen Reservierungen,
keine aktive Sitzung, keine Worker-error.json.

29/144 Aufgaben beendet: 23 OPTIMAL_UNCERTIFIED, fünf
RIGID_BOUNDARY_VERIFIED, eine CPU_LIMIT_UNKNOWN. Keine dieser
CP-SAT-Optimalitätsmeldungen ist ein unabhängig geprüftes Ausschlusszertifikat.
Bester gespeicherter Wert W=2076, keine lexikographische Verbesserung
gegenüber den jeweiligen Gründern. 115 Aufgaben sind noch nicht beendet.
Die Aussage betrifft diesen unvollständigen Lauf, nicht die Reparaturmethode.

## Ursache und genaues Ausmaß

Receipt 13, Aufgabe 2076_01_s60_defect:
Reservierung 3540,661237 s; tatsächliche wait4-CPU 3541,832848 s;
Überschreitung der Reservierung 1,171611 s.
Interne letzte Messung 3540,156673 s; danach weitere 1,676175 CPU-s.
Mit Kalibrierung 58,338763 s: 3600,171611 s insgesamt,
also 0,171611 s über der vorgesehenen Aufgabenstunde.

Die bisherige Reserve von zwei CPU-Sekunden und die Elternschwelle
von einer CPU-Sekunde reichten für Solver-Stopp und Prozessende nicht.
Der globale Abbruch war angesichts des vollständig abgerechneten,
kleinen Überschreitungsbetrags betrieblich zu empfindlich. Die genaue
Verteilung auf Solver-Nachlauf, Ergebnis-I/O und Objektfreigabe wurde
nicht gemessen; hierzu wird keine erfundene Profilierung behauptet.

## Entscheidung 28.09.2026

Der Nutzer hat die vorbereitete Wiederaufnahme 1.0.1 nicht gewählt.
Sie wurde erstellt und getestet, aber hier nicht als auf dem Ryzen gestartet
bestätigt. Stattdessen wird Version 1.1.0 vollständig neu gestartet; der
Fehllauf bleibt getrennt erhalten. Grund: früher technischer Abbruch,
zu empfindliche globale Abbruchpolitik, bessere Nachvollziehbarkeit eines
neuen Versuchs als einer nachträglich migrierten Einzelfallausnahme.

Die 0,171611 s bleiben eine tatsächliche Abweichung vom ursprünglichen
Aufgabenbudget. FAILED_RUN_AUDIT.json bestätigt die vollständige Abrechnung
und Kandidatengültigkeit unter ausdrücklicher Dokumentation dieses Einzelfalls.
Der alte Lauf wird nicht in einen uneingeschränkten PASS umetikettiert.

Ein erster Cloud-Integrationstest des verworfenen Wiederaufnahmepakets sah
eine bereits gelöschte Sitzungsdatei erneut; eine vollständige Wiederholung
in einem separaten temporären Verzeichnis bestand. Ursache nicht abschließend
profiliert; dies ist keine Behauptung eines identischen Ryzen-Problems.

Reproduktion des historischen Audits: Projekt-Auditpython, dann
forensic_audit.py ARCHIVVERZEICHNIS. Nur der exakte SHA256 von Receipt 13
wird als bekannte Abweichung ausgewiesen; neue Abweichungen werden verworfen.
