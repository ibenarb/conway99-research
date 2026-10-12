# Eigener Plan für LOW – vor Eingang des zweiten Reviews

Stand: 12.10.2026. Ausgangscommit: a0fa18c0daaa85c2994b05e556c1bde8fcfd2f8c.
Dies ist ein eigener Strategieentwurf zum späteren Vergleich mit dem Reviewer.
Keine neue Solverproduktion wurde gestartet; keine Laufzeitprognose wird behauptet.

## Entscheidungsvorschlag

LOW als 3.152 bekannte Wurzelfälle organisieren, aber vorerst keine vollständige
Verfeinerung über einen zweiten Anker und keinen neuen globalen Profilcensus erzeugen.
Mein bevorzugter zusätzlicher Ansatz ist die notwendige **Zwischenstruktur zwischen
den 24 festgelegten und den 60 übrigen Außenknoten**. Sie enthält genau 720 der
noch freien Primärbits. Ein kompakteres Suchproblem ist damit möglich, eine
Beschleunigung aber noch nicht nachgewiesen.

Zuerst diese Struktur mathematisch und kodierungstechnisch prüfen; danach sie
auf identischen Pilotfällen mit dem direkten vollständigen Modell vergleichen.
Wenn sie nicht trägt, ohne weitere Vorleistung zum direkten Modell zurückkehren.
Schwierige Fälle später adaptiv teilen. Ziel ist geringer Gesamtaufwand bis zum
geprüften Ausschluss, nicht eine möglichst große Zahl von Teilfällen.

## 1. Ausgangslage und unveränderte Grenzen

- Profil346 ist unter den dokumentierten historischen Zertifikatsvoraussetzungen
  abgeschlossen. Keine Wiederholung dieses Zweigs.
- LOW: 3.412 lokale Matchingpaarbahnen; 260 durch den neuen lokalen Test ausgeschlossen;
  3.152 Kandidaten verbleiben. Ein Wurzelfall besteht aus F0, den 132 Kantenfestlegungen
  für (L,N) und der Minimumausgradbedingung am gewählten Anker.
- Die acht L-Familien haben nach dem Filter 125, 296, 322, 634, 89, 471, 215 und
  1.000 Kandidaten in der Reihenfolge (1,1,2,2), (1,1,4), (1,2,3), (1,5),
  (2,2,2), (2,4), (3,3), (6).
- Eine Prozentzahl abgeschlossener Typen ist keine Prozentzahl erledigter Rechenarbeit.
  Es gibt weder einen bekannten globalen LOW-Lösungsraumumfang noch eine belastbare ETA.
- Nur universell gültige alte Ausschlüsse, etwa der belegte gegenseitige C4-Filter,
  dürfen ohne Hochgradvoraussetzungen übernommen werden. Ein historischer
  UNSAT-Beleg unter F346 rechtfertigt nicht dieselbe Klausel unter F0.

## 2. Konkrete mathematische Zwischenstruktur

Seien W_a und W_b=t(W_a) die beiden Zwölfermengen und Z die übrigen 60 Außenknoten.
Die Labels von Z sind alle ungepaarten Zweiermengen aus den zwölf anderen Ankern.
T sei die 60x60-Permutationsmatrix der Labelinvolution auf Z und R_Z die
60x12-Labelinzidenzmatrix. P,L,N werden zugleich als 12x12-Matchingmatrizen verwendet.

Setze X_(i,z)=1 genau dann, wenn der i-te Knoten aus W_a mit z benachbart ist.
H sei die noch unbekannte Adjazenz auf Z. Dann ist der Außenblock

\[
M=\begin{pmatrix}L&N&X\\N&L&XT\\X^T&TX^T&H\end{pmatrix}.
\]

Jeder z in Z hat genau zwei Nachbarn in W_a: z und a sind nicht benachbart,
und ihre beiden gemeinsamen Nachbarn müssen in W_a liegen. Die Nachbarn bilden
eine Nichtkante von L, da eine L-Kante bereits a als einzigen gemeinsamen
Nachbarn besitzt. Umgekehrt hat jede Nichtkante von L genau einen gemeinsamen
Nachbarn in Z: den anderen gemeinsamen Nachbarn neben a; innerhalb W_a oder W_b
kann kein weiterer liegen, da dort jeweils Matchings wirken. Somit entsteht
eine Bijektion zwischen den 60 Labels von Z und den 60 Nichtkanten von L.

Aus den bereits bewiesenen Blockgleichungen folgen notwendig:

\[
X\mathbf1=10\mathbf1,\qquad X^T\mathbf1=2\mathbf1,
\]
\[
XX^T=9I+J-L,
\]
\[
XTX^T=2J-P-N-LN-NL,
\]
\[
XR_Z=2J-I-P-L-NP.
\]

Alle Matrizen auf der rechten Seite sind nach Festlegung von (L,N) bekannt.
Die erste Gramgleichung beschreibt die Nichtkantenmarkierung, die zweite koppelt
sie mit dem Partnermatching und t; die letzte erzwingt die richtigen Ankerinzidenzen.
Der bisherige lokale Ausschluss ist eine unmittelbare Negativitätsobstruktion
in der rechten Seite der zweiten Gramgleichung. Die vollständigen Gleichungen
verlangen erheblich mehr als deren bloße Nichtnegativität.

**Arbeitsfrage:** Welche (L,N) erlauben überhaupt ein binäres X mit diesen Bedingungen?
Unlösbarkeit schließt den gesamten Wurzelfall aus. Lösbarkeit beweist nur diese
notwendige Zwischenstruktur und keinen Graphen auf 99 Knoten.

Die Aufteilung der 1.722 Primärbits ist exakt:

| Teil | Unabhängige Bits |
|---|---:|
| Bereits festgelegtes Paar (L,N) | 132 |
| Verbindungen X zwischen W_a und Z; Gegenstücke durch t | 720 |
| Innere Adjazenz H auf Z, t-invariant, ohne Partnerkanten | 870 |

Nach Fixierung von X enthält der W_a-Z-Block zusätzlich die in H lineare Bedingung

\[
LX+NXT+XH+X=2J-R_Z^T.
\]

Das macht eine gestufte Suche plausibel. Es rechtfertigt **keine** vollständige
Aufzählung aller X: Deren Anzahl könnte sehr groß sein. Vorrang haben notwendige
Obstruktionen, Propagation und nur bei Bedarf partielle X-Festlegungen.
Auch alle weiteren Bedingungen an H bleiben zu erfüllen.

## 3. Bereits während dieser Planung geprüft

Ein einfacher notwendiger Zuordnungstest wurde auf **allen 3.152 Kandidaten**
ausgeführt. Für ein Label z={c,d} darf eine Nichtkante {i,j} nur dann zugeordnet
werden, wenn die vier entsprechenden Restinzidenzforderungen positiv sind.
Die Restforderungen stehen in 2J-I-P-L-NP. Im daraus entstehenden bipartiten
Zuordnungsgraphen wird eine vollständige Paarung gesucht (Hall-Bedingung).

Ergebnis: **0 neue Ausschlüsse.** Die zulässigen Zuordnungen umfassen je Fall
noch 2.100 bis 3.600 der maximal 3.600 Label/Nichtkanten-Paare. Dies ist ein
negativer Befund für diese einfache Relaxation, nicht gegen das stärkere
gekoppelte Gleichungssystem. Allein diese Domänen weiter zu zählen ist vorerst
keine gute Verwendung von Rechenzeit.

Die vier hergeleiteten Blockidentitäten wurden außerdem bei 50 reproduzierbaren
zufälligen Matrixbelegungen gegen die Residuen der direkt aufgebauten
99x99-Adjazenzmatrix geprüft: PASS. Dies kontrolliert die algebraische Umsetzung,
nicht Existenz oder Unlösbarkeit. Der mathematische Ursprung sind die Blockprodukte.

Die vorhandenen Bahndaten zeigen zudem: **1.617 von 3.152 Kandidaten haben trivialen
Stabilisator von (P,L,N).** Bei diesen Fällen steht für die Normalisierung eines
zweiten Ankers keine weitere nichttriviale Wirkung dieser Gruppe zur Verfügung.
Eine erneute freie Verwendung der elf lokalen L-Normalformen wäre unzulässig.
Das spricht gegen eine vorab pauschal kanonisierte Zwei-Anker-Zerlegung.

## 4. Umsetzung in fünf Entscheidungsschritten

### A. Beweis- und Formelschnittstelle sichern

Die Wurzelfallliste erhält stabile IDs und Hashes. Jede mathematische Reduktion,
jede Fallteilung und jedes Zertifikat wird diesem Fallbaum zugeordnet.
Die 132 Kantenentscheidungen werden anhand der vorhandenen Variablenabbildung
in F0 übertragen; keine F346-Restformel als LOW-Basis verwenden.
Die Minimumbedingung und Eingradrestriktionen separat auf korrekte Reichweite prüfen.

Die neue X-Kodierung braucht einen dokumentierten notwendigen Übergang von F0.
Ein UNSAT-Beleg für die X-Formel schließt einen Wurzelfall nur zusammen mit dieser
Übergangsbegründung aus. Positive Kleinstkontrollen, einschließlich Paley(9),
helfen gegen Mappingfehler; dort ist die 60-Knoten-Struktur jedoch nicht vorhanden.
Sie ersetzen deshalb nicht die algebraische und unabhängige Kodierungsprüfung.

### B. Zwei Ansätze auf denselben kleinen Fällen vergleichen

Vorgeschlagener Anfang: 32 Wurzelfälle, vier aus jeder der acht L-Familien.
Je Familie zwei strukturelle Extremfälle (wenige/viele erlaubte Markierungszuordnungen)
und zwei vorab mit festem Seed ausgewählte weitere Fälle. Innerhalb dessen Eingrad,
Anzahl gemeinsamer L/N-Kanten und Stabilisator möglichst streuen.

- Ansatz A: direktes vollständiges F0 mit (L,N) und Minimumgradbedingungen.
- Ansatz B: notwendiges X-Modell; bei Erfolg im Sinne neuer Ausschlüsse dessen
  Aufwand einschließlich Zertifikat messen. Ein SAT-X-Ergebnis bleibt ein offener
  Wurzelfall und wird gegebenenfalls im vollständigen Modell weiterbehandelt.

Nur falls die isolierte X-Suche viel zulässt, aber ihre Darstellung gute Propagation
verspricht, eine dritte Variante testen: vollständiges Modell mit redundanter
Markierungskodierung. Nicht sofort zahlreiche Solvervarianten kombinieren.

Die 32 Fälle sind ein strukturierter Pilot, keine unverzerrte Stichprobe zur Hochrechnung.
Wenn er vielversprechend ist, vor einer Produktionsplanung eine unabhängige
Zufallsstichprobe als Kontrolle verwenden. Schwierige und ungelöste Fälle behalten.

### C. Aufwand messen, nicht nur gelöste Fälle zählen

Je Fall: Solver-CPU, Prüfer-CPU, Gesamtwallzeit, maximaler RAM, Proof-Bytes,
Status SAT/UNSAT_UNCERTIFIED/UNSAT_CERTIFIED/offen sowie erreichte Propagation.
Konfliktzahlen verschiedener Kodierungen sind nicht direkt vergleichbar.
Entscheidend sind vollständiger geprüfter Aufwand und die schwierigen verbleibenden Fälle.

Ein Beweiserzeugungslauf gehört von Anfang an zur Messung. Beweisfreie Suche darf
als gesonderter Scout dienen, ist aber keine Grundlage für den zertifizierten Abschluss.
UNSAT ohne fertige Prüfung gilt nicht als erledigter Fall.

Keine voreilige ETA aus dem Median der gelösten Fälle. Messungen an vorher vereinbarten
Kontrollpunkten auswerten; längere Nutzerläufe mit Ressourcenwächter und Herzschlag
mindestens alle 15 Minuten. Kein stilles Beenden bei Erreichen eines Zeitbudgets.

### D. Nur schwere Fälle weiter teilen

Zuerst auf schwierigen Pilotfällen zwei konkrete Teilungsarten vergleichen:

1. Eine ausgewählte noch freie Kante, vorzugsweise im X-Block. Die Kinder mit
   Kante=0 und Kante=1 sind vollständig und disjunkt; kein neuer Symmetriebeweis nötig.
   Die Auswahl nach beobachteter Propagation muss empirisch gegen eine einfache
   deterministische Auswahl bestehen.
2. Lokale Daten eines fest ausgewählten zweiten Ankerpaars. Nur unter dem tatsächlichen
   verbleibenden Stabilisator arbeiten. Bei trivialem Stabilisator keine zusätzliche
   kanonische Umbenennung voraussetzen. Alle tatsächlich möglichen lokalen Belegungen
   müssen abgedeckt sein; bloße Partitionstypen genügen nicht.

Nicht gleichmäßig alle Wurzeln tiefer teilen. Einen schwer lösbaren Elternfall zunächst
weiterlaufen lassen bzw. seinen Zustand erhalten und die Teilung kontrolliert beurteilen.
Eine Teilung ist vorteilhaft, wenn sie die erwartete Zeit bis zum geprüften Abschluss
bei tragbaren CPU-/Speicher-/Proofkosten senkt. Schlechtere Gesamt-CPU kann zugunsten
kürzerer Wallzeit akzeptabel sein, muss aber sichtbar bleiben.

Stoppregel: nicht weiter verfeinern, wenn Teilfälle schon gut lösbar sind oder zusätzliche
Tiefe vorwiegend Grundarbeit und Proofdaten vervielfacht. Keine starre Zieltiefe und
kein Zielwert „möglichst viele Fälle“. Falls sämtliche Varianten auch an Kontrollpunkten
kaum Fortschritt zeigen, zur Mathematik zurückkehren statt nur die Fallzahl zu erhöhen.

### E. Ausschlüsse verallgemeinern und Produktion erst danach planen

Aus erfolgreichen Ausschlüssen möglichst kleine hinreichende Teilbelegungen gewinnen.
Jede verallgemeinerte Aussage benötigt einen eigenen korrekten Beleg unter ihrer
wirklichen Basisformel; ein fertiger Proof lässt sich nicht einfach durch Weglassen
von Annahmen verallgemeinern. Symmetrietransporte nur mit nachgewiesener Gruppenwirkung.

Eine erst auf wenige weitere Wurzeln übertragbare Ausschlussregel kann mehr sparen
als eine viel feinere vollständige Enumeration. Das historische Musterverfahren ist
hier eine methodische Erfahrung, keine Garantie gleicher Wirksamkeit für LOW.

Produktionsfreigabe erst nach ausreichender Aussage über Prüferaufwand, schwierige
Restfälle und Ressourcenbedarf. Dann Wurzeln bzw. schwere Teilfälle dynamisch verteilen;
Prüferparallelität nach gemessenem RAM wählen, nicht nach der Zahl logischer Kerne.

## 5. Vergleichspunkte für den Reviewer

1. Hält er das gekoppelte X-System für eine aussichtsreiche notwendige Zwischenstufe,
   oder erwartet er fast immer zahlreiche Lösungen? Kann er konkrete Obstruktionen ableiten?
2. Welche Zerlegung ist vorzuziehen: X-Kanten, Markierungsdaten, zweiter Anker oder
   andere globale Invarianten? Welche Vollständigkeits- und Symmetrieargumente trägt sie?
3. Welche der Annahmen über Aufwand, Wiederverwendung und adaptive Tiefe bestreitet er?
4. Welche kleinste Messung könnte zwischen unseren Strategien entscheiden?

Dieser Plan wird vor dem Reviewerabgleich festgehalten. Neue Argumente oder negative
Versuchsergebnisse sollen ihn ändern dürfen; es gibt noch keine empirisch begründete
Festlegung auf einen vollständigen X-, Zwei-Anker- oder direkten LOW-Produktionslauf.
