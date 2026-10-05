# ROOT8105 Census 1.0.1-rc2 — Prüfbericht

Stand 2026-10-05T00:28:10.384118+02:00. Ergebnis: Cloud-Abnahme bestanden;
Kandidat für die Zielhardware-Abnahme, noch keine Produktionsfreigabe.

## Umsetzung

Review-RC1 als Basis, mathematischer Kernel/historical_core/Roots/Fixtures
byteidentisch zu 1.0.0. Recovery validiert vor Schreibzugriffen die Lauf- und
Paketidentität, Rootdaten, Kontenverknüpfungen und CPU-Werte. Inkohärente
RUNNING-Roots werden mit NEW_RUN_REQUIRED abgewiesen; kein irreführender
Verweis auf eine nicht mögliche Kontenreparatur. Trockenlauf lesend, Sperren
auch nach Fehlern freigegeben. Elternprozessprüfung mit PID und Startidentität.

## Eigene Prüfungen

- 20 Prozess-/GC-19-Betriebsprüfungen: PASS. Hostfehler über Linux-Attrappen,
  keine echte PowerShell. Unterbrechung, lokale Workerfehler und Recovery enthalten.
- 7 neue Recovery-Prüfgruppen: PASS. Veränderte Identitäten, verwaiste Roots
  und ungültige CPU-Werte werden ohne Kontenänderung abgewiesen.
- Vollständige Mathematikkontrolle: 152 SAT/DP/Vertex-Fälle, 81 Rangbijektionen,
  249 Fixture-Regressionen, 3 unabhängige m7-Vertexzahlen, 24 konkrete SAT-Zeilen,
  vollständige BvLS-Kontrolle mit 12 positiven Präfixen, ein unabhängig per SAT
  bestätigter Kapazitätsausschluss. Kein Leistungsnachweis der Filter auf99Vertices.
- Unveränderter vollständiger Preflight einschließlich Ressourcenprüfung PASS:
  131.590 CPU-Sekunden, Dateisystem overlay, Hostprüfung NOT_WSL.
- Echte Kalibrierung: 66 Roots, 5478 Counts, elf gleichzeitig aktive Worker.
  SIGTERM mitten in elf Roots; 390 Zielzählungen bei Resume unverändert
  übernommen. 77 Versuche, keine offenen Versuche oder Sitzungen; Ende
  CALIBRATION_COMPLETE, 8039 Roots weiterhin PENDING.
- Verbuchter Kalibrierungsgesamtverbrauch einschließlich Preflight:
  854.126 CPU-Sekunden, davon Worker 716.336,
  Supervisor 5.013, Hilfsarbeit 132.777.
  Keine Ryzen-ETA aus diesen Cloudzahlen ableiten.
- Echter SIGKILL-Test mit Root672: Worker stoppt nach37 Zielen; Recovery
  sichert diese separat, übernimmt sie nicht als exakte Endergebnisse und
  erhält CPU-Untergrenzen. Wiederaufnahme erfolgreich, keine offenen Konten.
- 332 zusätzliche unabhängige Vertex-Vergleiche auf vollständigen Roots,
  einschließlich des Crashroots: null Abweichungen. Dazu
  747 Fixture-Regressionsvergleiche in der Kalibrierungsmenge.
  Die2490 weiteren Reviewer-Vergleiche bleiben ausdrücklich zugeschrieben.

## Offengelegte Teststeuerungsfehler

Die ersten zwei Crash-Testversuche warteten auf einen Zwischenstand nach5s.
Beide Einzelroots waren unter geringer Last vorher vollständig fertig. Damit
scheiterte die Teststeuerung, ohne dass der Crash ausgelöst wurde. Die beiden
Konten/Logs bleiben im Roharchiv. Der dritte Versuch löste den Abschuss anhand
von mindestens1,5 gemessenen Worker-CPU-Sekunden aus; erst dessen kontrollierter
STOPPED_PARTIAL-Beleg und erfolgreiches Resume gelten als Crashnachweis.
Keine Quelländerung war dafür erforderlich. Die erfolgreichen66 Roots wurden
nicht erneut gerechnet.

## Grenzen und nächster Schritt

Reale Windows-/WSL- und Ryzen-Abnahme steht aus, einschließlich de-DE-Hostuhr,
Hintergrundbetrieb und elf Workern neben C2. Vollständiger OS-/Hostausfall
ungeprüft. Kein wsl --shutdown bei laufendem C2. Live-status.json enthält das
Untergrenzenkennzeichen noch nicht; Statusbefehl und Abschlussreport zeigen es.
Normale Interpreter-Nachlauf- und Crash-Abrechnungslücken bleiben offen benannt.

Dieser Lauf ist eine endliche Integration, kein vollständiger8105-Root-Zensus.
Keine tiefere Kampagne gestartet. Neue Run-ID für den Zielhardwaretest;
historische1.0.0/rc1-Konten wegen geändertem Codefingerprint nicht migrieren.
48 aggregierte CPUh bleiben später die Meldeschwelle gemäß GC-19, kein Zeitstopp.

Code-Fingerprint: `d187340ca9d606ae74ed3bc87d363b62e1b3a62dddd494ab673ac4a709401dbe`.
Rohbelege und ausführbare Teststeuerungen: validation/evidence.tar.gz.
Die Teststeuerungen sind Cloud-Prüfungen, keine Produktionsstarter.
