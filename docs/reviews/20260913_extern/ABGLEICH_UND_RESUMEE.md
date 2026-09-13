# Abgleich des externen Reviews vom 13. September 2026

## Status und Herkunft

Das unveränderte Original steht in `ORIGINAL.md`; Länge und SHA256 in `../../../results/reviews/20260913_extern/receipt.json`. Forschungsbasis: `450a1730e784822ef5425b27d7e5c608178fe078`. Das Review ist eine eigenständige externe Bewertung. Seine berichteten Eigenrechnungen werden als solche übernommen; die dazugehörigen selbst geschriebenen Skripte und vollständigen Ausführungslogs wurden nicht mitgeliefert. Der Bericht allein ersetzt diese Artefakte nicht.

Das Gesamturteil bestätigt unsere vorsichtig formulierte Bilanz. Besonders stark ist die berichtete unabhängige Reproduktion der gesamten 156→69→44→26-Kette sowie der K66-Arithmetik, Bahnen und Ergebnisverknüpfung. Die Primärliteratur und die K66-Encoder-/Zertifikatsschicht hat der Reviewer laut §5.2 dagegen nicht unabhängig auditiert. Daher wird der bisherige Beweisstatus nicht pauschal in „vollständig extern verifiziert“ umbenannt.

## Abgleich F1–F8

| Befund | Einordnung |
| --- | --- |
| F1: τ=27 schon durch algebraisches τ=6-Theorem ausgeschlossen | Richtig. Der Projektbeweis trägt den Ausschluss; f27 ist zusätzliche rechnerische Absicherung. Unsere Bilanz sagte bereits „zusätzlich“, die stärkere Gewichtung als Projekttheorem ist sinnvoll. |
| F2: 18 Zertifikate nicht bijektiv zu 18 Ausschlüssen | Richtig; die Vereinigungsmenge zählt. Überlappungen waren im früheren Resümee bereits ausdrücklich beschrieben. Ein behaupteter Atlasoffset darf nicht alleiniger Identitätsschlüssel werden: graph-/Gram-basierte Zuordnung ist robuster als Dateinummern. Die ℝ₊-Gültigkeit folgt unmittelbar durch nichtnegative Linearkombination der Profilungleichungen. |
| F3: Prüfer überschreibt Ergebnisdatei | Richtig; der vorhandene Reviewauftrag verlangte deshalb Scratch. Ein späterer --out-Modus verbessert die Benutzbarkeit, ist aber keine Reparatur der Mathematik. Im Rahmen dieses Abgleichs wurde der historische Prüfer nicht verändert. |
| F4: 84→62 angeblich nicht rekonstruierbar | Als Wunsch nach einer lokalen Erläuterung berechtigt; die Ursache ist keine fehlende Ausschlussbedingung. Es handelt sich um Quotientierung durch gemeinsame T-Vertauschung, siehe Rechnung unten. Diese Wirkung war im historischen V3-Dokument und im Bilanzgenerator enthalten. |
| F5: drei Lemmata explizit führen | Sinnvoll. Die Aussagen waren in Modell-/Zyklusdokumenten enthalten; ein gebündelter Beweis verbessert die Lesbarkeit. Siehe unten. |
| F6: 272 Proof-Hashes bei 656 CNFs | Selbst bestätigt. 656 bezeichnet Zertifikatsverwendungen, nicht unabhängige Proofbytes. Derselbe Proof muss für jede zugeordnete CNF gültig sein; die Mehrfachverwendung ist allein kein Fehler. |
| F7: historische a1=18-Voraussetzung erledigt | Richtig für diese Voraussetzung. „Unbedingt“ bedeutet weiterhin innerhalb des freien C3-Falls und des konkreten L-Typs, mit Modelltransfer und Checkergrundlage. Es ist kein unbedingter globaler Graphausschluss. Historische Manifeste bleiben unverändert. |
| F8: FULLCERT-Bindung | coverage_input.json fehlt weiterhin. Jedoch sind alle 656 TSV-Zeilen über ihre Schlüssel, Wurzeln, CNF-/Proof-/gzip-Hashes, Größen und Exitcodes mit dem festen certificate_manifest.json abgleichbar; der Abgleich bestand. Eine vollständige Rekonstruktion der ursprünglichen Coverage-Eingabe ist damit noch nicht erfolgt. Der gespeicherte Hash ist ein Fremddateiverweis, nicht im üblichen Sinn ein Hash der eigenen Manifestdatei. |

### 84→62 ohne verschwundene Fälle

Nach Permutation der drei Anschlussgruppen gibt es binom(9,3)=84 Multimengen dreier lokaler Typen aus sieben Typen. Die gemeinsame Vertauschung von T1,T2 tauscht die Typen 1 und 3; die übrigen fünf bleiben fest. Eine Multimenge ist genau dann invariant, wenn die Häufigkeiten von 1 und 3 gleich sind.

Es gibt binom(7,3)=35 invariante Multimengen ohne 1 und 3 sowie fünf mit je einer 1, einer 3 und einem übrigen Typ. Burnside liefert (84+40)/2=62. Alle s=0-Multimengen erfüllen die grundlegende Schnittgrößenbedingung. Die 22 Differenz entstehen aus Zweierbahnen, nicht aus 22 unmöglichen Mustern. Diese Zahlen wurden erneut enumeriert.

### Drei kurze tragende Lemmata

**T-Zeilen sind außerhalb der Diagonale binär.** In einem freien C3-Quotienten sei i ein Dreiecksorbit, also Qii=2. Aus Zeilensumme 14 folgt sum(j≠i) Qij=12. Aus der Diagonale von Q²+Q=12I+6J folgt 4+2+sum(j≠i) Qij²=18, also dieselbe Summe 12. Alle Einträge sind nichtnegative ganze Zahlen; deshalb ist jeder Summand Qij(Qij−1) null. Somit Qij∈{0,1}. Das beweist zugleich QTT=2I+X mit X einfach und die Binarität des Kreuzblocks C.

**Keine C4-Komponente in L.** Für gegenüberliegende Knoten einer C4-Komponente ist (L²)ij=2. Wegen Q≥2L und Nichtnegativität folgt (Q²+Q)ij≥4(L²)ij=8, während die Quotientengleichung dort 6 fordert. Widerspruch.

### FULLCERT-Zählung und Abgleich

Aus der festen Git-TSV selbst gezählt: 656 Zeilen, 656 CNF-Hashes, 272 Rohproof-Hashes. Histogramm „Verwendungen je Hash → Anzahl Hashes“: 1→224, 2→32, 4→4, 8→2, 16→7, 32→1, 64→1, 128→1. Die gewichtete Summe ist 656, die ungewichtete 272. Der oben bezeichnete TSV-/Manifestvergleich wurde hier ausgeführt. Die vom Reviewer berichtete geometrische Teilwürfelprüfung dieser Mehrfachgruppen wurde in diesem Abgleich nicht erneut durchgeführt; ebenso kein Produktionsproof-Replay.

## Urteil zur bisherigen Verifikation

Die 26er-Gram-Kette gewinnt durch das Review eine unabhängige Bestätigung. Die K66-Arithmetik ebenso. Die Aussage „P1 erledigt“ ist nur auf den tatsächlich durchgeführten Reviewumfang anwendbar. Insbesondere BDD-Übersetzung, Multiplizitätsschranke, rundenweise Profilreduktionen und Produktionsproofs wurden vom Reviewer nicht erneut geprüft. Diese tragen weiterhin unseren bisherigen internen Audit und die ausdrücklich bezeichnete Cake-Evidenz.

Die acht vollständigen Fallberichte würden den Vergleich der ursprünglichen lokalen Dateihashes ermöglichen. Der mathematisch relevante Abschlusslauf wurde bereits aus kompakten Git-Berichten erfolgreich rekonstruiert. Nicht alle sechs Ausgabedateien können wegen Laufzeit-/Herkunftsfeldern byteidentisch sein. „Erst danach vollständig aus Git reproduzierbar“ sollte daher in „erst danach auch an die acht ursprünglichen Vollbericht-Hashes bindbar“ präzisiert werden.

Die Aussage, alle 125 Profilproofs seien nur extern verfügbar, ist zu pauschal: Das Repository enthält bereits `data/k66_star125_20260913/k66_star125_export_20260913.zip` sowie Rekonstruktions- und Prüfberichte. Ob dieses Paket für jeden gewünschten frischen Replay alle benötigten Bytes enthält, wurde hier nicht erneut durch Archiveinsicht festgestellt. Ein Dateiinventar ist vor einer pauschalen Nachforderung erforderlich.

Die Sätze „kein zertifizierter Ausschluss auch nur eines vollständigen Quotienten“ und „Literaturablösung eine Größenordnung teurer“ benötigen ebenfalls Einschränkungen: Zwei L-Typen sind historisch ausgeschlossen; für die 101 übrigen wird kein vollständiger Typausschluss behauptet. Ein Kostenfaktor zwischen den noch offenen Zweigen ist nicht gemessen. Die Asymmetrieklasse kann ohne Bezugsmaß nicht als quantitativ größter Anteil dieses unbekannten Existenzraums bezeichnet werden.

## Priorität 1: kanonische Involution

Die Priorisierung wird als nächster **Modell- und Kalibrierungsauftrag** übernommen, nicht als Zusage einer kurzen UNSAT-Rechnung. Der wesentliche Vorteil ist richtig: Ein vollständiges Adjazenzmodell hat keine nachgelagerte Liftpflicht. Ein validiertes SAT-Modell wäre ein tatsächlicher Conway-Graph. UNSAT würde C2 ausschließen; C3 bliebe offen.

### Sofortiges Lemma: M(x,tx)=0

Sei v der einzige Fixpunkt. Wäre ein äußerer Knoten x zu tx benachbart, so hätte die Kante {x,tx} wegen λ=1 genau einen gemeinsamen Nachbarn w. Die Involution erhält diese Kante setweise, also fixiert sie w. Damit w=v. Aber x liegt außerhalb N(v), Widerspruch. Somit sind alle 42 t-invarianten Außenkanten verboten.

Die vom Reviewer gezählten 1.764 Kantenbahnen sind korrekt vor diesem Lemma. Danach bleiben **1.722 Primärvariablen**. Das ist kein Vergleich mit den etwa 120.000 historischen CNF-Variablen: Letztere enthalten Hilfsvariablen. Produktdefinitionen und Zählkodierungen können das neue CNF ebenfalls stark vergrößern. Eine Laufzeitfolgerung aus dem Primärvariablenvergleich ist unzulässig.

### Vollständiges Blockmodell

Ordne v, seine 14 Nachbarn und die 84 Außenknoten. Schreibe K für die Adjazenzmatrix von 7K2 und R für den 84×14-Labelinzidenzblock. Dann

A = [[0, 1ᵀ, 0], [1, K, Rᵀ], [0, R, M]].

Die Unbekannte M muss symmetrisch und binär sein, Diagonale null haben, mit der festen Außeninvolution kommutieren und M(x,tx)=0 erfüllen. Explizit aufzunehmen beziehungsweise als redundant zu beweisen sind:

M1 = 12·1,

M²+M = 12I+2J−RRᵀ,

**MR = 2J−R(K+I).**

Die letzte Gleichung stammt aus dem gemischten Außen-/Nachbarschaftsblock. Sie fehlt im aufgelisteten Modellkern des Reviews. Die Außengleichung ist notwendig; ohne Beweis ihrer Hinlänglichkeit für die gemischten Blöcke darf man sie nicht als vollständiges Modell verkaufen. Alle drei Gleichungen zusammen mit dem festen Rahmen liefern sämtliche Blöcke der SRG-Identität; die übrigen Blöcke sind durch die Labelkonstruktion erfüllt.

Für ein Label x={a,b} lautet die gemischte Gleichung besonders einfach:

sum(y enthält j) Mxy = 2 − 1[j∈{a,b}] − 1[j∈{ta,tb}].

Da a,b zu verschiedenen Matching-Paaren gehören, sind a,b,ta,tb vier verschiedene Positionen. Wir erhalten **vier Exact-One- und zehn Exact-Two-Gleichungen pro Außenknoten**. Dies beantwortet die Frage des Reviews nach einer Lemma-B-artigen Budgetstruktur unmittelbar. Diese notwendigen Gleichungen sind ein guter Ausgangspunkt für das Encoding; eine quantitative Beschleunigung ist noch nicht gemessen.

### Nachgerechnete kleine Daten

Eigene Enumeration bestätigt 84 Außenlabels, 3.486 Paare, davon 924 mit einem gemeinsamen Labelknoten und 2.562 disjunkte; 42 Fixpaare und 1.722 übrige Zweierbahnen. Die Framegruppe hat Ordnung 645.120. Da t auf bereits t-invarianten Belegungen trivial wirkt, enthält der Wirkungskern mindestens {1,t}; der maximal mögliche Reduktionsfaktor ist daher höchstens 322.560, nicht automatisch 645.120. Weitere Stabilisatoren reduzieren ihn.

Die Rook9-Positivkontrolle wurde hier als direkte Matrixkontrolle für die vollständige SRG-Identität, die Außenblockgleichung und die gemischte Gleichung ausgeführt und bestand. Das ist noch kein Test eines neuen CNF-Encoders. Der Rookfall hat dieselben Strukturprinzipien, aber k=4 und deshalb k−μ=2 statt 12 vor I. Es wäre falsch, die 99er-Koeffizienten unverändert zu verwenden.

### Präzisierter Arbeitsauftrag

1. Vollständige Modellspezifikation und Notwendigkeit einschließlich gemischter Gleichungen festhalten; die obigen unmittelbaren Lemmata integrieren.
2. Encoder mit vollständiger Rookkontrolle und unabhängiger Matrixvalidierung entwickeln. Gezielte Negativkontrollen wählen; nicht jede beliebige Koeffizientenmutation muss SAT/UNSAT ändern.
3. Eine kleine, begründete WLOG-Reduktion oder ein vollständiges binäres Cubing verwenden. Komplexe Symmetriebrechung nicht vor der korrekten Baseline erzwingen.
4. Begrenzter Ryzen-Pilot mit gespeicherten Eingaben, Status/ETA und nachfolgender Zertifizierung. Erst danach Solver-/Checkerzeiten, RAM und Proofwachstum für eine längere Kampagne bewerten.
5. Eine länger laufende Zertifizierung nur anhand tatsächlicher Engpässe planen. Timeouts lassen Teilfälle offen; im später ausdrücklich autorisierten Endgame gelten die vereinbarten Ressourcenregeln.

Eine Prognose „größter mathematischer Gewinn“ ist eine strategische Wertung. Gegenüber C3 ist der Gewinn besser abgrenzbar und die Realisierungslücke vermieden; geringere Rechenhärte ist nicht bewiesen. Die C3-Achse bleibt eine reale zweite Aufgabe. Ein erfolgloser begrenzter Versuch auf ihr ist kein Nachweis, dass stärkere Bedingungen keinen der 26 Typen ausschließen können.

## Resümee

Das Review stärkt die mathematischen Kernresultate erheblich, schließt aber nicht alle externen Abhängigkeiten oder Produktionsreplay-Fragen. Seine Priorisierung der Involution ist sachlich überzeugend, sobald der vollständige Modellkern, das sofortige Verbot der 42 Partnerkanten und die faire Variablenzählung berücksichtigt werden. Der nächste sinnvolle Schritt ist die Ausarbeitung dieses vollständigen Modells mit überprüfbarem Kleinfall, nicht der unmittelbare Start einer großen SAT-Kampagne. Originalreview, eigener Abgleich und eigene kleine Prüfergebnisse werden getrennt archiviert.
