# Memetischer H-Faser-Untersuchungspfad — Stand 2026-10-04

## Zweck

Dieses Dokument friert den Untersuchungspfad ein, der aus der memetischen \(\lambda\)-Suche und dem HealthyPrefix/Completion-Problem in eine strukturelle Untersuchung der exakten H-Faser geführt hat.

Leitfrage war zuletzt nicht mehr nur, ob ein bestimmter memetischer Operator \(W\) senkt, sondern:

> Welche exakten lokalen Bewegungen existieren überhaupt innerhalb der linearen H-Faser \(AP=M\), wie klein können sie sein, und wie stark ist die lokale Faser um praktisch relevante H-Zustände verbunden?

Die Resultate sind für die Fortsetzung des Augmentation-Zweiges relevant, weil sie zeigen, dass lokale exakte H-Nachbarschaften sehr dünn oder sogar bis zu beträchtlichem Radius leer sein können. Das ist kein Nicht-Existenzresultat für globale H-Zustände und kein Conway-99-Ausschluss.

---

## 1. Ausgangspunkt: HealthyPrefix / Completion

### HealthyPrefix 1.0.2

Der Pilot bestätigte den bereits sichtbaren Engpass:

- 14 EXTEND-Versuche;
- alle 14 endeten UNKNOWN;
- 0 SAT, 0 INFEASIBLE;
- 0 neue Präfixe, Tiefe blieb 0;
- pro Job wurden 96 Row-Kandidaten erzeugt;
- 56 Completion-Versuche lagen jeweils bei ungefähr 291–292 s und endeten UNKNOWN.

Die Row-Enumeration war billig; der Completion-Oracle war der Flaschenhals.

### CP-SAT Completion Gate 1.0.0

Drei garantiert erfüllbare Kontrollen wurden getestet:

- A: geshuffelter Root-Zustand — UNKNOWN nach ca. 620.0 s;
- B: eine bekannte feste Zeile — OPTIMAL/SAT nach ca. 381.3 s;
- C: gepflanzter 71-Vertex-Residualfall — OPTIMAL/SAT nach ca. 253.9 s.

Ergebnis: 2/3 SAT, 1/3 UNKNOWN. CP-SAT ist als Completer prinzipiell brauchbar, aber in dieser Form nicht robust und billig genug für einen breiten HealthyPrefix-Hauptlauf.

Strategische Folge: HealthyPrefix wurde eingefroren; CP-SAT bleibt ein möglicher Makro-Completer oder Kontrolloracle, aber nicht der primäre lokale Suchmotor.

---

## 2. H-DEFECT 0.1.x: lokale Defekt-Navigation

Das H-Modell hat 84 Outer-Vertices. Für einen exakten H-Zustand gilt:

- binäre symmetrische H-Adjazenz;
- H-Grad 12;
- feste Border-Margen \(AP=M\).

Bei erhaltenem Grad hat jede Defektzeile \(R=AP-M\) Zeilensumme 0. Ein Defekt mit genau einer \(\pm1\)-Margin ist daher strukturell unmöglich.

Als elementarer defekter Halbzug wurde ein undirektionaler grad-erhaltender 2-switch untersucht.

### H-DEFECT 0.1.2

Vier H-lineare Zustände:

- HealthyPrefix root witness 1;
- HealthyPrefix root witness 2;
- cand_A;
- cand_B.

Je Zustand wurden ungefähr 186k–190k gültige 2-switches untersucht.

Bestes elementares Defektprofil war in allen vier Fällen:

- 4 betroffene H-Zeilen;
- Defekt-Support 8;
- \(L_1=8\);
- \(L_\infty=1\);
- Zeilensummen 0.

Es wurde kein nichttrivialer Zwei-Schritt-Rückschluss in die exakte H-Faser gefunden. Der naive Versuch, einen exakten Move als zwei 2-switches zu realisieren, ist zudem strukturell ausgeschlossen: die einzige Zwei-Schritt-Kompensation ist im Wesentlichen die triviale Inversion.

Die Paar-Differenzen aller vier H-Zustände erfüllten \(\Delta P=0\), wie für Zustände derselben linearen H-Faser erwartet.

---

## 3. MINIMAL-H-CIRCUIT 0.2.0–0.2.3: untere Schranken

Es wurden die kleinen möglichen exakten Kernelmoves vollständig und solverfrei ausgeschlossen.

### 0.2.0 — 6 Vertices / 12 Kanten

- 12,180 Support/Matching-Kandidaten;
- zwei unabhängige Rekonstruktionen;
- XOR-Konsistenz und exhaustive lokale Vorzeichenprüfung;
- 0 Treffer.

Ergebnis: kein exakter nichttrivialer H-Kernelmove mit Support 6 / 12 geänderten Kanten.

### 0.2.1 — 7 Vertices / 14 Kanten

- 351,120 zulässige 7-Sets nach lokaler Balance;
- vollständiger notwendiger Neighborhood-Filter;
- 0 Überlebende.

### 0.2.2 — 7 Vertices / 15 Kanten

Einzige mögliche Gradfolge: \([6,4,4,4,4,4,4]\).

- 125,300 balancierte 6-Sets;
- 351,120 lokal zulässige Supportkandidaten;
- zwei unabhängige Vorzeichen-/GF(2)-Checker;
- 0 Treffer.

### 0.2.3 — 7 Vertices / 16 Kanten

Einzige mögliche Gradfolge: \([6,6,4,4,4,4,4]\).

Zwei notwendige balancierte 6-Sets müssten eine gemeinsame 5er-Teilmenge besitzen. Die vollständige Bucketsuche ergab:

- 751,800 5-subset-Einträge;
- 0 passende Bucket-Paare;
- 0 Kandidaten.

### Konsequenz

Jeder nichttriviale exakte H-Kernelmove erfüllt

\[
|\mathrm{supp}_V(\Delta)|\ge 8,\qquad
|\mathrm{supp}_E(\Delta)|\ge 16.
\]

---

## 4. Schärfe und vollständige Klassifikation der 8/16-Moves

Ein realer alter Omega-`4x4`-Move auf root witness 1 wurde geprüft:

- 8 gelöschte + 8 hinzugefügte H-Kanten;
- 16 geänderte H-Kanten;
- 8 betroffene H-Vertices;
- exakte H-Margen bleiben erhalten.

Die Schranke 8/16 ist also scharf.

### MINIMAL-H-CIRCUIT 0.3.0

Die vollständige Klassifikation aller minimalen 8/16-Circuits ergab:

- 2,121 balancierte Viererrelationen;
- unabhängiger alter Omega-`signed_vectors(4)`-Katalog stimmt exakt mit diesen 2,121 Relationen überein;
- 19,355 beschriftete 4-reguläre Supportgraphen auf 8 Vertices;
- 3,395 überleben die notwendige Schnittgeometrie;
- genau drei abstrakte Supportfamilien:
  - \(K_{4,4}\): 35 Beschriftungen;
  - Cube-complement: 840;
  - Wagner-complement: 2,520.
- Für die beiden Nicht-\(K_{4,4}\)-Familien liefern zwei unabhängige vollständige CSP-Verfahren jeweils 0 H-Labelungen.

Ergebnis:

> **ALL_MINIMAL_8_16_CIRCUITS_ARE_OMEGA_4X4**

Der alte Omega-`4x4`-Operator ist nicht nur minimal, sondern die vollständige Klasse aller minimalen exakten H-Kernelmoves.

### Real-State-Crosscheck

Direkt klassifizierter Movesatz gegen alten `omega_moves(...,"4x4")`-Stream:

- cand_A: 0 Moves;
- cand_B: 2 Moves;
- root witness 1: 49 Moves;
- root witness 2: 59 Moves.

Alle Movesätze stimmten exakt überein.

---

## 5. H-FIBRE-NEIGHBORHOOD 0.4.0

Vollständige Nachbarschaftszählung der vorhandenen exakten Omega-Familien:

| Zustand | W Basis | 4x4 | 4x6 | 6x6 |
|---|---:|---:|---:|---:|
| cand_A | 2338 | 0 | 0 | 0 |
| cand_B | 2333 | 2 | 0 | 0 |
| root witness 1 | 3083 | 49 | 0 | 4 |
| root witness 2 | 3046 | 59 | 0 | 3 |

Weitere Befunde:

- cand_B hat einen verbessernden 4x4-Move auf W=2331;
- root witness 1: bester 4x4 W=2983, bester 6x6 W=3080; ein 6x6→4x4-Zweischritt erreicht W=2981;
- root witness 2: bester 4x4 W=2944; 6x6 öffnet 4x4-Nachbarschaft, liefert aber keinen besseren Zweischritt als direkt 4x4.

Interpretation: die lokale Schwierigkeit ist nicht eine fehlende minimale Move-Familie, sondern starke Zustandsabhängigkeit / lokale Faser-Konnektivität.

---

## 6. H-FIBRE-SMALLMOVE 0.5.x: vollständige kleine exakte Moves

### 0.5.1 — Distanzen 16–19

Nach Korrektur eines reinen Implementierungsfehlers in 0.5.0 (`Counter`-Import) ist 0.5.1 der autoritative Lauf.

- cand_A:
  - E16: 0;
  - E17: 0;
  - E18: 0 in allen möglichen Support/Gradfällen;
  - E19: 0 in allen möglichen Support/Gradfällen.
- cand_B:
  - E16: exakt 2;
  - E17–E19: 0.

Der generische E16-Sucher reproduzierte die legacy-4x4-Moves exakt.

### 0.5.2 — Distanzen 20–21

Alle möglichen Gradfolgen einschließlich spezieller universeller Grad-8-Fälle wurden vollständig geprüft.

- cand_A: 0 Moves bei E20 und E21;
- cand_B: 0 Moves bei E20 und E21.

### 0.5.3 — Distanzen 22–24

Der Sucher wurde auf allgemeine Grad-4/6/8-Zeilen erweitert.

Grad-8-Erzeugung:

- vollständiger Index aller 1,929,501 Vierermengen;
- 163,401 Inzidenzsignaturen;
- state-spezifisch 631,736 Grad-8-Optionen für cand_A;
- 632,942 für cand_B.

Alle programmgenerierten zulässigen Gradfolgen für E22, E23 und E24 wurden vollständig geprüft.

Ergebnis:

- cand_A: **0 exakte H-Moves bei jeder Distanz 16–24**;
- cand_B: **genau 2 Moves bei Distanz 16, 0 bei jeder Distanz 17–24**.

Der Lauf war vollständig (`PASS`), keine Workerfehler und keine Budget-Zensierung.

---

## 7. H-FIBRE-OMEGA-EXTEND 0.6.0

Da die alten Produktfamilien 4x4/4x6/6x6 die sparse states kaum oder gar nicht bewegen, wurden größere algebraisch natürliche Produktmoves ergänzt:

- 4x8 — 32 geänderte H-Kanten;
- 4x10 — 40;
- 4x12 — 48;
- 6x8 — 48.

Kontrollen:

- neuer 4x4-Enumerator = legacy 4x4 exakt;
- neuer 4x6-Enumerator = legacy 4x6 exakt;
- neuer 6x6-Enumerator = legacy 6x6 exakt.

Ergebnis auf cand_A und cand_B:

- 4x8: 0;
- 4x10: 0;
- 4x12: 0;
- 6x8: 0.

Damit erklärt auch eine naheliegende Erweiterung des Omega-Produktkatalogs die lokale Isolation nicht weg.

---

## 8. H-FIBRE-NEAREST 0.7.0 — globaler Distanzlauf abgeschlossen

Statt die exakten Shells 25,26,27,… einzeln zu enumerieren, wurde ein globales 0/1-Optimierungsmodell gerechnet:

- 3,486 binäre undirektionale H-Kantenvariablen;
- 84 Gradgleichungen;
- 1,176 Margin-Gleichungen;
- Ziel: minimale H-Kantendistanz zum Ausgangszustand;
- Untergrenze 25, gestützt auf die vollständigen Shell-Ausschlüsse bis 24;
- OR-Tools 9.15.6755;
- zwei parallele Jobs mit je 4 Workern;
- nominelles Solverlimit 43,200 s; beobachtete Walltime ca. 47,468 s je Job.

### cand_B_next

Bekannt waren zwei Nachbarn bei Distanz 16 und keine bei 17–24. Der 0.7.0-Lauf suchte daher nur ab Distanz 25.

Ergebnis:

- verifizierter zulässiger H-Zustand bei Distanz **28**;
- CP-SAT Best Bound **25**;
- unabhängige H-Verifikation PASS;
- Status FEASIBLE, Optimalität nicht bewiesen.

Damit gilt

\[
25 \le d_{\min}^{>16}(\mathrm{cand\_B}) \le 28.
\]

Es bleiben genau die drei offenen Shells 25, 26 und 27.

### cand_A

Incumbents im Lauf:

- 786;
- 784;
- 778;
- 440;
- 200;
- schließlich **184**.

Ergebnis:

- verifizierter zulässiger H-Zustand bei Distanz **184**;
- CP-SAT Best Bound **25**;
- unabhängige H-Verifikation PASS;
- Status FEASIBLE, Optimalität nicht bewiesen.

Damit gilt

\[
25 \le d_{\min}(\mathrm{cand\_A}) \le 184.
\]

Die starke Verbesserung der konstruktiven Obergrenze ist nützlich, aber die Beweislücke bleibt groß.

### Interpretation

Der Befund bestätigt eine stark diskontinuierliche lokale H-Faser:

- cand_B ist nach seinen beiden 16er-Nachbarn bis 24 leer, besitzt aber spätestens bei 28 wieder einen exakten H-Zustand;
- cand_A ist bis 24 leer und der beste global gefundene andere Zustand liegt bislang erst bei 184.

Das spricht gegen die Vorstellung einer allmählich dichter werdenden lokalen Nachbarschaft. Für weitere Arbeit sollte cand_B jetzt durch gezielte Shell-Entscheidungen 25/26/27 exakt geschlossen werden; cand_A braucht eher eine separate Feasibility-/Threshold-Strategie als einen weiteren identischen 12h-Minimierungslauf.
---

## 9. Wissenschaftliche Gesamtinterpretation

### Was jetzt gesichert ist

1. Der kleinste nichttriviale exakte H-Move hat exakt 8 betroffene H-Vertices und 16 geänderte H-Kanten.
2. Jeder solche minimale Move ist ein alter Omega-4x4-Produktmove.
3. Der alte Operator war auf der minimalen Skala vollständig; es fehlte dort keine Move-Familie.
4. Praktisch relevante H-Zustände können trotzdem extrem dünne exakte Nachbarschaften haben.
5. cand_A ist vollständig isoliert in allen exakt geprüften Shells 16–24 und hat auch keine der getesteten größeren Produktmoves 4x8/4x10/4x12/6x8.
6. Für cand_A liefert die globale Suche inzwischen einen verifizierten anderen H-Zustand bei Distanz 184; damit gilt derzeit 25 ≤ d_min ≤ 184.
7. cand_B besitzt nur zwei minimale 16er-Nachbarn und danach keine exakten Nachbarn bis 24; ein weiterer verifizierter H-Zustand wurde bei Distanz 28 gefunden, also 25 ≤ d_min^(>16) ≤ 28.
8. Die W≈2100-Barriere der früheren \(\lambda\)-Memetik ist daher nicht sinnvoll dadurch zu erklären, dass der Sucher den elementarsten exakten H-Move übersehen hätte.

### Was ausdrücklich nicht gesichert ist

- cand_A ist nicht als global isolierter H-Zustand bewiesen; nur Distanzen 16–24 sowie die genannten Produktfamilien sind ausgeschlossen.
- Es gibt keinen Beweis, dass exakte H-Moves größerer Distanz nicht existieren.
- Die Resultate sagen nichts direkt über die Existenz eines SRG(99,14,1,2) oder eines Conway-99-Polytops.
- Die Resultate beweisen keine globale Tiefenbarriere für konstruktive Augmentation.

---

## 10. Bezug zum abgeschlossenen ROOT-8105 / Augmentation-Pilot

Der parallele Augmentation-Pilot endete mit:

- 256 Suchjobs;
- 512 Proofjobs;
- 276.26 CPU-hours;
- 256/256 Suchjobs: `CPU_LIMIT_UNKNOWN`;
- 512/512 Proofjobs: `PROJECTED_COVERAGE_DRAT_VERIFIED`;
- 512 zertifizierte lokale/projizierte Closures;
- 0 zertifizierte Root-Ausschlüsse;
- maximal beobachtete Tiefe 16;
- 1,447,471,813 beobachtete Rows;
- 33,748,941,099 Projektionsbytes;
- keine belastbare Full-Tree-/Runtime-Prognose.

Wegen sampled parents, Beam-Truncation und zensierten Widths ist daraus **keine globale Tiefenbarriere und keine Root-Erschöpfung** abzuleiten.

### Konkrete Folgerungen für eine Fortsetzung des Augmentation-Zweiges

1. **cand_A als planted positive control verwenden.**  
   cand_A ist ein vollständiger exakter H-Zustand, aber lokal im exakten H-Raum bis Distanz 24 ohne Nachbarn. Präfixe aus cand_A sind daher garantiert zu einem H-Zustand completable. Wenn eine Augmentation-/Completion-Strategie solche gepflanzten Präfixe bei Tiefe 16,24,32,… nicht robust weiterführen kann, ist das ein Algorithmus-/Oracleproblem und kein Existenzproblem.

2. **cand_B als fast-isolierten Kontrollfall verwenden.**  
   cand_B erlaubt genau zwei 16er-Moves, sonst keine Shell 17–24. Damit kann geprüft werden, ob ein Verfahren minimale lokale Alternativen überhaupt erkennt und danach wieder aus der dünnen Region herauskommt.

3. **Root witnesses als „bewegliche“ Kontrollen beibehalten.**  
   Mit 49 bzw. 59 minimalen 4x4-Nachbarn sind sie deutlich weniger lokal starr und eignen sich als Kontrast zu cand_A/B.

4. **Keine Fortsetzung ausschließlich über exakte kleine H-Moves planen.**  
   Die memetischen Resultate legen nahe, dass eine erfolgreiche Fortsetzung entweder
   - größere globale Rekonstruktionen,
   - zeitweilige H-Defekte mit späterer Reparatur,
   - oder eine konstruktive Präfix-/SAT-Augmentation außerhalb einer festen exakten H-Nachbarschaft
   benötigt.

5. **Pilot-Tiefe 16 nicht als strukturelle H-Barriere interpretieren.**  
   Die H-Faser-Ergebnisse zeigen starke lokale Starrheit bestimmter vollständiger Zustände, aber der Augmentation-Pilot war sampled und beam-beschränkt. Beide Befunde sind kompatibel; keiner impliziert den anderen.

6. **Planted-depth calibration vor einem neuen breiten Pilot.**  
   Empfohlen ist eine kleine Kalibrierungsserie mit bekannten vollständigen H-Zeugen und fest gepflanzten Präfixtiefen, bevor erneut sehr viel CPU in ungerichtete Wurzelsuche fließt.

---

## 11. Reproduzierbare Paketstände

Wichtige im Verlauf erzeugte Pakete:

- H-DEFECT 0.1.2 — ZIP SHA256 `e615ade39fa5ed4355325d55d42e8750963c6ee22fa99989d4ce3d787b3e99fe`
- MINIMAL-H-CIRCUIT 0.2.0 — `e42300ff5c7b1a5075185709c75007641bb5b2a436d041c7db697f24287c0700`
- MINIMAL-H-CIRCUIT 0.2.1 — `cfd9387b653789da705913c76227e56a8b15fa96ca39a5942934a9cb09a053ff`
- MINIMAL-H-CIRCUIT 0.2.2 — `6c0b9f0d9e0076dfa3b27ecdbe36d703f694ac090b8bd666c6b7c6206dbb8c35`
- MINIMAL-H-CIRCUIT 0.2.3 — `29f603c15b4c93019398e8f17c4855f84796bcaf02a44804a613e36d25fa2c41`
- MINIMAL-H-CIRCUIT 0.3.0 — `0012d50de4c3f47ad4d5d9dc35658ebf4c23b4afe172d0f451d6ed2c1a6ac39e`
- H-FIBRE-NEIGHBORHOOD 0.4.0 — `1c53875845c9047b4c7c6fd320e977836f461e6bdeb486fc8c3f8975aa0c3737`
- H-FIBRE-SMALLMOVE 0.5.1 — `b26bb61b8916afe4e05f0f48121c677629d89e533369cfa70d74a96cb303c1b1`
- H-FIBRE-SMALLMOVE 0.5.2 — `dadef85288f1e4fa0eed11884ea12b00afaedae2093c09dbb7e005a433c32886`
- H-FIBRE-SMALLMOVE 0.5.3 — `e573b1584fb7fcd05d9618d23ab66260d386b084c924d0189e2f1e06d7bc6a69`
- H-FIBRE-OMEGA-EXTEND 0.6.0 — `9ee38380cbe7a4719c505e991a9ead25e08d8ef1198bc4be7993ba6d036db550`
- H-FIBRE-NEAREST 0.7.0 — ZIP SHA256 `c6e3f2e1a8ec5efe5db7b082a6e3a9b89ff1486a9c35461a465c1fabff604f65`; Solverlauf abgeschlossen: cand_A 25≤d≤184, cand_B_next 25≤d≤28, beide FEASIBLE und unabhängig H-verifiziert.

---

## 12. Empfohlener nächster gemeinsamer Entscheidungspunkt

H-FIBRE-NEAREST 0.7.0 ist abgeschlossen. Der nächste kleine, hochinformative Schritt ist die exakte Entscheidung der drei offenen cand_B-Shells 25, 26 und 27; Distanz 28 ist bereits durch einen verifizierten Zustand belegt.

Für cand_A sollte statt eines identischen weiteren globalen Minimierungslaufs eine Feasibility-/Threshold-Kampagne mit harten Obergrenzen unter 184 verwendet werden, um entweder neue Incumbents zu finden oder die Untergrenze anzuheben.

Parallel kann der Augmentation-Zweig unmittelbar die planted-control-Idee aus Abschnitt 10 aufnehmen:

- **Nearest-H:** cand_B kann voraussichtlich kurzfristig exakt geschlossen werden; cand_A bleibt ein tiefer lokaler Stressfall.
- **Augmentation planted controls:** Kann die konstruktive Suche bekannte completable Präfixe zuverlässig tief weiterführen?

Diese Resultate sollten vor dem nächsten großen Rechenblock gemeinsam bewertet werden.
