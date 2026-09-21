# λ-Review: eigener Abgleich und geänderte Priorität

21.09.2026. Grundlage: eigener Strategiebericht vom selben Tag, Quellstand
`6cf206b7a7942672ef806c70d9e590bf27a1973c`, veröffentlichter Codex-Stand
`4f9ea8c9ca5a373e4bdd7e496fa686dcc4aefd6e` und eingereichter Reviewerbericht.

**Entscheidung:** Den vorbereiteten 18-CPU-Stunden-Versuch nicht unverändert
starten. Der Reviewer hat mit Pivot eine kleinere, unmittelbar wirksame Lücke
im Zugkatalog gefunden, die ich übersehen hatte. Pivot und vollständige
Nachbarschaften haben Vorrang. Mein gültiger Dreierzyklus bleibt eine
zusätzliche Option für die anschließende Untersuchung von Barrieren.
Dauerhafte Familienquoten sind derzeit kein Hauptvergleich mehr.

Originalreview byteidentisch im eigenen Zweig `reviews/20260921-lambda`:
[Archivcommit 52ad622](https://github.com/ibenarb/conway99-research/tree/52ad622dfa5d04ba0a0d26dd39e4aa7fc6927ce7/docs/reviews/20260921_lambda).
SHA256: `bbc861bae151e67957c5feb3bc41bda1c964748767c3720f2515ad36a8076052`.
Archivierung ist keine pauschale Bestätigung aller Reviewer-Aussagen.

## 1. Was wir jeweils gefunden haben

Mein ursprünglicher Befund war korrekt, aber die Priorisierung unvollständig:

- HoG57338 hat genau 46 Apex-Züge, keinen alten Rotationszug und unter diesem
  Katalog keinen neutralen oder verbessernden ersten Schritt für W/L1/F.
- Der Lift gen-lambda-13 ist unter dem alten Katalog isoliert.
- Allgemeine zyklische Tausche auf drei disjunkten Dreiecken liefern aus diesem
  Lift 363 gültige Züge, davon 33 F-Verbesserungen. 3.791 solche Züge auf 16
  Gründern wurden unabhängig geprüft.
- 48 von 72 alten λ-Endpopulationen haben nur noch HoG-Herkunft. Das ist ein
  beobachteter Selektionsbefund, aber noch keine Erklärung des Bestwertplateaus.

Der Reviewer ergänzt **Pivot**, einen Tausch zweier Dreiecke mit gemeinsamem
Knoten p:

\[
\{p,x,y\},\{p,u,v\}\longmapsto\{p,x,u\},\{p,y,v\}.
\]

Nur xy und uv werden gelöscht, xu und yv ergänzt. Die vier Kanten an p bleiben.
Mein Dreierzyklus verlegt dagegen sechs Kanten zwischen drei disjunkten
Dreiecken. Damit untersuchen die beiden Operatoren unterschiedliche kleine
Veränderungen. Eine Beschränkung auf disjunkte entfernte Dreiecke übersieht
Pivot vollständig.

**Meine Korrektur:** Ich hätte die Trades mit überlappenden Dreiecken zuerst
prüfen sollen. Die Korrektheit meines Operators und seine nachgewiesene
Erweiterung des alten Zuggraphen bleiben bestehen; seine Vorrangstellung vor
Pivot und Barrierensteuerung ist durch die neuen Daten nicht mehr begründet.

## 2. Jetzt selbst reproduzierte Reviewer-Befunde

`experiments/memetik/lambda_review_20260921/check_review.py` wurde ausgeführt;
`CHECK.json` enthält Graphen, Prüfsummen, Isomorphieklassen, Zensen und vollständige
Abstiegszüge. Es ist eine begrenzte Diagnose, kein Kampagnenstart.

### Gültigkeit und Scores der drei eingereichten Graphen

Alle drei graph6-Prüfsummen stimmen. Alle Graphen sind unabhängig als einfache
14-reguläre λ-Graphen nachgeprüft; alle fünf Scores stimmen.

| Graph | W | L1 | F | Linf | Nmax |
|---|---:|---:|---:|---:|---:|
| HoG57338, Ausgang | 2182 | 2398 | 2836 | 3 | 3 |
| Reviewer: L1-Abstieg | 2169 | **2392** | 2844 | 3 | 3 |
| Reviewer: W-Abstieg | **2155** | 2416 | 2948 | 3 | 5 |
| Reviewer: Tabu-Endpunkt | **2153** | 2430 | 3000 | 3 | 8 |

Die W- und L1-Abstiege wurden mit unserem eigenen Generator und einer expliziten
Tie-Break-Regel reproduziert. Sie ergeben **byteidentisch dieselben Graphen**
wie im Review: W=2155 nach fünf Pivot-Schritten, L1=2392 nach einem Pivot.
Für F bleibt HoG57338 ein exaktes Ein-Schritt-Minimum von Apex ∪ Pivot.
Der Linf-Abstieg ergibt (Linf,Nmax,L1)=(3,1,2416), ebenfalls wie angegeben.

Beim W=2153-Graphen ist der gültige Endpunkt unabhängig bestätigt; der behauptete
240-CPU-Sekunden-Tabulauf wurde nicht reproduziert. Dafür fehlen vollständiger
Suchcode, konkreter Seed und Verlauf. Endpunktgültigkeit und Herkunft eines
Endpunkts sind unterschiedliche Prüfpflichten.

### Pivot wurde unabhängig gegen Brute Force geprüft

Für sechs reale Zustände wurden jeweils alle 4.158 strukturellen Pivot-Kandidaten
mit vollständiger harter Graphprüfung verglichen. Die einfache Pivot-Bedingung
und Brute Force liefern identische Mengen:

| Zustand | Gültige Pivots |
|---|---:|
| HoG57338 | 78 |
| claude_v01_c | 56 |
| gen-lambda-11 | 0 |
| gen-lambda-03 | 198 |
| gen-lambda-13 | 99 |
| gen-lambda-17 | 99 |

Alle 530 gültigen erzeugten Kinder wurden zusätzlich unabhängig geprüft und
die Inversen exakt angewandt. HoG57338 hat sieben in (W,L1) bessere und einen
in L1 besseren Pivot, aber keinen F-verbessernden Pivot.

Zusätzliche mathematische Vereinfachung: In einem gültigen λ-Graphen induziert
N(p) genau sieben disjunkte Kanten. Daher sind sämtliche Querverbindungen
zwischen den beiden ausgewählten Nachbarpaaren ausgeschlossen. Die zusätzlichen
Adjazenzterme in Formel M6 des Reviewers sind hier null. Pivot ist genau dann
gültig, wenn xu und yv jeweils **nur p** als gemeinsamen Nachbarn besitzen:

\[
|N(x)\cap N(u)|=|N(y)\cap N(v)|=1.
\]

Nach dem Tausch bleiben p als gemeinsamer Nachbar der neuen Kanten und die
gewünschten zwei neuen Tripel erhalten. Ein zusätzliches Dreieck müsste eine
neue Kante enthalten und würde deren Bedingung verletzen. Grad und alle
beibehaltenen Tripel bleiben erhalten. Der verwendete Diagnosegenerator setzt
einen bereits gültigen λ-Ausgangsgraphen voraus; die Ergebnisprüfung erfolgt
zusätzlich unabhängig.

### Der frühere W-Erfolg wird mechanistisch erklärt

Der λ-W-06-A1-Endpunkt des 144-h-Laufs ist exakt folgender einzelner Pivot aus
HoG57338:

- entfernen: {40,60}, {89,95};
- ergänzen: {40,89}, {60,95};
- gemeinsamer Knoten: 16.

Dies ist anhand der graph6-Daten selbst bestätigt. Der alte Code musste also
einen Umweg zu einem Graphen nehmen, der im erweiterten Katalog direkter Nachbar
ist. Die tatsächliche historische Zugfolge lässt sich aus den gespeicherten
Bestendpunkten allein nicht rekonstruieren.

## 3. Abgleich und Grenzen der Schlussfolgerungen

| Thema | Urteil nach Abgleich |
|---|---|
| Hypergraphenbeschreibung | Übereinstimmung: Linearität, Grad 7 und keine Berge-Dreiecke sind notwendig; Hypergraphen-Gradtreue allein reicht nicht. |
| Dünner alter Zugkatalog | Übereinstimmung und jetzt stärkere konkrete Erklärung durch Pivot. |
| Lokales HoG-Minimum | Exakt unter dem alten Katalog bestätigt; unter Apex ∪ Pivot für W und L1 widerlegt. |
| Gründerverarmung | Eigener Befund bleibt richtig. Reviewer liefert plausible Evidenz für geringere Priorität; eine allgemeine Wirkungslosigkeit von Diversität folgt nicht. |
| Größere Trades | Mein Dreierzyklus bleibt gültig. Er bietet an den neuen W-Endpunkten zunächst keinen direkten W-Fortschritt. Sein Nutzen muss im Pfadvergleich gemessen werden. |
| Linf-Migration | Als sofortiges Hauptverfahren zurückstellen. Einige monotone Abstiege entscheiden nicht über alle nichtmonotonen Wege. Gleiche Scores allein beweisen auch nicht dieselbe Isomorphieklasse. |
| Gemeinsames Archiv | Als begrenzte passive Beobachtung sinnvoll; kein belegter Haupthebel für Suchleistung. |
| Reparatur/CP-SAT | Nachrangig, solange Pivot, exakte Nachbarschaften und unser bereits validierter größerer Operator nicht ausreichend untersucht sind. |

### Zu starke oder noch nicht reproduzierte Aussagen im Review

1. **„F=2836 exakt minimal“ ist nur lokal und katalogbezogen zulässig.**
   Bestätigt: kein besserer Apex-/Pivot-Nachbar von HoG57338. Ein globales
   Minimum der λ-Suche folgt daraus nicht. Beim W=2153-Graphen gibt es im
   Übrigen einen F-verbessernden Apex und acht F-verbessernde Pivots.
2. **„Die Baseline ist eingeschlossen“ ist als Komponentenbehauptung falsch.**
   Ihr eigener W=2180-Erfolg zeigt, dass sie das anfängliche Plateau verlassen
   kann. Dass ein direkter Pivot einen bisherigen Umweg ersetzt, begründet
   die Verbesserung des Katalogs, nicht eine Nichterreichbarkeit per alter Suche.
   Fast-A0 bleibt eine notwendige Vergleichsgruppe; als bevorzugte Produktions-
   methode ist die bisherige λ-Implementierung nun schlechter begründet.
3. Die **BFS bis Tiefe 4** ist hier nicht unabhängig reproduziert. Es fehlen
   Programm und vollständige Laufbelege. Akzeptiert man sie, folgt eine untere
   Schranke für Apex-Pfadlängen zu Verbesserungen. Das ist weder eine vollständige
   Komponentenbeschreibung noch die Rekonstruktion einer historischen Trajektorie.
   Rotation kann als Makrozug andere Pfade/Abstiegsentscheidungen ermöglichen,
   auch wenn sie durch mehrere Apex-Schritte darstellbar sein sollte.
4. **„Linf-Migration widerlegt“** ist zu weitgehend. Reviewer E7 betrifft die
   berichteten Starts und einen bestimmten monotonen Abstiegsalgorithmus. Die
   Transferläufe wurden hier nicht erneut gerechnet. Eine universelle Aussage
   über Migration, andere Ziele oder Wege mit Zwischenverschlechterung folgt nicht.
5. **P verändert mehrere Dinge gleichzeitig:** neuen Katalog, vollständigen
   Abstieg, laut Review auch die Verteilung der Perturbationszüge. Das ist als
   Verfahrenspaket zulässig, isoliert aber nicht „genau einen Effekt“. Jede
   behauptete Ursachenzerlegung braucht passende Kontrollvarianten.
6. Der geplante **46–58-CPU-Stunden-Vergleich ist noch nicht eindeutig definiert**:
   Seine Jobzahlen enthalten keinen Gründerfaktor, während die Entscheidungsregel
   Resultate pro Gründer verlangt. Die aufgelisteten Startgraphen sind zudem mehr
   als die festgelegte Population 16; codex_v01_c08 ist bereits einer der zehn
   Z33-Gründer. Eine konkrete Auswahl und Startzuordnung fehlen.
7. Die vorgeschlagene Prüfung `df /mnt/c` identifiziert **nicht allgemein das
   tatsächliche VHDX-Trägervolumen**. Der vorhandene Wächter, der die registrierte
   VHDX und deren Windows-Volume abfragt, bleibt bestehen. Auch die bestehende
   50-GiB-Windowsreserve wird nicht ohne Grund auf 20 GB abgesenkt.

### Neue Gegenprüfung meines Dreierzyklus an den Reviewer-Rekorden

| Zustand | Apex / Pivot / Dreierzyklus | Verbesserungen in (W,L1), jeweils |
|---|---|---|
| W=2155, L1=2416 | 35 / 69 / 29 | 0 / 0 / 0 |
| W=2153, L1=2430 | 42 / 66 / 27 | 0 / 0 / 0 |

Damit sind beide Zustände tatsächlich lokale W/L1-Minima auch im **gemeinsamen**
Katalog Apex ∪ Pivot ∪ unserem Dreierzyklus. Größere Nachbarschaft allein liefert
hier keinen unmittelbaren weiteren Abstieg. Das stützt die nächste Priorität:
kontrollierte Wege mit Zwischenverschlechterungen. Es beweist keine besonders
hohe oder unüberwindbare Barriere.

## 4. Meine geänderte Empfehlung

**Nachtrag nach Nutzerentscheidung:** Der nachfolgende damalige 16-h-Vorschlag
ist durch den freigegebenen [192-h-Vergleich mit fortsetzbaren Zuständen](../lambda_compare_20260921/DESIGN.md)
ersetzt. Insbesondere gelten die sechs Seeds, 600-s-Endpunkte, das 64-Klassen-Limit
und die damalige Auswahlschwelle nicht für die neue Umsetzung. Die historische
Empfehlung bleibt nachfolgend als Entscheidungsverlauf sichtbar.

### Unmittelbar

- Den alten vorbereiteten 18-h-Vergleich unverändert **nicht starten**.
- Pivot integrieren; alle bisherigen harten Bedingungen und unabhängigen
  Rekordprüfungen beibehalten. Der neue Diagnosecode ist bereits ausgeführt,
  aber noch keine Produktionsrevision des Controllers.
- Vollständige Nachbarschaften für die relevanten λ-Zustände verwenden und
  `LOCAL_MIN_EXACT` ausschließlich nach vollständiger Enumeration ausgeben.
  CPU-Abbruch bleibt ein eigener Status. Ein größeres Trade-Limit darf nicht
  als vollständiger lokaler Mindestnachweis etikettiert werden.
- Die Reviewer-Rekordgraphen dauerhaft aufbewahren. W, L1 und F bleiben getrennte
  Ziele; W=2153 ist kein Fortschritt in F.
- Für historische stärkere Aussagen die fehlenden BFS-/Tabu-/Transfer-Belege
  anfordern. Die bereits selbst reproduzierten Pivot-Schlüsse hängen davon nicht ab.

### Danach: kleinerer, klar definierter Vergleich statt sofort 46–58 CPU-h

Vorgeschlagene vier Verfahren:

| Variante | Aufgabe |
|---|---|
| B0 | Fast-A0 als unveränderte algorithmische Referenz |
| P | Pivot ergänzt, vollständiger Abstieg; als gemeinsames Verfahrenspaket ausgewiesen |
| T | Exakte Apex-/Pivot-Nachbarschaft mit eingefrorener Taburegel und begrenzten Neustarts |
| TC | Identisch zu T, zusätzlich der bereits geprüfte Dreierzyklus |

Der aussagekräftige Großtrade-Kontrast ist **TC gegen T**: Er verwendet denselben
Pfadalgorithmus, dieselben Starts und dasselbe CPU-Budget. P gegen T prüft das
Barrierenverfahren als Paket gegenüber monotonem Abstieg; B0 gegen P ist ein
Gesamtverfahrenvergleich, keine Einzeleffektanalyse. Ein neuer CP-SAT-Operator
wird in diesem ersten Vergleich nicht gleichzeitig eingeführt.

Alle vier Ziele bleiben aktiv: (W,L1), L1, F, (Linf,Nmax,L1).
Sechs neue gepaarte Seeds × vier Ziele × vier Varianten × 600 Worker-CPU-s =
**96 Jobs = 16 Worker-CPU-Stunden**. Höchstens **eine zusätzliche CPU-Stunde**
für Entwicklung, Kontrollen und kleine Durchsatzmessung vor dem Einfrieren.
Dieser Vorschlag ist neu zu entscheiden, nicht automatisch freigegeben und
noch nicht als neuer Kampagnencontroller implementiert. Auf Ryzen grob
60–90 Minuten plus Vorbereitung bei 18 Workern einplanen; kein gemessener
Durchsatz dieses neuen Codes und keine Lösungs-ETA.

Für einen sauberen Vergleich können alle Varianten den bereits exakt
festgelegten Bestand aus `lambda_strategy_0_1_0/founders.json` erhalten:
16 verschiedene Klassen, identische Eingänge, W-Startrekord (2180,2398), dazu
der bisherige Linf=2-Endpunkt. B0/P besitzen Population 16. T/TC initialisieren
ein maximal 64 Klassen großes Neustartarchiv aus denselben 16 Kandidaten und
starten am jeweiligen Zielbesten; weitere Starts kommen aus diesem Archiv.
Gemeinsame Quelldaten bedeuten nicht unberührte Testgraphen: bestätigt wird nur
über neue Laufseeds auf bereits bekannten Gründern.

Die **neuen** Reviewer-Rekordgraphen bleiben aus diesem Vergleich heraus und
werden in einer getrennt gekennzeichneten Rekordfortsetzung verwendet. Sonst
könnte der eingepflanzte W=2153-Start die gesuchte Wirkung der Pivot-Aufnahme
verdecken. Kein unbudgetierter Nebenlauf wird damit eröffnet.

Vor Start noch konkret festzulegen und einzufrieren: eine Tabuvariante,
Tie-Breaks, Restartregel und Archivverdrängung. Vorschlag für den technischen
Vorversuch: Attribut-Tabu für gelöschte Kanten (kurzzeitig keine Wiederergänzung),
Aspiration nur bei Verbesserung des aktiven Jobrekords, Verfall und feste
Speichergrenze; vergleichen mit einfachem Zustandstabu ausschließlich auf
Entwicklungsfällen. Der 240-s-Einzelversuch des Reviewers wählt diese Parameter
nicht verbindlich für uns.

Primärer Endpunkt: aktives (W,L1) des vollständigen W-Jobs, ergänzend alle anderen
Ziele, CPU-Zeit, Klassen, akzeptierte Operatoren und Rückkehr zum kanonisch
identifizierten Referenzminimum. Job/Seed ist die Replikationseinheit; bei einer
Population darf daraus keine unabhängige Replikation pro Gründer erfunden werden.
Als technische Auswahlregel: mindestens vier Siege von sechs Paaren, höchstens
eine Niederlage, sowie mediane Verbesserung im lexikographischen Ziel. Keine
Signifikanzbehauptung daraus. Einzelrekorde werden separat gewertet. Für TC muss
zusätzlich der direkte Vergleich gegen T überzeugen.

**Prioritätenfolge:** Pivot → exakte lokale Diagnose → kontrollierte Barrieren-
suche → Nutzen des Dreierzyklus innerhalb derselben Barrierensteuerung. Erst
anschließend weitere Linien-Neupartitionen/CP-SAT oder größere Herkunftsquoten.

Es wurde keine neue Ryzen- oder Office-Kampagne gestartet.
