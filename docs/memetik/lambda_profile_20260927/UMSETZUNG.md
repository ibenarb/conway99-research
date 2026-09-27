# Umsetzung des freigegebenen Weglängenprofils, 27.09.2026

Eigenständiges Paket `lambda_profile_1_0_0`, Forschungszweig λ-Memetik auf Ryzen.
Plan: [Vollreview und Plan V2](../lambda_review_20260927/ABGLEICH_VOLLREVIEW_UND_PLAN_V2.md)
bei Commit ed3193cf07ae29c284153c56f928564e4e80a1d9, vom Nutzer anschließend freigegeben.

Zwei exakte Startgraphen, zehn einzelne Weglängen, je300 Episoden. Höchstens20
Such-CPU-h (eine je Zelle),2 Hilfs-CPU-h,4 Windows-Hoststunden. Feste Seeds und
Starts, unveränderter Apex/Pivot-Katalog, ursprüngliche P-Gleichstandsbehandlung.
Eine bessere Episode ändert weder Startgraph noch Stichprobe. W2079 dient nur als
gezielt eingespeiste Kontrolle. Kein Tiefe-5-Lauf oder Populationshauptlauf.

Die Quellen der bisherigen Radiuskampagne und des alten Operators bleiben
unverändert. Der neue Controller basiert auf der geprüften Radius-Infrastruktur:
Windows-Hostuhr, wait4, vor Spawn persistierte CPU-Reservationen, Hash-Receipts,
geordnete Pause und Wiederaufnahme, keine stillen Resets nach einem harten Crash.
Zellen werden mit bis zu10 abgeschlossenen Episoden pro Sitzung reihum bedient;
ein eigener180-CPU-s-Sitzungsdeckel ermöglicht auch bei langen Episoden einen Wechsel.
Verbleibendes Zellbudget wird vor jedem Spawn reserviert, kleine Restreserven
werden nicht als zusätzliche Suchzeit ausgegeben. Geordnete Pausen behalten alle
bereits verbrauchten Budgets; Pausezeit zwischen Sitzungen zählt nicht als aktive
Hostlaufzeit. Bereits aktive oder unaufgelöste Sitzungen verhindern Doppelstarts.

## Prüfung

Über isoliertes `tools/memetik/audit_python.py`, pynauty2.8.8.1:

- Vergleich neuer Episoden mit dem unveränderten Produktions-Engine-Code: gleiche
  gesamte Zugfolge und gleicher RNG-Endzustand an beiden fixierten Starts.
- Positiver Vier-Zug-Zeuge und konkreter Steilstabstieg ab dessen Mittelpunkt geprüft.
- Erzwungene Unterbrechung innerhalb des Katalogs und direkt nach Zugwahl:
  fortgesetzte Pfade, Endpunkte und Indizes identisch zum ununterbrochenen Lauf.
- Tatsächliche Worker über mehrere Sitzungen, wait4-Abrechnung, Hash-Receipts,
  vollständige Wiederaufnahme ohne erneute Suchkosten und Taskmanipulationsschutz.
- Ausgeschöpfte Zelle blockiert keine andere Zelle; keine Budgetübertragung.
- Gesamte Pipeline mit kleiner Teststichprobe einschließlich Kontrollen,
  Kalibrierung, Bericht und geordnetem Abschluss erfolgreich.
- Tatsächliche kurze CPU-Sitzung pausiert mit gespeichertem Weg; Fortsetzung
  schließt dieselbe Episode ab, wait4-Sitzungssumme bleibt vollständig erhalten.
- Entpacktes ZIP: eigenständige Vorbereitung, Überschreibschutz, Quellmanipulation
  abgewiesen und kein vorgetäuschter Linux-Ersatz für die Windows-Uhr.

Ergebnisse: `TEST_RESULTS.json` und `INTEGRATION_RESULTS.json` beim Programm;
`PACKAGE_TEST_RESULTS.json` hier. Cloud-Schedulerprüfungen nutzen ausdrücklich
FakeHost, keine Behauptung eines hier ausgeführten Ryzen-/Windows-Tests.
Produktionsstart enthält den realen Windows-Host-/CPU-Kontrollschritt.

Beim ersten Kontrollaufruf gab es einen Syntaxfehler im neuen Testadapter
(reserviertes Wort `class` als Keywordargument); vor allen erfolgreichen
Kontrollläufen korrigiert. Ein lesender Befehl suchte die alte runtime.py zunächst
im falschen Verzeichnis; der tatsächliche gepinnte Pfad wurde anschließend gelesen.
Keine Daten oder eingefrorenen Programme wurden dadurch verändert.

## Ergebnisse und Grenzen

Vollständige Traces und Endpunkt-Graph6 stehen je Zelle in SQLite und abschließend
in JSONL. Alle Endpunkte werden unabhängig voll bewertet und kanonisiert;
verbessernde Wege zusätzlich Schritt für Schritt replay-geprüft. PROFILE.json
enthält Rückkehr-/Verbesserungsraten, Qualitäts-/Klassenkennzahlen und CPU-Kosten;
unvollständige Episoden bleiben mit ihrem Weg erhalten.

Phasen-CPU misst die Berechnung innerhalb Perturbation, Abstieg und Verifikation.
Start-, Schreib- und weitere Kosten sind vollständig in wait4, aber nicht exakt
pro Episode/Phase zugeordnet. Der Bericht weist diese Restkosten ausdrücklich
getrennt aus. Ein exakter Anteil sämtlicher CPU für Rückkehrepisoden wird daher
nicht behauptet. Die Mittelwert- und Methodenbewertung verwendet volle wait4-CPU.

Bei Start gemessene freie CPU-Kapazität begrenzt die Workerzahl konservativ,
maximal12; Worker nutzen nice10. Später entstehende Konkurrenz kann die Walltime
verlängern. Die Roharchive alter Läufe werden nicht gebraucht oder geändert.
Noch kein Produktionslauf auf dem Ryzen gestartet: dies erfolgt mit dem separat
bereitgestellten Einzeiler des Nutzers.
