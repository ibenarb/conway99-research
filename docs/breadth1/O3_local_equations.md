# O3-BREADTH-1 — Lokale Quotientengleichungen

**Stand:** 3. September 2026  
**Revision:** nach Peer-Review vor dem O3-BREADTH-1-Scout  
**Status:** eigene Rederivation; mit historischem Encoder abgeglichen; mechanische Template-Tests bestanden.

## 1. Scope und Statusetiketten

Wir betrachten einen hypothetischen `srg(99,14,1,2)` mit einer fixpunktfreien Automorphie `g` der Ordnung 3. Die Fixpunktfreiheit wird in diesem Dokument **nicht** neu bewiesen, sondern als publiziertes Resultat importiert. Alle folgenden Aussagen über Quotient, Zyklusstruktur und lokale Gleichungen werden dagegen hier erneut hergeleitet.

Die 99 Knoten zerfallen in 33 `g`-Orbits der Größe 3. Für zwei Orbits `O_i,O_j` sei

`q_ij := Q_ij`

die Zahl der Nachbarn eines festen Knotens aus `O_i` in `O_j`. Wegen der Transitivität von `g` auf jedem Orbit ist diese Zahl wohldefiniert. Da beide Orbits Größe 3 haben, gilt `q_ij=q_ji`; der Quotient `Q=(q_ij)` ist symmetrisch.

Zur Vermeidung einer historischen Notationskollision verwenden wir

- `\mathcal T` für die Menge der Quotientenknoten, deren 3-Orbit intern ein Dreieck ist;
- `U={0,...,32}\setminus\mathcal T` für die übrigen Quotientenknoten;
- `C=(v_0,...,v_{m-1})` für eine Zykluskomponente des späteren 2-Faktors `L`.

Das historische `qsat/core.py` verwendete dagegen `T` für `\mathcal T` und war auf `tau=6` spezialisiert.

## 2. Quotientenidentität

Für die Adjazenzmatrix des stark regulären Graphen gilt

`A^2+A=12I+2J`.

Der orbitkonstante Unterraum ist `A`-invariant. Auf ihm wird `A` durch den 33x33-Quotienten `Q` dargestellt. Da jeder Quotienteneintrag die Zahl der Nachbarn in einem 3-Orbit zählt, wird aus dem `2J`-Term nach Quotientierung `6J`. Somit

`Q^2+Q=12I+6J`,

und aus 14-Regularität

`Q 1 = 14 1`.

## 3. Diagonaleinträge und die Zerlegung Q=2D_T+S+2L

Innerhalb eines 3-Orbits ist wegen der Ordnung-3-Wirkung entweder keine Kante vorhanden oder alle drei Kanten. Daher

`q_ii in {0,2}`.

Setze

`\mathcal T={i:q_ii=2}`, `tau=|\mathcal T|`.

### 3.1 Dreieckorbit i in mathcal T

Aus der Diagonale der Quotientenidentität folgt

`(Q^2+Q)_ii=18`.

Für `i in \mathcal T` also

`4+2+sum_{j!=i} q_ij^2=18`,

folglich

`sum_{j!=i} q_ij^2=12`.

Die Zeilensumme gibt zugleich

`sum_{j!=i} q_ij=12`.

Da alle `q_ij` nichtnegative ganze Zahlen sind, folgt

`q_ij in {0,1}` für `j!=i`.

Damit besitzt ein Dreieckorbit genau 12 einfache Quotientennachbarn.

### 3.2 Nichtdreieckorbit i in U

Für `i in U` gilt `q_ii=0`, also

`sum_{j!=i} q_ij^2=18`,

während die Zeilensumme

`sum_{j!=i} q_ij=14`

liefert. Subtraktion ergibt

`sum_{j!=i} q_ij(q_ij-1)=4`.

Ein Eintrag `q_ij>=3` würde mindestens 6 beitragen und ist daher unmöglich. Also treten nur 0,1,2 auf. Genau zwei Einträge müssen gleich 2 sein; alle übrigen positiven Einträge sind 1. Nach Abzug der beiden Gewicht-2-Einträge verbleibt Gewicht 10, also genau zehn Gewicht-1-Einträge.

### 3.3 Struktur

Damit gilt zwingend

`Q = 2D_{\mathcal T}+S+2L`,

wobei

- `D_{\mathcal T}` die Diagonalmatrix der Indikatorfunktion von `\mathcal T` ist;
- `S` eine einfache symmetrische 0/1-Matrix ohne Diagonale ist;
- `L` ein einfacher 2-regulärer Graph auf `U` ist;
- `S` und `L` kantendisjunkt sind;
- `deg_S(i)=12` für `i in \mathcal T`;
- `deg_S(i)=10` für `i in U`.

Da jeder endliche einfache 2-reguläre Graph disjunkte Vereinigung von Zyklen ist, ist `L` ein 2-Faktor auf `U`.

## 4. Zulässige Werte von tau

Die Eigenwerte eines `srg(99,14,1,2)` sind `14,3,-4`. Der orbitkonstante Unterraum hat Dimension 33; daher besitzt `Q` ebenfalls nur diese Eigenwerte. Sei `r` die Multiplizität von 3 in `Q`. Dann hat -4 Multiplizität `32-r`. Andererseits

`tr(Q)=2 tau`.

Also

`2 tau = 14 + 3r - 4(32-r) = 7r-114`.

Daraus folgt

`tau == 6 (mod 7)`.

Mit `0<=tau<=33` erhält man genau

`tau in {6,13,20,27}`.

Somit hat `U` Größe 27,20,13 beziehungsweise 6.

## 5. Allgemeine lokale Paargleichung

Schreibe

`D=2D_{\mathcal T}=diag(d_i)`, mit `d_i=2 [i in \mathcal T]`.

Für `i!=j` expandieren wir

`Q=D+S+2L`.

Da `D` diagonal ist,

`(DS+SD+S)_ij=(d_i+d_j+1)S_ij`,

und

`(2DL+2LD+2L)_ij=2(d_i+d_j+1)L_ij`.

Ferner

`(S^2)_ij = |N_S(i) cap N_S(j)|`,

`(SL+LS)_ij = sum_k S_ik L_kj + sum_k L_ik S_kj`,

`(L^2)_ij = |N_L(i) cap N_L(j)|`.

Aus `(Q^2+Q)_ij=6` folgt daher für jedes ungeordnete Paar `i!=j`

`(S^2)_ij + 2(SL+LS)_ij + 4(L^2)_ij + (d_i+d_j+1)S_ij + 2(d_i+d_j+1)L_ij = 6`.  (E)

Da für `i!=j`

`Q_ij=S_ij+2L_ij`

gilt, kann man äquivalent schreiben

`(S^2)_ij + 2(SL+LS)_ij + 4(L^2)_ij + (d_i+d_j+1)Q_ij = 6`.  (E')

**Terminologieregel.** `q_ij` bezeichnet ausschließlich den Quotienteneintrag `Q_ij`. Es wird kein reskalierter `qterm` mehr als `q_ij` bezeichnet.

Für zwei Nichtdreieckorbits `i,j in U` ist `d_i=d_j=0`; dann reduziert sich (E') auf

`(S^2)_ij + 2(SL+LS)_ij + 4(L^2)_ij + Q_ij = 6`.

Dies ist genau der Spezialfall des früheren Review-Templates.

## 6. C4-Ausschluss

Sei `C_4` eine Komponente von `L` und `i,j` gegenüberliegende Knoten. Dann besitzen `i,j` zwei gemeinsame `L`-Nachbarn. Also

`4(L^2)_ij = 8`,

während die rechte Seite von (E) nur 6 ist. Alle übrigen Terme sind nichtnegative ganze Zahlen. Widerspruch.

Daher besitzt `L` keine `C_4`-Komponente.

## 7. Lemma B — Rederivation und tau-Scope

**Lemma B.** Sei `C=(a,b,c)` eine `C_3`-Komponente von `L`. Insbesondere liegen `a,b,c in U` und besitzen jeweils `S`-Grad 10. Dann besitzt jeder Quotientenknoten `w` außerhalb von `C` genau eine `S`-Kante nach `C`.

**Beweis.** Für das Paar `a,b` gilt

- `a,b in U`, also `d_a=d_b=0`;
- `L_ab=1`;
- `c` ist gemeinsamer `L`-Nachbar, also `(L^2)_ab=1`.

Gleichung (E) wird zu

`(S^2)_ab + 2(SL+LS)_ab + 4 + 2 = 6`.

Daher

`(S^2)_ab=0` und `(SL+LS)_ab=0`.

Insbesondere besitzen `a,b` keinen gemeinsamen `S`-Nachbarn. Dasselbe gilt für jedes der drei Paare in `C`. Somit kann jeder Außenknoten höchstens einen Knoten von `C` über `S` treffen.

Jeder Knoten von `C` liegt in `U` und hat `S`-Grad 10. Innerhalb von `C` sind alle drei Paare `L`-Kanten und daher keine `S`-Kanten. Es verlassen also genau `3*10=30` `S`-Kanten die Komponente. Außerhalb von `C` liegen `33-3=30` Quotientenknoten. Da jeder höchstens eine solche Kante aufnehmen kann, nimmt jeder genau eine auf. QED.

Der Beweis benutzt `tau` an keiner Stelle. Also gilt Lemma B für alle zulässigen

`tau in {6,13,20,27}`.

**Status:** eigene Ableitung; zweimal peer-reviewt; im Abschnitt O3-BREADTH-1 erneut hergeleitet.

## 8. Relabelling-WLOG

**Lemma 8.1 (Relabelling-Invarianz).** Sei `P` eine Permutationsmatrix auf den 33 Quotientenknoten. Dann transformiert

`Q -> P Q P^T`

die Gleichungen

`Q^2+Q=12I+6J` und `Q1=14 1`

in sich selbst. Ebenso werden `D_{\mathcal T}`, `S` und `L` simultan relabelt. Daher darf nach Wahl der `tau` Dreieckorbit-Knoten ohne Einschränkung

`\mathcal T={0,...,tau-1}`

gesetzt werden. Innerhalb von `U` darf jede 2-Faktor-Komponente durch eine kanonische Beschriftung ihres Zyklustyps repräsentiert werden.

**Beweis.** Wegen `PIP^T=I`, `PJP^T=J` und `P1=1` gilt

`(PQP^T)^2+PQP^T=P(Q^2+Q)P^T=12I+6J`

und

`PQP^T 1 = P Q 1 = 14 1`.

Die Zerlegung wird zu

`PQP^T=2(PD_{\mathcal T}P^T)+(PSP^T)+2(PLP^T)`.

Damit sind alle Bedingungen invariant. QED.

Der zugehörige mechanische Permutationstest ist Bestandteil der erweiterten Regression vor dem Scout.

## 9. Mechanische Validierung

### 9.1 Historischer tau=6-Core

Der historische `qsat.cli algebra`-Test konstruiert `Q` direkt und vergleicht `(Q^2+Q)_ij` mit der gespeicherten normalisierten LHS-Termstruktur. Auditbefund: Er prüfte nicht separat das gespeicherte RHS.

Diese Lücke wurde read-only über alle 103 `C_4`-freien `tau=6`-Typen geschlossen:

- 103 Typen,
- 528 Paare pro Typ,
- 54 384 RHS-Prüfungen,
- 0 Abweichungen,
- absichtliche RHS-Mutation erkannt.

### 9.2 Unabhängiger O3-BREADTH-1-Template-Test

`src/breadth1/o3_cycle_local_check.py` importiert keinen historischen `qsat`-Code. Es konstruiert für jede der vier `tau`-Klassen formale Quotientenmatrizen direkt und vergleicht direkte ganzzahlige Matrixmultiplikation mit (E).

Der revidierte Prüfer ergänzt:

- einen positiven Kontrollfall `srg(9,4,1,2)` mit `Q=I+J`;
- Distanzklassen-Assertions für kleine `m`;
- Lemma-Mutationen;
- explizite Ablation der inneren Konsistenzbedingung;
- Tests der Momentkappe für `m=13` und `m=27`.

## 10. Status dieses Deliverables

Damit sind für O3-BREADTH-1 neu rederiviert bzw. validiert:

1. Quotientenidentität und eindeutige Notation `q_ij=Q_ij`;
2. Zerlegung `Q=2D_T+S+2L`;
3. 2-Faktor-Struktur von `L`;
4. `tau in {6,13,20,27}`;
5. allgemeine lokale Paargleichung (E)/(E');
6. `C_4`-Ausschluss;
7. Lemma B einschließlich tau-Unabhängigkeit;
8. Relabelling-WLOG;
9. unabhängige Template-, Positiv-, Negativ- und Mutationstests.

Keine Aussage dieses Dokuments ist ein globaler Nichtexistenzbeweis für `srg(99,14,1,2)`.
