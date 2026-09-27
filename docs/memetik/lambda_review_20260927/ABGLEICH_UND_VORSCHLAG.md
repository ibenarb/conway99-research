# λ-Memetik: Reviewabgleich und nächster Schritt, 27.09.2026
> Nachtrag: Der vollständige Reviewtext ist inzwischen eingegangen. Der unten stehende vorläufige Versuchsplan wird durch [Abgleich und Plan V2](ABGLEICH_VOLLREVIEW_UND_PLAN_V2.md) ersetzt; die dokumentierten Prüfungen bleiben gültig.

**Empfehlung:** Ein begrenzter, instrumentierter Vergleich von drei Perturbationslängen-Verteilungen an den beiden fixierten Rekordgraphen. 24 Jobs mit je 30 CPU-Minuten, zusammen 12 Such-CPU-h plus höchstens 1 CPU-h Vorbereitung/Kontrollen. Keine adaptive Population während dieses Diagnosetests. Kein Tiefe-5-Lauf, kein großer unveränderter P-Lauf und kein gleichzeitiger Wechsel von Operator oder Zielfunktion. Dies ist ein Vorschlag, noch nicht implementiert oder gestartet.

## Eingang und fehlender Teil

Der übermittelte SHA256 stimmt:
`2299db62ac1b77ed90b2e83a7be6101970f7725e4d73e539f032497c0d1d9f69`.
Das ZIP hat 28889 Bytes, 20 Dateien und 19 gültige interne Manifestzeilen.
Alle neun Quellhashes stimmen mit den vorhandenen fixierten Projektdateien überein.
Der gelesene Reviewprompt ist byteidentisch zu unserem veröffentlichten Auftrag.

[Byteidentisches ZIP, ausgepackte Originaldateien und Eingangsmetadaten](https://github.com/ibenarb/conway99-research/tree/6d5004ce0669930ea858f04f0d4c64a01c1a6f7c/docs/reviews/20260927_lambda_radius), eigener Zweig `reviews/20260927-lambda-radius`.

**Das ZIP enthält einen Prüfsatz, aber keinen ausformulierten strategischen Review mit einer priorisierten Fortsetzungsempfehlung.** `README.md` beschreibt Ergebnisse und Grenzen; `REVIEWPROMPT_gelesen.md` ist unser Auftrag. Es wäre falsch, dem Reviewer einen bestimmten nächsten Versuch oder eine Empfehlung zur Pause zuzuschreiben. Der folgende Abgleich betrifft seine tatsächlich gelieferten Befunde. Der Versuchsplan ist unsere eigene Ableitung und kann durch einen nachgereichten Reviewtext geändert werden.

## Abgleich und eigene Prüfungen

Die kleinen Kontrollen liefen über `tools/memetik/audit_python.py` mit isoliertem pynauty 2.8.8.1. `audit_review.py` und `audit/` enthalten die reproduzierbare Prüfung. Originale wurden nicht verändert; bei Ausführung zweier Reviewerskripte wurde ausschließlich der lokale Importpfad im Arbeitsspeicher ersetzt.

| Aussage | Eigener aktueller Prüfstand | Bedeutung |
| --- | --- | --- |
| Drei Startgraphen samt fünf Scores, λ, Histogrammen, Vierkreisen und state-Hashes | Mit eigenem Mengen-Scorer nachgerechnet; graph6-Decodierung aus Projektcode | Bestätigt bisherige Werte; kein neuer Rekord |
| 56 bzw. 60 λ-erhaltende 2-Switches, genau die Pivot-Züge | Reviewer-Bruteforce erneut ausgeführt; beide Mengendifferenzen null | Vollständigkeit dieser Zugart an genau zwei Wurzeln, kein globaler Vollständigkeitsbeweis |
| 43 bzw. 35 cycle3-Züge, kein besseres (W,L1) | Census mit eingefrorenem Katalog erneut ausgeführt | Kein unmittelbarer Ausweg mit einem solchen Zug; längere Wege bleiben offen |
| Tiefe 3: 526476/459185 Übergänge; 195508/169048 neue Zustände, keine Verbesserung | Neue externe Nachzählung stimmt mit Ryzen überein; JSON, Logs und Histogrammsummen hier geprüft | Verstärkt den Tiefe-3-Befund; in dieser Runde nicht erneut vollständig von uns enumeriert |
| Tiefe 4 vollständig negativ | Unveränderter Ryzen-Befund und früherer Metadatenaudit | Auch der neue Reviewer hat Tiefe 4 nicht unabhängig voll reproduziert |
| F/O: 76,89 % / 79,24 % exakte Rückkehr zum jeweiligen Elternzustand | Aus allen 16 fixierten Originalresultaten neu aggregiert | Reale deskriptive Rückkehrhäufigkeit; keine Erfolgswahrscheinlichkeit künftiger Rekordstarts |

Residuenhistogramme des neuen Prüfsatzes zählen alle 4851 ungeordneten Paare, unsere frühere Tabelle nur die 4158 Nichtkanten. Deshalb sind seine Nullzähler jeweils um 693 größer. Das ist kein Widerspruch.

Weitere Präzisierungen:

- Die Tiefe-3-Nachzählung verwendet erneut den Projektkatalog und Projektscorer. Eigener Enumerationsablauf und unabhängige Score-Stichprobe sind nützlich, ersetzen aber keinen unabhängigen Operator. Die Zustandsdeduplikation verwendet blake2b-128 statt vollständiger Bytevergleiche; der Reviewer benennt diese Annahme korrekt. Checkpoints und Zustandslisten sind nicht beigefügt.
- Die 400 Score-Stichproben je Arm stammen aus Übergangsindizes 1 bis 449999. Sie erfassen nicht den gesamten Strom: die letzten 76477 bzw. 9186 Übergänge sind von dieser unabhängigen Stichprobe ausgeschlossen. Die vollständige Enumeration selbst ist davon nicht betroffen. Die Stichprobe ist keine unabhängige λ-Prüfung aller Kinder.
- `best_child_WL1` in den Tiefe-3-Dateien umfasst auch rückwärts erreichte Zustände niedrigerer Distanz. Die Minima der **exakten** Schicht 3 stehen in `best5_WL1_depth3`: (2082,2498) und (2085,2450). Die unterschiedlichen Werte sind deshalb konsistent.
- Die Root-Prüfung von 2-Switches behauptet nichts über alle 3-/4-Switches. Auch die cycle3-Zählung ist keine Vollständigkeitsprüfung aller möglichen λ-erhaltenden Trades.
- Die neue Einreichung stärkt unsere frühere Aussage zur lokalen Reichweite. Sie widerlegt weder unsere Pause des unveränderten Hauptlaufs noch begründet sie die endgültige Aufgabe des λ-Zweigs.

## Was die Rückkehrquoten aussagen — und was fehlt

| Kampagne | Abgeschlossene Episoden | Exakte Rückkehr | Länge 2–4 | Länge 5–32 | Mindestens Rückkehr unter Länge 5–32 |
| --- | ---: | ---: | ---: | ---: | ---: |
| F | 19597 | 15068 | 8677 | 10920 | 6391 = 58,53 % |
| O | 33477 | 26527 | 15140 | 18337 | 11387 = 62,10 % |

Die letzte Spalte folgt ohne statistische Annahme aus
`R_lang >= max(0, R_gesamt − N_kurz)`.
Selbst wenn jede kurze Episode zurückgekehrt wäre, bliebe eine hohe Rückkehrquote unter den längeren Episoden. Ein bloßes Streichen kurzer Perturbationen ist damit **keine bereits belegte Verbesserung**.

Die Endklassen-Rückkehrzahlen stimmen hier mit den exakten Rückkehrzahlen überein. Sämtliche gezählten Episoden endeten laut Protokoll in `LOCAL_MIN_EXACT_AP`. Die Daten sind Randhistogramme; die gemeinsame Zuordnung von Start, Längenklasse, Rückkehr, Qualitätsgewinn und Episodenkosten fehlt. Daher lässt sich weder ein Vorteil längerer Perturbationen noch „79 % der CPU-Zeit verschwendet“ daraus ableiten. Die Episodenzahl ist kein Zeitanteil. Die historische Population änderte sich adaptiv; Episoden sind keine unabhängigen gleichverteilten Versuche an unseren zwei heutigen Starts.

Der Endpunktlogger in `lambda_compare_0_2_0/worker.py` und die deduplizierte Grapharchivierung liefern keine vollständige solche Episodentabelle. Ohne konkreten weiteren Datenhinweis wäre eine pauschale Anforderung der großen alten SQLite-Archive dafür nicht gerechtfertigt.

Außerdem bedeutet Radius 4 nicht, dass Perturbationslängen 2–4 unter P niemals Erfolg bringen können: Auf die Perturbation folgt ein Abstieg, dessen Pfadlänge zusätzlich zählt. Ein kurzer Stoß kann den Eintritt in einen langen, anders verlaufenden Abstieg ermöglichen. Das wäre mit dem Radiusbefund vereinbar.

## Wahl des nächsten Schritts

| Option | Bewertung |
| --- | --- |
| Vollständige Tiefe 5 oder erneute Tiefe-4-Reproduktion | Beantwortet eine engere lokale bzw. Absicherungsfrage, aber erklärt den Rückkehrmechanismus nicht. Kein aktueller Widerspruch erzwingt diesen Aufwand; Radiuswachstum und Kosten von Tiefe 5 sind offen. Zurückgestellt. |
| Neuer Operator oder F-/Pareto-Suche | Mathematisch möglich. Die Root-Censuses und frühere PCesc-Ergebnisse liefern bislang keinen belastbaren Vorteil. Würde eine weitere Methodenfrage öffnen. Zurückgestellt. |
| Vergleich der Perturbationslängen bei festem Start und gleicher lokaler Verbesserung | Untersucht unmittelbar die neue offene Frage nach Rückkehr, nutzbaren Endpunkten und CPU-Kosten, bei nur einem variierten Suchbestandteil. **Priorität.** |

Die 12 CPU-h sind eine bewusst begrenzte Informationsinvestition, keine aus den Histogrammen hergeleitete notwendige Stichprobengröße. Es besteht keine Zusage eines neuen Rekords. Ein automatisches Fortsetzen der früheren 16er-Populationen folgt daraus nicht.

## Konkretes Protokoll: fester Start, variable Längenverteilung

**Frage:** Erzeugen längere P-Perturbationen an den beiden heutigen Starts bei gleichem CPU-Budget häufiger strikt bessere Endpunkte, oder tauschen sie Rückkehr lediglich gegen teurere und schlechtere lokale Minima?

**Starts:** Genau die Graphen aus `STARTS.json` des Radiuspakets bei Commit `8ec085cdb8402a6e33dc186ae0302fea4dd542ec`:

- W2076/L1=2488, state `8169eba8e1f2bf78eb655d99b94844a1eb5056df828e8c610a3778d537a7d0fe`.
- W2077/L1=2436, state `136bad89e063ba84bbc4201cfa5be21db6d511852602ad861a4d2c0e0ef8e49c`.

Jede Episode beginnt erneut am fixierten Start. Ergebnisse werden archiviert, aber nicht als neue Eltern übernommen. Startpopulation je Job also ein Graph. Beide Starts bilden getrennte Auswertungsgruppen; der Vergleich gilt nicht für Gründerfamilien im Allgemeinen.

| Arm | Gewichte für Längen 2–4 / 5–12 / 13–32 | Zweck |
| --- | --- | --- |
| A | 4:3:2 | Kontrollarm mit ursprünglicher P-Längenverteilung |
| B | 0:3:2 | Effekt des Weglassens der kurzen Längen |
| C | 0:0:1 | Nur lange Perturbationen als zusätzlicher Vergleich |

Innerhalb des ausgewählten Intervalls wird die Länge gleichverteilt gezogen. Apex/Pivot-Katalog, Zugauswahl während der Perturbation, unveränderte Zulässigkeit aller Zwischenzustände, exakter steilster Abstieg nach (W,L1), Katalogreihenfolge und Gleichstandsbehandlung bleiben wie im eingefrorenen P. Keine Vermeidung von Rückzügen, keine neue Taburegel, kein cycle3, kein Crossover und keine Migration. Der Kontrollarm ist **P-Episoden unter festem Start**, nicht eine Reproduktion der adaptiven P-Gesamtkampagne.

**Replikate und Zufall:** Vier feste Seed-Blöcke pro Start und Arm, Blocknummern 2026092701 bis 2026092704; insgesamt 2 × 3 × 4 = 24 Jobs. Ableitung des jeweiligen Zufallsstroms vorab deterministisch aus SHA256 von `lambda-length-v1|state|arm|block`, als unsigned Big-Endian-Integer. Gleiche Blocknummer bedeutet einen Organisationsblock, keine Behauptung identischer Zufallspfade oder gepaarter Einzelereignisse. Jobreihenfolge und Slotzuweisung vorab festlegen und über die Arme mischen. Seeds werden nach Ergebnissen nicht ausgetauscht.

**Budget:** Je Job 1800 verbuchte CPU-Sekunden einschließlich Bewertung, Kanonisierung und Episodenprotokollierung; 4 CPU-h je Arm, insgesamt 12 CPU-h. Vorbereitung, Kontrollen und kurze Durchsatzkalibrierung höchstens 1 CPU-h extra. Keine Budgetübertragung. Eine bei Budgetende unvollständige Episode wird checkpointiert und als zensiert ausgewiesen; ihre CPU bleibt vollständig verbucht. Sie zählt nicht als abgeschlossene Rückkehr oder abgeschlossener Endpunkt. Zusätzlich alle bereits besuchten gültigen Verbesserungen separat protokollieren.

**Ressourcen/Zeit:** Höchstens 12 Worker, nur tatsächlich verfügbare Ryzen-Kapazität, keine Beeinträchtigung anderer laufender Projekte. Gesamtrahmen 8 GiB RAM und 10 GiB Ausgaben; Pause unter 6 GiB verfügbarem RAM oder 25 GiB freiem Linux-/Windows-Speicher. Idealuntergrenze etwa eine Stunde Such-Walltime bei 12 voll ausgelasteten Kernen; Planung 1,5–3 Stunden einschließlich Kontrollen, abhängig von Belegung und Durchsatz. Harte Gesamtgrenze 4 Windows-Host-Stunden, bei weniger freien Ressourcen entsprechend weniger abgeschlossene Jobs statt Überschreitung. CPU per wait4, Zeit per Windows-Host-Monotonzeit, Status alle zehn Minuten mit ETA.

**Kontrollen vor Start:** Beide Eingaben unabhängig voll bewerten; Katalogquellhashes fixieren; bekannten Vier-Zug-Zeugen replayen; bei festen RNG-Zuständen Übereinstimmung von A mit den bisherigen einzelnen P-Episoden kontrollieren. Vorhandene Radiusartefakte nur lesen. Protokollierung, Pause/Fortsetzung und CPU-Buchung prüfen. Kein erneuter Radius-4-Lauf als Vorbedingung.

**Messungen pro Episode:** Start-state/-Klasse; Seed/Arm/Block; Soll-/Ist-Perturbationslänge; Abstiegslänge; CPU getrennt nach Perturbation/Abstieg samt Gesamtkosten; exakte und isomorphe Rückkehr; Endgraph/Graph6, fünf Scores und Klasse; Stopgrund; maximale zwischenzeitliche W/L1/F-Werte; replayfähige Zugfolge für jede Verbesserung. Für Vergleich und Archiv zusätzlich gleiche absolute CPU-Messpunkte 300/600/900/1200/1500/1800 Sekunden je Job. Alle vollständigen Endpunkte unabhängig voll bewerten, Klassen mit gepinntem nauty bestimmen; Prüfaufwand innerhalb des vereinbarten Budgets verbuchen.

**Auswertung:** Pro Start und Arm zuerst Anzahl der Replikate mit strikt (W,L1)-besserem vollständigem Endpunkt sowie Zeit zum ersten Treffer; daneben Klassen solcher Endpunkte je verbuchter CPU-h. Exakte/isomorphe Rückkehr nach tatsächlicher Länge und deren CPU-Anteil, Durchsatz, Endpunktqualitäten, neue Klassen und zensierte Episoden getrennt berichten. Ein Replikat zählt als Replikat; tausende Episoden werden nicht als tausende unabhängige Kampagnen behandelt. Keine Signifikanz- oder allgemeine Überlegenheitsbehauptung aus vier Blöcken.

## Vorab festgelegte Entscheidungen

1. **Globaler Erfolg:** Jeder unabhängig replay-geprüfte Graph mit W<2076 ist ein neuer globaler W-Rekord. Er wird gesichert; die übrigen Jobs laufen grundsätzlich bis zu ihren festen Budgets weiter, damit die Vergleichsbasis erhalten bleibt. Nur eine bestätigte SRG-Lösung beendet die Untersuchung vorzeitig als gelöst.
2. **Lokaler Erfolg:** Besseres (W,L1) relativ zum jeweiligen Start beantwortet die lokale Fluchtfrage positiv, auch ohne globalen W-Rekord. Vollständige Endpunkte und zensierte Zwischenzustände werden nicht vermischt. Jeder Treffer löst eine Pfadprüfung aus, nicht automatisch eine Kampagne.
3. **Kandidat für einen späteren Bestätigungstest:** B oder C erreicht bei demselben Start in mindestens zwei von vier vollständigen Replikaten bessere Endpunkte, insgesamt mehr erfolgreiche Replikate als A und einen mindestens ebenso guten besten (W,L1)-Endpunkt. Diese Schwelle ist eine vorab gewählte Pilotregel, kein statistischer Wirksamkeitsnachweis. Eine Wiederholung derselben Klasse zählt zur Reproduzierbarkeit des Treffers, nicht als Vielfalt. Erfüllen beide die Regel, entscheidet zunächst Anzahl erfolgreicher Replikate, dann bestes (W,L1), dann Klassen besserer Endpunkte; bei vollständigem Gleichstand B als kleinere Änderung. Ein Folgeversuch bedarf eines neuen Plans.
4. **Kein Qualitätsgewinn:** Kein lokaler Treffer in irgendeinem Arm nach vollständigen Budgets führt zur Pause weiterer W-Frontier-Läufe. Eine niedrigere Rückkehrquote oder mehr schlechtere Klassen allein rechtfertigt keinen Hauptlauf. Auch ein Einzelhit oder Gleichstand gegenüber A rechtfertigt keinen behaupteten Längenvorteil; Ergebnis sichern, Pfad analysieren und neu entscheiden. Verbesserungen nur unter A sprechen gegen das sofortige Ersetzen seiner Verteilung, nicht automatisch für einen großen A-Lauf.
5. **Unvollständigkeit:** Sicherheitsgrenze, Hostgrenze oder Kontrollfehler ergeben `INCOMPLETE` bzw. `CONTROL_FAILURE`, keinen negativen Methodenbefund. Score-/λ-/Replay-/Buchungswiderspruch stoppt die eigenen Jobs; fremde Prozesse bleiben unberührt. Keine automatische Budgetverlängerung.

Die Untersuchung ist bewusst eine Diagnose der Episode unter festen Starts. Selbst ein positives Ergebnis muss anschließend unter Population und Selektion bestätigt werden, bevor es einen memetischen Hauptlauf begründet. Wird kein nutzbarer Fortschritt erzielt, bleiben Starts, Paretopunkte und Protokolle erhalten; Wiederaufnahme erst mit überprüfbarem neuen Operator, konstruktivem Hinweis oder einer konkret anderen Hypothese.

## Reproduktion und Grenzen dieser Bearbeitung

Aus dem Repository über den Audit-Helfer `audit_review.py` mit Original-ZIP und neuem Ausgabeverzeichnis aufrufen. Der Prüfer verifiziert Hashes, Scores, zwei Root-Censuses, Episodensummen und die innere Konsistenz der gelieferten Tiefe-3-Dateien. Er programmiert oder startet keinen neuen Kampagnenlauf. Die langen Tiefe-3/4-Rechnungen wurden hier nicht wiederholt. Der strategische Reviewtext bleibt fehlend; nach Eingang ist ein echter Empfehlungsvergleich nachzuholen.

Ein erster lesender Shellaufruf verwendete für eine ausgepackte Datei den falschen relativen Pfad und brach vor den nachfolgenden Git-Befehlen ab. Der korrigierte Aufruf und alle eigentlichen Prüfungen waren erfolgreich. Keine Forschungsdaten wurden dadurch geändert.
