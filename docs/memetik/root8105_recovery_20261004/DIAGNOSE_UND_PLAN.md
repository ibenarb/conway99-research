# ROOT8105 Recovery 1.0.2 — 04.10.2026

## Befund

251 von 256 Suchaufträgen endeten regulär mit CPU_LIMIT_UNKNOWN.
Worker: 903622.85703 CPU s. Nebenarbeiten: 69639.70651290001 CPU s.
Gesamt: 973262.5635429 CPU s, 1262.5635429 s über dem alten 270-h-Budget.
Fünf Suchaufträge und die gesamte Zertifikatsphase fehlen. Maximaltiefe16
ist lediglich eine Stichprobenbeobachtung, kein Ausschlussbeweis.

Der alte Controller lief wiederholt rekursiv durch alle Dateien. Der genaue
Anteil dieses Vorgangs an den Nebenarbeiten wurde nicht separat profiliert.
Das nicht unterbrechbare Scannen erklärt einen konkreten Skalierungs- und
Reaktionszeitfehler; die neue Version begrenzt jeden Scanabschnitt auf maximal
4096 Einträge und ein Ziel von 0.05 Gast-Monotoniksekunden. Einzelne blockierte
OS-Aufrufe haben keine harte Laufzeitgarantie. Größenmessung bleibt eine
Stichprobe mit ausgewiesenem Fortschritt; verfügbare Plattenkapazität und CPU
werden in jeder Controller-Runde geprüft. Nach einem vollständigen Scan werden
300 Sekunden bis zum nächsten gewartet. Kein eigenes Scan-Unterprogramm.

## Exakter Umfang der Fortsetzung

- r8090_dynamic
- r8094_ordered, r8094_dynamic
- r8098_ordered, r8098_dynamic
- Anschließend bis zu512 bereits vorgesehene lokale Projektionszertifikate.

Originalpaket1.0.1, Mathematik, Solver, Beweisprüfer, Jobdateien, Manifest und
alte Vorprüfung bleiben byteidentisch. Der neue Controller verwendet die alte
isolierte Python-Umgebung und die ursprünglichen Worker direkt. Er ergänzt
Receipts und Nebenarbeitskonto; die251 alten Receipts werden vor jedem Start
inhaltlich gegen die übergebene Diagnose verglichen. Original-Metadaten werden
vor dem ersten Start unter before_recovery_102 gesichert. Fehlende Artefakte,
veränderte Quellen/Jobs, offener Sitzungsmarker oder ein belegtes Controllerlock
verhindern den Start. Ein SIGTERM erlaubt sauberes Pausieren; ein Absturz mit
offenem Marker verlangt erneut Audit, niemals manuelles Löschen des Markers.

## Explizite Ressourcenfreigabe

Vorgeschlagen: einmalig16 zusätzliche CPU-Stunden; gesamte Kampagnengrenze286h.
Das sind nach der bereits verbuchten Überschreitung noch56337.4364571 CPU s.
Fünf Suchstunden, bis512*40s nominelle Beweisbudgets, Nachlauf und großzügige
Reserve passen hinein. Maximal11Worker; RAM- und Plattengrenzen unverändert.
Erst --run zusammen mit --authorize-additional-cpu-hours 16 aktiviert dies.
Wiederaufnahmen addieren NICHT nochmals16h. --check startet keine Suche.
Die zusätzlichen16CPUh sind keine Walltimeprognose. Zielhardwareprüfung steht
vor Auslieferung noch aus; danach grob1–2h für die Fortsetzung, abhängig von
Beweisprüfungen und Nebenarbeit, ohne Zusage.

## Bedienung (in der Unterhaltung einzeln ausführen)

1. Separat entpacken, ursprüngliches Paket und Laufverzeichnis erhalten.
2. Mit dem Python aus1.0.1 recover.py RUN --package ORIGINALPAKET --check starten.
3. Erst nach RECOVERY_CHECK_PASS starten mit denselben Pfaden, --run und
   --authorize-additional-cpu-hours 16. Ausgabe in neues recovery_102.log,
   niemals controller.log überschreiben.
4. Nach Ende Status/Receipts sowie lokale Zertifikatsresultate prüfen.

Die Laufdaten werden nicht kopiert oder gelöscht. Kein anderer Prozess,
insbesondere der C2-Prüfer, wird verändert.

## Kontrollen und Grenzen

VALIDATION.json enthält Cloudtests mit echter Pause/Wiederaufnahme, exakt
bewahrter Vorabrechnung, echten SAT-/DRAT-Prüfungen, Korruptionskontrollen und
einer Fortsetzung ausschließlich zur Beweisprüfung. Vollständiger Hashabgleich
aller256 Jobdateien wurde unabhängig rekonstruiert. Tatsächliche Ryzen-
Checkpoints und Beweisartefakte werden erst durch --check geprüft.
Die synthetischen Tiefe84-Kontrollen sind KEINE Conway99-Graphen.
Keine Rootausschlüsse durch dieses Stichprobenverfahren.

Relevante Betriebsregeln: GC-01,02,03,05,08,10,11,15,16,17; neue Lehre:
Dateisystemüberwachung muss pro Supervisor-Runde beschränkt sein und ihr
Aufwand muss bei wachsendem Artefaktbestand separat sichtbar bleiben.
