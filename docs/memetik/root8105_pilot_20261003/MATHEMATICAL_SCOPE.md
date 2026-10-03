# Mathematischer Aussageumfang und Korrektur

## Feste Reihenfolge

Die pauschale Formulierung in RECONCILIATION.md, eine Barriere unter einer
festen Zeilenreihenfolge reiche nicht, ist zu ungenau.

Wähle eine beliebige feste Permutation aller 84 H-Zeilen. Jeder vollständige
Graph induziert durch Einschränkung seiner Zeilen einen Pfad in genau dieser
Reihenfolge. Enumeriert jede Erweiterungsstufe alle zulässigen Zeilen und
verwirft nur nach bewiesenen notwendigen Bedingungen, bleibt dieser Pfad
bis zur vollständigen Lösung erhalten. Eine vollständig zertifizierte
Erschöpfung unter einer festen Reihenfolge genügt daher zum Ausschluss.

Anders verhält es sich mit der maximal erreichbaren Zahl teilweise gebauter
Zeilen oder einer Suche, die frühere Zeilen nur beschränkt auswählt. Hier
kann die Identitätsreihenfolge eine künstliche Tiefenbarriere erzeugen.
GC-17 bleibt für solche Tiefen-/Stichprobenaussagen relevant.

## Encoder

Sei S die Menge vollständig gebauter H-Zeilen. Die noch unbekannten Kanten
sind symmetrische Variablen h_ij für i,j außerhalb S, i<j. Diagonalen sind null.
Jede spätere vollständige Lösung erfüllt für die gewählte nächste Zeile q:

- für jeden Randknoten a die exakte Inzidenzmarge 1 oder 2;
- für jedes u in S:
  sum_w H_uw H_qw = 2 - H_uq - |label(u) ∩ label(q)|.

Da H_u* fest ist, sind diese Gleichungen linear in den offenen Variablen.
Zusätzlich wird für jedes u in S und jeden H-Nachbarn v von u dieselbe
Gleichung erzwungen. Zusammen mit den bereits feststehenden Randmargen
von u beschreibt dies die Matchingstruktur seines vollständigen Nachbarsterns.
Insbesondere kann kein erlaubter vollständiger Graph durch diese lokale
Closure ausgeschlossen werden. Die Zielzeile hat wegen der Summe ihrer
Randmargen automatisch H-Grad 12; eine weitere Gradgleichung ist redundant.

Es werden nicht alle quadratischen Gleichungen zwischen zwei offenen
H-Zeilen eingebaut. SAT bedeutet deshalb lediglich zulässige Zeilenprojektion
in einer notwendigen Relaxation, nicht Fortsetzbarkeit zu einem SRG.

## Kanonisierung

Der gefärbte Graph enthält den 14er-Rand mit seinem Matching, sämtliche 84
H-Labels als Inzidenzvertices und alle durch gebaute Zeilen bekannten Kanten.
Farben unterscheiden Rand, ausgezeichnetes u, übrige gebaute und offene
H-Zeilen. Damit ist festgelegt, welche abwesenden Kanten bekannt null und
welche noch unbekannt sind. Jede farberhaltende Isomorphie erhält exakt
diese Daten. Die Randinzidenzen erzwingen eine legitime Randgruppenwirkung.

Die kanonische Identifikation entfernt Reihenfolge-Duplikate und legitime
Rootstabilisator-Duplikate. Der Pilot implementiert kein vollständiges
kanonisches Elternkriterium und keinen fertigen x/u-Umrootungsoperator für
beliebige partielle Zustände. Diese Erweiterungen dürfen erst nach eigenem
Coverage-Audit zum Beweis-Pruning werden. Der Level-2-Rollentausch wird
separat an vollständig bestimmten Zwei-Stern-Graphen gemessen.

## Lokale Zertifikate und globale Grenze

Nach Enumeration der Projektionen r_1,...,r_t wird F ∧ B(r_1) ∧ ... ∧ B(r_t)
frisch erzeugt, wobei B(r_i) genau diese Zeilenprojektion verbietet. Ein
separat geprüfter DRAT-Widerspruch zeigt, dass F keine weitere Projektion hat.
Jeder SRG-Fortsetzungspfad muss also eine der aufgeführten Projektionen nehmen.

Der Pilot behält aber nur ein Reservoir und eine begrenzte Frontier.
Deshalb gilt die lokale Coverage nicht automatisch für seinen weiteren
Suchverlauf. Insbesondere sind TIMEOUT, SAMPLED_FRONTIER und CPU_LIMIT
keine Rootausschlüsse. Auch alle 128 Fälle zusammen decken nur die
vorab ausgewählte Stichprobe der 8105 Rootklassen ab.
