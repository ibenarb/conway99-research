# Conway99 – Review λ-Arm (Memetik/Ryzen)

Stand 21.09.2026 · Reviewer-Bericht zum Fortsetzungsauftrag `FORTSETZUNG_LAMBDA_Codex_Reviewer_20260921.md`
Überarbeitete Fassung nach Nachreichung von `comparison_verified.tar.gz`.

> **Kurzfassung.** Der λ-Stillstand ist in erster Linie ein **Lücke im Zugkatalog**. Sample-Größe, Rechengeschwindigkeit und Selektion erklären ihn nicht.
>
> - Unter Apex (∪ Rotation) ist hog57338 ein exaktes striktes lokales Minimum für (W,L1), L1 und F. Innerhalb von 4 Apex-Zügen gibt es keinen besseren Zustand.
> - Der Katalog enthält aber nicht den einfachsten λ-erhaltenden Zug: den **Pivot**. Er tauscht Punkte zwischen zwei Linien durch einen **gemeinsamen** Punkt und ändert nur 4 Kanten.
> - Der einzige W-Erfolg des 144-h-Laufs (A1, W=2180) ist **genau ein solcher Pivot**. A1 hat ihn netto über ≥ 5 Apex-Züge realisiert.
> - Mit Apex ∪ Pivot liefert schon exakter steilster Abstieg aus hog57338 **(W,L1)=(2155,2416)** und **L1=2392**. Ein kurzer Tabu-Test (240 CPU-s, ein Seed) erreicht **(2153,2430)** und stagniert dann.
> - Das sind neue Bestwerte für W und L1. F bleibt auch mit Pivot bei 2836 exakt minimal.
>
> Empfehlung: Pivot in den Katalog aufnehmen, exakte Nachbarschaften statt Stichproben verwenden und dann gezielt Barrieren-Suche (Tabu) gegen größere Trades testen. Keine Hauptkampagne vor dem unten definierten begrenzten Experiment.

---

## 0. Grundlage und Prüfumfang

### Selbst geprüft

| Objekt | Ergebnis |
|---|---|
| `move_accel_verified.tar.gz` | SHA256 `1de55615…71ed` korrekt; 152 Einträge |
| `comparison_verified.tar.gz` | SHA256 `ada91cfa…4024` korrekt; alle **885** Inhaltsprüfsummen des Export-Manifests korrekt |
| Quellstand | Alle 22 Dateien des Quellfingerprints sind byteidentisch mit Commit `6cf206b7a7942672ef806c70d9e590bf27a1973c` |
| λ-Graphen | 16 Gründer, 4 Linf-Endpunkte (4-h-Lauf) und 6 neue Endpunkte (144-h-Lauf) mit eigenem Decoder/Prüfer geprüft. Alle λ-gültig, alle gespeicherten Scores stimmen. |
| 72 λ-Jobs des 144-h-Laufs | Endpunkte je Job geprüft. Die Siegbilanz A1/A0 aus der Zusammenfassung ist anhand der Endpunkte bestätigt: W 1/8/0, L1 0/9/0, F 0/9/0, Linf 0/1/8. |
| Neue Graphen dieses Reviews | Mit eigenem Prüfer **und** mit `common.checked(...,'lambda')` des Projekts (Validator plus unabhängiger Verifier) bestätigt |

### Übernommen, nicht selbst nachgerechnet

- CPU-Abrechnung und Receipts des 144-h-Laufs (143,92 h)
- Kalibrierung (`calibration_result.json`: 18 Worker am besten, Durchsatz 0,96 Episoden je Wall-Sekunde)
- Ω-Arm-Ergebnisse
- Census- und Transfer-Tasks

### Umgebung

- Sandbox mit 1 CPU, Python mit numpy 2.4.4, ohne pynauty. BFS-Zählungen beziehen sich auf **beschriftete** Zustände, nicht auf Isomorphieklassen. Aussagen der Form „kein besserer Zustand“ sind davon unabhängig.
- Ich habe nicht auf dem Ryzen oder dem Office-Rechner gerechnet.

---

## A. Diagnose

### A.1 Mathematischer Rahmen (hergeleitet; numerisch an den Daten bestätigt)

**(M1) λ-Arm als Hypergraph.** G liegt genau dann im λ-Arm, wenn G die 2-Sektion eines linearen, 3-uniformen, 7-regulären Hypergraphen H mit 231 Linien ohne Berge-Dreiecke ist.

- Richtung „⇒“: Wenn jede Kante in genau einem Dreieck liegt, zerlegen die Dreiecke die Kantenmenge. Daraus folgen Linearität und 7 Linien je Punkt. Jedes Dreieck von G ist eine Linie, also gibt es keine Berge-Dreiecke.
- Richtung „⇐“: direkt.
- Ein Hypergraph-Trade ist also **nicht automatisch** λ-erhaltend. Zusätzlich müssen Linearität und Dreiecksfreiheit erhalten bleiben.

**(M2) Allgemeiner Trade-Satz.** Man ersetzt die Linienmenge L_out durch L_in auf derselben Punktmultimenge. Das Ergebnis ist genau dann λ-gültig, wenn zwei Bedingungen gelten:
1. Kein neues Paar ist bereits über eine behaltene Linie kollinear.
2. Jedes neue kollineare Paar hat danach **genau einen** gemeinsamen Nachbarn.

Begründung: Nur Kanten an berührten Punkten können Dreiecke gewinnen oder verlieren. Jedes zusätzliche Dreieck enthält ein neues Paar mit einem zweiten gemeinsamen Nachbarn. Die Gradbedingung folgt aus der Punktmultimenge.

Folgerung für **disjunkte** entfernte Linien: Jeder bisherige 2-Weg x–w–y muss zerstört werden, also N(x)∩N(y) ⊆ L(x)∪L(y).

In guten Zuständen gilt μ≈2. Daher sind kleine gültige Trades selten und stark lokalisiert. Das ist die strukturelle Ursache der dünnen Zuggraphen.

**(M3) Residuen.** Auf dem λ-Arm gilt:
- R = A² + A − 12I − 2J hat Zeilensummen 0. Also Σr = 0 und L1 = 2·Σr⁺.
- F = ½·Σ(θ−3)²(θ+4)² über die nichttrivialen Eigenwerte θ. Äquivalent: F = 2Q − 8316 mit Q = Σ_{Nichtkanten} C(μ,2).
- F misst also die 4-Kreis-Zahl bzw. den spektralen Abstand zu {3, −4}.
- An 6 Graphen exakt bestätigt.

**(M4) Apex in geschlossener Form.** Tausch c↔d zwischen den disjunkten Linien {a,b,c} und {d,e,f} ist genau dann gültig, wenn:
- a,b ≁ d und c ≁ e,f, und
- CN(a,d) = A_cd + A_ae + A_af,
- CN(b,d) = A_cd + A_be + A_bf,
- CN(c,e) = A_ae + A_be + A_cd,
- CN(c,f) = A_af + A_bf + A_cd.

Auf allen 20 Graphen des 4-h-Pakets ist die Zugmenge identisch mit `fast_moves.apex_moves` und dem Referenzgenerator. Laufzeit etwa 20 ms (numpy) gegenüber etwa 300 ms (`fast_moves`) je vollständiger Nachbarschaft.

**(M5) Rotation.** Rotation ist die Hintereinanderausführung zweier Apex-Tausche (a↔b, dann a↔c) mit zusätzlicher Basis-Matching-Bedingung. Das Matching ist nicht aus λ hergeleitet. In allen 26 geprüften Graphen ist der Rotationsstrom leer.

**(M6) Pivot – der fehlende Zug.** Zwei Linien durch einen gemeinsamen Punkt p:

    {p,x,y}, {p,u,v}  →  {p,x,u}, {p,y,v}

Es ändern sich nur 4 Kanten (−xy, −uv, +xu, +yv). Die Kanten an p bleiben.

Gültig genau dann, wenn:
- x ≁ u und y ≁ v, und
- CN(x,u) = 1 + A_uy + A_xv, und
- CN(y,v) = 1 + A_yu + A_vx.

Beweis: N'(x) = N(x) − y + u und N'(u) = N(u) − v + x. Also gilt N'(x) ∩ N'(u) = (N(x)∩N(u)) \ {y,v}, und das muss genau {p} sein. Der Rest folgt aus (M2).

Eigenschaften:
- Der inverse Zug ist wieder ein Pivot.
- Es gibt 99·C(7,2)·2 = 4158 Kandidaten je Zustand.
- **Vollständigkeit und Korrektheit per Brute Force** (alle 4158 Kandidaten mit voller λ-Prüfung) auf hog57338, claude_v01_c, gen-lambda-11 und gen-lambda-03 bestätigt: 78 / 56 / 0 / 198 Züge, jeweils identisch.
- Apex verlangt disjunkte Dreiecke und kann den Pivot daher **nie in einem Schritt** darstellen.

### A.2 Evidenztabelle

| # | Befund | Herkunft | Interpretation | Alternative Erklärung | Offene Prüfung |
|---|---|---|---|---|---|
| E1 | hog57338: 131 734 strukturelle Apex-Kandidaten, **46 gültig**, Rotation 0. Minimale Änderungen dieser Züge: ΔW = +4, ΔL1 = +14, ΔF = +20. Keine neutralen Züge. | eigene Prüfung; identisch mit Projektgeneratoren | Exaktes striktes lokales Minimum unter Apex ∪ Rotation für (W,L1), L1 und F | – | – |
| E2 | Exakte BFS (nur Apex) um hog57338, Tiefe 1–4: 46 / 1 101 / 18 437 / 244 793 neue Zustände. Kein Zustand mit W<2182, L1<2398 oder F<2836. Bestes (W,L1) je Tiefe: (2186,2422), (2188,2428), (2192,2418), (2191,2424). | eigene Prüfung | Unter Apex hat das Becken einen Radius ≥ 5 und eine Barriere ≥ +4 W | – | – |
| E3 | Der einzige W-Erfolg des 144-h-Laufs (λ-W-06-A1, (2180,2398,2840), gefunden bei 3491 CPU-s) unterscheidet sich von hog57338 nur um **4 Kanten**: {16,40,60},{16,89,95} → {16,60,95},{16,40,89}. | eigene Prüfung, 144-h-Paket | Das ist genau **ein Pivot**. Mit E2 folgt, dass A1 ihn über ≥ 5 Apex-Züge netto (Escape-Segmente bis Länge 8) realisiert hat. Das erklärt den einzelnen A1-Treffer mechanistisch. | Zufall innerhalb eines Seeds; ein Treffer in 9 Paaren ist kein A1-Vorteil | – |
| E4 | Pivot-Nachbarschaften: 56–198 gültige Züge (Ausnahme gen-lambda-11: 0). hog57338 hat 7 (W,L1)-verbessernde und 1 L1-verbessernden Pivot; bester Einzelschritt (2169,2392). | eigene Prüfung, Brute Force validiert | hog57338 ist **kein** lokales Minimum mehr, sobald der Katalog vollständig um Pivot erweitert ist | – | – |
| E5 | Exakter steilster Abstieg mit Apex ∪ Pivot aus hog57338: **W → (2155,2416,2948)** in 5 Pivot-Schritten; **L1 → 2392** in 1 Schritt; **F bleibt 2836** (exaktes Minimum); Linf → (3,1,2416). | eigene Prüfung + `common.checked` | Neue Bestwerte gegenüber allen 144 CPU-h | – | Replikation mit Projektcode auf dem Ryzen |
| E6 | Tabu (Apex ∪ Pivot, Zustandstabu 7–15, 1 Seed, 240 CPU-s, 7 638 Iterationen): (2153,2430,3000) in Iteration 8, danach **keine Verbesserung** mehr | eigene Prüfung | Pivot öffnet einen Ausgang, führt aber in ein neues Becken. Die Barrierenfrage bleibt. | Tabu-Parameter ungünstig; nur ein Seed | Strategien T und L (Abschnitt B) |
| E7 | Exakter Apex-Abstieg von **allen** Linf=2-Endpunkten (4 aus dem 4-h-Lauf, 5 neue aus dem 144-h-Lauf, lambda_Linf2_00) für (W,L1): Mehrheitlich zurück nach (2182,2398), sonst (2226,2514) bzw. (2261,2554). **Nie** unter 2182. | eigene Prüfung | Die Linf=2-Kandidaten liegen im selben HoG-Becken bzw. schlechter. Migration Linf→W liefert **kein neues Becken**. | Längere, nicht exakt absteigende Wege | nur bei Bedarf |
| E8 | gen-lambda-13 und gen-lambda-17: 0 Apex- und 0 Rotationszüge, also im alten Katalog **eingefroren**. Mit Pivot: 99 Züge. gen-lambda-17 steigt dann auf (2443,3256) ab, gen-lambda-13 bleibt lokales Minimum. | eigene Prüfung | Der Familienschutz hat tote Zustände geschützt. Mit Pivot ist kein Gründer mehr isoliert (gen-lambda-11: 0 Pivot, aber 165 Apex). | – | – |
| E9 | Exakter Abstieg mit Apex ∪ Pivot von allen Z33- und triangle_packing-Gründern: bestes (W,L1) = (2399,3120) (gen-lambda-01). | eigene Prüfung | Die Nicht-HoG-Familien liegen weit hinter HoG. Gründerverarmung ist **nicht** die Hauptursache. | Tiefere Suche könnte sie heben | nur als Diversitätskontrolle |
| E10 | `sampled()` baut für jede Stichprobe und jeden Perturbationsschritt eine neue `MoveSource` und durchsucht bis zum n-ten gültigen Zug. A0 bricht den Abstieg bei der ersten nicht verbessernden Stichprobe ab. Bei einer Gültigkeitsrate von ≈ 0,03 % erklärt das die 91–93 % Generierungskosten. | Codeprüfung | `STALLED_SAMPLED` bedeutet „eine Stichprobe von 32 ohne Verbesserung“ | – | – |
| E11 | Die Vermutung „32 Züge hängen am ersten gemischten Dreieck“ ist **widerlegt** für hog57338: ≤ 3 gültige Züge je Dreieck, 32 von 46 ≈ 70 % der Nachbarschaft. | eigene Prüfung | Stichprobenbias ist nicht die Ursache | – | – |
| E12 | `worker.best()` protokolliert nur das aktive Ziel. Kinder sind nur Episodenendpunkte. | Codeprüfung | Kein zielübergreifendes Archiv. Nach E7 ist das für λ derzeit aber nicht der Engpass. | – | – |
| E13 | 144-h-Lauf: λ-A0 255–309 Episoden je CPU-h, A1 135–182. Alle W-, L1- und F-Endpunkte außer E3 sind wieder hog57338. | 144-h-Paket | Mehr Durchsatz ändert nichts, solange der Katalog das Becken nicht verlassen kann | – | – |

### A.3 Urteil zu den fünf Hypothesen

1. **Zugkatalog und Erreichbarkeit – bestätigt, Hauptursache.** Pivot fehlt. Mit Pivot fällt W sofort (E4–E5), und der historische A1-Erfolg war ein Pivot (E3). Rotation ist irrelevant (M5).
2. **Selektion und Gründerverarmung – Nebenursache.** Zwei Gründer waren eingefroren (E8). Die Nicht-HoG-Familien liegen aber auch nach exaktem Abstieg weit zurück (E9).
3. **Barrieren – bestätigt, jetzt eine Stufe tiefer.** Unter Apex allein liegt die Barriere hinter Radius ≥ 5 (E2). Mit Pivot folgt die nächste Stagnation bei (2153,2430) (E6). Das ist der eigentliche Prüfgegenstand des nächsten Experiments.
4. **Kooperation der Ziele – für λ derzeit verworfen.** Linf=2-Kandidaten fallen exakt ins HoG-Becken zurück (E7). Ein gemeinsames Archiv bleibt als Neustart-Quelle sinnvoll, aber nicht als eigene Strategie.
5. **Reparaturmodus – zurückgestellt.** Exakte k-Linien-Neupartition (Strategie L) deckt lokale exakte Reparatur ab, ohne ungültige Zustände. Pivot zeigt außerdem, dass Trades **mit gemeinsamen Punkten** berücksichtigt werden müssen. Die Disjunktheitsannahme meiner ersten Fassung war zu eng.

### A.4 Korrekturen gegenüber meiner ersten Fassung

- „hog57338 ist exaktes lokales Minimum“ gilt **nur für Apex ∪ Rotation**. Mit Pivot ist die Aussage falsch.
- Die 3-Linien-Trade-Prüfung war auf disjunkte Linien beschränkt. Sie hätte den Pivot nicht gefunden und ist durch (M2) ohne Disjunktheit zu ersetzen.
- Die Linf-Migrations-Hypothese ist jetzt durch E7 entschieden, nicht mehr nur offen.

---

## B. Vorgeschlagene Verfahren

Drei Strategien plus unveränderte Baseline. Jede Stufe isoliert genau einen Effekt.

| Kürzel | Inhalt | isolierter Effekt |
|---|---|---|
| **B0** | Fast-A0, unverändert | Baseline |
| **P** | wie B0, aber Katalog Apex ∪ Pivot (Rotation entfällt) und **exakte** Nachbarschaft im Abstieg (Best-Improvement bis `LOCAL_MIN_EXACT`) | Katalog + exakter Abstieg, übrige Memetik gleich |
| **T** | exakte Tabu-Suche über Apex ∪ Pivot mit Neustarts aus dem Elitearchiv | Barrierensteuerung |
| **L** | wie T, zusätzlich k-Linien-Neupartition (k=3 exakt enumeriert, k=4 per CP-SAT) inklusive Linien mit gemeinsamen Punkten | größere Trades |

### B.1 Definitionen

**Nachbarschaft.** N(s) = Apex(s) ∪ Pivot(s), exakt nach (M4) und (M6). Alle bewerteten Kinder werden mit exakten Scores geführt. Aufwand etwa 20 ms für Apex plus etwa 1 ms für Pivot plus die Bewertung von etwa 120 Kindern. Gemessen etwa 32 Tabu-Iterationen je CPU-Sekunde in reinem Python/numpy.

**P (in die bestehende Memetik eingebettet).**
- Perturbation wie bisher, aber Zugwahl gleichverteilt aus N(s). Gewichte Apex:Pivot proportional zur Nachbarschaftsgröße, also keine Streamgewichte.
- Abstieg:
```
wiederhole:
    C = {Kinder aus N(s), die im aktiven Ziel besser sind}
    wenn C leer: Status LOCAL_MIN_EXACT; Ende
    s = bestes Element von C
```
- Keine Stichproben mehr. Das CPU-Limit bleibt als Sicherung, ein Abbruch durch das Limit wird als `CPU_LIMIT` protokolliert, nie als Minimum.

**T (Tabu).**
```
s = Start; best = s; tabu = {}
für jede Iteration i:
    Kandidaten = N(s), sortiert nach (Zielschlüssel, Zufall mit Seed)
    wähle den ersten Kandidaten, der nicht tabu ist
        oder der best schlägt (Aspiration)
    tabu[hash(s)] = i + zufällig aus [t_min, t_max]    # t in [7,15], Entwicklung
    s = gewählter Kandidat; ggf. best aktualisieren
    wenn seit K Iterationen kein neuer best (K = 2000):
        Neustart aus dem Elitearchiv mit Zufallsweg von 5–8 Zügen aus N
    wenn N(s) leer: sofortiger Neustart
```

Das Zustandstabu hat sich im Test (E6) als zu schwach gezeigt. Für die Entwicklung sind zwei Attribut-Tabus vorgesehen: „entfernte Linien nicht wiederherstellen“ und „bewegten Punkt nicht erneut bewegen“. Eine Variante wird in Phase 1 festgelegt.

**L (k-Linien-Neupartition).**
- Auswahl von S: Linien durch die Punkte eines Hotspot-Paares (|r| ≥ 2) oder durch den gemeinsamen Punkt zweier Linien mit maximalem |r|-Beitrag. k = 3 oder 4, **gemeinsame Punkte erlaubt**, Multiplizitäten beachtet.
- Kandidatenlinien: Tripel der Punktmultimenge, deren neue Paare nicht über behaltene Linien kollinear sind und die notwendige 2-Wege-Bedingung aus (M2) erfüllen, verallgemeinert auf entfernte Kanten.
- k=3: exakte Überdeckungen enumerieren. k=4: CP-SAT (ortools 9.15) mit
  - Überdeckungsbedingung (jede Punktmultiplizität exakt),
  - paarweiser Linearität der neuen Linien,
  - Zielfunktion aus den exakten Residuen aller Paare mit einem Punkt in S. Für u∈S, v∉S ist μ linear in den Linienvariablen, innerhalb von S werden AND-Variablen verwendet. W wird über reifizierte Indikatoren abgebildet, L1 über Beträge, F über Tabellen μ∈[0,7].
- **Jede Lösung wird unabhängig voll λ-geprüft**, sonst verworfen. Das Zeitlimit je Teilproblem ist fest (Entwicklung: 0,5 s).
- L ist **nachrangig**: L wird nur in Phase 2 geführt, wenn T in Phase 1 auf den Entwicklungsstarts stagniert.

**Archiv (T und L).**
- Pareto-Menge über (W, L1, F, Linf, Nmax) aller bewerteten gültigen Kinder, dedupliziert nach kanonischer Klasse (pynauty).
- Obergrenze 256 Einträge insgesamt, 64 je Ziel. Bei Überlauf entscheidet der Zielrang, dann das Alter.
- Nur für Neustarts, nicht für die laufende Selektion.
- Nach E7 kein Linf→W-Migrationsmodus.

**Verworfen und warum:**
- Rotation: leer und Spezialfall von zwei Apex-Zügen.
- Mehr Episoden durch Beschleunigung: E13.
- Größere Zufallsperturbationen ohne exakten Abstieg: ineffektiv, weil die Barriere erst ab Radius ≥ 5 überwunden würde.
- Crossover.
- Linf-Migration: E7.
- Reparatur mit echten λ-Verletzungen: erst nach L.

### B.2 Pflichtkontrollen vor dem Einsatz (Codex/Implementierung)

1. Differentialtests Apex nach (M4) gegen `fast_moves.apex_moves` auf allen 26 λ-Graphen dieses Reviews: identische Zugmenge. Für 20 Graphen ist das hier bereits bestanden.
2. Pivot nach (M6) gegen Brute Force (4158 Kandidaten mit voller λ-Prüfung) auf mindestens 6 Graphen, darunter gen-lambda-11 (0 Züge) und gen-lambda-03 (198). Für 4 Graphen hier bestanden.
3. **Positive Kontrolle:** hog57338 → W-06-A1-Endpunkt ist genau der Pivot (p,x,y,u,v) = (16,40,60,89,95). Der Zug muss gefunden werden und (2180,2398,2840) ergeben.
4. **Negative Kontrollen:**
   - Pivot mit x~u wird abgelehnt.
   - Ein künstlich eingebauter zweiter gemeinsamer Nachbar führt zur Ablehnung.
   - Apex auf nicht disjunkten Dreiecken wird abgelehnt.
5. Inverse: Pivot∘Pivot⁻¹ und Apex∘Apex⁻¹ ergeben jeweils den Ausgangszustand.
6. Jedes adoptierte Kind wird in Stichproben voll λ-verifiziert, **jeder** neue Bestwert immer.
7. L: k-Neupartition muss Apex und Pivot als Spezialfälle wiederfinden (k=2), und jede CP-SAT-Lösung wird voll geprüft.
8. Budgetkontrolle: Der Exakt-Abstieg läuft unter derselben CPU-Abrechnung. Eine Wiederaufnahme erzeugt kein frisches Budget.

---

## C. Nächstes begrenztes Experiment „λ-Probe-2“

**Nicht freigegeben.** Neues Budget, getrennt von den alten 144 h und 4 h:

| Phase | Inhalt | Jobs | CPU | Walltime (18 Worker) |
|---|---|---|---|---|
| 0 | Deterministische Replikation mit Projektcode: exakter Abstieg (Apex ∪ Pivot) für W, L1, F und Linf von allen 26 λ-Graphen. Ergebnis sind die Referenzminima je Gründer. | 26 | ≤ 1 CPU-h | ≈ 10 min |
| 1 Entwicklung | B0, P, T × Ziele (W,L1) und F × 3 gepaarte Seeds × 0,5 CPU-h; Starts nur hog57338 und claude_v01_c | 18 | 9 CPU-h | ≈ 35 min |
| 2 Bestätigung | Parameter eingefroren; B0, P, T (+ L, falls T in Phase 1 stagniert) × (W,L1) und F × 6 **neue** gepaarte Seeds × 1 CPU-h | 36 (48 mit L) | 36 (48) CPU-h | ≈ 2 h (≈ 3 h) |
| **Summe** | | | **≈ 46 (58) CPU-h** | **≈ 3 (4) h** |

**Gründer der Bestätigung (Trennung von der Entwicklung):**
- HoG: hog57328, hog57271, hog57200, lambda_Linf2_00
- 5 Linf=2-Endpunkte des 144-h-Laufs
- alle 10 Z33-Gründer (auch gen-lambda-13 und -17; nicht mehr eingefroren)
- codex_v01_c08

hog57338, claude_v01_c und die hier gefundenen Rekordgraphen gehören **nicht** zur Bestätigung. Die Rekordgraphen dürfen nur in einer separat markierten Fortsetzungsspur verwendet werden.

**Populationen und Episoden:**
- B0 und P behalten Population 16 und die alte Selektion (P mit exaktem Abstieg).
- T und L sind Einzelpfad-Suchen mit Neustart aus dem Archiv. Das CPU-Budget je Job ist identisch.

**Speichergrenzen:**
- Archiv 256 Einträge je Job.
- Tabu-Tabelle höchstens 50 000 Hashes mit Verfall.
- Kurven nur bei Verbesserung.
- Freier Platz auf dem Windows-Trägervolumen **und** in WSL wird überwacht. Stopp bei unter 20 GB frei.

**Erfolgsfall:** Alle Residuen null → unabhängige Vollverifikation, sofortige Sicherung (graph6 + SHA256 an zwei Orten), Meldung, kontrollierter Stopp aller Worker.

**Fortschrittsanzeige:**
- Verbesserungen mit Ziel, Uhrzeit und Zeit seit der letzten Verbesserung, 25 Zeichen eingerückt je Ziel.
- Strategie/Seed/Start eindeutig benannt.
- Status alle 10 min mit Budget-ETA.
- Bestwerte **je Strategie getrennt**.

### C.1 Vorab festgelegte Entscheidungsregeln

- **Referenz** je Gründer und Ziel ist das exakte Abstiegsminimum aus Phase 0.
- **Robuste Verbesserung** einer Strategie X gegenüber B0: X unterschreitet die Referenz in ≥ 4/6 Seeds bei ≥ der Hälfte der Gründer, und B0 schafft das in ≤ 1/6 Seeds.
- **T gegenüber P:** T gilt nur dann als besser, wenn T bei ≥ der Hälfte der Gründer im Median über die Seeds ein strikt besseres (W,L1) erreicht als P.
- **L gegenüber T:** entsprechend.
- **Rekord:** jedes verifizierte (W,L1) < (2153,2430) bzw. F < 2836. Rekorde werden gemeldet, aber nicht als robuster Effekt gewertet.
- Aus 3 bzw. 6 Seeds werden keine Signifikanzaussagen abgeleitet.

---

## D. Messgrößen

**Primär:** (W,L1) des besten Zustands je Job, relativ zur Referenz des Gründers.

**Sekundär:**
- L1, F, Linf, Nmax
- CPU-Zeit bis zur ersten Unterschreitung der Referenz
- Zahl verschiedener Endklassen (kanonisch)
- Rückkehrquote ins Referenzbecken (exakter Abstieg führt zum Referenzminimum)
- Familienerhalt (nur B0 und P)
- realisierter Anteil Apex/Pivot/k-Trade
- realisierte Perturbations- und Tabu-Weglängen
- gültige Nachbarschaften und bewertete Kinder je CPU-Sekunde
- Anteil `LOCAL_MIN_EXACT` gegenüber `CPU_LIMIT`

Rekord und robuste Verbesserung werden getrennt berichtet.

---

## E. Empfehlung

1. **Sofort, ohne neue Kampagne:** Pivot nach (M6) und Apex nach (M4) implementieren und die Kontrollen aus B.2 bestehen lassen. Für λ `STALLED_SAMPLED` durch einen exakten Abstieg mit `LOCAL_MIN_EXACT` ersetzen. Die Beschleunigung aus `fast_moves` bleibt für Ω relevant.
2. **Dann λ-Probe-2** (≈ 46–58 CPU-h, ≈ 3–4 h wall) nach Freigabe.
3. **Übernahme in eine Hauptkampagne:**
   - T robust besser als P und B0 → T übernehmen.
   - Nur P robust besser als B0 → P übernehmen (minimale Änderung der bestehenden Memetik).
   - L robust besser als T → L übernehmen; zusätzlich Kosten je Verbesserung ausweisen.
   - Keine Strategie robust besser als B0 → keine Hauptkampagne mit diesen Verfahren. Nächste Kandidaten wären dann der Reparaturmodus mit echten λ-Verletzungen und neue Gründerfamilien.
4. **Die unveränderte Baseline beizubehalten ist für λ nicht vertretbar.** Sie ist nachweislich im HoG-Becken eingeschlossen, und der einzige Ausweg des 144-h-Laufs war ein fehlender Einzelzug.
5. Keine Lösungsprognose. F=2836 ist unter Apex ∪ Pivot exakt minimal, und W stagniert nach Pivot erneut (E6).

---

## Nächster manueller Schritt (Ryzen/Ubuntu/WSL, rein lesend)

Prüft Repo-Stand und freien Platz (Linux und Windows-Trägervolumen). Bitte ausführen und die Ausgabe zurückmelden:

```bash
cd /home/rb/conway99_workspace/conway99-research && git fetch -q origin && git status -sb | head -3 && git rev-parse HEAD origin/memetik && df -h / /mnt/c && nproc && free -g | head -2
```

---

## Anhang 1 – Referenzimplementierung Pivot (Prototyp, numpy)

```python
def pivot_valid(A):
    """Lines {p,x,y},{p,u,v} through common p -> {p,x,u},{p,y,v}. Exact criterion (M6)."""
    Af = A.astype(np.float32); CN = np.rint(Af @ Af).astype(np.int64)
    T = triangles(A); byp = {}
    for t in T:
        for p in t:
            byp.setdefault(p, []).append(tuple(q for q in t if q != p))
    out = []
    for p, ls in byp.items():
        for (x, y), (u, v) in itertools.combinations(ls, 2):
            for (x1, y1) in ((x, y), (y, x)):
                if A[x1, u] or A[y1, v]:
                    continue
                if CN[x1, u] == 1 + A[u, y1] + A[x1, v] and CN[y1, v] == 1 + A[y1, u] + A[v, x1]:
                    out.append((p, x1, y1, u, v))
    return out

def do_pivot(A, m):
    p, x, y, u, v = m; B = A.copy()
    B[x, y] = B[y, x] = 0; B[u, v] = B[v, u] = 0
    B[x, u] = B[u, x] = 1; B[y, v] = B[v, y] = 1
    return B
```

## Anhang 2 – Neue Bestgraphen dieses Reviews (λ-gültig; `common.checked` bestanden)

Format: Datei – Scores, λ-Prüfung, SHA256(graph6), dann graph6.

**hog57338_L1.g6** – {'W': 2169, 'L1': 2392, 'F': 2844, 'Linf': 3, 'Nmax': 3} True e618664166c22755c378efdcf96e6a1380d1e94d3c471ce997f9cb53751b450a

```
~?@bsaCKB?_CAP?c?_CS???????A???@G@??O??@??`??A??G??A?IG?@???CGP??FG??GGo?G?CG?AA`??OGO??A@?K?@?OOOA?DOK??C?`???O`??A??Co`??HG?@_O?_?@H?@ACKG@??G?GR??G`@?_aG??o??_G_?C?O@??p?IOIO?`@@GCB?_G`GS??D??@W?C?O_?GD?O?a?C????a_?SG_?C?A?g??_P??@?G?R??caA?_@gAOODO@OG?K@C@?GGA?OoCCG?S?G??C?BGE?G@_?D?G?`A???p_@@GOA@_?AH]??@IA??GOoGAO@?GR?G@??OAg@GO?Co?GOd??@O??GOAGP?GO?Gq?G?D_ga???G@?@_YK???O??P_?G?CAACA?gGCC?@T??O???D?P_@GD?_??G?a?_W??GA?GBC??g?_?GOGc?_o?_CEOO@?O?aOO?KCO?_?C_GHA?g?_@_g@?R???CAWB?A@C?@D@`@`?G?AA?@CGC??OgD??AoH?K?a?D?OQ?_I@@?c??o??@OAHGS?OA_??gCO??D?`OC?BE_B?O???@@O?C??C_?g[?OOo?`W@????@?GDCGOc???_A?OCQ@?Ao?HO??APg??C?CcAWGAK_?_???ACH?A?@a@DCGC???CAi_AO?a@OG???@H?_C_A?`??_@@@PGAOOO????og[?O?B?o??iG_?@?E?OOEOAA@oDA??????w?q?o_O??_@OA_A_??Eb@G@?????OA@O_CE???`_S_G?J???@A[??E?BO?OM?G???N?A{??CG??o?O????
```

**hog57338_W.g6** – {'W': 2155, 'L1': 2416, 'F': 2948, 'Linf': 3, 'Nmax': 5} True 47abeada115d2c416eab90b083527e8c904b947e760559dccfcd95a721b59db7

```
~?@bsaCKB?_CAP?C?_CS???????A???@G@?AO??@??`??A??G??A?IG?@???CGP??FG??GGo?G?CG?AA`??OGO??A@?K?@?OOOA?DOK??C?`???O`??A??Co`??HG?@_O?_?@H?@ACKG@??G?GR??G`@?_aG??o??_G_?C?O@?@p?AOIO?`@@GCB?_G`GS??D??@W?C?O_?GD?O?a?C????a_?SG_?C?A?g??_P??@?G?R??caAA_?gAOODO@OG?K@C@?GGA?OoCCG?S?G??C?BGE?G@_?D?G?`A???p_@@GOA@_??H]??@IA??GOoGAO@?GR?G@??OAg@GO?Co?GOd??@O??GOAGP?GO?Gq?G?D_ga???G@?@_YK???O??P_?G?CAACA?gGCC?@T??O???D?P_@GD?_??G?a?_W??GA?GBC??g?_?GOGc?_o?_CEOO@?O?aOO?KCO?_?C_GHA?g?_@_g@?R???CAWB?A@C?@D@`@`?G?AA?@CGC??OgD??AoH?K?a?D?OQ?_I@@?c??o??@OAHGS?OA_??gCO??D?`OC?BE_B?O???@@O?C??C_?g[?OOo?`W@????@?GDCGOc???_A?OCQ@?Ao?HO??APg??C?CcAWGAK_?_???ACG?AG@a@DCGC???CAi_AOGa@OG???@H?_C_A?`??_@@@PGAOOO????og[?O?A?o_?iG_?@?E?OOEOAA@oDA??????w?q?o_O??_@OA_A_??Eb@G@????OOA@O?CE???`_S_G?J???@A[??E?BO?OM?G???N?Qw??CG??o?O????
```

**tabu_hog57338_W_1.g6** – {'W': 2153, 'L1': 2430, 'F': 3000, 'Linf': 3, 'Nmax': 8} True cc244dabce203ca7d55ca6e81f96ba6e887e05ebcc751b9a37915b03417a7794

```
~?@bsaCKB?_CAP?C?_CS???????A???@G@?AO??@??`??A??G??A?IG?@???CGP??FG??GGo?G?CG?Aa`??OGO@?A@?K?@?OOOA?DOG??C?`???O`??A??Co`??HG?@_O?_?@H?@ACKG@??G?GR??G`@?_aG??o??_G_?C?O@?@p?AOIO?`@@GCB?_G`GS??D??@W?C?O_?GD?O?a?C????i_?SG_?C?A?g??_P??@?G?R??caAA_?gAOODO@OG?K@C@?GGA?OoCCG?S?G??C?BGE?G@_?D?G?`A???p_@@GOA@_??H]??@IA??GOoGAO@?GB?G@??OAg@GO?Co?GOd??@O??GOAGP?GO?Gq?G?D_ga???G@?@_YK???O??P_?G?CAACA?gGCC?@T??O???D?P_?GD?_??G?_?_X??GACGBC??g?_?GOGc?_o?_CEOO@?O?aOO?KCO?_?C_GHA?g?_@_g@?B???CAWB?A@E?@D@`@`?G?AA?@CGC??OgD??AoH?K?a?D?OQ?_I@@?c??o??@OAHGS?OA_??gCO??D?`OC?BE_B?O???@@O?C??C_?g[?OOo?`W@????@?GDCGOc???_A?OCQ@?Ao?HO??APg??C?CcAWGAK_?_???ACG?AG@a@DCGC???CAi_AOGa@OG???@H?_C_A?_??_@@@PGAOOO????og[?O?A?o_AiG_?@?A?OOEOAA@oDA??????w?q?o_O??_@OA_A_??Eb@G@????OOA@O?CE???`_C_G?J???`A[??E?BO?OM?G???N?Qw??CG??o?O????
```
