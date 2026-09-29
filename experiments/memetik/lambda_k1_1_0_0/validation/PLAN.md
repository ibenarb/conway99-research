# K1: Implementierte großzügige Kampagne, 29.09.2026

Nutzerfreigabe: Umsetzung, großzügig, höchstens24h Walltime je sechs Perspektiven,
sofern zusätzliche Suchchancen/Erkenntnisse begründbar sind. Die sechs Perspektiven
werden zu prüfbaren, teilweise gemeinsamen Verfahren verdichtet. Perspektiven sind
keine voneinander unabhängigen Erfolgschancen. Eine numerische Durchbruchswahrscheinlichkeit
ist unbekannt. Der neue Suchraum und kontrollierte Vergleiche begründen den Aufwand.

Basis: Reviewabgleich b9f215a4fb3a7824d71870743c38d1657b963d43;
Rohdaten1.2 SHA256 fbd30cf6bfaf9eb610da8afb0ae64b8a2003c766eb64bce8bf79fc1d8b0c82b6.
GC-01 bis GC-14 sowie docs/EXPERIMENT_RULES.md gelten. Keine Übernahme alter CPU,
Solverresultate oder als erledigt markierter Aufgaben. Ausgangsgraphen sind explizite Inputs.

| Familie | Untersuchung | Zellen | CPU je Zelle | Summe |
|---|---|---:|---:|---:|
| A | AP gegen AP+Stern, gleiche Suchsteuerung |32 Klassen×2|45min|48h|
| B | LP0/LP2×frei/Radius16, gepaarte Seeds/Fenster |48×4×2|1h|384h|
| C1 | Eltern-Differenzmaske D gegen zufällige Kontrollmaske R |24×2|2h|96h|
| C2 | Packing-Tabu gegen AP+Stern-λ-Suche mit Löschprojektion |12×2|4h|96h|
| Gesamt Suche |520 vorab eingefrorene Aufgaben|520|—|624h|

Gesamtgrenze672CPUh:624h Suchziele,24h Aux und24h Reservenspielraum.
Die Summe zulässiger Aufgaben-Nachlaufreserven liegt bei17h20; Reserven sind
keine Zusatzsuche. Höchstens12 Worker mit einem Solverthread. Ideale Projektion
624/12=52h; frühe Optima können verkürzen, Fremdlast/Speichergrenzen und letzte
Welle verlängern. Kein seriös gemessener Ryzen-Durchsatz für K1 liegt vor Start vor.
Harte aktive Windows-Walltime96h; bei Erreichen bleiben offene Aufgaben UNKNOWN.
Keine automatische Verlängerung und keine Umverteilung freigewordener Budgets.
Die Freigabe wird bewusst nicht als Auftrag interpretiert,144h blind zu verbrauchen.

## Herkunft der Vorschläge und konkrete Umsetzung

- Eigener Optimierer: Mobilität/Solverhemmnisse systematisch trennen → B und C1.
- Eigener Hubschrauber: Eltern-Differenzmasken und kontrollierte Kombination → C1;
  Operator-/Populationsvergleich → A in begrenzter iterierter Form.
- Eigener Maverick: Grenzen der λ-Mannigfaltigkeit/anderer Suchraum → C2 und
  Masken, die bisherige induzierte Fenster überschreiten.
- Reviewer-Optimierer: LP aus, kleine feste Bälle, positive Zeugen → B, Controls.
- Reviewer-Hubschrauber: Sternkatalog und Verbindung mit AP → A und λ-Arm von C2.
- Reviewer-Maverick: Packing/extremales Ziel693 → C2.

Nicht umgesetzt: spekulative Projektorsuche, unbewiesene Einzelfehler-Brücken,
SRG-Störung durch unmögliche gültige Sternzüge, sowie bloße Wiederholung historischer
C3-Operatoren unter anderem Namen. Sie würden getrennte mathematische Kontrollen benötigen.

## Eingefrorene Auswahl und Unterschiede zur ersten Skizze

A nutzt32 von33 unabhängig kanonisierten Poolklassen: alle8 neuen Sternendpunkte,
24 aus dem alten25er Pool (lexikografisch schlechteste alte Klasse ausgelassen).
Eine größere Archivpopulation bis1000 ist in diesem Paket nicht enthalten.
Der kontrollierte erste Vergleich konzentriert sich auf die geprüften Ausgangsklassen
und die acht neu nachgewiesenen Sternklassen; Sucharchive werden währenddessen erzeugt.
A ist iterierter Steilstabstieg mit4:3:2-Perturbationslängenmischung; die Steuerung
beider Arme ist gleich. Es ist keine Reproduktion der historischen Populations-P.
Die komplette unmittelbare Nachbarschaft wird enumeriert, solange CPU reicht;
ein unterbrochener Census wird nicht als Lokaloptimum gezählt. Archive maximal128
Graphen pro Aufgabe, beste Graphen sofort atomar gespeichert.

B nutzt genau die48 historischen60er-Fenster, aber vollständig neue Läufe.
Innerhalb der96 gepaarten Zellen bleiben Gründer, Kantenmaske, Seed, Hint,
Zielfunktion und Budget gleich. Ausschließlich LP-Level und Radius ändern sich.
Radius16 bedeutet höchstens16 geänderte ungerichtete Kanten gegenüber dem
ursprünglichen Gründer; kein Rezentrieren. Modellaufbau gehört zum Suchbudget.
Es gibt keine Kalibrierungspräfixe in wissenschaftlichen Aufgaben.

C1: je Herkunftslinie2076/2077 sechs nächste und sechs fernste Elternpaare,
Abstand nach symmetrischer Kantendifferenz, historische gemeinsame Nummerierung.
Keine behauptete optimale Isomorphieausrichtung. Größte D-Maske130 Kanten.
Kontrollmaske R hat gleiche Zahl vorhandener/fehlender variabler Kanten wie D;
R muss nicht denselben zweiten Elternteil zulassen. D erlaubt beide Eltern
hinsichtlich harter Grad-/λ-Bedingungen. Ein Ergebnis gleich einem Elternteil ist
Vererbung, keine neue Kombination; Verbesserungen werden auch gegen den besseren
der beiden Eltern und gegen den gesamten bekannten Pool ausgewertet. Die gemeinsame Zielgrenze kann einen
schlechteren zweiten Elternteil ausschließen; Start-/Hintgraph bleibt Elternteil A.

C2: je Herkunftslinie sechs niedrigste Gründer nach(W,L1).
Packinggrad zusätzlich höchstens14; CN-Kante<=1/CN-Nichtkante<=2.
Direktarm: randomisierte gültige Ergänzungen, Tabu und2/3/5/8/12-Kantenlöschungen.
λ-Arm: vollständiger AP+Stern-Census, bester Abstieg oder einzelner zufälliger Kick,
danach randomisierte Greedy-Löschprojektion. Das ist ein Verfahrensvergleich,
keine isolierte Messung eines einzigen Operators. Projektion kostet dieselbe
Task-CPU. Sie liefert erreichbare Defizite, kein exaktes Löschminimum.
Für99 Knoten erzwingt693 Packingkanten das SRG-Ziel; alle besten Packings
werden zusätzlich unabhängig mit Mengen geprüft. λ-Eltern liegen separat vor.

## Betrieb, Prüfungen und Auswertung

Neuer Ordner ryzen_lambda_k1_100_20260929; unverändertes vorhandenes Python3.12-
Solvervenv. Erst Windows-Stopwatch und Scheduler-Vorabtest, dann Mathematik-
und Kernelkontrollen, erst danach interleavte Familien. Größtes CP-Modell im
Aux-Konto gebaut; Speichergrenze aus dessen Prozesspeak konservativ abgeleitet.
30s CPU-Nachlauf pro Versuch,120s pro Aufgabe;5s Endmessungstoleranz.
Alle wirklichen CPU-Werte zählen. Endabrechnung via wait4, CPU-Überwachung/proc;
Windowszeit für Walltime und Eskalation. Status alle10min mit Zeitstempel,
Familienfortschritt und laufender CPU. Zielhardware-Vorabtest bleibt bei Übergabe offen.

Primär: unabhängig geprüfter λ-Graph mitW<2076 bzw Packing693.
Sekundär: gepaarte Änderungen von(W,L1), Verbesserungserstzeit, Varianten mit
weiteren zulässigen Graphen, neue kanonische Klassen im nachgelagerten Audit,
Packing-Kantenzahl/Defizit, vollständige versus abgebrochene Kataloge.
CPU-bedingtes UNKNOWN ist keine negative Existenzentscheidung; CP-OPTIMAL bleibt
unzertifiziert. Isomorphe Graphen müssen identische Scores besitzen.
Geplante/zertifizierte Aussagen werden getrennt von Solverberichten ausgewiesen.

Nutzerpause erhält Incumbents und Budget, startet aber Zufalls-/Solverzustände neu.
Solche Vergleiche sind bei Auswertung als unterbrochen zu markieren.
Frühe abgeschlossene Aufgaben geben ihr Budget nicht still an andere weiter.
Ein technischer Neustart erhält neue Kennung und bleibt vom Fehllauf getrennt.

Quellen: experiments/memetik/lambda_k1_1_0_0; README und MANIFEST sind Teil der
Paketprüfung. Testumfang und Grenzen stehen in VALIDATION.json. Keine Änderung
an der unabhängigen Office-C2-Kampagne.
