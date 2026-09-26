# Datenübersicht λ-Memetik — 26.09.2026

Ziel: srg(99,14,1,2). Alle hier untersuchten Kandidaten sind im λ-Arm:
99 Knoten, Grad 14, jede Kante hat genau einen gemeinsamen Nachbarn.
Für ungeordnete Paare r_uv = |N(u) ∩ N(v)| + A_uv − 2:
W = Anzahl r != 0; L1 = Summe |r|; F = Summe r²;
Linf = max |r|; Nmax = Anzahl der Paare mit |r| = Linf.
Zielfunktion der neuen Suchen lexikographisch (W,L1), Suchoperator P unverändert.

## Experimente und vorab definierte Kriterien

| Präfix | Experiment | Budget | Kriterium | Ergebnis |
| --- | --- | --- | --- | --- |
| D | V2: drei Frontier-Banken × zwei Seeds, je 2 CPU-h | 12 CPU-h | irgendein W < 2102 | 2096 und 2101; Median 2102 |
| D | V3: acht alte Jobs von 2 auf 8 CPU-h fortgesetzt | +48 CPU-h | irgendein W < 2150 | best 2177; Median 2214; Kriterium verfehlt |
| F | Banken 2096 und 2101, je vier neue Seeds × 4 CPU-h | 32 CPU-h | mindestens zwei Jobs W < 2096 | 8/8; vier Endklassen; best 2081 |
| O | Bank 2081 sechs Seeds, Bank 2092 zwei Seeds, je 7 CPU-h | 56 CPU-h | mindestens zwei Jobs W < 2081 | 7/8; vier erfolgreiche Endklassen; best 2076 |

Suchverbrauch: D 59.9808130375, F 31.9890119006, O 55.9890694183 CPU-h.
Hilfszeiten stehen in den jeweiligen Ledgers; die Archive enthalten nicht die
nach ihrer Erstellung verbuchte Exportzeit. D enthält für V3 frühere Kurven-
und CPU-Anteile: Fortsetzung ab 7200 bis 28800, nicht acht neue Stunden.

F-Endwerte: Bank 2096 → 2088,2081,2091,2081;
Bank 2101 → viermal derselbe beschriftete Graph mit W2092.
O-Endwerte: Bank 2081 → 2079,2076,2076,2079,2076,2078;
Bank 2092 → 2077,2084. Alle drei W2076-Treffer sind derselbe beschriftete Graph.
W2076: L1=2488,F=3352,Linf=3,Nmax=20.
W2077: L1=2436,F=3180,Linf=3,Nmax=13.

O: Nach vier Stunden je Job bereits sieben erfolgreiche Jobs; W2076 in zwei
Jobs. Ein dritter erreicht denselben Graphen nach 4.7512 CPU-h. Späte Verbesserungen
nach sechs Stunden in zwei anderen Jobs betreffen L1 bei unverändertem W.
Die ursprünglich vorgeschlagene Vier-Stunden-Zwischenentscheidung wurde VOR
Laufbeginn auf ausdrücklichen Benutzerwunsch durch einen durchgehenden
Übernachtlauf ersetzt; keine nachträgliche Veränderung der Erfolgsschwelle.

Die Wiederholungen einer Bank erhalten dieselben 16 Gründerklassen und neue
Seeds. Die beiden O-Banken wurden aus Endpopulationen der Vorläufer gebildet,
jeweils dedupliziert und nach (W,L1,state) auf 16 ausgewählt. Keine gemeinsamen
Klassen zwischen den O-Banken. Dies behauptet keine unabhängigen Suchbecken.
Bankauswahl ist adaptiv; 6:2 ist kein kausaler Überlegenheitstest.

## Inhalt und Prüfgrenzen

- Originale task/result/receipt-Dateien aller 30 Jobs, unverändert aus den Archiven.
- Originale Auswertungen, Pläne, Fingerprints, Kontrollen und Hilfszeit-Ledger.
- Vollständige Graph6-Kandidaten, Endpopulationen, Normrekorde, Bestwertkurven,
  Messpunkte und Histogramme in den result-Dateien.
- Protokolle sowie Gründerbanken, soweit separat vorhanden; D-Gründer in task.
- 02_ENDPOINTS.csv für schnellen Vergleich; 03_PROVENANCE.json für Herkunft.
- 04_VERIFY.py: unabhängige Standard-Python-Nachrechnung aller im result
  enthaltenen Kandidaten und task-Gründer, sowie Hashprüfung des ZIP-Inhalts.
  Ausführung nach Entpacken: python3 04_VERIFY.py. Kein pynauty erforderlich.

Nicht enthalten: große SQLite-Archive, Checkpoints, vollständige Controllerlogs
und Programmquellen. Receipts referenzieren daher auch Dateien außerhalb dieses
Pakets. Der beigefügte Prüfer ist kein vollständiger Receipt-/SQLite-Audit und
prüft keine Isomorphieklassen. Diese wurden bei unserer vorherigen Prüfung mit
pynauty 2.8.8.1 geprüft. Für eigene Kanonisierung sind Graph6 und Klassen vorhanden.
Der Übernachtlauf wurde gegen das veröffentlichte Paket bytegenau abgeglichen;
112 verschiedene Auswertungsgraphen wurden reproduziert, seine fünf verschiedenen
Endbestgraphen zusätzlich unabhängig nachgerechnet. Fremde Python-Version beim
Cloud-Audit ausdrücklich berücksichtigt; keine Behauptung identischer Laufumgebung.

Fixierte Quellen:
- D: https://github.com/ibenarb/conway99-research/tree/aca28f7c676a269b03b650dc5ac3433a99dceec1/experiments/memetik/lambda_decision_1_0_0
- F: https://github.com/ibenarb/conway99-research/tree/242c02ccb909c74ccd4ca0a5dada9fe32210b52f/experiments/memetik/lambda_frontier_1_0_0
- O: https://github.com/ibenarb/conway99-research/tree/a4d43966b7c09fac3e0e4bc87228280244cfc555/experiments/memetik/lambda_overnight_1_0_0

Die ursprünglichen V1/V3-Vorprüfungen waren Gegenstand des vorigen Reviews.
D ist vorsorglich erneut enthalten, falls der Reviewer diese Etappe bereits kennt.
Keine Empfehlung zur Fortsetzung wird im Auftrag vorgegeben.
