# K66: 125 Neighbor-Star-Entfernungen – Beweise und Rekonstruktion

Stand 13. September 2026. Das Originalarchiv `data/k66_star125_20260913/k66_star125_export_20260913.zip` besitzt SHA256 `11287fffa90e6700c7fea159d8c9e948e92418ca3b875c3a3e9556ff45bc3be0`. CRC, sämtliche 129 Datei-Hashes, Größen und Archivabdeckung stimmen mit dem enthaltenen Exportmanifest überein. Es enthält 125 CNFs und vier Runden-/Abschlussberichte.

## Ergebnisse

- Alle 125 CNFs syntaktisch geprüft, gemäß Originalgenerator bytegenau rekonstruiert und als UNSAT durch konkrete LRAT-Beweise nachgewiesen.
- 100 Beweise entstehen ausschließlich durch Einheitspropagation der Ausgangs-CNF; 25 mit Glucose4, DRAT-Ausgabe und Umwandlung durch drat-trim in LRAT.
- Alle 125 Beweise bestehen den lokalen C-lrat-check und zusätzlich einen neu implementierten unabhängigen, strengen Prüfer für ausschließlich positive RUP-Hinweise. Kein Beweis verwendet RAT-Schritte. Die Python-Prüfung fordert in jedem Ableitungsschritt einen tatsächlichen Konflikt unter der Negation der neuen Klausel und am Ende eine bewiesene leere Klausel.
- Die 124 Entfernungen aus Runde 1 werden mit voller jeweiliger Anfangsdomäne reproduziert. Der einzige Fall aus Runde 2, `v4_09317/profile_3520.cnf`, wird nach genau den 34 Entfernungen aus Runde 1 dieser Wurzel reproduziert. Entfernungen innerhalb einer Runde werden erst nach ihrer gesamten Rekonstruktion übernommen.
- Aus den so reduzierten Domänen entstehen **alle sieben Hauptlauf-Wurzel-CNFs mit exakt den bereits zertifizierten Hashes**. Damit ist der technische Übergang von diesen 125 Eingaben zu den sieben abgeschlossenen Wurzeln reproduziert.
- Cake ist in dieser Umgebung nicht vorhanden und wurde hier nicht ausgeführt. Das vorbereitete Ryzen-Paket prüft sämtliche Original-CNF-Hashes, die Beweis-Hashes, erneut alle RUP-Schritte, lrat-check und Cake. Erst dessen Ergebnis darf als hier nachgereichte LRAT-plus-Cake-Zertifizierung verbucht werden.

## Wichtiger Checker-Kontrollbefund

Der hier gebaute C-lrat-check akzeptiert den absichtlich falschen Beweis `3 0 1 2 0` auch zur erfüllbaren CNF mit zweimaliger Klausel `(1)`: Er druckt eine Warnung über einen bereits erfüllten Hinweis und anschließend `c VERIFIED`. Exitcode und Marker allein reichen für diese konkrete Prüferquelle daher nicht aus. Die getestete Quellversion ist über ihren SHA256 in `results/k66_star125_20260913/provenance.json` fixiert und mitgeliefert.

Keines der 125 echten lokalen Prüfprotokolle enthält WARNING oder ERROR. Darüber hinaus bestehen alle Beweise den unabhängigen strengen Python-Prüfer; dessen positiver Kontrollfall wird akzeptiert und dessen negativer Kontrollfall verworfen. Der Ryzen-Treiber verwirft jede WARNING/ERROR-Diagnose und verlangt zusätzlich Cake. Dieser Befund sagt nicht, dass die anders gehashte Ryzen-Binärdatei denselben Fehler besitzt; er wird dort durch dieselben Kontrollen abgefangen. Er widerlegt auch nicht automatisch frühere, zusätzlich von Cake bestätigte Ergebnisse.

## Reichweite

Die Zertifikate beweisen zunächst UNSAT **dieser 125 konkreten Star-CNFs**. Der bytegenaue Wiederaufbau mit dem Originalgenerator belegt Eingabeprovenienz und Rundenabhängigkeiten, ersetzt aber keinen unabhängigen Beweis der mathematischen Notwendigkeit des Star-Modells und aller vorgelagerten Profil-/Kapazitätsfilter.

Der bedingte Zusammensetzungsschluss ist klar: Wenn jedes tatsächliche Vorkommen eines Profils eine Belegung seiner Star-CNF induzieren müsste, schließt deren UNSAT dieses Vorkommen aus. Das gilt zunächst für Runde 1 und dann induktiv für Runde 2. Nach Entfernung dieser Profile müsste jedes verbleibende Objekt eine der sieben reduzierten Wurzel-CNFs erfüllen; deren zertifiziertes UNSAT schließt diese Fälle aus. Die Voraussetzungen dieser Abbildung und die vollständige übergeordnete K66-Fallabdeckung bleiben gesondert nachzuweisen.

## Dateien und Reproduktion

`data/k66_star125_20260913/` enthält Original-ZIP, Quellmanifest, Hauptlauf-Wurzelmanifest, Proofmanifest und das ausführbare ZIP-Paket `k66_star125_verify_20260913.pyz`. Letzteres enthält sämtliche 125 LRAT-Beweise (unkomprimiert insgesamt 15.724.318 Bytes), den strengen Prüfer und den Ryzen-Treiber. Die Quellen unter `src/k66_star125_20260913/` dokumentieren Erzeugung und Prüfung; Ergebnis-JSONs unter `results/k66_star125_20260913/` weisen jeden Einzelfall aus.

Das Original-ZIP zunächst in ein Eingabeverzeichnis entpacken. `reconstruct.py` erhält in dieser Reihenfolge Eingabeverzeichnis, `source_manifest.json`, Ergebnisdatei und `root_manifest.json`. Es benötigt NumPy. `unit_audit.py` erhält Eingabeverzeichnis, Beweis-Ausgabeverzeichnis und den Pfad zum aus der beigefügten Quelle gebauten lrat-check. `solve_remaining.py` erhält zusätzlich als drittes und viertes Argument drat-trim und lrat-check; es benötigt python-sat mit Glucose4. `strict_rup.py` erhält Eingabeverzeichnis und das Verzeichnis mit den entpackten Beweisen. Die historischen Rekonstruktionsskripte verwenden Assertions und dürfen nicht mit `python -O` gestartet werden. Der Ryzen-Treiber verwendet explizite Fehlerprüfungen.

## Ryzen-Prüflauf

Der Treiber enthält keine Solveraufrufe und verändert keine ursprünglichen CNFs oder bisherigen Forschungsresultate. Er erzeugt einen neuen Zeitstempelordner unter `neighbor_star_preflight_20260909/certify_star125_20260913/`, prüft nacheinander und schreibt nach jedem erfolgreichen Fall einen Zwischenstand. Positive und negative Kontrollen sind verpflichtend. Die bekannten lrat-check-/Cake-Binärdateien werden gegen die dokumentierten Ryzen-Hashes geprüft. Keine Wallclock-Abbruchgrenze; echte Fehler, weniger als 1 GiB verfügbarem RAM oder weniger als 5 GiB freiem Plattenplatz stoppen die Prüfung. Status nach jeweils zehn Fällen und während laufender externer Prüfungen mindestens alle zehn Minuten mit ETA.

Erwartete Dauer auf dem Ryzen: ungefähr 1–5 Minuten, geschätzt und noch nicht dort gemessen. Kein großer zusätzlicher Ressourcenbedarf zu erwarten: Eingaben 55,68 MiB, Beweise etwa 15 MiB; Checker nacheinander. Der maximale Speicherbedarf von Cake ist hier nicht gemessen. Bei Erfolg lautet der Status `ALL_125_LRAT_AND_CAKE_CERTIFIED`; das Ergebnis-ZIP wird automatisch in die Windows-Downloads kopiert. Ein Fehler erzeugt einen Bericht mit `STOPPED_ERROR` und darf nicht als vollständiger Abschluss interpretiert werden.
