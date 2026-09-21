# λ-Suche: Diagnose, neuer Dreieckstausch und begrenzter Vergleich

> Nachtrag: Die Versuchsempfehlung wurde nach dem Reviewer-Abgleich geändert.
> Den hier beschriebenen 18-CPU-h-Versuch nicht unverändert starten; siehe
> [Abgleich und neue Priorität](../lambda_review_20260921/ABGLEICH.md).
> Die nachfolgend dokumentierten ursprünglichen Prüfungen bleiben erhalten.

Stand: 21.09.2026. Eigenständige Codex-Bearbeitung des gemeinsamen Auftrags A–E.
Referenzcode: `6cf206b7a7942672ef806c70d9e590bf27a1973c`, Zweig `memetik`.

**Empfehlung:** den Zugkatalog um allgemeine zyklische Apex-Tausche auf drei
Dreiecken erweitern und gegen Fast-A0 prüfen. Als zweite Variante dieselbe
Erweiterung mit dauerhaftem Familienschutz und familienweiser Elternwahl
vergleichen. Der nächste Vergleich ist implementiert, aber nicht gestartet.
Vorgeschlagen sind **18 Worker-CPU-Stunden**, zusätzlich höchstens 10 CPU-Minuten
für Kontrollen und 10 CPU-Minuten für den Python-Controller. Windows-Abfragen
sind gesonderte Infrastruktur. Keine Freigabe einer Hauptkampagne.

Der wichtigste neue Befund ist stärker als eine Stagnationsvermutung:
`gen-lambda-13` ist unter dem bisherigen, vollständig aufgezählten Katalog
isoliert. Der neue Operator liefert dort 363 gültige Züge, davon 33 mit kleinerem
F. Damit ist eine tatsächliche Erweiterung der Erreichbarkeit belegt, auch
modulo Isomorphie: ein anderes F kann nicht durch Umbenennung entstehen.

## A. Eigene Nachprüfung und Diagnose

### Quellenlage

Beide Originalpakete wurden beschafft und lokal gelesen. Es fehlt kein
Ergebnispaket mehr. Ihre SHA256-Werte sind:

- `comparison_verified.tar.gz`: `ada91cfa86f4d2ba44e26c6066197957668b211cfdea86d7637ad79bd0f64024`.
- `move_accel_verified.tar.gz`: `1de55615b10dc01fd9300a8738da4613a88832b9d95e3a8376ce5c477c0f71ed`.

`diagnose.py` prüfte erneut alle 885 beziehungsweise 151 Inhaltsprüfsummen,
alle 144 beziehungsweise 48 Vergleichsjobs und ihre Task-/Resultatquittungen,
CPU-Grenzen, monotone Bestwertkurven und Anfangs-/Endwerte. 50 beziehungsweise
41 unterschiedliche (beschrifteter Graph, Arm)-Kombinationen wurden über
unabhängige Nachbarschaftsmengen nachgerechnet, einschließlich aller fünf
Scores. Die gespeicherten Isomorphiezertifikate wurden mit pynauty reproduziert.
Alle durch die Fingerprints referenzierten Quelldateien stimmen byteweise mit
dem ausgecheckten Referenzstand überein. Tatsächliche Workerzeit:
143,9219716878 beziehungsweise 3,9740038103 CPU-Stunden.

Gelesen wurden `search.py`, `moves.py`, `worker.py`, `evaluate.py`, `generate.py`,
`common.py`, `runtime.py`, `resources.py`, `progress.py`, `fast_moves.py`,
Beschleunigungs-Worker/-Kontrollen, `test_fast.py`, die tatsächlich importierten
`escape_0_2/operators.py`, `memetic_v2/core.py` und `verify.py` sowie die beiden
referenzierten Implementierungsberichte. Die alten Escape-/Minimax-Ergebnisse
werden hier nicht als eigene neue Evidenz verwendet.

### Evidenztabelle

| Eigener Befund | Interpretation | Alternative / Grenze | Unterscheidende Prüfung |
|---|---|---|---|
| HoG57338: 46 Apex-Züge, 0 alte Rotationen; keine Verbesserung in W/L1/F | Exaktes striktes Ein-Schritt-Minimum **dieses Katalogs** für W/L1/F | Kein globales Minimum und keine Aussage über größere Züge | Neuer Dreierkatalog und Mehrschrittpfade |
| Jeder dieser 46 Züge verschlechtert W, L1 und F | Erste Schritthürden mindestens +4 W, +14 L1, +20 F, jeweils separat minimiert | Diese drei Minima stammen nicht notwendig vom selben Zug; keine exakte gesamte Fluchtbarriere | Beobachtete Pfadmaxima und Rückkehrquote aufzeichnen |
| `gen-lambda-13`: 0 Apex, 0 alte Rotation, vollständig enumeriert | Isolierter Zustand im alten reversiblen Katalog | Andere Lifts müssen nicht isoliert sein | 363 neue Dreierzyklen, 33 F-Verbesserungen nachgewiesen |
| 48 von 72 langen λ-Läufen enden mit ausschließlich HoG-Herkunft | Reale Herkunftsverarmung der Populationen | Herkunftsetikett ist keine Strukturklasse; HoG könnte tatsächlich überlegen sein | CYCLE_QUOTA gegen CYCLE mit gleichen Eingängen |
| Alle 24 kurzen λ-Läufe behalten alle drei Familien | Der kurze Beschleunigungstest zeigt keine vollständige Familienverdrängung | Präsenz bedeutet nicht genügend Elternzeit | Elternauswahlen je Familie zusätzlich messen |
| Familienschutz nur in Epochen 0–4; 16 Kinder pro Selektion | Erste ungeschützte Selektion nach 96 zulässigen Episoden; kürzere Jobs erreichen sie oft nicht | CPU-Ende kann Kinder unzulässig machen; Episoden sind nicht immer Selektionseingänge | Epochengenaue Familienhistorie |
| Linf-Bestgraph (2,262,2532) hat 39 Apex-Züge, davon 5 W- und 2 L1-/F-Verbesserungen | Er ist eine konkret bewegliche alternative Startlage | Beweist keinen Weg unter W=2180 oder L1=2398 | Diesen Graphen in alle Startpopulationen aufnehmen |
| Nicht angenommene Nachbarn erreichen den alten `on_best`-Callback nicht | Informationen gehen trotz Berechnung aller Scores verloren | Ein solches Archiv allein verbessert keine Suche | Passives Vierzielarchiv in allen Varianten; Migration zunächst aus |
| Alte Rotation verlangt ein Dreieck der Spitzen und perfekte Matchings zwischen Basen | Der implementierte Katalog enthält starke lokale Strukturfilter | Daraus folgt keine globale erhaltene Symmetrie | Filter weglassen und sämtliche λ-Bedingungen am Ergebnis prüfen |

Im langen Vergleich endeten zusätzlich 11 Populationen mit HoG+Lift, 10 mit
HoG+Packung und nur 3 mit allen drei Familien. Im primären W-Ziel waren 13 von
18 Endpopulationen ausschließlich HoG. Das ist in `AUDIT.json` nachprüfbar.

**Diagnose:** mindestens zwei verschiedene Mechanismen überlagern sich:
HoG57338 liegt hinter einer echten lokalen Hürde; zumindest ein wichtiger Lift
ist durch den Katalog vollständig blockiert. Ein dritter Mechanismus ist die
spätere Selektion gegen schlechter startende Familien. Vierfach mehr Episoden
beseitigt diese Ursachen nicht automatisch. Die Befunde beweisen aber auch
nicht, dass HoG-Suche oder Fast-A0 langfristig erfolglos bleiben müssen.

### Budget- und Instrumentierungsfallen im bisherigen Code

- Das Feld `minimum_reached` bedeutet nur: untere angeforderte
  Perturbationslänge erreicht. Es bezeichnet **kein lokales Minimum**.
- `STALLED_SAMPLED` bedeutet: keine Verbesserung unter den bis zu 32 aktuell
  erzeugten Nachbarn. Nur unsere gesonderten vollständigen Zensen rechtfertigen
  die obigen exakten Ein-Schritt-Aussagen.
- Die Quellengewichte 90:10 sind Auswahlgewichte der Streams, keine garantierten
  Anteile realisierter Züge. Ein leerer Rotationsstrom kostet trotzdem Zeit.
- Die 45/75-CPU-Sekunden-Grenzen können Störungen bzw. Abstiege abschneiden;
  ausgeschöpfte Gesamtzeit und unvollständige Episoden sind getrennt zu berichten.
- Der A0-Teil besitzt bereits unbeschränkt verschlechternde gültige
  Perturbationen. „Erlaube erstmals Verschlechterungen“ wäre eine falsche Diagnose.
- A1-Gedächtnis und Fehlschlagszähler hängen an der Herkunftslinie, nicht an einem
  mathematisch definierten Becken. Seine vorhandenen Ergebnisse widerlegen
  weder Tabusuche noch einen anders definierten Barrierenversuch.
- Herkunft `HoG` bleibt nach vielen Trades bestehen; `fixed_source_template_holds`
  prüft feste Labels, nicht alle umnummerierten Darstellungen.

## B. Mathematik, Operator und überprüfbare Implementierung

### Exakte Hypergraphenbeschreibung

Ein gültiger λ-Graph besitzt 693 Kanten. Jede Kante liegt wegen λ=1 in genau
einem Dreieck. Diese Dreiecke bilden deshalb ein lineares 3-uniformes
Hypergraphensystem mit 231 Tripeln. Die 14 Nachbarn jedes Knotens sind in sieben
Paare aufgeteilt: der Hypergrad jedes Knotens ist sieben.

Umgekehrt liefert ein lineares, 3-uniformes, 7-reguläres System einen einfachen
14-regulären 2-Sektionsgraphen. **Linearität allein genügt nicht für λ=1.**
Drei verschiedene Tripel können die drei Paare xy, yz, zx enthalten und damit
ein zusätzliches Graphdreieck bilden. Diese Konfiguration ist genau ein
Berge-Dreieck. Ohne Berge-Dreiecke liegt jede Graphkante nur in ihrem eigenen
Tripeldreieck; damit gilt λ=1. Die äquivalente Inzidenzgraph-Bedingung lautet:
bipartit, Grade 7 und 3, keine 4- oder 6-Zyklen, also Taillenweite mindestens 8.
Dies ist eine direkte Herleitung, kein Literatur-Neuheitsanspruch.

### Zielfunktionen liefern unterschiedliche Informationen

Sei n_j die Anzahl der **Nichtkanten** mit j gemeinsamen Nachbarn. Dann gilt

\[
\sum_j n_j=4158,\qquad \sum_j j n_j=8316,\qquad
\sum_j(j-2)n_j=0.
\]

Begründung: Alle ungeordneten Paare erhalten zusammen
99·binom(14,2)=9009 gemeinsame Nachbarschaften; davon entfallen 693 auf Kanten.
Folglich

\[
L_1=2(2n_0+n_1),\qquad W=4158-n_2,\qquad
F=4C_4-8316=4(C_4-2079).
\]

Die letzte Formel folgt aus
C4 = 1/2 · Summe über alle Paare binom(c_uv,2); Kanten tragen hier null bei.
Sie gilt hier für den gültigen λ-Arm. Damit ist L1 stets gerade und F durch 4
teilbar. Am HoG57338: n0=89, n1=1021, n2=1976, n3=948, n4=121, n5=3;
L1=2398, C4=2788, F=2836. Die Formeln wurden rechnerisch kontrolliert.

Der vorhandene W-Rekord 2180 bei F=2840 enthält somit einen 4-Zyklus mehr als
HoG57338. Das ist kein Fehler: W minimiert die Zahl falscher Paarbedingungen,
F deren quadratische Streuung. W mit L1-Tie-Break bleibt deshalb das primäre
Ziel. F kann strukturierte Alternativwege eröffnen; L1 misst die Gesamtmasse der
Defizite und Überschüsse. Linf begrenzt Spitzenfehler, ohne den Gesamtfehler
notwendig zu senken. Keines ersetzt stillschweigend W.

### Alter und neuer Operator

Apex ersetzt zwei disjunkte Tripel `{a,b,c}`, `{d,e,f}` durch `{a,b,d}`, `{c,e,f}`.
Es löscht vier und ergänzt vier Graphkanten. Die Basiskanten ab und ef bleiben.
Gradgleichheit ist konstruktiv; fehlende neue Kanten und die abschließende
λ-Prüfung sind zwingend. Derselbe Tausch rückwärts ist die Inverse.

Die bisherige Rotation wählt Spitzen t0,t1,t2, die selbst ein Dreieck bilden,
und drei disjunkte Zweierbasen B0,B1,B2. Zwischen jedem Basenpaar fordert der
Code ein perfektes Matching. Die sechs Spitzen-Basis-Kanten werden zyklisch
umgehängt. Diese Filter bleiben beim neuen Operator nicht vorausgesetzt.

**Neuer allgemeiner Dreierzyklus:** Wähle drei paarweise disjunkte vorhandene
Tripel Ti=Bi∪{ti}, |Bi|=2. Ersetze sie gleichzeitig durch Bi∪{t(i+1 mod 3)}
oder die umgekehrte Orientierung. Es werden sechs Kanten gelöscht und sechs
ergänzt. Alle neun Knotengrade bleiben gleich. Erforderlich sind:

1. alle drei alten Tripel vorhanden, neun verschiedene Knoten;
2. alle sechs neuen Kanten vorher nicht vorhanden;
3. nach Anwendung haben alle Kanten mit mindestens einem betroffenen Endpunkt
   genau einen gemeinsamen Nachbarn.

Unberührte Endpunkte haben unveränderte Nachbarschaften. Ihre gemeinsame
Nachbarzahl bleibt daher unverändert. Die Prüfung in Punkt 3 erfasst sämtliche
möglicherweise veränderten λ-Bedingungen, einschließlich **beibehaltener**
Kanten. Damit ist die Erhaltung aller harten Bedingungen bewiesen. Die inverse
zyklische Umhängung erfüllt dieselben Voraussetzungen am Ergebnisgraphen.
Ein Trade muss nicht in gültige Apex-Einzelschritte zerfallen: der isolierte
Lift liefert bereits ein Gegenbeispiel zur generellen Zerlegbarkeit.

### Effiziente vollständige Erzeugung

Ein zunächst getesteter Zufallsvorschlag erzeugte in je 100.000 Versuchen auf
sechs Zuständen keinen gültigen Dreierzyklus. Das war eine schlechte
Erzeugungsstrategie, kein Nachweis fehlender Züge (`PROBE.json`).

Die Implementierung verwendet deshalb die 3·231=693 orientierten Tripel (B,t).
Ein gerichteter Kompatibilitätsbogen i→j bedeutet: Basis Bi kann Spitze tj
übernehmen, während tj seine alte Basis Bj verliert. Für jedes u∈Bi prüft sie

\[
(N(u)\setminus\{t_i\})\cap(N(t_j)\setminus B_j)=\varnothing,
\]

zusätzlich zu Disjunktheit und dem Fehlen neuer Kanten. Die neue Basenpartner-
Nachbarschaft liefert dann genau den einen gewünschten gemeinsamen Nachbarn
an der neuen Kante. Gerichtete Dreierzyklen in diesem Hilfsgraphen erzeugen
Kandidaten; danach folgt die vollständige lokale λ-Prüfung. Die kleinste
Indexposition und ein Move-Set verhindern doppelte Ausgaben.

Pseudocode:

    orientierte Tripel aufstellen
    alle zulässigen gerichteten Übernahmen i→j vorberechnen
    für i→j und k in ausgehend(j) ∩ eingehend(i):
        neun verschiedene Knoten und kanonischen Umlauf prüfen
        sechs Kanten gleichzeitig umhängen
        alle betroffenen Kantenbedingungen prüfen
        gültigen, bisher nicht ausgegebenen Trade liefern

Vorbereitung O((3T)^2) mit Bitmengen; danach gerichtete Dreierzyklen und lokale
Prüfungen, im gröbsten Fall O((3T)^3) Kandidatenarbeit. Keine Behauptung einer
linearen Laufzeit. Bei T=231 dauerte die reine Aufzählung an den drei zuerst
geprüften Zuständen in dieser Entwicklungsumgebung etwa 0,21–0,23 CPU-Sekunden;
das sind keine Ryzen-Durchsatzwerte. Der Hilfsgraph wird für jeden neuen Zustand
neu aufgebaut. Es gibt keinen ungültigen zustandsübergreifenden Cache.

### Kontrollen und konkrete neue Nachbarn

| Zustand | Neue Dreierzyklen | W/L1-verbessernde Züge | F-verbessernde Züge |
|---|---:|---:|---:|
| HoG57338 | 24 | 0 | 0 |
| gen-lambda-13 | 363 | 0 | 33 |
| claude_v01_c | 504 | 151 | 236 |
| gen-lambda-08 | 308 | 308 | 33 |
| Bisheriger W=2180-Endpunkt | 27 | 0 | 0 |
| Bisheriger Linf=(2,262,2532)-Endpunkt | 27 | 0 | 0 |

Insgesamt 3.791 Trades auf den 16 festgelegten Gründern wurden vollständig
angewandt, unabhängig auf Grad/λ/Scores geprüft und exakt invertiert. Alle
auf diesen Zuständen vorhandenen alten Rotationen sind im neuen Katalog
enthalten. 66 der 363 Züge auf gen-lambda-13 verlassen seine **feste**
Dreierpartition. Das beweist nicht, dass der Zielgraph keine andere
Dreifärbung oder Lift-Darstellung besitzt.

Weitere Tests: vollständiger Vergleich mit naiver Enumeration auf zwei kleinen
Graphen; positive Inversen; Ablehnung eines zusätzlichen extern verursachten
Dreiecks trotz gültigem Ausgangs-λ; Ablehnung überlappender Tripel und falscher
Orientierung; permanente Quoten ohne Isomorphieklone; passives Erfassen eines
für W verworfenen, für Linf besseren Nachbarn; Ablehnung einer falschen
F=0-Behauptung. Der unabhängige Verifikator erkennt den 9-Knoten-Rookgraphen als
positives srg(9,4,1,2)-Kontrollbeispiel. Fünf Testmethoden bestanden.
`CONTROLS.json` enthält die vorher ausgeführten vier Methoden und die 3.791
realen Prüfungen; die fünfte Archiv-/Erfolgskontrolle wurde danach ergänzt.

Es wurden echte kurze Worker-Prozesse aller drei Varianten geprüft, je 12 CPU-
Sekunden Obergrenze, ohne Ryzen-/Office-Zugriff. Alle endeten innerhalb ihres
Budgets. Dies ist ein Integrationstest, keine Aussage zur Suchqualität.
Ein echter Pause-/Wiederaufnahme-Test prüft die kumulierte CPU-Abrechnung.
Auch der eingefrorene Kontroll-Worker bestand alle fünf Testmethoden und die
3.791 realen Tradeprüfungen in 35,414 CPU-Sekunden (`FROZEN_CONTROL.json`).
Eine vollständige Produktionsausführung unter den Windows-Volumenwächtern
wurde hier mangels WSL/Windows nicht durchgeführt; diese Wächter werden nicht
umgangen. Ein tatsächlicher 99-Knoten-Erfolgsfall liegt selbstverständlich
nicht vor.

## C. Vorbereiteter begrenzter Vergleich

### Varianten

| Variante | Erzeugung | Elternwahl und Selektion |
|---|---|---|
| A0 | Unveränderte Fast-Streams Apex/alte Rotation, Gewichte 90:10 | Unverändertes Fast-A0 |
| CYCLE | Apex/alte Rotation/allgemeiner Dreierzyklus, Gewichte 72:8:20 | Wie A0 |
| CYCLE_QUOTA | Wie CYCLE | Dauerhafte Familienrepräsentanz; Elternfamilie gleichverteilt |

Die Gewichte beziehen sich auf Streamauswahlen; leere Streams fallen weg.
CYCLE gegen A0 isoliert die Katalogerweiterung samt notwendiger Erzeugungskosten.
CYCLE_QUOTA gegen CYCLE isoliert das Paket aus dauerhafter Herkunftsrepräsentanz
und familiengleicher Elternzuteilung. Das ist **keine** getrennte kausale
Identifikation von Quote und Elternwahl; ein Erfolg rechtfertigt deren spätere
Ablation. Eine Quotenvariante ohne neuen Operator wäre für den isolierten Lift
kein geeigneter Haupttest und wurde deshalb nicht ausgewählt.

Bei CYCLE_QUOTA bleiben die zwei globalen Besten erhalten. Danach werden
schrittweise bis zu vier vorhandene, verschiedene Isomorphieklassen je Familie
aufgenommen. Fehlen einer Familie vier Kandidaten, werden keine Klone erzeugt;
mindestens ihr vorhandener Vertreter bleibt erhalten. Qualität füllt bis zwölf,
Zufall die restlichen Plätze bis 16. Innerhalb der gleichverteilt ausgewählten
Familie gilt 80 % Dreiertournier, 20 % Zufall. Quoten betreffen **Herkunft**, keine
behauptete mathematische Teilklasse.

### Gründer und Paarung

`founders.json` enthält alle vollständigen graph6-Daten, Herkunft, fünf
nachgeprüfte Scores, Zustandshash und Isomorphiezertifikat. Population: 16.
Aus dem alten Bestand bleiben diese 14:

- HoG57338, HoG57328, HoG57271;
- gen-lambda-13, -01, -08, -21, -02, -03, -18, -11, -17, codex_v01_c08;
- claude_v01_c.

Ersetzt werden `lambda_Linf2_00` und `hog57200` durch:

- `endpoint_W2180`: W=2180, L1=2398, F=2840, Linf=3, Nmax=3;
  Zustand `990935af01048ab0f21fe978574a0766700f4560aec161080b16fb77f20efd32`.
- `endpoint_Linf2_N262`: W=2270, L1=2532, F=3056, Linf=2, Nmax=262;
  Zustand `10e3380aec347c55f3fc8241931c2004e5164e5a7eaf533a935548d5de21bb62`.

Alle 16 Klassen sind verschieden. Alle Varianten und Ziele beginnen mit
**demselben** Bestand; die historischen Ergebnisse werden nicht als gepaarte
Kontrolle recycelt. Die A0-Suchregeln bleiben gleich, die gemeinsamen Eingänge
sind ausdrücklich verbessert. Das anfängliche W-Bestpaar lautet jetzt
(2180,2398), nicht (2182,2398).

Neun neue gepaarte Seeds werden deterministisch gebildet:
`core.derive_seed(2026092103, ['lambda-confirmation', 100+i])`, i=0,…,8.
Der Code erzeugt die konkreten ganzen Zahlen im unveränderlichen Manifest.
Jeder Seed gilt gleichermaßen für die drei Varianten und vier Ziele;
Startreihenfolge der Varianten rotiert. Die neue Zufallsquelle verbraucht
zusätzliche Zufallszahlen; Seedpaarung bedeutet keine identischen Trajektorien.

Entwicklung: vorhandene Graphen, die oben genannten Operatorzensen und kurze
Tests mit Seeds 9219001/9219002. Die sechs Zufallsproben nutzten 921031.
Bestätigung: die neun neuen Laufseeds werden nicht zur Parametereinstellung
verwendet. Der bisherige zurückgehaltene Lift gen-lambda-23 wurde für die
Diagnose gelesen und ist damit **kein unberührter Holdout mehr**. Dieser
Versuch bestätigt gegebenenfalls über neue Zufallsläufe auf bekannten Gründern;
er beansprucht keine Übertragbarkeit auf ungesehene Graphfamilien.

### Episoden, Archiv, Kosten und Grenzen

Vier aktive Ziele: (W,L1), L1, F, (Linf,Nmax,L1). Keine aktive Migration und kein
Crossover. Störungen 2–4 / 5–12 / 13–32 mit Gewichten 4:3:2, maximal 45 CPU-s;
strikter A0-Abstieg mit Stichprobe 32, maximal 75 CPU-s. Es wird keine zusätzliche
A1-/Tabu-/Temperaturänderung eingeschleust. Gesamtes Jobbudget hat Vorrang.

Alle Varianten erhalten dieselbe passive Beobachtung: **jeder fertig bewertete
Nachbar**, auch ein anschließend verworfener, kann einen der vier Zielchampions
ersetzen. Vor Aufnahme unabhängige Gültigkeits- und Scoreprüfung; höchstens
vier gespeicherte Graphen pro Job. Gleiche Zielwerte verdrängen den alten
Champion nicht. Dieses Archiv führt keine Kandidaten in die Population zurück.
Ein vollständiges Paretoarchiv oder alle gleich guten Diversitätskandidaten
werden ausdrücklich nicht behauptet. Auch bei durch Zeitabbruch verworfener
32er-Stichprobe bleiben rechtzeitig geprüfte Beobachtungen erhalten.

Primär bleibt die alte aktive Bestwertsemantik erhalten; das passive Archiv
wird gesondert ausgewertet. Die gemeinsame zusätzliche Instrumentierung kostet
CPU in **allen** Varianten. Unter Zeitlimits kann sie gegenüber historischen
Läufen Trajektorien verändern, obwohl die A0-Entscheidungsregeln gleich bleiben.

108 Jobs = 3 Varianten × 4 Ziele × 9 Seeds, je 600 CPU-s, zusammen 64.800 s =
18 Worker-CPU-h. Vorgeschaltetes Kontrollkontingent 600 CPU-s. Python-Controller
höchstens 600 kumulierte CPU-s bis zur geordneten Pause, einschließlich
Wiederaufnahmen; geringfügige Abschlusskosten sind im Bericht als tatsächliche
Kosten sichtbar. Gesamtplanung damit etwa 18 h 20 min CPU plus externe
Windows-Abfrage-Infrastruktur. Die Kontrollgrenze ist ein Ceiling, keine
absichtliche Ausschöpfung.

18 Worker auf Ryzen, keine Office-Berechnung. Ideale Vergleichswandzeit
18h/18=1h. Mit Start-/Kontrollkosten und beobachtetem bisherigen Durchsatz grob
**70–100 Minuten** einplanen; das ist kein neuer Benchmark und keine Garantie.
Keine ETA für eine Lösung. Zwei Sekunden Abschlussreserve je regulärem Job
liegen im 600-s-Kontingent. Start, Prüfung, Kanonisierung, Archiv und Abschluss
werden berechnet. `wait4`-Quittungen bestimmen den tatsächlichen Verbrauch;
bei Überschreitung ist die reguläre Auswertung gesperrt.

Unveränderte Ressourcenwächter: 1 GiB Adressraum je Worker, 36 GiB Gruppenlimit,
6 GiB verfügbarer RAM als Reserve, 20 GiB Linux- und 50 GiB tatsächlicher
Windows-Trägerplatz als Reserve. Zusätzlich 2 GiB Obergrenze für diesen Laufbaum,
periodisch geprüft. Keine Proofdateien. Keine fremden Prozesse werden beendet.
Atomare Checkpoints, RNG-Zustand und kumulierte CPU-Quittungen bleiben erhalten;
ungeklärte aktive Quittungen verhindern automatischen Neustart mit frischem
Budget. Die Bundle-Fingerprints sichern den tatsächlich gestarteten Code.

Ein vollständig verifizierter F=0-Kandidat wird atomar mit Prüfergebnis in
`SOLUTION.json` dauerhaft auf dem Ryzen gesichert. Der Controller prüft ihn
erneut und stoppt nur eigene Worker geordnet. Ein falscher Nullscore wird
abgelehnt. Für weitere Veröffentlichung eines wirklichen Fundes wäre dessen
separate vollständige Ergebnisprüfung erforderlich.

Status alle zehn Minuten mit Budget-ETA; Verbesserungen nach der kurzen
Anlaufphase mit Uhrzeit/Abstand, Variante/Replikat und 0/25/50/75 Zeichen
Einrückung. Die Varianten tragen jetzt verschiedene Namen, sodass auch die
aggregierten Statusbestwerte sie getrennt führen.

### Bedienung und tatsächlicher Ausführungsstatus

Verzeichnis: `experiments/memetik/lambda_strategy_0_1_0`.
`run.py prepare <neues Laufverzeichnis>` friert Code, Gründer und Manifest ein
und endet mit `PREPARED_NOT_STARTED`. Erst `run.py run <Laufverzeichnis>` startet
den vorgeschlagenen Vergleich. Derselbe Aufruf setzt eine sauber quittierte
Pause mit Restbudget fort. `run.py evaluate <Laufverzeichnis>` prüft Ergebnisse.
Keine dieser Aktionen startet eine 48-Stunden-Kampagne.

Hier wurde ausschließlich eine Vorbereitung und kurze Entwicklungskontrolle
in der Arbeitsumgebung ausgeführt. **Auf Ryzen wurde nichts gestartet.**
Der nächste Nutzerbefehl wird erst nach Entscheidung über dieses neu bezifferte
Budget einzeln für Ryzen/Ubuntu/WSL ausgegeben; keine mehrstufige Befehlsliste.

## D. Messgrößen und vorher festgelegte Entscheidung

Primärer Endpunkt je Seed: bester aktiver (W,L1)-Wert im W-Job nach 600 CPU-s.
Neuer Rekord: lexikographisch kleiner als (2180,2398). L1<2398 und F<2836 sind
eigene ergänzende Rekorde. Ein Linf-Fortschritt allein zählt nicht als W-Erfolg.

Zusätzlich gespeichert:

- aktive Bestwertkurven aller vier Ziele und Zeit bis zur ersten Verbesserung;
  ohne Verbesserung ist die Zeit rechtszensiert bei 600 s, nicht als Null notiert;
- vier passive Zielchampions einschließlich Herkunft und Fund-CPU, gesondert
  von aktiven Bestwerten;
- verschiedene Endpunktklassen je Job, finale Population, beschriftete und
  isomorphe Rückkehr zum Elternzustand (keine Gleichsetzung mit einem Becken);
- Elternanzahl je Herkunft und Populationsanteile je Epoche;
- angeforderte/erreichte Störlängen, Abstiegslängen, Stör-Abbruchursachen und
  angenommene sowie bewertete Züge je Operator;
- maximale W/L1/F/Linf-Werte auf angenommenen Episodenpfaden relativ zum
  Elternzustand. Das sind beobachtete Hürden, keine exakten Minimaxwerte;
- gültige rechtzeitig abgeschlossene Episoden pro tatsächlicher CPU-s,
  Klassen pro CPU-s und Kostenkategorien einschließlich Archivprüfung.

Ein Bewertungsunterschied darf nicht aus nachträglich ausgesuchten Seeds oder
nur dem besten Einzelrekord abgeleitet werden. Die folgenden Regeln sind
**technische Auswahlregeln**, kein Signifikanznachweis:

1. Alle Aufgaben, Kontrollen, Scores und CPU-Belege müssen gültig sein.
   Fehlende Läufe dürfen nicht stillschweigend verschwinden.
2. Eine Variante ist für eine spätere unabhängige Bestätigung bevorzugt,
   wenn sie im primären W-Ziel mindestens 6 von 9 Paaren gewinnt, höchstens
   eines verliert und einen Median-Gewinn von mindestens 2 W erreicht.
   Alternativ bei Median-ΔW=0: mindestens fünf W-gleiche Paare und darin
   medianer L1-Gewinn mindestens 2, weiterhin mindestens 6 lexikographische
   Siege und höchstens eine Niederlage.
3. CYCLE_QUOTA muss diese Bedingung sowohl gegen A0 als auch gegen CYCLE
   erfüllen, um den Mehrmechanismus zu rechtfertigen. Erfüllen beide Varianten
   die A0-Regel, aber die Quotenvariante nicht die direkte CYCLE-Regel, wird
   die einfachere CYCLE-Variante bevorzugt.
4. Ein isolierter Rekord ist ein Anlass für eine gezielte Reproduktion und
   Grapharchivierung, aber keine automatische Verfahrenswahl.
5. Nur L1-/F-/Linf-Fortschritte oder viele neue Klassen ohne primären W-Vorteil
   rechtfertigen höchstens eine kleine Spenderinsel bzw. einen anschließenden
   gezielten Migrationstest, keine pauschale Ablösung der W-Baseline.
6. Ohne robuste Verbesserung bleibt Fast-A0 die Referenz; keine unveränderte
   48-Stunden-Verlängerung wird hiermit freigegeben. Die präzise vergrößerte
   Erreichbarkeit bleibt auch bei negativem Vergleich ein gültiger Befund.

`evaluate` liefert gepaarte Werte und Siege/Bindungen/Niederlagen für alle
vorgesehenen Kontraste, nicht automatisch eine statistische Gewinnerbehauptung.
Rohmessungen und Entscheidungsschwellen sind gemeinsam zu beurteilen. Nach
einem positiven Screen wäre vor einer Hauptkampagne eine unabhängig festgelegte
neue Seedserie sinnvoll; Parameter und Budget werden dann gesondert festgelegt.

## E. Prioritäten und bewusst zurückgestellte Alternativen

**Erste Priorität:** CYCLE, weil konkrete neue gültige Bewegungen aus einem
nachweislich isolierten Gründer existieren. **Zweite Priorität:** CYCLE_QUOTA,
weil die lange Suche Herkunftsverarmung zeigt und der neue Katalog diese
Familien jetzt überhaupt beweglich machen kann.

**Barrieren/Tabu:** kein weiterer gleichzeitiger Mechanismus. Schon der erste
HoG-Schritt muss verschlechtern; das vorhandene Perturbationsschema erlaubt
solche Schritte. Zunächst tatsächliche Hürden, Längen und isomorphe Rückkehr
messen. Wenn CYCLE fast immer in denselben Elternzustand zurückfällt, danach
gezielt einen konstant budgetierten Pfadversuch mit festen W-/L1-Ankern,
zustandsbezogenem Gedächtnis und protokollierten Hürden prüfen. Die jetzigen
Daten bestimmen keine optimale Temperatur oder Fluchtlänge.

**Mehrzielkooperation:** der beste gespeicherte Linf=2-Graph ist bereits ein
konkreter gemeinsamer Gründer. Das passive Archiv schließt die dokumentierte
Beobachtungslücke bei begrenztem Speicher. Eine spätere aktive Migration könnte
alle 16 Episoden einen der vier validierten Champions deterministisch an eine
andere Insel übergeben, dort nach deren Ziel selektieren und nicht den Elitenplatz
erzwingen. Sie müsste gegen identische unabhängige Inseln mit demselben
Gesamtbudget antreten. Dies ist hier nicht als geprüfter Suchmodus ausgegeben.

**Reparatur:** prinzipiell tragfähige Alternative in der Inzidenzbeschreibung:
eine begrenzte Menge von Tripeln entfernen, Punktgrade als Defizite festhalten,
neue Tripel über exakte lokale Suche ergänzen; Linearität und Berge-Dreieckfreiheit
müssen auch über die Grenze zur unveränderten Umgebung gelten. Alte
Konstruktion nicht bloß erneut zulassen, Zielrandbedingungen explizit halten.
Nur nach unabhängiger Vollprüfung darf ein Rückkehrgraph als λ-Kandidat gelten.
Ein SAT-/CP-Modell auf einem kleinen Gebiet kann dabei dennoch unlösbar sein;
Timeout ist keine Aussage über den vollständigen Suchraum. Kein ungeprüfter
Reparaturprototyp wird hier in die Produktionssuche aufgenommen. Solange direkte
3-Trades bereits tausende gültige Nachbarn liefern, ist eine zusätzliche exakte
Reparaturmaschine im selben Versuch nicht hinreichend begründet. Sie wird
prioritär, wenn neue Kataloge trotz ausreichender Erkundung weiterhin viele
relevante Gründer blockieren oder die gemessenen Hürden nicht überwinden.

**Strukturelle Diversität:** Klasse und Herkunft getrennt messen. Residuen-
Histogramme, Defektgradfolgen und C4 sind nützliche Deskriptoren, aber kein
Isomorphietest. Die Population wird deshalb weiterhin über echte unkolorierte
pynauty-Zertifikate dedupliziert; zehn umnummerierte Lifts zählen nicht als zehn
neue Klassen. Ein unbekanntes globales Zusatzinvariant von Apex/Rotation wird
nicht behauptet. Bewiesen sind die harten Invarianten, die lokalen
Katalogrestriktionen und mindestens ein isolierter Zustand.

Der Reviewer erhält denselben fachlichen Auftrag und kann diese Feststellungen
an den Quelldaten und Skripten eigenständig prüfen. Ein Reviewerbericht liegt
in diesem Arbeitsgang nicht vor; Übereinstimmung wurde weder vorausgesetzt
noch behauptet. Besonders prüfenswert sind die Vollständigkeit der gerichteten
Dreierzyklus-Aufzählung und die Abwägung zwischen Katalogerweiterung und
Familienselektion. Eine Literatur-Neuheit des Operators wird nicht beansprucht.
