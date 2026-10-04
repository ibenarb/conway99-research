# Vorschlag: ROOT8105-Autopilot 2 — exakte Breite und getrennte Modellkontrollen

Stand 04.10.2026. Vorschlag zur Prüfung, keine Freigabe und kein gestarteter Lauf. Die abschließende Entscheidung fällt Ralph nach Eingang des unabhängigen Reviews. Nearest-H 0.7.0 bleibt ein paralleler Erkenntnispfad; die Breitenmessung muss nicht auf dessen Lösung warten.

## 1. Ziel und messbarer Ertrag

Primäres Ziel: Für ausgewählte ROOT8105-Klassen die erste Erweiterung vollständig auszählen, ihre kanonisch verschiedenen Kinder bestimmen und die Vollständigkeit nachvollziehbar absichern. Anschließend die nächste Schicht für eine vorab ausgewählte Teilmenge vollständig bearbeiten oder die verbleibende offene Arbeit exakt benennen.

Separates Diagnoseziel: Bekannte H-lineare Zeugen und tatsächliche lokale Positivbelegungen verwenden, um Semantikfehler, Encoderfehler und Solverleistung auseinanderzuhalten. Keine neue Hypothese über SRG-Nichtexistenz aus UNKNOWN oder stagnierender Tiefe ableiten.

Ergebnis auch bei sehr großen Bäumen: exakte geschlossene Teilbereiche, belastbare Untergrenzen, offener Aufgabenbestand, CPU/Bytes je eindeutigem Kind und lokaler Zertifizierungsaufwand. Eine prognostizierte Gesamttiefe 20/30 ist kein Akzeptanzkriterium.

## 2. Vorbedingungen und Kontrollserie

### A. Modellvertrag und verfügbare Zeugen

Beschaffe die bytegenauen cand_A/B- und Root-witness-1/2-Dateien samt Labelkonvention, Hashes und Herkunft. Diese Rohobjekte sind in den drei gelesenen Dokumentationscommits nicht enthalten. Zulässige Border-Relabelings und die Abbildung einer ersten Zeile auf den ROOT8105-Katalog ausdrücklich prüfen; ein beliebiges H-lineares Präfix muss nicht bereits ein gültiger ROOT8105-Startzustand sein. Fehlen sie, wird dieser Kontrollteil als noch nicht vorbereitet ausgewiesen; keine erfundenen Zeugen oder behaupteten Tests.

Implementiere und vergleiche getrennt:

- L: globale H-lineare Faser (symmetrisch/binär/diagonalfrei, Grad und alle Border-Margen).
- F(S,t): historische lokale ROOT8105-Relaxation, unverändert als Referenz.
- F_all(S): alle offenen Margen und alle Paarbedingungen mit einer gebauten Zeile; entspricht semantisch `encode(..., target=None)` der Referenz. Erst künftig als möglicher notwendiger Filter nutzen, nach Audit.
- Vollständiger SRG-Checker: unabhängig von den drei Relaxationsencodern.

Vor jeder Solverzeitmessung die erwartete Positivbelegung beziehungsweise den bekannten Negativgrund unabhängig prüfen. Interne Hilfsvariablen der CNF durch vollständige SAT-Belegung oder separat validierte Cardinality-Gadgets kontrollieren.

**Konkrete L-Matrix:** vier vollständige H-Zeugen × Präfixtiefen {1,8,16,24,32,48,64,80} × drei fest veröffentlichte zulässige Border-Relabelings = 96 Fälle. Präfixe bestehen aus vollständigen Zeilen des Zeugen. Vergleiche identische Fälle einmal ohne Completion-Hint und einmal mit Hint (192 Solverversuche), ohne Hint als Forschungsfall und mit Hint als technische Diagnose. Nicht zur Pflicht machen, denselben ganzen Zeugen wiederzufinden: Jede unabhängig geprüfte gültige L-Completion zählt. Vorab alle 96 ursprünglichen Zeugenbelegungen direkt kontrollieren. Ein Hint-Erfolg allein gilt nicht als unvoreingenommene Solverleistung.

Diese L-Tests verwenden keinen `Geometry.verify`-Aufruf, der zusätzliche SRG-Paarbedingungen still voraussetzt. Pro Präfix separat berichten, welche stärkeren Bedingungen erfüllt/verletzt/unbekannt sind. Keinen notwendigen UNSAT-Befund allein aus einem verletzten mitgelieferten vollständigen Zeugen ableiten.

**F-Kontrollen:** Mindestens 24 verschiedene tatsächlich SAT-gelöste und unabhängig geprüfte lokale F(S,t)-Instanzen aus verschiedenen Rootklassen und Tiefen, soweit als echte Fälle verfügbar. Erfüllende Belegungen vollständig archivieren. Danach Relabeling, Wiederaufnahme und erneute Lösung ohne Hint testen. Fehlende tiefe SAT-Instanzen als fehlende Kontrollen ausweisen, nicht künstlich als positiv deklarieren. Zusätzlich bekannte kleine Positiv-/Negativfälle; falsch gesetzte Margen und Widersprüche müssen erkannt werden.

**End-to-end-Kontrolle:** 9er-Rook-SRG, vollständige Abdeckung der kleinen Testsuche gegen unabhängige Brute-Force-Zählung; Kontroll-Negativfälle mit Beweisen. Das testet Korrektheit und Coverage, nicht die Laufzeit für 99 Vertices. Bereits vorhandene Kontrollfälle wiederverwenden statt einen neuen mathematischen Befund zu behaupten.

Für die konkrete Entscheidung sind zwei Fehlertypen zu trennen: Ein nachweislich falsches UNSAT/ungültiges SAT blockiert die betroffene Implementierung; bloßes UNKNOWN misst Solverleistung und ist keine Korrektheitswiderlegung. Ein langsamer L-Completer verhindert nicht automatisch die unabhängige F-Breitenmessung.

## 3. Vollständige frühe Breitenmessung

### B. Auswahl vor dem Lauf fixieren

32 Rootklassen: 24 aus den bisherigen 128 und acht bisher ungetestete Kontrollen. Reproduzierbare Auswahl nach Stabilisatorgröße und Matchingzahl, mit Abdeckung trivialer und nichttrivialer Stabilisatoren sowie der Randbereiche. Innerhalb der alten 24 zusätzlich die bisherigen Tiefen-/Strategie-Kontrastfälle berücksichtigen und diese bewusste Auswahl offenlegen. Root-IDs, Selektionscode und Seed vor Messbeginn veröffentlichen; keine Auswahl nach später gesehenen Breiten.

Auf allen 32 zuerst die Erweiterung von Tiefe 1 nach 2 vollständig bestimmen. Die Auswahl ist keine Basis einer ungewichteten repräsentativen 8105-Prognose. Die vollständige Populationsverteilung der Strata ist für spätere Gewichtung verfügbar zu machen.

Auf acht vorab ausgewählten dieser Roots zusätzlich fixed-order als Vergleich ausführen. Primärarm ist eine dokumentierte deterministische dynamische Zielwahl, nicht zufällig vier Zielvertreter. Zielwahl nur durch billige Merkmale, nötigenfalls mit begrenzter Anzahl von Informationsabfragen; Aufwand separat verbuchen. Die Heuristik darf Reihenfolge bestimmen, aber keine gültigen Zeilen löschen.

Eine vollständige Suche braucht an jedem Zustand nur eine offene Zielzeile und alle ihre zulässigen Belegungen. Eine feste Reihenfolge ist bei vollständiger Aufzählung grundsätzlich vollständig. Der frühere Vorteil von dynamic betrifft sampled/beam-Suche; er allein entscheidet nicht über die beste exakte Strategie. Alle Zielzeilen parallel als Baupfade zu verfolgen würde zusätzliche Pfadduplikate erzeugen und benötigt einen eigenen Coverage-Nachweis.

### C. Zweite Schicht

Für vier schon vor dem Lauf bestimmte Roots (je nach Stratum, nicht nach günstiger gemessener Breite) alle deduplizierten Tiefe-2-Zustände nach Tiefe 3 bearbeiten. Das kann sehr groß sein: Keine Zusage, dass diese Schicht im ersten Ressourcenrahmen fertig wird. Alle nicht bearbeiteten Eltern bleiben explizite offene Aufgaben.

Optional nach der Entscheidung: Vergleich F versus F_all auf einem fest abgegrenzten gemeinsamen Satz von 64 Elternzuständen. Für nichtleere F_all-Cases unabhängige SAT-Zeugen; für UNSAT-Cases passende Zertifizierung. Kosten des stärkeren Filters gegen eingesparte Enumerations-/Kinderarbeit messen. Ein langsamer globaler Completion-Oracle wird nicht ungeprüft in jeden Suchknoten eingebaut.

## 4. Enumeration, Symmetrie und Beweiskette

Keine Reservoir-/Beam-Truncation in B/C. Ausgabeblöcke, etwa 65.536 Zeilen, sind reine Dateieinheiten und keine mathematischen Abbruchgrenzen. Nach Blockende bleibt die Enumeration mit vollständigem Fortsetzungszustand offen.

Bevorzugt disjunkte, vollständig deckende SAT-Cubes über Projektionsvariablen mit nachvollziehbarem binärem Splitbaum. Pro Blatt endliche Enumeration und Abschlussbeleg; schwierige Blätter weiter aufteilen. Coverage des Cube-Baums separat prüfen. Das begrenzt Modellblocklisten pro Solver, ohne ausgeschöpfte Teilmengen als vollständiges Elternproblem auszugeben. Ein reiner Neustart ohne alte Ausschlüsse ist keine Fortsetzung.

Symmetrie in zwei Stufen messen:

1. Pro festem Elternzustand eindeutig definierte Aktion seines Stabilisators auf den Erweiterungen. Orbitvertreter und gegebenenfalls Orbitgrößen beziehen sich nur auf diesen festen Elternraum.
2. Kinder verschiedener Eltern über vollständige kanonische Zustandsbeschreibungen zusammenführen; die Vereinigung nicht durch Addition überlappender Orbitgrößen ersetzen. Root-, Border- und gebaut/offen-Markierungen müssen erhalten bleiben.

Für jeden verworfenen isomorphen Zustand prüfbare Permutation auf einen behaltenen Vertreter oder eine separat geprüfte kanonische Gleichheit speichern. Hashwerte dienen zum Auffinden, nicht allein als Gleichheitsbeweis. Darstellungs- und Kanonisierungsprüfung auf kleinen vollständig bekannten Fällen und zufälligen zulässigen Relabelings.

Zunächst vollständige Schichtdeduplizierung verwenden. Das ist keine automatisch bewiesene McKay-Canonical-Augmentation mit kanonischem Elternkriterium. Ein solches Elternkriterium wäre eine separate Optimierung mit eigenem Vollständigkeitsbeweis, bevor es Kinder verwerfen darf.

Für eine zertifizierte Schicht müssen zusammenkommen: vollständige Root-/Elternliste, alle Cube-Coverage-Belege, lokale Projektions-Coverage, geprüfte Symmetrieabbildungen und keine offenen Eltern. Ein Root ist erst ausgeschlossen, wenn alle gültigen Fortsetzungen durch eine entsprechend vollständige Beweiskette erledigt sind. Ein exaktes UNSAT einer notwendigen Relaxation kann einen Teilzustand ausschließen; SAT beweist keine SRG-Completion.

Zusätzliche Probe: Projektionszeilen nicht nur gegen die partielle Zeilenprüfung, sondern gegen passende SAT-Belegungen der Relaxation kontrollieren. Der lokale DRAT-Coverage-Beweis allein sagt lediglich, dass außerhalb der ausgeschlossenen Liste nichts fehlt; er bestätigt nicht die Existenz jeder gelisteten Projektion.

## 5. Daten, Messgrößen und Controller

Pro Root, Elternzustand und Tiefe:

- Rohprojektionszahl, exakte/untere Breite und Abschlussstatus;
- eindeutige kanonische Kinder und unterschiedliche Eltern, getrennt von Versuchen;
- Stabilisator, Orbitgrößen im korrekten Raum, Duplikate über alle gespeicherten Vertreter;
- erzeugte, erledigte, offene und zertifizierte Cube-Aufgaben;
- Solver-, Encoding-, Kanonisierungs-, Proof- und Supervisor-CPU;
- gemessene und kumulative Speicher-/Plattenkosten, Checkpointkosten, Durchsatz;
- Anteil abgeschlossener Aufgaben nach Schwierigkeit; keine Throughput-ETA nur aus den schnell fertig gewordenen Blättern;
- Host-Walltime zusätzlich zu Gastuhren und wait4-Abrechnung.

Physisches Format: chunkweise binäre Bitsets oder sparse Zeilen; gegebenenfalls verlustfreie Kompression, Checksummen, Schema und unabhängiger Decoder. Die 84 Bits einer H-Zeile passen in 11 Bytes; das ist kein Speichermaß für ganze Zustände, kanonische Schlüssel, Indexe oder Zertifikate. Statische Inhalte referenzieren statt wiederholen. Keine Millionen kleiner Dateien; Manifest, Ledger und Index skalierbar organisieren. Die originalen Pilotdateien bleiben unangetastet.

Proofauswahl für Leistungsmessung künftig geschichtet nach Tiefe, Breite und SAT-/UNSAT-Charakter; außerdem alle Belege der als vollständig deklarierten Schichten. Falls Zertifikate noch fehlen, bleibt die Schicht als ausgezählt, aber nicht vollständig zertifiziert markiert.

## 6. Ressourcen und Zeitregel

Vorschlag für den nach Review separat freizugebenden ersten Messblock: 480 aggregierte CPU-Stunden als Meldeschwelle, davon planerisch 48 für Modell-/Betriebskontrollen, 352 für exakte Enumeration, 48 für Zertifizierung und 32 für Nebenarbeit. Das sind Planungsanteile, keine automatischen Teilabbruchlimits. Bei elf ständig beschäftigten Kernen entsprechen 480 CPUh idealisiert 43 h 38 min; das ist eine Budgetprojektion, keine Fertigstellungs-ETA.

Bis elf Single-Thread-Worker; der parallel laufende C2-Checker wird weder verändert noch unterbrochen. Vor Start aktuellen freien RAM und Plattenplatz messen. Anfänglich insgesamt höchstens 20 GiB für diesen Autopiloten und mindestens 8 GiB freie RAM-Reserve anstreben; Workeranzahl und External-Memory-Verfahren müssen an tatsächlich verfügbaren RAM angepasst werden. Kein unnötiger Swapdruck.

Vorschlag aktive neue Laufdaten höchstens 80 GiB, mindestens 30 GiB freier Plattenreserve; tatsächlichen C2-Datenbedarf und übrige Prozesse vor Start berücksichtigen. Erreichen einer echten Speichersicherheitsgrenze löst einen kontrollierten Zustandserhalt aus; diese Grenze darf kein verkleidetes Zeitbudget sein. Falls vollständige Frontiers diese Grenze überschreiten: offene Arbeit erhalten, bessere Partitionierung/Archivierung planen, keine gelöschten Aufgaben als erledigt zählen.

Verbindlich GC-19 und EXPERIMENT_RULES v1.1 bei `611be0b0bc14acf7e0dfd4dfe40db13b27487271`:

    time limit reached. ETA HH:MM. Extend [seconds] ?

Bei unbekannter Restzeit `ETA unknown`. Bis zur Antwort weiterrechnen und normal Aufgaben planen, tatsächlichen Verbrauch weiter verbuchen. Positive Sekunden addieren zum bisherigen gleichartigen Budget; 0 beendet den bezeichneten Auftrag kontrolliert. Aggregierte CPU-Sekunden nicht als zusätzliche Walltime interpretieren. Keine nativen Solver-/RLIMIT-/Watchdog-Zeitabbrüche hinter diesem Dialog. Dauerhafter Antwortkanal für nohup, eindeutige Anfrage-IDs, einmalige Verbuchung, EOF/ungültige Eingabe ohne Rechenstopp.

Round-Robin über klar abgegrenzte Aufgaben/Cubes verhindert, dass ein einzelner Root alle anderen verdrängt. Eine Pause wegen Nutzerentscheidung oder ein regulärer endlicher Teilaufgabenabschluss bleibt unterscheidbar von einem Budgetabbruch. Keine getarnte Wiedereinführung der historischen 30-Sekunden-Abbrüche als Scheduler-Funktion.

Status alle etwa zehn realen Minuten und an Phasenwechseln. Neue experimentelle Optimierungen erst nach Fertigstellung, Tests und Freigabe einsetzen. Der jetzige Dokumentationsauftrag startet nichts.

## 7. Akzeptanz und Entscheidung nach Messung

Vor Produktionsstart erforderlich:

- Kontrollsemantik und unabhängiger Checker stimmen; falsche SAT-/UNSAT-Behauptungen blockieren den betroffenen Pfad.
- Vollständige kleine Kontrollenumeration mit und ohne Symmetrie ergibt gleiche expandierte Menge; Cube-Coverage besitzt keine Lücken/Überlappungen.
- Unterbrechung mitten in einem Chunk und Resume erzeugen weder Verlust noch falschen Abschluss; Ledger und alte Resultate bleiben erhalten.
- GC-19-Verlängerung/0/EOF/ungültige/doppelte Eingabe, weiterlaufende Berechnung während offener Anfrage und nohup-Antwort auf dem Ryzen tatsächlich testen.
- Wachsende Datenbestände verursachen keine blockierenden Vollscans; Fehler einzelner Worker stoppen unabhängige gesunde Aufgaben nicht.

Entscheidung nach Daten statt festem Tiefenziel:

1. Erste Schicht vollständig und kanonisch handhabbar: geplante vollständige zweite Schicht weiterführen; unabhängige Schicht-Coverage prüfen.
2. Bereits erste Schicht bleibt sehr groß: genaue untere Breiten, Speicher-/CPUkosten und offene Cubes berichten; stärkere notwendige Bedingungen oder direkte Residual-SAT-Zerlegung vergleichen, statt alle 8105 gleichartig zu starten.
3. F_all spart messbar Gesamtarbeit: geprüften Filter übernehmen; sonst lokales F behalten und F_all nur gezielt einsetzen.
4. L-Completer bleibt trotz korrekter Positivfälle langsam: nicht flächig als verpflichtendes Gate einsetzen. Ein Erfolg der L-Kontrollen allein rechtfertigt ebenfalls kein Gate im stärkeren ROOT8105-Modell.
5. Kleine exakte H-Moves bleiben nur ein gesonderter heuristischer Kandidatenpfad. Defekt-/Reparaturideen verändern keine Beweiskette und liefern ohne unabhängigen Checker keine SRG-Kandidaten.

Vor einem echten 8105-Vollauftrag ist eine weitere Entscheidung erforderlich: exakte Schichtbreiten über mehrere Strata, repräsentative Proofkosten, tragfähiger Speicherentwurf und ein vollständiger Coverage-Vertrag müssen vorliegen. Keine Laufzeitgarantie aus den jetzigen Daten.

Relevante Betriebslehren: GC-01/05/08/10/11/14/15/16/17/18/19 und die neue GC-20-Modellkontrollregel dieses Reviewstands. Besonders GC-16 (Limits ≠ Erschöpfung), GC-18 (begrenzt aufwendige Überwachung), GC-19 (Weiterarbeit bis Antwort). Implementierung und Zielhardwaretests dieses Vorschlags stehen vollständig aus.
