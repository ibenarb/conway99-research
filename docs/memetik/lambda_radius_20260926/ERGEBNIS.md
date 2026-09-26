# λ-Radiusprüfung: Ergebnis und Audit, 26.09.2026

**Ergebnis des Ryzen-Laufs:** Beide fixierten Rekordgraphen sind im unveränderten
Apex-/Pivot-Katalog (W,L1)-Minima im Radius vier. Der Lauf meldet vollständige
Abdeckung, keine Verbesserung, keinen Budget- oder Ressourcenabbruch.
Das Rückgabepaket besteht die Prüfung von Quellen, Metadaten, Abrechnungen und
Kontrollzeugen. Die großen SQLite-Datenbanken sind nicht enthalten; der Audit
ist deshalb ausdrücklich keine unabhängige Vollreproduktion der Radiusrechnung.

## Rechenergebnis

| Startgraph | Tiefe-3-Eltern für die abschließende Prüfung | Kindübergänge in Tiefe 4 | Jobs vollständig | Such-CPU-h |
| --- | ---: | ---: | ---: | ---: |
| W2076 / L1=2488 | 195508 | 19873151 | 1528/1528 | 18,17643 |
| W2077 / L1=2436 | 169048 | 16408393 | 1321/1321 | 15,57459 |

Die Kindübergänge sind keine Anzahl verschiedener Endgraphen. Mehrere Pfade
können denselben Graphen erreichen. Die vorherige vollständige Tiefe-3-Prüfung
reproduzierte 526476 bzw. 459185 Kinder ohne Verbesserung und exakt die
Reviewerzähler für die beiden unteren Schichten.

Ende laut Windows-Host-Protokoll: 26.09.2026, **16:48:47 MESZ**.
Host-Walltime: 11185,7587786 s, gerundet **3 h 6 min 26 s**.
Hilfsbudget verbucht: 1,03725 CPU-h; insgesamt **34,78827 CPU-h**.
Alle drei CPU-Grenzen (20/20/2 h) und die Acht-Stunden-Hostgrenze eingehalten.
Die Hilfsabrechnung enthält 20 reservierte CPU-Sekunden für Vorbereitung/Start;
die Gesamtsumme ist daher eine Budgetabrechnung, keine rein gemessene CPU-Summe.

## Was neu geprüft wurde

- Archiv SHA256 `7d35c369e010252c02d5ed2ccf44af3e993618d6b3d134d65c40d6f409f35989`
  stimmt mit dem vom Ryzen übermittelten Wert überein.
- Alle 67 im Paketmanifest aufgeführten Dateien und das Manifest selbst sind
  byteidentisch zum veröffentlichten Startpaket im Commit
  `8ec085cdb8402a6e33dc186ae0302fea4dd542ec`.
- Alle 2934 Jobs mit je einer Sitzung: Task- und Ergebnis-Hashes stimmen,
  Exitcode null, Endstatus DONE. Darunter 2849 Tiefe-4-Jobs, 79 Tiefe-3-Jobs,
  zwei Schichtaufbauten, zwei Vereinigungen, Uhrprobe und mathematische Kontrollen.
- Die ID-Intervalle sind je Arm disjunkt und lückenlos über die gemeldeten
  Schichtgrenzen. Gemeldete Elternzahlen, letzte IDs, Kindzahlen und Endbericht
  stimmen exakt überein. Kein fehlender oder zusätzlicher Job.
- Referenzen auf untere SQLite-Dateien, Fragmente und Vereinigungen passen zu
  den Hashwerten ihrer Receipts. Dies prüft die Referenzkette, nicht die
  tatsächlichen Bytes der ausgelassenen SQLite-Dateien.
- wait4-Sitzungssummen stimmen; jede Sitzung liegt innerhalb ihrer Allokation
  und ist mit ihrem gemeldeten Windows-Host-Intervall vereinbar. Hilfsledger bis
  auf sechs Mikrosekunden Abfragezeitdifferenz reproduziert. Keine offene Sitzung.
- Drei Eingabegraphen samt Kennzahlen, λ-Zulässigkeit und nauty-Klassen erneut
  geprüft. Den bekannten positiven Kontrollpfad W2079→W2076 in vier Zügen
  vollständig nachgespielt: jeder Schritt im Katalog, jeder Graph unabhängig
  bewertet, Endgraph exakt der fixierte W2076.
- Alle Workerlogs sind leer. Die Host-Fehlerausgabe enthält ausschließlich
  724 PowerShell-CLIXML-Fortschrittsobjekte, keine Fehlerobjekte.

Der neue Prüfer musste für diesen letzten Punkt die anfängliche Annahme
„stderr muss leer sein“ korrigieren; außerdem wurden beim Kontrollvergleich
Python-Tupel und JSON-Listen einheitlich serialisiert. Dies waren Fehler bzw.
zu strenge Annahmen des Audit-Hilfsskripts, keine Änderungen am Forschungsprogramm
oder an den Rückgabedaten. Ein erster Shellaufruf nutzte außerdem einen falschen
relativen Uploadpfad; der anschließende Aufruf verwendete den korrekten Pfad.

## Präzise Reichweite

Gemäß der vollständigen Berechnung existiert von diesen beiden Startgraphen
keine strikt (W,L1)-bessere Konfiguration in höchstens vier zulässigen Zügen.
Falls eine solche Konfiguration im Katalog überhaupt erreichbar ist, beträgt
jede entsprechende Weglänge mindestens fünf. Das ist keine Aussage über eine
notwendige Höhe der zwischenzeitlichen W-Verschlechterung, andere Gründer,
andere Operatoren oder die Existenz eines srg(99,14,1,2).

Der Cloud-Audit hat **nicht** 36281544 Kindübergänge erneut berechnet, die
SQLite-Zustandsmengen eingelesen, ihre tatsächlichen Hashes überprüft oder
Host-Zeiten unabhängig gemessen. Er bestätigt die Integrität und innere
Konsistenz des gelieferten kleinen Prüfpakets und den positiven Kontrollzeugen.
Ein vollständiger Datenbankaudit wäre lokal auf dem Ryzen möglich; die
Originaldatenbanken sollen dafür erhalten bleiben.

## Konsequenz

Die vereinbarte begrenzte Untersuchung ist abgeschlossen. Die unveränderte
W-Frontier-Suche bleibt pausiert; kein automatischer Tiefe-5-Lauf, keine
Budgetverlängerung und kein großer unveränderter P-Lauf. Ein größerer Radius
bleibt mathematisch offen. Seine Untersuchung wäre eine neue Entscheidung,
keine Folgerung aus diesem Nullergebnis. Beide Rekordgraphen, die empirische
W/F-Paretofront und alle Originaldaten bleiben erhalten.

## Reproduktion und Artefakte

Originales kompaktes Rückgabearchiv:
[ryzen_lambda_radius_100_20260926_audit.tar.gz](../../../releases/memetik/ryzen_lambda_radius_100_20260926_audit.tar.gz).
`AUDIT.json` enthält das maschinenlesbare Prüfergebnis; `RESULT.json`,
`DEPTH3_VERIFIED.json`, `CALIBRATION.json`, `ledger.json` und `FINGERPRINT.json`
sind unveränderte Kopien aus dem Rückgabearchiv. `EINGANG.json` dokumentiert
Eingangsname, Archividentität und Quellstand.

`audit.py` wird über `tools/memetik/audit_python.py --` mit dem entpackten
Laufverzeichnis und einem neuen Ausgabe-JSON als zwei Argumenten ausgeführt.
Der Lauf benötigt keine SQLite-Dateien, verändert keine Forschungsdaten und
benutzt pynauty 2.8.8.1 in der isolierten Audit-Umgebung.
