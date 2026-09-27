Der Auftrag ist umfangreich. Ich hole mir jetzt das Repository und die verlinkten Artefakte, um tatsächlich rechnen zu können.

47 Befehle ausgeführt

## Review: nächster Schritt nach der λ-Radiusprüfung

### Empfehlung (zuerst)

**Kein Tiefe-5-Lauf, kein F-Wechsel, kein erneuter unveränderter P-Lauf.** Als einen nächsten Schritt empfehle ich einen **kontrollierten deterministischen Basin-/Escape-Pilot** auf den beiden fixierten Rekordgraphen (Kontrollarm W2079): Für Perturbationstiefen d = 1…3 (exakt, aus den vorhandenen `layers.sqlite`) und d ∈ {4, 6, 8, 12, 16, 24, 32} (geseedete Zufallswege im unveränderten Apex/Pivot-Katalog) wird jeweils P's exakter Steilstabstieg (`LOCAL_MIN_EXACT_AP`, identischer Code) ausgeführt und gemessen: Rückkehrrate zum Start, Endwertverteilung (W,L1), Zahl verschiedener Endminima mit gleichem oder besserem W, Barrierehöhe. Budget ≤ 30 CPU-h, ≤ 12 Worker, keine automatische Fortsetzung.

Begründung in einem Satz: Der Radius-4-Befund sagt nichts über das, was P tatsächlich tut (Perturbation 2–32 plus Abstieg), und die **schon vorhandenen O-/F-Histogramme zeigen, dass 77–80 % aller P-Episoden exakt zum Elternzustand zurückkehren** (eigene Auswertung unten). Die entscheidende, noch unbeantwortete Frage ist deshalb nicht „Radius 5?“, sondern: **Ab welcher Zugtiefe verlässt ein Abstieg das Becken der Rekordgraphen überhaupt, und landet er dann jemals besser?** Davon hängt ab, ob die λ-P-Linie pausiert oder mit gezielt geänderter Perturbations-/Akzeptanzregel weitergeführt wird.

### 1. Befundprüfung

Alle Prüfungen liefen in einer isolierten Sandbox (Python 3.12, pynauty 2.8.8.1, ein Kern) auf dem geklonten Repository und den gepinnten Commits. Zeilen mit **[N]** habe ich selbst gerechnet, **[Ü]** übernommen, **[H]** Interpretation.

| AussageStatusPrüfung / Quelle                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                        |                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Archivhashes: Rückgabearchiv `7d35c3…`, Quellpaket `af297f…`, `Lambda_Review_20260926.zip` `85604a…`                                                                                                                                                                                                     | **reproduziert [N]**                                                                                                                                                                                                                   | `sha256sum` der Blobs aus `4850aa0` bzw. `c3197a2`                                              |
| 46 `SOURCE_PINS.json`-Hashes und 67 `PACKAGE.json`-Dateien byteidentisch zum Baum `8ec085c`                                                                                                                                                                                                              | **reproduziert [N]**                                                                                                                                                                                                                   | eigener Hashlauf, 0 Abweichungen                                                                |
| Drei Startgraphen: Scores, state-Hash, λ-Zulässigkeit, 231 Dreiecke, `sum_nonedge r = 0`, `F = 4(Q−2079)` mit Q = 2917 / 2874 / 2911                                                                                                                                                                     | **reproduziert [N]**                                                                                                                                                                                                                   | `indep_scores.py`, reiner networkx-Scorer ohne Projektcode                                      |
| Schichten 1/2: 99/5222 (W2076) und 95/4768 (W2077), keine Verbesserung, 9993 bzw. 9178 Evaluationen (= `prepare_2076.evaluations`)                                                                                                                                                                       | **reproduziert [N]**                                                                                                                                                                                                                   | `layers12.py`, eingefrorener Katalog                                                            |
| Positiver Kontrollpfad W2079→W2076: Schnitt der Tiefe-2-Schichten genau ein Zustand, Gesamtlänge 4                                                                                                                                                                                                       | **reproduziert [N]**                                                                                                                                                                                                                   | `layers12.py`                                                                                   |
| Wurzelkatalog W2076: 43 Apex + 56 Pivot; W2077: 35 + 60                                                                                                                                                                                                                                                  | **reproduziert [N]**                                                                                                                                                                                                                   | `layers12.py`                                                                                   |
| **Pivot-Katalog = vollständige Menge aller λ-erhaltenden 2-Switches** (Brute-Force über alle 239 778 Kantenpaare × 2 Muster: 56 bzw. 60 Treffer, Differenz zum Katalog 0)                                                                                                                                | **neu geprüft [N]**                                                                                                                                                                                                                    | `twoswitch_completeness.py`                                                                     |
| Ausgeschlossene cycle3-Züge an der Wurzel: 43 (W2076) / 35 (W2077), keiner verbessert auf Tiefe 1                                                                                                                                                                                                        | **neu geprüft [N]**                                                                                                                                                                                                                    | `cycle3_census.py`                                                                              |
| Tiefe 3 Arm W2076: 526 476 Kinder, 195 508 neue Zustände, keine Verbesserung                                                                                                                                                                                                                             | **teilweise reproduziert [N]**: Stand bei Abbruch dieses Reviews 3500/5222 Eltern, 353 918 Kinder, 155 365 neue Zustände, 0 Verbesserungen, 0 Score-Abweichungen bei der unabhängigen Stichproben-Nachbewertung; die Zählung lief noch | `depth3_hist.py`                                                                                |
| Tiefe 3 Arm W2077                                                                                                                                                                                                                                                                                        | **nicht ausgeführt [Ü]**                                                                                                                                                                                                               | –                                                                                               |
| Abdeckung Tiefe 4: 1528/1321 Jobs, ID-Intervalle lückenlos und disjunkt, decken exakt die Merge-Grenzen 5323–200 830 bzw. 4865–173 912 ab; Elternsummen 195 508/169 048; Kindersummen 19 873 151/16 408 393; alle DONE, kein Zeuge, je Arm ein Eingabehash; Merge-Zählung {0:1, 1:99, 2:5222, 3:195 508} | **aus dem kleinen Archiv reproduziert [N]**                                                                                                                                                                                            | eigenes Skript über `jobs/*/task.json`, `slice_result.json`                                     |
| CPU-Abrechnung: Summe der `self_cpu` der Tiefe-4-Jobs 18,1716/15,5704 h gegenüber Ledger 18,1764/15,5746 h (plausibler wait4-Überhang), Gesamt 34,78827 h, Hilfs 1,03725 h, Walltime 3 h 6 min 25,76 s                                                                                                   | **reproduziert [N]**                                                                                                                                                                                                                   | Arithmetik aus `RESULT.json`, Jobdateien, `controller.log` (UTC 11:42→14:48 = 13:42→16:48 MESZ) |
| BFS-Logik: Merge fügt `lower.sqlite` vor den Tiefe-3-Fragmenten mit `INSERT OR IGNORE` bei `UNIQUE(rows)` ein, Tiefe-4-Jobs expandieren genau alle Knoten mit `depth=3`; jeder Zustand in exakt Abstand 4 hat einen Vorgänger in exakt Abstand 3                                                         | **Codeprüfung, korrekt [N]**                                                                                                                                                                                                           | `enumeration.py`, `support.py`, `jobs/merge_2076/task.json`                                     |
| Radiusbegriff: beschriftete Zustände; da Züge mit Umbenennung vertauschen und W isomorphieinvariant ist, deckt die beschriftete BFS jede Klasse ab, die von der Klasse des Starts erreichbar ist                                                                                                         | **[H], mathematisch tragfähig**                                                                                                                                                                                                        | –                                                                                               |
| Die 36,28 Mio. Übergänge, die SQLite-Zustandsmengen, deren Hashes und die Host-Zeiten                                                                                                                                                                                                                    | **nicht unabhängig reproduziert**                                                                                                                                                                                                      | wie im Bericht angegeben                                                                        |
| „Katalog vollständig“ jenseits der 2-Switches (Apex = spezielle 4-Switches; ob Apex∪Pivot∪cycle3 alle λ-erhaltenden Switches bis Größe 4 erschöpft)                                                                                                                                                      | **offene Frage**                                                                                                                                                                                                                       | nicht geprüft; Brute-Force über 3-/4-Switches nicht ausgeführt                                  |

**Zentrale neue eigene Auswertung [N]** (`episode_histograms.py`, aus den `histogram`-Feldern der 16 F-/O-Resultatdateien im flachen Paket): Von 19 597 F-Episoden kehrten 15 068 (76,9 %) exakt zum Elternzustand zurück, von 33 477 O-Episoden 26 527 (79,2 %); je Job zwischen 75,8 % und 80,3 %. `isomorphic_return` ist identisch mit `returned` (keine nichttrivialen isomorphen Rückkehrer). Median der Abstiegslänge 5–6 Züge; alle Episoden endeten mit `LOCAL_MIN_EXACT_AP`. Die Perturbationsklassen 2–4 / 5–12 / 13–32 verteilen sich 15 140 / 11 009 / 7 328 (O). Eine Kreuztabelle Rückkehr × Perturbationslänge existiert nicht; die SQLite-Archive dedupliziert nach Klasse (`INSERT OR IGNORE INTO graphs(class…)`), speichern also keine Episoden – **ein SQLite-Auszug kann diese Frage nicht beantworten**, weshalb ich keine Roharchive anfordere.

### 2. Entscheidungswert des Radius-4-Befunds

Was sich gegenüber dem Vorreview tatsächlich ändert:

1. Beide Rekordgraphen sind jetzt exakte (W,L1)-Minima im Radius 4 statt 3. Die beiden letzten Rekordschritte der Kampagne (2081→2079→2076) hatten exakt Länge 4. Die Schrittweite, die zuletzt Rekorde brachte, ist damit für beide Graphen ausgeschlossen; jeder weitere Rekordschritt braucht ≥ 5 Züge.
2. Für P selbst ist das eine schwache Aussage: P perturbiert 2–32 Züge und steigt danach im Median 5–6 Züge ab. Die Rückkehrquote von \~79 % zeigt zugleich, dass die Zahl der P-Episoden die tatsächliche Erkundung der Abstand-≥5-Region um Faktor \~5 überschätzt.
3. Tiefe 5 ist keine Folgerung. Grobe Hochrechnung unter der **Annahme**, dass die Deduplikationsquote der Tiefe 4 der von Tiefe 3 entspricht (195 508/526 476 ≈ 0,37): ≈ 7,4 Mio. verschiedene Tiefe-4-Zustände, ≈ 7,4 Mio × 101 ≈ 750 Mio. Tiefe-5-Übergänge, also ≈ 37× die Tiefe-4-Kosten (≈ 1300 CPU-h) und ≈ 9,5 GB Zustandsspeicher allein für Tiefe 4 (1287 B/Zustand) – außerhalb des 10-GiB-Rahmens. Das ist eine Schätzung, keine Prognose; die Kalibrierung (Deduplikationsquote eines zusammenhängenden Tiefe-3-ID-Blocks) ist unten Teil des Pilots.
4. Ein F-Wechsel folgt aus nichts Neuem; W2077 ist nicht einmal paketintern F-optimal.

Der Befund rechtfertigt also weder weitere unveränderte Suche noch einen Abschluss aus mathematischen Gründen, sondern eine letzte begrenzte Diagnose, deren Ergebnis die Pausenentscheidung trägt.

### 3. Priorisierte Frage und verworfene Optionen

**Frage:** Wie hängt für W2076, W2077 und den Kontrollstart W2079 das Ergebnis von P's exaktem Abstieg von der Perturbationstiefe d ab: Rückkehrrate R(d), Rate strikt besserer Endpunkte E(d), Zahl verschiedener Endminima mit W ≤ W(Start)+2 (Plateauindikator)? **Entscheidung, die daran hängt:** Pause der λ-P-Linie versus gezielter Folgeversuch mit geänderter Perturbations-/Akzeptanzregel (Plateauwalk, größere Mindesttiefe) – jeweils separat zu begründen.

| OptionBeantwortetKostenVerworfen weil                                                                                  |                                                       |            |                                                                                                                                                                                                                         |
| ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A. Zusätzliche Absicherung der Radiusrechnung (lokaler SQLite-Audit, unabhängige Neu-Enumeration eines Tiefe-4-Blocks) | ob der Nullbefund technisch stimmt                    | 2–5 CPU-h  | Innere Konsistenz ist reproduziert, Tiefe 3 wird gerade unabhängig nachgezählt, 2-Switch-Vollständigkeit ist bewiesen; die Restunsicherheit ändert keine Entscheidung, weil ohnehin nicht auf Tiefe 5 hochskaliert wird |
| **B. Basin-/Escape-Pilot (gewählt)**                                                                                   | was P von diesen Starts realistisch noch leisten kann | ≤ 30 CPU-h | –                                                                                                                                                                                                                       |
| C. Zielfunktions-/Startpopulationspilot (F-Arm, cycle3-Arm, neue Bank)                                                 | ob eine andere Methode weiterkommt                    | ≥ 32 CPU-h | Ändert Zielfunktion oder Operator, bevor bekannt ist, ob das Problem das Becken oder der Operator ist; Ergebnis wäre ohne B nicht interpretierbar                                                                       |

### 4. Ausführbarer Versuchsplan

| BestandteilFestlegung     |                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Startgraphen              | Exakt die drei `STARTS.json`-Zustände `8169eba8…` (W2076), `136bad89…` (W2077), `7acadd04…` (W2079, positiver Kontrollarm; von ihm ist ein 4-Zug-Verbesserungspfad bekannt)                                                                                                                                                                                         |
| Operator                  | Unveränderter Apex/Pivot-Katalog aus `lambda_compare_0_2_0/kernel.py` (a4d4396-Pins); kein cycle3, kein Crossover, keine Migration                                                                                                                                                                                                                                  |
| Perturbation              | d = 1, 2, 3: alle beschrifteten Zustände der exakten Schichten aus `jobs/prepare_*/lower.sqlite` bzw. `jobs/merge_*/layers.sqlite` (Tiefe 3: deterministisch jeder 195. bzw. 169. Knoten nach `id`, ≈ 1000 je Arm). d ∈ {4, 6, 8, 12, 16, 24, 32}: je 300 Wege, uniforme Zugwahl mit `random.Random(sha256(state ∥ d ∥ index))`, Zug-Trace protokolliert            |
| Abstieg                   | P's Regel: vollständiger Katalog, bester strikt (W,L1)-besserer Nachbar, Abbruch bei `LOCAL_MIN_EXACT_AP`; Tie-Break deterministisch nach Zugtupel; kein Neutralzug, kein Escape                                                                                                                                                                                    |
| Zielfunktion              | Lexikographisch (W,L1) relativ zum Start; sekundär F, Linf, Nmax, nauty-Klasse des Endpunkts, Maximum von W entlang des Weges (Barriere), Abstiegslänge, beschrifteter Kantenabstand Endpunkt–Start                                                                                                                                                                 |
| Kontrollen                | (a) W2079-Arm muss bei d = 2 (Meet-in-the-middle) mindestens einen Abstieg nach W2076 liefern, sonst `DIAGNOSIS_REQUIRED`; (b) d = 1, 2 Rückkehrraten müssen ≈ 1 sein (Radius-4-Konsistenz); (c) jeder Endpunkt mit key < Start wird mit `support.witness` unabhängig nachgespielt; (d) 1 % der Endpunkte werden mit dem Standard-Python-Verifier voll nachbewertet |
| Kalibrierung              | Vor dem Hauptlauf: 30 Abstiege je Arm bei d = 8 messen (CPU/Abstieg); Deduplikationsquote der Kinder eines zusammenhängenden Blocks von 5000 Tiefe-3-Eltern (Tiefe-5-Schätzung)                                                                                                                                                                                     |
| Replikate                 | Wie oben; Vollständigkeit für d ≤ 2, deterministische Stichprobe für d = 3, N = 300 je Tiefe für d ≥ 4                                                                                                                                                                                                                                                              |
| Budget                    | Annahme aus O: ≈ 6 CPU-s je Episode → ≈ 15 000 Abstiege je Arm-Paar ≈ 25 CPU-h; harte Grenze 30 CPU-h gesamt (je Arm 12/12/6), Hilfsarbeit 2 CPU-h, keine Übertragung                                                                                                                                                                                               |
| Parallelität / Ressourcen | ≤ 12 Worker, Arbeitseinheiten zu je ≈ 100 Abstiegen, RSS-Rahmen 8 GiB (Zustandsschichten nur lesend geöffnet, `immutable=1`), Ausgaben < 2 GiB (Endpunkte als graph6 + JSON), Pause bei < 6 GiB RAM / < 25 GiB Disk; realistische Walltime 2,5–3,5 h bei 12 freien Kernen, Statusmeldung alle 10 min über den Windows-Stopwatch-Helfer                              |
| Nicht anwendbar           | Migration/Population: ein Start je Arm; Isomorphie-Pruning: keines                                                                                                                                                                                                                                                                                                  |

Getrennte Bedeutung der Ausgänge: *lokale Verbesserung* = Endpunkt mit key < Start (auch gleiches W, kleineres L1); *globaler Rekord* = W < 2076, separat zu melden; *diagnostischer Gewinn* = die Profile R(d), E(d) und die Plateauzählung, unabhängig davon, ob ein Fund eintritt.

### 5. Vorabentscheidung

- **Erfolg:** Replay-geprüfter Endpunkt mit key < Start in einem Arm. Folge: Bericht mit d\* und Barriere; nächste Entscheidung ist ein separat zu genehmigender Folgeversuch, der genau diese Tiefe nutzt – kein automatisches Hochskalieren, kein Wechsel weiterer Methodenbestandteile.
- **Negatives Ergebnis:** 0 Verbesserungen über alle Tiefen bei vollständigem N. Mit 0/300 je Tiefe liegt die 95-%-Obergrenze der Erfolgswahrscheinlichkeit je Episode bei ≈ 1 % je Tiefenklasse; zusammen mit den ≈ 4000 O-Episoden je Job ohne Rekord nach 4,75 h ist dann ein unveränderter P-Lauf von diesen Starts nicht mehr begründbar. Folge: **Pause der λ-P-Linie** (Ressourcenentscheidung).
- **Plateaubefund:** ≥ 5 verschiedene Endminima mit W ≤ W(Start)+2 in einem Arm bei E(d) = 0. Folge: Ein Plateauwalk-Pilot (Neutralzüge, Tabu auf Zuständen) wird als eigene Methodenänderung vorgeschlagen; kein Start ohne Genehmigung.
- **Unvollständig:** Budget-/Ressourcengrenze vor Abschluss aller Tiefen → `INCOMPLETE`, Profil nur für abgeschlossene Tiefen, keine Verlängerung.
- **Abbruch:** Kontrollfehler (a)–(d), Score-Abweichung, RAM/Disk-Grenze → `DIAGNOSIS_REQUIRED`, laufende fremde Prozesse unberührt.

### 6. Falls Pause: Abschluss- und Wiederaufnahmebedingung

Abschlussschritt: Archivierung der Profile, der beiden Rekordgraphen, der (W,F)-Paretofront und der Tiefe-4-Artefakte samt erhaltenen SQLite-Dateien; eine Seite „Stand der λ-P-Linie“ mit den drei Zahlen Radius 4, Rückkehrquote 79 %, E(d)-Profil. Wiederaufnahme wäre gerechtfertigt durch: (i) einen Operator, der die Rückkehrquote bei d ≤ 4 messbar senkt (z. B. Vollständigkeitsnachweis und Test eines 3-/4-Switch-Ergänzungskatalogs), (ii) ein positives E(d) > 0 aus dem Pilot, oder (iii) einen neuen Gründer mit W < 2076 aus einer anderen Linie.

### Beigefügte Auswertungen

In der Sandbox liegen `indep_scores.py` (SHA256 `e16f6c1d…`), `layers12.py`, `twoswitch_completeness.py`, `cycle3_census.py`, `episode_histograms.py`, `depth3_hist.py` mit den zugehörigen JSON-Ergebnissen; die Tiefe-3-Nachzählung für W2076 war bei Redaktionsschluss bei 3500/5222 Eltern ohne Verbesserung und ohne Score-Abweichung. Ich konnte die Dateien in dieser Antwort nicht mehr als Download bereitstellen; auf Wunsch liefere ich sie im nächsten Schritt als Prüfsatz-ZIP mit Hashes nach. Alle Aussagen oben, die auf diesen Skripten beruhen, sind als **[N]** markiert; nichts davon wurde auf dem Ryzen ausgeführt, kein Suchlauf wurde programmiert oder gestartet.

Dachte 3 s nach

Ich prüfe zuerst, ob die Sandbox und die laufende Tiefe-3-Nachzählung noch vorhanden sind.

Hat einen Befehl ausgeführt

Der Hintergrundjob wurde mit der Sandbox-Pause beendet (Stand 3500/5222 Eltern). Ich baue die Nachzählung wiederaufnahmefähig um, damit eine erneute Unterbrechung keine Arbeit mehr verliert.

10 Befehle ausgeführt · 3 Notizen

## Zwischenstand: Tiefe-3-Nachzählung und Prüfsatz

Die Sandbox wurde zwischen den beiden Antworten angehalten. Dabei ging der laufende Tiefe-3-Job verloren, er war bei 3500 von 5222 Eltern. Ich habe die Nachzählung deshalb mit Checkpoints alle 250 Eltern neu gestartet (`depth3_resume.py`). Die Eltern werden jetzt deterministisch nach gepacktem Zustand sortiert. Verschiedene Zustände werden über blake2b-128-Digests gezählt; Kollisionen setze ich als vernachlässigbar voraus.

### Neu reproduziert

**Arm W2076, Tiefe 3: vollständig und unabhängig reproduziert [N].**

| GrößeRyzen-BerichtEigene Nachzählung          |                               |                            |
| --------------------------------------------- | ----------------------------- | -------------------------- |
| Tiefe-2-Eltern                                | 5222                          | 5222                       |
| Kinder in Tiefe 3                             | 526 476                       | 526 476                    |
| Verschiedene neue Zustände in exakter Tiefe 3 | 195 508                       | 195 508                    |
| Strikt (W,L1)-bessere Kinder                  | 0                             | 0                          |
| Stichprobe mit unabhängigem Scorer            | –                             | 400 Kinder, 0 Abweichungen |
| CPU                                           | 1743,9 s (mit SQLite-Inserts) | 1262 s (ein Sandbox-Kern)  |

Damit ist die Zahl 195 508 unabhängig bestätigt, und genau diese Zahl bestimmt die Eltern der Tiefe-4-Rechnung. Die Tiefe-4-Abdeckung stützt sich jetzt auf zwei Befunde:

- die eigene Tiefe-3-Zählung,
- die schon gezeigte lückenlose ID-Partition der 1528 Tiefe-4-Jobs über 5323–200 830.

Die 19,87 Mio. Tiefe-4-Übergänge selbst habe ich weiterhin nicht neu berechnet.

**Arm W2077, Tiefe 3: noch unvollständig.** Der letzte Stand ist 2500 von 4768 Eltern, 240 108 Kinder und 126 305 neue Zustände. Die Fortschrittszeilen enthalten keinen Verbesserungszähler. Über Verbesserungen in W2077 behaupte ich deshalb nichts, bis die Abschlussdatei vorliegt. Der Checkpoint `ck_2077.pkl` liegt in der Sandbox, sofern sie erhalten bleibt.

### Nebenbefund zur Landschaft um W2076 [N/H]

Er stammt aus derselben Rechnung:

- Bester Nachbar in Tiefe 1: (2078, 2488).
- Bester Zustand in exakter Tiefe 2: (2077, 2488), also nur W+1 bei gleichem L1.
- Bester neu erreichter Zustand in exakter Tiefe 3: (2082, 2498), W+6.
- Das beste Kind überhaupt in Tiefe 3 ist (2078, 2488), ein Rückweg in eine untere Schicht.

**[H]** Um W2076 steigt die Landschaft ab Tiefe 3 deutlich an. Innerhalb von Radius 2 gibt es jedoch einen Beinahe-Plateauzustand W2077. Beides passt zur hohen Rückkehrquote von P (≈ 79 %). Für den vorgeschlagenen Basin-/Escape-Pilot hat das eine praktische Folge: Das Plateaukriterium „Endminima mit W ≤ W(Start)+2“ ist tatsächlich besetzbar und kein leerer Test. Einen Einfluss auf Tiefe 5 leite ich daraus nicht ab.

### Unverändert

Die Empfehlung aus dem Review bleibt: der kontrollierte Basin-/Escape-Pilot, kein Tiefe-5-Lauf, kein F-Wechsel, kein unveränderter P-Lauf. Die neue Reproduktion stärkt nur die Prüfbasis; die Entscheidungslage ändert sie nicht.

### Noch offen

1. **W2077, Tiefe 3 abschließen.** Das sind etwa 9 CPU-Minuten ab dem Checkpoint.
2. **Prüfsatz-ZIP bauen und bereitstellen.** Die Bestandteile liegen in der Sandbox unter `/home/claude/review/`: 
   - die Skripte `indep_scores.py`, `layers12.py`, `twoswitch_completeness.py`, `cycle3_census.py`, `episode_histograms.py`, `depth3_resume.py` samt JSON-Ergebnissen,
   - `depth3_2076.json`,
   - `QUELLEN.json` mit den Hashes der gepinnten Commits, Eingabearchive und Quelldateien sowie den Umgebungsangaben.
    Der Hash der gelesenen Promptdatei ist `5accc580d2ef50f3994565646d896c452766b1b52f6bf490e8b388ea5680b731`.

Das Werkzeuglimit dieser Antwort ist erreicht. Mit „Weiter“ setze ich W2077 am Checkpoint fort und liefere danach das ZIP mit Hash. Falls die Sandbox inzwischen zurückgesetzt wurde, beginnt W2077 von vorn, was etwa 20 CPU-Minuten kostet. Das Ergebnis für W2076 steht dann nur noch in dieser Antwort und müsste für das ZIP neu gerechnet werden (etwa 21 CPU-Minuten).

Weiter

Hat einen Befehl ausgeführt

Sandbox und Checkpoint sind erhalten (Stand 3000/4768 Eltern). Ich setze W2077 am Checkpoint fort.

4 Befehle ausgeführt, dateien geteilt · 2 Notizen

Die Tiefe-3-Nachzählung ist für beide Arme abgeschlossen, und der Prüfsatz liegt unten als ZIP.

**Ergebnis:** Beide Arme stimmen exakt mit dem Ryzen-Lauf überein.

| ArmKinderNeue verschiedene Tiefe-3-ZuständeVerbesserndStichprobe mit unabhängigem Scorer |         |         |   |                            |
| ---------------------------------------------------------------------------------------- | ------- | ------- | - | -------------------------- |
| W2076                                                                                    | 526 476 | 195 508 | 0 | 400 Kinder, 0 Abweichungen |
| W2077                                                                                    | 459 185 | 169 048 | 0 | 400 Kinder, 0 Abweichungen |

Damit sind die Elternmengen der Tiefe-4-Rechnung in ihrer Größe unabhängig bestätigt. Zusammen mit der lückenlosen Job-ID-Partition ist die Abdeckung von Tiefe 4 gut gestützt. Die 36,28 Mio. Tiefe-4-Übergänge selbst habe ich weiterhin nicht neu berechnet.

**Korrektur zu meiner letzten Antwort:** Dort hatte ich geschrieben, das Plateaukriterium des Pilots „W ≤ W(Start)+2“ sei besetzbar. Das gilt nur für W2076.

| ArmBester Zustand in Tiefe 1Tiefe 2Tiefe 3 |              |              |              |
| ------------------------------------------ | ------------ | ------------ | ------------ |
| W2076                                      | (2078, 2488) | (2077, 2488) | (2082, 2498) |
| W2077                                      | (2080, 2436) | (2083, 2452) | (2085, 2450) |

- **W2076:** Innerhalb von Radius 2 gibt es je genau einen Zustand mit W ≤ 2078.
- **W2077:** Innerhalb von Radius 3 gibt es keinen einzigen Zustand mit W ≤ 2079. W2077 ist also deutlich isolierter.

Für den Pilot folgt daraus keine Planänderung. Die Kriterien sollten aber je Arm getrennt ausgewertet werden, denn ein Plateaubefund ist bei W2077 von vornherein weniger wahrscheinlich.

**Inhalt des ZIPs:**

- sechs Prüfskripte mit ihren JSON-Ergebnissen,
- die Protokolle beider Tiefe-3-Läufe,
- `QUELLEN.json` mit gepinnten Commits, Eingabehashes und Umgebung,
- der gelesene Reviewprompt,
- eine README mit Ergebnistabellen und Prüfgrenzen,
- `SHA256SUMS` über alle 20 übrigen Dateien.

SHA256 des ZIPs: `2299db62ac1b77ed90b2e83a7be6101970f7725e4d73e539f032497c0d1d9f69`.

Nächster Schritt für dich: Prüfe nach dem Herunterladen den Hash.

`sha256sum review_lambda_radius_20260927.zip`