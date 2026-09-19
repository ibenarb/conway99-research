# Unabhängiges Review: Conway99-Involutionsstrategie (C2)

Gegenstand: `docs/c2_review_20260919/BERICHT_UND_STRATEGIE.md`
Belegstand: `1dc3d773254cb914f49a067d298178a720ff6f72` (Belege), `b3d2f8d…` (Reviewerprompt)
Reviewdatum: 19. September 2026. Reviewer: externer Gutachter, keine Projektbeteiligung.

Alle unten als „nachgerechnet" oder „reproduziert" bezeichneten Ergebnisse wurden in
einer eigenen Umgebung aus dem geklonten Repository neu erzeugt. Es wurden **keine
Solverläufe** gestartet und **keine Projektdateien verändert**. Nicht zugängliche
Belege sind in Abschnitt 8 ausdrücklich als solche aufgeführt.

---

## 1. Gesamturteil

Der Bericht ist in Bezug auf das, was er behauptet, ungewöhnlich sauber. Ich habe
keine falsche mathematische Aussage und keine überzogene experimentelle Behauptung
gefunden. Sämtliche nachprüfbaren Zahlen stimmen exakt. Die Kritik richtet sich
deshalb nicht gegen Korrektheit, sondern gegen **Prioritäten**: Die mit Abstand
größte verfügbare und beweisbar zulässige Reduktion — die Restsymmetrie innerhalb
jedes der elf Fälle — wird nicht genutzt, während Vorschlag A (erste Priorität)
nach eigener Messung nur einen kleinen, einseitigen Propagationsgewinn bringt.
Zusätzlich fehlt eine Fortschrittsgröße mit sinnvollem Nenner, wodurch jede
weitere Kampagne uninformativ bleibt.

### Statusklassifikation

| Aussage | Status |
|---|---|
| E1–E3 sind notwendig **und** hinreichend für ein SRG(99,14,1,2) mit vorgeschriebener Involution | **bewiesen** (Beweis blockweise nachgerechnet, korrekt) |
| Rahmen 1+14+84, Lemma 1 (Wirkung von t), Lemma 2 (Partnerkantenverbot) | **bewiesen**, unter der Fixpunkt-Literaturvoraussetzung |
| Lemma 3 (F perfektes Matching, H 10-regulär), Lemma 4 (spec D = {0⁷,3²⁰,(−4)¹⁵}) | **bewiesen** (nachgerechnet) |
| Genau ein Fixpunkt jeder Involution | **angenommen** (Literatur, nicht auditiert) — siehe B-3 |
| Elf Matchingtypen = vollständige Orbitabdeckung von 10395 | **bewiesen und unabhängig reproduziert**; zusätzlich: die Zahl 11 ist **optimal**, nicht nur eine obere Schranke (siehe 3.3) |
| Referenz-CNF 570171 / 1990821, F-Bedingung byteidentisch | **reproduziert**, mit stärkerer Erklärung (siehe 3.2) |
| Encoderkorrektheit | **kontrolliert** (endliche Kontrollen + schriftliche Induktion), nicht zertifiziert |
| Alle elf Fälle offen nach je 34 h, 373.979 CPU-h | **reproduziert** (jede Tabellenzahl stimmt) |
| Geschwindigkeitsvorteil Totalizer | **nicht belegt** — Bericht behauptet das korrekterweise auch nicht |
| Irgendein Involutionsausschluss | **offen**. Auch in der Literatur (Stand Juli 2026) existiert keiner |

---

## 2. Reproduktionen

Alles in diesem Abschnitt wurde neu erzeugt, nicht aus dem Bericht übernommen.

**Referenzencoder.** `python3 src/c2_reference_20260913/c2_reference.py --k 14`
liefert in rund 4 Sekunden
`570171` Variablen, `1990821` Klauseln, `sha256 f9d6011c5e6eb8a0…`,
Quell-SHA256 `3a88f356831a4f955c79639bfe86aac5eea2a80f…` — identisch mit dem in
`src/c2_matching_20260915/THEOREM.md` und `src/c2_counter_ab_20260916/THEOREM.md`
fixierten Hash. Phasenaufteilung E1 38640/151242, E2 15792/58044,
E3 514017/1781535. `matching_identical: true`.

**Encoder-Selbsttests.** `test_reference.py` → `C2_REFERENCE_CONTROLS_PASS`
(3242 gewichtete Projektionskontrollen, 8 Rook-Kontrollen, unabhängiges DPLL).

**Orbitabdeckung.** Eigene Enumeration: 10395 beschriftete Matchings auf zwölf
Punkten, Gruppe C2 wr S6 der Ordnung 46080, Bahnenzerlegung durch direkte
Bahnberechnung (nicht über die Partitionsformel). Ergebnis: **genau 11 Bahnen**,
Größen 1, 30, 160, 180, 720, 960, 2304, 120, 1440, 640, 3840, Summe 10395 —
zeichengenau die Tabelle aus `THEOREM.md` §3.

**34h-Lauf.** `analyze.py` neben dem Originalarchiv reproduziert
`archive_sha256 a4cb49271e2b98f7…`, 38 Einträge, CRC bestanden,
373.978992 CPU-h, 122405 s Wall, 634325720 Konflikte, Median-Suchanteil 96.95 %,
RSS 596.1–797.3 MiB, CPU/Wall 0.99990. **Jede** Zelle der Berichtstabelle
(Konflikte, Variablen bei 24 h, Variablen zuletzt, Abnahme in Prozent)
stimmt exakt, einschließlich der Ausreißer 23.07 %, 9.41 %, 8.41 %.

**A/B-Lauf.** Reproduziert: Median-Spitzen-RSS 746.62 → 558.40 MiB (−25.21 %),
Restvariablen −34.03 %, irredundante Klauseln −3.28 %, Gesamtkonflikte **+13.14 %**.

---

## 3. Befunde nach Schweregrad

### A. Hoch

#### A-1 Die Restsymmetrie innerhalb der elf Fälle wird nicht genutzt

Das ist der wichtigste Befund dieses Reviews.

Nach Fixierung des lokalen Matchings L auf einen Standardvertreter bleibt der
**Stabilisator** `Stab_H(L) ≤ H = C2 wr S6` als beweisbar zulässige
Umbenennungsgruppe übrig. Genau diese Gruppe nennt `THEOREM.md` §2 selbst als die
einzig erlaubte weitere Reduktion — sie wird aber nirgends verwendet.
`SPEZIFIKATION.md` §6 sagt „Symmetriebrechung wird in der Baseline zunächst
weggelassen", und das ist bis heute so geblieben. Der Stabilisator erhält die 66
Einheitsklauseln des Falles elementweise, die Symmetriebrechung ist also
unmittelbar gültig (gleiches semantisches Argument wie in `THEOREM.md` §2).

Eigene Berechnung (Bahnen von ⟨Stab_H(L), t⟩ auf den 1722 Primärvariablen):

| Typ | \|Stab_H(L)\| | Bahnen auf 84 Außenknoten | Bahnen auf 1722 Primärbits |
|---|---:|---:|---:|
| 1+1+1+1+1+1 | **46080** | 3 | **11** |
| 2+2+2 | 384 | 5 | 41 |
| 1+1+1+1+2 | 1536 | 8 | 53 |
| 3+3 | 72 | 6 | 59 |
| 1+1+1+3 | 288 | 9 | 74 |
| 1+1+2+2 | 256 | 9 | 83 |
| 1+1+4 | 64 | 11 | 124 |
| 2+4 | 32 | 12 | 142 |
| 1+2+3 | 48 | 14 | 149 |
| 1+5 | 20 | 11 | 156 |
| 6 | 12 | 10 | 172 |

Im Fall 1+1+1+1+1+1 zerfallen 1722 Primärbits in **elf** Bahnen; der Solver
durchsucht dort denselben Konfliktraum bis zu 46080-fach. Selbst der ungünstigste
Fall (Typ 6) hat noch |Stab| = 12. Eine partielle Lex-Leader-Brechung über
Erzeuger kostet wenige tausend Klauseln und einige Arbeitsstunden.

Zum Vergleich: Vorschlag A (erste Priorität des Berichts) fügt 28980 Klauseln
hinzu und erzeugt nach eigener Messung (A-4) einen einseitigen, lokalen
Propagationsgewinn. Die Restsymmetrie ist eine *globale*, exponentiell wirkende
Redundanz. Die Priorisierung sollte umgekehrt werden.

*Nebenbefund:* Die Rangfolge der Stabilisatorgrößen ist fast umgekehrt zur
Bahngröße. Der „kleinste" Fall 1+1+1+1+1+1 (eine einzige beschriftete Belegung)
ist der symmetrischste und damit der am stärksten reduzierbare. Elf gleich
budgetierte Prozesse sind vor diesem Hintergrund zusätzlich fragwürdig.

#### A-2 Es fehlt eine Fortschrittsgröße mit Nenner

Der Bericht sagt korrekt, dass Restvariablen und Konflikte keine Beweisnähe
messen. Er zieht daraus aber nicht den konstruktiven Schluss: Es gibt eine Größe
mit natürlichem Nenner, nämlich die Zahl der **fixierten Primärbits von 1722**.
CaDiCaL meldet `fixed` nur über alle Variablen (nach 34 h: 125460–161405 von
570171) — projiziert auf die Primärbits wird nichts protokolliert.

Eigene Messungen als Basislinie:

- Reine Unit-Propagation auf der Baseline fixiert **0** der 1722 Primärbits
  (2394 Einheitsklauseln, alle auf Hilfsvariablen).
- Die 66 Einheitsklauseln eines Falles fixieren per UP:

| Fall | UP-Zuweisungen gesamt | fixierte Primärbits (von 1722) |
|---|---:|---:|
| 1+1+1+1+1+1 | 33120 | 186 (10.8 %) |
| 1+1+1+1+2 | 26514 | 146 |
| 1+1+1+3 | 23404 | 126 |
| 1+1+2+2 / 1+1+4 | 20333 | 106 |
| 1+2+3 / 1+5 | 17293 | 86 |
| 2+2+2 / 2+4 / 3+3 / 6 | 14148 | 66 (3.8 %) |

Muster: 66 + 20 × (Anzahl Einerteile). Nach den Fallannahmen sind also
89–96 % der Primärbits offen. Diese Zahl, über die Laufzeit protokolliert, ist
die einzige mir bekannte Größe, die überhaupt eine Deutung als Fortschritt
zuließe — und sie kostet nichts (periodisch die fixierten Literale abfragen und
gegen die Primärkarte aus `variables.json` schneiden).

Solange sie fehlt, ist jede weitere Kampagne nicht auswertbar, unabhängig von der
Laufzeit. Diese Instrumentierung sollte **vor** jedem weiteren Experiment stehen.

#### A-3 Die tragende Literaturvoraussetzung ist nicht auditiert und nicht elementar

Die Vollständigkeit des gesamten Modells hängt an „jede Involution hat genau einen
Fixpunkt". Der Bericht sagt das offen. Zwei Ergänzungen:

**(a) Der Satz ist nicht durch elementares Spurenrechnen zu bekommen.** Mit
spec(A) = {14¹, 3⁵⁴, (−4)⁴⁴}, f = 1 + α + β, e = 14 + 3α − 4β (e = Zahl der zu
ihrem Bild benachbarten Knoten), α, β gerade, f ungerade, e ≤ 14f habe ich alle
Lösungen aufgezählt: **jedes ungerade f von 1 bis 99** bleibt zulässig, für f = 3
etwa e ∈ {6, 20, 34}. Die Charakterkongruenz allein schließt also nichts aus.
Der Satz ist substanziell, und er trägt alles.

**(b) Unabhängige Bestätigung gefunden, aber nur teilweise.** Makhnevs Vortrag
formuliert den Satz explizit (Makhnev–Minakova [3]: für g von Primordnung p ist
Fix(g) ein Einzelknoten für p ∈ {2,7}, leer für p ∈ {3,11}, ein Dreieck für p = 3).
Zusätzlich habe ich eine dem Projekt unbekannte Arbeit gefunden — siehe A-5 —,
die daraus **a₁(t) = 14** ableitet, also: genau 14 Knoten sind zu ihrem Bild
benachbart. Das ist im Modell des Projekts exakt äquivalent zu Lemma 2 (die 14
Rahmenknoten sind zu ihrem Partner benachbart, kein Außenknoten zu seinem Partner)
und damit eine **unabhängige Konsistenzprüfung des Rahmens, die das Modell
besteht**. Es ersetzt aber nicht den Fixpunktsatz selbst: a₀ = 1 geht dort als
Voraussetzung ein.

Empfehlung: Beschaffung des russischen Originals (Diskret. Mat. **16** (2004)
Nr. 1, 95–104) oder der Übersetzung und ein kurzer, dokumentierter Audit des
Higman-Arguments. Bis dahin muss jedes Ergebnis ausdrücklich als *bedingt*
formuliert werden: „kein SRG(99,14,1,2) besitzt eine Involution, unter Annahme
des Fixpunktsatzes von Makhnev–Minakova".

#### A-4 Vorschlag A: gemessen, teilweise wirksam, aber deutlich kleiner als A-1

Ich habe die Behauptung nicht nur logisch, sondern **empirisch auf der echten CNF**
geprüft (eigener Unit-Propagations-Motor über die 1990821 Klauseln).

*Korrektheit.* Die Herleitung ist richtig. Für x, y mit genau einem gemeinsamen
Rahmenlabel ist die E3-Zeile `M_xy + Σ_z M_xz M_yz = 1`, also ist
`¬M_xy ∨ ¬M_xz ∨ ¬M_yz` gültig. Inhaltlich: **verboten sind alle Außendreiecke,
in denen mindestens ein Paar ein Rahmenlabel teilt.** Die Klausel ist in x, y, z
vollständig symmetrisch; das sollte im Encoder ausgenutzt werden (sonst werden
Duplikate erzeugt).

*Umfang.* Nach Involutionsidentifikation und Deduplikation: **28980 verschiedene
Dreierklauseln** (+1.46 % der Klauseln, +0 Variablen). Die Viererklauseln
dagegen: **3068604** vor Deduplikation, also mehr als eine Verdopplung der CNF.

*Propagationsstärke (Messung auf der Baseline-CNF).*

| Belegung | UP-Ergebnis |
|---|---|
| M_xy = 1, M_xz = 1 ⟹ M_yz = 0 | in **35 von 35** Stichproben bereits durch UP erschlossen |
| M_xz = 1, M_yz = 1 ⟹ M_xy = 0 | in **112 von 196** Stichproben (57 %) **nicht** erschlossen (61 × erschlossen, 23 × direkter Konflikt) |
| Viererfall (zwei gemeinsame Außennachbarn) | in 20 von 23 Stichproben kein UP-Konflikt |

Erklärung: `exact()` baut ein geordnetes BDD über die nach Variablennummer
sortierten Terme. M_xy ist Primärvariable und steht damit an der **Wurzel**.
Wird M_xy = 1 gesetzt, kaskadiert UP sofort „Restsumme = 0" durch das gesamte
BDD und setzt alle 84 Produktvariablen auf falsch — deshalb die 35/35. In der
Gegenrichtung muss die Information von einem späten Produktblatt zur Wurzel
zurücklaufen; das leistet die ITE-Kodierung nicht. Genau dort wirkt A.

*Konsequenz für den Bericht.* Die Formulierung „Diese Klauseln sind logische
Folgerungen" ist richtig; die im 34h-REPORT.md nahegelegte Lesart „bereits
logisch im Encoder enthalten, kann die Propagation nur verkürzen" ist **zu
schwach**: A erhöht die UP-Abschlussstärke in einer Richtung messbar. Die
Dreierklauseln sind billig genug, um sie ohne weiteres Gate aufzunehmen. Die
Viererklauseln sind so nicht bezahlbar und müssten mindestens auf Paare (z, z')
mit gemeinsamer Struktur gefiltert werden; ich empfehle, sie zunächst ganz
wegzulassen.

Das vom Bericht vorgeschlagene Gate („Zählen, normalisieren, Subsumption prüfen,
UP vergleichen") ist damit im Wesentlichen **erledigt** — die Zahlen stehen oben.
Was bleibt, ist der A/B-Lauf, und der sollte hinter A-1 eingereiht werden.

#### A-5 Literaturlücke: eine einschlägige Arbeit vom Juli 2026 fehlt

`LITERATURABGLEICH.md` ist auf den 13. September 2026 datiert und erfasst nicht:

> Y. Ishida, *No involutions in the missing Moore graph*, arXiv:2606.29183 (Juli 2026).

Die Arbeit betrifft primär den fehlenden Mooregraphen, enthält aber in **§8.4
einen Abschnitt ausschließlich über den Conway-99-Graphen**. Relevanz:

1. Sie liefert eine **Spur-Rang-Identität**, die die klassischen
   Charakterkongruenzen durch exakte Werte ersetzt, und daraus für eine Involution
   des Conway-99-Graphen **a₁(t) = 14** — die oben genannte unabhängige
   Bestätigung des Rahmens.
2. Sie bestätigt ausdrücklich den offenen Status: Makhnev–Minakova bestimmen die
   Fixpunktuntergraphen, Behbahani–Lam reduzieren die möglichen Primordnungen auf
   **2 und 3**; ein Involutionsausschluss existiert nicht. Das Neuheitsziel des
   Projekts ist also intakt.
3. Für die Ordnung 3 gibt sie (Prop. 8.7, Juli 2026) weiterhin **beide** Fälle an:
   Fix(x) = ∅ mit a₁ = 18, oder Fix(x) ≅ K₃ mit a₁ = 6.

Punkt 3 steht in Spannung zur Zeile „C3 fixpunktfrei" in `LITERATURABGLEICH.md`
(gestützt auf Crnković–Maksimović §7 und Cesarz–Woldar Kor. 3.13). Eine der
beiden Darstellungen ist ungenau. Das ist keine Gefahr für die C2-Arbeit, aber es
betrifft die Planung danach und sollte geklärt werden. **Offene Rückfrage 1.**

Einordnung der übrigen Literatur, soweit ich sie prüfen konnte (Abstracts,
Volltext teilweise):

- **Cesarz–Woldar (ALCO 2025):** Teilbarkeit durch 7 ⟹ G ≅ ℤ₇; folglich
  Teilbarkeit durch 2 ⟹ |G| teilt 6, G ∈ {ℤ₂, ℤ₆, S₃}. Damit gilt: **ein
  C2-Ausschluss zwingt |Aut| auf ungerade Ordnung, teilend 27.** Zusammen mit
  einem C3-Ausschluss wäre Aut trivial. Das ist eine präzisere und stärkere
  Motivationsformulierung, als der Bericht sie gibt.
- **Thakkar, arXiv:2608.11211 (13. Juli 2026):** Bericht eines autonomen
  KI-Agenten. Die „forced-structure reduction" ist dieselbe 1+14+84-Struktur mit
  12-regulärem Graphen auf 84 Knoten; das Orbitmodell für den
  Einfixpunktfall wurde nach 48 h Budget als *unknown* abgebrochen. **Kein
  C2-Ausschluss.** Die Projektbewertung ist zutreffend, und der Befund ist
  zusätzlich eine unabhängige Bestätigung, dass die Instanz für Standardsolver
  hart ist.
- Die Neuheitsaussagen des Projekts (keine beansprucht) sind damit korrekt kalibriert.

### B. Mittel

#### B-1 Die byteidentische CNF ist stärker als berichtet

Der Bericht sagt, die Ergänzung der F-Bedingung liefere eine byteidentische CNF.
Ich habe nachgerechnet, **warum**: `add_matching` erzeugt für Zeile i die Terme
`B_ij ∧ C_ij`. Dieselben Konjunktionen entstehen bereits in der E3-Zeile für das
Paar (x_i, t(x_i)): dort ist `edge(x_i, x_j) ∧ edge(x_j, t(x_i)) = B_ij ∧ C_ij`
und `edge(x_i, x_{j+42}) ∧ edge(x_{j+42}, t(x_i))` liefert dieselbe Konjunktion,
also Gewicht 2. Die Zielzahl ist 2 − |label(x_i) ∩ label(t(x_i))| = 2. Nach
gcd-Normierung durch 2 entsteht exakt `Σ_j (B_ij ∧ C_ij) = 1`. Verifiziert:
**42 von 42** F-Zeilenschlüsseln liegen bereits im Gleichungs-Cache der Baseline.

Die F-Bedingung ist also nicht „logisch impliziert und zufällig dedupliziert",
sondern **wörtlich dieselbe Nebenbedingung**. Der Bericht sollte das so sagen;
es ist ein stärkeres Argument dafür, A/B-Versuche mit F nicht zu wiederholen.

#### B-2 Beweisspeicher: konkrete Zahlen

Beobachtete Konfliktrate: 57.67 Mio. pro Fall in 122400 s = **471 Konflikte/s je
Prozess**, 5182/s über elf Prozesse. Bei LRAT-Kosten von 30/60/120 Byte pro
gelernter Klausel ergibt das **13.4 / 26.9 / 53.7 GB pro Tag** über alle
Prozesse. Der zuletzt bekannte Windows-Freiraum von rund 200 GiB reicht damit für
**4 bis 15 Tage** Beweisprotokollierung — und die Fälle sind nach 34 h nicht
annähernd fertig.

Folgerung: Eine Zertifizierung des jetzigen Zuschnitts ist speicherseitig
unmöglich. Zertifizierbarkeit ist kein nachgelagerter Schritt, sondern ein
**Entwurfszwang**, der auf Cubing mit pro-Cube begrenzten Beweisen führt (siehe
Abschnitt 6). Der Bericht nennt das Speicherbudget zu Recht, quantifiziert es
aber nicht.

#### B-3 Elf Prozesse auf 24 logischen Threads

24 logische Threads bedeuten auf einem Ryzen 12 physische Kerne. Elf
CaDiCaL-Prozesse sind also ungefähr ein Prozess je physischem Kern — für einen
speicherbandbreitengebundenen Solver eine **vertretbare, eher gute Wahl**.
Zweiundzwanzig Prozesse würden die SMT-Geschwister belegen; typisch sind dabei
10–30 % Gesamtdurchsatzgewinn bei 30–50 % Einzeljobverlangsamung. Bei nur elf
Fällen ist das nicht der Engpass.

Der eigentliche Punkt: Es gibt **nur elf Aufgaben**. Die ungenutzte Kapazität
gehört nicht in mehr Prozesse pro Fall, sondern in **mehr Teilprobleme** (Cubing,
Vorschlag C) oder in ein **Portfolio** (zweiter Seed, zweite Konfiguration,
zweiter Solver). Eine Messung 11 vs. 22 Worker über 2 × 20 Minuten kostet
1.5 CPU-h und beendet die Diskussion; sie hat aber niedrige Priorität.

#### B-4 Die Archivprüfung ist teilweise zirkulär — korrekt benannt, aber unterstrichen

`analyze.py` prüft überwiegend `summary.json` gegen `result.json` gegen `job.json`
— alles aus derselben Quelle. Wirklich unabhängig sind CRC, Loglängen, die
Konsistenz der Logtexte mit den gemeldeten Statuswerten und die abgeleiteten
Aggregate. Der Bericht sagt das (und nennt auch das Fehlen eines extern
gelieferten Soll-Hashes). Ich bestätige es und ergänze: Ohne die CNFs und die
Solverbinärdatei im Archiv ist die Kette „diese Zahlen gehören zu dieser Formel"
nur durch die aufgezeichneten Hashfelder belegt, also durch Provenienz, nicht
durch Prüfung. Für einen Scout ist das akzeptabel. Für eine Zertifizierung nicht.

### C. Niedrig

- **C-1** Die Tabellenspalte „Variablen bei ca. 24 h" nimmt die letzte Logzeile
  mit CPU-Zeit ≤ 24 h. Das ist dokumentiert und in Ordnung; bei den drei Fällen
  mit großem Rückgang (1+1+1+3: 23.07 %) lohnt aber ein Blick, ob dort schlicht
  ein Inprocessing-Durchlauf kurz nach der 24h-Marke liegt. Die Zahl misst dann
  den Zeitpunkt der Messung, nicht den Fall.
- **C-2** `exact()` dedupliziert über `self.equalities`. Das ist korrekt, macht
  aber die Klauselzahl schwer interpretierbar (2394 Gleichungen für 84 + 84·14 +
  3486 nominelle Bedingungen). Für die A-Auswertung sollte die
  Deduplikationsstatistik mit ausgegeben werden.
- **C-3** Die 66 Einheitsklauseln werden angehängt, der Klauselkörper bleibt
  exakter Präfix, der Header geht auf 1990887. Nachgeprüft, sauber.

---

## 4. Antworten auf die acht gestellten Fragen (Kurzform)

**1. Literatur und Neuheitsziel.** Fixpunktsatz bestätigt (Makhnev–Minakova, via
Makhnev-Vortrag und via Ishida §8.4), nicht auditiert, nicht elementar (A-3).
Kein vollständiger C2-Ausschluss existiert; Thakkar hat ihn nicht (A-5). Eine
verifizierte UNSAT-Kette wäre daher ein **neuer Beitrag**, kein Nachvollzug.
Sinnvolle unabhängige Zertifizierung: die Ausschlusskette selbst plus ein
maschinenprüfbares Symmetriezertifikat. Bloße Wiederholung wäre: Neubestimmung
der Fixpunktstruktur, Neuimplementierung von Thakkars Reduktion.

**2. Vollständigkeit des Modells.** Rahmen, E1/E2/E3, 1722 Bits und Rekonstruktion
blockweise nachgerechnet und korrekt; die Bedingungen sind gemeinsam auch
hinreichend (Satz 1 stimmt). C_ii = 0 wird a priori gesetzt und ist durch Lemma 2
gerechtfertigt, also keine zusätzliche Annahme. Fehlende Argumente: keine
mathematischen; fehlend ist die *Zertifizierung* des Encoders (Abschnitt 6).

**3. Symmetriereduktion.** Abdeckung unabhängig reproduziert. **Zusatzbefund: 11
ist optimal.** Die volle verfügbare Gruppe ist der Stabilisator des Rahmens, der
N(0) erhält, also (C2 wr S6) × ⟨(0 1)⟩; der Erzeuger (0 1) ist aber modulo der
vorgeschriebenen Involution t gleich dem „alle Paare flippen"-Element von H
(t∘(0 1) bildet x_{0,a} auf x_{0,a^1} ab). Es geht also nichts verloren; 11 ist
die exakte Bahnzahl, keine obere Schranke. F und L werden im Bericht korrekt
getrennt. Die byteidentische CNF ist in Wahrheit Gleichheit der Nebenbedingung
(B-1). **Zulässige weitere Normalisierung: genau Stab_H(L) — und die ist
ungenutzt (A-1).**

**4. Experimentelle Aussagekraft.** Vollständig reproduziert; keine Abweichung.
Keine Entscheidungen, alles budgetzensiert, ein Seed, feste Wellenreihenfolge —
im Bericht korrekt benannt. Restvariablen, Konflikte und Speicher sagen über
Beweisnähe nichts; sie sagen etwas über Encodergröße und Inprocessing. Als
unzulässig zu benennende Schätzungen kommen im Bericht **nicht** vor — das ist
ein Verdienst. Die einzige zulässige Fortschrittsgröße mit Nenner fehlt (A-2).
Gespeicherte Hashfelder sind keine Prüfung (B-4).

**5. Vorschlag A.** Klauseln korrekt; 28980 Dreierklauseln; **nicht** vollständig
durch UP erschlossen (einseitig, 57 % der Stichproben); Viererklauseln zu teuer.
Details und Zahlen in A-4. Besserer Encodereingriff: siehe A-1 und Abschnitt 5.

**6. Vorschläge B/C.** B ist in der vorgeschlagenen Form (zweites Matching als
Fallzerlegung) der falsche Zuschnitt derselben Idee: Die Abdeckung, die B beweisen
muss, ist genau die Bahnenrechnung unter Stab_H(L) — und die ist als
*Symmetriebrechung* (Constraints) billiger und risikofrei, als sie als
*Fallzerlegung* (Instanzen) wäre. Auswahlkriterium: derjenige zweite
Nachbarschaftsknoten, dessen Zeilenfixierung |Stab| am stärksten reduziert; das
ist vorab exakt berechenbar, kostet Sekunden. C bleibt richtig und ist der
**einzige Weg zur Zertifizierung** (B-2); Splitvariablen nach gemessener
beidseitiger Propagation, Frontier-Größe und Tiefe des dominanten Astes messen —
der Bericht beschreibt das Gate bereits korrekt.

**7. Vorschlag D.** Q/D-Kopplung und Spektralargument sind korrekt nachgerechnet
(Lemma 3, Lemma 4). **Aber:** Die P/N-Formulierung ist zur E1–E3-Form beweisbar
*äquivalent* und hat exakt dieselben 1722 primären Freiheitsgrade. Sie bringt
**keine Modellverkleinerung**. Das Spektrum ist keine Zusatzinformation: aus
D² + D − 12I = −VVᵀ folgt das Spektrum und umgekehrt; (D−3I)(D+4I) = −VVᵀ *ist*
Bedingung N. Rangbedingungen sind zudem in CNF nicht sinnvoll ausdrückbar. Der
realistische Wert von D liegt daher nicht in einem neuen Encoder, sondern in
Strukturlemmata. Dafür ein konkreter, mir nicht in der Literaturliste
begegneter Ansatzpunkt: D ist ein **vorzeichenbehafteter Graph auf 42 Knoten mit
genau drei Eigenwerten** (0, 3, −4) und 10-regulärem Betragsgraphen H. Zu
„signed graphs with few/three distinct eigenvalues" existiert eine eigene
Literatur; eine gezielte Suche dort kann entweder ein Ausschlusskriterium oder
zumindest starke lokale Obstruktionen liefern. Das ist billig und potenziell
wertvoll — aber es ist Literaturarbeit, keine Solverarbeit.

**8. Eigene Alternativen und Priorisierung.** Siehe Abschnitt 5. Elf Prozesse sind
in Ordnung, die Parallelisierungsfrage ist nicht der Engpass (B-3).

---

## 5. Begründete Rangfolge

| Rang | Maßnahme | Aufwand | Erwarteter Mechanismus | Risiko |
|---|---|---|---|---|
| 1 | **F — Instrumentierung: fixierte Primärbits über die Zeit** | 2–4 h | erstmals auswertbare Läufe | keines; ohne sie ist alles Weitere blind |
| 2 | **E — Lex-Leader-Symmetriebrechung unter Stab_H(L)** | 1 Arbeitstag | globale Redundanzreduktion bis Faktor \|Stab\| (12…46080) | Lex-Constraints können CDCL-Heuristiken stören; deshalb A/B, nicht Glaube |
| 3 | **A — 28980 Dreierklauseln** | halber Tag (Zählung liegt vor) | einseitiger UP-Gewinn, gemessen | +1.46 % Klauseln, gering |
| 4 | **C — Cubing auf Primärvariablen** | 1–2 Tage | mehr Teilprobleme, begrenzte Beweise, einziger Zertifizierungspfad | Spine-Problem; Gate des Berichts ist richtig |
| 5 | **B — zweite Nachbarschaft** | — | durch E ersetzt | als Fallzerlegung: kombinatorische Explosion |
| 6 | **D — Paar-/Vorzeichenmodell** | 1 Tag reine Algebra/Literatur | Strukturlemmata, evtl. Treffer in der Signed-Graph-Literatur | kein Encodergewinn zu erwarten |

### Von mir geprüfte und verworfene eigene Vorschläge

- **Wechsel auf den C3-Fall als „kleineres" Modell.** Nachgerechnet: fixpunktfrei
  33 Bahnen ⟹ 33·32/2·3 + 33 ≈ **1617** Primärbits; Fall Fix ≅ K₃ ≈ 1619. Gegenüber
  1722 für C2 ist das **kein** Gewinn. C3 muss für das Gesamtresultat trotzdem
  irgendwann bearbeitet werden, ist aber kein Ausweg aus der jetzigen Härte.
  Verworfen als Abkürzung.
- **Viererklauseln aus Vorschlag A flächendeckend.** 3.07 Mio. Klauseln, mehr als
  eine Verdopplung der Formel. Verworfen ohne Filterkriterium.
- **Spektral-/Rangbedingungen in die CNF.** In CNF nicht sinnvoll kodierbar und
  ohnehin äquivalent zu N. Verworfen.
- **Mehr Prozesse (22 statt 11).** Bei elf Aufgaben adressiert das den falschen
  Engpass. Verworfen zugunsten von Cubing/Portfolio.
- **Wiederholung der F-Bedingung in irgendeiner Form.** Sie steht bereits wörtlich
  in der CNF (B-1). Verworfen.

---

## 6. Konkretes nächstes Experiment

**Vorbereitung: wenige Arbeitsstunden. Suchzeit insgesamt 2 CPU-Stunden.**

**Schritt 0 (Voraussetzung, 2–4 h).** Worker so instrumentieren, dass er alle
60 s die Zahl der fixierten **Primärbits** (Schnitt der fixierten Literale mit den
1722 Variablen aus `variables.json`) ins Log schreibt. Ausgangswerte sind oben in
A-2 tabelliert und dienen als Nullpunkt.

**Hypothese.** Symmetriebrechung unter Stab_H(L) erhöht die Zahl der bis Minute 20
fixierten Primärbits und senkt die Konfliktzahl bis zum ersten
Primärbit-Fortschritt, und zwar monoton in |Stab_H(L)|.

**Design.** Drei Fälle mit stark verschiedenen Stabilisatoren:
`1+1+1+1+1+1` (46080), `2+2+2` (384), `6` (12). Je zwei Varianten (ohne / mit
Symmetriebrechung), gleicher Seed, gleiche Wellenreihenfolge, je 20 Minuten.
6 Jobs × 20 min = 2 CPU-h. Gegenprobe anschließend mit umgekehrter
Wellenreihenfolge und zweitem Seed nur für die Variante, die gewonnen hat.

**Erzeugung der Constraints.** Erzeuger von Stab_H(L) berechnen (die
Bahnenrechnung aus A-1 liefert sie mit; Laufzeit Sekunden), pro Erzeuger eine
Lex-Implikationskette über die 1722 Primärbits ausschreiben. Größenordnung:
wenige tausend Klauseln und Hilfsvariablen pro Erzeuger.

**Zulässigkeitskontrolle vor dem Lauf (Pflicht).** Für 10⁵ zufällige
Primärbelegungen prüfen, dass mindestens ein Bild unter der Gruppe die
Lex-Bedingungen erfüllt; zusätzlich am k=4-Kleinfall erschöpfend prüfen, dass die
Lösungsmenge modulo Gruppe unverändert bleibt. Ohne bestandene Kontrolle kein Lauf.

**Messgrößen.** (i) fixierte Primärbits bei 5/10/20 min; (ii) Konflikte;
(iii) Spitzen-RSS; (iv) etwaige Entscheidung. Konfliktrate allein entscheidet nicht.

**Vorab festgelegte Kriterien.**
- *Fortsetzen:* fixierte Primärbits bei 20 min im Fall `1+1+1+1+1+1` um ≥ 25 %
  höher **und** kein Fall um mehr als Faktor 2 in Konflikten schlechter. Dann E
  auf alle elf Fälle ausrollen und A darüberlegen.
- *Ändern:* Gewinn nur im Fall mit großem |Stab|. Dann Symmetriebrechung
  selektiv nur für Fälle mit |Stab| ≥ 256 (fünf Fälle) und Lex-Ketten kürzen.
- *Abbrechen:* kein Fall verbessert oder mehr als ein Fall deutlich verschlechtert.
  Dann E verwerfen, A allein als 2 × 20-min-A/B testen und danach zu C übergehen.

**Ausdrücklich nicht Teil des Experiments:** lange Läufe, neue 34h-Kampagnen,
Beweisprotokollierung.

---

## 7. Weg vom Scout zur unabhängig prüfbaren Zertifizierung

Der Endsatz wäre: *„Es gibt kein SRG(99,14,1,2) mit einer Involution"*, bedingt auf
den Fixpunktsatz. Er hängt an fünf Gliedern; jedes braucht ein eigenes Artefakt.

1. **Literaturvoraussetzung.** Zitat plus dokumentierter Audit oder ausdrückliche
   Konditionalität (A-3). Kein Rechenaufwand, aber im Ergebnis zu nennen.
2. **Encoderkorrektheit — das schwächste Glied.** Empfehlung: (a) CNF-Hash
   einfrieren; (b) **zweiter, unabhängig geschriebener Encoder** aus der
   Spezifikation, mit anderer Zählkodierung; Vergleich beider CNFs nicht
   byteweise, sondern semantisch: für 10⁵ zufällige Primärbelegungen muss die
   Erfüllbarkeit der Hilfsvariablen in beiden übereinstimmen (polynomial prüfbar),
   und im k=4-Kleinfall erschöpfend; (c) `variables.json`,
   `reconstruct`/`verify_graph` mitveröffentlichen, damit jedes SAT-Modell von
   Dritten direkt am 99-Knoten-Graphen geprüft werden kann. Das ist bereits
   vorhanden — es muss nur als Zertifikatsbestandteil deklariert werden.
3. **Symmetrieabdeckung.** `matching_orbits.py` erzeugt bereits für jedes der
   10395 beschrifteten Matchings einen expliziten Transporter. Das ist ein
   **maschinenprüfbares Zertifikat** und sollte als solches publiziert werden
   (Datei: Matching → Permutation → Bildmatching, prüfbar in Sekunden durch ein
   30-zeiliges Fremdprogramm). Mein eigener, unabhängig geschriebener Prüfer
   bestätigt die elf Bahnen und ihre Größen.
   Wird Symmetriebrechung nach A-1 eingeführt, kommt ein zweites Zertifikat
   hinzu: die Erzeuger von Stab_H(L) je Fall plus der Nachweis, dass die
   Lex-Bedingungen je Bahn mindestens einen Vertreter erhalten.
4. **Blattbeweise mit begrenztem Speicher.** Wegen B-2 ist ein einzelner
   LRAT-Beweis über 34 h ausgeschlossen. Konstruktion: Cubing (Vorschlag C), bis
   jedes Blatt in einem Lauf mit **hartem Beweisbudget von ≤ 2 GiB** schließt;
   Blätter, die das reißen, werden weiter gespalten. Prüfung je Blatt mit
   `cake_lpr` (verifizierter Prüfer) und sofortiges Löschen nach erfolgreicher
   Prüfung — so bleibt der Spitzenbedarf bei (Anzahl paralleler Jobs) × 2 GiB
   statt bei der Summe. Auf 200 GiB Windows-Freiraum sind damit bis zu ~90
   ungeprüfte Blätter gleichzeitig pufferbar; das ist reichlich.
   Getrenntes, explizites Budget auf Windows **und** Linux, wie im Bericht
   gefordert, mit Vorabreservierung (Datei anlegen) statt Freiplatzabfrage — die
   953-GiB-Fehlmeldung des virtuellen Dateisystems darf sich nicht wiederholen.
5. **Cube-Abdeckung.** Der Splitbaum ist selbst ein Zertifikat: binär, beide
   Zweige erhalten, Blätter lückenlos. Als Datei ausgeben und durch ein
   unabhängiges Programm prüfen (jeder innere Knoten hat genau zwei Kinder mit
   komplementärem Literal; die Blattmenge überdeckt alle Belegungen). Timeouts
   sind **keine** geschlossenen Blätter — der Bericht sagt das bereits.

Reihenfolge: Scout (ohne Proof-Logging) findet einen schließbaren Fall → derselbe
Fall wird gecubt → Blätter mit Beweis nachgefahren → Prüfung → erst wenn **alle
elf** Fälle so geschlossen sind, gibt es eine Aussage. Ein einzelner UNSAT-Fall
ist kein Teilergebnis, das publiziert werden sollte.

---

## 8. Belege: gelesen, reproduziert, nicht zugänglich

**Vollständig gelesen und rechnerisch reproduziert**
- `src/c2_reference_20260913/c2_reference.py` (neu ausgeführt, CNF neu erzeugt,
  Hashes verglichen), `test_reference.py` (bestanden)
- `src/c2_matching_20260915/{THEOREM.md, prepare_matching.py}`,
  `results/c2_matching_20260915/cover.json` (Bahnen unabhängig nachgerechnet)
- `results/c2_totalizer_34h_20260919/{REPORT.md, analyze.py, Original-ZIP}`
  (`analyze.py` neu ausgeführt, jede Tabellenzahl verglichen)
- `results/c2_counter_ab_20260917/{REPORT.md, analyze.py, Original-ZIP}`
  (neu ausgeführt)

**Vollständig gelesen, nicht ausgeführt**
- `docs/c2_spec_20260913/SPEZIFIKATION.md` (Sätze und Lemmas von Hand nachgerechnet)
- `docs/c2_spec_20260913/LITERATURABGLEICH.md`
- `src/c2_counter_ab_20260916/THEOREM.md` (Induktionsargument gelesen, plausibel;
  die 34208 Kontrollen nicht nachgefahren)
- `docs/c2_review_20260919/BERICHT_UND_STRATEGIE.md`

**Nicht gelesen** (im Prompt genannt oder benachbart, hier nicht geprüft)
- `docs/c2_reference_20260913/README.md`, `results/c2_reference_20260913/controls.json`
- `results/c2_matching_20260916/eight_hour/` (nur Verzeichnisstruktur)
- `src/c2_guard_fix_20260917/`, `src/c2_totalizer_34h_20260917/`
- sämtliche K66-Unterlagen — das „Spine-Problem" kenne ich nur aus der Erwähnung
  im Bericht (**offene Rückfrage 3**)

**Externe Literatur**
- *Gelesen (Volltext):* Ishida, arXiv:2606.29183, insbesondere §§4–5 und §8.4.
- *Gelesen (Abstract/Auszüge):* Cesarz–Woldar arXiv:2308.02978 und ALCO-Fassung;
  Thakkar arXiv:2608.11211 (Abstract und Auszüge der HTML-Fassung);
  Keramatipour arXiv:2604.23037 (nur Abstract/Gliederung);
  Makhnev-Vortragsfolien (nur die über die Suche zugänglichen Passagen,
  darunter die Formulierung des Fixpunktsatzes).
- *Nicht zugänglich:* Makhnev–Minakova 2004 im Volltext (De Gruyter,
  zugangsbeschränkt) — der Originalbeweis wurde auch von mir **nicht** gesehen;
  Crnković–Maksimović §7 im Volltext; Behbahani–Lam 2011 im Volltext;
  Wilbrink 1984.

**Nicht durchgeführt**
- Keine Solverläufe, keine Beweiserzeugung, keine Reproduktion der 34208
  Summenkontrollen, keine Prüfung der Produktions-CNFs der elf Fälle gegen die
  aufgezeichneten Hashes (die Dateien liegen nicht im Repository).
- Die Messungen in A-4 und A-2 sind Stichproben bzw. Einzelmessungen auf der
  Baseline-CNF, keine Solverbenchmarks. Stichprobengrößen sind jeweils angegeben.

---

## 9. Offene Rückfragen

1. **C3-Fixpunktstruktur.** Worauf genau stützt sich „C3 fixpunktfrei" im
   Literaturabgleich? Ishida (Juli 2026) führt für p = 3 weiterhin beide Fälle
   (∅ und K₃). Bitte Fundstelle mit Satznummer.
2. **Warum keine Symmetriebrechung?** Ist die Auslassung eine bewusste
   Entscheidung (etwa wegen Zertifizierbarkeitssorgen) oder nur Reihenfolge? Falls
   Ersteres: Das Argument aus `THEOREM.md` §2 trägt die Symmetriebrechung genauso
   wie die Fallabdeckung, und ein Erzeugerzertifikat macht sie prüfbar.
3. **K66-Spine-Problem.** Wo ist es dokumentiert? Das Gate für Vorschlag C hängt
   daran, und ich konnte es nicht nachlesen.
4. **Wurden `fixed` je auf die Primärbits projiziert?** Falls doch, irgendwo
   protokolliert: Dann ändert sich A-2 von „fehlt" zu „nicht ausgewertet".
5. **Solverportfolio.** Wurde außer CaDiCaL 2.2.1 etwas probiert (Kissat,
   CryptoMiniSat mit Symmetrie-/XOR-Unterstützung, `--forcephase`)? Bei elf
   Aufgaben und 24 Threads ist ein Portfolio fast kostenlos.
6. **Zielsetzung.** Ist ein *bedingter* Satz (unter Makhnev–Minakova) für die
   Projektziele akzeptabel, oder soll der Fixpunktsatz mit auditiert werden? Das
   ändert die Aufwandsschätzung erheblich.

---

## 10. Empfehlung in einem Satz

Die C2-Suche sollte **nicht beendet**, aber auch **nicht unverändert fortgesetzt**
werden: erst die Fortschrittsmessung auf Primärbits, dann die ungenutzte
Restsymmetrie unter Stab_H(L), dann Vorschlag A, dann Cubing als Zertifizierungs­pfad —
und keine weitere Langkampagne, bevor eine dieser Maßnahmen an einer Größe mit
Nenner einen Effekt gezeigt hat.
