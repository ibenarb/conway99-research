# O3-BREADTH-1 — Semantik des Grundmodells A

**Stand:** 6. September 2026, Revision 2  
**Zweck:** explizite Spezifikation dessen, was Layer `A` im Breadth-Scout mathematisch kodiert — und was nicht.

## Kurzfassung

Layer `A` ist **kein 99-Knoten-SRG-Modell**. Es ist ein exaktes **33-Knoten-Quotienten-Feasibility-Modell** für einen bereits fest gewählten fixpunktfreien Ordnung-3-Typ `(tau, cycle_type)`.

Für festes `tau` und einen fest kanonisch gelabelten 2-Faktor `L` sucht A nach einer einfachen 0/1-Matrix `S`, so dass

`Q = 2 D_T + S + 2 L`

die vollständigen Quotientenbedingungen

`Q 1 = 14 1`

und

`Q^2 + Q = 12 I + 6 J`

erfüllt. Zusätzlich enthält A für jede `C3`-Komponente von `L` die Exact-One-Klauseln aus Lemma B. Diese sind theorem-derived redundant: sie sollen Propagation verstärken, aber keine mathematisch zulässige Quotientenlösung entfernen.

Ein `UNSAT` von A schließt daher den betreffenden **Quotiententyp** aus. Ein `SAT` von A liefert zunächst nur eine zulässige Quotientenmatrix `Q`; es ist **noch kein** 99-Knoten-`srg(99,14,1,2)` und insbesondere kein Liftbeweis.

---

## 1. Feste Daten je Instanz

`src/breadth1/o3_generic_core.py` setzt `n=33`.

Für eine Instanz werden fest gewählt:

- `tau` in der jeweils mathematisch zulässigen Menge;
- `T={0,...,tau-1}` als kanonische Menge der Dreieckorbits (WLOG per Relabelling-Lemma);
- `U={0,...,32}\T`;
- ein kanonisch gelabelter einfacher 2-Faktor `L` auf `U` mit dem vorgegebenen `cycle_type`;
- damit die Gewicht-2-Diagonale `2D_T` und alle Gewicht-2-Kanten `2L`.

`L` besitzt genau `|U|=33-tau` Kanten.

**Aktualisierung 2026-09-06:** Der neue elementare Satz `tau ≡ 0 (mod 3)` reduziert die frühere Spurmenge `{6,13,20,27}` auf `{6,27}`. Siehe `docs/breadth1/O3_tau_mod3_theorem.md`. Historische Scout-Artefakte über alle vier tau-Werte bleiben unverändert.

---

## 2. Primäre Unbekannte

Für jedes ungeordnete Paar `{i,j}` mit `i<j`, das **keine** `L`-Kante ist, gibt es eine boolesche Variable

`s_ij in {0,1}`.

Sie entscheidet, ob `{i,j}` eine einfache `S`-Kante ist.

Damit ist automatisch

- `S` symmetrisch;
- `S` hat Null-Diagonale;
- `S` und `L` sind kantendisjunkt.

Die Zahl primärer `S`-Variablen ist

`C(33,2) - (33-tau) = 495 + tau`,

also insbesondere

- 501 bei `tau=6`,
- 522 bei `tau=27`.

Die ungefähr 120k CNF-Variablen der realen Instanzen sind daher überwiegend **Hilfsvariablen**, nicht 120k unabhängige Graphentscheidungen.

---

## 3. Produkt-Hilfsvariablen

Für die quadratischen Terme `(S^2)_ij` verwendet der Core Produktterme zu Paaren von Kandidatenkanten. Semantisch steht ein solcher Hilfsterm für

`p_{(i,k),(k,j)} = s_ik * s_kj`

bzw. boolesch

`p <-> (s_ik AND s_kj)`.

Diese Terme linearisieren die quadratischen Beiträge in den Paargleichungen. Die Hilfsvariablen ändern den mathematischen Lösungsraum auf den `s_ij` nicht.

---

## 4. Gradgleichungen

A erzwingt

`deg_S(i)=12` für `i in T`,

`deg_S(i)=10` für `i in U`.

Bei festem `D_T` und `L` haben diese Gleichungen zwei Bedeutungen zugleich.

### Zeilensumme

Für `i in T`:

`sum_j Q_ij = 2 + 12 = 14`.

Für `i in U` besitzt `i` genau zwei `L`-Nachbarn, beide mit Gewicht 2:

`sum_j Q_ij = 2*2 + 10 = 14`.

Damit gilt `Q 1 = 14 1`.

### Diagonale von `Q^2+Q`

Für `i in T`:

`(Q^2+Q)_ii = 2^2 + 12*1^2 + 2 = 18`.

Für `i in U`:

`(Q^2+Q)_ii = 2*2^2 + 10*1^2 = 18`.

Da `(12I+6J)_ii=18`, kodieren die Gradgleichungen zugleich die vollständigen Diagonalgleichungen der Quotientenidentität.

---

## 5. Alle 528 Off-Diagonal-Paargleichungen

Für **jedes** ungeordnete Paar `i<j` — insgesamt `C(33,2)=528` — erzeugt `o3_generic_core.py` eine exakte normalisierte Gleichung.

Sie ist algebraisch äquivalent zu

`(Q^2+Q)_ij = 6`.

In der dokumentierten Form lautet sie

`(S^2)_ij + 2(SL+LS)_ij + 4(L^2)_ij + (d_i+d_j+1)S_ij + 2(d_i+d_j+1)L_ij = 6`,

mit

`d_i = 2 [i in T]`.

Der Core verschiebt die ausschließlich von `L,T` abhängigen festen Terme auf die rechte Seite und repräsentiert die `S^2`-Terme durch die Produktvariablen.

`src/breadth1/o3_generic_core_regression.py` prüft diese Normalisierung unabhängig durch direkte ganzzahlige Matrixmultiplikation für alle vier historisch getesteten `tau`-Klassen.

Zusammen mit Abschnitt 4 kodiert A damit die **gesamte** Matrixidentität

`Q^2+Q=12I+6J`,

nicht nur ausgewählte lokale Ausschnitte.

---

## 6. Lemma-B-Exact-One für jede C3-Komponente

`src/breadth1/o3_abc_encode.py` baut A zunächst aus dem historischen Base-Core mit `lemma_triangle_eo=False` und fügt dann explizit `add_triangle_exactly_one(...)` hinzu.

Für jede `C3`-Komponente `C={a,b,c}` von `L` und jeden der 30 Quotientenknoten `w` außerhalb von `C` gilt:

`S_wa + S_wb + S_wc = 1`.

CNF-seitig ist dies eine ALO-Klausel plus drei paarweise AMO-Klauseln.

Es entstehen exakt

`30 * (# C3-Komponenten)`

Exact-One-Gruppen.

Wichtig für die Semantik: Lemma B ist aus den Quotientengleichungen und den S-Graden hergeleitet. Diese EO-Gruppen sind daher **redundante notwendige Konsequenzen** des Base-Modells; sie sollen den Solver stärken, nicht den mathematischen Lösungsraum verkleinern.

---

## 7. Was B gegenüber A hinzufügt — und was nicht

Layer B ist

`A + generic cycle-local pair-budget inequalities for every C_m, m>=5`.

Diese Ungleichungen entstehen aus den bereits in A vorhandenen **exakten** Paargleichungen, indem ausschließlich nichtnegative Terme außerhalb der betrachteten Zykluskomponente weggelassen werden. Daher gilt mathematisch

`A => B-extra`,

und somit haben A und B **denselben mathematischen Lösungsraum**.

B ist also keine stärkere mathematische Existenzbedingung, sondern ausschließlich eine **redundante Propagations-/Kodierungsschicht**. Der matched-seed A/B-Scout ist deshalb als Experiment zur Solverwirkung redundanter Klauseln zu interpretieren, nicht als Vergleich zweier mathematisch verschieden starker Modelle.

Bei `(3^9)` gibt es keine `m>=5`-Komponente; dort waren A und B im Hauptlauf byte-identische CNFs und erzeugten exakt identische Solverstatistiken. Beim bekannten Kontrolltyp `(6,3^7)` war B mit gleichem Seed/CPU deutlich schneller als A; das ist ein einzelnes Solver-Performance-Signal, kein neuer mathematischer Ausschluss und für sich allein kein allgemeiner Strategiebeweis.

---

## 8. Was A ausdrücklich NICHT kodiert

A kodiert **nicht**:

1. einen vollständigen 99x99-Adjazenzgraphen;
2. die konkreten 3x3-Blöcke / Phasen eines Lifts zwischen Ordnung-3-Orbits;
3. den Nachweis, dass eine zulässige Quotientenmatrix tatsächlich zu einem `srg(99,14,1,2)` liftet;
4. Automorphismen anderer Ordnungen oder den asymmetrischen Fall;
5. die zusätzliche Polytop-Hypothese;
6. die memetische `1+14+84`-Konstruktion;
7. zusätzliche Symmetry-Breaking-Klauseln für die Automorphismengruppe des festen `(T,L)`-Templates, soweit nicht bereits die kanonische Wahl von `T` und `L` als WLOG-Vorreduktion wirkt.

Daraus folgt die entscheidende logische Richtung:

`hypothetischer SRG mit diesem FPF-O3-Typ`

`=> zulässiger Quotient Q`

`=> SAT von A`.

Daher ist

`UNSAT(A) => kein SRG mit diesem Quotiententyp`.

Aber im Allgemeinen gilt **nicht** die Umkehrung

`SAT(A) => existierender 99-Knoten-SRG`.

---

## 9. Provenienz — Lücke geschlossen am 2026-09-06

Der Produktionsrunner `src/breadth1/o3_ab_matched_scout_runner.py` lud den historischen CNF-Encoder im tatsächlich ausgeführten Lauf aus dem lokalen FULLCERT-Freeze:

`O3_TASK03_FULLCERT_1.1_20260902/SOURCE/context/qsat/encode.py`.

Der komplette historische `qsat`-Quellbaum aus diesem unveränderten Freeze ist jetzt content-exakt im Repository vendored unter

`vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat/`.

Die Übertragung wurde über Dateiinhalts-Hashes auditiert. Insbesondere gilt für den tatsächlichen Base-Encoder:

`SHA256(encode.py) = 131cf8aea1fbf6eeb76e363357b55498d084f109ec93b42c51d0d0c6abdbe6f1`.

Die SHA256-Werte und Bytegrößen aller zehn Dateien stehen in

`vendor/O3_TASK03_FULLCERT_1.1_20260902/PROVENANCE.json`.

Zusätzlich wurden die Git-Blob-SHA1-Werte aller zehn vendorten Dateien gegen die aus dem hochgeladenen Freeze-Archiv lokal berechneten Werte geprüft; **10/10 stimmen exakt**.

Das Transferarchiv hatte SHA256

`85d331f6b45c79d166d45e784f8ea7dd722becceae73f2ff2f474b56f260e7b0`.

### Wichtige Implementierungsnuance

Der historische `encode.py` enthält selbst eine `triangle_components`-Hilfsfunktion mit hart codiertem Start `p=6`; sie stammt aus dem tau=6-Task03-Kontext. Im all-tau Breadth-Scout wird diese historische Triangle-Funktion **nicht** benutzt: `src/breadth1/o3_abc_encode.py` ruft

`legacy_encode.cnf_from_core(core, lemma_triangle_eo=False)`

auf und fügt die tau-generische C3-Exact-One-Schicht anschließend selbst hinzu.

Für einen externen Breadth-Rerun kann der historische lokale Pfad ersetzt werden durch

`--legacy-encode vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat/encode.py`.

Damit ist die zuvor offene Encoder-Provenienz-/Reproduzierbarkeitslücke für den Breadth-Scout geschlossen.
