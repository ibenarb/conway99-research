# λ-Folgelauf auf dem Ryzen, 22.–23. September 2026

## Gegenstand und Herkunft

Sachliche Laufdokumentation; die Entscheidung über den nächsten Versuch ist offen.
Ziel bleibt ein srg(99,14,1,2). Im λ-Arm sind Einfachheit, 99 Knoten,
Grad 14 und genau ein gemeinsamer Nachbar je Kante harte Bedingungen.
Für ungeordnete Knotenpaare ist r = gemeinsame Nachbarn + Adjazenz − 2.
W zählt Paare mit r≠0, L1 summiert |r|, F summiert r², Linf=max|r|;
Nmax zählt Paare mit |r|=Linf. F ist hier die quadrierte Norm über ungeordnete
Paare, nicht die Frobeniusnorm selbst. Ziel W wird lexikographisch als (W,L1)
verglichen; die übrigen Zielordnungen sind im Suchcode definiert.
Eine Lösung benötigt Nullresiduen, nicht lediglich λ-Gültigkeit.

- Lauf: `ryzen_lambda_followup_100_20260922` (der Name „100“ ist historisch;
  genehmigt waren 121 neue CPU-Stunden).
- Programm: [fixierter Stand 3bafd48](https://github.com/ibenarb/conway99-research/tree/3bafd487c9d9ec513da853577a6f4d2750a4e479/experiments/memetik/lambda_followup_1_0_0).
- Ursprüngliches Exportarchiv: `ryzen_lambda_followup_100_20260922_verified.tar.gz`,
  134509007 Bytes, SHA256 `5f0d95c436ab32b68e36c94802bae0d0213f603225b604c522f9030e36afb65e`.
- Vorgänger: [192-CPU-h-Vergleich](https://github.com/ibenarb/conway99-research/tree/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922).
- Vorab festgelegtes [Manifest und Startbank](https://github.com/ibenarb/conway99-research/tree/19d406fd188cfaf9de9d43bdea20c8b3fafe74fd/docs/memetik/lambda_synthesis_20260922).

## Versuchsaufbau

| Gruppe | Jobs | Neues Suchbudget | Start und Endpunkt |
|---|---:|---:|---|
| P/W | 12 | 36 CPU-h | Vorhandene 1-h-Zustände unverändert bis 4 h fortgesetzt |
| PC/W | 12 | 48 CPU-h | Ursprüngliche 16 Gründer, gepaarte Seeds, neu bis 4 h |
| TC/W | 3 | 9 CPU-h | Vorhandene Seeds 00–02 von 1 h bis 4 h |
| Rekord W | 6 | 12 CPU-h | Drei P/PC-Paare ab W=2114, je 2 h |
| Rekord Linf | 4 | 8 CPU-h | P ab (2,216,2468), je 2 h |
| Rekord L1 | 2 | 4 CPU-h | P ab L1=2388, je 2 h |

P und TC verwenden eingefrorene Originalworker. PC erweitert den P-Zugkatalog
in Perturbation und Abstieg um den vollständigen Dreierzyklus. Rekordstarts
wurden nicht in den Hauptvergleich eingespeist. Keine automatische Verlängerung.
Maximal 18 Worker; zusätzliche 4 CPU-h für Uhrenprobe, Kontrollen, Archivernte
und Infrastruktur. Diese sind vom Suchbudget getrennt.

## Abschluss und Zeitmessung

39 Jobs abgeschlossen. Abschluss der Suche: 23.09.2026, 04:29:04 UTC
(06:29:04 MESZ); Abschluss einschließlich Archivernte: 04:47:23 UTC
(06:47:23 MESZ). Hostgemessene Suchphase: 25301,985 Sekunden, rund 7 h 2 min.
Neue Such-CPU: **116,946299891 h**. Hilfs-CPU zum Auswertungszeitpunkt:
**1,366082840 h**, zusammen **118,312382731 h**. Kleine Abschlussreserven erklären,
warum die Suche nicht exakt 117 CPU-h verbraucht. Die frühere CPU-Zeit der
fortgesetzten Jobs wird nicht nochmals als neue Laufzeit gezählt.

Im Einzelworker-Test wich die WSL-Monotonuhr von der Windows-Hostzeit ab.
Laufzeit/ETA beruhen daher auf dem persistenten Windows-Zeitgeber;
Workerbudgets und CPU-Abrechnung sind davon getrennt. Originalbelege stehen
in CLOCK_PASS.json, auxiliary_ledger.json, status.json und den Job-Receipts.

## Ergebnisse

| Hauptvergleich bei 4 kumulativen CPU-h | P | PC |
|---|---:|---:|
| Bester W-Wert | 2110 | 2127 |
| Median W, zwölf Läufe | 2123 | 2136,5 |
| Gewonnene Paare nach (W,L1) | 12 | 0 |

| Getrennte Spur | Ergebnis |
|---|---|
| Rekord W mit P | W=2102, L1=2478, F=3260, Linf=3, Nmax=15 |
| Rekord W mit PC | W=2107, L1=2460, F=3192, Linf=3, Nmax=13 |
| Rekord L1 mit P | L1=2380, W=2141, F=2868, Linf=4, Nmax=1 |
| Rekord Linf mit P | (Linf,Nmax,L1)=(2,216,2468), unverändert |
| Drei TC-Fortsetzungen | Kein W unter 2141 |

Die Verbesserung von L1 gegenüber 2388 geht beim neuen Rekord mit Linf=4
statt 3 einher. Normen sind deshalb nicht austauschbar. Keine exakte Lösung.
F=2836 bleibt als bekannter beobachteter Kandidatenwert enthalten; dieser
Folgelauf war kein eigener F-Methodenvergleich.

Der Vergleich benutzt erneut bekannte Seeds und dieselbe Gründerbank. Er
beschreibt diese Versuchsanordnung; eine universelle Methodenrangfolge oder
statistische Unabhängigkeit der Startregionen folgt daraus nicht. Gleiche Seeds
erzwingen wegen verschiedener Zugkataloge keine gleichen Zufallspfade.
Die TC-Gegenprobe umfasst nur drei ausgewählte Fortsetzungen.

## Nachgelagerte Archivernte

HARVEST_SUMMARY meldet 192 bearbeitete Datenbanken im ursprünglichen
OBSERVED-Quellenbestand, 1515 gelesene Zeilen, 411 geprüfte beschriftete Graphen,
414 zielbezogene Abstiege und zehn ausgewählte Tiefe-2-Untersuchungen.
Das sind **nicht** 192 neue Suchjobs; dieser Folgelauf hat 39 Jobs.
Die Ernte veränderte keine Startbank. Herkunft und Einzelresultate stehen in
HARVEST.json. Die ursprünglichen 192 Quelldatenbanken sind nicht im Folgeexport.

## Prüfung dieser Veröffentlichung

Die Archiv-SHA256 stimmt. Das beigefügte `verify_results.py` prüfte erneut:
103 Fingerprint-Dateien, die vier Receipt-Dateihashes aller 39 Jobs
(einschließlich SQLite und Checkpoints), CPU-Sessionsummen, Endhorizonte,
erhaltene alte Kurvenpräfixe sowie λ-Gültigkeit und alle fünf Scores.
Die vom Suchkern getrennte Mengenimplementierung prüfte **1282 verschiedene
beschriftete Graphen in 3022 Graph-/Score-Einträgen**, einschließlich der
Ernte. Die frühere Chatangabe 786 bezog sich auf einen engeren Prüfumfang;
die jetzt protokollierte Anzahl stammt aus dem hier gespeicherten Prüfskript.

Prüfresultat: AUDIT.json, PASS. Kein erneuter Suchlauf und keine Reproduktion
sämtlicher Tiefe-2-Aufzählungen. Isomorphieklassenkennungen wurden hierbei
nicht unabhängig neu kanonisiert. Die Prüfung eines Scores ist kein Nachweis
für die Vollständigkeit eines Nachbarschaftskatalogs.

## Prüfsatz und Grenzen

Im flachen Prüfsatz-ZIP: Original-EVALUATION und -HARVEST, Manifest,
Abschluss-/Uhren-/Kontrollbelege, CPU-Ledger sowie je Job task/result/receipt;
ENDPOINTS.tsv und CURVES.tsv sind daraus abgeleitete Lesetabellen.
`result.json` enthält insbesondere Verbesserungsgraphen, Meilensteine,
Endpopulation, Familienangaben, beobachtete Bestwerte und Operatorstatistiken.

Das flache ZIP `lambda_followup_review_20260923_flat.zip` unter
`releases/memetik/` enthält zusätzlich sämtliche Nicht-SQLite-Nutzdateien des
Folgeexports, darunter Checkpoints, Ereignisprotokolle und eingefrorene Quellen.
FILE_INDEX.json ordnet die eindeutigen flachen Namen den Originalpfaden zu;
SHA256SUMS prüft die ZIP-Nutzdateien. Flüchtige pyc- und lock-Dateien fehlen.
Die 39 SQLite-Dateien (zusammen rund 950 MB unkomprimiert) sind ausdrücklich
nicht enthalten. Ein Reviewer kann damit die publizierten Populationen und
Kurven prüfen, aber keine vollständige Prüfung aller SQLite-Archivzustände
behaupten. Für weitergehende Archivfragen ist das Originalexportarchiv nötig.
Der Vollprüfer benötigt dieses entpackte Originalarchiv und den Git-Checkout.
