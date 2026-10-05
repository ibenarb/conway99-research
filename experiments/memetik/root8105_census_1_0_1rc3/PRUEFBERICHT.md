# ROOT8105 Census 1.0.1-rc3: WSL-Testisolierung

## Anlass und Ursache

Am05.10.2026 meldete Ralph im Ryzen-Preflight von rc2 einen AssertionError
im Fall clock-missing. Der synthetische Zensus endete mit sechs fertigen Roots,
aber die erwartete Meldung zur fehlenden PowerShell fehlte. Das Hosthelferlog
zeigte echten Windows-PowerShell-Code und Move-Item-Fehler mit Linux-/tmp-Pfaden.
Ursache: fakebin wurde dem geerbten PATH nur vorangestellt. Der simulierte
wslpath wurde gefunden, powershell.exe aber aus dem Windows-PATH nachgeladen.
Die korrekt in Windows PowerShell ausgeführte gezielte Prozessabfrage ergab
laut Ralph keine Treffer. Ein echter regulärer WSL-Hostuhrtest war das nicht.

Der fehlgeschlagene rc2-Preflight bleibt unverändert erhalten. Seine Windows-
Hosthelfer-CPU ist ohne lesbaren Endbeleg unbekannt; alte Kosten nicht als null
oder als exakt abgeschlossene Gesamtmessung behandeln. Noch keine produktiven
Censusroots auf Ryzen berechnet. Neue Version, neuer Lauf, neue Kennung/Konten.

## Korrektur und Abgrenzung

Nur operations_test.py funktional geändert: Jede simulierte Uhrensituation
bekommt ausschließlich ihren kontrollierten PATH. Der aufrufende Nutzer-PATH
und der echte reguläre Windows-Hostuhrpfad werden nicht geändert.

Regression mit zusätzlichem ausführbarem powershell.exe im geerbten PATH:
Die alte Suchfolge würde es finden; der isolierte Fehltest findet es nicht.
Die Positivfälle finden ausschließlich ihre Attrappen. Alle vier Uhrenszenarien
laufen mit der isolierten Umgebung, die zusätzliche Datei wird nie gestartet
(Startmarker bleibt aus). Die Assertion zum fehlenden Hosthelfer bleibt aktiv.

## Aktuelle eigene Validierung

Vollständiger unveränderter Preflight auf Linux erfolgreich: 21 Betriebschecks
(einschließlich neuer Isolation), sieben Recovery-Prüfgruppen und quick-
Mathematikkontrolle. Ressourcenprüfungen nicht abgesenkt. Scope NOT_WSL.
Konkrete Zahlen, Fingerprint und CPU-Belege stehen in VALIDATION.json;
Rohdaten in validation/rc3_evidence.tar.gz.

Produktionscontroller, Worker, Runtime, Recovery-Test, Windows-Uhrskript,
Preflight-Skript, Kernel, Filter und mathematische Prüfer sind byteidentisch
zu rc2. Deshalb keine erneute66-Root-Integration: Die erfolgreichen rc2-
Unterbrechungs-, Crash-,5478-Count- und332-Vertex-Belege bleiben getrennt unter
validation/rc2_basis erhalten und werden nicht als neue rc3-Rechnung ausgegeben.

## Nächster Schritt und Grenzen

Vollständiges rc3-Paket in neues Verzeichnis; neuer Lauf. Kein Überschreiben
von rc2-Dateien und kein Ändern alter Fingerprints. Zielhardware-Preflight
wiederholen; reale Windows-/WSL-Abnahme weiterhin offen. C2 nicht ändern.
Kein globaler WSL-Neustart und kein automatischer Produktionsstart.
48 aggregierte CPUh bleiben die Meldeschwelle gemäß GC-19, kein Zeitstopp.

Regel GC-21 wurde anhand dieses Fehlers ergänzt. Basis der Änderung ist
Commit6cc39317682c04c287943d07c738d873bf6306a0; rc2-Abnahme be1eabcc258bbf82efe1732121a02387961971ac.
