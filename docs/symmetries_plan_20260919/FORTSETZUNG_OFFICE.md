# Fortsetzung Conway99 – Involutionen und Symmetrien, Office
Stand: 19. September 2026.

Setze ausschließlich den Forschungszweig „Involutionen / Ausschluss von Symmetrien“ fort. Ziel ist ein neuer, unabhängig überprüfbarer mathematischer Beitrag; Fernziel: nichttriviale Automorphismen eines SRG(99,14,1,2) ausschließen. Keine Vermischung mit Memetik oder Topologie.

## Rechner und Arbeitsweise
Alle vom Nutzer auszuführenden lokalen Berechnungen dieses Chats finden vorerst auf OFFICE statt. Historischer Stand: Windows 10, WSL2 Ubuntu, Benutzer rb, 4 physische/8 logische Kerne, knapp 8 GiB physischer RAM, WSL-Limit 5 GiB plus 8 GiB Swap. Aktuelle Ressourcen, Pfade und laufende Prozesse bei Bedarf mit EINER lesenden Abfrage feststellen. Ryzen-Pfade /home/rb_debian und Debian-Kommandos nicht auf Office übertragen. Vorhandene Memetikprozesse nicht stoppen oder beeinträchtigen. Der Ryzen wird für einen möglichen größeren Memetikversuch vorgehalten; keine dortige Kampagne starten.

Office dient zunächst Implementierung, mathematischen Kontrollen und kleinen Propagationsversuchen. Elf SAT-Worker aus Ryzenkonfigurationen sind hier ungeeignet. Auch virtuelle Linux-Freiplatzangaben ersetzen keine Windows-Hostmessung. Aktuelle Last und RAM bestimmen die kleine Workerzahl; Swap nicht als frei nutzbaren Solver-RAM einplanen.

Deutsch, präzise, keine Erfolgsgarantien. Softwareanweisungen an Ralph: genau EIN Schritt pro Antwort, mit Betriebssystem und Konsole; Antwort abwarten. Shellbefehle einzeilig ohne Fortsetzungs-Backslashes. Keine manuellen Codepatches verlangen; vollständige versionierte Pakete liefern. Kleine Artefakte und Berichte bevorzugen. Forschungscode und Ergebnisse in Git dokumentieren; gewöhnliche projektbezogene Pushes sind autorisiert, keine Force-Pushes. Eingehende Reviews unverändert in eigenem Zweig archivieren. Keine externe Nachricht ohne ausdrücklichen Auftrag.

## Verbindliche Quellen
Repository: https://github.com/ibenarb/conway99-research
Bisher aktiver Forschungszweig: research/algebra-memetic-20260912. Der historische Zweigname erlaubt keine Bearbeitung der Memetikdateien. Vor Änderungen aktuellen Head lesen und fremde parallele Änderungen erhalten.
Zuerst AGENTS.md und docs/CONWAY99_COLLABORATION.md lesen.

Geprüfter Fortsetzungsstand:
https://github.com/ibenarb/conway99-research/tree/e29cfa7011ca6721b9bcc4def4054a125fe9ab86/docs/symmetries_plan_20260919
Lies vollständig ABGLEICH_UND_PLAN.md, checks.json und check_review.py.

Unverändertes externes Review, eigener Zweig reviews/20260919-c2:
https://github.com/ibenarb/conway99-research/tree/5a1d6108fab25e09eaeee99985879a6a388de560/docs/reviews/20260919_c2
Lies ORIGINAL.md und receipt.json. Fremde Ausführungsbehauptungen nicht als eigene Reproduktionen darstellen.

Vorheriger Bericht/Reviewerauftrag:
https://github.com/ibenarb/conway99-research/tree/b3d2f8dc4eb51be9c1db4fc2a35cb827a2b2501b/docs/c2_review_20260919

Weitere Quellen am Forschungsstand e29cfa7011ca6721b9bcc4def4054a125fe9ab86:
- docs/c2_spec_20260913/SPEZIFIKATION.md und LITERATURABGLEICH.md
- src/c2_reference_20260913/ und docs/c2_reference_20260913/
- src/c2_matching_20260915/THEOREM.md, matching_orbits.py
- results/c2_matching_20260915/cover.json
- src/c2_counter_ab_20260916/THEOREM.md und Encoder
- results/c2_matching_20260916/eight_hour/
- results/c2_counter_ab_20260917/
- results/c2_totalizer_34h_20260919/ (Originalarchiv, Analyse, Bericht)
Lies die tatsächlich benötigten Dateien; keine vollständige Wiederholung alter Kampagnen.

## Gesicherter Stand und Grenzen
Es gibt KEINEN C2-Ausschluss. Alle elf Matchingfälle blieben offen, zuletzt regulär nach je 34 Stunden, insgesamt 373.979 CPU-h, ohne Produktionsproofs. Ein früherer 12.5h-Lauf scheiterte am Windows-Guard, nicht mathematisch. Keine Solvercheckpoints zum Fortsetzen. Referenz-8h und Totalizer-34h sind kein gleich budgetierter Geschwindigkeitsvergleich.

Rahmen 1+14+84 unter dem publizierten Satz: jede Involution hat genau einen Fixpunkt. Originalbeweis Makhnev–Minakova noch nicht intern auditiert. E1 M1=12·1, E2 MR=2J−R(K+I), E3 M²+M=12I+2J−RRᵀ plus Binärität, Symmetrie, Nulldiagonale und vorgeschriebene Involution bilden das dokumentierte exakte Modell.
M=[[B,C],[C,B]], 1722 Primärbits.

F auf 42 Paaren (Doppelverbindungen) ist ein perfektes Matching und bereits wörtlich als normierte E3-Partnergleichung kodiert. Ergänzung ergab byteidentische CNF; diesen Vergleich nicht wiederholen.
Davon verschieden: L auf zwölf Außenknoten einer Rahmennachbarschaft. Unter C2 wr S6 ergeben die 10395 beschrifteten Matchings genau elf Typen (Partitionen von 6), mit expliziten Transportern. Keine gleich großen Anteile des vollständigen Lösungsraums.

Referenz-CNF: 570171 Variablen, 1990821 Klauseln,
SHA256 f9d6011c5e6eb8a0fab971fa324d159e94b8bc4526b7b17dc31ee55aee1c25ba.
Mapping SHA256 cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e.
Totalizer-Basis: 534135 Variablen, 1921773 Klauseln,
SHA256 7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd.
Fall-CNFs besitzen zusätzliche Matchingannahmen und andere Hashes.
CaDiCaL 2.2.1, Quellcommit 4198d817d0dcde5b1240eefbff70b555b7df2af9.
Ryzen-Binärhash nicht für einen Office-Neubau voraussetzen.

## Übernommene Reviewimpulse und Korrekturen
Eigene Neuberechnung bestätigte alle elf Stabilisatorordnungen und Primärbitbahnen sowie 28980 Dreierklauseln. Prüfer nutzt vorhandene Rahmenabbildung: kein vollständig unabhängiger Zweitencoder.
Stabilisatorgrößen in Typreihenfolge:
111111:46080; 11112:1536; 1113:288; 1122:256; 114:64; 123:48; 15:20; 222:384; 24:32; 33:72; 6:12.
Reviewer-UP-Stichproben wurden nicht mit Code geliefert und nicht selbst reproduziert, insbesondere noch nicht auf dem Totalizer.

Restsymmetrie verdient höhere Priorität. Aber:
- Variablen in einer Bahn NICHT gleichsetzen: Umbenennungssymmetrie ist keine geforderte zusätzliche Graphsymmetrie.
- Gruppengröße ist kein garantierter Beschleunigungsfaktor.
- Stabilisator erhält die Menge der Fallklauseln, nicht jede einzeln.
- Partielle Lex-Vergleiche mit gleicher globaler Bitordnung erhalten das globale Minimum jeder Lösungsbahn; Erzeuger allein liefern nicht unbedingt eindeutige Vertreter.
- Semantische Symmetrie der Primärbits ist nicht automatisch syntaktische Symmetrie des Hilfsvariablenencoders.
- Fixierte Primärbits sind Propagationsdiagnostik, kein Prozentmaß des Beweisfortschritts. Neue Fixierungen nach Lex können bloße Repräsentantenwahl sein.
- CaDiCaL-CLI bietet keine beliebige externe Liveabfrage der Primärfixierungen. Sicheren Listener/Wrapper prüfen, keine nebenläufigen unzulässigen API-Zugriffe.
- Spektrum von D allein ersetzt nicht die Matrixgleichung mit festem V; Nullraumlage und DV=0 bleiben relevant.
- Prüflogs ersetzen keine archivierten Zertifikate. Kein automatisches Löschen endgültiger geprüfter Proofs.
- Cubing ist eine Option, nicht der einzig denkbare Zertifizierungspfad.
- Einzelne zertifizierte Fälle dürfen als klar begrenzte Teilergebnisse dokumentiert werden.

## Literaturbilanz
Nach erneuter Volltextprüfung: Crnković–Maksimović 2020 §7, Sätze 7.1–7.3, plus Cesarz–Woldar 2025 Kor. 3.13 ergeben volle Aut-Gruppe nur 1,C2,C3; C3 fixpunktfrei. Diese publizierten Rechenausschlüsse sind nicht intern komplett reproduziert. Quellen im Plan.
Ishida arXiv:2606.29183 PDF v2 §8.4 ergänzt den Quellenbestand und a1(t)=14. Die schwächere C3-Alternative ∅/K3 widerlegt den stärkeren Ausschluss des Dreiecksfalls nicht.
Thakkars 48h-Lauf betraf C7, NICHT C2. Kein C2-Ausschluss daraus.
Makhnev–Minakova-Volltext erneut technisch nicht abrufbar; Satz als Literaturabhängigkeit markieren, nicht jeden Pilot von erneuter historischer Beweisführung abhängig machen.
K66 ist ein begrenzter Ordnung-3-Fall, nicht das gesamte C3-Problem. Git-Metadaten und vollständiges Proofarchiv nicht verwechseln.
Nach C2 bleibt C3; erst beide zusammen und die Literaturabdeckung ergeben den angestrebten Symmetrieausschluss.

## Nächste Arbeit
1. Quellen lesen und gültige nächste Implementierungsaufgabe bestimmen. Nicht erneut nur einen allgemeinen Forschungsplan schreiben.
2. Für die elf Fälle Stabilisatorerzeuger und induzierte Primärpermutationen prüfbar exportieren; zulässige partielle Lex-Ketten implementieren. Generischer Vertretererhaltungsbeweis, passende kleine exhaustive Kontrollen und Prüfung der Fallannahmen.
3. Vier getrennte Varianten vorbereiten: Totalizer / +Lex / +28980 Dreierklauseln / +beides. Gültigkeit, Hashes, Variablenkarten und kleine strukturierte UP-Vergleiche dokumentieren. Keine flächendeckenden Millionen Viererklauseln.
4. Aus dem bisherigen Ryzen-Pilotentwurf (3 Typen × 4 Varianten × 2 Seeds ×20 min =24 Jobs,8 nominelle CPU-h) einen Office-gerechten Ablauf ableiten. Auf Office dauert das entsprechend länger; NICHT die Ryzen-Schätzung „rund eine Stunde“ übernehmen. Vor großen Benchmarks erst Kleinkontrollen und Ressourcenprobe.
5. Auswahl anhand gleicher Aufgaben, Entscheidungen/CPU-Kosten; Timeouts bleiben zensiert. Bei lauter offenen Wurzeln identische vorab definierte primäre Cubes, beidseitige Propagation, vollständiger Splitbaum; dominante Spines erkennen.
6. Erst bei belastbarer Wirkung längeren Lauf vorschlagen. Scouts ohne Proof-Logging; Zertifizierung separat mit harten Ausgabegrenzen, Windows-/Linux-Reserve, unabhängiger Prüfung und dauerhafter Archivierung.

Alternative algebraische Spur: reguläre signed graphs mit drei Eigenwerten, Anđelić–Koledin–Stanić 2020. Für D: D³+D²−12D=0, Diagonalen D³=−10, D⁴=130, signed Dreiecksdifferenz je Knoten −5. Bereits Konsequenzen des Modells, kein neuer Ausschluss; möglicher Ansatz für lokale Muster. Zweite gekoppelte Nachbarschaft bleibt als zusätzliche strukturierte Zerlegung verfügbar.

Arbeite zuerst autonom an der Implementierung, soweit Deine Umgebung es erlaubt. Wenn lokale Ausführung nötig wird, gib Ralph genau den ersten passenden Office-Schritt und warte auf dessen Ausgabe. Kein Zugriff auf seinen PC vortäuschen.
