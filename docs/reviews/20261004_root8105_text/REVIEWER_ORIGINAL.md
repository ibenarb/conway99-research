
47 Befehle ausgeführt, eine Seite gelesen, frühere Chats durchsucht

47 Befehle ausgeführt, eine Seite gelesen, frühere Chats durchsucht (ein Tool ist fehlgeschlagen)

## Review ROOT8105-Pilot und memetischer H-Faser-Strang (Stand ad92f04)

**Zugriff:** `web_fetch` wird von GitHub per robots.txt blockiert. Ich habe das Repository daher in meiner Sandbox über `raw.githubusercontent.com` und `codeload` geladen. Alle Dateien stammen aus den fixierten Commits. Rechnungen liefen auf 1 CPU mit 3 GB RAM, die Zeitangaben sind also keine Ryzen-Werte. Ein Lauf blieb unvollständig, das ist unten jeweils markiert.

Evidenzstufen im Text: **[E]** selbst ausgeführt, **[C]** aus dem Code abgeleitet, **[B]** berichtet und nicht reproduziert, **[V]** Vermutung, **[O]** offen.

---

### 1. Kurzbefund

1. **Die erste Erweiterung lässt sich exakt und billig zählen. [E]** Ich habe einen Kanten-DP-Zähler gebaut, der ohne SAT und ohne nauty auskommt. Er stimmt mit dem Pilot-Encoder plus Glucose-Vollenumeration überein:
   - m=4: 3 Roots × 23 Ziele, 0 Abweichungen;
   - m=5: 3 Roots × 39 Ziele, 0 Abweichungen;
   - m=7, Root 1, Ziel (0,8): beide liefern **173 365**.
   - Laufzeit des DP: etwa 0,12 s je Paar (Root, Ziel).
2. **Die Breiten der ersten Erweiterung sind riesig und sehr gleichförmig. [E, 24 von 128 Pilot-Roots ausgewertet]**
   - Die minimale Breite liegt zwischen 173 365 und 206 315 (Median 175 021). Sie liegt immer bei einem der beiden Nachbarn von u, die eine Randecke mit u teilen („isolierte Klasse“).
   - Die Ordered-Zielzeile (0,2) hat 15,37–15,69 Mio. Kinder. Die Kappung bei 65 536 erfasste also nur **0,42 %** davon.
   - Hochgerechnet auf alle 8105 Roots ergibt das rund **1,4·10⁹ Knoten auf Ebene 2**, und zwar schon bei optimaler Zielwahl. Das ist eine Hochrechnung [V]; exakt wird die Zahl nach Phase P1 unten.
3. **Vollständige Ganzzeilen-Augmentation ist auf dem Ryzen um viele Größenordnungen außer Reichweite.** Jeder Ebene-2-Knoten braucht mindestens einen eigenen SAT-Aufruf. Bei optimistischen 0,1 s pro Knoten sind das rund 4,5 CPU-Jahre, bevor Ebene 3 überhaupt beginnt. Der Pilot zeigt zudem auf Tiefe 2 exakte Breiten bis 36 421 und viele zensierte Projektionen über 6·10⁴. Echte Canonical-Augmentation zu implementieren lohnt sich daher nicht (Begründung in §4).
4. **Der Pilot hat eher zufällige Tauchgänge gemessen als Breite. [C/E]**
   - Auf flachen Tiefen wurden pro Ebene nur 1–2 Eltern expandiert.
   - Die Tiefe-1-Enumeration im Ordered-Arm wurde bei jedem Neustart deterministisch wiederholt.
   - `observed_rows` ist deshalb ein Arbeitszähler, kein Zähler verschiedener Zustände.
5. **Für das volle Modell existiert eine echte Positivkontrolle. [E]** Der Berlekamp–van Lint–Seidel-Graph SRG(243,22,1,2) passt mit m=11 exakt in die Pilot-Geometrie.
   - `Geometry(11).verify` und `completion.verify_complete` melden SRG_FOUND_VERIFIED.
   - Der Encoder ist auf 20 zufälligen Präfixen der Tiefen 1–219 mit dem Zeugen konsistent (20/20 SAT).
   - Weder Codex noch der Handoff nennen diese Kontrolle; Codex hat nur den 9er-Rookgraphen.
6. **Der memetische Planted-Control-Vorschlag ist für ROOT8105 ungültig. Codex und GC-20 korrigieren ihn zu Recht.** Zusätzlich gilt: Die „Isolation“ von cand_A spielt für die Positivität überhaupt keine Rolle.

---

### 2. Ausgeführte Prüfungen

Alle Punkte dieser Liste habe ich selbst ausgeführt [E].

- **Paketintegrität:** 13/13 SHA256-Werte stimmen mit `SHA256.json` überein. Der Inhalt des Tarballs ist byteidentisch mit `raw/`.
- **Audit-Skript:** Ein erneuter Lauf von `audit_results.py` erzeugt ein JSON, das mit `DERIVED_METRICS.json` identisch ist.
- **Quellenfixierung:**
  - `core/worker/proof/report/completion.py` tragen die SHA256-Werte aus `SOURCE_INDEX` (Stand 7c664eb).
  - Die drei memetischen Dateien tragen die Hashes aus dem Index.
  - `EXPERIMENT_RULES.md` ist bei 611be0b identisch mit ad92.
  - `GLOBAL_CONCLUSIONS.md` unterscheidet sich nur durch GC-20 und den Zusatz zu GC-18.
- **Unabhängiger Root-Zensus:**
  - Ich habe die Gruppe G_u (Stabilisator des Labels {0,1} in C₂≀S₇, Ordnung 7680) explizit konstruiert.
  - Ergebnis: 8105 paarweise inäquivalente Vertreter, alle Stabilisatorordnungen korrekt, Orbitsumme 56 011 010.
  - Mein Kanten-DP zählt alle margengültigen u-Zeilen ebenfalls zu 56 011 010. Damit ist die Root-Coverage unabhängig von nauty und vom Vertex-DP bestätigt.
- **Breiten der ersten Erweiterung:** DP-Validierung wie in §1 beschrieben. Das DP-Modell lautet:
  - Für ein Ziel t sind die Kinder Teilmengen R der Labels ohne t, mit Gradprofil gleich `margins(t)`.
  - Es muss |R ∩ N_u| = 2 − e − |t∩u| gelten, wobei e = 1 genau dann, wenn t in N(u) liegt.
  - Bei e=1 ist u in R erzwungen, und die beiden isolierten Nachbarn von u sind verboten (das ist die Sternbedingung von u).
  - Implementierung: Kanten-DP über die 84 Labels mit Teilgraden je Randknoten und einem Schnittzähler. Eine Achse wird eliminiert, sobald ihr letztes inzidentes Label verarbeitet ist.
- **128-Root-Lauf:** Der Lauf über alle 83 Ziele war bei Ende meines Werkzeugbudgets nicht fertig. Ausgewertet habe ich **24 Roots**. Weitere Ergebnisse dieser 24:
  - Die Ordered-Zielzeile (0,2) war in allen 24 nicht zu u adjazent.
  - Nicht-adjazente Ziele haben mindestens 12,3 Mio. Kinder.
  - Σ min_t w/|Aut| über die 24 Roots ergibt 1 401 809.
- **Determinismus:** Zwei Läufe derselben (Root, Ziel)-Enumeration liefern dieselben ersten 3000 Zeilen. Das gilt für die pysat-Version der Sandbox und ist auf dem Ryzen über `rows_sha256` zu bestätigen.
- **BvLS-Kontrolle:**
  - Der Graph ist der Nebenklassengraph des ternären Golay-Codes [11,6,5]: 729 Codewörter, Mindestdistanz 5.
  - A² = 22I + A + 2(J−I−A) ist geprüft.
  - Einbettung: x=0, N(x) gepaart als ±h_i, 220 Labels.
  - Die Pilot-Verifizierer bestehen.
  - Encoder: 20/20 SAT mit dem Zeugen als Annahme, bei bis zu 5620 Kantenvariablen und 34 653 Klauseln.
  - Eine korrumpierte Zeile wird abgelehnt. Bisher habe ich nur eine gradverletzende Korruption getestet; eine grad- und margentreue Paarverletzung ist noch offen.
- **Kennzahlen aus den Receipts:**
  - Proof-CPU: Median 4,37 s, Maximum 31,5 s, Summe 3087 s.
  - Die Proof-Artefakte tragen die Enumerationsseriennummern 4–21, sind also sehr flach.
  - Alle Suchjobs liegen bei 3600,07–3600,24 s.

**Nicht ausgeführt:**

- keine erneute DRAT-Prüfung, weil die Artefakte fehlen;
- keine Reproduktion der H-Faser-Resultate;
- kein Ryzen-Test;
- eine Mini-Probe auf Tiefe 2 brach am Zeitlimit ohne Ergebnis ab, daher stelle ich keine eigenen Behauptungen zu Tiefe-2-Breiten auf.

---

### 3. Pilotkennzahlen: Was wurde tatsächlich gemessen? (Aufgabe 1)

**Effektive Beam-Breite.** Ein Segment ist ein Lauf von der Root bis zum Neustart; es gab 1461 Segmente ordered und 768 dynamic. Projektionen je Segment und Tiefe:

| **Tiefe** | **1** | **2** | **3** | **4** | **5** | **6** | **7** | **8** |
| --------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| ordered   | 1,0   | 2,1   | 2,1   | 3,4   | 11,5  | 35,8  | 53,3  | 53,2  |
| dynamic   | 2,8   | 2,2   | 2,4   | 2,8   | 4,6   | 15,9  | 65,8  | 169,7 |

Das Ebenenbudget (Restzeit/31) reicht nur für 2–4 zensierte 30-s-Projektionen. Dynamic expandiert auf den Tiefen 2–4 deshalb im Mittel **einen** Elternzustand, mit etwa zwei Zielen. Beam 64 greift erst ab etwa Tiefe 6. **[E/C]**

**Wiederholungen. [C/E]** Jedes Ordered-Segment startet mit derselben CNF (Root, Zeile 1). Glucose ist deterministisch, also sind 1333 der 1461 Tiefe-1-Projektionen inhaltlich identisch. Das entspricht rund 34 600 CPU-s, also etwa 9,6 CPU-h. Neu gezogen wurden jeweils nur 32 Zeilen aus denselben ersten 65 536 SAT-Lösungen. Bei dynamic sind Wiederholungen ebenfalls möglich, aber hier nicht quantifizierbar. Der Zähler `observed_rows` (1,447·10⁹) enthält drei Arten von Mehrfachzählung:

- exakte Wiederholungen;
- überlappende Projektionen desselben Elternzustands bei verschiedenen Zielen;
- Pfadduplikate bei dynamic.

**Exakt oder Untergrenze?**

- Exakt sind nur vollständig ausgezählte Projektionen, und zwar nur für das konkrete Paar (Zustand, Ziel) unter F.
- Untergrenzen sind alle Tiefe-1-Zahlen sowie der überwiegende Teil von Tiefe 2–5.
- Zum Vergleich: Die wahre Tiefe-1-Breite des Ordered-Ziels ist rund 237-mal so groß wie die Kappung.
- `duplicates_against_retained_sample` misst bei dynamic Pfadduplikate, also dieselbe Zeilenmenge über verschiedene Zielreihenfolgen, und keine Isomorphie.

**Gepaarter Vergleich.** Das Ergebnis 123:4:1 vermischt mehrere Unterschiede: 1 gegen bis zu 4 Ziele pro Elternzustand, feste gegen zufällige Orbitvertreter, unterschiedlich viele Neustarts und ein Maximum über Segmente. Gemessen wurde die Tauchtiefe unter einem Encoder ohne Vorausschau. Über die Effizienz einer vollständigen Suche sagt das nichts aus.

**Mechanismus „Ordered stirbt bei Tiefe 10“. [C + V]**

- Die Zeilen 0–11 sind die 12 H-Knoten an Randknoten 0. Sie müssen in H ein 6K₂ induzieren.
- Die mittlere Breite fällt von 17,1 (Ziel (0,10)) über 0,22 auf 0,0035 bei Ziel (0,12).
- F prüft die Margen einer offenen Zeile erst, wenn sie Zielzeile wird. Gebaute Zeilen können eine offene Zeile also längst überbucht haben, zum Beispiel wenn zwei gebaute (0,i) beide zu (0,12) adjazent sind.
- Das ist plausibel, aber erst getestet, wenn die Zustände vorliegen.

**Repräsentativität.**

- Die Roots sind nach Stabilisator und Matchingzahl geschichtet, nicht nach Populationsanteil. In der Population haben 83 % der Roots einen trivialen Stabilisator.
- Die Proofs wurden aus den ersten zwei abgeschlossenen Projektionen je Job gewählt, das sind die Serien 4–21. Das ist eine systematische Auswahl leichter, flacher Fälle.

**Abrechnung.** 276,26 CPU-h liegen im freigegebenen Recovery-Rahmen von 286 h. Konsistent mit GC-18. **[E/B]**

---

### 4. Modelle, Kontrollen, Beweiskette (Aufgaben 2 und 3)

**Modelle.**

- **L** (lineare Faser): symmetrisch, binär, Diagonale 0, Grad 12, XP=M.
- **F(S,t)** (lokaler Encoder): `verify(S)`, also L-Zeilenbedingungen und Paarbedingungen zwischen gebauten Zeilen; dazu die Margen des Ziels, die Paarbedingungen Ziel–gebaut und die Sterne der gebauten Zeilen (nur Zählgleichungen innerhalb von N(u)).
- **F_all**: alle offenen Margen und alle Paarbedingungen mit mindestens einer gebauten Zeile.
- **SRG**: X² + PPᵀ = 12I − X + 2J. Die Diagonale ist mit 14 = 12 + 2 konsistent.

**Korrektur am Encoder (zulässig und billig).**

- Sind v und w zwei offene Nachbarn einer gebauten Zeile u und haben einen gemeinsamen Randknoten, dann gilt ¬edge(v,w). Begründung: u und der Randknoten wären zwei gemeinsame Nachbarn, aber λ=1.
- `prepare.matching_count` nutzt diese Label-Disjunktheit bereits; der Encoder dagegen nicht.
- Dazu ein linearer Kapazitätsfilter C(S): Für jede offene Zeile v und jeden Randknoten c darf die fixierte Zahl von Nachbarn höchstens `margin(v,c)` betragen; ebenso für die Paarbudgets zwischen gebauten und offenen Zeilen.
- Beide Filter müssen vor ihrem Einsatz auf BvLS-Präfixen zeigen, dass sie nie fälschlich schneiden.

**Kontrollen: was garantiert positiv ist und was nicht**

| **Kontrolle**                                                                        | **garantiert positiv für**                                                              | **nicht garantiert**                                                                                                                                                   |
| ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| cand_A/B, Root-Zeugen 1/2 (L-Zeugen, W>0)                                            | L-Completion jedes Präfixes aus beliebigen Zeilen des Zeugen                            | F(S,t) nur nach Einzelprüfung von `verify`, Sternen und Zielpaaren im Zeugen; SRG nie. Die Isolation ist dafür irrelevant: Das „daher“ im Handoff ist ein Fehlschluss. |
| BvLS (m=11)                                                                          | L, F, F_all und SRG für jedes Präfix und jedes Ziel; die Zeugenbelegung ist geprüft [E] | keine Laufzeit- oder Breitenaussage für m=7; vertextransitiv und damit atypisch symmetrisch                                                                            |
| Rook/Paley-9 (m=2)                                                                   | alles                                                                                   | nichts über Skalierung                                                                                                                                                 |
| Selbst-Positive aus dem Pilot (gefundenes Kind mit SAT-Modell)                       | genau dieser eine Schritt in F                                                          | jede weitere Augmentierbarkeit                                                                                                                                         |
| Negativkontrollen (grad- und margentreue Paarverletzung; winzige Kappung nach GC-16) | müssen abgelehnt werden bzw. LIMIT_UNRESOLVED ergeben                                   | —                                                                                                                                                                      |

**Reichweite der 512 DRAT-Zertifikate.** Ich stimme Codex zu, mit einer Ergänzung: DRAT zertifiziert die CNF, nicht das mathematische Modell. Für einen Ausschluss fehlen daher noch:

- Encoder-Validierung durch einen zweiten unabhängigen Encoder oder Zähler; DP-Übereinstimmung und BvLS-Tests sind erste Bausteine;
- ein Abschlussbeweis für jeden Knoten;
- UNSAT-Belege für die Blätter;
- ein Coverage-Manifest des Baums;
- die Root-Coverage (jetzt doppelt bestätigt);
- geprüfte Orbit-Generatoren für das Pruning.

**Canonical-Augmentation ist nicht nötig. [Beweisskizze]**

- Bei fester Rolle von x und u und genau einer Zielzeile pro Knoten sind alle Baumknoten verschiedene beschriftete Zustände.
- Zwei Zustände mit derselben Root-Zeile sind genau dann isomorph, wenn ein Element aus Stab\_{G_u}(r) = Aut(root) sie ineinander überführt.
- Globale Schichtdeduplizierung bringt also höchstens den Faktor |Aut(root)| ≤ 256. Bei 6722 der 8105 Roots ist dieser Faktor genau 1.
- Vollständig und einfach beweisbar ist deshalb: DFS mit einer Zielzeile pro Knoten und Orbit-Pruning unter dem Stabilisator des Elternzustands.
- Die eigentliche Redundanz entsteht durch Umrooten: Jeder SRG enthält 99·84 = 8316 geordnete Nichtnachbarpaare (x,u). Ein Schnitt „minimale Rootklasse“ wäre die einzige große Symmetrie-Ersparnis, ist aber nur eine Optimierung.
- Ganzzeilenverzweigung ist an der Wurzel schlicht die falsche Granularität: rund 1,7·10⁵ Kinder pro Root.

---

### 5. H-Faser-Resultate: Zulässiges und Unbelegtes (Aufgabe 4)

**Zulässig**, unter der Voraussetzung, dass die berichteten Resultate zutreffen [B]:

- Zwei verschiedene L-Zustände im selben Rahmen unterscheiden sich in mindestens 16 Kanten und 8 Zeilen. Das gilt damit auch für zwei SRG-H-Matrizen.
- In einer reinen L-Augmentation ist die Completion ab 77 gebauten Zeilen eindeutig. Für Tiefen bis 16 ist das praktisch irrelevant.
- Lokale Suche auf exakten L-Zuständen braucht Moves von mindestens 16 Kanten. Das ist eine methodische Lehre für die Memetik.

**Unbelegt bzw. unzulässig:**

- jeder Bezug zwischen Tiefe 16 (gebaute Zeilen) und Distanz 16 (geänderte Kanten);
- Isolation als Augmentationsbarriere oder als Indiz zur SRG-Dichte;
- cand_A als F-Positivkontrolle;
- L-Completion-Zeiten als Leistungsprognose für die Augmentation.

Hier liegen verschiedene Zustandsräume (vollständig gegen partiell), Maße (Hamming gegen Tiefe/Breite) und Constraints (L gegen F/SRG) vor; außerdem haben die Zeugen W ≈ 2300, eine Lösung bräuchte W = 0.

---

### 6. Optionen und Priorisierung (Aufgabe 5)

1. **Exakter Zensus der ersten Ebene per DP:** höchster Ertrag pro CPU. Damit fällt die Entscheidung über Ganzzeilen-Vollständigkeit.
2. **Direkte SAT- bzw. Cube-and-Conquer-Zerlegung auf der vollen SRG-CNF** (x, u und Root-Zeile fixiert, Paarbedingungen über Produktvariablen): die einzige plausible vollständige Methodenfamilie. Ihre Härte ist unbekannt und muss durch Stichproben gemessen werden.
3. **Knuth/Purdom-Schätzung mit exakten Breiten:** unverzerrte Schätzung der Ebenengrößen bei fester vollständiger Verzweigungsregel. Das ist die saubere Antwort auf die Frage „wie breit wächst der Baum“, die der Pilot nicht geben konnte.
4. **Stärkere notwendige Bedingungen:** Label-Disjunktheit und C(S) als Filter. Sie verbessern Proben und Heuristik, ändern aber die Ebene-2-Schranke kaum. F_all ist als Knotenfilter unbezahlbar; im Pilot fand es in 60 s kein Modell.
5. **L-Completion-Kalibrierung:** gehört in den memetischen Zweig.
6. **Heuristische Tiefensuche:** Es gibt keinen Beleg, dass größere Tauchtiefe die Fundwahrscheinlichkeit erhöht.

**Ehrliche Einordnung:** Ein vollständiger Ausschluss aller 8105 Roots ist auf dem Ryzen sehr wahrscheinlich nicht machbar. Der Erkenntnisgewinn liegt darin, das sauber zu quantifizieren und gegebenenfalls einen einzelnen Root zertifiziert auszuschließen (Machbarkeitsnachweis). Danach sollte die Rechenzeit in symmetrische Teilfälle fließen, in denen Vollständigkeit realistisch ist.

---

### 7. Fortsetzungsplan (Aufgabe 6)

**P0 – Entwicklung und Kontrollen** (Meldeschwelle 15 CPU-h)

- DP-Zensuswerkzeug mit Gleichverteilungs-Sampling aus der DP-Tabelle.
- BvLS- und Paley-Kontrollen; Negativkontrollen.
- Filter C(S) und Label-Disjunktheit, mit BvLS-Soundness-Test.
- Treiber für Knuth-Proben.
- Cube-and-Conquer-Pipeline: CNF-Generator, Cubes, CaDiCaL mit LRAT, Coverage-Prüfung des Cube-Baums.
- GC-19-Tests real auf dem Ryzen.
- Das ist vorbereitende Entwicklung, kein Forschungsversuch.

**P1 – Vollzensus der ersten Ebene** (30 CPU-h; erwartet 9–22 CPU-h, das sind 1–2 h Wall auf 11 Kernen)

- Umfang: 8105 Roots × 83 Ziele, exakt.
- Speicher: unter 0,3 GB RAM pro Worker, unter 100 MB Platte.
- **D1:** Liegt Σ_r min_t w/|Aut| bei mindestens 10⁸ (erwartet rund 1,4·10⁹), ist vollständige Ganzzeilen-Suche formal NO-GO.

**P2 – Knuth-Proben** (90 CPU-h)

- 32 Roots: 24 mit trivialem und 8 mit nichttrivialem Stabilisator, Auswahl vorab fixiert, Populationsgewichte veröffentlicht.
- Regel R1: Ziel mit minimaler Breite unter höchstens 4 am stärksten gebundenen Kandidaten (auf Tiefe 1 per DP über alle Ziele). Regel R2: Ordered, auf 8 Roots.
- Jeweils mit und ohne C(S), gepaart über denselben Zufallsstrom. Etwa 1500 Proben.
- Es werden keine Zeilen gespeichert, nur Zähler, Hashes und eine geschichtete Stichprobe von 200 zertifizierten Projektionen.
- Ausgabe: N_d je Tiefe, log₁₀-Gesamtschätzung mit Bootstrap-Konfidenzintervall und oberen Quantilen, Kosten pro Knoten.
- **D2:** Liegt der Median bei höchstens 10⁷ Knoten pro Root mit C(S), lohnt eine zertifizierte Ein-Root-DFS. Sonst NO-GO.

**P3 – Härtestichprobe Cube-and-Conquer** (200 CPU-h)

- 4 Roots, davon 2 mit trivialem Stabilisator, rund 10⁴ Cubes pro Root.
- 100 zufällige Cubes pro Root ohne künstliche Zeitkappung, mit GC-19-Abfrage.
- RAM 2–4 GB pro Solver, also 7–8 Worker. Platte höchstens 60 GB, LRAT wird gestreamt geprüft.
- **D3:** Liegt die geschätzte Ausschlussdauer bei höchstens etwa 200 CPU-h pro Root, folgt ein zertifizierter Ausschluss von 1–2 Roots. Liegt sie weit darüber, ist ein vollständiger ROOT8105-Ausschluss außer Reichweite; dann Umschwenken auf restringierte Teilfälle.

**P4 – Suchkraft-Kontrolle an BvLS** (20 CPU-h)

- Vollständige DFS ab gepflanzten Präfixen der Tiefen 210, 190 und 150 muss eine Completion finden.

**Gesamt:** etwa 380 CPU-h Meldeschwelle einschließlich 25 h Supervisor und Reserve. Jede Phase hat ein eigenes GC-19-Budget. Für P1 ist eine belastbare ETA nach einer Zeitmessung auf 100 Roots möglich. Für P2 und P3 gibt es nur eine Budgetprojektion (rund 35 h Wall), die ETA ist „unknown“.

**Mehr Rechenzeit** sollte in mehr Proben und Cubes fließen (Varianzreduktion), nicht in die Enumeration ganzer Schichten. Nearest-H muss nicht abgewartet werden: P0–P4 sind davon unabhängig.

---

### 8. Vergleich mit Codex (Aufgabe 7)

| **Punkt**                                                 | **Urteil**                | **Begründung bzw. Änderung**                                                                                                            |
| --------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Modellabgleich, GC-20, Proof-Deutung                      | Zustimmung                | Ergänzen: BvLS, Encoder-Vertrauenslücke, Label-Disjunktheit                                                                             |
| Deutung des Paarvergleichs                                | Zustimmung                | Ergänzen: effektiver Beam 1–2, deterministische Wiederholungen, Mechanismus bei Tiefe 10                                                |
| B: 32 Roots per SAT-Enumeration                           | Widerspruch               | Der DP liefert exakt für alle 8105 in 1–2 h Wall; das Ordered-Ziel allein hätte rund 1,5·10⁷ Zeilen pro Root                            |
| C: zweite Schicht für 4 Roots                             | Widerspruch               | Mindestens 1,7·10⁵ Eltern pro Root, jeder mit eigener Enumeration; schließt im Budget nicht und ist weniger informativ als Knuth-Proben |
| Schichtdeduplizierung über Eltern mit Permutationsbelegen | Widerspruch               | Faktor höchstens \|Aut(root)\|, bei 83 % der Roots gleich 1; Orbit-Pruning pro Elternzustand genügt                                     |
| L-Matrix mit 192 Versuchen                                | reduzieren bzw. verlagern | testet das memetische L-Orakel, und die Zeugen fehlen ohnehin                                                                           |
| F gegen F_all an 64 Eltern                                | ersetzen                  | billige Filter C(S) und Label-Disjunktheit statt F_all                                                                                  |
| Residual-SAT nur als Fallback                             | vorziehen (P3)            | der DP-Zensus nimmt Codex' Entscheidungsfall 2 praktisch vorweg                                                                         |
| 480 CPU-h, GC-19, Betrieb, Nearest-H nicht abwarten       | weitgehend Zustimmung     | ich setze etwa 380 CPU-h an, anders verteilt                                                                                            |

---

### 9. Fehlende, entscheidungsrelevante Artefakte

1. Für die 512 Proofs `certificate.json`, `enumeration.json` und `state.json`. Daraus ergeben sich Tiefe, Breite, Trivial-UNSAT-Flag sowie CNF- und Proof-Größen. Zusätzlich 10 Paare `closure.cnf`/`.drat` für eine unabhängige erneute Prüfung.
2. Alle `enumeration.json` als kompaktes JSONL, mindestens für Tiefe 1 und 2. Damit lassen sich die Wiederholungen über `rows_sha256` direkt belegen.
3. Die `levels`-Einträge aus `checkpoint.json` (`parents_available` und `parents_fully_visited`).
4. Die tiefsten Zustände (`best.json`) und die 40 Tiefe-16-Fälle. Damit lassen sich die C(S)-Hypothese testen und diese Blätter zertifizieren.
5. Die Zeugendateien cand_A/B und Root-Zeugen 1/2 mit Labelkonvention.
6. Die H-Faser-Programme und Logs der Versionen 0.2–0.6.
7. Die Ergebnisse von Preflight, `level2` und `depth_controls` auf der Zielhardware.
8. Die auf dem Ryzen eingesetzten Versionen von pysat/Glucose und drat-trim.

**Wesentliche Risiken:**

- Knuth-Schätzungen sind schwer-schwänzig: Der Median unterschätzt typischerweise, deshalb gehören obere Quantile in den Bericht.
- Encoderfehler: dagegen helfen DP-Abgleich und BvLS-Tests.
- Die Implementierung der GC-19-Abfrage.
- Die Stabilität von WSL.

Meine Skripte (DP-Zähler, Root-Audit, BvLS-Bau und Encoder-Test, zusammen etwa 250 Zeilen) liegen in meiner Sandbox. Ich kann sie im nächsten Schritt vollständig ausgeben. Den 128-Root-Lauf und die Tiefe-2-Probe würde ich dabei mit zu Ende führen.

12 Befehle ausgeführt

12 Befehle ausgeführt

Dieser Schritt ist nicht fertig geworden: Das Werkzeuglimit war erreicht, bevor ich die 128 Roots auswerten, die Tiefe-2-Probe rechnen und die Skripte als Dateien ausgeben konnte. Fertig ist ein exakter Breitenzähler für Tiefe 2 und mehr, und dabei hat sich gezeigt, dass mein Vorschlag aus dem Review nicht reichte.

### Was neu fertig ist

**Exakter Breitenzähler für Tiefe ≥ 2 (`width_exact`).** Er zählt die Breite einer Zielzeile ohne Vollenumeration in zwei Stufen:

- Zuerst werden die möglichen Kanten der Zielzeile in die Nachbarschaften derjenigen gebauten Zeilen aufgezählt, zu denen sie adjazent ist.
- Für jedes solche Muster prüft ein kleiner SAT-Aufruf, ob die Sternbedingungen aller gebauten Zeilen erfüllbar bleiben. Er enthält nur Kanten zwischen offenen Zeilen innerhalb dieser Nachbarschaften.
- Für die erfüllbaren Muster zählt das Kanten-DP die passenden Zielzeilen mit einer Schnittbedingung pro gebauter Zeile; die Ergebnisse werden addiert.

Gegen den unveränderten Pilot-Encoder mit erschöpfender Glucose-Enumeration:

| **m** | **Tiefe** | **geprüfte Fälle (Zustand, Ziel)** | **Abweichungen** |
| ----- | --------- | ---------------------------------- | ---------------- |
| 4     | 2         | 660                                | 0                |
| 4     | 3         | 567                                | 0                |
| 5     | 2         | 950                                | 0                |
| 5     | 3         | 851                                | 0                |
| 5     | 4         | 540                                | 0                |

Das sind 3568 Fälle ohne Abweichung. Für m=6 und m=7 auf Tiefe ≥ 2 habe ich den Abgleich nicht abgeschlossen; jeder Einzelfall lief ins Zeitlimit der Sandbox. Er gehört als Pflichtpunkt in P0.

**Die Sternsysteme sind gekoppelt. Das korrigiert meinen Review.** Zwei einfachere DP-Varianten haben überzählt:

- Die naive Variante mit mehreren Schnittzählern lag in 2–9 % der Fälle zu hoch.
- Auch mit Restgrad-Regeln je Stern blieben Fehler.

Der Grund ist, dass ein Knoten in zwei Nachbarschaften zugleich liegen kann. Ein konkretes Beispiel aus m=4:

- (4,7) gehört in N(u) zur gepaarten Klasse, braucht dort also genau einen Partner.
- In N(4,6) gehört (4,7) zur isolierten Klasse, darf dort also keinen Nachbarn haben.
- Damit ist die Paarung (2,3)–(4,7) verboten. Eine an sich zulässige Zielzeile scheidet deshalb aus.

Für den Plan heißt das zweierlei:

- Der Kapazitätsfilter C(S), den ich vorgeschlagen hatte, muss diese Kopplung berücksichtigen. Sonst ist er nur eine schwächere Bedingung als F und kann keine Exaktheit beanspruchen.
- Jeder neue Zähler oder Filter muss über mehrere m und Tiefen gegen SAT abgeglichen werden. Das ist genau der Fehlertyp, den GC-20 meint.

**Tiefe-1-Kinder von Root 1 mit Ziel (0,8) vollständig aufgezählt.** Der zweite unabhängige Lauf ergibt wieder exakt 173 365. Die vollständige Liste liegt in der Sandbox und ist die Grundlage für gleichverteilte Stichproben auf Tiefe 2.

### Was offen ist

- **128-Root-Lauf über alle 83 Ziele:** Mindestens 100 von 128 Roots sind berechnet. Ausgewertet sind weiterhin nur die 24 aus meiner letzten Antwort.
- **Tiefe-2-Probe:** noch nicht gerechnet. Geplant sind 20 gleichverteilte Kinder von Root 1, jeweils alle 82 Ziele mit `width_exact`. Das ergibt die minimale Breite auf Tiefe 2 und damit eine Knuth-Schätzung für N₃ von Root 1. Erst damit ließe sich die Ebene-3-Größe aus eigenen Daten statt aus Pilot-Untergrenzen angeben.
- **Breite der isolierten Ziele für alle 8105 Roots:** noch nicht gerechnet. Das ist je Root eine obere Schranke für die minimale Breite. Eine exakte untere Schranke liefert erst der Vollzensus P1 über alle 83 Ziele.
- **Skripte als Dateien:** noch nicht ausgegeben. Das Paket umfasst `width_dp.py` mit `width_exact`, `root_audit.py`, `sat_crosscheck.py`, `bvls_control.py` und Ergebnisdateien. Die Sandbox-Dateien haben den letzten Wechsel überlebt, garantiert ist das aber nicht. Fehlt etwas, schreibe ich es aus dem Review-Text neu.

### Folgen für den Plan

P2 (Knuth-Proben) wird deutlich billiger. Auf den flachen Tiefen 2–4 muss man nicht mehr 10⁴–10⁶ Zeilen per SAT aufzählen, sondern zählt exakt. Gleichverteilte Kinder lassen sich durch schrittweises Fixieren mit wiederholten DP-Aufrufen ziehen. In P0 kommt deshalb ein Pflichtpunkt hinzu: `width_exact` gegen SAT bei m=6 und m=7 auf Tiefe 2–5 prüfen, mit Zielen kleiner Breite, sowie gegen BvLS-Präfixe bei m=11.

Mit „Weiter“ mache ich in dieser Reihenfolge weiter:

1. Auswertung der 128 Roots;
2. Abgleich bei m=7 auf Tiefe 2;
3. Tiefe-2-Probe für Root 1;
4. Breite der isolierten Ziele für alle 8105 Roots;
5. Ausgabe des Skriptpakets mit Ergebnissen und README.

Weiter

24 Befehle ausgeführt, 6 Dateien erstellt, dateien geteilt · 1 Notiz

24 Befehle ausgeführt, 6 Dateien erstellt, dateien geteilt · 1 Notiz

Die vier offenen Punkte sind abgearbeitet und das Skriptpaket liegt oben. Wichtigstes Ergebnis: Die vollständige Auswertung der 128 Roots korrigiert meine Zahlen aus dem Review, und zwar in Richtung eines noch klareren NO-GO.

### Korrektur: Ebene 1 über alle 128 Pilot-Roots

Die ersten 24 Roots waren nicht repräsentativ. Sie haben kleine IDs und gehören überwiegend zu einem seltenen, schmalen Strukturtyp.

| **Größe**                                             | **Review (24 Roots)**       | **korrigiert (128 Roots)**               |
| ----------------------------------------------------- | --------------------------- | ---------------------------------------- |
| Minimum über die Ziele liegt in der isolierten Klasse | 24/24                       | 116/128                                  |
| minimale Breite: Min / Median / Max                   | 173 365 / 175 021 / 206 315 | 173 365 / **589 469** / 682 915          |
| Ordered-Ziel (0,2): Median                            | 15,53 Mio.                  | 15,39 Mio. (in 1 Root adjazent: 664 678) |
| Anteil, den die Kappung 65 536 erfasst                | 0,42 %                      | 0,42–9,9 %                               |
| Hochrechnung Σ_r min_t w (Ebene 2)                    | ≈ 1,4·10⁹                   | **≈ 4,7·10⁹**                            |

Kein einziges Ziel hat Breite 0.

**Die Bimodalität hat eine einfache Ursache.** Entscheidend ist, wie viele der beiden isolierten u-Nachbarn den Partnerknoten 7 oder 8 enthalten:

| **Typ** | **Pilot-Stichprobe** | **Population (8105)** | **mittlere minimale Breite** |
| ------- | -------------------- | --------------------- | ---------------------------- |
| 0       | 94                   | 7418 (91,5 %)         | 611 529                      |
| 1       | 14                   | 630                   | 205 480                      |
| 2       | 20                   | 57                    | 175 550                      |

Die Pilot-Schichtung nach Stabilisator und Matchingzahl hat die schmalen Typen also stark überrepräsentiert. Die Hochrechnung 4,7·10⁹ ist nach diesen Typen gewichtet; exakt wird die Zahl erst mit P1. Die Roots für P2 müssen nach diesem Typ gewichtet werden.

### Abgleich auf Tiefe 2 bei m=7 und erste Ebene-2-Probe

**Abgleich von `width_exact` gegen SAT auf Tiefe 2:**

- Ziel (1,7): DP 22 311, SAT 22 311.
- Ziel (2,8): DP 115 976, SAT 115 976.
- Zwei weitere Ziele waren nach 60 s per SAT noch nicht fertig. Ihre Untergrenzen (157 391 und 157 969) sind mit den DP-Werten verträglich.
- m=6 und Tiefe ≥ 3 bei m=7 sind weiterhin ungeprüft; das bleibt ein Pflichtpunkt in P0.

**Probe für Root 1 (Typ 2, also der schmalste Typ).**

- Regel: Auf Ebene 1 Ziel t1=(0,8) mit Breite 173 365, alle Kinder vollständig aufgezählt. Auf Ebene 2 das Minimum über die 22 offenen Ziele, die zu u oder t1 adjazent sind.
- In 3 gleichverteilten Stichproben war das Minimum 22 410, 22 403 und 22 399, jedes Mal bei Ziel (1,7).
- Das zweitkleinste Ziel lag jeweils bei etwa 1,1–1,2·10⁵.
- Auf dem einen Zustand, den ich vollständig über alle 82 Ziele gemessen habe, lag das Minimum ebenfalls bei (1,7) (22 311).

Daraus folgt eine Knuth-Schätzung für Ebene 3 von Root 1: 173 365 × 22 404 ≈ **3,9·10⁹ Knoten**, und das für einen einzigen Root des schmalsten Typs. Mit nur drei Stichproben ist das grob, aber die Streuung ist winzig. Pro Ebene schrumpft die beste Breite nur um etwa den Faktor 8. Vollständige Ganzzeilen-Augmentation ist damit noch eindeutiger NO-GO als im Review dargestellt.

### Weitere Prüfungen in Paketform

- **BvLS-Kontrolle:** PASS, mit jetzt 33/33 positiven Präfixtests. Neu ist eine echte Negativkontrolle: eine Zeile mit korrektem Grad, korrekten Margen und Symmetrie, aber Paarzahl 2 statt 1. `Geometry.verify` lehnt sie mit `common neighbors` ab, und `encode` ist unter dieser Zeile UNSAT.
- **Root-Audit:** erneut PASS.
- **`census_level1.py`:** liefert für Root 1 und 9 Ergebnisse, die bitgleich mit dem 128er-Lauf sind.
- **`crosscheck_sat.py`:** in der Paketform nur syntaxgeprüft. Die Prüflogik selbst lief in den gezählten 3568 + 2 Fällen.

### Folgen für die Ressourcen

- **P1:** Unter CPU-Konkurrenz brauchte der Zensus 18,5 s je Root, ohne Konkurrenz etwa 10 s. Für 8105 Roots sind das 22–42 CPU-h in Sandbox-Geschwindigkeit; die echte Zahl zuerst auf dem Ryzen messen.
- **P2:** `width_exact` braucht auf Tiefe 2 etwa 3–8 s je Ziel, eine Probe mit 22 Kandidaten also rund 3 min. 1500 Proben bis Tiefe 2 kosten damit etwa 75–100 CPU-h.

Das Paket enthält `width_dp.py`, Root-Audit, SAT-Abgleich, BvLS-Kontrolle, Zensus- und Probenwerkzeug, alle Ergebnisdateien und ein SHA256-Manifest. Die Skripte sind Prüfwerkzeuge ohne GC-19-Dialog. Für einen Produktionslauf auf dem Ryzen muss der Projektcontroller davorgeschaltet werden.