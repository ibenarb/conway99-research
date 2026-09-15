# C2: vollständige lokale Matching-Fallabdeckung

Stand 15.09.2026. Bezug: C2-Spezifikation `docs/c2_spec_20260913/SPEZIFIKATION.md`, Referenzencoder SHA256 `3a88f356831a4f955c79639bfe86aac5eea2a80febdd676cbd1009e86f1e9b29`. Diese Reduktion ist ein vollständig begründeter Vorbereitungsschritt. Ein neuer Literaturbeitrag oder ein Involutionsausschluss wird nicht beansprucht.

## 1. Modell und lokales Matching

Die Wurzel heißt o. Ihre Nachbarn tragen die Labels 0,...,13; ihre sieben Matchingkanten sind {0,1},...,{12,13}. Die vorgegebene Involution wirkt durch a -> a xor 1. Außenknoten heißen x_{a,b} für nichtgematchte ungeordnete Paare {a,b}. Der Encoder beschreibt alle übrigen Adjazenzen invariant unter dieser Involution.

Für den Rahmenknoten 0 gilt

N(0) = {o,1} vereinigt mit {x_{0,a}: 2 <= a <= 13}.

In einem SRG mit lambda=1 induziert jede Nachbarschaft einen 1-regulären Graphen: Für jede Kante vz hat z genau einen Nachbarn in N(v), denn diese sind genau die gemeinsamen Nachbarn von v,z. Die Kante o--1 verbraucht die beiden Knoten o,1 in N(0). Daher bilden die zwölf übrigen Knoten ein perfektes Matching L.

Dies folgt auch direkt aus E2: Für x=x_{0,a} ist die Summe der Außenkanten von x zu Labels, die 0 enthalten, gleich 2-1-0=1. Symmetrie und Nulldiagonale liefern das Matching.

L ist ein Matching auf zwölf Außenknoten innerhalb einer einzelnen Nachbarschaft. Es ist NICHT das in der ursprünglichen Plus/Minus-Formulierung beschriebene Matching der Doppelverbindungen auf 42 Außenpaaren. Diese beiden Strukturen dürfen nicht gleichgesetzt werden.

## 2. Zulässige Rahmenumbenennungen

Betrachte H als Gruppe aller Permutationen der Labels 2,...,13, die deren feste Paarung

P = {{2,3},{4,5},{6,7},{8,9},{10,11},{12,13}}

erhalten und 0,1 einzeln festlassen. H ist C2 wr S6 und hat Ordnung 2^6 * 6! = 46.080. Hier dient P zunächst als Paarung von Labels; wir behaupten nicht, dass sie gleich L ist.

Jedes p in H erweitert sich auf alle Graphknoten durch o -> o, a -> p(a), x_{a,b} -> x_{p(a),p(b)}. Diese Abbildung erhält die festen Rahmenkanten, die Labelinzidenzen und kommutiert mit der vorgegebenen Involution. Sie erhält auch die verbotenen Außenpartnerkanten.

Damit ist sie eine zulässige Umbenennung jeder vollständigen Lösung: Grade und gemeinsame Nachbarzahlen ändern sich unter Knotenpermutation nicht. Äquivalent bleiben E1-E3 erhalten. Auf den 1722 primären B/C-Variablen entsteht eine Bijektion; B und C dürfen dabei im Allgemeinen ineinander übergehen. Es wird keine beliebige S42-Umbenennung verwendet.

Für die Hilfsvariablen der BDD-Kodierung wird KEINE syntaktische CNF-Automorphie behauptet. Der Schritt ist semantisch: Eine umbenannte vollständige Graphlösung erfüllt die gleichen Gleichungen, und die Encoderkorrektheit liefert eine Erweiterung auf die Hilfsvariablen. Das ist für die UNSAT-Fallabdeckung ausreichend.

## 3. Orbitklassifikation

Identifiziere x_{0,a} mit a. Vereinige die feste Paarung P und L als zweifarbiges Multigraphensystem. Jede Komponente ist ein alternierender gerader Kreis. Gemeinsame Kanten werden als zwei parallele Kanten verschiedener Farbe behalten; sie bilden einen Kreis der Länge 2.

Hat eine Komponente 2r Knoten, enthält sie r Kanten jeder Farbe. Die Halbkreisgrößen ergeben somit eine ganzzahlige Partition lambda von 6. Diese Partition ist unter H invariant.

Umgekehrt genügt sie zur Klassifikation. Durchlaufe jede Komponente abwechselnd entlang einer P-Kante und einer L-Kante. Ordne Komponenten gleicher Größe beliebig und nummeriere die durchlaufenen P-Paare aufeinanderfolgend. Dies erzeugt eine Permutation in H, welche L auf das Standardmatching des entsprechenden Typs abbildet. Gleiche Partition bedeutet daher gleiche H-Bahn.

Für einen Teil r lautet der Standardvertreter auf lokalen Positionen 0,...,2r-1:

P_i = {2i,2i+1},
L_i = {2i+1, 2((i+1) mod r)}  für 0 <= i < r.

Für mehrere Teile werden disjunkte aufeinanderfolgende Blöcke verwendet. Die lokalen Positionen 0,...,11 entsprechen den Außenlabels (0,2),...,(0,13).

Die elf Typen und ihre beschrifteten Anzahlen sind:

| Partition von 6 | Anzahl |
|---|---:|
| 1+1+1+1+1+1 | 1 |
| 1+1+1+1+2 | 30 |
| 1+1+1+3 | 160 |
| 1+1+2+2 | 180 |
| 1+1+4 | 720 |
| 1+2+3 | 960 |
| 1+5 | 2304 |
| 2+2+2 | 120 |
| 2+4 | 1440 |
| 3+3 | 640 |
| 6 | 3840 |
| Summe | 10395 |

Die Gesamtzahl aller beschrifteten Matchings ist 11!! = 12!/(2^6*6!) = 10.395. Für einen Typ lambda mit l Teilen und m_r Teilen gleich r ist seine Anzahl

2^(6-l) * 6! / (Produkt_i lambda_i * Produkt_r m_r!).

Denn der Stabilisator im farberhaltenden Automorphismensystem hat Ordnung Produkt_r (2r)^(m_r) * m_r!. Für r=1 berücksichtigt 2r=2 die Vertauschung der Enden der doppelt vorhandenen Kante. Die Formel stimmt für alle Typen mit der unabhängigen Enumeration überein.

## 4. Vollständigkeit der elf SAT-Fälle

Zu jeder Lösung des ursprünglichen C2-Modells gehört das notwendige Matching L. Nach Abschnitt 3 gibt es p in H, das L auf einen der elf Vertreter abbildet. Nach Abschnitt 2 ist die umbenannte Graphstruktur wiederum eine Lösung desselben Modells. Sie erfüllt daher einen der elf festgelegten Matchingfälle.

Folglich gilt: Wenn sämtliche elf Vertreter-CNFs nachweislich UNSAT sind, ist die Referenz-CNF UNSAT. Ein SAT-Modell irgendeines Vertreters ist dagegen bereits eine Lösung des ursprünglichen Modells. Über die bestehende Fixpunkt-Literaturvoraussetzung der C2-Spezifikation würde ein vollständiger UNSAT-Beweis den Involutionsfall ausschließen.

Es ist KEINE Partition sämtlicher beschrifteter Belegungen in elf CNF-Mengen: Nichtkanonische Lösungen werden durch eine Umbenennung erfasst. Verschiedene Typen liefern disjunkte Festlegungen in der gewählten Rahmennummerierung; weitere Isomorphismen könnten sie trotzdem verbinden. Eine minimale Klassifikation unter der gesamten Rahmengruppe wird nicht behauptet.

Pro Vertreter werden alle 66 Kanten zwischen den zwölf Außenknoten festgelegt: sechs positive und 60 negative Einheitsklauseln. Die ursprüngliche CNF bleibt als exakter Klauselkörperpräfix erhalten. Nur der DIMACS-Klauselzähler wird um 66 erhöht. Die spiegelbildliche Festlegung in N(1) ist bereits durch die gemeinsame primäre Variablenrepräsentation erzwungen; zusätzliche unbewiesene Annahmen werden nicht eingeführt.

Keiner der elf Matchingtypen wird vorab als zu einem vollständigen SRG erweiterbar bezeichnet. Die restlichen E1-E3-Gleichungen können weitere Typen ausschließen. Die lokale Anzahl eines Typs ist auch kein Maß für dessen Anteil an den vollständigen Graphlösungen oder seiner Rechenschwierigkeit.

## 5. Ausgeführte Kontrollen und Grenzen

`matching_orbits.py` erzeugt alle 10.395 Matchings, berechnet jeweils eine konkrete Transportpermutation, prüft deren Paarungserhaltung und das exakte Bildmatching. Alle elf Häufigkeiten werden gegen die unabhängige Formel geprüft.

Elf Erzeuger von H (sechs Paarflips, fünf benachbarte Paarvertauschungen) werden auf sämtlichen Außenkanten und Labelinzidenzen geprüft. Die 1722 primären Variablen bilden jeweils eine Bijektion; verbotene Kanten bleiben verboten. Zusätzlich wird die Rekonstruktion einer deterministischen Belegung als vollständiger 99-Knoten-Graph mit der entsprechenden Knotenpermutation verglichen. Dies ist eine endliche Implementierungskontrolle, kein Test aller möglichen Graphen. Die allgemeine Gültigkeit folgt aus dem schriftlichen Umbenennungsargument.

Die elf Produktions-CNFs wurden lokal vorbereitet und ihre exakten Präfixe/Einheitsklauseln geprüft. Ihre Schwierigkeit wird erst der Ryzen-Scout messen. Solver-Kontrollen benutzen winzige bekannte Formeln. Kein produktiver C2-UNSAT-Beweis wurde in dieser Vorbereitung erzeugt.
