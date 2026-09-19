# Ryzen-Memetik nach dem tatsächlichen Review: Plan V2
Stand 19.09.2026. Ersetzt die Ausführungsprioritäten aus docs/memetik/ryzen_plan_20260919/RYZEN_PLAN.md. Die älteren Dokumente bleiben als Planungshistorie erhalten. Dies ist ein konkreter Versuchsplan, keine gestartete Kampagne oder fertige Auslieferung.

## 1. Entscheidung
Nicht sofort 64 aktive Individuen je Arm/Ziel in einem einzigen Lauf. Zuerst Methodenvergleich mit 16 je Arm/Ziel und mehr unabhängigen Seeds; danach drei unabhängige Suchläufe mit 32 je Arm/Ziel. Ein Gründerreservoir mit bis zu 64 verschiedenen Graphen je Arm bleibt Ziel. Es wird aber weder vorab als vorhanden behauptet noch zur Startbedingung gemacht.

Breite und Wiederholungen beantworten verschiedene Fragen:
- Eine große Einzelpopulation kann seltene interessante Strukturen erhalten, liefert aber keine unabhängige Wirksamkeitsschätzung ihrer Steuerung.
- Kleine replizierte Populationen prüfen Methoden besser, können jedoch seltene Familien früh verlieren.
- Kompromiss: kleinere kontrollierte Vergleichspopulation, danach größere Suchpopulation mit begrenztem Neuheitsanteil; später 64 nur bei gemessener Ausbeute, ausreichender Strukturbreite und ohne zu wenige Bearbeitungen je Linie.

## 2. Ausgangspopulation und Generatoren
Die gleichen Gründer eines Arms starten jeweils unter L1, F und (Linf,Nmax,L1). W bleibt Diagnose. 32 je Arm ergeben 64 physisch verschiedene Gründer, 192 Zielplätze pro unabhängiger Wiederholung; drei Wiederholungen verwalten 576 Plätze, nicht 576 unabhängige Gründer.

### Zielquoten pro Hauptlauf
| Ω-Erzeugung/Herkunft | Plätze bei 32 |
|---|---:|
| Historische Kontrollen und geprüfte Nachfahren (A einmal, B, C02 etc.) | 8 |
| Neue F02-Viererfasergraphen | 12 |
| Freier Ω-CSP | 4 |
| G1: kantenweiser Aufbau mit zulässigen Kontaktgrenzen | 2 |
| G2: Randmatchings zuerst | 2 |
| G4: Ω hart, begrenzte λ-Überschüsse | 2 |
| Reserve: G3 oder lokale, anschließend freigegebene Strukturvorlage | 2 |

| λ-Erzeugung/Herkunft | Plätze bei 32 |
|---|---:|
| HoG-Referenzen und geprüfte Nachfahren, einschließlich Linf=2 | 8 |
| Tatsächlich erzeugte gültige Tripelpackungsgraphen, bevorzugt vorhandene Claude-C-Methode | 8 |
| Z33-Lifts: F03 zwei, F04 sechs | 8 |
| Geprüfte größere Reparaturen verschiedener gültiger Eltern | 4 |
| Experimentelle Reserve: insbesondere G3, sofern erfolgreich | 4 |

Diese Tabellen sind Zielverteilungen, keine Erfolgsprognosen. Die Summe ist je 32. Für den Methodenvergleich wird ein vorab fixierter Satz von 16 je Arm aus den tatsächlich gelieferten Graphen gewählt: Qualitätsanker plus mehrere vorhandene Erzeugungsgruppen. Unsichere Generatoren nicht als lieferbare Quellen zählen. Für Hauptlauf-Wiederholungen identische vorab fixierte 32er-Pools bei verschiedenen Suchseeds verwenden; alternative Gründerzusammensetzung ist ein separates Experiment.

Begründung der Ungleichverteilung: F02 hat mehrere unabhängig geprüfte gute Ω-Gründer geliefert; eine größere Quote ist gerechtfertigt. Nur F02 wäre dennoch ein ungetestetes Vertrauen auf einen engen Raum. G1/G2 sind Verfahrensvarianten und werden in der Herkunftsauswertung gemeinsam ausgewiesen, solange kein struktureller Unterschied nachgewiesen ist. F03 ist Spezialfall von F04; beide als Liftgruppe führen. Reparaturen behalten die Elternabstammung. Historische C02-Nachfahren zählen zur F02-Familie, obwohl sie einen Archivplatz belegen.

Familienregister enthält mathematisches Prinzip, Code/Version, Parameter, Seed, Eltern, ungefähren Erzeugungsaufwand, exakte kanonische Klasse und beide Armprüfungen. KI-Anbieter ist Metadatum, keine Familie. Vorhandene Abnahmen weiterverwenden. Kanonische Zertifikate für alle tatsächlich verwendeten Gründer/ausgewählten Endpunkte; Profile nur diagnostisch. Für Ω Arbeitsrahmen zusätzlich erhalten. Kein ungefärbter Isomorphiequotient der Suchzustände ohne Operatorverträglichkeitsbeweis.

Bei 32 Plätzen höchstens 12 aus einer Abstammungsfamilie und höchstens zwei direkte Varianten desselben unmittelbaren Elternteils, soweit genügend gültige Alternativen vorliegen. Falls Archiv-C02 plus zwölf neue F02 die Familiengrenze überschreiten, neue F02-Plätze reduzieren und an unterrepräsentierte gültige Quellen vergeben. Keine als „neue Familie“ etikettierten Reparaturnachfahren.
Fehlen gültige Kandidaten, Plätze aus anderen unterrepräsentierten bestehenden Quellen besetzen; reichen diese nicht, mit 16 oder der ehrlich ausgewiesenen kleineren Zahl arbeiten. Kein Warten auf G3, kein Auffüllen mit Umnummerierungen. Geschlossene A-Komponente nicht mehrfach als aktiven Suchbestand verwenden; A bleibt Kontrollgraph.

## 3. Option 1, G1–G4 und neue Konstruktionen
Aus dem früheren Chat werden Kantenaufbau, Randmatchings, äußere Tripel und λ-Fehlerbudgets übernommen, aber nur als zu qualifizierende Generatorverfahren.

G1: Im partiellen Aufbau höchstens ein gemeinsamer Nachbar je vorhandener Kante, mit Prüfung aller betroffenen Kanten und Rücknahme; Grad- und Ω-Restmargen müssen erfüllbar bleiben. Am fertigen Graphen gilt der harte Armvertrag. Null gemeinsame Nachbarn sind damit nicht ausgeschlossen.
G2: Erst 14 Randmatchings (84 H-Kanten), dann 420 weitere H-Kanten. Diese Matchings sind bereits durch Ω erzwungen; neue Aufbaufolge, nicht bewiesener neuer Suchraum.
G3: Rest durch 140 äußere Dreiecke ergänzen und unerwünschte weitere Dreiecke ausschließen. Dann Ω∩λ. Schwieriges eigenes Konstruktionsziel; keine Startvoraussetzung.
G4: Überschussbudget Bλ=Σ_{Kanten}max(0,c_uv−1). Zusätzlich Null-Kontakt-Kanten und Σ|c_uv−1| erfassen. Probe zunächst mit b=16 und 64 als unoptimierten Parametern; bei fehlender Ausbeute Quelle begrenzen statt Budget endlos erhöhen.
Nie gleichzeitig c_uv≤1 für alle Kanten und c_uv≤2 für alle Nichtkanten als Aufnahmehürde verlangen: mit Regularität erzwingt die Summengleichheit bereits die exakte Lösung.

Tripelrepräsentation allein ist kein neuer Generator. Der Review meldet bei mehreren neuen Algorithmen 0 gültige Ergebnisse, bestenfalls 230/231 Tripel; Code/Seeds fehlen im Paket. Die bestehende Claude-C-Konstruktion hat dagegen einen geprüften gültigen Graphen geliefert, aber viele weitere unabhängige Seeds sind nicht zugesagt.
Ein eigenes Endspiel muss den Defizitvektor und Konflikte bearbeiten. Drei fehlende Inzidenzen müssen nicht drei verschiedene defiziente Punkte sein. Zerstörung/Reparatur mit unzulässigen Zwischenständen bleibt ein separater Erzeugungsoperator; nur gültige Endpunkte aufnehmen.

Lokale K66/C2/C3-Muster höchstens als kleine optionale Vorlagen mit explizit freigegebenen globalen Symmetriebedingungen. Keine ausgeschlossenen exakten Modelle als erfüllte Voraussetzung übernehmen; keine neue Ausschlussrechnung. Keine bloße Wiederholung der erfolglosen A-Fenster-/MILP-Formulierungen. Für D=xyᵀ+yxᵀ sind überlappende Träger wegen D_ii=2x_i y_i ausgeschlossen; andere kompensierende Formen wären gesondert zu prüfen.

## 4. Operatoren zuerst effizient machen
Der Office-Pilot verbrauchte 55,50 von 63,10 CPU-Stunden in Ω; 1009/1020 geführte Ω-Störungen blieben unter Mindestlänge. Dies bleibt die wichtigste technische Vorbedingung:
- statische Kernvektoren/Träger vorberechnen, H-abhängige Zulässigkeit korrekt aktualisieren;
- Erzeugung, Score, Kanonisierung und Reparaturkosten getrennt messen;
- tatsächliche akzeptierte Trades sowie Abbruchgrund berichten;
- Störung und Abstieg erhalten getrennte Kontingente.

Alte bestandene Tests nicht pauschal wiederholen. Nur geänderte Erzeugung und Datenhaltung gegen die Referenz gezielt kontrollieren. Außerdem an repräsentativen F02-/Lift-Gründern prüfen, ob Operatoren die feste Faser-/Dreiteilungsstruktur tatsächlich verlassen. Trivialer Automorphismenverlust reicht nicht als solcher Nachweis. Die exakte Liftvorlage kann keine Conway-Lösung enthalten; eingeschränkte Linien daher kennzeichnen.

## 5. Referenz und adaptive Variante
A0: zulässige zufällige Störung, danach strikt verbessernder stichprobenbasierter Abstieg; Bestarchiv und dieselbe Diversitätsselektion wie A1.
A1: zusätzlich zielbezogener Besuchsspeicher, begrenzte neutrale Exploration und vom Anker aus begrenzte Verschlechterungen. Alles andere einschließlich CPU, Population, Gründer und Überleben gleich.
Bei unklarem Vorteil startet A0. Einfache Referenz bedeutet nicht, dass während der initialen Störung niemals eine Verschlechterung vorkommt.

Bei 32 Plätzen: vier geschützte beste verschiedene Zustände, 20 weitere nach Zielrang unter Herkunftsgrenzen, acht Explorationsplätze. Bei 16: zwei, zehn, vier. Verbesserungen und Archive je Ziel getrennt; Population darf in den Explorationsplätzen zeitweilig schlechtere zulässige Zustände behalten.
Elternwahl 80 % Dreierturnier, 20 % unterrepräsentierte Herkunft gleichberechtigt. Zielgleiche Endpunkte werden anhand exakter Klasse und zulässigem Arbeitsrahmen unterschieden. Kein nach außen als bewiesen ausgegebenes Neuheitsmaß aus Histogrammen.
In ersten fünf Epochen mindestens ein gültiger Vertreter je ausgewählter Herkunftsgruppe; spätere Quoten an beobachteten Nutzen anpassen, Explorationsanteil beibehalten. Bestrekorde werden nicht gelöscht.
Keine Migration während des Methodenvergleichs. Erst später begrenzter Austausch zwischen Zielen desselben Arms als gesonderte Änderung; kein ungeprüfter Armwechsel.

## 6. Episoden, Verschlechterungen und Zyklen
Startrezepte: 40 % kurze Ausflüge mit 2–4, 30 % mittlere mit 5–12, 20 % längere mit 13–32 akzeptierten Trades; 10 % frische gültige Gründer oder qualifizierte größere Reparatur. Ohne lieferbare neue Kinder diesen Anteil offen umverteilen, nicht als erfülltes Rezept zählen.
Je Episode höchstens 45 CPU-Sekunden Störung plus eigene 75 CPU-Sekunden Abstieg. Diese Obergrenzen werden durch Durchsatzkalibrierung geprüft; kürzere Aufgaben können früh enden. Kein gemeinsames Bewertungslimit, das den Abstieg vorab verhindert.
Abstieg bis Stillstand oder Budget. Vollständig enumerierter Stillstand ist lokales Minimum im Katalog; stichprobenbasierter Stillstand wird STALLED_SAMPLED genannt. Nicht alle Individuen teuer vollständig zensieren.

A1 führt pro Ziel/Arbeitslinie einen Speicher der letzten 128 beschrifteten Zustände. Bei Stillstand höchstens 32 neue neutrale Zustände innerhalb des verbliebenen Budgets erkunden. Neutral bei Linf bedeutet Gleichheit des vollständigen Tupels. Gleicher Graph darf für ein anderes Ziel weiter untersucht werden. Erreichen der Neutralgrenze ist keine bewiesene Plateauerschöpfung.
Danach bzw. in späterer Escape-Episode Verschlechterung relativ zum Anker am Episodenbeginn, nicht kumulativ gegen den jeweils letzten Zustand. Für L1/F zunächst drei Stufen aus dem 75-%-Quantil positiver Einzeltrade-Änderungen s: s,2s,4s, jeweils höchstens 10 % des Ankerwerts. Ganze Werte nach unten runden. Bei weniger als 32 Kalibrierbeobachtungen Arm/Ziel-Pool verwenden oder neu kalibrieren; keine W-Barrieren auf F/L1 übertragen. Die 10-%-Kappe ist eine Kandidateneinstellung, nicht mathematisch privilegiert; nur Trainingsmaterial zur Wahl der Schwellen nutzen, vor Bestätigung einfrieren.
Linf: normale Exploration hält Linf fest, erlaubt höchstens max(1,ceil(0,1·Nmax_Anker)) zusätzliche Maximalfehler und höchstens 5 % mehr L1; strikt lexikographisch bessere Zustände werden unabhängig von diesen Verschlechterungsgrenzen als Verbesserungen behandelt. In höchstens 10 % der Escape-Episoden versuchsweise Linf+1 für höchstens acht Trades zulassen, dann Abstieg; getrennte Erfolgsbilanz. Keine skalare Gewichtung der Linf-Komponenten.
Diese zusätzlichen Linf-Mechanismen erst im Training auswählen; der Bestätigungsversuch prüft eine eingefrorene Variante, nicht ständig neue Parameter.

Nach vier erfolglosen Bearbeitungen derselben Linie Schwellenstufe wechseln; nach acht größeren Ausflug oder Austausch vorschlagen. Erfolg getrennt nach Zielfunktionsverbesserung und neuer Endpunktklasse berichten. Lange Wege 33–64 erst als Folgeexperiment, wenn mindestens 80 % der 13–32-Versuche die Mindestlänge erreichen. Trade-Trägergröße, Weglänge und Populationsepoche strikt auseinanderhalten.

Crossover zunächst Quote null in der Hauptvariante. Eigene kleine Probe gegen Mutation einschließlich Ausrichtung/Reparatur/Abstieg. Nur eigenständige gültige Kinder und überprüfter Zusatznutzen rechtfertigen spätere 10 %, nicht automatisch die früher gewünschten 20 %.

## 7. Belastbarerer Vergleich und Startentscheidung
Erste technische/Parameterkalibrierung: begrenztes Budget auf bekannten Kontrollzuständen. Zusätzlich vorab festgelegte, nicht zur Schwellenwahl verwendete Gründer vorhalten. Wiederholte Parameterauswahl an A/B/C08/HoG allein vermeiden. „Unbenutzte Seeds derselben Methode“ ist kein Test einer ganz neuen Familie.

Bestätigung:
- zwölf unabhängig randomisierte, gepaarte Laufseeds pro Arm/Ziel;
- je Paar A0 und A1 mit exakt denselben 16 Gründern, Population und CPU-Kontingenten;
- je Variante und Arm/Ziel eine CPU-Stunde pro Seed;
- insgesamt 12×2×6=144 Worker-CPU-Stunden.

Das ist ein vorab begrenzter Pilot, kein Nachweis universeller Überlegenheit. Ein unabhängiger Beobachtungswert ist ein kompletter Laufseed, nicht ein Individuum, eine Generation oder ein Graph. Herkunftskorrelationen bei Aussagen über neue Familien berücksichtigen.
Primäre Entscheidung je Arm/Ziel: bester Zielwert am gemeinsamen CPU-Endpunkt; bei Linf direkter lexikographischer Vergleich. Bericht gepaarter Siege/Gleichstände/Niederlagen, tatsächlicher Effektgrößen und vollständiger Verläufe.
Vorab einseitigen exakten Vorzeichentest als einfache robuste Prüfung festlegen; Gleichstände transparent behandeln, keine künstlichen Siege. Wegen sechs Entscheidungen Holm-Korrektur bei Gesamtalpha 0,05. Der Test ist bei vielen Bindungen wenig mächtig; dann Referenz, nicht nachträglich ein günstigeres Kriterium wählen. Ein signifikantes, aber praktisch belangloses Ergebnis rechtfertigt keine große Zusatzkomplexität; Kosten/Effekt und Stabilität mitberichten.
Sekundär Klassenvielfalt, Familienerhalt, Störlängen, Rückkehrquote und Zeit je gültigem Kind. Sie erklären Befunde, ersetzen nicht nachträglich das primäre Erfolgskriterium.
Bei unklaren Befunden startet A0; aussichtsreiche A1 bleibt ein gesondertes Experiment. Ergebnisse dürfen pro Arm/Ziel unterschiedlich ausfallen. Die absolute Zahl zwölf garantiert keine hinreichende Teststärke; benötigte Effektgröße und Streuung nach Pilot offen ausweisen.

## 8. Ryzen-Ressourcen und Hauptkampagne
Bekannter Planungsstand: 12 physische Kerne/24 logische Prozessoren, ungefähr 47 GiB WSL-RAM. Vor Start direkt messen, einschließlich aktuell laufender Prozesse und freiem Speicher/Platz. Keine Office-Prozesse verändern, keine fremden Ryzen-Jobs beenden.
Unabhängige Prozesse, interne Solver-/BLAS-Threads begrenzen. Kurzer 12/18/24-Worker-Durchsatzvergleich; Einstellung mit größtem Gesamtdurchsatz gültiger abgeschlossener Episoden nutzen. Alle physischen Kerne beschäftigen; 24 Threads sind keine 24 physischen Kerne.
Bei 24 Workern zunächst vier je Arm/Ziel, zentrale Queue gleicht kumulierte CPU aus und nutzt freie Slots. Die drei unabhängigen Hauptlauf-Replikate teilen sich den Pool; nie 24 Worker je Replikat. Fehlversuche, Reparaturen, Kindprüfung zurechnen; gemeinsame Infrastruktur separat bilanzieren.
Maximal 36 GiB gesamte Prozessgruppe bei bestätigtem RAM; normale Aufgaben bis 1 GiB, höchstens zwei Reparaturjobs mit je 3 GiB, Controller/Caches mitrechnen. Unter 6 GiB verfügbar keine neuen schweren Aufgaben. Keine großen Minimax-Datenbanken je Individuum. Score-/Quellenfehler stoppen betroffene Aufgaben; keine Löschung von Checkpoints.
Monotone Sitzungsuhr, explizite Worker-CPU, UTC zusätzlich. Früheren Uhrzählerversatz nicht als geklärt behandeln; neue Buchhaltung gezielt testen. Status alle zehn Minuten mit Budget-ETA, tatsächlichen Längen, Klassen und Zielwerten.

Nach Bestätigung vorgeschlagen: 48 Stunden gemeinsame Wandzeit, drei unabhängige Hauptlauf-Replikate, je 32 Plätze je Arm/Ziel, Zwischenprüfung nach 24 Stunden. Bei 24 ausgelasteten Workern rechnerisch höchstens 1152 Worker-CPU-Stunden insgesamt, also 64 pro Arm/Ziel/Replikat; mit 12 Workern 576 insgesamt. Keine Zusage einer Zahl von Generationen.
Eine Epoche pro Replikat: 192 Episoden, bei maximal 120 CPU-Sekunden je Episode höchstens 6,4 Worker-CPU-Stunden. Für alle drei zusammen 19,2 CPU-Stunden, ohne zusätzliche Generator-/Validierungskosten. Wirkliche Zeit aus Messung; nicht physische und logische Kernzahl verwechseln.

## 9. Was sofort vorbereitet werden soll
1. Herkunftsregister der tatsächlich vorhandenen Gründer und vorhandenen Generatoren; unsichere Quellen begrenzen, B ab 2080 fertig untersuchen.
2. Ω-Erzeugung effizienter machen und echte Ausflüge sowie getrennte Budgets messen.
3. Einfache und adaptive Variante mit gleicher Population implementieren, notwendige kleine Kontrollen.
4. 144-CPU-Stunden-Bestätigung ausführen, dann ausgewählte Hauptkampagne. Kein weiterer allgemeiner Plan anstelle der Umsetzung im nächsten Arbeitsschritt.
Keine komplette C08-/HoG-Untersuchung und keine beidseitig großen A-Trades als Pflicht. Bei fehlenden Generatoren kleiner beginnen. Die 64er-Population ist eine spätere Budget-/Diversitätsentscheidung, kein Automatismus.

## Quellen und Prüfstatus
Reviewarchiv d2140c17bf4643295d7d71abe23c034a31a65944; begutachteter Stand 958744f8b53ce66894a8b29e9bdfa033871574b0. Eigener vorheriger Ryzen-Entwurf 39bbcb50a72daae1e853e9a762dd110e79a76490. Vorliegende Office-Pilotberichte, Kandidatenabnahmen und Escape-/Minimax-Prüfungen bleiben Grundlage.
Kandidatenkonstruktionschat aus zuvor abgerufenen Ausschnitten G1–G4; keine neue vollständige Chat-/Literaturprüfung. Abgleich und eigene Katalogkontrollen stehen daneben. Sämtliche neuen Quoten/Schwellen sind vorläufige Versuchseinstellungen.

