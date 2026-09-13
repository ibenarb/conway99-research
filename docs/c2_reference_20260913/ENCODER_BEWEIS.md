# C2-Referenzencoder 1.0.0: Korrektheitsargument und Reichweite

Grundlage: vollständige mathematische Spezifikation im Commit `31c563f6ba460227c6ae4eebcd519257fcba5ad4`, `docs/c2_spec_20260913/SPEZIFIKATION.md`. Dieses Dokument beschreibt die Projektion der erzeugten CNF auf ihre primären Variablen. Die endlichen Kontrollen sind zusätzliche Fehlerkontrollen, kein Ersatz für das allgemeine Argument. Noch keine externe Prüfung dieses Encoders und kein Produktions-UNSAT-Zertifikat.

## 1. Variablen und feste Nullen

Die Nachbarlabels sind 0,...,k−1, Partner a xor 1. Außenlabels sind die nichtgematchten Zweiermengen. Lexikographisch kleinere Labels jeder Involutionsbahn bilden die erste Hälfte, ihre Partner die zweite. Zuerst werden B_ij, danach C_ij für i<j lexikographisch nummeriert. Bei k=14 gibt es 1722 primäre Bits. Ein Matrixeintrag innerhalb derselben Hälfte verwendet B, zwischen den Hälften C. Diagonalen sowie Außenpartnerkanten sind konstant falsch. Keine andere Kante wird fixiert; keine weitere Symmetriebrechung ist eingebaut.

Diese Zuordnung ist genau die Blockmatrix M=[[B,C],[C,B]] aus der Spezifikation. Jede Belegung ergibt eindeutig eine einfache, involutionsinvariante Außenmatrix, und jede solche Matrix mit verbotenen Partnerkanten besitzt eine Belegung.

## 2. Produkte

Für p iff (u AND v) werden die drei Klauseln

(−p OR u), (−p OR v), (p OR −u OR −v)

verwendet. Sie erlauben genau den korrekten Produktwert. Die Vereinfachungen mit konstant wahr/falsch, u=u und u=−v sind wahrheitstafeltreu. Produkte werden unter dem sortierten Literalpaar wiederverwendet. Dadurch werden identische Produkte identifiziert, ihre mehrfachen Vorkommen in Summen aber nicht entfernt.

## 3. Exakte gewichtete Gleichheit

Jede angeforderte Summe wird zu sum_i w_i x_i=t normalisiert. Wahrkonstanten werden von t abgezogen, Falschkonstanten weggelassen; mehrfache positive Variablen erhalten die entsprechende positive ganzzahlige Multiplizität w_i. Anschließend werden Gewichte und Ziel durch den gemeinsamen Teiler der Gewichte gekürzt. Ist t durch diesen Teiler nicht teilbar, ist die Gleichheit unmöglich und es wird eine leere Klausel ausgegeben. Die übrigen Gewichte werden nach Variablennummer sortiert. Bereits identische normalisierte Gleichheiten brauchen keine zweite Kodierung.

Der BDD-Zustand N(i,r) bedeutet, dass die gewichtete Restsumme ab Position i gleich r ist. Bei r<0 oder r größer als der restlichen Gewichtssumme ist er falsch. Am Ende ist er genau für r=0 wahr. Ansonsten gilt

N(i,r) iff (x_i ? N(i+1,r−w_i) : N(i+1,r)).

Für y iff (x ? h : l) dienen vier Klauseln:

(−y OR −x OR h), (−y OR x OR l), (y OR −x OR −h), (y OR x OR −l).

Konstante Literale, doppelte Literale und Tautologien werden exakt vereinfacht. Gleiche Zweige werden identifiziert; die Fälle (h,l)=(wahr,falsch) und (falsch,wahr) liefern x bzw. −x. Boolesche Konstanten und Integer-Variablennummern werden dabei ausdrücklich unterschieden.

Induktion über die verbleibenden Positionen beweist: Zu jeder Belegung der Eingabevariablen ist der Wert jedes erreichbaren Knotens eindeutig bestimmt; der Wurzelwert ist genau die geforderte Gleichheit. Die Wurzel wird als Einheitsklausel verlangt. Somit existiert eine Belegung der Hilfsvariablen genau dann, wenn die arithmetische Gleichheit gilt. Das Argument benötigt keine Unabhängigkeit der Eingabevariablen; sie dürfen selbst korrekt definierte Produkte sein.

## 4. Vollständige Graphbedingungen

`encode_base` erzeugt alle drei Familien der Spezifikation:

- E1: für jeden Außenknoten x die Summe seiner Außenkanten gleich k−2;
- E2: für jedes Außenlabel x und jeden Nachbarn a die Summe über Außenknoten mit a im Label gleich 2−[a in x]−[a xor 1 in x];
- E3: für jedes ungeordnete Paar verschiedener Außenknoten x,y die Summe aller Produkte M_xz M_zy plus M_xy gleich 2−|x intersect y|.

E3 enthält auch die Paare x,t(x). Die Diagonale von E3 ist bereits exakt E1, weil M binär und symmetrisch ist. Die festen übrigen Blöcke der vollständigen Graphmatrix erfüllen ihre Bedingungen automatisch, wie in der Spezifikation bewiesen. Aus den Abschnitten 1–3 folgt daher: Die Projektion der Baseline-CNF ist genau die Menge der Graphlösungen des vollständigen C2-Modells.

Unter dem zitierten Fixpunktsatz erfasst dieses Modell alle Involutionen von SRG(99,14,1,2). Die Kodierung allein beweist nicht, dass es keine Lösung gibt.

## 5. Wichtiger Befund: Doppelmatching ist schon direkt kodiert

Für das Außenpartnerpaar x_i,t(x_i) ist E3 genau

2 sum_(j != i) (B_ij AND C_ij) = 2.

Nach der oben beschriebenen Kürzung ist das exakt die zusätzliche Matchingbedingung sum_j (B_ij AND C_ij)=1. Die Produktvariablen sind bereits vorhanden. Das Wiedererkennen identischer normalisierter Gleichheiten entfernt die gesamte vermeintliche Erweiterung. Bei k=14 sind baseline.cnf und matching.cnf daher byteidentisch.

Eine frühe, noch nicht veröffentlichte Entwicklungsfassung ohne Kürzung erzeugte für dieselbe Bedingung 3318 zusätzliche Hilfsvariablen und 11676 zusätzliche Klauseln. Diese stellten nur eine doppelte Kodierung dar. Die endgültige Fassung vermeidet sie. Der vorgeschlagene Pilotvergleich „mit/ohne Doppelmatching“ wird dadurch gegenstandslos. Dies ist ein praktischer Abgleich unserer Forschungsplanung, kein neuer mathematischer Ausschluss.

## 6. Ausgeführte unabhängige endliche Kontrollen

Das getrennte Testskript enthält einen kleinen DPLL-Prüfer; es verwendet keine BDD-Zustände des Encoders. Es prüft die Existenz einer CNF-Erweiterung unter vollständigen primären Belegungen:

- 3242 gewichtete Projektionsfälle einschließlich mehrfacher Variablen, Konstanten, unzulässiger Ziele und gemeinsamer Teiler;
- vollständige Wahrheitstafeln der AND- und ITE-Gatter;
- sieben Negativkontrollen: Entfernen jeder einzelnen Klausel der allgemeinen Gatter lässt eine verbotene Belegung zu;
- alle vier primären Rook-Belegungen in beiden Encoder-Modi, verglichen mit direkter Prüfung sämtlicher gemeinsamer Nachbarzahlen;
- unabhängig konstruierter Rookgraph als Positivkontrolle und eine korrumpierte Kante als Negativkontrolle;
- Zurückweisung unvollständiger bzw. widersprüchlicher primärer SAT-Ausgaben.

Die beiden erzeugten 99-Knoten-Dateien werden zusätzlich vollständig auf DIMACS-Klauselzahlen, Literalgrenzen, SHA256 und exakte Präfixgleichheit geprüft. Die Vorbereitung wird nochmals ausgeführt und ihre CNF-Hashes mit festen Erwartungswerten verglichen. Produktionssolver und LRAT-Prüfer werden dabei nicht gestartet.

## 7. Spätere Beweis- und Pilotpflichten

Ein Solver-UNSAT allein genügt nicht. Für einen Ausschluss werden ein gültiges unabhängig geprüftes Zertifikat, die Bindung an genau diese CNF sowie gegebenenfalls die vollständige Cube-Abdeckung benötigt. Eine SAT-Ausgabe wird über die primären Bits zu einer vollständigen Adjazenzmatrix rekonstruiert und unabhängig auf Symmetrie, Binärität, Diagonale, Grade sowie alle gemeinsamen Nachbarn geprüft.

Die Baseline ist nun reproduzierbar verfügbar. Der nächste Pilot muss entweder ihren tatsächlichen Durchsatz messen oder eine nachweislich andere Kodierung bzw. weitere hergeleitete Bedingungen untersuchen. Eine zweite Berechnung der byteidentischen Matchingdatei liefert keinen eigenständigen Vergleich.
