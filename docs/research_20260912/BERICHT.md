# Conway 99: ausgeführte Forschungsarbeiten zu Algebra, Symmetrie und memetischer Suche

**Stand: 12. September 2026. Auftraggeber: Ralph Beckmann.**

**Nachtrag:** Für den abschließenden Stand nach Review ist das [finale Resümee](../review_synthesis_20260912/FINALES_RESUEMEE.md) maßgeblich. Es ersetzt insbesondere die vorläufige Zahl 40 durch 26 und dokumentiert zusätzliche Gegenprüfungen.

Dieser Bericht führt den Forschungsauftrag vom selben Tag durch überprüfbare Herleitungen, Reproduktionen und begrenzte Experimente aus. Er ist zugleich Übergabe an den unabhängigen Reviewer. Er meldet keinen vollständigen Symmetrieausschluss und keine nachgewiesene Verbesserung einer ganzen evolutionären Kampagne. Die dafür verbleibenden Aufgaben sind ausdrücklich bezeichnet.

## 1. Ergebnis und Entscheidung

Die ergiebigste Übernahme ist die **gewichtete Profilaggregation für den fixpunktfreien Ordnung-3-Fall τ=6**. Eine neu implementierte notwendige Prüfung reduziert die 156 Isomorphietypen des Graphen auf den sechs Dreiecksorbits auf 40. Davon sind 116 Typen exakt ausgeschlossen: 87 durch einen negativen Gram-Eintrag, 25 durch einen negativen Hauptminor und vier durch gespeicherte ganzzahlige Dualzertifikate. Ein zweiter Prüfer benötigt ausschließlich die Python-Standardbibliothek und deckt zusätzlich alle 32.768 beschrifteten Sechsknotengraphen ab. Das ist ein konkreter Fortschritt gegenüber dem geprüften Projektstand, kein weltweiter Neuigkeitsanspruch. Es ist insbesondere kein Ausschluss von 116 vollständigen Conway-Kandidaten oder von 116 der bisherigen L-Zyklentypen.

Für **K66** konnte der strukturierte Weg auf alle vier Wurzeln übertragen werden. Profilidentitäten, originale Gram-Blockzuordnung, Brückenpläne, Blattzuordnung und RUP-Abdeckung sind vorbereitet und geprüft. Die noch zu erzeugenden Einzelbeweise bleiben eigene Pflichten. Damit gibt es eine konkrete Alternative zum langen Aufspaltungsverfahren, aber noch keinen Anlass, laufende Prozesse ohne abschließende Zusammensetzungsprüfung zu ersetzen.

Für die **memetische Suche** sind zwei Befunde unmittelbar relevant. Erstens lässt sich der gesamte Fehler im Ω-Teilraum auf einen 70-dimensionalen invarianten Raum konzentrieren. Das liefert saubere Diagnostik und einen Ansatz für Reparaturen. Zweitens ist die Mutationserzeugung in den gemessenen Ausschnitten der eigentliche Zeitverbraucher. Die implementierte inkrementelle Bewertung ist isoliert ungefähr drei- bis viermal schneller, lässt für Erzeugung plus Bewertung aber nur geringe Gesamtgewinne erwarten. Die erste praktische Optimierungspriorität ist daher die Erzeugung zulässiger größerer Änderungen.

Ein vorgeschlagener allgemeiner Cross-over über alternierende Züge erhält Grade, aber nicht automatisch unsere weiteren Invarianten. Bei drei untersuchten Ω-Elternpaaren ist unter der geprüften Ausrichtung überhaupt kein echtes Kind möglich, das ausschließlich Elternkanten mischt und alle gemeinsamen Entscheidungen festhält. Ein exakter Rangtest weist dies nach. Rekombination muss dort die Ausrichtung ändern oder zusätzliche Reparaturkanten zulassen.

Die publizierte Siebenknotentabelle wird **vorerst nicht als Ausschlussfilter übernommen**. Der Summenfehler wurde nun auch gegen sämtliche 208 Gleichungen im originalen arXiv-TeX bestätigt. Seine Zuordnung zu einzelnen falschen Formeln ist weiterhin offen.

## 2. Arbeitsgrundlage und Grenzen des Zugriffs

Geprüfter aktueller Projektstand: `ibenarb/conway99-research`, Branch `memetic/office-v0.2.0-multinorm-20260911`, Commit `052611b67ee9d083634eaeb5a0de2f2960722fa2`. Historischer Symmetrievergleich: `o3-review-reconciled-20260907`, Commit `b279cd6de420bc4ad64869c8c7f99d653c73a195`. Forschungscode, Ergebnisdateien und Bericht werden separat unter `research_20260912` abgelegt; produktive Operatoren und Controller wurden nicht geändert.

Zusätzliche Grundlage ist das originale Paket `Conway99_PromptA_Audit_20260912.zip` mit CNFs, Profilmodellen und gekoppelten Bäumen. Sein Hash steht im Eingabemanifest. Die aktuellen Ryzen-Dateien und der aktuelle Office-Laufzustand wurden nicht live gelesen. Der letzte mitgeteilte Nebenlaufstand bleibt daher 422/3076; die berichteten 6,61 Stunden sind kein inzwischen verifizierter Fertigstellungstermin. Es wurden keine lokalen Prozesse des Nutzers gestartet, beendet oder verändert.

### Quellenstände

| Quelle | Fixierter Stand | Verwendung und Grenze |
|---|---|---|
| [Lundle22, cyclic lifts](https://github.com/Lundle22/conway-99-cyclic-lifts/tree/eb2487672ed2d0852978fc483ef8a444291b617b) | Commit `eb2487672ed2d0852978fc483ef8a444291b617b` | Modulares Vervollständigungskriterium; eigene exakte Kontrollen und zusätzliche Reduktionen |
| [infinityscroll, f27](https://github.com/infinityscroll/conway99-order3-f27/tree/e8f4d629cdf03b4bb14ebed01e4ebe7e8dbf3f8b) | Commit `e8f4d629cdf03b4bb14ebed01e4ebe7e8dbf3f8b`, Release v0.1.0 | Reenumeration, CNF-Regeneration und frische Prüfung aller 13 DRAT-Beweise |
| [C3-Orbitformalisation](https://github.com/Kuberwastaken/conway99-c3-orbit-restriction/tree/be7b0ae3394721a4c3a1375008a1dbfca44981fc) | Commit `be7b0ae3394721a4c3a1375008a1dbfca44981fc` | Quelltextprüfung; kein Lean-Build |
| [Reimbayev, arXiv:2608.19410](https://arxiv.org/abs/2608.19410) | v1; HTML und Original-TeX über Hash fixiert | Eigener symbolischer Konsistenztest |
| [Ishida, arXiv:2606.29183v2](https://arxiv.org/html/2606.29183v2) | 8. Juli 2026, insbesondere §8.4 | Wichtige nachgetragene algebraische Vorarbeit; spezieller Schluss unten hergeleitet |
| [Crnković–Maksimović, 2020](https://cdm.ucalgary.ca/article/view/62323) | Theoreme 7.1–7.3 | Literaturrestriktionen der Automorphismen; teilweise auf Behbahani–Lam zurückgeführt |
| [Cesarz–Woldar, 2025](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf) | insbesondere Korollar 3.13 | Einschränkung gerader Automorphismengruppen |
| [Makhnev–Minakova, 2004](https://doi.org/10.1515/156939204872374) | Fixpunktklassifikation; zusätzlich [Behbahanis Dissertation](https://spectrum.library.concordia.ca/976720/1/NR63369.pdf), Theorem 1.6 | Literaturgrundlage der Involution mit genau einem Fixpunkt; kein eigener vollständiger Beweis des historischen Satzes |

Diese Quellen sind nicht sämtlich Veröffentlichungen der letzten sieben Tage. Ein Repository-Update, eine neue Zertifikatsverpackung und ein neuer mathematischer Satz sind verschiedene Ereignisse. Insbesondere muss die zuvor fehlende Juli-Vorarbeit in jede Neuigkeitsbewertung aufgenommen werden.

## 3. Was für den gesamten Symmetrieausschluss fehlt

Für eine endliche nichttriviale Automorphismengruppe liefert Cauchys Satz ein Element von Primordnung. Mit den genannten Literaturrestriktionen bleiben die Primordnungen 2 und 3. Die Literatur schließt den Ordnung-3-Fall mit Fixpunkten bereits aus; ein verbleibendes Ordnung-3-Element wirkt frei. Zusammen mit den Ausschlüssen von Gruppen der Ordnung 6 und 9 ergeben sich die bekannten verbleibenden Gesamtgruppen `1`, `C2`, `C3`. Für unsere praktische Ausschlussstrategie genügt bereits die Primordnungsreduktion: **alle Involutionen und alle freien C3-Wirkungen ausschließen**.

Dabei sind zwei Beweisziele auseinanderzuhalten:

* Mit Übernahme der Literatur sind K66 und die anderen festen Dreiecksfälle bereits ausgeschlossene Kontrollfälle. Ihre eigene Zertifizierung verbessert Nachvollziehbarkeit und Verfahrenstechnik.
* Für eine vollständig eigene maschinengeprüfte Kette müssen auch Literaturrestriktionen beziehungsweise deren endliche Reduktionen und sämtliche vorgelagerten Domänenpflichten erfasst werden. Ein K66-Blattlauf leistet dies nicht automatisch.

### 3.1 Ein kurzer algebraischer Weg zu τ=6

Für einen Conway-Graphen ist der Spektralprojektor zum Eigenwert 3

\[
E_3=\frac47I+\frac17A-\frac{2}{77}J.
\]

Er ist über den 3-adischen ganzen Zahlen definiert. Bei einer freien C3-Wirkung ist der Knotenmodul ein freier Modul vom Rang 33 über `Z₃[C3]`. Das Bild des kommutierenden Idempotenten ist ein direkter Summand, also projektiv. Die Gruppenalgebra ist lokal; endlich erzeugte projektive Moduln darüber sind frei. Da der ganzzahlige Rang des Bildes 54 beträgt, ist sein Gruppenalgebrarang 18. Auf jedem regulären C3-Modul hat ein nichttriviales Gruppenelement Spur null. Folglich

\[
0=\operatorname{tr}(gE_3)=\frac{a_1(g)-18}{7},
\]

wobei `a₁(g)` die Anzahl der zu ihrem Bild benachbarten Knoten bezeichnet. Jeder innere Dreiecksorbit trägt drei dazu bei. Deshalb gilt **τ=6**.

Das ist eine eigenständig nachvollzogene Spezialisierung der von [Ishida, §8.4](https://arxiv.org/html/2606.29183v2) behandelten Methode. Es wurde kein vollständiges Audit seiner gesamten Arbeit und kein Beweisassistentenabschluss vorgenommen. Insbesondere überträgt sich der Titel „No involutions in the missing Moore graph“ nicht als Involutionsausschluss auf Conway 99.

### 3.2 Involution in unserem Ω-Koordinatensystem

Unter der Literaturvoraussetzung eines einzigen Fixpunkts `v` muss die Involution die sieben Kanten in `N(v)` jeweils vertauschen. Beweis: Wären `u` und `tu` in `N(v)` nicht benachbart, hätten sie zwei gemeinsame Nachbarn, darunter `v`. Der andere wäre ebenfalls fix, ein Widerspruch. Eine vertauschte benachbarte Knotenpaarung außerhalb von `N(v)` hätte einen eindeutigen gemeinsamen Nachbarn; dieser müsste `v` sein, ebenfalls ein Widerspruch.

Die 84 äußeren Knoten entsprechen eindeutig den ungepaarten Zweiermengen der 14 Nachbarn. Nummeriert man die sieben Partnerpaare als `a↔a+7`, ist damit auch die äußere Involution eindeutig bestimmt: `{a,b}↔{a+7,b+7}`. **Es genügt in diesem Rahmen eine kanonische Involution**, nicht die Suche über alle Permutationen von 99 Knoten. Für H ist zusätzlich die Kommutation mit dieser Permutationsmatrix zu erzwingen. Dies ist eine konkrete Modellreduktion, aber der entsprechende vollständige SAT-/CP-Ausschluss wurde hier nicht ausgeführt.

## 4. Quotient, Phasen und modulares Vervollständigen

### 4.1 Richtige Verbindung zum bestehenden Encoder

Der bestehende O3-ABC-Ansatz ist bereits ein **Quotientenmodell**. Für τ=6 verwendet seine primäre S-Beschreibung 501 Bits; hinzu kommen viele Hilfsvariablen. Es wäre falsch, diese mit 198 Phasenvariablen zu vergleichen und daraus unmittelbar eine Beschleunigung zu folgern: Die Phasen lösen eine nachgelagerte Aufgabe, nachdem ein exakter Quotient vorliegt.

Für einen exakten Quotienten R gelten

\[
R^2+R-12I=6J,\quad R\mathbf1=14\mathbf1,
\]

mit Diagonale 0/2 und legalen übrigen Einträgen. Die 198 nichttrivialen ungeordneten Supportstellen entsprechen Phasenentscheidungen. Definiert man `B=(R+I) mod 3`, dann ist B idempotent. In der π-adischen Entwicklung mit `π=1−ω` ergibt sich die lineare Bedingung

\[
BZ+ZB-Z=0
\]

und die zweite Bedingung

\[
BU+UB-U=B+I+2J-Z^2.
\]

Z ist schiefsymmetrisch; U ist durch die legale Eintragstabelle aus R und Z bestimmt, nicht frei optimierbar. Die Vollständigkeit beruht auf der Beschränkung der nichtnegativen Fourier-Koeffizienten: Bei Summe sechs erzwingt Teilbarkeit durch π³ die Gleichverteilung. Diese Voraussetzungen sind wesentlicher Bestandteil des [Lundle-Kriteriums](https://github.com/Lundle22/conway-99-cyclic-lifts/tree/eb2487672ed2d0852978fc483ef8a444291b617b).

### 4.2 Eigene weitere Reduktion

Da B symmetrisch und idempotent ist, zerfällt der Raum orthogonal in Bild und Kern. Die lineare Bedingung lässt für Z nur die Kreuzblöcke zu. Für τ=6 hat B Rang 18: Das Quotientenspektrum ist `14¹,3¹⁸,(−4)¹⁴`; das charakteristische Polynom von R+I reduziert sich auf `x¹⁵(x−1)¹⁸`. Der abstrakte Raum der schiefsymmetrischen Lösungen hat somit Dimension `18·15=270`. Erst Supportbedingungen reduzieren auf die tatsächlich zulässigen Phasen.

Mit Q=I−B folgt aus der zweiten Gleichung

\[
BUB=2B-BZ^2B,\qquad QUQ=-Q-2J+QZ^2Q.
\]

Die Kreuzblöcke von U werden durch diese Gleichung nicht auf null gesetzt. Ein Basiswechsel muss außerdem die bilineare Form, den Support und das legale Alphabet mittransformieren. Bloß 18/15 Blöcke aufzuschreiben erzeugt keinen äquivalenten binären Suchraum.

Orbitweise Phasenverschiebungen liefern `Z↦Z+[B,D_h]`. Der Quotientensupport ist zusammenhängend; daher kann ein Spannbaum 32 Gaugefreiheiten entfernen. Das Skript `f3_lift.py` berechnet die F3-Kernbasis und prüft diese Differenz der Nullitäten. Die verbleibende Dimension ist höchstens `198−32=166`; ein genauer Wert für einen echten τ=6-Quotienten wurde nicht gemessen, weil kein solcher vollständiger Eingabequotient vorlag.

### 4.3 Kontrollen und die Näherungsgraphen-Lücke

Exakt geprüft wurden die skalare Phasentabelle, 25 zufällige legale Alphabetmatrizen und die vollständige Residuenentwicklung einschließlich eines nichtverschwindenden Quotientenfehlers. Eine zusätzliche Dimensionskontrolle mit n=9 und Rang B=4 ergibt die erwarteten 20 linearen Freiheitsgrade. Ungültige Quotienten werden zurückgewiesen.

Für einen ungenauen Quotienten bleibt bereits der Term `E_Q=R²+R−12I−6J`. Er darf in der π-adischen Entwicklung nicht verschwinden gelassen werden. Deshalb sind kleine modulare Residuen eines Näherungskandidaten kein Vervollständigkeitsbeweis. Die Tests ersetzen keinen erfolgreichen Lift einer echten Conway-Quotientenlösung.

## 5. Profilaggregation für τ=6: 156 → 44 → 40

### 5.1 Mathematisches Modell

Schreibe den Quotienten, mit den sechs Dreiecksorbits zuerst, als

\[
R=\begin{pmatrix}2I+X&C\\C^T&U\end{pmatrix},\qquad U=S_U+2L.
\]

X ist ein einfacher Sechsknotengraph. C ist binär. L ist ein 2-regulärer Graph auf den 27 übrigen Orbits, S_U ist einfach und zu L kantendisjunkt. Aus der Quotientengleichung folgen

\[
CC^T=G=6I+6J-X^2-5X,
\]
\[
CU=6J-3C-XC.
\]

Für einen Spaltenprofiltyp `r∈{0,1}⁶` sei `n_r` seine Häufigkeit und `t(r)=6·1−3r−rX` sein gewichteter Bedarf. Notwendig sind `0≤t_j(r)≤14−|r|`. Man verwendet nur diese Profile und führt ganzzahlige Anzahlen `s_rs,l_rs` der Kanten zwischen ihren Klassen ein. Bei gleichen Klassen zählt eine Kante in der Gradbilanz zweimal.

Die Bedingungen sind:

1. `Σ n_r=27` und `Σ n_r r_i r_j=G_ij`.
2. Die S-Gradbilanz der Klasse r ist `(10−|r|)n_r`; die L-Gradbilanz ist `2n_r`.
3. Die mit 1 beziehungsweise 2 gewichtete Summe der Nachbarprofile ist `t(r)n_r`.
4. Eine S-Kante verlangt `r·s≤5`, eine L-Kante `r·s≤4`. Dies folgt aus `U²+U+CᵀC=12I+6J` und der Nichtnegativität von U².

Das Modell verwendet sichere globale Schranken `n_r≤27`, `s_rs≤135`, `l_rs≤27`. Es verlangt noch keine tatsächliche Realisierung auf 27 unterscheidbaren Knoten, keine konkrete Zykluspartition von L und keine Phasen. **Jeder zulässige Quotient liefert eine Lösung dieses Modells; die Umkehrung wird nicht behauptet.**

### 5.2 Gemessene und zertifizierte Ergebnisse

| Stufe | Anzahl | Evidenz |
|---|---:|---|
| Alle Sechsknotentypen X | 156 | Unabhängig alle 32.768 beschrifteten Graphen durch disjunkte Permutationsorbits abgedeckt |
| Ausschluss durch negativen Eintrag von G | 87 | Ganze Zahlen |
| Weiterer Ausschluss durch negativen Hauptminor | 25 | Exakte rationale Determinante |
| Danach verbleibend | 44 | Keine numerische PSD-Toleranz verwendet |
| Weitere Ausschlüsse durch Aggregation | 4 | Ganzzahlige Dualzertifikate, Typindizes 19,20,36,37 |
| Verbleibend | **40** | Davon zehn mit exakter Aggregatlösung, 30 nach begrenzter Suche unentschieden |

Der Scout erhielt pro Typ maximal zwei Sekunden Solverzeit. Deshalb ist „unentschieden“ weder ein Machbarkeitsnachweis noch ein Ausschluss. Die zehn gespeicherten ganzzahligen Lösungen wurden gegen das Matrixmodell und separat gegen die Profilbedeutung nachgerechnet.

Für die vier weiteren Ausschlüsse ist das numerische Solverurteil nicht die Vertrauensbasis. Der gespeicherte ganzzahlige Vektor w erfüllt für `Az=b, 0≤z≤u` exakt

\[
b^Tw>\sum_j u_j\max(0,(A^Tw)_j).
\]

Dies widerspricht jeder reellen, also auch jeder ganzzahligen Lösung. Die positiven Abstände sind 3129, 31603, 34184 und 55130. Die unabhängige Implementierung `replay_tau6_exact.py` rekonstruiert die Koeffizienten direkt und prüft alle 116 Ausschlüsse ohne NumPy, SAT, LP oder MILP.

**Übernahme:** Diese X-Ausschlüsse können vor einer vollständigen τ=6-Quotientensuche angewendet werden, sofern ihre sechs ausgezeichneten Orbits genau der hier definierten Menge entsprechen. Die 40 X-Typen sind eine andere Klassifikation als die im Projekt verbliebenen 101 L-Zyklentypen. Ihre Zahlen oder Reduktionsfaktoren dürfen nicht multipliziert werden. Erst die gemeinsame Zuordnung kann die tatsächliche Entlastung der offenen Instanzen zeigen.

## 6. K66: vier konkrete Ersatzpläne

Die Profilidentität

\[
z_i^2-\sum_{j\in Q\setminus\{i\}}z_i z_j=4[\,z_i=2\,]
\]

wurde auf der jeweiligen legalen Profildomäne jeder Wurzel geprüft. Sie ist keine Identität für beliebige z. Die vier zugehörigen Gram-Zielwerte erzwingen jeweils genau einen Träger; die betreffenden Profile haben Kapazität eins. Die Pläne enthalten die originalen Gram-CNF-Blöcke, CNF-Hashes und Brückenannahmen.

| Wurzel | Brücken | Blätter | RUP-Abdeckungsschritte |
|---|---:|---:|---:|
| v4_09322 | 118 | 2551 | 463 |
| v4_09323 | 113 | 1519 | 286 |
| v4_09332 | 135 | 2722 | 453 |
| v4_09333 | 112 | 3076 | 527 |

Die gekoppelten ursprünglichen Bäume wurden exakt erneut durchlaufen: 3014, 1805, 3175 beziehungsweise 3603 Knoten. Für alle vier wurde die explizite RUP-Abdeckung mit geordneten Hinweisen unabhängig nachgerechnet. Bei v4_09333 stimmt deren SHA-256 mit dem bisherigen Pilot überein.

**Zertifizierungsgrenze:** Die Abdeckung setzt die aufgeführten Brücken- und Blattklauseln voraus. Sie beweist diese Klauseln nicht. Die neuen Pläne für die anderen Wurzeln sind keine abgeschlossenen LRAT/Cake-Läufe. Original-CNF-Hashes wurden geprüft; es wird hier keine erneute vollständige Regeneration aller Ausgangsencoder behauptet. Die vorgelagerten, historisch 125 NeighborStar-Domänenpflichten bleiben getrennt zu behandeln.

Nach Abschluss des Nebenlaufs ist die sinnvolle nächste Messung ein kleiner strukturierter Blattpilot für die anderen Wurzeln mit Beweisprüfung. Aus der Anzahl 1519 gegenüber 3076 allein folgt keine halbierte Laufzeit. Der Hauptlauf besitzt weiter den Wert eines unabhängigen Vervollständigungswegs; sein hoher Wiederholungsaufwand macht einen strukturierten Ersatz aber nun konkret prüfbar.

## 7. Memetik: Zustandsräume und zusätzliche Algebra

### 7.1 Tatsächlich vorhandene Implementierung

Office v0.2.0 vergleicht L1, L2 und L∞ auf denselben 64 paarweise nichtisomorphen Startgraphen: 32 Ω- und 32 λ-Kandidaten aus zehn Gründerfamilien. Die gespeicherte Konfiguration verwendet drei Arbeiter, acht Versuche pro Elternaufgabe, 30 CPU-Sekunden beziehungsweise 256 Bewertungen, lokale Abstiege, Tabu und eine Aufwärmphase. Es wurde kein neuer Live-Generationsstand aus diesen Startdaten abgeleitet.

λ erhält Einfachheit, Grad 14 und genau einen gemeinsamen Nachbarn auf jeder Kante. Ω erhält zusätzlich den kanonischen Wurzel-/Nachbarschaftsrahmen und die P-Margen des äußeren H-Blocks. Jeder exakte Conway-Graph lässt sich nach Wahl einer Wurzel in diesen Rahmen bringen; nicht jeder 14-reguläre Näherungsgraph liegt darin. Ein beliebiger Wechsel zwischen den Zustandsräumen benötigt deshalb eine eigene Konstruktion.

Für einfache 14-reguläre Graphen setze `E=A²+A−12I−2J` und `F=Σ_{i<j}E_ij²`. Die bereits im Projekt bekannten Identitäten sind

\[
E\mathbf1=0,\quad F=4C_4+6T-9702.
\]

In λ ist `T=231`, also `F=4(C₄−2079)`. Außerdem ist die L1-Summe zweimal die Summe der positiven Paarfehler. Diese Beziehungen sind keine neuen unabhängigen Selektionsmerkmale. Fehlerhistogramm und sortierte Fehlergrade sind bereits implementiert; sie dürfen nicht als neue Operatoren ausgegeben werden.

### 7.2 Konzentration auf 70 Dimensionen

P ist die ungerichtete Inzidenzmatrix von `K14` ohne die sieben Partnerkanten; M ist deren Permutationsmatrix. Dann

\[
PP^T=11I+J-M,\qquad (PP^T)^{-1}=(22I+2M-J)/240.
\]

Die Ω-Marge ist äquivalent zu `HPᵀ=Pᵀ(J−I−M)`. Somit ist das Bild von Pᵀ invariant; dort besitzt H das feste Spektrum `12¹,(−2)⁶,0⁷`. Zusammen mit Wurzel und Nachbarschaft entsteht ein fester 29-dimensionaler A-Anteil mit Spektrum `14¹,3¹⁴,(−4)¹⁴`.

Mit dem orthogonalen Projektor

\[
\Pi=I-P^T(PP^T)^{-1}P
\]

bleibt `ker P` von Dimension 70. Für die Einschränkung T von H darauf gilt bereits für jeden Ω-Zustand `tr T=0`, `tr T²=840`. Eine Lösung verlangt `Spec(T)=3⁴⁰,(−4)³⁰` und

\[
F=\tfrac12\|T^2+T-12I\|_F^2.
\]

Alle ganzzahligen Identitäten, einschließlich `E_HPᵀ=0` und der Kommutation von E_H mit H, wurden auf allen 32 Ω-Starts geprüft. Dies isoliert den veränderlichen Fehler mathematisch. Es verringert nicht automatisch die Zahl legaler binärer H-Matrizen.

Die sortierten Eigenwerte liefern über Hoffman–Wielandt eine untere Schranke für die Zahl unterschiedlicher Kanten zu jeder exakten Ω-Lösung:

\[
d_{\rm edge}\ge\tfrac12\sum_{i=1}^{70}(\lambda_i(T)-\lambda_i^*)^2.
\]

Die gelieferten Zahlen wurden in Gleitkommaarithmetik berechnet und sind deshalb Diagnostik, keine zertifizierten harten Schranken. Als neues Diversitätsmerkmal bietet sich der freie Spektralverlauf bei gleicher Fitness an. Ob er spätere Verbesserung vorhersagt, ist nicht gemessen; die konstanten ersten beiden Momente können dafür jedenfalls nicht dienen.

## 8. Mutation, Bewertung und Cross-over

### 8.1 Exakte lokale Aktualisierung und gemessener Nutzen

Für `A'=A+Δ` folgt direkt

\[
E'=E+AΔ+ΔA+Δ^2+Δ.
\]

Wenn Δ nur Kanten zwischen einer Menge betroffener Knoten verändert, können Paarfehler außerhalb der zu diesen Knoten inzidenten Paare unverändert übernommen werden. `memetic_incremental.py` implementiert die vollständigen bestehenden Kennzahlen entsprechend. Auf 139 legalen Änderungen aus zehn Gründern stimmen alle Kennzahlen mit vollständiger Neuberechnung überein; auch die Rücknahme jeder Änderung wurde geprüft.

Sechs wechselweise angeordnete Zeitmessungen auf identischen vorbereiteten Kindern ergeben ungefähr **2,92–4,07-fache Bewertungsbeschleunigung**. Der separate Kostenpilot umfasst zehn Gründer und drei Seeds, je maximal zwei CPU-Sekunden und 32 erzeugte Änderungen. Dort beträgt der aggregierte Bewertungsanteil etwa 0,63 % in Ω und 6,34 % in λ. Unter Einsetzen der gemessenen Bewertungsbeschleunigung liegt der Median des optimistischen Gesamtgewinns für Erzeugung plus Bewertung nur bei etwa **0,33 % beziehungsweise 4,2 %**.

Das sind statische Elternströme. Ausrichtung, Kanonisierung, CP-Cross-over und Kampagnenverwaltung sind nicht enthalten. Ein festes Bewertungslimit erhöht sich durch schnellere Bewertung ebenfalls nicht von selbst. **Entscheidung:** Korrekte inkrementelle Bewertung ist verfügbar, besitzt aber keine erste Integrationspriorität. Die Messung begründet zunächst Arbeit an der legalen Mutationserzeugung.

### 8.2 Algebraisch geführte Änderungen

Die bestehenden Ω-Produktänderungen `Δ=xyᵀ+yxᵀ` mit `Px=Py=0` und disjunkten Trägern erhalten die P-Marge. Binärität und erlaubte Vorzeichen bleiben separat zu prüfen. Eine größere, konkret formulierbare Reparatur wählt einen äußeren Knotenbereich S, fixiert alle Kanten außerhalb von S×S und löst darin die binären Entscheidungen unter `PΔ=0` neu. Die oben angegebene Fehleraktualisierung ermöglicht eine exakte anschließende Bewertung. Für λ muss zusätzlich die gemeinsame-Nachbar-Bedingung auf allen betroffenen Kanten kontrolliert werden; Gradtreue allein genügt nicht.

Als Selektionsregel für einen solchen Pilot ist eine feste Quote für gute F-Werte und eine zweite Quote für strukturell verschiedene Fehlerprofile sinnvoll. Ein freier Spektraldeskriptor kann in Ω experimentell hinzutreten. Dies ist eine spezifizierte Hypothese, kein beobachteter Vorteil. Vor einer Erhöhung der Operatorvielfalt sollte man insbesondere redundante erneute Durchmusterung derselben zulässigen Produktträger messen und vermeiden.

### 8.3 Warum naiver alternierender Cross-over scheitert

Bei zwei gleichgradigen einfachen Eltern sind rote und blaue Differenzkanten an jedem Knoten gleich zahlreich. Paarung entgegengesetzter Farben zerlegt sie in kantenfremde alternierende geschlossene Züge. Der vollständige Austausch eines solchen Zuges erhält jeden Grad. Da hinzugefügte Kanten aus der Differenz stammen, entstehen weder Mehrfachkanten noch Schleifen.

Die konkreten Kontrollen zeigen jedoch: Keiner der einzeln ausgetauschten Züge der vier untersuchten Elternpaare erhielt die volle jeweilige Arm-Invariante. Dies widerlegt die automatische Übertragung von Gradtreue auf Ω oder λ.

Ein stärkerer Ω-Test bildet die ganzzahlige Matrix D der Änderungen der P-Margen für jede Differenzkante. Beide Eltern sind gültig, also `D·1=0`. Ist der Rang modulo einer Primzahl bei d Differenzkanten genau d−1, dann ist der rationale Kern genau `span(1)`. Eine binäre Auswahl aus diesem Kern ist nur 0 oder 1: Es gibt unter dieser Ausrichtung kein echtes reines Mischkind.

| Elternpaar | Differenzkanten d | Rang modulo 1.000.003 | Ergebnis |
|---|---:|---:|---|
| H_minus / H_plus | 16 | 15 | Nur die beiden Eltern |
| Ω-Paar 0 | 818 | 817 | Nur die beiden Eltern |
| Ω-Paar 1 | 822 | 821 | Nur die beiden Eltern |

Der vorhandene CP-Cross-over behandelt P-Margen bereits korrekt. Der neue Test ist eine exakte ausreichende Vorprüfung; seine Laufzeitersparnis gegenüber diesem Solver ist noch nicht gemessen. Die Aussage gilt nur für die festgelegte Ausrichtung, gemeinsame Kanten und erlaubte Differenzkanten. Sie verbietet weder andere Ausrichtungen noch Reparaturen mit zusätzlichen Kanten und beweist keine Unzusammenhängendheit des Ω-Suchraums.

### 8.4 Welche Ausschlüsse sicher sind

| Bedingung | Harte Anwendung | Anwendung auf mutierbare Kandidaten |
|---|---|---|
| Exakter X-/Profilwiderspruch | Quotientenzweig mit festem X und erfüllten Modellvoraussetzungen verwerfen | Keine allgemeine Populationssperre |
| K66-Trägerwiderspruch | Konkrete zertifizierte Annahmenkombination ausschließen | Nur wenn Nachkommen diese Annahmen beibehalten |
| Freie-C3-Bedingung τ=6 | Suche nach exakten freien C3-Lösungen einschränken | Keine Bedingung für beliebige Dreiergruppierung |
| Cross-over-Rang d−1 | Diesen ausgerichteten Mischraum überspringen | Eltern nicht generell aussondern |
| F>0, spektraler Abstand | Aktueller Graph ist keine Lösung; Distanzdiagnose | Gerade der Normalfall eines Suchzustands |
| Siebenknotentabelle | Derzeit keine sichere neue Verwendung | Kein Filter und keine begründete Fitnessformel |

## 9. Reimbayev-Audit und interne Fehlerkorrektur

Die 208 publizierten Häufigkeiten wurden symbolisch aus HTML-LaTeX und MathML ausgelesen und dann einzeln gegen das originale arXiv-TeX geprüft. Alle drei Darstellungen stimmen überein. Bei n=99,k=14 ergibt ihre Summe 14.792.997.384 statt `binom(99,7)=14.887.031.544`: Es fehlen **94.034.160**. Die freien Parameter können diese Differenz nicht beheben. Die Kontrolle n=9,k=4,n₃=z₁₁=0 liefert dagegen korrekt 36 und keine negativen Einträge.

Der allgemeine Summenfehler nach Einsetzen von `n=(k²+2)/2` ist

\[
-\frac{k(k-4)(k-2)(k^2+2)}{336}
(19k^4-456k^3+4484k^2-21752k+42008).
\]

Der Befund betrifft damit nicht nur eine beschädigte HTML-Darstellung. Es wurde keine einzelne Formel als Ursache identifiziert und keine Korrektur erfunden. Die Isomorphietypzuordnung und sämtliche kombinatorischen Einzelherleitungen wurden nicht unabhängig rekonstruiert; eine Liste neu freigegebener Siebenknotenfilter ist daher leer. Quelle: [Reimbayev, arXiv:2608.19410](https://arxiv.org/abs/2608.19410).

Ein eigener früherer Reviewtext enthält außerdem eine unbewiesene Umkehrung: Aus einer durch einen Apex-Move erzeugten Lösungssignatur bei F=160 folgt nicht, dass jeder λ-Graph mit diesem Wert und entsprechendem Prismaprofil genau einen Apex-Move von einer Lösung entfernt ist. Die dortige Herleitung zeigt nur eine notwendige Signatur. Bis zu einem zusätzlichen Beweis ist diese Behauptung zurückzunehmen. Das Profil kann einen explizit zu prüfenden Rückwärtsversuch auslösen. Ein Gegenbeispiel zur Umkehrung wurde hier nicht konstruiert.

## 10. Satzregister und Beweiskette

| Kennung | Aussage | Status / Reichweite |
|---|---|---|
| S1 | Freie C3-Wirkung erzwingt τ=6 | Algebraisch hergeleitet mit Standard-Modulsatz; Juli-Vorarbeit, kein Lean-Abschluss |
| S2 | B hat Rang 18 bei exaktem τ=6-Quotienten; lineare Z-Struktur und Gauge | Herleitung plus exakte Kontrollen; kein tatsächlicher Quotientenlift |
| S3 | 116 der 156 X-Typen unmöglich | Exakte Zertifikate einer notwendigen gewichteten Relaxation; unabhängiger Standardbibliothek-Prüfer |
| S4 | Alle vier K66-Abdeckungspläne korrekt | Exakte RUP-Prüfung unter Brücken-/Blattannahmen; diese bleiben zu zertifizieren |
| S5 | Ω-Fehler lebt auf ker P von Dimension 70 | Algebraische Herleitung und 32 exakte Startkontrollen |
| S6 | Inkrementelle Bewertung stimmt mit Vollbewertung überein | Exakte lokale Formel; 139 geprüfte Änderungen einschließlich Rücknahme |
| S7 | Drei ausgerichtete Ω-Mischräume haben nur Elternlösungen | Exakter modularer Rangtest; kein globales Cross-over-Verbot |
| S8 | Siebenknotentabelle verletzt notwendige Summenidentität | Symbolisch gegen Originalquelle bestätigt; keine Einzelkorrektur |

| Übergang | Was vorliegt | Was fehlt |
|---|---|---|
| Graph → freie Orbitstruktur | Literaturrestriktionen; spezieller τ=6-Schluss | Vollständige Formalisierung aller historischen Eingaben |
| Graph → exakter Quotient | Bekannte Modellherleitung und vorhandener Encoder | Neue end-to-end-Beweisassistentenverbindung |
| Quotient → Profile | Notwendige Block- und Gewichtsgleichungen | Rückrichtung absichtlich nicht behauptet |
| Aggregation → tatsächlicher Quotient | Zehn Aggregatzeugen | Knotenrealisierung, L-Zyklen, sämtliche Paarbedingungen |
| Exakter Quotient + legale Phasen → Graph | Modulares Kriterium und Kontrollen | Reale τ=6-Instanz, gemessene Phasensuche |
| Profil-/Trägerargument → CNF-Zertifikat | Originalblockpläne, Hashes, vier Abdeckungen | Neue Einzelbeweise, Encoder-/Domänenkette |
| Arithmetik → Lean-Satz | Externer bedingter C3-Baustein | Graph-, Spektral- und Dreiecksfelder konstruktiv liefern; Build |
| Lokale Bewertungsbeschleunigung → bessere Suche | Bewertungs- und Kostenpiloten | Kampagnenvergleich mit gleicher Zeit und gleichen Seeds |

Das f27-Paket wurde bis zu frischen DRAT-Prüfungen aller 13 Beweise reproduziert, einschließlich der sechs zusätzlich regenerierten Ausgangs-Gram-CNFs. Sein Quotientenausschluss ist logisch stärker als ein bloßer Lift-Ausschluss desselben τ=27-Falls. Die vollständige mathematische Reduktion ist dadurch trotzdem nicht in LRAT/Cake oder Lean formalisiert.

## 11. Priorisierter begrenzter weiterer Recheneinsatz

**Symmetrie, zuerst:** Die 40 X-Typen mit den tatsächlich offenen L-Zyklentypen des Projekts zusammenführen. Zunächst die zehn Aggregatzeugen auf echte U-Realisierbarkeit prüfen; parallel dazu keine unbeschränkte Phasensuche ohne exakten R starten. Ein nächster lokaler Pilot sollte höchstens 30 Minuten Gesamtbudget erhalten, pro ausgewähltem Paar (X,L) feste Limits, gespeicherte Eingaben und genaue Statuscodes. Hauptmessgröße ist Zahl zusätzlich exakt ausgeschlossener offener Instanzen beziehungsweise gefundener exakter Quotienten. Zeitüberschreitungen bleiben offen. Dieses Budget ist ein vorgeschlagener Rahmen, keine Laufzeitprognose; der Pilot wurde nicht auf dem Ryzen gestartet.

**K66:** Nach tatsächlichem Abschluss des Nebenlaufs einschließlich Komposition pro anderer Wurzel eine begrenzte Stichprobe strukturierter Blattbeweise mit Solver- und Checkerzeit messen. Erst damit den Hauptlauf bewerten. Keine Schätzung der gesamten Symmetriezeit aus K66-Blattzahlen.

**Memetik, zuerst:** Erzeugungskosten nach Operatorfamilie und wiederholten Trägerprüfungen aufschlüsseln; dann Caching beziehungsweise gezielte zulässige Reparatur testen. Für einen neuen Operator genügen zunächst drei feste Seeds auf denselben ausgewählten Ω- und λ-Gründern, gleiche CPU-Budgets und eine unveränderte Baseline. Primär vergleichen: bestes F über Zeit, Zahl tatsächlich legal bewerteter Kinder und Plateauflucht; zusätzlich Herkunft, Fehlerprofil und Reparaturzeit. Größere Kampagnen erst bei einem wiederholbaren Vorteil. Die inkrementelle Bewertung kann dabei identisch in beiden Armen verwendet werden, um einen Operatorvorteil nicht mit Bewertungsleistung zu verwechseln.

**Cross-over:** Erst nach Ausrichtung den Rangtest messen und gegen vorhandenen CP-Cross-over vergleichen. Bei erwiesen leerem echtem Mischraum eine neue Ausrichtung oder einen explizit begrenzten Reparaturbereich wählen. Ein Vergleich gegen gleich teure Mutationen bleibt erforderlich.

**Zurückstellen:** Siebenknotenfilter bis zur unabhängigen Einzelkorrektur; flächige Lean-Formalisierung vor Schließung der konkret entscheidenden Graph-zu-Modell-Lücke; globale Restzeitversprechen. Die Evidenz rechtfertigt strukturelle τ=6-Reduktion und Optimierung legaler Mutationserzeugung. Sie rechtfertigt noch keine bevorzugte Großkampagne aufgrund eines behaupteten Gesamtspeedups.

## 12. Auftrag an den Reviewer

Bitte zuerst die stärksten neuen Aussagen angreifen: (1) die gewichtete τ=6-Relaxation einschließlich Profilverwerfung und globaler Variablenschranken; (2) den Standardbibliothek-Replay der vier Dualzertifikate; (3) die Gültigkeit der P-Zerlegung für den tatsächlich implementierten Ω-Raum; (4) die Voraussetzungen des modularen Liftkriteriums und die Behandlung von U; (5) die Reichweite des Cross-over-Rangarguments.

Danach die K66-Brücken gegen die originalen vier Gram-Blöcke und die Abdeckung gegen die gelisteten Annahmen prüfen. Die Summenprüfung der Siebenknotentabelle soll unabhängig wiederholt werden; die vierte Potenz oder eine einzelne Häufigkeit nicht allein zur Reparatur der Summe verändern. Die zurückgenommene Apex-Umkehrung verdient einen separaten Beweis oder ein Gegenbeispiel.

Erwarteter Rücklauf: pro Satz `bestätigt / widerlegt / offen`, genaue Voraussetzung oder Gegeninstanz, ausführbarer Prüfer und getrennte Einschätzung von mathematischer Gültigkeit, Zertifizierungsreife und Suchwirkung. Aus diesem Auftrag folgt kein Auftrag, laufende Prozesse, Produktionscode oder fremde Repository-Zweige zu verändern.
