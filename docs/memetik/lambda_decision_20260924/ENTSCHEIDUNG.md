# Reviewabgleich und verbindlicher nächster Versuch — 24.09.2026

Der vorgeschlagene 864-CPU-h-Hauptlauf wird zurückgezogen. Autorisiert ist die
angepasste V2/V3-Etappe: 60 zusätzliche Such-CPU-h, notwendige Hilfsarbeiten auf
maximal 2 CPU-h begrenzt. Kein neuer Operator, kein Crossover, keine Sprungmutation.

## Eigene Nachprüfung der Vorprüfungen

Archiv SHA256 6a251f5f63eb56dde7b77e8b0460cee5d7aee3eee8c8a5035df09d9bb1928abd.
95 eingefrorene Eingabedateien, 24 Receipts/Checkpoints/SQLite-Dateien geprüft.
1201 unterschiedliche beschriftete Graphen aus Bestwerten, Endpopulationen,
beobachteten Normrekorden und Kurven: lambda-Bedingungen und alle Scores nachgerechnet.
Keine Abweichung. Keine Behauptung eines vollständigen Audits aller SQLite-Graphen.
31.96686631 Such-CPU-h + 0.4189682061 erfasste Hilfs-CPU-h = 32.3858345161 CPU-h.
Exportkosten nach Archivabschluss sind darin nicht enthalten.

V1: PCesc 5:3 nach (W,L1), mediane gepaarte W-Differenz -0.5; P-Median 2141,
PCesc-Median 2138.5; beide bestes W 2126. Kein nachgewiesener Endwertvorteil.
495 cycle3-Adoptionen, 3490 vollständige Anfragen, rund 5.1% Katalog-CPU-Anteil.
V3: beste Endwerte 2222, Median 2250; keine Unterschreitung von 2200.
Fünf von acht Jobs verbessern W im letzten Budgetviertel; rechtfertigt begrenzte
Fortsetzung, nicht die Hälfte eines großen Hauptlaufbudgets.

Eigene Histogrammaggregation: V1/P mediane W-Auslenkung +91, 90%-Quantil +268,
Maximum +460, beschriftete Rückkehr 63.5556%. Für alle V1-Jobs zusammen:
Median +93, p90 +272, Rückkehr 63.1240%. Die Reviewzahlen beziehen sich auf P,
nicht auf alle V1/V3-Episoden gemeinsam.

## Übernommene Kritik

- 432 CPU-h für Nicht-HoG waren unbegründet; zwei Wiederholungen begründen keine
  bevorzugte Ausstattung von gen-lambda-03.
- Vorgeschlagene Barrierenhöhen sind keine Erweiterung vorhandener Auslenkungen;
  ein gezielter anderer Mechanismus war nicht spezifiziert.
- Große Sprungbudgets und Crossover sind ohne belastbare Vorprüfung nicht gerechtfertigt.
- Zu viele gleichzeitige Methodenänderungen, zu wenig Replikation der Kontrollen,
  fehlende operative Erfolgskriterien.

## Nicht übernommene Überdehnungen

Kein signifikanter PCesc-Vorteil widerlegt nicht alle Fluchtmechanismen.
Die vor dem Lauf dokumentierte Entscheidung hatte automatische Ausschlussregeln
bereits ausdrücklich nicht übernommen; keine nachträgliche Änderung des README.
Summierte Kantenänderungen eines Weges sind keine Netto-Kantendistanz.
V3-Erholungszeiten beweisen keinen Nullertrag perturbierter HoG-Nachkommen.
Ein logarithmischer Kurzzeitfit ist kein Erschöpfungs-/Nichtexistenzbeweis.

## Festlegung vor Implementierung des Ryzen-Laufs

V2: drei P-Rekordpopulationen, je zwei neue Seeds und 7200 CPU-s; Signal W<2102.
V3: alle acht Originalzustände unverändert bis 28800 CPU-s; Signal W<2150.
Ein Treffer ist nur ein Fortsetzungssignal. Negative Ergebnisse begründen eine
Budgetentscheidung zur Pause, keinen mathematischen Ausschluss.
Keine automatische Folgeinvestition. Technische Fehler pausieren eigene Worker;
ansonsten feste Budgets, keine nachträgliche Auswahl von Linien oder Endpunkten.

Die 16er-Startbank pro V2-Frontier wird deterministisch aus Bestgraph plus
Endpopulation des entsprechenden P-Jobs gebildet. Keine neu erzeugten Varianten.
V2 testet Frontier-Produktivität, nicht Überlegenheit gegenüber gleichzeitigem
Gründer-Seeding (eine solche Kontrollgruppe ist nicht enthalten).

14 Worker gleichzeitig, davon 8 mit je sechs zusätzlichen CPU-Stunden:
Mindestens sechs Stunden Walltime, vorsichtig etwa 6–8 Stunden plus Vorprüfung;
vier Stunden sind für diese Aufgabenstruktur nicht möglich.

Implementierung, feste Seeds, Datenherkunft, Tests und Bedienung:
[README](../../../experiments/memetik/lambda_decision_1_0_0/README.md).
