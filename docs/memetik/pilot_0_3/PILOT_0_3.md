# Pilot 0.3: Population, Mutationen und Metriken

Stand: 13. September 2026. Spezifikation zur Diskussion; noch nicht implementiert oder gestartet.
Grundlage: [Befunde](BEFUNDE.md), [Analyse](ANALYSE.md), [Schlussfolgerungen](SCHLUSSFOLGERUNGEN.md).

## Grundpopulation

Ziel: 64 verschiedene Graphen, 32 je Arm. Jeder dieser Graphen startet in L1, L2² und verfeinertem Linf, also 192 normgebundene Plätze. Das sind keine 192 unabhängigen Gründer.

| Herkunft je Arm | Plätze | Zweck |
| --- | ---: | --- |
| Fünf ursprüngliche Gründer unverändert | 5 | Historische Kontrollen; insbesondere ursprünglicher B bleibt erhalten |
| Ausgewählte verschiedene Endgraphen des abgeschlossenen Piloten | 11 | Erreichten Fortschritt übernehmen |
| Frisch konstruierte gültige Graphen | 16 | Andere Strukturangebote erschließen |
| Summe je Arm | 32 | Feste Populationsgröße |

Im λ-Endbestand ist der Linf=2-Zeuge verpflichtend. In Ω werden die drei normabhängigen B-Endgraphen aufgenommen, soweit nichtisomorph; übrige Endplätze nach Qualität und unterschiedlichen Residuen-/Defektprofilen, nicht nur global nach F.

Für die 16 frischen Plätze je Arm ist das erste Projektziel fünf zusätzliche Gründerkonstruktionen je Arm, zehn insgesamt. Aus deren Generatoren dürfen mehrere Kandidaten kommen. Die Zahl 16 bezeichnet Graphen, nicht 16 unabhängige Prinzipien. Insgesamt mindestens vier begründet verschiedene Konstruktionsprinzipien anstreben. Verschiedene KI-Namen oder Seeds sind keine unabhängigen Prinzipien.

Frische Kandidaten werden nicht durch bloße Umnummerierung oder kurze Trades der alten Gründer ersetzt. Wenn nicht genügend gültige verschiedene Graphen vorliegen, kleinere tatsächliche Population ausweisen und die passende Kontrollpopulation gleich groß wählen. Alle 64 Startgraphen müssen für alle drei Normen identisch sein; keine nachträgliche Auswahl verschiedener Starter je Norm.

Harte Bedingungen: 99 Knoten, einfach, Grad 14. λ zusätzlich genau ein gemeinsamer Nachbar pro Kante. Ω kanonischer Rahmen, H-Grad 12 und exakte P-Margen, ohne pauschal global λ=1 zu unterstellen. Keine neue Symmetrievorgabe. [Gründervertrag](../GRUENDERVERTRAG.md) bleibt maßgeblich.

## Mutationen

Zunächst dieselben acht Versuchstypen je Elternrunde wie in 0.2 beibehalten, um die technische Änderung vergleichbar zu machen:

| Typ | Versuche je Elter | Geplante Störlänge |
| --- | ---: | --- |
| Kurzer zufälliger Ausflug | 3 | 2–4 zulässige Züge |
| Mittlerer zufälliger Ausflug | 2 | 5–12 |
| Längerer zufälliger Ausflug | 1 | 13–32 |
| Zum zweiten Elternteil geführter Ausflug | 1 | 8–16 |
| Ω: Cross-over; λ: weiterer geführter Ausflug | 1 | Cross-over separat; λ 8–16 |

Ein Versuch ist eine Störung plus anschließende lokale Verbesserung. Schlechtere Zwischenstände sind erlaubt; Übernahme nur bei Verbesserung im aktiven Kriterium oder bei Gleichstand und zulässiger Strukturneuheit. Bestes geeignetes besuchtes Ergebnis sichern, Originalelter und seine Umnummerierungen nicht als Erfolg zählen. Keine globale Verdrängung aller schwächeren Herkunftsgruppen.

λ verwendet die vorhandenen validierten Apex-/Rotationsoperatoren. Ω zunächst die vorhandenen validierten gekoppelten Trades mit effizienterer Erzeugung. Ein einfacher alternierender Zyklus wird nicht allein wegen Gradtreue als gültig angenommen. Neue größere Fensterreparaturen erst in einer gesonderten Operatorprobe vergleichen.

Technische Änderungen: statische Trägerkataloge vorberechnen; Kandidaten pro Zustand nicht für jede Auswahl erneut von vorn erzeugen; nach Mutation nur korrekt aktualisierte oder neu geprüfte Gültigkeit verwenden. Kosten von Erzeugung, Bewertung und Kanonisierung getrennt messen.

Vorläufiger großzügiger Versuchsrahmen zur Kalibrierung: bis 120 CPU-Sekunden für Störung bzw. Cross-over, danach bis 60 weitere CPU-Sekunden für Abstieg. Der Abstieg beginnt also nicht mit einem bereits verbrauchten Budget. Die Zahlen sind Versuchseinstellungen, keine Leistungszusage. Eine nicht vollendete Störung erhält einen eigenen Status; etwaiger anschließender Abstieg wird separat als verkürzter Versuch ausgewertet. Das alte gemeinsame 256-Bewertungslimit darf die neue Trennung nicht unbemerkt wieder aufheben; separate Auswertungskontingente nach Kalibrierung.

Der vollständige Fehlervektor wird beim akzeptierten Graphen unabhängig geprüft. Ein Archiv erhält die besten Graphen nach W, L1, F und Linf, auch wenn sie in ihrer Population nicht mehr vertreten sind. Für Zwischenschritte reichen kompakte Zähler und ausgewählte Fluchtzeugen; nicht jede schlechte Matrix wird gespeichert.

## Metriken

Für alle 4851 ungeordneten Paare gilt r_ij=(A²)_ij+A_ij−2.

| Größe | Rolle |
| --- | --- |
| W = Anzahl r≠0 | Vollständige Treffer-/Fehlerzahl; Archivrekord, vorerst kein vierter Selektionsarm |
| L1 = Summe der Fehlerbeträge | Erste aktive Zielfunktion |
| F=L2² = Summe r² | Zweite aktive Zielfunktion |
| (Linf, Nmax, L1) lexikographisch | Dritte aktive Zielfunktion; Nmax zählt Fehler mit maximalem Betrag |
| Residuenhistogramm, sortierte Defektgrade | Fehlerkonzentration und strukturelle Unterschiede |
| Kanonische Klassen, Herkunftsbelegung | Identität und Erhalt der Vielfalt |
| Tatsächliche Stör-/Abstiegslängen | Was wirklich ausgeführt wurde |
| CPU je gültigem Kind und je Verbesserung | Vergleich der Suchleistung |
| Rückkehr, neutral neu, strikt besser, bereits bekannte andere Klasse | Unterschiedliche Versuchsausgänge |

Scores einer Tabellenzeile können unabhängige Minima verschiedener Graphen sein. Jeder besondere Fund wird zusätzlich mit vollständigem Kennzahlentupel und Graphhash berichtet.

Bei der Aufnahme frischer Graphen mehrere standardisierte Abstiegsproben ausführen, um häufige Rückkehr zu denselben Endgraphen zu erkennen. Diese Diagnose ist kein Beweis von Plateauidentität und darf neue Familien nicht automatisch allein aufgrund eines einzelnen Abstiegs verwerfen.

## Ablauf und fairer Vergleich

A. Technische Kalibrierung auf festem kleinem Elternsatz: Ω mindestens A, ursprünglicher B und ein B-Endgraph; λ HoG 57338, Linf=2-Zeuge und ein weiterer HoG-Gründer. Alter und verbesserter Operator mit denselben Eltern und festen Seeds. Gleiche CPU-Kontingente; vollständige Störung separat von abgebrochener zählen. Ziel: mehr tatsächlich abgeschlossene Störung-plus-Abstieg-Versuche je CPU, nicht nur größere nominelle Budgets.

B. Erst danach Populationspilot. Gleicher verbesserter Operator auf historischem und erneuertem Startbestand, gleiche Populationsgrößen und CPU-Kontingente; mehrere Seeds. Ein Unterschied in Startqualität muss berichtet werden und verhindert gegebenenfalls die isolierte Zuschreibung zur Vielfalt. Umfang anhand der Kalibrierung so wählen, dass jede Linie wiederholt bearbeitet wird.

C. Orientierungsrahmen für die neue Office-Kampagne: drei Worker, nominell 48 Stunden Gesamtbetrieb, also höchstens ungefähr 144 Worker-CPU-Stunden bei voller Auslastung. Zuteilung gleichmäßig auf sechs Norm×Arm-Gruppen, bei einer einzelnen Population rechnerisch 24 CPU-Stunden je Gruppe. Bei zwei Populationsvarianten teilt sich dieses Kontingent nochmals. Vor Start entscheiden anhand des Durchsatzes, ob längere Laufzeit oder eine kleinere kontrollierte Stichprobe erforderlich ist.

Eine vollständige Runde bei 64 Graphen × 3 Normen × 8 Versuchen hat 1536 Versuche. Bei maximal 180 CPU-Sekunden pro Versuch wären das 76,8 CPU-Stunden. Deshalb sind in 48 Stunden keine zehn Generationen zugesagt. Es wäre falsch, großzügigere Einzelbudgets zu wählen und trotzdem unverändert hohe Generationenzahlen zu versprechen. Vor Auslieferung werden gemessener Durchsatz und erwartete Rundenzahl mitgeteilt.

Status alle zehn Minuten: jeweilige CPU-Kontingente, abgeschlossene Versuche/Runden, Bestwerte, tatsächliche Zuglängen und ETA zum endlichen Budget. Atomare Checkpoints und Wiederaufnahme. Bereits bekannte funktionierende Kontrollen nur für betroffene Änderungen wiederholen. Keine Änderungen an Ryzen-Ausschlussläufen.

## Offene Entscheidungen

Die 120/60-Sekunden-Aufteilung und 48-Stunden-Planung sind vorläufige Kalibrierungswerte. Noch nicht nachgewiesen: schneller neuer Ω-Generator, ausreichend viele frische Gründer, Vorteil einer größeren Strukturvielfalt, minimale Fluchtlänge. Die Population und die drei Normvarianten sind der konkrete Zielentwurf; eine neue Implementierung wurde mit dieser Dokumentation nicht behauptet.
