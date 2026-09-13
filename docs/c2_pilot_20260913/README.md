# C2-Baseline-Pilot 1.0.0

Stand: 13. September 2026. Referenzencoder: Commit 578ce74871bbdd9d8a53444fe69c1f16d355da47. Dieser Commit stellt den Pilot bereit; er enthält kein Ergebnis einer tatsächlichen C2-Suche.

## Messfrage und Umfang

Vier CaDiCaL-Seeds 0,1,2,3 bearbeiten dieselbe vollständige CNF mit LRAT-Ausgabe, je höchstens 7200 Sekunden Suchzeit. Vier Prozesse auf vier Kernen, keine Fallpartition. Gemessen werden Laufzeit, Solverstatistiken und Beweiswachstum; die vollständigen Logs bleiben erhalten. Der Matchingvergleich entfällt wegen byteidentischer CNFs.

Ein einzelner gültiger UNSAT-Beweis genügt für die gesamte Referenz-CNF. Vier Timeouts schließen keinen mathematischen Teilfall aus. Ein Erfolg wird nicht aus Laufzeit oder Solvermeldung abgeleitet. Die Rückübertragung von CNF-UNSAT auf den Involutionsausschluss verwendet weiterhin den dokumentierten Encoderbeweis und den zitierten Fixpunktsatz.

## Vor Ort bestätigte Eingaben

- CNF: `/home/rb/conway99_workspace/c2_reference_v1/prepare_20260913_160812_780017/k14/baseline.cnf`
- CNF-SHA256: `f9d6011c5e6eb8a0fab971fa324d159e94b8bc4526b7b17dc31ee55aee1c25ba`
- CaDiCaL: `/home/rb/.local/bin/cadical`, Version 2.2.1; die konkrete Binärprüfsumme wird beim Start gespeichert.
- Cake: `/home/rb/conway99_workspace/o3_reconciliation_runs/k66_v4_cert_20260908_231256_132359/tools/cake_lpr`
- Cake-SHA256: `e63d772e463265d26ace5f52125506024126b36c4a34901e2ed61c4378742d0a`
- Nutzer meldete 24 CPU-Threads, MemAvailable 48363840 kB, SwapFree 16777216 kB und 281.7 GiB freien Plattenplatz. Beim Lauf werden Ressourcen erneut gemessen.

## Ablauf

`pilot.py` startet einen abgekoppelten Controller in einem neuen datierten Verzeichnis unter `~/conway99_workspace/c2_reference_v1/`. Das Schließen des Terminalfensters beendet den Controller nicht. Ein Rechner- oder WSL-Shutdown unterbricht den Lauf; es gibt keine automatische Fortsetzung des internen Solverzustands.

Der Controller prüft die gepinnten Eingabe- und Prüferbytes, kopiert die CNF in das Laufverzeichnis und protokolliert Versionen, Hashes, Befehle und PIDs. Vor Produktion läuft genau ein kleiner UNSAT-LRAT-Positivtest mit dem wirklichen CaDiCaL und Cake. Derselbe Beweis muss gegen eine erfüllbare Kontroll-CNF abgelehnt werden. Schlägt dieser Verbindungstest fehl, startet keine Produktionssuche.

Die vier Seeds laufen mit `--lrat --no-binary --seed=N -t 7200`. Status wird alle zwei Sekunden atomar gespeichert und mindestens alle zehn Minuten samt verbleibendem Suchbudget ausgegeben. Rohlogs und LRAT-Dateien bleiben bestehen. Keine Änderung an anderen Forschungsprozessen.

Nach einer terminalen Solverantwort werden die übrigen eigenen Prozesse beendet, um Platz für die Prüfung zu schaffen. UNSAT wird nur bei Exit 20 und passender Statuszeile zur Prüfung angenommen. Cake muss Exit 0, ausschließlich `s VERIFIED UNSAT` auf stdout und leeres stderr liefern. CNF und Proof werden an ihre Hashes gebunden. SAT wird durch den gepinnten Referenz-Graphprüfer kontrolliert, einschließlich sämtlicher gemeinsamer Nachbarzahlen; fehlende Modellbits werden nicht ergänzt.

## Ressourcen und Zeitrahmen

Suchbudget: rund zwei Stunden Wandzeit bzw. maximal acht Kernstunden, zuzüglich kurzer Startkontrolle. Die abschließende Cake-Prüfung hat keine feste Zeitgrenze; ihr Zeitbedarf ist vor einem echten Proof unbekannt. Bei einem frühen Ergebnis kann die Suche entsprechend früher enden.

Alle zwei Sekunden werden verfügbarer RAM und freier Plattenplatz geprüft. Unter 75 GiB freiem Plattenplatz oder unter 2 GiB MemAvailable werden nur eigene aktive Prozesse beendet; dies ist kein Ausschluss. Cake läuft nach dem Stoppen der Solver allein, um den verfügbaren Speicher nutzen zu können. Es gibt keine starre kleine Heap- oder Proofdateigrenze. Falls Cake selbst eine Allokationsgrenze meldet, bleibt das Ergebnis ungeprüft und der Fehler wird gespeichert.

CaDiCaL erhält das explizite Pilot-Zeitbudget. Ein zusätzlicher Watchdog greift erst nach Budget plus 60 Sekunden ein. Dies ist kein Endgame ohne Zeitlimit. Beweise und Teilbeweise werden nicht automatisch gelöscht; die Plattenreserve bleibt deshalb entscheidend.

## Ergebnisdateien

- `driver.log`: Startkontrollen, Statusmeldungen und Abschluss.
- `inputs.json`: Input-/Toolhashes und Befehlsparameter.
- `jobs.json`, `seed_N/result.json`: Versuchszustände; endgültige Einzelzustände stehen in den Einzeldateien und in summary.json.
- `status.json`: aktueller atomarer Stand oder Abschluss/Fehlermeldung.
- `summary.json`: Endergebnis aller Versuche.
- `seed_N/solver.log`, `proof.lrat`: Originalausgaben.
- `seed_N/cake.stdout`, `cake.stderr`: Prüferausgaben, soweit geprüft.

Mögliche Abschlüsse: C2_UNSAT_CERTIFIED (zertifizierte CNF), C2_GRAPH_FOUND (direkt geprüfter Graph), PILOT_OPEN (kein Abschluss, Gründe separat), PILOT_ERROR oder CONTROLLER_FAILED. Keine dieser Bezeichnungen ersetzt den jeweils angegebenen mathematischen Scope. Insbesondere ist PILOT_OPEN kein Beweis gegen C2.

## Hier ausgeführte Tests

`test_controller.py` prüft strikte Akzeptanzregeln, Statusklassifikation, Prozessbeendigung und die vollständigen Abläufe für Timeout, simulierte UNSAT-Akzeptanz und simulierte Prüferablehnung. Dafür werden ausdrücklich Fake-Solver und Fake-Prüfer benutzt. Diese Tests liefern keine LRAT-Verifikation und keinen Conway99-Befund. Die tatsächliche Werkzeugverbindung wird automatisch erst auf dem Ryzen geprüft.

Das flache ZIP enthält Controller, unveränderten Referenz-Graphprüfer, Testskript, README und Dateimanifest. Hashprüfung vor dem Entpacken ist Bestandteil des Startbefehls. Es müssen keine neuen Programme installiert werden.
