# ROOT-8105 — Abgleich mit unabhängigem Review

Stand: 2026-10-02.

## Gemeinsamer Nenner

Die Rootreduktion ist bestätigt.

Für jeden hypothetischen `srg(99,14,1,2)` und jeden gewählten Knoten `x` gilt:

1. `N(x)` induziert zwingend `7K2`.
2. Die 84 Knoten außerhalb `N[x]` sind bijektiv mit den 84 nicht-gepaarten Zweiermengen von `N(x)` bezeichnet.
3. Nach Relabeling darf ein Außenknoten `u` auf das Standardlabel `{0,1}` gelegt werden. Dies ist reine WLOG-Relabeling-Symmetrie, keine Annahme einer Automorphie des unbekannten SRG.
4. Die gerootete Randgruppe hat Ordnung `2^7*7! = 645120`; der Stabilisator von `u` hat Ordnung `7680`.
5. Mit `H_uu=0` gibt es exakt `56,011,010` zulässige erste H-Zeilen.
6. Diese zerfallen unter dem Stabilisator exakt in `8105` Orbits.

Die frühere Zahl `58,311,050` ist die Variante, in der das verbotene Diagonalelement `H_uu` mitgezählt wird.

## Unabhängige Reproduktionen

Der externe Review reproduzierte die Rootzahlen durch mehrere voneinander verschiedene Verfahren:

- unabhängige Vertex-DP für `56,011,010`;
- Burnside über alle 7680 Stabilisatorelemente einzeln: Fixpunktsumme `62,246,400`, also `8105` Orbits;
- vollständige Enumeration aller 56,011,010 Zeilen mit Lex-Min-Kanonisierung: ebenfalls `8105`;
- nauty-Gegenprobe: 8105 paarweise nicht-isomorphe Level-1-Repräsentanten und passende Automorphismenordnungen;
- Orbit-Coverage über die Repräsentantenliste: Summe der Orbitgrößen = `56,011,010`.

Zusätzlich wurde die 8105er Repräsentantenliste gegen die Produktionskonvention
von `row_build.py` gekreuzt: alle 8105 PASS, einschließlich Diagonalverbot und Randmargen.

## Präzisierung: lokale 7K2-Closure

Die lokale Struktur um den ersten Außenknoten `u` ist eine weitere exakte notwendige Bedingung:
`N(u)` muss ebenfalls `7K2` induzieren.

Sie reduziert aber **keinen** der 8105 Rootorbits sofort.

Für jeden Rootorbit existieren 292 bis 372 kompatible lokale Matchings.
Über die 8105 Repräsentanten entstehen 2,944,568 Level-2-Objekte vor Quotientierung
durch den jeweiligen Rootstabilisator.

Orbitzahlen auf Level 2:

- `2,677,638` mit ausgezeichneten Rollen `x,u`;
- `1,345,721` wenn zusätzlich die legitime Rollentausch-Symmetrie `x <-> u` zugelassen wird.

Diese Level-2-Zahl ist **keine Alternative zu 8105**. Sie beschreibt eine stärker
ausgearbeitete Fallstufe nach Wahl des lokalen Matchings. Die x-u-Symmetrie wird
erst auf dieser vollständig bestimmten Zwei-Stern-Struktur wohldefiniert.

## Präzisierung: PSD / Spektrum

Der Review testete auf allen 2,944,568 Level-2-Objekten die beiden üblichen
SRG-PSD-Matrizen

`44 I + 11 A - 2 J` und `27 I - 9 A + J`

auf dem vollständig bestimmten 28-Knoten-Teilgraphen. Es wurden numerisch keine
PSD-Verstöße gefunden. Damit ist der rohe PSD-Test auf Level 2 als Filter praktisch wirkungslos.

Dies widerspricht nicht der stärkeren, herausprojizierten Rangbedingung:

- `44 I + 11 A - 2 J` hat Gesamtrang 54;
- `27 I - 9 A + J` hat Gesamtrang 44;
- auf dem festen 15-Knoten-Rand `{x} ∪ N(x)` haben beide Blöcke Rang 14;
- nach orthogonaler Projektion auf das Komplement des Randspans bleiben für die 84 H-Knoten
  Residualränge 40 bzw. 30.

Die Rang-30-Bedingung kann daher erst ab 31 H-Knoten nichttrivial werden.
Sie wurde im Review nicht getestet und bleibt ein separater, mathematisch sounder
Kandidat für tiefere Necessary-Condition-Pruningtests. Ihre praktische Stärke ist offen.

## Globale Folgerung

Die 8105 Rootorbits sind eine vollständige Wurzelabdeckung, aber noch kein
Nichtexistenzbeweis.

Wenn für **jeden** der 8105 Repräsentanten mit einer vollständigen und sounden
Fortsetzungssuche bewiesen wird, dass keine vollständige 84x84-H-Belegung existiert,
dann existiert kein `srg(99,14,1,2)`.

Äquivalent genügt ein zertifizierter universeller Nachweis, dass die maximale
erreichbare Zahl konsistent aufgebauter H-Zeilen strikt kleiner als 84 ist,
sofern die verwendete Augmentationsregel vollständig ist: jeder hypothetische
vollständige Graph muss mindestens einen Suchpfad besitzen.

Nicht ausreichend sind:

- eine beobachtete Tiefenbarriere unter einer festen Zeilenreihenfolge, wenn die früheren Zeilenbelegungen nicht vollständig ausgeschöpft wurden;
- eine Barriere nur für gespeicherte oder gesampelte Basen;
- begrenzte Enumeration;
- Timeout;
- heuristisches Pruning ohne Necessity-Beweis.

## Konsequenz für die nächste Beweisarchitektur

Die Rootstufe ist klein und auditierbar: 8105 Fälle.

Die naive explizite Level-2-Expansion ist dagegen bereits groß. Zudem besitzen
6722/8105 Rootorbits trivialen Stabilisator; reine Reststabilisator-Symmetrie
wird nach Level 1 bei den meisten Fällen wenig sparen.

Daher sollte ein Exhaustionspilot vorzugsweise:

1. die 8105 Rootrepräsentanten plus Coverage-Zertifikat als feste Eingangsschicht verwenden;
2. die lokale 7K2-Bedingung symbolisch propagieren, statt zwangsläufig 1.35 Mio. Level-2-Cubes vorab auszuschreiben;
3. kanonische Augmentation bzw. partielle Graphkanonisierung nutzen, insbesondere die x-u-Rollentauschsymmetrie sobald Level 2 vollständig bestimmt ist;
4. Necessary-Condition-Filter nur mit unabhängigen Regressionen einsetzen;
5. UNSAT, Timeout und begrenzte Suche strikt trennen;
6. für einen endgültigen Ausschluss SAT/Proof-Logging und einen separaten Coverage-Audit vorsehen.

## Abgrenzung des Reviews

Der externe Review prüfte das ROOT-8105-Paket und seine eigenen unabhängigen
Programme, nicht den gesamten Produktionssolver. Der Root-Konventionsabgleich
gegen `row_build.py` wurde anschließend separat durchgeführt und bestand für
alle 8105 Repräsentanten. Dies ist kein Audit der übrigen WALK-/DFS-Implementierung.

## Präzisierung vom 03.10.2026

Eine **vollständig** ausgeschöpfte und zertifizierte Suche in einer beliebigen
festen Reihenfolge aller 84 Zeilen genügt zum Ausschluss vollständiger Graphen.
Jeder hypothetische vollständige Graph besitzt auch in dieser Reihenfolge einen
Pfad. Reihenfolgeabhängig sind dagegen erreichbare partielle Tiefen bei
beschränkter Auswahl. Siehe [mathematischen Aussageumfang des Piloten](../root8105_pilot_20261003/MATHEMATICAL_SCOPE.md).
