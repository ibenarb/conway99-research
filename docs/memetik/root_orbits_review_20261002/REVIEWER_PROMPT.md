# Reviewerauftrag: ROOT-8105 kritisch prüfen

## Aufgabe

Bitte prüfe die folgende mögliche Reduktion des Conway-99-Problems unabhängig und kritisch. Ziel ist **nicht**, die vorgelegte Argumentation zu bestätigen, sondern Fehler, versteckte WLOG-Annahmen, unzulässige Symmetriequotienten oder Zählfehler zu finden.

Die zentrale Behauptung lautet:

> Für einen hypothetischen srg(99,14,1,2) kann nach Fixierung der erzwungenen 1+14+84-Normalform und eines ersten H-Knotens die Menge aller zulässigen ersten H-Zeilen in genau 8105 Orbits unter dem Stabilisator dieses H-Knotens zerlegt werden.

Bitte reproduziere die Rechnung möglichst unabhängig vom beigelegten Python-Code.

## Zu prüfende Argumentationskette

1. Wähle in einem hypothetischen srg(99,14,1,2) einen Knoten x.
2. N(x) hat 14 Knoten und induziert wegen lambda=1 einen 1-regulären Graphen, also 7K2.
3. Jeder der übrigen 84 Knoten hat wegen mu=2 genau zwei Nachbarn in N(x).
4. Ein gepaartes lokales Kantenpaar kann keinen solchen Außenknoten gemeinsam sehen, weil x bereits der eine gemeinsame Nachbar des adjazenten Paars ist.
5. Jedes nichtadjazente Paar in N(x) hat wegen mu=2 neben x genau einen weiteren gemeinsamen Nachbarn. Dieser liegt außerhalb N[x].
6. Damit sind die 84 Außenknoten bijektiv mit den 84 nicht-gepaarten Zweiermengen der 14 lokalen Knoten bezeichnet.
7. Die volle Relabeling-Gruppe der gerooteten Randstruktur ist C2 wr S7 mit Ordnung 2^7*7! = 645120 und wirkt transitiv auf diesen 84 Außenlabels.
8. Daher darf ein erster H-Knoten u auf ein festes Label, hier {0,1}, gelegt werden. Sein Stabilisator hat Ordnung 645120/84 = 7680.
9. Die zwölf H-Nachbarn von u müssen als zwölf der übrigen 83 Außenlabels gewählt werden. Ihre Inzidenzgrade auf den 14 Randknoten müssen
   - 1 an den beiden Endpunkten von u und deren beiden 7K2-Partnern,
   - 2 an den übrigen zehn Randknoten
   betragen.
10. Der Koeffizientenzähler für diese Bedingung ergibt 56,011,010 zulässige erste H-Zeilen. Die frühere Zahl 58,311,050 entsteht, wenn man fälschlich das Diagonalelement H_uu als mögliche Auswahl zulässt.
11. Burnside über den 7680er Stabilisator ergibt eine Fixpunktsumme 62,246,400 und damit 62,246,400 / 7680 = 8105 Orbits.

## Konkrete Prüfaufträge

Bitte beantworte mindestens folgende Fragen:

1. Ist die 1+14+84-Normalform wirklich für **jeden** srg(99,14,1,2) zwingend, auch ohne Vertextransitivität oder sonstige Symmetrieannahmen?
2. Ist die Bijektion zwischen den 84 Außenknoten und den 84 nicht-gepaarten Zweiermengen vollständig bewiesen?
3. Ist C2 wr S7 genau die zulässige Relabeling-Gruppe der gerooteten Randstruktur? Ist ihre Wirkung auf den 84 Außenlabels transitiv?
4. Ist das Fixieren eines ersten H-Knotens auf {0,1} eine reine Relabeling-WLOG und keine zusätzliche Graphsymmetrieannahme?
5. Ist der Stabilisator wirklich von Ordnung 7680 und wirkt er vollständig auf der Menge der zulässigen ersten H-Zeilen?
6. Reproduziere unabhängig die Zahl 56,011,010.
7. Reproduziere unabhängig die Zahl 8105, vorzugsweise mit einer zweiten Methode oder zumindest einer unabhängig formulierten Burnside-/Canonicalisierungskontrolle.
8. Prüfe den beigelegten Standalone-Checker auf Implementierungsfehler. Insbesondere: Diagonalverbot, Matchingdefinition, Stabilisatorerzeugung, Konjugationsklassen, Fixpunktzählung und Burnside-Summe.
9. Gibt es eine **weitere** zwingende Reduktion der 8105 Rootfälle, die bereits aus der SRG-Struktur folgt, ohne mögliche Lösungen auszuschließen? Bitte trenne echte Symmetriequotienten von bloßen Necessary-Condition-Filtern.
10. Bestätige oder widerlege die Folgerung:
   Wenn alle 8105 Rootorbit-Repräsentanten vollständig und sound auf Fortsetzungen untersucht werden und für keinen eine vollständige 84-Zeilen-H-Matrix existiert, dann existiert kein srg(99,14,1,2).
11. Wäre ein zertifizierter Nachweis einer universellen Maximalhöhe n<84 äquivalent ausreichend? Welche Coverage- und Zertifikatsbedingungen müssten dafür erfüllt sein?
12. Welche Architektur würdest Du für einen solchen Exhaustionsbeweis empfehlen: kanonische Augmentation, SAT/cube-and-conquer, Orbit-Coverage, PSD-/Spektralfilter, lokale 7K2-Closure oder etwas anderes?

## Erwartete Rückgabe

Bitte liefere:

- **Reproduzierte Zahlen** mit eigener Methode.
- **Verdict je Behauptung**: bestätigt / falsch / noch nicht ausreichend belegt.
- **Fundstellen eines möglichen Fehlers** möglichst konkret.
- Eine klare Aussage, ob Du selbst ebenfalls auf **8105** kommst.
- Eine klare Aussage, ob eine zertifizierte globale Schranke n<84 die Nichtexistenz von srg(99,14,1,2) beweisen würde.
- Einen Vorschlag für den kleinsten nächsten Rechenschritt, der den Übergang von Heuristik zu einem auditierbaren Exhaustionsbeweis testet.

Bitte behandle Timeouts, Sampling und begrenzte Enumeration niemals als Exhaustion.
