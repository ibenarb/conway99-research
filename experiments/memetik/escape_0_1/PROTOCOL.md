# Escape 0.1.0 – Stufe 1: unmittelbare Nachbarschaften

Dies ist die erste ausführbare Stufe des Escape-Experiments, noch keine mehrschrittige Breitensuche. Keine lokalen Nutzerläufe werden verändert. Zielrechner: Office-Ubuntu, drei Worker, je Prozess höchstens 1 GiB virtueller Adressraum. Erforderlich: Python 3.10+ unter Linux; keine pip-Abhängigkeiten.

Acht Starts: A_legacy, ursprünglicher B, B-Endgraph nach F, HoG57338, bisheriger λ-Linf2-Zeuge, Codex C02 (Ω), C06 und C08 (λ). Gründerdateien samt Herkunft, SHA256 und vollständigen Ausgangsmetriken sind eingebettet. Alle müssen vor Start harte Bedingungen und unabhängig mit Mengen berechnete Metriken bestehen.

## Genau untersuchte Nachbarschaft

Für jeden Ω-Start die bestehenden Familien 4x4, 4x6, 6x6; für jeden λ-Start Apex und Rotation. Insgesamt 20 Aufgaben. Je Familie bis 3600 CPU-Sekunden einschließlich Erzeugung, Gültigkeitskontrolle und Bewertung. Früh vollständig durchlaufene Aufgaben enden sofort. Keine unveränderte Wiederholung des populationsbasierten Office-Piloten; weder Crossover noch Zufallswanderung.

Die Generatoren und der Kern wurden byteidentisch aus dem Forschungsstand übernommen; eigene Steuerung separat in runner.py. Die Vollständigkeit bezieht sich auf genau deren implementierte endliche Familien. Die 6x6-Familie umfasst die dort erzeugten Trägerformen, nicht sämtliche denkbaren gekoppelten Trades. Nicht alle grad- oder armerhaltenden Änderungen sind erfasst. Generatoren deduplizieren innerhalb einer Familie; keine Isomorphiequotientierung, keine Gleichsetzung gleicher Scores mit gleicher Struktur.

Ein 4x4-Trade entfernt acht und ergänzt acht Kanten; 4x6 entsprechend zwölf, 6x6 achtzehn. Apex entfernt/ergänzt vier, Rotation sechs. Jeder untersuchte Übergang hat Weglänge eins. Die Tradegröße und die Weglänge werden getrennt behandelt.

Alle Ergebnisse werden gleichzeitig nach W, L1, F sowie lexikographisch (Linf,Nmax,L1) bewertet. W ist hier eine zusätzliche Diagnose desselben Nachbarschaftsscans; es entsteht kein zusätzlicher Populationsarm. Pro Kriterium werden bessere, neutrale und schlechtere Trades gezählt und der beste gefundene Verbesserungszeuge gespeichert. Auf Gleichstand verschiedener Graphen folgt keine Plateauidentitätsbehauptung.

## Ergebnislogik

- EXHAUSTED: Generatorfamilie vollständig durchlaufen.
- CPU_BUDGET, MEMORY_LIMIT, DISK_FLOOR_10_GiB: unvollständig. Kein negativer Existenzschluss.
- ERROR: Implementierungs-/Prüffehler, kein Forschungsergebnis.
- IMPROVEMENT_AT_DISTANCE_1: konkreter unabhängig geprüfter Zeuge vorhanden. Dieser Start ist bezüglich dieses Kriteriums kein lokales Minimum der untersuchten Vereinigung.
- NO_IMPROVING_ONE_TRADE_NEIGHBOR: nur wenn sämtliche Familien des Arms vollständig sind und keine Verbesserung gefunden wurde. Das belegt nur das Fehlen einer direkten Verbesserung; neutrale Pfade können weiterführen.
- UNKNOWN: fehlende Verbesserung bei unvollständiger Suche.

Es wird weder ein kompletter neutraler Plateauzusammenhang ermittelt noch Minimalität eines mehrschrittigen Fluchtwegs behauptet. Nach dem Census: verbesserbare Starts gezielt absteigen lassen, vollständige lokale Endpunkte bestimmen und erst daran Suche nach Tiefe zwei und größer ansetzen. Bei einer begrenzten Exploration kürzerer Tiefen bleibt jede gefundene längere Flucht lediglich eine obere Schranke.

## Betrieb

Python-Zipapp `Conway99_Escape_Office_0.1.0.pyz`, Aufrufmodus `start`: Vorprüfung, eigener zeitgestempelter Laufordner neben der Zipapp, abgetrennter Prozess mit eigener Session und umgeleiteten Ein-/Ausgaben. Schließen des Terminals beendet den Lauf nicht; Abschalten von Windows/WSL kann ihn beenden. Laufsteuerung verändert keine WSL-Konfiguration.

`status.json` wird während laufender Aufgaben etwa alle zehn Sekunden aktualisiert, `console.log` enthält spätestens alle zehn Minuten einen Status. `active_run.json` enthält PID und Laufpfad. Aufgaben schreiben atomar ihren Zwischenstand einschließlich bisheriger Verbesserungszeugen. Status-ETA beschreibt das verbleibende CPU-Kontingent bei voller Auslastung, keine Lösungserwartung und keine garantierte Wandzeit. Höchstens 20 CPU-Stunden entsprechen bei voller Auslastung dreier Worker ungefähr sieben Stunden, zuzüglich Verwaltungsaufwand; vorzeitig erschöpfte Familien verkürzen den Lauf.

Am Ende `CENSUS_FINISHED`; die Zahlen exhausted/incomplete stehen daneben. Das Ende des geplanten Kontingents ist nicht mit vollständiger Nachbarschaftserkundung zu verwechseln. Der vollständige Bericht steht in `summary.json`, einzelne Zeugen in den Aufgaben-JSONs.

Wiederaufnahme mit `run --run-dir ...` und identischen Einstellungen überspringt abgeschlossene Aufgaben. Eine durch Prozessabbruch unterbrochene Aufgabe (Status RUNNING) beginnt ihre deterministische Enumeration erneut. Bereits budgetbeendete Aufgaben werden nicht automatisch mit neuem Kontingent wiederholt. Kein Anspruch auf Fortsetzung mitten im Generator. Für größere Kontingente wird ein neuer Lauf mit explizit größerem Budget angelegt.

## Vorprüfung der Auslieferung

Acht Eingangsgraphen sowie Kern und Operatoren gegen Git-Blob-IDs geprüft. Kurzlauf mit 0,1 CPU-Sekunden je Aufgabe und drei Prozessen: alle 20 Aufgaben abgewickelt; vollständige und offene Familien getrennt. Die dabei gesicherten Verbesserungszeugen werden separat aus Ausgangsgraph und gespeicherten Trades rekonstruiert und unabhängig nachbewertet. Kurzlaufzahlen sind keine Leistungsprognose für den Office-PC. Endgültige Zipapp zusätzlich im abgetrennten Startmodus geprüft.
