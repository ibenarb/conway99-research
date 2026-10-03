# Ergebnis der Entwicklung und Hardwareentscheidung

Der Pilot 1.0.0 ist für den eigenen Vorabtest auf dem Ryzen bereit.
Ein Hauptlauf wurde auf dem Rechner des Nutzers nicht gestartet.

Der unabhängige Rootaudit reproduzierte 8105 kanonisch verschiedene Roots,
Stabilisatoren und Orbitgrößensumme 56011010. Eine separate Vertex-DP
lieferte dieselbe Gesamtzahl. Die 128er-Auswahl ist vorab eingefroren und
nach (Stabilisatorordnung, lokale Matchingzahl) geschichtet.

Der lokale Encoder fand bei Root 1, Zielzeile 1, 10000 verschiedene
Projektionen in ungefähr 1,62 CPU-s; danach war die Enumeration begrenzt,
nicht vollständig. Ein Test der stärkeren globalen linearen Relaxation
an Root 101 fand in 60 CPU-s kein erstes Modell. Das war kein UNSAT.

Ein echter Zwei-Arm-Test an Root 1 mit jeweils 120 CPU-s erreichte Tiefe 10
(ordered) und 14 (dynamic), 715795 beobachtete Projektionen und 1297
vollständig abgeschlossene lokale Projektionsenumerationen. Vier davon
wurden für separate Zertifikatstests ausgewählt. Drei bestanden sofort;
der vierte bestand nach Diagnose des dokumentierten drat-trim-Exitcode-
Sonderfalls und unabhängiger Unit-Propagation. Der ursprüngliche Befund
wurde erhalten. Die beiden Bestzustände wurden zusätzlich über die
vollständige Randgraphkonstruktion mit direkten Nachbarschnittzahlen geprüft.

Diese Ergebnisse belegen den produktiven Codepfad, nicht einen statistisch
abgesicherten Vorteil des dynamischen Arms oder die Erreichbarkeit von
Tiefe 20/30. Schon die flachen, großen Breiten rechtfertigen Reservoir und
explizite Zensierungsangaben im Infrastrukturpilot.

Die Elf-Aufgaben-Kalibrierung erreichte in der Cloud Tiefe 9–10 nach jeweils
20 CPU-s, bei maximal etwa 33 MiB pro Worker. Aufgrund der RAM-Reserve liefen
hier höchstens zwei gleichzeitig. Der finale Quellstand durchlief nach der
Prüferkorrektur erneut den Kontrollpfad samt Zwei-Worker-Kalibrierung,
Pause/Resume und Erkennung offener Sitzungsabrechnungen.

Das ist kein Test mit elf gleichzeitig laufenden Ryzen-Workern. Der
mitgelieferte Preflight auf dem Ryzen plant eine Elf-Aufgaben-Welle und
protokolliert die tatsächlich erreichte Parallelität. Die Controller-
RAM-Zulassung kann sie bei knappen Ressourcen reduzieren.

Empfohlen wird der vorhandene Ryzen, maximal elf Worker, 1,5 GiB
Adressraumgrenze je Worker und 6 GiB freie Reserve. Der laufende C2-Prozess
bleibt unangetastet. Für Daten höchstens 100 GiB plus 25 GiB freie Reserve.
Keine zusätzliche Hardware kaufen, bevor Breiten, Durchsatz, Zensierungsrate
und Zertifikatskosten auf der eigenen Maschine vorliegen.

256 CPU-h Suche entsprechen bei elf voll ausgelasteten Kernen rechnerisch
23,27 Stunden, 270 CPU-h Gesamtrahmen 24,55 Stunden. Frühe Abschlüsse,
RAM-bedingt kleinere Parallelität, I/O und WSL-/Hosteffekte können die reale
Walltime deutlich verändern. Eine belastbare ETA liegt noch nicht vor.
