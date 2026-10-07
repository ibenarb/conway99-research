# N1-Bindung und Zeugenprüfung 0.3.0: Abschluss

Basis: 88f762419e5668754f0ebe7c30141f106f3a051c.
Paketumfang: N1-Eingabebindung und unabhängige dekodierte SAT-Zeugenprüfung, nur kleine Kontrollen.
Keine freie 99er-Klasse gelöst, kein Root ausgeschlossen, keine Produktionsfreigabe.

Ergebnis: finale N1-Suite 11/11, Laufsteuerung 16/16, Recovery 11/11 – zusammen 38 Prüfungen bestanden. Die drei finalen gehashten Ergebnisbelege liegen separat bei. TEST_EVIDENCE.tar.xz erhält auch die vorherigen erfolgreichen Teststände vor Korrekturen an Testaussage und Testabsicherung.

## Neue Funktionen

- Fixierter vorhandener Encoder erzeugt CNF und Binding. Init prüft die exakte Regeneration; CNF, Descriptor und Kantenabbildung sind anschließend gehasht an den Lauf gebunden.
- Separater Standardbibliotheksprüfer rekonstruiert Labels und feste Kanten und kontrolliert die dekodierte Matrix direkt an den N1-Gleichungen. Kein Aufruf von encode/decode/check/fixed_edges des Encoders.
- Neuer Status SAT_N1_VERIFIED erst nach CNF- und direkter Matrixprüfung; gehashter Zeugenbeleg. N1-SAT bleibt eine Relaxationslösung, kein SRG-Fund.
- Wiederverwendung und Recovery prüfen den Zeugen unabhängig nach. Bei künstlichem Supervisorabbruch vor Zeugenpersistierung werden der gesicherte Solverbeleg übernommen und Matrix/Prüfung im Recoverybericht abgelegt.

## Konkrete Kontrollen

Bekannte 3x3-Rookgeometrie mit tatsächlicher Randadjazenz; unabhängige Sollmatrix. Native CaDiCaL-Suche auf dem kleinen N1-Modell erfolgreich. Vier freie Kantenbelegungen erschöpfend verglichen, genau eine gültig. Falsche Matrizen, Zuordnungen, Bindungen, CNFs und unvollständige Belegungen abgewiesen. Keine Aussage über Suchhärte der 99er-Fälle.

Die Katalogbezeichnungen root_id/class_id sind an die Taskannahmen gebunden, aber ihre historische Katalogzugehörigkeit ist noch nicht geprüft. catalog_identity_checked=false bleibt erhalten. Dieses Paket ersetzt keine Matchingabdeckungsprüfung und behauptet keinen Rootausschluss.

## Testkorrekturen und Umgebung

Der erste N1-Testlauf bestand, enthielt aber eine unwirksame assert-Importkontrolle innerhalb eines mit Python -O gestarteten Unterprozesses. Bei Durchsicht korrigiert: ausdrücklicher if/raise-Zweig. Die vollständige N1-Suite besteht auch danach. Originaltestquelle und beide Ergebnisbestände erhalten.

Die übernommene generische Testsuite enthielt noch die pauschale Einschränkung „No N1 decoded witness integration“. Diese Ergebnisbeschreibung wurde auf den tatsächlichen Umfang dieser allgemeinen CNF-Kontrollen präzisiert; die N1-Prüfung erfolgt in test_n1.py. Suite anschließend erneut bestanden. Vorherige Testquelle und Ergebnisse ebenfalls erhalten.

Der vorgeschriebene Audit-Helfer fand anfangs kein pynauty, installierte die fixierte Version 2.8.8.1 in der isolierten Cloudumgebung und bestand seine Kanonisierungs-/Automorphismenkontrollen. Für den bestehenden Encoder python-sat1.9.dev15 ergänzt (six1.17.0). Keine Solverrechnung außerhalb der kleinen Kontrollen. Keine Änderungen auf Ryzen/Office.

Quellen/Belege und vollständiges ZIP sind durch PROVENANCE.json gebunden. Der vorhandene Encoder ist unverändert und wird im ZIP für dessen relative Importstruktur mitgeführt; die Git-Originaldatei wird nicht geändert. Alte Runtimeversionen und Forschungsprovenienzen bleiben erhalten.

## Offene Grenze

Kein Hardware-/Produktionsnachweis, keine vollständige Kampagnengesamtabrechnung, keine realen 99er-SAT-Zeugen. Die historische CPU-Lücke bleibt unverändert. Nächster einzelner Schritt: die beiden archivierten Klasse-0-Inputs von Root 210 und 6682 gegen Root-/Matchingkatalog und Bindung prüfen, ohne Suchstart.
