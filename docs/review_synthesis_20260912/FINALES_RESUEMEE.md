# Conway 99: finales Resümee nach unabhängigem Review und Gegenprüfung

**Stand: 12. September 2026.** Forschungsgegenstand ist ein einfacher stark regulärer Graph mit Parametern `(99,14,1,2)`, ohne zusätzliche geometrische Voraussetzungen.

Dieses Dokument gleicht den Forschungsbericht, den externen Review und eigene Nachprüfungen der strittigen Punkte ab. Es ersetzt deren vorläufige Schlussfolgerungen, soweit unten korrigiert. Die mathematischen Detailherleitungen des [Forschungsberichts](../research_20260912/BERICHT.md) bleiben ergänzende Grundlage. „Exakt geprüft“ bezeichnet einen angegebenen mathematischen oder ganzzahligen/rationalen Nachweis; es bedeutet nicht automatisch einen vollständigen Beweisassistentenabschluss.

## 1. Gemeinsamer belastbarer Stand

**Für die fixpunktfreie Ordnung-3-Suche verbleiben auf der Ebene des sechs Dreiecksorbits umfassenden Skeletts genau 26 binär-Gram-mögliche Typen.** Die anderen 130 der 156 Sechsknotentypen sind durch notwendige Bedingungen ausgeschlossen. Jeder der 26 Überlebenden besitzt einen exakt geprüften binären Gram-Zeugen. Ein solcher Zeuge ist noch kein vollständiger Quotient und kein Conway-Graph.

Der Review verbessert damit unseren zunächst berichteten Stand von 40 auf 26. Unsere vier zusätzlichen gewichteten Aggregationsausschlüsse sind vollständig in seinen 18 Gram-Ausschlüssen enthalten. Es verbleiben **26, nicht 22** Typen. Der Wert 26 war im historischen Projekt bereits als Reproduktionsziel bekannt; der Fortschritt liegt in der jetzt vorliegenden, unabhängig nachgeprüften Zertifikatskette und nicht in einem beanspruchten neuen weltweiten Zahlenrekord.

**Für K66 ist kein Fehler der tatsächlich verwendeten Profilidentität nachgewiesen.** Die vom Reviewer geforderte Gruppensumme 2 gilt für sämtliche Profile der vier konkreten Wurzeln. Die vorbereiteten strukturierten Abdeckungen bleiben gültig unter ihren ausgewiesenen Brücken- und Blattannahmen. Ihre vollständige Einzelzertifizierung und die vorgelagerten Domänenpflichten bleiben gesonderte Aufgaben.

**Für die memetische Suche ist die Erzeugung zulässiger Änderungen die erste nachgewiesene Optimierungspriorität.** Ein schnelleres Bewertungsverfahren ist vorhanden, aber die gemessene lokale Beschleunigung darf nicht als gleich großer Gewinn der gesamten Suche ausgegeben werden. Der algebraische Cross-over-Vorfilter ist korrekt unter festen Elternausrichtungen. Die stärkere Behauptung, die Ausrichtung ändere sein Potenzial nicht, ist durch ein konkretes Gegenbeispiel widerlegt.

Ein vollständiger Symmetrieausschluss, eine vollständige τ=6-Quotientensuche oder eine verbesserte Konvergenz der evolutionären Kampagne werden nicht behauptet.

## 2. Review-Eingang und Reproduzierbarkeit

Das eingereichte Archiv enthält acht Dateien. Die Prüfsummen aller vorhandenen, im Manifest genannten Dateien stimmen. Es fehlen jedoch sieben dort aufgeführte Bestandteile: `f27_uside_ilp.json` sowie `bvls.py`, `check_A_lundle_lemma.py`, `eisen.py`, `lift.py`, `reimbayev_partial.py` und `tau6_skeleton.py`. `run_all.py` liegt flach im Archiv, stimmt mit seinem Manifesthash überein, importiert aber fehlende Module. Deshalb ist der vollständige Reviewer-Lauf aus diesem Archiv nicht ausführbar.

Die fehlenden Dateien verhindern nicht die unabhängige Prüfung der gelieferten Gram-Zertifikate und Profilzeugen. Dafür wurde ein eigener Prüfer geschrieben. Die strittigen K66- und Ausrichtungsfragen sowie zwei positive Liftkontrollen und ein negatives Quotientenbeispiel wurden mit eigenen Skripten bearbeitet. Weitere Reviewer-Messungen ohne vollständige Eingaben bleiben ausdrücklich Fremdberichte.

Archivhash und Einzelstatus stehen in `results/review_synthesis_20260912/reviewer_package.json`. Es wurden keine laufenden Ryzen- oder Office-Prozesse verändert.

## 3. Exakte Synthese der τ=6-Reduktion

Mit X als einfachem Graphen auf den sechs Dreiecksorbits und C als binärem 6×27-Kreuzblock gilt notwendig

\[
CC^T=G(X)=6I+6J-X^2-5X.
\]

Die binäre Gram-Machbarkeit ist äquivalent zur Existenz nichtnegativer ganzer Profilhäufigkeiten `n_r`, `r∈{0,1}⁶`, mit

\[
\sum_r n_r=27,\qquad \sum_r n_r r_i r_j=G_{ij}.
\]

| Prüfungsstufe | Verbleibende Typen | Nachweis |
|---|---:|---|
| Alle einfachen Sechsknotengraphen bis auf Isomorphie | 156 | Vollständige Abdeckung aller 32.768 beschrifteten Graphen |
| Eintragsweise nichtnegative Gram-Matrix | 69 | 87 exakte Eintragswidersprüche |
| Zusätzlich positiv semidefinite Gram-Matrix | 44 | 25 weitere exakte negative Hauptminoren |
| Binäre Gram-Machbarkeit mit 27 Spalten | **26** | 18 rationale Separationszertifikate; 26 ganzzahlige Profilzeugen |

Für jedes gelieferte Zertifikat wurde unabhängig geprüft:

\[
y_0+\sum_{i\le j}y_{ij}r_i r_j\le0\quad\text{für alle 64 Profile},
\]

während für den ausgeschlossenen Typ eine geeignete Nummerierung

\[
27y_0+\sum_{i\le j}y_{ij}G_{ij}>0
\]

erfüllt. Summation über die 27 Spalten wäre ein Widerspruch. Nenner werden vollständig beseitigt; die Prüfung verwendet nur ganze Zahlen und rationale Arithmetik.

Die Typnummern beider Pakete wurden nicht ungeprüft gleichgesetzt. Der neue Prüfer untersucht die Umnummerierungen der Gram-Matrizen. Die Zertifikate schließen zusammen genau 18 der 44 Typen aus; die 26 unabhängig geprüften Profilzeugen decken disjunkt genau den Rest ab. Manche Separationsvektoren schließen unter verschiedenen Umnummerierungen mehrere Typen aus. Maßgeblich ist ihre Vereinigungsmenge.

In der bisherigen nullbasierten Projektzählung sind die 26 verbleibenden Indizes:

`0, 1, 2, 5, 8, 13, 22, 24, 26, 27, 39, 40, 41, 46, 51, 52, 64, 65, 71, 72, 75, 95, 96, 98, 121, 122`.

### Zusätzliche Untersuchung der Überlebenden

Die bereits entwickelte gewichtete Relaxation mit Typkantenanzahlen für `U=S_U+2L` wurde auf alle 26 Überlebenden angewandt. Alle 26 kontinuierlichen LPs wurden vom Solver als machbar gemeldet. Bei 14 konnten die Lösungen exakt als rationale Zeugen zurückgewonnen und gegen sämtliche Gleichungen und Schranken geprüft werden. Bei zwölf scheiterte die einfache Bruchrekonstruktion an der exakten Gleichheitsprüfung; sie werden ausschließlich als numerisch machbar geführt. Keiner der 14 neuen rationalen Zeugen ist ganzzahlig.

Daraus folgt **kein zusätzlicher Ausschluss**. Die vorliegenden zehn früheren ganzzahligen Aggregatzeugen bleiben gültig. Die Untersuchung zeigt insbesondere, dass die bisherige kontinuierliche Aggregation allein noch keinen überzeugenden Weg von 26 auf null liefert. Nächste Stufen müssen Ganzzahligkeit, Knotenrealisierung, konkrete L-Zyklen oder weitere notwendige Bedingungen ausnutzen.

Die 103 C4-freien Zyklentypen sind aus `src/breadth1/o3_generic_core.py` reproduzierbar: Partitionen von 27 mit Teilen mindestens 3, ohne Teil 4. Die Liste ist jetzt mitgeliefert. Bei Übernahme der zwei bereits im Projekt zertifizierten Typausschlüsse bleiben 101. Deren Zertifikate wurden in dieser Syntheserunde nicht erneut geprüft.

**Keine Multiplikation von Erfolgsquoten:** 26 Skeletttypen und 101 offene Zyklentypen beschreiben unterschiedliche Strukturmerkmale. Ihr kartesisches Produkt ist eine mögliche Organisation bedingter Modellinstanzen, keine gemessene Restgröße der vollständigen Graphsuche. Eine Prognose „Stunden bis Tage“ lässt sich nicht allein aus den f27-Laufzeiten ableiten.

## 4. K66: Domänenkritik beantwortet

Die relevante Identität lautet für eine Vierergruppe Q

\[
z_i^2-\sum_{j\in Q\setminus\{i\}}z_i z_j=4[\,z_i=2\,].
\]

Bei Gruppensumme 2 ist sie für `z_i∈{0,1,2}` korrekt. Die Reviewer-Warnung vor ihrer Anwendung auf beliebige Profile ist berechtigt. Die Schlussfolgerung, unsere konkrete K66-Anwendung sei deshalb zu verwerfen, war ohne Einsicht in deren Domänen jedoch nicht begründet.

| Wurzel | Geprüfte Profile | Gruppensummen in allen drei Vierergruppen |
|---|---:|---|
| v4_09322 | 654 | ausschließlich 2 |
| v4_09323 | 708 | ausschließlich 2 |
| v4_09332 | 724 | ausschließlich 2 |
| v4_09333 | 741 | ausschließlich 2 |

Insgesamt wurden 33.924 koordinatenweise Identitäten erneut exakt geprüft. Ein Gegenbeispiel mit Gruppensumme 1 liegt außerhalb dieser Eingabedomänen. Für eine einzelne Nullkoordinate gilt die Identität übrigens unabhängig von der Gruppensumme; die Formulierung „genau dann Gruppensumme 2“ benötigt eine passende Quantifizierung. Die allgemeineren Zählidentitäten `n₂=(t−s)/2` und `n₁=2s−t` sind korrekt. Sie ersetzen aber nicht ohne Weiteres den konkreten Nachweis einer Trägerhäufigkeit über verschiedene Profile.

Unverändert offen bleiben die Vollständigkeit der vorgelagerten Domänenreduktionen und sämtliche noch nicht abgeschlossenen Einzelzertifikate. Ein erfolgreicher algebraischer Domänentest schließt diese Lücken nicht. Die vier vorbereiteten Abdeckungen sind daher weiterhin als **bedingt auf Brücken- und Blattklauseln geprüft** zu führen.

## 5. Modulares Liftkriterium: bestätigte Reichweite

Ein exakter Quotient R ist eine zwingende Voraussetzung für die Verwendung des modularen Systems als vollständiges Liftkriterium. Das bestehende O3-ABC-Modell sucht den Quotienten; die Phasensuche nach [Lundle22](https://github.com/Lundle22/conway-99-cyclic-lifts/tree/eb2487672ed2d0852978fc483ef8a444291b617b) löst die nachgelagerte Aufgabe. Beide sind keine austauschbaren Kodierungen derselben Variablenmenge.

Eigene erneute End-to-end-Kontrollen:

* Für die beiden angegebenen freien C3-Wirkungen des Rook-Graphen auf neun Knoten wurden jeweils alle 27 Phasenbelegungen untersucht. Genau neun ergeben einen SRG; genau dieselben neun erfüllen das modulare System.
* Für den im Review angegebenen 4×4-Quotienten mit Zeilensumme 5 wurden alle 729 Phasenbelegungen untersucht. Zwei erfüllen das modulare System, aber keine ergibt einen SRG. Der Quotient ist nicht exakt; eine vollständige Gegeninstanz einschließlich Z und Liftmatrix ist gespeichert.

Damit ist die Domänengrenze konkret belegt. Die zusätzlichen Reviewer-Angaben zur vollständigen 34.157-Fälle-Enumeration und zur BvLS-Konstruktion wurden wegen der fehlenden Skripte nicht vollständig reproduziert. Sie werden nicht für die hier publizierten Schlussfolgerungen benötigt.

Die Idempotenz von `B=(R+I) mod 3` setzt bei exaktem Quotienten `k≡2 mod 3` voraus. Die Rook-Kontrolle mit k=4 validiert folglich das allgemeine modulare Kriterium, **nicht** die Conway-spezifische Bild/Kern-Zerlegung. Deren synthetische Kontrollen und algebraische Herleitung bleiben getrennt.

Falsch-positive modulare Nullen außerhalb exakter Quotienten widerlegen die Verwendung als hartes Kriterium. Sie beweisen für sich genommen weder statistische Nutzlosigkeit noch Nützlichkeit als Heuristik. Dazu fehlen kontrollierte Suchversuche.

## 6. Memetik und Cross-over: Übernahme mit zwei wesentlichen Korrekturen

Die Fehlerformel

\[
E'=E+A\Delta+\Delta A+\Delta^2+\Delta
\]

und die Ω-Margenerhaltung `PΔ=0` sind bestätigt. Die Identität `F=4(C₄−2079)` im λ-Arm war bereits im geprüften Projektstand dokumentiert. Sie ist kein zusätzlicher unabhängiger Fitnesskanal. Auch die ersten niedrigen spektralen Momente liefern dort keine neue Information; daraus folgt kein generelles Verbot höherer Spektraldiagnostik.

Unsere früheren Kostenmessungen bleiben maßgeblich: ungefähr 2,92–4,07-fache Beschleunigung der isolierten Bewertung, jedoch nur geringe erwartbare Gesamtwirkung bei dominierender Mutationserzeugung. Ein Kampagnenvorteil wurde nicht gemessen.

### 6.1 Was die Kerndimension tatsächlich beweist

Für ein fest ausgerichtetes Elternpaar und d Differenzkanten sei D das lineare Margensystem und `ν=d−rang(D)`. Es gilt `D·1=0`. Bei ν=1 sind nur die beiden Eltern zulässig. Ein Rang d−1 modulo einer Primzahl zusammen mit der bekannten Kernrichtung genügt für diesen exakten Schluss.

Bei ν≥2 folgt hingegen nicht allein aus der Dimension, dass echte Kinder existieren oder dass es genau `2^ν−2` gibt. Das erfordert zusätzlich eine nachgewiesene Basis aus disjunkten binären Blockindikatoren. Schon der allgemeine Kern der Matrix `[1,−2,1]` hat Dimension 2 und enthält den Einsvektor, aber seine einzigen binären Vektoren sind `000` und `111`. Dieses kleine Beispiel ist keine realisierte Ω-Gegeninstanz; es zeigt, warum der reine Dimensionsschluss logisch nicht ausreicht.

Solverfreie Blockrekombination ist deshalb nur nach Prüfung der konkreten Blockbasis korrekt. Ob alle relevanten Ω-Elternpaare eine solche Basis besitzen, bleibt offen. Die im Review genannte Verteilung von 120 Paaren, insbesondere „77 % ohne echtes Kind“, ist ohne Paarliste, Seeds und Rechenskripte nicht vollständig nachprüfbar. Sie wird nicht als eigene Messung übernommen. Auch „Rangtest deutlich billiger als CP-SAT“ bedarf eines Zeitvergleichs.

### 6.2 Ausrichtung: ein exaktes Gegenbeispiel

Für die Startpopulation desselben Basiscommits wurden die Eltern mit Indizes 0 und 25 untersucht:

| Darstellung desselben Graphpaars | Differenzkanten | Exakte Dimension des Margenkerns |
|---|---:|---:|
| Ursprüngliche Ausrichtung | 32 | 2 |
| Zweiter Elternteil relativ durch zulässigen Frame umnummeriert | 826 | 1 |

Die Dimension 2 ist durch rationale Kernbasis und modularen Rang gesichert; die Dimension 1 durch den Einsvektor und modularen Rang. Die konkrete Permutation ist gespeichert. Damit ist die behauptete Ausrichtungsunabhängigkeit widerlegt. In umgekehrter Richtung stellt die Rückausrichtung den zweidimensionalen Raum wieder her.

Gleichzeitige Umnummerierung beider Eltern und relative Umnummerierung nur eines Elternteils sind verschiedene Operationen. Die erste erhält die Aufgabe bis auf Koordinatenwechsel; die zweite kann sie verändern. 48 erfolglose Zufallsversuche beweisen keine Invarianz.

**Praktische Konsequenz:** Elternausrichtung bleibt ein legitimer Optimierungsansatz. Ob minimale Hamming-Distanz, Kerndimension, nachgewiesene Blockzahl oder erwartete Reparaturkosten die bessere Zielgröße liefern, muss gemessen werden. Ein Erfolg beliebiger Zufallsausrichtung wird nicht behauptet.

## 7. Literatur, Reimbayev und vollständige Symmetrie

Die im Forschungsbericht nachgetragene [Ishida-Arbeit vom Juli, §8.4](https://arxiv.org/html/2606.29183v2) bleibt in der Prioritätsbewertung zu berücksichtigen. Sie liefert bereits einen algebraischen Zugang zu τ=6 für freie Ordnung 3. Der Review hat diesen Literaturstrang nicht vollständig überprüft und ersetzt unsere Quellenprüfung insoweit nicht.

Mit den im Forschungsbericht belegten Literaturrestriktionen bleiben zum vollständigen Ausschluss nichttrivialer Symmetrie die freie C3-Wirkung mit τ=6 und die Involution mit einem Fixpunkt. K66 ist ein eigener Nachvollzugs- und Zertifizierungsstrang eines bereits literaturseitig ausgeschlossenen Fixdreiecksfalls. Die Zahl 26 beendet weder die C3-Suche noch den Involutionsfall.

Bei Reimbayev ist der eigene Befund stärker als die unvollständige Reviewer-Auslesung: Alle 208 Gleichungen stimmen zwischen HTML-LaTeX, MathML und Original-TeX überein; ihre Summe bei `(99,14)` ist um **94.034.160** zu klein. Dieser Befund wurde bereits mit einem funktionierenden Download- und Prüfskript reproduziert. Die konkrete fehlerhafte Einzelherleitung bleibt unlokalisiert.

Die vom Reviewer aus einer Teilmenge der Formeln abgeleitete Bedingung `4 | z₁₁` ist zunächst nur eine Konsequenz jener ungeklärten Formeln. Sie wird ohne unabhängige kombinatorische Herleitung nicht als neue notwendige Graphbedingung veröffentlicht. Eine passende Gesamtsumme am Neunknoten-Kontrollpunkt bestätigt keine individuellen Siebenknotenformeln.

## 8. Bereinigter Folgeplan

1. **τ=6:** Die 26 zertifizierten Gram-Typen als vorgeschalteten Filter übernehmen. Danach eine ausdrücklich stärkere Ganzzahl-/Realisierungsaufgabe mit konkretem L-Typ untersuchen. Der vorliegende LP-Pilot hat keinen weiteren Typ ausgeschlossen. Erst an Stichproben der tatsächlich stärkeren Modelle Laufzeiten kalibrieren.
2. **K66:** Den Nebenlauf einschließlich Komposition abschließen lassen; dann den strukturierten Ersatz anhand gemessener Brücken-/Blattkosten bewerten. Weder aus Skelettzahlen noch aus Baumtiefe eine globale ETA ableiten.
3. **Memetik:** Zulässige Mutationserzeugung profilieren und verbessern. Cross-over-Rangvorprüfung und nachgewiesene Blockrekombination gegen den bestehenden CP-Weg messen. Relative Ausrichtung als variable Entscheidung beibehalten.
4. **Reimbayev:** Erst eine unabhängige Einzelherleitung kann einen Tabellenfilter freigeben. Die Summendifferenz ist ein gesicherter Fehlerhinweis, keine automatisch bekannte Reparatur.

Zwei Testanforderungen aus dem Review werden korrigiert: Ein früher ausgeschlossener vollständiger Graphfall muss in einer schwächeren Relaxation nicht unzulässig sein. Umgekehrt muss ein Gram-Zeuge nicht alle stärkeren Quotientenbedingungen erfüllen. Positive und negative Kontrollen müssen stets dieselbe Modellstufe betreffen.

Auch eine erfolglose lange Zufallssuche beweist keine Unzusammenhängendheit des Mutationsraums. Dafür wäre eine erhaltene trennende Invariante oder eine vollständige Erreichbarkeitsanalyse nötig. Höherer Matrixrang eines einzelnen Moves beweist nicht, dass er keine Folge kleinerer Moves besitzt.

**Veröffentlichungsfazit:** Der verlässlichste neue gemeinsame Ertrag ist die exakte 26-Typen-Kette mit unabhängigem Prüfer. Hinzu kommen eine geklärte K66-Domäne, bestätigte Liftkontrollen und eine konkrete Korrektur der Cross-over-Ausrichtungsbehauptung. Der nächste Recheneinsatz sollte diese konkreten Ergebnisse nutzen; ein vollständiger Symmetriebeweis oder ein bereits überlegener memetischer Algorithmus wäre eine Überinterpretation.
