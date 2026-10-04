# P0/P1: Zählsemantik, Ganzzahlsicherheit und neue Filter

Regelbasis/Forschungsstand: a8c88807acb0e07aae1c102cce18facdbcbdfecb,
AGENTS.md, docs/EXPERIMENT_RULES.md und docs/operations/GLOBAL_CONCLUSIONS.md.
Freigabe: ROOT8105-Übergabe04.10.2026,21:02Berlin. Regeln GC-01/02/10/11/15/18/19/20.

## Historisches F bei einer gebauten Rootzeile u=0

H-Labels sind alle nicht gematchten Zweiermengen des14er-Borders. Eine Zielzeile
ist eine Teilmenge dieser84 Labels, ohne Diagonale. Das Bordergradprofil beträgt
1 auf den vier Labels-Endpunkten/Partnern und sonst2, Summe24, somit12 H-Nachbarn.
Für target t gilt zusätzlich die festgelegte Adjazenz zu u und
|N(t)∩N(u)|=2−A(t,u)−|label(t)∩label(u)|.

Die beiden Borderendpunkte von u haben jeweils Marge1. Daher gibt es in N(u)
genau zwei Labels mit einem gemeinsamen Borderpunkt mit u; diese müssen im
H-Stern von u isoliert sein. Die übrigen zehn Labels haben im Stern Grad1,
bilden also ein beliebiges Matching. Bei t∉N(u) ist dieser Stern unabhängig
von den Zielvariablen. Bei t∈N(u) ist t entweder isoliert oder erhält genau
einen Partner unter den nichtisolierten Labels. Nach seiner Festlegung bleiben
zehn oder acht nichtisolierte Vertices: ein Matching existiert. Deshalb genügen
in Tiefe1 die in `constraints` kodierten Verbote und Schnittzahl. Diese Argumentation
würde bei mehreren gebauten Sternen nicht genügen: dort sind Sternvariablen
gekoppelt. Der neue Produktionskern bietet absichtlich kein allgemeines Tiefe-DP.

Die Kanten-DP nimmt jedes erlaubte Label einmal auf oder lässt es weg. Für
Pflichtlabels fehlt der Weglasszweig. Nach dem letzten inzidenten Label eines
Bordervertex wird dessen Achse auf die Sollmarge eingeschränkt und entfernt.
Die Schnittzahlachse verwirft Überschreitungen. Jede gültige Teilmenge besitzt
genau einen Pfad; der Endwert zählt Zielzeilen, nicht SAT-Hilfsbelegungen.

## Overflow: alle Zwischenzellen, nicht nur Endcounts

Ein Zwischenzustand entspricht einer Menge bereits bearbeiteter Labels mit
insgesamt höchstens12 Kanten: auch eliminierte Achsen haben ihre festgelegten
Sollgrade, aktive Achsen überschreiten ihre Margen nicht. Jede Teilmenge wird
höchstens einmal pro Zelle gezählt. Daher gilt für jeden additiven Zwischenwert

B7 = Summe(k=0..12) binomial(84,k) = 134744793483572 < 2^63−1.

Nichtnegativität und disjunkte include/exclude-Zweige machen diese Schranke
auch für die Addition selbst gültig. Für m11 ergibt derselbe grobe Ansatz
13209545928180561418432660246 und rechtfertigt **kein int64**.
Der NumPy-Zähler prüft Bm vor der Allokation und verweigert m11.
Der unabhängige Vertexzähler verwendet beliebig große Python-Integer;
daraus folgt keine Speicher-/Laufzeitfreigabe für m11.

## Uniformsampler und deterministische Zielregel

Im Vertexzähler wird der kleinste Bordervertex mit positivem Restgrad gewählt.
Alle Kombinationen seiner späteren Nachbarn werden lexikographisch durchlaufen;
jede Restbelegung wird eindeutig an einem solchen Zweig gezählt. Diese Zerlegung
liefert eine Bijektion [0,W)→gültige Zeilen. `randrange(W)` und exaktes Unranking
sind damit uniform, ohne Gleitkomma-Gewichte. Exhaustive kleine Rangbijektionen
und unabhängig SAT-geprüfte m7-Ränge kontrollieren die Implementierung.
Dies ist ausschließlich ein Tiefe1-Sampler; kein P2-Baumsampler wurde freigegeben.
Die bereitgestellte spätere Zielregel R-min-all-v1 minimiert (Breite,Label-ID)
über alle offenen Zeilen, inklusive Breite0, ohne verborgenen Zufallszustand.
Der Zensus selbst misst ohnehin alle83 Ziele und verwendet keine Pfadgewichtung.

## LD: Label-Disjunktheit

Sind v,w beide Nachbarn einer gebauten H-Zeile u und teilen einen Bordervertex c,
hätte eine Kante v–w die beiden verschiedenen gemeinsamen Nachbarn u,c. Das
verletzt lambda=1. Also wird edge(v,w)=0 erzwungen. Ist diese Kante bereits1,
wird der Zustand verworfen. Bei offenen Paaren reduziert LD die verfügbaren
Kapazitäten. Keine Behauptung einer exakten Zählung überlebender Kinder.

## C(S): Kapazitäten

Jede noch offene H-Zeile v hat Grad2m−2, feste Border-Margen und für jede gebaute
Zeile u die lineare Gleichung sum(w∈N(u)) A(v,w)=2−A(u,v)−|label(u)∩label(v)|.
Bekannte Einsen liefern lo; Einsen plus noch mögliche unbekannte Variablen hi.
Jede echte Completion erfüllt lo≤Soll≤hi. Diagonale und bewiesene LD-Nullen
zählen nicht als Möglichkeiten. Verletzung irgendeiner dieser Ungleichungen
ist daher ein notwendiger Widerspruch. Getrennte Kapazitätsintervalle prüfen
keine gekoppelte Gleichzeitigkeit aller Stern-/Margengleichungen.

Die Modellkennung `F+LD+CAP-v1-per-state` bleibt getrennt vom historischen F.
Die24 gepaarten m7-Kontrollen nutzen identische gespeicherte Eltern und Kinder;
sie sind feste Prüffälle mit Rand-/Mittelrängen plus Zufallsrängen, **keine
repräsentative Wirksamkeitsstichprobe**. Erst die Zensusdaten und ein eigener
gepaarter Messplan tragen spätere Wirksamkeitsentscheidungen. Kein vollständiger
zweiter Zensus wird automatisch gestartet.

## Abgrenzung der neuen P0-Prüfung

Die acht Tiefe3-Vergleiche (m4–m7), einschließlich344295 und328668 bei m7,
bleiben die bereits ausgeführten Belege des übernommenen Reviews. Dieses
Paket verändert keinen allgemeinen Tiefe-DP und beansprucht keine erneute
Ausführung dieser acht Fälle. Neue Kontrollen konzentrieren sich auf den
tatsächlich ausgelieferten Tiefe1-Zähler, den Sampler und die notwendigen
Filter. Insbesondere ersetzt die Kapazitätsprüfung keine gekoppelte
Stern-SAT-Prüfung eines späteren allgemeinen Zählers.
