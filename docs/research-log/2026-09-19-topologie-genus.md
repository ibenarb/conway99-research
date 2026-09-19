# Conway-99: Flächeneinbettungen, Dimension und Genus

Stand: 19. September 2026. Recherche und mathematische Ausarbeitung.
Status: bedingte Aussagen unter der Annahme, dass ein G = srg(99,14,1,2) existiert.
Die hier ausgearbeiteten Beweise sind keine unabhängig begutachteten Ergebnisse; ein wissenschaftlicher Neuheitsanspruch wird nicht erhoben.

## 1. Ergebnis

Für eine **topologische**, kreuzungsfreie Einbettung gilt:

| Fragestellung | Gesicherte Antwort |
|---|---|
| Kleinste Dimension einer frei wählbaren Mannigfaltigkeit, die G enthält | Genau 2 |
| Orientierbarer Graphengenus gamma(G) | 96 <= gamma(G) <= 182 |
| Nichtorientierbarer Graphengenus, Zahl der Kreuzhauben | Mindestens 192 |
| Kleinste Dimension eines euklidischen Raums für eine topologische Einbettung | Genau 3 |
| Exakter minimaler Flächengenus | Hier nicht bestimmt; insbesondere ist gamma(G)=96 nicht bewiesen |
| Zusätzlich alle Kanten gleich lang in einer vorgegebenen Metrik | Eigenständige geometrische Frage; folgt nicht aus den Genusschranken |

Eine Fläche bleibt auch mit hundert Henkeln zweidimensional. Ihr Einbettungsraum kann dreidimensional sein. Das Genus eines Graphen ist das Minimum über seine Flächeneinbettungen, nicht eine aus den SRG-Parametern automatisch eindeutig bestimmte Zahl.

## 2. Begriffsklärung und das Beispiel mit neun Knoten

Der eindeutige srg(9,4,1,2) ist der 3x3-Turmgraph bzw. das kartesische Produkt C3 □ C3; siehe [3]. Auf dem flachen Torus R²/(3Z)² liegen die neun Knoten bei (i,j), i,j in {0,1,2}. Verbunden werden horizontale und vertikale Nachbarn modulo 3. Die Kanten sind kreuzungsfreie geodätische Strecken gleicher Länge 1. Es entstehen neun quadratische Flächen.

Das ist eine präzise Bedeutung von „äquidistant“: benachbarte Knoten sind gleich weit voneinander entfernt. Nicht alle Knotenpaare haben denselben Abstand. Die Metrik des flachen Quotiententorus ist außerdem nicht die durch den üblichen glatten Rotationstorus in R³ induzierte Metrik. Eine topologische Übertragung des Bildes auf einen solchen Torus erhält keine Längen.

Dass der Graph nicht planar ist, folgt bereits aus seiner Dreieckszahl: Er hat 18 Kanten und sechs Dreiecke. In einer planaren Einbettung wären f=11 Flächen nötig, deren gesamte Randlänge mindestens 4f-6=38 wäre. Tatsächlich stehen nur 2m=36 Kanten-Seiten zur Verfügung. Daher ist sein orientierbarer Genus genau 1.

Bemerkenswert: In der beschriebenen quadratischen Toruseinbettung ist **keines der sechs graphentheoretischen Dreiecke eine Fläche**. Sie laufen als nicht zusammenziehbare Kurven um den Torus. Schon dieses kleine Beispiel warnt davor, Kreise und Flächen gleichzusetzen.

Eine eindimensionale Mannigfaltigkeit hat lokal höchstens zwei Richtungen; darin kann kein Knoten vom Grad 14 eingebettet werden. Jede endliche Graphstruktur besitzt hingegen eine Einbettung in eine orientierbare Fläche: Knoten durch Scheiben, Kanten durch Bänder ersetzen und die Randkomponenten mit Scheiben schließen. Damit ist die minimale Mannigfaltigkeitsdimension genau 2.

Jeder endliche Graph lässt sich auch in R³ mit geraden Kanten kreuzungsfrei einbetten: Man wählt die Knoten in allgemeiner Lage, insbesondere ohne vier koplanare Punkte. Zwei disjunkte sich schneidende Strecken hätten vier koplanare Endpunkte. R² scheidet hier wegen der unten bewiesenen Genusschranke aus. In Dimension 3 ist „Genus“ ohne nähere Definition kein entsprechender Oberflächenparameter; sogar S³ enthält jeden endlichen Graphen.

## 3. Was die Recherche belegt – und was nicht

### 3.1 Allgemeine Flächentheorie

**Mohar–Thomassen, Graphs on Surfaces (2001)** [1] ist die Standardreferenz für zelluläre Einbettungen, Rotationssysteme und Genusfragen. Die zugängliche Autorenseite bestätigt Buch und Kapitelstruktur; der vollständige Buchtext wurde hier nicht durchgearbeitet.

**Esperet–Lévêque, Local certification of graphs on surfaces (2021, überarbeitete Fassung 2022)** [2], insbesondere Abschnitt 3, stellt die benötigte Theorie explizit dar: Euler-Genus, Reduktion auf zelluläre Einbettungen und Rekonstruktion einer orientierbaren Einbettung aus zwei Permutationen. Ihr Gegenstand ist die Zertifizierung von Einbettungen, nicht die Existenz des Conway-99-Graphen.

### 3.2 Stark reguläre Graphen und Conway-99

**Brouwer–Van Maldeghem, Strongly regular graphs** [3], insbesondere Abschnitt 1.1, die Diskussion auf Buchseite 16 und die Parametertabelle auf Buchseite 374, behandelt die SRG-Grundlagen und führt (99,14,1,2) als offenen Parametersatz. Dort werden auch Einschränkungen der Automorphismen referiert. In den hier geprüften einschlägigen Passagen steht keine Bestimmung des Flächengenus dieses hypothetischen Graphen.

**Reimbayev, The Lower Bound for Number of Hexagons in Strongly Regular Graphs with Parameters lambda=1 and mu=2 (2024)** [4] untersucht kurze induzierte Kreise und deren Häufigkeiten. Proposition 3 gibt die Dreiecks- und Viereckszahlen an, die wir unten unabhängig herleiten. Die Arbeit enthält zusätzliche Aussagen und eine Vermutung über Sechseckzahlen. Eine Häufigkeit graphentheoretischer Sechsecke ist jedoch keine Häufigkeit sechseckiger Einbettungsflächen. Die Vermutung wird hier nicht als bewiesen verwendet.

### 3.3 Reichweite der Suche

Gesucht wurde unter anderem nach Kombinationen von „Conway“, „99,14,1,2“, „strongly regular“, „genus“, „surface“ und „embedding“. Die allgemeine Suche lieferte vielfach unpassende Treffer; deshalb wurden die oben genannten Primärquellen direkt gelesen. Mehrere direkte Tabellen-/HTML-Aufrufe scheiterten, während die verlinkten PDF-Quellen zugänglich waren.

**Es wurde keine belastbar überprüfte Veröffentlichung gefunden, die speziell den minimalen Flächengenus von srg(99,14,1,2) bestimmt.** Das ist ein begrenzter Recherchebefund, kein Nachweis, dass eine solche Untersuchung nicht existiert. Insbesondere werden die Zahlen 96 und 182 hier durch die folgenden Beweise begründet, nicht einer nicht gefundenen Publikation zugeschrieben. Ein Recherchetreffer zu einer weiteren Reimbayev-Arbeit von 2026 konnte nicht am arXiv-Original verifiziert werden und wird nicht als Beleg verwendet.

## 4. Eigene Herleitung der unteren Schranke

### 4.1 Zählwerte

Es gelten n=99 und m=99·14/2=693. Weil lambda=1 ist, gehört jede Kante zu genau einem Dreieck. Die Dreiecke zerlegen daher die Kantenmenge, und ihre Anzahl ist

T = m/3 = 231.

An jedem Knoten ist der von seinen 14 Nachbarn induzierte Graph genau 7K2: Jeder Nachbar hat darin genau einen Partner.

Es gibt 99·84/2=4158 nichtadjazente Knotenpaare. Wegen mu=2 ist jedes die Diagonale genau eines Vierecks. Dieses Viereck ist induziert: Eine weitere Diagonale würde eine Kante mit zwei gemeinsamen Nachbarn erzeugen und lambda=1 verletzen. Jedes Viereck hat zwei Diagonalen. Folglich

Q = 4158/2 = 2079.

### 4.2 Flächen zählen

Es genügt, zelluläre Einbettungen zu betrachten; die Flächen sind dann offene Scheiben [2]. Sei f die Flächenzahl und t die Zahl der dreieckigen Flächen. Es gilt t<=231. Ein Dreieck kann nicht beidseitig Fläche sein: An seinen Knoten müssten seine beiden Kanten beide lokalen Sektoren besetzen, was bei Grad 14 unmöglich ist.

Die übrigen Flächen haben Randlänge mindestens vier. Längen eins und zwei sind bei einem einfachen Graphen mit diesem Grad ausgeschlossen. Randlängen werden mit Durchlaufvielfachheiten gezählt; ein allgemeiner Flächenrand muss nicht einfach sein.

Damit gilt

2m = Summe aller Flächenrandlängen >= 3t+4(f-t) = 4f-t >= 4f-231,

also

f <= floor((1386+231)/4) = 404.

Für eine orientierbare Fläche ist

2-2g = n-m+f = -594+f.

Daraus folgt **g>=96**. Die gewöhnliche Abschätzung ohne die Dreiecksbeschränkung hätte nur g>=67 geliefert.

Für eine nichtorientierbare Fläche mit h Kreuzhauben lautet Euler

2-h = -594+f,

also **h>=192**. Ein nichtorientierbarer geschlossener Flächenträger lässt sich nicht selbst kreuzungsfrei als geschlossene Fläche in R³ einbetten; das ist von der abstrakten Einbettung des Graphen in ihn zu unterscheiden.

## 5. Eine konstruktive obere Schranke

**Lemma:** In einem Graphen, dessen Kanten disjunkt in Dreiecke zerfallen, kann man sämtliche Dreiecke gleichzeitig zu Flächen einer orientierbaren Einbettung machen, sofern die lokalen Paarblöcke zu zyklischen Ordnungen verbunden werden.

Beweis für unseren Fall: Orientiere jedes der 231 Dreiecke beliebig. Für ein gerichtetes Dreieck u→v→w→u fordere in der zyklischen Nachbarordnung am Knoten v, dass auf u unmittelbar w folgt; analog an u und w. An jedem Knoten sind dies sieben disjunkte geordnete Zweierblöcke. Ordne die sieben Blöcke beliebig zu einem einzigen zyklischen Wort der Länge 14 an.

Diese Nachbarordnungen bilden ein Rotationssystem. Mit der Konvention „Kante umkehren, dann zyklischen Nachfolger nehmen“ ist jedes der vorgegebenen gerichteten Dreiecke ein Flächenumlauf. Die Standardkonstruktion liefert eine geschlossene orientierbare Fläche [2].

Es bleiben die jeweils entgegengesetzten 693 gerichteten Kanten für weitere Flächen übrig. Mindestens eine weitere Fläche existiert, somit f>=232. Euler ergibt für diese Einbettung

g=(596-f)/2 <= (596-232)/2 = 182.

Zusammen folgt **96<=gamma(G)<=182**.

Dies behauptet nicht, dass eine Einbettung minimalen Genus alle Dreiecke facial macht. Die Konstruktion liefert lediglich eine zusätzliche, sicher verfügbare Einbettung. Sie benötigt auch keinerlei Automorphismus des Graphen.

## 6. Exakte Defektgleichung und der Fall Genus 96

Für eine orientierbare zelluläre Einbettung definiere

D = Summe über Flächen der Länge l>=5 von (l-4).

Dann ist 2m=4f-t+D. Mit f=596-2g folgt

t-D=998-8g,

äquivalent

**(231-t)+D=8g-767.**

Der linke Ausdruck zählt fehlende Dreiecksflächen und überschüssige Randlänge über vier. Er ist stets nichtnegativ und kongruent 1 modulo 8.

Bei g=96 ist der Wert genau 1. Damit bleiben exakt zwei notwendige Flächenprofile:

| Profil | Dreiecke | Vierecke | Fünfecke | Längere Flächen | Gesamt |
|---|---:|---:|---:|---:|---:|
| A | 230 | 174 | 0 | 0 | 404 |
| B | 231 | 172 | 1 | 0 | 404 |

Das sind arithmetisch notwendige Profile, keine Existenznachweise.

Für g=97 beträgt der Defekt 9, für g=98 beträgt er 17. Bei nichtorientierbarem Genus h gilt entsprechend (231-t)+D=4h-767; h=192 hat dieselben beiden Profile.

Zusätzliche lokale Aussagen:

- In Profil A sind genau die drei Knoten des einzigen nichtfacialen Dreiecks an nur sechs statt sieben Dreiecksflächen beteiligt. Jeder andere Knoten liegt an sieben Dreiecks- und sieben Vierecksflächen; diese wechseln sich in seiner zyklischen Ordnung ab.
- In Profil B wechseln sich überall sieben Dreiecksflächen mit sieben anderen Flächen ab. An den fünf Knoten des Fünfecks ist eine dieser anderen Flächen das Fünfeck; an den übrigen Knoten sind alle sieben Vierecke.
- In Profil A liegt jede Kante außerhalb des nichtfacialen Dreiecks zwischen einem Dreieck und einem Viereck. Die drei Kanten dieses Dreiecks liegen zwischen zwei Vierecken.
- In Profil B liegt jede Kante zwischen einem Dreieck und einer Nichtdreiecksfläche.

## 7. Warum das Auffüllen aller kurzen Kreise kein Nichtexistenzbeweis ist

Füllt man sämtliche 231 Dreiecke und 2079 Vierecke mit Scheiben, erhält man einen zweidimensionalen Zellkomplex, aber **keine Fläche**.

Für eine Kante uv gibt es zwölf Vierecke durch uv: Wähle einen der zwölf Nachbarn x von u außerhalb des Dreiecks uvw. Das nichtadjazente Paar x,v hat neben u genau einen gemeinsamen Nachbarn y. So entsteht eindeutig u-v-y-x-u.

Jede Kante liegt deshalb an 1+12=13 Zellen, während sie in einer geschlossenen Fläche genau zwei Seiten hat.

Noch deutlicher ist der Link an einem Knoten v. Seine 14 inzidenten Kanten werden die Linkknoten. Jedes Paar davon liegt entweder in seinem eindeutigen Dreieck oder in seinem eindeutigen Viereck. Daher ist dieser Link **K14**, kein Kreis. Für eine Flächeneinbettung muss die Auswahl der tatsächlichen Flächenecken dagegen lokal einen einzelnen C14 bilden.

Die Euler-Zahl des vollständig aufgefüllten Komplexes ist 99-693+231+2079=1716. Sie darf nicht in 2-2g eingesetzt werden: Die Flächenvoraussetzung fehlt.

Das trifft bereits das Neun-Knoten-Beispiel: Füllt man dort alle sechs Dreiecke und neun Vierecke, ist der Link K4 und jede Kante liegt in drei Zellen. Trotzdem existiert der Graph und besitzt eine Toruseinbettung.

Auch die frühere zusätzliche Projektannahme „Graph eines einfachen konvexen 14-Polytops“ ist wesentlich stärker als die SRG-Bedingung. Flächeneinbettung, zweidimensionaler Zellkomplex und zweidimensionales Skelett eines 14-Polytops dürfen nicht gleichgesetzt werden. Ein Ausschluss der Polytoprealisierung wäre für sich kein Ausschluss des SRG.

## 8. Mögliche Umkehrschlüsse und Forschungsstrategie

### 8.1 Was unmittelbar folgt

Jeder angebliche Conway-99-Kandidat mit einer behaupteten Einbettung auf einer orientierbaren Fläche vom Genus <=95 ist fehlerhaft. Dagegen ist ein Nachweis „keine Einbettung bei Genus 96“ mit der Existenz eines solchen Graphen vereinbar: Sein Genus könnte höher sein.

Ein hinreichender Weg zu einem Nichtexistenzbeweis wäre beispielsweise:

1. Universell beweisen, dass jeder hypothetische Conway-99-Graph eine Einbettung mit Genus <=95 besitzt.
2. Dies mit der unteren Schranke 96 kombinieren.

Eine solche universelle obere Schranke liegt hier nicht vor. Die bewiesene obere Schranke 182 widerspricht der unteren nicht.

### 8.2 Konkreter erster Untersuchungszweig: Genus-96-Profile

Die Profile A und B lassen sich getrennt als kombinatorische Existenzprobleme formulieren. Gesucht werden gleichzeitig ein SRG und ein Rotationssystem mit dem jeweiligen Flächenprofil.

Ein Modell muss prüfen:

- die vollständigen SRG-Bedingungen;
- die Auswahl bzw. die Umläufe der Flächen;
- genau zwei Flächenseiten je Kante;
- einen einzelnen zyklischen Link C14 an jedem Knoten;
- bei orientierbaren Einbettungen eine konsistente Orientierung.

Die Kantenbedingung allein genügt nicht: Ohne zusammenhängende Knotenlinks können singuläre Verklebungen entstehen. Profil B erlaubt die Reduktion auf zyklische Ordnungen der sieben Dreieckspaare an jedem Knoten. In Profil A muss das eine nichtfaciale Dreieck ausdrücklich ausgenommen werden.

Ein zertifiziertes UNSAT beider Profile würde die Schranke auf gamma(G)>=97 verbessern. Es würde **nicht** die Nichtexistenz des SRG beweisen. Dies ist ein überschaubar definierter mathematischer Erkenntnisgewinn, aber kein vorab als rechnerisch leicht einzustufender Auftrag.

### 8.3 Vollständiger, aber möglicherweise teurer Ansatz

Die Dreiecksblockkonstruktion aus Abschnitt 5 ist für jeden hypothetischen G verfügbar. Ein gemeinsames Existenzmodell „SRG plus orientierbares Rotationssystem mit allen 231 Dreiecken facial“ wäre daher vollständig bezüglich der SRG-Existenz, sofern es keine zusätzliche unbegründete Genus- oder Flächenbeschränkung enthält.

In dieser Klasse reichen die möglichen Genera von 96 bis 182. Ein vollständiger Ausschluss der ganzen Klasse würde den Graphen ausschließen. Die Zusatzvariablen können jedoch mehr Aufwand als Nutzen erzeugen; ohne Pilot ist keine Beschleunigung gegenüber dem Adjazenzmodell belegt.

Eine sinnvolle Pilotfrage lautet deshalb: Erzeugen die Rotations- und Flächenbedingungen frühere Widersprüche als das bestehende SRG-Modell, oder fügen sie vor allem redundante Wahlmöglichkeiten hinzu?

### 8.4 Verbindung zu Symmetrien und Kandidatensuche

Ein Automorphismus des Graphen muss ein gewähltes Rotationssystem nicht erhalten. Deshalb darf ein Ordnung-2- oder Ordnung-3-Automorphismus nicht ohne Beweis als flächenerhaltende Symmetrie derselben Einbettung vorausgesetzt werden. Ein Ausschluss symmetrieverträglicher Einbettungen wäre zunächst nur ein Ausschluss dieser Zusatzannahme.

Für die memetische Suche können Flächenkompatibilität und die Defektzahl als zusätzliche experimentelle Kriterien dienen, sobald die relevanten SRG-Eigenschaften tatsächlich vorliegen. Bei bloß angenäherten Kandidaten stimmen Dreieckszahlen und lokale Paarzerlegungen möglicherweise nicht; dann gelten die obigen Formeln nicht unverändert. Niedriger Genus ist außerdem kein bisher bewiesenes Merkmal einer Lösung. Eine darauf gerichtete Auswahl wäre eine Suchheuristik, kein sicherer Filter.

## 9. Ausgeführte Kontrollen

Die arithmetischen Werte wurden mit Python und exakten rationalen Zahlen nachgerechnet: m=693, T=231, Q=2079, f<=404, g>=96, h>=192, obere Schranke 182 und Defektkonstante 767.

Eine ganzzahlige Aufzählung der bei Defekt 1 möglichen Dreieck-/Viereck-/Fünfeckzahlen ergab genau (230,174,0) und (231,172,1). Das Vorliegen längerer Flächen ist schon durch D<=1 ausgeschlossen.

Für C3 □ C3 wurde das Rotationssystem der periodischen Quadratzeichnung tatsächlich durchlaufen: 36 gerichtete Kanten ergeben neun Flächenumlaufzyklen der Länge 4 und Euler-Zahl 0.

Diese Kontrollen überprüfen Arithmetik und das kleine Vergleichsbeispiel. Es wurde weder ein Conway-99-Graph konstruiert noch eine SAT-Suche nach seinen Flächeneinbettungen durchgeführt.

## Quellen

[1] Bojan Mohar, Carsten Thomassen: *Graphs on Surfaces*. Johns Hopkins University Press, 2001. Autorenseite mit Inhaltsverzeichnis: https://www.sfu.ca/~mohar/Book.html

[2] Louis Esperet, Benjamin Lévêque: *Local certification of graphs on surfaces*. arXiv:2102.04133, 2021; Fassung v4 von 2022. https://arxiv.org/abs/2102.04133 — Volltext: https://arxiv.org/pdf/2102.04133. Besonders Abschnitt 3.

[3] Andries E. Brouwer, Hendrik Van Maldeghem: *Strongly regular graphs*. Online-Monographie der Autoren: https://homepages.cwi.nl/~aeb/math/srg/rk3/srgw.pdf. Besonders Abschnitte 1.1 und 1.3.5 sowie die Conway-99-Diskussion und Parametertabelle.

[4] Reimbay Reimbayev: *The Lower Bound for Number of Hexagons in Strongly Regular Graphs with Parameters lambda=1 and mu=2*. arXiv:2409.10620, 2024. https://arxiv.org/abs/2409.10620 — geprüfter Volltext: https://arxiv.org/pdf/2409.10620. Auch im Verlagsverzeichnis 2024, S. 1–14: https://ejaam.org/volumes/2024.
