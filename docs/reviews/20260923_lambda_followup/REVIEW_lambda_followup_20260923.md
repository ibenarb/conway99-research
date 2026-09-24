# Unabhängiger Review: λ-Suche nach dem Ryzen-Folgelauf

**Gegenstand:** `lambda_followup_review_20260923_flat.zip`, SHA256
`460a4aa5de49a15284ef5b0fc40c33d849cf34f62717f1e2a3989df0aec589a8`, aus
`ibenarb/conway99-research` blob `7f146a2`, 517 Dateien, `sha256sum -c SHA256SUMS`
vollständig OK. Fixierte ausführbare Grundlage: Commit `3bafd48`.
**Datum:** 23. September 2026.

**Kennzeichnung:** **[G]** selbst nachgerechnet · **[B]** aus Belegen übernommen ·
**[H]** plausibel vermutet · **[U]** ungeklärt.

---

## Kurzurteil

Der Lauf ist handwerklich einwandfrei. Ich habe jede prüfbare Zahl des Berichts
unabhängig reproduziert und **keinen einzigen Fehler** gefunden. Der publizierte
Quellstand, das ausgelieferte Paket und die eingefrorenen Originalquellen sind
byteweise identisch.

Inhaltlich fällt mein Urteil anders aus als die Zahlen es auf den ersten Blick
nahelegen. Drei Befunde bestimmen meine Empfehlung:

1. **Der Ertrag ist logarithmisch in der CPU-Zeit.** Der Median W der P-Arme
   folgt über vier Messpunkte sehr genau `W ≈ 2246 − 12,9 · ln(CPU-s)`. Das sind
   rund 9 W je Verdopplung des Budgets. Eine Extrapolation dieser Anpassung gibt
   für 128 kumulative CPU-h je Job den Median 2078 und für W = 2000 rund
   **53 000 CPU-h je Job**. Ein größerer Lauf derselben Bauart kann eine exakte
   Lösung nicht erreichen — nicht knapp nicht, sondern um Größenordnungen nicht. **[G]**
2. **Der Nachteil von PC ist ein Kosten-, kein Qualitätseffekt.** PC schafft nur
   **197 statt 407 Episoden je CPU-Stunde**. Ursache ist im Quelltext greifbar:
   `kernel.catalogue()` zählt bei jedem exakten Abstiegsschritt den vollständigen
   cycle3-Katalog auf, dessen Verträglichkeitsvorberechnung eine 693²-Doppelschleife
   ist — gegen 4 158 Pivotkandidaten. PC kauft einen besseren Abstiegsschritt zum
   doppelten Preis. Bei diesem Budget lohnt sich das nicht. **[G]**
3. **Die gesamten 117 CPU-h liefen in einem einzigen Becken.** 27 der 39 Jobs
   starteten von *demselben* Graphen, alle 39 Bestwerte tragen `family = HoG`,
   und alle 1 496 Graphen des Pakets außer den 10 konstruierten Gründern sind
   starr (|Aut| = 1). Die zweite Hälfte der Gründerbank hat nie einen Bestwert
   produziert. **[G]**

Dazu kommt ein Effizienzbefund, der die Bauweise des nächsten Laufs unmittelbar
betrifft: die **Rekordspur W brauchte 6 neue CPU-h für W = 2102**, der
Methodenarm Pext 36 CPU-h für 2110 und PC 48 CPU-h für 2127. Der beste Graph des
gesamten Laufs kam aus der billigsten Spur. **[G]**

**Empfehlung:** kein größerer Hauptlauf. Stattdessen drei eng budgetierte
Voruntersuchungen mit zusammen **46 CPU-h**, deren Ausgänge jeweils eine konkrete
Entscheidung erzwingen. Das Manifest liegt bei.

---

## Prüfumfang und Grenzen

Alle Prüfungen sind in `reviewer_lambda_followup_20260923_pruefsatz.zip`
reimplementiert; Projektcode wird nirgends importiert. graph6-Decoder,
λ-Prüfung und die fünf Scores stammen aus den Definitionen in BERICHT.md.

| Prüfung | Umfang | Ergebnis |
|---|---|---|
| λ-Gültigkeit und fünf Scores | 9 827 Datensätze, 1 496 Graphen | 0 Abweichungen |
| Receipt-Dateihashes | 132 Vergleiche (task/result/checkpoint) | 132 exakt |
| SOURCE_PINS gegen `3bafd48` | 46 Dateien | 46 exakt |
| PACKAGE gegen `3bafd48` und ZIP | 69 Dateien | 69 exakt |
| CPU-Abrechnung | Such- und Hilfsledger | auf 9 Stellen reproduziert |
| Kurvenpräfixe der Fortsetzungen | 15 Jobs | alle erhalten |
| Zugzeugen | 414 Erntekurven (635 Schritte), 3 Tiefe-2-Zeugen, 9 Spurenschritte | vollständig repliziert |
| Pivotkontrollen, hog-Zensus | 6 Linien, Apex 46 / Pivot 78 | exakt reproduziert |
| Kanonisierung mit nauty | 1 496 Graphen | 1 496 Isomorphieklassen |
| Ableitungstabellen | ENDPOINTS.tsv, CURVES.tsv | konsistent |

**Nicht geprüft:** die 39 SQLite-Vollarchive liegen nicht bei. Damit sind
`archive_sha256`, die gemeldeten Archivklassenzahlen und die Vollständigkeit der
Nachbarschaftskataloge unbelegt. Die Tiefe-2-Aufzählungen selbst (14 000–21 000
Sequenzen je Quelle) habe ich nicht nachgezählt, nur ihre Zeugen. Es wurde kein
Suchlauf reproduziert und keine Trajektorie nachvollzogen. **Dies ist keine
vollständige Rohdatenprüfung.**

*Zusätzliche Daten, die ich für weitergehende Prüfungen bräuchte:* die
`archive.sqlite` der 24 Methodenjobs, um zu prüfen, ob die gemeldeten
Archivklassenzahlen (Pext 25 404 gegen PC 13 278 im Median) tatsächlich
verschiedene Isomorphieklassen zählen und nicht beschriftete Duplikate. Ohne sie
bleibt mein zentraler Vielfaltsbefund auf Endpopulationen und Endpunkte gestützt,
und aus Endpopulationen leite ich keine Archivaussagen ab.

---

## A. Eigenständige Befundbewertung

### A.1 Was trägt

| Behauptung im BERICHT | Mein Befund |
|---|---|
| 39 Jobs, 116,946299891 neue Such-CPU-h, 1,366082840 h Hilfs-CPU | exakt reproduziert, alle Gruppenkontingente eingehalten **[G]** |
| Hauptvergleich bei 4 CPU-h: bester W P 2110 / PC 2127, Median 2123 / 2136,5, Paare 12 : 0 | exakt **[G]** |
| Rekorde W 2102 (P), 2107 (PC), L1 2380, Linf (2, 216, 2468) unverändert | exakt; (2, 216, 2468) ist unter der deklarierten Linf-Ordnung zugleich der global beste Eintrag des Pakets **[G]** |
| TC-Fortsetzungen: kein W unter 2141 | exakt, aber irreführend knapp formuliert — siehe A.2 **[G]** |
| Ernte: 192 Datenbanken, 1 515 Zeilen, 411 Graphen, 414 Abstiege, 10 Tiefe-2 | exakt, Startbank unverändert **[G]** |
| AUDIT PASS, 1 282 Graphen in 3 022 Einträgen | reproduziert; mein Umfang ist mit 1 496 / 9 827 ein echter Oberbereich, weil `verify_results.py` nur `result.json` und `HARVEST.json` durchläuft **[G]** |
| „Isomorphieklassen nicht unabhängig neu kanonisiert" | **diese Einschränkung kann entfallen.** Mit nauty sind die 1 496 Graphen paarweise nicht isomorph, und die Klassenkennungen des Laufs sind auf dieser Menge ein gültiges Invariant **[G]** |
| WSL-Monotonuhr weicht ab | quantifiziert: **8,06 % zu langsam**, last­unabhängig (1 und 18 Worker praktisch gleich). Die Entscheidung, ETA auf den Windows-Zeitgeber und Budgets getrennt auf getrusage/wait4 zu stützen, ist damit bestätigt **[G]** |

### A.2 Was nicht trägt

**Die drei TC-Fortsetzungen sind ein Datenpunkt, nicht drei.** Sie enden auf dem
*identischen beschrifteten Graphen* und waren dort schon nach der ersten Stunde
des Originallaufs. In den drei zusätzlichen CPU-h je Job kam **kein einziger neuer
Kurvenpunkt** hinzu. Die letzte Verbesserung liegt bei 19,7 / 19,4 / 19,8 CPU-Sekunden,
und die drei Kurven sind trotz verschiedener RNG-Seeds bis auf 1–2 % zeitgleich:
2180 → 2169 → 2164 → 2159 → 2155 → 2154 → 2153 → … → 2141. TCs Abstieg aus dem
HoG-Gründer ist seed-unabhängig deterministisch. 9 CPU-h haben rund 46 700
Iterationen ohne eine einzige Verbesserung geliefert. **[G]**

**Ertragslose Kontingente werden nicht benannt.** Die vier Linf-Rekordjobs haben
je genau einen Kurvenpunkt, nämlich den Startpunkt: 8 CPU-h ohne Bewegung. Dazu
R-P--L1-00 mit 2 CPU-h ohne Bewegung und die 9 CPU-h TCx. Zusammen **rund 19 der
117 neuen Such-CPU-h (16 %) ohne einen einzigen neuen Kurvenpunkt.** Bei TCx und
Linf war das vorher absehbar: beide Startpunkte waren schon als exakte lokale
Minima des jeweiligen Katalogs bekannt. **[G]**

**Ein nicht erwähnter Confounder im Hauptvergleich.** Die erste Stunde von Pext
wurde im Originallauf vom 21.09. unter dessen Workerbelegung gemessen, die übrigen
drei in diesem Lauf bei 16,64 CPU-s je Hostsekunde. Die Abrechnung in CPU-Sekunden
ist korrekt, aber der Durchsatz je CPU-Sekunde kann sich mit SMT- und Cache-Konkurrenz
unterscheiden. Bei 12 : 0 ändert das die Richtung nicht; bei knapperen künftigen
Vergleichen muss es vermieden werden, indem beide Arme im selben Lauf neu starten. **[H]**

**Eine irreführende Feldbezeichnung.** `EVALUATION.json` nennt das Feld
`auxiliary_cpu_seconds_at_evaluation`, enthält aber die nach der Ernte
aktualisierten Werte (harvest 1 082,5 statt der zum Auswertungszeitpunkt
protokollierten 0). Der Zahlenwert im BERICHT ist der richtige. **[G]**

### A.3 Kosten und Stagnation: warum PC verliert

Das ist der inhaltlich wichtigste Befund, und er steht so nicht im BERICHT.

| Arm | Episoden/CPU-h | ausgewertet/CPU-h | adoptiert/CPU-h | endpoint_classes (Median) | archive_classes (Median) | bester W |
|---|---:|---:|---:|---:|---:|---:|
| Pext (P) | **406,6** | 778 698 | 7 078 | 439 | 25 404 | 2110 |
| PC | **197,0** | 701 271 | 3 665 | 298 | 13 278 | 2127 |
| R-P--W | 413,5 | — | 7 157 | 216 | 12 835 | **2102** |
| R-PC--W | 184,8 | — | 3 501 | 145 | 6 551 | 2107 |
| TCx | — (Tabu) | 799 762 | 3 893 | **9** | 15 591 | 2141 |

PC halbiert praktisch jede Durchsatzgröße. Der Mechanismus steht im Quelltext:

- `kernel.catalogue(rows, include_cycles, guard)` liefert **sequentiell und
  vollständig** apex, dann pivot, dann — nur für PC/TC — cycle3. Der exakte
  Abstieg wertet den gesamten Strom aus und wählt den besten verbessernden Zug. **[G]**
- `strategy.cycle_moves` baut aus 231 Dreiecken 693 orientierte Dreiecke und
  läuft eine **693²-Doppelschleife** zur Verträglichkeitsvorberechnung, bei jedem
  Aufruf, unabhängig davon, ob cycle3 etwas liefert. Zum Vergleich: der
  Pivotkandidatensatz hat 4 158 Elemente, der Apex-Paarsatz C(231,2) = 26 565. **[G]**
- Folge: PCs Abstiegsschritt ist echt stärker (größere Nachbarschaft,
  Bestverbesserung), kostet aber ungefähr das Doppelte. Die Daten sagen, dass der
  Aufpreis sich bei diesem Budget nicht rechnet. **[G]**

Entscheidend ist die Lesart: cycle3 **funktioniert**. In PC sind 31,9 % aller
adoptierten Züge cycle3, deutlich über den 20 % Perturbationsgewicht, der Operator
wird also auch im Abstieg tatsächlich gewählt. Und der einzige bekannte
Zwei-Schritt-Zeuge auf W = 2116 braucht cycle3 als zweiten Schritt — ich habe ihn
aus dem Ausgangsgraphen selbst nachgerechnet. **Getestet wurde bisher nur „cycle3
in jedem Abstiegsschritt".** Die naheliegende billige Variante — cycle3 nur am
exakten AP-Minimum als Fluchtoperator — ist nie ausprobiert worden. Aus 12 : 0
zu schließen, der Dreierzyklus sei verworfen, wäre überzogen. **[G] / [H]**

Derselbe Mechanismus erklärt TC: 56 % des Auswertungsbudgets in einen Operator
mit 0,095 % Annahmequote, ein Zehntel der Pivotquote. **[G]**

### A.4 Herkunft, Vielfalt und Verwandtschaft

**Die Gründerbank ist nominell.** Alle 39 Jobs starten ihre Bestwertverfolgung
von nur **4 verschiedenen Graphen**; 27 davon von einem einzigen
(`endpoint_W2180`, W = 2180). Die übrigen sind die drei Rekordsaaten. **[G]**

**Alle 39 Bestwerte tragen `family = HoG`.** Die konstruierten Familien erscheinen
in Endpopulationen (Z33_lift 33 von 624, triangle_packing 3) und in der
Elternschaft (Z33_lift 1 093 und triangle_packing 765 von 37 553, zusammen 5 %),
aber **keine davon hat je einen Bestwert geliefert**. **[G]**

**Symmetrie verschwindet sofort.** Von 1 496 Graphen sind 1 486 starr. Die 10
Ausnahmen haben alle |Aut| = 33 und sind genau die konstruierten Gründer
(`gen-lambda-*`, `codex_v01_c08`). Ihre Scores liegen bei W = 2475 bis 2838, also
weit vom Frontbereich 2102–2182. Sobald ein Zug angewandt wird, ist die Symmetrie
weg. Der gesamte Suchaufwand fand im starren, HoG-abstammenden Becken statt. **[G]**

**Beschriftet verschieden ≠ verschiedene Suchregion.** Die 24 Methodenendpunkte
sind paarweise nicht isomorph, aber sie liegen dicht beieinander: die paarweise
Kantendistanz der 12 P-Endpunkte hat den Median 183 von 693 Kanten, und jeder
Endpunkt ist vom gemeinsamen Start 72 bis 148 Kanten entfernt (Median 116). Der
W = 2102-Rekord liegt 164 Kanten von hog57338 entfernt, also sind 24 % der Kanten
verändert. Das ist eine ausgedehnte, aber zusammenhängende Nachbarschaft, keine
Menge unabhängiger Regionen. **[G]**

**PC verliert zusätzlich Vielfalt.** Zwei PC-Jobs mit verschiedenen Seeds
(PC--W-03 und PC--W-10) enden auf dem identischen beschrifteten Graphen; bei P
kommt das nicht vor. Dazu 32 % weniger endpoint_classes und ein halb so großes
Archiv. **[G]**

**Die Normen sind im Frontbereich gegenläufig.** Über alle 1 496 Graphen sind
W und F positiv korreliert (+0,58), über die 39 Endpunkte aber **negativ (−0,57)**.
Das quantifiziert den Satz des BERICHTs, die Normen seien nicht austauschbar: nahe
der Front drückt jede W-Verbesserung F nach oben. Der beste W-Graph (2102) hat
F = 3260, das globale F-Minimum (2836) hat W = 2182. **[G]**

### A.5 Welche Aussagen über Lösungsnähe unzulässig wären

- **„W = 2102 von 4 851 Paaren, also 43 % — wir sind fast da."** Unzulässig. Das
  Residuenhistogramm des Rekords ist {−2: 159, −1: 921, **0: 2 749**, +1: 820,
  +2: 187, +3: 15}. Die Gründer liegen bei 51–58 %; 300 CPU-h haben den Anteil um
  rund 8 Prozentpunkte gesenkt. Der Zusammenhang zwischen W und Lösungsabstand ist
  nicht linear und nicht bekannt. **[G]**
- **„Der Grenzertrag wird schon wieder anziehen."** Nichts in den Daten stützt
  das. Über 3 600 → 7 200 → 10 800 → 14 400 CPU-s fällt der Median um 10,5 / 4,0 / 3,5,
  und der beste Wert der 12 P-Jobs steht seit der Marke 7 200 unverändert bei 2110 —
  die letzten 24 CPU-h haben keinen neuen Bestwert erzeugt. **[G]**
- **„Linf = 2 ist nahe an einer Lösung."** Unzulässig. Dieser Punkt hat W = 2252,
  also mehr Fehlpaare als jeder Methodenendpunkt. Ein kleines Maximum des Residuums
  bedeutet nicht wenige Residuen. **[G]**
- **„F = 2836 ist ein lokales Minimum, also ein struktureller Kandidat."**
  Nur im *deklarierten* Katalog apex ∪ pivot. Über andere Züge ist nichts bekannt. **[B]**
- **„1 496 verschiedene Isomorphieklassen zeigen breite Exploration."** Die Zahl
  stimmt, aber sie misst beschriftete Vielfalt in einer Nachbarschaft, nicht die
  Zahl abgesuchter Regionen (siehe A.4). **[G]**
- **Jede Aussage über die Vollständigkeit der abgesuchten Nachbarschaften** ist
  ohne die SQLite-Archive unbelegt. **[U]**

---

## B. Entscheidung und Voruntersuchungen

**Ich empfehle keinen größeren Hauptlauf.** Begründung in einem Satz: der
gemessene Grenzertrag ist logarithmisch, und keine Verdopplung des Budgets, die
auf dieser Maschine realistisch ist, bringt die Suche auch nur in die Nähe einer
Lösung. Mehr Stunden derselben Bauart sind die eine Fortsetzung, die die Daten
ausschließen.

Ich empfehle stattdessen **drei Voruntersuchungen mit zusammen 44 Such-CPU-h und
2 h Hilfskontingent**. Jede beantwortet genau eine Frage, deren Ausgang eine
Entscheidung ändert. Das beiliegende `MANIFEST_vorpruefungen.json` enthält sie
maschinenlesbar mit exakt aufaddiertem Budget.

Vorab, ohne neue Rechenzeit, ist bereits erledigt: die Grenzertragsanpassung, die
Kosten- und Durchsatzanalyse, die Kanonisierung und die Vielfaltsauswertung. Sie
stecken in `analyse_run.py` und `check_isomorphism.py` und sind reine
Nachauswertung des vorhandenen Exports.

### V1 — cycle3 als Fluchtoperator statt als Abstiegsschritt · 16 CPU-h

**Offene Frage:** Ist PCs Nachteil Kosten oder Qualität?
**Minimaler Aufbau:** `kernel.catalogue()` ruft `cycle_moves` nur dann, wenn
apex ∪ pivot keinen verbessernden Zug liefert, also genau am exakten AP-Minimum;
im gewöhnlichen Abstiegsschritt nie. Sonst unverändert. Arm `PCesc`, Start
`endpoint_W2180`, die 8 ersten der bestehenden gepaarten Methoden-Seeds,
je 7 200 CPU-s.
**Benötigte Daten:** keine neuen; Kontrolle sind die gespeicherten Pext- und
PC-Werte an der Marke 7 200 CPU-s.
**Entscheidungskriterium:** Episoden je CPU-Stunde ≥ 0,90 × Pext **und** gepaarte
Siege nach (W, L1) gegen Pext ≥ 4 von 8.
**Wenn ja:** cycle3 geht als Fluchtoperator in die Konfiguration jedes weiteren
Laufs — zu vernachlässigbaren Kosten, weil er nur am Minimum gerufen wird.
**Wenn nein:** cycle3 wird ersatzlos gestrichen; alles Weitere läuft auf
apex ∪ pivot, was das Budget jedes künftigen Laufs faktisch verdoppelt.

### V2 — Frontier-Seeding gegen Gründer-Seeding · 12 CPU-h

**Offene Frage:** Ist das Fortsetzen ab der Bestmarke je CPU-Stunde produktiver
als der Neustart ab dem Gründer? Der Lauf legt das nahe (6 CPU-h → 2102 gegen
36 CPU-h → 2110), aber die Rekordspur hatte einen besseren Startpunkt, also ist
der Vergleich noch nicht sauber.
**Minimaler Aufbau:** Arm P, Starts die drei Endpunkte W = 2102 / 2107 / 2108,
je zwei Replikate, je 7 200 CPU-s.
**Entscheidungskriterium:** Median W nach 7 200 CPU-s, und erreicht mindestens
ein Job W < 2102?
**Wenn ja:** jeder weitere Lauf startet überwiegend an der Frontier; die
Gründerbank dient nur noch der Diversität.
**Wenn nein:** die Frontier ist ausgeschöpft. Dann ist das Becken abgesucht, und
ein größerer Lauf gleicher Art ist endgültig nicht zu rechtfertigen — das ist ein
klares, verwertbares negatives Ergebnis.

### V3 — Gibt es außerhalb des HoG-Beckens überhaupt etwas? · 16 CPU-h

**Offene Frage:** Erreicht eine Suche aus nicht-HoG-Starts in vergleichbarer Zeit
überhaupt den Bereich W < 2200? Bisher ist das schlicht nie gemessen worden: die
konstruierten Gründer sind in 300 CPU-h nie zu einem Bestwert geworden, aber sie
waren auch nie Startpunkt eines eigenen Jobs.
**Minimaler Aufbau:** Arm P, acht Starts ohne HoG-Abstammung — sechs
`gen-lambda`-Gründer, `endpoint_Linf2_N262` und ein triangle_packing-Vertreter
aus den Endpopulationen —, je 7 200 CPU-s.
**Entscheidungskriterium:** absolut, erreicht irgendein Job W < 2200?
**Wenn ja:** Vielfalt ist ein lebender Hebel; ein Hauptlauf bräuchte Inselstruktur
und eine echte Gründerbank.
**Wenn nein:** die Gründerbank wird auf die HoG-Linien reduziert. Das spart in
jedem weiteren Lauf Budget und beendet eine Scheindiversität, die bisher in jeder
Planung mitgeschleppt wurde.

### Was ich ausdrücklich nicht vorschlage

- **Keine Wiederholung des Methodenvergleichs mit größerem Budget.** Sein Ergebnis
  ist klar, und A.3 erklärt es besser, als eine Wiederholung es könnte.
- **Keine weitere TC-Spur.** Drei Seeds, eine Trajektorie, 20 CPU-Sekunden
  Fortschritt. Ohne Änderung an der Tabu-Regel selbst ist jede weitere TC-Stunde
  verloren.
- **Keine weiteren Linf-Rekordjobs** vom bekannten (2, 216, 2468)-Punkt. Vier
  Jobs haben dort 8 CPU-h verbracht, ohne einen Zug zu adoptieren.
- **Keine Archivernte mehr im selben Umfang.** 1 CPU-h für 411 Graphen mit
  bestem Ergebnis W = 2121, schlechter als die Suche. Sie schadet nicht, aber sie
  trägt nichts mehr bei.

---

## C. Hauptlauf: Bedingungen statt Spezifikation

Ich lege bewusst keine vollständige Bauanleitung vor, weil meine Auswertung
gegen einen Hauptlauf dieser Bauart spricht. Statt dessen die Bedingungen, unter
denen ich dazu überginge, und was die jeweilige Bedingung erzwingt.

**Bedingung 1 — die Grenzertragskurve ändert ihre Steigung.** Eine Maßnahme aus
V1–V3 müsste den Median W bei 7 200 CPU-s um mehr als **zwei Standardabweichungen
der Jobstreuung** verbessern, also um mehr als rund 18 W gegenüber dem
gemessenen Pext-Median 2130,5. Das ist bewusst hoch angesetzt: alles darunter ist
vom logarithmischen Trend nicht zu unterscheiden und verlängert nur eine Kurve,
die ohnehin nicht zum Ziel führt. Tritt das ein, ist die betreffende Maßnahme
der Kern des Hauptlaufs, und die Spezifikation schreibt sich aus dem Ergebnis
weitgehend von selbst: Seeding-Politik aus V2, Operatorsatz aus V1, Inselstruktur
aus V3.

**Bedingung 2 — V3 findet einen zweiten Bereich.** Erreicht ein nicht-HoG-Start
W < 2200, ist die Frage „ein Becken oder viele" offen und damit wieder
interessant. Dann bräuchte der Hauptlauf ein Inselmodell mit getrennten Archiven
je Herkunftsfamilie, Migration erst nach nachgewiesener Stagnation, und ein
Diversitätsmaß auf Isomorphieklassen statt auf beschrifteten Graphen —
die Kanonisierung dafür liegt in `check_isomorphism.py` und kostet rund 4 ms
je Graph, ist also im laufenden Betrieb bezahlbar.

**Bedingung 3 — ein anderes Ziel wird plausibel gemacht.** Die gegenläufige
Korrelation von W und F nahe der Front (A.4) ist der einzige Hinweis im ganzen
Paket auf eine qualitativ andere Landschaft. Der W-getriebene Lauf hat sich von
F = 2836 systematisch entfernt, bis F = 3260 beim W-Rekord. Ein Lauf mit einer
Pareto-Front über (W, L1, F, Linf) statt einer einzelnen lexikographischen Ordnung
ist ein echter Mechanismuswechsel und nicht getestet. Ich schlage ihn hier
**nicht** vor, weil ich dafür keine Evidenz habe, die über die Korrelation
hinausgeht — aber er ist der Kandidat, den ich zuerst prüfen würde, falls V1–V3
negativ ausfallen und die λ-Spur trotzdem fortgesetzt werden soll.

**Was in jedem Fall gilt,** sobald ein Hauptlauf gebaut wird:

1. Beide Vergleichsarme starten **im selben Lauf** neu, keine Fortsetzung aus
   einem früheren Lauf als Vergleichsarm (Confounder aus A.2).
2. Die primäre Messgröße wird **vor** dem Start festgelegt und enthält neben dem
   Zielwert die Episoden je CPU-Stunde, damit Kosten- und Qualitätseffekte
   trennbar bleiben — genau das fehlte diesem Lauf.
3. Vorab definierte Zwischenbilanz nach einem Viertel des Budgets mit Abbruchregel.
4. Rekordsuche und Methodenvergleich bleiben getrennt, wie schon in diesem Lauf.
5. Kein Operator wird in den Abstiegsschritt aufgenommen, ohne dass seine
   Enumerationskosten gegen die Annahmequote gemessen wurden.

---

## D. Offene Risiken und Unsicherheiten

1. **Die Extrapolation ist eine Extrapolation.** Vier Messpunkte aus einem Lauf,
   angepasst über eine Größenordnung CPU-Zeit. Dass die Kurve bei 100-facher Zeit
   noch logarithmisch ist, ist nicht bewiesen, nur die naheliegendste Lesart. Sie
   müsste brechen, damit Skalierung sinnvoll wird — und nichts in den Daten
   deutet auf einen Bruch hin. **[H]**
2. **Archivvielfalt unbelegt.** Ohne SQLite bleibt offen, ob Pexts doppelt so
   große Archivklassenzahl echte Isomorphieklassen zählt. Mein Vielfaltsbefund
   stützt sich auf Endpunkte und Endpopulationen, die ich kanonisiert habe. **[U]**
3. **Die Rolle der Symmetrie ist ungeklärt.** Alle 10 symmetrischen Graphen haben
   |Aut| = 33, alle liegen weit von der Front, und keine Suche hat je in ihrer
   Nähe gearbeitet. Ob symmetrieerhaltende Suche auf 99 Knoten ein sinnvoller
   Mechanismus wäre, kann dieser Lauf nicht beurteilen, und ich beurteile es
   hier auch nicht. V3 misst nur, ob diese Starts überhaupt konkurrenzfähig sind. **[U]**
4. **V1 könnte am Aufwand scheitern, nicht an der Sache.** Der Eingriff in
   `kernel.catalogue()` ist klein, berührt aber den eingefrorenen 0.2.0-Pfad. Er
   gehört in eine Kopie, wie PC es schon vormacht, und der Originalworker bleibt
   unangetastet. **[H]**
5. **Der 8-%-Uhrenversatz reproduziert einen älteren Befund.** In einem früheren
   Review dieses Projekts war von rund 9 % Frühauslösung die Rede. Dass beide
   Messungen so nahe beieinander liegen, spricht für einen systematischen
   WSL2-Effekt und nicht für einen Einzelfall. Das ist keine Fehlerquelle des
   Laufs — die Budgets laufen über getrusage —, sollte aber für jede künftige
   Wanduhr-Aussage vermerkt bleiben. **[G] / [H]**
6. **Mehrfachvergleiche.** Der Lauf hat sechs Gruppen und mehrere Zielnormen
   nebeneinander ausgewertet. Die 12 : 0-Aussage ist dafür robust genug, aber
   jede künftige knappere Aussage braucht eine vorab festgelegte primäre Größe.

---

## Beiliegende Dateien

`reviewer_lambda_followup_20260923_pruefsatz.zip` — flaches Archiv mit
`indep.py` (eigener graph6-Decoder/Encoder, λ-Prüfung, fünf Scores), den sechs
Prüf- und Analyseskripten, ihren Ergebnis-JSONs, `MANIFEST_vorpruefungen.json`
und einer README mit Eingabehashes, Laufzeiten und den Grenzen des Prüfsatzes.
Die Skripte sind deterministisch und verwenden keinen Zufallszahlengenerator.
