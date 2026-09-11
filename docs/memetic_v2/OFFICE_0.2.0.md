# Conway-99 Office 0.2.0: vollständige Startpopulation und drei Zielfunktionen

Stand: 11. September 2026. Nachfolger des angehaltenen Office-Piloten 0.1.0.
Die frühere Fassung und ihre Laufdaten werden nicht überschrieben.

## Entscheidung und tatsächlicher Bestand

64 paarweise nichtisomorphe Startgraphen liegen im Paket bereits vollständig vor:
32 im Omega-Arm (H84 einschließlich exakter P-Margen), 32 im Lambda-Arm
(99 Knoten, Grad 14, genau ein gemeinsamer Nachbar pro Kante).
Alle zehn Gründer sind unverändert enthalten. 54 zusätzliche Graphen wurden
mittels echter zulässiger Trades erzeugt; ihre Vorgänger, Änderungen und Seeds
sind gespeichert. Die unabhängige Kontrolle spielt jede Abstammungskante nach.
64 bedeutet verschiedene Graphen, nicht 64 unabhängige Erfindungen oder
statistisch unabhängige Stichproben. Die vorbereiteten Nachfahren liegen noch
in der Nähe ihrer Gründer. Es wird keine Gleichverteilung behauptet.

| Gründer | Plätze je Normvariante | W | L1 | L2² | Linf |
|---|---:|---:|---:|---:|---:|
| A: best_hard | 8 | 2175 | 2718 | 3926 | 4 |
| B: Maple 29.08.2026 | 11 | 2110 | 3512 | 9716 | 10 |
| H_Z14 | 3 | 2310 | 2940 | 4312 | 3 |
| H_minus | 5 | 2341 | 3118 | 4980 | 5 |
| H_plus | 5 | 2331 | 3122 | 5016 | 5 |
| HoG 57338 | 4 | 2182 | 2398 | 2836 | 3 |
| HoG 57177 | 7 | 2823 | 3754 | 5864 | 4 |
| HoG 57200 | 7 | 2474 | 2916 | 3848 | 4 |
| HoG 57271 | 7 | 2420 | 2798 | 3580 | 3 |
| HoG 57328 | 7 | 2395 | 2768 | 3540 | 3 |

A stammt aus Eintrag 1 des historischen input_checkpoint_168039s.bin im
Archiv conway99_dynamic_fiber_islands_0.2.0.tar.gz. Die ehemalige Paarung a xor 1
wurde explizit in die Paarung a+7 modulo 14 umnummeriert. B stammt aus
conway99_near_candidate_maple_20260829.txt und erhielt dieselbe Umnummerierung.
Die vollständige H-Konformität beider Graphen wurde nach der Umnummerierung
unabhängig erneut geprüft. A war im vorigen Piloten irrtümlich nicht enthalten.

Die zusätzlichen Internetquellen sind die Originalbeiträge:
- https://math.stackexchange.com/questions/5146421/what-graph-is-closest-to-the-conway-99-graph-if-it-does-not-exist
- https://github.com/optimath/99-vertex-locally-7-3-windmill-graph
- https://houseofgraphs.org/graphs/57177
- https://houseofgraphs.org/graphs/57200
- https://houseofgraphs.org/graphs/57271
- https://houseofgraphs.org/graphs/57328

Die API-Dateien wurden heruntergeladen, ihre Adjazenzlisten eigenständig geprüft.
HoG 57338 wurde laut Kabenyuk aus 57200 erzeugt. Getrennte Stammkennungen im
Experiment bedeuten hier getrennte Ausgangsgraphen, nicht unabhängige Herkunft.
Der Thakkar-Zirkulant aus https://arxiv.org/html/2608.11211 wurde nachgebaut:
W=1584, L1=2772, L2²=5346, Linf=3; 495 Kanten verletzen Lambda=1. Er erfüllt
keinen der beiden unveränderten Suchräume und wird nicht als zulässiger Gründer
hineingeschoben. Die besseren reinen Trefferzahlen rechtfertigen keinen Bruch
der harten Bedingungen. Reparatur dieses anderen Ansatzes bleibt spätere Arbeit.

## Warum drei Normen?

Für jedes ungeordnete Paar i<j definieren wir r_ij = c_ij + A_ij - 2.
Betrachtet wird der Vektor dieser 4851 Einträge, keine induzierte Matrixnorm.
W zählt r!=0 und ist keine Norm. L1=sum |r|, L2=sqrt(sum r²), Linf=max |r|.
Die Optimierung von L2² statt L2 hat exakt dieselbe Rangfolge und benötigt
keine Gleitkommazahlen. Für Grad 14 gilt an jedem Knoten sum_j r_ij=0,
also auch global sum r=0 und L1=2*sum positiver Residuen.
L1 misst somit die gesamte unausgeglichene Nachbarzahl. Es ist weder ein
statistisches Rauschmodell noch ein bewiesener Abstand in erlaubten Trades.

L2² gewichtet konzentrierte große Fehler stärker. Das ist hier keine bloße
Gewohnheit: Für jeden einfachen 14-regulären 99-Graphen gilt
L2²=4*C4+6*T-9702. Im Lambda-Arm ist T=231 fest, also L2²=4*(C4-2079).
Die Quadratsumme hat dort eine unmittelbare kombinatorische Bedeutung.
Das beweist nicht, dass sie die beste Suchheuristik ist.

Linf begrenzt den schlimmsten Einzelfehler. Weil nur wenige ganzzahlige Werte
auftreten, hat es sehr große Plateaus. Die fest definierte Verfeinerung lautet
lexikographisch (Linf, Anzahl der Residuen mit diesem Betrag, L1).
Das ist ausdrücklich eine verfeinerte Minimax-Suche, nicht ausschließlich Linf.
L1 und L2² bekommen keine zusätzliche andere Fehlernorm als Gleichstandsregel;
bei gleichem Primärwert entscheidet die schon vereinbarte Strukturneuheit.
Alle drei Varianten haben genau dieselbe Nullmenge: die gesuchte SRG-Gleichung.

Die identischen 64 Starter werden je einmal in L1, L2 und Linf eingesetzt:
192 Plätze, 64 unterschiedliche Ausgangsgraphen. Zwischen Normvarianten findet
kein Crossover und keine Migration statt. Innerhalb jeder Variante gelten
Isomorphiededuplikation und feste Abstammungslinien. Die Stammplatzanzahlen
bleiben erhalten. Die drei Varianten erhalten abwechselnd ein Taskkontingent;
maximal drei Worker arbeiten insgesamt. Gleiche Versuchszahlen und gleiche
CPU-Obergrenzen sind nicht identisch mit gleicher tatsächlich verbrauchter
CPU-Zeit. Diese wird gesondert protokolliert.

Unverändert: acht Versuche pro Elternteil, 30 CPU-Sekunden und 256 Bewertungen
pro Versuch, bis 32 Abstiegsschritte, Tabu 8, kurze/mittlere/lange Störungen,
geführte Mutation sowie Omega-Crossover. Erst nach zehn Generationen greift
die bestehende Stagnationsanpassung. Schlechtere Zwischenstände sind weiterhin
zulässig; zusätzliche Zwischenstandsstatistiken oder Graphdateien werden nach
dem Nutzerhinweis nicht erzeugt. Übernommene Eltern werden im jeweiligen
Auswahlkriterium niemals schlechter. Das beweist keine Konvergenz zur Lösung.

## Dateien und Betrieb

Branch: memetic/office-v0.2.0-multinorm-20260911
Ausgangspunkt auf Office: d53ce5b373641868404d9200b43a083c8f632d64.
Neue Pfade: src/memetic_v2, data/memetic_v2/reference, configs/memetic_v2,
docs/memetic_v2, results/memetic_v2 und manifests/memetic_v2.
Externer Lauf: /home/rb/conway99_workspace/conway99_memetic_office_0.2.0/runs/pilot-001.
Konfiguration: configs/memetic_v2/office-0.2.0.json.
Vorhandene Python-Umgebung aus Office 0.1.0 wird unverändert weiterbenutzt.
Keine Compiler, kein CMake, keine neuen Pakete; OR-Tools 9.15.6755 und
pynauty 2.8.8.1 sind weiterhin die direkten Abhängigkeiten.

Checkpoints: drei rotierende atomare gzip-JSON-Dateien, Schema v2,
normalisierte JSON-Prüfsummen, fsync, feste Seeds und Wiederaufnahme nur bei
identischem Code, Input, Konfiguration und Laufzeitumgebung. Das alte
Checkpoint-Schema wird nicht in-place migriert. SIGTERM speichert kontrolliert;
nach Windows-Neustart setzt derselbe Startaufruf die neue Version fort.

Vor jedem Commit werden Status und vollständiges gestagtes Diff geprüft und
im externen Audit gespeichert. Push und Laufstart erfolgen erst nach vollständiger
lokaler Validierung. Der neue Launcher öffnet auch die laufende Statusanzeige.
Strg+C beendet diese Anzeige; der abgekoppelte Runner bleibt aktiv.

## CSV und Diagramme

convergence.csv: UTF-8 mit BOM, Semikolon, Dezimalpunkt, eine Kopfzeile.
In deutschem Excel über Daten / Aus Text/CSV importieren, Trennzeichen Semikolon,
Dezimalzahlen mit Gebietsschema Englisch lesen. Jede Stichprobe enthält
36 Zeilen: zehn Stämme und zwei Armgesamtwerte, jeweils für drei Zielfunktionen.
Die ersten Zeilen entstehen sofort, danach alle 600 Sekunden, zusätzlich beim
Ende. Atomare JSON-Stichproben in reports/ sichern die rekonstruierbare CSV.

Wichtige Spalten: sample_id, utc, active_seconds, phase, generation, objective,
arm, founder, population_n. Für W, L1, L2_squared und Linf jeweils
_best, _mean, _worst und _best_ever; außerdem L2_best und L2_mean.
variant_cpu_seconds und variant_completed_tasks gelten für die ganze
Normvariante und dürfen beim Gruppieren über Stämme nicht aufsummiert werden.
objective_best_graph identifiziert den nach dem Variantenkriterium besten Graphen.
Die Minima unterschiedlicher Metriken können zu unterschiedlichen Graphen gehören.

Für Diagramme nach objective/arm/founder filtern, active_seconds/3600 als
Zeitachse verwenden und beispielsweise L1_best, L1_mean, L1_best_ever zeichnen.
Die Population wechselt erst bei Generationsabschluss; _best_ever wird bereits
mit geprüften Funden während einer Generation aktualisiert. Das verhindert,
dass Wartezeit bis zur Selektion als ausbleibender Suchfortschritt missverstanden
wird. Oszillation sekundärer Metriken ist möglich, im primären Kriterium der
fortgeführten Linie gibt es durch die Auswahlregel nur Abstieg oder Plateau.
Es werden keine zusätzlichen Statistiken der schlechten Zwischenstände geführt.

## Ressourcen und Aussagegrenzen

Planung für Office: drei Worker, je ein Solverthread, niedrige Prozesspriorität.
5 GiB WSL-Limit bleibt ausreichend geplant; erwarteter Gesamtrahmen 1-3 GiB RSS.
Der kombinierte Wächter greift bei 3072 MiB gemessener RSS, einzelne Worker
bei 1100 MiB. Unter 768 MiB verfügbarem Host-RAM keine neuen Tasks; unter
384 MiB kontrollierter Stopp. Swap dient nicht als reguläres Arbeitsbudget.
Freier-Platten-Floor 10 GiB unter Linux und auf /mnt/c, wenn vorhanden.

64*3*8=1536 Versuche je gemeinsame Generation. 1536*30/3=15360 Sekunden,
also 4 h 16 min bei ausgeschöpften CPU-Budgets und voller Dreierauslastung,
zuzüglich Verwaltung; kein garantierter Wallclock-Maximalwert. Die Kalibrierung
hat 96 Versuche (bis 16 Minuten reine CPU-Verteilung). Danach 24 aktive Stunden.
Absehbar deutlich weniger Generationen als im alten 20er-Pilot; zehn volle
Generationen sind innerhalb eines Tages nicht zugesagt.

Bis zu drei logische Kerne ausgelastet, grob 37,5 Prozent von acht logischen
Prozessoren; physische Kernauslastung und Windows-Reaktionszeit hängen vom
Scheduler ab. Ein lokaler Resume-Kontrollcheckpoint lag bei etwa 1 MB.
Geplant: gewöhnliche Checkpoints jeweils unter 10 MiB, CSV wenige MiB,
Logs und Berichte typischerweise unter 0,5 GiB pro Tag, gesamter erster Lauf
unter 1 GiB. Das sind Planungswerte, keine mathematischen Obergrenzen.
Logs rotieren; Laufdaten und Populationen bleiben außerhalb des Repositorys.
ETA basiert auf gemessenem Koordinator-Durchsatz einschließlich Checkpointarbeit.
Es gibt eine ETA zum Ende des Batches und des Zeitbudgets, keine ETA zur Lösung.

## Validierung

Kontrollen prüfen alle zehn Gründer, alle 64 Starter und ihre gespeicherten
Abstammungen, gegensätzliche Normrangfolgen, 1536 getrennt gesetzte Seeds,
Normisolation beim Partner- und Nachfolgervergleich, CSV-Zeilen und Mittelwerte,
mathematische Positiv-/Negativkontrollen, echten SIGKILL und Resume bis COMPLETE.
Der vollständige Bericht liegt in results/memetic_v2/full_validation_0.2.0.json.
Vor Start auf Office wird dieselbe vollständige Kontrolle dort ausgeführt.
