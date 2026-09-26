# Conway99 · Memetik λ · Review der Etappen D, F und O

Stand 26.09.2026 · Reviewer-Bericht zu `00_REVIEWERPROMPT.md` im flachen ZIP `Lambda_Review_20260926.zip`.
Kontext: Review vom 24.09.2026 (Etappe D, Empfehlung „letzter begrenzter Frontier-Lauf“).

> **Kurzfassung.**
>
> - Die Rekorde sind echt und unabhängig bestätigt. Die Serie hat meine Prognose vom 24.09. klar übertroffen: Ich hatte „realistisch um 2090“ erwartet, F erreichte 2081 und O 2076.
> - Der Fortschritt entsteht durch Bankerneuerung, nicht durch Laufzeit. Eine neue Bank steigt 1–3 h lang ab und friert dann ein. Die W-Ereignisrate fällt von 0,81 (F) über 0,41 (O, 0–4 h) auf 0,04 je CPU-h (O, 4–7 h).
> - Es gilt die exakte Identität **F = 4·(Q − 2079)** mit Q = Anzahl der 4-Kreise. Linie A senkt W, während der 4-Kreis-Überschuss steigt; sie entfernt sich also algebraisch von der Lösung. W2077 aus Linie B ist strukturell der bessere Kandidat.
> - W2076 und W2077 sind exakte (W,L1)-Minima **bis Tiefe 3** unter Apex ∪ Pivot, vollständig ausgezählt mit 526 476 bzw. 459 185 Kindern. Die gemessenen Rekordschritte 2081 → 2079 → 2076 brauchten jeweils **genau 4** Züge.
> - Empfehlung: Abschlussbericht schreiben. Optional folgt eine deterministische Tiefe-4-Auszählung an 2076 und 2077 mit fester Schließregel. Mehr Seeds oder längere Läufe auf denselben Bänken empfehle ich nicht.

Kennzeichnung: **[N]** selbst nachgerechnet · **[Ü]** übernommen · **[H]** Interpretation oder Hypothese.

---

## 1. Nachgerechnete Befunde

### 1.1 Datenbasis und Endpunkte [N]

**Prüfskript.** `04_VERIFY.py` läuft mit PASS: 1 465 verschiedene Graphen, 2 318 Vorkommen. Das Skript zählt 126 Hashes, `05_CHECK_RESULT.json` nennt dagegen 125. Vermutlich wurde das Manifest nachträglich um eine Datei ergänzt. Die Abweichung ist harmlos, sollte aber vereinheitlicht werden.

**Endpunkte.** Alle 22 Vergleichsendpunkte aus D/V2, F und O habe ich mit eigenem Code geprüft (`analysis.py`); darunter sind 12 verschiedene Graphen.
- Scores und λ-Gültigkeit stimmen überall.
- Die pynauty-2.8.8.1-Zertifikate reproduzieren das Feld `class`.

Die Isomorphieklassen der **Endpunkte** sind damit unabhängig bestätigt, die übrigen 1 453 Graphen nicht.

**Angaben der Datenübersicht.** Alle geprüften Angaben stimmen:
- Bei 4 h waren 7 von 8 O-Jobs unter 2081. Die Stände bei 14 400 s lauten 2079, 2079, 2076, 2079, 2076, 2078, 2077 und 2084.
- W2076 erreichten zwei Jobs vor 4 h. Der dritte erreichte ihn nach 17 104 s = 4,75 h.
- Nach 6 h gab es nur L1-Verbesserungen, und zwar in F-W2081-5 und F-W2092-1.
- Die drei W2076-Treffer sind derselbe beschriftete Graph.

**Nicht geprüft:** CPU-Summen der Ledger, SQLite-Archive, Receipts außerhalb des Pakets.

### 1.2 Identität F = 4·(Q − 2079) [N]

Die Identität gilt für jeden λ-Graphen mit n = 99 und k = 14.

1. Auf Kanten gilt stets r = 0, denn CN = 1.
2. Die Summe von CN über alle Paare ist 99·C(14,2) = 9 009. Davon entfallen 693 auf die Kanten. Auf die 4 158 Nichtkanten entfallen also 8 316 = 2·4 158, und die Residuen der Nichtkanten haben Summe 0. Folglich ist L1 = 2·Σ r⁺.
3. Die Diagonalen eines 4-Kreises sind Nichtkanten, denn wegen λ = 1 haben benachbarte Knoten nur einen gemeinsamen Nachbarn. Deshalb gilt Σ_Nichtkanten C(CN,2) = 2Q.
4. Daraus folgt F = Σ(CN − 2)² = (4Q + 8 316) − 4·8 316 + 4·4 158 = 4Q − 8 316.

Die Identität ist an allen 22 Endpunkten numerisch bestätigt. **F misst genau den 4-Kreis-Überschuss; eine Lösung liegt genau bei Q = 2079 vor.**

### 1.3 Zwei Linien mit gegenläufiger Struktur [N]

| Linie | Graph | W | L1 | F | Q − 2079 | L1 − W | Nmax |
|---|---|---|---|---|---|---|---|
| A | V2-W2102-0 | 2096 | 2480 | 3272 | 818 | 384 | 12 |
| A | F-W2096-1/3 | 2081 | 2488 | 3336 | 834 | 407 | 17 |
| A | O-W2081-0/3 | 2079 | 2484 | 3328 | 832 | 405 | 17 |
| A | O-W2081-1/2/4 | **2076** | 2488 | 3352 | 838 | 412 | 20 |
| B | V2-W2108-1 | 2101 | 2450 | 3172 | 793 | 349 | 12 |
| B | F-W2101-* | 2092 | 2448 | 3196 | 799 | 356 | 1 (Linf 4) |
| B | O-W2092-0 | **2077** | 2436 | 3180 | 795 | 359 | 13 |

Beschriftete Kantenabstände:
- W2076 ↔ W2077: 128 Kanten.
- In Linie A: 2096 → 2081 sind 28, 2081 → 2079 sind 10, 2079 → 2076 sind 10 Kanten.
- In Linie B: 2101 → 2092 sind 34, 2092 → 2077 sind 40 Kanten.

Zum Vergleich der F-Rekord 2836 aus dem Review vom 21.09. **[Ü]**.

### 1.4 Lokale Minimalität und Zugabstände [N]

Alle Rechnungen verwenden den eingefrorenen Katalog `kernel.catalogue` aus `lambda_compare_0_2_0` in a4d4396, Apex ∪ Pivot ohne cycle3, wie im produktiven P.

**Tiefe 2.** 2076, 2077, 2078, 2079, 2081, 2084 und 2092 sind exakte Zwei-Zug-Minima für (W, L1). Je Graph wurden 8 741 bis 9 894 Zugfolgen geprüft; keine verbessert.

**Tiefe 3.** Bei 2076 und 2077 ist die Auszählung vollständig: jedes Kind jedes verschiedenen Tiefe-2-Zustands, zusammen mit Tiefe 1 und 2.

| Graph | Tiefe 1 | Zustände Tiefe 2 (verschieden) | Kinder Tiefe 3 | verbessernd |
|---|---|---|---|---|
| W2076 | 99 | 5 222 | 526 476 | 0 |
| W2077 | 95 | 4 768 | 459 185 | 0 |

**Zugabstände.** Gerechnet im Meet-in-the-middle-Verfahren; Apex und Pivot sind jeweils zu sich selbst invers.
- 2081 → 2079: **genau 4** Züge.
- 2079 → 2076: **genau 4** Züge.
- 2096 → 2081: mehr als 4 Züge.

### 1.5 Trichter, Herkunft, Ereignisraten [N]

**Trichter.**
- Bank 2101: 4 von 4 Seeds enden im selben beschrifteten 2092-Graphen, 3 davon über (2099, 2474).
- Bank 2096: 2 von 4 Seeds enden im selben 2081-Graphen, 3 laufen über (2091, 2488).
- O-Bank A: 5 von 6 Seeds laufen über denselben 2079-Graphen, 3 von 6 enden in 2076.

**Herkunft** [N, Methode heuristisch]. Bestimmt über den kleinsten beschrifteten Abstand zu den Gründern der Bank:
- Der 2092-Attraktor stammt in allen vier Jobs aus Gründer Nr. 8 (W2108), nicht aus dem Bestgraphen 2101. Der Abstand beträgt 18 zu Gründer Nr. 8 und 34 zum Bestgraphen.
- W2077 stammt aus Gründer Nr. 2 (W2096) der 2092-Bank, nicht aus 2092. Der Abstand beträgt 26 zu Gründer Nr. 2 und 40 zu 2092.
- In O-Bank A stammt alles vom Bestgraphen. Diese Bank ist eng: Alle Gründer liegen höchstens 36 Kanten vom Bestgraphen entfernt. Bank B streut bis 50.

**Ereignisraten.** Gezählt sind W-Verbesserungen als Schübe mit mehr als 60 s Abstand.

| Etappe | Ereignisse | CPU-h | je CPU-h | W-Gewinn der Etappe |
|---|---|---|---|---|
| D/V2 | 8 | 12 | 0,67 | 2102 → 2096 |
| F | 26 | 32 | 0,81 | 2096 → 2081 |
| O, 0–4 h | 13 | 32 | 0,41 | 2081 → 2076 |
| O, 4–7 h | 1 | 24 | 0,04 | keine neue Klasse |

Die letzten W-Ereignisse je Job, in Stunden:
- F: 3,67 / 2,87 / 2,45 / 2,00 / 0,63 / 1,79 / 1,39 / 1,64.
- O: 3,03 / 4,75 / 2,36 / 2,00 / 3,36 / 0,59 / 1,01 / 3,71.

Die längste Wartezeit vor einem späteren Erfolg betrug etwa 3,2 h.

---

## 2. Interpretation [H]

**Fortschritt kommt aus Bankerneuerung.** D, F und O zeigen jeweils dasselbe Muster: Eine neue Bank steigt schnell ab und friert dann ein. Seeds verschieben den Zeitpunkt, kaum das Ziel.

In zwei von vier Bänken stammt der spätere Rekord von einem Gründer, der nicht der Bestgraph war. Vielfalt in der Bank war dort entscheidend. Das sind nur zwei Fälle; ein kausaler Nachweis ist es nicht.

**Längere Läufe lohnen nicht.** Die Stunden 4–7 der O-Läufe, zusammen 24 CPU-h, lieferten keine neue Klasse. Das ist kein Protokollfehler, die Entscheidung fiel vor dem Start. Die Daten stützen aber für künftige Läufe eine Plateau-Regel je Job. Sie sollte bei 3,5 h oder mehr liegen, weil vor Erfolgen Wartezeiten bis etwa 3,2 h vorkamen.

**Beide Entscheidungsregeln stimmen überein.** Nach eurem Kriterium lautet das Ergebnis REPEATED_SIGNAL_REVIEW_ONLY. Meine Regel vom 24.09. greift ebenfalls: Die Ausbruchsrate sinkt deutlich. Beides passt zusammen. Rekorde sind noch möglich; eine Annäherung an eine Lösung zeigen sie nicht.

**W ist hier ein irreführender Fortschrittsmaßstab.** Linie A senkt W, indem sie Residuen auf weniger Paare konzentriert: L1 − W steigt von 384 auf 412, Nmax von 12 auf 20. Zugleich steigt der 4-Kreis-Überschuss von 818 auf 838. Nach §1.2 ist das eine Bewegung weg von Q = 2079.

Auch bei W = 2076 ist rund die Hälfte der 4 158 Nichtkanten-Paare noch falsch. Die Ertragskurve spricht nicht dafür, dass diese Suche W = 0 erreichen kann: −6, −15 und −5 W in 12, 32 und 56 CPU-h.

**Die Landschaft um die Rekorde hat einen Radius von mindestens 4.** Die zwei gemessenen Rekordschritte hatten genau diese Länge, und an beiden Rekordgraphen gibt es bis Tiefe 3 nichts. Das erklärt, warum Perturbationen der Länge 2–4 gefolgt von Abstieg noch Rekorde finden, aber immer seltener.

**Meine eigene Fehlprognose.** Die Prognose „um 2090“ vom 24.09. war zu pessimistisch. Die Schlussfolgerung daraus, die Frontier als letztes Kapitel zu behandeln, halte ich trotzdem aufrecht.

---

## 3. Offene Fragen

1. Gilt der Radius von 4 Zügen allgemein, oder nur für die zwei gemessenen Schritte in Linie A? Der Schritt in Linie B, 2092 → 2077, ist mit 40 Kanten nicht gemessen.
2. Gibt es bei 2076 oder 2077 eine Verbesserung in Tiefe 4?
3. Hilft eine auf Vielfalt ausgerichtete Bankauswahl tatsächlich? Bisher gibt es dafür nur zwei Einzelfälle.
4. Wie verläuft die (W, F)-Pareto-Front? Warum hält Linie B F niedrig?
5. Offene Prüfungen: Isomorphie jenseits der Endpunkte, SQLite-Archive, Ledger-Summen.

---

## 4. Empfehlungen

**E1 – Abschlussbericht der λ-Memetik.** Kein CPU-Budget. Er sollte enthalten:
- die Ertragskurve und die Ratentabelle aus §1.5;
- die Identität F = 4(Q − 2079) und die gegenläufigen Linien;
- die Trichter und die Herkunftsanalyse;
- die exakten Minima bis Tiefe 3 und den Rekordschritt von 4 Zügen;
- die Befunde aus den früheren Reviews: das V1-Nullergebnis und den Rückstand der Nicht-HoG-Familien.

**E2 – optional: deterministische Tiefe-4-Auszählung an W2076 und W2077.**
- Fragestellung: Gibt es eine (W, L1)-verbessernde Folge aus 4 Zügen?
- Budget: grob 15–20 CPU-h je Graph in reinem Python, zusammen höchstens 40 CPU-h. Auf dem Ryzen sind das parallel etwa 1–2 h Wanduhr. Die Schätzung ist aus den Tiefe-3-Laufzeiten hochgerechnet und nicht gemessen. Die Deduplikation der Tiefe-3-Zustände braucht einige hundert MB.
- Vorab festgelegt:
  - Findet sich eine Verbesserung, ist das ein neuer Rekord ohne Zufallssuche. Anschließend wird nur deren Abstieg dokumentiert, keine neue Kampagne.
  - Findet sich keine, ist ein Radius von mindestens 5 an beiden Rekorden belegt, und die W-Frontier wird **endgültig geschlossen**.
- Begründung: Die Antwort ist deterministisch und entspricht genau der beobachteten Schrittweite.

**E3 – nur falls ausdrücklich ein weiterer Rekordversuch gewünscht ist.**
- Umfang: eine Runde mit 8 Jobs × 4 h = 32 CPU-h, dazu höchstens 1 Hilfs-CPU-h.
- Warum 4 h: Diese Grenze erfasst 15 von 16 finalen Rekordereignissen aus F und O.
- Bänke: A′ aus den sechs O-Endpopulationen von Linie A, B′ aus den zwei von Linie B, Aufteilung 4:4.
- Gründerauswahl je Bank: 8 nach (W, L1), dazu 8 Graphen, die den paarweisen Mindestabstand maximieren, beschränkt auf W ≤ Bestwert + 25.
- Vorab festgelegt:
  - Erfolg bedeutet mindestens zwei Jobs mit W < 2076.
  - Gibt es keinen Treffer oder bleibt der Bestwert bei 2072 oder darüber, wird die W-Frontier geschlossen.
  - F wird für jeden Rekord mitberichtet.
  - Es gibt keine Verlängerung.
- Erwartung: bestenfalls 2070–2075; kein Treffer ist ebenso plausibel.

**Nicht empfohlen:** weitere Seeds auf denselben Bänken, längere Einzelläufe, jede Formulierung dieser Linie als Weg zu einer Lösung.

---

## 5. Prüfsatz

Das flache ZIP `reviewer_lambda_20260926_pruefsatz.zip` enthält Skripte, Ergebnisse und README. Aufrufe und Grenzen stehen dort. Ausgeführt wurde alles in meiner Umgebung (Python 3.12, pynauty 2.8.8.1, ein Kern), nicht auf dem Ryzen. Der Gesamtaufwand betrug etwa 1 CPU-h.

## Anhang – Rekordgraphen (graph6, SHA256 = `state`)

**W2076** – {'F': 3352, 'L1': 2488, 'Linf': 3, 'Nmax': 20, 'W': 2076}, class `a49787a89c19e7bd28a63906316055f1cac3e6c910d4c1fa03c52894c7768afc`, state `8169eba8e1f2bf78eb655d99b94844a1eb5056df828e8c610a3778d537a7d0fe`

```
~?@boACSJ?_D?O?_?_COO??????E???@G@??SC????p?@A??G?@A?AI??????G??GDG@GGGO?G?CG?B__O?OGOAOA@?KC??OOOA?DOG??C@_???O`??a@?C_`??HG?@_OC_??HG?ACKG@??K??R???`B?_aG??@??_?o?C?O???o?ESGO?`@@GCB?_G`GS??C??@y?C?O_??D?OCa?c????I_?S@_?CCA?g??_P??@?G?VO?c?A?_@gAOODO@OG?K@C@?GGA?OoDCG?S?G??C?BGE?G?_?D???`A???p_@@GOA@_??H]??@A???GWoGAO`??B?G@???Ag@GOGCo?GO`?A@O???OAGP?GO?Gq?G?D__A?@?GP?@@YK???O??P_?G?CAACAGgGCD?@P??O???[?O_@GB?_??G?O?_X??GACGB???g@_?GOGc?`O?_CEOO@?OAaCOCKCO?_??_G@Aag?_@?g@?O???sAWB?A@C?H@@`@_CG?AA@@?GC??OhD??AoH?K?o?D?OQ?_I@@?c??o??@OAHGS?OAc??_?OU?C?`SC?AE_B?O???@@O?C???_?g[?OOp?`G@????@??DCGOc???_A?OCA@?AoGCO??APg??C?CcAWGAK_?_???A?HCAI?a@DCGC????AIaAOGa@OG??A@X?_??AP_??_@@@@?AoB?????oG[?Q?B?O@AiG_C@?A??OEOAA@oDA??????w?q_O_O??_@OA_A_??Eb@G@????OOA@O?CE???`_C_G?J???`A[??C?AOCOM?G@??N?A{??CG??o?O????
```

**W2077** – {'F': 3180, 'L1': 2436, 'Linf': 3, 'Nmax': 13, 'W': 2077}, class `04ef357d68a09ac6c807bc1188ad78f219bc09bb4e1d28390f1775d0de8b3717`, state `136bad89e063ba84bbc4201cfa5be21db6d511852602ad861a4d2c0e0ef8e49c`

```
~?@bpACSJ?_D?O?_?_COO??????A???@?@???CC@??`?@A??G?CA?GI?@@???GP?GF??GGGo?G?C??Aa`??OGOAOA@?K???OOOA?DOG??C?`???Oh??a@?Co`??HG?@_OC_??H??ACLG@??K??R???`B?_aG??`O?_?o?CGO???o?ASIO?`@@GCB?_G`GS??D?GBG?C?O_??@?OCA?c????A_?S?_?C?A?g??_P??@?G?VO?c?A?_@gAOODO@OG?K@C@?GGA?OoDCG?S?G??C?BGE?G@_?D???`A???p_@@?OA`_??H]??@A???GWoGAO`??B?G@???Ag@GOGCo?GOd??@O???OAGP?GO?Gq?G_D__A?@?GP?@@YK???O??P_?G?CAACA?gGCD?@P??O???S?P_@GD?_??G?O?_X??GACGBC??gC_?GOGC?`O?_CE?o@?OAaCO?KCO?_?C_G@AAg?_@_g@?P???cAWB?A@C?H@@?@_CG?AA?@?GC??Oj@??AoH?K?a?@?OQ?_IH@?c??o??@OAHGS?OA_??gCOO?D?`SC?AE_B?O???@@O?C???g?g[?OOp?`G@????@??DCGOc???_A?QCQ??Ao?HO??APg??C?CcAWGAK_?_???A?H?AG@a@DCGC???CAI_AOGa@OG??A@X?_?_??a??_@H@PGAOOO????og[?O?B?O?Yi?AC@?A??OEOAA@oDA??????w?Q?oo???`@OA_A_??Eb@G@????OOA@O?CE???`aC_G?J???@A[??C?AOCOM?G@??N?A{??CG??o?O????
```
