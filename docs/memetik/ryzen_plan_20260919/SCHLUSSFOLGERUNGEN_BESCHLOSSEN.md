# Beschlossene Schlussfolgerungen — Memetik/Ryzen
Stand: 19.09.2026. Vom Nutzer nach Vorlage des Reviewabgleichs und des Plans V2 angenommen. Verbindliche Grundlage: memetik/81c3a440c61670c0221103ec1d2cdd37b084bf67.

1. Der nächste Schritt ist die Implementierung und Durchführung eines begrenzten Ryzen-Methodenvergleichs, nicht ein weiterer allgemeiner Plan und noch nicht die große 48-Stunden-Suche.
2. A0 ist die einfache Referenz: zulässige Störung, danach strikt verbessernder Abstieg. A1 ergänzt zielbezogenen Besuchsspeicher, begrenzte neutrale Exploration und kalibrierte Escape-Steuerung. Gleiche Population, gleiche Gründer und gleiche Überlebensregel; keine unbemerkten weiteren Unterschiede.
3. Vergleich: 16 Individuen je Arm/Ziel, zwei Arme und drei Selektionsziele L1/F/(Linf,Nmax,L1), zwölf gepaarte unabhängige Laufseeds, zwei Varianten, je eine Worker-CPU-Stunde pro Arm/Ziel/Variante/Seed: insgesamt 144 CPU-Stunden. W bleibt Diagnose.
4. Primäre Beobachtungseinheit ist der vollständige Laufseed. Drei Wiederholungen reichen nur zum Screening. Die vorab festgelegte Entscheidung berücksichtigt gepaarte Resultate, Effektgrößen, Bindungen und sechs Zielentscheidungen; bei unklarem Vorteil bleibt A0 Standard.
5. Herkunftsregister und tatsächliche Generatorausbeute gehen vor nominellen Gründerquoten. F02 wird angemessen gewichtet, aber nicht zur alleinigen Familie. G1–G4 und Reparaturverfahren sind zu qualifizieren, keine zugesagte Lieferung. Bei Engpässen transparent kleiner starten statt Klone als neue Gründer ausgeben.
6. Ω-Bewegungserzeugung effizienter machen; Störung und Abstieg getrennt budgetieren. Zunächst höchstens 45+75 CPU-Sekunden je Episode als zu kalibrierende Obergrenzen. Tatsächlich ausgeführte Längen und unvollendete Aufgaben dokumentieren. Keine vollständige lokale-Minimum-Behauptung aus Stichproben.
7. Crossover zunächst nicht als Pflichtbestandteil oder mit fester 20-%-Quote. Größere A-Operatoren, komplette C08-Komponente und HoG-Vertiefung bleiben nachgeordnet.
8. Ryzen: alle nutzbaren physischen Kerne, bis 24 unabhängige Worker nach Durchsatzvergleich 12/18/24. Keine verschachtelte Threadexplosion. Gleiche CPU-Kontingente für alle sechs Arm/Ziel-Gruppen. Office und fremde laufende Aufgaben unberührt lassen.
9. Nach dem Vergleich ist eine gesonderte 48-Stunden-Hauptkampagne mit drei unabhängigen Wiederholungen und je 32 Individuen pro Arm/Ziel vorgesehen. 64 aktive Plätze bleiben eine spätere Skalierungsoption, keine Startvoraussetzung.
10. Reviewgrenzen bleiben bestehen: HoG≥192 checkpointgestützt, nicht vollständig unabhängig nachenumeriert. Vollständigkeit kleiner Produktklassen ist kein Ausschluss aller Ω-Änderungen. Überlappende Träger im unveränderten Rang-2-Ansatz sind wegen der Nulldiagonale unmöglich. Reviewer-Tripelgeneratorversuche ohne mitgelieferte Scripts/Logs sind Fremdbefunde.

## Laufzeitplanung für den ersten Schritt
Reiner Vergleich: 144 Worker-CPU-Stunden.
| Gleichzeitig CPU-versorgte Worker | Idealisierte Wandzeit |
|---|---:|
| 12 | 12 Stunden |
| 18 | 8 Stunden |
| 24 | 6 Stunden |

Dies ist Budgetarithmetik, kein gemessener Ryzen-Benchmark und keine Aussage einer 24-fachen physischen Beschleunigung. Bei SMT kann jede Aufgabe je CPU-Stunde weniger Arbeit leisten; deshalb zählt im Durchsatztest auch die Leistung pro Wandzeit und in der Auswertung die tatsächliche Arbeit.

Vorläufiges praktisches Planungsfenster: etwa 8–16 Stunden für den Vergleich einschließlich Laufverwaltung/Prüfung/Export bei verfügbarer Maschine. Für die vorbereitende Rechenarbeit weiterhin höchstens 16 CPU-Stunden Technik/Kalibrierung und bis 32 CPU-Stunden neue Gründer als Rahmen; vorhandene Abnahmen wiederverwenden und Budget nicht zwangsweise ausschöpfen. Insgesamt damit bis 192 CPU-Stunden: nominal 8–16 Stunden bei 24 bis 12 Workern, praktisch ungefähr 10–20 Stunden bei guter Parallelisierung. Serielle Generatoren, Speicherengpässe oder Hintergrundlast können dieses Fenster überschreiten. Kein harter Wandzeitabschluss zugesagt.
Softwareentwicklung, Fehlerkorrektur und manuelle Übertragung/Antwortzeiten sind darin nicht enthalten. Nach kurzer Ryzen-Kalibrierung die Schätzung durch gemessene ETA ersetzen. Die spätere 48-Stunden-Kampagne ist in diesen Zahlen nicht enthalten.
