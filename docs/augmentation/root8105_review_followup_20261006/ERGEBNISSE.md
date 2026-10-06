# Ausgeführte Folgeprüfungen

## Tiefe 2

Run `953a7068044b432b89c6d885278ed950`, Code-SHA256
`d5588024b4a6617c218ea98b435e08ef2f41b3fa7f41777c44d1d9ce0550782f`.

3072 Zustände,12288 Entscheidungen: **keine Abweichung** von den vorher gespeicherten
Vorhersagen (je Ziel vor dessen Filteraufrufen gespeichert; Vorhersageformel vor
dem gesamten Lauf fixiert). Die Tabelle ist zusätzlich mathematisch begründet; ein endlicher
Falsifikationstest allein wäre kein allgemeiner Beweis.

| Relation | Zustände | LD verworfen | CAP verworfen | Kombination verworfen |
|---|---:|---:|---:|---:|
| (0,1) |1536|0|133|133|
| (1,0) |1536|158|158|158|

Die Stichprobenzahlen dienen der Implementierungskontrolle. Maßgeblich für Quoten
sind die exakten Breiten:

| Relation | Summe F-Breiten der24 Ziele | Exakt verworfen | Bereich je Ziel |
|---|---:|---:|---:|
| (0,1) |366101533|29416666|3,1509–9,8396%|
| (1,0) |75725196|7811518|0–14,6136%|

Alle48 Partitionen erfüllen exakt: Breite der durch Verbote erzeugten guten Zeilen
plus Summe der auf einen schlechten gemeinsamen Nachbarn konditionierten Breiten
= historische F-Breite. Weil der gemeinsame Nachbar eindeutig ist, sind die
schlechten Teilmengen disjunkt. Bei einem (1,0)-Ziel ist die Verwerfungsbreite null.
Es wird keine globale Durchschnittsquote über alle672715 Ziele behauptet.

91 unabhängig kodierte SAT-Kontrollen der nach eingefrorener Regel ausgewählten
Verwerfungen ergaben `UNSAT_UNCERTIFIED`. Sie sind zusätzliche Kontrollen, keine
formalen UNSAT-Zertifikate. Positive BVLS-Kontrollen, erzwungene Kantenwerte gegen
den vollständigen Zeugen und exakte kleine Samplervergleiche bestanden ebenfalls.

CPU allein für Filter im neuen Lauf: (1,0) LD0,099318s, CAP10,264603s; CAP ist in
dieser Implementierung etwa103mal teurer bei denselben Entscheidungen. Eine
maschinenunabhängige Kostenrelation wird nicht behauptet.

## Matchingobjekte

Auf den24 ausgewählten Roots:7884 zulässige Matchings vor Symmetriereduktion,
5182 Stabilisatororbits. Je Root292–372 rohe Matchings und28–371 Orbits.
Jede Orbitzerlegung ist unter den ermittelten Gruppengeneratoren geschlossen;
Summe der Orbitgrößen = rohe Matchingzahl. Kein unmittelbarer Rootausschluss.
Die vollständigen Repräsentanten und Orbitgrößen stehen in SUMMARY.json.

## Betrieb und Grenzen

Neue mathematische, Budgetdialog-, Uhren-, Workerfehler- und Recoverykontrollen
bestanden. Das sind Linux-Cloud-Belege; WSL/Windows bleibt separat zu prüfen.
Der Tiefe-2-Lauf einschließlich Vorabprüfungen verbuchte192,891002CPU-s im Endexport (192,476704CPU-s vor Export);
kein offener Versuch, keine als null behandelte Verbrauchslücke.
Zusätzliche Entwicklungsproben außerhalb des Controllers sind nicht in diesem
Laufkonto enthalten; ihre CPU ist nicht vollständig endabgerechnet und wird nicht
als null angesetzt. Die vollständige Abrechnungsaussage gilt für die bezeichneten
Kampagnen, nicht für den gesamten Entwicklungsaufwand. Verfügbare Kontrollausgaben
sind als Entwicklungsbelege separat archiviert.
Es gibt keine aus diesem Paket abgeleitete Gesamtlaufzeitprognose.

Die Ergebnisse der Suchpfadkalibrierung stehen separat in TREE_CALIBRATION.json.
Ihre96 Abstiege sind kein Ersatz für die geplanten40000 Abstiege der Hauptmessung.

## Kalibrierung:96 abgeschlossene Abstiege

| Reihenfolge | Propagation | log10 beobachteter mittlerer kumulierter Knoten | ESS | Tiefe13 erreicht |
|---|---|---:|---:|---:|
| numerisch | nein |36,6876|5,67|0/24|
| numerisch | ja |35,4481|7,34|1/24|
| Nachbarschaft zuerst | nein |30,5858|3,23|0/24|
| Nachbarschaft zuerst | ja |29,4224|3,03|0/24|

Dies sind **instabile explorative Punktschätzungen**, keine Größenordnungsgewinne
mit abgesicherter Unsicherheit. Im neuen Reihenfolgearm stammt ungefähr die Hälfte
des Gesamtgewichts von einem einzigen Abstieg. Alle vier Auswertungen melden daher
INSUFFICIENT_INFORMATION; kein Bootstrapintervall und keine Standardumstellung.
Die Daten motivieren die größere, nach Roots geschichtete Messung, nicht eine
vollständige Suchkampagne. Ein nicht erreichter Endknoten ist kein Rootausschluss.

Ergebnisexport aus96 validierten Endresultaten reproduziert. Beim persistierten
Kalibrierungsledger besteht eine Abschlussabweichung; deshalb kein freigegebener
Wiederaufnahmestand. Berichteter Verbrauch293,124005CPU-s, ohne Behauptung eines
unabhängig konsistenten relationalen Endledgers. Details und Betriebskorrektur1.0.1:
ABSCHLUSS_ABWEICHUNG.md. Die40k-Hauptmessung ist vorbereitet, **nicht ausgeführt**.

Betriebsversion1.0.1: neue mathematische und Betriebs-Vorabprüfung einschließlich
Abschlussbeleg-Regression bestanden (129,146271CPU-s). Code-SHA256
`15fde20b5a11afa4de4bcd942eb5ef50cee2dfc2355449f3e3d987a9e585821a`.
Dabei wurden keine neuen produktiven3072er oder96er Rechnungen gestartet.
