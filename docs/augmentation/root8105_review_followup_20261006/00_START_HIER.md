# ROOT8105 — umgesetzte Review-Fortsetzung,06.10.2026

1. `ABGLEICH.md`: Was am Review übernommen wird, zusätzliche Korrekturen und Beweis.
2. `ERGEBNISSE.md`: abgeschlossene neue Rechnungen und ihre Aussagegrenzen.
3. `PLAN.md`: angepasste Fortsetzung und Entscheidungen vor einer Großkampagne.
4. `ABSCHLUSS_ABWEICHUNG.md`: Cloud-Persistenzabweichung und Betriebsversion1.0.1.

## Stand

- Alter Census, Audit und4608er Pilot nicht wiederholt.
-3072 neue Zustände:12288/12288 vorhergesagte Filterentscheidungen stimmen.
-48 exakte eingeschränkte Breiten; keine Stichprobenquoten als Ersatz.
-24 Roots:7884 Matchings,5182 Stabilisatororbits, kein Rootausschluss.
-96 Kalibrierungsabstiege abgeschlossen; starke Gewichtskonzentration, keine
 abgesicherte Beschleunigung und keine globale Machbarkeitsfreigabe.
-40000-Abstiege-Hauptmessung implementiert und vorbereitet, nicht ausgeführt.

Quellen: `experiments/memetik/root8105_review_followup_1_0_0` für die ausgeführten
mathematischen Läufe; `..._1_0_1` als neue Betriebsversion mit vollständigem atomarem
Abschlussbeleg. Beide enthalten den unveränderten historischen Kern in `reference/`.
Im Downloadpaket liegen diese unter `code/`.

Die Datei TREE_CALIBRATION.json ist ein aus96 validierten Endergebnissen
rekonstruierter Analyseexport. Die zugehörige alte SQLite-Datei hat einen
widersprüchlichen Endstand und darf nicht als freigegebener Resume-Stand dienen.
Originale Rohstände bleiben in den beiden tar.gz-Archiven erhalten. AUDIT.json
trennt den konsistent geschlossenen Tiefe-2-Lauf von dieser Kalibrierungsabweichung.

Regeln:40c0050af19353fd9c9d1a203e58f5df07636229; GC-22 wird mit diesem Paket ergänzt.
Reviewarchiv:e4d4d6387a71b096ae949b3cc5e629891f7ab862.
C2 und alte Pakete nicht verändern. Keine fertigen Zählungen wiederholen.

Nächster praktischer Schritt: Betriebsversion1.0.1 auf der vorgesehenen
Zielhardware vorbereiten und dort den Vorabtest ausführen. Erst dann die neue
Hauptmessung starten; Details im README dieser Version.
