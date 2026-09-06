# Conway 99 — gemeinsamer Strategie- und Mathematik-Reviewauftrag

**Datum:** 6. September 2026  
**Adressaten:** ChatGPT / Claude (Peer Reviewer) / GPT Astra  
**Arbeitsmodus:** zunächst **unabhängige** Analyse; keine Annahme, dass frühere Modellurteile richtig sind.  
**Repository:** `ibenarb/conway99-research`  
**Kanonischer Ausgangsstand:** `main` nach Fast-Forward auf Commit `c269d0e40198822c52cf850f0cfca2da0e8b200d` sowie Tag `o3-breadth1-ab-matched-20260905`  
**Früherer zertifizierter Meilenstein:** Tag `o3-task03-fullcert-1.1`

---

## 1. Auftrag

Du bist mathematischer Forschungspartner im Projekt **Conway 99**. Ziel ist nicht, den vorhandenen Projektstand lediglich zusammenzufassen, sondern ihn **kritisch zu verstehen, unabhängig zu auditieren, mathematisch weiterzuentwickeln und in eine belastbare nächste Forschungsphase zu überführen**.

Das Fernziel ist weiterhin:

> Einen `srg(99,14,1,2)` zu finden oder seine Nichtexistenz zu beweisen.

Das unmittelbare Nahziel ist der **Symmetriezweig**:

> Die möglichen Symmetrien eines hypothetischen `srg(99,14,1,2)` so weit wie möglich beweisbar zu klassifizieren oder auszuschließen, insbesondere den fixpunktfreien Ordnung-3-Fall vollständig zu entscheiden.

Parallel dazu sollen wir den gesamten Suchraum besser strukturieren und mathematische Aussagen gewinnen, die auch dann wertvoll bleiben, wenn ein vollständiger Existenz-/Nichtexistenzbeweis noch nicht erreicht wird.

Beantworte insbesondere:

1. **Welche mathematischen Schlüsse lassen sich aus dem derzeitigen Stand bereits beweisbar ziehen?**
2. **Welche neuen Lemmata oder globalen Zähl-/Spektralbedingungen lassen sich aus den vorhandenen Gleichungen herleiten?**
3. **Welche Folgeuntersuchungen sollten beauftragt werden?**
4. **Wie sollte der Suchraum strukturiert und zerlegt werden, statt 137 harte Fälle monolithisch zu behandeln?**
5. **Welcher Weg hat die höchste erwartete Information pro lokaler Rechenstunde?**
6. **Welche Aussagen könnten mit vertretbarem Aufwand vollständig zertifiziert werden?**
7. **Welche aktuellen Annahmen, Modellierungen oder Schlussfolgerungen könnten falsch, zu schwach oder unnötig restriktiv sein?**

Wichtig: Behandle die im Projekt zuletzt geäußerte Präferenz für **Cubing/Zerlegung** als eine zu prüfende Hypothese, nicht als vorgegebenes Ergebnis.

---

## 2. Evidenzdisziplin

Trenne in Deiner Antwort strikt zwischen:

- **publizierter/externer Mathematik**, die als Eingangssatz benutzt wird;
- **eigener rein mathematischer Ableitung** aus dokumentierten Voraussetzungen;
- **maschinenzertifizierten Resultaten** (LRAT/Cake bzw. dokumentierte vollständige Zertifikatskette);
- **Solver-Signalen ohne Zertifikat** (`UNSAT_UNCERTIFIED` etc.);
- **explorativen/heuristischen Ergebnissen**;
- **Vermutungen und Forschungsideen**.

Ein TIMEOUT ist kein mathematisches Ergebnis. Ein Solver-UNSAT ohne geprüfte Zertifikatskette ist kein neues Theorem. Ein numerisches Muster ist kein Lemma, solange es nicht bewiesen oder vollständig und korrekt zertifiziert wurde.

Wenn Du eine bestehende Aussage übernimmst, nenne möglichst die Datei bzw. den Commit, aus der sie stammt. Wenn Du sie neu beweist, gib einen eigenständigen Beweis oder eine klare Beweisskizze mit den noch offenen Schritten.

---

## 3. Pflichtlektüre im Repository

Lies nicht nur diese Aufgabenbeschreibung. Prüfe mindestens die folgenden Quellen und folge bei Bedarf deren Verweisen in `src/`, `results/`, `manifests/` und `docs/`.

### Projektüberblick und frühere externe Prüfung

1. `docs/status/Conway99_Statusbericht_2026-09-03_rev1.tex`
2. `docs/reviews/ClaudeAI_Statusbericht_2026-09-03.md`

### Vollständig zertifizierter Ordnung-3-Meilenstein

3. `docs/milestones/O3_TASK03_FULLCERT_1.1.md`
4. Tag `o3-task03-fullcert-1.1`

### Verallgemeinerte Ordnung-3-Mathematik

5. `docs/breadth1/O3_local_equations.md`
6. `docs/breadth1/O3_cycle_lemmas.md`
7. `src/breadth1/o3_generic_core.py`
8. `src/breadth1/o3_generic_core_regression.py`
9. `src/breadth1/o3_cycle_local_check.py`
10. `src/breadth1/o3_type_coverage.py`

### Aktueller Breadth-Scout

11. `docs/breadth1/O3_AB_MATCHED_MAIN_20260905.md`
12. `results/breadth1/O3_ab_matched_main_20260905_summary.json`
13. `results/breadth1/O3_ab_matched_main_20260905_types.tsv`
14. `src/breadth1/o3_ab_matched_scout_runner.py`
15. `src/breadth1/o3_ab_matched_finalize.py`
16. `src/breadth1/o3_abc_encode.py`
17. `src/breadth1/o3_smt_benchmark.py`

Prüfe selbst, ob zusätzliche Dateien für eine belastbare Aussage nötig sind. Verlasse Dich nicht allein auf Zusammenfassungen.

---

## 4. Derzeitiger Stand, den Du **verifizieren** sollst

Die folgenden Punkte sind Orientierung, keine Aufforderung zum ungeprüften Übernehmen.

Für einen hypothetischen `srg(99,14,1,2)` gilt für die Adjazenzmatrix

`A^2 + A = 12 I + 2 J`.

Im fixpunktfreien Ordnung-3-Fall zerfallen 99 Knoten in 33 Orbits. Der Quotient erfüllt

`Q^2 + Q = 12 I + 6 J`,  `Q 1 = 14 1`,

und besitzt die Zerlegung

`Q = 2 D_T + S + 2 L`,

wobei `L` ein einfacher 2-Faktor auf den Nicht-Dreieckorbits ist. Aus dem Spektrum folgen

`tau in {6,13,20,27}`.

Die projektinterne Klassifikation ergibt nach Ausschluss von `C4`-Komponenten insgesamt **139** Zyklustypen:

- `tau=6`: 103
- `tau=13`: 28
- `tau=20`: 6
- `tau=27`: 2

Die aktuellen lokalen Gleichungen, Lemma B für `C3`, die `C_m`-Lemmata für `m>=5`, die Momentbedingungen und die mechanischen Regressionsprüfungen stehen in den genannten Breadth-Dokumenten.

Der Typ `(6,3^7)` bei `tau=6` ist durch den früheren FULLCERT-Meilenstein ausgeschlossen: die lemma-verstärkte CNF wurde über eine vollständige Cubing-/Coverage-Struktur mit **656/656** terminalen Zertifikaten geprüft. Der Transfer auf den Quotiententyp benutzt das dokumentierte Lemma B.

Der aktuelle matched-seed A/B-Breadth-Scout behandelte alle 139 `C4`-freien Typen mit 20 logischen Kernen und 5760-s-Solverbudget pro Instanz. Finaler Audit:

- 139/139 Typen vollständig;
- 278/278 A/B-Instanzen;
- 139/139 gleiche Seeds;
- 139/139 gleiche CPUs;
- 275 `TIMEOUT`;
- 3 `UNSAT_UNCERTIFIED`;
- diese drei Signale gehören ausschließlich zu den zwei bereits bekannten Kontroll-/Ausschlusstypen `(3^9)` und `(6,3^7)`;
- für die **137 verbleibenden offenen O3-Typen**: A = 137/137 TIMEOUT, B = 137/137 TIMEOUT;
- also **kein neuer UNSAT-Kandidat** im Breadth-Scout.

Beim Kontrolltyp `(3^9)` sind A und B byte-identische CNFs und liefern mit gleichem Seed exakt identische Konflikt-/Entscheidungs-/Propagationszahlen. Beim Kontrolltyp `(6,3^7)` läuft A in den Timeout, B findet mit demselben Seed/CPU UNSAT wesentlich früher. Das zeigt einen realen algorithmischen Effekt der zusätzlichen B-Bedingungen im Kontrollfall, aber keine sichtbare Generalisierung auf die 137 offenen Typen.

Prüfe insbesondere, ob aus dieser Beobachtung überhaupt eine Strategieempfehlung folgt und wenn ja, welche.

---

## 5. Mathematische Forschungsfragen

Suche ausdrücklich nach **neuen beweisbaren Konsequenzen**, nicht nur nach besseren SAT-Heuristiken.

### 5.1 Globale Summen aus den lokalen Paargleichungen

Untersuche, was entsteht, wenn die allgemeine Paargleichung

`(S^2)_ij + 2(SL+LS)_ij + 4(L^2)_ij + (d_i+d_j+1)Q_ij = 6`

über systematisch gewählte Paarmengen summiert wird:

- innerhalb einer `L`-Komponente;
- zwischen zwei `L`-Komponenten;
- zwischen `T` und einer `L`-Komponente;
- über alle Paare gleicher Zyklusdistanz;
- über alle Paare eines bestimmten Quotienten-Typs.

Suche nach integralen, paritätischen, modularen oder konvexen Widersprüchen, die ganze Familien von Zyklustypen ohne SAT ausschließen.

### 5.2 Stärkere Moment- und Gradbedingungen

Die vorhandenen `M1/M2`-Formeln sind nur ein Anfang. Prüfe insbesondere:

- höhere Momente oder Doppeltzählungen;
- gemeinsame Außeninzidenzen mehrerer Komponenten;
- Beschränkungen für die Verteilung der Werte `d_w` getrennt nach `w in T` und `w in U`;
- schärfere, tau-abhängige Kappen statt der sicheren Relaxationskappe 12;
- kombinierte Momentbedingungen mehrerer Zykluskomponenten;
- Gale-Ryser-/bipartite Gradfolgenbedingungen für die Inzidenz zwischen Komponenten;
- lineare oder semidefinite notwendige Bedingungen.

### 5.3 Spektrum, Rang und positive Semidefinität

Untersuche, ob sich aus dem bekannten Spektrum von `Q` oder aus geeigneten Polynomen in `Q`, `S`, `L` zusätzliche notwendige Bedingungen gewinnen lassen:

- Eigenwert-Interlacing;
- Rangbedingungen über `R`, `Q` oder endlichen Körpern;
- modulare Determinanten-/Minorenargumente;
- Gramdarstellungen;
- PSD-Bedingungen;
- Association-Scheme-/Bose-Mesner-Techniken;
- equitable refinements der Quotientenpartition.

### 5.4 Struktur von `S` relativ zum 2-Faktor `L`

Suche nach Aussagen, die mehrere Komponenten koppeln. Die bisherige lokale `C_m`-Analyse behandelt Komponenten weitgehend einzeln. Der nächste starke Satz könnte gerade aus der **globalen Konkurrenz um S-Grad und gemeinsame Nachbarn** entstehen.

Fragen:

- Welche S-Kantenzahlen zwischen zwei Komponenten sind überhaupt möglich?
- Gibt es exakte Formeln abhängig nur von den Zykluslängen und `tau`?
- Lassen sich kleine Komponenten wie `C3`, `C5`, `C6` als „Constraint Amplifier“ verwenden?
- Welche Mischungen von Zykluslängen sind schon auf Aggregatebene unmöglich?
- Können manche der 139 Typen zu wenigen universellen Familien zusammengefasst werden?

### 5.5 Symmetrieziel

Prüfe die exakten publizierten Voraussetzungen zu Automorphismen erneut aus Primärquellen. Leite klar auseinander:

- was der vollständige Ausschluss aller Ordnung-3-Fälle bedeuten würde;
- welche weiteren Automorphismen danach noch möglich wären;
- welche zusätzlichen Ordnung-2-, Ordnung-7- oder sonstigen Fälle tatsächlich separat behandelt werden müssten;
- unter welchen **präzisen** Literaturannahmen ein späterer Asymmetriesatz folgen würde.

Übernimm keine verkürzte Sekundärbehauptung wie „O2 und O3 ausgeschlossen ⇒ asymmetrisch“, solange die Gruppentheorie nicht vollständig geprüft ist.

---

## 6. Suchraum-Architektur

Entwirf eine bessere Hierarchie als „139 Typen jeweils monolithisch lösen“.

Prüfe mindestens folgende Ebenen als mögliche Suchraumstruktur:

1. `tau`;
2. `L`-Zyklustyp;
3. mathematische Aggregate/Invarianten des Typs;
4. zulässige interne S-Sehnenmuster je Komponente;
5. Inzidenzprofile zwischen Komponenten und `T`;
6. kanonische Isomorphieklassen statt bloßer Labelings;
7. Exact-One-/At-Most-One-Gruppen;
8. gezielte Cube-Variablen;
9. terminale SAT-Teilprobleme;
10. Zertifikatsstruktur und Coverage-Beweis.

Der Task03-Erfolg ist ein wichtiges Vergleichsobjekt: dort erzeugten neun Chord-Entscheidungen `2^9=512` Root-Cubes; 488 wurden schnell gelöst, nur 24 mussten weiter entlang Exact-One-Gruppen zerlegt werden. Prüfe, **warum** diese Zerlegung gut funktionierte und ob dieses Prinzip algebraisch/generalisiert auswählbar ist.

Gesucht ist möglichst eine **allgemeine Cubing-Regel oder ein Typ-Scoring**, nicht 137 handgemachte Spezialfälle.

Untersuche dazu beispielsweise:

- Entropie/Balance einer Branching-Variable;
- erwartete Propagationsstärke;
- Größe des Residual-Cores;
- Anzahl ausgelöster lokaler Paargleichungen;
- Komponentenkopplung;
- Automorphismen des Typtemplates;
- historische Konfliktprofile aus dem A/B-Scout.

Schlage vor, wie ein kleiner Pilot objektiv entscheiden kann, ob Cubing, stärkere Mathematik, alternative Kodierung oder ein anderer Solver den größten Hebel besitzt.

---

## 7. Konstruktiver Gegenpfad

Das Projekt darf sich nicht ausschließlich auf Nichtexistenz fixieren.

Prüfe, welche Suchpfade realistisch einen **Kandidaten** finden könnten:

- SAT/CP-SAT mit weniger Symmetrieannahmen;
- gezielte Quotienten-Lifts;
- memetische/grad-erhaltende Switches im `1+14+84`-Rootmodell;
- lokale Suche mit exakt erhaltenen SRG-Strafmaßen;
- algebraisch erzeugte Startpunkte;
- Kombination von Heuristik und anschließend exakter Verifikation.

Heuristische Konstruktion und formaler Ausschluss müssen als getrennte Evidenzpfade geführt werden.

---

## 8. Ressourcen- und Arbeitsregeln

Lokale Ressourcen auf dem Ryzen-Rechner sind billig; Cloud-Compute und viele Interaktionsrunden sind teuer.

Planungsannahmen:

- **20 logische Kerne** dürfen genutzt werden;
- **48 GiB RAM** stehen zur Verfügung;
- Plattenplatz kann bei Bedarf geschaffen/erweitert werden und ist kein primärer Engpass;
- einzelne lokale Läufe bis etwa **50 Stunden Walltime** sind akzeptabel;
- lieber ein robuster autonomer Lauf als viele kleine Chat-/Pilot-Schleifen;
- vor jedem vorgeschlagenen Rechenlauf: erwartete Walltime, Kerne, RAM, Plattenbedarf und Stop-Kriterien angeben;
- Produktionsrunner sollen einen automatischen **10-Minuten-Status mit ETA** ausgeben;
- nicht wegen willkürlich knapper Timeouts abbrechen; nur bei echtem Fehler oder Ressourcengefahr;
- teure Cloud-Rechnung nur empfehlen, wenn der Informationsgewinn gegenüber lokaler Rechnung klar begründet ist.

Entwirf Untersuchungen so, dass möglichst viele Hypothesen in **einem** Lauf geprüft werden können und die Ergebnisse maschinenlesbar, reproduzierbar und später zertifizierbar sind.

---

## 9. Geforderte Antwortstruktur

Liefere einen substantiellen Forschungsbericht, nicht nur eine Ideenliste.

### A. Executive verdict

Maximal etwa eine Seite: Was ist nach Deiner Prüfung der wichtigste mathematische und strategische Befund?

### B. Claim audit

Tabelle oder klar strukturierte Liste der wichtigsten gegenwärtigen Aussagen mit Status:

`THEOREM / MACHINE-CERTIFIED / EXTERNAL-INPUT / SCOUT-EVIDENCE / CONJECTURE / GAP`.

Markiere jede mögliche Überziehung oder unbewiesene Transferstelle.

### C. Neue mathematische Schlüsse

Formuliere alle neuen Lemmata/Sätze, die Du jetzt beweisen kannst. Gib Beweise oder ausreichend genaue Beweisskizzen. Trenne echte neue Sätze von bloßen Forschungsrichtungen.

### D. Red-team analysis

Versuche aktiv, den Projektansatz zu widerlegen:

- Wo könnte eine Modellierungsannahme falsch sein?
- Wo ist WLOG eventuell nicht WLOG?
- Wo könnte eine Zertifikats-/Coverage-Aussage zu weit interpretiert sein?
- Welche alternative Erklärung gibt es für die Solverbeobachtungen?

### E. Struktur des verbleibenden Suchraums

Gib eine konkrete hierarchische Zerlegung der 137 offenen O3-Typen bzw. eine mathematisch bessere Aggregation an. Wenn möglich, schätze Größenordnungen nach jeder Stufe.

### F. Vergleich möglicher nächster Strategien

Vergleiche mindestens:

- stärkere reine Mathematik;
- Aggregate-/ILP-/SMT-Vorfilter;
- Cubing + SAT;
- alternative SAT-Kodierung/Branching;
- andere Solver;
- konstruktive/heuristische Suche.

Bewerte jeweils erwarteten Erkenntnisgewinn, Beweiswert, Implementierungsrisiko und lokalen Ressourcenbedarf.

### G. Konkreter Folgeplan

Priorisierte Vorschläge `P0/P1/P2` mit für jeden Lauf:

- wissenschaftliche Frage;
- genaue Eingabe-/Ausgabeartefakte;
- vorgeschlagene Methode;
- erwartete Walltime;
- Kerne;
- RAM;
- erwarteter Plattenbedarf;
- Erfolgskriterium;
- Abbruch-/Stopregel;
- wie ein positives oder negatives Ergebnis die nächste Entscheidung verändert;
- wie aus einem UNSAT-Signal später ein überprüfbarer Beweis wird.

### H. Drei nächste Entscheidungen

Nenne am Ende genau die **drei** Entscheidungen, die der Projektleiter als nächstes treffen sollte, in Prioritätsreihenfolge.

---

## 10. Unabhängigkeit und spätere Synthese

Dies ist bewusst derselbe Auftrag an mehrere Modelle. Führe die erste Analyse **unabhängig** durch und versuche nicht, vermutete Antworten der anderen Modelle vorherzusunehmen.

Bevorzuge begründete Abweichung gegenüber künstlichem Konsens. Wenn Du glaubst, dass der bisher favorisierte Weg falsch ist, sage das und begründe es.

Die drei Berichte werden anschließend gegeneinander gelegt. In einer zweiten Runde sollen Schnittmenge, Widersprüche und komplementäre Ideen identifiziert und in einen einzigen Forschungsauftrag überführt werden.

**Ziel dieses Reviews ist nicht mehr Text, sondern eine bessere mathematische Entscheidung.**
