# Grok v01: Befunde, Analyse und Schlussfolgerung

Eingang 2026-09-15. Modellkennung Grok-4 laut Antwort; Modus „schnell“ laut Nutzer. Beides als Herkunft dokumentiert, nicht extern verifiziert. Originaldatei unverändert einschließlich CRLF-Zeilenenden in `original.md`.

## Entscheidung

**Keine Aufnahme.** Null Graphdaten eingereicht, null zulässige Kandidaten erzeugt oder unabhängig abgenommen. Die Abgabe wird als `INCOMPLETE_NO_CANDIDATES` archiviert. Die klare Angabe von null Kandidaten ist korrekt; die behauptete Vollständigkeit der Generatoren und des Prüfers ist falsch. Die 14 bereits aufgenommenen KI-Graphen bleiben der aktuelle Bestand.

## Befunde aus dem empfangenen Code

- F01 und F02 sind als Python-Blöcke vorhanden. F03–F06 werden ausdrücklich „aus Platzgründen“ ausgelassen. Es handelt sich diesmal um im Text angekündigte Auslassungen, nicht lediglich um einen vermuteten Kopierverlust.
- F02 enthält auch im Erfolgszweig keine graph6-Ausgabe, sondern einen Kommentarplatzhalter. `helpers.to_graph6` besteht aus `pass`.
- F01, Seed 42, ein vollständiger Greedy-Versuch: Exit 1, `FAILED`. Das ist kein Unmöglichkeitsbeweis für Dreieckskonstruktionen.
- F02, Seed 1, ein Versuch: sofortiger TypeError bei `nx.is_regular(G, DEG)`. NetworkX 3.6.1 erlaubt dort keinen zweiten Positionsparameter. Derselbe falsche Aufruf steht im Erfolgszweig von F01 und im Prüfer.
- `check_hard` des Prüfers scheitert schon an `nx.is_simple_path(G)`, weil das erforderliche Argument `nodes` fehlt. Die spätere Überschreibung des Ergebnisses wird nicht erreicht.
- Die Ω-Prüfung ist ausdrücklich ein Platzhalter (`None`). Zusätzlich liefert die NumPy-basierte Prüfung von Einfachheit ein NumPy-Bool, das der spätere Identitätstest `is True` nicht als Python-True anerkennen würde. Die Residuenhistogramme werden vom Hauptprüfer nicht mit den gemeldeten Histogrammen verglichen.
- Der Prüfer läuft über die leere Kandidatenliste mit Exit 0 und ohne Ausgabe. Das ist keine erfolgreich absolvierte Kandidatenprüfung.
- Positiv: Der graph6-Encoder in F01 stimmt auf unserem 99-Knoten-Prüfgraphen mit NetworkX überein. Beide Metrikfunktionen stimmen dort vollständig mit einer unabhängigen Berechnung über Nachbarmengen überein. Der Prüfgraph ist ein Fehlergegenbeispiel, kein zulässiger Gründer.

Die kleinen tatsächlich ausgeführten Prüfungen, Versionen, Parameter und Fehlermeldungen stehen in `audit.json`; Wiederholung: `python audit.py` aus diesem Verzeichnis mit NetworkX und NumPy. Keine vollständigen Monte-Carlo-Budgets und keine langen Solverläufe gestartet.

## Mathematische Analyse

### F01: Linearität des Hypergraphen reicht nicht

Eine Zerlegung ausgewählter Kanten in Dreiecke verhindert nicht zusätzliche Dreiecke aus Kanten verschiedener Blöcke. Das konkrete Gegenbeispiel besteht aus den Blöcken {0,1,2}, {0,3,4}, {1,3,5}. Jedes Knotenpaar liegt in höchstens einem Block, aber im Kantengraphen entsteht zusätzlich das Dreieck {0,1,3}. Die Kante {0,1} hat die gemeinsamen Nachbarn 2 und 3. Die behauptete Äquivalenz muss um das Verbot solcher zusätzlichen Dreiecke (Berge-Dreiecke im linearen Hypergraphen) ergänzt werden.

F01 kontrolliert beim Einfügen nur Grad und bisher unbenutzte Kanten; es verhindert diesen Defekt nicht. Die abschließende λ-Prüfung würde ihn erkennen, erzeugt aber keine Reparatur. Der Ansatz an sich ist sinnvoll, die Zulässigkeitsbehauptung und die Umsetzung sind unzureichend.

### F02: Der gesamte vorgeschlagene λ-Suchraum ist leer

Für einen ungerichteten Cayley-Graphen auf Z99 ist die Abbildung x ↦ d−x eine Automorphie, die die Endpunkte der Kante {0,d} vertauscht. Gäbe es genau einen gemeinsamen Nachbarn, müsste dieser ein Fixpunkt sein, also x=d/2 (2 ist modulo 99 invertierbar). Die Kante {0,d/2} hat dann d als gemeinsamen Nachbarn. Dessen Eindeutigkeit unter der entsprechenden Spiegelung verlangt 2d=d/2, somit 3d=0 modulo 99.

Folglich dürfen sämtliche Verbindungselemente nur 33 oder 66 sein. Der Grad ist höchstens 2, nicht 14. Bereits λ=1 ist hier unmöglich; die Beschränkung auf „λ-Näherung“ statt exakte SRG rettet den Ansatz nicht, da unsere Aufnahme λ=1 exakt verlangt. Dies stimmt mit dem früheren Projektausschluss überein und braucht keine Monte-Carlo-Suche. Die beiden möglichen nichtnull Elemente wurden zusätzlich direkt berechnet.

### F04: Eine gewöhnliche Überlagerung erhält den Grad

Ein 11-facher Lift eines 4-regulären Graphen auf neun Knoten hat 99 Knoten und bleibt 4-regulär. Er wird nicht 14-regulär. Zusätzliche Kanten müssten eigens definiert und auf λ geprüft werden; dann läge mehr als die angegebene gewöhnliche Überlagerung vor. Auch das Schließen der Dreieckslifts wäre gesondert zu erzwingen.

### F03, F05, F06: Beschreibungen ohne implementierte Verfahren

F03 benennt lokale λ-Reparatur, liefert aber keinen Reparaturcode. F05 beschreibt das bereits bekannte lineare Ω-CSP, das Gemini tatsächlich umgesetzt hat. Die Fixierung kanonischer Labels erzwingt keine globale Partnerautomorphie. F06 beschreibt eine Residuenreparatur, spricht aber von Swaps, die das Residuum erhalten: Ein erhaltenes nichtnull Residuum kann so nicht zu null werden. Gemeint sein könnten gradbewahrende, residuenverringernde Swaps; sie sind nicht implementiert.

Die Auswahl von Ω-Kandidaten nach „kleinem Rahmen-Residuum“ ist außerdem kein Auswahlkriterium innerhalb des zugelassenen Ω-Arms: Dort muss dieses Residuum exakt null sein.

Der weitere Vorschlag nichtabelscher Gruppen der Ordnung 99 eröffnet keinen zusätzlichen Fall: Nach Sylow sind sowohl die 11-Sylowgruppe (Anzahl teilt 9 und ist 1 modulo 11) als auch die 3-Sylowgruppe (Anzahl teilt 11 und ist 1 modulo 3) normal und eindeutig. Ihre Ordnungen sind 11 und 9; beide Gruppen sind abelsch. Ihr direktes Produkt ist daher abelsch.

## Belastbarkeit der Herkunfts- und Laufbehauptungen

Repositoryzugriff und berichtete Sandboxläufe sind Selbstangaben ohne beigefügte Laufprotokolle. F02 wird in der Familienbeschreibung mit null Versuchen, später mit mehreren Tausend ausgeführten Versuchen angegeben. Das lässt sich aus der Abgabe nicht auflösen; der gelieferte F02-Code bricht in der angegebenen NetworkX-Version beim ersten Versuch ab. Andere tatsächlich verwendete Skripte sind nicht mitgeliefert. Daraus folgt eine Dokumentationslücke, kein Nachweis, dass überhaupt keine Ausführung stattfand.

Die Behauptung, HoG-Gründergraph6 seien öffentlich nicht extrahierbar, trifft auf unseren öffentlichen Projektstand nicht zu: Zehn Referenzgraphen einschließlich HoG-Dateien stehen unter `data/memetic_v2/reference/`; ihre Verfügbarkeit wurde beim vorherigen Codex-Abgleich gegen Commit `5a6d150568d4ec637bdb1090d44febc9cf27b5b1` bzw. dessen Vorgänger belegt. Einschränkungen von Groks eigenem Zugriff bleiben möglich.

Die vorgeschlagenen mindestens 16 GiB RAM sind für diese Abgabe nicht hergeleitet. Das bereits ausgeführte Gemini-CSP und die reproduzierten Codex-Konstruktionen zeigen, dass die hier vorliegenden Vollständigkeits- und Konstruktionsprobleme nicht pauschal auf mehr RAM verschoben werden können.

## Schlussfolgerung

Keine dieser sechs Familien liefert hier einen neuen geprüften Gründer. Mehrfamilienrhetorik, Ressourcenangaben und ein leeres maschinenlesbares Ergebnis ersetzen keine lauffähige Konstruktion. Die Abgabe ist als Kandidatenlieferung erfolglos; sie erlaubt keine allgemeine Rangfolge von Grok gegenüber anderen Modellen oder Modi.

Falls ein weiterer Versuch gewünscht ist, sollte er sich auf genau eine vollständig implementierte Konstruktion (F01 mit Verbot zusätzlicher Dreiecke oder F05 als exaktes CSP) konzentrieren. Dafür genügt zunächst ein gültiger, nachvollziehbar prüfbarer Graph. Ein großer Ryzen-Lauf mit den vorliegenden Skripten ist nicht gerechtfertigt. Die erfolgreiche Kandidatensammlung und das geplante Fluchtwegsexperiment können unabhängig davon fortgesetzt werden.
