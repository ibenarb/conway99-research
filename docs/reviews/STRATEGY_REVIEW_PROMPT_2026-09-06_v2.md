# Conway 99 — Strategie- und Mathematik-Reviewauftrag, Version 2

**Datum:** 6. September 2026  
**Adressaten:** ChatGPT / Claude / GPT Astra  
**Arbeitsmodus:** zunächst **unabhängige** Analyse.  
**Repository:** `ibenarb/conway99-research`  
**Kanonischer Stand:** aktueller Branch `main`; historische Meilenstein-Tags bleiben unverändert.  
**Diese Datei ersetzt für neue Reviews die Version 1** `STRATEGY_REVIEW_PROMPT_2026-09-06.md`.

---

## 1. Auftrag

Du bist mathematischer Forschungspartner im Projekt **Conway 99**. Ziel ist nicht, den vorhandenen Projektstand nur zusammenzufassen. Du sollst ihn **kritisch verstehen, unabhängig auditieren, mathematisch weiterentwickeln und in eine belastbare nächste Forschungsphase überführen**.

Fernziel:

> Einen `srg(99,14,1,2)` finden oder seine Nichtexistenz beweisen.

Nahziel im aktuellen Symmetriezweig:

> Die möglichen Symmetrien eines hypothetischen `srg(99,14,1,2)` beweisbar klassifizieren oder ausschließen, zunächst den fixpunktfreien Ordnung-3-Fall möglichst vollständig entscheiden.

Parallel sollen wir den Suchraum mathematisch strukturieren, Familien statt Einzelinstanzen verstehen und Sätze gewinnen, die unabhängig vom Erfolg eines konkreten SAT-Laufs Bestand haben.

Beantworte insbesondere:

1. Welche mathematischen Schlüsse sind aus dem aktuellen Stand **bereits wirklich bewiesen**?
2. Welche zusätzlichen Sätze oder Lemmata lassen sich jetzt herleiten?
3. Welche Folgeuntersuchungen versprechen den höchsten Erkenntnisgewinn?
4. Wie sollte der verbleibende Suchraum strukturiert werden?
5. Welche Bedingungen leben nur auf Quotientenebene und welche zusätzlichen notwendigen Bedingungen entstehen erst beim 99-Knoten-**Lift**?
6. Welche Rechenstrategie liefert unter den lokalen Ressourcen die höchste Information pro Walltime und ist später sauber zertifizierbar?
7. Welche bisherigen Annahmen, WLOG-Schritte, Kodierungen oder strategischen Schlussfolgerungen könnten falsch, zu schwach oder unnötig restriktiv sein?

**Keine nächste Strategie ist vorgegeben.** Insbesondere sind Cubing, längere monolithische Läufe, neue Mathematik, alternative Encodings und konstruktive Suche als konkurrierende Hypothesen zu prüfen.

---

## 2. Evidenzdisziplin

Trenne strikt zwischen:

- `THEOREM`: intern bewiesene Mathematik;
- `EXTERNAL-INPUT`: publizierte Mathematik, die als Eingangssatz benutzt wird;
- `MACHINE-CERTIFIED`: vollständige maschinelle Zertifikatskette;
- `SCOUT-EVIDENCE`: Solver-/Performancebeobachtung ohne Beweiswert;
- `HEURISTIC`: konstruktive oder memetische Evidenz;
- `CONJECTURE`: Vermutung;
- `GAP`: ungeklärte Transfer-, Coverage-, Provenienz- oder Modellierungsstelle.

Ein TIMEOUT ist kein mathematisches Resultat. `UNSAT_UNCERTIFIED` ist kein neues Theorem. Ein SAT-Quotient ist kein 99-Knoten-SRG, solange kein Lift vorliegt. Ein numerisches Muster wird erst nach Beweis oder vollständiger Zertifizierung zur mathematischen Aussage.

Wenn Du eine bestehende Behauptung übernimmst, nenne die Repository-Datei oder Primärquelle. Wenn Du einen neuen Satz formulierst, gib einen eigenständigen Beweis oder kennzeichne exakt den noch fehlenden Schritt.

---

## 3. Wichtige Korrekturen gegenüber dem früheren Reviewauftrag

Diese Punkte sind **Teil des zu auditierenden aktuellen Projektstands**. Prüfe sie unabhängig; übernimm sie nicht nur deshalb, weil sie hier stehen.

### 3.1 Was Grundmodell A tatsächlich kodiert

Layer A ist **kein 99-Knoten-SRG-Modell**, sondern ein exaktes 33-Knoten-Quotienten-Feasibility-Modell für einen fest gewählten fixpunktfreien Ordnung-3-Typ.

Für festes `T` und `L` sucht A nach einer einfachen 0/1-Matrix `S` in

`Q = 2 D_T + S + 2 L`

und kodiert

`Q 1 = 14 1`

sowie die vollständige Matrixgleichung

`Q^2 + Q = 12 I + 6 J`.

Die 528 Off-Diagonal-Paargleichungen sind vollständig enthalten; die Diagonalbedingungen folgen aus den S-Gradgleichungen. Zusätzlich enthält A die aus Lemma B abgeleiteten C3-Exact-One-Klauseln.

Daher gilt

`SRG mit diesem FPF-O3-Typ => zulässiger Quotient Q => SAT(A)`

und folglich

`UNSAT(A) => dieser Quotiententyp ist ausgeschlossen`.

Aber im Allgemeinen **nicht**

`SAT(A) => existierender srg(99,14,1,2)`.

Pflichtlektüre hierzu: `docs/breadth1/O3_LAYER_A_MODEL_SPEC.md`.

### 3.2 Exact source provenance is now in Git

Die frühere Reproduzierbarkeitslücke ist geschlossen. Der vollständige historische `qsat`-Quellbaum aus dem unveränderten FULLCERT-Freeze steht content-exakt unter

`vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat/`.

Provenienz und Content-Hashes stehen in

`vendor/O3_TASK03_FULLCERT_1.1_20260902/PROVENANCE.json`.

Der tatsächlich verwendete historische Base-Encoder hat

`SHA256(encode.py) = 131cf8aea1fbf6eeb76e363357b55498d084f109ec93b42c51d0d0c6abdbe6f1`.

Audit-Hinweis: Der historische Encoder enthält tau=6-spezifische Triangle-Helfer. Im all-tau Breadth-Scout werden diese nicht benutzt: der Breadth-Layer ruft den historischen Encoder mit `lemma_triangle_eo=False` auf und fügt die tau-generische C3-EO-Schicht selbst hinzu. Prüfe diese Aufrufkette ausdrücklich.

### 3.3 Layer B ist mathematisch redundant zu A

B fügt für `C_m`, `m>=5`, zykluslokale Budget-Ungleichungen hinzu. Diese entstehen aus bereits in A vorhandenen exakten Paargleichungen durch Weglassen nichtnegativer Terme. Damit sind die B-extra-Bedingungen **logische Konsequenzen von A**.

A und B stellen also dieselbe mathematische Feasibility-Frage; B ist eine redundante Propagations-/Kodierungsschicht. Der matched-seed A/B-Scout darf deshalb nur als **Solver-/Encoding-Experiment** interpretiert werden, nicht als Test „schwächere Mathematik A gegen stärkere Mathematik B“.

Die Beobachtung beim bekannten Kontrolltyp `(6,3^7)` — A TIMEOUT, B schneller UNSAT mit gleichem Seed/CPU — ist ein reales Performance-Signal für genau diesen Lauf, aber kein Beweis eines allgemeinen B-Vorteils.

### 3.4 Neuer elementarer tau-Satz

Im fixpunktfreien Ordnung-3-Fall gilt

`tau ≡ 0 (mod 3)`.

Begründung: `lambda=1` gibt genau 231 Graphdreiecke. Unter der fixpunktfreien Ordnung-3-Automorphie haben Dreiecksorbits Länge 1 oder 3; die setweise fixierten Dreiecke sind genau die `tau` Vertexorbits, die selbst Dreiecke induzieren. Also `231 = tau + 3k`.

Zusammen mit der früheren Spurrestriktion

`tau in {6,13,20,27}`

folgt

`tau in {6,27}`.

Pflichtlektüre: `docs/breadth1/O3_tau_mod3_theorem.md`.

Damit fallen alle 28 tau=13-Typen und alle 6 tau=20-Typen mathematisch weg. Von den historisch 139 C4-freien Typen bleiben 105. Nach den zwei bereits ausgeschlossenen tau=6-Kontroll-/Typfällen `(3^9)` und `(6,3^7)` ist der aktuelle Arbeitsstand **103 offene O3-Typen** = 101 bei tau=6 + 2 bei tau=27.

Maschinenlesbar: `results/breadth1/O3_post_tau_coverage_20260906.json`.

Der historische 139-Typen-Breadth-Scout bleibt unverändert als Experiment dokumentiert; seine tau=13/20-Läufe sind heute lediglich nicht mehr Teil des mathematisch live Suchraums.

---

## 4. Pflichtlektüre

Lies mindestens:

### Projektüberblick und früheres Peer-Review

1. `docs/status/Conway99_Statusbericht_2026-09-03_rev1.tex`
2. `docs/reviews/ClaudeAI_Statusbericht_2026-09-03.md`

### Korrigierter aktueller O3-Stand

3. `docs/breadth1/O3_LAYER_A_MODEL_SPEC.md`
4. `docs/breadth1/O3_tau_mod3_theorem.md`
5. `results/breadth1/O3_post_tau_coverage_20260906.json`
6. `docs/breadth1/O3_local_equations.md`
7. `docs/breadth1/O3_cycle_lemmas.md`

### Historischer zertifizierter Meilenstein

8. `docs/milestones/O3_TASK03_FULLCERT_1.1.md`
9. `manifests/O3_TASK03_FULLCERT_1.1/final_audit.json`
10. `manifests/O3_TASK03_FULLCERT_1.1/coverage_manifest_656.tsv`
11. Tag `o3-task03-fullcert-1.1`

### Exact code/provenance

12. `vendor/O3_TASK03_FULLCERT_1.1_20260902/PROVENANCE.json`
13. `vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat/encode.py`
14. `vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat/core.py`
15. `src/breadth1/o3_generic_core.py`
16. `src/breadth1/o3_generic_core_regression.py`
17. `src/breadth1/o3_abc_encode.py`
18. `src/breadth1/o3_abc_dryrun.py`
19. `src/breadth1/o3_cycle_local_check.py`
20. `src/breadth1/o3_type_coverage.py`
21. `src/breadth1/o3_post_tau_coverage.py`

### Historischer matched A/B scout

22. `docs/breadth1/O3_AB_MATCHED_MAIN_20260905.md`
23. `results/breadth1/O3_ab_matched_main_20260905_summary.json`
24. `results/breadth1/O3_ab_matched_main_20260905_types.tsv`
25. `src/breadth1/o3_ab_matched_scout_runner.py`
26. `src/breadth1/o3_smt_benchmark.py`

Folge allen weiteren Dateien, die für einen belastbaren Audit erforderlich sind. Zusammenfassungen sind Orientierung, nicht Ersatz für den Quelltext oder einen Beweis.

**Nicht als Baseline verwenden:** unveröffentlichte Vorabantworten anderer Reviewer. Falls Du aus einer früheren eigenen Sitzung Ideen kennst, behandle sie als Hypothesen und leite sie neu her.

---

## 5. Gegenwärtiger mathematischer Kern

Für einen hypothetischen `srg(99,14,1,2)` gilt

`A^2 + A = 12 I + 2 J`.

Im fixpunktfreien Ordnung-3-Fall gibt es 33 Vertexorbits. Der Quotient erfüllt

`Q^2 + Q = 12 I + 6 J`,

`Q 1 = 14 1`,

`Q = 2 D_T + S + 2 L`,

wobei `L` ein einfacher 2-Faktor auf den Nicht-Dreieckorbits ist.

Nach C4-Ausschluss und tau-Satz sind nur tau=6 und tau=27 live.

- tau=6: 103 C4-freie Zyklustypen; 101 derzeit offen.
- tau=27: 2 C4-freie Zyklustypen; beide derzeit offen.

Der Typ `(6,3^7)` bei tau=6 wurde im früheren FULLCERT-Meilenstein über eine vollständige Cubing-/Coverage-Struktur mit 656/656 terminalen Zertifikaten ausgeschlossen. Prüfe die exakte Reichweite und den Lemma-B-Transfer.

Der historische matched A/B-Breadth-Scout löste keinen damals offenen Typ im getesteten Budget. Da B logisch redundant zu A ist, ist das ein Performance-/Encoding-Befund, kein Beweis dafür, dass zusätzliche Mathematik versagt hätte, und kein direkter Beweis für die Überlegenheit einer nächsten Sucharchitektur.

---

## 6. Mathematische Forschungsfragen

Suche ausdrücklich nach **neuen beweisbaren Konsequenzen**. Vorrang haben Sätze, die ganze Familien ausschließen oder die Lift-Frage schärfen.

### 6.1 Globale Summen und Doppelzählungen

Summiere die exakten Paargleichungen systematisch:

- innerhalb einer L-Komponente;
- zwischen zwei L-Komponenten;
- zwischen T und einer L-Komponente;
- nach Zyklusdistanz;
- über alle Paare einer Quotientenklasse.

Suche nach ganzzahligen, paritätischen, modularen, konvexen oder extremalen Konsequenzen. Prüfe jeden vermeintlich starken neuen Satz an wenigstens einem von Hand kontrollierten Spezialfall, bevor Du ihn als Resultat führst.

### 6.2 Spektrum, Rang, PSD und Interlacing

Nutze das bekannte Quotientenspektrum und die Struktur `Q=2D_T+S+2L`:

- Eigenwert-Interlacing für natürliche Hauptblöcke;
- Rang- und Minorenbedingungen;
- modulare Ränge über endlichen Körpern;
- Gram-/PSD-Bedingungen;
- Association-Scheme-/Bose-Mesner-Methoden;
- equitable refinements.

Ein numerisch erfüllbares SDP ist kein Ausschluss. Bei einem numerischen Widerspruch ist eine exakte oder rational zertifizierbare Fassung erforderlich.

### 6.3 Komponentenübergreifende Struktur von S

Die bisherigen lokalen `C_m`-Bedingungen behandeln Komponenten stark einzeln. Suche nach Kopplungen:

- mögliche S-Kantenzahlen zwischen Komponenten;
- gemeinsame Außeninzidenzen;
- Gradfolgenbedingungen (z.B. bipartite Realisierbarkeit);
- exakte Formeln abhängig von Zykluslängen und tau;
- globale Konkurrenz um S-Grad und gemeinsame Nachbarn;
- Familien von Zyklustypen, die mit einem einzigen Satz ausgeschlossen werden können.

### 6.4 Die zwei tau=27-Typen als analytische Sonderfälle

Tau=27 lässt nur sechs U-Orbits und zwei L-Typen übrig. Untersuche diese Fälle besonders gründlich. Der große T-Block könnte stärkere Spektral-, Design-, Common-neighbor- oder Blockmatrixbedingungen erlauben als im tau=6-Fall.

Ziel: wenn möglich tau=27 **rein mathematisch** ausschließen, bevor SAT investiert wird.

### 6.5 Lift-Bedingungen: die derzeit wichtigste Modellgrenze

A entscheidet nur Quotientenfeasibility. Suche deshalb nach notwendigen Bedingungen dafür, dass ein zulässiger gewichteter 33x33-Quotient tatsächlich durch 3x3-Orbitblöcke zu einem 99-Knoten-SRG geliftet werden kann.

Fragen:

- Wie viele konkrete 3x3 circulante/permutierte Blocktypen entsprechen einem Quotienteneintrag 0,1,2,3?
- Welche Phasen-/Orientierungsvariablen entstehen zwischen Orbitpaaren?
- Welche SRG-Gleichungen koppeln diese Phasen?
- Kann man einen kleinen, exakt prüfbaren Lift-Obstruction-Layer formulieren, der auf Quotientenebene unsichtbar ist?
- Gibt es Kohomologie-/Gain-Graph-/Voltage-Graph-Interpretationen?
- Lassen sich Quotienten bereits durch notwendige Lift-Konsistenzbedingungen ausscheiden, ohne den vollständigen 99-Knoten-SAT aufzubauen?

Dies ist ausdrücklich ein bevorzugtes Gebiet für neue Mathematik, weil A die vollständige Quotientengleichung bereits kodiert.

### 6.6 Automorphismen und Symmetrieziel

Prüfe aus Primärquellen die exakten Aussagen zu möglichen Automorphismen des Conway-99-Graphen.

Leite präzise auseinander:

- was ein vollständiger Ausschluss aller FPF-O3-Fälle beweist;
- welche Primordnungen danach noch separat möglich sind;
- welche Ordnung-2-/Ordnung-7-/sonstigen Fälle wirklich verbleiben;
- unter welchen exakt zitierten Gruppentheorieannahmen ein späterer Asymmetriesatz folgt.

Keine verkürzte Schlusskette ohne Primärquellen-Audit.

---

## 7. Suchraum-Architektur

Entwirf eine bessere Hierarchie für die **103 live offenen O3-Typen** als „jeden Typ monolithisch mit demselben Timeout lösen“.

Prüfe mindestens:

1. tau = 6 vs 27;
2. L-Zyklustyp;
3. mathematische Invarianten/Aggregate;
4. zulässige interne S-Sehnenmuster;
5. Inzidenzprofile zwischen Komponenten und T;
6. Template-Automorphismen und kanonische Isomorphieklassen;
7. Exact-One-/At-Most-One-Strukturen;
8. Lift-Konsistenzprofile;
9. gezielte Cube-Variablen;
10. terminale SAT-Teilprobleme;
11. Coverage- und Zertifikatsstruktur.

Task03 ist ein Vergleichsobjekt, aber kein Dogma. Erzeuge eine nachvollziehbare Erklärung dafür, warum sein Cubing erfolgreich war. Wenn Du eine allgemeine Cubing-Regel vorschlägst, quantifiziere mindestens:

- Vollständigkeit der Cube-Auswahl;
- Zahl der Cubes pro Typ;
- Balance/Entropie;
- Propagationsstärke;
- Residual-Core-Größe;
- Template-Symmetrie;
- erwartete Zertifikatskosten.

Vergleiche Cubing bei gleichem Rechenbudget mit längeren monolithischen Läufen und ggf. Seed-Streuung. Vermeide Schlussfolgerungen aus nur einem Seed oder nur einem Kontrolltyp.

---

## 8. Konstruktiver Gegenpfad

Das Projekt darf sich nicht ausschließlich auf Nichtexistenz fixieren.

Untersuche realistische Wege zu einem Kandidaten:

- Quotientensuche plus systematischer 3-Lift;
- SAT/CP-SAT ohne oder mit schwächeren Symmetrieannahmen;
- grad-erhaltende Switches im `1+14+84`-Rootmodell;
- lokale/memetische Suche mit exakten SRG-Residualmaßen;
- algebraisch erzeugte Startpunkte;
- Heuristik mit anschließender exakter Verifikation.

Halte konstruktive Heuristik und formalen Ausschluss als getrennte Evidenzpfade.

---

## 9. Ressourcen- und Arbeitsregeln

Lokale Ressourcen auf dem Ryzen-Rechner sind billig; Cloud-Compute und viele Interaktionsrunden sind teuer.

Planungsannahmen:

- 20 logische Kerne nutzbar;
- 48 GiB RAM verfügbar;
- Plattenplatz kann bei Bedarf geschaffen werden und ist kein primärer Engpass;
- einzelne autonome lokale Läufe bis etwa **50 h Walltime** sind akzeptabel;
- lieber ein robuster gebündelter Lauf als viele kleine Chat-/Pilot-Schleifen;
- vor jedem vorgeschlagenen Produktionslauf: Walltime, Kerne, RAM, erwarteter Plattenbedarf und Stopregeln angeben;
- Produktionsrunner sollen alle 10 Minuten Status und ETA ausgeben;
- keine willkürlich knappen Timeouts; Abbruch nur bei echter Ressourcengefahr, Fehlern oder wissenschaftlich vorab definierten Futility-Kriterien;
- Cloud-Rechnung nur empfehlen, wenn der zusätzliche Informationsgewinn gegenüber lokalem Compute klar begründet ist.

Wenn ein Experiment mehrere Strategien vergleichen soll, fordere **faire Kontrollarme**: gleiche Instanzen, Seeds/Seed-Verteilung, Hardwarebudget und klar definierte Metrik.

---

## 10. Geforderte Antwortstruktur

### A. Executive verdict

Maximal etwa eine Seite: wichtigste mathematische und strategische Befunde.

### B. Claim audit

Status der tragenden Aussagen als

`THEOREM / EXTERNAL-INPUT / MACHINE-CERTIFIED / SCOUT-EVIDENCE / HEURISTIC / CONJECTURE / GAP`.

Prüfe insbesondere:

- tau-mod-3-Satz;
- Scope von A;
- A=>B-extra-Redundanz;
- FULLCERT-Coverage und Lemma-B-Transfer;
- Fixpunktfreiheits-Import;
- Status/Provenienz der beiden bereits ausgeschlossenen Kontrolltypen.

### C. Neue mathematische Schlüsse

Formuliere alle neuen Sätze/Lemmata mit Beweis. Trenne sie von Ideen, die erst untersucht werden müssen.

### D. Red-team analysis

Versuche aktiv, den Projektansatz zu widerlegen. Suche nach:

- falscher Modellierungsannahme;
- nicht gerechtfertigtem WLOG;
- fehlerhaftem Lift-/Quotienten-Transfer;
- Coverage-Lücke;
- Encoder-/Auxiliary-variable-Fehler;
- statistischer Überinterpretation von Solverläufen;
- alternativer Erklärung historischer Performancebeobachtungen.

### E. Struktur des verbleibenden Suchraums

Gib eine konkrete Hierarchie oder Aggregation der 103 offenen O3-Typen an. Schätze Größenordnungen nach den vorgeschlagenen Stufen.

### F. Vergleich der nächsten Strategien

Vergleiche mindestens:

- stärkere reine Mathematik;
- Lift-Obstruction-Mathematik/Encoding;
- Aggregate-/ILP-/SMT-Vorfilter;
- Cubing + SAT;
- längere monolithische SAT-Läufe;
- alternative Encodings/Branching;
- andere Solver/PB-Systeme;
- konstruktive Suche.

Bewerte Erkenntnisgewinn, Beweiswert, Implementierungsrisiko, lokale Ressourcen und Zertifizierbarkeit.

### G. Konkreter Folgeplan P0/P1/P2

Für jeden Vorschlag:

- wissenschaftliche Frage;
- Eingaben/Ausgaben;
- Methode;
- erwartete Walltime;
- Kerne;
- RAM;
- Plattenbedarf;
- Erfolgskriterium;
- Futility-/Stopregel;
- wie positives und negatives Ergebnis die nächste Entscheidung ändern;
- wie ein UNSAT-Signal später zu einem überprüfbaren Beweis wird.

### H. Drei nächste Entscheidungen

Am Ende genau **drei** Entscheidungen für den Projektleiter, priorisiert.

---

## 11. Unabhängigkeit

Dies ist bewusst derselbe Auftrag an mehrere Modelle.

Führe die erste Analyse unabhängig aus. Wenn Dir Ergebnisse aus einer früheren Sitzung bekannt sind, **rederive** sie und führe sie nicht als Beleg für sich selbst an. Bevorzuge begründete Abweichung gegenüber künstlichem Konsens.

Die drei neuen Berichte werden anschließend getrennt verglichen:

`Schnittmenge + Widersprüche + exklusive Ideen -> gemeinsamer Forschungsauftrag`.

**Ziel dieses Reviews ist nicht mehr Text, sondern eine bessere mathematische Entscheidung.**
