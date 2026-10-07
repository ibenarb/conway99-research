# Conway99-Arbeit

Vor projektbezogenen Git- und Review-Aktionen `docs/CONWAY99_COLLABORATION.md` lesen. Dort sind die allgemeine Push-Freigabe des Eigentümers und Git als Standardweg für den Reviewer-Austausch dokumentiert.

Laufende lokale Forschungsprozesse des Nutzers nicht aufgrund von Dokumentations- oder Reviewaufgaben verändern.

## Python für memetische Prüfungen

Vor memetischen Audits und pynauty-abhängigen Prüfungen `python3 tools/memetik/audit_python.py` ausführen. Danach den ausgegebenen Interpreter verwenden oder die Prüfung direkt über `python3 tools/memetik/audit_python.py -- SCRIPT [ARGUMENTE]` starten. Der Helfer stellt pynauty==2.8.8.1 in einer isolierten Projektumgebung bereit und prüft Kanonisierung sowie Automorphismen. Nicht auf die temporäre Benutzerinstallation des allgemeinen `python3` vertrauen.

Dies ist ausschließlich die Audit-Umgebung. Laufende/fixierte Ryzen- oder Office-Umgebungen, Quellpakete und Kampagnen-Fingerprints dadurch nicht ändern. Nach Verlust der gesamten Arbeitsumgebung den Helfer aus Git erneut ausführen; eine Cloud-Installation ist nicht dauerhaft garantiert. Details: `tools/memetik/README.md`.

## Dauerhafte Regeln für Experimente

Vor Planung, Implementierung, Startanweisung oder Bewertung eines Rechenexperiments `docs/EXPERIMENT_RULES.md` und `docs/operations/GLOBAL_CONCLUSIONS.md` lesen. Ralph bevorzugt großzügige Ressourcen und ausdrücklich höhere Toleranz für kleine erklärbare Zeitüberschreitungen. Solche vollständig verbuchten Abweichungen lokal behandeln; globale Stopps für echte Ressourcen-/Integritätsprobleme reservieren. Erreichte Zeitbudgets lösen gemäß `docs/EXPERIMENT_RULES.md` die Abfrage `time limit reached. ETA HH:MM. Extend [seconds] ?` aus: 0 bedeutet kontrollierter Abbruch, positive Sekunden bedeuten Verlängerung; bis zur Antwort unverändert weiterrechnen, weder pausieren noch abbrechen; tatsächlichen Verbrauch und Überschreitung weiter verbuchen. Auch Hintergrundläufe brauchen einen dokumentierten Antwortkanal. Keine stillen Budgeterhöhungen und keine Abschwächung mathematischer Prüfungen. Relevante GC-IDs in Plan und Übergabe nennen. Neue Regeln ändern keine laufenden/fixierten Experimente automatisch.

## Eine Bearbeitungsrunde, ein Arbeitspaket

Gemäß `docs/CONWAY99_COLLABORATION.md` (Nutzeranweisung 07.10.2026) pro Chat-Bearbeitungsrunde genau ein zu Beginn benanntes, abgegrenztes Arbeitspaket durchführen. Ergebnisse, Prüfstatus und Fortsetzungsstand dauerhaft sichern und die Sicherung überprüfen; dann die Antwort beenden. Das nächste Paket beginnt erst mit „weiter“. Umfangreiche Rohdaten in Dateien belassen und nur gezielte Auszüge/Zusammenfassungen in den Chat übernehmen. Ältere pauschale Fortsetzungsaufträge werden insoweit ersetzt. Laufende Rechenprozesse werden durch das Antwortende nicht abgebrochen; GC-19 bleibt gültig. Keine zuverlässige Kenntnis verbleibender Kontextkapazität oder garantierte Vorwarnung behaupten.
