# Externes Review: Conway99 — nicht-evolutionärer Forschungszweig

**Auftraggeber:** Ralph Beckmann · **Datum:** 13. September 2026
**Gegenstand:** Bewiesene Ausschlüsse, mathematische Transfers, externe Abhängigkeiten und nächster Forschungsauftrag im mathematischen, geometrischen und zertifizierenden Projektzweig. Der evolutionäre Teil ist nicht Gegenstand.

---

## 0. Prüfbasis und Arbeitsweise

| Referenz | Rolle |
|---|---|
| `769ee6df774a11b90ed18982ce6ff5aca325260a` | feste Forschungsbasis (Artefakte) |
| `450a173` (Branch `research/algebra-memetic-20260912`) | Bilanzschicht über der Basis |
| `b279cd6de420bc4ad64869c8c7f99d653c73a195` | historische Referenz (Fixdreieck, Versöhnung, FULLCERT, vendor/qsat) |
| `e8f4d629cdf03b4bb14ebed01e4ebe7e8dbf3f8b` | externes Repository `infinityscroll/conway99-order3-f27` |

Gearbeitet wurde in isolierten Git-Worktrees. In die Forschungsbasis wurde nichts zurückgeschrieben; Prüfer, die Ergebnisdateien erzeugen, liefen ausschließlich in Scratch-Kopien. Es wurden keine unbegrenzten Solverläufe und keine neuen Suchkampagnen gestartet.

**Evidenzstufen**, wie sie in diesem Bericht verwendet werden: *selbst hergeleitet* (Mathematik vollständig nachvollzogen) · *selbst reproduziert* (Rechnung mit eigenem, unabhängig geschriebenem Code wiederholt) · *Lauf wiederholt* (Projektcode in Scratch ausgeführt, Ausgabe verglichen) · *gelesen* (Artefakt inspiziert, nicht nachgerechnet) · *ungeprüft*.

---

## 1. Gesamturteil

Die zentrale zu prüfende Aussage ist **durch die Evidenz gedeckt**:

> Mit den bezeichneten externen Automorphismensätzen bleiben als Symmetrieaufgaben die freie C3-Wirkung mit τ=6 und die Involution mit einem Fixpunkt. Das Projekt schließt zwei historische L-Typen aus, reduziert eine notwendige T-Gram-Aufgabe auf 26 Typen und besitzt einen eigenen abgeschlossenen K66-Fallbeweis. Es schließt weder alle freien C3-Wirkungen noch Involutionen noch asymmetrische Conway-Graphen aus.

In keinem geprüften Teil wurde eine falsche mathematische Aussage gefunden. Alle Befunde sind Präzisierungslücken in der Darstellung, nicht Fehler im Ergebnis. In zwei Fällen (F1, F7) **unterschätzt** die Bilanz die eigene Leistung.

Auch die Korrektur der vorangegangenen Auskunft ist an den Primärquellen zutreffend: unter Literaturannahme E1 ist der gesamte Fixdreiecks-Zweig bereits ausgeschlossen; `t145` ist eine interne Nachvollzugspflicht, keine offene mathematische Symmetrieaufgabe. τ=27 ist ebenfalls keine offene globale Symmetrieaufgabe mehr.

Bemerkenswert: die Bilanz hat dem Reviewer zwei ihrer schwächsten Stellen selbst angezeigt (fehlende sechs f27-Marker im gespeicherten Log; 897 Hauptblätter ohne neuen Replay). Beide Selbstangaben erwiesen sich als korrekt. Die erste wurde in diesem Review geschlossen, die zweite bleibt eine echte Zugangsgrenze.

---

## 2. Tabelle jeder tragenden Aussage

| # | Aussage | Geltungsbereich | Quelle | Eigene Prüftätigkeit | Urteil | Restpflicht |
|---|---|---|---|---|---|---|
| A1 | 693 Kanten, 231 Dreiecke, 4158 Nichtkanten, 2079 C4; A²+A=12I+2J | global | ZWISCHENFAZIT §3 | selbst hergeleitet | **akzeptiert** | — |
| A2 | N(v)≅7K2; 84 äußere Knoten ↔ 84 nichtbenachbarte Paare, bijektiv | global, symmetriefrei | ZWISCHENFAZIT §3 | selbst hergeleitet, C(14,2)−7=84 | **akzeptiert** | — |
| A3 | Q1=14·1, Q²+Q=12I+6J, Q symmetrisch | freie C3 | ZWISCHENFAZIT §5.1 | selbst hergeleitet | **akzeptiert** | — |
| A4 | Q=2D_T+S+2L, L 2-Faktor auf U | freie C3 | Layer-A-Spec | selbst hergeleitet; unabhängig bestätigt durch THEOREM.md des Fremdrepos | **akzeptiert** | — |
| A5 | Kein Gewicht-2-Eintrag zwischen zwei Dreiecksorbits ⇒ B_TT = 2I+X | freie C3 | implizit | **selbst bewiesen** (λ=1-Eindeutigkeit der Dreieckskante) | **akzeptiert** | nicht als Lemma geführt (F5) |
| A6 | Kreuzblock C ist binär | freie C3 | ZWISCHENFAZIT §5.3 | **selbst bewiesen**: Σ_j C²=Σ_j C=12−d_i ⇒ x²=x | **akzeptiert** | nicht als Lemma geführt (F5) |
| A7 | CC^T = 6I+6J−X²−5X | freie C3, τ=6 | ZWISCHENFAZIT §5.3 | selbst hergeleitet aus (Q²+Q)_TT | **akzeptiert** | — |
| A8 | 231=τ+3m ⇒ τ≠13,20 | freie C3 | O3_tau_mod3_theorem | selbst nachgerechnet | **akzeptiert** | — |
| A9 | E3=(4/7)I+(1/7)A−(2/77)J ist der 3-Eigenraumprojektor, Rang 54 | global | ZWISCHENFAZIT §5.1 | selbst hergeleitet, Spektrum 14/3⁵⁴/(−4)⁴⁴, Spur 4158/77=54 | **akzeptiert** | — |
| A10 | 3-adische Integrität von E3 | global | ebd. | Nenner 7, 77 teilerfremd zu 3 | **akzeptiert** | — |
| A11 | Bild(E3) projektiv ⇒ frei über Z₃[C3] ⇒ tr(gE3)=0 ⇒ a1=18 ⇒ τ=6 | **nur freie C3** | ebd.; Ishida v2 §8.4 | **vollständig selbst nachvollzogen** | **akzeptiert** | Geltungsbereich strikt wahren |
| A12 | τ=27 ausgeschlossen | freie C3 | Bilanz | folgt bereits aus A11 allein | **akzeptiert** | siehe F1 |
| A13 | C4-Komponente in L unmöglich | freie C3 | O3_cycle_lemmas §3.3 | **selbst bewiesen**: (L²)=2 ⇒ 8+nichtneg=6 | **akzeptiert** | nur Nebensatz (F5) |
| A14 | 103 L-Typen | freie C3, τ=6 | AUSSCHLUSSBILANZ | selbst abgezählt: 103 (ohne C4-Regel 191); Ledgerliste elementweise identisch | **akzeptiert** | — |
| A15 | Lemma B: S_wa+S_wb+S_wc=1 für jede C3-Komponente, alle 30 äußeren w | freie C3, τ=6 | Layer-A-Spec §6 | **selbst bewiesen** (AMO aus Paargleichung, ALO aus Gradzählung 30=3·10) | **akzeptiert**, Redundanz bestätigt | — |
| A16 | Layer B ⊆ A, gleicher Lösungsraum | freie C3 | Layer-A-Spec §7 | Ableitung geprüft | **akzeptiert**; A/B-Laufzeitunterschiede sind Encodingeffekte | — |
| A17 | Zykluslokale Fingerabdrücke 6/66/478/14615 und 6/66/408/6717 | C5–C8 | O3_cycle_lemmas §12 | **mit eigenem Enumerator exakt reproduziert** | **akzeptiert** | — |
| A18 | 156 Isomorphieklassen, 32.768 beschriftete X | τ=6 | ZWISCHENFAZIT §5.3 | selbst enumeriert; die 156 Projektmatrizen sind exakt ein vollständiges, redundanzfreies Repräsentantensystem | **akzeptiert** | — |
| A19 | 87 Ausschlüsse durch negativen Gram-Eintrag | τ=6 | ebd. | selbst nachgerechnet: 87 | **akzeptiert** | — |
| A20 | 25 Ausschlüsse durch fehlende PSD | τ=6 | ebd. | selbst nachgerechnet, exakte Rationalarithmetik über **alle** Hauptminoren: 25 | **akzeptiert** | — |
| A21 | 18 exakte rationale Separationszeugnisse | τ=6 | tau6_farkas_18.json | **alle 18 selbst validiert**, ganzzahlig skaliert, gegen alle 64 Profile | **akzeptiert**, stärker als behauptet (gültig über ℝ₊) | siehe F2 |
| A22 | 26 ganzzahlige Gram-Zeugen, je genau 27 Spalten | τ=6 | tau6_gram_44.json | **alle 26 selbst verifiziert** | **akzeptiert** | — |
| A23 | Ergebnis 26, nicht 22; die vier älteren Ausschlüsse sind enthalten | τ=6 | ZWISCHENFAZIT §5.3 | selbst bestätigt: {19,20,36,37} ⊂ den 18 | **akzeptiert** | — |
| A24 | X↦G injektiv; keine Orbitkollisionen unter den 44 | τ=6 | implizit | **selbst bewiesen und nachgerechnet** | **akzeptiert** | nicht dokumentiert |
| A25 | 156 X-Statuszuordnungen im `exclusion_ledger.json` | Bilanz | ledger | **156/156 stimmen** mit meiner Rechnung | **akzeptiert** | — |
| A26 | f27: 13 DRAT-Beweise frisch geprüft, CNFs regeneriert | extern | infinityscroll @ e8f4d629 | **vollständig selbst ausgeführt** (s. §4) | **akzeptiert**, Stufe REPRODUCED | — |
| A27 | f27 ist Quotientenausschluss, nicht bloßer Lift-Ausschluss | extern | THEOREM.md | Satzformulierung geprüft | **akzeptiert** | — |
| A28 | 27 Bilanzquellen mit Commit/Länge/SHA256/Blob-ID | Bilanz | source_manifest.json | **alle 27 byteexakt verifiziert** (23 Basis, 4 historisch) | **akzeptiert** | — |
| A29 | Fixdreieck: 72 Klassen = 29 V3 + 1 K66 + 42 N | interner Nachvollzug | AUSSCHLUSSBILANZ | gegen V3-Frontierbericht geprüft: 22/40-Regel reproduziert s=0 **exakt**; s=1-Hartfälle exakt k66/k68/k70; 43−1=42 | **akzeptiert unter Voraussetzung** (V3-Klassifikator korrekt) | siehe F4 |
| A30 | E1–E4 ⇒ Restgruppen 1, C2, C3 | extern | Literatur | Bilanztext geprüft, **Primärliteratur nicht gelesen** | **ungeprüft** | Literaturprüfung |
| A31 | Involution: einziger Fixpunkt ⇒ t vertauscht jede Kante von N(v) ⇒ eindeutige Wirkung auf 84 Paarlabels, Typ 1¹2⁴⁹ | unter E2 | ZWISCHENFAZIT §7 | **selbst nachvollzogen und ergänzt** (s. §7) | **akzeptiert** als WLOG-Reduktion, **kein** UNSAT-Beweis | vollständiges Matrixproblem |
| A32 | Modulares Liftkriterium erfordert exakten Quotienten | Lift | ZWISCHENFAZIT §7 | **Lauf wiederholt**, `lifts.json` identisch | **akzeptiert** | — |
| A33 | δ=5-Solver-Signale sind kein Graph-/Polytopausschluss | geometrisch | ZWISCHENFAZIT §3 | Einordnung geprüft | **akzeptiert** (korrekte Selbstbeschränkung) | — |
| A34 | Reimbayev: Differenz 94.034.160, kein reparierter Filter | Quellenkritik | ZWISCHENFAZIT §8 | nur gelesen | **REPORTED** | — |
| A35 | K66: Stabilisator 64, 246 Bahnen, Burnside 15.744 | K66 | K66_BEWEISABSCHLUSS | **vollständig selbst reproduziert**; `orbit_partition.json` byteidentisch | **akzeptiert** | — |
| A36 | 223 Bahnen mit exakt negativem Hauptminor von G=C_H−H²−H | K66 | negative_minors.json | **alle 223 Determinanten selbst nachgerechnet** | **akzeptiert** | — |
| A37 | 897 Hauptblätter: archivierte Cake-Evidenz, kein neuer Replay | K66 | K66_BEWEISABSCHLUSS | gelesen | **REPORTED**, korrekt gekennzeichnet | nicht per Git behebbar |
| A38 | P²+P = 12I+6J−3 diag(J₄,J₄,J₄,0₂₀) und G=ZᵀZ | K66 | MATHEMATISCHER_AUDIT §3 | **selbst hergeleitet** | **akzeptiert** | — |
| A39 | 23 Restfälle: Ränge 4×11 / 19×12, 254 Einheiten, Codebindung | K66 | manifest + residual_links | **selbst reproduziert** | **akzeptiert** | — |
| A40 | Abschlussprüfer 1.0.1, Bindung an die kompakten Berichte | K66 | close_k66.py | **Lauf wiederholt**; alle 23 gepinnten Hashes verifiziert | **akzeptiert** | 8 Vollberichte fehlen |
| A41 | FULLCERT 488+168=656, vollständige Coverage der 512 Wurzelmuster | τ=6, (6,3⁷) | coverage_manifest_656.tsv | **selbst nachgerechnet** | **akzeptiert**, mit Präzisierung F6 | Bindung der Git-TSV |
| A42 | Lemma-CNF → Quotient-Transfer bei FULLCERT | τ=6, (6,3⁷) | certificate_manifest.json, vendor/qsat | **Transferrichtung selbst bewiesen**; Encoder hashverifiziert und mathematikkonform | **akzeptiert** | — |
| A43 | (3⁹) historisch zertifiziert | τ=6, (3⁹) | Versöhnungsbericht | Hashangaben gelesen, kein Replay | **REPORTED** | Produktionsdateien extern |
| A44 | Momentfilter 6/34/309/5754 | C5–C8 | O3_cycle_lemmas §12 | **selbst reproduziert** | **akzeptiert** | — |

---

## 3. Liste tatsächlicher Fehler und Ungenauigkeiten

Keine der folgenden Positionen widerlegt ein Ergebnis. Es sind Darstellungs- und Nachvollziehbarkeitsmängel.

**F1 — Die f27-Kette ist mathematisch redundant, die Bilanz gewichtet sie zu hoch.**
τ=27 wird unter „Algebraischer τ=6-Schluss; *zusätzlich* eigenständig reproduzierte externe f27-Zertifikatskette" geführt. Formal richtig, aber A11 (a1=18 ⇒ τ=6) erledigt den Fall **allein und ohne jeden Computer**. Die 103 MiB Zertifikate und 13 DRAT-Beweise liefern keinen mathematischen Zugewinn, sondern Redundanzabsicherung. Die Bilanz sollte τ=27 als **Projekttheorem** ausweisen.

**F2 — „18 rationale Separationszeugnisse" suggeriert eine nicht bestehende 1:1-Zuordnung.**
Minimales Gegenbeispiel: das Zertifikat `atlas_index=4` ist strikt positiv auf **vier** Klassen {3, 19, 36, 37}; die Zertifikate 20, 21 und 38 sind auf derselben Fünfermenge {19,20,36,37,38} positiv. Die 18 Zertifikate überlappen stark und sind nicht minimal. Die Sachaussage („für jeden der 18 Ausschlüsse existiert ein exaktes Zeugnis") bleibt wahr und wurde bestätigt. Zusätzlich: die Zertifikatsdatei verwendet eine **um 1 verschobene Atlasnummerierung** (cert 4 → Klasse 3, cert 102 → Klasse 101). Das Projekt überbrückt das über Gram-Orbit-Matching statt über den Offset — funktioniert, ist unnötig fragil und nirgends dokumentiert.

**F3 — `verify_review.py` schreibt in die Forschungsbasis.**
Der Prüfer überschreibt `results/review_synthesis_20260912/verification.json`. Wer ihn im Checkout startet, verändert das zu prüfende Artefakt. Empfehlung: `--out`-Parameter mit Default außerhalb des Repos.

**F4 — Nicht dokumentierte Lücke in der 72er-Rekonstruktion.**
Die 62 s=0-Klassen sind Multimengen der Größe 3 über sieben lokalen D8-Typen; davon existieren 84, die Bilanz führt 62. Welche 22 Kombinationen warum ausfallen, ist aus der Bilanz nicht rekonstruierbar. Die 22/40-Aufteilung *innerhalb* der 62 stimmt exakt mit dem V3-Bericht überein — die Vorstufe nicht.

**F5 — Drei tragende Lemmata sind nicht als Lemmata geführt.**
A5 (B_TT=2I+X), A6 (Binarität von C) und A13 (C4-Ausschluss) sind Voraussetzungen der gesamten 156→26-Kette bzw. der Zahl 103, stehen aber nirgends als bewiesene Aussagen — A13 nur als Nebensatz. Alle drei wurden hier bewiesen; sie halten. Ohne sie wäre die Kette unbegründet.

**F6 — 656 Zertifikate sind nur 272 verschiedene Beweise.**
Bei 656 paarweise verschiedenen CNF-Hashes gibt es nur 272 verschiedene `raw_proof_sha256`: ein Beweis bedient 128 Zertifikate, einer 64, einer 32, sieben je 16, zwei je 8, vier je 4, 32 je 2, 224 sind Einzelstücke. Die Auflösung ist **unbedenklich**: jede Mehrfachgruppe ist exakt ein Teilwürfel des 9-Bit-Wurzelraums (128 ↔ `11*******`, 64 ↔ `011******`, 32 ↔ `0101*****`, 16 ↔ `00011****`), Gruppengröße = 2^(freie Positionen) exakt. Es sind legitime Präfixwiderlegungen. Zu präzisieren ist lediglich die Lesart: nicht 656 unabhängige Beweisartefakte.

**F7 — Der historische FULLCERT-Scope-Vermerk ist überholt, zugunsten des Projekts.**
Das Manifest notiert `"documented a1=18 conditionality; later tau in {13,20,27}"`. Im August 2026 war a1=18 eine übernommene Annahme und die übrigen τ offen. Beides ist inzwischen intern bewiesen (A8, A11). Der Geltungsbereich des Zertifikats ist heute **unbedingt**. Die Bilanz zieht diesen Gewinn nicht ein.

**F8 — FULLCERT-Hashbindung ist aus Git nicht schließbar.**
`coverage_input_sha256 = ed317be0…` ist ein selbstreferenzielles Feld in `certificate_manifest.json` und zeigt auf `/home/rb/…/coverage_input.json`, das nicht in Git liegt. Die committete `coverage_manifest_656.tsv` (SHA256 `a5958b74…`) ist an diese Kette nicht kryptographisch gebunden. Die „observed == recorded"-Aussage des Audits ist intern-zu-intern.

**Korrektur einer eigenen Fehlangabe (Teil 1 → Teil 2).**
Das K66-Laufmanifest wurde von mir zunächst als „nur auf dem Ryzen" eingestuft. Das war falsch: es liegt in Git unter `data/k66_star125_20260913/source_manifest.json` mit exakt dem gepinnten Hash `63cbc21e…`. Mein Suchfilter griff auf den Dateinamen `manifest.json`; das Projekt hat beim Commit umbenannt. Die Zugangsgrenze war enger als gemeldet — zu Lasten des Projekts. Gleiches gilt für die 23 Encoder-Fallberichte unter `results/k66_encoder_audit_20260913/reproduction/`.

---

## 4. Ausgeführte Reproduktionen

### 4.1 Quellenintegrität

Alle **27** Quellen aus `source_manifest.json` gegen Git-Blob-ID, Dateilänge und SHA256 geprüft — **keine Abweichung**. 23 auf der Basis `769ee6df`, 4 auf der historischen Referenz `b279cd6e`. Die 10 Dateien des historischen Encoders `vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat` gegen `PROVENANCE.json` geprüft — **keine Abweichung**.

### 4.2 T-Gerüstkette 156 → 69 → 44 → 26

Die Kette wurde **von Null neu aufgebaut**: eigene Isomorphieklassen-Enumeration, eigene G-Berechnung, exakte Rationalarithmetik, eigenständige Zertifikatsvalidierung.

| Stufe | Projektangabe | Eigene Rechnung |
|---|---:|---:|
| beschriftete X | 32.768 | **32.768** |
| Isomorphieklassen | 156 | **156**, deckungsgleich mit der Projektliste |
| negativer Gram-Eintrag | 87 | **87** |
| kein PSD (alle Hauptminoren) | 25 | **25** |
| exakt binär-Gram-ausgeschlossen | 18 | **18** |
| überlebend | 26 | **26** |

Überlebende Indizes exakt wie dokumentiert: 0, 1, 2, 5, 8, 13, 22, 24, 26, 27, 39, 40, 41, 46, 51, 52, 64, 65, 71, 72, 75, 95, 96, 98, 121, 122. Die vier älteren Ausschlüsse {19, 20, 36, 37} sind in den 18 enthalten — **26, nicht 22**, bestätigt. Alle 156 Statuszuordnungen im `exclusion_ledger.json` stimmen mit meiner Rechnung überein. Die 18 Farkas-Zeugnisse trennen bereits über ℝ₊ und sind damit stärker als für den ganzzahligen Fall nötig.

### 4.3 Zykluslemmata

Mit einem unabhängig geschriebenen Enumerator reproduziert:

| | C5 | C6 | C7 | C8 |
|---|---:|---:|---:|---:|
| Sehnenbelegungen gesamt | 32 | 512 | 16.384 | 1.048.576 |
| ohne innere Konsistenz | **6** | **66** | **478** | **14.615** |
| mit innerer Konsistenz | **6** | **66** | **408** | **6.717** |
| nach Momentfilter (Kappe min(m,12)) | **6** | **34** | **309** | **5.754** |

Alle acht vorregistrierten Fingerabdrücke stimmen. Die Warnung, eine pauschale Kappe 10 wäre unsound, ist berechtigt (Außenknoten in T haben S-Grad 12).

### 4.4 Externe f27-Kette

Release-Asset `conway99-f27-certificates-v0.1.0.tar.gz` (89.171.452 Bytes) heruntergeladen, SHA256 gegen `RELEASE_ASSET.sha256` geprüft — **stimmt**. `drat-trim` aus dem Quelltext selbst kompiliert.

- Schnellaudit: `PASS_F27_CERTIFICATE_BUNDLE fresh_proofs=False proofs=13`
- Vollreplay mit eigenem Checker: **alle 13 `PASS_FRESH_DRAT`**, `fresh_proofs=True proofs=13`
- Projektzusatzskript `replay_f27.py`: **alle sechs `PASS_REGENERATED_INITIAL_GRAM`**

Die von der Bilanz selbst offengelegte Evidenzlücke (sechs Marker fehlten im gespeicherten Log) ist damit geschlossen. Der externe Satz ist ein **Quotientenausschluss** („no such orbit matrix exists"), nicht bloß ein Lift-Ausschluss.

### 4.5 K66

Die gesamte Arithmetik- und Bahnenschicht wurde **mit eigenem Code aus der dokumentierten Modellbeschreibung** neu implementiert.

Mathematische Grundlage selbst hergeleitet: beim Kollaps auf 32 Dreierorbits plus drei Fixpunkte trägt jeder angeschlossene Orbit i∈A_r über f_r den Zusatzterm 1·3, sonst nichts — also P²+P = 12I+6J−3·diag(J₄,J₄,J₄,0₂₀). Mit P=[[H,Zᵀ],[Z,B]] folgt ZᵀZ = C_H−H−H² = G; Z ganzzahlig ⇒ G notwendig PSD. Ein negativer Hauptminor ist ein echter Widerspruch.

| Prüfgegenstand | Ergebnis |
|---|---|
| Stabilisator, erschöpfend über 6.144 Kandidaten | Ordnung **64**; Identität, Inverse, Abschluss, Zielkovarianz geprüft |
| `stabilizer.json` | mit meiner Permutationsmenge identisch |
| Burnside-Fixpunktsumme | **15.744**; 15.744/64 = **246** |
| Bahnenpartition | **246** Bahnen, 60×32 + 186×64 = 13.824; Bahn-Stabilisator-Satz je Bahn |
| `orbit_partition.json` (191.144 Bytes) | **byteidentisch** |
| 223 Hauptminoren | alle mit eigener rationaler Gauß-Elimination neu berechnet, **alle 223 exakt gleich**, alle strikt negativ |
| 223 `gram_sha256` | alle stimmen |
| Gegenkontrolle: ist eine der 223 doch PSD? | **0 von 223** |
| 23 Restbahnen, exakte Gram-Ränge | **4×11, 19×12** |
| Partition | 223 ∩ 23 = ∅, Vereinigung = alle 246 Codes; 12.672 + 1.152 = 13.824 |
| 254 kanonische Primärbelegungen | für alle 23 mit eigener Implementierung reproduziert |
| Matching-Codes ↔ `v4_0xxxx` | für alle 23 identisch |
| 23 gepinnte veröffentlichte Fallberichte | **alle 23 Hashes verifiziert**, gemeinsame Identität `8a9ed864…`, alle PASS |

**Vollständiger Lauf des Abschlussprüfers 1.0.1** in offline zusammengestelltem Workspace (Manifest und Fallberichte aus Git, `gh api` durch lokalen Git-Blob-Stub ersetzt): `K66_ARITHMETIC_AND_ORBIT_COVERAGE_PASS`, 1,66 s.

Vergleich der sechs Ausgabedateien gegen die committeten:

- `identity.json`, `negative_minors.json`, `orbit_partition.json`, `stabilizer.json` — **byteidentisch**
- `summary.json` — Abweichung nur in `wall_seconds`
- `residual_links.json` — Abweichung nur im Feld `encoder_case_result_sha256`, bei **genau 8 von 23** Fällen (9232, 9316, 9317, 9322, 9323, 9331, 9332, 9333)

Diese acht sind exakt die Fälle mit Reduktionsrunden: ihr *vollständiger* lokaler Bericht enthält `rounds[].before/after` und `cnfs[].depends_on_earlier_removed`, die in der veröffentlichten kompakten Fassung fehlen. Bei den übrigen 15 sind voll und kompakt identisch. Meine Werte stimmen für die acht mit `encoder_published_result_sha256` überein. Das ist eine präzise lokalisierte Datengrenze — und bestätigt die dokumentierte Fehlerkorrektur: genau diese Serialisierungsverwechslung war der Fehler der Version 1.0.0.

### 4.6 FULLCERT-Coverage

656 Zeilen = 488 ROOT + 168 LEAF. Die 488 Roots decken 488 der 512 möglichen 9-Bit-Wurzelmuster direkt; die 168 Leaves decken die restlichen 24. Vereinigung = alle 512, keine Lücke. Alle 656 mit `cake_exit=0`. Übereinstimmung mit der protokollierten Prüferzeile `roots=512 direct488=488 hard24=24`. Zur Beweisanzahl siehe F6.

### 4.7 Liftkontrollen

`check_lifts.py` in Scratch-Kopie neu ausgeführt; erzeugtes `lifts.json` **identisch** zum committeten.

| Fall | Phasen | modular zulässig | echte SRG | Fehlalarme |
|---|---:|---:|---:|---:|
| Rook-Quotient 1 (exakt) | 27 | 9 | 9 | **0** |
| Rook-Quotient 2 (exakt) | 27 | 9 | 9 | **0** |
| nicht exakter Quotient | 729 | 2 | 0 | **2** |

Die Domänengrenze ist damit an einem konkreten Gegenbeispiel belegt, nicht bloß behauptet. Es bleibt ein Kontrollbefund, kein allgemeiner Satz — so stellt es die Bilanz auch dar.

---

## 5. Fehlende Daten und nicht ausgeführte Replays

### 5.1 Echte Zugangsgrenzen (auch mit unbegrenzter Zeit nicht per Git behebbar)

1. Die **897 K66-Hauptlaufblätter**, **28 Replay-Beweise** und **125 Profilbeweise** — Cake-Bestätigungen archiviert, Proofdateien extern.
2. Die **FULLCERT-Produktionsbeweise** (~200,76 GiB gzip) sowie `coverage_input.json`, an dem die Audit-Hashkette hängt (F8).
3. Die **acht vollständigen K66-Encoder-Fallberichte** mit Reduktionsrunden (§4.5).

Das Projekt deklariert 1. und 2. korrekt und behauptet für sie keinen Replay. Ein vollständiger frischer Produktionsreplay ist mit Git allein ausgeschlossen; das ist eine Zugangsgrenze, kein Gegenbeweis.

### 5.2 Bewusst nicht geprüft

- **Primärliteratur E1–E5** (Crnković–Maksimović Theorem 7.1 und §7, Behbahani Theorem 1.6, Makhnev–Minakova, Cesarz–Woldar, Ishida v2 §8.4). Die Bilanz behauptet für sie ausdrücklich keine Reproduktion fremder Computerbeweise; diese Selbstbeschränkung ist korrekt. A11 zeigt allerdings, dass E5 intern ersetzbar ist.
- **Reimbayev-Audit** (`results/research_20260912/reimbayev.json`) — als REPORTED übernommen.
- **K66-Zertifikatsschicht im engeren Sinn**: 167 CNF-Bytevergleiche, BDD-Übersetzung, Multiplizitätsschranke zwei, Profil 3520, simultane Reduktionsrunden. Gelesen, nicht nachgerechnet.

---

## 6. Urteil zu K66-Beweiskette und 26er-Gram-Reduktion

### 26er-Gram-Reduktion — **akzeptiert, vollständig unabhängig verifiziert**

Das am besten abgesicherte Ergebnis des Zweigs. Die Kette wurde von Null neu aufgebaut und ergibt exakt 87/25/18/26 mit exakt der dokumentierten Überlebendenliste. Die 18 Ausschlüsse sind echte Unmöglichkeitsbeweise, die 26 Überlebenden echte Machbarkeitszeugen **nur der binären Gram-Stufe**. Die Selbstbeschränkung der Bilanz — binärer Gram-Zeuge ≠ Quotient ≠ Graph — ist korrekt und wird eingehalten. Die Warnung gegen 26×101 ist berechtigt und im Ledger als `cross_product_warning` verankert.

### K66-Beweiskette — zweistufiges Urteil

> **Arithmetik-, Bahnen- und Verknüpfungsschicht: akzeptiert, vollständig unabhängig verifiziert.** Die Zerlegung der 13.824 unfiltrierten Crossmatchings in 246 Bahnen ist erschöpfend und disjunkt; die 223 Ausschlüsse sind exakte Unmöglichkeitsbeweise; die 23 Restfälle sind eindeutig und nachrechenbar an die auditierten Encoder-Eingaben gebunden.
>
> **Zertifikatsschicht der 23 Restfälle: akzeptiert unter benannter Voraussetzung** — der archivierten Cake-Evidenz für 897 Hauptblätter, 28 Replays und 125 Profilbeweise. Diese Dateien liegen nicht in Git und wurden nicht geprüft. Das Projekt behauptet für sie auch keinen Replay.

Der Satz „k66_s1_t225 ist ausgeschlossen" steht auf zwei Beinen sehr unterschiedlicher Prüfbarkeit: **92 %** der beschrifteten Fälle (12.672 von 13.824) ruhen auf exakter, hier nachgerechneter Arithmetik, die restlichen **8 %** auf externer Zertifikatsevidenz.

Die Selbstdeklaration der Kette ist ungewöhnlich diszipliniert: Arithmetikschicht als eigener Lauf ausgewiesen, 897 Blätter ausdrücklich ohne neuen Replay, das fehlerhafte `lrat-check` ausdrücklich als nicht tragend, der 1.0.0-Serialisierungsfehler offen dokumentiert und durch meinen Lauf bestätigt.

---

## 7. Korrigierte Restbilanz

### Freie C3-Wirkung, τ=6 — **offen**

τ=6 ist ein **eigenes Theorem** (A11), nicht nur Literaturübernahme; τ=13, 20, 27 sind vollständig erledigt. Verbleibend: 101 L-Typen ohne vollständigen Ausschluss (zwei historisch zertifiziert, nicht neu abgespielt) und 26 T-Gerüste, die die notwendige binäre Gram-Bedingung überleben. Beide Achsen sind **Koordinaten derselben Aufgabe**, keine addierbaren Falllisten. Kein zertifizierter Ausschluss auch nur eines vollständigen Quotienten liegt vor. Die Liftkontrollen zeigen zudem, dass die modulare Bedingung an nicht exakten Quotienten Fehlalarme produziert — die Realisierungslücke ist real und messbar.

### Involution mit einem Fixpunkt — **offen, aber am besten vorbereitet**

Die kanonische Wirkung ist mathematisch vollständig festgelegt. Ergänzend zur Bilanz sei festgehalten: die Fixpunktfreiheit auf den 84 äußeren Knoten ist **nicht gesondert zu fordern, sondern erzwungen**. Wäre ein Label {a,b} unter t fix, so müsste wegen ta≠a gelten ta=b — aber a und ta sind Partner in der Matching-Kante und damit benachbart, während Labels aus *nicht*benachbarten Paaren bestehen. Also ist die Orbitstruktur zwingend 1¹2⁴⁹ (1 + 7 + 42 = 1 + 98 = 99 ✓). Es liegt **kein** zertifizierter UNSAT-Abschluss dieses Modells vor. Eine kanonische Permutation ist eine WLOG-Reduktion, kein Beweis.

### Interne Literaturablösung — **größtenteils offen, und zu Recht nachrangig**

Unter E1 ist der gesamte Fixdreiecks-Zweig mathematisch erledigt; die 42 N-Zeilen und 29 V3-Zeilen sind **Vertrauens-, keine Mathematikpflichten**. E1/E2 sind intern nicht rekonstruiert. Der Zwischenstand — 1 von 72 Klassen mit eigenem Abschluss — zeigt die Kosten: eine vollständige interne Ablösung ist eine Größenordnung teurer als der verbleibende mathematische Kern, bei null Zugewinn für das Hauptziel. E5 ist dagegen durch A11 bereits intern ersetzt.

### Global

Existenz von SRG(99,14,1,2) weder bewiesen noch widerlegt. Selbst bei Erledigung beider Symmetrieaufgaben bliebe der **asymmetrische Fall** — der mit Abstand größte Teil des Problems — unberührt. Das stellt die Bilanz korrekt dar.

---

## 8. Priorisierte Folgeaufträge

**P1 (Abschluss der K66-Verifikation) ist durch dieses Review erledigt** (§4.5). Damit rückt P2 auf Platz eins. Das Argument dafür ist nach den Liftkontrollen stärker geworden, nicht schwächer.

---

### P2 — Vollständiges SRG-Modell mit der kanonischen Involution · **Priorität 1**

**Mathematischer Gewinn.** Der größte im Projekt. Ein UNSAT schließt zusammen mit E1/E3/E4 und einem späteren C3-Ausschluss per Cauchy **jede** nichttriviale Automorphismengruppe aus. Ein SAT liefert eine konkrete Kandidatenstruktur mit Symmetrie. Entscheidend: es gibt **keine Lift-Lücke**. Das Modell ist direkt das 99-Knoten-Problem, nicht ein Quotient, aus dem noch geliftet werden müsste. Genau die methodische Hauptlücke der C3-Achse entfällt.

**Notwendige Modellstärke.** Volles 99×99-SRG-Modell unter der festen Permutation 1¹2⁴⁹ im kanonischen 1+14+84-Koordinatensystem.

**Abschlusskriterium.** Zertifiziertes UNSAT, Cake-geprüft, mit dokumentiertem Notwendigkeitsbeweis jeder kodierten Bedingung — oder ein explizit ausgegebener, exakt nachgerechneter Graph.

#### Modellkern (vorab hergeleitet und nachgerechnet)

Alle Kanten inzident zu v ∪ N(v) sind **vollständig determiniert**: 14 Kanten von v, 7 Matching-Kanten in N(v), 168 Kanten N(v)↔außen (jeder äußere Knoten hängt genau an seinen zwei Labelknoten). Unbekannt ist ausschließlich der 84×84-Block M. Kantenbudget: 14 + 7 + 168 + 504 = **693** ✓.

Sei R der bekannte 84×14-Inzidenzblock (jede Zeile genau zwei Einsen, durch das Label gegeben). Da kein äußerer Knoten zu v benachbart ist, liefert A²+A = 12I+2J auf dem Außenblock die **explizite** Gleichung

```
M² + M = 12·I₈₄ + 2·J₈₄ − R·Rᵀ ,      (RRᵀ)_xy = |label(x) ∩ label(y)|
```

mit vollständig bekannter rechter Seite. Auswertung:

| Fall | Bedingung |
|---|---|
| x = y | Diagonale: Grad 12 im Außenblock (12·1 + 2 − 2 = 12 ✓) |
| Labels teilen einen Knoten (**924** Paare) | (M²)_xy + M_xy = **1** |
| Labels disjunkt (**2.562** Paare) | (M²)_xy + M_xy = **2** |

924 + 2562 = 3486 = C(84,2) ✓; 924 = 14·C(12,2) ✓ (jeder Knoten von N(v) liegt in genau 12 Labels).

**Variablenzahl.** t operiert auf den 3.486 Außenpaaren mit 42 Fixpaaren {x, tx}; die übrigen 3.444 bilden 1.722 Zweierbahnen. Unter Kommutation mit t bleiben also **1.764 freie Boolesche Variablen**. Das ist eine sehr kleine Aufgabe verglichen mit den ~120k CNF-Variablen der historischen Quotientenmodelle — und ohne nachgelagerte Liftpflicht.

**Restsymmetrie.** Der Zentralisator der Situation (v fest, t fest) enthält S₇ ⋉ C₂⁷ der Ordnung 7!·2⁷ = **645.120**, wirkend durch Umnummerierung der sieben Matching-Kanten und Vertauschen innerhalb jeder Kante. Das ist erhebliches, bisher ungenutztes Symmetriebrechungspotential; t selbst ist das Produkt aller sieben Innenvertauschungen.

#### Teilaufgaben und Schritte

**P2.1 — Modellherleitung und Notwendigkeitsbeweis (keine Solverzeit).**
Die obige Blockgleichung und die Fallunterscheidung 1/2 als eigenständiges, reviewfähiges Dokument ausformulieren, im Stil von `O3_LAYER_A_MODEL_SPEC.md`. Für **jede** später kodierte Klausel ist auszuweisen, ob sie exakt notwendig oder theoremabgeleitet redundant ist — die Trennung, die Layer A/B vorbildlich durchhält. *Abschluss:* Dokument mit vollständiger Notwendigkeitsbegründung, keine unbegründete Bedingung.

**P2.2 — Elementare Vorabableitungen (Papier, hoher Hebel).**
Vor jedem Encoding die kleinen strukturellen Fragen klären, die den Suchraum kollabieren lassen könnten:
- Ist x ~ tx erzwungen, verboten oder frei? (42 Variablen, potentiell entscheidend)
- Welche Bedingungen erzwingen die Labels mit gemeinsamem Knoten? (924 Paare mit der scharfen Budgetgleichung = 1)
- Gibt es ein Analogon zu Lemma B, also eine Exact-One-Struktur aus Budgetsättigung?
Erfahrungsgemäß liefert genau diese Stufe den größten Gewinn: Lemma B und der C4-Ausschluss sind beide so entstanden. *Abschluss:* Liste bewiesener Zusatzlemmata mit Angabe, wie viele der 1.764 Variablen sie fixieren.

**P2.3 — Positivkontrolle auf srg(9,4,1,2) (verifiziert verfügbar).**
Der 3×3-Rookgraph ist srg(9,4,1,2) und besitzt eine Involution mit **genau einem Fixpunkt** (Zeilen 1↔2 und Spalten 1↔2 vertauschen; einziger Fixpunkt (3,3)). Die Struktur ist das exakte Kleinbild: N(v) ≅ 2K2, 4 äußere Knoten ↔ 4 nichtbenachbarte Paare, Orbittyp 1¹2⁴. Dasselbe Modell muss hier SAT liefern **und** den Rookgraphen rekonstruieren. Diese Kontrolle ist vor jedem 99-Knoten-Lauf zu bestehen. *Abschluss:* SAT, und die extrahierte Matrix ist isomorph zum Rookgraphen.

**P2.4 — Negativkontrollen und Mutationstests.**
Nach dem Vorbild von `o3_cycle_local_check.py`: Koeffizienten-Mutationen der Blockgleichung müssen die Kontrollergebnisse verändern; eine bewusst unsoundgemachte Bedingung muss die Positivkontrolle zerstören. Ein leerer Beweis muss vom Checker zurückgewiesen werden. *Abschluss:* vorregistrierte Fingerabdrücke, alle Mutationen schlagen wie erwartet an.

**P2.5 — Symmetriebrechung mit Notwendigkeitsnachweis.**
Aus der Gruppe der Ordnung 645.120 eine kanonische Normalform ableiten (z. B. Ordnung der sieben Matching-Kanten nach einem Invariantenvektor, dann Orientierung innerhalb jeder Kante). Jede brechende Klausel braucht einen Beweis, dass mindestens ein Vertreter jeder Isomorphieklasse erhalten bleibt — sonst ist ein UNSAT wertlos. Hier wird die WLOG-Reduktion zum ersten Mal beweispflichtig. *Abschluss:* Beweis der Vollständigkeitserhaltung; Messung des tatsächlichen Reduktionsfaktors an der Positivkontrolle.

**P2.6 — Encoding und exakte Gegenrechnung.**
CNF-Erzeugung mit Produkt-Hilfsvariablen analog `qsat/encode.py`. Vor jedem Lauf: unabhängige Ganzzahl-Gegenrechnung der erzeugten Gleichungen durch direkte Matrixmultiplikation — die Methode, die bei Layer A und im K66-Encoder-Audit die Übersetzung abgesichert hat. *Abschluss:* Gegenrechnung für alle 84 Grad- und 3.486 Paargleichungen bestanden; CNF-Hash festgeschrieben.

**P2.7 — Gestufter Lauf mit vorab definiertem Abbruchkriterium.**
Nicht mit dem Volllauf beginnen. Reihenfolge: (a) Positivkontrolle, (b) Teilmodell auf einer Wurzelaufspaltung nach wenigen hochinformativen Variablen, (c) Volllauf. Vorab festzulegen: Blattbudget, maximale Gesamtlaufzeit, Abbruchbedingung. Ausdrücklich **keine** Laufzeitprognose aus dem 2,1-Sekunden-K66-Abschlusslauf oder aus der Zahl 26 ableiten — der K66-Lauf prüft ausschließlich Arithmetik über gespeicherten Daten, die eigentliche Beweislast lag in den 897 Blättern und 125 Profilbeweisen.

**P2.8 — Zertifizierung ausschließlich über Cake.**
CaDiCaL → LRAT → `cake_lpr`. Das historische `lrat-check` zählt nach eigener Projektfeststellung nicht als zweite unabhängige Positivinstanz und darf in dieser Kette keine tragende Rolle spielen. Alle CNF- und Proofhashes ins Manifest, Proofdateien mit Größenangabe und Speicherort. *Abschluss:* `s VERIFIED UNSAT` von `cake_lpr` für jedes Blatt, vollständige Bytebindung der Eingaben.

**P2.9 — Verwertung.**
Bei **UNSAT**: zusammen mit einem künftigen C3-Ausschluss folgt per Cauchy die Asymmetrie jedes Conway-Graphen. Das ist ein Symmetriesatz, **kein** Nichtexistenzbeweis — die Formulierung muss das tragen. Bei **SAT**: die gefundene Matrix exakt gegen A²+A=12I+2J und die Kommutation mit t prüfen; ein SAT des Modells ist hier tatsächlich ein Graph, nicht bloß ein Quotient. Das wäre die Lösung des Conway-Problems und verlangt entsprechend sorgfältige unabhängige Nachrechnung.

---

### P3 — Die 26 T-Gerüste mit U-Realisierbarkeit und L-Typen koppeln · **Priorität 2**

**Mathematischer Gewinn:** mittel und unsicher. Die schwache LP hat **keinen** weiteren Typ ausgeschlossen; sie erneut zu lösen ist wertlos. Der Gewinn liegt allein in echter Modellverstärkung.

**Modellstärke:** zusätzlich zur bereits erschöpften Gram-Bedingung CC^T die vollständigen Blockgleichungen C^TC = 12I+6J−U²−U und XC = 6J−3C−CU, gekoppelt an einen konkreten L-Zyklentyp. Die Lemma-B-Schicht ist auf den C3-Komponenten verfügbar, die Zykluslemmata C5–C8 sind verifiziert vorhanden.

**Abschlusskriterium:** mindestens ein T-Gerüst aus der Liste {0, 1, 2, 5, 8, 13, 22, 24, 26, 27, 39, 40, 41, 46, 51, 52, 64, 65, 71, 72, 75, 95, 96, 98, 121, 122} mit exaktem Zeugnis ausgeschlossen — oder der dokumentierte Nachweis, dass die verstärkten Bedingungen keinen weiteren Typ treffen. Im zweiten Fall ist die Achse auszusetzen und die Kraft auf P2 zu verlagern.

---

### P4 — Schließung der verbliebenen Bindungslücken · **Priorität 3, geringer Aufwand**

Kein mathematischer Gewinn, aber billig und beseitigt die drei konkreten Reviewbefunde:
1. Die acht vollständigen K66-Encoder-Fallberichte in Git nachreichen (§4.5) — danach ist `close_k66.py` **vollständig** aus Git reproduzierbar.
2. `coverage_input.json` oder eine kryptographische Bindung der committeten `coverage_manifest_656.tsv` an die FULLCERT-Auditkette nachreichen (F8).
3. `verify_review.py` mit `--out`-Parameter versehen (F3); den Atlas-Offset der Zertifikatsdatei dokumentieren (F2); A5, A6, A13 als benannte Lemmata führen (F5).

---

### Ausdrücklich **nicht** empfohlen

- **Weitere K66-artige Rechnungen** zur internen Ablösung der 42 bzw. 29 Fixdreiecksklassen. Unter E1 ist dieser Zweig mathematisch abgeschlossen; der Aufwand pro Klasse ist durch K66 belegt hoch, der Beitrag zum Hauptziel null. Falls die externe Abhängigkeit ersetzt werden soll, wäre der wirksame Hebel eine interne Rekonstruktion von **E1 selbst**, nicht die Klasse-für-Klasse-Abarbeitung ihrer Konsequenzen.
- **Globale Laufzeitprognosen** aus dem K66-Abschlusslauf oder aus der Zahl der Gram-Typen.
- **Erneutes Lösen der schwachen LP** auf der 26er-Achse.

---

## Anhang: Verwendete Werkzeuge und Läufe

| Lauf | Ergebnis |
|---|---|
| 27 Manifestquellen gegen Git-Blob/Länge/SHA256 | keine Abweichung |
| 10 vendor/qsat-Dateien gegen PROVENANCE.json | keine Abweichung |
| Eigene Enumeration aller 6-Knoten-Graphen | 32.768 / 156 |
| Eigene Gram-, PSD-, Farkas- und Zeugenprüfung | 87 / 25 / 18 / 26 |
| Eigener Zykluslemma-Enumerator C5–C8 | 6/66/478/14615, 6/66/408/6717, 6/34/309/5754 |
| `drat-trim` aus Quelltext kompiliert, f27-Vollreplay | 13/13 `PASS_FRESH_DRAT` |
| `replay_f27.py` mit gepinntem Fremdcommit | 6/6 `PASS_REGENERATED_INITIAL_GRAM` |
| Eigene K66-Implementierung (Stabilisator, Bahnen, Minoren, Ränge) | 64 / 246 / 15.744 / 223 / 4×11+19×12 |
| `close_k66.py` 1.0.1, offline | `K66_ARITHMETIC_AND_ORBIT_COVERAGE_PASS`, 4 von 6 Dateien byteidentisch |
| `check_lifts.py` in Scratch | `lifts.json` identisch |
| FULLCERT-Coverage-Nachrechnung | 488 + 24 = 512 Wurzelmuster, lückenlos |

*Erstellt als unabhängiges externes Review. Die Urteile beziehen sich ausschließlich auf die benannten Commits und die dort vorgefundenen Artefakte.*
