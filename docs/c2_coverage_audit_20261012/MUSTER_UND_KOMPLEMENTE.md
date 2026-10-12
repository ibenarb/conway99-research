# Von 7.388.648 Censusbahnen zu genau 234.691 Restfällen

Stand 12.10.2026. Eigene Fortsetzung nach dem Reviewerpaket V2.
Die Aussagen gelten relativ zu F346 und übernehmen die historischen UNSAT-Prüfungen.
Kein allgemeiner C2-Ausschluss und keine erneute Prüfung der DRAT-Beweisdateien.

## 1. Transportlemma für partielle Muster

Seien P und N disjunkte Mengen gerichteter Ankerpaare. Das Muster U(P,N) fordert
alle Pfeile in P und verbietet alle Pfeile in N; andere Pfeile bleiben frei.
Ist F346 zusammen mit U(P,N) unerfüllbar, so kann kein mathematisches F346-Modell
einen Pfeilgraphen D besitzen, in den sich dieses Muster durch eine Permutation
der sieben Anker einbetten lässt.

Beweis: Angenommen, eine Permutation g bettet das Muster in D ein. Benenne das
vollständige Rahmenmodell mit g invers um. Die Gleichungen E1–E3 und die
Beschränkung aller sieben Ausgrade auf {3,4,6} bleiben erhalten. Das umbenannte
Modell erfüllt U(P,N) und lässt sich nach ENC auf eine Belegung der betreffenden
CNF erweitern. Dies widerspricht dem gebundenen UNSAT-Ergebnis. Eine syntaktische
Permutation der Hilfsvariablen ist nicht erforderlich. Ebenso wenig wird eine
zusätzliche Grad- oder Matchingnormalisierung in der Formel vorausgesetzt.

Die Verbindung der 42 Bitpositionen mit den Primärvariablen wurde neu aus den
Labels und B/C-Einträgen der erzeugten `variables.json` abgeleitet. Für jedes
verwendete Muster stimmen positive Maske, negative Maske, geordnete Units und
negierte Ausschlussklausel miteinander überein.

## 2. Was der Mustertest genau entscheidet

Der unverändert übernommene historische `coverage.cpp` wird hier im Quelltext
begründet und neu ausgeführt; er ist **keine unabhängige Neuimplementierung**.

Er durchsucht injektive Zuordnungen derjenigen Musterknoten, die an wenigstens
einer geforderten oder verbotenen Kante beteiligt sind. Die Suchreihenfolge ist
nur eine Heuristik. Die Vorprüfungen zu positiven und negativen Ein-/Ausgraden
sind notwendige Bedingungen und entfernen daher keine gültige Zuordnung.
Nach der Zuordnung eines Knotens werden sämtliche Bedingungen in beiden
Richtungen zu allen bereits zugeordneten Knoten geprüft. Am Suchblatt sind
folglich sämtliche Musterbedingungen geprüft. Musterknoten ohne Bedingungen
lassen sich beliebig bijektiv auf die noch freien Zielknoten verteilen.

Damit liefert der Test genau dann einen Treffer, wenn eine Permutation aus S7
das Muster in den Zielgraphen einbettet. Er prüft jedes Muster; überlappende
Treffer zählen für die Vereinigung nur einmal. Die Datei der Nichttreffer behält
alle Originalzeilen und deren Reihenfolge bei.

Zusätzlich wurden die historischen Kontrolltests neu ausgeführt: alle 4.096
beschrifteten gerichteten Vierknotengraphen mit mehreren Mustermengen,
einschließlich leerer Mengen und negativer Bedingungen, sowie 82
Siebenknotengraphen. Vergleichsinstanz ist die explizite Enumeration sämtlicher
Permutationen. Diese Tests ergänzen das Argument, ersetzen es aber nicht.

## 3. Exakte Mengenübergänge

| Übergang | Entfernte Bahnen | Verbleibende Bahnen |
|---|---:|---:|
| Originalcensus | — | 7.388.648 |
| Vereinigung der sechs Generalize-Muster | 4.686.633 | 2.702.015 |
| Verbliebene Fälle mit genau einem Grad-3-Anker | 1.032 | 2.700.983 |
| Vereinigung der 86 Generalize2-Muster | 2.466.285 | 234.698 |
| Verbliebene Fälle mit genau zwei Grad-3-Ankern | 7 | 234.691 |

Die 86 Muster umfassen 18 partielle Muster und 68 vollständige Pfeilprofile.
Die 68 Profile sind die nach Entfernung redundanter Mustersupersets tatsächlich
verbliebenen Pilotmuster. Diese Zahl ist nicht mit den 80 im historischen
Generalize2-Lauf zusätzlich übernommenen Pilotfällen gleichzusetzen.

Die ersten und dritten Übergänge wurden über die vollständigen Eingabelisten
neu berechnet. Alle einzelnen Mustertrefferzahlen stimmen ebenfalls mit den
historischen Berichten überein. Die One3- und Two3-Schritte wurden aus den
jeweils neu gebildeten Restlisten gefiltert und mit den Zertifikatsfallmengen
verglichen. Insbesondere wird keine ganze Gradscheibe allein wegen ihres
Namens verworfen: Genau ihre noch vorhandenen Elemente müssen zertifiziert sein.

Jede resultierende Restdatei reproduziert den historischen SHA-256-Wert. Die
letzte Datei ist bytegleich mit `remaining_234691.tsv`. Damit ist sie jetzt als
**exaktes Komplement** dieser Ausschlussvereinigung bestimmt; zuvor war nur ihre
Teilmengenbeziehung zum Census neu geprüft.

Die vollständigen Zahlen und Hashes stehen in
[set_audit.json](../../results/c2_coverage_audit_20261012/set_audit.json).

## 4. Bindung an die historischen Ausschlüsse

Für die gemeinsame Basis F346 mit SHA-256
`33fc424d5e0ce00179a5abbde52c56b40e4e1fcbc272c36d595ef29354e3b030`
wurden die historischen Formeln als Basis plus die geordneten Unit-Klauseln
neu gehasht. Geprüft wurden:

| Beleggruppe | Geprüfte Belege |
|---|---:|
| One3 | 1.032 |
| Two3 | 7 |
| Zertifizierte Generalize-Versuche | 38 |
| Zertifizierte Generalize2-Versuche | 96 |
| Zertifizierte ursprüngliche Pilotfälle | 200 |
| Summe | 1.373 |

Für jeden Beleg stimmen Formelhash, Solver-/Checker-Kommandopfade,
Solver-Proofhash, archivierter Rohproofhash sowie die gehashten Solver- und
Checkerlogs zusammen. Die Logzeilen enthalten die erwarteten Endurteile;
die separat gespeicherten Operationsberichte stimmen mit den eingebetteten
Berichten überein. Vollständige Profile enthalten genau die 42 zum jeweiligen
Code gehörenden positiven oder negativen Units. Alle sechs beziehungsweise
86 tatsächlich benutzten Muster sind an wenigstens einen dieser Belege gebunden.

Die Zahl 1.373 ist die Anzahl geprüfter Belegdatensätze, nicht die Anzahl
paarweise verschiedener ausgeschlossener Bahnen; partielle Muster überdecken
viele Bahnen und verschiedene Belege können sich überlappen.

Berichte: [binding_audit.json](../../results/c2_coverage_audit_20261012/binding_audit.json)
und [certificate_bindings.json](../../results/c2_coverage_audit_20261012/certificate_bindings.json).

**Prüfgrenze:** Die archivierten Proofhashes sind hier Identitätsangaben aus den
historischen Belegen. Die externen komprimierten Beweise wurden in diesem Audit
nicht gelesen; kein SAT-Solver und kein DRAT-Checker wurde gestartet. Die
UNSAT-Aussagen werden aus den historischen erfolgreichen Prüfungen übernommen.
Die neue Leistung ist die durchgehende Zuordnung ihrer Formeln und Muster sowie
die neu berechnete exakte Abdeckung.

## 5. Schluss und verbleibende Aufgaben

Unter ENC, dem semantischen S7-Transport und Anerkennung der genannten
historischen Checkerprüfungen liegt jeder nach diesen Schritten noch mögliche
Censusfall in genau der gehashten Restliste mit 234.691 Elementen.

Damit ist der Übergang **Census → Rest234691** geschlossen innerhalb dieser
expliziten Prüfgrenzen. Noch gesondert zu schließen sind die nachfolgenden
Musterübergänge über 6.651 und 406 zu Rest218. Der vorhandene Rest218-Abschlussaudit
und die allgemeinen offenen Fälle mit Ankergrad 0, 1 oder 2 werden dadurch
weder ersetzt noch erweitert. H346 und der allgemeine C2-Satz bleiben bis zur
jeweiligen vollständigen Verbindung bedingte Ziele.

## 6. Reproduktion und Provenienz

Die Programme `audit_bindings.py` und `audit_sets.py` stehen unter
`src/c2_coverage_audit_20261012`. Sie erwarten als einziges Argument das lokale
Arbeitsverzeichnis mit den im Eingabemanifest beschriebenen entpackten Quellen,
dem Originalcensus und der bereits rekonstruierten Basis samt Variablenabbildung.
Python-Assertions müssen aktiviert bleiben. `audit_sets.py` kompiliert den
gehashten historischen Matcher mit `g++ -O3 -std=c++17`, führt die Kontrollen aus
und berechnet die beiden vollständigen Musterabdeckungen.

Die erforderlichen historischen Archive sind dieselben bereits im Quellenregister
verorteten Originalexporte. Das Eingabemanifest nennt ihre Hashes, die verwendeten
lokalen Extraktionsnamen und die zentralen Metadatendateien. Die Originalarchive
binden auch die gelesenen Logs und Operationsberichte; die einzelnen
Checkerloghashes stehen zusätzlich im Belegregister. Dauerhafte
öffentliche Downloadadressen für noch externe Beweis-/Datenarchive sind weiterhin
eine eigene Aufgabe vor dem Publikationsrelease. Lokale Pfade sind keine
öffentlichen Bezugsadressen.

## Nachtrag zur Fassung 0.5

Die in Abschnitt 5 noch offenen Übergänge bis Rest218 wurden in der
[späten Fortsetzung](../c2_late_audit_20261012/ABSCHLUSS_PROFIL346.md) geschlossen.
Die historischen Checkerprüfungen und der vorhandene Rest218-Abschlussaudit
bleiben unter ihren ausdrücklich dokumentierten Grenzen übernommen.
