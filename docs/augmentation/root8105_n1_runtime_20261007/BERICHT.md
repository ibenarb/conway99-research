# N1-Prototyp 0.1.0: Ergebnis dieser Bearbeitungsrunde

Basis: 34c51bd80e040bb705fdb68ae13b1074f9a3c8b5.
Umfang: nativer Worker und minimale Steuerung, echte kleine Prozesskontrollen.
Ergebnis: 16/16 Prüfungen des abschließenden Laufs bestanden. Keine N1-Klassensuche, keine Ryzen-Rechnung, keine Produktionsfreigabe.

## Technischer Befund und Korrektur

Erster Testlauf: SAT und Wiederverwendung bestanden; danach FileNotFoundError bei /proc/9/stat vor Beginn des UNSAT-Kindprozesses. Die Cloud-Prozessnamespace-PID unterscheidet sich vom eingehängten procfs. Die Korrektur gleicht Namespace-Inode und NSpid ab und speichert zusätzlich die procfs-PID und Startidentität. Signale/wait4 verwenden weiterhin ausschließlich das eigene Popen-Kind, Liveproben die verifizierte procfs-Identität. Zweiter Testlauf: 13/13. Abschließend um Import-Abbruch, ungültige Antwort und beschädigten Checkpoint erweitert: 16/16. Alle drei Bestände erhalten.

## Prüfstatus

TEST_RESULTS.json ist das byteidentische gehashte Ergebnis des letzten Testlaufs. TEST_EVIDENCE.tar.xz enthält Rohbelege aller drei Läufe einschließlich des fehlgeschlagenen Laufs. Positive Checks: vollständiger SAT-Zeuge auch mit ungenutzter deklarierter Variable, Wiederverwendung fertiger Arbeit, echter CaDiCaL-DRAT-Beweis und externer drat-trim, disjunkte wait4-Endkonten, Falschbeweis-/Zeugenabwehr, Weiterrechnen bei EOF/offener Anfrage, Prozessbesitz, veraltete Antwort, einmalige Verlängerung trotz doppelter Zustellung, erneutes Budgetende, 0-Abbruch, neuer Versuch mit altem Teilbeweis und kumulativer CPU, Abweisung ungeschlossener Sitzung, Integritätsfehler, 0 während Import, ungültige Antwort und Checkpointhash.

Keine vollständige Abnahme des Vertrags: ausführliche offene Punkte in tools/memetik/root8105_n1_runtime/README.md. Insbesondere Produktionsgesamtabrechnung, N1-Dekodierung, Checker-Recovery, Crash-Reconciliation, persistente Vorgängergenerationen und Windows/WSL fehlen. Diese Runde liefert einen getesteten Kern, keinen freigegebenen Kampagnenrunner.

Build: g++ 13.3.0, -std=c++11 -O2 -Wall -Wextra -pthread; CaDiCaL rel-2.2.1 / 4198d817d0dcde5b1240eefbff70b555b7df2af9, Bibliothek mit upstream configure und make -j4. drat-trim 2e3b2dc0ecf938addbd779d42877b6ed69d9a985 mit gcc -std=c99 -O2, getc_unlocked-Warnung unverändert. Python 3.12.14. build.py bildet diese Befehle nach; die gesamten Drittbibliotheken wurden nicht nochmals über dieses neue Hilfsskript gebaut.

Die kontrollierten Abbruchtests senden als Testentscheidung ausdrücklich 0, nachdem der zu prüfende Zustand erreicht ist. Kein allgemeiner harter Testtimeout, keine Beendigung fremder Prozesse. Keine Aussage über SAT-Suchlaufzeiten auf Zielhardware.

Sicherung: Quellpaket N1_RUNTIME_0.1.0.zip mit vollständigen Quellen, README und Testbelegen; PROVENANCE.json bindet Quell-/Belegdateien und Paket über SHA256. Alte Forschungsbelege und die historische Diagnose-CPU-Lücke unverändert.

Nächstes Paket: Checkerphasen-Recovery und Supervisorzustands-Recovery mit injizierten Prozess-/Speicherfehlern. Keine Zielhardwarefreigabe aus diesen Cloudtests ableiten.
