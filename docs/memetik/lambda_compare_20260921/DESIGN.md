# Freigegebener λ-Vergleich: Umsetzung nach der Budgetkritik

Stand 21.09.2026. Dieser Stand ersetzt die Vorschläge mit 16 beziehungsweise
18 CPU-Stunden und einem maximal 64 Klassen großen Archiv. Nutzerentscheidung:
Zustimmung zum erweiterten Vorgehen, anschließend „Dann setz das so um“.
Die bereits früher ausgeschlossene automatische 48-Stunden-Hauptkampagne bleibt
außerhalb dieses Auftrags. Jetzt freigegeben ist der folgende konkrete Vergleich.

## Forschungsfrage und Design

Wir prüfen, ob Pivot mit vollständiger Nachbarschaft sowie nichtmonotone
Tabupfade das dokumentierte λ-Plateau überwinden, und ob der allgemeine
Dreierzyklus innerhalb derselben Tabusuche zusätzliche Wirkung hat. Ein neuer
Bestgraph wäre Suchfortschritt, kein Nichtexistenzbeweis oder globaler
Optimalitätsnachweis. Die mathematische Review-Abgleichung steht weiter in
`../lambda_review_20260921/ABGLEICH.md`.

| Faktor | Festlegung |
|---|---|
| Replikationen | 12 neue Seeds, `derive_seed(2026092104, ['lambda-compare', i])`, i=0,…,11 |
| Ziele | (W,L1), L1, F, (Linf,Nmax,L1) |
| Verfahren | B0, P, T, TC |
| Starts | Identische 16 kanonisch verschiedene Gründer aus `founders.json` |
| Pro Job | 3600 Worker-CPU-Sekunden einschließlich fünf Sekunden Abschlussreserve |
| Umfang | 192 Jobs, 192 Worker-CPU-Stunden Vergleichsbudget |
| Gleichzeitigkeit | 18 Worker, Variantenreihenfolge pro Seed/Ziel zyklisch versetzt |
| Messpunkte | 600, 1800, 3600 Sekunden derselben fortgesetzten Trajektorie |
| Kontrollen | Ein separater Job mit maximal 3600 CPU-Sekunden; tatsächliche Kosten zählen |
| Erweiterung | Nur explizit; dieselben Jobs mit höherem kumulativem Budget |

Die Gründer enthalten drei ursprüngliche HoG-Linien, zehn Z33-Lifts, eine
Packing-Linie und zwei validierte frühere Endpunkte. Ausgangsrekorde:
(W,L1)=(2180,2398), L1=2398, F=2836, (Linf,Nmax,L1)=(2,262,2532).
Die Reviewer-Rekorde W=2155/W=2153/L1=2392 sind **Kontrollfälle**, keine eingesetzten
Startlösungen. Neue Seeds auf bekannten Graphen sind keine unabhängige
Bestätigung auf unbekannten Graphfamilien. Die Replikationseinheit ist der Job,
nicht jeder seiner 16 Gründer.

## Warum diese Zeit- und Mengenparameter?

Die erste Stundenmarke ist ein vorab festgelegter Vergleichsendpunkt, keine
Aussage, dass spätere Fortschritte unwahrscheinlich seien. Zehn Minuten allein
wären für seltene Fluchtpfade schwach; zwölf statt sechs Seeds verbessern die
Sicht auf Streuung. Auch zwölf Seeds liefern keine automatische Signifikanz oder
Aussage über Langzeit-Erfolgsraten. Die Messpunkte zeigen, ob der Vorteil früh
entsteht, sich vergrößert oder zwischenzeitlich verschwindet.

Ein Plateau beendet keinen Job vorzeitig. Bei Budgetende bleiben begonnene
Episoden, Nachbarschaften und Pfade erhalten. Auch Restarts beenden die Kampagne
nicht. Eine spätere Entscheidung kann dieselben Pfade länger laufen lassen;
sie muss die zusätzlichen CPU-Stunden ausdrücklich benennen. Die automatische
Auswertung ordnet Ergebnisse ein, startet jedoch keine Folgekampagne.

192/18 = 10 Stunden 40 Minuten ist lediglich die idealisierte Kapazitätsuntergrenze.
Bei gleich langen Jobs und 18 Slots sind ohne weitere Effekte elf Belegungswellen
nötig. Tatsächliche Walltime hängt von Ryzen-Durchsatz, Ressourcenprüfungen,
Archivzugriffen und verbleibenden Slots ab. Die alte gemessene Beschleunigung
kalibriert den neuen vollständigen Katalog nicht. Der Controller meldet eine
Budget-ETA aus beobachtetem Durchsatz; keine Lösung-ETA.

Entfallen sind der pauschale 64-Klassen-Deckel, der pauschale 2-GiB-Laufdeckel und
der 600-CPU-Sekunden-Controllerstopp. SQLite speichert alle akzeptierten validierten
Klassen sowie alle beobachteten Rekorde. Nicht jeder wertlose bewertete Nachbar
wird gespeichert. Es gibt weder automatisches Löschen alter Klassen noch einen
unbegrenzten RAM-Container. SQLite-Seitencache: 16 MiB; die tatsächlichen
Ressourcenreserven bleiben die Grenze.

Beibehalten: 1 GiB Adressraum pro Worker, 36 GiB Gruppen-RAM, 6 GiB freie
Host-RAM-Reserve, 20 GiB freier Linux-Platz und 50 GiB auf dem **tatsächlichen
Windows-VHDX-Trägervolumen**. Diese Regeln verhindern einen bekannten technischen
Ausfall. Sie sind keine Behauptung, dass die Suchlandschaft damit vollständig
untersucht sei. Bei einem Wächterstopp bleiben sauber pausierte Zustände erhalten.

Population 16 bleibt nur in B0/P fixiert, damit der Vergleich nicht gleichzeitig
die Populationsgröße variiert. T/TC haben je einen Pfad und das wachsende Archiv.
Die Tabudauer und Restartschwelle sind unten offen ausgewiesene Suchparameter,
keine aus Daten bewiesenen Optima. Ihre separate Abstimmung gehört in einen
späteren Vergleich, nicht in nachträgliches Tuning derselben zwölf Seeds.

## Exakte Verfahrensdefinition

**B0:** Fast-A0, 90:10 gewichtete Apex-/Rotationsquelle, dieselbe zufällige
Quellenreihenfolge, Perturbationslängen 2–4/5–12/13–32 mit Gewichten 4:3:2,
Stichprobe 32 für strikten Abstieg, historische Phasengrenzen 45/75 CPU-Sekunden.
Elternwahl 80 % Dreiertournament, 20 % schwächste Herkunftshäufigkeit; Elite 2,
Qualitätsauswahl bis 12, Exploration auf 16, Familienschutz in den ersten fünf
Generationen. Alte Auswahlfunktionen werden unverändert importiert.

Die neuen Archiv- und Beobachtungskosten werden auch B0 belastet. Damit bleibt
B0 eine algorithmische Referenz, aber ist kein bitidentischer historischer
Durchsatzbenchmark. Eine differenzielle vollständige Episode ohne bindende
Zeitgrenze prüft identischen Endgraphen und RNG. Bei zeitgebundenen Phasen kann
zusätzlicher Aufwand die späteren Entscheidungen verändern.

**P:** Dieselbe Eltern-, Längen- und Populationsauswahl. Jeder Perturbationsschritt
wählt gleichverteilt aus der vollständigen eindeutigen Apex-/Pivot-Nachbarschaft.
Der Abstieg wählt den besten strikt besseren Nachbarn; Gleichstand nach stabiler
Generatorreihenfolge (Apex, dann Pivot). Kein 45/75-s-Episodenstopp und kein
32-Züge-Limit. Nur nach vollständig geprüfter Nachbarschaft ist
`LOCAL_MIN_EXACT_AP` erlaubt. P gegen B0 ist ein Verfahrenspaketvergleich, keine
isolierte Messung nur des Pivot-Effekts.

**T:** Start beim besten Gründer im aktiven Ziel. Alle Apex-/Pivot-Nachbarn werden
bewertet. Gelöschte Kanten bleiben für zufällig 7–15 weitere Zugiterationen gegen
Wiedereinfügung tabu. Strikte Verbesserung des aktiven Jobrekords erlaubt
Aspiration. Unter zulässigen Nachbarn: bestes Ziel, bei Gleichstand zufällige
Wahl. Auch neutrale und verschlechternde Schritte sind erlaubt. Sind sämtliche
Züge tabu, wird der Iterationszähler deterministisch bis zum nächsten Verfall
vorgestellt; kein verbotener Zug wird trotzdem übernommen.

Nach 2000 akzeptierten Schritten ohne aktiven Jobrekord folgt ein Restart; ebenso
bei leerem vollständigen Katalog. Der Zähler zählt akzeptierte Schritte, nicht
CPU-Sekunden oder die oben beschriebene Verfallsvorstellung. Restart: mit 25 %
Wahrscheinlichkeit eine gleichverteilte archivierte Klasse, sonst das Zielbeste
aus acht mit Zurücklegen gleichverteilten Archivklassen. Danach 5–8 zufällige
Schritte, Tabuliste anfangs leer. Das Archiv enthält auch nicht akzeptierte
Nachbarn, sofern sie beobachtete Rekorde eines der vier Ziele sind. Somit ist die
passive Zielbeobachtung bei T/TC über spätere Restarts nutzbar, jedoch nicht durch
Migration aus anderen Jobs. Diese Regel ist bei T und TC identisch.

**TC:** Identisch zu T, zusätzlich vollständiger allgemeiner Dreierzyklus aus dem
bereits geprüften Kompatibilitätsdigraphen. Kein „erste 32 Zyklen“-Filter. Der
primäre Test des zusätzlichen Operators ist TC gegen T bei identischem Budget.
Größere Kataloge kosten mehr Zeit; gleicher CPU-Aufwand, nicht gleiche Zuganzahl,
ist die Vergleichsbasis.

Rekordprüfung und jede Übernahme verwenden zusätzlich den unabhängigen Verifier.
Inkrementelles Scoring verändert nur die Berechnung der exakt ganzzahligen
Werte. Apex benutzt die ganzzahlige Reviewer-M4-Bedingung; Pivot benutzt die
bereits unabhängig hergeleitete CN=1-Bedingung für beide neuen Basiskanten.
Die Kataloge setzen gültige λ-Eingaben voraus.

## Messung, Entscheidung und Fortsetzung

Primärer Endpunkt ist der **aktive** (W,L1)-Rekord nach 3600 Budgetsekunden im W-Job.
Ergänzend: alle Ziele und Messpunkte; beobachtete, auch verworfene Nachbarrekorde;
CPU bis Verbesserung; Klassen/Endklassen; realisierte Perturbations- und
Abstiegslängen; Rückkehr zum identischen/kanonisch gleichen Ausgang; Herkunft
und Operatorhäufigkeit; akzeptierte Pfadmaxima relativ zum jeweiligen Start.
Letztere sind beobachtete Exkursionshöhen, keine minimax-optimalen Barrieren.
Bei T/TC stehen der noch laufende Pfad und seine Maxima zusätzlich im Endresultat.

Vorab festgelegte **deskriptive** Auswahlschwelle: mindestens acht Siege und
höchstens zwei Niederlagen in zwölf gepaarten aktiven W-Endpunkten gegenüber B0.
TC muss zusätzlich diese Schwelle gegenüber T erfüllen, um speziell den
Dreierzyklus als Hauptmethode zu begründen. Paarwerte bleiben vollständig sichtbar;
die Regel ist kein Signifikanztest. Andere Ziele informieren über Zielkonflikte,
ersetzen aber nicht nachträglich den primären W-Endpunkt. Kein robustes Signal:
Baseline als Referenz behalten und anhand der Kurven über Fortsetzung oder
gezielte Änderung entscheiden. Einzelrekorde werden unabhängig davon gesichert.

Messpunkte gehören zu derselben Trajektorie; es gibt keine Neustarts bei 10/30/60
Minuten. Die fünf Sekunden Abschlussreserve sind im Budget enthalten. Ungenutzte
Reserve eines abgeschlossenen Endpunkts bleibt bei Verlängerung als geschlossener
Budgetanteil verbraucht, wird aber nicht als tatsächlich gerechnete CPU verbucht.
Receipts enthalten beide Größen und jede wait4-Sitzung. Dadurch kann eine spätere
Verbesserung nicht rückwirkend den 3600-s-Endpunkt ändern. Replay nach Pause zählt
voll, ebenso Verifikation, Kanonisierung, SQLite-Zugriffe und Checkpoints im Worker.

Fortsetzung speichert alte Endpunktdateien unverändert, erhöht nur das separate
Budgetledger und setzt denselben Suchzustand fort. Abbruch ohne belastbaren
CPU-Receipt wird nicht durch ein neues Budget kaschiert. Keine Änderungen an
Office oder fremden Prozessen; der Controller sendet Signale nur eigenen Kindern.

Ein Nullresiduen-Kandidat wird unabhängig für n=99, Grad 14 und sämtliche Paare
geprüft, dauerhaft als graph6 mit Hash und Prüfbericht gesichert und führt zum
kontrollierten Stopp. Das positive technische Fixture ist ausdrücklich kleiner;
es ist kein gefundener srg(99,14,1,2).

## Lieferstand und Beleggrenzen

Code: `experiments/memetik/lambda_compare_0_2_0`.
Kontrollberichte: `CONTROLS.json`, `INTEGRATION.json`, `PREPARATION.json` im
vorliegenden Dokumentationsverzeichnis. Die Kontrollen laufen zusätzlich vor dem
Ryzen-Vergleich aus dessen eingefrorenem Bundle. Die lokale Prozesskontrolle
ersetzt ausschließlich im Test die Hostabfrage; die tatsächliche WSL-/Windows-
Vorprüfung muss auf Ryzen erfolgen. Bis dahin ist kein Ryzen-Durchsatz gemessen
und kein Ergebnis der 192-Stunden-Kampagne vorhanden.
