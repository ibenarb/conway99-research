# N1-Recovery 0.2.0: Abschluss

Basis: 9a4637f67207f6bc17ab028c93210af5a35ad772.
Abgegrenztes Paket: Wiederaufnahme der Prüferphase und Supervisorzustands-Recovery.
Keine N1-Klassensuche, kein Ryzen-Start. Produktion weiterhin nicht freigegeben.

Ergebnis: 11/11 Recoverytests und 16/16 Regressionen bestanden. Zwei byteidentisch übernommene Ergebnisbelege liegen neben diesem Bericht; TEST_EVIDENCE.tar.xz enthält sämtliche fünf Testbestände (drei fehlgeschlagene Zwischenstände, zwei abschließende erfolgreiche Läufe).

## Nachgewiesen

- Echter Supervisorabbruch nach Such-Endbeleg: lesender Recoveryplan verändert nichts; zweimaliges Apply bucht CPU nicht doppelt; anschließend nur Prüferneustart mit demselben Proofhash.
- Echter Supervisorabbruch nach Prüfer-Endbeleg oder finalem Receipt: zertifiziertes Ergebnis ohne Wiederholung übernommen.
- Echte externe Prüfung plus expliziter Verzögerungsadapter: VERIFIED bei lebendem Prozess wird nicht vorzeitig akzeptiert; 0 beendet den Prüfversuch, frischer Prüfversuch nutzt unveränderte Eingaben.
- Generation vor Cache gesichert, danach Prozessabbruch und beschädigter Cache: Wiederherstellung aus maßgeblicher Generation; alte beschädigte Cachebytes erhalten.
- Injizierter Schreibfehler vor replace: vorherige gültige Datei und Zustand bleiben unverändert.
- Beschädigte maßgebliche Generation: Abweisung ohne zurückgerollte Budget-/Antwortbuchungen.
- wait4 ausgeführt, Endreceipt noch nicht gesichert, dann Prozessabbruch: CPU unbekannt, keine Nullbuchung, kein automatischer Wiederanlauf.
- Echter lebender verwaister Solver: Recovery verweigert Adoption/Doppelstart; Test beendet ausschließlich diesen Solver kooperativ; fehlende Endabrechnung bleibt offen.
- Echter Prozessabbruch nach Antwortcommit vor Cache/Quittung: Verlängerung bei Wiederanlauf weiterhin genau einmal.
- Sämtliche 16 Funktionsprüfungen aus 0.1.0 bestehen im neuen Versionsverzeichnis.

## Gefundene Fehler und Änderungen

1. recovery-regression-01: Statusleser meldete den kurzen regulären Abstand zwischen Generation und Cache als Fehler. Korrektur: Generation ist allein maßgeblich; Cache ist redundant. Nach Testabbruch waren Supervisor und Kind nicht mehr lebend; die letzte Liveprobe von 0,34 CPU-s ist kein vollständiger Endverbrauch. Der Fehlbestand bleibt als unvollständig erhalten, nicht als Null gebucht.
2. recovery-regression-02: Ein alter Regressionstest wollte seinen vorigen In-Memory-Snapshot über eine bereits neuere Generation schreiben. Die neue Sperre wies dies korrekt ab. Test angepasst, indem er für seine absichtliche Statuswiederherstellung die aktuelle Sequenz übernimmt. Kein Produktfehler umgangen.
3. recovery-tests-01: Der abgewiesene Recoveryversuch erzeugte erstmals die Sperrdatei, wodurch der Bestand streng genommen verändert war. Korrektur: Sperrdatei bereits bei init anlegen. Der entsprechende Unverändertheitstest besteht.
4. Ein lokaler Hilfsaufruf zur Rekonstruktion alter Quellfassungen hatte einen JavaScript-Syntaxfehler und wurde korrigiert; dabei lief kein Testprozess und kein Forschungslauf.

Grenzen: Prozess- und gezielte Dateischreibfehler, kein echter Stromausfall/Datenträgerausfall. Ein beschädigter autoritativer Transaktionsstand wird sicher abgewiesen, nicht beliebig rekonstruiert. Fehlende wait4-Werte sind nicht nachträglich berechenbar. Keine N1-Zeugenintegration, keine Hostuhr-/WSL-Abnahme, keine vollständige Supervisor-/Host-Endabrechnung oder Kampagnensteuerung. Details in der README des Versionsverzeichnisses.

Sicherung: vollständiges Quellpaket mit Testbelegen und SHA256-Manifest. Die 0.1.0-Dateien und früheren Provenienzangaben bleiben unverändert.

Nächstes Paket: N1-Inputbindung und unabhängige dekodierte SAT-Zeugenprüfung, ausschließlich mit kleinen Kontrollen; keine Klassenkampagne.
