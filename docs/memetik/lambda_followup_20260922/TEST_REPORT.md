# Prüfbericht – lambda_followup_1_0_0

Stand: 22.09.2026. Umsetzung des angenommenen 121-CPU-h-Vorschlags.

## Ausgeführt

- Python-Syntaxprüfung aller neuen Module.
- Mathematische PC-Kontrollen: Differentialprüfung über 20 Episoden
  (Diagnose-Perturbationslänge zwei), identische Zugfolgen, RNG, Population,
  Kinder, Bestgraph und Epoche bei abgeschaltetem cycle3.
- Deterministische Unterbrechung vor Adoption und mitten im Katalog für PC,
  P und TC; folgende vier Züge/RNG/Bestgraph/Tabu/Restartstatus identisch.
- Reviewer-Zyklus als Mitglied auch des tatsächlichen PC-Engine-Katalogs geprüft;
  W=2116-Zeuge validiert, Inversen geprüft, ungültiger Graph abgewiesen.
- Reale kurze Worker-Sitzungen P und PC unter derselben neuen Steuerung:
  Pause, Wiederaufnahme, Abschluss, Überspringen fertiger Jobs und Verlängerung.
  Alte Kurven/Messpunkte und geschlossene Reserven bleiben erhalten.
- Manipulierte task/result/checkpoint/archive-Dateien und aktive Marker ohne
  finalen Receipt werden abgewiesen.
- Globaler Erfolgspfad für beide Datenwurzeln mit echter srg(9,4,1,2)-Fixture
  und expliziter Testinjektion; Produktionsparameter n=99/k=14 bleiben unverändert.
  Falscher Nullscore und falsche Knotenzahl werden abgewiesen.
- Budgetüberlappung und Hilfsbudgetüberschreitung werden abgewiesen;
  bereits verbrauchte CPU bleibt verbucht.
- Persistente Host-Transportstrecke mit echtem Python-Pipe-Server als Fixture,
  einschließlich geordnetem Abschluss. Kein Windows-Test behauptet.
- Tatsächliche Dateideskriptor-Vererbung: exklusiver Controller-Lock bleibt nach
  Schließen des Elternhandles im Kind bestehen.
- Archivernte-Erfolgspfad: falscher Nullscore abgewiesen, positive explizite
  Rook-Fixture zweimal gesichert und Diagnose beendet.
- Uhren-Entscheidungsregeln mit Fixtures: Gastdrift wird erkannt, zu große
  CPU gegenüber unabhängigen Hostintervallen abgewiesen.
- Hostplatten-Reserve als Negativfixture getestet.

Die mathematische Hauptsuite verbrauchte etwa 217 lokale Prozess-CPU-s,
die abschließende reale Worker-Integration etwa 24,05 Kindprozess-CPU-s.
Dies sind Testkosten in der Codex-Umgebung, keine Ryzen-Kampagne.
Nach Ergänzungen an Fehlerpfaden wurden die betroffenen kurzen Tests gezielt
wiederholt. Die frozen P-/TC-Suchquellen wurden nicht geändert.

## Noch auf dem Ryzen auszuführen

1. Paket-/Originalabgleich und reale VHDX-/RAM-Prüfung.
2. Uhrenprobe mit einem und 18 Workern unter echter Windows-/WSL-Interop.
3. Wiederaufnahmeprobe an einer separaten Kopie des originalen P/W-00-Zustands.
4. Produktionsvorbereitung der 39 Jobs und erst danach Start.

Es wurde kein längerer Suchlauf gestartet. Der 121-CPU-h-Rahmen wird durch feste
Jobbudgets und vier getrennte Hilfskontingente abgebildet. Benutzerseitige
read-only Statusabfragen gehören nicht zu den Suchjobs; Controller, Vorbereitung,
Diagnose, Export und Windows-Hilfsprozess werden gesondert verbucht.

## Implementierungsentscheidungen

Die Archivernte läuft nach den eigentlichen Suchjobs, damit sie den primären
P/PC-Vergleich nicht mit weiterer CPU-/SMT-Last beeinflusst. Die feste Rekordbank
bleibt unverändert. Das ist eine zeitliche Einordnung der vorgesehenen
Zusatzdiagnose, kein neuer Sucharm.

Alle neuen Quelltexte und ihre vollständigen Abhängigkeiten werden im ZIP
ausgeliefert. Die Manifeste und Seedzahlen stammen unverändert aus der
angenommenen Synthese. P/TC-Fortsetzungen benutzen die unveränderten Worker;
PC benutzt dieselbe Workerlogik mit der separat geprüften Katalogerweiterung.
