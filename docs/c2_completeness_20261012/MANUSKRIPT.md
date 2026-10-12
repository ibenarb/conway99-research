# Involutionen im Conway-99-Problem: Rahmenreduktion und bedingte Profilausschlüsse

**Arbeitsfassung 0.1 vom 12.10.2026. Kein allgemeiner C2-Ausschluss.**

## Zusammenfassung und Aussagegrenze

Wir untersuchen einfache ungerichtete stark reguläre Graphen mit Parametern
$(99,14,1,2)$ und einer Involution. Ein zitierter Fixpunktsatz führt zu einem
vollständigen Rahmenmodell auf 84 Außenknoten beziehungsweise 42 Zweierorbits.
Wir begründen dessen Matrixbedingungen, die zulässigen Rahmenumbenennungen und
elf lokale Matchingtypen. Ein bedingter Ausschluss des Zweigs, in dem alle sieben
Ankergrade zu $\{3,4,6\}$ gehören, reduziert einen hypothetischen C2-Fall auf einen
Anker mit Grad höchstens zwei. Für einen Anker minimalen Grades ergeben sich dabei
acht lokale Matchingtypen. Deren vollständiger Ausschluss ist hier offen.

Die abgeschlossenen Rechnungen decken eine Liste mit 234.691 Profilcodes unter
übernommenen Voraussetzungen ab. Die Einordnung dieser Liste in einen Census
mit 7.388.648 Vertretern und dessen historische Ausschlussstufen wird gesondert
dokumentiert. Eine leere Restliste ersetzt weder den Vollständigkeitsnachweis des
Census noch die Rechtfertigung seiner mathematischen Einschränkungen.

## 1. Begriffe und Ziel

Eine Involution ist ein nichtidentischer Automorphismus $t$ mit $t^2=1$.
Das angestrebte Endergebnis lautet:

> **Zielsatz, derzeit unbewiesen:** Kein $srg(99,14,1,2)$ besitzt eine Involution.

Eine stärkere Nicht-Existenzbehauptung für alle solchen Graphen wird nicht erhoben.
Aussagen zu C3 werden hier nicht behandelt. Ein **C4** im Folgenden bezeichnet
stets einen Vierzyklus im gegenseitigen Ankergraphen, keine Automorphismenordnung.

## 2. Fixpunktreduktion und vollständiger Rahmen

**Literatursatz L1.** Jede Involution eines $srg(99,14,1,2)$ hat genau einen Fixpunkt.
Dies ist der Fall $|g|=2$ in Satz 1 von Makhnev–Minakova [MM04], Druckseite 96.
Die Satzstelle wurde am 12.10.2026 im Originalscan geprüft; die Behandlung der
Involutionen steht auf Druckseiten 100–101. Der Satz wird als veröffentlichtes
Resultat zitiert. Die vorgelagerte Klassifikation der Fixpunktgraphen wird hier
nicht als unabhängig neu bewiesen ausgegeben.

Sei $o$ dieser Fixpunkt und $A=N(o)$. Wegen $\lambda=1$ hat jeder Knoten in
$G[A]$ genau einen Nachbarn. Also ist $G[A]=7K_2$. Bezeichne seine Kanten mit
$\{a_p,b_p\}$, $0\le p<7$, und den Matchingpartner von $a$ mit $a^*$.

**Lemma L2 (Außenlabels).** Die übrigen 84 Knoten stehen bijektiv zu den ungeordneten
Zweiermengen $L=\{a,b\}\subset A$ mit $b\ne a^*$.

*Beweis.* Ein Nichtnachbar von $o$ hat genau zwei gemeinsame Nachbarn mit $o$.
Diese beiden Nachbarn können keine Kante in $G[A]$ bilden, da diese Kante bereits
$o$ als einzigen gemeinsamen Nachbarn besitzt. Umgekehrt haben zwei verschiedene
nicht gepaarte Anker genau zwei gemeinsame Nachbarn. Einer ist $o$. Der zweite
liegt außerhalb von $A$, weil in $7K_2$ kein Knoten zu beiden Ankern benachbart ist.
Er ist eindeutig. Die Zahl der Labels ist $\binom{14}{2}-7=84$. ∎

**Lemma L3 (Wirkung und verbotene Kanten).** Es gilt $t(a)=a^*$ auf $A$ und
$t(x_{\{a,b\}})=x_{\{a^*,b^*\}}$. Auf den Außenknoten entstehen genau 42 Zweierorbits;
für jeden Außenknoten $x$ gilt $x\not\sim t(x)$.

*Beweis.* Auf $A$ gibt es keine Fixpunkte. Wäre $t(a)$ nicht der Matchingpartner,
so wäre das zulässige Label $\{a,t(a)\}$ unter $t$ fest. L2 würde damit einen
zweiten Fixpunkt liefern. Die Wirkung auf Labels folgt aus ihrer Eindeutigkeit.
Ein festes Außenlabel müsste ein Partnerpaar sein, das ausgeschlossen wurde.
Wären $x,t(x)$ benachbart, wäre ihr einziger gemeinsamer Nachbar unter $t$ fest,
also $o$. Dieser ist aber zu keinem Außenknoten benachbart. ∎

L1–L3 behandeln sämtliche C2-Fixpunkt- und Orbitfälle unter dem zitierten Satz L1.
Die Auswahl eines Vertreters aus jedem Außenorbit ist eine Koordinatenwahl.

## 3. Adäquanz des mathematischen Modells

Sei $R$ die $84\times14$-Inzidenzmatrix der Außenlabels, $K$ die Matchingmatrix auf
$A$ und $M$ die Außenadjazenzmatrix. Wir verlangen: $M$ ist symmetrisch, binär,
hat Nulldiagonale, ist $t$-invariant und erfüllt $M_{x,t(x)}=0$.
Die vollständige Adjazenzmatrix lautet

$$
\mathcal A=\begin{pmatrix}
0&\mathbf1^T&0\\
\mathbf1&K&R^T\\
0&R&M
\end{pmatrix}.
$$

**Satz L4 (Modelläquivalenz).** Die folgenden Gleichungen beschreiben genau die
Graphen mit diesem Rahmen:

$$
\tag{E1} M\mathbf1=12\mathbf1,
\qquad
\tag{E2} MR=2J_{84\times14}-R(K+I_{14}),
$$
$$
\tag{E3} M^2+M=12I_{84}+2J_{84}-RR^T.
$$

*Beweis.* Für eine symmetrische binäre Matrix mit Nulldiagonale ist
$\mathcal A^2+\mathcal A=12I_{99}+2J_{99}$ äquivalent zu den Parametern
$(99,14,1,2)$: Die Diagonale erzwingt Grad 14, die übrigen Einträge erzwingen
je nach Adjazenz einen beziehungsweise zwei gemeinsame Nachbarn.
Der Außen-Anker-Block ergibt E2, der Außen-Außen-Block E3. Die Grade der
Außenknoten ergeben E1. Für die Umkehrung genügen zusätzlich die festen Identitäten
$R\mathbf1=2\mathbf1$, $R^T\mathbf1=12\mathbf1$, $K^2=I$ und
$R^TR=11I+J-K$. Der Anker-Anker-Block ist daher
$J+K^2+R^TR+K=12I+2J$. Die Wurzelblöcke haben ebenfalls die geforderten Einträge.
Alle Blöcke der Matrixgleichung sind erfüllt. Die Konstruktion ist $t$-invariant.
Die Diagonale von E3 impliziert bereits E1; ihre gesonderte Kodierung ist redundant. ∎

Nach Auswahl der 42 Vertreter ist

$$M=\begin{pmatrix}B&C\\C&B\end{pmatrix},$$

wobei $B,C$ symmetrische binäre $42\times42$-Matrizen mit Nulldiagonale sind.
Die Symmetrie von $C$ folgt aus Symmetrie und $t$-Invarianz von $M$; seine
Nulldiagonale folgt aus L3. Es gibt $2\binom{42}{2}=1722$ primäre Bits.

## 4. Rahmenumbenennungen und Ankerpfeile

**Lemma L5 (semantische Symmetrie).** Jede Permutation der sieben Partnerpaare und
jede Vertauschung innerhalb eines Paares erweitert sich auf Labels und auf den
vollständigen Graphen. Sie erhält den Rahmen und E1–E3.

*Beweis.* Die Erweiterung ist $o\mapsto o$, $a\mapsto g(a)$,
$x_{\{a,b\}}\mapsto x_{\{g(a),g(b)\}}$. Sie erhält Partnerrelation,
Labelinzidenzen, Schnittgrößen und $t$-Paare. Die Gleichungen werden lediglich
umindiziert. ∎

Die verfügbare Umbenennungsgruppe ist $C_2\wr S_7$ der Ordnung 645.120.
Dies ist keine Behauptung über die Automorphismengruppe eines gesuchten Graphen.
Insbesondere steht keine beliebige $S_{42}$-Umbenennung zur Verfügung.

Definiere für $p\ne q$ den Pfeil

$$
x_{pq}=M_{\{a_p,a_q\},\{a_p,b_q\}}\in\{0,1\},\qquad
 d(p)=\sum_{q\ne p}x_{pq}.
$$

Ein Flip in Paar $q$ vertauscht nur die Enden dieser Kante. Ein Flip in Paar $p$
bildet die Kante auf ihr $t$-Bild ab. Beide erhalten daher $x_{pq}$; andere Flips
wirken nicht darauf. Auf den 42 Pfeilen wirkt nur die Paarpermutation $S_7$.
Der gegenseitige Ankergraph enthält $\{p,q\}$ genau dann, wenn $x_{pq}=x_{qp}=1$.

Für UNSAT-Transport genügt diese semantische Symmetrie zusammen mit korrekter
CNF-Erweiterbarkeit. Eine syntaktische Permutation sämtlicher Hilfsvariablen
wird nicht vorausgesetzt.

## 5. Lokale Matchings und vollständige Fallaufteilung

In $N(a_0)$ bilden $o,b_0$ eine Matchingkante. Die übrigen zwölf Knoten
$x_{\{a_0,a_q\}},x_{\{a_0,b_q\}}$, $q\ne0$, bilden ein perfektes Matching $L$.
Vergleiche $L$ mit der festen Paarung $P$ der beiden Labels jedes anderen Ankerpaares.
Genau die gemeinsamen Kanten von $P$ und $L$ werden von den Pfeilen $x_{0q}$ gezählt.

**Lemma L6 (Matchingtypen).** Die Bahnen von $L$ unter dem Stabilisator der einzeln
festgehaltenen Anker $a_0,b_0$, also $C_2\wr S_6$, entsprechen den Partitionen von 6.
Der Ankergrad ist die Anzahl der Teile gleich 1.

*Beweis.* In der zweifarbig gezählten Vereinigung $P\cup L$ ist jede Komponente
ein alternierender Kreis auf $2r$ Knoten. Eine gemeinsame Kante bleibt mit beiden
Farben erhalten und ergibt $r=1$. Die Halbgrößen sind eine Partition von 6.
Umgekehrt liefert das alternierende Durchlaufen gleich großer Komponenten eine
paarungserhaltende Umbenennung zwischen zwei Matchings mit derselben Partition.
Die Teile gleich 1 sind genau die gemeinsamen Kanten. ∎

| Partition | $d(0)$ | Anzahl beschrifteter Matchings |
|---|---:|---:|
| $1+1+1+1+1+1$ | 6 | 1 |
| $1+1+1+1+2$ | 4 | 30 |
| $1+1+1+3$ | 3 | 160 |
| $1+1+2+2$ | 2 | 180 |
| $1+1+4$ | 2 | 720 |
| $1+2+3$ | 1 | 960 |
| $1+5$ | 1 | 2.304 |
| $2+2+2$ | 0 | 120 |
| $2+4$ | 0 | 1.440 |
| $3+3$ | 0 | 640 |
| $6$ | 0 | 3.840 |

Die Summe ist $11!!=10.395$. Für eine Partition mit $\ell$ Teilen und
Multiplizitäten $m_r$ ist die Anzahl
$2^{6-\ell}6!/(\prod_i\lambda_i\prod_r m_r!)$.
Eine erneute vollständige Enumeration der 10.395 Matchings bestätigte diese Tabelle;
der allgemeine Klassifikationsbeweis steht in L6. Insbesondere ist
$d(p)\in\{0,1,2,3,4,6\}$; Grad 5 ist unmöglich.

**Lemma L7 (gemeinsame Normalisierung).** Ein Anker minimalen Grades kann an Position 0
gebracht und sein lokales Matching anschließend auf den Standardvertreter seines
Typs abgebildet werden. Beide Bedingungen bleiben gemeinsam erfüllbar.

*Beweis.* Zunächst benutzt man die Transitivität der Rahmengruppe auf Ankerpaaren.
Anschließend benutzt man ausschließlich den in L6 beschriebenen Stabilisator.
Dieser hält Anker 0 fest und permutiert die übrigen Anker. Er erhält daher die
Eigenschaft $d(0)=\min_p d(p)$. ∎

Eine zusätzliche Sortierung aller Ankergrade in absteigender Reihenfolge darf
nicht ungeprüft mit der Festlegung des minimalen Grades an Position 0 kombiniert
werden. Der historische Profil346-Census benötigt diese Minimum-Normalisierung nicht.

## 6. Reichweite von Profil346 und verbleibende Beweispflicht

Sei $F_0$ die CNF für das uneingeschränkte Rahmenmodell. Die verwendete Formel ist

$$F_{346}=F_0\ \land\ \bigwedge_{p=0}^{6}[d(p)\in\{3,4,6\}].$$

Dies ist unmittelbar im übernommenen `regenerate_base.py` und in der Schleife
über alle sieben Anker in `anchor_profile.py` nachprüfbar. Die Einschränkung ist
ein zu untersuchender Zweig und folgt nicht allein aus E1–E3.

**Satz L8 (bedingte Reduktion).** Ist der gesamte Profil346-Zweig ausgeschlossen,
so besitzt jeder hypothetische C2-Graph einen Anker mit Grad höchstens zwei.
Nach L7 genügt für einen vollständigen weiteren Ausschluss die Behandlung der
acht Matchingtypen mit $d(0)\le2$ unter $d(q)\ge d(0)$ für alle $q$.

*Beweis.* Wären alle Ankergrade mindestens 3, so lägen sie nach L6 in $\{3,4,6\}$;
das wäre der ausgeschlossene Zweig. Andernfalls wähle einen Anker minimalen Grades
und wende L7 und L6 an. ∎

Eine mögliche vollständige Restfamilie besteht daher aus acht Formeln
$F_0\land U(L_\lambda)\land\bigwedge_q[d(q)\ge d(0)]$, wobei
$U(L_\lambda)$ alle 66 Kantenpositionen des lokalen Matchings festlegt.
Die Profil346-Einschränkung gehört nicht zu diesen Restformeln.
Diese Formeln wurden in dieser Arbeitsphase weder als Produktionsfälle erzeugt
noch gelöst. Ein vollständiger früherer Ausschluss dieser acht Typen ist bislang
nicht lokalisiert. Jeder Typ beschreibt eine Familie globaler Konfigurationen.

## 7. Übergang vom Modell zu CNF und Zertifikaten

Die für einen Ausschluss notwendige Richtung lautet: Jede mathematisch mögliche
Graphlösung erzeugt eine Belegung der Primärvariablen und eine Erweiterung auf die
Hilfsvariablen, die die jeweilige CNF erfüllt. Im idealen Encodervertrag gilt die
Äquivalenz zwischen Modellgleichungen und Projektion der CNF-Lösungen.

Produkte müssen vollständig als $z\leftrightarrow(u\land v)$ kodiert werden.
Durch die Orbitabbildung zusammenfallende Terme müssen mit ihrer korrekten
Multiplizität gezählt werden. BDD- und Totalizer-Bausteine benötigen allgemeine
Korrektheitsargumente; lokale Wahrheitstabellen allein beweisen keine vollständige
Programmadäquanz. Die historischen Beweise für Referenzencoder und Totalizer sind
verortet, ihre lückenlose Bindung an alle tatsächlich benutzten Formeln bleibt
Teil des Audits.

**Lemma L9 (Zertifikattransport).** Ein geprüftes UNSAT-Zertifikat für
$F_{346}\land U(D)$ schließt bei Encoderadäquanz und L5 die gesamte $S_7$-Bahn von
$D$ aus. Ist stattdessen eine Formel $H$ geprüft UNSAT und wurde unabhängig
$H\subseteq F_{346}\cup U'$ mit $U'\subseteq U(D)$ nachgewiesen, so gilt derselbe
Ausschluss für alle von $U'$ erfassten Profile.

*Beweis.* Eine erfüllende Belegung der stärkeren Formel würde deren Teilformel $H$
erfüllen. Der Widerspruch transportiert über L5 auf umbenannte Graphlösungen. ∎

Damit sind Beweischecker, Klauselteilmengenprüfung, Variablenzuordnung und
Profilabdeckung verschiedene Glieder der Vertrauenskette.

## 8. Census, Abdeckung und Veröffentlichungsstand

Die genaue historische Fallmenge, die Zählkette und die neu ausgeführten
Datenprüfungen stehen in [CENSUS_UND_COVERAGE.md](CENSUS_UND_COVERAGE.md).
Der Census enthält C4-freie Pfeilgraphen mit allen Graden in $\{3,4,6\}$ und
mindestens einem Grad 3. Der Zweig ohne Grad 3 benötigt den früheren Profile46-Ausschluss;
der C4-Filter benötigt den korrekt gebundenen C4-Ausschluss.

Der Status jeder Beweispflicht steht in [BEWEISREGISTER.md](BEWEISREGISTER.md).
Die veröffentlichungsfähige Schlussfolgerung muss auf den schwächsten noch
unbewiesenen Übergang begrenzt bleiben. Diese Arbeitsfassung enthält bereits
prüfbare mathematische Herleitungen und neue Datenverknüpfungen; sie enthält
keinen geschlossenen Beweis des Zielsatzes.

## Quellen

- **[MM04]** A. A. Makhnev, I. M. Minakova: *On automorphisms of strongly regular graphs with the parameters λ=1 and μ=2*. Diskretnaya Matematika 16(1), 95–104 (2004). DOI [10.4213/dm144](https://doi.org/10.4213/dm144). [Original und bibliographischer Datensatz](https://m.mathnet.ru/eng/dm144). Satz 1, S. 96; Involutionsfall S. 100–101.
- Historische Rahmen- und Modellspezifikation: [SPEZIFIKATION.md, festgeschriebener Commit](https://github.com/ibenarb/conway99-research/blob/5a1d6108fab25e09eaeee99985879a6a388de560/docs/c2_spec_20260913/SPEZIFIKATION.md).
- Historischer Matchingbeweis: [THEOREM.md, festgeschriebener Commit](https://github.com/ibenarb/conway99-research/blob/5a1d6108fab25e09eaeee99985879a6a388de560/src/c2_matching_20260915/THEOREM.md).
- Referenzencoder: [ENCODER_BEWEIS.md](https://github.com/ibenarb/conway99-research/blob/5a1d6108fab25e09eaeee99985879a6a388de560/docs/c2_reference_20260913/ENCODER_BEWEIS.md).
- Totalizer: [THEOREM.md](https://github.com/ibenarb/conway99-research/blob/5a1d6108fab25e09eaeee99985879a6a388de560/src/c2_counter_ab_20260916/THEOREM.md).
- Unveränderte aktuelle Quellkopien und Herkunftshashes: [source_provenance.json](../../results/c2_completeness_20261012/source_provenance.json).
