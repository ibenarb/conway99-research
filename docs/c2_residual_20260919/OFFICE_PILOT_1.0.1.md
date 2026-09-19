# Office-Pilot 1.0.1: SIGALRM-Zeitlimit korrekt erkennen

Basis: cb3d24ceacbebecc9e3b7aabf63f99880367689c, 19. September 2026.

## Beobachtung auf Office

Der Nutzer übermittelte den ersten technischen Lauf und anschließend dessen
Logende. run_dir:
/home/rb/conway99_workspace/Conway99_C2_Office_Residual_1.0.0/office_pilot_runs/pilot_20260919_103350_017292

Nur die Totalizer-Variante wurde gestartet. Gemeldet wurden Rückgabecode -14,
55.109039233997464 Sekunden Wrapper-Wandzeit, 50.75014 CPU-Sekunden und
592908288 Bytes Spitzen-RSS. Das Log endet mit `c raising signal 14 (SIGALRM)`;
es enthält die konfigurierte Frist von 55 Sekunden. 15789 Konflikte und 73194
Entscheidungen sind diagnostische Solverstatistiken, kein Ausschlussresultat.

Der alte Starter 1.0.0 klassifizierte das als EXECUTION_ERROR und stoppte
vorsichtshalber. Die Signatur passt zur Beendigung am konfigurierten Wandzeitlimit.
Der Fall bleibt offen. Diese Feststellung beruht auf Nutzer-Ausgaben, nicht auf
hier abgerufenen Originaldateien. Der übermittelte Loghash lautet
7c0f55eca9b560799c7b289546a3e3c5658f1f1d637c797c88634316d2b2cc4c;
er wurde hier nicht gegen die vollständige Datei nachgerechnet.

## Korrektur

Der vollständige Starter office_pilot.py trägt jetzt Version 1.0.1. Er erkennt
WALL_TIME_LIMIT nur bei gemeinsamem Vorliegen von:

- Rückgabecode -SIGALRM;
- einem vom Aufrufer ausdrücklich angegebenen positiven Solver-Wandzeitlimit;
- abgelaufener Frist, mit höchstens min(1 Sekunde, 5 Prozent der Frist) Toleranz;
- passender Logmeldung über das konfigurierte Wandzeitlimit;
- der Schlussmeldung `c raising signal 14 (SIGALRM)`;
- keiner im Log ausgegebenen SAT-/UNSAT-Entscheidung.

WALL_TIME_LIMIT ist ein offener, zensierter Ausgang. Der Starter darf dann mit
der nächsten Variante fortfahren. Andere Signale, zu frühe SIGALRM-Ereignisse,
fehlende Logbelege oder widersprüchliche Entscheidungen bleiben Fehler.

Solver, CNFs, Seed, Reihenfolge, Speicher-/Dateigrenzen und Schutz bestehender
Prozesse bleiben unverändert. Alte Logs und der alte Summary werden nicht
überschrieben oder nachträglich als Erfolg umetikettiert. Ein neuer Viererlauf
bekommt ein neues Zeitstempelverzeichnis; er ist kein Solvercheckpoint-Restart.
Die bisherige einzelne Minute ist kein vollständiger Variantenvergleich.

## Gezielte Kontrolle

Die Feldsignatur wurde direkt gegen die neue Klassifikation geprüft, dazu fünf
negative Gegenbeispiele. Ein wirklicher kurzlebiger Kindprozess wurde nach einer
Sekunde mit SIGALRM beendet und korrekt als WALL_TIME_LIMIT erfasst. Die bestehenden
Kontrollen für Entscheidungen, andere Fehler, Ressourcenabbruch, Ausgabegrenze
und fehlgeschlagene Windows-Messungen bestehen weiter.

Prüfergebnis: results/c2_residual_20260919/pilot_controller_controls_1.0.1.json.
Es wurde hier kein neuer C99-Solverlauf gestartet und nicht auf Office zugegriffen.
