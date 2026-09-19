# Reviewerauftrag: Memetik-Bilanz und Vorbereitung des Großversuchs

Du begutachtest kritisch das Forschungsprojekt Conway_99, ausschließlich Memetik/Escape. Arbeitsziel ist ein baldiger größerer Populationsversuch mit mehreren tatsächlich verschiedenen Gründerfamilien. Bitte prüfe sowohl die mathematischen Schlussfolgerungen als auch den experimentellen Nutzen der vorgeschlagenen Vorarbeiten. Du sollst unsere Vorschläge ausdrücklich verwerfen, abändern oder durch eigene ersetzen, wenn die Evidenz dies nahelegt.

## Material und Zugriff
Öffentliches Repository: https://github.com/ibenarb/conway99-research
Fester Ergebnisstand: 96db50629232709a79166200efa93adfd82fbbc3.
Die zu begutachtenden neuen Dokumente sind BERICHT.md und VORUNTERSUCHUNGEN.md im Verzeichnis docs/memetik/review_grossversuch_20260919/ des mit diesem Prompt gelieferten Commits. Notiere dessen SHA in Deiner Antwort; verwende nicht unbemerkt eine spätere Branchspitze.

Pflichtquellen am festen Ergebnisstand:
- docs/memetik/GRUENDERVERTRAG.md
- docs/memetik/UEBERGABE_ESCAPE_20260916.md
- results/memetik/escape_followup_20260916/REPORT.md, symmetry.json, endpoint_symmetry.json, witness_audit.json
- results/memetik/landscape_20260917/REPORT.md und die dort bezeichneten komprimierten Sublevelzertifikate/Isomorphiedaten
- results/memetik/minimax_20260919/REPORT.md, AUDIT.json, audit.py, verify_results.py sowie beide Aufgaben-JSONs
- experiments/memetik/minimax_0_3_0/ (Suchcode/Protokoll), experiments/memetik/escape_0_2/PROTOCOL.md.

Git enthält nicht das große Minimax-Originalarchiv oder die endgültigen SQLite-Dateien. Original: Ergebnisse_Minimax_030_minimax_20260917_213047_385349.zip, 292828623 Bytes, SHA256 eb0b94a06ee2740d0439354146e6785f054e484816670464595ade4214444fe7. Falls Du es nicht erhältst, kennzeichne genau, welche Prüfung deshalb nicht möglich ist. Berichte gelesene Quellen und tatsächlich ausgeführte Prüfungen getrennt. Kannst Du Git nicht erreichen, fordere die benötigten Dateien an; simuliere keinen Zugriff.

## Mathematischer Vertrag
Ziel srg(99,14,1,2), r_uv=(A²)_uv+A_uv−2 für ungeordnete Paare. W zählt Nichtnullfehler, L1 summiert Absolutfehler, F Quadrate. Linf-Selektion: (Linf,Nmax,L1) lexikographisch. Einfache ungerichtete 14-reguläre Graphen auf 99 Knoten; Ω mit kanonischem Rahmen und PH=2J−(C+I)P, λ mit genau einem gemeinsamen Nachbarn je Kante. Ω garantiert nicht global λ=1.
Katalog: Ω-Produkttrades 4×4/4×6/6×6; λ-Apex/Rotation. Alle Zusammenhangs-/Minimalitätsaussagen gelten nur für den untersuchten Katalog. Weglänge, maximale Fehlerbarriere, Isomorphieklasse und beschrifteter Zustand auseinanderhalten. Populationsziele sind L1, F, verfeinertes Linf; W bleibt Diagnose.

## Zu prüfende Kernaussagen
A: geschlossene Achtzustandskomponente, kein besserer Zustand darin.
C08: neutraler W-Ausgang in zwei Schritten; 33 direkte neutrale Nachbarn untereinander isomorph, Gesamtplateau offen; L1/F verschlechtern sich.
C02: W=2031 mit L1=2428,F=3298; F=3292 gehört zu anderen Endpunkten.
B: W=2080 über fünf Schritte ab 2082 und maximale Höhe 2094; zusammen mit geschlossenem Subniveau W<2094 minimale Barriere 12. Kein Nachweis kürzester Länge fünf oder lokalen Minimums bei 2080.
HoG: keine F-Verbesserung, 2142386 gespeicherte Zustände, 76258 expandiert, Minimax-Frontier 3028 gegenüber Start 2836. ≥192 ist bislang code-/checkpointgestützt; keine vollständige unabhängige Nachbarschaftsreproduktion. Vollständigkeitsflags allein sind kein solcher Nachweis.
Acht von 14 KI-Kandidaten sind asymmetrisch; einige unterschiedliche Starts führen unter den untersuchten Abstiegen zu isomorphen Endpunkten.

## Kritische Fragen
1. Welche Aussagen sind bewiesen innerhalb des Katalogs, welche nur unabhängig nachgerechnete Zeugen, welche implementierungsabhängig oder offen? Finde insbesondere Überinterpretationen der Minimax-Frontier und der Begriffe Plateau/Minimum.
2. Ist der bisherige Prüfstand hinreichend für einen heuristischen Großversuch? Welche zusätzlichen Kontrollen ändern tatsächlich eine Entscheidung, welche wären unverhältnismäßig?
3. Reicht die Gründerdiversität? Wie trennst Du Konstruktionsfamilie, Isomorphieklasse, Ω-Arbeitsrahmen und empirisches Einzugsgebiet? Welche Messungen sind ihren Aufwand wert?
4. Sind neutraler Besuchsspeicher und begrenzte Escape-Episoden gerechtfertigt? Welche Stopp-/Umschaltregel würdest Du konkret verwenden? Prüfe Zielkonflikte und lexikographische Neutralität.
5. Priorisiere B-Abstieg, C08-Plateau, A-Operatorerweiterung, HoG-Vertiefung, Gründererzeugung und Rekombination. Was muss vor dem Großversuch geschehen, was darf warten?
6. Prüfe die vier Generatorskizzen, insbesondere die Ω-Kernelbedingungen und die λ-Tripelkonstruktion ohne Berge-Dreiecke. Sind die Bedingungen richtig, zu streng, schon bekannt oder praktisch kaum erzeugbar? Falls Du Neuheit/Literatur beurteilst, recherchiere Primärquellen und verlinke sie.
7. Vergleiche Strategien A/B/C und die vorgeschlagene Ablation. Wie vermeidest Du Unterschiede im Rechenbudget, Startqualität, Überanpassung und Scheinreplikation? Sind vier Abstiegsseeds bzw. drei Screening-Wiederholungen ausreichend für die jeweils beabsichtigte Aussage?
8. Sind 32→64 Plätze je Arm/Ziel und zeitweilige Familienquoten sinnvoll? Welche Alternative wäre bei identischem Budget besser? Muss Crossover überhaupt enthalten sein?
9. Entwickle mindestens zwei eigene, substanziell andere Vorschläge. Gib Mechanismus, erwarteten Nutzen, Scheitermöglichkeit und den kleinsten entscheidenden Versuch an; keine bloße Namensliste heuristischer Verfahren.

## Gewünschte Antwort
- Kurzes Urteil: startbereit / nach benannten Korrekturen startbereit / noch nicht startbereit.
- Tabelle: Aussage – Evidenz – Einwand – notwendige Korrektur.
- Rangliste der Voruntersuchungen mit Aufwand als begründeter Schätzung, Entscheidungswert und Abbruchkriterium.
- Konkreter bevorzugter Versuchsplan mit einfacher Referenz, Messgrößen und Kriterien zur Skalierung.
- Eigene Alternativen, Literaturhinweise soweit tatsächlich geprüft und offene Unsicherheiten.

Sprache Deutsch. Keine Fortsetzung von K66/Involutionsausschluss/C2/O3. Keine neuen Office- oder Ryzen-Läufe starten und keine vorhandenen Checkpoints ändern.
