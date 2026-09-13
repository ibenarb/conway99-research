# Externer Reviewauftrag: Conway99 ohne evolutionäre Suche

Du prüfst als unabhängiger mathematischer Reviewer den bisherigen nicht-evolutionären Forschungszweig von Ralph Beckmanns Conway99-Projekt. Ziel ist ein belastbares Urteil über bewiesene Ausschlüsse, mathematische Transfers, externe Abhängigkeiten und den nächsten sinnvollen Forschungsauftrag. Eine positive Zusammenfassung ohne Gegenprüfung erfüllt den Auftrag nicht.

## Zugang und feste Ausgangspunkte

Repository: https://github.com/ibenarb/conway99-research

Lies zuerst `docs/project_balance_20260913/ZWISCHENFAZIT.md`, danach `AUSSCHLUSSBILANZ.md` und die Dateien unter `results/project_balance_20260913`. Verwende für die dort beschriebenen Forschungsartefakte die feste Basis **769ee6df774a11b90ed18982ce6ff5aca325260a**. Die Bilanz selbst ist eine spätere Dokumentationsschicht über dieser Basis.

Hole auch die historische Referenz **b279cd6de420bc4ad64869c8c7f99d653c73a195**. Dort liegen die in der aktuellen Basis teilweise fehlenden Fixdreiecks- und Versöhnungsdokumente. Alle 27 für die Bilanz tatsächlich gelesenen Quellen sind mit Commit, Pfad, Länge, SHA256 und Git-Blob-ID in `source_manifest.json` identifiziert. Ein nicht im aktuellen Branch vorhandener historischer Pfad ist nicht automatisch eine verlorene Datei.

Zusätzlich erforderlich für den externen f27-Nachweis: https://github.com/infinityscroll/conway99-order3-f27 am Commit **e8f4d629cdf03b4bb14ebed01e4ebe7e8dbf3f8b**. Literaturquellen sind im Zwischenfazit präzise verlinkt. Trenne ausdrücklich zwischen eigenen Projektbeweisen und übernommenen Literaturergebnissen.

## Zentrale zu prüfende Gesamtaussage

Mit den bezeichneten externen Automorphismensätzen bleiben als Symmetrieaufgaben die freie C3-Wirkung mit τ=6 und die Involution mit einem Fixpunkt. Das Projekt schließt zwei historische L-Typen aus, reduziert eine notwendige T-Gram-Aufgabe auf 26 Typen und besitzt einen eigenen abgeschlossenen K66-Fallbeweis. Es schließt weder alle freien C3-Wirkungen noch Involutionen noch asymmetrische Conway-Graphen aus.

Prüfe insbesondere, ob diese Aussage exakt durch die Evidenz gedeckt ist. Die vorige Auskunft im Gespräch hatte den literaturseitig bereits ausgeschlossenen Fixdreiecks-Zweig irrtümlich als vorrangig mathematisch offene Aufgabe dargestellt. Die neue Bilanz korrigiert das. Prüfe die Korrektur an den Primärquellen, nicht durch Mehrheitsvergleich früherer Antworten.

## Prüfprogramm

1. **Globale Abdeckung und Literatur.** Prüfe Theorem 7.1 sowie §7 von Crnković–Maksimović, die Fixpunktklassifikation aus Makhnev–Minakova/Behbahani und die geraden Gruppenordnungen bei Cesarz–Woldar. Zeige präzise, warum Primordnungen 2 und 3 genügen. Unterscheide den übernommenen Fixpunktfreiheitsbeweis von unserem unvollständigen internen Nachvollzug. Keine Behauptung über vollständig neue Reproduktion fremder Computerbeweise ohne tatsächlichen Lauf.

2. **Algebraischer τ=6-Transfer.** Prüfe den Projektor E3, seine 3-adische Integrität, die Modulstruktur über Z3[C3], die Lokalität der Gruppenalgebra, Projektivität/Freiheit des Bildes und den Spurschluss. Vergleiche Ishida v2, §8.4. Begrenze die Verwendung auf den tatsächlich begründeten Spezialfall; der Mooregraph-Titel schließt Conway-Involutionen nicht aus. Prüfe separat den elementaren Dreieckskongruenzbeweis.

3. **τ=27.** Prüfe den Unterschied zwischen Quotientenausschluss und bloßem Lift-Ausschluss. Lies `src/research_20260912/replay_f27.py` und den gespeicherten Log. Falls Du die Fremdkette neu ausführst, verwende den festen Commit, regeneriere auch die sechs Anfangs-Gram-CNFs und prüfe alle 13 DRAT-Beweise. Der aktuelle Log enthält die 13 Replay-Marker, aber nicht die sechs Zusatzmarker; dokumentiere genau, was selbst nachgerechnet wurde.

4. **FPF-Layer A/B und historische Zertifikate.** Prüfe die exakten Quotientengleichungen, C4-Ausschluss, Lemma B, den historischen Encoder unter `vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat` und den all-τ-Aufruf. B ist nach Projektbehauptung redundant zu A. Prüfe die beiden historischen L-Typausschlüsse, insbesondere die Lemma-CNF-zu-Quotient-Richtung und die vollständige Coverage von 488+168=656. Der historische `lrat-check` zählt nicht als zuverlässige unabhängige Positivinstanz; Cake-Ausgaben und deren Hashbindung sind gesondert zu prüfen.

5. **156→69→44→26.** Prüfe die vollständige Sechsknotengraph-Enumeration und exakte Negativzeugen. Prüfe die 18 rationalen Separationszeugnisse gegen alle 64 binären Profile, die Zuordnung unter Umnummerierung und die 26 ganzzahligen Gram-Zeugen. Der eigene Prüfer ist `src/review_synthesis_20260912/verify_review.py`; er verwendet die Daten der vorherigen Aggregationsrechnung. Prüfe deshalb die erste Enumeration zusätzlich, statt den späteren Prüfer als Nachweis sämtlicher Vorstufen auszugeben. Die vier älteren Ausschlüsse sind in den 18 enthalten. Es bleiben 26, nicht 22. Keine Addition oder unqualifizierte Multiplikation mit den 101 L-Typen.

6. **K66.** Lies `K66_BEWEISABSCHLUSS.md` und `MATHEMATISCHER_AUDIT.md` unter `docs/k66_encoder_audit_20260913`. Prüfe Notwendigkeit aller Profil-/Paar-/Projektor-/Starbedingungen, BDD-Übersetzung, Multiplizität höchstens zwei, simultane Runden und das Profil 3520. Prüfe die 167 CNF-Verknüpfungen, 28 zusätzlichen Replays, 125 Profilbeweise sowie die Coverage und archivierte Cake-Evidenz der 897 Hauptblätter. Die 223 negativen Hauptminoren plus 23 Restfälle müssen exakt die 246 Bahnen und 13.824 Crossmatchings decken. Verwechsle alternative alte Brücken-/Blattpläne nicht mit dem tatsächlich benutzten Hauptbeweis. Prüfe die Version 1.0.1 des Abschlussprüfers und ihre Bindung an die veröffentlichten kompakten Berichte.

7. **Involution.** Prüfe den Übergang vom einzigen Fixpunkt zur Vertauschung jeder Kante von N(v)=7K2 und zur eindeutig induzierten Wirkung auf den 84 äußeren Paarlabels. Benenne das noch zu lösende vollständige Matrixproblem. Eine kanonische Permutation ist eine WLOG-Reduktion, kein UNSAT-Beweis.

8. **Lift und Nebenstränge.** Prüfe die Domäne des modularen Liftkriteriums: exakter Quotient erforderlich. Die kleinen Rook-Kontrollen und das 729-Phasen-Gegenbeispiel stehen in Git. Unterscheide sie von einem allgemeinen Beweis. Ordne den geometrischen δ=5-Zweig und den Reimbayev-Fehlerbefund korrekt ein; keiner ist ein neuer globaler Ausschluss. Keine Behandlung des evolutionären Projektteils erforderlich.

## Datenzugang und Ausführungsdisziplin

Git ermöglicht die Prüfung von Code, Herleitungen, kleinen Zeugen, Manifesten und gespeicherten Resultaten. Große historische LRAT-Dateien liegen teilweise ausschließlich auf Ralphs Rechner. Ein vollständiger frischer Produktionsreplay ist mit Git allein dann nicht möglich. Melde die exakt fehlenden Dateien anhand der Manifeste, statt einen Replay zu behaupten oder automatisch den mathematischen Satz zu verwerfen.

Arbeite in einem isolierten Checkout. Einige vorhandene Prüfer schreiben Ergebnisdateien: Vergleiche mit dem festen Commit und überschreibe keine Forschungsbasis. Führe keine unbegrenzten Solverläufe und keine neuen großen Suchkampagnen aus. Beginne mit mathematischer und kleiner exakter Zertifikatsprüfung. Falls große Daten fehlen, liefere das bis dahin vollständige Urteil mit präziser Zugangsgrenze.

Ein TIMEOUT, ein numerischer LP-Status, eine gespeicherte PASS-Zeile und ein selbst wiederholter Proofcheck sind verschiedene Evidenzstufen. Auch eine vollständig verifizierte UNSAT-CNF benötigt einen korrekten mathematischen Transfer zum Graphfall.

## Erwartete Rückgabe

Erstelle einen zusammenhängenden Reviewbericht mit:

- einer Tabelle jeder tragenden Aussage: exakter Geltungsbereich, Quelle/Commit, eigene Prüftätigkeit, Urteil und Restpflicht;
- einer Liste tatsächlicher Fehler mit minimalem Gegenbeispiel oder präziser fehlerhafter Ableitung;
- einer getrennten Liste fehlender Daten und nicht ausgeführter Replays;
- einem Urteil über die K66-Beweiskette und die 26er-Gram-Reduktion;
- einer korrigierten Restbilanz für freie C3-Wirkung, Involution und interne Literaturablösung;
- höchstens drei priorisierten Folgeaufträgen mit mathematischem Gewinn, notwendiger Modellstärke und eindeutigem Abschlusskriterium.

Gib konkrete Urteile je Teilbehauptung: akzeptiert, akzeptiert unter benannter Voraussetzung, Nachweis unvollständig oder widerlegt. Ein pauschales GO ohne diese Auflösung genügt nicht. Keine globale Laufzeitprognose aus dem K66-Nachprüflauf oder aus der Anzahl der Gram-Typen ableiten.
