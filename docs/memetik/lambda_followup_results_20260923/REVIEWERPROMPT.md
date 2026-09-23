# Unabhängiger Review: λ-Suche nach dem Ryzen-Folgelauf

Arbeite am Conway99-Projekt ausschließlich im Zweig MEMETIK/λ auf dem Ryzen.
Ziel ist die Suche nach srg(99,14,1,2), nicht der Symmetrieausschluss.

**Auftrag:** Werte den abgeschlossenen Folgelauf eigenständig aus. Welche
Schlussfolgerungen ziehst Du? Würdest Du weitere Voruntersuchungen empfehlen,
einen größeren Hauptlauf beginnen oder eine andere Fortsetzung wählen?
Keine dieser Antworten wird vorausgesetzt. Entwickle Deine Empfehlung aus
den Daten und kennzeichne Unsicherheit. Es gibt keine vorgegebene Präferenz
für einen Operator, eine Population oder ein Rechenbudget des nächsten Laufs.

## Quellen und Arbeitsweise

Beginne mit BERICHT.md und den Originaldaten im unten genannten flachen ZIP. Die großen Ergebnisdateien werden ausschließlich im ZIP bereitgestellt; FILE_INDEX.json ordnet die flachen Dateinamen ihren Originalpfaden zu.
Nutze EVALUATION.json, ENDPOINTS.tsv, CURVES.tsv, jobs/*/result.json,
task.json und receipt.json sowie plan.json, HARVEST.json und AUDIT.json.
Die Endpopulationen, Verbesserungskurven und Graphen sind mitgeliefert.
Das ergänzende flache ZIP liegt unter `releases/memetik/lambda_followup_review_20260923_flat.zip`.
FILE_INDEX.json enthält die ursprünglichen Pfade; mitgelieferte SHA256SUMS
ermöglichen eine Integritätsprüfung. Quellen werden nicht allein durch ihre
Dateinamen beschrieben: lies die relevanten Implementierungen tatsächlich.

Fixierte ausführbare Grundlage:
https://github.com/ibenarb/conway99-research/tree/3bafd487c9d9ec513da853577a6f4d2750a4e479/experiments/memetik/lambda_followup_1_0_0

Vorheriger Vergleich und Roh-Ergebnisprüfsatz:
https://github.com/ibenarb/conway99-research/tree/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922

Ursprünglicher Suchcode mit Gründerbank:
https://github.com/ibenarb/conway99-research/tree/b659cb8743dd6036d91dafb466b2d12cb21a29b0/experiments/memetik/lambda_compare_0_2_0

Der aktuelle Befundbericht enthält keine Empfehlung für die nächste Kampagne.
Ältere Planungsmeinungen sind keine Vorgabe; urteile zunächst aus Ergebnissen
und Implementierung. Trenne Methodenvergleich, separate Rekordsuche und
nachträgliche Archivernte. Berücksichtige wiederverwendete Seeds, gemeinsame
Gründer, selektive TC-Fortsetzungen und unterschiedliche Zielnormen.

Die SQLite-Vollarchive sind nicht im Prüfsatz. Erkläre konkret, falls eine
Deiner notwendigen Prüfungen zusätzliche Daten braucht. Leite fehlende
Archivinformationen nicht aus Endpopulationen ab. Unterscheide selbst
nachgerechnet, aus Belegen übernommen, plausibel vermutet und ungeklärt.
Führe keinen längeren Suchlauf aus; kleine klar budgetierte Diagnosen sind zulässig.

## A. Eigenständige Befundbewertung

Welche Ergebnisse sind belastbar, welche nicht? Prüfe relevante Scores,
Paarvergleiche und Zeit-/Budgetfragen. Was zeigen Verläufe und Operatorzahlen
über Fortschritt, Stagnation und Kosten? Was lässt sich über Herkunft,
Vielfalt und Verwandtschaft der Kandidaten sagen? Unterscheide beschriftete
Unterschiede, Isomorphie und tatsächlich verschiedene Suchregionen.
Welche Aussagen über die Nähe zu einer exakten Lösung wären unzulässig?

## B. Entscheidung und eventuelle Voruntersuchungen

Welche Fortsetzung empfiehlst Du, und warum? Falls Du Voruntersuchungen
vorschlägst: Gib für jede die offene Frage, den minimalen Versuchsaufbau,
benötigte Daten, CPU-Budget, Entscheidungskriterium und Konsequenz beider
möglichen Ausgänge an. Unterscheide Auswertung vorhandener Daten von neuer
Rechenarbeit. Welche Untersuchung ist vor einem Hauptlauf notwendig, welche
optional, welche kann in ihn eingebaut werden? Ein begründetes „keine weitere
Voruntersuchung“ ist ebenso zulässig. Vermeide Vorschläge, deren Ergebnis
keine konkrete Entscheidung ändern würde.

## C. Falls Du einen Hauptlauf empfiehlst: vollständige Bauanleitung

Spezifiziere den Lauf so genau, dass ein anderer Entwickler ihn ohne eigene
Forschungsentscheidungen implementieren kann. Falls Du ihn noch nicht
empfiehlst, benenne die Bedingungen, unter denen Du dazu übergehen würdest.

1. **Anfangspopulation:** konkrete Quellen und Familien, Größe, Anzahl Inseln,
   Anteile alter/neuer/rekordnaher Kandidaten, Erzeugungsverfahren, harte
   Gültigkeit, Deduplikation, Diversitätsmaß und Mindestvielfalt. Wie werden
   fehlende oder zu ähnliche Gründer ersetzt? Welche Rolle hätten weitere
   Konstruktionsfamilien, sofern Du sie überhaupt benötigst?
2. **Bewertung und Selektion:** Ziele, Zielordnungen oder Pareto-Regeln,
   Elternauswahl, Selektionsdruck, Elitismus, Überlebensauswahl, Umgang mit
   Gleichständen und Duplikaten. Falls Ziele wechseln: genaue Regel.
3. **Mutation und lokale Suche:** konkrete Operatoren, Mischungsanteile,
   Perturbationslängen, Zulässigkeit, Reparatur, Akzeptanz verschlechternder
   Schritte, lokale Abstiegskriterien, Budgets und Abbruchregeln. Gib an,
   welche Eigenschaften mathematisch erhalten bleiben und was geprüft wird.
4. **Crossover:** Verwenden oder weglassen? Begründe dies. Bei Verwendung:
   Elternausrichtung, Rekombinationseinheiten, Algorithmus/Pseudocode,
   Erhaltung der λ-Bedingungen oder definierte Reparatur mit Kostenlimit,
   Quote, Fehlversuchsbehandlung, anschließende lokale Suche. Erkläre, wie
   Nutzen gegenüber Mutation und Neustarts bei fairem CPU-Budget messbar wird.
5. **Population und Austausch:** Generations- oder Steady-State-Modell,
   Ersatzpolitik, Alterung, Archive, Stagnation, Neustarts sowie gegebenenfalls
   Migration zwischen Inseln mit Zeitpunkt, Auswahl und Annahmeregel.
6. **Versuchsdesign:** Kontrollarme nur soweit sachlich nötig, gepaarte oder
   neue Seeds, Zahl unabhängiger Wiederholungen, gleiche Budgetbasis,
   Trennung von explorativer Rekordsuche und Methodenvergleich. Berücksichtige
   Selektion nach bereits bekannten Ergebnissen und Mehrfachvergleiche.
7. **Betrieb auf Ryzen/WSL2:** Workerzahl, CPU-/RAM-/Plattenbudget, Walltime
   mit Annahmen, Checkpoints und reproduzierbare Wiederaufnahme, Zeitgeber,
   Status alle zehn Minuten, Ressourcenabbruch, Lösungserkennung und
   unabhängige Validierung. Office ist nicht Teil dieses Laufs.
8. **Auswertung vorab:** primäre/sekundäre Kriterien, Messpunkte, Zwischenbilanz,
   vorab definierte Fortsetzungs-/Änderungs-/Abbruchentscheidung und maximale
   Gesamtkosten. Erkläre, was ein negatives Ergebnis bedeuten würde.

## D. Konkrete Rückgabe

Liefere eine eigenständige Markdown-Datei mit Kurzurteil, Evidenztabelle,
priorisierten Voruntersuchungen (gegebenenfalls leer), der gegebenenfalls
empfohlenen Hauptlauf-Spezifikation und offenen Risiken. Füge ein maschinenlesbares
Versuchsmanifest mit exakt aufaddiertem CPU-Budget hinzu, sofern Du einen Lauf
empfiehlst. Prüfskripte und neue Zeugen bitte als flaches ZIP, mit Eingabehashes,
Seeds, Laufzeit und Ergebnissen. Keine pauschale Behauptung einer vollständigen
Rohdatenprüfung, wenn Du nur den reduzierten Prüfsatz gelesen hast.
