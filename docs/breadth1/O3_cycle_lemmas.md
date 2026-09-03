# O3-BREADTH-1 — Zykluslokale C_m-Lemmata

**Stand:** 3. September 2026  
**Revision:** nach Peer-Review vor dem O3-BREADTH-1-Scout  
**Status:** Papierableitung plus unabhängige mechanische Kontrolle; C5–C8 vollständig enumeriert.

## 1. Setup

Sei

`C=(v_0,...,v_{m-1})`, `m>=5`,

eine Zykluskomponente des 2-Faktors `L`. Indizes werden modulo `m` gelesen. Alle Knoten von `C` liegen in `U`, also ist `d_i=0` auf `C` und jeder Knoten von `C` besitzt gesamten `S`-Grad 10.

Für ein Paar `i,j` in `C` definieren wir:

- `x_ij=S_ij in {0,1}`; dies ist eine **Sehne**, wenn `i,j` keine Zyklusnachbarn sind;
- `a_ij`: Zahl der gemeinsamen `S`-Nachbarn von `i,j`, die ebenfalls in `C` liegen;
- `c_ij`: Zahl der gemeinsamen `S`-Nachbarn von `i,j` außerhalb von `C`;
- `b_ij=(SL+LS)_ij`; dies zählt die gemischten `S/L`-Zweiwege.

Dann

`(S^2)_ij=a_ij+c_ij`.

Die allgemeine Paargleichung reduziert sich innerhalb von `C` zu

`a_ij+c_ij+2b_ij+4(L^2)_ij+x_ij+2L_ij=6`.  (C)

Alle Variablen `a_ij,b_ij,c_ij` sind nichtnegative ganze Zahlen; `x_ij` ist boolesch.

## 2. Innere Konsistenz

**Lemma 2.1 (innere Konsistenz).** Für jedes Paar `i,j in C` ist

`a_ij = sum_{k in C\{i,j}} x_ik x_kj`

und daher

`(S^2)_ij >= a_ij`.

Äquivalent muss der durch (C) bestimmte Außenrest

`c_ij = 6 - 4(L^2)_ij - 2L_ij - x_ij - 2b_ij - a_ij`

eine nichtnegative ganze Zahl sein.

**Beweis.** Jeder Knoten `k in C`, der sowohl `S_ik=1` als auch `S_kj=1` erfüllt, ist per Definition ein gemeinsamer `S`-Nachbar von `i,j`. Diese internen gemeinsamen Nachbarn bilden eine Teilmenge aller gemeinsamen `S`-Nachbarn. QED.

Diese Bedingung war im ersten Prüfer bereits implementiert, im ersten Lemma-Dokument aber nicht als eigenständiges Lemma hervorgehoben. Der revidierte Prüfer hält beide Regressionsfingerabdrücke fest:

- **ohne** innere Konsistenz: `C5/C6/C7/C8 = 6/66/478/14615`;
- **mit** innerer Konsistenz: `6/66/408/6717`.

Damit ist die vom Peer-Review identifizierte Papier/Prüfer-Lücke explizit geschlossen.

## 3. Klassifikation nach Zyklusdistanz

Sei `delta(i,j)` die kürzere Zyklusdistanz.

### Lemma 3.1 — Distanz 1

Für `delta=1` gilt `L_ij=1`. Für `m>=5` besitzen benachbarte Zyklusknoten keinen gemeinsamen `L`-Nachbarn, also `(L^2)_ij=0`. Da eine `L`-Kante keine `S`-Kante sein kann, ist `x_ij=0`.

Somit

`a_ij+c_ij+2b_ij=4`.  (D1)

### Lemma 3.2 — Distanz 2

Für `delta=2` ist `L_ij=0` und es gibt genau einen gemeinsamen `L`-Nachbarn. Daher

`a_ij+c_ij+2b_ij+x_ij=2`.  (D2)

Insbesondere:

1. `b_ij<=1`;
2. bei `x_ij=1` gilt `b_ij=0` und `a_ij+c_ij=1`;
3. bei `b_ij=1` gilt `x_ij=0` und `a_ij=c_ij=0`.

### Lemma 3.3 — Distanz mindestens 3

Für jedes Paar, das weder Distanz 1 noch Distanz 2 hat, gilt

`L_ij=0`, `(L^2)_ij=0`.

Somit

`a_ij+c_ij+2b_ij+x_ij=6`.  (D3)

Für `m=5` gibt es keine solchen Paare. Für `m=6` gibt es genau drei, die Durchmesserpaare. Allgemein ist für `m>=5`

`# {ungeordnete Paare mit delta>=3} = binom(m,2)-2m`.

Eine `C_4`-Komponente ist bereits ausgeschlossen; dort wäre die Distanz-2-Form wegen zweier gemeinsamer `L`-Nachbarn nicht gültig.

## 4. Generische flankierende At-Most-One-Regel

Betrachte das Distanz-2-Paar `(v_i,v_{i+2})`. Seine beiden möglichen gemischten `S/L`-Beiträge stammen genau von den Sehnen

`x_{i,i+3}` und `x_{i-1,i+2}`.

Daher lautet (D2)

`a_{i,i+2}+c_{i,i+2}+2(x_{i,i+3}+x_{i-1,i+2})+x_{i,i+2}=2`.

Alle übrigen Terme sind nichtnegativ. Folglich:

**Lemma 4.1 (flankierende AMO-Regel).** Für jedes `m>=5` und jedes `i` gilt

`x_{i,i+2}+x_{i,i+3}+x_{i-1,i+2} <= 1`.  (AMO)

## 5. Erstes und zweites Außenmoment

Für einen Außenknoten `w notin C` setze

`d_w = |N_S(w) cap C|`.

Sei `e` die Zahl der `S`-Sehnen in `C`, und `s_v` der interne Sehnengrad eines Knotens `v in C`.

### Lemma 5.1 — erstes Moment

Jeder Knoten von `C` hat gesamten `S`-Grad 10. Die `e` internen Sehnen verbrauchen zusammen `2e` dieser Inzidenzen. Daher

`sum_{w notin C} d_w = 10m - 2e`.  (M1)

### Lemma 5.2 — zweites Moment

Jeder Außenknoten `w` ist gemeinsamer `S`-Nachbar von genau `binom(d_w,2)` ungeordneten Paaren in `C`. Also

`sum_{w notin C} binom(d_w,2) = sum_{i<j in C} c_ij`.

Summation von (C) über alle ungeordneten Paare liefert:

- rechte Seite `6 binom(m,2)=3m(m-1)`;
- `sum 2L_ij=2m`;
- `sum 4(L^2)_ij=4m`;
- `sum x_ij=e`;
- `sum a_ij=sum_{v in C} binom(s_v,2)`;
- jede Sehne erzeugt genau vier gemischte `S/L`-Zweiwege, also `sum b_ij=4e` und `sum 2b_ij=8e`.

Daher

`sum_{w notin C} binom(d_w,2) = 3m(m-3) - 9e - sum_{v in C} binom(s_v,2)`.  (M2)

### Sichere Kappe im relaxierten Moment-Test

Für jeden Außenknoten gilt

`d_w <= min(m,deg_S(w)) <= min(m,12)`,

weil Außenknoten in `\mathcal T` `S`-Grad 12 und Außenknoten in `U` `S`-Grad 10 besitzen.

Der tau-freie mechanische Moment-Test verwendet deshalb ausschließlich die sichere Relaxationskappe

`d_w <= min(m,12)`.

**Eine pauschale Kappe 10 wäre unsound.** Für `m>=13` wird die Kappe 12 erstmals relevant. Der revidierte Prüfer enthält deshalb explizite Regressionstests für `m=13` und `m=27`, die eine Grad-12-Konfiguration zulassen und dieselbe Konfiguration unter einer falschen Kappe 10 verwerfen.

## 6. Konsequenz: sehnenfreie C5

Für eine sehnenfreie `C_5` ist `e=0` und `s_v=0`. Aus (M1),(M2):

`sum d_w = 50`,

`sum binom(d_w,2)=30`.

Es gibt `33-5=28` Außenknoten.

Wären alle `d_w<=2`, dann wäre

`sum binom(d_w,2)`

gleich der Zahl der Außenknoten mit `d_w=2` und damit höchstens 28; sogar die erste Momentgleichung verschärft dies auf höchstens 25. Beides widerspricht dem Wert 30.

**Korollar 6.1.** Jede sehnenfreie `C_5` besitzt mindestens einen Außenknoten `w` mit

`d_w>=3`.

## 7. Spezialfall C5

Eine `C_5` besitzt genau fünf mögliche Sehnen; jede ist eine Distanz-2-Sehne. Aus (AMO) folgt, dass keine zwei Sehnen gleichzeitig gewählt werden können. Daher gibt es genau

`1+5=6`

lokal zulässige Sehnenbelegungen: die leere Belegung und die fünf Einzel-Sehnen.

**Satz 7.1.** Für `C_5` sind genau `6` der `2^5=32` Sehnenbelegungen zykluslokal zulässig.

## 8. Spezialfall C6

Eine `C_6` besitzt neun mögliche Sehnen:

- sechs Distanz-2-Sehnen;
- drei Durchmessersehnen.

Vollständige Enumeration unter (C), einschließlich Lemma 2.1, liefert exakt

`66/512`

lokal zulässige Muster.

Die falsche Behauptung „eine C6 besitzt höchstens eine S-Sehne“ wird durch konkrete zulässige Mehrsehnenbelegungen widerlegt.

Der zusätzliche relaxierte Moment-Test reduziert 66 auf 34.

## 9. Spezialfälle C7 und C8

Unter der vollständigen lokalen Bedingungsmenge (C) einschließlich Lemma 2.1 liefert die unabhängige Enumeration:

- `C_7`: `408/16384`;
- `C_8`: `6717/1048576`.

Ohne Lemma 2.1 wären es dagegen:

- `C_7`: `478`;
- `C_8`: `14615`.

Nach zusätzlichem relaxiertem Moment-Test verbleiben:

- `C_7`: `309`;
- `C_8`: `5754`.

Die vier lokalen Zahlen `6,66,408,6717` und die vier Momentzahlen `6,34,309,5754` sind mechanische Enumerationsresultate. Sie wurden im Peer-Review vom 3. September 2026 durch einen unabhängig geschriebenen Enumerator reproduziert.

## 10. Einheitliche Aussage für m>=9

Für jede `C_m` mit `m>=9` gelten unverändert:

1. innere Konsistenz (Lemma 2.1);
2. Distanz 1: (D1);
3. Distanz 2: (D2);
4. jede Distanz `delta>=3`: (D3);
5. flankierende AMO-Regel;
6. erstes Außenmoment (M1);
7. zweites Außenmoment (M2);
8. sichere Momentkappe `d_w<=min(m,12)`.

Damit ist keine neue Formel erforderlich; nur Zahl und Größe der lokalen Variablensysteme wachsen.

## 11. Kein universelles Exact-One-Analogon zu Lemma B

Lemma B für `C_3` entsteht aus vollständiger Budget-Sättigung. Für `m>=5` verbleibt auf einer Zykluskante dagegen gemäß (D1) Budget 4; gemeinsame `S`-Nachbarn sind nicht ausgeschlossen.

Die sehnenfreie `C_5` zeigt sogar zwingend einen Außenknoten mit mindestens drei Treffern. Daher existiert kein universelles Lemma-B-Analogon der Form

`|N_S(w) cap C|=1 für alle w notin C`

für alle `C_m`, `m>=5`.

Dies schließt stärkere Aussagen für spezielle `m`, Sehnenmuster oder zusätzliche globale Hypothesen nicht aus.

## 12. Mechanische Validierung und Regressionsfingerabdrücke

Das eigenständige Skript `src/breadth1/o3_cycle_local_check.py`

- importiert keinen historischen `qsat`-Encoder;
- prüft die Quotienten-Templateformel per direkter Matrixmultiplikation für alle vier `tau`;
- enthält den positiven Kontrollfall `srg(9,4,1,2)`;
- prüft kleine Distanzklassen explizit;
- enumeriert `m=5,6,7,8`;
- hält die Ablation ohne innere Konsistenz als Regressionsfingerabdruck fest;
- prüft (M2) auf zwei Wegen;
- testet die sichere Kappe 12 bei `m=13,27`;
- enthält Koeffizienten-Mutationen, die die Enumerationszahlen verändern;
- enthält Negativkontrollen.

Vorregistrierte Fingerabdrücke:

- ohne innere Konsistenz: `6/66/478/14615`;
- mit innerer Konsistenz: `6/66/408/6717`;
- mit Momentfilter: `6/34/309/5754`.

Keine dieser mechanischen Zählungen ist ein globaler Nichtexistenzbeweis.
