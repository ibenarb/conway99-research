# Begrenzte Frontier-Folgeetappe, 24. September 2026

Die abgeschlossene V2/V3-Etappe verbrauchte 59.9808130375 zusätzliche Such-CPU-h.
V2: Endbestwerte 2096,2102,2102,2102,2102,2101; zwei von sechs Jobs erfüllen W<2102.
V3: bestes W2177, Median2214; kein Job erfüllt W<2150. Nicht-HoG vorerst pausiert.
Archiv SHA256: 4b8c28b75241b6490388127b532351833fcb6fb5f07adb1ec8cd8413bb5dc4a4.

Eigene Nachprüfung: eingefrorene Eingaben, Receipts/Checkpoints/SQLite, alte
V3-Kurven und Messpunkte sowie 1152 verschiedene beschriftete Kandidaten aus
Resultaten geprüft. Historische Python-Version ausdrücklich als fremde Umgebung
behandelt; keine Behauptung eines erneuten Windows-Hosttests hier.
Die beiden Rekorde zusätzlich durch eigene graph6-Decodierung und direkte
Ganzzahl-Matrixrechnung geprüft (NumPy; NetworkX war nicht installiert).
Kein Audit aller in SQLite enthaltenen Zwischenzustände behauptet.

W2096 entstand nach 5951.63 CPU-s, W2101 nach 4039.94 CPU-s.
Vier V2-Jobs teilen denselben beschrifteten W2102-Endbestgraphen.
W2177 entstand bei V3-gen-lambda-11-1 nach insgesamt 26687.2 CPU-s.
Späte Verbesserungen begründen längere Einzeljobs, keinen großen Inselhauptlauf.

Freigegebener Folgetest: je vier neue Seeds aus zwei konkreten 16er-Populationen,
vier CPU-h je Job, insgesamt32 CPU-h plus maximal1 CPU-h Hilfsarbeiten.
P und bisherige Selektion unverändert; kein Crossover, keine Sprungmutation,
keine Migration. Startbanken teilen fünf Klassen und besitzen unterschiedliche
Fitnessverteilungen; keine kausale Überlegenheits- oder Beckenbehauptung.

Primärkriterium W<2096. Kein Treffer: W-Frontier pausieren. Ein Treffer:
Einzelsignal bewerten. Mehrere Treffer: wiederholtes Signal bewerten, getrennt
nach Klassen. Keine automatische nächste Etappe und kein Ersatzkriterium aus F/L1.

[Verbindliche Spezifikation und Startanleitung](../../../experiments/memetik/lambda_frontier_1_0_0/README.md).
