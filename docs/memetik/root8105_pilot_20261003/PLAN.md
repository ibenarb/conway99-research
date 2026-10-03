# ROOT-8105 Augmentationspilot 1.0.1

Stand: 03.10.2026. Ein instrumentierter SAT-Zeilenpilot mit kanonischer
Zustandsidentifikation, kein fertiger erschöpfender Canonical-Construction-Path-
Solver. Der Pilot liefert insbesondere keinen Rootausschluss.

## Zweck und Umfang

128 Rootklassen, geschichtet nach exakter Stabilisatorordnung und Zahl der
lokalen Matchings; mindestens ein Vertreter jeder besetzten Schicht. Die
vollständige Eingangsliste mit 8105 Vertretern ist enthalten. Vorbereitung
prüft alle Vertreter, nauty-Klassen, Automorphismenordnungen und die
Orbitgrößensumme gegen eine unabhängige Vertex-Eliminations-DP.

Jeder Root erhält zwei Suchaufgaben mit je 3600 CPU-Sekunden:

- `ordered`: immer die kleinste noch offene H-Zeilenidentität;
- `dynamic`: je Elternzustand bis zu vier zufällig gewählte Vertreter der
  offenen Zeilenorbits unter der Automorphismengruppe des Zustands.

Beide Arme haben denselben Root-Seed. Die Pfade sind danach verschieden;
kein Anspruch auf identische Zufallsfolgen oder repräsentative Tiefenfrontiers.

Keine künstliche Tiefengrenze: Gesucht wird bis zu allen 84 H-Zeilen,
solange Ressourcen verfügbar sind. Tiefen 20, 30, 32, 40, 50, 60, 70, 80
und 84 sind nur Meilensteine mit gesicherten Zuständen. Ein Zustand besteht
aus vollständigen H-Zeilen, nicht bloß einem induzierten Untergraphen.
Erreichbarkeit hoher Tiefen wird nicht zugesagt.

## Exakte lokale Regeln und begrenzte Auswahl

Der SAT-Encoder baut für die nächste Zeile sämtliche Randmargen und die
Gemeinsame-Nachbarn-Gleichungen zu den gebauten Zeilen. Zusätzlich erzwingt
er für jede gebaute Zeile symbolisch deren gesamte lokale 7K2-Struktur.
Unbekannte Kanten innerhalb dieser Sterne bleiben SAT-Variablen. Es gibt
keinen vorgeschalteten Katalog von Millionen Level-2-Matching-Cubes.

SAT-Modelle werden ausschließlich auf die nächste H-Zeile projiziert. Eine
Blockierklausel sperrt danach diese ganze Projektion, unabhängig von den
Hilfsvariablen. Alle erzeugten Zeilen werden erneut auf Grad, Diagonale,
Randmargen, Symmetrie und gemeinsame Nachbarn geprüfter Zeilen geprüft.

Pro Zeilenprojektion: 30 CPU-Sekunden oder 65536 verschiedene Zeilen;
zusätzlich 180 Gast-Wallsekunden als Betriebsgrenze. Vollständigkeit erst bei
abschließendem UNSAT. Auch ein Limit genau nach der letzten tatsächlich
existierenden Lösung bleibt ohne diesen Nachweis `LIMIT_UNRESOLVED`.

Bis zu 32 Zeilen werden per Reservoir aus der beobachteten Enumeration
gewählt. Nur bei vollständiger Enumeration ist dies ein gleichverteiltes
Reservoir der gesamten Projektionsmenge. Bei Abbruch bleibt es eine
SAT-reihenfolgeabhängige Stichprobe. Es wird nicht als Zufallsstichprobe des
unbekannten vollständigen Suchbaums verkauft.

Die nächste Frontier enthält höchstens 64 kanonisch verschiedene Zustände.
Der exakte nauty-Zertifikatbytestring entscheidet Gleichheit. SHA256 wird nur
als reproduzierbare Auswahlpriorität verwendet, nicht als Gleichheitsbeweis.
Die Zeilenreihenfolge selbst ist kein Bestandteil des Zustands. Unbekannte
Kanten sind durch die Färbung gebaut/offen von bekannten Nichtkanten getrennt.
Die Rollen x und u bleiben im Hauptsuchlauf fest.

Die frühe Zeitverteilung bleibt bis Tiefe 28 wie in 1.0.0. Ab Tiefe 29 gilt
ein rollierender Planungshorizont von mindestens vier Erweiterungsstufen:
Schichtbudget = min(Restzeit, max(Knotenbudget, Restzeit / max(4, 32-Tiefe))).
Die Zahl 32 ist dabei ausschließlich ein Planungsparameter. Sie beendet
die Suche nicht; auch Tiefe 33 bis 84 wird unter dem gleichen Zeitbudget
weiterverfolgt. Das verhindert sowohl eine Verknappung flacher Stufen durch
einen 84er-Divisor als auch den gezielten Verbrauch der Restzeit bei Tiefe 31.
Bei leerer ausgewählter Frontier startet ein neues Reservoir-Suchsegment ab
Root; alte Messungen und CPU-Konten bleiben erhalten. Eine begrenzte,
leer gewordene Frontier ist kein Nichtexistenzbeweis.

Eine vollständig gebaute H-Matrix wird sofort in den Gesamtgraphen
zurückübersetzt und unabhängig mittels aller Grade und Nachbarschnittzahlen
geprüft. Nur bei Erfolg lautet der Status `SRG_FOUND_VERIFIED`; der Controller
prüft den gespeicherten Graphen erneut und beendet die Kampagne geordnet.
Ein solcher Fund ist ein Existenznachweis, kein Rootausschluss.

## Zertifikate und Rollentausch

Für höchstens zwei vollständig enumerierte Projektionen pro Suchaufgabe
wird anschließend die Formel mit allen Projektions-Blockierklauseln neu
aufgebaut. Glucose erzeugt einen DRAT-Beweis; der separat kompilierte
`drat-trim` prüft ihn. Formeln, Projektionen, Beweise und Prüferlogs bleiben
für spätere Prüfung erhalten. Budget: 40 CPU-Sekunden je Prüfaufgabe,
höchstens 512 Prüfaufgaben. Ein Timeout bleibt unzertifiziert.

Ein solcher Beweis zeigt: In dieser notwendigen Relaxation fehlt keine
weitere Zeilenprojektion. Er beweist nicht, dass die behaltene Beam-Frontier
alle Fortsetzungen abdeckt. `certified_root_exclusions` bleibt deshalb null.

`level2.py` misst zusätzlich die x/u-Rollentauschquotientierung auf allen
lokalen Matchings der ausgewählten 128 Roots. Diese Teilmenge ist nicht
unter Umrootung abgeschlossen. Die Zahlen gelten nur innerhalb der
Teilmenge und werden ausdrücklich nicht als vollständige Level-2-Zahlen
oder als Pruningregel für tiefere partielle Zustände verwendet.

Die globale lineare Relaxation ist in `core.encode(..., target=None)` für
weitere Audits vorhanden. Sie wird im Hauptpiloten nicht verwendet: Ein
Entwicklungstest fand in 60 CPU-Sekunden noch kein erstes Modell, während
die lokale Variante schnell Breitenmessungen liefert.

## Hardware und Budgets

Empfohlen: vorhandener Ryzen unter WSL2/Linux, elf einzelne Suchworker,
keine GPU, keine neue Hardware. Elf Worker bedeuten elf native Solverthreads;
der leichte Überwachungs-Thread pro Worker verbraucht praktisch keine
zusätzliche Rechenkapazität. Es gibt keine harte CPU-Affinität gegenüber C2.

| Größe | Grenze |
| --- | ---: |
| Suchziel | 256 CPU-h |
| Gesamtbudget einschließlich Prüfungen/Hilfsarbeit/Reserve | 270 CPU-h |
| Gleichzeitige Worker | höchstens 11 |
| Adressraum pro Worker | 1,5 GiB |
| Freier RAM außerhalb reservierter Workerbudgets | 6 GiB |
| Notstopp bei verfügbarer RAM-Menge unter | 2 GiB |
| Maximale Größe dieses Laufs | 100 GiB |
| Verbleibende freie Plattenreserve | 25 GiB |
| Regulärer Status im Controllerlog | alle 10 Minuten |
| Atomare Statusdatei | etwa jede Sekunde |

Für den Start möglichst mindestens 125 GiB frei halten. Die Überwachung
berücksichtigt auch den laufenden C2-Prozess über `MemAvailable`, ohne ihn
anzufassen. Falls der freie RAM elf reservierte Worker nicht zulässt,
starten entsprechend weniger. 256/11 = 23,27 Stunden ist eine reine
Budgetprojektion bei voller CPU-Auslastung, keine Ryzen-ETA. Die Gastuhren
UTC, monotonic und MONOTONIC_RAW werden getrennt protokolliert. Eine
Windows-Hostuhr wird nicht behauptet oder synthetisch korrigiert.

Suchaufgaben dürfen bis 30 CPU-Sekunden Beendigungsreserve verbrauchen.
Überschreitungen werden vollständig per `wait4` gebucht und als lokale
Warnung ausgewiesen. Ein-/Ausgabe, CPU-Konten und Resultate bleiben
getrennt. Controllerfehler oder ungeordnete WSL-Neustarts lassen einen
Sitzungsmarker zurück; ein Folgestart verweigert dann die stille
Wiederaufnahme. Dafür ist ein Recovery-Audit nötig. Den Marker nicht löschen.

## Enthaltene Werkzeuge

Alle folgenden Programme laufen mit dem eigenen Interpreter `.venv/bin/python`
im entpackten Paketverzeichnis; Laufverzeichnis als separates Verzeichnis
außerhalb des Pakets wählen. Keine bestehende Memetik-/C2-Umgebung ändern.
Die interaktive Einrichtung erfolgt mit Ralph jeweils genau einen Schritt
pro Nachricht; hier nur die Zuordnung, kein automatisch startender Hauptlauf.

| Datei | Aufgabe |
| --- | --- |
| `setup.py` | Neue isolierte Umgebung; fixierte Abhängigkeiten; DRAT-Prüfer kompilieren |
| `prepare.py LAUFVERZEICHNIS` | Rootprüfung, 128er-Auswahl, 256 eingefrorene Aufgaben |
| `preflight.py LAUFVERZEICHNIS` | Kontrollen, Level-2-Messung und reale parallele Zielhardwarekalibrierung |
| `campaign.py LAUFVERZEICHNIS` | Hauptlauf oder saubere Wiederaufnahme; erzwingt aktuellen Preflight |
| `report.py LAUFVERZEICHNIS` | CSV-Auswertungen und JSON-Zusammenfassung |

Voraussetzungen: Linux/WSL, Python >=3.10 mit venv, C-Compiler `cc`, Internet
für die Python-Abhängigkeiten. Der DRAT-Prüferquelltext ist enthalten.
`--test` ist ausschließlich für die im Paket enthaltenen Betriebsprüfungen;
im Hauptlauf nicht verwenden.

Für eine saubere Pause SIGTERM an den Controller senden oder Strg+C im
Vordergrund. Er beendet seine eigenen Worker, erstellt CPU-Endbelege und
schließt die Sitzung. Fortsetzen mit derselben `campaign.py`-Invocation.
Ein CPU-Limit ist ein regulärer UNKNOWN-Abschluss der betreffenden Aufgabe;
es wird bei Wiederaufnahme nicht still verlängert.

## Ergebnisinterpretation

`growth_by_depth.csv` trennt exakte Projektionsbreiten von zensierten
Untergrenzen. Es enthält SAT-/Encoder-/Kanonisierungszeit, beobachtete
Kandidaten, Duplikate gegen die behaltene Stichprobe und Speicherhöchstwerte.
`roots_summary.csv` enthält die erreichten Tiefen je Root und Arm.
`summary.json` enthält CPU-Abrechnung, Zertifikatszahlen und Fehlerstatus.

Die Duplikatzahl ist keine vollständige kanonische Schichtbreite. Es gibt
keine ungesicherte Multiplikation durchschnittlicher Verzweigungsfaktoren
zu einem vermeintlichen Gesamtbaum. Große zensierte Breiten und geringe
Kompressionsraten sind bereits aussagekräftige Warnsignale für explizite
Vollenumeration. Exakte Gesamtbaumgrößen bleiben unbekannt.

## Referenzen

Projekt- und Regelstand: Commit `002dc628005ee2c819bbc17d26498d1f06d28ca7`.
Relevante Regeln: GC-01/02/05/08/10/11/14/15/16/17. Die Präzisierung zu
GC-17 steht im Pilotplan: Vollständige feste Reihenfolge genügt zum
Ausschluss vollständiger Graphen; begrenzte Tiefenbarrieren genügen nicht.

Rootliste: bereitgestelltes `ROOT_8105_reps_package_convention.tsv`, SHA256
`c525d03be144a7493c3239340c6263dcb8a29b5521e5d3b152ce43afe90cac41`.
Die eigenen Kontrollen übernehmen weder fremde Prüflogs als eigene
Ausführung noch den früheren WALK-Solver als auditierte Grundlage.

DRAT-Trimmer: https://github.com/marijnheule/drat-trim,
Commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, Originalquelltext und
Lizenz unter `vendor/`. SAT-API: https://pysathq.github.io/docs/api/solvers.html.

## Versionswechsel 1.0.1

Neue Paketversion und neues Laufverzeichnis verwenden. Alte 1.0.0-Manifeste
mit `target_depth` werden ausdrücklich abgewiesen; laufende oder archivierte
1.0.0-Versuche werden nicht verändert. Ressourcenbudgets bleiben unverändert.
`depth_controls.py` testet synthetische Steuerpfade über Tiefe 32 bis 84
und CPU-Abbruch bei Tiefe 35, außerdem eine echte vollständige 9er-Rooklösung
samt Kampagnenstopp und Zurückweisung eines beschädigten Vollgraphen.
Die synthetischen Tests sind ausdrücklich keine 99-Knoten-Konstruktionen.
