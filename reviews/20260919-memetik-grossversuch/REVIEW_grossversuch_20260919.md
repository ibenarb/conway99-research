# Review: Memetik-Bilanz und Vorbereitung des Großversuchs

**Gegenstand:** `docs/memetik/review_grossversuch_20260919/BERICHT.md` und `VORUNTERSUCHUNGEN.md`
**Reviewter Commit:** `958744f8b53ce66894a8b29e9bdfa033871574b0` — Spitze von `origin/memetik`, ein Commit nach dem Ergebnisstand. Es wurde *nicht* stillschweigend eine spätere Branchspitze verwendet.
**Fester Ergebnisstand aller Pflichtquellen:** `96db50629232709a79166200efa93adfd82fbbc3` (verifiziert als Vorfahr von `958744f`; der Diff dazwischen umfasst ausschließlich die drei Reviewdokumente, 166 Zeilen, keine Ergebnisänderung).
**Datum:** 19. September 2026
**Rahmen:** ausschließlich Memetik/Escape. Keine Fortsetzung von K66 / Involutionsausschluss / C2 / O3. Keine Office- oder Ryzen-Läufe gestartet, keine vorhandenen Checkpoints verändert. Alle Rechnungen liefen in einem getrennten Arbeitsverzeichnis gegen einen frischen, schreibgeschützten Checkout.

---

## 1. Kurzes Urteil

**Nach benannten Korrekturen startbereit.**

Der mathematische Kern ist deutlich solider, als der Bericht selbst behauptet. Ich habe die zentralen Aussagen unabhängig nachgerechnet und alle bestätigt, teils schärfer als formuliert. Die offenen Punkte sind nicht mathematischer, sondern versuchsplanerischer Natur:

1. Die Gründerdiversität ist derzeit nicht belegt — nicht die Zahl der Graphen fehlt, sondern die Zahl der Konstruktionsprinzipien.
2. Das Vergleichsdesign (vier Seeds, drei Wiederholungen) trägt die beabsichtigten Aussagen nicht; die Beweislast liegt falsch herum.
3. Eine der vier Generatorskizzen ist eine Umformulierung des Armvertrags statt eines Generators.
4. Die Sublevelzertifikate sind nicht selbsttragend — behoben, siehe Abschnitt 9.

---

## 2. Gelesene Quellen und ausgeführte Prüfungen, getrennt

### 2.1 Gelesen (alle am festen Stand)

- `docs/memetik/GRUENDERVERTRAG.md`
- `docs/memetik/UEBERGABE_ESCAPE_20260916.md`
- `results/memetik/escape_followup_20260916/REPORT.md`, `symmetry.json`, `endpoint_symmetry.json`, `witness_audit.json`
- `results/memetik/landscape_20260917/REPORT.md` und die komprimierten Sublevelzertifikate
- `results/memetik/minimax_20260919/REPORT.md`, `AUDIT.json`, `status.json`, `config.json`, `audit.py`, `verify_results.py` und beide Aufgaben-JSONs
- `experiments/memetik/minimax_0_3_0/` (`minimax.py`, `search.py`, `operators.py`, `core.py`, `PROTOCOL.md`)
- `results/memetik/office_escape_20260917_043002/REPORT.md`
- `data/memetik/ai_candidates/` (registry und akzeptierte Graphen)
- Die beiden zu begutachtenden Dokumente

### 2.2 Nicht erhalten

`Ergebnisse_Minimax_030_minimax_20260917_213047_385349.zip` (292 828 623 Bytes, SHA256 `eb0b94a06ee2740d0439354146e6785f054e484816670464595ade4214444fe7`) und die endgültigen SQLite-Dateien.

**Dadurch nicht möglich:** `audit.py` auszuführen. Konkret unbelegt bleiben: SQLite-`integrity_check`, die Zählungen 2 142 386 / 76 258 und 9 241 / 37, die Konsistenz aller Elternverweise, die 76 258 Vollständigkeitsflags und die Frontier-Zeile `(id 2140748, value 3024, peak 3028)`. Diese Zahlen stammen aus `AUDIT.json`, das von demselben Skript erzeugt wurde, das sie prüfen soll. Ebenfalls ungeprüft: Existenz des Originals und der Release-Hash `8bfc6d9f…4cf4`.

**Folge:** Die HoG-Barriere **≥192 ist die einzige Kernaussage des Projekts, die ich nicht verifizieren konnte.** Der Bericht kennzeichnet sie bereits korrekt als code- und checkpointgestützt.

### 2.3 Selbst ausgeführt

Eigener graph6-Decoder, eigene Vertrags- und Kennzahlenprüfung, bewusst nicht von `core.py` / `verify_results.py` abgeleitet. Isomorphie mit frisch installiertem pynauty 2.8.8.1.

| Prüfung | Ergebnis |
|---|---|
| B-Minimax-Zeuge: 6 Graphen, Ω-Rahmen inkl. PH=2J−(C+I)P, alle Kennzahlen, 5 Kantenänderungen rekonstruiert | **PASS** — W-Folge 2082→2094→2094→2086→2090→2080, Barriere 12, Endvektor (2080, 3360, 8980, 10, 34) |
| B-Sublevelzertifikat: 13 Zustände, 26 gerichtete / 13 ungerichtete innere Kanten | **PASS** — zusammenhängend, min innen 2082, max innen 2092, alle < 2094 |
| HoG-Sublevelzertifikat: 85 Zustände, 240 / 120 Kanten | **PASS** — zusammenhängend, min innen 2836, max innen 2924 |
| **Randmengen neu aufgezählt** (archivierter Operatorcode, alle Familien, alle Sublevelzustände) | B: 3425 Trades, 3256 Randgraphen, **min W = 2094**. HoG: 3817 Trades, 2750 Randgraphen, **min F = 2928**. Familienzensen zustandsweise exakt. Seedgrößen 3269 bzw. 2835 exakt reproduziert |
| Alle 13 Abstiegs- und Neutralzeugen aus `escape_followup` | **PASS** — Tabelle im REPORT stimmt zeilengenau |
| C08-Nachbarschaft neu aufgezählt | 66 Apex-, 0 Rotationstrades, 66 verschiedene Kinder, **33 W-neutral, 0 W-besser**, die 33 bilden **genau eine** Isomorphieklasse; \|Aut(C08)\| = 33, \|Aut(Endpunkt)\| = 1 |
| lambda_Linf2-Endpunkte gegen HoG57338 | descent_F / L1 / W **isomorph**; descent_Linf **nicht** |
| Paarweise Nichtisomorphie | B-Sublevel 13/13, HoG-Sublevel 85/85 Klassen |
| Automorphismen der acht Escape-Gründer | 1, 2, 1, 1, 1, 1, 66, 33 — exakt wie berichtet |
| **A_legacy-Komponente von Grund auf neu geschlossen** | 8 Zustände, 12 Übergänge, jeder Zustand genau 3 4×4-Nachbarn und 0 4×6/6×6 → Q3 bestätigt; A eindeutig bester Zustand in W, L1, F; **8 paarweise nichtisomorphe** Zustände |
| **Alle 14 akzeptierten KI-Kandidaten** | Armverträge **14/14 PASS**; Automorphismenordnungen **stimmen exakt** mit `symmetry.json`; 8 asymmetrisch / 6 nichttrivial bestätigt; **14 verschiedene Isomorphieklassen**, keine verdeckten Dubletten |

---

## 3. Eigenes Ergebnis: der Ω-Katalog ist vollständig charakterisiert

Der Bericht behandelt „Ω-Produkttrades 4×4/4×6/6×6" durchgehend als black box („gilt nur für den implementierten Katalog"). Das ist zu bescheiden.

Aus `operators.py` und `core.py` ergibt sich, und ich habe es nachgerechnet:

> Ein zulässiger Trade ist genau eine symmetrische Rang-2-Änderung
> **D = x yᵀ + y xᵀ**
> mit x, y ∈ ker(P) ∩ {0, ±1}⁸⁴, disjunkten Trägern der Größe 4 oder 6, und der Binaritätsbedingung an H + D (die der Code als Vorzeichenkonsistenz von y gegen die H-Spalten implementiert).

Die ±1-Kernvektoren von P entsprechen eineindeutig den Teilgraphen des Rahmengraphen K₁₄ minus perfektem Matching, in denen jeder Knoten gleich viele +- wie −-Kanten trägt.

- **Träger 4:** genau die 4-Kreise.
- **Träger 6:** genau die 6-Kreise und die Bowties (zwei Dreiecke mit einem gemeinsamen Knoten). Zwei disjunkte Dreiecke sind ausgeschlossen, weil ein ungerader Kreis keine alternierende Vorzeichenbelegung zulässt.

**Verifiziert:** Brute force über alle Träger-4-Teilmengen liefert 2121 Vektoren modulo Vorzeichen — exakt die Zahl, die `signed_vectors(4)` erzeugt. Für Träger 6: 108 080 6-Kreise + 17 220 Bowties = **125 300** = exakt die Zahl aus `signed_vectors(6)`.

**Folgen:**

1. Der Operatorkatalog ist mathematisch exakt beschreibbar und für Träger 4 und 6 **beweisbar vollständig**, nicht nur „implementiert". Alle Negativaussagen werden dadurch wesentlich stärker.
2. Die nächste Katalogerweiterung ist präzise benannt: Träger 8/10, überlappende Träger von x und y, Rang > 2.
3. **D ist symmetrisch in x und y, und die Binaritätsbedingung ebenfalls.** Familie a×b ist damit *dieselbe Zugmenge* wie b×a. Die an A getesteten Familien 4×8/4×10/4×12 decken den Fall „Linksträger 8" bereits mit ab.

---

## 4. Tabelle: Aussage – Evidenz – Einwand – notwendige Korrektur

| Aussage | Evidenz | Einwand | Notwendige Korrektur |
|---|---|---|---|
| **A:** geschlossene Achtzustandskomponente, A bester Zustand | Vollständig neu erzeugt und bestätigt | Keiner. Der Bericht *unterschätzt*: „acht beschriftete Zustände sind keine behaupteten acht Isomorphieklassen" — es sind tatsächlich acht Klassen | Formulierung aktualisieren; der Vorbehalt ist erledigt |
| **C08:** kürzester Verbesserungsweg Länge zwei, W-Barriere 0 | Neu aufgezählt: 66 direkte Nachbarn, 0 W-bessere → Länge 1 ausgeschlossen | „Kürzeste Länge" ist hier **zu Recht** behauptet, anders als bei B. Der Bericht macht diesen Unterschied nicht sichtbar | Explizit als *bewiesene* Minimalität kennzeichnen |
| **C08:** 33 neutrale Nachbarn untereinander isomorph | Unabhängig bestätigt (1 Klasse) | Keiner | — |
| **C02:** W = 2031 mit (2428, 3298); F = 3292 bei anderen Endpunkten | Alle 13 Zeugen nachgerechnet | Keiner | — |
| **B:** Barriere genau 12 ab W = 2082 | Zeuge und Sublevelrand reproduziert; Dijkstra-Argument im Code korrekt | Keiner. Das ist die stärkste Aussage des Projekts: **exakte** minimale Fluchtbarriere, nicht nur eine Schranke | Im Bericht als „minimal" führen, nicht als „mindestens" |
| **B:** fünf Schritte nicht als kürzeste Länge bewiesen | Korrekt | Zu vage. Aus der Office-BFS (Tiefen 0–1 vollständig expandiert) folgt Länge ≥ 3 | Präzisieren: **minimale Länge ∈ {3, 4, 5}**. Nur zwei Fälle offen |
| **B:** 2080 nicht als lokales Minimum geprüft | Korrekt und ehrlich | — | P0-Punkt in VORUNTERSUCHUNGEN ist richtig gesetzt |
| **HoG:** Barriere ≥ 92 aus geschlossenem Subniveau | **Reproduziert**, Randminimum 2928 aus 2750 Randgraphen | Das Sublevel-„Zertifikat" enthält die Randgraphen **nicht** — nur die Zahl `minimum_boundary`. Es ist nicht selbsttragend | Randgraphen mit archivieren → **erledigt, Abschnitt 9** |
| **HoG:** Barriere ≥ 192 aus Minimax-Frontier 3028 | **Nicht prüfbar** ohne die SQLite-Dateien | Der Algorithmus ist korrekt (echte Bottleneck-Dijkstra, `last_settled_peak`-Monotonie asserted, Relaxation kann bei monotoner Entnahme nie greifen — konsistent mit `relaxations: 0`). Die Aussage hängt an 76 258 Vollständigkeitsflags, die nur `audit.py` gesehen hat | Als code- und checkpointgestützt führen, wie bereits geschehen |
| **HoG:** BFS ohne Verbesserung bis Länge vier | Bestätigt: Tiefen 0–3 expandiert, 244 793 Tiefe-4-Zustände bewertet | Keiner | — |
| Acht von 14 KI-Kandidaten asymmetrisch | Alle 14 unabhängig nachgerechnet, Ordnungen stimmen exakt | Keiner | — |
| Laufzeitzähler 122 402 vs. 132 601 s | Ungeklärt, im Bericht offengelegt | Harmlos, aber ein Hinweis auf ungeprüfte Zeitbuchhaltung, die später Budgetvergleiche verzerren kann | Vor dem Großversuch klären, weil A0/A1/A2 über **gleiches CPU-Budget** verglichen werden sollen |

### 4.1 Wo ich Überinterpretation *nicht* gefunden habe

Der Auftrag fordert ausdrücklich, Überinterpretationen der Minimax-Frontier und der Begriffe Plateau/Minimum zu suchen. Ich habe sie gesucht und **keine** gefunden:

- `snapshot()` nennt das Feld korrekt `necessary_barrier_at_least`.
- Das Protokoll sagt explizit, dass `frontier_peak` ohne Fund nur eine untere Schranke ist und „keine Erfolgsprognose".
- Der Zeuge trägt `shortest_path_length_claimed: False`.
- VORUNTERSUCHUNGEN §1 trennt „lokales Minimum" sauber von striktem Minimum und budgetbeendetem Endpunkt.

Die Begriffsdisziplin dieses Projekts ist überdurchschnittlich. Der eigentliche Mangel liegt anderswo: **die Dokumente untertreiben mehrfach** (A-Isomorphieklassen, C08-Minimalität, B-Barriere als „mindestens" statt „genau"). Untertreibung kostet bei der Priorisierung genauso viel wie Übertreibung.

---

## 5. Die vier Generatorskizzen

### Skizze 3 (λ über lineare 3-uniforme Hypergraphen): korrekt, aber kein Generator

Die Rechnung stimmt: 231 Tripel × 3 = 693 Inzidenzen, 693/99 = 7 pro Punkt; Linearität macht den Schatten einfach mit 693 Kanten, also 14-regulär. Der Ausschluss von Berge-Dreiecken ist genau die richtige Zusatzbedingung: jede Kante liegt in genau einem Tripel, also in mindestens einem Dreieck; ein zweites Dreieck über derselben Kante müsste seine beiden anderen Kanten aus verschiedenen Tripeln nehmen, wäre also ein Berge-Dreieck. **Linear + keine Berge-Dreiecke ⟺ λ = 1.**

Genau deshalb ist es aber **keine neue Konstruktion, sondern eine Äquivalenzumformung des λ-Armvertrags**. Jeder 14-reguläre Graph auf 99 Knoten mit λ = 1 *ist* per Definition der Schatten eines solchen Hypergraphen — die Dreiecke zerlegen die Kantenmenge, die Nachbarschaft jedes Knotens ist ein perfektes Matching aus 7 Kanten. Als Neuheitsbehauptung wäre das nicht haltbar.

*Ich habe hierzu keine Primärquellenrecherche durchgeführt und behaupte entsprechend keine Literaturzuordnung. Die Aussage stützt sich allein auf die von mir nachgerechnete Definitionsäquivalenz.*

Der praktische Wert ist real, muss aber anders begründet werden: als **Erzeugungsrepräsentation**. Tripelpackung ist ein gutmütigerer Suchraum als Kantenmutation, weil λ = 1 zur lokalen Nebenbedingung wird statt zur globalen Prüfung. Effizienzargument, nicht Strukturargument. Messergebnis dazu in Abschnitt 8.

### Skizze 2 (größere Kerneländerungen von H): richtig, teils redundant, dupliziert vorhandene Arbeit

**Erstens ist die aufgeführte Gradbedingung impliziert und damit überflüssig.** Jede Spalte von P hat genau zwei Einsen, also 1ᵀP = 2·1ᵀ. Aus PD = 0 folgt 2·1ᵀD = 0, also verschwinden alle Spaltensummen von D, wegen Symmetrie auch die Zeilensummen, also bleibt der H-Grad bei 12. Die echte Restriktion ist allein die Binarität: D_uv ∈ {−1, 0, +1} mit −1 nur dort, wo H_uv = 1.

**Zweitens hat die `escape_followup`-Arbeit diese Skizze bereits umgesetzt** — CP-SAT mit Kantendistanzschranke, sparse MILP, CP-SAT in induzierten H-Fenstern, bis zum vollen Fenster mit 1008 Änderungen. Ergebnis: UNKNOWN bzw. fensterlokales INFEASIBLE; der Warmstart gab nur C02 unverändert zurück. VORUNTERSUCHUNGEN führt die Skizze als Prüfkandidat auf, ohne diesen Befund zu erwähnen. **Das ist die einzige Stelle, an der die Vorlage den eigenen Ergebnisstand ignoriert.**

Was fehlt, ist nicht die Formulierung, sondern eine *traktable* Restriktion. Die Charakterisierung aus Abschnitt 3 liefert sie: Rang 2 mit Trägern 8/10, überlappende Träger, oder Rang 3.

### Skizzen 1 und 4

Unbedenklich, aber unterspezifiziert; Arbeitsrichtungen, keine prüfbaren Vorschläge. Skizze 4 („feste Symmetrie höchstens als Erzeugungshilfe") ist durch die eigenen Daten gut gestützt: die Hindernisse bei A und HoG treten bei \|Aut\| = 1 auf, und C08 mit \|Aut\| = 33 erreicht einen asymmetrischen besseren Nachfahren — beides bestätigt.

---

## 6. Gründerdiversität, Versuchsdesign, Population

### 6.1 Reicht die Gründerdiversität? Nein

Die Trennung in VORUNTERSUCHUNGEN §1 (Konstruktionsfamilie / Graphstruktur / Arbeitszustand / empirisches Einzugsgebiet) ist begrifflich sauber. Der Bestand erfüllt sie nicht:

- **Konstruktionsfamilien:** Der GRUENDERVERTRAG verlangt mindestens vier nachvollziehbar verschiedene Prinzipien. Faktisch stammen 10 der 14 Kandidaten von einem Anbieter, und der Vertrag sagt selbst: „viele Seeds einer Methode sind keine vielen Methoden." Die Zahl der belegten *Prinzipien* steht nirgends. Das ist die Lücke, die vor dem Start zu schließen ist — nicht die Zahl der Graphen. Die Strukturseite ist sauber (14 verschiedene Klassen, alle Verträge erfüllt); die Herkunftsseite ist eine Dokumentenfrage.
- **Einzugsgebiete:** Drei von vier lambda_Linf2-Abstiegen enden HoG-isomorph. Bei nur zwei λ-Gründern mit nichttrivialer Suchhistorie ist das ein hoher Redundanzanteil.
- **Ω-Arbeitsrahmen:** Der Hinweis in §3, ungefärbte Isomorphie dürfe Ω-Arbeitszustände nicht automatisch entfernen, ist **korrekt und wichtig**. Abschnitt 3 macht den Grund konkret: die Operatoren leben auf ker(P) im *festen* Rahmen. Ein ungefärbter Isomorphismus, der den Rahmen nicht erhält, transportiert die Nachbarschaftsstruktur nicht. Eine Quotientensuche im Ω-Arm wäre derzeit unsicher.

**Welche Messung ihren Aufwand wert ist:** exakte kanonische Zertifikate für alle Gründer und alle geprüften Endpunkte. Ich habe das für 8 Gründer, 14 Kandidaten, 98 Sublevelzustände, 13 Endpunkte und 33 C08-Nachbarn in wenigen Minuten Gesamtrechenzeit gemacht. Billig, gehört nach P0. **Nicht ihren Aufwand wert:** Residuenhistogramme und Defektgradprofile als Diversitätsmaß, solange die exakte Isomorphie ohnehin durchläuft — sie sind schwächer und verleiten dazu, „verschiedenes Profil" als „verschiedene Struktur" zu lesen. Als Diagnose behalten, nicht als Auswahlkriterium.

### 6.2 Vier Seeds und drei Wiederholungen reichen nicht

VORUNTERSUCHUNGEN sagt selbst, vier Seeds seien „eine Vorauswahl, keine belastbare Wirksamkeitsstudie" — dann darf der A0/A1/A2-Vergleich aus §5 nicht mit drei Wiederholungen über die Skalierung entscheiden.

- **Was drei Wiederholungen können:** eine deutlich schlechtere Variante ausschließen. Als Screening von drei auf zwei Varianten genügt das.
- **Was sie nicht können:** einen Vorteil von A1 oder A2 gegenüber A0 belegen. Bei gepaarten Gründerbeständen und drei Paaren ist die kleinstmögliche einseitige Irrtumswahrscheinlichkeit eines Vorzeichentests 1/8.
- **Korrektur:** Den Entscheidungssatz in §6 umdrehen. Die Referenz A0 startet, *außer* die Steuerung zeigt einen Vorteil, der bei gepaartem Design über mindestens acht Gründerpaaren nicht mehr durch Startqualität erklärbar ist. Gleicher Aufwand, richtige Beweislast.
- **Scheinreplikation:** Der Hinweis, Generationen nicht als unabhängige Stichproben zu behandeln, gehört in den Auswertecode, nicht nur in den Text.
- **Überanpassung:** Strategie B nennt das Risiko selbst — die Escape-Parameter stammen aus A/B/C08/HoG. Die Prüfung an nicht zur Parametrierung verwendeten Gründern muss **verbindlich** sein, nicht empfohlen.

### 6.3 32 → 64 Plätze, Familienquoten, Crossover

Die Planungsgröße ist plausibel, die Begründung nicht. 192 aktive Plätze bei vermutlich unter fünf belegten Konstruktionsprinzipien heißt, dass die Population überwiegend Nachfahren weniger Gründer enthält.

**Bessere Alternative bei identischem Budget:** weniger Breite, mehr Wiederholungen. 16 Plätze je Arm/Ziel bei doppelter Seedzahl liefert für die eigentliche Frage („ändert die Steuerung etwas?") mehr Information als 32 Plätze mit einem Lauf. Die Vorlage sagt selbst „reichen strukturell verschiedene gültige Gründer nicht, kleiner beginnen" — das sollte der Default sein, nicht der Rückfall.

**Crossover: nein, nicht als Pflichtbestandteil.** Die Begründung in Strategie C ist bereits richtig; 20 % ist erkennbar eine gesetzte Zahl. Rekombination gehört in die P1-Probe mit der genannten Erfolgsdefinition (eigenständiger Strukturbeitrag, nicht bloße Elternrückgabe) und kommt erst in den Großversuch, wenn diese Probe positiv ist.

### 6.4 Neutraler Besuchsspeicher und Escape-Episoden: gerechtfertigt

Die Daten sagen konkret warum: C08 zeigt eine Barriere 0 mit neutralem Ausgang, B eine echte Barriere 12, A eine abgeschlossene Komponente. Drei Hindernistypen; ein strikter Abstieg behandelt nur den trivialen Fall.

**Konkrete Stopp-/Umschaltregel:**

1. Strikter Abstieg bis zum ersten Endpunkt ohne strikt besseren Nachbarn.
2. Neutrale Exploration mit Besuchsspeicher bis zu einer festen Zahl neutraler Kanten (C08 legt einige Dutzend nahe, da dort schon der erste neutrale Schritt genügte).
3. Erst bei Erschöpfung ohne Ausgang eine Minimax-Episode mit **zielspezifischer** Höhenschranke, kalibriert aus beobachteten Trade-Kosten desselben Arms — Größenordnung 12 für Ω/W, ≥ 92 für λ/F.

Diese beiden Zahlen dürfen ausdrücklich **nicht** gemeinsam skaliert werden; die Vorlage sagt das bereits und hat recht. Für Linf durchgehend lexikographisch über (Linf, Nmax, L1), nie skalar gewichtet.

**Zielkonflikte:** Der wichtigste unterbelichtete Befund ist, dass W-Fortschritt L1 und F verschlechtert — bei C08 in beiden Größen, bei C02 mit unvereinbaren Endpunkten. Da W Diagnose bleibt und L1/F/Linf selektieren, gilt: ein neutraler Schritt bezüglich des Selektionsziels ist nicht neutral bezüglich der Diagnose und umgekehrt. **Der Besuchsspeicher muss pro Ziel geführt werden, nicht global.**

---

## 7. Rangliste der Voruntersuchungen

Abweichend von der Vorlage.

### Muss vor dem Start (P0)

| # | Untersuchung | Aufwand (Schätzung) | Entscheidungswert | Abbruchkriterium |
|---|---|---|---|---|
| 1 | Gründerregister mit exakten kanonischen Zertifikaten **und belegter Zählung der Konstruktionsprinzipien** | Rechenzeit: Minuten. Aufwand liegt in der Herkunftsrecherche | Hoch — bestimmt die Populationsgröße | Unter vier belegten Prinzipien → Versuch startet kleiner, nicht später |
| 2 | Kontrollvergleich A0/A1/A2 **mit umgekehrter Beweislast** | Wie in §5 geplant, plus mehr Wiederholungen statt mehr Plätze | Höchster im ganzen Paket | Kein Vorteil nach gepaartem Kriterium → A0 startet |
| 3 | B ab W = 2080 fertig untersuchen | Gering, Zustand liegt geprüft vor | Mittel — klärt, ob die teuerste Escape-Linie an einem lokalen Minimum endet | Katalogzensus abgeschlossen, unabhängig vom Ergebnis |
| 4 | Randgraphen der Sublevelzertifikate archivieren | Rund 4 Minuten CPU | Mittel, Verhältnis unschlagbar | **Erledigt, siehe Abschnitt 9** |

### Herabgestuft

- **Kleine randomisierte Abstiegsserie** (in der Vorlage P0): auf P1. Sie misst Streuung, aber die Entscheidung trifft Punkt 2. Vier Seeds ändern keine Startentscheidung.
- **C08-Plateau:** bleibt P1, richtig eingeordnet.
- **HoG-Vertiefung, vollständige HoG-Rezertifizierung, komplette C08-Komponente, lokale A-Flucht:** bleiben P2 und ausdrücklich **keine** Startbedingung. Die ≥192-Schranke ist genau der Grund: sie ist so groß, dass HoG als Fluchtziel im aktuellen Katalog unattraktiv ist, während HoG als hochwertiger Gründer wertvoll bleibt. Beides gleichzeitig zu halten ist richtig.
- **Minimale Weglänge für B** (3, 4 oder 5): billig, aber ohne Entscheidungswert. Nicht aufnehmen.

### Zur 10–15-%-Regel

Akzeptabel als Planungsgröße, aber derzeit an nichts gebunden. Sinnvoller wäre die Bindung an Punkt 2: die Vorbereitung endet, wenn der Kontrollvergleich entschieden ist, unabhängig vom Prozentsatz.

---

## 8. Eigene Vorschläge — vorgeschlagen *und* ausgeführt

### 8.1 Vorschlag 1: Rangerweiterung des Ω-Katalogs — **negativ entschieden**

**Mechanismus (ursprünglich).** Minimale echte Erweiterung des Katalogs aus Abschnitt 3: Träger 8 auf beiden Seiten, überlappende Träger von x und y, Rang 3.

**Selbstkorrektur.** Beim Aufsetzen zeigte sich, dass der Vorschlag zur Hälfte redundant war: weil D symmetrisch in x und y ist, ist „Linksträger 8" durch die bereits getesteten 4×8/4×10/4×12 mitabgedeckt.

**Ersatzversuch, billiger und beweisstärker.** Die bindende Größe ist, wie viele Labels überhaupt mit einem Kernvektor kompatibel sind. Ist dieses Maximum m, sind **alle** Familien \|x\|×r mit r > m an diesem Zustand leer — unendlich viele Familien auf einen Schlag.

**A_legacy**, Träger 4, alle 2121 Kernvektoren, Verteilung der kompatiblen Labels:

```
0:39   1:196   2:422   3:536   4:467   5:283   6:128   7:37   8:10   9:3
```

Maximum **9**. Zulässige Rechtsvektoren insgesamt: 4×4 → **6**, 4×6 → **0**, 4×8 → **0**. Die 6 ordnen sich paarweise zu 3 Zügen — exakt der Zensuswert `4x4: 3`, was die Symmetrieeinsicht unabhängig bestätigt.
Träger 6: Maximum kompatibler Labels **5**, also 6×6 und alles darüber leer — ebenfalls exakt der Zensus.

> **Ergebnis:** Der gesamte Ω-Produktkatalog liefert an A_legacy über *alle* Trägerpaare, bei denen eine Seite 4 oder 6 hat, genau die drei bekannten 4×4-Trades. Aufgezählt, nicht beobachtet. Offen bleibt nur der Bereich beide Träger ≥ 8.

**Vergleich mit B_end_F**, gleiche Rechnung: Maximum **18** kompatible Labels; Rechtsvektoren 4×4 → 180, 4×6 → 33, 4×8 → 52, 4×10 → 8, 4×12 → 13.

Das erklärt, *warum* A feststeckt: nicht wegen Symmetrie (\|Aut(A)\| = 1) und nicht durch Zufall der Suche, sondern weil das Vorzeichenmuster der H-Matrix von A fast keine kompatiblen Labels zulässt. Die Landschaft um B ist um zwei Größenordnungen reicher. **Der Vorlagenvorschlag, A ins Archiv zu stellen, ist damit begründet statt vermutet. Vorschlag 1 ist nicht weiterzuverfolgen.**

### 8.2 Vorschlag 2: Gründererzeugung durch Tripelpackung — **Stufe 1 ausgeführt**

**Mechanismus.** Skizze 3 nicht als Struktur-, sondern als Erzeugungsvorschlag ernst nehmen: zufällige gierige Packung von 231 Tripeln auf 99 Punkten unter Linearität, mit lokaler Reparatur, anschließend Prüfung auf Berge-Dreiecke.

**Zulässigkeitsbedingung (selbst hergeleitet).** Ein neues Tripel {a, b, c} ist genau dann erlaubt, wenn die drei Paare Nichtkanten sind **und** N(a), N(b), N(c) paarweise disjunkt sind. Denn ein x ∈ N(a) ∩ N(b) gäbe der neuen Kante ab einen zweiten gemeinsamen Nachbarn neben c und zugleich der alten Kante ax den neuen gemeinsamen Nachbarn b.

**Test validiert:** HoG57338 und Codex_C08 zerfallen in genau 231 Dreiecke und werden von der Prüfung akzeptiert. Die Zielobjekte existieren und sind erreichbar; ein Fehlschlag wäre ein Algorithmus-, kein Existenzproblem.

**Ergebnis** (zusammen rund 20 Minuten CPU):

| Verfahren | Versuche | Erfolge | bestes Ergebnis |
|---|---|---|---|
| Greedy, meist eingeschränkter Punkt zuerst | 1000 | 0 | 227/231 |
| + Rücknahme-Reparatur (bis 5000 Sackgassen) | 1200 | 0 | 227/231 |
| Stinson-artiges Hill-Climbing mit Zwangseinfügung | 8 × 30 s | 0 | 127/231 |
| Hybrid: Greedy + minimaler Konfliktabbau + Perturbation | 20 | 0 | **230/231** |

Das Hill-Climbing, bei Steiner-Tripelsystemen Standard und dort praktisch immer erfolgreich, versagt hier deutlich: die Zusatzbedingung „Nachbarschaften paarweise disjunkt" macht jede Zwangseinfügung zu teuer, weil sie bis zu einem Dutzend Tripel mitreißt. Der Hybrid kommt reproduzierbar auf 230 und bleibt dort. Bei 230 Tripeln sind genau drei Punktplätze offen; das Schlusstripel muss zwischen exakt diesen drei Punkten liegen und zugleich die Disjunktheitsbedingung erfüllen.

**Bewertung gegen mein eigenes Abbruchkriterium.** Ich hatte „< 1 % Rate → Skizze erledigt" gesetzt. Formal erfüllt — inhaltlich wäre der Schluss falsch. Korrigierte Fassung: Die Skizze ist **kein einsatzfähiger Generator** und braucht ein eigenes Endspielverfahren (gezielter Tausch über die drei defizienten Punkte statt zufälliger Rücknahme). Ob dieser Aufwand lohnt, ist eine Entscheidung — aber er ist jetzt beziffert statt geschätzt, und das war der Zweck von Stufe 1.

**Stufe 2** (acht Ergebnisse, kanonische Zertifikate, je ein deterministischer F-Abstieg; Entscheidung: mindestens die Hälfte der Endpunkte nicht isomorph zu HoG57338 oder einem der zwölf bekannten Endpunkte) bleibt bis dahin ausgesetzt.

---

## 9. Ausgelieferte Artefakte: die fehlenden Randzertifikate

Mein Haupteinwand an den Sublevelzertifikaten war, dass sie nur die Zahl `minimum_boundary` enthalten und damit nicht selbsttragend sind. Die Randmengen sind jetzt materialisiert: jeder Randgraph mit graph6, vollständigem Kennzahlenvektor, erreichendem Innenzustand und Operatorfamilie.

| Datei | innen | Rand | Minimum | Barriere | unabhängig nachgerechnet |
|---|---|---|---|---|---|
| `B_escape_W2082__bfs_W_boundary.json.gz` | 13 | 3256 | W = 2094 | ≥ 12 | 42 Graphen |
| `HoG57338__bfs_F_boundary.json.gz` | 85 | 2750 | F = 2928 | ≥ 92 | 53 Graphen |

Die Familienzensen stimmen zustandsweise exakt mit den Originalzertifikaten; die Seedgrößen 3269 bzw. 2835 aus dem Minimax-Protokoll werden exakt reproduziert. Nachgerechnet wurden alle Minimalstellen plus eine deterministische Stichprobe.

SHA256 der unkomprimierten Inhalte:

```
B_escape_W2082__bfs_W_boundary   7fb350904331b4faddab3491e57dcee4e031378cc4553a5ff171ecc0dcf799ef
HoG57338__bfs_F_boundary         3e8a8ac2ff73d6f56f2606d7c4f9e7a4cd2c77a503c4fc8fa787f8e942ed83d6
```

Ablageort: `results/memetik/landscape_20260917/`.

---

## 10. Offene Unsicherheiten

1. **HoG-Minimax-Zahlen.** Ohne die SQLite-Dateien ist ≥ 192 nicht nachvollzogen; die 76 258 Vollständigkeitsflags sind der Angelpunkt der Aussage.
2. **Konstruktionsprinzipien der 14 Kandidaten.** Struktur und Automorphismen sind verifiziert, die Herkunftsfrage ist eine Dokumentenfrage, die am Ergebnisstand nicht abschließend zu klären war.
3. **Keine Literaturrecherche durchgeführt.** Die Aussage zu Skizze 3 stützt sich ausschließlich auf die selbst nachgerechnete Definitionsäquivalenz, nicht auf Primärquellen.
4. **Reproduktionstiefe der Randmengen.** Die Neuaufzählung beruht auf dem archivierten Operatorcode. Sie zeigt, dass die Zertifikatszahlen aus diesem Code folgen — sie ist **keine** von der Operatorsemantik unabhängige Bestätigung. Die einzige wirklich implementierungsunabhängige Aussage ist die Vollständigkeitscharakterisierung der Träger-4- und Träger-6-Familien aus Abschnitt 3; die gilt gegen jede korrekte Implementierung.
5. **Bereich beide Träger ≥ 8** im Ω-Katalog an A_legacy bleibt unaufgezählt.
