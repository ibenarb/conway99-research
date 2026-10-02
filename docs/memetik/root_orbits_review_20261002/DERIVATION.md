# ROOT-8105: mathematische Herleitung und reproduzierbarer Prüfstand

## 1. Erzwungene Normalform

Sei G ein hypothetischer srg(99,14,1,2) und x ein beliebiger Knoten.

Für y in N(x) ist die Zahl der Nachbarn von y innerhalb N(x) gleich der Zahl gemeinsamer Nachbarn von x und y, also lambda=1. Daher induziert N(x) einen 1-regulären Graphen auf 14 Knoten: 7K2.

Es bleiben 99-1-14=84 Knoten außerhalb N[x]. Für jeden solchen Knoten z sind die gemeinsamen Nachbarn von x und z genau seine Nachbarn in N(x), also genau mu=2.

Sind a,b ein Kantenpaar des lokalen 7K2, dann haben a,b wegen lambda=1 genau einen gemeinsamen Nachbarn; x ist bereits dieser gemeinsame Nachbar. Also existiert kein Außenknoten, der gleichzeitig an a und b hängt.

Sind a,b dagegen zwei nichtadjazente lokale Knoten, dann haben sie wegen mu=2 genau zwei gemeinsame Nachbarn. Einer davon ist x. Der zweite kann nicht in N(x) liegen, denn jeder lokale Knoten hat dort nur seinen 7K2-Partner. Also existiert genau ein Außenknoten, der an a und b hängt.

Damit sind die 84 Außenknoten kanonisch bijektiv mit den
C(14,2)-7 = 84
nicht-gepaarten Zweiermengen der lokalen 14 Knoten bezeichnet.

## 2. Randgruppe und Fixierung des ersten H-Knotens

Die gerootete Randstruktur besteht aus x plus sieben ungeordneten Kantenpaaren. Ihre Relabeling-Gruppe auf den 14 lokalen Knoten ist die Wreath-Produktgruppe

C2 wr S7,

also unabhängiges Vertauschen der Endpunkte jedes der sieben Paare und Permutieren der sieben Paare. Ihre Ordnung ist

2^7 * 7! = 645120.

Diese Gruppe wirkt transitiv auf den 84 nicht-gepaarten Zweiermengen. Deshalb kann ein gewählter erster Außen-/H-Knoten per Relabeling auf u={0,1} gelegt werden. Der Stabilisator hat nach Orbit-Stabilizer

645120 / 84 = 7680

Elemente.

## 3. Exakte Bedingung für die erste H-Zeile

Jeder Außenknoten hat zwei Nachbarn im lokalen Rand und Gesamtgrad 14, also H-Grad 12.

Für u={0,1} seien die lokalen 7K2-Partner 7 und 8. Für die zwölf H-Nachbarn von u gilt folgende Inzidenzforderung auf den 14 Randknoten:

- Grad 1 an 0 und 1, weil u mit diesen Randknoten adjazent ist und lambda=1 gilt;
- Grad 1 an 7 und 8, weil dort bereits je ein gemeinsamer Randnachbar vorhanden ist;
- Grad 2 an den übrigen zehn Randknoten, weil u dort nichtadjazent ist und kein gemeinsamer Randnachbar vorhanden ist.

Die Zielgradfolge ist also viermal 1 und zehnmal 2, Gesamtsumme 24 = 2*12.

Die auswählbaren H-Nachbarn sind die 83 übrigen nicht-gepaarten Zweiermengen; u selbst ist wegen H_uu=0 ausgeschlossen.

Der Standalone-Checker bestimmt den entsprechenden Koeffizienten von

prod_(e in E_allowed_without_u) (1 + prod_(v in e) x_v)

bei der Zielgradfolge und erhält exakt

56,011,010.

Wenn u fälschlich als eigener H-Nachbar zugelassen wird, erhält man 58,311,050. Diese Zahl ist deshalb **nicht** die korrekte Startzahl.

## 4. Burnside

Der Stabilisator von u ist isomorph zu

S2 x (C2 wr S5)

und hat 7680 Elemente. Seine Konjugationsklassen lassen sich durch

- Fixieren/Vertauschen der beiden von u berührten 7K2-Paare und
- positive/negative signed cycle types auf den übrigen fünf Paaren

klassifizieren. Es entstehen 72 Klassen.

Für jedes Stabilisatorelement zerfällt die Menge der 83 möglichen H-Nachbarlabels in Kantenorbits. Eine unter diesem Element fixe erste Zeile muss eine Vereinigung ganzer solcher Orbits sein. Der Checker zählt per Grad-DP die fixen gültigen Zeilen für einen Repräsentanten jeder Klasse und multipliziert mit der Klassenmultiplizität.

Die Summe aller Fixpunktzahlen über den gesamten Stabilisator ist

62,246,400.

Burnside liefert daher

62,246,400 / 7680 = 8105

Orbits zulässiger erster H-Zeilen.

## 5. Bedeutung und Grenze

Die Zahl 8105 ist nur dann relevant für einen Existenz-/Nichtexistenzbeweis, wenn die obige Normalform, Gruppenwirkung und Coverage korrekt sind.

Sind sie korrekt, dann enthält jeder hypothetische srg(99,14,1,2) nach Wahl eines beliebigen Roots x und Relabeling eines beliebigen ersten Außenknotens eine erste H-Zeile aus genau einem dieser 8105 Orbits.

Daraus folgt: Wenn für **jeden** dieser 8105 Rootorbits sound und vollständig bewiesen wird, dass keine komplette 84x84-H-Belegung existiert, dann existiert kein srg(99,14,1,2).

Ein Timeout, eine begrenzte Enumeration oder ein heuristischer DFS-Nichtfund reicht dafür ausdrücklich nicht.

## 6. Dateien

- verify_root_orbits.py: eigenständiger Rechenchecker ohne Import aus dem Produktionssolver.
- verify_root_orbits_output.json: vollständige Ausgabe einschließlich aller 72 Stabilisator-Konjugationsklassen.
- REVIEWER_PROMPT.md: kritischer Prüfauftrag.

Produktionsdefinition der 84 Außenlabels und Randmargen:
experiments/memetik/row_constructive_0_2_0/row_build.py

Aktueller WALK-Plan:
docs/memetik/row_constructive_walk_20261002/PLAN.md

Globale Experimentregeln:
docs/EXPERIMENT_RULES.md
docs/operations/GLOBAL_CONCLUSIONS.md
