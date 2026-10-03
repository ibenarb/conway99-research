# Änderung 1.0.1: kein künstlicher Tiefenabbruch

Auf ausdrücklichen Wunsch von Ralph am 03.10.2026 wird die Grenze 32 entfernt.
Die Suche läuft unter unveränderten CPU-, RAM- und Plattenlimits bis zu einer
vollständigen 84-Zeilen-H-Matrix. Alte Pakete und ihre Kontrollbelege bleiben
als Version 1.0.0 erhalten; die neue Implementierung steht unter
`experiments/memetik/root8105_pilot_1_0_1`.

## Zeitverteilung

Ein bloßer Austausch von target_depth=32 gegen 84 hätte die flachen Stufen
unnötig verknappt. Stattdessen sind erlaubte Suchlänge und Zeitscheduling
getrennt. Die Schichtzeit lautet jetzt

min(Restzeit, max(Knotenzeit, Restzeit / max(4, 32 - aktuelle_Tiefe))).

Bis einschließlich Tiefe 28 entspricht das, abgesehen von expliziter
Begrenzung auf die tatsächlich verbleibende Restzeit, der bisherigen
Verteilung. Ab Tiefe 29 bleibt ein rollierender Horizont von vier
Erweiterungsstufen. Ein breiter Zustand bei Tiefe 31 beansprucht dadurch
nicht planmäßig die ganze verbleibende Zeit. Der Wert 32 ist ausschließlich
ein Schedulingparameter, keine Erfolgsmeldung und keine Abbruchbedingung.

Tiefen 20/30/32/40/50/60/70/80/84 erzeugen Meilensteindateien. Bestzustände
werden weiterhin unmittelbar gesichert. Bei 84 Zeilen rekonstruiert ein
separater Prüfer den Gesamtgraphen und testet alle Grade, Diagonale,
Symmetrie sowie die gemeinsame-Nachbarn-Zahl für jedes Knotenpaar. Erst
anschließend wird SRG_FOUND_VERIFIED gemeldet. Der Controller prüft die
Datei erneut und beendet seine Kampagne geordnet. CPU-Limits bleiben UNKNOWN.

## Kontrollen und Aussagegrenze

- 84 Vergleiche der frühen Budgetverteilung (28 Tiefen, drei Restbudgets).
- Synthetischer Steuerpfad überschreitet 32 und erreicht 84.
- Synthetischer CPU-Abbruch nach Überschreiten von 32 meldet UNKNOWN bei 35.
- Tatsächlicher Suchpfad auf srg(9,4,1,2) findet den vollständigen Rookgraphen;
  unabhängiger Gesamtgraphprüfer und Kampagnenstopp werden real ausgeführt.
- Beschädigter vollständiger Graph wird zurückgewiesen.
- Die vorhandenen SAT-, Root-, DRAT-, Fehlerisolations- und Pause/Resume-
  Kontrollen laufen im neuen Preflight mit.

Die synthetischen Steuerpfade enthalten keine echten 99-Knoten-Zustände.
Es wird weder Tiefe 33 noch 84 als mathematisch erreichte Konstruktion
behauptet. Sie prüfen ausschließlich die Aufhebung der technischen Schranke.
Die ursprünglichen echten Suchbefunde (maximal Tiefe 14) bleiben unverändert.

Neue Manifeste und ein neues Laufverzeichnis sind erforderlich. 1.0.0-
Manifeste werden nicht still umgedeutet. Der komplette Ryzen-Hauptlauf wurde
weiterhin nicht gestartet. Relevante Regeln: insbesondere GC-08/10/14/16/17.
