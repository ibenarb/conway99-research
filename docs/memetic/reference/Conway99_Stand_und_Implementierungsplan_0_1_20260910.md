# Conway 99: Stand nach Pong 3 und Entwurf für Version 0.1

Stand: 10. September 2026. Grundlage: drittes Pong mit `bvls.py`, die geprüften Zustände aus Runde 2, unsere bisherigen Vereinbarungen und die unten dokumentierten neuen Prüfrechnungen.

**Entscheidung:** Die Grundlage reicht für die Entwicklung einer ersten Experimentsoftware auf dem zusätzlichen Intel-Vierkerner. Der Kernversuch ist konkret: unterschiedliche zulässige Startgraphen, strukturerhaltende Ausflüge mit zeitweisen Verschlechterungen, anschließende lokale Verbesserung und Übernahme neuer gleich guter oder besserer Kandidaten. Die Erzeugung ausreichender Startdiversität und die Wirksamkeit der Bewegungen werden dabei ausdrücklich gemessen. Der bisherige Symmetrie- und Zertifizierungsstrang bleibt eine getrennte Arbeit.

In dieser Auswertung wurden Prüfrechnungen ausgeführt und der Implementierungsentwurf präzisiert. Eine neue memetische Suchsoftware wurde noch nicht implementiert oder auf dem Intel gestartet.

**1. Was der Reviewer gesehen hat**

Der wichtigste praktische Befund ist die Rückwegfalle. Ein guter Elternzustand wird durch einen zufälligen Tausch zunächst schlechter. Beginnt unmittelbar danach ein gieriger Abstieg, ist häufig die Rücknahme dieses Tausches die beste Verbesserung. Ein solcher Versuch verbraucht Rechenzeit und liefert den Elternzustand zurück.

Der Reviewer schlägt deshalb vor, einen Versuch in eine Störung durch mehrere zulässige Züge und einen anschließenden lokalen Abstieg zu gliedern. Eine kurze Rückwegsperre erschwert das sofortige Rückgängigmachen. Während des ganzen Versuchs wird der beste geeignete Zwischenstand gespeichert. Das entspricht dem Grundmuster einer iterierten lokalen Suche; die Literatur liefert dafür eine methodische Grundlage, aber keine Leistungszusage für Conway 99. [Lourenço, Martin und Stützle: Iterated Local Search](https://arxiv.org/abs/math/0102188).

Sein zweiter wichtiger Punkt betrifft Deine Diversität: Verschiedene Zufallszahlen, Beschriftungen oder Startfamilienbezeichnungen ergeben noch keine verschiedenen Graphen. Und selbst eine anfangs vielfältige Population kann durch globale Bestenauswahl zu einer einzigen Familie zusammenschrumpfen. Er empfiehlt deshalb Isomorphieprüfung, Familienquoten, Strukturbeschreibungen und ein Archiv guter Vertreter verschiedener Bereiche.

Die dritte Verbesserung ist die Bestpunktübernahme. Wenn ein Versuch zwischenzeitlich einen guten neuen Kandidaten erreicht und später wieder schlechter wird, soll dieser Fund erhalten bleiben. Damit wird aus Deiner Endpunktregel eine Regel für den besten geeigneten besuchten Zustand; die Forderung „gleich gut oder besser als der Elter“ bleibt erhalten.

Er hat außerdem die früheren Überdehnungen zu Graver-Primitivität, Zensusumfang, vermeintlichen Erfolgswahrscheinlichkeiten und Solverlaufzeiten zurückgenommen. Diese Korrekturen sind sachlich hilfreich: Direkte Rekombinierbarkeit, Erreichbarkeit über Zwischenzustände und tatsächlich gemessene Suchleistung sind verschiedene Fragen.

**2. Neue vollständige Prüfung der HoG-Nachbarschaft bis Tiefe zwei**

Ich habe sämtliche ersten und zweiten zulässigen Apex-Tausche ab dem bereits geprüften HoG-Graphen #57338 enumeriert. Ein Apex-Tausch vertauscht die Spitzen zweier disjunkter Dreiecke, entfernt vier Kanten und fügt vier hinzu; jeder Nachfolger wurde auf Grad 14 und genau einen gemeinsamen Nachbarn je Kante geprüft.

| Größe | Ergebnis |
| --- | ---: |
| Ausgangswert F | 2836 |
| Unmittelbare Apex-Nachbarn | 46 |
| Bester Wert nach genau einem Tausch | 2856 |
| Enumerierte gerichtete Wege aus zwei Tauschen | 2072 |
| Verschiedene beschriftete Endzustände nach zwei Tauschen, einschließlich Ausgangsgraph | 1102 |
| Neue beschriftete Zustände in Abstand genau zwei | 1101 |
| Bester F-Wert dieser neuen Zustände | 2896 |
| Erste Nachbarn, bei denen die Umkehrung der einzige verbessernde Zug ist | 45 von 46 |
| Erste Nachbarn, bei denen die Umkehrung der beste Zug ist | 46 von 46 |

Damit gibt es innerhalb von höchstens zwei Apex-Tauschen keinen neuen gleich guten oder besseren Zustand. Jeder erfolgreiche Ausflug dieser Art müsste mindestens drei Tausche umfassen. Ob bereits drei genügen, ist offen; Tiefe drei wurde hier nicht untersucht.

Die Deduplizierung erfolgte nach beschrifteter Adjazenzmatrix, nicht nach Isomorphieklassen. Die 1101 Zustände sind deshalb keine Behauptung über 1101 strukturell verschiedene Graphen. Die vollständigen Aussagen über die minimalen Fehlerwerte hängen von einer Isomorphieklassifikation nicht ab.

Die Prüfung dauerte in dieser Umgebung etwa 45,5 Sekunden. Das ist keine Laufzeitprognose für den Intel. Dateien: `depth2_audit.py` und `depth2_results.json`.

Dieser Befund stützt die Rückwegsperre und eine echte Störphase sehr deutlich. Er stützt keine allgemeine Behauptung, dass längere Folgen irgendwann sicher Erfolg haben.

**3. Was mathematisch bestätigt ist und was korrigiert werden muss**

**Apex und Defektsignatur.** Das vom Reviewer gelieferte BvLS-Skript wurde ausgeführt; die Konstruktion ergibt einen SRG mit 243 Knoten und Grad 22. Bestätigt wurden 891 Dreiecke, 8910 Prismen und der geprüfte Apex-Nachbar mit F = W = 288. Die Anzahl von 26730 zulässigen Apex-Tauschen aus dieser Lösung folgt aus drei Tauschmöglichkeiten je Prisma.

Der allgemeine Zusammenhang lautet, sofern ein solcher Tausch aus einer exakten Lösung möglich ist:

\[
F=W=16(k-4).
\]

Für Conway 99 ergibt das 160. Das zusätzliche Defektgradprofil des Reviewers wurde ebenfalls bestätigt. Für 99 Knoten lautet die notwendige Häufigkeitsverteilung einschließlich isolierter Knoten im Defektgraphen:

| Defektgrad | Anzahl Knoten |
| --- | ---: |
| 0 | 33 |
| 2 | 40 |
| 4 | 20 |
| 20 | 4 |
| 40 | 2 |

**Die Umkehrung ist damit nicht bewiesen:** Ein Zustand mit F = W = 160 und diesem Gradprofil ist nicht allein deshalb nachweislich einen Tausch von einer Lösung entfernt. Die richtige Programmregel ist: Profiltreffer erkennen, die nahegelegten inversen Tausche untersuchen und das Ergebnis vollständig validieren. Erst F = 0 zusammen mit den exakten Graphbedingungen ist ein Lösungsnachweis. F ist auch kein allgemeiner Abstand in Anzahl der benötigten Tausche.

**Dreierrotation.** Auch die 40 vom Reviewer untersuchten Rotationen wurden bestätigt. Sie tauschen die Spitzen dreier Dreiecke zyklisch, betreffen neun Knoten und ändern zwölf ungerichtete Paare: sechs Kanten werden entfernt und sechs ergänzt. Am BvLS-Graphen ergibt sich jeweils F = W = 432.

Es gibt jedoch keinen unabhängigen Zielzugang zu einem hypothetischen prismenfreien Graphen: Die Voraussetzungen der vorgeschlagenen Rotation enthalten bereits Prismen. In den 40 geprüften Fällen ließ sich jede Rotation exakt als Folge zweier zulässiger Apex-Tausche schreiben; die Fehlerwerte waren 0 → 288 → 432. Eine größere zusammengesetzte Störung kann trotzdem algorithmisch nützlich sein.

Für diese konkrete Konfiguration lässt sich die Formel F = W = 24(k−4) zusätzlich allgemein begründen. Die drei Spitzen bilden ein Dreieck; die drei Zweierbasen sind paarweise perfekt gematcht. Von den acht abstrakten Kombinationen der Basenmatchings verletzen vier bereits die oberen Schranken für gemeinsame Nachbarn. Die übrigen vier sind Beschriftungen des 3×3-Turmgraphen, also eines SRG(9,4,1,2). Zusätzliche interne Kanten sind wegen λ = 1 ausgeschlossen. Diese vollständige Fallprüfung ist im Prüfskript enthalten.

In einem eingebetteten solchen Neunergraphen sind die gemeinsamen Nachbarn jedes internen Paares bereits vollständig vorhanden. Daher kann kein Außenknoten an zwei seiner Knoten angrenzen. Die neun äußeren Nachbarmengen sind folglich disjunkt und haben jeweils k−4 Elemente. Die Rotation erhält intern den Turmgraphen und ändert vier Inzidenzen je Spitze sowie zwei je Basisknoten. Dadurch entstehen genau [3·4 + 6·2](k−4) = 24(k−4) fehlerhafte Paare mit Residuum ±1. Für k = 14 wären das 240, **falls die erforderliche Konfiguration in einer Lösung existiert**. Die allgemeine m-Rotationsleiter bleibt unbelegt und wird keine harte Programmannahme.

**Prismenzahl.** Die Nachfrage des Reviewers lässt sich aus Reimbayevs Sechsknotenzählung beantworten. Dort ist der Prismenzähler n₁ durch n₁ = nk(k−2)/12 − n₃/3 ausgedrückt; n₃ bleibt ein freier Zähler. Für Conway 99 folgt:

\[
N_{\mathrm{Prisma}}=1386-\frac{n_3}{3},
\qquad N_{\mathrm{Apex}}=4158-n_3.
\]

Diese Zählidentität allein erzwingt keine positive Prismenzahl. „Frei“ bedeutet hier auch nicht, dass jeder rechnerisch mögliche Wert realisierbar wäre. [Reimbayev, Abschnitt 2, Seite 3](https://arxiv.org/pdf/2508.03377).

**Minimaler H84-Tausch.** Die bereits bestätigte scharfe Untergrenze bleibt bestehen: Unter den strengen Kopplungsbedingungen sind mindestens acht Außenknoten beteiligt; die gelieferte Einbettung entfernt acht und ergänzt acht Kanten. Das ist kein einzelner alternierender Achterzyklus mit vier entfernten und vier ergänzten Kanten. Der H84-Tausch ist eine gekoppelte Änderung mit sechzehn geänderten ungerichteten Paaren.

Die erneut behauptete Vollständigkeit der Produktklassifikation bei sechzehn Paaren folgt allerdings nicht aus dem angegebenen Dimensionsargument. Auf den acht Rahmenkanten eines K₂,₄ hat die eingeschränkte Inzidenzmatrix Rang fünf und damit Kerndimension drei. Das wurde exakt mit rationaler Arithmetik geprüft. Es widerlegt die benutzte Annahme „auf acht Koordinaten immer Kerndimension zwei“, nicht bereits die Produktklassifikation selbst. Die bekannten Produkte bleiben gültige Operatoren; ihre Vollständigkeit wird nicht behauptet.

**4. Präzisierungen am Suchentwurf**

Die Aussage „alle sieben Barrieren sind behoben“ geht zu weit. Rückwegsperren, neue Strukturen bei Gleichstand und Bestpunktspeicherung beheben konkrete Fehlmechanismen. Sie beweisen weder Zusammenhang des zulässigen Suchraums noch das Überschreiten beliebig breiter Barrieren oder Konvergenz zu F = 0.

Aus dem bisherigen einzelnen 100-Schritt-Lauf ergibt sich eine Nettozunahme von 22,52 Fehlerpunkten je Schritt. Das ist noch kein stationärer Erwartungswert unabhängiger Schritte. Eine Formel für die Endpunktannahme aus Mittelwert und Streuung allein ist deshalb nicht belastbar. Wir messen die Erfolgsraten verschiedener Folgenlängen direkt über wiederholte Versuche und rechnen deren Kosten mit.

Bei Bestpunktspeicherung ist außerdem zwischen Endpunkt und unterwegs gefundenem Kandidaten zu unterscheiden: Verlängert man denselben Pfad unter Beibehaltung seines Anfangs, kann ein schon gefundener geeigneter Zwischenstand nicht wieder verloren gehen. Die Chance, irgendwann einen solchen Zustand besucht zu haben, sinkt durch diese Verlängerung nicht. Die Effizienz je CPU-Sekunde kann dennoch sinken. Adaptive Folgenlängen bleiben damit sinnvoll untersuchbar.

Ein Bestpunktspeicher darf den ursprünglichen Elternzustand oder dessen bloße Umnummerierung nicht als erfolgreichen Nachfahren melden. Gespeichert wird der beste vollständig zulässige neue Kandidat. Scheitert der Versuch, bleibt der Elternzustand erhalten.

Die vom Reviewer vorgeschlagenen Neustarts brauchen eine saubere Buchführung: Ein schlechterer frischer Start kann eine alte Linie nicht ersetzen und zugleich deren aktuelle Fehlerfolge monoton halten. Ein Neustart beendet deshalb ausdrücklich eine Linie und eröffnet eine neue Kennung; das Bestarchiv bleibt erhalten. In der ersten Vergleichsserie bleiben automatische schlechtere Neustarts ausgeschaltet. Eine spätere Serie kann sie gesondert testen.

Ebenso muss ein Kind, das einen anderen ähnlichen Kandidaten ersetzt, mit genau diesem ersetzten Kandidaten verglichen werden. Ein Vergleich allein mit seinem biologischen Elternzustand garantiert keine Monotonie des ersetzten Platzes. Version 0.1 verwendet daher zunächst den einfacheren Elternvergleich und feste Familienplätze.

**5. Konkreter Vertrag für Version 0.1**

**Zustände und harte Bedingungen.** Zwei ausdrücklich getrennte Versuchsarme bleiben vorgesehen:

| Arm | Harte Bedingungen | Rolle und erste Bewegungen |
| --- | --- | --- |
| H84/Ω | Binäres symmetrisches H mit Nulldiagonale; kanonischer Rahmen; PH = 2J − (C+I)P; H-Zeilengrad 12 | Hauptarm für Deinen Rahmenansatz; validierte gekoppelte Produkte und ihre Folgen |
| Wurzelfreier λ-Arm | Einfacher 14-regulärer Graph auf 99 Knoten; jede Kante hat genau einen gemeinsamen Nachbarn | Getrennter Vergleichsarm; Apex-Tausche und zusammengesetzte Störungen |

Die harten Bedingungen müssen bei jedem akzeptierten Einzelzug gelten. Eine spätere Reparaturphase mit zeitweise verletzten Bedingungen wäre ein eigens gekennzeichneter zusätzlicher Operator. Für die erste Version sind solche unzulässigen Zwischenzustände nicht nötig.

HoG gehört zum zweiten Arm. Er erfüllt den strengen H84-Rahmen an keiner Wurzel unverändert und darf daher nicht einfach als Ω-Start deklariert werden. Ein Austausch zwischen den Armen setzt einen erfolgreichen vollständigen Gültigkeitstest für den Zielarm voraus. Der zweite Arm ersetzt die H84-Bedingungen des ersten nicht.

Für beide Arme wird derselbe vollständige Fehlerwert verwendet. Für eine 99×99-Adjazenzmatrix A mit Grad 14:

\[
R=A^2+A-12I-2J,\qquad
F=\tfrac12\|R\|_F^2=\sum_{i<j}R_{ij}^2.
\]

W zählt zusätzlich die verletzten ungeordneten Paarbedingungen. F entscheidet über Qualität; W und das Residuenprofil erklären sie. Das exakte vollständige Zielspektrum wird nicht als leicht erfüllbare Startbedingung verlangt: Zusammen mit den Graphbedingungen wäre dies schon die gesuchte Lösung.

**Starterzeugung als eigenes Modul.** Die Software erhält getrennte Anbieter für importierte geprüfte Projektzustände, randomisierte Konstruktion beziehungsweise Reparatur unter den harten Bedingungen und Abkömmlinge unterschiedlicher algebraischer Startkonstruktionen. Jeder Anbieter dokumentiert seine tatsächliche Methode, Herkunft, Zufallsinitialisierung, Kosten und Erfolgsquote. Das sind Implementierungsaufgaben; ausreichend schnelle und vielfältige Generatoren sind noch nicht nachgewiesen.

Mehrere Zufallsinitialisierungen desselben Konstruktionsprinzips zählen nicht als mehrere Prinzipien. Mehrere Umnummerierungen desselben Graphen zählen nicht als mehrere Strukturen. Für den Beginn stehen die geprüften Ω-Beispiele und HoG als Kontrollen zur Verfügung; sie belegen noch keine hinreichend vielfältige Population. Eine gewünschte Population von beispielsweise 32 Mitgliedern wird nur mit tatsächlich verschiedenen zulässigen Kandidaten gefüllt. Fehlen diese, meldet der Starterzeugungsversuch die kleinere erreichte Population und verbrauchte Zeit. Er erzeugt keine scheinbare Vielfalt durch Kopien.

Die alten guten Adjazenzmatrizen und die genaue frühere Operatorimplementierung fehlen weiterhin im vorliegenden Austausch. Ihr Import ist vorgesehen; historische Scoreangaben allein werden nicht als vergleichbare Ausgangsmessung verwendet. Die Entwicklung des neuen Kerns kann dennoch beginnen.

**Ein Nachfahrenversuch.** Vom unveränderten Elternzustand mit F₀ aus wird eine zufällige Länge L aus einem dokumentierten Bereich gewählt. Es folgen L zulässige Störzüge, bei denen F steigen darf. Direkte Rücknahmen und kurzfristige Wiederbesuche werden nach einer begrenzten Taburegel vermieden. Eine leere erlaubte Nachbarschaft beendet die Phase, statt eine Endlosschleife auszulösen.

Danach folgt ein lokaler Abstieg mit eigenem Budget für Zugauswertungen. Der beste zulässige neue Zwischenstand aus beiden Phasen bleibt gespeichert. Ein gegenüber F₀ strikt besserer Kandidat ist übernahmefähig; bei gleichem F kommen kanonische Neuheit und die vereinbarte Diversitätsregel hinzu. Ohne geeigneten Fund bleibt der Elter erhalten. Jeder Versuch protokolliert insbesondere Rückkehrkopien, neutrale neue Funde, echte Verbesserungen, Budgetende und fehlende Züge getrennt.

Länge, Anzahl der Versuche je Elter und Abstiegsbudget sind verschiedene Parameter. Der Programmcode verwendet dafür unterschiedliche Namen; das Symbol k bleibt in mathematischen Aussagen dem Graphgrad vorbehalten. Längere Störungen werden nach gemessener Stagnation häufiger ausprobiert, bleiben aber durch ein endliches Gesamtbudget begrenzt.

**Population und Auswahl.** Eine Runde bearbeitet einen festgehaltenen Populationsstand. Pro Elter entstehen höchstens q abgeschlossene Versuche; Rücklauf zum Elter zählt nicht als Kind. Der beste geeignete Nachfahre ersetzt zunächst seinen eigenen Elter. Dadurch bleiben Familienplätze erhalten. Die globale Auswahl nur der n niedrigsten Fehlerwerte aus allen Kindern wird nicht als Standard verwendet, weil sie Deine gewollte Vielfalt leicht verdrängt.

Ein unverlierbares globales Bestarchiv und ein kleines Archiv nach Strukturmerkmalen ergänzen die Population. Das Prinzip eines besten Vertreters je Merkmalszelle ist durch MAP-Elites angeregt. [Mouret und Clune: Illuminating search spaces by mapping elites](https://arxiv.org/abs/1504.04909). Archivplätze mit anderen Merkmalen dürfen höhere F-Werte enthalten; das ändert die Annahmeregel einer laufenden Elternlinie nicht.

**Diversität.** Für strukturelle Identität ist die kanonische Form des ungewurzelten 99-Graphen maßgeblich. Im Ω-Arm kommt eine geeignete gewurzelte beziehungsweise gefärbte Form hinzu, die die Rahmenstruktur respektiert. Unterschiedliche Wurzeln desselben Gesamtgraphen können verschiedene Arbeitsdarstellungen sein; im Bericht bleiben sie eine ungewurzelte Klasse. Kanonisierung wird bei Aufnahme und Archivierung eingesetzt; ihre Kosten werden auf der Zielmaschine gemessen.

Als günstige Beschreibungen dienen Residuenhistogramm und Defektgradprofil. Spektrum und längere Zykluszahlen sind optionale Diagnosen bei Aufnahme, nicht Pflichtberechnungen bei jedem Zug. Deskriptorabstände erkennen nicht alle Isomorphien und ersetzen daher keine Identitätsprüfung.

Im λ-Arm gilt F = 4(C₄−2079). Ein Raster mit den Achsen F und Vierecküberschuss enthält dort zweimal dieselbe Information. Geeigneter ist zum Beispiel F zusammen mit maximalem Defektgrad. Gemeldet werden Zahl der kanonischen Klassen, Familienbelegung, nahe Deskriptorabstände und die Verteilung neutraler beziehungsweise verbessernder Aufnahmen.

Kurze standardisierte Abstiege verschiedener Mitglieder können gelegentlich ähnliche Suchgebiete sichtbar machen. Ihre Endpunkte hängen jedoch von Budget, Zugreihenfolge und Zufallsentscheidungen ab und müssen keine lokalen Minima sein. Derselbe beobachtete Endpunkt ist ein Hinweis auf Ähnlichkeit, kein Beweis vollständiger Redundanz.

**Vier Kerne und Laufbetrieb.** Ein gemeinsamer Arbeitsvorrat wird von höchstens vier Suchprozessen bearbeitet. Jeder Prozess verwendet einen Rechenthread; numerische Bibliotheken und spätere Solver dürfen nicht zusätzlich alle Kerne belegen. Populationsgröße und Prozesszahl sind unabhängig. Eine anfängliche Aufteilung von zwei Arbeitern pro Versuchsarm ist eine organisatorische Startkonfiguration, kein behauptetes Optimum.

Aufgaben erhalten eindeutige Kennungen und daraus abgeleitete Zufallsinitialisierungen. Runden werden in fester Reihenfolge ausgewertet, damit die Fertigstellungsreihenfolge keine verdeckte Selektionsregel wird. Prüfbare Checkpoints enthalten Population, Archive, Zufallszustände, Konfiguration und Zähler. Wiederaufnahme, begrenzte Laufzeit und regelmäßige Statusmeldungen gehören zur ersten Version. Eine Restzeit wird nur für ein festes Rechenbudget angegeben, nicht bis zu einer unbekannten Lösung.

Intel-Modell, Betriebssystem und verfügbarer Arbeitsspeicher sind vor Auslieferung zu prüfen. Angaben der anderen Projektmaschine werden nicht übertragen. Eine kurze Kalibrierung bestimmt Zugauswertungen pro Sekunde, Speicherkosten und sinnvolle Aufgabenbudgets.

**6. Was zunächst Erweiterung bleibt**

Eine begrenzte exakte Fensterreparatur ist als nächster stärkerer Operator sinnvoll vorgesehen. Sie wird gebraucht, falls die verfügbaren gekoppelten Tauschfamilien wenig wirksame Bewegung liefern. Sie muss aber korrekt formuliert und gegen gleiche CPU-Kosten verglichen werden.

Werden nur Kanten innerhalb einer Knotenmenge S geändert, können sich gemeinsame Nachbarzahlen sowohl für Paare innerhalb von S als auch für Paare zwischen S und außen ändern. Nur Paare mit beiden Endpunkten außerhalb bleiben unverändert. Eine Reparatur, die ausschließlich interne Fehler zählt oder prüft, kann daher einen falschen Erfolg melden.

W ist als Funktion der Adjazenzvariablen nicht von selbst linear: Bereits gemeinsame Nachbarzahlen enthalten Produkte von Einträgen. Ein exaktes lineares oder CP-SAT-Modell braucht zusätzliche Variablen und die entsprechenden Beziehungen. Wird W als Ersatzzielfunktion optimiert, wird das ausdrücklich protokolliert; die Übernahme entscheidet weiterhin der vollständig berechnete F-Wert. Fenstergröße, Lösungszeit und Erfolg sind Versuchsergebnisse und keine zugesicherten Eigenschaften.

Rekombination zweier Eltern, breitere Ω-Änderungen und zusätzliche Rotationen bleiben separat messbare Erweiterungen. Ihre Schnittstellen werden vorgesehen. Version 0.1 benötigt keine Behauptung, dass diese Familien den gesamten zulässigen Raum verbinden.

**7. Welche erste Versuchsserie etwas entscheidet**

Zuerst wird für jeden Arm geprüft, ob er genügend verschiedene zulässige Starts erzeugt und welche Bewegungen darauf tatsächlich verfügbar sind. HoG dient dabei als kontrollierter schwieriger Ausgangspunkt im λ-Arm; die drei Ω-Beispiele sind Kontrollen für den Rahmenarm. Keiner dieser Bestände ersetzt die Prüfung weiterer Startfamilien.

Dann werden mehrere kurze Wiederholungen mit gleichem CPU-Budget verglichen: reine Zufallsfolgen mit Bestpunktspeicherung gegen Störung plus lokalen Abstieg. Für den Nutzen Deiner Diversitätsidee folgt ein eigener Vergleich mit gleicher Starterzeugung und gleichem Bewegungsverfahren, einmal mit und einmal ohne Erhalt verschiedener Familien beziehungsweise Strukturbereiche. Werden gleichzeitig Startverfahren, Operatoren und Auswahl geändert, lässt sich ein Vorteil nicht sauber der Diversität zuschreiben.

Zentrale Größen sind Verbesserungen pro CPU-Stunde, Erfolgsrate nach Störlänge, Zahl neuer gleich guter Klassen, Anteil der Rückkehrkopien, erhaltene Vielfalt und validierter Bestwert. Zugzahl allein ist kein ausreichender Erfolgsmesser; viele Züge können in denselben Bereich führen. Ein längerer Lauf wird anhand dieser Messungen begründet.

Der unverlierbare Bestwert kann nur sinken oder gleich bleiben. Bei der beschriebenen Elternersetzung gilt dies auch für jede fortgeführte Linie. Daraus folgt keine Annäherung an null: Ganzzahlige Fehlerwerte können nach endlich vielen Verbesserungen auf einem Plateau stehenbleiben. Das erste Ziel ist ein kontrollierter Nachweis, dass wir neue nützliche Suchgebiete erreichen und Vielfalt erhalten.

**8. Belege und Reproduzierbarkeit**

Das Begleitpaket enthält das unveränderte dritte Pong und sein BvLS-Skript, die neuen Prüfskripte samt Ergebnissen, den benötigten HoG-Graphen, die gemeinsame Prüfroutine aus Runde 2 und die benötigten Rahmendaten. `structural_checks.py` prüft BvLS, die Defektsignatur, die Zerlegung der 40 Rotationen und das Dimensionsgegenbeispiel. `depth2_audit.py` enumeriert die hier ausgewertete vollständige beschriftete Nachbarschaft bis Tiefe zwei.

Die Prüfer verwenden Python und NumPy. Sie sind kein Suchprogramm für einen Dauerlauf. Dateibyte-Prüfsummen und die beim Audit benutzten Laufzeitversionen liegen dem Paket bei. Alle numerischen Aussagen in Abschnitt 2 und die neuen Strukturkontrollen sind aus diesen Dateien nachvollziehbar. Nicht untersucht wurden Tiefe drei, eine breite Starterzeugung, die Laufgeschwindigkeit auf dem Intel und die Wirksamkeit einer implementierten Fensterreparatur.
