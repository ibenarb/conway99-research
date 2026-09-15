# Conway99: geprüfte Startgraphen — Codex, 15. September 2026

## 7.1 Zusammenfassung

**Zehn tatsächlich erzeugte, selbst geprüfte, paarweise nichtisomorphe Kandidaten: fünf Ω und fünf λ.**
KI-Kennung: **OpenAI Codex**; eine verlässlich auslesbare feinere Modell-/Buildkennung ist in dieser Arbeitsumgebung nicht verfügbar.
Eigene Prüfung ersetzt keine spätere unabhängige Abnahme.

Repositoryzugriff bestand auf den Zweig `memetik`, fixiert auf Commit
`bb43b0ab4fad36e142832923b83dcf3f6a186652`. Alle vier vorgegebenen Referenzdateien wurden vollständig gelesen.
Der öffentliche Bestand enthält inzwischen auch angenommene Gemini-/Claude-Graphen.
Das private vollständige Pilot-Roharchiv wurde nicht beschafft; ein vollständiger Altbestandsvergleich wird nicht behauptet.

Ausführung: Linux x86_64, AMD EPYC 9V74, Python 3.12.14. Generatorabhängigkeiten:
NumPy 2.3.5, NetworkX 3.6.1, OR-Tools 9.15.6755.
Zusatzprüfung: pynauty 2.8.8.1 mit nauty2_8_8.
Jeder Solverlauf verwendete **einen Worker**; höchstens vier Erzeugerprozesse wurden zugleich gestartet.
Die dokumentierten Speicherwerte sind Prozess-Spitzen, keine WSL-Gesamtspeichermessung.
Die tatsächlich erfolgreichen Konstruktionen benötigen hier jeweils weniger als 106 MiB Prozess-RSS und weniger als 0,25 Sekunden eigentliche Erzeugungszeit.
Python-Start und Modulimporte kommen hinzu. Es wird keine identische Laufzeit auf dem Office-PC zugesagt; die Konfiguration ist für vier Kerne und etwa 5 GiB RAM geeignet.

**Wichtigster Qualitätsbefund:** C02 erreicht im Ω-Arm
**W=2074, L1=2506, F=3472, L∞=4, Nmax=6**.
Damit unterbietet er die im abgeschlossenen Office-Pilot berichteten Ω-Bestwerte W=2110, L1=2718, F=3926.
Das ist ein Vergleich mit diesen dokumentierten Referenzwerten, kein Anspruch auf eine unbekannte aktuelle Gesamt- oder Weltbestmarke.
Die Ω-L∞-Bestmarke 3 wird nicht verbessert.
Quelle: [Office-Pilot-Auswertung am geprüften Commit](https://github.com/ibenarb/conway99-research/blob/bb43b0ab4fad36e142832923b83dcf3f6a186652/docs/memetik/OFFICE_PILOT_001_AUSWERTUNG_20260913.md).

Untersucht wurden **drei Konstruktionsprinzipien**: freie Ω-Margenergänzung,
Vierpunkt-Blocküberlagerung und zyklisches Dreieckssystem. Letzteres hat zwei explizit verwandte Varianten F03/F04.
Vier Familienkennungen bedeuten deshalb **nicht vier unabhängige Prinzipien**.
Erfolgreiche Kandidaten stammen aus zwei dieser Prinzipien; die freie Ergänzung blieb in den begrenzten Läufen ohne Treffer.
Alle drei verlangten Suchrichtungen sind vertreten: kombinatorisch, algebraisch sowie constraint-basiert/randomisiert.

Es gab **14 primäre Erzeugungsaufrufe: zehn erfolgreiche und vier zeitbegrenzte UNKNOWN-Ergebnisse**.
Zusätzlich wurden die zehn erfolgreichen Erzeugungen mit dem eingebetteten endgültigen Generator wiederholt;
alle zehn graph6-Zeichenfolgen wurden byteidentisch reproduziert.
Kein erzeugter Kandidat fiel bei der Zulässigkeitsprüfung durch.
Drei weitere Ideen werden in 7.8 nur vorgeschlagen, ohne Code oder Ergebnisbehauptung.

Alle zehn Graphen sind zusammenhängend. Exakte nauty-Zertifikate zeigen keine Duplikate
innerhalb der Einreichung oder unter den **26 verfügbaren .g6-Dateien mit 18 unterschiedlichen Graph6-Bytefolgen**.
Die fünf benannten Ω- und fünf benannten λ-Gründer sowie die verfügbaren angenommenen KI-Kandidaten sind darin enthalten.
ZIP-Inhalte, andere Datenformate, historische Commits und das private Roharchiv sind nicht vollständig erfasst.

| Kandidat | Familie | Arm | W | L1 | F | L∞ | Nmax | λ-fehlerhafte Kanten |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C01 | F02 | omega | 2114 | 2724 | 4098 | 5 | 2 | 240 |
| C02 | F02 | omega | 2074 | 2506 | 3472 | 4 | 6 | 239 |
| C03 | F02 | omega | 2153 | 2692 | 3900 | 4 | 3 | 253 |
| C04 | F02 | omega | 2105 | 2572 | 3612 | 4 | 4 | 258 |
| C05 | F02 | omega | 2215 | 2766 | 3994 | 4 | 5 | 258 |
| C06 | F03 | lambda | 2244 | 3828 | 8184 | 4 | 198 | 0 |
| C07 | F03 | lambda | 2772 | 4488 | 8976 | 4 | 132 | 0 |
| C08 | F04 | lambda | 2673 | 3498 | 5412 | 3 | 132 | 0 |
| C09 | F04 | lambda | 2871 | 3828 | 6072 | 4 | 33 | 0 |
| C10 | F04 | lambda | 2739 | 3696 | 5940 | 4 | 33 | 0 |

## 7.2 Konstruktionsfamilien

### F01 — Freie Ω-Margenergänzung

Richtung: constraint-basiert/randomisiert. Ziel: Ω.
Für jedes ungeordnete Außenknotenpaar wird eine Boolesche Variable angelegt:
3486 Variablen, Symmetrie durch gemeinsame Variable, Diagonale null.
Es werden ausschließlich Grad 12 und sämtliche 1176 Einträge von
PH=2J−(C+I)P gefordert. Der Grad folgt auch aus dem Aufsummieren der PH-Gleichungen,
wird zur Kontrolle und Propagation redundant aufgenommen.
Weder λ noch μ noch ein Spektrum oder eine Fehlerschranke werden hinzugefügt.

Die erste Suchvariante verwendet eine zufällige lineare Hilfszielfunktion auf H-Kanten und beendet sich beim ersten zulässigen Treffer.
Das ist keine der drei Qualitätsselektionen und würde keine optimale Lösung der Hilfszielfunktion garantieren.
Die weiteren Varianten verwenden ein reines Erfüllbarkeitsmodell, randomisierte Verzweigungen und ausgeschaltete LP-Linearisierung.
Drei Versuche, kein Treffer: Seed 101 mit Hilfsziel/60 Sekunden; Seeds 102 und 103 ohne Hilfsziel/je 120 Sekunden.
Alle Status UNKNOWN. Keine Unmöglichkeitsaussage.

Diese Formulierung ergibt sich direkt aus dem Auftrag und entspricht auf Prinzipienebene auch Geminis bereits vorhandener Ω-CSP-Konstruktion.
Sie wird **nicht als gegenüber Gemini neue Methode** ausgegeben.
Kein Gründergraph und keine Graphdatei wird eingelesen; keine erzwungene Zusatzsymmetrie.
Quelle zum Projektvergleich: [Gemini-Generator](https://github.com/ibenarb/conway99-research/blob/bb43b0ab4fad36e142832923b83dcf3f6a186652/data/memetik/ai_candidates/submissions/20260914_gemini_v01/generator.py).

### F02 — Vierpunktfasern über dem Knesergraphen KG(7,2)

Richtung: kombinatorische Blockkonstruktion / algebraische Überlagerung, vervollständigt durch CP-SAT. Ziel: Ω.
Dies ist die erfolgreiche Ω-Familie, mit fünf Seeds als **Varianten derselben Familie**.

Schreibe jedes Nachbarlabel eindeutig als (i,s), mit i∈{0,…,6}, s∈{0,1} und Label i+7s.
Jedes Außenpaar hat zwei unterschiedliche Gruppen i,j. Die vier Bitkombinationen bilden
eine Faser B_{ij} mit vier Knoten. Es gibt 21 Fasern.

1. In jeder Faser wird das Quadrat C4 gesetzt: zwei Außenpaare sind verbunden, wenn genau ein Bit wechselt.
2. Zwischen Fasern mit genau einer gemeinsamen Gruppe gibt es keine H-Kanten.
3. Zwischen Fasern mit disjunkten Gruppenträgern wird ein beliebiges perfektes Matching gewählt.
   Diese Faserpaare sind genau die Kanten des Knesergraphen KG(7,2).
4. Für jeden Außenknoten x und jede der fünf nicht in seinem Träger liegenden Gruppen k
   müssen unter den vier Matchingnachbarn, deren Träger k enthält, genau zwei das Bit 0 und zwei das Bit 1 tragen.

**Beweis der harten Ω-Bedingungen.** Jeder Faserträger hat zehn disjunkte Zweierträger.
Daher erhält x zwei innere Quadratnachbarn und zehn Matchingnachbarn, also H-Grad 12.
Die beiden Quadratnachbarn enthalten jedes der vier Labels aus den beiden eigenen Partnergruppen genau einmal.
Das entspricht dort RHS=1.
Jede übrige Gruppe liegt in vier disjunkten Zweierträgern; Bedingung 4 verteilt ihre Inzidenzen auf beide Labels mit Häufigkeit zwei.
Das entspricht dort RHS=2. Somit gilt PH=2J−(C+I)P exakt.
Symmetrie und Einfachheit folgen aus ungerichteten Quadraten und Matchings.
Der feste Rahmen ergänzt jeden Außenknoten um zwei P-Kanten auf Grad 14.

Der Generator modelliert 1680 freie Boolesche Kanten zwischen disjunkten Fasern,
fixiert die übrigen H-Einträge und erzwingt Matching- sowie PH-Gleichungen.
H hat 84 innere Quadratkanten und 420 Matchingkanten, insgesamt 504.
Der Teilgraph aus den Matchingkanten ist eine vierblättrige Überlagerung von KG(7,2);
H selbst enthält zusätzlich die inneren Quadrate.
Die Matchingpermutationen bleiben frei, soweit die Bitbilanzen erfüllt sind.
Ein globaler Decktransformations- oder Bitflip-Automorphismus wird **nicht** vorausgesetzt.

Alle fünf erzeugten vollständigen Graphen besitzen laut nauty Automorphismengruppenordnung 1.
Blockstruktur ist hier also nicht mit globaler Graphsymmetrie gleichzusetzen.
Erzwungene Struktur ist die angegebene Faserzerlegung, keine transitive Gruppenwirkung.

Sechs primäre Versuche: Seed 201 mit Hilfsziel nach 60 Sekunden UNKNOWN;
Seeds 202–206 ohne Hilfsziel sämtlich erfolgreich.
Die fünf ersten erfolgreichen Lösungen wurden unverändert aufgenommen:
keine W-, F- oder L∞-Optimierung, keine Auswahl aus einer verschwiegenen größeren Stichprobe.
Die zusätzlichen Seeds 205/206 dienen der Replikation und Variation innerhalb der Familie, nicht einer Erhöhung der Prinzipienzahl.

Die Konstruktion wurde hier aus dem kanonischen Paarrahmen hergeleitet.
Es gibt keine Abstammung von bekannten Gründergraphen.
Eine Literatur-Neuheit des Bauprinzips oder ein großer Mutationsabstand zum Altbestand wird nicht behauptet.

### F03 — Progressionsfreie Mengen und zyklische Dreiecke

Richtung: additive Kombinatorik / zyklische Überlagerung, randomisierte Auswahl. Ziel: λ.
Knoten sind (p,x) mit p∈{0,1,2}, x∈Z33; graph6-Label 33p+x.
Für eine Menge D⊂Z33 mit |D|=7 werden die 231 Tripel

T(x,d)={(0,x),(1,x+d),(2,x+2d)}

zu Dreiecken ergänzt. D muss die Eigenschaft haben:
d_i+d_j=2d_k impliziert i=j=k.
Es werden auch wiederholte Indizes geprüft; alle Rechnungen erfolgen modulo 33.

**Beweis.** Zwischen jedem Paar von Farbklassen bilden die sieben Verschiebungen sieben unterschiedliche perfekte Matchings;
2 ist modulo 33 invertierbar. Daher hat jeder Knoten sieben Nachbarn in jeder anderen Klasse, insgesamt 14.
Ein zusätzliches Dreieck müsste Verschiebungen mit d_i+d_j=2d_k verwenden;
die Progressionsfreiheit erzwingt das ursprüngliche Tripel. Jede Kante liegt deshalb in genau einem Dreieck.
Einfachheit und Schleifenfreiheit folgen aus den drei getrennten Klassen.

Der Generator durchsucht eine zufällig permutierte Liste der 33 möglichen Verschiebungen gierig,
prüft jede Erweiterung vollständig und startet bei Bedarf neu.
Zwei Primärversuche, Seeds 301 und 302; beide bereits im ersten Greedy-Durchlauf erfolgreich.
Ein Seed ist kein zusätzliches Prinzip.

Erzwungen sind eine semireguläre Z33-Translation und eine Dreifärbung mit drei gleich großen Klassen.
Zusätzlich erhält die Abbildung
(0,x)↦(2,−x), (1,x)↦(1,−x), (2,x)↦(0,−x)
die Dreiecke. In beiden Exemplaren hat die vollständige Automorphismengruppe Ordnung 66 und zwei Knotenbahnen.
Die Wahl von D bleibt frei unter der Progressionsbedingung.
Keine bekannten Graphen werden als Eltern verwendet. Kein Anspruch auf eine neue Literaturkonstruktion.

### F04 — Freie zyklische Dreiecksmatchings

Richtung: algebraisch / kombinatorisch mit randomisierter Konfliktprüfung. Ziel: λ.
Dies ist eine **Verallgemeinerung von F03 im selben Dreieckslift-Prinzip**, kein vierter unabhängiger Grundansatz.

Ersetze (d,2d) durch sieben Paare (a_i,b_i)∈Z33² und setze

T(x,i)={(0,x),(1,x+a_i),(2,x+b_i)}.

Die a_i, b_i und b_i−a_i müssen jeweils paarweise verschieden sein.
Zusätzlich muss für alle i,j,k gelten:

a_i+(b_j−a_j)=b_k genau dann, wenn i=j=k.

Die drei Verschiebungslisten garantieren Grad 14; die letzte Bedingung verhindert exakt die zusätzlichen Dreiecke.
Damit gilt derselbe direkte λ-Beweis wie in F03, ohne eine Progressionsmenge oder b_i=2a_i vorzuschreiben.
Der Generator durchsucht die 1089 Offsetpaare in Seed-Reihenfolge mit vollständiger Konfliktprüfung.
Drei Primärversuche, Seeds 401–403; alle im ersten Greedy-Durchlauf erfolgreich.

Die Z33-Translation bleibt erzwungen. Ein Farbaustausch wird nicht erzwungen.
Die vollständigen Automorphismengruppen der drei Exemplare haben jeweils Ordnung 33 und drei Knotenbahnen.
Kein bekannter Gründer ist ein Elter. Mehr Freiheitsgrade als F03 bedeuten keine bewiesene größere Einzugsgebietsvielfalt.

**Gemeinsame Einschränkung von F03/F04.**
Die drei unabhängigen 33er-Klassen verhindern eine exakte Conway-Lösung, solange diese Struktur erhalten bleibt.
Dies lässt sich ohne Spektralannahme zählen:
Für eine feste Klasse U enthalten die 66 äußeren Knoten jeweils sieben Nachbarn in U.
Somit ist

Σ_{ {u,v}⊂U } |N(u)∩N(v)| = 66·binom(7,2) = 1386.

Bei global μ=2 müsste die Summe hingegen 2·binom(33,2)=1056 sein.
Die Differenz ist 330 je Klasse. Diese Familien sind zulässige Näherungsstarts,
aber eine erfolgreiche Fortsetzung muss die erzwungene gleichmäßige Dreiklassenstruktur verlassen.
Mutationen sind später ausschließlich an die λ-Bedingungen zu binden, nicht an die Lift-Schablone.
Das Portfolio beansprucht keine λ-Qualitätsverbesserung gegenüber HoG 57338.

### Gemessene Kosten der primären Aufrufe

Wall/CPU umfassen Modellaufbau bzw. Greedy-Suche und Matrixaufbau ab dem internen Messpunkt nach den Importen, nicht Python-Start, Importe, graph6-Serialisierung oder Dateischreiben. Peak-RSS ist der gesamte Prozesshöchstwert unter Linux.

| Aufruf | Ergebnis | Wall s | CPU s | Peak MiB |
| --- | --- | ---: | ---: | ---: |
| free101 + Hilfsziel | UNKNOWN | 60.061591 | 60.046602 | 143.559 |
| free102 | UNKNOWN | 120.050968 | 120.026587 | 191.297 |
| free103 | UNKNOWN | 120.065771 | 120.019304 | 171.758 |
| cover201 + Hilfsziel | UNKNOWN | 60.072748 | 60.027196 | 109.340 |
| cover202 | Graph | 0.176039 | 0.175401 | 105.098 |
| cover203 | Graph | 0.241205 | 0.240986 | 103.988 |
| cover204 | Graph | 0.212594 | 0.211474 | 105.047 |
| cover205 | Graph | 0.208134 | 0.208145 | 104.902 |
| cover206 | Graph | 0.211326 | 0.211142 | 103.883 |
| ap301 | Graph | 0.000610 | 0.000609 | 90.602 |
| ap302 | Graph | 0.000523 | 0.000521 | 91.043 |
| offset401 | Graph | 0.001414 | 0.001412 | 90.895 |
| offset402 | Graph | 0.001430 | 0.001428 | 90.340 |
| offset403 | Graph | 0.001816 | 0.001814 | 91.047 |

## 7.3 Maschinenlesbare Kandidaten

Der folgende Block ist der **einzige JSON-Codeblock** dieses Dokuments.
Alle Scores beziehen sich auf sämtliche 4851 ungeordneten Paare im vollständigen Graphen.
Die nachgewiesen falsche λ-Bedingung bei Ω-Kandidaten ist korrekt als false ausgewiesen;
sie verletzt den Ω-Vertrag nicht.

```json
{
    "schema_version": "conway99-candidates-1.0",
    "submission_id": "Codex_2026-09-15",
    "candidates": [
        {
            "candidate_id": "C01",
            "family_id": "F02",
            "arm": "omega",
            "status": "self_verified",
            "graph6": "~?@bsaCCB?gC_P?`?__OGB??S?@G?AG?AC?@@??OCCA?OOG?__O?__O?OOG?CC@_??DI??A_c?K?@C?GO@A?AG?__O??GA?gC@?G@AOC?OG__G?Q?G_G?G_OOB??E??og??IP?C_?CIO?P??B?c?`?O??Q?__I?_??OCB?D?_C?`G?_S?_Ac??OOA?E?_O?_B??COC`_A_?G_K@_@G?@ICA??P?G?_A?OACA_A??@?GGO?_@_??OCa?A?OK?OAO@I?AA?G?b?AC?W_@_?AGIGOC?I?A_?SS?a?c?O?W@?c_@C?I@??BP?@ACO?OC?Q??_`?EO??O??GAH?_AG?@_@?K@A?GO?A?B??ECOAOK?_D?A?g@??O?OC_CGC?g@G??AGC_?DGA??G?`C_??S@O???CCo?O?@@?_??ODAA@??Q?O_?W?G?`?Qa?OC?S@A?OGA?CG_?H?Q@_?_A??P?AGo??CA@?c@??Ob?C_??@A?C?@@Q?G?O_A?C??@_?_@?@_B@h?O@O?OAGC?D?q_G?c?C?QK?OB?GC?G_?_AgO?P?HS?@A?AO_?gGDC?o?CC?D_AC?O?HO??E?@OC?O?j?E@@?D?OGA@CA@CGAO?AO?K?`OE?OA?_??a@C?CD?cAQ@???CI?_?S?o??AOI??K?BA_?_CGOE??g?S?`?S?_aACI_???Q?KH??PO@@?OGO?Gd??I?C@O_?aO_?@_I?GOQ?_GoG????I?o_G?_AGOb?G???cAOa@O?CGOA?A???oD?S?`B?CA_??@??gAOK?IQ?AOAG????K`?CcG??g?__GA?",
            "graph6_sha256": "aea4dbb26be9a1507fa12144c38f2bc889c529e8719a09227a862455562a3eef",
            "seed": "202",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "cover",
                "--seed",
                "202",
                "--seconds",
                "120",
                "--out",
                "C01_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": false,
                "omega_frame_condition": true
            },
            "scores": {
                "W": 2114,
                "L1": 2724,
                "F": 4098,
                "Linf": 5,
                "Nmax": 2,
                "lambda_bad_edges": 240,
                "residual_histogram": {
                    "-2": 225,
                    "-1": 912,
                    "0": 2737,
                    "1": 656,
                    "2": 268,
                    "3": 44,
                    "4": 7,
                    "5": 2
                }
            },
            "omega_frame": {
                "canonical_to_graph6": [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    53,
                    54,
                    55,
                    56,
                    57,
                    58,
                    59,
                    60,
                    61,
                    62,
                    63,
                    64,
                    65,
                    66,
                    67,
                    68,
                    69,
                    70,
                    71,
                    72,
                    73,
                    74,
                    75,
                    76,
                    77,
                    78,
                    79,
                    80,
                    81,
                    82,
                    83,
                    84,
                    85,
                    86,
                    87,
                    88,
                    89,
                    90,
                    91,
                    92,
                    93,
                    94,
                    95,
                    96,
                    97,
                    98
                ]
            },
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.17603932000201894,
                "cpu_seconds": 0.17540136100000003,
                "peak_rss_mib": 105.09765625,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Vierpunktfasern mit C4 und perfekten Matchings ueber KG(7,2); keine Normoptimierung."
        },
        {
            "candidate_id": "C02",
            "family_id": "F02",
            "arm": "omega",
            "status": "self_verified",
            "graph6": "~?@bsaCCB?gC_P?`?__OGB??S?@G?AG?AC?@@??OCCA?OOG?__O?__O?OOG?CC@_??II?A?_c?G?`C?@G@A?CA?__O??GA@GC@?GE?OC?O`?_G?OAG_G?GO_OB??Q?_Og??HB?C_D?A??P?OAA??`?O?AO?__C@_??OC?`?`_C?_S?aC?_A@C?IOA?Cg??o_B??SC?OAA_?g?DC_@G?H?COH?P?G?GAG_AC?GQ?C@?GG?Ab?_??OC_AA?EC?OA?P`?GA?G?w?A??O_@_?EE??GG?I?a??CS?W?c?O?Q?CcG@C?@P?@_@G@AD???c??O?__D?S@?o??GAH??QI?@_@?I?QC?ACA?B??E?K`A?@?D?A?G`G?@A?C_GCC?c?C?OAGA?`_G?WA??`AC@?OOO?A?CCO@B??Gg_??OE@A??C@Oo_?W?GCAG??_oS?SB??O?COD???H?A`_?_O??I?AGCA?go@???O?O`ACG?G?Q?g?@@GOK??OO?c??@_?_@??YG?w?_@O?OCACCO?g?_?c?C@A@GOW?C??G_?c?a?AH?CH?@A?AOGa?G@CB??CC?D?`AOA??O??E?O_C?OCIGA@@?D?AGA@AA@OaA??AOK??`CCGO??K??aS??C@C_?A?oG?CGB??Y??OW_OC??KP??C?_C?X@CS??S@AOA?`?A?gD?_?Q?gGO?ODG@E????Ga@?g?DAO??__o?@a?GC`??_GgO_???I_CA??gAS?_AK???cAQ_?O?CGKA@????s@?CG_A?CAg?A@??gD?aGOO?A?AQ?O??Ko?EAO?_??__KA?",
            "graph6_sha256": "7f4ff150f5b49c6acde3222b30a952eea7b4fa70f6f62c45771bc0c5a0ea41d7",
            "seed": "203",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "cover",
                "--seed",
                "203",
                "--seconds",
                "120",
                "--out",
                "C02_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": false,
                "omega_frame_condition": true
            },
            "scores": {
                "W": 2074,
                "L1": 2506,
                "F": 3472,
                "Linf": 4,
                "Nmax": 6,
                "lambda_bad_edges": 239,
                "residual_histogram": {
                    "-2": 138,
                    "-1": 977,
                    "0": 2777,
                    "1": 710,
                    "2": 210,
                    "3": 33,
                    "4": 6
                }
            },
            "omega_frame": {
                "canonical_to_graph6": [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    53,
                    54,
                    55,
                    56,
                    57,
                    58,
                    59,
                    60,
                    61,
                    62,
                    63,
                    64,
                    65,
                    66,
                    67,
                    68,
                    69,
                    70,
                    71,
                    72,
                    73,
                    74,
                    75,
                    76,
                    77,
                    78,
                    79,
                    80,
                    81,
                    82,
                    83,
                    84,
                    85,
                    86,
                    87,
                    88,
                    89,
                    90,
                    91,
                    92,
                    93,
                    94,
                    95,
                    96,
                    97,
                    98
                ]
            },
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.24120503299855045,
                "cpu_seconds": 0.24098638100000003,
                "peak_rss_mib": 103.98828125,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Vierpunktfasern mit C4 und perfekten Matchings ueber KG(7,2); keine Normoptimierung."
        },
        {
            "candidate_id": "C03",
            "family_id": "F02",
            "arm": "omega",
            "status": "self_verified",
            "graph6": "~?@bsaCCB?gC_P?`?__OGB??S?@G?AG?AC?@@??OCCA?OOG?__O?__O?OOG?CC@_??HI??Q?c??@`C?D?@A??E?__O??GA?gC@?GOCOC?Og?_G?OB?_G?J??OB??I??og?H?B?C_?C`O?P??E?c?`?O?K??__GA_??OCO_?@_C?_?Y_C?_Ac??OOA?CW@?O_B??AGG`OA_AC?SC?@G?OIC?@?P?G?K??oAC?gA?@_?GG?Ad?_??OC@A?aOK?OA_C_?CA?G?w?A?G?_@_CA?A?PD?I?OG?T??A?c?OB?C???@CA@@??G?W@ACO??S?I??__I?W?PO??GAH?_AG?@_@?GCQCAGOA?B?OGO?_?AE?D?A?_OGCGO?C_W?C?@@?I?AGC_G@G??I??`?_H?PCO???CC?H@_D@O_??OC?oCaGP??_?W?GA?aO?S_??S?o?O?cc??A?H?a?`?_G?CG?AGA_?gC`?g???OcA?_?QDA?C?@@K?K??_?@C??@_?_@??gKO`_G@O?OAGC@C?og??c?C@OGCO@K???G_?_?oWOH?GH?@A?A?a`?PCC@O?CC?C@c@G?KGO??E?O_C?OCIGC@@?D??WAE?A?D?AS?AOD??_@k?OO?C??a?D?Cg?K?Q?b??CGB??WA?T?_O???KA@A_?_C?OF??_?S?g?S?_BAKC??O?Q?H@G?SOG@A_???Go@A??CPE?G_@??@e?C????_GW`AAG?I@O@GAGAI?a?????c@O_QG?C?SAO????qCAOG???CAGH_@??hOCG?_A?AOA?@Q??KQ?B?QA_C?__C??",
            "graph6_sha256": "66d52edd767625ced6e1b5ebf5d6005f6a5d7c1bafac282a2f2f1b3bee38ba90",
            "seed": "204",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "cover",
                "--seed",
                "204",
                "--seconds",
                "120",
                "--out",
                "C03_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": false,
                "omega_frame_condition": true
            },
            "scores": {
                "W": 2153,
                "L1": 2692,
                "F": 3900,
                "Linf": 4,
                "Nmax": 3,
                "lambda_bad_edges": 253,
                "residual_histogram": {
                    "-2": 177,
                    "-1": 992,
                    "0": 2698,
                    "1": 684,
                    "2": 241,
                    "3": 56,
                    "4": 3
                }
            },
            "omega_frame": {
                "canonical_to_graph6": [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    53,
                    54,
                    55,
                    56,
                    57,
                    58,
                    59,
                    60,
                    61,
                    62,
                    63,
                    64,
                    65,
                    66,
                    67,
                    68,
                    69,
                    70,
                    71,
                    72,
                    73,
                    74,
                    75,
                    76,
                    77,
                    78,
                    79,
                    80,
                    81,
                    82,
                    83,
                    84,
                    85,
                    86,
                    87,
                    88,
                    89,
                    90,
                    91,
                    92,
                    93,
                    94,
                    95,
                    96,
                    97,
                    98
                ]
            },
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.21259398400070495,
                "cpu_seconds": 0.21147373599999997,
                "peak_rss_mib": 105.046875,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Vierpunktfasern mit C4 und perfekten Matchings ueber KG(7,2); keine Normoptimierung."
        },
        {
            "candidate_id": "C04",
            "family_id": "F02",
            "arm": "omega",
            "status": "self_verified",
            "graph6": "~?@bsaCCB?gC_P?`?__OGB??S?@G?AG?AC?@@??OCCA?OOG?__O?__O?OOG?CC@_??HI???Wc??`@C??W@A?OC?__O??GA@_C@?GACOC?P_?_G?Og?_G?GQ?OB?AC??Gg?A@E?C_?gAG?P?D??g?`?O?GO?__?E_??OCA@?E_C?`C??s?_A_GG?OA?CAPO?_B?A?OG_OA_?A`G@O@G@GAO???P?G?ACOGAC?aA??E?GG?QD?_??OCA@c?CC?OA@_?acA?G?q??COG_@_@G?AWO??I?G_c?@?O?c?OB??_C?@C?AH?G@C?@AC@A?C?O??__B?AG`O??GA_GA?CHG_@?IO?IA?CQ?B?Q??C?oW?_D?A?A_?gWS?C_?DC@C?@B?AGC?`CGA?C??`E?C???O@_?CCO_O_@?@_??OCAa_?OO_?_?W?G?B?Q`?OE?S?`?OA_O_O??HA?__?_OG?H?AG?a?cC`?c@??O_AQCGA?A?S?@@?IG_P?AAC??@_?_@?`@C_@?O@O?OOCC?@oG???c?CC@P?O?@GK?G_?__WA?P?@K?@A?A_H??@BCB??CC?CQ?EH?E?O??E?W?C?OCGF??C?DAG?AC?A?CHGE?AOG_?`_CGO??G_?aW??CG?GGQC???CH?O?OI_@?EOO??K@?a_?_CCG@C?_?S@A@O?`_A?g??o?Q?c?Q?PCS@?@G??Ga@?E?CIO?Oa_??@cG?OA@?_G_?Oc??IC@AG?gAO?_EC???c@Oc@G?CGOA?A???oAKG@?E?CAO?@@??k@??_oP?AGAAO???L_?BC???g?_oCA?",
            "graph6_sha256": "1216da8016e7cda285d56ba43573aa443ffa48899c2b2d122ce2c9d8b301ff90",
            "seed": "205",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "cover",
                "--seed",
                "205",
                "--seconds",
                "120",
                "--out",
                "C04_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": false,
                "omega_frame_condition": true
            },
            "scores": {
                "W": 2105,
                "L1": 2572,
                "F": 3612,
                "Linf": 4,
                "Nmax": 4,
                "lambda_bad_edges": 258,
                "residual_histogram": {
                    "-2": 139,
                    "-1": 1008,
                    "0": 2746,
                    "1": 679,
                    "2": 234,
                    "3": 41,
                    "4": 4
                }
            },
            "omega_frame": {
                "canonical_to_graph6": [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    53,
                    54,
                    55,
                    56,
                    57,
                    58,
                    59,
                    60,
                    61,
                    62,
                    63,
                    64,
                    65,
                    66,
                    67,
                    68,
                    69,
                    70,
                    71,
                    72,
                    73,
                    74,
                    75,
                    76,
                    77,
                    78,
                    79,
                    80,
                    81,
                    82,
                    83,
                    84,
                    85,
                    86,
                    87,
                    88,
                    89,
                    90,
                    91,
                    92,
                    93,
                    94,
                    95,
                    96,
                    97,
                    98
                ]
            },
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.20813420900230994,
                "cpu_seconds": 0.208144587,
                "peak_rss_mib": 104.90234375,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Vierpunktfasern mit C4 und perfekten Matchings ueber KG(7,2); keine Normoptimierung."
        },
        {
            "candidate_id": "C05",
            "family_id": "F02",
            "arm": "omega",
            "status": "self_verified",
            "graph6": "~?@bsaCCB?gC_P?`?__OGB??S?@G?AG?AC?@@??OCCA?OOG?__O?__O?OOG?CC@_??KI??A_c??`@C?O@@A?GO?__O??GA@OC@?GC@OC?OG__G?Og?_G?I?OOB?A?G?Gg??`COC_@_?I?P?OAG??`?O?GC?__@A_??OCA_?c_C?`OAOC?_A?HAGOA?CI?_O_B??IC?_@A_?_GKC_@GA?G_AO?P?G?GCAGACAOA??A?GG@AB?_??OCO@D?OC?OA@_?IIA?G?aOOC?G_@_?BAO?W?GI??go??OG?c?O?AK@?G@CB?@?A?@?@AC?O?S?CO?_aG?G?gO??GAG@@_K?O_@?IO?gG?AA?B??Q?KAaO@?D?A?o?GC?O?C_?WC@G?@I?AG?oC@G?o?_?`A?cO??OA_?CC`??B?H?_??OE_?_?I@?__?W?GC@G?ACOO?S?o?OE?C_???H??gS?_H?o??AGQ?C_?`?G_??O`A?AaOOA???@@I??o_?AAC??@_?_@??sG_?_o@O?O?WC?BP?Y??c?CA@S?O?GGC?G_?_o?PI@?G??@A?AAO`?DCC?O?CC?DA@A?_SAO??E?_GC?OG_BA?I?D?GOA?`A@OI@??AO@C?c_G?OOAC??aGC?C@`?PA?AG?CG@_?Ogo?C_O???K?OcA?_C?QDGO??S@G@C?_PAC_G?O?Q_CO??S??PC`@O?Ge??K?CAO?OaGO?@_COCOa?_GPg????I_OG??gA?Oe?c???c@OCPG?CWOA?????qCCA??D?CAW@?@??k?OC?gCOAWA?O???K@b?A??_C?_qC??",
            "graph6_sha256": "349576854d497b44ac25f57d0250c8892d687c9db8a7b14461524ab169a4f35c",
            "seed": "206",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "cover",
                "--seed",
                "206",
                "--seconds",
                "120",
                "--out",
                "C05_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": false,
                "omega_frame_condition": true
            },
            "scores": {
                "W": 2215,
                "L1": 2766,
                "F": 3994,
                "Linf": 4,
                "Nmax": 5,
                "lambda_bad_edges": 258,
                "residual_histogram": {
                    "-2": 200,
                    "-1": 983,
                    "0": 2636,
                    "1": 739,
                    "2": 240,
                    "3": 48,
                    "4": 5
                }
            },
            "omega_frame": {
                "canonical_to_graph6": [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    53,
                    54,
                    55,
                    56,
                    57,
                    58,
                    59,
                    60,
                    61,
                    62,
                    63,
                    64,
                    65,
                    66,
                    67,
                    68,
                    69,
                    70,
                    71,
                    72,
                    73,
                    74,
                    75,
                    76,
                    77,
                    78,
                    79,
                    80,
                    81,
                    82,
                    83,
                    84,
                    85,
                    86,
                    87,
                    88,
                    89,
                    90,
                    91,
                    92,
                    93,
                    94,
                    95,
                    96,
                    97,
                    98
                ]
            },
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.21132597100222483,
                "cpu_seconds": 0.21114156300000003,
                "peak_rss_mib": 103.8828125,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Vierpunktfasern mit C4 und perfekten Matchings ueber KG(7,2); keine Normoptimierung."
        },
        {
            "candidate_id": "C06",
            "family_id": "F03",
            "arm": "lambda",
            "status": "self_verified",
            "graph6": "~?@b????????????????????????????????????????????????????????????????????????????????????????PO?dC@D?ASOAI?Cg_AI?Cg_@D?ASO?PO?dCCAI?Cg?OGg?Q_?_PO?d??_PO?d?COGg?Q?@CAI?C_?g_PO?_?Aa@D?A??DCAI?C??dCAI????Qa@D????Cg_PO????dCAI????ASOGg????Cg_PO????Cg_PO????ASOGg?????dCAI?????Cg_PO?????Qa@D????O?dCAG????O?dCAG????g?Qa@?????I?Cg_O????@O?dCA?????D?ASOG????AI?Cg_?????@_r?_?PO?dC?oX_O?Gg?Qa?KEWC?AI?Cg_@_r?_?PO?dC?EBKA?@D?ASO?KEWC?AI?Cg_?KEWCCAI?Cg??EBKAA@D?AS??@_r?__PO?d???KEWCCAI?Cg???oX_SOGg?Q???@_r?g_PO?c?C?@_r?g_PO?_?A??oX_SOGg?O??_?KEWDCAI?C??C?@_rCg_PO????O?EBKQa@D?????_?KEWdCAI?????_?KEWdCAI????_O?EBGQa@D????WC?@_oCg_PO???B?_?KE?dCAI????KA??oWASOGg???AWC?@__Cg_PO???EWC?@_?Cg_PO???BKA??o?ASOGg????r?_?KO?dCAG????EWC?@a?Cg_P?????X_O?Eg?Qa@??????r?_?LO?dCA?????_r?_?HO?dCA?????oX_O??g?Qa@?????KEWC?AI?Cg_??????",
            "graph6_sha256": "13721ddc6b5391899a427f5fe9557b18ef120d3c99be2936a71c14200f22dd71",
            "seed": "301",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "ap",
                "--seed",
                "301",
                "--restarts",
                "1000",
                "--out",
                "C06_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": true,
                "omega_frame_condition": null
            },
            "scores": {
                "W": 2244,
                "L1": 3828,
                "F": 8184,
                "Linf": 4,
                "Nmax": 198,
                "lambda_bad_edges": 0,
                "residual_histogram": {
                    "-2": 660,
                    "-1": 594,
                    "0": 2607,
                    "1": 462,
                    "2": 330,
                    "4": 198
                }
            },
            "omega_frame": null,
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.0006102219995227642,
                "cpu_seconds": 0.0006085739999999173,
                "peak_rss_mib": 90.6015625,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Drei unabhaengige 33er-Klassen; zyklische Dreiecksmatchings. Offsets: [[6, 12], [12, 24], [26, 19], [32, 31], [15, 30], [28, 23], [10, 20]]. Keine Normoptimierung."
        },
        {
            "candidate_id": "C07",
            "family_id": "F03",
            "arm": "lambda",
            "status": "self_verified",
            "graph6": "~?@b?????????????????????????????????????????????????????????????????????????????????????????@GYAO?C`gHO?HBOOO?HBOOG?C`gGQ?@GY?AO?HBO?H??cL??Q?@GY??Q?@GY??H??cL?AAO?HB??OQ?@GW?D@G?C`??YAO?H???YAO?H???L@G?C_??BOQ?@G???YAO?H???`gH??_??@BOQ?@???@BOQ?@???C`gH?????@GYAO?????HBOQ??????cL@G?????@GYAO?????@GYAO??????cL@G??????HBOQ??????@GYAO??????C`gH???????HBOQ??????IG?WW?@GYAODC?KK??cL@G@P?BBO?HBOO?IG?WY?@GYAC?g_@`G?C`gGW@P?BAO?HBO?W@P?BAO?HBO?K?g_@`G?C`g?B?IG?WQ?@GY??W@P?BAO?HBO?`_DC?GH??cL?BB?IG?OQ?@GW?BB?IG?OQ?@GW?@`_DC?gH??cG??WW@P?YAO?H???BB?IGBOQ?@G???KK?g_L@G?C_???WW@P?YAO?H????WW@P?YAO?H????KK?gcL@G?C????BB?IHBOQ?@?????WW@PGYAO?G???_@`_DC`gH?????@?BB?IHBOQ?????@?BB?IHBOQ??????_@`_DC`gH?????AG?WW@@GYAO?????P?BB?GHBOQ?????DC?KK??cL@G?????IG?WW?@GYAO?????IG?WW?@GYAO?????DC?KK??cL@G?????@P?BB??HBOQ??????",
            "graph6_sha256": "d0bdc05ba376cdb4918504d18ab91ab2a6d3945069a244c02de5ba54087c27d0",
            "seed": "302",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "ap",
                "--seed",
                "302",
                "--restarts",
                "1000",
                "--out",
                "C07_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": true,
                "omega_frame_condition": null
            },
            "scores": {
                "W": 2772,
                "L1": 4488,
                "F": 8976,
                "Linf": 4,
                "Nmax": 132,
                "lambda_bad_edges": 0,
                "residual_histogram": {
                    "-2": 660,
                    "-1": 924,
                    "0": 2079,
                    "1": 528,
                    "2": 396,
                    "3": 132,
                    "4": 132
                }
            },
            "omega_frame": null,
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.0005234140007814858,
                "cpu_seconds": 0.0005213430000000074,
                "peak_rss_mib": 91.04296875,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Drei unabhaengige 33er-Klassen; zyklische Dreiecksmatchings. Offsets: [[13, 26], [22, 11], [11, 22], [19, 5], [2, 4], [5, 10], [14, 28]]. Keine Normoptimierung."
        },
        {
            "candidate_id": "C08",
            "family_id": "F04",
            "arm": "lambda",
            "status": "self_verified",
            "graph6": "~?@b????????????????????????????????????????????????????????????????????????????????????????cACACaOGOGQC_O_Occ_O_O_QOGOGOCcACACCc_O_O?QQ@A@??ccACA??ccACA??QQ@A@?ACc_O_??OccAC??@AQOGO??ACc_O_??ACc_O_??@AQOGO???OccAC??CACc_O???OGQQ@????_OccA????_OccA????OGQQ@???ACACc_????O_Occ????@A@AQO????ACACc_????ACACc_????@A@AQO?????O_Occ????CACACc?????OGOGQO?????_O_Oc_?????OE_ODA??LPSGBOGA@??EghA?sA?oO?@iGgOE_OAA??LPA`?Y@?gG??t?DA?sA@OO?@i?DA?sA@OO?@i?A`?Y@?gG??t??gOE_QIA??L??DA?sAPOO?@g??SGBOLD@??E?A?gOE_IIA??K?A?gOE_iIA??G?@?SGBOtD@?????ODA?sLPOO????A?gOE`iIA?????GA`?YEggG?????ODA?sLPOO????_ODA?oLPOO????OGA`?WEggG????SA?gOC@iIA????E_ODA??LPOO????Y@?SG??tD@?????sA?gO?@iIA?????sA?gO?@iIA?????Y@?SG??tD@?????E_ODA??LPOO?????sA?gO?@iIA?????BOGA`??EggG????OE_ODA??LPO?????OE_ODA??LPO?????GBOGA`??Egg?????A?sA?gO?@iI??????",
            "graph6_sha256": "cc39043a75d31be24fe9f6e96410180fb6a12e3bf258511fd070cc44f18173fe",
            "seed": "401",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "offset",
                "--seed",
                "401",
                "--restarts",
                "1000",
                "--out",
                "C08_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": true,
                "omega_frame_condition": null
            },
            "scores": {
                "W": 2673,
                "L1": 3498,
                "F": 5412,
                "Linf": 3,
                "Nmax": 132,
                "lambda_bad_edges": 0,
                "residual_histogram": {
                    "-2": 330,
                    "-1": 1089,
                    "0": 2178,
                    "1": 891,
                    "2": 231,
                    "3": 132
                }
            },
            "omega_frame": null,
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.0014140399980533402,
                "cpu_seconds": 0.0014124809999999655,
                "peak_rss_mib": 90.89453125,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Drei unabhaengige 33er-Klassen; zyklische Dreiecksmatchings. Offsets: [[11, 21], [18, 20], [30, 1], [3, 11], [23, 3], [6, 18], [0, 29]]. Keine Normoptimierung."
        },
        {
            "candidate_id": "C09",
            "family_id": "F04",
            "arm": "lambda",
            "status": "self_verified",
            "graph6": "~?@b?????????????????????????????????????????????????????????????????????????????????????????G_PAo?a@CJO@CAGSo@CAGOW?a@CGU?G_P?Ao@CAG?J?COG_?U?G_P??U?G_P?CJ?COG?@Ao@CA??GU?G_O??`W?a@??PAo@C???PAo@C???G`W?a???AGU?G_???PAo@C???@CJ?CO???AGU?G_??CAGU?G???A@CJ?C????_PAo@????CAGU?G???COG`W?????G_PAo?????G_PAo?????COG`W?????@CAGU??????G_PAo??????a@CJ??????@CAGU?????@IC_GGOD?qC?dAOCCGA_XA?HOc@@A?gEO_@IC_GGOD?qCCCgQ?_@?SBGOGHOc@?A?gEO_GHOc@CA?gEO?CCgQ?a@?SBG?@@IC_G_OD?q??GHOc@CA?gEO?__dAO?OGA_X?@@@IC_O_OD?o?@@@IC_O_OD?o??__dAOGOGA_W??GGHOcQCA?gC??@@@ICeO_OD????CCCgQXA@?S????GGHOcqCA?g???_GGHO_qCA?g???OCCCgOXA@?S???C@@@ICEO_OD???C_GGHO?qCA?g???Q?__dCBGOGA????c@@@IGEO_OC????c@@@IgEO_O?????Q?__dSBGOG????AC_GGHD?qCA?????Oc@@@GgEO_O????DAOCCCA_XA@?????IC_GGGD?qCA?????IC_GGGD?qCA?????dAOCC?A_XA@?????HOc@@A?gEO_??????",
            "graph6_sha256": "9a289dc01928217cca40edcd39635045645001305388a863bc76b5eb153ceef6",
            "seed": "402",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "offset",
                "--seed",
                "402",
                "--restarts",
                "1000",
                "--out",
                "C09_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": true,
                "omega_frame_condition": null
            },
            "scores": {
                "W": 2871,
                "L1": 3828,
                "F": 6072,
                "Linf": 4,
                "Nmax": 33,
                "lambda_bad_edges": 0,
                "residual_histogram": {
                    "-2": 462,
                    "-1": 990,
                    "0": 1980,
                    "1": 1056,
                    "2": 264,
                    "3": 66,
                    "4": 33
                }
            },
            "omega_frame": null,
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.0014302839990705252,
                "cpu_seconds": 0.0014283550000000478,
                "peak_rss_mib": 90.33984375,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Drei unabhaengige 33er-Klassen; zyklische Dreiecksmatchings. Offsets: [[5, 4], [14, 28], [2, 26], [21, 10], [25, 31], [10, 21], [3, 18]]. Keine Normoptimierung."
        },
        {
            "candidate_id": "C10",
            "family_id": "F04",
            "arm": "lambda",
            "status": "self_verified",
            "graph6": "~?@b?????????????????????????????????????????????????????????????????????????????????????????aCaK?AGQGo?COcP_?COcP_?AGQGo??aCaKC?COcP?o?PAP?@_?aCa?@_?aCa??o?PAP?AK?COc??P_?aC_?@E?AGQ??AK?COc??aK?CO_??PE?AGO??CP_?aC??CaK?CO???QGo?P????cP_?a????cP_?a????QGo?P???ACaK?C????OcP_?_???@APE?A????ACaK?C????aCaK??????PAPE??????COcP_??????aCaK??????AGQGo??????COcP_????????dPW??OWQo??Qgk??GKHW??CiJO?ABAS???dP]??OWQC??ATDW?@@`GW??CiIo?ABA?W??CiIo?ABA?k??AT@W?@@`?J???dQU??OW?@W??CiQo?AB??D_??QhJ??GK?AJ???dAU??OW?AJ???dAU??OW?DD_??Q`J??GG?@PW??CwQo?A???iJ???bAU??O??Agk??AKHW?@???DPW??CWQo?A???dPW???WQo?A???Qgk???KHW?@???CiJ??ABAU??????dPW??OWQo?????ATD_?@@`J??????CiJ??ABAU??????CiJ??ABAU??????ATD_?@@`J???????dPW??OWQo??????CiJ??ABAU???????Qgk??GKHW???????dPW??OWQo???????dPW??OWQo???????Qgk??GKHW???????CiJ??ABAU??????",
            "graph6_sha256": "2ea485dfd5d07077b7f11060bb3c00871d1aab5b1fb305360d03732a4f0ee3db",
            "seed": "403",
            "parents": [],
            "generator_id": "G01",
            "generator_args": [
                "--kind",
                "offset",
                "--seed",
                "403",
                "--restarts",
                "1000",
                "--out",
                "C10_run.json"
            ],
            "hard_checks": {
                "order_99": true,
                "simple_undirected": true,
                "regular_14": true,
                "lambda_edge_condition": true,
                "omega_frame_condition": null
            },
            "scores": {
                "W": 2739,
                "L1": 3696,
                "F": 5940,
                "Linf": 4,
                "Nmax": 33,
                "lambda_bad_edges": 0,
                "residual_histogram": {
                    "-2": 396,
                    "-1": 1056,
                    "0": 2112,
                    "1": 858,
                    "2": 330,
                    "3": 66,
                    "4": 33
                }
            },
            "omega_frame": null,
            "isomorphism": {
                "method": "pynauty 2.8.8.1 / nauty2_8_8; exact uncolored canonical certificates, 45 submission pairs and all 26 tracked .g6 files at bb43b0ab4fad36e142832923b83dcf3f6a186652",
                "within_submission": "complete",
                "against_project_archive": "partial",
                "duplicate_of": []
            },
            "runtime": {
                "wall_seconds": 0.0018158339989895467,
                "cpu_seconds": 0.001813973999999996,
                "peak_rss_mib": 91.046875,
                "environment": "Linux x86_64; Python 3.12.14; one solver worker"
            },
            "notes": "Drei unabhaengige 33er-Klassen; zyklische Dreiecksmatchings. Offsets: [[23, 4], [6, 11], [11, 13], [7, 15], [18, 5], [27, 7], [15, 18]]. Keine Normoptimierung."
        }
    ]
}
```

## 7.4 Graph6- und Prüfsummenkonvention

Standard-graph6 ohne Header, Leerzeichen oder eingebettete Zeilenumbrüche.
Graph6-Knotenlabels sind 0,…,98. Der Encoder ist NetworkX; der separate Prüfer dekodiert
Ordnung, Bitreihenfolge, Länge und Nullpadding selbst mit der Python-Standardbibliothek.

Jede Prüfsumme ist SHA256 über die ASCII-Bytes der **dekodierten**
JSON-Zeichenfolge graph6, gefolgt von genau einem LF-Byte 0x0A.
JSON-Backslash-Escapierung gehört nicht zu den gehashten Graphdaten.

## 7.5 Ω-Rahmenbeschreibung und Isomorphieumfang

Alle Ω-Kandidaten stehen bereits in kanonischer Reihenfolge:
Position 0 ist die Wurzel; Positionen 1,…,14 entsprechen Nachbarlabels 0,…,13;
Positionen 15,…,98 den lexikographisch sortierten Nichtpartnerpaaren.
Partner sind a und (a+7) modulo 14.
Jede Identitätspermutation ist im JSON vollständig ausgeschrieben.
Bei λ ist omega_frame=null.

Die Isomorphieprüfung verwendete **ungefärbte vollständige Graphen**:
exakte nauty-Kanonisierungszertifikate, ohne Rahmenfarben und ohne Beschränkung auf vorgegebene Gruppenwirkungen.
Die Zertifikatsbytes wurden direkt verglichen; nicht bloß ihre Hashes, Scores oder Spektren.
45 interne Paare sind nichtisomorph.
Daraus folgt insbesondere auch die Nichtäquivalenz der unterschiedlichen Ω-Kandidaten unter rahmenerhaltenden Abbildungen:
Jede solche Äquivalenz wäre zugleich eine Graphisomorphie.
Ein zusätzlicher farbiger Rahmen-Kanonisierungslauf wurde nicht ausgeführt und war für diese negativen Paarentscheidungen nicht nötig.
Eine vollständige Klassifikation aller möglichen Ω-Arbeitsrahmen desselben Graphen ist nicht Bestandteil der Untersuchung.

Für den Archivvergleich wurden am fixierten Commit alle folgenden 26 .g6-Dateien vollständig gelesen,
jeweils eine Graphzeile. Sie enthalten 18 verschiedene Bytefolgen;
dies ist ausdrücklich eine Bytezählung, keine hier behauptete Zahl von Archiv-Isomorphieklassen.
Kein Einreichungskandidat stimmt mit einem ihrer nauty-Zertifikate überein.

| Archivdatei und Zeile | SHA256 der Graphzeile mit LF |
| --- | --- |
| `data/memetic/reference/H_Z14_invariant_A99.g6:1` | `98c8f6e3bd86e2a581f7269763cc3164345425945934f0e66043dc6deabb758c` |
| `data/memetic/reference/H_minus_Z2_template_A99.g6:1` | `f73b8457a1115acc0cae0c18bb6fbce7f0fd4ba65b0eed8e13eeab8af2eabaf0` |
| `data/memetic/reference/H_plus_Z2_template_A99.g6:1` | `6f8ea3c706220a9ecf22fd04ef5a7972cd4dac4d7a51beb4bfb53901e48c3b18` |
| `data/memetic/reference/hog57338.g6:1` | `18a7bf225053c8c3c180ac9e01b65b733143ff22430b479c056f1e3241673bdd` |
| `data/memetic_v2/reference/A_legacy_best_hard.g6:1` | `23e64ba808aa2aeceb7b88128987d88144b9f069503039b05c8a8c7c291ee282` |
| `data/memetic_v2/reference/B_maple_20260829.g6:1` | `1c39edc85e85e0c41c2de323fcd2665c8872d946fe2dd8c1b9ace8c2ac4e1bfb` |
| `data/memetic_v2/reference/H_Z14_invariant_A99.g6:1` | `98c8f6e3bd86e2a581f7269763cc3164345425945934f0e66043dc6deabb758c` |
| `data/memetic_v2/reference/H_minus_Z2_template_A99.g6:1` | `f73b8457a1115acc0cae0c18bb6fbce7f0fd4ba65b0eed8e13eeab8af2eabaf0` |
| `data/memetic_v2/reference/H_plus_Z2_template_A99.g6:1` | `6f8ea3c706220a9ecf22fd04ef5a7972cd4dac4d7a51beb4bfb53901e48c3b18` |
| `data/memetic_v2/reference/hog57177.g6:1` | `2678f59b9ce5f5a65386951828fa34da87c1da46be8294789b4cfd21157a66dc` |
| `data/memetic_v2/reference/hog57200.g6:1` | `e774278e293380e347214fd94a8b6c80b06c84f7ebfa94f4489b5be0886fb35b` |
| `data/memetic_v2/reference/hog57271.g6:1` | `902624afa21e0dcfc638c28ebc59ad707b2847456ff07d5fd871b1d61051d152` |
| `data/memetic_v2/reference/hog57328.g6:1` | `24739005beb6c08975f4c895579e8b4f9d2df58af83e2778c21a5f4acf9a54e4` |
| `data/memetic_v2/reference/hog57338.g6:1` | `18a7bf225053c8c3c180ac9e01b65b733143ff22430b479c056f1e3241673bdd` |
| `data/memetik/ai_candidates/accepted/lambda/claude_v01_c.g6:1` | `138e640c4e6f982f5773acc78b4c80d7ec12169bb59efd6ea2a0c5afad33be66` |
| `data/memetik/ai_candidates/accepted/omega/claude_v01_a.g6:1` | `3620c9d10034fb130ac4b6f6529f31f9de9481089c1ad4291ba1d3011369a6d5` |
| `data/memetik/ai_candidates/accepted/omega/claude_v01_b.g6:1` | `ca1de4bcd2d22b631ce4c8058dcdebddc1d62e143e2d2c70abc563b8b44c0774` |
| `data/memetik/ai_candidates/accepted/omega/gemini_v01_seed42.g6:1` | `5dbfad84a90aa1622f51c171c0b72857ad8721173b74f23ed21473616c91dffb` |
| `data/memetik/ai_candidates/submissions/20260914_gemini_v01/kandidat_42.g6:1` | `5dbfad84a90aa1622f51c171c0b72857ad8721173b74f23ed21473616c91dffb` |
| `data/memetik/ai_candidates/submissions/20260915_claude_v01/kandidat_01.g6:1` | `3620c9d10034fb130ac4b6f6529f31f9de9481089c1ad4291ba1d3011369a6d5` |
| `data/memetik/ai_candidates/submissions/20260915_claude_v01/kandidat_02.g6:1` | `ca1de4bcd2d22b631ce4c8058dcdebddc1d62e143e2d2c70abc563b8b44c0774` |
| `data/memetik/ai_candidates/submissions/20260915_claude_v01/kandidat_03.g6:1` | `138e640c4e6f982f5773acc78b4c80d7ec12169bb59efd6ea2a0c5afad33be66` |
| `results/memetik/office_pilot_001_20260912/B_descendant_L1.g6:1` | `cee1d02de341ecf06e2ab98b41dcc567badf0470f5b5a582cec82ef7cc2f5639` |
| `results/memetik/office_pilot_001_20260912/B_descendant_L2.g6:1` | `0c0b0f3f943dd0d7e3f92d79142003a0314e5cdc111f3ca5acae5c4ececbd5f3` |
| `results/memetik/office_pilot_001_20260912/B_descendant_Linf.g6:1` | `95c66ac94a6d7d702a9023f157e7ab1467cfe70f064622e96a61e116bc7ded7e` |
| `results/memetik/office_pilot_001_20260912/lambda_Linf2_00.g6:1` | `f25b75e0d8cdfd61731d6249aed1265bee5d3616d1c4f3ab2118853eb4d19aeb` |

Ausgenommen bleiben private Archive, ZIP-Inhalte, in anderen Formaten eingebettete Kandidaten sowie nicht ausgecheckte Historie.
Deshalb steht im JSON against_project_archive=partial.
Keine Aussage über maximale Vielfalt, globale Neuheit, Mutationsmindestabstand oder verschiedene Einzugsgebiete folgt aus diesen Vergleichen.

## 7.6 Vollständige Generatoren

Die nachfolgenden Python-Blöcke sind vollständige Dateien. Gemeinsame lokale Hilfsabhängigkeiten sind ebenfalls in diesem Dokument enthalten.
Sie können aus dem Dokument als die angegebenen Dateinamen gespeichert werden.
Der Generator benötigt keine Projektdateien und keine bestehenden Graphen.

generator_id: G01

Dateiname: `generate.py`  
Sprache: Python 3.12.14; vier Leerzeichen je Einrückungsebene.  
Abhängigkeiten: numpy==2.3.5, networkx==3.6.1, ortools==9.15.6755.  
Installation im gewünschten Python-Umfeld, falls nötig:

```bash
python -m pip install numpy==2.3.5 networkx==3.6.1 ortools==9.15.6755
```

Ausführbarer Beispielaufruf für C02:

```bash
OPENBLAS_NUM_THREADS=1 python generate.py --kind cover --seed 203 --seconds 120 --out C02_run.json
```

Alle Kandidaten haben ihre vollständigen Argumentlisten im JSON.
Für die beiden ersten erfolglosen Versuche wird zusätzlich `--objective` gesetzt:
free/101 und cover/201 jeweils mit `--seconds 60`;
free/102 und free/103 wurden ohne Hilfsziel mit `--seconds 120` ausgeführt.

Der Generator schreibt einen Laufdatensatz inklusive graph6 und Hash, wenn er einen Graphen findet.
UNKNOWN erzeugt ausdrücklich keinen Graphdatensatz.
CP-SAT-Status OPTIMAL beim Modell ohne Zielfunktion bedeutet lediglich erfüllt, **keine optimale Conway-Fehlerqualität**.
Greedy-Restartlimits sind ebenfalls kein Unmöglichkeitsbeweis.

Die zehn graph6-Ergebnisse wurden mit dem untenstehenden endgültigen Code auf derselben Umgebung byteidentisch reproduziert.
Zeitlimits können auf anderer Hardware früher greifen; ein Seed allein garantiert keine versionsübergreifende identische Solverausgabe.
Die eingebetteten Graphdaten bleiben unabhängig von erneuter Erzeugung prüfbar.

```python
import argparse
import hashlib
import itertools
import json
import platform
import random
import resource
import time

import networkx as nx
import numpy as np
from ortools.sat.python import cp_model


def frame():
    pairs = [(a, b) for a in range(14) for b in range(a + 1, 14)
             if b != (a + 7) % 14]
    p = np.zeros((14, 84), dtype=np.int64)
    for i, ab in enumerate(pairs):
        p[list(ab), i] = 1
    c = np.zeros((14, 14), dtype=np.int64)
    for a in range(14):
        c[a, (a + 7) % 14] = 1
    return pairs, p, c


def omega(kind, seed, seconds, objective):
    pairs, p, c = frame()
    rhs = 2 - (c + np.eye(14, dtype=np.int64)) @ p
    model = cp_model.CpModel()
    h = {}
    supports = [frozenset(a % 7 for a in ab) for ab in pairs]
    for i in range(84):
        for j in range(i + 1, 84):
            if kind == "free":
                h[i, j] = model.new_bool_var(f"h_{i}_{j}")
            elif supports[i] == supports[j]:
                h[i, j] = int(len(set(pairs[i]) & set(pairs[j])) == 1)
            elif supports[i].isdisjoint(supports[j]):
                h[i, j] = model.new_bool_var(f"h_{i}_{j}")
            else:
                h[i, j] = 0
    def entry(i, j):
        return 0 if i == j else h[min(i, j), max(i, j)]
    for j in range(84):
        model.add(sum(entry(i, j) for i in range(84)) == 12)
        for a in range(14):
            model.add(sum(entry(i, j) for i in range(84) if p[a, i])
                      == int(rhs[a, j]))
    if kind == "cover":
        blocks = sorted(set(supports), key=lambda s: tuple(sorted(s)))
        for i in range(84):
            for block in blocks:
                if supports[i].isdisjoint(block):
                    model.add(sum(entry(i, j) for j in range(84)
                                  if supports[j] == block) == 1)
    rng = random.Random(seed)
    variables = [v for v in h.values() if not isinstance(v, int)]
    if objective:
        model.minimize(sum(rng.randint(-100, 100) * v for v in variables))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.stop_after_first_solution = True
    if not objective:
        solver.parameters.randomize_search = True
        solver.parameters.random_branches_ratio = 0.1
        solver.parameters.linearization_level = 0
    status = solver.solve(model)
    info = {"solver_status": solver.status_name(status),
            "boolean_variables": len(variables),
            "branches": solver.num_branches, "conflicts": solver.num_conflicts}
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return None, info
    a = np.zeros((99, 99), dtype=np.int64)
    a[0, 1:15] = a[1:15, 0] = 1
    a[1:15, 1:15] = c
    a[1:15, 15:] = p
    a[15:, 1:15] = p.T
    for (i, j), var in h.items():
        value = var if isinstance(var, int) else solver.value(var)
        a[15 + i, 15 + j] = a[15 + j, 15 + i] = value
    return a, info


def triangle(seed, limit, general):
    rng = random.Random(seed)
    best = 0
    for attempt in range(1, limit + 1):
        pool = [(a, b) for a in range(33) for b in range(33)] if general else [
            (d, 2 * d % 33) for d in range(33)]
        rng.shuffle(pool)
        chosen = []
        for ab in pool:
            trial = chosen + [ab]
            if len({a for a, b in trial}) != len(trial):
                continue
            if len({b for a, b in trial}) != len(trial):
                continue
            if len({(b - a) % 33 for a, b in trial}) != len(trial):
                continue
            if any((trial[i][0] + trial[j][1] - trial[j][0] - trial[k][1]) % 33 == 0
                   for i, j, k in itertools.product(range(len(trial)), repeat=3)
                   if not i == j == k):
                continue
            chosen = trial
            if len(chosen) == 7:
                a = np.zeros((99, 99), dtype=np.int64)
                for u, v in chosen:
                    for x in range(33):
                        tri = [x, 33 + (x + u) % 33, 66 + (x + v) % 33]
                        for i, j in itertools.combinations(tri, 2):
                            a[i, j] = a[j, i] = 1
                return a, {"restarts": attempt, "offsets": chosen,
                           "general_offsets": general}
        best = max(best, len(chosen))
    return None, {"restarts": limit, "largest_partial": best}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["free", "cover", "ap", "offset"], required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--restarts", type=int, default=1000)
    parser.add_argument("--objective", action="store_true")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    wall, cpu = time.perf_counter(), time.process_time()
    if args.kind in ("free", "cover"):
        a, info = omega(args.kind, args.seed, args.seconds, args.objective)
    else:
        a, info = triangle(args.seed, args.restarts, args.kind == "offset")
    elapsed = time.perf_counter() - wall
    used = time.process_time() - cpu
    result = {"kind": args.kind, "seed": args.seed, "objective": args.objective, "details": info,
              "runtime": {"wall_seconds": elapsed, "cpu_seconds": used,
                          "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                          "environment": f"{platform.system()} {platform.machine()}; Python {platform.python_version()}; one solver worker"}}
    if a is not None:
        data = nx.to_graph6_bytes(nx.from_numpy_array(a), header=False)
        result["graph6"] = data.decode("ascii").rstrip("\n")
        result["graph6_sha256"] = hashlib.sha256(data).hexdigest()
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    print(json.dumps({k: v for k, v in result.items() if k != "graph6"}))


if __name__ == "__main__":
    main()
```

generator_id: G02

Dateiname: `compare.py`  
Sprache: Python 3.12.14.  
Zweck: optionale zweite Scoreberechnung per Ganzzahl-Matrixprodukt, exakte Isomorphieprüfung und Automorphismengruppen.
Abhängigkeiten: numpy==2.3.5, networkx==3.6.1, pynauty==2.8.8.1 sowie die vollständig eingebettete Datei `verify.py` aus 7.7.
G02 ist ein Analyseprogramm, kein weiterer Konstruktionsgenerator.

Zusätzliche Installation, falls benötigt:

```bash
python -m pip install pynauty==2.8.8.1
```

Aufruf ohne Repositoryzugriff:

```bash
OPENBLAS_NUM_THREADS=1 python compare.py --markdown CONWAY99_KANDIDATEN_Codex.md --out comparison.json
```

Für einen Archivvergleich kann `--archive repo` ergänzt werden, wenn ein Checkout des angegebenen Commits im Ordner repo vorliegt.
Die Archivdaten selbst sind nicht Bestandteil dieser Einreichung.
Die eingebetteten Kandidaten und ihre Zulässigkeit sind ohne diesen Checkout prüfbar.

```python
import argparse
import hashlib
import itertools
import json
import pathlib
import time

import networkx as nx
import numpy as np
import pynauty

from verify import calculate, decode, load_document


def canonical(g):
    adj = {int(i): sorted(int(j) for j in g.neighbors(i)) for i in g.nodes}
    return pynauty.certificate(pynauty.Graph(len(g), adjacency_dict=adj))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--archive")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    graphs, certificates, rows = {}, {}, {}
    document, _, _ = load_document(args.markdown)
    for data in document["candidates"]:
        name = data["candidate_id"]
        g = nx.from_graph6_bytes(data["graph6"].encode("ascii"))
        graphs[name] = g
        certificates[name] = canonical(g)
        a = nx.to_numpy_array(g, nodelist=range(99), dtype=np.int64)
        r = (a @ a + a - 2)[np.triu_indices(99, 1)]
        values, counts = np.unique(r, return_counts=True)
        mx = int(np.abs(r).max())
        scores = {"W": int(np.count_nonzero(r)), "L1": int(np.abs(r).sum()),
                  "F": int((r * r).sum()), "Linf": mx,
                  "Nmax": int(np.count_nonzero(np.abs(r) == mx)),
                  "lambda_bad_edges": int(np.count_nonzero(
                      ((a @ a) != 1) & (a == 1))) // 2,
                  "residual_histogram": {str(v): int(c) for v, c in zip(values, counts)}}
        arm = data["arm"]
        frame = data["omega_frame"]
        hard, direct = calculate(decode(data["graph6"]), arm, frame)
        assert scores == direct == data["scores"]
        assert hard["regular_14"]
        assert hard["omega_frame_condition" if arm == "omega" else "lambda_edge_condition"]
        assert hashlib.sha256((data["graph6"] + "\n").encode()).hexdigest() == data["graph6_sha256"]
        pg = pynauty.Graph(99, adjacency_dict={i: sorted(g[i]) for i in g})
        aut = pynauty.autgrp(pg)
        rows[name] = {
            "hard_checks": hard, "scores": scores, "connected": nx.is_connected(g),
            "automorphism_order_mantissa": aut[1], "automorphism_order_exponent": aut[2],
            "vertex_orbits": aut[4], "duplicates": [], "archive_duplicates": []}
    for i, j in itertools.combinations(graphs, 2):
        if certificates[i] == certificates[j]:
            rows[i]["duplicates"].append(j)
            rows[j]["duplicates"].append(i)
    archive = []
    if args.archive:
        for path in sorted(pathlib.Path(args.archive).rglob("*.g6")):
            for line_number, line in enumerate(path.read_bytes().splitlines(), 1):
                if not line:
                    continue
                label = str(path.relative_to(args.archive)) + ":" + str(line_number)
                g = nx.from_graph6_bytes(line)
                item = {"path": label, "order": len(g),
                        "sha256": hashlib.sha256(line + b"\n").hexdigest()}
                if len(g) == 99:
                    cert = canonical(g)
                    for name in graphs:
                        if certificates[name] == cert:
                            rows[name]["archive_duplicates"].append(label)
                archive.append(item)
    result = {"candidates": rows, "archive_scope": archive,
              "wall_seconds": time.perf_counter() - start,
              "networkx_version": nx.__version__, "pynauty_version": pynauty.__version__}
    pathlib.Path(args.out).write_text(json.dumps(result, indent=4))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

## 7.7 Separater Prüfer

Dateiname: `verify.py`  
Sprache: Python 3.12.14; **nur Standardbibliothek**, keine Solver-/NumPy-/NetworkX-Abhängigkeit.  
Aufruf:

```bash
python verify.py CONWAY99_KANDIDATEN_Codex.md
```

Der Prüfer dekodiert graph6 selbst, rekonstruiert Nachbarmengen, zählt gemeinsame Nachbarn direkt
und prüft den Ω-Rahmen über die tatsächlichen Inzidenzhäufigkeiten.
Er importiert den Generator nicht und vertraut weder Generatornamen noch Prüfflags.
Familienverweise werden gegen die Überschriften F01–F04 und Generatorverweise gegen die expliziten generator_id-Zeilen geprüft.
Das Dokument muss genau einen JSON-Block enthalten; doppelte JSON-Schlüssel und nichtendliche Zahlen werden abgewiesen.

- **PASS:** alle geforderten Kandidatendaten sind vorhanden, harte Aufnahmebedingungen erfüllt, Hash und sämtliche Scores stimmen.
- **FAIL:** eine harte Bedingung ist falsch, eine Angabe widerspricht der Nachrechnung oder ein vorliegender Wert verletzt das Schema.
- **UNVERIFIED:** ohne festgestellten Widerspruch fehlt eine erforderliche Angabe oder eine erforderliche Prüfung bleibt offen.

Nullwerte sind nur dort zulässig, wo der Vertrag sie erlaubt. Unbekannte Laufkosten dürfen null bleiben.
Fehlende Isomorphieprüfung disqualifiziert einen sonst vollständigen Kandidaten nicht;
der Standardbibliothek-Prüfer weist die gemeldeten Isomorphieumfänge separat aus und führt nauty nicht selbst aus.
PASS bestätigt damit Zulässigkeit und Datenkonsistenz, **keine Neuheit**.
Bei Ω ist die optionale λ-Prüfung unabhängig von der obligatorischen Ω-Prüfung.

Rückgabecodes: 0 bei ausschließlich PASS, 1 bei mindestens einem FAIL,
2 bei mindestens einem UNVERIFIED ohne FAIL.
Der zusätzliche Matrixprodukt-/nauty-Lauf in G02 ist die getrennte zweite Kontrolle.

```python
"""Independent standard-library verifier for the embedded candidate JSON."""
import argparse
import collections
import hashlib
import itertools
import json
import math
import re
import sys


def decode(g):
    if not isinstance(g, str) or not g or any(not 63 <= ord(c) <= 126 for c in g):
        raise ValueError("Invalid graph6 bytes/header/whitespace")
    v = [ord(c) - 63 for c in g]
    if v[0] != 63:
        n, start = v[0], 1
    elif len(v) >= 4 and v[1] != 63:
        n, start = (v[1] << 12) + (v[2] << 6) + v[3], 4
        if n < 63:
            raise ValueError("Noncanonical graph6 order")
    else:
        raise ValueError("Unsupported or malformed graph6 order")
    if n != 99:
        raise ValueError(f"Order {n}, required 99")
    bits = [(x >> b) & 1 for x in v[start:] for b in range(5, -1, -1)]
    count = n * (n - 1) // 2
    if len(v) != start + (count + 5) // 6 or any(bits[count:]):
        raise ValueError("Wrong graph6 length or nonzero padding")
    a = [set() for _ in range(n)]
    pos = 0
    for j in range(1, n):
        for i in range(j):
            if bits[pos]:
                a[i].add(j)
                a[j].add(i)
            pos += 1
    return a


def calculate(a, arm, frame):
    n = len(a)
    hist = collections.Counter()
    bad = 0
    for i in range(n):
        for j in range(i + 1, n):
            common = len(a[i] & a[j])
            edge = j in a[i]
            hist[common + int(edge) - 2] += 1
            bad += int(edge and common != 1)
    linf = max(map(abs, hist))
    scores = {
        "W": sum(v for k, v in hist.items() if k),
        "L1": sum(abs(k) * v for k, v in hist.items()),
        "F": sum(k * k * v for k, v in hist.items()),
        "Linf": linf,
        "Nmax": sum(v for k, v in hist.items() if abs(k) == linf),
        "lambda_bad_edges": bad,
        "residual_histogram": {str(k): hist[k] for k in sorted(hist)}
    }
    hard = {
        "order_99": n == 99,
        "simple_undirected": all(i not in a[i] and all(i in a[j] for j in a[i])
                                 for i in range(n)),
        "regular_14": all(len(s) == 14 for s in a),
        "lambda_edge_condition": bad == 0,
        "omega_frame_condition": None
    }
    if arm == "omega" or frame is not None:
        if not isinstance(frame, dict) or set(frame) != {"canonical_to_graph6"}:
            raise ValueError("Missing or malformed omega frame")
        q = frame["canonical_to_graph6"]
        if (not isinstance(q, list) or any(type(x) is not int for x in q)
                or sorted(q) != list(range(99))):
            raise ValueError("Frame is not a permutation of 0,...,98")
        inv = {v: k for k, v in enumerate(q)}
        b = [{inv[v] for v in a[q[i]]} for i in range(99)]
        pairs = [(i, j) for i in range(14) for j in range(i + 1, 14)
                 if j != (i + 7) % 14]
        ok = b[0] == set(range(1, 15))
        for i in range(14):
            expected = {0, 1 + (i + 7) % 14}
            expected.update(15 + k for k, pair in enumerate(pairs) if i in pair)
            ok = ok and b[i + 1] == expected
        for j, pair in enumerate(pairs):
            ok = ok and b[j + 15] & set(range(15)) == {x + 1 for x in pair}
            outer = {v - 15 for v in b[j + 15] if v >= 15}
            ok = ok and len(outer) == 12
            for label in range(14):
                actual = sum(label in pairs[k] for k in outer)
                required = 2 - int(label in pair) - int((label + 7) % 14 in pair)
                ok = ok and actual == required
        hard["omega_frame_condition"] = bool(ok)
    return hard, scores


def verify(c, families, generators):
    fail, missing = [], []
    if not isinstance(c, dict):
        return "FAIL", ["Candidate is not an object"]
    fields = {
        "candidate_id", "family_id", "arm", "status", "graph6", "graph6_sha256",
        "seed", "parents", "generator_id", "generator_args", "hard_checks",
        "scores", "omega_frame", "isomorphism", "runtime", "notes"
    }
    missing.extend("Missing field: " + x for x in sorted(fields - set(c)))
    for key in ("candidate_id", "family_id", "generator_id", "notes"):
        if key in c and (not isinstance(c[key], str) or not c[key]):
            fail.append("Invalid string: " + key)
    for key, allowed in [("arm", {"lambda", "omega"}),
                         ("status", {"generated_unverified", "self_verified"})]:
        if key in c and (not isinstance(c[key], str) or c[key] not in allowed):
            fail.append("Invalid " + key)
    if c.get("family_id") is not None and c["family_id"] not in families:
        fail.append("Unknown family reference")
    if c.get("generator_id") is not None and c["generator_id"] not in generators:
        fail.append("Unknown generator reference")
    if c.get("seed") is not None and not isinstance(c["seed"], str):
        fail.append("Seed must be string or null")
    for key in ("parents", "generator_args"):
        if key in c and (not isinstance(c[key], list)
                         or any(not isinstance(v, str) for v in c[key])):
            fail.append("Invalid list: " + key)
    iso = c.get("isomorphism")
    if not isinstance(iso, dict):
        missing.append("Isomorphism object absent")
    else:
        keys = {"method", "within_submission", "against_project_archive", "duplicate_of"}
        missing.extend("Isomorphism field absent: " + x for x in keys - set(iso))
        if iso.get("method") is not None and not isinstance(iso["method"], str):
            fail.append("Invalid isomorphism method")
        for key in ("within_submission", "against_project_archive"):
            if key in iso and iso[key] not in ("not_checked", "partial", "complete"):
                fail.append("Invalid isomorphism scope")
        if "duplicate_of" in iso and (not isinstance(iso["duplicate_of"], list)
                or any(not isinstance(v, str) for v in iso["duplicate_of"])):
            fail.append("Invalid duplicate list")
    runtime = c.get("runtime")
    if not isinstance(runtime, dict):
        missing.append("Runtime object absent")
    else:
        for key in ("wall_seconds", "cpu_seconds", "peak_rss_mib", "environment"):
            if key not in runtime:
                missing.append("Runtime field absent: " + key)
            elif key == "environment":
                if runtime[key] is not None and not isinstance(runtime[key], str):
                    fail.append("Invalid runtime environment")
            elif runtime[key] is not None and (type(runtime[key]) not in (int, float)
                    or not math.isfinite(runtime[key]) or runtime[key] < 0):
                fail.append("Invalid runtime number: " + key)
    if c.get("graph6") is None:
        missing.append("Graph data absent")
        return ("FAIL" if fail else "UNVERIFIED"), fail + missing
    try:
        a = decode(c["graph6"])
        if c.get("arm") not in ("lambda", "omega"):
            return ("FAIL" if fail else "UNVERIFIED"), fail + missing
        if c["arm"] == "omega" and c.get("omega_frame") is None:
            missing.append("Required omega frame absent")
            hard, scores = calculate(a, "lambda", None)
        else:
            hard, scores = calculate(a, c["arm"], c.get("omega_frame"))
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        return "FAIL", fail + [str(exc)] + missing
    required = ["order_99", "simple_undirected", "regular_14"]
    required.append("lambda_edge_condition" if c["arm"] == "lambda" else "omega_frame_condition")
    for key in required:
        if hard[key] is False:
            fail.append("Hard condition violated: " + key)
        elif hard[key] is None:
            missing.append("Hard condition open: " + key)
    digest = hashlib.sha256((c["graph6"] + "\n").encode("ascii")).hexdigest()
    if c.get("graph6_sha256") is None:
        missing.append("SHA256 absent")
    elif c["graph6_sha256"] != digest:
        fail.append("SHA256 mismatch")
    reported_hard = c.get("hard_checks")
    if not isinstance(reported_hard, dict):
        missing.append("Hard-check object absent")
    else:
        for key, value in hard.items():
            if key not in reported_hard:
                missing.append("Hard-check field absent: " + key)
                continue
            reported = reported_hard[key]
            if reported is not None and type(reported) is not bool:
                fail.append("Invalid hard-check type: " + key)
            elif reported is not None and value is not None and reported != value:
                fail.append("Hard-check mismatch: " + key)
            elif reported is not None and value is None:
                missing.append("Reported hard check cannot be verified: " + key)
            elif key in required and reported is None and c.get("status") == "self_verified":
                missing.append("Self-verified hard-check flag absent: " + key)
    reported_scores = c.get("scores")
    if not isinstance(reported_scores, dict):
        missing.append("Score object absent")
    else:
        for key, value in scores.items():
            reported = reported_scores.get(key)
            if reported is None:
                missing.append("Score absent: " + key)
            elif key == "residual_histogram":
                if (not isinstance(reported, dict)
                        or any(not isinstance(k, str) or not re.fullmatch(r"-?(0|[1-9][0-9]*)", k)
                               or type(v) is not int or v < 0 for k, v in reported.items())):
                    fail.append("Invalid residual histogram")
                elif reported != value:
                    fail.append("Histogram mismatch")
            elif type(reported) is not int or reported != value:
                fail.append("Score mismatch: " + key)
    return ("FAIL" if fail else "UNVERIFIED" if missing else "PASS"), fail + missing


def load_document(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    blocks = re.findall(r"^\x60{3}json[ \t]*\n(.*?)^\x60{3}[ \t]*$", text, re.M | re.S)
    if len(blocks) != 1:
        raise ValueError(f"Expected exactly one JSON block, found {len(blocks)}")
    def reject(x):
        raise ValueError("Nonfinite JSON constant: " + x)
    def object_pairs(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError("Duplicate JSON key: " + k)
            result[k] = v
        return result
    doc = json.loads(blocks[0], parse_constant=reject, object_pairs_hook=object_pairs)
    if not isinstance(doc, dict) or doc.get("schema_version") != "conway99-candidates-1.0":
        raise ValueError("Invalid schema_version")
    if not isinstance(doc.get("submission_id"), str) or not doc["submission_id"]:
        raise ValueError("Missing submission_id")
    if not isinstance(doc.get("candidates"), list):
        raise ValueError("Candidates must be an array")
    families = set(re.findall(r"^### (F[0-9]+)\b", text, re.M))
    generators = set(re.findall(r"^generator_id: (G[0-9]+)\b", text, re.M))
    return doc, families, generators


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown")
    args = parser.parse_args()
    try:
        doc, families, generators = load_document(args.markdown)
    except (ValueError, OSError) as exc:
        print("FAIL document:", exc)
        return 1
    counts = collections.Counter()
    ids = [c.get("candidate_id") for c in doc["candidates"] if isinstance(c, dict)]
    for c in doc["candidates"]:
        try:
            status, reasons = verify(c, families, generators)
        except (TypeError, ValueError, KeyError) as exc:
            status, reasons = "FAIL", ["Malformed schema: " + str(exc)]
        cid = c.get("candidate_id") if isinstance(c, dict) else None
        if cid is not None and ids.count(cid) != 1:
            status, reasons = "FAIL", reasons + ["Duplicate candidate ID"]
        counts[status] += 1
        print(status, cid, "; ".join(reasons) if reasons else "Hard conditions, SHA256 and scores agree")
        iso = c.get("isomorphism") if isinstance(c, dict) else None
        if isinstance(iso, dict):
            print("  Isomorphism: reported only; not rerun by this verifier:",
                  iso.get("within_submission"), iso.get("against_project_archive"))
    print("TOTAL", dict(counts))
    return 1 if counts["FAIL"] else 2 if counts["UNVERIFIED"] else 0


if __name__ == "__main__":
    sys.exit(main())
```

### Ausgeführte Verifikation

Alle zehn Kandidaten bestanden sowohl die direkte Mengenprüfung als auch die zweite Ganzzahl-Matrixberechnung;
alle Kennzahlen und Hashes stimmen.
Sämtliche Histogramme summieren sich zu 4851. Zusätzlich gilt bei allen Kandidaten die Kontrollidentität

Σ_{i<j} r_ij = 99·binom(14,2)+693−2·4851 = 0.

Alle graph6-Ergebnisse wurden einmal separat reproduziert.
Der gemessene gesamte Wall-Aufwand dieser zehn Wiederholungen einschließlich Prozessstarts und Importen betrug 5,451751 Sekunden.
Die primären Laufkosten im JSON wurden dadurch nicht überschrieben.

Der endgültige eingebettete Prüfer wurde auf dieser Datei ausgeführt: zehn PASS.
Gezielte Negativkontrollen prüfen falschen Hash, falschen Score, ein gekipptes Kantenbit,
eine ungültige Ω-Rahmenpermutation, einen falschen Familienverweis und doppelte Kandidatenkennungen.
Sie müssen jeweils FAIL auslösen. Ein entfernter Hash muss UNVERIFIED auslösen.
Die Ergebnisse dieser Kontrollen wurden vor Auslieferung geprüft.

## 7.8 Fehlversuche und nicht ausgeführte Vorschläge

**Tatsächlich ausgeführte erfolglose bzw. zeitbegrenzte Versuche:** F01/101 (60 s),
F01/102 (120 s), F01/103 (120 s), F02/201 (60 s).
Alle endeten mit UNKNOWN; kein SAT-Zeuge und kein UNSAT-Nachweis.
Die jeweiligen gemessenen Zeiten einschließlich Modellaufbau stehen in 7.2.
Kein manueller Prozessabbruch und kein Ressourcenabbruch.
Kein erzeugter, nachweislich ungültiger Graph wurde als Kandidat aufgenommen.

**Erfolgreiche Versuche:** F02/202–206, F03/301–302, F04/401–403.
Zehn von zehn erfolgreiche Graphen wurden übernommen, nicht nach Fehlerqualität vorselektiert.
Die zehn Reproduktionen sind Kontrollläufe und werden nicht als zehn weitere Kandidaten gezählt.

**Drei nicht ausgeführte Folgeideen — keine vorliegenden Konstruktionen, keine gemessenen Erfolge:**

1. F02 mit größeren Fasern oder veränderten inneren Fasergraphen systematisch verallgemeinern.
   Vor einem Solverlauf müssen die analogen Inzidenzbilanzen erneut hergeleitet werden.
2. Die F03/F04-Gründer mit ausschließlich λ-erhaltenden, aber nicht farb- oder translationsgebundenen Trades bearbeiten.
   Zuerst messen, ob die Dreiklassenstruktur tatsächlich verlassen wird; kein gleicher Einzugsbereich wird unterstellt.
3. Für F01 längere reine Erfüllbarkeitsläufe mit verschiedenen Solverstrategien durchführen.
   Dies ist eine Fortsetzung eines begrenzten Fehlversuchs, keine begründete Erfolgsgarantie.
   Mehr Rechenzeit ist auf dem größeren Rechner möglich, aber für die Prüfung dieser Einreichung nicht erforderlich.

Kein vollständiger Cayley-Ansatz auf einer Gruppe der Ordnung 99 wurde hier erneut untersucht.
Der vorhandene Claude-Review berichtet bereits einen entsprechenden λ-Ausschluss.
Unsere Z33-Lifts sind keine regulären Cayley-Wirkungen auf allen 99 Knoten:
ihre tatsächlich berechneten Gruppen haben zwei bzw. drei Knotenbahnen.
Quelle für diesen Projektstand, ohne erneute Übernahme als eigener Beweis:
[Claude-Review](https://github.com/ibenarb/conway99-research/blob/bb43b0ab4fad36e142832923b83dcf3f6a186652/data/memetik/ai_candidates/submissions/20260915_claude_v01/REVIEW.md).

## 7.9 Auswahl für das gemeinsame Portfolio

**Startqualität — lexikographisch und je Arm getrennt:**

| Kriterium | Ω-Sieger dieser Einreichung | λ-Sieger dieser Einreichung |
| --- | --- | --- |
| (W,L1) | C02: (2074,2506) | C06: (2244,3828) |
| (F,W) | C02: (3472,2074) | C08: (5412,2673) |
| (L∞,Nmax,L1,W) | C03: (4,3,2692,2153) | C08: (3,132,3498,2673) |

C02 ist die erste Qualitätsempfehlung im Ω-Arm; C04 mit F=3612 ist eine sinnvolle zweite Variante derselben Familie.
C03 gewinnt die separate Ω-Minimaxauswahl dieser Einreichung aufgrund Nmax=3.
Diese Rangfolgen verwenden **keine gewichtete Summe**: eine spätere Komponente entscheidet nur bei Gleichstand aller früheren.
Die bestehenden Ω-L∞=3- und λ-L∞=2-Referenzen bleiben bezüglich dieses vorrangigen Maßes stärker.

**Vermuteter Beitrag zur strukturellen Vielfalt:**
Einen F02-Graphen, insbesondere C02, als neue konkrete Strukturprobe aufnehmen.
Zusätzlich C06 als arithmetischen Lift und C08 als allgemeineren zyklischen Lift erhalten;
die Verwandtschaft dieser beiden λ-Varianten offenlegen.
Die übrigen Varianten dürfen für Replikation und Streuung archiviert bleiben.
Die λ-Startwerte geben keinen Anlass, vorhandene HoG-Gründer zu ersetzen.
Ihre Dreifärbung und große Automorphismengruppe sind Strukturmerkmale und zugleich Beschränkungen, kein Qualitätsbeweis.

Die Isomorphieprüfung gegen die verfügbaren öffentlichen Gründer, die verfügbaren KI-Kandidaten und die interne Einreichung ist ausgeführt.
Offen bleiben der vollständige private Altbestand, weitere KI-Einreichungen und eine systematische Rahmenklassifikation.
Alle Graphen wurden ohne Gründergraph als Eingang erzeugt; daraus folgt weder eine Mindestzahl notwendiger Mutationen
noch ein anderes Einzugsgebiet.
Nächster empirischer Vergleich: dieselben CPU-Budgets und dieselben drei lexikographischen Kriterien für alte und neue Starts,
tatsächliche erreichte Zwischenstände protokollieren und Ω- sowie λ-Operatoren getrennt bewerten.
Gleiche Scores bedeuten kein gleiches Plateau; Nichtisomorphie bedeutet kein anderes Plateau.

Projektgrundlagen:
[Gründervertrag](https://github.com/ibenarb/conway99-research/blob/bb43b0ab4fad36e142832923b83dcf3f6a186652/docs/memetik/GRUENDERVERTRAG.md),
[Pilotbefunde](https://github.com/ibenarb/conway99-research/blob/bb43b0ab4fad36e142832923b83dcf3f6a186652/docs/memetik/pilot_0_3/BEFUNDE.md),
[Pilotanalyse](https://github.com/ibenarb/conway99-research/blob/bb43b0ab4fad36e142832923b83dcf3f6a186652/docs/memetik/pilot_0_3/ANALYSE.md).
Die Vorgaben des vorliegenden Auftrags haben Vorrang vor älteren Zielfunktions- oder Mengenvorschlägen.

