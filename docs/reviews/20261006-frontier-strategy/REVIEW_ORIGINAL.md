**Grundlage.** Ich habe den Stand `0e693a3` und das Reviewarchiv `e4d4d63` gelesen. GitHub sperrt meinen Webabruf, deshalb habe ich das Repository ohne Dateiinhalte geklont und die Dateien mit `git show` angezeigt. Ich habe keines eurer Programme ausgeführt, nichts nachgezählt und keine Belege geprüft.

Neben den Berichten habe ich Quelltext gelesen: `certify_dead.py`, `rup_check.py`, `widths.py`, `membership.py`, `historical_core.encode`, `propagation.py`, `row_sampler.py` und `tree_probe.py`. In `FRONTIER_DATA.zip` habe ich nur die gespeicherten Felder `attempts` der 17 Ausschlussdateien angesehen. Einfache Umrechnungen veröffentlichter Zahlen weise ich aus.

Kennzeichnung: **[M]** mathematische Folgerung · **[R]** berichteter oder aus euren Dateien abgelesener Rechenbefund · **[S]** statistische Schätzung · **[V]** Vermutung · **[P]** offener Prüfauftrag.

### Kurzfassung

Die 17 Ausschlüsse sind korrekt begründet. Der Übergang von „Präfixprüfung bestanden" zu „nicht ergänzbar" ist logisch sauber. Das liegt aber nicht daran, dass die Prüfung schrittweise strenger wurde. Es wurde erstmals ein anderes Modell angewandt: die gemeinsame Erfüllbarkeit aller Gleichungen *einer* offenen Zeile, einschließlich der μ-Gleichungen. Weder der Abstieg noch das Präfixaudit haben diese Prüfung je auf eine andere als die nächste Zielzeile angewandt.

Daraus folgt der eigentlich wichtige Befund. Die gemessenen Bäume bestehen vermutlich ganz überwiegend aus Knoten, die bereits tot sind [V]. Die Punktschätzungen messen also Widerlegungskosten schwach prunender Verfahren, nicht die Größe eines Raums lebensfähiger Teilgraphen.

Strategisch ist die zeilenweise Aufzählung nicht nur zu teuer, sondern strukturell ausgereizt. Schon die Ebenen 2 und 3 sind so groß, dass ein nachgelagerter stärkerer Test wenig retten kann. Ich empfehle, die Hauptlinie auf SAT-basierte, zertifizierte Ausschlüsse ganzer (a,M)-Klassen zu verlegen. Euren 17-Pfade-Vorschlag würde ich nur als Spezialfall einer gewichteten Messung über alle Abstiege mitnehmen.

### 1. Welche Schlussfolgerungen tragen?

Falsch im strengen Sinn ist nur eine Formulierung. Inhaltlich arbeitet ihr sorgfältig. Die Schwächen liegen in Gewichtung, Modellbenennung und strategischer Folgerung.

#### 1.1 Tiefe 2, Matchingklassen, Kalibrierung (`review_followup`)

Dieser Teil ist getragen. Der Beweis in ABGLEICH.md und 12.288/12.288 vorab festgelegte Entscheidungen stützen die Tabelle [M]+[R].

Beide Korrekturen am Review sind richtig:

- Die 2/11–4/11-Heuristik übersah, dass F zwei der formal schlechten Kandidaten schon verbietet. Die exakten Breiten ersetzen sie [R].
- Die Gegenbeispiele zur Schichtung nach t sind schlüssig [R].

Ebenso richtig sind die Präzisierungen zu Vereinigung und Schnitt sowie zur Rolle von μ im c′-Fall [M]. Die 96er-Kalibrierung ist durch die Hauptmessung überholt. Der Teil ist abgeschlossen und liefert strategisch nur konstante Faktoren.

#### 1.2 Hauptmessung (`tree_results/BERICHT.md`)

Getragen sind:

- Das Gate ist nicht erfüllt, der Status INSUFFICIENT_INFORMATION ist korrekt.
- Es gibt keine Hochrechnung auf 8105 Roots.
- „Zeilenweise Erschöpfung ist keine realistische Kampagne" [S].
- Die Trennung von kumulierter und Endgewichts-ESS ist richtig und wichtig.

Korrekturen und Ergänzungen:

- **Formulierung.** „Rund 1,03 Millionen weniger geschätzte Knoten" meint einen Faktor, keine Differenz.
- **Reihenfolgeeffekt.** Er ist robuster, als der Bericht nahelegt, weil er sich auf Ebenen mit voller Überlebensrate aufbaut. Auf Ebene 3 stehen 10^16,07 gegen 10^12,91, jeweils bei 10.000/10.000 positiven Abstiegen, also etwa Faktor 1.400 (Umrechnung) [S].
- **Propagationseffekt.** Der Faktor ×30–54 entsteht dagegen auf Ebene 8–11, wo die Überlebensrate einbricht. Er ist weniger belastbar [S].
- **Was „numerisch" heißt.** Nach `tree_probe.py` ist die Reihenfolge `range(1, 84)`. Bei lexikographischer Labelung sind die Zeilen 1–11 genau L(0) ohne a. Der numerische Arm schließt also auf Ebene 12 die H-Nachbarschaft des Randknotens 0 ab [M, aus Code und Labelkonvention]. Verglichen wird damit „N_H(a) mit vorgegebenem Matching" gegen „L(0) ohne vorgegebenes L(0)-Matching", nicht „strukturiert gegen unstrukturiert". Die 102 numerischen Endpunkte sind folglich L(0)-Abschlüsse plus eine Zeile und natürliche Vergleichsobjekte.
- **Mitgliedschaftstest.** Der SAT-Mitgliedschaftstest hat in allen 40.000 Abstiegen keinen Vorschlag abgelehnt. `tree_probe.py` bricht in diesem Fall mit `REJECTED_PROPOSAL_NOT_EMPTY_F_BRANCH` ab. Diese Kategorie fehlt in allen vier `termination_counts`, und die übrigen Kategorien summieren sich je Zelle zu 10.000 [R]. Die F-Arme waren damit empirisch reine Vorschlagsbäume. An der Frontier lehnte der Test 3 von 1.432 Vorschlägen ab [R]. Die in ABGLEICH.md ausführlich begründete Unterscheidung „lokaler Vorschlag vs. F" war in dieser Messung praktisch folgenlos.
- **„Klarer Kandidat".** Die Aussage, die neue Reihenfolge sei ein klarer Kandidat, gilt nur innerhalb des Zeilenparadigmas und ist durch die Frontier überholt.

#### 1.3 Präfixprüfung

Getragen im abgegrenzten Umfang [R]. Der Bericht vermittelt aber mehr Stärke, als das Modell hatte.

Die „gemeinsame Sternrelaxation" umfasst nur λ-Gleichungen: 392 = 28 × 14 Gleichungen, eine für jede vollständige Zeile und jeden ihrer Nachbarn. μ-Gleichungen zwischen einer vollständigen Zeile und einem Nichtnachbarn wurden nur einzeln als Intervalle geprüft. Das ist dieselbe Relaxationsstufe wie die Kapazitätspropagation des Abstiegs, nur unabhängig implementiert.

Unabhängige Implementierung prüft Korrektheit, nicht Prunestärke. Bemerkenswert: `historical_core.encode(rows, target=None)` lag bereits im Code vor („alle offenen Margen und jedes Paar mit gebauter Zeile"). Es wäre stärker gewesen als Sternrelaxation und Einzeilentest zusammen (siehe Abschnitt 2).

#### 1.4 Frontier

**Der Ausschluss ist getragen [M].** Ich habe die Herleitung („Warum eine einzige Nullzeile …") und `certify_dead.encode` gelesen. Alle Bedingungen sind notwendig und korrekt übersetzt:

- Randmarge 1 genau für c ∈ S(t) ∪ S(t)′, sonst 2.
- Paargleichung 2 − A[u,t] − |S(u)∩S(t)|.
- x_t = 0 und feste Einträge aus den gebauten Zeilen.
- Leere Klausel bei unzulässiger rechter Seite.

RowProposal dient nur der Auswahl der Zielzeile, nicht der Begründung. Euer RUP-Prüfer ist korrekt: Die Unit-Propagation stimmt, das Ignorieren von Löschungen ist für reine RUP-Prüfung sound, RAT wird abgewiesen. Die 17 Positivkontrollen testen genau die Richtung, auf die es ankommt: Jede ganzzahlige Lösung muss zu einem CNF-Modell erweiterbar sein. Die Vertrauensbasis ist klein und benannt.

Überzogen oder unvollständig:

- **„601 Nullbreiten" sind keine 601 Einzeilenwidersprüche.** Es sind Nullen unter RowProposal mit LD-Nullen und gespeicherten Festlegungen. Unabhängig getestet wurden nur 19 Ziele: 17 UNSAT und 2 SAT. Die beiden SAT-Fälle sind `prefix_r6682_w290`, Ziele 13 und 15, laut Feld `attempts` [R]. Mindestens zwei Nullen beruhen also auf Propagation, deren allgemeine Korrektheit ihr selbst als unbewiesen bezeichnet. SUMMARY.json sollte das ausweisen.
- **„Teilausschluss" ist in der Gewichtung irreführend.** Formal ist es korrekt. Aber 17 gelabelte Punkte stehen gegen eine geschätzte Ebene-13-Population von etwa 10^27 je Root [S]. Ich würde von einem zertifizierten Diagnosebefund sprechen.
- **Stiller Strategiewechsel.** PLAN.md §8 sieht schon bei drei Größenordnungen über Budget vor, zertifizierbare (a,M)-Klassen zu priorisieren. Der Vorbehalt geringer Belastbarkeit trägt bei mehr als 15 Größenordnungen nicht mehr. Die Frontier-Empfehlung bleibt dennoch im Zeilenabstieg, ohne das zu diskutieren.

Richtig und wichtig ist die Aussage, dass Reihenfolgeänderungen unterhalb toter Präfixe nichts retten.

### 2. Modelle und Übergänge

| Modell                                  | wo                        | prüft gemeinsam                                                                                         | fehlt                                           |
| --------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Loc(t): RowProposal                     | Abstieg, Frontierbreiten  | Margen von t, Paargleichungen t–gebaute Zeilen, LD-Nullen, Festlegungen A                               | alles zu anderen offenen Zeilen                 |
| F(t): `encode(rows,t)` + Mitgliedschaft | Abstieg, Frontier         | wie Loc, plus λ-Sterne gebauter H-Zeilen                                                                | Margen und μ-Gleichungen anderer offener Zeilen |
| Prop: `propagate`                       | starke Arme               | alle Grad-, Rand- und Paargleichungen aller offenen Zeilen, aber jede einzeln; Matchings auf N(u), L(c) | gemeinsame Erfüllbarkeit innerhalb einer Zeile  |
| S: Präfixaudit                          | 17 Präfixe                | λ-Sterne aller 28 vollständigen Zeilen                                                                  | μ-Gleichungen (nur Einzelintervalle)            |
| R(t): `certify_dead`                    | Ausschlüsse               | alle 14 Margen und 13 Paargleichungen von t                                                             | Kopplung an andere Zeilen                       |
| Z: R(t) für alle offenen t              | nirgends systematisch     | –                                                                                                       | Kopplung zwischen Zeilen                        |
| G: `encode(rows, None)`                 | im Code, nicht im Abstieg | alle offenen Margen und alle Paargleichungen mit gebauter Zeile, geteilte Variablen                     | Paargleichungen zweier offener Zeilen           |

**Logik [M].** Ergänzbar ⇒ G ⇒ (S und Z). S und Z sind unvergleichbar: S fehlen die μ-Gleichungen, Z die Kopplung zwischen Zeilen. Der Abstieg prüfte je Schritt nur die nächste Zielzeile und Einzelgleichungen, also weniger als Z. „S bestanden, Z verletzt" ist daher kein Widerspruch. Der Übergang ist sauber begründet; problematisch ist nur die Darstellung des Audits als stark.

Unbemerkte Modellwechsel gibt es an vier Stellen:

1. **„F" ist überladen.** Gemeint sind je nach Stelle das historische F₀ des Census, F unter festem M oder F mit Festlegungen A. Diese sollten getrennt benannt werden, etwa F₀, F_M, F\_{M,A}.
2. **„Sternrelaxation" bezeichnet zwei Dinge.** Im Audit sind es 28 Zeilen samt Randsternen. Im historischen Encoder mit Ziel (Zeilen 125–138) sind es nur die Sterne der gebauten H-Zeilen und die Margen der Zielzeile. „Historische vollständige Sternrelaxation" in ABGLEICH.md ist daher irreführend.
3. **Nullbreite und Unerfüllbarkeit werden vermischt.** Nullbreite (Loc mit A) und zertifizierte Unerfüllbarkeit (R) stehen in Kurzfassungen nebeneinander, als wären sie dasselbe (siehe 1.4).
4. **Der Mechanismus ist nicht neu.** 57 % der Abstiege in Zelle 3 enden mit EMPTY_LOCAL_PROPOSAL [R]. Das ist derselbe Einzeilentest, nur verspätet und für jeweils eine Zeile. Neu an der Frontier ist seine Breite.

### 3. Bedeutung der Baumgrößen

**Gültigkeit.** Als Schätzungen der Knotenzahl der vier Verfahren bis Tiefe 13 auf den 24 Roots bleiben sie gültig, mit den bekannten Vorbehalten zu schweren Rändern [S]. Tote Knoten werden besucht und zählen.

**Deutung.** Die Werte messen Widerlegungskosten.

- In den F-Armen erreichte kein Abstieg Tiefe 11 (Zelle 0) bzw. 12 (Zelle 2). Dort approximieren die Werte den gesamten Widerlegungsbaum dieser Verfahren, bis auf seltene, nicht gezogene tiefe Äste [S].
- Für Zelle 3 mit zusätzlichem Endtest gilt dasselbe, sofern auch die nicht gezogenen Abschlüsse tot sind [V].

**Einfluss des Ebene-13-Ausschlusses.** Er ändert die Kennzahl praktisch nicht. Aus dem Profil mit gleicher Rootgewichtung umgerechnet stammen etwa 52 % der Masse von Ebene 9, 37 % von Ebene 10, 9 % von Ebene 8 und nur rund 0,5 % von den Ebenen 12 und 13 zusammen [S].

**Z-konsistente Abschlüsse.** Bei einer Endgewichts-ESS von 2,55 gibt es keine informative obere Schranke [S]. Selbst ungewichtet, unter dem Vorschlagsmaß und bei unterstellter Unabhängigkeit, folgt aus 17/17 nur: höchstens etwa 16 % der erreichten Endpunkte lebendig (95 %). Wegen der Häufung in 12 Roots ist auch das zu optimistisch.

Was sich zusätzlich sagen lässt, ohne die Auswahl zu verallgemeinern:

- **Die Kosten liegen vor dem Abschluss von N[a].** Danach sind 601 von 1.207 Zeilen leer. Positive Zeilen haben im Mittel etwa 2,4 Kandidaten, höchstens 11 [R]. Ein Z-konsistenter Abschluss hätte vermutlich einen kleinen Restbaum [V]. Die harte Teilaufgabe ist also, Abschlüsse zu finden oder zu widerlegen.
- **Die letzten beiden Zeilen sind fast festgelegt.** In allen 17 Endpfaden hatte die 13. Zeile die Breite 1. Das folgt aus identischen Profilwerten auf Ebene 12 und 13 bei 17 positiven Abstiegen, da Gewichte Produkte von Breiten ≥ 1 sind [M aus R]. Die 12. Zeile, das erste randgepaarte w, beendete 123 von 140 Abstiegen [R].
- **Kapazität je Gleichung ist viel schwächer als die gemeinsame Prüfung je Zeile.** Die RUP-Belege brauchen 34–1.347 Additionen. Unit-Propagation allein sieht diese Widersprüche nicht [R].
- **Klassenausschlüsse brauchen Gleichungen nach außen.** Für die (a,M)-Klassen der 17 Präfixe ist die innere Konsistenz von N[a] erfüllbar [M]. Jeder Klassenausschluss muss also Gleichungen zu Knoten außerhalb von N[a] nutzen.
- **Z-Tod frühestens auf Ebene 2.** Der Census fand keine Nullbreite, also gilt Z auf Ebene 1 für alle 8105 Roots [R].

### 4. Strategische Lage

**Was gesichert ist.** Das Tiefe-2-Lemma, die Matchingorbits für 24 Roots, 17 tote Präfixe und die statistisch gut gestützte Aussage: Zeilenweise Aufzählung liegt auf den gewählten Roots um mehr als 15 Größenordnungen jenseits jedes realistischen Budgets. Einen Fortschritt in Richtung eines Rootausschlusses gibt es noch nicht.

**Warum ein stärkerer Test im Zeilenabstieg das kaum ändert.**

- Im besten Arm liegen je Root etwa 10^8,0 Knoten auf Ebene 2 und 10^12,9 auf Ebene 3, bei voller Überlebensrate [S].
- Der Census zeigt global schon für die sparsamste zweite Zeile 4,85·10^9 gelabelte Ebene-2-Knoten [R].
- Ein Test nach dem Erzeugen kostet mindestens (Anteil lebender Ebene-2-Knoten) × (Ebene-3-Breite).
- Nehmen wir Tausende Roots, etwa 1 ms je Prüfung und rund 10^4 CPU-Stunden Budget an. Dann müsste dieser Anteil bei etwa 10^-5 oder darunter liegen [V, Überschlag mit angenommenen Größen].

Dass zwei gebaute Zeilen fast immer eine leere Zeile erzwingen, halte ich für unplausibel [V]. Es ist aber billig prüfbar (Vorschlag B). Trifft es nicht zu, muss die Prüfung in die Erzeugung wandern. Das heißt: auf einzelnen Kanten mit gelernten Widersprüchen verzweigen, statt auf Zeilen mit 10^5–10^7 Kandidaten. Das ist ein SAT-Solver. Zeilen und Matchings dienen dann nur noch zur obersten Aufteilung und zur Symmetriereduktion.

**Zu eurem Vorschlag.** Der Kern ist richtig: Man muss wissen, wie früh Widersprüche entstehen. Als eigenständiger Schritt hat er aber vier Schwächen:

- Die 17 Pfade sind die 0,17 % Überlebenden. Die Baummasse liegt zu fast 90 % in Abstiegen, die auf Ebene 9–10 endeten.
- 17 Pfade aus 12 Roots bei einer Endgewichts-ESS von 2,55 tragen keine Entwurfsentscheidung.
- Die früheste tote Ebene allein sagt nichts über Kosten und Nutzen einer Prüfung.
- Er bleibt im Paradigma, dessen Grenze schon ohne ihn sichtbar ist.

**Zurückstellen** würde ich:

- weitere Importance-Kampagnen mit schwacher Prüfung,
- Reihenfolgeoptimierung und Reihenfolgen jenseits Tiefe 13,
- Rootdesigns zur Hochrechnung von Verfahrenskosten,
- Arbeit unterhalb toter Präfixe,
- den Mitgliedschaftstest im Abstieg.

Zum Betrieb: Viel Aufwand fließt in CPU-Abrechnung und Ledgerabweichungen bei Läufen, deren Ergebnis keine Entscheidung ändert. Volle Belegstrenge würde ich auf zertifikatsbildende Läufe beschränken.

### 5. Fortsetzungsvorschläge

#### A (Priorität 1): Ganze (a,M)-Klassen per SAT zertifiziert entscheiden

**Fragestellung.** Gibt es zu einer (a,M)-Klasse Zeilen für die zwölf H-Nachbarn von a, so dass gemeinsam erfüllt sind:

- alle Randmargen aller 84 H-Knoten,
- alle Paargleichungen, die einen Knoten aus N[a] berühren,
- jeweils mit geteilten symmetrischen Variablen?

Das ist `encode(rows, None)` mit den zwölf Nachbarzeilen als Variablen; ich nenne es N1. Die Instanz hat grob 3.300 freie Kanten und etwa 7·10^4 Produktvariablen. Für CDCL ist das handhabbar; die Härte ist offen [V].

**Korrektheit [M].** Jeder SRG mit a in der Klasse liefert ein Modell. UNSAT schließt die Klasse aus, UNSAT aller Orbitrepräsentanten den Root. Voraussetzungen sind die Vollständigkeit der Matchingaufzählung und dass jeder Generator eine echte Symmetrie ist. Ob die Generatoren die volle Gruppe erzeugen, ist für die Korrektheit gleichgültig.

Kontrollen: Die 17 toten Präfixe als feste Belegung müssen UNSAT ergeben. Das srg(9,4,1,2)-Analogon muss SAT ergeben.

**Erkenntnisgewinn.** Das wären die ersten Ausschlüsse von messbarem Gewicht: eine Klasse von im Mittel etwa 216 je Root statt 17 Punkte. Außerdem ein direkter Test, ob schon die lokale Konsistenz um einen H-Knoten scheitert.

**Pilot und Entscheidungskriterium.** Alle Orbitrepräsentanten zweier vorab festgelegter Roots, etwa die mit der kleinsten Orbitzahl und Root 6682 (vier tote Endpunkte). Kissat oder CaDiCaL mit DRAT/LRAT, Prüfung mit drat-trim oder cake_lpr, festes Zeitlimit je Instanz, etwa 1 CPU-h.

**Konsequenzen.**

- **≥ 90 % zertifiziert UNSAT, Median ≤ 10 % des Limits:** eine Root vollständig ausschließen. Danach ein Kostenmodell über eine am Census geschichtete Zufallsstichprobe von Roots.
- **Einzelne SAT:** Das Modell ist das wertvollste Objekt bisher. Es wird direkt gegen alle Gleichungen geprüft und dann einer stärkeren Relaxation N2 übergeben, etwa mit Paargleichungen der zweiten Nachbarschaft. Ist mehr als die Hälfte SAT, ist N1 zu schwach.
- **Überwiegend UNKNOWN:** Per Lookahead in Würfel zerlegen, nicht nach ganzen Zeilen, und die Würfelhärte messen. Bleiben auch moderate Würfel ungelöst, ist der SAT-Weg beim verfügbaren Budget nicht tragfähig. Dann rücken C und symmetrische Teilfälle in den Vordergrund.

#### B (Priorität 2, billig, zuerst): Z über die gespeicherten Abstiege gewichtet messen

**Fragestellung.** Ab welcher Ebene sind gewichtet betrachtete Knoten Z-tot? Wie groß ist der Baum „Zelle 3 plus Z-Test"?

**Methode.**

- Eine feste, nach Roots geschichtete Stichprobe, etwa 40 Abstiege je Root aus Zelle 3, dazu alle 119 Endpunkte.
- Rekonstruktion aus Seeds und Rängen.
- Z als Leerheitstest von R(t) mit LD, ohne gespeicherte Propagation.
- Monotonie [M]: Aus P ⊆ P′ folgt R(t|P′) ⊆ R(t|P). Die erste tote Ebene lässt sich daher per Bisektion mit etwa vier Tests je Abstieg finden.
- Der Schätzer Σ_d W_d · 1{Knoten lebendig} ist für den beschnittenen Baum erwartungstreu [M].

Der Aufwand liegt bei Stunden [V]. Eine Vorstufe nur für Ebene 2 und 3 ist noch schneller.

**Entscheidungskriterium.**

- Lebendiger Anteil auf Ebene 2 ≥ 10^-3 oder beschnittene Schätzung ≥ 10^20 je Root: Zeilenaufzählung dokumentiert einstellen, alles auf A.
- Beschnittene Schätzung ≤ 10^12: Zeilenwiderlegung mit integriertem Z-Test wird zweiter Weg und im Pilot gegen A verglichen.

**Erkenntnisgewinn.** Ein gewichteter Befund statt einer Anekdote. Die erste tote Ebene steuert zudem die Würfeltiefe in A. Euer 17-Pfade-Vorschlag ist darin als Spezialfall enthalten.

#### C (Priorität 3): Anatomie der Einzeilenwidersprüche

**Fragestellung.** Sind die Widersprüche schon in der LP-Relaxation über [0,1] unzulässig? Liegen die toten Zeilen strukturell gleich, etwa in L(c) für c ∈ S(a) ∪ S(a)′?

**Methode.**

- LP-Test der 17 zertifizierten und aller 601 Nullziele.
- Farkas-Multiplikatoren für die LP-unzulässigen Fälle.
- Klassifikation der toten Ziele.
- Handanalyse des kleinsten Belegs: `r0061_w224`, Ziel 23, 34 Additionen.

**Erkenntnisgewinn.** Ein polynomieller Z-Test für B. Lineare Schnitte für A. Eine zweite, lesbare Belegart für die 17 Ausschlüsse. Möglicherweise ein Lemma, das ganze Familien ohne Rechnung ausschließt.

**Entscheidungskriterium und Konsequenzen.**

- ≥ 15/17 LP-unzulässig: LP-Test als Standard in B und A.
- Gemeinsames Farkas-Muster: Lemma formulieren, von Hand beweisen und gegen die Ergebnisse von A testen.
- Sonst: Die Widersprüche sind wesentlich ganzzahlig. Dann mit minimalen unerfüllbaren Gleichungsteilmengen nach Struktur suchen.

**Reihenfolge:** zuerst die Ebene-2/3-Vorstufe von B, parallel den A-Pilot vorbereiten, C nebenher.

### 6. Offene Prüfaufträge [P]

- **`r6682_w290`, Ziele 13 und 15.** Zeigen, dass jede Lösung von R(t) eine LD-Null oder Festlegung verletzt. Das ist zugleich ein Vollständigkeitstest von RowProposal. Ein Fehler dort würde Schätzungen verzerren und eine erschöpfende Suche unsound machen.
- **Externer Prüfer.** Die 17 RUP-Belege zusätzlich mit drat-trim oder per LRAT mit cake_lpr bestätigen.
- **Numerische Endpunkte.** Die 102 L(0)-Abschlüsse (alle 24 Roots) durch dieselbe Frontierpipeline schicken. Ein Z-konsistenter Abschluss ginge direkt als Kandidat in A.
- **Repräsentativität.** Die 24 Roots mit der Censusverteilung vergleichen: Minimalbreiten, Roottypen, Orbitzahlen.
- **Vor dem ersten Rootausschluss.** Vollständigkeit der Matchingaufzählung und Gültigkeit jedes Generators belegen.
- **Kosten des Mitgliedschaftstests.** Seinen Kostenanteil aus den Schrittbelegen ablesen (`sampler_cpu_s` gegen `cpu_s`).
- **Nullziele nach Labelklassen.** Die Verteilung der 601 Nullziele über die Labelklassen relativ zu a bestimmen, als Vorarbeit für C.