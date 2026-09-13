# Vollständiges C2-Modell für Conway99 — Spezifikation 1.0.0

Stand: 13. September 2026. Ausgangscommit: ba8d71ccaab4d64088cc6802382a8ea4dbe68603.
Status: allgemeine mathematische Herleitung und ausgeführte kleine Integerkontrollen; kein C2-Ausschluss, noch kein Produktionsencoder. Neuheit der strukturellen Folgerungen wird nicht beansprucht.

## 1. Genaue Zielaussage und Literaturvoraussetzung

Ziel ist die Unlösbarkeit des unten vollständig angegebenen endlichen Modells. Unter dem bekannten Satz, dass jede Involution eines SRG(99,14,1,2) genau einen Fixpunkt hat, wäre dies äquivalent zum Ausschluss sämtlicher Involutionen. Wir verwenden diesen Satz als Literaturvoraussetzung. Ein Autorenbeleg ist Makhnevs Vortrag, Folien 12–15, insbesondere Theorem 1 auf der 16. PDF-Seite: https://www.math.uni-bielefeld.de/~baumeist/sommerschule/makhnev.pdf . Dort wird Makhnev–Minakova (2004) als Originalquelle angegeben. Der heutige Abruf des Verlags-PDFs scheiterte; der Originalbeweis wurde hier nicht neu auditiert.

## 2. Der feste Rahmen ist vollständig

Sei o der einzige Fixpunkt der Involution t. Wegen lambda=1 induzieren seine 14 Nachbarn sieben disjunkte Kanten. Wir nummerieren die Nachbarn 0,...,13 mit Partnerabbildung a -> a xor 1. Jeder der übrigen 84 Knoten hat genau zwei Nachbarn in N(o). Diese sind nicht gematcht, denn sonst läge deren Kante auf zwei Dreiecken. Jedes nichtgematchte Paar besitzt neben o genau einen gemeinsamen Nachbarn. Damit sind die Außenknoten bijektiv die Mengen {a,b} mit a<b und b != a xor 1.

**Lemma 1 (Wirkung von t).** Auf N(o) vertauscht t genau die beiden Enden jeder Matchingkante. Denn t hat dort keinen Fixpunkt. Wäre t(a) kein Matchingpartner von a, dann wäre der eindeutig durch {a,t(a)} bezeichnete Außenknoten ein weiterer Fixpunkt. Also t(a)=a xor 1. Auf den Außenlabels gilt notwendig t({a,b})={t(a),t(b)}. Keines dieser Labels ist fest. Es gibt genau 42 Außenpaare. Diese Argumentation erfasst alle Involutionen unter der Literaturvoraussetzung; es wurde keine zusätzliche Symmetrie angenommen.

**Lemma 2 (Partnerkantenverbot).** Für jeden Außenknoten x gilt x nicht benachbart zu t(x). Andernfalls wäre der einzige gemeinsame Nachbar dieser Kante unter t fest, also gleich o; o ist aber zu keinem Außenknoten benachbart.

R sei die 84×14-Inzidenzmatrix der Außenlabels, K die 14×14-Matchingmatrix. Der vollständige Graph hat die Blockmatrix

\[
A=\begin{pmatrix}0&\mathbf1^T&0\\\mathbf1&K&R^T\\0&R&M\end{pmatrix}.
\]

M ist symmetrisch, binär, mit Nulldiagonale, t-invariant und erfüllt Lemma 2.

## 3. Notwendige und hinreichende Gleichungen

\[
\tag{E1}M\mathbf1=12\mathbf1,
\qquad\tag{E2}MR=2J_{84\times14}-R(K+I_{14}),
\]
\[
\tag{E3}M^2+M=12I_{84}+2J_{84}-RR^T.
\]

**Satz 1.** M erfüllt E1–E3 genau dann, wenn das rekonstruierte A ein SRG(99,14,1,2) ist. Mit der vorgeschriebenen Invarianz besitzt es die oben angegebene Involution.

**Beweis.** Die SRG-Bedingung ist A²+A=12I+2J für eine einfache symmetrische binäre Matrix. Ihr Diagonaleintrag erzwingt Grad 14 und die außerdiagonalen Einträge die richtigen gemeinsamen Nachbarzahlen. Im Außenblock ergibt sie E3 und im Außen-Nachbarblock E2; aus den Graden folgt E1. Umgekehrt sind diese Blöcke damit korrekt. Die festen Blöcke sind automatisch korrekt: R1=2·1, R^T1=12·1, K²=I und R^TR=11I+J−K. Der Nachbar-Nachbarblock ist daher J+K²+R^TR+K=12I+2J. Die Wurzelblöcke ergeben unmittelbar 14 auf der Diagonale und 2 außerhalb. E1 ist durch die Diagonale von E3 bereits redundant, wird aber als explizite Gradbedingung beibehalten. Damit gilt die volle Matrixgleichung. Die Blockkonstruktion kommutiert mit t. Umgekehrt wurde jeder Graph mit Involution durch Abschnitt 2 erfasst. QED.

E2 wird nicht durch eine unbewiesene Redundanzannahme entfernt. Pro Außenzeile schreibt E2 vier Summen gleich 1 und zehn Summen gleich 2 vor: Die vier Nachbarpositionen sind a,b,t(a),t(b).

## 4. Exakte Darstellung auf 42 Paaren

Für jedes Außenpaar wählen wir das lexikographisch kleinere Label als Repräsentanten x_i. Außenreihenfolge: x_0,...,x_41,t(x_0),...,t(x_41). Dann

\[
M=\begin{pmatrix}B&C\\C&B\end{pmatrix},\quad Q=B+C,\quad D=B-C.
\]

B und C sind symmetrische binäre 42×42-Matrizen, beide mit Nulldiagonale (bei C wegen Lemma 2). Es gibt 2·binom(42,2)=1722 primäre Bits. Q hat Einträge 0,1,2; D hat Einträge −1,0,1. Ihre **exakte Kopplung** pro Position ist

\[
(Q_{ij},D_{ij})\in\{(0,0),(1,1),(1,-1),(2,0)\}.
\]

Q allein ist keine hinreichende Graphbeschreibung.

Definiere W,V in Z^(42×7) durch

\[
W_{ih}=R_{i,2h}+R_{i,2h+1},\qquad V_{ih}=R_{i,2h}-R_{i,2h+1}.
\]

Jede W-Zeile hat zwei Einsen; jede V-Zeile zwei Einträge aus {−1,1}. Direkt aus den Labels erhält man

\[
V^TV=12I_7,\quad W^TW=10I_7+2J_7,\quad (VV^T)_{ii}=(WW^T)_{ii}=2.
\]

Die äquivalente vollständige Formulierung lautet

\[
Q\mathbf1=12\mathbf1,\quad QW=4J_{42\times7}-2W,\quad DV=0,
\]
\[
\tag{P}Q^2+Q=12I_{42}+4J_{42}-WW^T,
\qquad\tag{N}D^2+D=12I_{42}-VV^T.
\]

**Beweis der Äquivalenz.** Addieren bzw. Subtrahieren der beiden Außenblockspalten von E3 ergibt P bzw. N. Analog ergeben Addition bzw. Subtraktion der beiden Nachbarspalten 2h und 2h+1 von E2 die Bedingungen QW=4J−2W und DV=0. Die Umkehrung folgt durch Halbieren von Summe und Differenz; die Kopplung stellt sicher, dass B=(Q+D)/2 und C=(Q−D)/2 binär sind. Es fehlt kein Hebungsschritt: B und C rekonstruieren M unmittelbar.

## 5. Konkrete strukturelle Folgerungen

**Lemma 3 (perfektes Matching der Doppelverbindungen).** Setze H=|D| und F_ij=1 genau dann, wenn Q_ij=2. Dann

\[
Q=H+2F,\quad H\mathbf1=10\mathbf1,\quad F\mathbf1=\mathbf1.
\]

H ist ein einfacher 10-regulärer Graph auf 42 Knoten; F ist ein zu H kantendisjunktes perfektes Matching mit 21 Kanten. Die H-Kanten tragen die Vorzeichen aus D. Eine F-Kante bedeutet eine vollständige K2,2-Verbindung zwischen den betreffenden Außenpaaren; eine H-Kante bedeutet eine der beiden möglichen Matchingverbindungen.

**Beweis.** Aus der Diagonale von N folgt sum_j D_ij²=12−2=10. Weil D_ij in {−1,0,1}, hat H somit Grad 10. Aus Q1=12·1 und Q=H+2F folgt Grad(F)=1. Symmetrie und Nulldiagonale machen F zu einem perfekten Matching. QED.

**Lemma 4 (Spektrum des vorzeichenbehafteten Teils).**

\[
\operatorname{spec}(D)=\{0^{(7)},3^{(20)},(-4)^{(15)}\},\qquad \operatorname{rank}(D)=35.
\]

**Beweis.** V^TV=12I impliziert rank(V)=7. Auf im(V) ist D wegen DV=0 gleich null. Auf dessen orthogonalem Komplement ist VV^T=0, also erfüllt D dort z²+z−12=0. Deshalb treten dort nur 3 und −4 auf und keine weiteren Nullen. Die beiden Vielfachheiten a,b erfüllen a+b=35 und 3a−4b=tr(D)=0. Also a=20,b=15. QED.

Diese Lemmas sind hier vollständig hergeleitete Konsequenzen des Modells. Sie sind noch keine neue Ausschlussfamilie. Eine knappe Literaturrecherche ohne exakten Treffer beweist ihre Originalität nicht.

## 6. Verbindlicher Encodervertrag

Die erste Produktionsversion soll B_ij,C_ij (i<j, lexikographisch) als primäre Variablen verwenden. Die direkt ausgeschriebene 84-Knoten-Form E1–E3 ist die Referenz. Matchingbedingungen aus Lemma 3 dürfen als bewiesene redundante Bedingungen ergänzt werden. Ein ausschließlich auf Q beruhender Encoder ist unzulässig.

Für E3 außerhalb der Diagonale wird genau die Gleichung

sum_z (M_xz AND M_zy) + M_xy = 2 − |label(x) intersect label(y)|

kodiert. Produkte erhalten eine vollständige Äquivalenz p iff (u AND v), nicht nur eine Implikation. Fallen durch die Orbitabbildung Variablen zusammen, werden Terme mit korrekter Multiplizität gezählt; u AND u wird u. E2 und E1 sind exakte Kardinalitätsgleichungen. Für eingesetzte Zählkodierung und Hilfsvariablen muss die Existenz einer Erweiterung genau der arithmetischen Gleichung entsprechen.

Vor Produktion: deterministische Variablenkarte; kleine erschöpfende Kontrollen der Produkt-/Zählkodierung; Quervergleich direkter Graphbedingungen und Encoder am Rookgraphen; direkte Prüfung jeder SAT-Ausgabe; dokumentierte allgemeine Encoderkorrektheit. Die jetzigen Kontrollen prüfen noch keinen solchen Encoder.

Symmetriebrechung wird in der Baseline zunächst weggelassen. Spätere Beschränkungen benötigen einen Nachweis, dass mindestens ein Repräsentant jeder Lösung erhalten bleibt. Insbesondere darf F nicht willkürlich auf ein einzelnes Standardmatching festgelegt werden: Die festen W,V-Labels lassen keine beliebige S42-Umbenennung zu. Rahmenumbenennungen stammen aus C2 wr S7. Die Wirkung der vorgeschriebenen Involution ist auf invarianten Belegungen bereits trivial.

Ein vollständiges binäres Cubing ist zulässig, wenn jeder Split beide Belegungen enthält und die Blätter lückenlos nachgewiesen sind. Pilot-Timeouts bleiben offene Blätter. Vollständiges UNSAT erfordert korrekten Encoder, sämtliche Blattbeweise, unabhängige Prüfung und Fallabdeckung.

## 7. Ausgeführte Kontrollen

`src/c2_spec_20260913/check_spec.py` prüft mit Integerarithmetik:

- die festen Gramidentitäten bei k=14;
- die Residuenidentitäten der direkten und der Plus/Minus-Blöcke an 32 deterministisch erzeugten Belegungen bei k=14;
- alle 64 einfachen Außenmatrizen im k=4-Kleinfall gegen die vollständige SRG-Gleichung;
- alle vier partnerkantenfreien invarianten Kleinbelegungen gegen die Plus/Minus-Form;
- den gefundenen Kleinfall gegen einen unabhängig über gleiche Zeile/Spalte konstruierten 3×3-Rookgraphen.

Ergebnis: C2_SPEC_CONTROLS_PASS; im fest beschrifteten Kleinrahmen genau eine Lösung. Laufzeit hier unter einer Sekunde. Die Spektralaussage für k=14 folgt aus dem schriftlichen Beweis, nicht aus einem gefundenen 99-Knoten-Graphen. Die Kontrollen ersetzen weder den allgemeinen Beweis noch eine Produktionszertifizierung.

Reproduktion im Repository mit Python 3 und NumPy:

`python3 src/c2_spec_20260913/check_spec.py`

Ausgabe: `results/c2_spec_20260913/controls.json`. Das Skript schreibt diesen eigenen Kontrollbericht neu; historische Forschungsresultate bleiben unberührt.

## 8. Nächster Schritt

Auf dieser Spezifikation den deterministischen Referenzencoder implementieren und gegen die direkte Graphprüfung absichern. Danach in einem begrenzten Pilot Baseline und zusätzliches perfektes Matching vergleichen. Der Forschungsgegenstand ist die gemeinsame Realisierbarkeit von F, H und den Vorzeichen unter den festen W,V-Bedingungen. Ein kleinerer Matrixindex oder weniger primäre Variablen allein garantiert keine geringere Rechenhärte.
