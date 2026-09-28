# λ-Reparatur 1.1.0: sauberer Neustart

Freigegeben von Ralph Beckmann am 28.09.2026 um 08:02 MESZ.
Der technisch gescheiterte 1.0.0-Lauf wird archiviert, nicht fortgesetzt.
Das zuvor erstellte Wiederaufnahmepaket 1.0.1 ist durch diese Entscheidung
überholt und soll nicht gestartet werden.

Wissenschaftlicher Input bleibt byteidentisch: 24 Gründer, 144 Fenster,
Seeds, Modell, unabhängiger Graphprüfer und Dependency-Lock. Neuer RUN
ryzen_lambda_repair_110_20260928. Neue Aufgaben-CPU-Konten und keine geerbten
Kandidaten, Erledigungen oder alten Verbrauchszähler.

Suchziel 3600 CPU-s je Aufgabe; explizite Nachlaufreservierung bis 20 s
je Versuch, kumuliert höchstens 60 s zusätzlicher Aufgabenrahmen. Jede
reale CPU-Sekunde zählt zum unveränderten Gesamtbudget 156 CPU-h;
Hilfsbudget weiterhin höchstens 12 CPU-h, aktive Hostzeit höchstens 24 h.
Der globale Reservierungsmechanismus begrenzt auch die Summe aller aktiven
Nachlaufreservierungen. Toleranz bedeutet keine stillschweigende Erhöhung.
Geringe erklärte Überschreitungen des Suchziels sind lokale Warnungen.
Nicht antwortende Prozesse werden lokal beendet. Lokale Workerfehler
werden separat markiert; Integritätsfehler und echte Gefahren bleiben global.

Vor produktiver Suche muss der echte Ryzen folgende Gates bestehen:
Windows-Hostuhr, zwölf parallele CPU-Probes mit zwei absichtlich um drei
CPU-Sekunden verzögerten Enden, Übereinstimmung interner CPU/proc/process_time,
vollständige wait4-Abrechnung und Nachweis weiterlaufender anderer Worker;
danach mathematische Kontrollen und drei Größenkalibrierungen.
Alle Probes laufen durch den produktiven Controller und zählen zum Hilfsbudget.
Die Freigabemeldung lautet SCHEDULER_PREFLIGHT_PASS mit clock=WINDOWS_STOPWATCH.
Bis diese Meldung vom Ryzen vorliegt, ist die Zielhardwareprüfung OFFEN.

Ausgeführte Cloudtests (FakeHost, kein Windows-Test):
- zwölf parallele Probes, erwartete lokale Nachläufe, andere Worker weiter aktiv;
- kleiner realer CP-SAT-Lauf mit Signalpause, Wiederaufnahme und Budgetabschluss;
- Quellenkorruption und ungeklärte CPU-Reservierung werden abgewiesen;
- absichtlich lokaler Exitcode 7: übrige Aufgaben fertig, COMPLETED_WITH_LOCAL_ERRORS;
- absichtlich ungültiger Graph: RESULT_INTEGRITY_ERROR, CPU vollständig verbucht,
  Audit verweigert Erfolgsstatus;
- historische Diagnose über isolierten Projekt-Auditinterpreter erneut geprüft.
Die maschinenlesbaren Reports und Logs liegen in diesem Verzeichnis.
Die Testquellen stehen vollständig im neuen Experimentverzeichnis.

Regeln: GC-01/02/04/05/06/08/09; docs/EXPERIMENT_RULES.md und
 docs/operations/GLOBAL_CONCLUSIONS.md. Vor neuen Kampagnen relevante Regeln
und Regressionen prüfen. Eine kleine Laufzeitabweichung ist kein mathematischer
Fehler; ein ungültiger Graph bleibt unabhängig von Toleranz unzulässig.

Abschlussinterpretation: W<2076 primärer Erfolg, W=0 nur nach unabhängiger
Vollprüfung. OPTIMAL_UNCERTIFIED kein Beweiszertifikat; Timeouts UNKNOWN.
Gegenüber Gründern verbesserte Werte separat melden; keine Konvergenzbehauptung.
