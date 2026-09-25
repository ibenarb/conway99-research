# Conway99-Arbeit

Vor projektbezogenen Git- und Review-Aktionen `docs/CONWAY99_COLLABORATION.md` lesen. Dort sind die allgemeine Push-Freigabe des Eigentümers und Git als Standardweg für den Reviewer-Austausch dokumentiert.

Laufende lokale Forschungsprozesse des Nutzers nicht aufgrund von Dokumentations- oder Reviewaufgaben verändern.

## Python für memetische Prüfungen

Vor memetischen Audits und pynauty-abhängigen Prüfungen `python3 tools/memetik/audit_python.py` ausführen. Danach den ausgegebenen Interpreter verwenden oder die Prüfung direkt über `python3 tools/memetik/audit_python.py -- SCRIPT [ARGUMENTE]` starten. Der Helfer stellt pynauty==2.8.8.1 in einer isolierten Projektumgebung bereit und prüft Kanonisierung sowie Automorphismen. Nicht auf die temporäre Benutzerinstallation des allgemeinen `python3` vertrauen.

Dies ist ausschließlich die Audit-Umgebung. Laufende/fixierte Ryzen- oder Office-Umgebungen, Quellpakete und Kampagnen-Fingerprints dadurch nicht ändern. Nach Verlust der gesamten Arbeitsumgebung den Helfer aus Git erneut ausführen; eine Cloud-Installation ist nicht dauerhaft garantiert. Details: `tools/memetik/README.md`.
