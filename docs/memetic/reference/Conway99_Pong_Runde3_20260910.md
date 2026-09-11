# Conway 99 — Pong, Runde 3

Stand: 10. September 2026. Antwort auf `Conway99_Auswertung_Pong2_und_Ping3_20260910.md` und auf den Zusatz zum vereinbarten Entwurf. Rechnungen sind Prüfrechnungen; keine Suchsoftware, kein Eingriff in den laufenden Zertifizierungsauftrag.

Statuskonvention: **Geprüft — Herleitung / Rechnung / Quelle**, **Hypothese**, **Offen**.

## 0. Kurzfassung

1. Das Prisma-Lemma und F = 16(k−4) sind korrekt; ich habe sie unabhängig kombinatorisch bewiesen (nicht über Spuren) und erhalte zusätzlich die vollständige Defektsignatur des Apex-Nachbarn einer Lösung. Numerisch bestätigt am BvLS-Graphen (eigene Konstruktion aus dem ternären Golay-Code): 8910 Prismen, F = W = 288.
2. Der nächste λ-erhaltende Operator, die 3-Rotation (drei Dreiecke, Apexdreieck, Basen paarweise gematcht), ist aus der BvLS-Lösung ebenfalls zulässig: F = W = 432 = 24(k−4) in allen 40 geprüften Fällen. Für Conway 99 hieße das: Apex-Nachbarn einer Lösung bei F = 160, 3-Rotations-Nachbarn bei F = 240.
3. Vier Aussagen aus Pong 2 werden zurückgenommen oder eingeschränkt (Abschnitt 1).
4. Der vereinbarte Entwurf hat drei strukturelle Barrieren, die sich mit vorhandenen Zahlen quantifizieren lassen: den Rückweg als besten Zug, den Aufwärtsdrift langer Folgen und die Gleichheitsakzeptanz als Kopierkanal. Alle drei sind mit kleinen Änderungen behebbar (Abschnitt 7). Diversität ist nur über umnummerierungsinvariante Größen messbar; ich schlage ein konkretes Maßsystem und Erhaltungsregeln vor (Abschnitt 8).

## 1. Korrekturen an Pong 2

- **Graver-Folgerung.** Zurückgenommen. Eine primitive Elterndifferenz D schließt nur Ω-Pfade innerhalb des Kastens [min(H₁,H₂), max(H₁,H₂)] aus; Pfade dürfen den Kasten verlassen. Das Matching-Gegenbeispiel {12,34,56} → {23,14,56} → {23,45,16} ist korrekt. Richtige Aussage: Teildifferenz-Kinder existieren genau dann, wenn D nicht primitiv ist; das ist eine Aussage über direkte Rekombination, nicht über Verbindbarkeit.
- **Zensusumfang.** Eingeschränkt auf die gezählten Produktfamilien 4×4, 4×6, 6×6 mit disjunkten Trägern. Nicht gezählt: 4×8, Summen überlappender Vorlagen, allgemeine NBNᵀ (Abschnitt 4).
- **„10⁻² bis 10⁻³“ und „≈ 100 Züge“.** Nicht gemessen; die Schwelle ist eine Versuchskonvention.
- **„200 s ohne Symmetrie“.** Kein Beweis einer Mindestzeit; symmetrische Ω-Zustände erfüllen das freie Modell. Die 14 Nachfahren des ℤ₁₄-Zustands bilden einen Orbit unter der Rahmentranslation und sind daher paarweise isomorph als gewurzelte Strukturen; sie liefern eine neue Klasse, nicht vierzehn.
- Technik: Prüfsummen künftig über Dateibytes; `in_omega` in `omega_sym.py` prüft keine Binärität (in `omega_check.py` enthalten). F als primärer Vergleichswert, W und Residuenverteilung zusätzlich — einverstanden.

## 2. Prüfauftrag 1 — Apex-Zielzugang

### 2.1 Lemma und F = 16(k−4). Geprüft — Herleitung (unabhängig) und Rechnung.

Sei G ein SRG mit λ = 1, μ = 2, Grad k; Dreiecke abc, def; Tausch → abd, cef. Zwischen disjunkten Dreiecken liegen wegen λ = 1 nur Matchingkanten. Vor dem Tausch hat das nichtadjazente Paar (a,d) genau zwei gemeinsame Nachbarn; b scheidet aus (bd wird neu), also müssen beide in {c, e, f} liegen: cd ∈ E und genau eine von ae, af. Dasselbe für (b,d) erzwingt die dritte Matchingkante. Umgekehrt genügt das Prisma. ✓

Fehlerwert direkt gezählt statt über Spuren. Mit R_v := N(v) minus die sechs Prismenknoten (|R_v| = k−3) gilt: R_a, R_b, R_c, R_d, R_e, R_f sind paarweise disjunkt bis auf genau drei Knoten w_ae ∈ R_a∩R_e, w_bf ∈ R_b∩R_f, w_cd ∈ R_c∩R_d (die dritten Dreiecksknoten der Matchingkanten). Die Änderung der gemeinsamen Nachbarzahl ist ±1 genau für die Paare

- (c, R_a∪R_b) −1, (c, R_e∪R_f) +1, (d, R_a∪R_b) +1, (d, R_e∪R_f) −1,
- (a, R_c), (b, R_c) −1; (a, R_d), (b, R_d) +1; (e, R_c), (f, R_c) +1; (e, R_d), (f, R_d) −1,

jeweils ohne die drei w-Knoten (deren Beiträge sich aufheben); alle Paare innerhalb des Prismas und alle Paare ohne Prismenknoten bleiben korrekt, alle Kanten behalten λ = 1. Das sind 16 Gruppen zu je k−4 Paaren mit Residuum ±1, also **F = W = 16(k−4)**. Unabhängig von den sechs Spurwerten des Pings; deren Endergebnis ist damit bestätigt.

**Defektsignatur (Prisma-Signatur).** Der Defektgraph (falsche Paare) ist bipartit: sechs Naben c, d mit Defektgrad 4(k−4) und a, b, e, f mit 2(k−4); außen 4(k−4) Knoten mit Grad 2 und 2(k−4) Knoten mit Grad 4; alle Residuen ±1. Für k = 14: Naben 40, 40, 20, 20, 20, 20; außen 40 Knoten Grad 2, 20 Knoten Grad 4; W = F = 160. **Rechnung am BvLS-Apex-Nachbarn (k = 22): Profil {2: 72, 4: 36, 36: 4, 72: 2}, Residuen {−1, +1}** — exakt die Formel. Nutzen: Jeder lokal lineare Zustand mit W = F = 160 und diesem Profil ist genau einen Apex-Tausch von einer Lösung entfernt; die beiden Naben vom Grad 40 sind die zu tauschenden Spitzen. Das ist ein billiger Archiv-Trigger.

### 2.2 BvLS als Kontrolle. Geprüft — Rechnung.

Eigene Konstruktion: zyklischer ternärer Golay-Code [11,6,5] mit g = x⁵+x⁴−x³+x²−1, Syndromgraph auf F₃⁵ mit 22 Erzeugern; SRG-Gleichung A² + A = 20I + 2J elementweise bestätigt. 891 Dreiecke, **8910 Prismen, also 26 730 zulässige Apex-Tausche aus der Lösung**; ein Tausch liefert lokal linear, F = W = 288. Die Lösung ist in dieser Familie also nicht isoliert, sondern extrem gut angebunden — eine heuristische Zufallsschätzung hätte etwa 470 Prismen ergeben; die Cayley-Struktur liefert das Zwanzigfache. Für Conway 99 ist daraus nichts zu folgern; die Zahl zeigt aber, dass „isoliert unter Apex“ eine starke, nicht die naheliegende Annahme wäre.

### 2.3 Ist ein Prisma erzwungen? Offen, mit exakter Umformung.

Für eine Kante cd mit Dreieck cdw seien X = N(c)∖{d,w}, Y = N(d)∖{c,w} (je 12 Knoten). Aus μ = 2 folgt: die Kanten zwischen X und Y bilden ein perfektes Matching φ (jedes y ∈ Y hat mit c genau die gemeinsamen Nachbarn d und φ(y)); w hat keine Nachbarn in X ∪ Y. Prismen über cd sind genau die gemeinsamen Kanten der beiden perfekten Matchings M_c (Dreiecke an c) und φ(M_d) auf X. Also

    #Prismen = (1/3) · Σ_{cd ∈ E} |M_c ∩ φ_cd(M_d)|.

Zwei perfekte Matchings auf 12 Punkten können kantendisjunkt sein; ein Zählargument, das Prismen erzwingt, sehe ich nicht. Heuristische Erwartung ≈ 693·(6/11)/3 ≈ 126. Ob der Prismenzähler in arXiv:2508.03377 zu den parameterbestimmten oder zu den freien Sechsknotenzählern gehört, wäre die entscheidende Nachfrage an den Peer-Reviewer, der die Arbeit gelesen hat.

### 2.4 Nächster Operator: 3-Rotation. Geprüft — Rechnung (BvLS), Herleitung für die Zulässigkeit.

Dreiecke T_i = {a_i, x_i, y_i}, i = 1,2,3, Tausch → {a₂,x₁,y₁}, {a₃,x₂,y₂}, {a₁,x₃,y₃} (9 Knoten, 12 Paare). Aus einer Lösung heraus zulässig genau dann, wenn (Herleitung wie beim Prisma über μ = 2 für jede neue Kante) **a₁a₂a₃ ein Dreieck ist und aufeinanderfolgende Basen {x_i,y_i}, {x_{i+1},y_{i+1}} perfekt gematcht sind**. BvLS: 8910 solche Konfigurationen; alle 40 geprüften Tausche bleiben lokal linear mit **F = W = 432 = 24(k−4)**.

**Hypothese.** Eine m-Rotation aus einer Lösung liefert F = W = 8m(k−4) mit Residuen ±1; für k = 14: 160, 240, 320, … Das gibt eine Leiter von Zielabständen, an der sich Kandidaten einordnen lassen: Ein Zustand bei F = 240 mit 3-Rotations-Signatur wäre zwei Ebenen unter der Lösung.

Folgerung zur Zielzugänglichkeit: Falls ein hypothetischer Conway-Graph kein Prisma hätte, wäre er unter Apex isoliert, aber die 3-Rotation bräuchte nur ein Dreieck mit paarweise gematchten Nachbarbasen — ebenfalls nicht erzwungen, aber eine unabhängige zweite Zugangsmöglichkeit. Beide Operatoren zusammen in der Zugfamilie zu führen, ist billig (die 3-Rotation ist die Vereinigung zweier überlappender Apex-Muster).

## 3. Prüfauftrag 2 — Lokale Minima

Befund akzeptiert: HoG ist striktes lokales Minimum unter Apex (46 Nachbarn, bester +20), H₋ und der ℤ₁₄-Zustand unter den Produktfamilien. Empfohlene begrenzte Operationen, in dieser Reihenfolge, jede mit Kontrolle:

1. **Erschöpfende Tiefe 2 und 3 ab HoG** (≈ 46·50 bzw. ≈ 10⁵ Zustände, Dedup über kanonische Form). Ergebnis: existiert ein Zustand mit F < 2836 in Tiefe ≤ 3? Das misst die Barrierenbreite direkt und kostet Minuten. Kontrolle: keine nötig, es ist eine Messung.
2. **Kick-und-Abstieg statt reiner Zugfolge**: L zufällige zulässige Züge, danach gieriger Abstieg mit Rückwegsperre bis Stagnation, Übernahme des besten besuchten Zustands, falls ≤ F₀. Kontrolle: derselbe CPU-Aufwand als gleichverteilter Lauf (wie der 100-Schritt-Lauf) und als reiner Abstieg. Messgrößen: Anteil der Läufe mit F < 2836, bester F, Zahl verschiedener kanonischer Zustände unter 2836.
3. **Exakte Mehrdreiecksreparatur (LNS)**: Fenster = Vereinigung von m Dreiecken (m ≈ 6–10, 18–30 Knoten); alle Paare im Fenster frei, außerhalb fest; Bedingungen lokal linear und Grad 14; Ziel: Zahl der Vierecke mit mindestens einem Fensterknoten minimieren (CP-SAT mit Hilfsvariablen für gemeinsame Nachbarn). Das ist der „λ-erhaltende Mehrdreieckstausch“ in vollständiger Form. Messgrößen: Anteil der Fenster mit strikter Verbesserung, ΔF-Verteilung, Solversekunden je Fenster. Kontrolle: Kick-und-Abstieg bei gleicher CPU.
4. Für Ω dasselbe Fenstermodell mit Ω-Bedingungen; Zielfunktion dort über W im Fenster (linear) statt F (quadratisch), F nur zur Bewertung.

## 4. Prüfauftrag 3 — Zensusumfang

Präzisierte Aussage: In H₋ und im ℤ₁₄-Zustand gibt es keine anwendbaren Änderungen der Form xyᵀ + yxᵀ mit disjunkten Trägern der Größen 4×6 und 6×6. Nicht abgedeckt:

- **Zerfallende Produkte** sind bereits abgedeckt: Ist supp x unzusammenhängend im Labelgraphen (x = x₁ + x₂), so zerfällt Δ in Δ₁ + Δ₂ auf disjunkten Paarmengen; Anwendbarkeit und Ω-Erhaltung gelten stückweise. 4×(4+4) ist also im 4×4-Zensus enthalten.
- **Nicht abgedeckt, echt neu:** (a) Summen zweier 4×4-Vorlagen mit überlappenden Trägern, bei denen sich Einträge zu 0 aufheben — einzeln unanwendbar, gemeinsam anwendbar (die algebraische Form einer Ausstoßkette); (b) zusammenhängende Träger-8-Vektoren (alternierende 8-Zyklen, zwei 4-Zyklen mit gemeinsamem Label) als Faktor; (c) NBNᵀ mit dim K ≥ 3 und überlappenden Trägern.
- Vollständigkeit der 16-Paar-Klassifikation als Produktform folgt aus dem Satz (dim K = 2 erzwingt Produktform); für ≥ 24 Paare nicht.

**Entscheidungsrelevant** ist kein weiterer Familienzensus, sondern die Frage, ob auf den alten guten Ω-Zuständen **verbessernde** Ω-Änderungen beliebiger Form innerhalb eines Fensters existieren: Fenster-SAT mit Zielfunktion (W im Fenster) über alle 6-Label-Fenster. Anteil der Fenster mit strikter Verbesserung > 0 ändert die Entscheidung zugunsten von Ω; Anteil 0 über alle Fenster und alle acht Komponenten spricht endgültig für weiche Kopplung.

## 5. Prüfauftrag 4 — Graver und Austritte

Korrektur siehe Abschnitt 1. Austrittstest präzise: (1) Fenster wählen; (2) Ω-Zustand mit mindestens einem abweichenden Eintrag im Fenster suchen; (3) Ergebnis kanonisieren (gewurzelter, gefärbter 99-Graph, nauty/Traces) und mit der kanonischen Menge **aller** Komponentenzustände vergleichen; (4) liegt es in der Komponente, den beschrifteten Zustand per Blockierklausel ausschließen und wiederholen; (5) Abbruch nach N Wiederholungen. Ausgeschlossen wird nach Kanonisierung, nicht über die 645 120 Rahmenbilder je Zustand. UNSAT für alle 6-Label-Fenster schließt Änderungen in diesen Fenstern aus, nichts darüber hinaus.

## 6. Prüfauftrag 5 — Bestand

Ohne Dateien keine Aussage. Vorgeschlagenes Austauschformat, damit alle Skripte unverändert laufen: `H.npy` (84×84, 0/1) plus `meta.json` mit Labelkonvention (Partner i ↔ i+7 oder Permutation), `outer`-Liste, Wurzel, Scoredefinition, Seed, Programmversion; alternativ der 99-Knoten-Graph als graph6 mit Wurzelangabe.

## 7. Der vereinbarte Entwurf — Barrieren der Endpunkt-Selektion

Der Entwurf ist eine iterierte lokale Suche mit Better-or-Equal-Akzeptanz auf Populationsebene (Lourenço–Martin–Stützle 2003). Seine Stärke ist die Einfachheit der Garantie: Bestwert je Linie monoton, Archiv unverlierbar. Seine Barrieren:

**B1 Rückweg-Barriere (Geprüft — Herleitung; Messung vorgeschlagen).** Nach einem verschlechternden Zug ist dessen Umkehrung typischerweise der beste verfügbare Zug. Jede innerhalb der Folge auch nur leicht abwärts gerichtete Schrittwahl kollabiert deshalb zu Hin-und-Zurück; rein zufällige Folgen vermeiden das (Rückwegwahrscheinlichkeit ≈ 1/Zugzahl, im HoG-Lauf 2 von 100), bezahlen aber mit B2. Abhilfe: Rückwegsperre (Tabu auf den letzten m Zügen). Messung an HoG: für jeden der 46 Nachbarn prüfen, ob die Umkehrung der einzige verbessernde Zug ist.

**B2 Drift-Barriere (Geprüft — Rechnung am HoG-Lauf des Pings).** Gleichverteilte Züge erhöhen F im Mittel um ≈ 22 je Schritt (2836 → 5088 in 100 Schritten). Die Wahrscheinlichkeit, dass eine zufällige Folge der Länge L bei ≤ F₀ endet, fällt mit L (näherungsweise Φ(−μ√L/σ) für Mittel μ > 0 und Streuung σ der Zuggewinne). **„Längere Folgen bei Stagnation“ senkt die Übernahmewahrscheinlichkeit, statt sie zu erhöhen**, solange die Schritte ungeführt sind. Abhilfe: Folge = Kick (L zufällige Züge) + Abstieg mit Rückwegsperre; oder Schrittwahl mit begrenztem ΔF (Metropolis bei fester Temperatur). Messung: μ und σ der ΔF-Verteilung aller zulässigen Züge entlang des Laufs; daraus die Übernahmewahrscheinlichkeit je L.

**B3 Endpunkt statt Bestpunkt.** Ein Zustand mit F < F₀ in Schritt j < L geht verloren, wenn die Folge höher endet. Da alle Zwischenzustände zulässig sind, sollte der beste besuchte Zustand übernommen werden; inkrementelles ΔF macht das kostenfrei.

**B4 Gleichheitsakzeptanz als Kopierkanal.** „Gleich gut“ umfasst Elternkopien (Rückwegzyklen) und Plateauduplikate. Ohne Dedup über kanonische Form füllt sich die Population mit Kopien, und die globale Auswahl verstärkt das. Regel: gleich gute Endpunkte nur, wenn kanonisch neu; getrennt zählen als „neutral und neu“.

**B5 Ratschen-Barriere.** Linienweise monotone Akzeptanz überquert nur Barrieren, deren Überquerung innerhalb einer Folge wieder auf ≤ F₀ zurückführt. Barrierenbreite messbar über Tiefe-2/3-Nachbarschaften (Abschnitt 3.1). Ist die Breite größer als die praktisch übernahmefähige Folgenlänge, hilft nur exakte Reparatur (LNS) oder Populationsakzeptanz mit begrenzter Verschlechterung (Metropolis auf Endpunkten, ILS-„LSMC“).

**B6 Mindestnachbarschaft.** Bei 3–14 Zügen je Zustand (Ω-Produktfamilien) sind Folgen fast nur Rückwege; bei 30–73 (Apex ab HoG) sind sie sinnvoll. Vor jedem Lauf: Median der Zugzahl je Zustand messen.

**B7 Sekundärkriterium.** Bei vielen gleich guten Endpunkten entscheidet ohne Regel der Zufall; die Auswahl braucht ein zweites Kriterium (Neuheit im Deskriptorraum), sonst driftet die Population zu Duplikaten.

Alle sieben sind mit Rückwegsperre, Bestpunktübernahme, kanonischem Dedup, Kick-und-Abstieg und einem Sekundärkriterium behebbar, ohne die vereinbarten Garantien (monotone Linien, unverlierbares Archiv) aufzugeben.

## 8. Echte Diversität messen und erhalten

**Identität.** Kanonische Form des ungewurzelten 99-Graphen (nauty/Traces; für Ω zusätzlich gewurzelt und gefärbt), Kosten Millisekunden. Schlüssel für Population, Archiv und Endpunktannahme. Kennzahl: Zahl verschiedener Klassen.

**Abstand (umnummerierungsinvariant).** Deskriptorvektor je Zustand: sortiertes Spektrum (99 Werte), Residuenhistogramm (Anzahlen von −2, −1, +1, +2, …), Gradprofil des Defektgraphen, Zahl der Vierecke (bei λ = 1 ist F = 4(#C₄ − 2079)), Fünfecke, Sechsecke, λ- und μ-Fehler getrennt. Abstand euklidisch auf standardisierten Deskriptoren. Warnung: Pseudometrik (kospektrale, gleich profilierte Zustände fallen zusammen); für Identität nur die kanonische Form.

**Innerhalb einer Linie** ist der beschriftete Hamming-Abstand gültig, weil Züge nicht umnummerieren; zwischen Familien ist er bedeutungslos.

**Basin-Diversität (empfohlene Hauptgröße).** Von jedem Populationsmitglied ein fester kurzer Abstieg (gleiches Budget), Ergebnis kanonisieren; die Zahl verschiedener Ergebnisse ist die wirksame Diversität. Zwei Mitglieder mit demselben Abstiegsziel sind redundant, auch wenn ihre Deskriptoren verschieden sind.

**Populationskennzahlen je Generation.** Verschiedene kanonische Klassen; mittlerer paarweiser Deskriptorabstand; effektive Linienzahl (Hill-Zahl der Linienanteile); Zellabdeckung in einem Deskriptorgitter (z. B. F × Vierecküberschuss × maximaler Defektgrad); Basin-Diversität alle g Generationen.

**Erhaltung.** (1) Dedup über kanonische Form; (2) feste Quoten je Startfamilie (Inseln, seltene Migration); (3) Ersetzung des ähnlichsten Mitglieds derselben Nische statt des schlechtesten global (Mahfoud 1995); (4) Neuheitsschwelle für Aufnahme; (5) Bestarchiv je Deskriptorzelle statt nur global (MAP-Elites, Mouret–Clune 2015) — das verallgemeinert das unverlierbare Bestarchiv und schützt auch schlechtere, aber strukturell andere Zustände; (6) Linien ohne Verbesserung über g Generationen durch frische Starts derselben Familie ersetzen.

**Prisma-Trigger im Archiv.** Jeder lokal lineare Zustand mit W = F = 160 wird sofort auf die Signatur aus 2.1 geprüft; Treffer werden direkt in den Apex-Tausch überführt und validiert.

## 9. Dateien

- `bvls.py`: Konstruktion des BvLS-Graphen aus dem Golay-Code, SRG-Prüfung, Dreiecke, Prismenzählung, Apex-Tausch mit F, 3-Rotations-Suche mit Vorfilter und Validierung.
- Zustände und Skripte aus Pong 2 unverändert gültig.

## 10. Fünf Punkte für das nächste Ping

1. Tiefe-2/3-Nachbarschaft ab HoG unter Apex (Dedup kanonisch): gibt es F < 2836 in Tiefe ≤ 3? Und: Ist für die 46 Nachbarn die Umkehrung jeweils der einzige verbessernde Zug (B1)?
2. ΔF-Verteilung aller zulässigen Züge entlang des 100-Schritt-Laufs (Mittel, Streuung, Anteil ΔF ≤ 0) — daraus die Übernahmewahrscheinlichkeit je Folgenlänge (B2).
3. Prismenzähler in arXiv:2508.03377: parameterbestimmt oder frei?
4. Fenster-SAT mit Zielfunktion W auf einem Zustand jeder der acht Komponenten: Anteil der 6-Label-Fenster mit strikter Verbesserung (Abschnitt 4).
5. Bestand im Austauschformat aus Abschnitt 6; ohne ihn bleibt der Vergleich mit dem alten Projektstand unmöglich.
