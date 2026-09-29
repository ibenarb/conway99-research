# λ-Reparaturpilot 1.2.0 — geprüfter Abschluss, 29.09.2026

## Ergebnis

144/144 Aufgaben abgeschlossen, 24 paarweise nichtisomorphe Gründer, je sechs Fensteraufgaben (24/40/60 Knoten, defect/random). Gründer, Fenster, Seeds und wissenschaftliche Aufgaben sind gegenüber 1.1.0 unverändert; Suchbudget je Aufgabe von 3600 auf 7200 CPU-Sekunden erhöht und Kalibrierungsabschlussfehler korrigiert. Keine Übernahme alter Suchergebnisse. Ein vollständiger Neustart ist kein exakter zeitlicher Präfixvergleich.

Bester W-Wert bleibt 2076. Einzige Verbesserung gegenüber einem Gründer: 2077_08_s60_defect, (W,L1)=(2139,2516)→(2127,2498). Der Kandidat ist zur Verbesserung aus 1.1.0 isomorph; die beschrifteten Graphen unterscheiden sich. 25 Graphklassen einschließlich 24 Gründer, keine neue Klasse gegenüber 1.1.0. Kanonisierung: pynauty 2.8.8.1; unabhängige set-basierte Prüfung aller gespeicherten Kandidaten durch den archivierten Audit reproduziert.

| Fenster | OPTIMAL_UNCERTIFIED | RIGID_BOUNDARY_VERIFIED | CPU_LIMIT_UNKNOWN |
|---|---:|---:|---:|
|24|43|5|0|
|40|45|0|3|
|60|0|0|48|
|Summe|88|5|51|

Gegenüber 1.1.0 zwei zusätzliche Optimalitätsmeldungen: 2076_01_s40_defect und 2077_09_s40_random. CP-SAT-Optimalität ist nicht unabhängig zertifiziert und betrifft nur das jeweilige feste Fenster. Zeitlimits bleiben UNKNOWN. Insbesondere sind alle großen Fenster weiterhin offen. Keine Aussage über globale Nichtexistenz oder Erschöpfung der Reparaturmethode.

## Betrieb und Fehlerbehebung

Abschluss 29.09.2026 08:20:15 MESZ. Host-Walltime 36153.7796692 s = 10 h 2 min 33.78 s. Kampagnenkonto 105.1207063203 CPU h; Exportkonto einschließlich nachträglicher CLI-Reservierungen 105.1707063203 CPU h. Diese zusätzlichen 0.05 h sind keine zusätzliche Suche.

Audit PASS_WITH_RECORDED_LOCAL_DEVIATIONS; 51 weiche Warnungen einschließlich zweier absichtlicher Preflight-Verzögerungen, keine harten lokalen Überschreitungen und keine lokalen Fehler. Kleine Abschaltnachläufe wurden vollständig erfasst. Keine Schlussfolgerung zur Langzeitstabilität sämtlicher Gastuhren.

GC-10 im Zielhardwarelauf bestätigt: 2076_01_s40_defect lief nach Kalibrierung bis zum lokalen Solveroptimum (insgesamt 2833.314639 CPU s); 2076_01_s60_defect verbrauchte 7200.466464 CPU s. Kein vorzeitiger Aufgabenabschluss bei 60 s. Die letzte ETA um 08:10:15 lag bei etwa 11 min 17 s; tatsächlicher Abschluss knapp 10 min später. Das ist ein lokaler Beleg für die verbesserte Endphasenprojektion, keine allgemeine Laufzeitgarantie (GC-11).

## Bewertung

Eine weitere reine Verlängerung derselben festen Fenster hat derzeit geringe empirische Priorität. Verdoppeltes Budget brachte zwei lokale Optimalitätsmeldungen, aber keine neue Klasse und keinen besseren Rekord. Fensterwahl, Freiheitsgrade, Übergänge zwischen Kandidaten und Zielmaße sollten als getrennte Hypothesen untersucht werden. Das Nullergebnis ist kein Gleichwertigkeits- oder Erschöpfungsbeweis (GC-08).

## Matrizen

Beste_Kandidaten_Maple.txt enthält die zwei in (W,L1) nichtdominierten Klassen des geprüften 25-Klassen-Pools: (2076,2488) und (2077,2436). Lexikographisch ist der erste Kandidat der Beste. Keine Behauptung einer globalen Paretofront über alle früheren Projektarchive. Alle_25_Kandidaten_Maple.txt enthält den gesamten Pool. 99×99, Einträge 0/1, symmetrisch, Nulldiagonale, Grad 14, λ=1. Originalbeschriftung, keine kanonische Neunummerierung. Maple-Syntax A1 := <a,b,...;c,d,...;...>: . Beide Achsen verwenden dieselbe Knotenreihenfolge.

## Reproduktion und Herkunft

Originalarchiv 1.2.0 SHA256 fbd30cf6bfaf9eb610da8afb0ae64b8a2003c766eb64bce8bf79fc1d8b0c82b6.
Originalarchiv 1.1.0 SHA256 63fd94806b2235d6182178c0b066c1274fcf268a17f9cae951d65d3ef2ed5c8f.
Veröffentlichte 1.2.0 Quellen/Plan: Commit 24489ef3179e6b341b037eb76e8e0857de4e2cda.

Mit Projekt-Auditinterpreter analyze.py RUN120 RUN110 OUT ausführen. Das Skript wiederholt Audit, Inputvergleich, Klassenvergleich und Matrixexport. Ein erster Export-Prüflauf verglich vollständige Best-Records mit einer Graphprojektion und scheiterte an zusätzlichen Metadatenfeldern; die Prüfung wurde auf graph6/state/scores korrigiert und bestand danach. Keine Änderung von Eingangsgraphen oder Scoreprüfung.

Die drei Agentenberichte sind ausdrücklich Vorschläge und Hypothesen, keine Resultate ausgeführter neuer Suchläufe. Neue Kampagne noch nicht gestartet.
