# Codex v01: unabhängige Abnahme, 2026-09-15

## Entscheidung

Alle zehn eingereichten Graphen werden aufgenommen: C01–C05 im Ω-Arm, C06–C10 im λ-Arm. Die Originalantwort bleibt unverändert in `original.md`; dieser Bericht ist die davon getrennte Prüfung. Die Modellbezeichnung Codex ist die Eingangsangabe, keine externe Modellverifikation.

Alle harten Bedingungen, SHA256-Prüfsummen und vollständigen Residuenmetriken stimmen. Alle zehn erfolgreichen Generatoraufrufe wurden erneut ausgeführt und lieferten byteidentische graph6-Daten. Kein Graph löst srg(99,14,1,2).

## Befunde

| ID | Familie | Arm | W | L1 | F | Linf | Nmax | Aut-Gruppe |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C01 | F02 | Ω | 2114 | 2724 | 4098 | 5 | 2 | 1 |
| C02 | F02 | Ω | 2074 | 2506 | 3472 | 4 | 6 | 1 |
| C03 | F02 | Ω | 2153 | 2692 | 3900 | 4 | 3 | 1 |
| C04 | F02 | Ω | 2105 | 2572 | 3612 | 4 | 4 | 1 |
| C05 | F02 | Ω | 2215 | 2766 | 3994 | 4 | 5 | 1 |
| C06 | F03 | λ | 2244 | 3828 | 8184 | 4 | 198 | 66 |
| C07 | F03 | λ | 2772 | 4488 | 8976 | 4 | 132 | 66 |
| C08 | F04 | λ | 2673 | 3498 | 5412 | 3 | 132 | 33 |
| C09 | F04 | λ | 2871 | 3828 | 6072 | 4 | 33 | 33 |
| C10 | F04 | λ | 2739 | 3696 | 5940 | 4 | 33 | 33 |

Die unabhängige Prüfung dekodiert graph6 ohne NetworkX, zählt gemeinsame Nachbarn mit Mengenoperationen und prüft bei Ω den vollständigen kanonischen Rahmen einschließlich aller 1176 PH-Gleichungen. Bei λ haben alle 693 Kanten genau einen gemeinsamen Nachbarn. Die nichtverschwindenden λ-Fehler der Ω-Graphen sind dort erlaubt. Die Scores summieren über ungeordnete Paare u<v, ohne Diagonale.

Zusätzlich wurden der mitgelieferte Verifier und der mitgelieferte Isomorphieprüfer ausgeführt. Die eigenständige nauty-Prüfung bestätigt Zusammenhang, Automorphismengruppen und paarweise Nichtisomorphie aller zehn Graphen. C01–C05 haben jeweils 99 Knotenorbits, C06/C07 zwei, C08–C10 drei.

Der unabhängige Altbestandsvergleich umfasst genau die 18 in `reference_manifest.json` benannten Dateien: zehn Gründer, vier Office-Zeugen, Gemini und drei Claude-Graphen. Alle lokalen Referenzbytes stimmen über ihre Git-Blob-IDs mit Remote-Commit `bb43b0ab4fad36e142832923b83dcf3f6a186652` überein. Kein neuer Graph ist zu einem dieser 18 Graphen isomorph. Die Aussage erfasst keine weiteren Graphen in historischen JSON-Populationen, privaten Archiven oder unaufgeführten Dateien. Sie belegt keine neuen Einzugsgebiete.

## Analyse der Konstruktionen

**F02 ist der wichtigste Beitrag.** 84 Außenknoten werden in 21 Viererfasern aufgeteilt. Jede Faser enthält einen C4. Zwischen Fasern mit disjunkten Zweierträgern liegt jeweils ein perfektes Matching; sonst gibt es keine äußeren Kanten. Jede Faser hat zehn disjunkte Partnerfasern: H-Grad 2+10=12. Die zusätzlich erzwungenen PH-Bilanzen liefern exakt den Ω-Rahmen. Der Generator hat 1680 freie Boolesche Kantenvariablen. Er verlangt keine globale nichttriviale Automorphie; deren Fehlen ist an allen fünf Ergebnissen bestätigt.

C02 unterbietet die dokumentierten Office-Ω-Bestwerte W=2110, L1=2718 und F=3926 gleichzeitig mit W=2074, L1=2506, F=3472. Das sind Vergleiche der jeweiligen besten Kennzahlen, nicht notwendigerweise desselben alten Graphen. Auch C04 verbessert diese drei Vergleichswerte. C02 verbessert nicht den bisherigen Ω-Linf-Wert 3. Der λ-Bestwert F=2836 bleibt ebenfalls niedriger; deshalb kein armübergreifender oder weltweiter Rekordanspruch. Die neuen Graphen entstanden ohne Optimierung dieser Fehlernormen.

**F03/F04 erweitern die Startstrukturen, sind aber verwandt.** Es handelt sich um dreiteilige Z33-Lifts mit sieben Dreiecksoffsets. F03 ist der Spezialfall (a,b)=(d,2d) von F04. Die Offsetbedingungen garantieren 14-Regularität und genau ein Dreieck pro Kante. Diese Graphen sind nicht knotentransitiv und widersprechen dem früheren Cayley-Ausschluss auf 99 Knoten nicht.

Die feste Dreiteilung in Klassen zu 33 Knoten verhindert eine exakte Lösung: Für eine Klasse U hat jeder der 66 Außenknoten genau sieben Nachbarn in U. Daher beträgt die Summe gemeinsamer Nachbarn über Paare in U genau 66·C(7,2)=1386. Da U unabhängig ist, würde μ=2 stattdessen 2·C(33,2)=1056 verlangen. Die Differenz 330 ist ein strukturelles Hindernis dieser Vorlage. Als λ-Gründer bleiben die Graphen zulässig; die nachfolgende Suche muss die Klassenstruktur verlassen können. Ob unsere konkreten Trades dies wirksam tun, ist noch nicht geprüft.

**F01 bleibt ein offener Erzeugungsversuch.** Der freie Ω-CSP ist prinzipiell derselbe Ansatz wie bei Gemini, hier mit anderen Solverparametern. Die vier berichteten UNKNOWN-Aufrufe wurden nicht wiederholt. Sie belegen weder Unmöglichkeit noch eine belastbare Laufzeitüberlegenheit von F02. Die eigenen Wiederholungen betreffen ausschließlich die zehn erfolgreichen Aufrufe.

## Schlussfolgerung für den Pilot

1. C02 als vorrangigen neuen Ω-Gründer berücksichtigen, C04 als weiteren guten Normstart. C03 ergänzt die Auswahl nach (Linf,Nmax). Die anderen F02-Graphen als kontrollierte Varianten derselben Familie behandeln.
2. C08 als besten F-Wert der neuen λ-Gruppe berücksichtigen; mindestens einen F03-Graphen als Strukturkontrast aufnehmen. Die höheren Fehlerzahlen allein sind bei einem Diversitätsexperiment kein Ablehnungsgrund.
3. Nicht zehn zusätzliche Graphen mit zehn unabhängigen Suchprinzipien gleichsetzen. Familienzugehörigkeit bei Stichprobe und Auswertung berücksichtigen.
4. Vor dem neuen Pilot die geplante Fluchtwegserkundung durchführen. Neben den alten Plateaus mindestens C02 und einen λ-Lift nach demselben lokalen Abstieg untersuchen. Nichtisomorphie und triviale Automorphismengruppe garantieren weder unterschiedliche Plateaus noch kurze Fluchtwege.
5. Die freie Suchbewegung im Ω-Arm darf nicht auf die F02-Matchings beschränkt werden; im λ-Arm darf die feste Dreiteilung nicht zur unbeabsichtigten Invariante werden. Umfang und Erreichbarkeit der vorhandenen Operatoren sind dafür gesondert zu prüfen.

## Reproduzierbarkeit

`submission.json`, `generate.py`, `compare.py`, `verify.py` sind unverändert aus den markierten Blöcken der Originalantwort extrahiert. `audit.py`, `audit_helpers.py` und `reproduce.py` sind eigene Prüfwerkzeuge. Die Hilfsfunktionen für graph6 und harte Bedingungen stammen aus der vorherigen unabhängigen Claude-Abnahme und wurden ohne deren Claude-spezifischen Hauptlauf übernommen.

Aus dem Verzeichnis dieser Einreichung, mit dem Repository in REPO_ROOT:

```bash
python audit.py --reference-root "$REPO_ROOT"
python reproduce.py
python verify.py original.md
python compare.py --markdown original.md --out comparison.json
```

Die letzte Zeile prüft nur die Einreichung untereinander; der Referenzvergleich erfolgt im eigenen `audit.py`. Abhängigkeiten und tatsächlich verwendete Versionen stehen in `environment.json`. Wiedererzeugung: zehn Einzelprozesse, jeweils höchstens 30 Sekunden äußerer Timeout, ursprüngliche Generatorargumente unverändert bis auf Ausgabepfad. Die aufsummierte interne Walltime betrug etwa 0,94 s, ohne Python-Prozessstarts. Das ist eine einzelne Wiederholung, kein Benchmark. `reproduction.json` enthält die vollständigen Resultate.
