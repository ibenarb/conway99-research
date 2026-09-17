# Fehlerbarrieren und Strukturvielfalt – Office Escape 0.2.2

## Ergebnis

| Start / Ziel | Geschlossene Komponente unter | Beschriftete Graphen | Isomorphieklassen | Kleinster Randwert | Notwendige Barriere |
|---|---|---:|---:|---:|---:|
| HoG57338 / F=2836 | F<2928 | 85 | 85 | 2928 | mindestens 92 |
| B-Endpunkt / W=2082 | W<2094 | 13 | 13 | 2094 | mindestens 12 |

Beide Komponenten wurden ohne Tiefengrenze bis zum Abschluss enumeriert.
Bei HoG wurden 3817 gerichtete Trades erzeugt, bei B 3425. Innerhalb gibt es
120 bzw. 13 ungerichtete Nachbarschaftskanten. Sämtliche Operatorfamilien
wurden an jedem Zustand vollständig enumeriert. Der beste interne Zielwert
ist jeweils genau der Startwert. Alle internen Graphen erfüllen den Armvertrag;
ihre Kennzahlen wurden zusätzlich unabhängig mengenbasiert nachgerechnet.
Die Randkennzahlen wurden mit dem bisherigen exakten ganzzahligen Scorecode
berechnet. Es erfolgte keine zweite unabhängige Nachrechnung aller Randgraphen.

Begründung: Jeder Weg zu einem besseren Zielwert muss die erreichbare
Startkomponente im strikten Sublevel verlassen. Sein erster äußerer Zustand
hat mindestens den angegebenen Randwert. Das gilt für beliebige Weglängen,
aber ausschließlich für den implementierten Operatorenkatalog. Es beweist
weder die Existenz eines Verbesserungswegs noch die Hinlänglichkeit der Barriere.
Die Komponenten sind NICHT die gesamten unbeschränkten Suchkomponenten.
HoG verbessert die bisherige notwendige Schranke +88 auf +92. Die B-Schranke
+12 gilt ab W=2082; sie ersetzt nicht die frühere exakte +4-Barriere ab B_original/W=2110.

Die bisherigen Weglängenschranken bleiben: HoG mindestens fünf Schritte,
B ab 2082 mindestens drei, falls überhaupt ein Verbesserungsweg existiert.

## Warum Barrierensteuerung statt nur größerer BFS-Tiefe?

Die neue B-Sublevelkomponente enthält vier Graphen der Weglänge drei, die noch
nicht in der großen Office-Datenbank gespeichert waren. Für drei weitere
bekannte Zustände ist ein Weg mit niedrigerer maximaler W-Höhe vorhanden als
der dort gespeicherte erste BFS-Weg. Alle 13 Graphen sind paarweise nichtisomorph.
Damit gibt es konkrete strukturell verschiedene und niedrig-barrierige Wege,
die in der rein nach Weglänge und Entdeckungsreihenfolge gesteuerten Suche
noch nicht oder nur über ungünstigere Elternpfade erschlossen waren.
Keiner dieser vier neuen Graphen ist W-besser als der Start.

Die 85 HoG-Sublevelgraphen waren bereits gespeichert (Tiefen 0:1, 1:36, 2:46, 3:2).
Ihre gespeicherten BFS-Wege besitzen bereits die minimale Fehlerhöhe innerhalb
der geschlossenen Sublevelkomponente. Hier entsteht der Mehrwert durch die
stärkere Barrierenuntergrenze, nicht durch neue Graphen.

Nächste Suchrichtung: Minimax-Suche, priorisiert nach der kleinsten bekannten
maximalen Fehlerhöhe eines Wegs. Für eine Kante u->v gilt die Relaxation
b(v) = min(b(v), max(b(u), Zielwert(v))). Erneute Entdeckung muss den Wegwert
verbessern können; ein einziges unveränderliches BFS-Elternfeld reicht nicht.
Gleichstand deterministisch, vollständige Familienprüfung, beschriftete
Identität und nachvollziehbare Wege beibehalten. HoG zunächst am nächsten
zulässigen Rand F=2928, B am Rand W=2094 öffnen; keine willkürlichen Sprünge
in hohe Fehlerbereiche und keine globale Erfolgsgarantie.

Die vorhandenen Office-Checkpoints unverändert bewahren. Ein neues Verfahren
braucht eine eigene Zustands-/Kantenablage oder geprüfte Migration. Keine
ungeprüfte Umdeutung der bisherigen BFS-Datenbanken. In dieser Sitzung wurde
kein neuer Office-Lauf und noch kein neues produktives Suchpaket gestartet.

## Strukturelle Wiederholungen

Exakte kanonische Zertifikate mit pynauty/nauty für ungefärbte vollständige
99-Knoten-Graphen. Automorphismengeneratoren der ausgewählten Datenbankgraphen
wurden zusätzlich direkt an allen Knotenpaaren geprüft. Keine Isomorphiequotienten
wurden in irgendeiner Suche verwendet. Ω-Rahmenverträglichkeit einer Quotientensuche
ist durch ungefärbte Graphisomorphie allein nicht gewährleistet.

| Explizit untersuchte Menge | Beschriftete Zustände | Isomorphieklassen |
|---|---:|---:|
| HoG: Start und alle direkten Nachbarn | 47 | 47 |
| HoG: alle gespeicherten Graphen mit F<=2932 | 159 | 159 |
| HoG: feste Zufallsstichprobe der offenen Frontier | 256 | 256 |
| B: Start und alle direkten Nachbarn | 270 | 266 |
| B: alle gespeicherten Graphen mit W<=2100 | 40 | 29 |
| B: feste Zufallsstichprobe der offenen Frontier | 256 | 256 |

Die Mengen überlappen und dürfen nicht addiert werden. Bei B ist der zweite
W=2082-Zustand (ID 1947) zum Start isomorph. Er ist keine neue Struktur.
Diese Befunde rechtfertigen keine Behauptung, alle 634370 gespeicherten Zustände
seien klassifiziert. Besonders bei HoG gibt es in den untersuchten Mengen
keinen Hinweis auf starke Einsparung durch Isomorphiededuplikation.

## Zielkonflikte

Alle gespeicherten Kennzahlen wurden nach Ziel und Tiefe ausgewertet. Die unten
angegebenen Extremalzeugen und ihre gespeicherten Elternwege wurden zusätzlich
unabhängig auf Arm, Kennzahlen und Kantenänderungen geprüft. Keine erneute
unabhängige Bewertung aller Datenbankgraphen. Die Auswahl bei Linf erfolgt
lexikographisch nach (Linf,Nmax,L1).

| Linie / Auswahl | W | L1 | F | Linf | Nmax |
|---|---:|---:|---:|---:|---:|
| B: Start / bestes W | 2082 | 3368 | 9060 | 10 | 38 |
| B: kleinstes gespeichertes L1 | 2090 | 3336 | 8708 | 10 | 30 |
| B: kleinstes gespeichertes F | 2181 | 3402 | 8478 | 10 | 24 |
| B: bestes gespeichertes Linf-Tupel | 2174 | 3398 | 8482 | 10 | 24 |
| HoG: Start / bestes W,L1,F | 2182 | 2398 | 2836 | 3 | 3 |
| HoG: bestes gespeichertes Linf-Tupel | 2229 | 2476 | 2972 | 3 | 1 |

Dies sind verschiedene Graphen, keine kombinierbaren Bestwertvektoren und
keine globalen Projektbestwerte. Das bessere HoG-Linf-Tupel senkt Nmax, nicht Linf.
Das bestärkt die Trennung von Zielkonflikten und bestätigt nicht die Überlegenheit
einer Norm. Der Populationspilot bleibt nachgeordnet.

## Reproduktion und Provenienz

Eingang: Ergebnisse_Escape_022_continue_20260917_043002_073517.zip,
SHA256 18723e6b853bdeeb522cef271ebdd451805c7af755aa5ea7c827d314fbf9b440.
Datenbanken wurden nur lesend geöffnet. Operator-/Scorequellen unter source/
stammen byteidentisch aus der enthaltenen Zipapp 0.2.2. Codeabhängigkeit für
Isomorphie: pynauty, genaue Version in diversity.json.

Arbeitslayout der Analyseskripte: Original-ZIP in ein Verzeichnis audit022/
entpacken; dieses Berichtsverzeichnis als analysis022/ daneben ablegen.
Vom gemeinsamen Elternverzeichnis scan.py und diversity.py ausführen.
Sublevelaufrufe verwenden task, arm, objective, strict_threshold als Argumente:
HoG57338__bfs_F lambda F 2928 bzw. B_escape_W2082__bfs_W omega W 2094.
Die Schutzgrenzen der lokalen Sublevelprüfung sind 240 CPU-Sekunden und 3000
Zustände; beide tatsächlichen Läufe endeten vollständig vor den Grenzen.
Gemessen wurden rund 162 bzw. 238 CPU-Sekunden in der Analyseumgebung, keine
Office-Laufzeitprognose. Die Vollständigkeit stützt sich auf diese Enumeration,
nicht auf die Schutzgrenzen. Die komprimierten Sublevel-JSONs enthalten alle
inneren Graphen, Kennzahlen, Familienzensen und inneren Übergänge. Vor Ausführung
von component_summary.py müssen sie wieder als *_sublevel.json vorliegen.

scan.json enthält Häufigkeiten der maximalen Fehlerhöhe der gespeicherten
BFS-Elternwege; diese sind im Allgemeinen KEINE minimalen Barrieren.
component_summary.json verwendet hingegen eine Minimax-Berechnung auf den
vollständig enumerierten inneren Komponentenkanten.

Die größeren JSON-Ausgaben (scan, diversity, extrema_witnesses und Sublevelzertifikate) sind gzip-komprimiert archiviert. verify_extrema.py liest die komprimierte Zeugendatei direkt.
