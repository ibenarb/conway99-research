# Conway99 dauerhaft gesunde Zeilen — Pilot 0.1.0

Ziel: monotone Vergrößerung einer **geschützten Gesundheitsmenge** bei festem `1+14+84`-Rand; nur Kanten im symmetrischen `84x84`-Block H werden verändert.

## Modell
Für die vollständige 99x99-Adjazenzmatrix `B` gilt für `i != j` Gesundheit genau dann, wenn `(B^2)[i,j] + B[i,j] = 2`. Das bestehende Projektmaß `W` ist daher exakt die Zahl ungesunder ungeordneter Paare. Eine vollständige gesunde Zeile `i` bedeutet Gesundheit aller 98 Paare `{i,j}`.

Varianten:
- `targeted`: anfangs nichts geschützt; nach Vollendung einer Zeile werden alle 98 Beziehungen dieser Zeile geschützt.
- `strict_initial`: alle bereits im Startgraphen gesunden Paare sind von Beginn an geschützt; anschließend wie `targeted`.
- `frozen_rows`: wie `targeted`, zusätzlich werden nach Vollendung die H-Kantenwerte der Zeile eingefroren. Dies ist ausdrücklich nur Vergleichsarm.
- `baseline_W`: gewöhnliche W-Minimierung ohne Gesundheitsschutz.

Die Suche benutzt grad-erhaltende 2-Switches in H sowie atomare Doppel-Switches. Ein atomarer Doppel-Switch wird nur im Endzustand auf sämtliche geschützten Paare geprüft. Jede akzeptierte Veränderung wird außerdem gegen Symmetrie, Grad 14 und den vollständigen festen Rand geprüft. Sackgassen werden nur als `SEARCH_STUCK` bzw. `TIME_BUDGET` bezeichnet; 0.1.0 enthält **keinen** Unmöglichkeitsbeweis.

Population: 8 parallele Lanes = 4 targeted, 2 strict_initial, 1 frozen_rows, 1 baseline_W. Zeilenreihenfolgen und Seeds unterscheiden sich. Bei Fehlschlag einer Zielzeile wird kontrolliert zu einem früheren Zustand zurückgekehrt und der Rest der Reihenfolge neu gemischt. Checkpoints sind atomare JSON-Dateien; Statusausgabe alle 600 s ist kürzer als 80 Zeichen.

## Kandidat M
`M` ist absichtlich **nicht** mit `B_maple_20260829` oder einem anderen Kandidaten gleichgesetzt. `config.office.json` blockiert den Produktionsstart, bis die tatsächliche Quelldatei eingetragen und der feste Rand verifiziert ist. `discover_m.py` durchsucht den lokalen Conway99-Arbeitsbaum nach plausiblen M-/Maple-Dateien und prüft graph6-Treffer unabhängig.

## Ressourcen
Office: 8 Prozesse (4+4 logisch), Ziel-Walltime 18 h pro Lane. Kleine lokale Zeitüberschreitungen werden nicht als mathematischer Befund interpretiert. Relevante Betriebsregeln: GC-01, GC-02, GC-06, GC-08, GC-10, GC-11, GC-14, GC-15.

## Kontrollen
`test_pilot.py` prüft u.a., dass eine Änderung eine geschützte Beziehung an anderer Stelle beschädigen kann und dies erkannt wird. Der Produktions-Preflight validiert jede Quelle auf 99 Knoten, Symmetrie, Grad 14 und exakten Rahmen.

## Darstellung
`render_state.py CHECKPOINT.svg` erzeugt aus einem Checkpoint eine SVG-Matrix. Grün/rot zeigen aktuelle Gesundheit; dunkelgrün geschützte Beziehungen, blau eingefrorene H-Kantenwerte, gelb die aktuelle Zielzeile und grau den festen Rand. Damit bleibt sichtbar, dass Schutzbeziehungen über die gesamte 99x99-Matrix laufen und der Rest kein automatisch kleineres SRG-Problem ist.

## Reproduzierbarkeit
Regel- und Quellbaseline vor diesem Paket: `cfce7a66750328eb8cf6b9d15fb7c34fba05884a` auf `memetik`.
Lokales Pilotarchiv SHA256: `c31e3405db3ee67a6d1a27598a54448462318a92a47fa04bdb039162b7064845`.
