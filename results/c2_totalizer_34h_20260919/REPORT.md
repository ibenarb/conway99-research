# C2-Totalizer: Auswertung des 34-Stunden-Laufs

Run `matching_20260917_190757_558001`, Release `totalizer-long-1.0.2`,
Commit `767ed22f663cd5fe4e6d06bc184c5504388b6f86`.

## Ergebnis und Integrität

Alle elf Fälle OPEN_BUDGET, keine SAT/UNSAT-Entscheidung, kein neuer Ausschluss.
122405 Sekunden Kampagnenlaufzeit, 373.978992 CPU-Stunden. Keine abgebrochenen
Jobs, keine Beweisdateien; zwölf abgefangene Guard-Leseversuche und null
Schreibwiederholungen. Die Ressourcenprobleme früherer Läufe traten hier nicht auf.

Original-ZIP: 724032 Bytes, SHA256
`a4cb49271e2b98f7b322f068cda41ddb220fa06e1629848eb9dca61ad1a89be8`.
38 Einträge; CRC vollständig bestanden. Elfmal stimmen summary.json,
result.json und job.json überein. Loglängen geprüft, alle Logs enden mit UNKNOWN
und Exit 0. Kein unabhängiger vom Benutzer mitgelieferter ZIP-Sollhash vorhanden.

Die elf aufgezeichneten CNF-Hashes stimmen mit dem früheren A/B-Archiv überein.
Controller- und Guard-Hash stimmen mit den lokalen Dateien des veröffentlichten
34h-Releases überein. Das Archiv enthält weder die CNFs noch die Solver-Binärdatei:
deren Bytes wurden hier nicht erneut geprüft. Der Worker meldet seine vor/nach
jedem Solverlauf ausgeführten CNF-Hashprüfungen über den erfolgreichen Status.

## Was die Solver getan haben

634325720 Konflikte insgesamt. Median der profilierten Suchzeitanteile 96.95 %.
Die CPU-Zeit entspricht 99.994 % der summierten Solver-Wallzeit: kein Hinweis,
dass diese Läufe hauptsächlich auf I/O oder CPU-Zuteilung gewartet hätten.
RSS-Spitzen 596–797 MiB je Prozess. Logdateien insgesamt 3763045 Bytes.

| Matching-Typ | Konflikte (Mio.) | Variablen bei ca. 24 h | Variablen zuletzt | Abnahme danach |
|---|---:|---:|---:|---:|
| 1+1+1+1+1+1 | 68.55 | 77802 | 77345 | 0.59 % |
| 1+1+1+1+2 | 64.43 | 81531 | 80989 | 0.66 % |
| 1+1+1+3 | 55.49 | 122613 | 94327 | 23.07 % |
| 1+1+2+2 | 59.86 | 70437 | 70138 | 0.42 % |
| 1+1+4 | 60.08 | 85108 | 84418 | 0.81 % |
| 1+2+3 | 56.50 | 85493 | 84888 | 0.71 % |
| 1+5 | 56.35 | 85058 | 84517 | 0.64 % |
| 2+2+2 | 52.83 | 88800 | 81333 | 8.41 % |
| 2+4 | 53.43 | 89816 | 81361 | 9.41 % |
| 3+3 | 52.96 | 87014 | 86439 | 0.66 % |
| 6 | 53.86 | 76144 | 75239 | 1.19 % |

Die Zeitpunkte sind die jeweils letzten protokollierten Zeilen vor dem
CPU-Zeitpunkt, keine separaten Messungen zur exakt gleichen Sekunde. Die letzte
Zeile liegt kurz vor Budgetende. Verbleibende Variablen umfassen Hilfsvariablen.
Sie messen weder den Anteil ausgeschlossener Graphen noch die Beweisnähe.
Eliminierung kann außerdem die Klauselzahl vergrößern. Endstände: rund
0.87–1.44 Millionen irredundante Klauseln.

Acht Fälle verlieren zwischen ca. 24 und 34 Stunden weniger als 2 % ihrer dann
noch vorhandenen Variablen; drei zeigen größere Reduktionen. Das widerlegt einen
pauschalen Stillstand, liefert aber keine belastbare Restlaufzeitschätzung.
Insbesondere ist der Fall 6 mit den wenigsten bzw. wenigen Variablen nicht damit
als leichtester Fall identifiziert. Konfliktraten sind kein Erfolgsmaß.

## Nächster sinnvoller Versuch

Keine weitere unveränderte Langkampagne. Zunächst eine strukturell begründete
Verstärkung auf Primärvariablen untersuchen. Ein konkreter Kandidat ist die
explizite ternäre Klausel für drei verschiedene äußere Knoten x,y,z mit genau
einem gemeinsamen Rahmenlabel von x,y:

`not M_xy or not M_xz or not M_yz`.

Denn E3 lautet `M_xy + sum_z M_xz M_yz = 2 - |labels(x) intersect labels(y)|`.
Die rechte Seite ist hier 1; drei gesetzte Kanten liefern links mindestens 2.
Diese Folgerung ist bereits logisch im Encoder enthalten. Explizites Hinzufügen
kann die Propagation verkürzen, muss es aber nicht; es ist keine neue
mathematische Ausschlussaussage. Konstanten, involutionsbedingt gleiche Variablen
und doppelte Klauseln müssen vor Ausgabe korrekt normalisiert werden.

Vor einem Benchmark: Anzahl und Anteil bereits vorhandener Klauseln messen,
Implikation und Normalisierung unabhängig kontrollieren und Mehrkosten erfassen.
Nur falls die Ergänzung tatsächlich neue kurze Klauseln liefert, gleicher
Seed/gleiche elf Fälle in einem kurzen A/B-Vergleich (beispielsweise zwei Wellen
zu je 20 Minuten plus Vorbereitung). Bewertet werden Entscheidungen und
begründete Propagations-/Kostenmaße; Konfliktrate allein entscheidet nicht.
Bleibt das ohne Nutzen, ist eine feinere vollständige strukturelle Fallzerlegung
mit geprüftem Cover der nächste Ansatz. Kein automatischer Neustart ausgeführt.

## Reproduktion

`python3 analyze.py` neben dem Originalarchiv erzeugt die Kernauswertung.
`analysis.json` enthält Fallstatistiken und protokollierte Zeitpunkte.
Der Vergleich zum früheren A/B-Archiv ist ein Zusatzabgleich der aufgezeichneten
Hashfelder, kein Benchmark mit gleichen Laufzeiten.
