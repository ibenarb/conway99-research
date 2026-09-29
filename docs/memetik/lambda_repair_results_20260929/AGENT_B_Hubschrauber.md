# Agent B: Hubschrauber — Gesamtsicht und neue Kombination

Stand: 29.09.2026. Eigenständige strategische Analyse, keine gestartete Kampagne und kein Wirksamkeitsnachweis.

## Haupturteil

Wir besitzen inzwischen eine leistungsfähige lokale Suche und einen funktionierenden exakten Reparaturbaustein. Was noch fehlt, ist ein kontrollierter Mechanismus, der die **unterschiedlichen Strukturen bereits vorhandener guter Graphen gemeinsam nutzt**. Meine Priorität ist deshalb eine durch Elternunterschiede bestimmte, harte λ-erhaltende Rekombination mit anschließendem unverändertem P-Abstieg. Sie kombiniert Archivwissen, exakte Reparatur und lokale Verbesserung. Sie ist enger prüfbar als ein vollständiger neuer genetischer Hauptlauf.

Die vorgeschlagene Neuheit ist projektspezifisch. Rekombination, Path Relinking und Large Neighbourhood Search sind etablierte Ideen; daraus folgt keine bekannte Erfolgsgarantie für Conway99.

## Was die bisherigen Versuche gemeinsam sagen

1. **P war produktiv, zusätzliche lokale Operatoren nicht automatisch.** Im Vierstundenvergleich gewann P alle zwölf Paare gegen PC; Median W 2123 gegenüber 2136,5. Die zusätzliche C3-Nachbarschaft allein begründete keinen Vorteil. Quelle: `docs/memetik/lambda_followup_results_20260923/BERICHT.md`.
2. **Vorhandene gute Starts weiterzuentwickeln lohnte zunächst.** Die V2-Frontier erreichte W2096; später wurden W2076 und W2077 erreicht. V3 blieb trotz längerer Erholung hinter seinem Ziel. Das ist Evidenz für die damaligen Start-/Operatorpakete, kein Verbot weiterer Herkunftsfamilien. Quellen: `lambda_frontier_20260924/ENTSCHEIDUNG.md`, `lambda_radius_20260926/ERGEBNIS.md`.
3. **Die aktuellen Rekorde sind für den vorhandenen AP-Katalog schwer lokal zu verbessern.** Radius vier brachte keinen Treffer. Im Perturbationsprofil gab es 5685 fertige Episoden ohne Verbesserung; große k reduzierten die Rückkehr deutlich, verbesserten aber keine Endpunkte. Weglänge, Nicht-Rückkehr und Vielfalt allein sind keine Fortschrittsmaße. Quellen: `lambda_radius_20260926/ERGEBNIS.md`, `lambda_profile_20260927/ERGEBNIS.md`.
4. **Exakte Fensterreparatur kann eine bessere Struktur finden, doch die gewählten Fenster liefern wenig.** Der aktuelle Befund 1.2.0 — vom Hauptaudit dieser Übergabe übernommen, hier nicht erneut berechnet — lautet: 144 Aufgaben, 24 Gründer, nur dieselbe Verbesserung 2139→2127 wie zuvor, kein W<2076, 88 Solver-Optimalitätsmeldungen, fünf starre und 51 offene Aufgaben. Insbesondere bleiben sämtliche 48 Fenster der Größe 60 offen. Das begründet weder globale Starrheit noch eine Erschöpfung der exakten Methode.
5. **24 Klassen sind keine 24 unabhängigen Abstammungslinien.** Die aktuelle Bank stammt aus Profilnachkommen zweier Rekordstarts. Sie ist nach Klassen und Fehlermerkmalen diversifiziert, aber dieser engere Herkunftskorridor bleibt relevant. Quelle: `lambda_repair_pilot_20260927/PLAN_V2.md`.

Die gemeinsame Engstelle könnte daher weniger die Zahl der Sekunden als die Wahl der **gleichzeitig freigegebenen Variablen** sein. Dies ist eine Hypothese: Knotenfenster frieren alle Außenkanten ein; notwendige koordinierte Änderungen könnten räumlich verteilt sein. Die bisherigen Daten beweisen diese Erklärung nicht.

## Konkrete Kombination: elterninformierte Rekombinationsreparatur

Für zwei gültige λ-Graphen A und B auf denselben 99 beschrifteten Knoten sei D die symmetrische Differenz ihrer Kantenmengen.

- Außerhalb D werden sämtliche Paarvariablen auf den gemeinsamen Elternwert fixiert; innerhalb D dürfen Kanten frei gewählt werden. Grad 14 und λ=1 bleiben für den gesamten Ergebnisgraphen hart.
- Beide Eltern sind in diesem Modell zulässig. Das liefert unmittelbar zwei positive Kontrollbelegungen. Es beweist nicht, dass eine dritte zulässige Mischung existiert.
- Zur mechanischen Diagnose werden beide exakten Elternbelegungen per No-good ausgeschlossen. Findet das Modell nun einen gültigen dritten Graphen, existiert ein nichttrivialer Rekombinationsraum. UNSAT gilt zunächst nur als Solvermeldung, solange kein unabhängig geprüftes Zertifikat vorliegt.
- Eine zweite Maske ergänzt vorab bestimmte, an D angrenzende Paarvariablen. Dadurch kann die Suche über reine Mischungen hinausgehen. Der Zusatzumfang muss vorab fixiert und vollständig gespeichert werden.
- Alle neuen gültigen Kinder erhalten denselben unveränderten P-Abstieg. Verbesserungen werden vor und nach diesem Abstieg getrennt ausgewiesen. Keine ungültige Zwischenbelegung zählt als λ-Kandidat.

**Beschriftung ist ein Forschungsparameter.** Kanonisierung beseitigt Isomorphieduplikate; sie ist keine optimale strukturelle Ausrichtung nichtisomorpher Eltern. Bei Profilverwandten ist die gemeinsame historische Nummerierung zunächst ein reproduzierbarer Start. Andere Herkunftsfamilien benötigen eine explizite, zeitlich verbuchte Ausrichtungsheuristik und Kontrollvergleiche. Sonst misst man beliebige Nummerierung statt gute Rekombination.

## Ein ausreichend breiter, interpretierbarer Versuch

Vor einem neuen Hauptlauf schlage ich 24 festgelegte Elternpaare und drei Arme vor. Ein Elternteil kommt jeweils aus der bestehenden 24er-Bank; der Partner wird aus einer unabhängig geprüften Archivbank von bis zu 64 Klassen gewählt. Diese enthält gute W-Kandidaten, gute L1/F-Kandidaten und strukturell verschiedene Profilendpunkte. Auswahl, Scoreband, Paarbildung, Beschriftung und Masken werden vor Beginn veröffentlicht. Historische, bislang schwächere Herkunftslinien dürfen als Donoren vorkommen, ohne ihnen sofort ganze langfristige Sucharme zuzuweisen.

- **R:** Zufällige verteilte Paarmaske um den Empfänger, passend zur Variablenzahl und möglichst auch zur Knoteninzidenz der jeweiligen D-Maske. Referenz für die bloße Form/Größe der Freigabe.
- **D:** Elternunterschiede als Maske.
- **D+:** Dieselbe Elternmaske plus vorab definierter Puffer; getrennte größere Nachbarschaft, kein reiner Vergleich bei identischer Modellgröße.

Jede Zelle erhält eine CPU-Stunde einschließlich Ausrichtung, Modellbau, Reparatur und Nachabstieg; 24×3=72 Such-CPU-h, dazu beispielsweise zwölf Hilfs-CPU-h. Auf zwölf Workern ergibt das sieben Stunden ideale Gesamtbudgetprojektion; tatsächliche Walltime wird auf Ryzen gemessen, nicht aus Cloudzeiten zugesagt. Dies ist ein Budgetvorschlag, keine laufende Freigabe. Der Vergleich R gegen D untersucht informierte Freigabe bei ähnlicher Größe; D gegen D+ untersucht zusätzliche Freiheit und kann wegen größerer Modelle keine reine Informationswirkung isolieren.

Zuerst technische Kontrollen: beide Elternbelegungen, unabhängige Scores/λ, Isomorphiededuplikation, kleine vollständig enumerierte Rekombinationsmodelle, No-good-Wirkung, budgetierte Modellbau- und Nachabstiegszeiten. Ein begrenzter mechanischer Vorabtest soll lediglich einen unbrauchbaren Encoder erkennen; er ersetzt nicht die breite 24-Paar-Stichprobe. Die Suchkampagne erhält eine feste Zahl von Versuchen pro Zelle oder vollständige Aufzeichnung aller innerhalb des Budgets begonnenen Versuche; keine versteckte Wiederholung nur erfolgreicher Paarungen.

## Erfolg und Widerlegung

Primär bleibt ein unabhängig geprüfter W-Rekord unter 2076. Sekundär zählen strikt bessere Kinder gegenüber dem besseren Elternteil, neue Klassen und Nachabstiegsgewinne pro tatsächlicher CPU-Stunde. Ein Kind, das nur den schlechteren Elternteil verbessert, wird separat ausgewiesen. Unterschiedliche Beobachtungen desselben Kindes sind keine unabhängigen Treffer.

- Liefert D praktisch nur Eltern oder keine dritten gültigen Klassen, ist **reine Elternmischung in diesen Masken** mechanisch schwach; D+ kann prüfen, ob eingefrorene Übereinstimmungen die Ursache sind.
- Liefert D viele neue gültige Klassen, aber keine besseren Nachabstiegsendpunkte, ist Vielfalt als Hilfsmittel bestätigt, der behauptete Optimierungsnutzen jedoch nicht.
- Schlägt D die ähnlich großen R-Masken nicht, gibt es hier keinen positiven Beleg für den Informationswert der Elternunterschiede.
- Liefert nur D+ etwas, darf das nicht allein der Rekombination zugeschrieben werden: größere Freiheit ist eine konkurrierende Erklärung.
- Bleiben überwiegend UNKNOWN-Modelle ohne Kinder, ist der Encoder/Solverdurchsatz der nächste Untersuchungsgegenstand. Kein globaler negativer Schluss über Rekombination.

Vorab kann man eine pragmatische Fortsetzungsregel festlegen: mindestens ein neuer Rekord oder Verbesserungen gegenüber dem jeweils besseren Elternteil bei mindestens drei unterschiedlichen Empfängern und Vorteil von D gegenüber R in der CPU-Nutzenbilanz. Das ist eine Managementregel, kein Signifikanztest und kein Konvergenzbeweis.

## Literaturanschluss und Grenzen

Glover, Laguna und Martí, *Scatter Search and Path Relinking: Foundations and Advanced Designs*, Fassung 27.06.2002, beschreiben die systematische Kombination qualitäts- und diversitätsorientierter Referenzlösungen sowie anschließende Verbesserungsverfahren. Primärquelle, im Browser gelesen: https://www.uv.es/~rmarti/paper/docs/ss7.pdf . Diese Quelle begründet die allgemeine Verfahrensfamilie; sie behandelt nicht unseren λ-Raum und beweist keinen Vorteil des vorgeschlagenen Encoders. Der hier vorgeschlagene direkte CP-SAT-Mischraum ist insbesondere kein nachgewiesener AP-Pfad zwischen den Eltern.

Die allgemeine LNS-Idee wird in Paul Shaw, *Using Constraint Programming and Local Search Methods to Solve Vehicle Routing Problems* (1998), DOI https://doi.org/10.1007/3-540-49481-2_30 eingeführt. Der DOI-Aufruf lieferte in dieser Sitzung einen Browserfehler; daher wird daraus kein ungelesenes Detailargument abgeleitet. Der Vorschlag ist primär aus dem Projektbefund und der gelesenen Scatter-Search-Quelle motiviert.

Angewandte globale Regeln: GC-01/02 (Hostuhr, lokale tolerierte Nachläufe und tatsächliche Abrechnung), GC-08 (Reichweite begrenzen), GC-10 (Versuch/Aufgabe/Planerfüllung trennen), GC-11 (Budgetprojektion von Prognose unterscheiden). Keine laufenden Prozesse oder eingefrorenen Quellen wurden geändert.
