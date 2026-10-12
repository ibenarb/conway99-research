# Adäquanz der tatsächlich verwendeten C2-Basis

Stand 12.10.2026. Status: **mathematisch hergeleitet und an die konkrete
Implementierung gebunden; unabhängiges Review ausstehend**. Kein UNSAT-Ergebnis.

## 1. Präzise Aussage und Versionsbindung

Sei $F_0$ die erzeugte DIMACS-Formel mit SHA-256
`7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd`.
Sie hat 534.135 Variablen und 1.921.773 Klauseln. Die ersten 1.722 Variablen
beschreiben die beiden symmetrischen Außenblöcke $B,C$.

**Satz ENC0.** Eine Belegung dieser Primärvariablen ist genau dann auf eine Lösung
von $F_0$ erweiterbar, wenn ihre Außenmatrix die Gleichungen E1–E3 des
[Manuskripts](../c2_completeness_20261012/MANUSKRIPT.md) erfüllt.

Für die folgenden Quellen wird diese Aussage begründet:

| Datei | SHA-256 |
|---|---|
| `c2_reference.py` | `3a88f356831a4f955c79639bfe86aac5eea2a80febdd676cbd1009e86f1e9b29` |
| `counter.py` | `b9d97c440585d65799108a31ed42615de3f6821f34b32aafceae6f34a4c722dd` |
| `model.py` | `370cb2766e78b19112ce4c92f8f1099b4053c80faa4020491cfbf00303888640` |
| `anchor_profile.py` | `327d85c9b1dbd73aceab770fdb34f96abb056955fc12206ff984ee7fd0fb91fd` |

Die Dateien liegen unverändert unter
[vendor/rest218/legacy](../../vendor/c2_completeness_20261012/rest218/legacy).
Der neue Filteraudit bestätigte ihre Byteidentität mit den vier Dateien des
Profile46-Abschlussexports. Damit gilt das Argument für dieselbe Quellfassung
in beiden Stufen, nicht nur für einen ähnlichen historischen Referenzencoder.

## 2. Rahmen und primäre Variablen

`Frame` bildet alle ungepaarten Zweiermengen der 14 Anker. Die lexikographisch
kleineren Labels der Involutionsbahnen stehen in der ersten Hälfte; ihre Partner
in der zweiten. Für jedes $i<j$ wird zunächst $B_{ij}$, dann $C_{ij}$ allokiert.
`edge(x,y)` liefert die entsprechende Variable innerhalb beziehungsweise zwischen
den Hälften und genau bei $x=y$ oder $y=t(x)$ konstant falsch.

Damit ist die Zuordnung zwischen primären Belegungen und symmetrischen binären
Matrizen $M=\left(\begin{smallmatrix}B&C\\C&B\end{smallmatrix}\right)$ mit
Nulldiagonalen von $B,C$ bijektiv. Andere Kanten werden nicht festgelegt.
Die Wahl der Labels ist eine Koordinatenwahl, keine zusätzliche graphentheoretische
Einschränkung. Der neue Audit konstruierte die Zuordnung separat und verglich
alle $84^2=7.056$ Einträge mit dem verwendeten `Frame`.

## 3. Klauselvereinfachung, Produkte und Auswahlgatter

`clause` entfernt falsche Konstanten und wiederholte Literale. Eine Klausel mit
wahrer Konstante oder einem komplementären Literalpaar wird ganz weggelassen.
Dies sind jeweils äquivalente Vereinfachungen. Eine leere verbleibende Klausel
ist der Widerspruch. Boolesche Konstanten werden vor Integerliteralen behandelt.

`conjunction(a,b)` erzeugt für einen neuen Produktwert $y$ genau

$$ (\neg y\lor a)\land(\neg y\lor b)\land(y\lor\neg a\lor\neg b), $$

also $y\leftrightarrow(a\land b)$. Konstanten, identische und komplementäre
Eingänge werden exakt vereinfacht. Wiederverwendung identischer Produkte entfernt
keine ihrer mehrfachen Vorkommen in einer Summe.

`select(x,h,l)` erzeugt für einen neuen Auswahlwert $y$ vier Klauseln:

$$
(\neg y\lor\neg x\lor h),\quad(\neg y\lor x\lor l),\quad
(y\lor\neg x\lor\neg h),\quad(y\lor x\lor\neg l).
$$

Für $x=1$ erzwingen sie $y=h$, für $x=0$ erzwingen sie $y=l$.
Die Sonderfälle gleicher Zweige und der beiden komplementären konstanten Zweige
sind äquivalent. Der Typvergleich verhindert dabei die Verwechslung von
`True` mit Variablennummer 1.

## 4. Gewichtete Gleichheiten und BDD für E1/E2

Jede Summe wird zu $\sum_i w_i x_i=t$ normalisiert. Wahre Konstanten werden vom
Ziel abgezogen, falsche entfernt und wiederholte Variablen mit ganzzahliger
Multiplizität gezählt. Kürzen mit dem gemeinsamen Teiler der Gewichte ist genau
dann möglich, wenn auch das Ziel teilbar ist; andernfalls ist die Gleichung
unmöglich. Das Entfernen identischer normalisierter Gleichungen erhält die
Konjunktion. Das Argument ist punktweise und verlangt keine unabhängigen Eingänge.

Der BDD-Zustand $N(i,r)$ bedeutet, dass die gewichtete Restsumme ab Position $i$
gleich $r$ ist. Für Ziele außerhalb des noch erreichbaren Intervalls ist er falsch,
am Ende genau für $r=0$ wahr. Sonst gilt

$$N(i,r)\leftrightarrow\bigl(x_i?N(i+1,r-w_i):N(i+1,r)\bigr).$$

Die Auswahlgatter aus Abschnitt 3 setzen diese Rekursion exakt um. Rückwärtsinduktion
über $i$ beweist sowohl die Existenz einer Hilfsvariablenbelegung bei erfüllter
Gleichung als auch die Notwendigkeit der Gleichung bei erfüllter CNF. Die Wurzel
wird wahr gesetzt. `CounterCNF` verwendet diesen Encoder unverändert für E1/E2.

## 5. Abgeschnittener Totalizer für E3

Nach derselben Normalisierung hat E3 Ziel $t\le2$. Negative Ziele oder Ziele
oberhalb der gesamten Gewichtssumme erzeugen eine leere Klausel. Für $t=0$
werden alle beteiligten Variablen falsch gesetzt. Für $t>0$ wird jede Variable
mit Gewicht $w>t$ falsch gesetzt; die übrigen Blätter bestehen aus $w$ Kopien
derselben Variablen. Das $j$-te Blattbit bezeichnet daher korrekt: Beitrag
mindestens $j$. Reicht die verbleibende Gewichtssumme nicht bis $t$, entsteht
wieder die leere Klausel. Sonst ist mindestens ein Blatt vorhanden.

Ein innerer Knoten speichert höchstens $K=t+1$ Schwellenwerte. Für seine
Kindvektoren $A,B$ gelten $A_0=B_0=1$ und ein direkt hinter dem jeweiligen
Vektor liegender Sentinel 0. Für alle programmierten Indizes werden hinzugefügt:

$$\neg A_i\lor\neg B_j\lor R_{i+j},$$
$$A_{i+1}\lor B_{j+1}\lor\neg R_{i+j+1},$$

jeweils nur, wenn der angegebene Elternindex zwischen 1 und der gespeicherten
Elternlänge liegt.

**Induktionsschritt.** Für einen gespeicherten Index $s\le K$ sei die tatsächliche
Summe der beiden Beiträge $a+b$. Ist $a+b\ge s$, so lassen sich verfügbare
$i,j$ mit $i+j=s$, $i\le a$, $j\le b$ wählen. Die erste Klausel erzwingt $R_s=1$.
Ist $a+b<s$, so sind beide tatsächlichen Beiträge kleiner als $K$ und deshalb
nicht durch die Abschneidung verloren. Man kann verfügbare $i,j$ mit
$i+j=s-1$, $i\ge a$, $j\ge b$ wählen: Die Summe der verfügbaren Kindlängen ist
mindestens $s$. Die zweite Klausel erzwingt $R_s=0$.

Sentinels oberhalb einer bei $K$ abgeschnittenen Kindlänge werden in diesem
zweiten Fall nicht benutzt: Dazu wäre schon $i+j+1>K$ nötig. Bei kürzeren
Kindvektoren ist der Sentinel tatsächlich die unerreichbare nächste Schwelle.
Umgekehrt erfüllt die Belegung aller $R_s$ durch ihre echten Schwellenwerte
sämtliche Klauseln. Der Schluss gilt auch für korrelierte Eingänge und mehrfach
vorkommende Primärvariablen.

Induktion über den balancierten Baum beweist die korrekte Bedeutung aller
Hilfsvariablen. Die Einheitsklauseln $R_t$ und, falls vorhanden, $\neg R_{t+1}$
erzwingen genau Summe $t$. Ist die nächste Schwelle nicht allokiert, kann die
Summe diese ohnehin nicht erreichen. Dies beweist die Projektionsäquivalenz
des in `counter.py` verwendeten E3-Encoders.

## 6. Vollständige Gleichungsfamilien und ausgeführte Bindung

`encode_variant` ruft ausschließlich folgende drei Familien auf:

| Familie | Anzahl vor Zusammenfassung | Inhalt |
|---|---:|---|
| E1 | 84 | Alle Außenzeilensummen gleich 12. |
| E2 | 1.176 | Alle Kombinationen aus Außenlabel und Anker. |
| E3 | 3.486 | Alle ungeordneten Paare verschiedener Außenknoten, einschließlich Außenpartnerpaare. |

Die Diagonale der Matrixgleichung E3 ist E1. Symmetrie ersetzt die zweite
Dreieckshälfte; es werden keine anderen Gleichungen ausgelassen.

Der neue Prüfer instrumentiert `exact` **vor** Normalisierung und Totalizerbildung,
löst Produktvariablen in ihre primären Monome auf und erfasst alle Multiplizitäten.
Eine getrennte Konstruktion aus den Labelmengen erzeugt die mathematisch erwarteten
Gleichungen. Beide geordneten Listen stimmen vollständig überein: 4.746 Aufrufe,
2.394 verschiedene Gleichungen. Gleichzeitig erzeugt der instrumentierte Encoder
die unveränderte Basis mit dem oben festgelegten SHA-256-Wert.

Prüfer: [audit_encoder_equations.py](../../src/c2_filter_audit_20261012/audit_encoder_equations.py).
Ergebnis: [encoder_equations.json](../../results/c2_filter_audit_20261012/encoder_equations.json).

Zusammen mit den Abschnitten 2–5 folgt ENC0. Unter L1–L4 des Manuskripts erzeugt
also jeder mathematisch mögliche C2-Graph eine erfüllende Belegung von $F_0$.
Die endliche Gleichungsprüfung ergänzt das allgemeine Gatter- und Induktionsargument;
sie ersetzt es nicht.

## 7. Profilformeln und Grenzen

`anchor_profile.profile_clauses` verbietet für jedes nicht erlaubte Gewicht jede
vollständige Belegung der sechs ausgehenden Pfeile mit genau diesem Gewicht.
Eine solche Klausel ist genau auf dieser Belegung falsch. Ihre Konjunktion ist
daher äquivalent zur angegebenen Gradbedingung. Dies wurde zusätzlich für beide
Mengen $\{4,6\}$ und $\{3,4,6\}$ an allen sieben Ankern in insgesamt 896
Wahrheitstafelfällen bestätigt.

Daraus folgen die genauen Bedeutungen

$$F_{46}=F_0\land\bigwedge_p[d(p)\in\{4,6\}],\qquad
F_{346}=F_0\land\bigwedge_p[d(p)\in\{3,4,6\}].$$

Der Quellpfad `model.build_base` ruft nach der Primärallokation nur `encode_variant`
auf. Weder Matchingnormalformen noch Ankergradordnungen oder C4-Klauseln sind dort
zusätzlich eingebaut. `augment` übernimmt die Basisklauseln unverändert und hängt
nur die angegebenen Klauseln an; lediglich die DIMACS-Kopfzeile wird angepasst.
Die neu reproduzierten Hashes verbinden diese Aussagen mit den historischen Formeln.

Der Nachweis gilt für diese konkrete Basis und ihre beschriebenen Erweiterungen.
Andere historische Kerne, anders erzeugte Formeln oder zusätzliche Symmetriebrechungen
benötigen weiterhin ihre eigene Bindung. Eine verifizierte Compilerkette oder ein
Beweisassistent wurde nicht benutzt. Es wurden weder Solver noch Beweischecker gestartet.
