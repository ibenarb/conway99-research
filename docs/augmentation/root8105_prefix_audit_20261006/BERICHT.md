# ROOT8105: unabhängige Prüfung der 17 Tiefe-13-Präfixe

Stand 06.10.2026. Ausgangsstand d402d52f69d23b7f71ee7a77ff86db958f7e4e2b;
fixierter Suchcode 05fee711592baebc469ab7461376be3ca89046d0;
Run fb64e03e22304cb496455ceaa0af1c27.

## Ergebnis

**17/17 gespeicherte Endpfade des Arms Nachbarschaft zuerst plus Vorwärtsprüfung
wurden rekonstruiert und bestehen die unten genau abgegrenzten unabhängigen
Präfixprüfungen.** Es sind 17 verschiedene beschriftete Präfixe aus 12 Roots;
eine Isomorphieklassifikation wurde nicht vorgenommen. Für jedes Präfix existiert
zusätzlich eine explizite, direkt geprüfte gemeinsame Belegung seiner abgeschlossenen
Sternbedingungen. Die Akzeptanzkriterien dieses Arbeitspakets sind erfüllt.

Dies ist ein rechnerisch geprüfter Nachweis für die angegebenen endlichen
Bedingungen und Sternrelaxationen, kein Nachweis einer vollständigen SRG-Ergänzung,
kein Rootausschluss und keine Aussage über alle 8105 Roots. Die Unsicherheit der
früheren Baumgrößenschätzung und INSUFFICIENT_INFORMATION bleiben unverändert.

## Rekonstruktion und Unabhängigkeit

Die Auswahl sind exakt die 17 Datensätze mit cell=3 aus DEPTH13_PATHS.json des
veröffentlichten Audits. Es gab keine Ersatzpfade. Der Quellbestand wurde mit dem
Fingerprint des ursprünglichen Manifests abgeglichen. Für die benötigten 12 Roots
wurden die Matchingrepräsentanten zur eindeutigen Auflösung der gespeicherten
Matchingklassen rekonstruiert. Anschließend wurden ausschließlich die gespeicherten
204 Zeilenränge entpackt; die dafür erforderlichen Rekursionssummen stimmen mit
den gespeicherten Vorschlagsbreiten überein. Keine neuen Zufallsabstiege,
keine Wiederholung der 40000er Messung und kein Vollcensus.

Die Rekonstruktion verwendet bewusst den originalen Sampler und die originale
Propagation, um dieselben gespeicherten Objekte wiederherzustellen. Der separate
Prüfer independent_check.py importiert keines dieser Module. Er erzeugt die
Labelabbildung und den partiellen 99-Graphen selbst und prüft die expliziten
Nachbarschaftslisten. Rekonstruktion und unabhängige Prüfung sind unterschiedliche
Schritte. Die gespeicherten Propagationsbelegungen werden auf Widersprüche geprüft;
damit wird nicht die allgemeine Korrektheit jeder Regel des Propagationsprogramms
bewiesen.

## Geprüfte Bedingungen

Nummerierung des unabhängigen Prüfers: Basisvertex 0; Randvertices 1 bis 14;
H-Vertex u hat Nummer 15+u. Die Randpaare sind (1,8), ..., (7,14).
Die 84 H-Labels sind lexikographische Zweiermengen aus 0,...,13 ohne antipodale
Paare. Die gespeicherten H-Nachbarschaftslisten verwenden weiterhin 0,...,83.

Jedes Präfix enthält die vollständige H-Zeile 0 und genau ihre zwölf H-Nachbarn.
Zusammen mit Basis und Rand sind damit 28 von 99 Nachbarschaftszeilen vollständig;
71 H-Zeilen sind offen. Geprüft werden:

- Labelabbildung, Indexgrenzen, doppelte Nachbarn, Schleifenfreiheit und Symmetrie;
- H-Grad 12, Gesamtgrad 14 aller vollständigen Zeilen und notwendige Gradintervalle
  der offenen Zeilen unter den gespeicherten Festlegungen;
- exakte gemeinsame Nachbarzahlen für alle 378 Paare vollständiger Zeilen:
  1 bei Kanten, 2 bei Nichtkanten. Das umfasst insbesondere die Randmargen und
  Paarbedingungen der H-Zeilen;
- notwendige Unter-/Obergrenzen gemeinsamer Nachbarzahlen für alle 4851
  Vertexpaare. Bei unbekannter Kante werden beide Möglichkeiten zugelassen;
- Matchingvorbelegung der Wurzelnachbarschaft: genau die zehn nicht randgepaarten
  H-Nachbarn bilden die fünf disjunkten Matchingkanten; die beiden randgepaarten
  Nachbarn besitzen innerhalb dieser H-Nachbarschaft keine Kanten;
- gemeinsame Erfüllbarkeit der 392 orientierten abgeschlossenen Sternbedingungen.

Für jede vollständige Zeile u und jeden Nachbarn v gilt dabei
sum_{w in N(u)} A[v,w] = 1. Damit muss jede vollständige Nachbarschaft ein Matching
bilden. Alle diese Gleichungen teilen dieselben Variablen für offene Kanten;
es werden nicht lediglich getrennte lokale Matchingtests durchgeführt. Die
14 Randnachbarschaften sind ebenfalls enthalten. Auch der Stern der zuletzt
rekonstruierten H-Zeile wird einbezogen; dies ist mehr als ein bloßes Wiederholen
des letzten historischen Projektionsaufrufs vor dem Einfügen dieser Zeile.

Glucose4 findet die Belegungen einer unabhängig aufgebauten CNF. Danach prüft
verify_witness jede ursprüngliche Ganzzahlgleichung direkt, ohne CNF-Hilfsvariablen
oder Solverstatus als alleinigen Beleg. Die 17 Belegungen umfassen jeweils
643 bis 660 noch offene Kanten und sind in den Präfixdateien gespeichert.

**Grenze:** Die Sternbelegung belegt nur die Sternrelaxation. Sie wird nicht als
Belegung sämtlicher noch offener Grad-, Rand- und Codegreegleichungen ausgegeben.
Die Intervallprüfungen gelten für den gespeicherten partiellen Zustand; sie sind
keine gemeinsame Erfüllbarkeitsprüfung aller SRG-Bedingungen. Insbesondere bleiben
die Paarbedingungen zwischen zwei offenen vollständigen Zukunftszeilen ungelöst.

## Kontrollen und Betrieb

Ein vollständig und unabhängig ausgewerteter 3x3-Rookgraph srg(9,4,1,2) besteht
als Positivkontrolle derselben parametrisierten Graphbedingungen. Neun gezielte
Beschädigungen werden erkannt: vertauschte Labels, Schleife, gelöschte Kante,
doppelter Nachbar, asymmetrische Kante bei erhaltenem Zeilengrad, doppelte
Matchingkante, widersprüchliche Festlegung, gekippte und fehlende Sternbelegung.
CONTROLS.json enthält die konkreten Ablehnungsgründe. Die Positivkontrolle
begründet keine Laufzeitprognose für 99 Vertices (GC-20).

Die erneute Kontrolle der 17 gespeicherten expliziten Präfixe benötigt weder
Rekonstruktion noch SAT-Aufruf. verify_saved.py verwendet ausschließlich die
Nachbarschaftslisten und die gespeicherten Sternbelegungen; sein kleiner
Positivkontrollgraph wird separat geprüft.

Gemessen: 13,551289447 CPU-Sekunden für Rekonstruktion und neue Prüfungen im
Cloud-Prozess, einschließlich laufender Ergebnissicherung bis zur letzten
Zeitabfrage. Kein Gesamtprozesskonto und keine Ryzen-Zeitprognose. Keine neue
Zeitbudgetkampagne. Vorab lief der vorgeschriebene audit_python.py-Selbsttest
mit pynauty 2.8.8.1; numpy 2.2.6 und python-sat 1.8.dev24 waren vorhanden.

Ein erster technischer Start scheiterte vor jeder Rechnung, weil der neue Git-
Worktree die Ergebnisdateien wegen geerbter Sparse-Checkout-Auswahl nicht enthielt.
Nach Ergänzung der beiden benötigten Verzeichnisse lief die Rekonstruktion vollständig.
Keine Änderung am ursprünglichen Datensatz oder am eingefrorenen Suchpaket.

## Nächster Arbeitsschritt

Für jedes dieser 17 geprüften Präfixe die 71 offenen Zielzeilen vergleichen:
zunächst die notwendige lokale Vorschlagsbreite bestimmen. Diese ist nicht die
Zahl F-zulässiger Erweiterungen. Deren Bestimmung bzw. Schätzung muss separat
geplant werden, mit klarer Trennung zwischen vollständiger Enumeration,
Stichprobenbefund und UNKNOWN bei begrenzter Bearbeitung. Die gespeicherten
Sternbelegungen dürfen dabei nicht als zusätzliche dauerhafte Kantenfestlegung
verwendet werden: Sie sind lediglich Zeugen einer Relaxation.

Erst daraus eine Reihenfolge für Tiefe 14 und höher ableiten. Keine Großkampagne
oder zertifizierten Teilausschlüsse wurden in diesem Arbeitspaket begonnen.
Relevante Regeln: GC-08, GC-16, GC-17, GC-20, GC-22; bei neuen Zeitbudgets GC-19.
Offene Betriebskorrektur des bisherigen Laufpakets: finale Receipt-Serialisierung
separat abrechnen. Die abgeschlossene Messung bleibt unverändert.
