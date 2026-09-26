# Reproduktion der kleinen Prüfungen

Ausgangspunkt ist der memetik-Commit mit diesem Bericht. Der Archivcommit
`7a00a6a93227eb7eb09980355b4d3129975489fc` muss lokal verfügbar sein
(ein gewöhnlicher Fetch des Reviewbranches genügt). Die Originale werden aus
Git gelesen und nur in einer temporären Kopie umgeschrieben.

Der Einstieg `reproduce.py` verwendet ausschließlich den vorgeschriebenen
Audit-Helfer. Er entpackt das fixierte Datenpaket und den originalen Prüfsatz,
ersetzt lediglich die drei fest codierten Reviewerpfade, führt 04_VERIFY,
analysis, depth2, mitm und supplement aus und schreibt neue Ausgaben in ein
frisches temporäres Verzeichnis. Optional akzeptiert er dessen Zielpfad als
Argument. Es werden keine bestehenden Forschungsdaten überschrieben.

`python3 docs/memetik/lambda_review_20260926/audit/reproduce.py`

Die hier archivierten Ergebnisse entstanden mit denselben Originalskripten
und identischen Pfadersetzungen in Einzelaufrufen. Die zusammenfassende
Replay-Hülle wurde syntaktisch geprüft, nicht nochmals als Gesamtablauf gestartet.
Laufzeitfelder sind maschinenabhängig; analysis_result war byteidentisch,
depth2_result stimmte nach Entfernen von cpu_s vollständig mit dem Review überein.

Zusätzliches supplement.py: volle Kanonisierung aller 1465 Kandidaten,
Abgleich aller 1140 vorhandenen class-Felder, empirische W/F-Paretofront,
neue Klassen relativ zu frühen O-Bestwertkurven, Residuenhistogramme und
Automorphismen der beiden mittels vollständigem state-Hash identifizierten
Rekordgraphen. W allein ist kein eindeutiger Graphbezeichner.

Grenzen: Die Klassenprüfung ist eine eigene Nachrechnung mit derselben
pynauty-Version, keine unabhängige zweite Kanonisierungsimplementierung.
Die Tiefe-2-/MITM-Prüfung nutzt denselben eingefrorenen Operatorcode wie der
Reviewer. Tiefe 3 wurde nur per Code- und Endzählerprüfung nachvollzogen,
nicht vollständig erneut ausgeführt. Keine neue Tiefe-4-Suche enthalten.
PROVENANCE.json dokumentiert Interpreter und eingefrorene Quellhashes.
