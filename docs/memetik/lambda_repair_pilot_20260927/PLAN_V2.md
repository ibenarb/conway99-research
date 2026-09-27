# Gemeinsame Kantenreparatur: erweiterter Pilot V2

27.09.2026. Ralph Beckmann hat dem Pilotversuch zugestimmt und ausdrücklich
eine breitere Startpopulation sowie ausreichende Ryzen-Ressourcen verlangt.
Dieser Plan ersetzt den Zwei-Start-/Drei-CPU-Stunden-Vorschlag vom selben Tag.
Vorbereitet und geprüft sind Startbank und Fenster. Ein ausführbares
Solver-/Ryzen-Paket ist hiermit noch nicht veröffentlicht; kein neuer
Suchlauf wurde gestartet.

## Fragestellung und Umfang

Kann gemeinsame exakte Neuverdrahtung innerhalb größerer Knotenfenster
einen unabhängig geprüften λ-Kandidaten mit **W<2076** erzeugen?
Zusätzlich messen wir Fortschritt relativ zum jeweiligen Gründer,
Zeit bis zum ersten Treffer, Schranken und tatsächlich abgeschlossene
Aufgaben. Vielfalt und geringere Rückkehrquoten gelten nicht als Erfolg.

Der frühere Vorschlag war als technischer Funktionstest brauchbar, für
eine strategische Negativentscheidung aber zu schmal. Mehr Ressourcen
werden nun sowohl für mehr Gründer als auch für größere gemeinsame
Änderungen und längere Einzelrechnungen eingesetzt.

## Eingefrorene Startbank

`MANIFEST.json` enthält 24 vollständige graph6-Datensätze, Zustands- und
Klassenkennungen sowie alle 144 konkreten Fensteraufgaben. Alle Starts
wurden erneut unabhängig auf Grad, λ und W/L1/F/Linf/Nmax geprüft und
mit dem isolierten pynauty-2.8.8.1-Audit kanonisiert. Die 24 Klassen sind
paarweise verschieden. Das beweist keine 24 unabhängigen Suchbecken.

Quelle ist das bereits geprüfte Profil-Endarchiv, SHA256
`ccdb709a98ab0e5f32794807955026e1fe2819364de668f9eb3c37fe4854c2f3`.
Es enthält genügend bestehende Endpunkte; neue Gründer-Suchläufe sind
für diese Vorbereitung nicht erforderlich.

Je Herkunftslinie werden zwölf Klassen gewählt:

- Sechs beste nach (W,L1,state), einschließlich des jeweiligen Originals.
- Sechs weitere durch deterministische Maximin-Auswahl anhand von
  isomorphieinvarianten Fehlermerkmalen, mit W höchstens Original-W+100.

Die Merkmale sind die sortierten 99 Fehlergrade und das Histogramm der
gemeinsamen Nachbarzahlen an Nichtkanten. Verwendet wird die L1-Differenz
des Vektors `(42*sortierte Fehlergrade, Histogramm)`. Die Skalierung und
die W+100-Grenze sind vorab gewählte heuristische Designentscheidungen,
keine mathematisch begründeten Beckenabstände. Gleiche Merkmale beweisen
keine Isomorphie; unterschiedliche Merkmale keine Suchunabhängigkeit.

Es gibt 206 geeignete Klassen aus A und 220 aus B, vor globaler
Deduplikation. Auswahlreihenfolge ist A, dann B; bereits gewählte Klassen
werden ausgeschlossen. Es wird daraus kein kausaler Familienvergleich
abgeleitet. Herkunft bezeichnet beobachtete Profilherkunft, keine
bewiesene Trennung der Landschaft.

| Herkunft | Sechs beste W | Sechs zusätzlich gewählte W |
| --- | --- | --- |
| A, Original 2076 | 2076, 2077, 2079, 2082, 2083, 2086 | 2175, 2132, 2114, 2157, 2157, 2125 |
| B, Original 2077 | 2077, 2085, 2088, 2088, 2089, 2089 | 2177, 2139, 2170, 2171, 2176, 2128 |

Die Hälfte der Bank konzentriert sich damit auf gute Scores, die andere
erweitert die beobachteten Fehlerprofile innerhalb eines begrenzten
Qualitätsverlusts. Es bleibt eine feste Startbank, keine fortlaufend
selektierte memetische Population. Neue Treffer werden archiviert, aber
nicht während dieses Piloten zu neuen Aufgaben verarbeitet.

## Vergleichsarme und konkrete Fenster

24 Starts × drei Größen (24, 40, 60 Knoten) × zwei Auswahlregeln ergeben
**144 Aufgaben**, jeweils mit einer CPU-Stunde Obergrenze.

Beide Regeln wachsen entlang bestehender Kanten, sodass jedes Fenster
zusammenhängend ist. Die erste priorisiert hohen Fehlergrad, die zweite
eine feste Pseudozufallsreihenfolge. SHA256-Rangfolgen mit vollständig
veröffentlichten Seedtexten bestimmen Startknoten und Gleichstände;
die Implementierung steht in `prepare_manifest.py`. Alle konkreten
Knotenlisten sind bereits festgelegt, innerhalb eines Gründers verschieden
und werden nicht anhand von Suchergebnissen ersetzt.

Größen und Regeln sind die Vergleichsarme, mit denselben Gründern und
denselben CPU-Obergrenzen. Pro Gründer/Größe/Regel gibt es nur ein Fenster:
dies ist ein breiter Mechanismus-Pilot, keine präzise Schätzung der
Fenster-Auswahlverteilung. Bei einem positiven Signal gehört eine
Wiederholung mit neuen Fenstern in eine separate Bestätigungsphase.

## Bereits durchgeführte Randbedingungen-Prüfung

`check_boundary.py` propagiert ausschließlich notwendige Bedingungen:
interne Restgrade, λ=1 an festen Fenster-Außen-Kanten und verbotene
interne Kanten bei mehr als einem gemeinsamen Außennachbarn. Keine Suche,
keine neue Optimierung, keine Änderung eines Startgraphen.

| Fenstergröße | Aufgaben | Vollständig festgelegt | Noch freie Kantenvariablen, Median |
| --- | ---: | ---: | ---: |
| 24 | 48 | 5 | 22,5 |
| 40 | 48 | 0 | 229,5 |
| 60 | 48 | 0 | 1040 |

Die fünf vollständig festgelegten Fenster können keinen anderen
zulässigen Graphen enthalten. Sie werden als solche dokumentiert und
brauchen keine lange Solverrechnung. Freie Variablen in anderen Fenstern
beweisen dagegen weder einen alternativen zulässigen Graphen noch dessen
Verbesserbarkeit. Dieser Befund begründet größere Fenster besser als
eine bloße Erhöhung der Laufzeit kleiner Fenster.

## Modell, Kontrollen und Zielfunktion

Nur Kanten mit beiden Endpunkten im Fenster sind variabel. Grad14 und
λ=1 gelten hart für den vollständigen Endgraphen. Globale Zielfunktion
bleibt lexikographisch (W,L1), etwa als `50000*W+L1`; unter den harten
Bedingungen ist L1≤49896. Fenster-Außen-Paare gehören in Modell und
Bewertung. Außen-Außen-Paare bleiben unverändert. Zwischenbelegungen des
Solvers müssen keine λ-Graphen und keine AP-Zugfolge bilden.

Vor produktiver Suche müssen erfüllt sein:

1. Startbelegung in jedem Modell zulässig, Startscore exakt reproduziert.
2. Kleine vollständige Modelle gegen exhaustive Enumeration geprüft.
3. Bekannte Reparatur N=(2077,2488)→A=(2076,2488) mit enthaltenem
   Acht-Knoten-Zugträger wiedergefunden und unabhängig geprüft.
4. Prozessabbruch, CPU-Buchung, Checkpoints und Wiederaufnahme geprüft.
5. Speicherbedarf der drei Größen gemessen und Parallelität danach
   festgelegt. Größenverkleinerung oder Modellvereinfachung niemals still.

Ein Kontrollfehler stoppt die Freigabe produktiver Aufgaben. Bestehende
Ryzen-Umgebungen bleiben unverändert; eine Solverabhängigkeit gehört in
eine neue isolierte Umgebung mit fixierten Versionen. Das ausführbare
Paket muss die hier eingefrorenen Daten und die Budgetregeln übernehmen.

## Ryzen-Ressourcen

| Posten | Obergrenze |
| --- | ---: |
| 144 Aufgaben, jeweils einschließlich Modellbau/Initialisierung | 144 CPU-h |
| Kontrollen, Kalibrierung, Koordination, unabhängige Nachprüfung | 12 CPU-h |
| Gesamt | **156 CPU-h** |
| Aktive Windows-Host-Walltime | **24 h** |
| Gleichzeitige Solverprozesse | bis zu 12, ein CPU-Thread je Prozess |

Nicht verbrauchte Aufgabezeit wird nicht automatisch auf andere Aufgaben
übertragen. Die fünf starren Fenster reduzieren den tatsächlichen Bedarf.
Die Obergrenze ist kein Verbrauchsziel. Nach vollständigem exaktem
Abschluss einer Aufgabe wird ihr Prozess sofort beendet. Ein neuer
W-Rekord beendet die übrigen Aufgaben nicht automatisch; W=0 beendet nach
unabhängiger Prüfung die Kampagne.

Bei zwölf dauerhaft verfügbaren Kernen beträgt die rechnerische volle
Budgetlaufzeit 13 Stunden. **Vorläufiges Planungsfenster: etwa 14–20 Stunden**,
abhängig von Speicher, Last, unterschiedlich frühen Abschlüssen und
Verifikation; keine Leistungsmessung oder Zusage. Bei weniger Parallelität
kann die 24-h-Grenze vor dem CPU-Budget erreicht werden. Dann lautet das
Ergebnis ausdrücklich unvollständig.

Nach Kalibrierung höchstens 24 GiB Gruppen-RAM und mindestens 6 GiB
freier RAM. Bei Unterschreitung werden zunächst keine neuen Aufgaben
gestartet; bestehende Prozesse werden bei einer tatsächlichen
Grenzüberschreitung kontrolliert beendet und als unterbrochen erfasst.
Keine Überbelegung durch solverinterne Threads. Windows-Host-Monotonzeit,
wait4-CPU-Abrechnung und Status alle zehn Minuten mit ETA. Die ETA muss
auf verbleibenden Aufgaben/Budgets beruhen und nach Kampagnenende entfallen.

## Vorabentscheidungen

- **Primär positiv:** unabhängiger gültiger λ-Graph mit W<2076.
  Das ist ein neuer Rekord und ein Mechanismusnachweis, keine Garantie
  der Konvergenz zu W=0. Bestätigungsversuch separat planen.
- **Sekundär:** verbesserter (W,L1)-Wert relativ zu einem Gründer,
  neue Klassen, beweisbare Schranken und Kosten. Diese Befunde begründen
  allein keine große Folgekampagne, helfen aber, die Methode zu beurteilen.
- **Kein Rekord:** Ergebnis nach abgeschlossenen, exakt ausgeschlossenen
  und ungelösten Aufgaben aufschlüsseln. Keine automatische Verlängerung.
  Viele Timeouts zeigen vor allem eine Grenze von Modell/Solver/Budget;
  sie schließen weder größere Reparaturen noch die λ-Suche aus.
- **Abschluss mit Ausschlussbehauptung:** nur bei tatsächlich gesichertem
  exaktem Ergebnis; bei SAT ist ein geprüftes Zertifikat erforderlich.
  Die Aussage gilt ausschließlich für das konkrete eingefrorene Fenster.
- **Technischer Abbruch:** fehlerhafte Kontrolle/Verifikation,
  Budget- oder Speichergrenze, beschädigte Eingaben oder CPU-Abrechnung.
  Verwertbare Teilergebnisse und bereits verbrauchte Ressourcen erhalten.

Insbesondere entfällt die frühere pauschale Folgerung, bereits nach
16 erfolglosen Kurzaufgaben die konstruktive λ-Linie ruhen zu lassen.
Nach diesem breiteren Pilot entscheiden wir anhand der tatsächlich
gelösten Aufgaben und der Qualität der erreichten Schranken. Mehr
Rechenzeit ersetzt dabei weder einen brauchbaren Freiheitsgrad im
Modell noch ein nachvollziehbares Entscheidungskriterium.
