# Maverick: Änderungen am Suchraum statt weiterer Laufzeit

Stand 29.09.2026. Grundlage: Modell/Verifier der Reparatur 1.2.0, AGENTS, EXPERIMENT_RULES, GLOBAL_CONCLUSIONS (GC-08/10/11) und `docs/memetik/lambda_profile_20260927/endpoints/ABGLEICH_UND_NEUAUSRICHTUNG.md`. Laufbefunde 1.2.0 stammen aus dem übergebenen Ergebnisstand; dieser Beitrag ist keine weitere unabhängige Kampagnenprüfung. Die Vorschläge sind neue überprüfbare Arbeitsrichtungen für dieses Projekt, keine Behauptungen weltweiter Originalität; vor Freigabe ist Literatur-/Altversuchsabgleich nötig.

## Diagnose, die ich infrage stelle

W≈2076 bedeutet nicht, dass wir einem Zielgraphen in einer bekannten Metrik nahe sind. Etwa die Hälfte der Nichtkantenbedingungen ist verletzt. 24 nichtisomorphe Gründer aus wenigen Herkunftslinien sind außerdem kein Beleg für globale Vielfalt. Die 88 Optimalitätsmeldungen gelten für einzelne feste Fenster, nicht für deren überlappende Folge oder die gesamte λ-Komponente. Die 51 Zeitlimits sind offen. Das Experiment rechtfertigt eine neue Mechanismushypothese, keinen Ausschluss der λ-Suche.

### 1. Priorität: Reparatur an Dreiecksblöcken einschließlich Schnittstelle

**Hypothese:** Das Einfrieren aller Kanten über die Fenstergrenze sperrt entscheidende kollektive Bewegungen. Im aktuellen Modell sind nur Kanten mit beiden Enden im Fenster variabel. Mehr interne Vertices allein muss diese Sperre nicht wirtschaftlich lösen.

Jeder 14-reguläre λ=1-Graph zerfällt in 231 eindeutige Dreiecke, sieben je Knoten. Man kann ihn als linearen 3-uniformen, 7-regulären Hypergraphen darstellen. Seine Inzidenzstruktur darf weder 4-Zyklen (doppelt belegtes Knotenpaar) noch 6-Zyklen (zusätzliche Dreiecke aus drei Blöcken) enthalten. Diese Bedingungen sind exakt: Die Clique-Expansion liefert dann einen 14-regulären λ=1-Graphen.

**Vorschlag:** Nicht ein induziertes Knotenfenster freigeben, sondern eine zusammenhängende Menge alter Dreiecke entfernen und aus deren Knotenvorkommen neue Dreiecke bilden. Jeder Knoten erhält exakt so viele neue Blockinzidenzen, wie entfernt wurden. Zulässigkeit und Zielfunktion stets am vollständigen Graphen kontrollieren. Die ausgewählten Dreiecke dürfen die bisherige Fenstergrenze überqueren; damit können die bisherigen Kreuzkanten ausdrücklich geändert werden. Es geht um gemeinsam gelöste Blockänderungen, nicht um die bloße Wiederholung eines kleinen bekannten Trades.

**Aussagekräftiger erster Test:** Auf denselben 24 Gründern gepaart interne Fenster und Blockfreigabe vergleichen. Aus 12, 24 und 48 entfernten Dreiecken jeweils mehrere vorab fixierte zusammenhängende Ausschnitte erzeugen. Zuerst reine Mobilitätsfrage lösen: Existiert überhaupt eine andere zulässige λ-Belegung, die nicht nur umbenannt ist? Danach erst W optimieren. Begrenzte mechanistische Vorstufe: höchstens 12 CPU-h insgesamt, Aufgaben in großzügigen Einzelbudgets; bei offenen Fällen keine Starrheitsaussage. Bei hinreichender Mobilität eigener breiter Suchpilot.

**Messgrößen:** Zahl veränderbarer Kreuzkanten, alternative λ-Lösungen, kanonische Distanz/Duplikate, W-/L1-Änderung und vollständige Bau-/Such-CPU. Vorteil ist nur belegt, wenn erfolgreiche Reparaturen oder bessere Endpunkte je Gesamt-CPU entstehen. Neue Graphklassen allein sind sekundär.

**Risiko:** Dies kann vorhandenen P-/Triangle-Trade-Katalogen nahekommen; deshalb expliziter Katalogabgleich und Messung, ob neue gemeinsame Endpunkte erreichbar sind. Die 6-Zyklusbedingungen können das Modell wiederum starr machen. Ein negativer Mobilitätstest wäre trotzdem informativer als ein weiterer unanalysierter 2h-Timeout.

### 2. Zweite Priorität: Kontrollierte Ausflüge aus λ=1 mit messbarer Rückkehrchance

**Hypothese:** Der zulässige λ-Raum ist unter unseren tatsächlich implementierten Zügen ungünstig verbunden; eine kurze Passage durch wenige λ-Verletzungen kann günstigere Rückkehrpunkte erschließen. Das ist eine Hypothese über Operatoren, keine Behauptung, der vollständige λ-Raum sei unzusammenhängend.

**Vorschlag:** Grad14 und Einfachheit stets exakt halten (z.B. allgemeine 2-Switches). Vorübergehend höchstens q verletzte Kantenbedingungen zulassen, mit q aus einer kleinen vorab fixierten Staffel, etwa 2, 4, 8. Die λ-Schuld ist eine eigene Kennzahl und kein still geändertes Endziel. Nach einer festen Ausflugsphase gemeinschaftlich auf λ=1 zurückreparieren; nur vollständig geprüfte λ-Graphen kommen in die Ergebnisbank. Den genauen Verletzungszähler und gegebenenfalls die gesamte Residuenmasse getrennt protokollieren.

**Test:** Auf 24 gepaarten Gründern je vier Replikate mit identischem Gesamtbudget gegen λ-erhaltende Kicks antreten lassen. Als erste Freigabe 24 CPU-h insgesamt: ausreichend zur Messung von Rückkehrrate, Rückkehr zum selben Minimum und Endpunktqualität, kein Konvergenzversuch. Jede Rückreparatur-CPU zählt zum Arm. Vorher anhand bekannter kleiner Zielgraphen zeigen, dass die Rückkehrprüfung keine ungültigen Punkte akzeptiert.

**Entscheidung:** Nur wenn ein Arm bei gleicher CPU brauchbare Rückkehrhäufigkeit und systematisch bessere validierte Endpunkte zeigt, lohnt Skalierung. Sonst droht genau das bekannte Muster: Flucht gelingt, Abstieg vernichtet den Vorteil. Die frühere ω-Linie und größere Kicks sind relevante Gegenbelege, deshalb muss dieser gezielte Mechanismus von ihnen unterschieden werden; 'λ weicher machen' allein wäre keine neue Idee.

### 3. Hoher Forschungswert, höheres Risiko: Konstruktion als diskreter Rang-54-Projektor

**Hypothese:** Eine globale kontinuierliche Darstellung eröffnet Bewegungen, die kantenlokale Operatoren kaum erzeugen. Dies ist eine Alternative für die Gründererzeugung, kein nachgewiesen besserer Solver.

Für einen Zielgraphen gilt A²+A=12I+2J. Auf dem Raum senkrecht zum Einsvektor sind die Eigenwerte 3 und −4 mit Vielfachheiten 54 und 44. Folglich ist

    E = (A + 4I − (2/11)J)/7

orthogonaler Projektor vom Rang54 mit E1=0, Diagonale6/11 und Offdiagonale9/77 an Kanten bzw. −2/77 an Nichtkanten. Umgekehrt liefert jede solche Matrix durch A=7E−4I+(2/11)J einen Zielgraphen. Die rationale Rechnung einschließlich Rang und Diagonale wurde mit Python/Fraction geprüft. Dies ist eine exakte Umformulierung, keine zusätzliche Existenzannahme.

**Vorschlag:** Zwei Mengen abwechselnd annähern: (i) Rang54-Projektoren in 1⊥; (ii) symmetrische diskrete Matrizen mit genau den beiden Offdiagonalwerten, korrekter Diagonale und Grad14. Für die diskrete Projektion ist ein 14-reguläres gewichtetes Graphproblem zu lösen; unabhängiges Runden je Zeile ist unzulässig. Aus Zwischenständen entstehen neue Gründer, deren λ-Verletzungen danach ausdrücklich repariert werden müssen. Mehrere Startfamilien, darunter wirklich neue Projektoren, gegen die jetzigen Gründer testen. Projektionsresiduum, W und tatsächliche λ-Fehler stets getrennt berichten.

**Billiger Test mit hohem Informationsgehalt:** Zunächst auf einem bekannten kleinen SRG, etwa dem 3×3-Rookgraphen mit (9,4,1,2), die algebraische Rückabbildung und Wiederherstellung gestörter Lösungen testen. Danach bis zu 99-Knoten-Größen nur kurze Konstruktionstests aus zwei Dutzend Seeds, zusammen höchstens 12 CPU-h. Erfolgskriterium ist die Produktion unabhängig geprüfter λ-Gründer mit neuartigen kanonischen/strukturellen Merkmalen und konkurrenzfähiger Qualität; kleines kontinuierliches Residuum allein genügt nicht.

**Risiken:** Nichtkonvexe Projektionszyklen, teure diskrete Projektion, erneute λ-Reparaturbarriere. Die spektrale Residuenenergie ist eng mit dem schon bekannten quadratischen Residuenmaß F verbunden; bloß F umzubenennen wäre wertlos. Neu wäre hier die globale Projektorbewegung samt anderer Gründererzeugung. Ein positiver Kleingraphentest beweist keinerlei Aussicht auf Conway99.

## Entscheidungsempfehlung

Zuerst Option1 als Untersuchung des eingefrorenen Randes, anschließend je nach Befund Option2. Option3 parallel als kleiner Methodenprototyp mit harten Validitätskontrollen, nicht sofort als neuer Nachtlauf. Keine weitere reine Budgetverdopplung der gleichen 144 Fenster. Vor Start jede Hypothese, Vergleichsarm, Gesamtbudget und Akzeptanzregel fixieren; tolerante Zeitabrechnung und strenge Mathematik beibehalten (GC-02/08/10/11).
