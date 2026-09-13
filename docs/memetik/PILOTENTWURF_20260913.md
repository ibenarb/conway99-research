# Memetik: Bewertung und neuer Pilot

Stand: 13. September 2026. Status: Forschungsentwurf mit ausgeführtem Gründeraudit; keine neue Kampagne gestartet.

## 1. Entscheidung

Beide Ideen von Ralph Beckmann werden aufgenommen: gezielt neue Ausgangsstrukturen und systematische Untersuchung lokaler Fluchtwege. Sie werden zunächst getrennt gemessen, damit ein Erfolg einer veränderten Mutation nicht irrtümlich der Startvielfalt zugeschrieben wird.

Die interne Gegenprüfung erfolgte durch zwei getrennte Analyseaufträge zu Diversität und Plateauwechsel; die folgenden Abwägungen sind unsere Synthese, kein neues externes Reviewer-Pong.

## 2. Welche vorhandene Evidenz maßgeblich ist

Fester Quellenstand: `31c563f6ba460227c6ae4eebcd519257fcba5ad4`.

- `docs/memetic/reference/Conway99_Pong_Runde3_20260910.md`: Rückwegfalle, Drift, Bestpunktübernahme und Diversität.
- `docs/memetic/reference/Conway99_Stand_und_Implementierungsplan_0_1_20260910.md`: korrigierte Auswertung; vollständige beschriftete HoG-Nachbarschaft bis Tiefe zwei; eingeschränkte Reichweite mehrerer Reviewer-Aussagen.
- `docs/memetic_v2/OFFICE_0.2.0.md`: 64 nichtisomorphe Starter aus zehn Gründern, 54 davon durch gründernah ausgeführte Trades; drei getrennte Zielfunktionsvarianten.
- `docs/review_synthesis_20260912/FINALES_RESUEMEE.md`, Abschnitt 6: Mutationserzeugung als gemessener Engpass; Cross-over hängt von relativer Ausrichtung ab; Kerndimension allein garantiert kein echtes Kind.
- `results/research_20260912/memetic_scoring.json`: B besitzt unter fünf dort geprüften Ω-Änderungen zwei L2²-Verbesserungen. B ist deshalb nicht bereits als L2²-Minimum dieser Zugfamilie zu behandeln.

Ein abschließender archivierter Bericht des jüngsten produktiven Office-Laufs ist in den für diesen Auftrag gelesenen Forschungsständen nicht enthalten. Die sichtbare frühere CSV-Stichprobe bei Generation 10 ersetzt keinen Abschlussbericht. Vor einer tatsächlichen Neuauslieferung werden dessen letzter Checkpoint, Konfiguration und vollständige Auswertung übernommen. Hier wird kein Live-Zustand der Nutzerrechner behauptet.

## 3. Kandidat B: weniger falsche Paare, stärkere Einzelverletzungen

Die archivierten Graphbytes wurden erneut eingelesen und die Scores mit unabhängig implementierten Mengenintersektionen berechnet. Die Dateibytes stimmen mit den Git-Blob-IDs überein. Prüfer: `src/memetik/audit_founders.py`; Ergebnis: `results/memetik/founder_audit_20260913.json`.

| Graph | W | L1 | L2² | Linf | Kanten mit λ-Verletzung |
| --- | ---: | ---: | ---: | ---: | ---: |
| B Maple 29.08.2026 | 2110 | 3512 | 9716 | 10 | 460 |
| HoG 57338 | 2182 | 2398 | 2836 | 3 | 0 |

Alle Scores beziehen sich auf sämtliche 4851 ungeordneten Paare. Beide Graphen sind einfach und 14-regulär. B erfüllt den kanonischen Ω-Rahmen und alle P-Margen. Seine 42 Residuen +10 tragen allein 4200 zur Quadratsumme 9716 bei. Das ist ein konkretes Motiv für gezielte Reparatur hoher Fehlerkonzentration, kein Nachweis einer kurzen Reparatur.

W misst die Zahl falscher Paarbedingungen, nicht die Anzahl notwendiger Kantenänderungen. Ein einziger Trade verändert viele Paarbedingungen; diese sind gekoppelt. B bleibt als strukturell und im Fehlerprofil anderer Gründer wertvoll. Der Vorsprung in W beweist keinen geringeren Reparaturabstand.

**Korrektur einer älteren Formulierung:** Abschnitt 7.1 von `docs/research_20260912/BERICHT.md` bezeichnet Ω missverständlich als λ mit zusätzlichen Rahmenbedingungen. Der tatsächlich implementierte Ω-Vertrag erzwingt λ nicht auf allen Außenkanten. B ist ein expliziter Gegenbeleg. Der neue Pilot behält die bestehenden, unterschiedlichen Armverträge bei; B wird nicht durch nachträgliches Verschärfen seiner Zulässigkeit ausgeschlossen. Die ursprünglichen Dokumente und produktiven Programme werden in diesem Commit nicht umgeschrieben.

Ein zunächst versuchter lokaler Import von NetworkX scheiterte wegen fehlender Installation. Danach wurden die Werte einmal mit eigener graph6-Dekodierung und NumPy, anschließend mit dem gespeicherten unabhängigen Standardbibliothek-Prüfer erfolgreich berechnet. Kein Suchresultat wird aus dem gescheiterten Aufruf abgeleitet.

## 4. Streitfrage Ausgangsvielfalt

**Argument dafür:** Kurze Trades um bekannte Gründer können einen stark konzentrierten Bestand liefern, selbst bei 64 nichtisomorphen Graphen. Andere Konstruktionsprinzipien können bislang unerreichte Regionen erschließen. Das wurde durch den bisherigen Aufbau nicht widerlegt.

**Einwand:** Zehn KI-Ausgaben sind keine zehn unabhängigen Konstruktionen. Modelle können dieselben Quellen, Symmetrien oder Reparaturziele verwenden. Schlechtere Ausgangsqualität kann den Nutzen von Vielfalt verdecken; ein besserer Ausgangsgraph kann ihn vortäuschen.

**Synthese:** Zunächst zehn zusätzliche Gründer insgesamt anstreben, möglichst fünf je Arm, aus mindestens vier dokumentierten Prinzipien. Methodenfamilien statt Modellnamen sind die Herkunftseinheiten. Dazu gehören als zu prüfende Möglichkeiten randomisierte exakte Konstruktion, Reparatur unabhängiger Rohstarts, algebraische Konstruktion mit anschließendem Symmetriebrechen und gezielte Konstruktion unter abweichenden Strukturdeskriptoren. Die Machbarkeit und Neuheit jeder Methode müssen tatsächlich gezeigt werden.

Der separate [Gründervertrag](GRUENDERVERTRAG.md) gibt Minimalbedingungen und Lieferformat vor. Bereits vorhandene zulässige Starts bleiben Kontrollen. Keine allgemeine Behauptung, Vielfalt sei immer besser: Bei festem Budget kann zu große Population die Verbesserung jeder Linie aushungern.

Ein neuer kanonischer Graph ist eine neue Strukturklasse. Ein neues Abstiegsziel ist eine Beobachtung unter einem bestimmten Algorithmus. Ein neues Plateau verlangt eine Aussage über neutrale Erreichbarkeit in einem festgelegten Zuggraphen. Diese Ebenen bleiben getrennt.

## 5. Streitfrage minimale Zykluslänge

Für einen festen zulässigen Raum S, eine reversible Zugfamilie M und eine Zielfunktion F unterscheiden wir:

| Messung | Bedeutung |
| --- | --- |
| Einzelzykluslänge 2k | Ein einfacher alternierender Kreis mit k entfernten und k ergänzten Kanten |
| Trägergröße | Zahl betroffener Knoten und Zahl geänderter ungerichteter Paare eines allgemeinen Trades |
| Zugdistanz | Kleinste Zahl von M-Zügen bis zu einem ausdrücklich definierten Ziel |
| Barrierenhöhe | Kleinster maximaler Anstieg von F über F(Start) auf einem Weg zu diesem Ziel |
| Kicklänge | Zahl Störzüge vor einem festgelegten anschließenden Abstieg |

Ein Wechsel zu einem anderen gleich guten lokalen Endpunkt und das Erreichen irgendeines besseren Graphen sind zwei verschiedene Zielmengen. Ein Plateau ist hier eine Zusammenhangskomponente neutraler M-Züge. Eine begrenzte erfolglose Abstiegsprobe zertifiziert weder ein Minimum noch ein Plateau.

Alternierende Kreise erhalten Grade, aber nicht automatisch λ oder P-Margen. Allgemeine gültige gekoppelte Trades müssen nicht einzelne einfache Kreise sein. Insbesondere entfernt der bekannte minimale Ω-Produkttausch acht Kanten und fügt acht hinzu: Er ist kein einzelner alternierender Achterkreis. Ein negativer Kreis-Zensus schließt allgemeinere gekoppelte Änderungen nicht aus.

**Vorhandene Untergrenze:** Für HoG 57338 ist F=2836, alle 46 Apex-Nachbarn haben F≥2856; die vollständige historische Zwei-Tausch-Untersuchung fand keinen neuen gleich guten oder besseren Zustand. Damit braucht ein solcher Endpunkt mindestens drei Apex-Züge. HoG ist bezüglich dieser Nachbarschaft ein striktes lokales Minimum. Es ist nicht gezeigt, dass drei genügen. Die Aussage ist kein Mindestwert einer einzelnen Zykluslänge und gilt nicht automatisch für Ω oder größere Trades.

**Argument dafür:** Vollständige kleine Schichten liefern belastbare lokale Schranken und konkrete Fluchtzeugen. Dies kann die Wahl von Störlängen erstmals empirisch begründen.

**Einwand:** Globale Minimalität kann einen sehr großen Teil des Suchraums verlangen. Die Rechnung an einem Gründer könnte dessen Sonderstruktur statt eines allgemeinen Suchmechanismus messen.

**Synthese:** Kleine Radien vollständig, größere Radien als klar bezeichnete begrenzte Exploration. Die erste unvollständige Schicht ist UNKNOWN. Gefundene Wege geben obere Schranken; nur abgeschlossene kleinere Schichten geben untere. Keine Beschneidung höherer Fehlerstände, wenn uneingeschränkte Zugdistanz behauptet werden soll. Mit Fehlerdeckel gilt der Schluss ausschließlich unter diesem Deckel.

Eine exakte lokale Enumeration muss einen vollständigen Generator verwenden; der begrenzte Zufallsstrom des produktiven Mutators genügt dafür nicht. Einfacher Start: beschriftete Matrixzustände deduplizieren. Isomorphiequotientierung ist nur mit nachgewiesener Äquivarianz der Zugfamilie und korrekter Berücksichtigung des Ω-Rahmens sicher. Tabu- oder Historienzustände gehören nötigenfalls zum Suchzustand; sie dürfen nicht stillschweigend in eine Minimumsbehauptung einfließen.

## 6. Konkreter Pilotvorschlag

### Stufe A: Bestand und Diagnose

B, HoG und Altgründer bleiben referenziert. Neuen produktiven Abschlussstand importieren und auswerten. Kandidatengeneratoren gemäß Gründervertrag bauen und Kandidaten unabhängig abnehmen. Kosten der Starterzeugung getrennt erfassen. Kein behauptetes Zeitfenster für die Erzeugung zehn neuer Familienvertreter vor einer Kalibrierung.

B zunächst unter den gewählten bestehenden Ω-Zügen absteigen lassen: mindestens zwei L2²-Verbesserungen sind bereits dokumentiert. Erst einen anschließend vollständig nachbarschaftsgeprüften Endpunkt als lokales Minimum verwenden. HoG ist der historische λ-Kontrollpunkt. Zusätzliche neue Gründer liefern Vergleichspunkte.

Die Ω- und λ-Experimente behalten ihre eigenen harten Bedingungen. Ein direkter gemeinsamer Zuggraph für B und HoG wird nicht unterstellt.

### Stufe B: Lokale Fluchtuntersuchung

- HoG: historische Schichten 1 und 2 gegen fixierte Eingaben reproduzieren; vollständige Schicht 3 als erstes neues Ziel.
- Ω: an einem abgestiegenen B-Nachfahren und weiteren Kontrollzuständen eine ausdrücklich benannte vollständige kleine Tradefamilie untersuchen.
- Unabhängig davon größere gekoppelte Reparaturen in begrenzten Fenstern als neuen Operator prüfen. Nur interne Kanten sind variabel; die volle Bewertung umfasst auch betroffene Paare zwischen Fenster und Außenbereich.
- Größere Kicks mit mehreren festen Seeds und identischem Abstieg testen. Erfolg: neuer geprüfter Endpunkt, strikte Verbesserung, Rückkehr oder Budgetende getrennt zählen.
- Keine neue Speicherung jeder schlechten Zwischenmatrix. Für Minimalitätsbelege nur notwendige Schichten-/Vorgängerinformation und ausgewählte Zeugen; sonst kompakte Taskzusammenfassungen, entsprechend der bisherigen Speicherpräferenz.

Vorab etwa 15–30 Minuten Kalibrierung der Enumeration auf der Zielmaschine. Zeit bis Schichtabschluss anschließend aus gemessener Frontier und Durchsatz schätzen. Falls eine Schicht zu groß wird, mit vollständigem Wiederaufnahmestand parken; der Pilotvergleich bleibt davon unabhängig.

### Stufe C: Kontrollierter Vergleich

Zwei Fragen über einen 2×2-Vergleich trennen:

| | Bestehende Störung plus Abstieg | Neuer anhand Stufe B bestimmter Operator |
| --- | --- | --- |
| Gründernaher Kontrollbestand | Baseline | Operatorwirkung |
| Strukturell breiter Bestand | Vielfaltwirkung | Zusammenspiel |

Je Arm getrennt auswerten. Vorgeschlagen: 20 Plätze pro Zelle, bei breitem Bestand fünf Gründer mit vier Plätzen, soweit der echte Bestand dies erlaubt; identische Populationgröße im Kontrollbestand. Qualität nach Möglichkeit innerhalb desselben Arms und derselben Norm angleichen. Wenn keine vergleichbare Qualitätsüberlappung existiert, als durch mehrere Einflussgrößen überlagerte Pilotbeobachtung melden, nicht als isolierten Diversitätsnachweis. Gleiche Auswahl, Rückwegsperre, Bestarchiv und CPU-Zuteilung in allen Zellen.

Drei vorab festgelegte Wiederholungsseeds. Pro Zelle und Seed zunächst eine CPU-Stunde. Für L2² allein sind das 2 Arme × 4 Zellen × 3 Seeds = 24 CPU-Stunden; dies ist eine vorgeschaltete Diagnose, keine Abschaffung der historischen Normvarianten. Vollständig mit L1 und verfeinertem Linf: 72 CPU-Stunden. Keine Migration zwischen Normen. Erst die drei objektivspezifischen Auswertungen zusammen begründen eine breite Empfehlung.

Planungsarithmetik auf dem Intel mit drei Workern: idealisiert acht Stunden für die L2²-Diagnose, 24 Stunden für alle drei Normen, jeweils zuzüglich Verwaltung, Starterzeugung, Enumeration und Unterauslastung. Keine Laufzeitgarantie; Ryzen-Budgets werden erst mit seiner tatsächlichen parallelen Belegung festgelegt.

Zwei Kostenperspektiven ausweisen: Verbesserungen bei gleichem Suchbudget und Gesamtnutzen einschließlich Starterzeugung. Die einmaligen Konstruktionskosten nicht durch beliebige nachträgliche Wiederverwendung rechnerisch verschwinden lassen. Vorhandene Norm- und Familienvarianten bleiben als historische Baseline reproduzierbar.

### Messgrößen und Entscheidung

Primär vollständiger Zielfunktionswert über tatsächlich verbrauchte CPU-Zeit; zusätzlich beste Werte aller vier Kennzahlen, Verbesserung pro CPU-Stunde, Zahl neuer kanonischer Klassen, Rückkehrquote, Kosten je legalem Kind, beobachtete Übergänge nach Kicklänge, Fehlerkonzentration und erhaltene Gründerfamilien. Drei Seeds liefern eine Orientierung, keine starke statistische Absicherung.

Ein einzelner Glückstreffer rechtfertigt keinen allgemeingültigen Algorithmusanspruch. Ein gültiger besserer Graph bleibt dennoch ein wertvolles Ergebnis. Für eine größere Kampagne soll sich ein Vorteil in wiederholten, vergleichbaren Läufen zeigen; sonst wird die konkrete Hypothese angepasst.

Alle Suchläufe: atomare Wiederaufnahme, vollständige Seeds/Versionen, Status alle zehn Minuten mit ETA zum aktuellen endlichen Budget beziehungsweise zur gemessenen Schicht, keine ETA zur Lösung. Vorhandene Nutzerprozesse werden nicht verändert. Experimentelle Budgets sind Vergleichsgrenzen, keine mathematischen Ausschlüsse und keine willkürlichen Abbrüche laufender Zertifizierung.

## 7. Fazit für die Forschungsentscheidung

Neue Konstruktionsvielfalt ist einen kontrollierten Versuch wert. Die Menge zehn ist eine praktikable erste Sammlung, keine mathematisch ausgezeichnete Populationsgröße. KI-Partner helfen am ehesten durch unterschiedliche überprüfbare Konstruktionen.

Die systematische Fluchtuntersuchung ergänzt dies: Sie zeigt, ob vorhandene Operatoren zu lokal bleiben und welche größeren Änderungen tatsächlich nützen. Beide Ideen passen zur Reviewer-Kritik, wenn wir reale Strukturunterschiede, Zulässigkeit und vollständige lokale Aussagen konsequent von heuristischen Beobachtungen trennen.
