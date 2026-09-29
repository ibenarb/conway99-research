# Review-Abgleich und Vorschlag K1, 29.09.2026

## Urteil

Der Review bringt wichtige neue Befunde, die unsere frühere Diagnose konkretisieren: (1) zu wenige günstige Zugträger werden freigegeben; (2) die Solver-Betriebsart übersieht sogar enthaltene Verbesserungen; (3) gute neue Kandidaten werden nicht ausreichend nachoptimiert. Meine frühere Betonung von Fensterwechsel/Rekombination war deshalb unvollständig. Die vorgeschlagene K0-Kampagne übernehme ich jedoch nicht unverändert: Ihr zentraler Stern-Rückkehrtest ist mathematisch nicht ausführbar, und die Ein-Defekt-Variante enthält unmögliche Zustände.

Originalreview und Prüfsatz sind byteidentisch im gesonderten Reviewzweig archiviert: `reviews/20260929-lambda-repair-120`, Commit `5873fec638c699aaba9bcea03b1e45b1f2494085`. Ausgangsstand unserer Daten: `68001f9f5aae97a3550d6039dfe731e0dd394e18`. Archivierung ist keine Zertifizierung fremder Befunde.

## 1. Was wir jetzt selbst geprüft haben

- Original-Upload SHA256 `5d29480effcaad2d3d97abd2831ba19a3afe4606f546844e4e2ead9f7a5b7e42`; alle Checksummen des inneren Prüfsatzes stimmen.
- Unabhängige Sternaufzählung: eigenes Matching-Verfahren auf vollständigen gemeinsamen Nachbarmengen, eigener Graphumbau, vollständige Prüfung jedes erzeugten Graphen mit unserem set-basierten Verifier. Für alle25 Poolgraphen stimmen Zahl zulässiger Züge, Zahl verbessernder Züge und bester Score mit dem Review überein.
- Unter den24 Gründern:11 verbessernde Sternzüge bei8 Gründern. Nur2 liegen in den Kampagnenfenstern:2139→2127 und2170→2155. Der zweite wurde vom Kampagnenlauf verfehlt.
- Den Zeugen2170→2155 unabhängig auf Grad,λ,Score und festen Fensterrand geprüft. Zusätzlich Reviewer-Skript am ursprünglichen CP-SAT-Modell wiederholt: fixierter Zeuge wird als zulässig/optimal bei Ziel107752564 bestätigt. Das beweist nicht ein unfixiertes Optimum, sondern die Existenz dieser enthaltenen Verbesserung.
- Alle25 gelieferten Sternabstiegs-Endpunkte vollständig auf Graphgültigkeit und Scores geprüft und neu kanonisiert. Sie bilden24 Klassen;8 davon fehlen im bisherigen25er-Pool. Die Vereinigung hat33 Klassen. Keine neue Rekordverbesserung. Das ist eine Ergänzung gegenüber dem ausdrücklich nicht kanonisierten Review, kein Widerspruch zu unserem vorherigen Laufbefund.
- Den gelieferten Radius16-Zeugen geprüft:W2140,L1=2540. Die zeitlichen Solververgleiche und die Tiefe2-Aufzählung sind weiterhin Reviewer-Messungen, nicht unabhängig wiederholte Benchmarks.
- Mobilitätsprüfung Größe24 mit dessen Skript wiederholt:36 INFEASIBLE,12 alternative Belegungen. Das ist Reproduktion mit derselben Modellierung, kein unabhängiges Ausschlusszertifikat. Größe40 ebenfalls wiederholt:42 alternative Belegungen,6 INFEASIBLE; sämtliche Statuswerte stimmen mit dem Review überein.
- Packungsrechnung unabhängig hergeleitet; zusätzlich sämtliche einfachen Graphen bis6 Knoten auf Schranke und Abgeschlossenheit unter Kantenlöschung geprüft. Dieser Kleintest ersetzt den allgemeinen Beweis nicht.

Die reproduzierbaren Dateien heißen independent.py, VALIDATION.json, STAR_WITNESSES.json, math_controls.py und MATH_CONTROLS.json. independent.py nutzt derzeit explizite Sitzungspfade; vor einer Reproduktion sind ROOT und review anzupassen. Es verändert keine Kampagnendaten.

## 2. Erklärung der Befunde

88 OPTIMAL-Meldungen bedeuten nicht88 repräsentative lokale Becken. Bei36 der48 kleinen Fenster gibt es laut reproduzierter Solverprüfung nicht einmal eine zweite Füllung.31 dieser eindeutigen Fälle waren zuvor als Solveroptimum gezählt,5 bereits durch Randpropagation als starr erkannt. Das bisherige Ergebnis war formal richtig, seine Suchraumbedeutung aber schwach.

Umgekehrt sind große Fenster nicht automatisch nutzlos: eine Verbesserung ist nachweislich vorhanden und wird verfehlt. Die schwachen Schranken und wenigen Konflikte passen zu einer ungünstigen Suchführung, beweisen für sich aber nicht die Ursache. Die Reviewer-Gegenversuche liefern einen konkreten Hinweis auf eine Wechselwirkung zwischen LP-Abschaltung und Hamming-Kugel. Einzelläufe können weder eine allgemeine Überlegenheit noch eine Ryzen-Laufzeit belegen.

Das Ergebnis2127 ist außerdem kein Endpunkt einer guten allgemeinen lokalen Optimierung: weitere gültige Sternzüge führen laut geliefertem Abstieg bis2118; den Endpunkt haben wir geprüft. Das ist kein neuer Rekord, zeigt aber eine vermeidbare Lücke im damaligen Reparaturpilot.

Acht neue Klassen aus den Reviewer-Nachrechnungen widersprechen nicht den null neuen Klassen aus1.2.0 gegenüber1.1.0. Es sind neue Rechnungen nach dem Lauf. Sie werden getrennt archiviert, nicht rückwirkend als Kampagnenertrag verbucht.

## 3. Widersprüche und notwendige Korrekturen

### 3.1 Der wichtigste Punkt: Der vorgeschlagene Rückkehrtest kann nicht starten

Sei G ein exakter SRG mitλ=1 undμ≥2, und p ein Knoten. N(p) ist ein disjunktes Matching. Zwei Nachbarn x,y aus verschiedenen Matchingkanten sind nicht benachbart. Sie haben μ gemeinsame Nachbarn, darunter p. Innerhalb N(p) können sie keinen weiteren gemeinsamen Nachbarn haben, weil dort jeder Knoten nur seinen Matchingpartner besitzt. Somit liegen μ−1≥1 gemeinsame Nachbarn außerhalb N[p].

Genau dies verbietet nach dem korrekten Sternkriterium das neue Paar{x,y}. Es bleibt nur das ursprüngliche Matching. Jeder solche exakte SRG ist daher unter nichttrivialen Sternneupaarungen isoliert. Das gilt für243,22,1,2 ebenso wie für9,4,1,2 sowie die vorgeschlagenen GQ-Beispiele mitμ=3 bzw5. Am9er-Rookgraphen ergibt die eigene Aufzählung erwartungsgemäß null Züge.

Damit ist „bekannte Lösung mit2,4,8,… gültigen Sternzügen stören und zurückkehren“ unmöglich. Weil Sternzüge reversibel sind, kann eine reine Sternsuche einen solchen Zielgraphen auch nicht aus einem anderen gültigenλ-Graphen erreichen. Das ist eine strukturelle Grenze dieses Operators; daraus folgt nichts Entsprechendes für alle größerenλ-Trades oder die gesamte Memetik.

Ersatz: bekannte Zeugen in unseren99er-Fenstern als positive Suchkontrollen; bekannte SRGs durch explizites Löschen/Freigeben von Kanten als kontrollierte Vervollständigungsaufgaben. Eine Rückkehrquote setzt tatsächlich erzeugte, gültige Störungen voraus. Bei fehlenden Störungen lautet der Befund „Test nicht anwendbar“, nicht „Methode gescheitert“. Auch ein korrekt negativer Kontrolltest bei anderer Größe könnte niemals Nichtexistenz vonConway99 von algorithmischer Untauglichkeit trennen.

### 3.2 Genau ein Defekt ist in der beschriebenen Form unmöglich

Bei99 Knoten und Grad14 gibt es693 Kanten. Für jeden Graphen gilt Σ_{uv∈E}CN(u,v)=3T. Haben alle Kanten genau einen gemeinsamen Nachbarn bis auf eine mit0 bzw2, ergäbe sich692 bzw694; beides ist nicht durch3 teilbar. Die vorgeschlagene einzelne±1-λ-Verletzung kann so nicht existieren.

Alternativ nur ein Gradpaar13/15 zulassen und überallλ=1 halten geht ebenfalls nicht: Die Nachbarn jedes Knotens müssen dann paarweise zu Dreiecken gepaart sein; jeder Grad ist gerade. Falls mehrere Bedingungen zugleich gelockert oder signierte uneigentliche Zustände gemeint sind, braucht es erst eine genaue Definition. Ein einziges „Defektobjekt“ in einer erweiterten Darstellung ist nicht dasselbe wie eine einzige verletzte Graphkante. Vor einer Suche kleine konsistente Defektmuster konstruieren und ihre Rückführung prüfen.

### 3.3 Frühere C3-Versuche sind kein direkter Gegenbeleg gegen Sternzüge

Im vorhandenen `lambda_strategy_0_1_0/strategy.py` verlangt cycle_move drei disjunkte Dreiecke auf neun verschiedenen Knoten und permutiert deren Spitzen. Ein Sterndreierzyklus hat dagegen einen gemeinsamen Mittelpunkt und sechs Nachbarn. Die Kataloge sind verschieden. PgegenPC beantwortete nicht die Frage nach vollständiger Sternneupaarung. Unser bisheriger historischer Abgleich war hier zu unscharf.

### 3.4 Der Packungssatz stimmt

Fürn=99,m=|E| und die ObergrenzenCN≤1 auf Kanten,CN≤2 auf Nichtkanten gilt

    Σ_v binom(d_v,2) ≤ 9702−m,
    Σ_v d_v² ≤19404,
    (2m)² ≤99·19404=1386².

Also m≤693. Gleichheit erzwingt durch Cauchy–Schwarz konstante Grade14 und anschließend Gleichheit in sämtlichen CN-Obergrenzen. Der Graph ist dann exakt das gesuchte SRG. Kantenlöschung bewahrt die Packungsbedingungen: gemeinsame Nachbarzahlen können nur sinken, und eine gelöschte Kante erhält sogar die schwächere Nichtkantengrenze.

Diese Umformulierung ist mathematisch sauber und für uns strategisch interessant. Ein weltweiter Neuheitsanspruch ist damit nicht belegt. Das Packungsdefizit693−m ist nicht direkt mitW vergleichbar. Bei einer nur heuristischen Löschprojektion ist die Zahl gelöschter Kanten lediglich eine obere Schranke für das minimale Löschdefizit; ein ILP-Zeitlimit darf nicht als exakt berechnetes Minimum ausgegeben werden.

### 3.5 Der vorgeschlagene Faktorversuch ist noch nicht sauber getrennt

LP ja/nein und Kugel ja/nein müssen mit gleicher Zielform, gleichem Hint, gleichem Start, gleichem Prozess-CPU-Budget und denselben Seeds verglichen werden. Nur inB3 Radiusstaffel und Neuzentrierung einzuführen vermischt mehrere Änderungen. Der alte7200s-Lauf ist eine historische Referenz, kein Ersatz für einen frischen1800s-Kontrollarm; insbesondere sind alte Solverwandzeiten wegen der Uhrenproblematik keine zuverlässigen CPU-Zeitpunkte.

Mehr Konflikte sind kein Erfolgsmaß, sondern ein diagnostisches Merkmal. Ein4-Worker-Portfolio wird nicht allein durch seine Workerzahl als LNS-Versuch ausgewiesen: tatsächlich aktive Subsolver protokollieren. Die bloße Nichtzerlegung eines Treffers beweist nicht, dass er außerhalb eines Katalogs liegt; Katalog, maximale Weglänge und etwaige monotone Einschränkung exakt definieren. Ein Sternzug ist außerdem kein „neuer Rekordmechanismus“, solange sein Nutzen nur bekannte Katalogschritte beschleunigt.

### 3.6 Weitere Präzisierungen

- „Alle bisherigen konstruktiven Suchen hieltenλ exakt“ ist für die gesamte Projektgeschichte falsch; es gab denω-Zweig. Für den jüngstenλ-Teil stimmt die Einschränkung.
- BudgetM1:25 Klassen×2 Arme×1h sind50CPUh vor Defizitberechnung, nicht48. Das ist vor Freigabe zu korrigieren.
- Die Hauptlaufskizze legt weder Crossoverhäufigkeit noch vollständige Alternativen bei fehlenden Gründerfamilien fest. „Gleiche Klasse, bessererScore“ ist bei unseren isomorphieinvarianten Scores unmöglich und wäre ein Integritätsfehler. Die Skizze ist deshalb noch keine implementierungsfertige Spezifikation.
- N[p]∪N[q]-Fenster haben von Überschneidungen abhängige Größen;29bis43 darf nicht als feste garantierte Größe benutzt werden.
- Der Literaturanschluss des Rang54-Projektors ist bestätigt: Ishida, arXiv2606.29183v2,§8.4 nennt E3=4I/7+A/7−2J/77. Neuer algorithmischer Nutzen folgt daraus nicht. Die SAT-Arbeit2604.23037 existiert ebenfalls. Symmetrieausschluss-Aussagen des Reviews werden hier nicht als neue Resultate unserer separatenC2/O3-Linien übernommen.

## 4. Die sechs Perspektiven zusammengeführt

| Perspektive | Unser Agent | Reviewer | Gemeinsame Konsequenz |
|---|---|---|---|
| Optimierer | Beweglichkeit gegen Verbesserbarkeit; neue Fensterwahl | Sternzensus, Solvermodus, Nachabstieg | Billigen vollständigen Katalog als Baseline; danach fairer Solververgleich mit bekannten Zeugen |
| Hubschrauber | Elterninformierte D/D+-Masken und passende Zufallskontrolle | Neue Gründer, Designfabrik, gegebenenfalls Symmetriequotienten | Herkunft erweitern und verteilte Freigaben testen; Quellenvielfalt von Klassenvielfalt trennen |
| Maverick | Dreiecksblöcke,λ-Schuld,Projektoren | Packung,Kontrollgraphen,Ein-Defekt-Pfade | Packung priorisieren; Blockumbauten alsλ-Alternative; ungültige Kontroll-/Defektspezifikationen zuerst korrigieren |

Die neue Evidenz verschiebt meine Priorität: Die elterninformierte Rekombination bleibt aussichtsreich, benötigt aber zunächst eine brauchbare Suchführung und einen starken gemeinsamen Nachabstieg. Die Packung erhält einen eigenständigen Erkundungsarm. Den isolierten, langen Mobilitätsversuch meines Optimierers würde ich nicht mehr unverändert rechnen; wesentliche Teile sind schon beantwortet.

## 5. Vorschlag K1: eine Kampagne mit drei getrennten Fragen

Dies ist ein Planungsangebot, keine gestartete oder bereits freigegebene neue Rechnung. Bestehende Office-C2-Läufe bleiben unberührt. Vorab Seeds, Auswahl, Budgets und Erfolgskriterien einfrieren; GC-02/08/10/11 gelten.

| Teil | Fragestellung und Umfang | CPU-Obergrenze |
|---|---|---:|
| A: Katalog und Kontrollen |25 Poolklassen, zusätzlich vorab gezogene bis1000 Archivklassen; AP gegenAP+Stern nach einheitlicher Regel. Prüfen, ob vollständige Stichprobe im Budget erreicht wird. Positive99er-Zeugen und kleine Vervollständigungsaufgaben. |24h|
| B: sauberer Faktorversuch |48 identische60er-Fenster×4 Arme(LP an/aus × Kugel aus/fest r16)×2 Seeds×1800CPU-s; Ziel und Hint überall identisch, zunächst keine Neuzentrierung. Modellbau zählt. |192h|
| C1: verteilte Rekombination |24 vorab ausgewählte Elternpaare×2 Arme(D-Maske,angepasste Zufallsmaske)×1800CPU-s; gleicher validierter Solvermodus und Nachabstieg. Beschriftung und Maskengröße kontrollieren. |24h|
| C2: Packungspilot |12 Gründer×2 gepaarte Arme(Packungs-Tabu vsλ-Abstieg+Projektion),je3600CPU-s einschließlich Projektion.24 Gründer-Armpaare statt scheinbar50h in48h. |24h|
| Reserve |Audits,Kanonisierung,Kontrollaufbau und verbuchte Nachläufe |24h|
| Gesamt | feste Konten, keine stille Aufstockung |288h|

Zwölf nutzbare CPU-Slots ergeben rechnerisch24h bei vollständiger Ausschöpfung. Praktischer Planungskorridor etwa24–32 Hoststunden unter ähnlicher Auslastung wie bisher, keine Garantie; vorgeschlagene harte Hostgrenze36h. Viele kleine Aufgaben können früh enden. Speichergrenzen und tatsächlicheCPU bestimmen die Parallelität; kein Ziel, ausschließlich zwölf Aufgaben zu erzwingen. Ein zusätzlicher4-Worker-Portfolioarm wäre ein separater Budgettausch, kein unbezahlter Zusatz.

A und technische Kontrollen kommen zuerst. B startet erst nach bestandenem Encoder-/Zeugentest. C1 folgt nur mit funktionsfähiger Rekombinationsmaske; beide Eltern müssen zulässig sein, alternative Kinder ausdrücklich prüfen. C2 benötigt einen unabhängigen Packungsverifier und eine wohldefinierte Projektion; bei fehlendem Prototyp ist dieser Teil nicht startbereit. Unverbrauchte Konten werden ausgewiesen, nicht ohne Freigabe anderen Armen zugeschlagen.

Erfolgskriterien: PrimärW<2076 für gültigeλ-Graphen bzw693 Kanten für gültige Packungen. Sekundär Verbesserung gepaarter Gründer, neue Klassen, ZeitbisTreffer und TrefferCPU, für Packungen gesicherte Defizite/Schranken. B misst zusätzlich die Wiederfindung der bekannten enthaltenen Zeugen. Verbessert ein Arm nur bekannte Sternschritte, kann das technische Suchführung bestätigen; ein darüber hinausgehender Optimierungsnutzen ist dann noch nicht gezeigt. Kein universeller Schluss aus fehlender Rückkehr am243er-Kontrollgraphen.

## 6. Alternativen und Empfehlung

**Konservativ:** NurA+B,216CPUh plus18h Reserve=234CPUh. Beantwortet sauber den Solverengpass, schafft aber noch keine neue globale Suchrichtung.

**Empfohlen:** K1 mit288CPUh. Es verbindet vorhandene Stärken, überprüfbare Ursachen und zwei begrenzte neue Richtungen. Die Katalogarbeit ist eine gemeinsame Basis, kein weiterer beliebiger Vorversuch.

**Explorativer Schwerpunkt:** NachA die freiwerdende Solverzeit vorab in Packung und neue Tripelgründer umwidmen. Größere Chance auf methodischen Erkenntnisgewinn, schwächere direkte Vergleichbarkeit und noch kein begründeter Vorteil fürW<2076. Dafür wäre eine eigene genaue Spezifikation erforderlich.

Ein memetischer Hauptlauf mit vielen zugleich geänderten Mechanismen kommt danach. Population, Familienquoten, Crossoverrate und Ersatzregeln erst anhand der gemessenen nützlichen Operatoren festlegen. Es genügt nicht, alle sechs Vorschlagslisten zusammen in einen großen Lauf zu packen.

## Primärquellen außerhalb des Projekts

- https://arxiv.org/html/2606.29183v2 ,§8.4: Projektorformel und Kontext; geöffnet/gelesen.
- https://arxiv.org/abs/2604.23037 : SAT-Arbeit, Abstract gelesen; keine pauschale Untauglichkeit vonSAT daraus abgeleitet.
- https://arxiv.org/html/2409.10620v1 : Familieλ=1,μ=2 und bekannte Beispiele; relevante Einführung gelesen.
- https://arxiv.org/abs/2308.02978 : Automorphismenarbeit; keine neueC2/O3-Entscheidung dieses Abgleichs.
