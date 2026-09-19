# Abgleich des tatsächlichen Reviews — 19.09.2026
Dieser Bericht ersetzt die Aussage „Reviewertext fehlt“ für den jetzt vorliegenden Eingang files (10).zip. Die frühere Feststellung über files (9).zip bleibt korrekt. Eigene Bewertung und Original sind getrennt.

## Provenienz
Originalreview und ZIP byteidentisch archiviert auf reviews/20260919-memetik-grossversuch, Commit d2140c17bf4643295d7d71abe23c034a31a65944.
Review: REVIEW_grossversuch_20260919.md, SHA256 d9bc59667bef661806d91c6d1bbd89607acd6bbec97586650872018bffe3e1cb.
ZIP: 221632 Bytes, SHA256 642ea670030b5646bcf86ec23f40da21d6613c898b0be4bf2eca3325deae87e5.
Der Review begutachtet 958744f8b53ce66894a8b29e9bdfa033871574b0, nicht unseren erst danach verfassten Ryzen-Plan 39bbcb50a72daae1e853e9a762dd110e79a76490. Seine Kritik darf nicht rückwirkend als Prüfung dieses neueren Plans ausgegeben werden.

Beide Randdateien sind byteidentisch zum vorigen ZIP, inklusive der im Review angegebenen SHA256 der unkomprimierten Inhalte. Ihre 6006 Graphen wurden bereits im vorigen Schritt unabhängig vollständig auf Arm und Kennzahlen geprüft. Keine unnötige Wiederholung. Die Randvollständigkeit beruht weiterhin auf der Katalogenumeration; bloß alle Randgraphen zu liefern macht ein Negativzertifikat noch nicht selbsttragend.

## Kurzurteil
Dem Urteil „nach benannten Korrekturen startbereit“ stimme ich methodisch zu. Es bezeichnet die Bereitschaft zum begrenzten methodischen Vergleich, nicht die Lieferfähigkeit sämtlicher Generatoren oder eine bereits implementierte Großkampagne.
Wichtigste Änderung: nicht 128 lieferbare Gründer und 384 Plätze vorab unterstellen, sondern kleinere Vergleichspopulationen und ausreichende unabhängige Wiederholungen. Gute bestehende Familien bevorzugen, neue Erzeuger getrennt qualifizieren.

## Übereinstimmungen und Präzisierungen
| Gegenstand | Abgleich |
|---|---|
| B-Barriere 12, vollständiger Zeuge | Stimmt mit eigener Prüfung überein. War bereits als exakt minimal dokumentiert; hier korrigiert der Review eher die Betonung als einen Fehler. Minimale uneingeschränkte Verbesserungsweglänge liegt nach vorhandener BFS und Zeuge zwischen 3 und 5; nicht zwangsläufig dieselbe Optimierungsfrage wie kürzester barriereoptimaler Weg. |
| C08: kürzester W-Weg Länge zwei | Bereits ausdrücklich so dokumentiert, durch Reviewer-Nachrechnung zusätzlich gestützt. Kein neuer Befund erstmals aus dem Review. |
| HoG≥192 | Review kann mangels SQLite nicht prüfen. Wir hatten Integrität, Zählungen und Elternrekurrenzen tatsächlich geprüft. Fehlender Reviewerzugriff macht diese Prüfung nicht ungeschehen; vollständige unabhängige Nachbarschaftsreproduktion fehlt weiterhin. |
| A: acht Isomorphieklassen | Zusätzlicher Reviewerbefund; eigene neue Sitzung prüft nicht nochmals die Isomorphien. Als extern nachgerechnet kennzeichnen, nicht als von uns neu erzeugtes Zertifikat. |
| Familienregister, Ω-Rahmen, zielbezogene Besuchsspeicher | Übernommen. Ein gemeinsam gespeicherter Graph darf mehreren Zielen dienen, aber „bereits besucht/ausgeschöpft“ ist ziel- und zustandsabhängig. |
| Kleine Seedzahlen | Kritik berechtigt. Drei Läufe dürfen eine grob schlechte Variante aussortieren, nicht generell Überlegenheit beweisen. Neue Bestätigung mit unabhängigen gepaarten Laufseeds und vorher festgelegtem Kriterium. |
| Tripeldarstellung | Äquivalenz zum λ-Vertrag ist eine korrekte Repräsentation, kein Beleg einer neuen Strukturklasse oder eines leistungsfähigen Generators. |
| Gradbedingung bei PD=0 | Mathematisch redundant: 1ᵀP=2·1ᵀ, also 1ᵀD=0; mit D symmetrisch auch D1=0. Grad im unabhängigen Prüfer trotzdem kontrollieren, um Implementierungsfehler zu entdecken. |
| Frühere A-Reparaturversuche | Unsere erste Generatorskizze hätte diese Vorarbeit ausdrücklich nennen müssen. Bekannte CP-SAT/MILP-Fensterformulierungen nicht nochmals als neue Idee anbieten. |
| Generische Tripelgeneratoren erfolglos | Als Reviewerexperiment ernst nehmen, jedoch ohne Code/Seeds/Logs nicht eigenständig reproduziert. Claudes vorhandener gültiger Kandidat bleibt gültig; kein Widerspruch zur Existenz solcher Graphen. |

## Eigene Zusatzprüfung des Ω-Katalogs
Kombinatorisch unabhängig gezählt: 2121 Viererkreise, 108080 Sechskreise, 17220 Bowties im Rahmengraphen K14 minus 7K2. Ein ±1-Kernvektor balanciert die Vorzeicheninzidenzen an jedem Rahmenknoten. Bei Träger 4 ist nur ein Viererkreis möglich; bei Träger 6 ein Sechskreis oder zwei Dreiecke mit gemeinsamer Ecke. Disjunkte Dreiecke lassen keine Vorzeichenbalance zu. Je zulässigem Träger gibt es genau eine Belegung modulo globalem Vorzeichen.

Mit der archivierten Vektorenumeration zusätzlich geprüft: keine Dubletten modulo Vorzeichen, alle erzeugten Vektoren tatsächlich in ker(P), Anzahl 2121 bzw. 125300. Damit passt die implementierte Enumeration zur kombinatorischen Charakterisierung.
Am Startgraphen A bestätigen sich für Träger 4 exakt die Kompatibilitätszahlen des Reviews (Maximum 9) und die sechs rechten 4-Vektoren, keine rechten 6- oder 8-Vektoren. Für Träger 6 beträgt das Maximum 5, mit Verteilung 0:76113, 1:38952, 2:8930, 3:1177, 4:111, 5:17.
Prüfcode und CATALOG_CHECK.json sind beigefügt. Diese Aussagen betreffen den Startgraphen A, nicht automatisch jeden der sieben anderen Zustände unter erweitertem Katalog. Vollständigkeit einer Produktklasse ist kein Vollständigkeitsbeweis für alle Ω-erhaltenden Änderungen.

## Einwände gegen den Review
1. **Überlappende Träger im selben Rang-2-Ansatz sind ausgeschlossen.** Für D=xyᵀ+yxᵀ ist D_ii=2x_i y_i. Nulldiagonale erzwingt disjunkte Träger. Überlappung ist erst in einer anderen Formulierung mit zusätzlichen kompensierenden Termen möglich; das ist keine einfache Erweiterung derselben Familie.
2. **Randlisten allein sind kein selbsttragender Vollständigkeitsbeweis.** Sie machen Randkennzahlen unabhängig prüfbar. Es muss weiterhin nachgewiesen werden, dass kein zulässiger Ausgang fehlt. Die mitgelieferten Randobjekte nennen Eltern/Familie, aber keine vollständige unabhängige Abdeckung aller Trades.
3. **230 Tripel bedeuten drei fehlende Inzidenzen, nicht zwangsläufig drei verschiedene defiziente Punkte.** Bei maximal sieben Tripeln pro Punkt können die Defizite auch 2+1 oder 3 lauten. Ein einziges abschließendes Tripel funktioniert nur bei drei verschiedenen Punkten mit jeweils Defizit eins und passenden Nachbarschaften. Ein Endspiel muss den ganzen Defizitvektor verwenden.
4. **Anbieterzahl belegt keine Methodenzahl.** Die zehn Codex-Graphen stammen aus F02 und den verwandten F03/F04-Lifts. Die vorhandenen Abnahmen dokumentieren außerdem Z14, freien Ω-CSP und unregelmäßige Tripelpackung. Das Register ist zu vervollständigen, aber „zehn von einem Anbieter“ ist kein Gegenargument gegen mehrere Methoden. Ebenso sind G1/G2 nicht automatisch getrennte Familien.
5. **Acht Gründerpaare garantieren keine statistische Absicherung.** Bei drei unabhängigen Paaren hat ein einseitiger Vorzeichentest selbst bei drei Siegen p=1/8. Bei acht lauter Siegen wäre p=1/256, aber das sagt nichts über Effektgröße, Abhängigkeiten, Auswahleffekte oder mehrere Ziele. Neue Statistik basiert auf unabhängigen vollständigen Läufen, nicht auf Individuen derselben Population.
6. **Isomorphie und Strukturabstand beantworten verschiedene Fragen.** Kanonische Zertifikate entscheiden Identität, liefern allein keine sinnvolle Distanz zwischen Nichtisomorphen. Profile bleiben Diagnostik; für die erste Kampagne verwende ich sie nicht als primären Neuheitsbeweis oder fest gewichtetes Qualitätsziel.
7. **„A-Erweiterung negativ entschieden“ gilt nur eingeschränkt.** Die gemessene Starrheit rechtfertigt geringe Priorität. Sie schließt weder beidseitig große Träger noch andere algebraische Formen oder Ausgänge an anderen Komponentenzuständen aus.
8. **Existenz ist nicht algorithmische Erreichbarkeit.** Gültige HoG/C08-Graphen zeigen, dass λ-Kandidaten existieren, nicht dass ein bestimmter Greedy-/Reparaturalgorithmus sie erreichen kann.

## Konsequenz
RYZEN_PLAN_V2.md ersetzt die operative Empfehlung des vorherigen Ryzen-Plans. Keine neuen langen Minimax-Läufe, keine Wiederholung alter erfolgloser A-Modelle. Kleine Populationen für Methodenvergleich, konservative Referenz als Standard, größere Suchpopulation erst nach Prüfung von Generatorausbeute und Durchsatz. Der Review selbst bleibt unverändert archiviert.

