# λ-Vorprüfungen 1.0.0 — Ryzen, 24. September 2026

Freigegebene Umsetzung der im Chat beschlossenen V1/V3-Etappe. Keine V2-Rekordspur,
kein Hauptlauf, keine Wiederaufnahme alter Suchjobs. Referenzquellen 3bafd48,
Ergebnis-/Reviewergrundlage 7f146a2. Die 46 eingefrorenen Quelldateien bleiben unverändert.

## Experiment und Budget

| Teil | Aufbau | Such-CPU |
|---|---|---:|
| V1 | 8 neue Seedpaare; P und PCesc, je 3600 s, identische originale 16er-Gründerbank | 16 h |
| V3 | 4 isolierte Herkunftslinien × 2 Replikate × 7200 s; P | 16 h |
| Hilfsarbeiten | Hostprobe 1140 s; Kontrollen 4260 s; gesamte Infrastruktur 1800 s | höchstens 2 h |
| Summe | 24 Jobs, keine automatische Verlängerung | höchstens 34 h |

V1 startet als vollständige Welle mit 16 Ein-Kern-Workern. V3 startet erst danach
mit acht Workern. Frei werdende V1-Slots werden nicht mit V3 gefüllt. So werden
kontrollierte Vergleiche nicht mit neuen Jobtypen vermischt. Unterschiedliche
SMT-/Cache-Effekte zwischen Varianten bleiben grundsätzlich möglich; die
gemeinsame Welle reduziert den historischen Belegungsunterschied.

V1-Seeds: 2026092400 bis 2026092407, innerhalb eines Paares identisch.
V3-Seeds: 2026092500 bis 2026092507. Ziel stets lexikographisch (W,L1).
V1-Messpunkte: 600/1800/3600 CPU-s; V3 zusätzlich 7200 CPU-s. Die gemeinsame
Abschlussreserve von 5 CPU-s gehört zum Jobbudget; Messpunkte am Budgetende
tragen den zuletzt erreichten Bestwert fort. Keine Suche in der Reserve.

## PCesc

Perturbation und normaler Abstieg verwenden ausschließlich Apex und Pivot (AP).
Erst wenn ein **vollständig** ausgewerteter AP-Katalog keinen strikt besseren
Zug enthält, wird cycle3 vollständig ausgewertet. Der beste strikt verbessernde
cycle3-Zug wird angenommen; danach beginnt wieder AP. Ohne Verbesserung endet
die Episode. Keine neutralen oder verschlechternden cycle3-Fluchten.

Die eingefrorene P-Logik, Elternauswahl, Perturbationslängen und Populationsauswahl
bleiben bestehen. Beide Arme tragen dieselbe zusätzliche Instrumentierung.
`experiment_metrics` protokolliert AP-/cycle-Katalog-CPU einschließlich Bewertung,
cycle-Abfragen, abgeschlossene Abfragen, Abfragen mit Verbesserung, adoptierte
cycle-Züge und Replay. Die vorhandenen Histogramme protokollieren Rückkehr in
dieselbe Isomorphieklasse. Ein angefangener Katalog ist kein bewiesenes Minimum.

## Isolierte V3-Startpopulationen

Gründer: gen-lambda-11, gen-lambda-13, gen-lambda-03, claude_v01_c.
Die ersten drei sind Z33_lift, der letzte triangle_packing. endpoint_Linf2_N262
ist HoG-abstämmig und wird NICHT als unabhängiger Gründer verwendet.

`ISOLATED_BANKS.json` enthält pro Gründer 16 kanonisch verschiedene Kandidaten:
den Gründer selbst sowie die ersten 15 neuen Isomorphieklassen eines festen,
zufälligen AP-Walks ohne Fitnessselektion. Seeds 20260924000 bis 20260924003.
Beide Wiederholungen einer Linie erhalten dieselbe Bank. Alle 60 Übergänge sind
mit Operator, Zug und Resultat aufgezeichnet und werden vor Produktion erneut
geprüft. Die etwa 15 CPU-s zur Erzeugung sind Entwicklungsaufwand vor dem Lauf,
separat protokolliert; es ist keine heimliche Ryzen-Suche. Jede Linie bleibt in
ihrer eigenen Population, ohne HoG-Zumischung und ohne Migration.

Die 16er-Startbank ist nötig für die eingefrorene Auswahl. V3 misst daher die
Exploration aus einer kleinen gültigen AP-Umgebung des Gründers, nicht nur einen
strikten Abstieg direkt aus dem unveränderten Gründer. Die vier Linien sind
keine nachgewiesenen unabhängigen Attraktionsbecken.

## Vorab festgelegte Auswertung

V1 primär: die acht gepaarten Differenzen der Endwerte (W,L1) bei 3600 CPU-s,
Median der W-Differenzen, alle Einzelpaare und Sieg/Gleichstand/Niederlage.
Sekundär: Verläufe, Episoden je zugeteilter CPU-h, cycle-CPU-Anteil, erfolgreiche
cycle-Erweiterungen und isomorphe Rückkehr. Kein automatisches 4-aus-8-Kriterium,
keine pauschale 90-%-Durchsatzhürde. Ein knapper Ausgang ist offen. Ein negativer
Ausgang verwirft nur diese getestete Einsatzregel, nicht den Operator generell.

V3: beide Wiederholungen getrennt berichten, absolute Endwerte, Verbesserungen
gegenüber dem anfänglichen Bankbestwert, Verläufe und Klassenkennungen.
W<2200 ist ein positives Signal, keine notwendige Bedingung für den Wert einer
Familie. Kein Schluss auf vollständige Exploration oder Nichtexistenz.

Die vorbereitete Auswertung prüft Receipts, SQLite-Integrität, Kurven- und
Kandidatenscores sowie die Herkunft aller V3-Endpopulationen. Ein exakter
Nullresiduenkandidat wird vom unabhängigen Projektprüfer kontrolliert und
zweifach gesichert; dann werden nur eigene Worker geordnet gestoppt.

## Start und Fortsetzung

Vorhandenen Ryzen-Interpreter `~/conway99_workspace/venvs/memetik/bin/python`
verwenden, pynauty 2.8.8.1. Kein Office-Lauf. Das Paket ist eigenständig; alte
Runs müssen weder verschoben noch verändert werden.

Nach dem Entpacken startet `start.py` im Paketwurzelverzeichnis nacheinander
Vorbereitung, echte WSL-/Windows-Hostprobe, Kontrollen und den Hintergrundlauf.
Das neue Runverzeichnis ist standardmäßig
`~/conway99_workspace/ryzen_lambda_prechecks_100_20260924`.
Ein vorhandenes Verzeichnis wird nicht überschrieben. Bei einer Unterbrechung
nicht `start.py` neu ausführen, sondern den dokumentierten Run-CLI benutzen.

Der CLI liegt unter `experiments/memetik/lambda_prechecks_1_0_0/run.py` und bietet
prepare/check/launch/status/pause/evaluate/export. Nach der Vorbereitung führen
schreibende Aktionen automatisch die eingefrorene Programmkopie im Run aus.
`pause` signalisiert nur den eigenen eindeutig identifizierten Controller.
`launch` setzt eine sauber pausierte Rechnung mit Restbudget und RNG-Zustand
fort. Ungeklärte aktive Marker oder technische Fehler verlangen Diagnose;
keine automatische Löschung und kein unkontrollierter Neustart.

Status mit ETA alle zehn Minuten in `controller.log` und `status.json`, keine
automatischen Chatnachrichten. Windows liefert die Host-Zeit; Worker-CPU wird
mit getrusage und wait4 abgerechnet. Voraussichtlich etwa 3–5 Stunden inklusive
Kontrollen bei vergleichbarer Ryzen-Leistung; keine Laufzeitgarantie.

Ressourcen: 1 GiB Adressraum je Worker, 36 GiB eigene Gruppe, 6 GiB RAM-Reserve,
20 GiB Linux- und 50 GiB Windows-VHDX-Plattenreserve. Die Hostprobe verwendet
kurzzeitig 18 Worker. Technische Risiken pausieren die eigenen Prozesse;
Stagnation allein beendet keine Suchjobs.

## Prüfstatus

Die ausgelieferten TEST_RESULTS enthalten echte kurze Linux-Workerläufe mit
Pause/Wiederaufnahme, Budgetabrechnung und negativen Manipulationskontrollen.
Hostdaten im Integrationstest sind ausdrücklich Fixtures. Die echten
Windows-/WSL-Kontrollen müssen auf dem Ryzen bestehen; ein Containertest ersetzt
sie nicht. Das Paket startet die Suche erst nach diesen Gates.
