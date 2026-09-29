# Review λ-Reparatur 1.2.0 — drei Perspektiven und strittige Gesamtempfehlung

Stand 29.09.2026. Auftrag: `docs/memetik/lambda_repair_results_20260929/REVIEWERPROMPT.md`, Zweig `memetik`, Commit `68001f9f5aae97a3550d6039dfe731e0dd394e18`.

**Kennzeichnung.** [N] selbst nachgerechnet in der Sandbox (ein Kern, 4 GB RAM, CP-SAT 9.14.6206 wie im Lauf, keine Zertifikate). [Ü] aus Projektdokumenten übernommen. [L] Literatur mit Quellenangabe in Anhang A. [H] Hypothese oder Interpretation.

**Arbeitsreihenfolge.** (1) Paket und Rohdaten gelesen, eigene Rechnungen. (2) Drei Berichte und Empfehlung entworfen. (3) Nachtrag: Kugeltests am 60er-Modell (§2.5), noch vor der Agentenlektüre. (4) Erst danach `AGENT_A/B/C` und `SYNTHESE.md` gelesen; der Abgleich steht getrennt in §7. Die Abschnitte 3 bis 6 enthalten gegenüber dem Entwurf nur die Kugeltests und zwei Zählkorrekturen (§2.3), keine Anpassung an die Agentenberichte.

**Korrektur gegenüber der ersten Chatfassung.** Bei der Neuauszählung ergeben sich 36 statt 34 eindeutige 24er-Fenster und 42 statt 41 bewegliche 40er-Fenster; entsprechend sind mindestens 31 statt 29 der 43 OPTIMAL-Meldungen der Größe 24 reine Eindeutigkeitsaussagen. Die Einzelergebnisse waren richtig, nur die Summen waren verzählt.

---

## 0 Kurzfassung

- **Budget ging an den Engpass vorbei.** 91 % der Kampagnen-CPU flossen in 48 Fenster der Größe 60. Dort arbeitete CP-SAT mit einem einzigen Worker LP-gestützt; nach der Hint-Phase kamen im Median rund 2 950 Konflikte in zwei Stunden zustande [N].
- **Die einzige Verbesserung ist ein Sternzug:** drei Linien durch einen Punkt, zyklisch neu gepaart, sechs Kanten [N].
- **Ein exakter Sternzensus** (0,1 s je Graph) findet 11 verbessernde Züge bei 8 von 24 Gründern. Nur 2 davon lagen in irgendeinem Kampagnenfenster [N].
- **Eine enthaltene Verbesserung wurde verfehlt.** Im Fenster `2077_09_s60_defect` lag die zulässige Verbesserung 2170→2155; CP-SAT fand sie in 7200 s nicht. Mit Hamming-Kugel r=8 **und** abgeschalteter LP-Relaxation findet derselbe Solver sie nach rund 40 s Wanduhr. Kugel mit LP oder LP-frei ohne Kugel: nicht in 200 s [N].
- **Kleine Fenster sind meist eindeutig.** 36 von 48 der 24er-Fenster haben überhaupt keine andere zulässige Füllung [N].
- **Rekorde bleiben lokal minimal.** 2076 und 2077 sind bis Tiefe 2 sternminimal; der Sternabstieg aller 25 Klassen bringt keinen Rekord [N].
- **Neue exakte Umformulierung (Maverick).** srg(99,14,1,2) existiert genau dann, wenn es einen Graphen mit höchstens einem gemeinsamen Nachbarn auf Kanten, höchstens zwei auf Nichtkanten und 693 Kanten gibt (§5, M1) [N].
- **Strittige Empfehlung:** kein Hauptlauf. Stattdessen die Kalibrierung **K0** mit Katalogzensus, einem faktoriellen Vergleich der Solverbetriebsart auf denselben 48 Fenstern und einer Kalibrierung am bekannten srg(243,22,1,2). Budgetobergrenze etwa 190 CPU-h, keine Laufzeitzusage.

| Kategorie | Stand |
|---|---|
| Rekordverbesserung | keine; W = 2076 bleibt [Ü, N] |
| Neue Graphklassen | Sandbox-Abstiege erzeugen neue beschriftete Graphen (z. B. W 2118, 2136); nicht kanonisiert, daher keine Klassenbehauptung |
| Mechanismusnachweis | (a) Die Verbesserung von 1.2.0 ist ein Sternzug. (b) Große Fenster verfehlen eine enthaltene 6-Kanten-Verbesserung in der Betriebsart von 1.2.0 und finden sie mit Kugel ohne LP. (c) Die Radius-16-Lösung 2140 zerfällt in drei gültige Sternzüge. |
| Zertifizierte Aussagen | keine. CP-SAT-Meldungen sind unzertifiziert; der Sternzensus ist eine deterministische exakte Aufzählung ohne unabhängige Zweitimplementierung. |

---

## 1 Datengrundlage und Prüfumfang

Hochgeladen war nur der Prompt. Das Paket stammt aus Git: `docs/memetik/lambda_repair_results_20260929` in `68001f9`, einschließlich `RESULTS_120.tar.gz`; Quellen und Manifest von 1.2.0 aus `experiments/memetik/lambda_repair_1_2_0` (`24489ef`); Pilotplan `lambda_repair_pilot_20260927/PLAN_V2.md` und `prepare_manifest.py`; Regeln `docs/EXPERIMENT_RULES.md` und `docs/operations/GLOBAL_CONCLUSIONS.md` (GC-01 bis GC-11).

**Ausgewertet:** BERICHT, SUMMARY, TASKS_120.csv, CANDIDATES_25.json, alle 139 Jobverzeichnisse des Archivs (`model.json`, `result.json`, Solverprotokolle). 139 statt 144 Verzeichnisse sind konsistent mit den fünf starren Fenstern ohne Solverjob.

**Nicht geprüft:** RUN110-Rohdaten, `FILE_INDEX.json`, `SOURCE_SHA256SUMS.txt`, HISTORY-Dateien in Paketform, Ledger- und Receiptsummen, ein Lauf von `analyze.py`. Kanonische Klassen für neue Sandbox-Graphen wurden nicht berechnet.

---

## 2 Befundkern

### 2.1 Wohin die CPU ging [N]

| Fenster | Aufgaben und Status | CPU je Aufgabe | Modell (Median) | Solverkonflikte (Median) |
|---|---|---|---|---|
| 24 | 43 OPTIMAL, 5 starr | etwa 2 s | 14 525 Variablen | 0 |
| 40 | 45 OPTIMAL, 3 UNKNOWN | Median etwa 6 s bei OPTIMAL | 42 981 Variablen | 0 (Maximum 47 809) |
| 60 | 48 UNKNOWN | 7 200 s | 120 871 Variablen, 330 731 Constraints | etwa 2 950 (Maximum 5 640) |

Die Aufgaben verbrauchten zusammen 105,0 CPU-h, davon 96,0 CPU-h (91 %) in den 60er-Fenstern. Die Solverschranke `bound/50000` liegt dort zwischen 509,3 und 860,7 (Median 699,6). Wegen L1 ≤ 49 896 entspricht das ungefähr einer unteren W-Schranke dieser Größe; der Abstand zu den gefundenen W-Werten beträgt im Median rund 1 410.

### 2.2 Was in den 60er-Fenstern geschah [N]

Jedes Protokoll zeigt `Starting search ... with 1 workers` und `1 full problem subsolver: [main]`. Es liefen also weder LNS noch Feasibility Jump noch lokale Suche, nur die LP-gestützte Baumsuche; im Median etwa 12 Mio. LP-Iterationen je Aufgabe.

Die einzige Verbesserung (`2077_08_s60_defect`) entstand in der Hint-Phase nach 67,4 s Wanduhr (78,5 s Prozess-CPU, Protokollmarke `main [hint]`). Danach folgten knapp zwei Stunden mit 2 981 Konflikten und ohne weiteren Fund. Laut BERICHT wurde derselbe Graph schon in 1.1.0 gefunden [Ü]. Die Verdopplung des Budgets betraf damit ausschließlich eine Phase, die nichts mehr beitrug.

### 2.3 Beweglichkeit der festen Fenster [N]

`alt.py` ersetzt die Zielfunktion durch die Bedingung „mindestens eine variable Kante weicht vom Gründer ab“; Grad 14, λ = 1 und der Rand bleiben hart.

- **24er-Fenster:** 36 von 48 haben keine andere zulässige Füllung (die 5 starren eingeschlossen). Mindestens 31 der 43 OPTIMAL-Meldungen dieser Größe sind damit reine Eindeutigkeitsaussagen. Die übrigen 12 Fenster haben Alternativen mit genau 4 geänderten Kanten; keine ist besser, eine hat gleiches W und schlechteres L1.
- **40er-Fenster:** 42 von 48 haben Alternativen mit 4 bis 80 geänderten Kanten; keine ist besser, im Einklang mit den OPTIMAL-Meldungen.

Alle diese Statusmeldungen sind unzertifiziert.

**Strukturmerkmale (Median).** Anteil des Gründer-W auf Paaren, die das Fenster berühren: 46 %, 68 % und 87 % für die Größen 24, 40 und 60. Von den 7 Linien je Knoten liegen im Mittel 0,5, 1,2 bis 1,3 und 2,6 vollständig im Fenster. Die übrigen Linien kreuzen den festen Rand.

### 2.4 Sternzüge [N]

**Definition.** An einem Punkt p wird das perfekte Matching der 14 Nachbarn (die 7 Linien durch p) durch ein anderes perfektes Matching ersetzt. Pivot (zwei Linien) und Dreierzyklus (drei Linien) sind Spezialfälle.

**Zulässigkeitskriterium** (selbst hergeleitet). Der Zug erhält Grad 14 und λ = 1 genau dann, wenn jedes neue Paar {x, y} bisher nicht benachbart ist und x, y keinen gemeinsamen Nachbarn außerhalb von N[p] haben.

*Begründung:* Innerhalb von N[p] hat x nach dem Zug genau p und den neuen Partner als Nachbarn. Kanten von x nach außen sind nur betroffen, wenn der Außenknoten auch zum neuen Partner benachbart ist; genau das schließt die Bedingung aus. Die Entfernung des alten Partners erzeugt keine Verletzung, weil der alte Partner außer p keinen gemeinsamen Nachbarn mit Außenknoten von x haben konnte.

Jeder angewandte Zug wurde zusätzlich mit einer vollen λ-Prüfung kontrolliert. Kontrolle: Der Zensus am Gründer 2139 findet genau die Kampagnenverbesserung auf (2127, 2498) an p = 7.

**Zensus über alle 25 Poolklassen.** 149 bis 204 zulässige Sternzüge je Graph, im Median einer je Punkt; Rechenzeit 0,1 s je Graph.

| Gründer | (W, L1) | bester Sternzug | Träger | in einem Kampagnenfenster? |
|---|---|---|---|---|
| 2076_07 | (2175, 2636) | (2173, 2626) an p 69 | 6 | nein |
| 2076_11 | (2157, 2584) | (2150, 2584) an p 12 | 8 | nein |
| 2077_04 | (2088, 2466) | (2084, 2464) an p 47; zusätzlich (2085, 2456) an p 54 | 6 | nein |
| 2077_06 | (2089, 2468) | (2085, 2464) an p 28 | 6 | nein |
| 2077_08 | (2139, 2516) | (2127, 2498) an p 7 | 6 | ja, s60_defect (gefunden) |
| 2077_09 | (2170, 2590) | (2155, 2564) an p 15 | 6 | ja, s60_defect (**nicht gefunden**) |
| 2077_11 | (2176, 2588) | drei Züge, bis (2173, 2580) | 6–8 | nein |
| 2077_12 | (2128, 2518) | (2125, 2530) an p 1 | 6 | nein |

Auch die neue Klasse 2127 hat noch zwei verbessernde Sternzüge; der beste führt auf (2119, 2484).

**Steilster Abstieg nur mit Sternzügen:**
- (2088, 2466) → (2084, 2464)
- (2089, 2468) → (2081, 2458)
- (2127, 2498) → (2118, 2480)
- (2128, 2518) → (2125, 2530)
- (2139, 2516) → (2118, 2480)
- (2157, 2584) → (2150, 2584)
- (2170, 2590) → (2136, 2534)
- (2175, 2636) → (2173, 2626)
- (2176, 2588) → (2168, 2586)

Die übrigen 16 Klassen sind sternminimal. Kein Endpunkt liegt unter 2076.

**Tiefe 2 an den Rekordklassen:**
- (2076, 2488): 184 Züge und 35 414 Zweierfolgen, keine Verbesserung.
- (2077, 2436): 157 Züge und 25 526 Zweierfolgen, keine Verbesserung.
- (2077, 2488): erreicht in zwei Zügen den bekannten Graphen (2076, 2488).

### 2.5 Verfehlte Verbesserung und Betriebsart [N]

`check2077_09.py` fixiert im Kampagnenmodell von `2077_09_s60_defect` die Kanten des Sternzugs an p = 15: Das Modell ist zulässig mit Ziel 107 752 564, also (2155, 2564). Die Kampagne endete nach 7 200 s bei (2170, 2590).

Kugeltests am selben Modell (`localbranch.py`, ein Worker, Solverwanduhr auf einem Sandbox-Kern, Einzelläufe mit Standardseed):

| Fenster | Betriebsart | Solverzeit | Ergebnis | Konflikte |
|---|---|---|---|---|
| 2077_09 | Kugel r=8, LP wie in 1.2.0 | 200 s | 2170, kein Fund | 620 |
| 2077_09 | ohne Kugel, `linearization_level=0` | 200 s | 2170, kein Fund | 55 991 |
| 2077_09 | Kugel r=8, ohne LP | 120 s | **2155 nach 39,8 s** (Presolve etwa 21 s) | 31 919 |
| 2077_08 | Kugel r=8, ohne LP (Kontrolle) | 120 s | **2127 nach 24,8 s** | 41 862 |
| 2077_09 | Kugel r=16, ohne LP | 100–150 s | **2140 nach etwa 80–86 s** | 14 334–29 549 |
| 2076_01 | Kugel r=16, ohne LP | 120 s | 2076, nichts gefunden (UNKNOWN) | 23 457 |

**Die Radius-16-Lösung 2140** ändert 14 Kanten und ersetzt 7 Linien. Sie zerfällt in drei Sternzüge: an p 15, danach an p 26, danach an p 6. Alle Zwischenzustände sind gültige λ-Graphen, der Weg ist monoton: 2170 → 2155 → 2141 → 2140 (`seqcheck.py`). Der Zug an p 26 ist erst nach dem Zug an p 15 zulässig. Das Fenster hat hier also eine Folge von Katalogzügen gefunden, nichts darüber hinaus.

**Einordnung [H].** Beide Faktoren wirken zusammen: Die LP-Relaxation drückt den Konfliktdurchsatz um etwa zwei Größenordnungen, die Kugel lenkt die Suche in die Nähe des Gründers. Die Tests sind Einzelläufe in der Sandbox; sie belegen einen Mechanismus, keine Rate und keine Ryzen-Laufzeit.

---

## 3 Bericht 1 — Optimierer

**Diagnose.** Das Budget je Aufgabe ist nicht der Engpass. Es sind drei:

1. **Platzierung.** Feste, entlang von Kanten gewachsene Fenster treffen die kleinen Träger verbessernder Züge kaum (2 von 11).
2. **Betriebsart.** In großen Fenstern arbeitet ein einzelner LP-gestützter Worker praktisch ohne Suchfortschritt; eine enthaltene 6-Kanten-Verbesserung blieb unentdeckt, obwohl eine Kugel ohne LP sie in Sekunden findet.
3. **Keine Wiederverwendung.** Gefundene Graphen werden nicht weiter verbessert; schon 2127 hat wieder verbessernde Sternzüge.

Kleine Fenster sind überwiegend eindeutig; die Zahl der „lokalen Optima“ überschätzt deshalb die geprüfte Landschaft.

### O1 — Zugkatalog vor Fenstern

**Mechanismus.** Exakter Zensus bis Tiefe 2 für drei Zugfamilien: Sternneupaarungen, Kompositionen zweier Sternzüge und nicht konkurrente Linientrades mit 3 Linien. Alle Gründer werden zuerst auf katalogminimale Punkte abgestiegen. Fenster messen danach nur noch, was sie über den Katalog hinaus leisten.

**Gegenargumente.**
- Die Rekorde sind sternminimal bis Tiefe 2, die Gewinne anderswo betragen 2 bis 34 W. Ein Weg zu W = 0 ergibt sich daraus nicht.
- Die Gefahr, die ruhende P-Linie in neuer Form fortzusetzen, ist real.

**Messbare Hypothese.** Mindestens 30 % der Archivendpunkte sind nicht sternminimal. An 2076 und 2077 gibt es bis Tiefe 3 im erweiterten Katalog keine Verbesserung.

**Kleinster aussagekräftiger Vergleich.** Die 25 Poolklassen unter drei Katalogen: Apex ∪ Pivot, zusätzlich Stern, zusätzlich Stern und 3-Linien. Dazu das geprüfte Profilarchiv (`ccdb709a…`) als Stichprobe von mindestens 1 000 Endpunkten.

**Gründer und Operatoren.** Alle 25 Klassen und Archivendpunkte. Operatoren: Apex, Pivot, Stern (k ≤ 7 Linien), 3-Linien-Trades.

**Budget.** Höchstens 24 CPU-h, vor allem für den 3-Linien-Enumerator und die Archivstichprobe. Der Sternzensus allein braucht Minuten.

**Erfolg und Widerlegung.** Jede Klasse mit W < 2076 ist ein Rekordkandidat und muss unabhängig geprüft werden. Bleiben die Rekorde minimal, folgt eine exakt ausgezählte Radiusaussage für genau diesen Katalog, ohne Zertifikat. Die Hypothese ist widerlegt, wenn weniger als 10 % der Archivendpunkte nicht sternminimal sind; dann bringt der Katalog nur Einzelfälle.

**Kategorie.** Mechanismus- und Landschaftsbefund; Rekord nur als Nebenprodukt.

### O2 — Betriebsart großer Fenster

**Mechanismus.** Faktorieller Vergleich auf denselben 48 Fenstern der Größe 60, mit den Faktoren LP ja/nein und Kugel ja/nein:

- **B0 (Basis):** LP an, keine Kugel. Das ist 1.2.0 selbst; die Werte zu jedem Zeitpunkt stammen aus dessen Protokollen, ohne neuen Lauf.
- **B1:** LP aus (`linearization_level=0`), keine Kugel.
- **B2:** LP an, Kugel.
- **B3:** LP aus, Kugel. Lokales Verzweigen mit Radius 8, danach 16, danach 32; nach jedem Fund wird die Kugel neu zentriert.
- **B4 (Portfolio):** 4 Worker einschließlich LNS, Standardparameter.

Jede Verbesserung wird in Linientrades zerlegt und gegen den Katalog aus O1 geprüft.

**Gegenargumente.**
- Mehr Worker je Aufgabe bedeuten weniger parallele Aufgaben.
- B3 findet möglicherweise nur Katalogzüge, wie bei 2140.
- Kugeln begrenzen gerade die großen kollektiven Änderungen, derentwegen man große Fenster überhaupt baut.

**Messbare Hypothese.**
- B3 findet beide bekannten enthaltenen Verbesserungen (2077_08, 2077_09) jeweils innerhalb von 300 CPU-s.
- B3 verbessert mindestens 6 der 48 Fenster, B0 dagegen 1.
- Mindestens eine Verbesserung ist nicht aus Sternzügen, Apex und Pivot zusammengesetzt.

**Kleinster aussagekräftiger Vergleich.** Die vier neuen Arme auf den 48 Fenstern mit gleichem CPU-Budget je Fenster; B0 aus Protokollen.

**Gründer und Operatoren.** Die 24 Gründer aus 1.2.0 unverändert, damit der Vergleich mit 1.2.0 gilt. Ein zweiter Durchgang von katalogminimalen Starts aus O1 folgt nur bei positivem Ergebnis.

**Budget.** 4 Arme × 48 Fenster × 1 800 CPU-s = 96 CPU-h, dazu 6 CPU-h Hilfszeit. Beim Portfolio zählt die Summe der 4 Worker.

**Erfolg und Widerlegung.**
- **Erfolg:** Kriterien der Hypothese erfüllt. Dann wird B3 zur lokalen Optimierung für O3.
- **Widerlegung:** B3 findet nur Katalogzüge. Dann lohnen große feste Fenster keine Solverzeit mehr; die Ressourcen gehen an O1 und die Maverick-Optionen.

UNKNOWN bleibt UNKNOWN; eine Zeitgrenze ist kein Ausschluss.

**Kategorie.** Mechanismusnachweis; Rekordchance gering.

### O3 — Iterierte Fenstersuche auf Sternvereinigungen

**Mechanismus.**
- **Fenster:** N[p] ∪ N[q], gegebenenfalls ∪ N[r], mit p und q an Nichtkantenpaaren mit CN ≠ 2; 29 bis 43 Knoten. Anders als in 1.2.0 wachsen die Fenster also nicht entlang von Kanten, sondern über Linienbüschel.
- **Solver:** Betriebsart B3, Radius höchstens 16, 30 bis 60 s je Fenster.
- **Annahme:** strikt besseres (W, L1) oder gleiches W mit kleinerem L1. Danach wird neu zentriert.
- **Tabu:** Eine Tabuliste auf Fenster-Hashes verhindert Wiederholungen.

**Gegenargumente.** Die 40er-Fenster waren bereits optimal; Büschelvereinigungen könnten nur Sternkompositionen reproduzieren.

**Messbare Hypothese.** Von katalogminimalen Starts erreicht O3 bei mindestens 5 von 25 Starts Verbesserungen, die sich nicht in Katalogzüge zerlegen lassen.

**Kleinster aussagekräftiger Vergleich.** 25 Starts × 2 Arme × 2 CPU-h. Arm 1: Büschelfenster. Arm 2: Wachstumsregel aus 1.2.0 bei gleicher Größe und gleicher Betriebsart.

**Budget.** 100 CPU-h.

**Erfolg und Widerlegung.** Erfolg bei Gewinnen außerhalb des Katalogs oder W < 2076. Widerlegt, wenn beide Arme nur Katalogzüge liefern.

**Kategorie.** Mechanismusnachweis; Rekordchance gering bis mäßig.

---

## 4 Bericht 2 — Hubschrauber

**Diagnose aus der Geschichte [Ü].**
- **Ertrag:** Über mehrere hundert CPU-h fiel W vom HoG-Start bis 2076 mit logarithmisch abnehmendem Ertrag.
- **Gründer:** Alle 24 Gründer von 1.2.0 stammen aus den zwei Profilarmen um 2076 und 2077 (`PLAN_V2.md`).
- **Suchraum:** Jede bisherige konstruktive Suche war lokal in einem Raum mit exaktem Grad und exaktem λ.
- **Abstand zum Ziel:** Bei W = 2076 ist rund die Hälfte der 4 158 Nichtkantenpaare falsch.

**Außenlage [L].**
- **Automorphismen:**
  - Makhnev–Minakova: Die Gruppenordnung teilt 2·3³·7·11, bei gerader Ordnung sogar 42.
  - Cesarz–Woldar: 7 teilt die Ordnung ⇒ ℤ₇; gerade Ordnung ⇒ ℤ₂, ℤ₆ oder S₃.
  - Behbahani–Lam: Nur die Primordnungen 2 und 3 überleben eine Orbitmatrix-Rechnung, also ein computergestütztes Resultat.
  - Folgerung: Ein Zielgraph wäre fast oder ganz asymmetrisch.
- **Geometrie:** Ein λ = 1-Graph ist der Kollinearitätsgraph einer partiellen linearen Struktur mit Linien der Größe 3. Mit der μ-Bedingung ist das Ziel genau ein Partial Quadrangle PQ(2, 6, 2) im Sinne von Cameron (1975).
- **Familie:** λ = 1, μ = 2 enthält die bekannten srg(9,4,1,2) und srg(243,22,1,2). Der zweite stammt von Berlekamp, van Lint und Seidel aus dem ternären Golay-Code. Reimbayev vermutet Nichtexistenz im 99er-Fall, falls eine untere Schranke für Sechsecke erreicht wird; die beiden bekannten Graphen erreichen sie.
- **Verfahren:**
  - Hill-Climbing für Designs (Stinson 1985; Dinitz–Stinson 1987).
  - Markovketten über uneigentliche Zustände mit genau einem Eintrag −1 (Jacobson–Matthews 1996; kurzer Zusammenhangsbeweis über Bitrades bei Aryapoor–Mahmoodian).
  - Tabu-Suche und AlphaZero mit Curriculum für kantenmaximale Graphen ohne 3- und 4-Kreise (Mehrabian u. a., IJCAI 2024).
  - Eine SAT-basierte Arbeit zum Conway-99-Problem (arXiv:2604.23037, nur Literaturverzeichnis gelesen).
- **Konkurrenz:** Epoch AI führt das Problem als offene KI-Konstruktionsaufgabe mit automatischem Prüfer.

### H1 — Gründerfabrik aus der Designtheorie

**Mechanismus.**
- **Zustand:** eine partielle, dreiecksfreie lineare Tripelstruktur auf 99 Punkten mit höchstens 7 Linien je Punkt. Dreiecksfrei heißt: Drei paarweise kollineare Punkte liegen immer auf einer gemeinsamen Linie.
- **Züge nach Stinson:** Linie ergänzen, wenn möglich. Sonst die blockierende Linie entfernen und die neue einsetzen.
- **Ende:** Bei 231 Linien liegt ein 14-regulärer λ = 1-Graph vor; es folgt der Katalogabstieg aus O1.
- **Zweck:** Tausende unabhängiger Becken statt Varianten der HoG-Linie.

**Gegenargumente.** Nicht-HoG-Familien lagen historisch mehr als 100 W zurück [Ü]. Zufällige λ-Graphen starten vermutlich deutlich über 2 300 [H].

**Messbare Hypothese.** Nach Katalogabstieg landen mindestens 1 % der Starts innerhalb von 2076 + 40.

**Kleinster aussagekräftiger Vergleich.** 10 000 Fabrikstarts gegen 1 000 zufällig gezogene Archivendpunkte, gleicher Katalogabstieg.

**Budget.** 48 CPU-h; die Generatorkosten sind vorab zu kalibrieren (GC-05).

**Erfolg und Widerlegung.** Erfolg bei W < 2076 oder mindestens 1 % innerhalb von +40. Widerlegt, wenn der beste Abstieg bei 2150 oder darüber bleibt.

**Kategorie.** Neue Graphklassen; Rekord unwahrscheinlich.

### H2 — Suche im Symmetriequotienten als Brücke zu den exakten Linien

**Mechanismus.**
- **Gruppen:** nur ℤ₃ fixpunktfrei (τ = 6) oder ℤ₂ mit den literaturverträglichen Fixpunktstrukturen.
- **Suche:** Die Suche läuft auf Bahnen, mit Sternzügen auf Bahnebene.
- **Verwertung:** Endpunkte gehen als Würfelhinweise an die O3-SAT-Linie (Ordnung 3, QSAT) und an die C2-Linie, nach Symmetriebrechung außerdem als Gründer in den asymmetrischen Raum.

**Gegenargumente.**
- Wird der jeweilige Fall durch die exakten Linien ausgeschlossen, ist der Arm gegenstandslos.
- Frühere Z33-Gründer trugen eine für Zielgraphen unmögliche Symmetrie [Ü].
- Ein Quotientenoptimum ist kein Hinweis auf ein asymmetrisches Optimum.

**Messbare Hypothese.** Quotientenendpunkte erreichen nach Symmetriebrechung und Katalogabstieg Werte innerhalb von +60 der Linie A/B.

**Kleinster aussagekräftiger Vergleich.** 200 ℤ₃-Starts gegen 200 H1-Starts bei gleichem Abstieg.

**Budget.** 24 CPU-h auf dem Ryzen; Office und die C2-Arbeit bleiben unberührt.

**Kategorie.** Neue Graphklassen und Werkzeug für die exakten Linien.

### H3 — Werkzeuge der Extremalgraphensuche auf der Packungsformulierung

**Mechanismus.** Die Packungsformulierung aus M1 ist vom selben Typ wie das Problem bei Mehrabian u. a.: maximale Kantenzahl unter lokalen verbotenen Konfigurationen. Übernommen würde Tabu-Suche mit Curriculum, das aus dem kanonischen Rahmen 1 + 14 + 84 wächst.

**Gegenargument.** Dort gibt es kein Gleichheitsziel; hier wird ein perfektes Extremobjekt gesucht.

**Budget.** Pilot 24 CPU-h. Die Überschneidung mit M1 ist beabsichtigt: Hubschrauber und Maverick kommen unabhängig voneinander hier an.

---

## 5 Bericht 3 — Maverick

**Infrage gestellte Annahmen.**
- **Grad und λ exakt:** Dadurch summieren sich die Residuen auf Nichtkanten zu null, und jeder Mangel ist an einen Überschuss gekoppelt.
- **W als Ziel:** W sank durch Konzentration der Residuen, während F stieg [Ü].
- **Gründer:** Sie stammen aus zwei Linien.
- **Lokale Reparatur:** Um die Rekorde gilt ein Radius von mindestens 4 unter Apex ∪ Pivot [Ü] und Sternminimalität bis Tiefe 2 [N].
- **Existenz:** Solange der 99er-Graph nicht existieren muss, ist ein Scheitern ohne Kontrollfall mit bekannter Lösung nicht interpretierbar.

### M1 — Packungsformulierung

**Satz [N, elementar].** srg(99,14,1,2) existiert genau dann, wenn es einen Graphen G auf 99 Knoten gibt mit
- höchstens einem gemeinsamen Nachbarn für jede Kante,
- höchstens zwei gemeinsamen Nachbarn für jede Nichtkante und
- 693 Kanten.

**Beweis.**
1. Die Summe der gemeinsamen Nachbarn über alle Paare ist Σ_v C(d_v, 2).
2. Mit den Obergrenzen folgt Σ_v C(d_v, 2) ≤ |E| + 2(4 851 − |E|) = 9 702 − |E|.
3. Wegen C(d, 2) + d/2 = d²/2 heißt das Σ_v d_v² ≤ 19 404.
4. Cauchy–Schwarz: (2|E|)² ≤ 99 · Σ d_v² ≤ 1 386², also |E| ≤ 693.
5. Gleichheit erzwingt d_v = 14 für alle v und Schärfe aller Ungleichungen, also 1 auf Kanten und 2 auf Nichtkanten. Die Umkehrung ist klar.

**Folgerungen.**
- Die zulässige Menge ist abwärts abgeschlossen; das Ziel lautet 693 − |E|.
- Die Rückführung ist automatisch: Jeder zulässige Zustand mit 693 Kanten ist ein Zielgraph, eine Reparatur entfällt.
- **Brückenmaß:** Das Packungsdefizit eines λ-Graphen ist die kleinste Zahl von Kantenlöschungen, nach der keine Nichtkante mehr drei oder mehr gemeinsame Nachbarn hat; berechenbar als Hitting-Set-ILP.

**Mechanismus.**
- Kante hinzufügen, wenn zulässig.
- Tauschzüge: eine Kante entfernen, eine oder zwei hinzufügen.
- Stinson-artige Blockadeauflösung.
- Tabu über die zuletzt entfernten Kanten.

**Gegenargumente.**
- Auch der Packungsraum kann tiefe Fallen haben; die Gleichheit verlangt zusätzlich Regularität.
- Das Defizit der Rekorde könnte groß sein, sodass der Brückenvergleich wenig trennt.

**Messbare Hypothese.** Die Packungssuche erreicht bei gleicher CPU ein kleineres Defizit als das kleinste Defizit aller λ-Archivgraphen.

**Kleinster aussagekräftiger Vergleich.** Von denselben 25 Klassen, auf ihre Packungsprojektion gebracht: Packungs-Tabu gegen λ-Katalogabstieg mit anschließender Projektion, je 1 CPU-h.

**Budget.** 48 CPU-h einschließlich der Defizitberechnung.

**Erfolg und Widerlegung.** Erfolg: Defizit unter dem Archivminimum oder ein Graph mit 693 Kanten; letzterer ist nach unabhängiger Prüfung ein Zielgraph. Widerlegt, wenn die Packungssuche über dem Archivminimum stagniert.

**Kategorie.** Neue Suchraumklasse; Mechanismus.

### M2 — Kalibrierung an bekannten Lösungen

**Mechanismus.**
- **Testfall:** srg(243,22,1,2) als Nebenklassengraph des ternären Golay-Codes, also mit exakt bekannter Lösung. Dazu die λ = 1-Graphen srg(15,6,1,3) und srg(27,10,1,5) aus GQ(2,2) und GQ(2,4).
- **Rückkehr:** Nach k zufälligen gültigen Sternzügen (k = 2, 4, 8, 16, 32) wird jeweils mit W, L1 und F abgestiegen, mit Katalog und optional mit Fenstern der Betriebsart B3. Gemessen wird die Rückkehrquote, also der Anteil der Abstiege, die W = 0 erreichen.
- **Zufällige Starts:** H1-artige λ-Starts werden abgestiegen; gemessen wird, wie nahe sie relativ kommen. Zum Vergleich: bei 99 liegt 2076/4158 ≈ 0,50.

**Gegenargumente.** Der 243er-Graph ist knotentransitiv, der 99er kann es nicht sein. Die Beckenstruktur kann sich unterscheiden; ein positives Ergebnis überträgt sich nicht automatisch.

**Messbare Hypothese** (das Verfahren ist lösungssuchend): Rückkehrquote von mindestens 50 % bei k ≤ 8 unter mindestens einem der drei Ziele.

**Kleinster aussagekräftiger Vergleich.** k-Staffel × 3 Ziele × 50 Wiederholungen am 243er-Graphen, dazu 200 zufällige Starts.

**Budget.** 48 CPU-h.

**Erfolg und Widerlegung.**
- **Rückkehr fast null schon bei k = 4:** Das Verfahren findet Lösungen selbst in ihrer unmittelbaren Nähe nicht. Dann ist W-Abstieg im λ-Raum kein Weg zu W = 0 (Ressourcenentscheidung, kein mathematisches Urteil).
- **Hohe Rückkehr, aber zufällige Starts bleiben bei relativem W ≈ 0,5:** Der Einzugsbereich ist klein; dann entscheiden Gründer und globale Züge (H1, M1).

**Kategorie.** Mechanismusnachweis über das Verfahren selbst.

### M3 — Übergänge über genau einen Defekt

**Mechanismus.** Analog zu Jacobson–Matthews ist genau ein uneigentliches Element erlaubt: eine Kante in 0 oder 2 Dreiecken oder ein Gradpaar 13/15. An 2076 und 2077 werden alle Folgen bis Tiefe 3 über solche Zustände exakt ausgezählt. Angenommen werden nur eigentliche λ-Zustände, also ohne Reparatur am Ende.

**Gegenargument.** Möglicherweise wird nur eine Zugfolge neu formuliert, die der Katalog schon abdeckt; die Aufzählung kann groß werden.

**Messbare Hypothese.** Es gibt einen eigentlichen Zustand mit W < 2076 höchstens drei Übergänge entfernt.

**Kleinster aussagekräftiger Vergleich.** Dieselbe Tiefe ohne Defekterlaubnis, also der reine Katalog.

**Budget.** 12 CPU-h.

**Erfolg und Widerlegung.** Treffer bedeutet einen Rekord nach Prüfung. Ohne Treffer gilt eine exakte Radiusaussage für den erweiterten Zugraum.

---

## 6 Zusammenführung und strittige Gesamtempfehlung

### 6.1 Widersprüche

- **Optimierer:** Er sieht den Hebel in der Technik, also Katalog, Betriebsart und Platzierung.
- **Hubschrauber:** Er sieht ihn in der Herkunft der Gründer und in Verfahren aus der Designtheorie.
- **Maverick:** Er bezweifelt, dass W-Abstieg im λ-Raum überhaupt zu Lösungen führt, und will den harten Bedingungssatz tauschen.

Die Daten stützen alle drei teilweise. Der Katalog findet in 0,1 s mehr als die ganze Kampagne; die Gewinne bleiben aber 2 bis 34 W groß und damit weit von W = 0. Hubschrauber und Maverick kommen unabhängig bei der Packungssicht an.

### 6.2 Am günstigsten zu entscheiden

- **O1:** Minuten bis wenige Stunden. Er entscheidet, ob Fenster überhaupt über den Katalog hinaus messen.
- **M2:** Stunden. Er entscheidet die Paradigmenfrage, denn nur ein Kontrollfall mit bekannter Lösung trennt „Verfahren untauglich“ von „Graph existiert nicht“.

### 6.3 Empfehlung (strittig): Kalibrierung K0, kein Hauptlauf

| Teil | Inhalt | Budgetobergrenze |
|---|---|---|
| K0-A | O1: Katalogzensus und Abstieg aller 25 Klassen sowie einer Archivstichprobe | 24 CPU-h |
| K0-B | O2: faktorieller Vergleich der Betriebsart auf denselben 48 Fenstern der Größe 60 | 102 CPU-h |
| K0-C | M2: Kalibrierung an srg(243,22,1,2) und den beiden GQ-Graphen | 48 CPU-h |
| Hilfszeit | Kontrollen, unabhängige Prüfung, Kanonisierung | 10 CPU-h |
| Summe | | ≈ 184 CPU-h |

Das ist eine Obergrenze. Nach GC-11 ist das keine Fertigstellungszeit; viele Teile enden früh. Nach GC-02 sind kleine, verbuchte Nachläufe lokale Ereignisse.

**Strittig** ist die Rangfolge: Ich stelle K0-C strategisch vor K0-A und K0-B, obwohl A billiger ist. Nach den Daten von 1.2.0 sind weitere Fenstervarianten ohne Kontrollfall nicht interpretierbar.

**Vorab festgelegte Folgen:**
1. **K0-C negativ** (Rückkehr fast null bei k = 4): W-orientierte λ-Memetik als Weg zu W = 0 ruhen lassen. Das ist eine Ressourcenentscheidung, kein mathematisches Urteil. Die Ryzen-Zeit geht an M1 und die exakten Linien.
2. **K0-C positiv und K0-B positiv** (mindestens 6 von 48 Fenstern, mindestens eine Verbesserung außerhalb des Katalogs): Hauptlauf nach §6.4.
3. **K0-C positiv, K0-B liefert nur Katalogzüge:** kein Fensterhauptlauf; stattdessen Piloten zu H1 und M1.
4. **K0-C gemischt** (hohe Rückkehr, zufällige Starts bleiben bei relativem W ≈ 0,5): zuerst H1 und M1, danach neue Bewertung.

Ein W < 2076 aus K0-A oder K0-B wird als Rekord gemeldet und unabhängig geprüft. An den Folgen oben ändert er nichts.

### 6.4 Bedingter memetischer Hauptlauf (nur bei Folge 2)

Vorab vollständig definiert, damit keine weitere Planungsschleife nötig ist.

- **Population:** 4 Inseln × 12 Individuen = 48.
- **Gründerfamilien:**
  - F1: katalogminimale Nachkommen der 25 Klassen, höchstens 12;
  - F2: die besten 12 H1-Fabrikstarts nach Abstieg;
  - F3: 12 symmetriegebrochene H2-Endpunkte, sonst weitere F2;
  - F4: 12 Archivendpunkte nach Maximin über die Merkmale aus `PLAN_V2`.
  - Jede Familie bekommt zunächst eine eigene Insel.
- **Vielfalt und Isomorphie:**
  - keine zwei isomorphen Individuen in einer Insel (pynauty-Zertifikat);
  - Aufnahme nur bei Merkmalsabstand über einem vorab fixierten Schwellwert (Median der Startbank);
  - gleicher Klassenhash ⇒ nur das bessere (W, L1) bleibt.
- **Selektion:** Turnier der Größe 3 auf (W, L1) innerhalb der Insel.
- **Mutation:** k zufällige gültige Sternzüge oder Apex-Züge, k ∈ {2, 4, 8} gleichverteilt.
- **Crossover:**
  - Elternunterschiedsmaske: Kanten, in denen die Eltern übereinstimmen, bleiben fix; die übrigen werden unter Grad 14 und λ = 1 neu belegt, Betriebsart B3.
  - Nur innerhalb einer Insel und nur bei gemeinsamer Beschriftung, also bei Profilverwandten.
- **Sprungmutation:** Mit Wahrscheinlichkeit 0,05 je Kind ein M3-Übergang über einen Defekt, sonst ein Neustart aus der H1-Fabrik.
- **Lokale Optimierung:** Katalogabstieg (Apex ∪ Pivot ∪ Stern ∪ 3-Linien), danach O3-Fenstersuche mit höchstens 20 Fenstern je Kind.
- **Ersatz:**
  - Das Kind ersetzt das schlechteste Inselindividuum, wenn es besser ist und seine Klasse fehlt.
  - Bei gleichem W zählt kleineres L1 zusammen mit dem Mindestabstand.
  - Migration des besten Individuums im Ring alle 2 CPU-h je Insel.
- **Budget:** 288 CPU-h (12 Worker × 24 h) als Obergrenze.
  - Kein Stopp wegen Stagnation; vorab festgelegte Auswertungen bei 25, 50 und 100 % des Budgets.
  - W = 0 wird unabhängig geprüft und beendet den Lauf.

---

## 7 Abgleich mit den Agentenberichten des Absenders

Gelesen nach Abschluss des unabhängigen Entwurfs und nach den Kugeltests.

**Übereinstimmung.** Alle drei Agenten, die SYNTHESE und dieses Review lehnen eine weitere Budgetverdopplung derselben Fenster ab. Alle unterscheiden Bewegung von Verbesserung. Alle betonen, dass die Gründer aus zwei Linien stammen.

**AGENT_A (Optimierer).**
- **Übereinstimmung in den Zahlen:** Seine Schrankenwerte stimmen mit meinen überein (509,31 bis 860,67, Median 699,63).
- **Schon beantwortet:** Seine Mobilitätsfrage ist für die Größen 24 und 40 hier bereits beantwortet (§2.3). Für die Größe 60 ist gezeigt, dass enthaltene strikte Verbesserungen existieren und in der bisherigen Betriebsart verfehlt werden.
- **Ergänzung:** Stellt man seine Entscheidungsfragen mit der Betriebsart von 1.2.0, ist wieder überwiegend UNKNOWN zu erwarten. Die LP muss aus sein, oder es braucht eine Kugel. Ich übernehme seine Entscheidungsform („Ziel ≤ Gründerziel − 1“) als Variante von B1 und B3.
- **Fensterauswahl nach Freiheit:** Sein Vorschlag deckt sich mit O3, dort aber über Linienbüschel statt über freie Variablen.

**AGENT_B (Hubschrauber).**
- **Stärke:** Die Elternunterschiedsmaske (D, D+, Kontrolle R) löst das Problem des eingefrorenen Randes.
- **Zwei Ergänzungen:**
  - Der Nachabstieg „unverändertes P“ verfehlt die billigsten Verbesserungen, die bei 8 von 24 Gründern Sternzüge sind. Der Stern gehört in den Abstieg.
  - Auch D-Masken brauchen die Betriebsart B3.
- **Einwand gegen meine O1:** Er berichtet, dass im Vierstundenvergleich P gegen PC (P mit Dreierzyklen) alle zwölf Paare gewann [Ü, `lambda_followup_results_20260923`]. Das stützt die Erwartung, dass O1 keinen Rekord bringt, nicht aber, dass die Gründer katalogminimal wären. Ob der dortige C3-Katalog genau die Sterndreierzyklen umfasste, habe ich nicht geprüft.
- **Einordnung:** Seine Rekombination ist in §6.4 als Crossover übernommen. Als eigenständiger Versuch käme sie nach K0-B.

**AGENT_C (Maverick).**
- **C1 (Neubelegung ganzer Dreiecksblöcke über den Rand):** Sternzüge sind die kleinsten Instanzen davon. Mein Zensus liefert genau den Katalogvergleich, den C selbst fordert, und zeigt: Bis Tiefe 2 im Stern bewegt sich an den Rekorden nichts.
- **C2 (Ausflüge mit λ-Schuld q = 2, 4, 8):** Das ist die stochastische Schwester von M3. Ich würde zuerst die exakte Variante q = 1 an den Rekorden auszählen, weil sie billiger ist und eine klare Radiusaussage liefert.
- **C3 (Projektor):** Die Formel E = (A + 4I − (2/11)J)/7 habe ich nachgerechnet: Diagonale 6/11, Werte 9/77 auf Kanten und −2/77 auf Nichtkanten, Spur 54. Das ist das bekannte primitive Idempotent E₃ (arXiv:2606.29183, §8.4). Wie C selbst sagt, liegt es nahe am Maß F.
- **Schnittmenge:** Der Test am (9,4,1,2)-Graphen deckt sich mit M2, M2 greift aber mit 243 Knoten weiter.

**Neu gegenüber den Agentenberichten:**
- Sternzensus und die verfehlte enthaltene Verbesserung;
- die Diagnose der Betriebsart mit den Kugeltests;
- die Zerlegung der Radius-16-Lösung in Katalogzüge;
- der Packungssatz (M1);
- die Kalibrierung am bekannten srg(243,22,1,2) (M2).

**Ändert der Abgleich die Empfehlung?** Nur in Details. K0 bleibt; K0-B enthält die Entscheidungsform aus A; die Rekombination aus B wird Crossover im bedingten Hauptlauf; C1 geht in O1 und O3 auf.

---

## 8 Prüfsatz

Flaches ZIP `reviewer_lambda_repair_120_20260929_pruefsatz.zip`. Die Umgebungsvariable `REPO` zeigt auf einen Checkout von `68001f9` (Zweig `memetik`), `RUN120` auf das entpackte `RESULTS_120.tar.gz`, also `…/ryzen_lambda_repair_120_20260928`. Python 3.12, `ortools==9.14.6206`. Alle Skripte im selben Verzeichnis ausführen, weil einige Hilfsteile per `exec` aus Nachbarskripten laden.

| Skript | Zweck | Ausgabe | Laufzeit (1 Sandbox-Kern) |
|---|---|---|---|
| `lines.py` | graph6-Decoder, Manifest, Linienstruktur je Fenster | `lines_stats.json`, `lines.log` | Sekunden |
| `alt.py 24 60`, `alt.py 40 120` | Existenz einer anderen zulässigen Füllung | `alt_24.json`, `alt_40.json`, `alt_24.log` | etwa 10 s bzw. 2 min |
| `wout.py` | adressierbarer W-Anteil; Struktur der Verbesserung 2139→2127 | `wout.log` | Sekunden |
| `star.py` | Sternzensus der 25 Klassen | `star_census.json`, `star_census.log` | etwa 3 s |
| `star_descent.py` | steilster Sternabstieg mit voller λ-Prüfung | `star_descent.json`, `star_descent_endpoints.json` (graph6, Rundlauf geprüft), `star_descent.log` | Sekunden |
| `star_d2.py` | Tiefe 2 an den Rekordklassen | `star_d2.log` | etwa 1 min |
| `contain.py` | verbessernde Sternzüge der Gründer und Fensterzugehörigkeit | `contain.log` | Sekunden |
| `check2077_09.py` | Zulässigkeit der verfehlten Verbesserung im Kampagnenmodell | `check2077_09.log` | etwa 30 s |
| `localbranch.py TASK R SEC MODE` | Kugeltests; MODE ∈ {ball, ballnolp, nolp, lns} | `lb_*.json`, `best_*.json` | 2 bis 4 min je Lauf |
| `decompose.py`, `seqcheck.py` | Zerlegung der Lösung 2140 in Sternzüge | `decompose.log`, `seqcheck.log` | Sekunden |

**Grenzen.**
- Alle CP-SAT-Statusmeldungen sind unzertifiziert.
- Die Kugeltests sind Einzelläufe mit Standardseed; die Zeiten gelten für die Sandbox und sind keine Ryzen-Prognose.
- Der Sternzensus beruht auf der hergeleiteten Zulässigkeitsbedingung und prüft angewandte Züge vollständig nach. Eine unabhängige Zweitimplementierung fehlt.
- Neue Sandbox-Graphen sind nicht kanonisiert. Der Graph `best_2077_09_s60_defect_ballnolp_r16.json` (W 2140) ist kein Rekord und nur Beleg für §2.5.

---

## Anhang A — Literatur

Gelesen wurden Abstracts, Inhaltsangaben oder Literaturverzeichnisse, keine Volltexte. Die Aussagen oben sind darauf beschränkt.

- P. G. Cesarz, A. J. Woldar: *On the automorphism group of a putative Conway 99-graph*, arXiv:2308.02978. Enthält die Aussagen von A. A. Makhnev, V. V. Minakova, Discrete Math. Appl. 14(2) (2004) 201–210.
- M. Behbahani, C. Lam: *Strongly regular graphs with non-trivial automorphisms*, Discrete Math. 311(2) (2011) 132–144. Aussage über die Primordnungen hier nach arXiv:2606.29183, §8.4 (Sekundärzitat); dort auch das Idempotent E₃.
- P. J. Cameron: *Partial quadrangles*, Quart. J. Math. Oxford 26 (1975) 61–73, doi:10.1093/qmath/26.1.61. Definition nach J. Bamberg, F. De Clerck, N. Durante, arXiv:0812.2871.
- E. R. Berlekamp, J. H. van Lint, J. J. Seidel: *A strongly regular graph derived from the perfect ternary Golay code*, in: A Survey of Combinatorial Theory (1973) 25–30.
- R. Reimbayev: *The lower bound for number of hexagons in strongly regular graphs with parameters λ=1 and μ=2*, arXiv:2409.10620.
- *Approaching the Conway-99 problem using SAT solvers*, arXiv:2604.23037.
- D. R. Stinson: *Hill-climbing algorithms for the construction of combinatorial designs*, in: Algorithms in Combinatorial Design Theory, North-Holland Math. Stud. 114 (1985) 321–334, doi:10.1016/S0304-0208(08)72988-8.
- J. H. Dinitz, D. R. Stinson: *A hill-climbing algorithm for the construction of one-factorizations and Room squares*, SIAM J. Alg. Disc. Meth. 8(3) (1987) 430–438.
- M. T. Jacobson, P. Matthews: *Generating uniformly distributed random Latin squares*, J. Combin. Des. 4(6) (1996) 405–437.
- M. Aryapoor, E. S. Mahmoodian: *On uniformly generating Latin squares*, arXiv:1005.0121.
- A. Mehrabian u. a.: *Finding increasingly large extremal graphs with AlphaZero and tabu search*, IJCAI 2024, 6985–6993, doi:10.24963/ijcai.2024/772; arXiv:2311.03583.
- Epoch AI, FrontierMath Open Problems: *Conway's 99-Graph Problem*, https://epoch.ai/frontiermath/open-problems/conway-99-graph.

**Regeln:** Angewendet wurden GC-02 (tolerierte, verbuchte Nachläufe), GC-08 (Reichweite von Aussagen an den geprüften Raum gebunden), GC-10 (Versuch, Aufgabe und Planerfüllung getrennt) und GC-11 (Budgetprojektion ist keine Prognose). Grundlage ist `docs/EXPERIMENT_RULES.md` Version 1.0 im Stand von `68001f9`.
