# C2: abgeschlossener Literaturabgleich und vollständige Modellspezifikation

Stand: 13. September 2026. Fortsetzung des Forschungsplans aus Commit ba8d71ccaab4d64088cc6802382a8ea4dbe68603.

- [Literaturabgleich und begrenzte Aussage zur Neuheit](LITERATURABGLEICH.md)
- [Vollständige Spezifikation mit Beweisen und Encodervertrag](SPEZIFIKATION.md)
- Prüfrechnung: `src/c2_spec_20260913/check_spec.py`
- Ergebnis: `results/c2_spec_20260913/controls.json`
- Integritätsmanifest: `results/c2_spec_20260913/manifest.json`

Ergebnis: C2_SPEC_CONTROLS_PASS. Der Graphfall mit Involution ist vollständig durch die Spezifikation erfasst, unter Verwendung des zitierten Fixpunktsatzes. Die 42-Paar-Darstellung erzwingt ein perfektes Matching von Doppelverbindungen, einen vorzeichenbehafteten 10-regulären Rest und dessen Spektrum. Diese Konsequenzen erhalten ausdrücklich keinen ungeprüften Neuheitsanspruch.

Noch offen: Produktionsencoder und dessen Verifikation, Ryzen-Pilot und jeder neue C2-Ausschluss. Es wurde keine Solverkampagne gestartet und kein Prozess auf dem Rechner des Nutzers verändert.

Der folgende Implementierungsschritt ist bereits durch den angenommenen Forschungsplan vorgesehen. Status/ETA eines späteren lokalen Suchlaufs mindestens alle zehn Minuten; Pilotbudget und gemessene Ressourcen vor Start angeben. Für ein späteres ausdrücklich vereinbartes Endgame gelten dessen Ressourcenregeln, nicht automatisch Pilot-Timeouts.
