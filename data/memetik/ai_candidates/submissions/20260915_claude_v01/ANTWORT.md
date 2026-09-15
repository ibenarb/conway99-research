# CONWAY99 — Startkandidaten für srg(99,14,1,2)

## 1. Modellkennung und Codeausführung

Modell: **Claude Opus 5** (Anthropic), Chat-Oberfläche mit Werkzeug zur Codeausführung.

**Code wurde tatsächlich ausgeführt.** Alle in diesem Bericht genannten Zahlen,
Prüfflags und Graphdaten stammen aus echten Läufen von `generator.py` in einem
Linux-Container mit CPython 3.12.3. Nichts ist geschätzt oder aus dem Gedächtnis
zitiert. Die drei beiliegenden `.g6`-Dateien sind die Ausgabe dieser Läufe und
wurden zusätzlich unabhängig mit NetworkX wieder eingelesen und nachgeprüft
(NetworkX wird vom Generator selbst **nicht** benötigt).

---

## 2. Konstruktion, Suchraum und Begründung der harten Bedingungen

### 2.1 Der Ω-Rahmen ist nicht willkürlich, sondern erzwungen

Sei G ein srg(99,14,1,2), ∞ ein Knoten, N(∞) seine 14 Nachbarn, X die 84
übrigen Knoten.

* λ = 1 ⇒ jeder Nachbar a ∈ N(∞) hat mit ∞ genau einen gemeinsamen Nachbarn,
  der in N(∞) liegt. Also induziert N(∞) eine **perfekte Paarung** auf 14
  Punkten — das ist C. Die Wahl „Partner = a+7 mod 14“ ist reine Nummerierung.
* Ein x ∈ X ist zu ∞ nicht benachbart, also hat x wegen μ = 2 genau **zwei**
  Nachbarn in N(∞); x bestimmt damit ein Paar {a,b} ⊂ N(∞).
* Partnerpaare sind ausgeschlossen: wäre x zu a und a+7 benachbart, so hätte
  die **Kante** a–(a+7) die zwei gemeinsamen Nachbarn ∞ und x, im Widerspruch
  zu λ = 1.
* Für nicht benachbarte a,b ∈ N(∞) (also b ≠ a+7) liefert μ = 2 genau einen
  gemeinsamen Nachbarn außer ∞, und der liegt in X. Die Zuordnung
  x ↦ {a,b} ist also eine **Bijektion** von X auf die
  C(14,2) − 7 = 91 − 7 = **84** Nicht-Partnerpaare. Damit ist P vollständig
  festgelegt, es bleibt keine Wahlfreiheit.
* Jeder Außenknoten hat 14 − 2 = **12** Nachbarn innerhalb von X: Zeilensumme
  von H ist 12.

**Die Gleichung PH = 2J − (C+I)P** codiert exakt die λ/μ-Bedingungen für alle
Paare (a, x) mit a ∈ N(∞), x ∈ X: Es ist (PH)ₐₓ = #{y ∈ X : a ∈ y, y ~ x} und
(2J − (C+I)P)ₐₓ = 2 − Pₐₓ − P₍ₐ₊₇₎ₓ. Fallunterscheidung:

| Lage | gefordert | linke Seite | rechte Seite |
|---|---|---|---|
| a ∈ x (Kante) | λ = 1 | 1 | 2 − 1 − 0 = 1 |
| a ∉ x, a+7 ∈ x | μ = 2, davon a+7 schon einer | 1 | 2 − 0 − 1 = 1 |
| a ∉ x, a+7 ∉ x | μ = 2 | 2 | 2 − 0 − 0 = 2 |

Alle Bedingungen an Paaren innerhalb {∞} ∪ N(∞) sind durch C und P bereits
automatisch erfüllt. **Frei — und damit der eigentliche Suchraum — bleibt
ausschließlich der Außen-Außen-Block H.**

### 2.2 Lokale Umformulierung von Ω (Grundlage aller drei Suchen)

Für x = {a,b} ∈ X sei n_ℓ(x) die Zahl der H-Nachbarn von x, die das Label ℓ
tragen. Da jeder Nachbar zwei Labels trägt, ist Σ_ℓ n_ℓ(x) = 24. Die obige
Tabelle ist äquivalent zu

> n_ℓ(x) = 1 für ℓ ∈ {a, b, a+7, b+7}, und n_ℓ(x) = 2 für die übrigen zehn
> Labels.   (Summe 4·1 + 10·2 = 24 ✓)

Liest man die 12 Nachbarn von x als Kantenmenge eines Graphen auf Z₁₄, so ist
N(x) ein Graph mit zwölf Kanten, Grad 1 in a, b, a+7, b+7 und Grad 2 sonst —
also eine **disjunkte Vereinigung von Kreisen und genau zwei Wegen** mit den
Endpunkten a, b, a+7, b+7, ohne Partnerkanten. Diese lokale Fassung ist die
Grundlage der Nachbarschaftszüge in der Suche.

Die Zeilensumme 12 muss nicht separat erzwungen werden, sie folgt aus
Σ_ℓ n_ℓ(x) = 24.

### 2.3 Kandidat A — algebraisch: Z₁₄-symmetrisches H

Parametrisiere die Außenknoten als (a,d) ↔ {a, a+d} mit d ∈ {1,…,6}, a ∈ Z₁₄
(6·14 = 84, Bijektion). Verlange, dass H unter der Translation a ↦ a+1
invariant ist. Dann ist H durch Verbindungsmengen

    S[d][e] ⊆ Z₁₄ ,   (a,d) ~ (a+s, e)  ⟺  s ∈ S[d][e]

beschrieben, mit S[e][d] = −S[d][e] und 0 ∉ S[d][d]. Das sind **252 freie
Bits** statt 3486, und die Ω-Bedingung wird zu 84 Zählgleichungen

    Σ_e ( [ℓ ∈ S[d][e]] + [ℓ−e ∈ S[d][e]] ) = REQ[d][ℓ] ,  d = 1..6, ℓ ∈ Z₁₄.

Gelöst durch Min-Conflicts-Lokalsuche über Variablenkippungen (Seed 1,
9055 Schritte). *Herkunft:* Z₁₄ operiert auf den Paaren mit sechs Bahnen
gleicher Länge 14 und erhält die Partnerrelation, weil 7 unter Translation fix
bleibt — die Symmetrie ist also mit dem Rahmen verträglich.

### 2.4 Kandidat B — constraint-basiert: Drift aus A, ohne auferlegte Symmetrie

Ausgehend von A wird „destroy and repair“ im **exakt zulässigen Bereich**
betrieben: alle H-Kanten an k ∈ {12,16,20} zufälligen Außenknoten werden
gelöscht, danach wird mit Min-Conflicts auf E = Σ (n_ℓ(x) − Soll)² wieder
E = 0 hergestellt. Neben einfachen Kantenkippungen benutzt die Reparatur
**zusammengesetzte Tauschzüge**: ersetze Nachbar {ℓ,m} durch {ℓ′,m}; das
verschiebt genau eine Einheit von n_ℓ(x) nach n_{ℓ′}(x) und wirkt sonst nur an
zwei weiteren Knoten. Akzeptiert werden nur nicht verschlechternde Lösungen
bezüglich F (mit kleiner Toleranz), so dass die Kette innerhalb von Ω wandert
und F nebenbei sinkt.

*Empirische Beobachtung (gemessen, nicht bewiesen):* Zerstörungen an ≤ 5 Knoten
werden **identisch** repariert — das System ist lokal starr. Erst ab etwa zehn
gelöschten Nachbarschaften driftet die Lösung wirklich.

### 2.5 Kandidat C — kombinatorisch: Dreieckszerlegung im λ-Suchraum

λ = 1 bei Grad 14 heißt: die Kantenmenge zerfällt in Dreiecke, jeder Knoten
liegt in genau 7 davon, je zwei Knoten in höchstens einem. Gesucht ist also ein
**partielles Steiner-Tripelsystem** mit 99 Punkten, 231 Blöcken und Replikation
7 (99·7/3 = 231, 231·3 = 693 = 14·99/2 ✓), dessen Blockgraph **keine
transversalen Dreiecke** enthält.

Schlüssel für die Suche: Fügt man {u,v,w} ein, so entsteht genau dann kein
zweiter gemeinsamer Nachbar für irgendeine Kante, wenn die drei Paare *vor* dem
Einfügen **keinen** gemeinsamen Nachbarn haben. (Begründung: u gewinnt die
Nachbarn v,w; ein neuer zweiter gemeinsamer Nachbar entsteht nur für Paare
(x,y) mit x ∈ {v,w}, y ∈ N_alt(u), und „v benachbart zu N_alt(u)“ ist
gleichbedeutend mit N_alt(u) ∩ N_alt(v) ≠ ∅.) Die Invariante (A²)ᵢⱼ ≤ 1 auf
Kanten bleibt damit während der ganzen Konstruktion erhalten; bei 231 Blöcken
ist sie automatisch = 1. Gebaut wird greedy vom Knoten kleinsten Grades aus,
mit gezielter Ejection-Reparatur (Entfernen von Blöcken in der Nähe des
blockierten Knotens), Seed 4.

### 2.6 Geprüftes Hindernis: keine Cayley-Graphen im λ-Suchraum

Vorab argumentativ, dann erschöpfend nachgerechnet:

* |G| = 99 = 3²·11. n₁₁ ≡ 1 (mod 11) und n₁₁ | 9 ⇒ n₁₁ = 1; n₃ ≡ 1 (mod 3) und
  n₃ | 11, und 11 ≡ 2 (mod 3) ⇒ n₃ = 1. Beide Sylow-Gruppen sind normal, G ist
  direktes Produkt und daher **abelsch**: G ≅ Z₉₉ oder G ≅ Z₃×Z₃×Z₁₁.
* In einem Cayley-Graphen mit λ = 1 zerfallen die 231 Dreiecke in
  Translationsbahnen der Länge 99 (volle Bahn, 3 Dreiecke pro Punkt) oder 33
  (kurze Bahn = Nebenklassen einer Untergruppe der Ordnung 3, 1 Dreieck pro
  Punkt). Aus 7 = 3m + k folgt (m,k) ∈ {(2,1), (1,4), (0,7)}.
* **k = 4** gibt es nur in Z₃×Z₃×Z₁₁, und dort sind das *alle* vier
  Untergruppen der Ordnung 3; ihre Vereinigung ist E₉ \ {0}, jede E₉-Nebenklasse
  wird zum **K₉**. Das ist mit λ = 1 unvereinbar: jede innere Kante hätte
  mindestens sieben gemeinsame Nachbarn. (Genau das im Auftrag genannte
  Hindernis.)
* **k = 7** ist unmöglich, da es höchstens vier Untergruppen der Ordnung 3 gibt.
* Bleibt **k = 1, m = 2**. Dieser Fall wurde für beide Gruppen erschöpfend
  durchsucht (1440 bzw. 1442 Basisblock-Bahnen, alle disjunkten Paare):

> **Ergebnis: Es gibt keinen Cayley-Graphen über einer Gruppe der Ordnung 99 im
> λ-Suchraum.** Knotentransitivität via reguläre Gruppenoperation scheidet als
> Konstruktionsprinzip aus. Kandidat C musste deshalb ohne sie gebaut werden.

Dieselbe Rechnung erklärt auch, warum die naheliegenden Zirkulanten (etwa
C₉₉(1,2,3,5,6,11,33) aus den Basisblöcken {0,1,3}, {0,5,11}, {0,33,66}) zwar
ein partielles Steiner-System liefern, aber stets transversale Dreiecke
erzeugen — bei diesem Beispiel treten die Werte (A²)ᵢⱼ ∈ {1,2,5,6} auf Kanten
auf.

---

## 3. Tatsächlich ausgeführte Prüfungen und Ergebnisse

Bewertung wie gefordert über **alle** 4851 ungeordneten Paare i<j:
r_ij = (A²)_ij + A_ij − 2.

| | Kandidat A | Kandidat B | Kandidat C |
|---|---|---|---|
| Suchraum | Ω | Ω | λ |
| Datei | `kandidat_01.g6` | `kandidat_02.g6` | `kandidat_03.g6` |
| n / Grade / Kanten | 99 / {14} / 693 | 99 / {14} / 693 | 99 / {14} / 693 |
| A symmetrisch, Diagonale 0 | ja / 0 | ja / 0 | ja / 0 |
| H: symmetrisch, Diag 0, Zeilensumme | ja / 0 / 12 | ja / 0 / 12 | — |
| **PH = 2J − (C+I)P elementweise** | **erfüllt** | **erfüllt** | — (nicht anwendbar) |
| **(A²)_ij auf Kanten** | 0…5 | 0…5 | **konstant 1** |
| **W** | 2338 | **2333** | 2729 |
| **L1** | 3192 | **3070** | 3596 |
| **F** | 5180 | **4798** | 5476 |
| **L∞** | 4 | 5 | 4 |
| invariant unter a ↦ a+1 auf Z₁₄ | **ja** | **nein** | nein |

Verteilung von (A²)_ij über die Nichtkanten:

* A: {0:322, 1:910, 2:2226, 3:504, 4:168, 5:28}
* B: {0:258, 1:970, 2:2175, 3:528, 4:178, 5:42, 6:6, 7:1}
* C: {0:373, 1:1052, 2:1429, 3:877, 4:366, 5:55, 6:6}

Weitere ausgeführte Prüfungen:

* Ω-Gleichung für A und B **elementweise** über alle 14·84 = 1176 Einträge
  verglichen, maximale Abweichung 0.
* Kandidat C: alle 693 Kanten einzeln geprüft, (A²)_ij = 1 ausnahmslos; zusätzlich
  geprüft, dass keine zwei der 231 Tripel ein Paar teilen.
* Die drei `.g6`-Dateien wurden zurückgelesen (eigener Decoder und unabhängig
  NetworkX `from_graph6_bytes`): jeweils n = 99, 693 Kanten, alle Grade 14,
  bei `kandidat_03.g6` λ ≡ 1. Zeilenlänge 813 Zeichen = 4 Kopfbytes +
  ⌈4851/6⌉ = 809 Datenbytes, wie für graph6 ohne optionalen Header erwartet.
* Symmetrische Differenz der Kantenmengen von H(A) und H(B): **786** Kanten;
  bei je 504 Kanten teilen sich die beiden also nur 111 Kanten.

### Strukturelle Unterschiede — was belegt ist und was nicht

**Belegt (Isomorphie-Invariante):** Die Multimenge {(A²)_ij : ij Nichtkante}
bleibt unter Isomorphie erhalten. Die drei oben angegebenen Verteilungen sind
paarweise verschieden (B nimmt die Werte 6 und 7 an, A nicht; C hat auf Kanten
konstant 1, A und B nicht). Also sind **A, B und C paarweise nicht isomorph**.
Das ist eine Rechnung, keine Vermutung.

**Nicht behauptet:** Über die vollen Automorphismengruppen wird nichts
behauptet. Für B ist ausschließlich geprüft, dass die *eine* vorgegebene
Permutation (Translation a ↦ a+1) kein Automorphismus ist — daraus folgt nicht,
dass B asymmetrisch wäre. Ebenso wird **kein** neues Einzugsgebiet, keine Nähe
zu einer Lösung und keine Fortsetzbarkeit zu einem srg(99,14,1,2) behauptet.

### Erzwungene Eigenschaften (offengelegt)

* **Kandidat A** besitzt konstruktionsbedingt einen Automorphismus der Ordnung
  14, der ∞ fixiert und N(∞) zyklisch permutiert. Das ist eine bewusst gesetzte
  Einschränkung zur Reduktion des Suchraums, keine hergeleitete Eigenschaft. In
  der Literatur existieren Nichtexistenzaussagen für Automorphismen kleiner
  Primordnung bei srg(99,14,1,2); ich habe diese **nicht** nachgerechnet und
  stütze mich nicht darauf, weise aber darauf hin, dass A als Startpunkt für
  eine Vervollständigung deshalb riskanter ist als B.
* **Kandidat B** erbt von A die Struktur des Ω-Rahmens (die ohnehin erzwungen
  ist), aber keine Symmetrie; der Drift ist mit 786 abweichenden Kanten
  erheblich.
* **Kandidat C** hat keine auferlegte Symmetrie, erfüllt dafür aber nur die
  λ-Bedingung; über μ wird nichts erzwungen, und die μ-Verteilung ist
  entsprechend breit.
* Alle drei Kandidaten sind 14-regulär und einfach; das ist in beiden
  Suchräumen gemeinsame Pflichtbedingung.

### Offene Punkte

* Kein Kandidat erfüllt beide Bedingungen gleichzeitig; F = 0 wird nicht erreicht
  und wird auch nicht behauptet.
* Ob der Ω-Suchraum bei festgehaltenem Z₁₄ überhaupt eine Fortsetzung zu einem
  srg erlaubt, ist nicht untersucht.
* Ob F im Ω-Bereich deutlich unter 4798 gedrückt werden kann, ist offen; die
  LNS-Optimierung war nach 100 Runden noch nicht ausgereizt (15 akzeptierte
  Schritte, weiterhin fallend).
* Die Beobachtung der lokalen Starrheit (≤ 5 zerstörte Nachbarschaften werden
  eindeutig repariert) ist empirisch, nicht bewiesen.
* Vollständige Automorphismengruppen und kanonische Formen wurden nicht berechnet.

---

## 4. Abhängigkeiten, Seeds und reproduzierbarer Aufruf

**Abhängigkeiten:** ausschließlich die Python-Standardbibliothek.
Getestet mit CPython 3.12.3 unter Linux. Kein NumPy, kein SAT-Solver, kein
NetworkX (Letzteres wurde nur für die *unabhängige Gegenprüfung* der
`.g6`-Dateien benutzt, nicht vom Generator).

**Determinismus:** Alle Zufallsentscheidungen laufen über
`random.Random(<fester Seed>)`. Es werden nirgends Mengen von Tupeln iteriert
(Verletzungen sind als ganze Zahl x·14+ℓ codiert, Nachbarmengen werden vor der
Iteration sortiert), daher ist der Lauf unabhängig von `PYTHONHASHSEED`.

**Seeds:** Stufe A `seed = 1`; Stufe B `seed = 11`, 100 Runden; Stufe C
Seeds 0,1,2,3,**4** (die ersten vier scheitern, Seed 4 liefert die Zerlegung).

**Aufruf:**

```
python3 generator.py            # alle Stufen, ca. 4-5 Minuten
```

oder stufenweise (Zwischenergebnisse liegen als JSON im Arbeitsverzeichnis):

```
python3 generator.py A          #   3 s  -> cand_A.json
python3 generator.py C          #  52 s  -> cand_C.json
python3 generator.py cayley     #   4 s  -> cayley.json
python3 generator.py B          # 187 s  -> cand_B.json   (benoetigt cand_A.json)
python3 generator.py final      #   3 s  -> kandidat_01..03.g6, bewertung.json
```

Gemessene Laufzeiten des tatsächlichen Laufs sind oben angegeben.
`cand_A.json`, `cand_B.json`, `cand_C.json` und `bewertung.json` liegen bei, so
dass `python3 generator.py final` ohne erneute Suche reproduziert werden kann.

**Knotenreihenfolge der graph6-Daten** (kanonisch wie im Auftrag definiert,
für `kandidat_01.g6` und `kandidat_02.g6`):

* Index 0 = ∞
* Index 1+a = Label a, a = 0,…,13 (Partner a ↔ a+7 mod 14)
* Index 15+j = das j-te Nicht-Partnerpaar {a,b}, a<b, in lexikographischer
  Ordnung, j = 0,…,83

Für `kandidat_03.g6` (λ-Suchraum) ist die Knotennummerierung 0,…,98 beliebig
und trägt keine Zusatzbedeutung.

**Format:** Standard-graph6 ohne optionalen Header, eine Zeile je Datei,
abgeschlossen mit `\n`.

---

## 5. Dateien in diesem Paket

| Datei | Inhalt |
|---|---|
| `ANTWORT.md` | dieser Bericht |
| `generator.py` | vollständiger Generator, alle Stufen, Verifikation, graph6 |
| `kandidat_01.g6` | Kandidat A — Ω, Z₁₄-symmetrisch |
| `kandidat_02.g6` | Kandidat B — Ω, ohne auferlegte Symmetrie |
| `kandidat_03.g6` | Kandidat C — λ-Suchraum, (A²)_ij ≡ 1 auf Kanten |
| `cand_A.json`, `cand_B.json` | Adjazenzlisten von H (84 Außenknoten) |
| `cand_C.json` | die 231 Tripel |
| `cayley.json` | Ergebnis der erschöpfenden Cayley-Prüfung |
| `bewertung.json` | maschinenlesbare Fassung der Bewertungstabelle |

ENDE DER ABGABE
