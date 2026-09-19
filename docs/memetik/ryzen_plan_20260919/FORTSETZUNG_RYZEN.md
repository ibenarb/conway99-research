# Fortsetzung: begrenzten Memetik-Vergleich auf Ryzen implementieren und ausführen

Setze Conway_99 ausschließlich im Forschungszweig Memetik fort. Arbeite auf Deutsch. Setze den angenommenen Plan konkret um; liefere nicht lediglich einen weiteren Strategieentwurf.

## Auftrag und Freigabe
Der Nutzer hat den Reviewabgleich und Plan V2 angenommen und beauftragt jetzt deren Umsetzung. Nächster Schritt ist ein begrenzter Ryzen-Methodenvergleich mit 144 Worker-CPU-Stunden, einschließlich der notwendigen begrenzten Vorbereitung. Implementierung, gezielte Kontrollen, Auslieferung, Anleitung zum Start und anschließende Auswertung sind der Auftrag. Nicht nochmals allgemein fragen, ob umgesetzt werden soll.
Die spätere 48-Stunden-Hauptkampagne wird erst nach Auswertung konkret festgelegt; nicht automatisch mitstarten.

Zielrechner ist jetzt der Ryzen, nicht der Office-PC. Bekannter Planungsstand: 12 physische Kerne, 24 logische Prozessoren, etwa 47 GiB WSL-RAM. Alte Modellbezeichnungen sind widersprüchlich; CPU-Modell, Affinität, RAM, freien Platz und vorhandene Last vor Auslieferung direkt feststellen. Office läuft separat im Zweig Symmetrien; dort nichts starten, stoppen oder verändern. Auch keine fremden Ryzen-Prozesse beenden.

## Quellen zuerst lesen
Repository https://github.com/ibenarb/conway99-research, Branch memetik.
Fester fachlicher Ausgangsstand: 81c3a440c61670c0221103ec1d2cdd37b084bf67. Die Branchspitze zusätzlich prüfen; spätere fremde Arbeit bewahren.
Zuerst AGENTS.md und docs/CONWAY99_COLLABORATION.md.
Dann:
- docs/memetik/ryzen_plan_20260919/REVIEWABGLEICH.md
- docs/memetik/ryzen_plan_20260919/RYZEN_PLAN_V2.md
- docs/memetik/ryzen_plan_20260919/REVIEWINDEX.md
- docs/memetik/ryzen_plan_20260919/SCHLUSSFOLGERUNGEN_BESCHLOSSEN.md (mit diesem Fortsetzungsprompt veröffentlicht)
- docs/memetik/OFFICE_PILOT_001_AUSWERTUNG_20260913.md
- docs/memetik/GRUENDERVERTRAG.md
- data/memetik/ai_candidates/registry.json und Abnahmen der tatsächlichen Generatoren.

Unveränderter externer Review: eigener Branch reviews/20260919-memetik-grossversuch, Commit d2140c17bf4643295d7d71abe23c034a31a65944, Verzeichnis reviews/20260919-memetik-grossversuch/.
Der Review begutachtet 958744f8b53ce66894a8b29e9bdfa033871574b0, nicht den späteren Ryzen-Plan. Nicht pauschal alle Reviewerbehauptungen übernehmen; Korrekturen stehen im Abgleich.

Relevante Software:
- src/memetic_v2/ und configs/memetic_v2/office-0.2.0.json als historische Referenz, nicht ungeprüft produktiv übernehmen.
- experiments/memetik/escape_0_2/ für Operatoren/Abstiege.
- experiments/memetik/minimax_0_3_0/ für robuste Datenhaltung und konkrete Suchmechanik.
- results/memetik/review_reconciliation_20260919/ für bereits erledigte Katalogkontrollen.
Wähle eine neue eindeutige Paket-/Versionsbezeichnung nach Prüfung vorhandener Releases. Alte Ergebnisse/Checkpoints nie überschreiben oder als neue Läufe wiederverwenden.

## Mathematischer Vertrag
Ziel srg(99,14,1,2). Für ungeordnete Paare r_uv=(A²)_uv+A_uv−2.
W zählt Nichtnullfehler; L1 summiert Absolutfehler; F summiert Quadrate; Linf-Selektion vergleicht (Linf,Nmax,L1) lexikographisch.
Beide Arme: einfacher ungerichteter 14-regulärer Graph auf 99 Knoten.
Ω: kanonischer 1+14+84-Rahmen und harte Gleichungen, insbesondere PH=2J−(C+I)P.
λ: jede Kante genau ein gemeinsamer Nachbar.
Ω impliziert nicht global λ=1. Aufnahme und vollständige Scores unabhängig prüfen.
W bleibt Diagnose, kein vierter Selektionsarm. Keine ungeprüften Transfers zwischen Armen oder ungefärbten Isomorphiequotienten im Ω-Arbeitsraum.
Keine Fortsetzung von K66-, C2-, O3- oder Involutionsausschlussrechnungen. Deren lokale Strukturideen sind höchstens optionale Erzeugungsvorlagen unter dem Armvertrag.

## Gesicherter Forschungsstand; nichts davon pauschal wiederholen
- A: geschlossene Achtzustandskomponente im bisherigen Produktkatalog, keine Verbesserung darin. Keine neuen unbeschränkten A-Suchen.
- C08: kürzester W-Verbesserungsweg 2673→2673→2668, Länge zwei, W-Barriere null; L1/F schlechter. 33 neutrale Nachbarn untereinander isomorph, Gesamtplateau nicht geschlossen.
- C02: W=2031,L1=2428,F=3298 an einem Graphen; F=3292 an anderen Endpunkten.
- B: ab W=2082 geprüfter Pfad 2082→2094→2094→2086→2090→2080, minimale W-Barriere genau 12. Kürzeste Verbesserungsweglänge zwischen drei und fünf; W=2080 noch nicht als lokales Minimum nachgewiesen. Gezielten Abstieg/Zensus dieses neuen Starts in Vorbereitung integrieren.
- HoG: F=2836; Minimax-Endstand 2142386 Zustände,76258 Expansionen, notwendige Barriere ≥192 checkpointgestützt. Kein Verbesserungsweg gefunden, keine abgeschlossene unbeschränkte Komponente.
- Alle 6006 gelieferten Randgraphen der älteren B-/HoG-Sublevel wurden unabhängig auf Verträge und Scores geprüft. Keine neuerliche pauschale Prüfung.
- Exakte Isomorphieentscheidungen nicht mit Einzugsgebietsidentität verwechseln.

## Die konkrete Umsetzung
1. Erstelle das gemeinsame Gründer-/Generatorregister aus vorhandenen geprüften Dateien. Mathematisches Prinzip, Codeversion, Seed, Abstammung, graph6/Hash, Scores, ungefähre Erzeugungskosten, Isomorphieklasse und Ω-Rahmen getrennt führen. KI-Anbieter ist keine Familie.
2. Verwende vorhandene Abnahmen und Zeugen. Qualifiziere zusätzliche Generatoren nur mit begrenztem Budget. F02 ist bewährt, F03/F04 verwandt; Tripelrepräsentation ist allein kein lieferfähiger Generator. G1–G4 und K66-inspirierte Vorlagen nicht als bereits implementiert behaupten.
3. Für den Vergleich 16 tatsächliche verschiedene Gründer je Arm auswählen: Qualitätsanker und mehrere verfügbare Herkunftsgruppen, gleicher vorab fixierter Satz für beide Varianten und alle drei Ziele des Arms. Gelingt diese Größe nicht, konkreten Engpass melden und die kleinere tatsächliche Größe in beiden Varianten gleich verwenden; keine Klone zur Mengenerfüllung. Genügend wiederholte Bearbeitung je Linie prüfen, sonst Aussagekraft begrenzen, nicht unbemerkt das Gesamtbudget erhöhen.
4. Ω-Erzeugung beschleunigen: statische Katalogteile vorberechnen, H-abhängige Zulässigkeit korrekt aktualisieren, Erzeugungs-/Score-/Kanonisierungskosten messen. Nach Änderungen kleine gezielte Referenzkontrollen; keine allgemeine Testwiederholung.
5. Zwei Varianten implementieren:
   A0 = zulässige zufällige Störung + strikt verbessernder Abstieg.
   A1 = zusätzlich zielbezogener Besuchsspeicher, neutrale Exploration und kalibrierte Escape-Steuerung.
   Gleiche Gründer, Populationsgröße, Überlebensregel und CPU. Beide haben dieselbe allgemeine Anfangsstörung; A0 ist nicht künstlich bewegungsunfähig.
6. Parametrierung aus Plan V2: 40/30/20 % Ausflüge der Längen 2–4/5–12/13–32; 10 % neue gültige Gründer oder qualifizierte Reparatur, Ausfälle offen behandeln. Eigene Budgets höchstens 45 CPU-Sekunden Störung +75 Abstieg je Episode; tatsächliche Längen/Teilabbrüche erfassen. Bei 16 Plätzen Überleben 2 Elite+10 Qualität+4 Exploration. Crossover zunächst null.
7. A1: Besuchsspeicher 128 Zustände, neutrale Probe bis32 neue Zustände im Restbudget. Schwellen nach Arm/Ziel kalibrieren, relativ zu festem Episodenanker. L1/F-Stufen s,2s,4s bis vorläufig10% Ankerwert; s aus positiven Tradeänderungen. Linf bleibt lexikographisch, Sonderausflug Linf+1 streng begrenzt wie in V2. Nicht alle freien Parameter ständig variieren: Training/Parameterwahl beenden und Konfiguration vor Bestätigung einfrieren. Andere als die zur Wahl verwendeten Gründer als Übertragungsprüfung vorsehen.
8. Vergleichsmatrix: 12 gepaarte unabhängige Laufseeds ×2 Varianten ×2 Arme ×3 Ziele ×1 Worker-CPU-Stunde =144 CPU-Stunden. Keine Generationen oder Individuen als unabhängige Replikate zählen. Keine Migration während des Vergleichs. Seed- und Auftragsmanifest vor Start speichern.
9. Primär je Arm/Ziel bester aktiver Zielwert am CPU-Endpunkt; Linf direkt lexikographisch. Siege/Gleichstände/Niederlagen, Effektgrößen und Verläufe auswerten. Vorab festgelegter einseitiger exakter Vorzeichentest mit Holm-Korrektur für sechs Entscheidungen; keine nachträgliche Auswahl eines günstigeren Kriteriums. Bei unklarem Vorteil A0. Sekundär Klassenvielfalt, Familienerhalt, Kosten, tatsächliche Störlängen, Rückkehrquote.
10. Paket mit atomaren Checkpoints, konsistenter CPU-Buchhaltung, Wiederaufnahme ohne neues Budget, überprüfbarem Export und 10-Minuten-Status liefern. Vollständige unabhängige Prüfung akzeptierter besonderer Funde. STALLED_SAMPLED ist kein lokales Minimum.
11. Nach realer Ryzen-Kalibrierung die notwendige einzelne Installations-/Startanweisung geben. Nach Abschluss exportieren, prüfen, auf Git dokumentieren und eine konkrete Entscheidung zur Hauptkampagne treffen.

## Ressourcen und Laufzeiterwartung
Bis24 unabhängige Single-Thread-Worker, Vergleich von12/18/24 nach gültigen abgeschlossenen Episoden pro Wandzeit. Solver-/BLAS-Unterthreads begrenzen. Alle verfügbaren physischen Kerne nutzen; die drei späteren Hauptlauf-Replikate würden denselben Workerpool teilen, nicht jeweils24Worker erhalten.
Gleiche kumulierte CPU-Kontingente der sechs Arm/Ziel-Gruppen. Fehlversuche und Reparaturkosten mitrechnen. CPU über Kindprozesse korrekt aggregieren; monotone Sitzungsuhr, UTC zusätzlich. Ungeklärten alten Zeitversatz nicht übernehmen.
Bei tatsächlich bestätigten47GiB RAM höchstens36GiB gesamte Prozessgruppe; normale Jobs bis1GiB, höchstens zwei schwere Reparaturen gleichzeitig bis3GiB; unter6GiB verfügbar keine neuen schweren Jobs. Freien Plattenplatz und existierende Last prüfen. Keine Millionen-Zustandsdatenbank pro Individuum.
Vorbereitung als Rahmen höchstens16CPU-Stunden Technik/Kalibrierung und bis32CPU-Stunden neue Gründer; nicht zwangsweise ausschöpfen.
Reiner Vergleich nominal6–12Stunden bei24–12 versorgten Workern; vorläufig praktisch8–16Stunden. Einschließlich vorbereitender Rechenarbeit ungefähr10–20Stunden bei guter Parallelisierung. Das sind ungemessene Planungsfenster, keine Obergrenzen; Softwareentwicklung und manuelle Wartezeit fehlen. Nach Messung aktualisieren.

## Arbeitsweise und Daten
Eigenständig zugängliche Recherche/Implementierung/Prüfung selbst erledigen. Benutzeranweisungen ausschließlich einzeln: genau ein ausführbarer Bash-Einzeiler, Ausführungsort „Ryzen, Ubuntu/WSL“ ausdrücklich nennen, Rückmeldung abwarten. Keine erneute allgemeine Einrichtung, keine Befehlsserien.
Normale Forschungscommits/Pushes und Forschungsdateien jeder Art sind autorisiert; keine Force-Pushes oder Löschung fremder Arbeit. Lokalen Commit nie als Veröffentlichung ausgeben. Revieweroriginal bleibt unverändert.
Scratch-Dateien aus alten Chats können durch Wartung fehlen. Git ist die primäre Quelle; fehlende große Originale nur gezielt nachfordern, wenn tatsächlich benötigt. Für diesen Vergleich keine zwingende Abhängigkeit vom großen HoG-SQLite-Archiv einführen: geprüfte Graphzeugen stehen auf Git.
Der große Minimax-Export ist nicht auf dem Forschungsbranch veröffentlicht. Bei Bedarf: Ergebnisse_Minimax_030_minimax_20260917_213047_385349.zip,292828623Bytes,SHA256 eb0b94a06ee2740d0439354146e6785f054e484816670464595ade4214444fe7. Nicht ungeprüft heutige lokale Verfügbarkeit behaupten.
Beginne jetzt mit Quellenprüfung, Register und Implementierung der minimal notwendigen Vergleichssoftware.
