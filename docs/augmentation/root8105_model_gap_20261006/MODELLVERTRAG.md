# Modellvertrag, 06.10.2026

o: Basispunkt; B=N(o):14 Randknoten mit antipodalem Matching c--c';
H:84 Zweierlabels l(v) ohne antipodale Paare. H-Grad12.
P: vollständige feste H-Zeilen; a=0: Rootzeile. X_uv=X_vu binär, X_uu=0.
Alle Modelle tragen ausdrücklich feste Kantenannahmen E. M fixiert sämtliche
Kanten innerhalb N_H(a): Matching auf den zehn nicht randgepaarten Nachbarn,
übrige Kanten dort null. A: hergeleitete Kantenwerte, keine beliebigen SAT-Werte.

## Grundgleichungen

Randmarge für erforderliches t,c:
    sum_{v: c in l(v)} X_tv = 1 für c in l(t) vereinigt l(t)', sonst 2.
Summation über c impliziert H-Grad12. Paarbedingung für erforderliches u,v:
    sum_w X_uw X_vw + X_uv = 2 - |l(u) geschnitten l(v)|.
Für u in P wird die Summe linear: sum_{w in N_H(u)} X_vw.

## Definitionen

| Modell | Gemeinsam gelöste Bedingungen |
| --- | --- |
| R(t;P,E) | Eine offene Zeile: Diagonale, Symmetrie zu P,14 Randmargen, Paargleichungen zu jedem u in P und auf t wirkende E. |
| R+LD | R plus die auf t wirkenden Nullen beider in check_gap.py hergeleiteten LD-Regeln. Keine übrige Propagation. |
| Loc(t;P,M,A) | Historischer RowProposal: R, seine Null-Sternregeln und auf t wirkende M/A. Weitere LD-Nullen können über A einfließen. |
| F0(t;P) | encode(P,t): Zielmargen, Paargleichungen t--P und λ-Sterne jedes gebauten H-Knotens; geteilte symmetrische Kanten. Keine zusätzlichen M/A. |
| FM | F0 mit M. |
| FM,A | FM mit A; der historische Mitgliedschaftstest fixiert außerdem die gesamte vorgeschlagene Zielzeile. |
| S(P,E) | Gemeinsame λ-Sterne aller vollständigen99er-Knoten: o, B und P. Separate Kapazitätsvorprüfungen des Audits sind keine zusätzlich gemeinsam gelösten Gleichungen. |
| G(P,E) | Alle offenen H-Randmargen und alle Paargleichungen mit mindestens einem Endpunkt in P, gemeinsame symmetrische Variablen. encode(P,None) plus E. |
| N1(a,M;E) | Alle H-Randmargen und alle H-Paargleichungen mit mindestens einem Endpunkt in U={a} vereinigt N_H(a). Anfangs nur a und M fest; Nachbarzeilen variabel. Feste zusätzliche Präfixzeilen für Kontrollen in E. |

F kann eine Erfüllbarkeitsaussage oder ihre Zielzeilenprojektion bezeichnen:
immer kenntlich machen. Ablehnung eines Kandidaten beweist keine leere Projektion.
Bei historischen Annahmen werden nur vorkommende Variablen festgesetzt;
Konsistenz mit festen Zeilen muss separat geprüft werden.

## Implikationen unter identischen festen Annahmen

SRG-Ergänzung => N1 und G. G => S, jedes R(t) und jede entsprechende F0-Prüfung.
FM,A => FM => F0 => R für die jeweilige Zielzeile. A ohne Verlust echter
Ergänzungen nur bei notwendiger Herleitung unter denselben Annahmen verwenden.
Für vollständig festes P=U entspricht N1 dem G(P,E). Für P={a} enthält N1
zusätzliche Bedingungen mit variablen Nachbarzeilen: keine Gleichsetzung.

G enthält nicht automatisch die LD-Regel zwischen zwei offenen Nachbarn mit
gemeinsamem Randlabel: deren gegenseitige Paargleichung kann fehlen.
Daher G=>R+LD nicht ungeprüft behaupten. Einzelzeilentests ersetzen keine
gemeinsame Lösung G. Eine Unvergleichbarkeit bestimmter Varianten wird hier
ohne Gegenbeispiele nicht behauptet.

## Produkte und Zertifizierung von N1

Für z=X_uw AND X_vw mit zwei freien Faktoren drei Äquivalenzklauseln:
(-z OR X_uw), (-z OR X_vw), (z OR -X_uw OR -X_vw).
Konstanten vorher exakt vereinfachen; Kantenvariablen symmetrisch teilen.
Die Paarform mit +X_uv vermeidet einen bedingten rechten Wert.
SAT direkt an ursprünglichen Ganzzahlgleichungen und M prüfen.
Beide Endpunkte außerhalb U: Paarbedingung bleibt offen. SAT ist kein SRG.
UNSAT benötigt externe DRAT-/LRAT-Prüfung. Rootausschluss erfordert zusätzlich
vollständige Matchingklassenabdeckung und korrekte Symmetrieabbildungen.
