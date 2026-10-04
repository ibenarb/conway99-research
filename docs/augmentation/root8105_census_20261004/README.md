# ROOT8105 P0/P1: geprüfter Zensuscontroller1.0.0

Freigabe aus Übergabe vom04.10.2026: historisches F vollständig zählen,
GC-19 technisch umsetzen, Wiederaufnahme/Abrechnung prüfen, neue notwendige
Filter getrennt entwickeln. Keine P2/P3- oder Vollbaumkampagne gestartet.

Quellen: `experiments/memetik/root8105_census_1_0_0`.
`MATHEMATIK.md` beschreibt Modell, Ganzzahlbeweis, Sampler und Filter.
`VALIDATION.json` enthält den finalen Paketfingerprint und die Prüfmatrix.
`MATHEMATICAL_CHECKS.json` enthält auch die24 expliziten gepaarten Zustände.
`INTEGRATION_CHECKS.json` und `INTEGRATION_RAW.tar.gz` sichern den isolierten
elf-Worker-Test:66 Roots,5478 Counts, nach Wiederaufnahme weiterhin exakt66
Versuche und zwei geschlossene Sitzungen. Keine Cloudzeiten als Ryzen-ETA.

Ergebnis:152 kleine SAT/DP/Vertex-Abgleiche,81 exhaustive Rangbijektionen,
249 m7-Reviewerbreiten,3 unabhängige m7-Vertexzahlen und24 historische
F-SAT-Kontrollen bestanden. Ein zusätzlicher Kapazitätswiderspruch wurde
in einer separaten SAT-Aufgabe als UNSAT bestätigt; keine formale Zertifizierung
und keine repräsentative Filter-Wirksamkeitsschätzung.
BvLS243 vollständig per Adjazenzmatrix/Paarzahlen kontrolliert,12 Präfixe
bestehen beide Filter. Kein Conway99-Fund.

`ENTWICKLUNG.md` und `development_evidence.tar.gz` dokumentieren die
abgefangenen Fehler einschließlich des ersten widersprüchlichen
Cloud-Persistenztests. Nur der abschließende isolierte Ablauf ist als
Betriebsbeleg gewertet. Ungeklärte offene Sitzungen blockieren Resume weiterhin.

Nächster Nutzerablauf: Paket herunterladen, isolierte Installation,
Ryzen-Preflight,66-Root-Kalibrierung, Messwerte auswerten, vollständiger
8105×83-Zensus mit11 Workern.48 aggregierte CPUh sind eine Meldeschwelle;
keine Antwort lässt den Zensus weiterrechnen. Status ca.alle10min.
Windows-Stopwatch und echte WSL-Last sind noch auf Zielhardware zu prüfen.
