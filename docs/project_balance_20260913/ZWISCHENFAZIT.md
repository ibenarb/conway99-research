# Conway99: geschlossenes Zwischenfazit und Ausschlussbilanz

**Stand:** 13. September 2026, nach K66-Abschluss. **Geltungsbereich:** mathematischer, geometrischer und zertifizierender Projektzweig; die evolutionäre Suche ist nicht Gegenstand dieses Berichts.

**Feste Forschungsbasis:** [769ee6df774a11b90ed18982ce6ff5aca325260a](https://github.com/ibenarb/conway99-research/tree/769ee6df774a11b90ed18982ce6ff5aca325260a). **Zusätzlich benötigte historische Basis:** [b279cd6de420bc4ad64869c8c7f99d653c73a195](https://github.com/ibenarb/conway99-research/tree/b279cd6de420bc4ad64869c8c7f99d653c73a195). Einige Versöhnungs- und Fixdreiecksunterlagen liegen nur an dieser zweiten Referenz. Ein Checkout des aktuellen Branches allein ersetzt sie nicht.

## 1. Ergebnis in geschlossener Form

Das Projekt hat die Existenz eines stark regulären Graphen mit Parametern (99,14,1,2) weder bewiesen noch widerlegt. Auch der Ausschluss aller nichttrivialen Automorphismen ist offen.

Mit Übernahme der ausdrücklich bezeichneten publizierten Automorphismensätze konzentriert sich die Symmetriefrage auf zwei Aufgaben: den Ausschluss einer **freien C3-Wirkung mit genau sechs dreieckigen Knotenorbits** und den Ausschluss einer **Involution mit genau einem Fixpunkt**. Für die erste Aufgabe liegen eine exakte Quotientenformulierung, zertifizierte Teilfälle und eine auf 26 T-Gerüste reduzierte notwendige Gram-Bedingung vor. Für die zweite liegt eine kanonische Beschreibung der Wirkung vor, aber kein vollständiger Ausschluss.

Der neu abgeschlossene Fall **k66_s1_t225** gehört zum separaten Fixdreiecks-Zweig. Sein computergestützter Beweis verbindet exakte Arithmetik, vollständige Bahnenüberdeckung, auditierte notwendige CNFs und die bezeichnete Cake-Evidenz. Dieser eigene Nachvollzug ersetzt einen Teil der historischen externen Computerabhängigkeit. Er erweitert nicht die schon literaturseitig bekannte Fixpunktfreiheit von Ordnung-3-Automorphismen.

Die wichtigste verbleibende methodische Lücke ist die Realisierung: Ein binärer Gram-Zeuge ist kein vollständiger Quotient, und ein vollständiger Quotient ist noch kein Graph. Erfolgreiche Machbarkeitsprüfungen einer schwächeren Modellstufe werden deshalb nicht als Existenznachweise einer stärkeren Stufe gezählt.

## 2. Evidenzklassen und Korrektur der unmittelbar vorherigen Auskunft

Wir unterscheiden **THEOREM** (angegebene mathematische Herleitung), **EXTERNAL** (übernommener Literatur-/Fremdbeweis), **CERTIFIED** (bezeichnete maschinelle Beweiskette), **REPRODUCED** (tatsächliche Wiederholung eines spezifizierten Prüfschritts), **REPORTED** (archivierter Bericht ohne erneute Einzelprüfung in dieser Bilanz), **OPEN** und **SCOUT**.

Die vor dieser Bilanz gegebene Auskunft, nach K66 müsse zunächst t145 als mathematisch offener Fixdreiecksfall bearbeitet werden, war unvollständig und strategisch irreführend. Sie berücksichtigte unseren Forschungsstand vom 12. September nicht hinreichend. **Mit Literaturannahmen ist der gesamte Fixdreiecks-Zweig bereits ausgeschlossen.** t145 ist eine offene Aufgabe für eine vollständig interne Rekonstruktion dieses Ausschlusses. Ebenso ist τ=27 nicht mehr als offene globale Symmetrieaufgabe zu zählen.

Der Wunsch nach einer eigenen durchgängigen Zertifikatskette ist ein legitimes zweites Ziel. Er darf nicht mit dem verbleibenden mathematischen Suchraum unter Übernahme publizierter Sätze verwechselt werden.

## 3. Globale Mathematik und Reichweite des geometrischen Zweigs

Für die Adjazenzmatrix A eines hypothetischen Graphen gilt

\[
A=A^T,\quad A_{ii}=0,\quad A_{ij}\in\{0,1\},\quad A\mathbf1=14\mathbf1,
\qquad A^2+A=12I+2J.
\]

Es folgen 693 Kanten, 231 Dreiecke, 4.158 Nichtkanten und 2.079 Vierzyklen. Jeder Nichtkante ist ihr Paar gemeinsamer Nachbarn zugeordnet; jeder Vierzyklus wird über seine zwei Diagonalen zweimal gezählt. Ein solcher Vierzyklus hat keine Diagonalkante, da diese zwei gemeinsame Nachbarn hätte und damit λ=1 verletzte.

Um einen fest gewählten Knoten v gilt N(v) ≅ 7K2. Jeder der 84 übrigen Knoten ist eindeutig durch ein nichtbenachbartes Paar in N(v) bezeichnet. Das liefert ein kanonisches Koordinatensystem und notwendige Blockgleichungen, ohne eine Graphsymmetrie vorauszusetzen. Quellen: historischer Statusbericht sowie `docs/breadth1/O3_local_equations.md` im Repository.

Die zusätzliche Hypothese einer Realisierung als 1-Skelett eines einfachen konvexen 14-Polytops ist **keine Voraussetzung des allgemeinen Conway-Problems**. Im historischen Defektzweig wurde δ=2079−q untersucht. Die verwendete Gleichung

\[
\sum_{|F|\ge5}|F|=4\delta
\]

ist im damaligen Bericht ausdrücklich an n3=231 dreieckige 2-Flächen gebunden. Die negativen Solver-Signale bei δ=5 sind kein allgemeiner Graph- oder Polytopausschluss. Ein vollständig geprüfter geometrischer Gesamtsatz wird hier nicht nachgetragen. Maßgeblicher Scope: [Statusbericht vom 3. September](https://github.com/ibenarb/conway99-research/blob/769ee6df774a11b90ed18982ce6ff5aca325260a/docs/status/Conway99_Statusbericht_2026-09-03_rev1.tex).

## 4. Literaturabhängigkeiten der Symmetrieabdeckung

| ID | Übernommene Aussage | Präzise Quelle / eigene Reichweite |
| --- | --- | --- |
| E1 | Primordnungen nur 2 und 3; jedes Ordnung-3-Element wirkt frei | Behbahani–Lam, ausdrücklich als Theorem 7.1 in Crnković–Maksimović 2020 wiedergegeben. Der ursprüngliche gesamte Computerbeweis wurde in dieser Bilanz nicht wiederholt. |
| E2 | Eine Involution hat genau einen Fixpunkt | Makhnev–Minakova; Theorem 1.6 in Behbahanis Dissertation. Die schwächere arithmetische Alternative mit 15 Fixpunkten ist keine zusätzliche offene Familie. |
| E3 | Keine Gruppenwirkung der Ordnung 6 oder 9 | Crnković–Maksimović, §7. Diese Einschränkung allein beseitigt C2 und C3 nicht. |
| E4 | Bei gerader Automorphismengruppenordnung teilt diese 6 | Cesarz–Woldar 2025. Zusammen mit E1 und E3 bleiben als Gesamtgruppen 1, C2, C3. |
| E5 | Für freie Ordnung 3 gilt a1=18 und daher τ=6 | Ishida, v2, §8.4, Proposition 8.7; eigene spezialisierte Herleitung im Bericht vom 12. September, §3.1. Kein vollständiger Audit der gesamten Arbeit. |

Quellen: [Crnković–Maksimović, PDF, §7](https://cdm.ucalgary.ca/article/download/62323/54015/204856), [Behbahani, Dissertation, Theorem 1.6](https://spectrum.library.concordia.ca/976720/1/NR63369.pdf), [Cesarz–Woldar](https://alco.centre-mersenne.org/articles/10.5802/alco.418/), [Ishida v2](https://arxiv.org/html/2606.29183v2#S8.SS4). Die Aussagen wurden für diese Bilanz an den bezeichneten Quellen nachgelesen; dies ist keine erneute vollständige Beweisreproduktion ihrer Computerrechnungen.

Der gruppentheoretische Abschluss wäre: Jede nichttriviale endliche Automorphismengruppe enthält ein Element von Primordnung. Wenn weder C2 noch C3 wirken kann, ist der Graph asymmetrisch. Das wäre ein Symmetriesatz, weiterhin kein Nichtexistenzbeweis für asymmetrische Graphen.

## 5. Ausschlussbilanz der freien Ordnung 3

### 5.1 Modell und Reduktionen

Die 99 Knoten zerfallen in 33 Dreierorbits. Ihr symmetrischer Quotient Q erfüllt

\[
Q\mathbf1=14\mathbf1,\qquad Q^2+Q=12I+6J,\qquad Q=2D_T+S+2L.
\]

T bezeichnet die dreieckigen Orbits; L ist ein einfacher 2-Faktor auf den übrigen Orbits, S ist einfach und zu L kantendisjunkt. Layer A kodiert die notwendigen exakten Quotientengleichungen einschließlich der dokumentierten Lemma-B-Schicht. Layer B fügt logisch redundante Zyklusungleichungen hinzu. Unterschiede der A/B-Laufzeiten sind damit Encodingeffekte, keine zusätzliche mathematische Ausschlusskraft. Begründung: `docs/breadth1/O3_LAYER_A_MODEL_SPEC.md` und `O3_cycle_lemmas.md`.

Die historische Spurrestriktion gab τ∈{6,13,20,27}. Das Zählen der 231 Dreiecke unter der freien C3-Wirkung gibt 231=τ+3m und schließt τ=13,20 aus. Der stärkere algebraische Weg zu τ=6 nutzt den 3-adisch ganzzahligen Spektralprojektor

\[
E_3=\tfrac47I+\tfrac17A-\tfrac{2}{77}J.
\]

Sein Bild ist bei freier Wirkung ein projektiver direkter Summand des freien Z3[C3]-Moduls, somit frei über der lokalen Gruppenalgebra. Der Rang 54 ergibt Gruppenalgebrarang 18 und Spur null für ein nichttriviales Gruppenelement. Aus tr(gE3)=(a1−18)/7 folgt a1=18=3τ. Diese Projektivitäts-/Lokalitätsargumentation ist ausdrücklich Teil des mathematischen Reviewauftrags; numerische Kontrollen ersetzen sie nicht.

### 5.2 Typenbilanz

| Familie | Bilanz | Evidenz / Grenze |
| --- | --- | --- |
| τ=13 | 28 historische C4-freie L-Typen ausgeschlossen | Dreieckskongruenz |
| τ=20 | 6 historische C4-freie L-Typen ausgeschlossen | Dreieckskongruenz |
| τ=27 | Beide historischen L-Typen ausgeschlossen | Algebraischer τ=6-Schluss; zusätzlich eigenständig reproduzierte externe f27-Zertifikatskette |
| τ=6, L=(3^9) | Historisch zertifiziert ausgeschlossen | Im Versöhnungsbericht wiedergefundenes LRAT/Cake-Zertifikat mit konkreten CNF-/Proof-Hashes; kein neuer Replay in dieser Bilanz |
| τ=6, L=(6,3^7) | Historisch zertifiziert ausgeschlossen | FULLCERT: 488 Root-Zertifikate + 168 Leaves = 656; Transfer zur Mathematik über Lemma B |
| τ=6, übrige L-Typen | **101 offen** | Keine vollständigen Ausschlüsse dieser Typen in den ausgewerteten Quellen |

Alle 103 L-Partitionen von 27 mit Teilen mindestens 3 und ohne 4 sind einzeln in `exclusion_ledger.json` enthalten. Die Zahl 101 übernimmt die zwei historischen Typausschlüsse samt deren ausgewiesenen Transferannahmen.

Der f27-Nachweis stammt aus [infinityscroll, festem Commit e8f4d629cdf03b4bb14ebed01e4ebe7e8dbf3f8b](https://github.com/infinityscroll/conway99-order3-f27/tree/e8f4d629cdf03b4bb14ebed01e4ebe7e8dbf3f8b). Im Projekt wurden 13 DRAT-Beweise frisch geprüft und CNFs regeneriert. Nachweise: `data/research_20260912/f27-audit.log`, `src/research_20260912/replay_f27.py`, Bericht vom 12. September. Der gespeicherte Log enthält die 13 Replay-Marker; die sechs zusätzlichen Anfangs-Gram-Regenerationen sind im Zusatzskript und Forschungsbericht dokumentiert, aber nicht als sechs separate Marker in genau dieser Logdatei. Diese Evidenzunterscheidung soll der Reviewer berücksichtigen.

### 5.3 Unabhängige T-Gerüstachse

Für den einfachen Graphen X auf den sechs T-Orbits und den binären Kreuzblock C mit 27 Spalten gilt notwendig

\[
CC^T=G(X)=6I+6J-X^2-5X.
\]

| Stufe | Neue Ausschlüsse | Verbleibend |
| --- | ---: | ---: |
| Alle Sechsknotengraphen bis auf Isomorphie | — | 156 |
| Eintragsweise Nichtnegativität von G | 87 | 69 |
| Positive Semidefinitheit | 25 | 44 |
| Binäre Gram-Machbarkeit mit 27 Spalten | 18 | **26** |

Die erste Enumeration deckt 32.768 beschriftete X ab. Für die letzten 18 Ausschlüsse liegen exakt geprüfte rationale Separationszeugnisse vor; für jeden der 26 Überlebenden ein ganzzahliger Profilzeuge. Die vier früheren gewichteten Ausschlüsse sind bereits in diesen 18 enthalten: **26, nicht 22**. Die letzte Reduktion wurde anhand aller Umnummerierungen mit den Projektindizes abgeglichen.

Verbleibende Projektindizes: **0, 1, 2, 5, 8, 13, 22, 24, 26, 27, 39, 40, 41, 46, 51, 52, 64, 65, 71, 72, 75, 95, 96, 98, 121, 122**.

Sämtliche 156 X-Matrizen und ihr jeweiliger Ausschlussstatus stehen in der maschinenlesbaren Bilanz. Grundlage: `results/research_20260912/tau6_aggregate.json`, `results/review_synthesis_20260912/verification.json` und die beiden Zeugendateien unter `data/review_synthesis_20260912`.

Die 26 X-Gerüste und die 101 L-Typen sind verschiedene Koordinaten einer stärkeren Aufgabe. Ihr Produkt ist höchstens ein Organisationsraster, keine gezählte Menge machbarer Quotienten oder Graphen. Eine binäre Gram-Lösung sagt noch nichts über die Realisierbarkeit des gesamten U-Blocks und des vorgeschriebenen L-Typs. Die nachgelagerte kontinuierliche Aggregation hat keinen weiteren Typ ausgeschlossen; 14 rationale LP-Zeugen wurden exakt gewonnen, zwölf weitere Machbarkeitsmeldungen blieben numerisch. Das rechtfertigt keine zusätzliche Streichung.

## 6. Fixdreieck: externe Erledigung und interner Nachvollzug

Der eigene Fixdreiecksansatz besitzt 35 Orbits einschließlich der drei Fixpunkte. Die Herleitung erzwingt zwölf angehängte Dreierorbits, zwei dreieckige weitere Orbits und 18 gewöhnliche Orbits. Die 32×32-Untermatrix P erfüllt die modifizierte Quotientengleichung aus dem K66-Audit. Die ursprüngliche 72er-WLOG-Partition betrifft T-Anschlussgerüste, nicht die 246 K66-Crossmatchingbahnen.

| Interner Nachvollzugsstand | Anzahl Strukturklassen | Qualität der hier verfügbaren Evidenz |
| --- | ---: | --- |
| In V3 als LRAT/Cake-zertifiziert berichtet | 29 | Historischer Frontierbericht; Einzelzertifikate in dieser Bilanz nicht erneut inspiziert |
| K66 später abgeschlossen | 1 | Vollständiger gesonderter Audit und Abschlussbericht |
| Übrige historische Frontierklassen | 42 | Kein interner Abschluss in den ausgewerteten Quellen nachgewiesen |
| Gesamt | 72 | 62 Klassen mit s=0, zehn mit s=1 |

Die 42 sind **keine 42 verbleibenden mathematischen Symmetriefamilien unter E1**. Sie bezeichnen interne Nachvollzugspflichten. Darunter liegen k37_s0_t145, k68_s1_t256 und k70_s1_t566. Die 29 historischen Zuordnungen wurden aus dem ausdrücklich beschriebenen V3-Klassifikator rekonstruiert; ihre Kennzeichnung behauptet keinen neuen Zertifikatscheck. Eine spätere, hier nicht gesicherte Rechnung kann die interne Bilanz weiter verkleinert haben.

Alle 72 Klassen und beide Statusachsen stehen einzeln in der JSON-Bilanz. Die alte Frontiergewichtung 92,420697 % beschreibt beschriftete T-Gerüste im historischen Lauf, keine Erfolgswahrscheinlichkeit und keinen Anteil an allen Conway-Graphen. Die außerhalb dieser Git-Nachweise früher genannten 93.860 beziehungsweise 12.203 V4-/PSD-Bahnen werden hier nicht als frisch bestätigte Gesamtzählung übernommen.

### K66-Beweiskette

Für k66_s1_t225 wurde der vollständige unfiltrierte Raum von 24³=13.824 Crossmatching-Kombinationen durch direkte Kantenwirkung eines Stabilisators der Ordnung 64 in 246 Bahnen zerlegt. 223 Bahnen mit 12.672 beschrifteten Fällen besitzen exakt negative Hauptminoren von G=C_H−H²−H. Da G=ZᵀZ notwendig ist, sind sie unmöglich. Die 23 Restbahnen mit 1.152 beschrifteten Fällen sind mit den auditierten Encoder-Fällen und ihrer UNSAT-Kette verknüpft.

167 vollständige CNF-Bytevergleiche, genaue Profil-/Paargegenrechnung und die mathematische Übersetzungsbegründung verbinden die Eingaben. Die zusätzlichen 28 vorhandenen Beweise wurden mit Cake erneut geprüft; 125 Profilbeweise wurden neu erzeugt und Cake-geprüft. Die 897 Hauptlaufblätter tragen archivierte Cake-Bestätigungen, geprüfte Integrität und vollständige binäre Überdeckung, **keinen neuen Replay im Abschlussaudit**.

Maßgeblich: [K66-Beweisabschluss](https://github.com/ibenarb/conway99-research/blob/769ee6df774a11b90ed18982ce6ff5aca325260a/docs/k66_encoder_audit_20260913/K66_BEWEISABSCHLUSS.md). Die alten alternativen strukturierten Brücken-/Blattpläne sind für diesen abgeschlossenen Hauptbeweis nicht erforderlich; ihre früheren offenen Zusatzpflichten werden dadurch nicht nachträglich als zertifiziert ausgegeben.

## 7. Involution und Lift: die echten Realisierungsaufgaben

Unter E2 ist v der einzige Fixpunkt einer Involution t. Für u∈N(v) müssen u und tu benachbart sein: Andernfalls wäre ihr zweiter gemeinsamer Nachbar neben v ebenfalls fix. Somit vertauscht t die Endpunkte jeder der sieben Kanten von N(v). Die 84 äußeren Paarlabels werden dadurch eindeutig mitvertauscht. Im kanonischen Koordinatensystem genügt also **eine fest vorgegebene Permutation** mit Orbitstruktur 1¹2⁴⁹. Offen ist die Existenz einer vollständigen SRG-Matrix, die mit ihr kommutiert. Es liegt in dieser Bilanz kein zertifizierter UNSAT-Abschluss dieses Modells vor.

Für freie C3-Wirkungen ist ein exakter Quotient Voraussetzung der nachgelagerten Phasen-/Liftaufgabe. Die modularen Bedingungen wurden an zwei freien C3-Wirkungen des Neunknoten-Rookgraphen vollständig kontrolliert: jeweils neun von 27 Phasen ergeben genau die tatsächlichen SRG-Lifts. An einem nicht exakten Quotienten liefern zwei von 729 Phasen modulare Nullen, aber keinen SRG. Das belegt die notwendige Domänengrenze. Quellen: `src/research_20260912/f3_lift.py`, `src/review_synthesis_20260912/check_lifts.py`, `results/review_synthesis_20260912/lifts.json`.

Ein Quotientenausschluss ist hinreichend, um alle zugehörigen Lifts auszuschließen. Falls Quotienten überleben, müssen deren Lifts vollständig behandelt werden; die Suche darf nicht beim Quotienten-SAT enden.

## 8. Scout-Ergebnisse und nicht freigegebene Filter

Der historische matched A/B-Scout umfasste 139 Typen und 278 Instanzen: 275 TIMEOUTs und drei unzertifizierte UNSAT-Meldungen ausschließlich bei bereits ausgeschlossenen Kontrolltypen. Er lieferte **keinen neuen zertifizierten Typausschluss**. Die später mathematisch beseitigten τ=13/20-Typen bleiben in seinen Rohdaten erhalten und dürfen nicht weiter als offene Arbeit gezählt werden.

Der Reimbayev-Audit meldet bei 208 zwischen Darstellungen abgeglichenen Formeln eine Summendifferenz von 94.034.160 gegenüber der erforderlichen Gesamtzahl. Die fehlerhafte Einzelherleitung ist nicht lokalisiert, kein reparierter Filter freigegeben. Dies ist ein Ergebnis der Quellenkritik, kein Ausschluss einer Graphfamilie. Nachweis: `results/research_20260912/reimbayev.json` und zugehöriges Audit-Skript.

Frühere geometrische Scouts, begrenzte Suche und nicht vollständig reproduzierbare Partnerläufe werden nicht in neue Ausschlusssätze umgedeutet. Für die Zwischenbilanz genügt ihre klare Einordnung; es wurden keine neuen langen Suchläufe gestartet.

## 9. Was mit Git überprüfbar ist — und was zusätzlich benötigt wird

Die neue Bilanz hat 27 Quellen vollständig aus festen Git-Referenzen gelesen und gegen ihre Git-Blob-IDs geprüft. `source_manifest.json` enthält Pfad, Commit, Dateilänge, SHA256 und Direktlink. Ergänzend tragen die K66-Abschlussunterlagen ihre eigenen vollständigen Ergebnismanifeste.

Die JSON-Bilanz wurde aus den vorhandenen Falllisten und der kleinen 72er-Gerüstenumeration erstellt; Typenmengen, Summen und Disjunktheit wurden rechnerisch geprüft. **Diese Tätigkeit ist eine Quellen- und Bilanzprüfung, kein erneuter Lauf aller mathematischen Zertifikatsprüfer.** Historische Resultate behalten ihre ursprüngliche Evidenzstufe.

| Reviewgegenstand | Zugang |
| --- | --- |
| Mathematische Ableitungen, Encoder und kleine Zeugen | Bezeichnete öffentliche Git-Commits |
| 156/44/26-T-Gerüstkette | Daten und eigener exakter Prüfer in Git; erste Enumeration separat nachrechnen |
| K66-Quellen, Ergebniszuordnungen, Zeugen und Überdeckung | Git; vollständige Produktionsreproduktion benötigt zusätzlich die im Prüfer bezeichneten Ryzen-Dateien |
| FULLCERT 656 und K66 897 große Produktionsbeweise | Manifeste und archivierte Prüfberichte in Git; vollständiger frischer Replay benötigt die extern liegenden großen Proofdateien |
| Externe f27-Kette | Zusätzlich das fest gepinnte öffentliche Fremdrepository und DRAT-Checker |
| Vollständige interne Rekonstruktion von E1/E2 | Nicht durch einen bloßen Checkout dieses Projekts erledigt |

Die FULLCERT-Archive umfassen historisch etwa 200,76 GiB gzip. Das ist ein Zugriffshinweis, kein neu gemessener Bestand. Fehlende große Dateien sind eine Grenze des ausschließlich Git-basierten Replays, nicht automatisch ein Gegenbeweis zur dokumentierten Aussage.

Das historische `lrat-check` wurde als unzuverlässig erkannt. Es wird nicht als zweite unabhängige positive Instanz gezählt. Bei FULLCERT zeigen der spätere Versöhnungsbericht und die historischen Metadaten die positiven Cake-Marker; bei K66 gelten die ausdrücklich dokumentierten Kontrollen und Replays. Der Reviewer soll diese Vertrauenskette gezielt prüfen.

## 10. Geschlossener nächster Forschungsauftrag

**Mathematisches Hauptziel:** Freie C3-Wirkung bei τ=6 und kanonische Involution ausschließen; danach Cauchys Satz anwenden. Für einen globalen Nichtexistenzbeweis müsste zusätzlich der asymmetrische Fall ausgeschlossen werden.

**Nächste sinnvolle Modellentwicklung:** Die 26 T-Gerüste mit tatsächlicher U-Realisierbarkeit und konkreten L-Zyklentypen verbinden. Vor einem großen Lauf Notwendigkeit aller Bedingungen und neue Symmetriebrechungen beweisen. Eine schwache LP erneut zu lösen genügt nicht; sie hat keinen weiteren Typ ausgeschlossen. Als zweiter klar abgegrenzter Ansatz steht das vollständige SRG-Modell mit der kanonischen Involution bereit.

**Eigenständiges Vertrauensziel:** Falls die externe Computerabhängigkeit ersetzt werden soll, die 42 verbliebenen internen Fixdreiecks-Nachvollzugspflichten und die 29 nur historisch berichteten Abschlüsse gezielt inventarisieren. Dies muss als eigener Auftrag gegen seinen Nutzen für das mathematische Hauptziel abgewogen werden. Eine weitere K66-artige Rechnung ist nicht automatisch der nächste stärkste Schritt zum Symmetrieausschluss.

**Reviewerentscheidung:** Vor neuer langer Suche die Korrektheit des τ=6-Transfers, die 26er-Gram-Kette, die historischen Typtransfers und die kanonische Involution beurteilen. Ein belastbares Review soll jede Aussage mit Satz, Git-Pfad/Commit und konkreter Prüftätigkeit verbinden sowie fehlende Daten ausdrücklich benennen.
