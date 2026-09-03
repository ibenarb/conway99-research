# Peer-Review: Conway-99-Statusbericht vom 03.09.2026

**Reviewer-Bericht, 3. September 2026.** Grundlage: Review-Paket (9/9 SHA-Prüfsummen OK), Statusbericht als PDF und TeX-Quelle, Factsheet, Claim-Ledger, Timeline, Freeze-Evidenz, Evidenzgrenzen — sowie der vollständige frühere Projektkontext einschließlich der von mir am 28./29.08. selbst geprüften Encoder-Quellen, `state.json`-Bäume und CNF-Hashes.

**Prüfprotokoll.** Ich habe nicht nur gelesen, sondern jede mathematische Aussage des Ledgers unabhängig nachgerechnet (Skriptlaufzeit unter 10 s): Spektrum und Vielfachheiten über die Standardformel; C² = I für 7K₂ und daraus alle drei Blockgleichungen; Nichtkanten- und Vierkreiszählung; die Polytop-Identität über zwei unabhängige Wege; die τ-Kongruenz; sämtliche Zyklentypzählungen für alle vier τ; die Gradbilanz, auf der Lemma B ruht; sowie zwei Konsistenzproben, die der Bericht selbst nicht zieht. **Ergebnis: alle 20 Ledger-Aussagen C01–C20 sind korrekt.** Kein einziger Zahlenfehler.

---

## Antworten auf die sieben Prüfpunkte

**1. Mathematische Grundlagen — korrekt.** A² + A = 12I + 2J folgt eintragsweise; die nichttrivialen Eigenwerte 3 und −4 sind die Nullstellen von x² + x − 12; die Vielfachheiten 54 und 44 bestätigt die Standardformel mit √((λ−μ)² + 4(k−μ)) = 7 exakt. Die Blockzerlegung 1 + 14 + 84 und N(v) = 7K₂ folgen aus λ = 1. Die P-Margins (Zeilensumme 12, Spaltensumme 2, H-Zeilensumme 12) sind elementar. Die drei Blockgleichungen habe ich nachgerechnet: Der (2,2)-Block liefert J + C² + PPᵀ + C = 12I + 2J, und da C das perfekte Matching 7K₂ ist, gilt C² = I, also **PPᵀ = 11I + J − C** ✓. Ebenso CP + PH + P = 2J ✓ und PᵀP + H² + H = 12I + 2J ✓.

**2. Geometrischer Zweig — korrekt und sauber abgegrenzt.** 4158 Nichtkanten ✓. Die Halbierung zu 2079 Vierkreisen ist richtig begründet: Jede Nichtkante liefert über ihre genau zwei gemeinsamen Nachbarn genau einen Vierkreis, und jeder Vierkreis besitzt zwei Nichtkanten-Diagonalen — die Zuordnung ist also 2:1. Die Identität Σ_{|F|≥5}|F| = 4δ habe ich über zwei Wege bestätigt: Σ_F |F| = V·C(14,2) = 99·91 = 9009 und ebenso E·(d−1) = 693·13 = 9009; mit n₃ = 231 folgt 9009 − 693 = 8316 = 4·2079 ✓. Die Trennung zwischen Hypothese, explorativer Rechnung und Beweis ist im Bericht **ausreichend klar** — die Formulierung „wichtige Ausschlüsse bzw. Strukturtests innerhalb eines speziellen geometrischen Ansatzes, kein globaler Nichtexistenzbeweis" ist genau richtig. Eine unausgesprochene Voraussetzung fehlt allerdings (siehe D6).

**3. Memetischer Zweig — inhaltlich richtig dargestellt.** Der 2-Switch erhält die Gradfolge und damit die 12-Regularität von H; dass er die Bedingungen für gemeinsame Nachbarn **nicht** erhält, ist die entscheidende Einschränkung und wird korrekt benannt. Die Gleichsetzung mit dem alternierenden 4-Zyklus (a,b),(b,c),(c,d),(d,a) ist zutreffend. Eine Ungenauigkeit siehe B4.

**4. Ordnung-3-Zweig — alle Zahlen bestätigt.** Fixpunktfreie Wirkung ⇒ 33 Orbits der Größe 3 ✓. Die τ-Werte folgen aus Spur 14 + 3a − 4b = 2τ mit a + b = 32, also a = (2τ + 114)/7 ganzzahlig, mithin τ ≡ 6 (mod 7) und **τ ∈ {6, 13, 20, 27}** ✓. L ist 2-regulär auf den 33 − τ Nicht-Dreieckorbits, Typen sind Partitionen in Teile ≥ 3. Meine unabhängige Enumeration reproduziert **jede einzelne Zahl der Tabelle**: 191/103, 49/28, 10/6, 2/2, Summen 252/139 ✓. Der C₄-Ausschluss ist korrekt (zwei gegenüberliegende C₄-Knoten haben zwei gemeinsame L-Nachbarn, die je 2·2 = 4 zu (Q²) beitragen, also ≥ 8 > 6 = 6 − q). Lemma B ist korrekt, und die Reichweitenangabe für (6,3⁷) mit 7·30 = 210 Exact-One-Gruppen stimmt.

**5. Zertifizierung — Trennung korrekt, ein Argument fehlt.** Die Unterscheidung Solver-UNSAT / vorhandener Proof / extern geprüftes Zertifikat ist sauber und wird konsequent durchgehalten. Die Kette CaDiCaL 2.2.1 → LRAT → `lrat-check` → `cake_lpr` ist angemessen beschrieben; die Akzeptanzbedingung (beide Prüfer erfolgreich) ist explizit. Zwei Konsistenzproben, die ich zusätzlich gezogen habe, stützen die Angaben: 656 Proofs + 656 CNFs + 1 Quell-CNF = **1313 Manifest-Einträge** ✓, und die 512 Wurzeln sind genau 2⁹ über die C(6,2) − 6 = **9 Nicht-L-Paare** der C₆-Komponente ✓. **Der Bericht formuliert den Satz nicht weiter als die geprüfte Instanz — eher zu eng** (siehe C1). Es fehlt jedoch das Überdeckungsargument (D1), ohne das 488 + 168 = 656 eine bloße Behauptung bleibt.

**6. Grenzen — keine Überziehung gefunden.** Ich habe gezielt danach gesucht: Der Bericht erweckt an **keiner** Stelle den Eindruck, Nichtexistenz eines srg(99,14,1,2), Ausschluss aller Ordnung-3-Automorphismen, Asymmetrie oder Nichtexistenz einer polytopalen Realisierung seien bewiesen. Der Abschnitt „Was daraus ausdrücklich noch nicht folgt" benennt genau diese vier Punkte, das Abstract sagt „ausdrücklich noch kein Nichtexistenzbeweis", und die Aut(G) = 1-Passage ist als „Forschungsziel, noch kein Resultat" markiert. Das ist vorbildlich. Einzige Ausnahme ist eine Prioritätsbehauptung (B2).

**7. Forschungsstrategie — richtig, aber auf einer zu optimistischen Datenbasis.** Die Reihenfolge Struktur/Lemmas → Breite Ordnung 3 → Ordnung 2 ist richtig; die Entscheidung, die 101 Resttypen **nicht** einzeln zu zertifizieren, ist die zentrale und korrekte Einsicht des Berichts. Zur Frage nach der zuerst zu schließenden Lücke siehe F1 — die Antwort ist eindeutig und wird durch eine Messung gestützt, die der Bericht nicht enthält.

---

## A. VERDICT

**GO WITH FIXES.**

Der Bericht ist mathematisch fehlerfrei und in der Frage der Reichweite vorbildlich diszipliniert. Er ist als Statusdokument publikationsreif, **sobald drei tragende Begründungen ergänzt** und die Provenienz der Literaturergebnisse korrigiert ist. Keiner der Befunde stellt ein Resultat in Frage; alle betreffen Nachvollziehbarkeit und Zuschreibung.

## B. Konkrete sachliche Fehler

**B1 — Ordnung-2-Orbitstruktur zu bestimmt formuliert.** Der Bericht schreibt, eine Involution führe im Root-Modell auf 1 + 7·2 + 42·2. Das ist ein **Spezialfall**, nicht die allgemeine Lage. Da 99 ungerade ist, hat jede Involution eine ungerade Zahl von Fixpunkten. Fixpunkte innerhalb N(v) treten paarweise auf (σ erhält das Matching 7K₂; ist ein Endpunkt fix, so auch sein Partner), also in gerader Zahl; entsprechend ist auch die Zahl der äußeren Fixpunkte gerade. Die allgemeine Struktur lautet 1 + 2a + f_außen mit geradem f_außen, und 1 + 7·2 + 42·2 ist der Fall a = f_außen = 0. Formulierung entsprechend als Fallunterscheidung anlegen — sonst startet der Ordnung-2-Zweig mit einer unbegründeten Einschränkung.

**B2 — Prioritätsbehauptung widerspricht dem eigenen Text.** Das Kurzfazit sagt, damit sei „erstmals ein nichttrivialer Ordnung-3-Teilraum … vollständig zertifiziert ausgeschlossen". Der Bericht selbst nennt zwei Absätze früher den bereits zertifizierten Typ 3⁹. „Erstmals" ist zudem eine Aussage über die gesamte Literatur, die nicht belegt wird. Ersatz: „nach unserer Kenntnis erstmals mit maschinell geprüften Zertifikaten" oder Streichung.

**B3 — Fehlzuschreibung der Fixpunktfreiheit.** „Für eine hypothetische Automorphismusgruppe der Ordnung 3 **konnten wir** die relevante Situation auf fixpunktfreie Wirkungen reduzieren" liest sich als eigene Ableitung. Es ist ein publiziertes Resultat (Crnković–Maksimović 2020: ein Ordnung-3-Automorphismus ist fixpunktfrei; Ordnungen 6 und 9 treten nicht auf). Das ist mehr als eine Höflichkeitsfrage: Die gesamte Zählung „137 verbleibende Typen" setzt Fixpunktfreiheit voraus. Ohne Zitat wirkt die Klassifikation lückenhaft (Fixpunktfälle scheinbar unbehandelt), obwohl sie es nicht ist.

**B4 — Zählung der Matrixpositionen beim 2-Switch.** Ein 2-Switch verändert vier ungeordnete Knotenpaare, in der symmetrischen Matrix also **acht** Einträge (vier symmetrische Paare). Die Formulierung „Flippen von vier symmetrischen Matrixpositionen" ist mindestens missverständlich; für die Reproduzierbarkeit des Suchoperators sollte dort „vier symmetrische Positionspaare, also acht Einträge" stehen.

## C. Überzogene oder zu schwache Formulierungen

**C1 — Das zertifizierte Resultat ist zu schwach formuliert (der wichtigste Punkt dieses Abschnitts).** Der Satz endet mit „…, der alle im Modell kodierten Quotientenbedingungen erfüllt". Das klingt, als hinge das Resultat von einer beliebigen Kodierungsentscheidung ab. Tatsächlich sind **alle kodierten Bedingungen bewiesen notwendig** — die nichttriviale darunter ist Lemma B. Damit ist der Ausschluss für den Typ (6,3⁷) unbedingt. Zugleich muss aber offengelegt werden, dass die Zertifikate die **lemma-verstärkte** CNF betreffen und der Transfer auf das Grundmodell über den Papierbeweis von Lemma B läuft. Empfohlene Zwei-Stufen-Formulierung:

> *Stufe 1 (vollständig maschinell geprüft):* Die CNF `source_task03_triangle_eo` ist unerfüllbar; belegt durch 656 modulare LRAT-Zertifikate, doppelt geprüft, plus das Überdeckungsargument.
> *Stufe 2 (Kompositsatz):* Da jede kodierte Bedingung — insbesondere Lemma B — eine bewiesen notwendige Bedingung ist, existiert kein fixpunktfreier Ordnung-3-Quotient vom Typ (6,3⁷) bei τ = 6. Formal: *maschinell verifiziert modulo dokumentiertem Lemma-B-Transfer.*

**C2** — siehe B2.

**C3 — positiv zu vermerken:** Der δ-Zweig, der memetische Zweig und die Aut(G) = 1-Passage sind eher vorsichtiger formuliert als nötig. Das ist der richtige Fehler in dieser Richtung; ich empfehle keine Verschärfung.

## D. Fehlende Begründungen und Belege

**D1 — Das Überdeckungsargument fehlt (kritischster Punkt).** Der Bericht nennt 488 + 168 = 656, erklärt aber nicht, **warum** diese Menge den gesamten Suchraum überdeckt. Das Argument ist kurz und sollte wörtlich in den Bericht: Die 9 Nicht-L-Paare der C₆-Komponente erzeugen eine Partition in 2⁹ = 512 Wurzeln; 488 davon werden direkt entschieden, 24 sind schwer. Jeder schwere Knoten wird an **einer Exact-One-Gruppe** verzweigt, deren ALO- und AMO-Klauseln syntaktisch in der Eltern-CNF stehen; deshalb partitionieren die drei Kinder 001/010/100 die Lösungsmenge des Elternknotens **exakt**. Rekursion bis zu 168 Blättern, alle UNSAT ⇒ CNF UNSAT. Wichtig: Dieses Argument ist **rein aussagenlogisch** und braucht Lemma B nicht — der Coverage-Checker trägt damit keine Beweislast, sondern nur Buchführung. Das stärkt das Resultat und sollte nicht verschenkt werden.

**D2 — Lemma B ohne Beweis.** Lemma B steckt als 210 Exact-One-Gruppen in der CNF und trägt den Transfer auf das Grundmodell; es ist damit die einzige nicht maschinengeprüfte Komponente der Kette. Der Beweis passt in fünf Zeilen und gehört in den Bericht: Für L-benachbarte t_a, t_b eines Dreiecks hat die Paargleichung die rechte Seite 6 − 4·1 − 2·1 = 0, weil der dritte Dreiecksknoten bereits einen Gewicht-2-Weg beisteuert; alle Terme sind nichtnegativ, also haben t_a, t_b **keinen** gemeinsamen S-Nachbarn (⇒ höchstens eine Kante je Außenknoten). Innerhalb des Dreiecks gibt es keine S-Kanten, also verlassen alle 3·10 = 30 S-Kanten der Dreiecksknoten das Dreieck und treffen 33 − 3 = 30 Außenknoten mit Kapazität 1 — also **genau eine** ✓. Die Gradbilanz (deg_S = 10 auf Nicht-Dreieckorbits, 12 auf Dreieckorbits) habe ich nachgerechnet.

**D3 — C₄-Ausschluss ohne Beweis.** Ebenfalls eine Zeile, ebenfalls tragend (er eliminiert 113 der 252 Typen): Zwei gegenüberliegende Knoten einer C₄-Komponente haben zwei gemeinsame L-Nachbarn mit je Beitrag 2·2 = 4, also (Q²) ≥ 8; verlangt ist (Q²) + q = 6 mit q ≥ 0 — Widerspruch.

**D4 — Herkunft der 512 Wurzeln.** Nicht erklärt; ein Halbsatz genügt (2⁹ über die 9 Nicht-L-Paare der C₆-Komponente).

**D5 — Literaturzitate fehlen vollständig.** Der Bericht enthält kein einziges Zitat. Mindestens erforderlich: Crnković–Maksimović (Fixpunktfreiheit bei Ordnung 3), Behbahani–Lam (alle Primordnungen außer 2 und 3 ausgeschlossen), Makhnev–Minakova (|Aut| teilt 2·3³·7·11), Cesarz–Woldar (gerade Ordnung ⇒ |G| teilt 6). Die letzten drei sind zwingend, sobald der Bericht Aut(G) = 1 als Fernziel nennt: **ohne sie folgt aus „Ordnung 2 und 3 ausgeschlossen" gerade nicht die Trivialität der Gruppe.**

**D6 — Unausgesprochene Voraussetzung der Polytop-Identität.** Σ_{|F|≥5}|F| = 4δ gilt nur unter der Annahme n₃ = 231, also dass **jedes** Graphendreieck eine 2-Fläche berandet. Aus λ = 1 folgt lediglich, dass dreieckige 2-Flächen eindeutig den Graphendreiecken entsprechen, nicht die Umkehrung. Die Annahme ist im explorativen Zweig legitim, muss aber dastehen.

**D7 — Reichweite der Hash-Prüfung ungenau.** Der Bericht sagt „SHA256-Prüfung aller 656 komprimierten Proofarchive". Das Factsheet präzisiert, dass die Roh-Proof-Hashes nur geprüft werden, „where recorded". Beides ist vereinbar, aber der Bericht sollte die Abdeckung auf Rohdatenebene beziffern (wie viele der 656 haben einen aufgezeichneten Roh-Hash?).

**D8 — Prüfer-Provenienz weiterhin offen.** CaDiCaL ist mit Version 2.2.1 benannt; für `lrat-check` und `cake_lpr` fehlen Version und Binär-SHA256. Das war bereits mein MUST-FIX M7 vom 29.08. und ist die letzte ungebundene Vertrauenskomponente der Kette: Ein Zertifikat ist nur so gut wie der identifizierbare Prüfer. Für `cake_lpr` sollte zusätzlich die verwendete Heap-Konfiguration (CML_HEAP_SIZE=16384) als Teil der Prüferidentität dokumentiert werden.

**D9 — Coverage-Manifest nicht im proof-freien Export.** Ein externer Gutachter kann die Überdeckung derzeit nicht prüfen, ohne 206 GiB anzufordern. Die 656 Zeilen (Job-Key, Elternknoten, Split-Gruppe, CNF-SHA256, Proof-SHA256, Prüfer-Exitcodes) sind wenige hundert KiB und gehören in den Git-Export. Damit wäre die Überdeckung vollständig extern nachrechenbar — ich habe genau das am 29.08. für den Vorgängerstand getan und alle 216 Job-CNFs bitgenau aus der Quell-CNF rekonstruiert.

## E. Empfohlene Änderungen vor dem Git-Meilenstein

1. **Anhang mit drei Beweisen** ergänzen: Überdeckungssatz (D1), Lemma B (D2), C₄-Ausschluss (D3). Das ist die mit Abstand wichtigste Änderung — sie verwandelt drei Behauptungen in nachprüfbare Mathematik.
2. **Zwei-Stufen-Formulierung des Resultats** nach C1 übernehmen.
3. **Lemma B in voller Allgemeinheit aussprechen.** Der Bericht stellt es als τ = 6-Aussage dar. Tatsächlich ist es **τ-unabhängig**: deg_S = 10 gilt auf jedem Nicht-Dreieckorbit für jedes τ, und 33 − 3 = 30 ebenfalls. Lemma B gilt also für *jedes* τ und *jede* C₃-Komponente von L. Genau das trägt die geplante Breitenstrategie und sollte deshalb als eigenständiges Lemma formuliert werden, nicht als Task-03-Detail.
4. **Literaturabschnitt** nach D5 einfügen; Fixpunktfreiheit korrekt zuschreiben (B3).
5. **Ordnung-2-Passage** nach B1 als Fallunterscheidung umschreiben.
6. **Prüfer-Provenienz** (D8) und **Coverage-Manifest** (D9) in den Export aufnehmen.
7. Kleinigkeiten mit Wirkung auf Reproduzierbarkeit: 2-Switch-Positionszählung (B4), Herkunft der 512 (D4), n₃-Annahme (D6), Hash-Abdeckung (D7), „erstmals" (B2). Ferner die Formulierung „Die vom Nutzer vorgeschlagene Beschreibung" — in einem Statusbericht sollte die Herkunft eines Vorschlags sachlich bezeichnet werden.

## F. Offene Fragen für den Fortsetzungsauftrag

**F1 — Welche Lücke zuerst? Antwort: die dreiecksfreien Typen. Und die Datenbasis ist optimistischer, als der Bericht erkennen lässt.** Ich habe die Dreiecksverteilung über alle C₄-freien Typen berechnet — diese Messung fehlt im Bericht und ändert die strategische Lage:

| τ | C₄-freie Typen | davon **ohne jede C₃-Komponente** | Verteilung der Dreiecksanzahl |
|---|---:|---:|---|
| 6 | 103 | **42** | 9:1, 7:1, 6:1, 5:3, 4:5, 3:9, 2:15, 1:26, 0:42 |
| 13 | 28 | **13** | 5:1, 4:1, 3:2, 2:4, 1:7, 0:13 |
| 20 | 6 | **3** | 2:1, 1:2, 0:3 |
| 27 | 2 | **1** | 2:1, 0:1 |
| **gesamt** | **139** | **59** | |

Zwei Folgerungen. Erstens: Bei **59 der 139 Typen greift Lemma B überhaupt nicht**, bei weiteren 35 nur mit einer einzigen Dreieckskomponente. Die Breitenstrategie steht und fällt also mit zykluslokalen Lemmas für C₅, C₆, C₇ …, nicht mit Verallgemeinerungen der Dreiecksbedingung. Zweitens, und unbequemer: **Die beiden erledigten Typen sind exakt die beiden dreiecksreichsten.** 3⁹ hat neun Dreiecke (das Maximum), (6,3⁷) ist der eindeutige Typ mit sieben — acht ist arithmetisch unmöglich, da 27 − 24 = 3 wieder ein Dreieck ergäbe. Jede Aufwandsprognose, die aus diesen beiden Läufen extrapoliert, ist damit systematisch zu optimistisch: Die verbleibenden 101 Typen sind im Mittel strukturärmer und mithin härter. Der Bericht sollte diese Verzerrung ausdrücklich benennen, bevor Ressourcen zugesagt werden.

**F2 — Konkreter erster Schritt.** Vor jeder weiteren Massenzertifizierung: die zykluslokalen Gesetze für C₅ und C₆ herleiten und als Klauselfamilie messen. Aus meinem Review vom 28.08. liegen die C₆-Gleichungen bereits vor — für C₆-Kanten ist der gemeinsame S-Nachbargrad gerade (0, 2 oder 4), für Distanz-2-Paare gilt eine Paritätskopplung mit höchstens einem der beiden flankierenden Durchmesser. Diese Familien sind der natürliche Ersatz für Lemma B im dreiecksfreien Sektor. Messgröße: Wie viele der 59 dreiecksfreien Typen fallen mit diesen Klauseln in einem 300-Sekunden-Scout?

**F3 — Kalibrierung statt Extrapolation.** Bevor die 101 Typen angegangen werden, ein billiger Scout über alle 103 τ = 6-Typen mit der jeweils anwendbaren Lemma-Schicht, um die Härte gegen die Dreiecksanzahl aufzutragen. Das ergibt eine belastbare Aufwandskurve statt einer Hochrechnung aus zwei Extremfällen.

**F4 — Ordnung 2 erst nach der Fallklassifikation.** Gemäß B1 ist zunächst die Fixpunktstruktur zu klassifizieren (1 + 2a + f_außen, beide gerade Anteile), und zwar unter Einbezug der Literaturschranken. Ein Ordnung-2-Zensus vor dieser Klassifikation liefe Gefahr, einen Spezialfall für den allgemeinen Fall zu halten.

**F5 — Zweite externe Kopie.** Der Bericht sagt korrekt, dass die WSL-Originale bis zur Verifikation der zweiten Kopie nicht gelöscht werden. Diese Zusage sollte als Freigabebedingung im Git-Meilenstein festgehalten werden, nicht nur im Fließtext.

---

## Schluss

Der Bericht gibt den erreichten Stand **korrekt und ohne Übertreibung** wieder; in der Frage der Reichweite ist er strenger als die meisten Arbeiten, die ich in diesem Projekt begutachtet habe. Was fehlt, ist nicht Zurückhaltung, sondern das Gegenteil: Drei kurze Beweise und ein Literaturabschnitt würden aus mehreren als Behauptung dastehenden Kernpunkten nachprüfbare Mathematik machen — und die Zwei-Stufen-Formulierung würde das Resultat sogar **stärker** und zugleich ehrlicher aussprechen als bisher. Die einzige strategisch relevante Korrektur betrifft nicht das Erreichte, sondern die Prognose: Die beiden abgeschlossenen Typen sind die beiden günstigsten des gesamten Suchraums.
