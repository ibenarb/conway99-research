# Conway99 · Memetik λ · Reviewer-Ausarbeitung zum gemeinsamen Auftrag vom 22.09.2026

Stand: 22. September 2026. Unabhängig erstellt, ohne Abstimmung mit der Codex-Ausarbeitung.

**Grundlage:** Ergebnisstand `84c46aac2b39d718c44daee2a7b994c29930e6c5`, eingefrorener Suchcode
`b659cb8743dd6036d91dafb466b2d12cb21a29b0`, Auftrag `0a3b7b6870f7892cbb229c5aee9fb04860e69fd1`.

**Datenlage:** Das vollständige Originalarchiv `ryzen_lambda_compare_020_20260921.tar.gz`
(287 MiB, SHA256 `c9856a66…c32b382`) lag mir **nicht** vor. Alle Aussagen, die nur daraus
prüfbar wären (Archivzeilen, Ereignisprotokolle, Pfadhistogramme, Statusintervalle), sind
als übernommen oder als fehlend gekennzeichnet. Eine vollständige Rohdatenprüfung wird
nicht behauptet.

**Kennzeichnung der Evidenz**

- **[S]** selbst ausgeführt oder nachgerechnet (Programme im beigefügten ZIP)
- **[Ü]** übernommen aus dem Codex-Audit, `BERICHT.md`, `SUMMARY.json`, `DESIGN.md`
- **[H]** Hypothese
- **[F]** fehlende Daten

**Abgrenzung meiner Prüfungen:** Eigener graph6-Decoder, eigene Residuen-/Score-Rechnung,
eigene λ-Gültigkeitsprüfung und eigene Brute-Force-Enumeration von Apex und Pivot sind
projektcodefrei (`indep.py`, `neigh.py`). Der allgemeine Dreierzyklus, das inkrementelle
Scoring und die Tabu-Entscheidungsregel stammen in meinen Sonden aus dem eingefrorenen
Projektcode; jedes daraus erzeugte Ergebnis habe ich anschließend unabhängig nachgeprüft.

---

## A. Urteil

### A.1 Was der abgeschlossene Vergleich belegt

**1. P als Arbeitsreferenz ist gut begründet, eine TC-Verlängerung dagegen kaum.**

- P verbessert W in 11 von 12 Läufen noch zwischen 1800 und 3600 s; die letzten aktiven
  W-Verbesserungen liegen bei 1681,2 – 3521,5 CPU-s [S, aus `ENDPOINTS.json` neu berechnet].
- T ist faktisch früh fertig: 11 von 12 letzten W-Verbesserungen fallen bis 101,4 s,
  eine einzige bei 1958,8 s [S].
- TC ist nach 19,3 – 19,8 s fertig [S/Ü].
- B0 verbessert in **keinem** der zwölf W-Jobs irgendetwas (letzte Verbesserung 0,0 s) [S].

Meine Neuberechnung der Paarbilanzen aus `ENDPOINTS.json` stimmt mit den veröffentlichten
Zahlen überein [S]:

| Kontrast (W-Ziel) | 600 s | 1800 s | 3600 s |
|---|---:|---:|---:|
| P gegen B0 | 12/0/0 | 12/0/0 | 12/0/0 |
| T gegen B0 | 12/0/0 | 12/0/0 | 12/0/0 |
| TC gegen B0 | 12/0/0 | 12/0/0 | 12/0/0 |
| T gegen P | 10/2/0 | 4/3/5 | 1/0/11 |
| TC gegen T | 10/0/2 | 10/0/2 | 10/0/2 |
| TC gegen P | 12/0/0 | 11/0/1 | 6/0/6 |

**2. Die identische TC-Bestlösung ist aus dem Code erklärbar; ein Implementierungsfehler
ist dafür nicht nötig** [S].

- `begin_path()` startet deterministisch beim besten Gründer im aktiven Ziel, im W-Ziel
  also `endpoint_W2180`. Der Seed spielt für den Start keine Rolle.
- Der strikte Bestabstieg 2180 → 2169 → 2164 → 2159 → 2155 hat in jedem Schritt eine
  Gleichstandsmenge der Größe 1, ist also seedunabhängig [S].
- Meine getreue Nachbildung von `Engine.step_tabu` für alle zwölf echten Kampagnenseeds
  ergibt: identische Pfade bis Iteration 14, drei Zweige in den Iterationen 15–18 allein
  durch unterschiedliche Tabu-Tenures, und in **Iteration 22 in allen zwölf Seeds wieder
  denselben Graphen (2141, 2492)** [S].
- Das passt zu den berichteten 19,3–19,8 CPU-s bei rund einer Iteration pro Sekunde
  (Median 3546,5 Iterationen in 3600 s) [S].
- Folge: Die zwölf TC-Seeds sind in der entscheidenden Frühphase keine zwölf unabhängigen
  Replikate, sondern Pseudoreplikate eines nahezu determinierten Trichters.

**3. Danach driftet der Tabupfad aus der guten Region heraus** [S, Simulation Seed 0, 250 Iterationen].

- TC/W: Median W über die 250 Iterationen 2231, über die letzten 100 Iterationen 2245,
  Maximum 2261. Alle 250 Zustände sind paarweise verschieden.
- T/W: Median 2242,5, letzte 100 Iterationen 2260, Maximum 2294.
- Der Restart kommt erst nach 2000 stagnierenden akzeptierten Schritten, bei TC also
  etwa einmal pro Stunde (`restarts` = 1 je TC-Job, 3 je T-Job) [S].
- Die Restartquelle ist das Jobarchiv, das überwiegend aus eben diesem Driftgebiet
  stammt; ein Turnier über acht zufällige Archivklassen führt daher selten zur Elite [H].
- P kehrt dagegen über Elitenpopulation, begrenzte Perturbation (2–32 Züge) und strikten
  Abstieg regelmäßig in gute Regionen zurück. Das ist die plausibelste Mechanik hinter der
  Rangumkehr zwischen 600 und 3600 s [H, gestützt durch S].
- Die Archivzahlen sprechen gegen ein enges Zykeln: bei T und TC kommen auf jede Iteration
  etwa 1,003–1,006 Archivklassen [S].

**4. Der gesamte bisherige Fortschritt ist lokale Verfeinerung um einen einzigen
HoG-Graphen** [S].

- Alle 192 aktiven Endbesten stammen aus drei Linien, alle aus der Familie HoG:
  `hog57338`, `endpoint_W2180`, `endpoint_Linf2_N262`.
- Beschrifteter Kantenabstand zu `hog57338` (von 693 Kanten):

  | Graph | ausgetauschte Kanten |
  |---|---:|
  | `endpoint_W2180` | 2 |
  | Linf-Rekord (2, 221, 2462) | 14 |
  | L1-Rekord 2388 | 20 |
  | aktiver W-Rekord 2130 | 29 |
  | TC-Bestgraph 2141 | 48 |
  | beobachteter W-Rekord 2123 | 59 |
  | Ein-Schritt-Zeuge 2121 | 60 |

  Die übrigen Gründer liegen bei etwa 553–595 ausgetauschten Kanten, also auf dem Niveau
  unverwandter Beschriftungen.
- Strikter Bestabstieg im vollständigen TC-Katalog ab jedem der 16 Gründer endet bei [S]:
  (2155, 2416) für `hog57338` und `endpoint_W2180`; (2184, 2506) für den Linf-Gründer;
  2311 und 2312 für die beiden anderen HoG-Linien; 2367 für die Packing-Linie;
  2353–2440 für die Z33-Lifts; `gen-lambda-13` ist bei 2508 bereits lokales Minimum.
  Bei den Z33-Lifts treten Gleichstandsmengen der Größe 33 auf, offenkundig ein
  Symmetrieeffekt der Lift-Konstruktion.
- Konsequenz: Die Ergebnisse sind Aussagen über lokale Suche in einer HoG-Region,
  nicht über Startfamilien allgemein.

**5. Archivrekorde enthalten nachweislich weiteren Fortschritt, und zwar über zwei Züge** [S].

- Ich reproduziere die veröffentlichte Nachdiagnose unabhängig: Für alle sechs Zensusgraphen
  stimmen meine Brute-Force-Zahlen für Apex und Pivot exakt mit `RECORD_CENSUS.json`
  überein, sowohl die Zuganzahlen als auch die Verbesserungszahlen je Ziel.
- Alle 19 Zensus-Zeugen sind gültig, ihre Scores stimmen, und die angegebenen Züge
  erzeugen genau den angegebenen graph6 [S].
- Der Ein-Schritt-Zeuge W=2121 ist im vollständigen Katalog (37 Apex + 61 Pivot +
  38 Zyklus = 136 Züge) in Tiefe 1 lokal minimal [S].
- In **Tiefe 2** (18.892 Folgen) existieren zwei verbessernde Zustände. Der beste ist

  **(W, L1, F, Linf, Nmax) = (2116, 2452, 3148, 3, 12)**,

  erreicht über Pivot `{(14,26),(43,44)} → {(14,44),(26,43)}` nach (2128, 2454, 3128, 3, 11)
  und anschließend einen Dreierzyklus
  `{(14,61),(22,61),(25,48),(44,92),(48,53),(81,92)} → {(14,48),(22,48),(25,92),(44,61),(53,92),(61,81)}` [S].
  Unabhängig geprüft: λ-gültig, alle fünf Scores stimmen. graph6 in
  `witness_2116_result.json`.
- Kategorie: nach dem Lauf erzeugter Zwei-Schritt-Zeuge. Kein Kampagnenendpunkt, kein
  globaler Rekordanspruch, **nicht** weiter abgestiegen.
- W=2130 und W=2141 haben in Tiefe 2 keine Verbesserung (19.630 bzw. 17.295 Folgen) [S].

**6. Das F-Plateau reicht mindestens zwei Züge tief** [S].

Am HoG-Graphen mit F=2836 gibt es 148 Züge und 21.961 Zwei-Zug-Folgen ohne jede
F-Verbesserung. Das ist kein globaler Minimalitätsbeweis, aber es erklärt, warum alle
48 F-Jobs unverändert blieben.

**7. Die Zeitanomalie ist eingegrenzt, aber nicht geklärt** [S].

Bei höchstens 18 gleichzeitigen, einthreadigen Workern und mindestens 3595,022205 CPU-s
je Job gilt zwingend Makespan ≥ ⌈192/18⌉ · 3595,022205 s = **39.545,2 s** (10 h 59 min 05 s).

| Größe | Wert | Differenz zur Schranke |
|---|---:|---:|
| Untere Schranke (wait4, 18 Slots) | 39.545,2 s | – |
| UTC-Dauer | 39.890 s | +344,8 s (+0,87 %) |
| `comparison_timing.json` (monoton) | 36.910,9 s | −2634,4 s (−6,7 %) |

Die monotone Dauer ist mit den wait4-Messungen **unvereinbar**, solange beide dieselbe
Zeitbasis haben. UTC und wait4 sind dagegen verträglich; der Rest von 345 s entspricht
Startaufwand und Taillenlücken. Entweder läuft CLOCK_MONOTONIC zu langsam (Faktor etwa
1,071–1,081), oder rusage und CLOCK_REALTIME weichen gemeinsam um denselben Faktor ab [H].
Da die Gast-UTC per Hyper-V-Zeitsynchronisation vom Host kommt, halte ich die langsame
monotone Uhr für die sparsamere Erklärung [H]; entschieden wird das nur mit einer
unabhängigen Hostzeit (D1). Das CPU-Budget selbst steuert wait4 und wurde für alle Arme
gleich gemessen; der Vergleich bleibt intern fair. Aus der monotonen Dauer wird kein
Durchsatz und keine Beschleunigung abgeleitet.

### A.2 Befundtabelle

| Befund | Alternativerklärung | Erforderliche Zusatzprüfung | Konsequenz |
|---|---|---|---|
| P/T/TC schlagen B0 12/12 im W-Ziel [S] | Verfahrenspaket, nicht Einzeloperator; B0 verbessert überhaupt nichts [S] | keine | B0 nur noch historische Kontrolle, kein Arm mehr |
| P schlägt T 11/0/1 bei 3600 s, T schlägt P 10/2/0 bei 600 s [S] | T ist früh stark und driftet danach ab [S-Simulation] | Pfadmaxima/`histogram` aus `result.json` [F] | T wird nicht fortgeführt |
| TC erreicht in allen 12 Seeds denselben Graphen [S] | deterministischer Start, gleichstandsfreier Abstieg, Trichter über Iteration 22 [S] | erledigt: Nachbildung trifft Bestwert und Iteration in allen 12 Seeds [S] | TC-Seeds sind Pseudoreplikate; keine volle TC-Verlängerung |
| TC findet nach 20 s nichts mehr trotz Restart [Ü/S] | Drift nach W≈2240; Restartschwelle 2000 Schritte; Restartquelle im Driftgebiet [H] | 3-Seed-TC-Verlängerung als Diskriminator (Stufe 2, optional) | Elite-Restart-Variante TE statt Verlängerung |
| TC schlägt T 10/0/2 [S] | Katalogvorteil **innerhalb** einer driftenden Tabusuche | Katalogeffekt im langfristig besten Rahmen messen | neuer Arm PC = P + Dreierzyklus |
| P verbessert noch spät [S] | Rest-Verbesserungen könnten kurz danach versiegen | zustandserhaltende Verlängerung mit Zwischenmesspunkten | P/W 12 Jobs auf 4 h |
| Alle Endbesten aus einer HoG-Region [S] | Elitenselektion verdrängt fremde Familien früh | Gründerdiversität als eigener späterer Versuch | keine Verallgemeinerung auf Startfamilien |
| 2123 → 2121 → (Tiefe 2) 2116 [S] | Einzelfall; kein Beleg für Kooperation allgemein | Ernte aller OBSERVED-Zeilen (D5) | Rekordfortsetzung R, getrennt vom Vergleich |
| F=2836 in Tiefe 1 und 2 unverbesserbar [S] | Barriere ≥ 3 Züge oder ungeeignete Startregion | Tiefe-3-Zensus (jetzt nicht budgetiert) | F bleibt nachrangig |
| monotone Dauer unter der Makespan-Schranke [S] | Uhrendrift unter WSL2/Hyper-V oder rusage-Inflation [H] | D1 mit unabhängiger Hostzeit | Budget per wait4 gilt; ETA erst nach D1 |

### A.3 Bewertung der vorgegebenen Optionen

**Option A – länger laufen lassen.** Der P-Teil (36 CPU-h) wird übernommen: P verbessert
nachweislich bis ans Budgetende. Der TC-Teil (36 CPU-h) wird verworfen: zwölf Pfade aus
demselben Trichter mit etwa einem Restart pro Stunde liefern wenig zusätzliche Information.
Meine falsifizierbare Vorhersage lautet: Eine TC-Verlängerung auf 4 h unterschreitet
W=2141 in höchstens einem von drei Seeds. Das kleinste Experiment, das meine Einschätzung
von der 72-h-Variante unterscheidet, ist genau das: TC/W, Seeds 00–02, von 1 auf 4 h,
also 9 CPU-h (Stufe 2, optional). `extend --cpu-hours 4` darf dafür nicht benutzt werden,
es würde 576 zusätzliche CPU-Stunden über alle 192 Jobs freigeben.

**Option B – Archivrekorde nutzen.** Umsetzung in zwei getrennten Teilen: eine
schreibgeschützte Ernte aller OBSERVED-Zeilen mit anschließendem strikten Abstieg (D5)
und eine pragmatische Rekordfortsetzung R mit unverändertem P ab den besten bekannten
Klassen. Migration zwischen Jobs oder ein gemeinsames Archiv wird jetzt **nicht** eingebaut;
das würde Verfahrensvergleich und Rekordjagd vermischen. Der saubere spätere Test wäre
P gegen P+Migration auf neuen Seeds mit klar definierten Empfängern, Zeitpunkten und
CPU-Zurechnungen. Der Vergleich ohne Migration ist genau Stufe 1.

**Option C – TC-Konvergenz und Barrieren.** Ursache nach A.1 Nr. 2–3 soweit geklärt, wie
Git-Daten reichen. Zwischen den vier Erklärungen ordne ich ein: strukturelles Becken
teilweise (2141 ist in Tiefe 2 unverbesserbar [S]), unzureichende Diversifikation
überwiegend (ein deterministischer Start, ein Restart pro Stunde, Restartquelle im
Driftgebiet), ungeeignete Restartparameter ja (Schwelle 2000), Implementierungsfehler:
in den geprüften Teilen kein Hinweis. Die gezielte Kontrolle ist der Arm TE, der genau
den Restart-Mechanismus ändert und sonst nichts.

**Option D – F-Plateau, neue Familien, Operatoren.** F braucht nach A.1 Nr. 6 mindestens
Drei-Zug-Barrieren oder andere Startregionen. Beides ist ein eigener Versuch und wird
jetzt nicht budgetiert. Neue Gründerfamilien sind laut A.1 Nr. 4 die strategisch größte
offene Frage, aber ebenfalls ein eigener, separat zu kontrollierender Versuch. Ω bleibt
geschlossen.

**Priorisierte Fortsetzung:** D1-Uhrdiagnose → Stufe 1 (P-Verlängerung, PC, TE) → Ernte →
Stufe 2 (Rekordfortsetzung R, optional TC-Diskriminator).

---

## B. Versuchsmanifest

### B.1 Stufe 0 – Diagnose und Kontrollen (Deckel 2,25 CPU-h, erwartet etwa 0,5 CPU-h)

| ID | Inhalt | CPU-Deckel |
|---|---|---:|
| D1 | Uhrenkalibrierung: ein Spinner über 600 s; davor und danach CLOCK_REALTIME, CLOCK_MONOTONIC, CLOCK_MONOTONIC_RAW, CLOCK_BOOTTIME, wait4-CPU des Kindes und Windows-Hostzeit; zusätzlich ein Sampler alle 30 s während Stufe 1 | 0,17 h |
| D2 | Wiederaufnahmeprobe an einer **Kopie** von `P--lambda-W-00` mit Obergrenze 3720 s | 0,05 h |
| D3 | Code-Kontrollen für PC und TE (siehe C.5) | 1,0 h |
| D5 | Ernte: alle OBSERVED-Zeilen der 192 Original-Archive schreibgeschützt lesen, unabhängig prüfen, strikt absteigen, Tiefe-2-Check der zehn besten W-Kandidaten | 1,0 h |

### B.2 Stufe 1 – vorab registrierter Vergleich, W-Ziel, 18 Worker

| Arm | Jobs | Start | Seeds | Horizont je Job | neue CPU |
|---|---|---|---|---|---:|
| **Pext** (Referenz P, algorithmisch unverändert) | `P--lambda-W-00 … 11` | Zustandsfortsetzung einer Kopie des Originalzustands | Original-Seeds | 3600 → 14.400 s kumulativ | 12 × 10.800 s = **36 h** |
| **PC** (neu) | 12 | dieselben 16 Gründer | `derive_seed(2026092104, ['lambda-compare', i])`, i = 0…11, identisch zu P_i | 14.400 s | 12 × 14.400 s = **48 h** |
| **TE** (neu) | 12 | dieselben 16 Gründer | wie PC | 14.400 s | **48 h** |

- Zwei neue Strategien plus begründete Referenz; B0 und T entfallen.
- Messpunkte 600 / 1800 / 3600 / 7200 / 10.800 / 14.400 s derselben fortgesetzten Trajektorie.
  Für Pext werden 7200 und 10.800 nachträglich aus `curves` abgeleitet, weil `task.json`
  hash-gebunden ist und nur 600/1800/3600 enthält; die Ableitung ist dieselbe Regel, die
  `evaluate()` schon benutzt.
- Queue-Reihenfolge verschränkt: PC_i, TE_i, Pext_i für i = 0…11.
- Simulation der Belegung [S]: Makespan 8,0 h, Auslastung 91,7 %, mittlere erlebte
  Gleichzeitigkeit 17,78 (Pext) gegen 16,92 (PC, TE). Damit erleben die Arme eine ähnliche
  SMT-Last; der Durchsatz wird zusätzlich als Kovariate protokolliert.
- Wiederaufnahme und Präfix-Replay zählen innerhalb der Jobbudgets.
- Die geschlossene Abschlussreserve der alten Pext-Endpunkte beträgt 3600 − 3595,03 ≈ 4,97 s
  je Job; sie wird als `closed_reserve_cpu_seconds` ausgewiesen und nicht als gerechnete CPU.
- Bereits verbrauchte 191,735 CPU-h plus 75,48 CPU-s Kontrollen erscheinen nirgends als
  neu verfügbare Zeit.

### B.3 Stufe 2 – erst nach Auswertung von Stufe 1 und erneuter Freigabe

| Arm | Inhalt | CPU |
|---|---|---:|
| R | Rekordfortsetzung mit unverändertem P, W-Ziel; 16 Gründer = beste kanonisch verschiedene (W,L1)-Klassen aus Ernte, Zeugen (einschließlich 2116) und Stufe-1-Ergebnissen; 6 neue Seeds `derive_seed(2026092104, ['lambda-record', i])` | 6 × 4 h = 24 h |
| TCx (optional) | TC/W, Seeds 00–02, 1 → 4 h, als Diskriminator gegen die 72-h-Variante | 3 × 3 h = 9 h |

Ein vorläufiger Pool liegt vor [S]: 56 kanonisch verschiedene Klassen allein aus den in Git
verfügbaren Graphen; die besten sechzehn reichen von (2121, 2440) bis (2145, 2428).
P-W-03 und P-W-08 teilen dabei dieselbe Klasse. Gleichstände werden über den
graph6-SHA256 aufgelöst. Die endgültige Liste entsteht deterministisch nach der Ernte.

### B.4 Budgetrechnung

```
Stufe 0   ≤   2,25 CPU-h   (Deckel; erwartet ≈ 0,5)
Stufe 1     132,00 CPU-h   = 36 (Pext) + 48 (PC) + 48 (TE)
------------------------------------------------------
jetzt beantragt ≤ 134,25 CPU-h
Stufe 2 später 33,00 CPU-h = 24 (R) + 9 (TCx, optional)
Planhorizont  ≤ 167,25 CPU-h
```

**Sparvariante ohne TE:** Pext + PC = 84 CPU-h, simulierter Makespan 7,0 h, Auslastung
jedoch nur 66,7 % [S].

---

## C. Mathematisch und algorithmisch präzise Regeln

Betroffene Dateien: `engine.py`, `archive.py`, `worker.py`, `config.json`, `controls.py`
sowie neu `continue.py`, `clockprobe.py`, `harvest.py`, `founders_R.json` in einem neuen
Paket `experiments/memetik/lambda_continue_0_3_0`. Geänderte Quellen sind eine neue
Versuchsversion; der Originallauf bleibt unberührt.

### C.1 PC – P mit vollständigem Dreierzyklus

Einzige Änderung gegenüber P:

```
# engine.Engine.batch
catalogue(rows, include_cycles = self.variant in ('TC','TE','PC'), guard)

# engine.Engine.step
if self.variant in ('B0','P','PC'): self.step_episode(guard)
else:                               self.step_tabu(guard)
```

- Jeder Perturbationsschritt zieht gleichverteilt aus der vollständigen eindeutigen
  Apex ∪ Pivot ∪ Dreierzyklus-Nachbarschaft.
- Der Abstieg nimmt den besten strikt besseren Nachbarn; Gleichstand nach stabiler
  Generatorreihenfolge (Apex, Pivot, Zyklus).
- `LOCAL_MIN_EXACT_AP` wird nur nach vollständig geprüfter Nachbarschaft gesetzt.
- Elternwahl, Perturbationslängen und -gewichte, Populationsgröße 16, `select` und
  Familienschutz bleiben unverändert.
- Gültigkeit: Der Zyklusgenerator liefert nur Züge aus dem bereits geprüften
  Kompatibilitätsdigraphen; jede Übernahme läuft zusätzlich durch den unabhängigen
  Verifier (`make_item` → `checked`).
- Inverse: Jeder Zug ist ein Tausch gleich vieler gelöschter und eingefügter Kanten; die
  Umkehrung ist der Zug mit vertauschten Mengen, in P ohne Sperre erreichbar.
- Begründung: Der einzige von mir gefundene Weg unter W=2121 benötigt einen Dreierzyklus [S],
  und TC schlägt T bei gleichem Budget 10/0/2 [S]. Ob der größere Katalog auch im
  langfristig besseren Rahmen hilft, ist genau die offene Frage.

### C.2 TE – TC mit Elite-Restart

```
S_TE = 200                  # statt 2000 akzeptierte Schritte ohne aktiven Jobrekord
elite  = die 8 besten kanonisch verschiedenen Klassen des Jobarchivs nach key(·,target),
         Gleichstand nach graph6-SHA256; im Checkpoint gehalten und bei jedem
         archive.put inkrementell aktualisiert (kein SQL-Scan im Suchpfad)

restart:
    u = rng.random()
    if u < 0.75: parent = rng.choice(elite)          # Intensivierung
    else:        parent = gleichverteilte Archivklasse   # unveränderte Exploration
    walk = rng.randint(5, 8); Tabuliste leer; stagnant = 0
```

- Start, Katalog, Tenure 7–15, Aspiration, deterministische Verfallsvorstellung bei
  vollständig tabuisierten Katalogen und die Rekordbeobachtung bleiben unverändert.
- RNG-Verbrauchsreihenfolge fest: `random()`, dann `choice`/`randrange`, dann `randint`.
- Begründung für S = 200: Der Pfad verlässt die gute Region binnen etwa 60 Iterationen um
  mehr als 60 W-Einheiten [S]; S = 200 lässt das Zehnfache der beobachteten Driftdauer zu.
  Der Wert ist vorab festgelegt und wird nicht anhand derselben Seeds nachjustiert.
- Erwartete Wirkung [H]: etwa 15–18 Restarts pro Vierstundenjob statt vier, mit Start
  jeweils nahe der Elite.

### C.3 Zustandserhaltende Fortsetzung Pext ohne Eingriff in den Originallauf

1. Neues Verzeichnis `ryzen_lambda_continue_030_<datum>` neben dem Originallauf.
2. `bundle/` des Originals kopieren und gegen `fingerprint.json` hashprüfen.
3. Für die zwölf Jobs `task.json`, `receipt.json`, `result.json`, `checkpoint.json` und
   `archive.sqlite` byteweise kopieren; alle SHA256 ins Fortsetzungsmanifest.
4. Im neuen Root `budget.json` mit `per_job_cpu_seconds = 14400`, Ledger-Revision 1 mit
   Begründung, Vorgänger-Snapshot-Hashes.
5. Pext-Worker werden mit dem **unveränderten 0.2.0-`worker.py` aus der Bundle-Kopie**
   gestartet; der Controller kennt den Worker-Pfad je Job aus dem Manifest.
6. Die Schutzprüfungen des Workers bleiben aktiv: `task_sha256`, `result_sha256`,
   `checkpoint_sha256`, `base = max(budget_cpu_seconds, endpoint_cpu_seconds)`.
7. Das vorhandene `extend` wird nicht aufgerufen.
8. Der Originallauf wird nur gelesen; nichts wird gelöscht oder überschrieben.

### C.4 Ernte der Archivrekorde (D5)

```
for db in original/tasks/*/archive.sqlite:
    connect('file:' + db + '?mode=ro&immutable=1', uri=True)   # keine WAL-/SHM-Dateien
    SELECT target, cpu, value, role FROM records WHERE role = 'OBSERVED'
Deduplizierung nach class
je Kandidat:
    unabhängige Prüfung (n=99, Grad 14, CN=1 je Kante, fünf Scores)
    strikter Bestabstieg im vollständigen Katalog je Ziel bis zum lokalen Minimum
    zusätzlich Tiefe-2-Zensus für die zehn besten W-Kandidaten
Ausgabe HARVEST.json: Herkunft (Job, CPU, Rolle), Kategorie 3, alle Züge explizit
```

Die Ernte-CPU wird getrennt verbucht. Ergebnisse gehen nie rückwirkend in Messpunkte ein.

### C.5 Positive und negative Kontrollen

**Positiv**

- PC übernimmt in einer 120-s-Probe mindestens einen `cycle3`-Zug.
- TE löst in einer Probe über 500 Iterationen mindestens einen Elite-Restart aus, und die
  Restartquelle liegt nachweislich in `elite`.
- Die bestehende Erfolgsfallkontrolle über srg(9,4,1,2) mit expliziten Testparametern bleibt.

**Differenziell**

- PC mit leerem Zyklusgenerator (Testmonkeypatch) muss P über 20 Episoden byteidentisch
  reproduzieren, inklusive RNG-Zustand und Endgraph.
- TE mit S = 2000 und Eliteanteil 0 muss TC über 300 Iterationen byteidentisch reproduzieren.

**Negativ**

- Ein injizierter ungültiger Zyklus muss in `apply_move` oder `checked` eine Ausnahme auslösen.
- Ein manipulierter Checkpoint in der Pext-Kopie muss „Changed or corrupt checkpoint“ auslösen.
- Ein manipuliertes `result.json` muss die Receipt-Prüfung auslösen.

**D2-Abnahmekriterien**

- Die Messpunkte 600/1800/3600 der Kopie bleiben unverändert.
- `replayed_moves` wächst, die Sitzungssumme stimmt mit `cpu_seconds` überein,
  `closed_reserve_cpu_seconds` beträgt etwa 4,97 s.

---

## D. Vorab festgelegte Auswertung

**Primärer Endpunkt:** aktives (W, L1) im W-Job nach 14.400 Budget-CPU-Sekunden.
**Vergleichseinheit:** der Job, gepaart nach Seedindex; zwölf Paare je Kontrast.
**Primäre Kontraste:** PC gegen P und TE gegen P.

**Getrennt berichtet**

- Paarbilanzen bei 3600 s (beide Arme ohne Wiederaufnahme), 7200, 10.800 und 14.400 s.
- Streuung: Minimum, Median, Maximum je Arm und Messpunkt; alle Paarwerte bleiben sichtbar.
- Zeitverlauf: CPU bis zur letzten aktiven Verbesserung, Anzahl Verbesserungen je Intervall.
- Einzelrekorde und beobachtete Nachbarn getrennt von aktiven Endpunkten; beobachtete
  Rekorde gehen nie in die Paarstatistik ein.
- Durchsatzkovariate: Episoden bzw. Iterationen je CPU-Sekunde, Katalogeingänge je Zug.
- Anzahl verschiedener Endklassen je Arm (Hinweis auf Pseudoreplikation).

Zwölf Seeds liefern keine Signifikanz; die Schwellen unten sind deskriptiv.

| Ergebnis | Entscheidung |
|---|---|
| Arm X ∈ {PC, TE}: ≥ 8 Siege und ≤ 2 Niederlagen gegen P bei 14.400 s | X wird Arbeitsverfahren, auch für R |
| P: ≥ 8 Siege gegen X | X verworfen |
| sonst | **P bleibt Referenz ohne Zusatzmechanismus**; X wird nicht verlängert |
| ≥ 6/12 Pext-Jobs mit aktiver Verbesserung in (10.800, 14.400] oder Median-W sinkt zwischen 7200 und 14.400 um ≥ 3 | Verlängerung des besten Arms auf 8 h vorschlagen (+48 CPU-h je 12 Jobs) |
| ≤ 2/12 Pext-Jobs verbessern sich im letzten Intervall | Horizontplateau für dieses Verfahren; nächster Schritt Diversifikation statt mehr Zeit |
| TCx gelaufen und ≥ 2/3 Seeds unter W = 2141 | meine Drift-Hypothese ist geschwächt; volle TC-Fortsetzung neu bewerten |
| irgendein Kandidat mit sämtlichen Residuen null | unabhängige Prüfung, Zeuge sichern, kontrollierter Stopp eigener Worker |

Die primäre Zielfunktion wird nicht nachträglich geändert. Ein Plateau in einem Ziel gilt
nicht als Beweis fehlender späterer Chancen.

---

## E. Umsetzung, Ressourcen, Risiken

### E.1 Operative Reihenfolge

1. Freigabe des Budgets von ≤ 134,25 CPU-h für Stufe 0 und 1.
2. D1-Uhrdiagnose, Auswertung nach der Tabelle in E.2.
3. Paket 0.3.0 schreiben, Kontrollen D3 laufen lassen, Ergebnis dokumentieren.
4. D2-Wiederaufnahmeprobe an der Kopie, dann Ernte D5.
5. Fortsetzungsverzeichnis anlegen (`prepare`-Analogon), Preflight mit Hostwächtern.
6. Stufe 1 starten, Sampler mitlaufen lassen, Status alle zehn Minuten.
7. Auswertung nach D, Abgleich mit der Codex-Ausarbeitung.
8. Entscheidung über Stufe 2.

Je Rückmeldung wird genau ein ausführbarer Bash-Einzeiler gegeben.

### E.2 Zeitmessung, Entscheidungslogik, ETA

Die Diagnose vergleicht mindestens: UTC/CLOCK_REALTIME, CLOCK_MONOTONIC,
CLOCK_MONOTONIC_RAW, CLOCK_BOOTTIME, Prozess-CPU über `wait4` und eine unabhängige
Hostzeit über die Windows-Interop, zusätzlich die aktive Clocksource.

| Befund aus D1 | Folge |
|---|---|
| Hostzeit ≈ REALTIME, MONOTONIC läuft langsamer | monotone Uhr ist die Abweichung; ETA aus REALTIME; Budget unverändert; starten |
| Hostzeit ≈ MONOTONIC und Spinner-CPU > Hostdauer | rusage-Sekunden sind Kernel-Sekunden mit Faktor; Budget bleibt armübergreifend fair, ETA und absolute CPU-Stunden mit ausgewiesenem Faktor berichten; starten |
| alle Uhren konsistent, Anomalie nicht reproduzierbar | Sampler während Stufe 1 mitlaufen lassen; starten |
| Sprünge über 5 s oder CPU > Hostdauer + 2 % | nicht starten, erst diagnostizieren |

Was welche Zeitbasis steuert: das Ergebnisbudget steuert ausschließlich `wait4`-CPU
(Receipts, `budget.json`); die ETA und die Statusintervalle steuerten bisher
CLOCK_MONOTONIC und werden auf die nach D1 geprüfte Uhr umgestellt; Checkpoint-Intervalle
bleiben Wanduhr und sind unkritisch.

**Vorsichtige ETA:** Stufe 0 etwa 1 bis 1,5 h real. Stufe 1 **8 h 15 min bis 9 h**
(Simulation 8,0 h, plus rund 1 % Overhead analog zum Originallauf, plus Replay und
Wächterprüfungen). Fällt D1 zugunsten der zweiten Zeile aus, sind es real etwa 7,5 h.
Das ist eine Budget-ETA, keine Lösungs-ETA.

### E.3 Ressourcen

- 18 Worker, je 1 GiB Adressraum: im Originallauf ausreichend; PC und TE liegen im
  Speicherprofil zwischen P und TC [H]. Neu protokolliert werden `ru_maxrss` je Receipt
  und die Archivgröße je Job.
- Gruppen-RAM 36 GiB, freie RAM-Reserve 6 GiB, 20 GiB freier Linux-Platz, 50 GiB frei auf
  dem tatsächlich ermittelten Windows-VHDX-Trägervolumen: Ich halte diese Regeln für
  geeignet und schlage **keine** Änderung vor. Der frühere Ausfall war physischer
  Windows-Platzmangel; die Prüfung des Trägervolumens bleibt zwingend.
- Kein fester 64-Klassen-Deckel, kein pauschaler 2-GiB-Lauf-Deckel, kein
  600-CPU-s-Controllerstopp: bleibt so.
- Archivwachstum: 36 Jobs über 4 h; Größenordnung aus dem Originallauf grob skaliert,
  die unkomprimierten Archivgrößen sind mir jedoch nicht bekannt [F]. Vor dem Start wird
  der freie Platz gemessen und der Wächter greift ohnehin.
- Erhalten bleiben: unabhängige Kandidatenprüfung, Lösungserkennung bei sämtlichen
  Residuen null, Zeugensicherung, kontrollierter Stopp nur eigener Kinder, faire
  CPU-Abrechnung, keine Office-Pfade, keine fremden Prozesse.

### E.4 Offene Risiken

1. **SMT-Last:** Eine CPU-Sekunde ist bei 18 Workern auf 12 Kernen nicht konstant viel
   Arbeit. Gemildert durch verschränkte Queue (erlebte Gleichzeitigkeit 17,8 gegen 16,9)
   und durch die Durchsatzkovariate. Nicht vollständig eliminierbar.
2. **Ungeklärte Uhr:** Bis D1 bleibt der absolute Bezug der CPU-Stunden offen. Der
   Armvergleich ist davon nicht betroffen.
3. **Wiederaufnahme-Asymmetrie:** Pext zahlt Replaykosten, PC und TE nicht. Der Betrag
   wird je Job aus `replayed_moves` und der Sitzungsdifferenz berichtet; die Paarbilanz
   bei 3600 s ist davon frei.
4. **Gründer-Monokultur:** Alle Arme starten in derselben HoG-Region. Aussagen gelten
   nur dort.
5. **Wiederverwendung derselben zwölf Seeds** für PC und TE: Die neuen Arme wurden nicht
   an diesen Ergebnissen justiert, aber Gründer und Seedindizes sind dieselben wie bisher.
6. **Meine Tabu-Sonde ist eine Nachbildung**, keine echte Pfadreproduktion des Workers.
   Sie trifft den berichteten Bestwert und die Iteration in allen zwölf TC-Seeds sowie in
   acht von zwölf T-Seeds, deren letzte Verbesserung im simulierten Fenster liegt; die
   übrigen vier verbessern sich laut Receipts später als simuliert.
7. **Dreierzyklus und inkrementelles Scoring** stammen in meinen Sonden aus dem
   Projektcode. Unabhängig nachgebaut habe ich Decoder, Gültigkeit, Scores, Apex und Pivot.

### E.5 Fehlende Daten und gezielte Anforderung

Nicht in Git und für folgende Aussagen nötig [F]:

- `tasks/*/result.json` mit `histogram` (`tabu_observed_path_maxima`, `tabu_path_length`,
  `tabu_isomorphic_return`, `observed_path_maxima`), `evaluated_moves`, `curves`,
  `continuing_path` – nötig, um meine Drift-Hypothese an echten Pfaden statt an der
  Simulation zu prüfen. Minimal ausreichend: die 24 Dateien der T- und TC-W-Jobs.
- Die OBSERVED-Zeilen aller `archive.sqlite` – nötig für die Ernte und den endgültigen
  R-Gründerpool.
- `comparison_timing.json`, `status.json` und `controller.log` – nötig, um die
  Zeitabweichung über die Statusintervalle zu lokalisieren.
- Unkomprimierte Archivgrößen und Speicher-Höchstwerte je Worker – nötig für eine
  belastbare Platz- und RAM-Prognose.

Ohne diese Dateien bleibt die Planung wie oben gültig; nur die genannten Einzelaussagen
sind dann Simulation oder Hypothese statt Rohdatenbefund.

### E.6 Was ich selbst ausgeführt habe

Alles in meiner eigenen Umgebung, nichts auf Ryzen, kein Suchlauf gestartet.
Gesamtaufwand etwa eine CPU-Stunde. Programme und Ergebnisse liegen im ZIP.

1. `indep.py` – eigener graph6-Decoder, eigene Residuen, Scores und λ-Gültigkeit
   (Grad 14, CN = 1 je Kante, 231 Dreiecke, sieben je Knoten), ohne Projektcode.
2. `check_all.py` – 43 verschiedene graph6 aus allen 192 Endbesten, den vier beobachteten
   Zielrekorden und den Zensusgraphen: alle gültig, alle Scores stimmen. Zusätzlich
   19 Zensus-Zeugen: gültig, Scores stimmen, und die angegebenen Züge erzeugen genau den
   angegebenen Graphen. Null Abweichungen.
3. `neigh.py` + `run_census.py` – Brute-Force-Apex und -Pivot nach Definition mit
   vollständiger lokaler λ-Prüfung an allen sechs Zensusgraphen: Zuganzahlen und
   Verbesserungszahlen je Ziel stimmen exakt mit `RECORD_CENSUS.json` überein.
4. `paired.py` – Paarbilanzen, Messpunkte, Mediane, Restarts, Iterationen, Archivklassen,
   Operatorhäufigkeiten und Zeitpunkte der letzten Verbesserung aus `ENDPOINTS.json`
   neu berechnet; Übereinstimmung mit den veröffentlichten Bilanzen.
5. `timing.py` – Makespan-Schranke aus den Receipts gegen UTC und monotone Dauer.
6. `probe_descent.py` – Bestabstieg im T- und TC-Katalog ab dem jeweils gewählten
   Startgründer, mit Gleichstandsprotokoll.
7. `probe_tabu.py` – getreue Nachbildung von `step_tabu` für alle zwölf echten Seeds
   (TC/W 40 Iterationen, T/W 60 Iterationen) und für Seed 0 über 250 Iterationen.
8. `probe_founders.py` – Bestabstieg im TC-Katalog ab allen 16 Gründern.
9. `lineage_distance.py` – beschriftete Kantenabstände zwischen Gründern und Rekorden.
10. `depth2.py` – Tiefe-2-Zensus an F=2836, W=2121, W=2130 und W=2141.
11. `witness_2116.py` – expliziter, unabhängig geprüfter Zwei-Schritt-Zeuge W=2116.
12. `record_pool.py` – vorläufiger R-Gründerpool mit pynauty-Zertifikaten.
13. `schedule.py` – Listen-Scheduling-Simulation der Stufen und Varianten.

**Ausdrücklich nicht getan:** kein Zugriff auf das Originalarchiv, keine Prüfung der
1.490.795 Archivzeilen, keine Neuberechnung der Kanonisierungszertifikate des Laufs,
keine vollständige Pfadreproduktion, keine erfundenen Zyklus-, BFS- oder Tabutrajektorien,
kein Start eines Laufs auf Ryzen oder Office, keine Änderung am vorhandenen Laufbundle.

### E.7 Einziger Bash-Einzeiler, erst nach Freigabe von D1

```bash
python3 -c "import time,os,subprocess as s,json;t=lambda:{k:time.clock_gettime(getattr(time,'CLOCK_'+k)) for k in ('REALTIME','MONOTONIC','MONOTONIC_RAW','BOOTTIME')};h=lambda:s.run(['/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command','[DateTime]::UtcNow.ToString(\"o\")'],capture_output=True,text=True).stdout.strip();a,ha=t(),h();p=s.Popen(['python3','-c','import time\ne=time.monotonic()+600\nwhile time.monotonic()<e: pass']);_,_,u=os.wait4(p.pid,0);b,hb=t(),h();print(json.dumps({'before':a,'host_before':ha,'after':b,'host_after':hb,'child_cpu':u.ru_utime+u.ru_stime,'clocksource':open('/sys/devices/system/clocksource/clocksource0/current_clocksource').read().strip()}))"
```

Erwartung bei gesunder Zeitbasis: `child_cpu` ≈ Hostdifferenz ≈ REALTIME-Differenz ≈
MONOTONIC-Differenz, jeweils innerhalb von etwa 1 %.
