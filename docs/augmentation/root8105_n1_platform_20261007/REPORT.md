# Memetik VI: Plattformanbindung 0.7.0 abgeschlossen, Ryzen-Abnahme als nächster Schritt

Basiscommit: 22b3da3fef6995158f7c3cf9602abb1df52533b2.
Auftrag vom 07.10.2026: Forschungsweg bis zur nächsten Ryzen-Kalibrierung fortführen.
Veröffentlicht wird ein Abnahmekandidat, keine N1-Produktionsfreigabe.

## Erledigter Umfang

Windows-Stopwatch-/Speichersampler plus besitzender Windows-Endabrechner,
Linux-Adapter, kontinuierliche Cgroup-/Host-/Gast-/RSS-/Plattenbeobachtung im
äußeren CLI-Prozess, sitzungsgebundene native Stopübergabe, Endbelegbindung an
CLI-Abschluss und gesondertes echtes Zielhardware-Abnahmeprogramm implementiert.
0.6.0, der wissenschaftliche Encoder, Katalog und CNFs bleiben unverändert.
Details einschließlich Abrechnungsgrenzen in tools/memetik/root8105_n1_runtime_0_7_0/README.md.

Der Adapter besitzt keinen Schalter zur Produktionsfreigabe. Alle N1-Klassenstarts
bleiben durch die ausstehende Zielhardwareabnahme blockiert. Klasse 0 von Root 210
und 6682 bleibt die vorgesehene spätere Forschungskalibrierung. Keine neue
Baumgrößenmessung, keine N1-Klassensuche, kein Rootausschluss, kein Ryzen-Zugriff.

## Ausgeführte Prüfungen

| Gruppe | Bestandene Kontrollen |
| --- | ---: |
| Runtime | 16 |
| Recovery | 11 |
| N1-Integration | 11 |
| Abrechnung | 9 |
| Guard | 18 |
| Preflight | 13 |
| Plattformprotokoll und Ressourcenfehler | 22 |
| Gesamte CLI mit simulierter Windows-Schnittstelle | 4 |
| Summe | 104 |

Die 78 alten Kontrollen wurden gegen die veränderte Laufsteuerung erneut ausgeführt,
weil Manifestbindung, Abrechnung und Startpfad geändert wurden. Der Mathematikkern
wurde nicht erneut erforscht. Keine Wiederholung der 40000er- oder 960er-Messungen.

Neue Kontrollen: Hostidentität und Sequenz, Zeit-/CPU-Rücklauf, NaN, fehlender
Zeitfortschritt, unbekannte/falsche Endabrechnung, veränderte Cgroup-Mitgliedschaft,
fallende Reserve, OOM-Zuwachs/Zählerrücklauf, fehlende Werte, ausdrücklich unbegrenzte
Cgroup; echte Linux-Prozesse für Solver-STOP, Prüfer-pidfd und fremde Prozessidentität.
Ein unabhängiger Prozess läuft weiter. Die äußere Beobachtung liefert Daten während
reiner CPU-Arbeit des inneren Prozesses. SAT/UNSAT, Ergebnisübernahme, Host-/Linux-
Kontensummen und bytegebundene Hostendbelege werden im vollständigen CLI-Pfad geprüft.
Ein fehlerhafter Hostabschluss führt trotz erfolgreichem innerem CLI-Aufruf zu
Exit78; der unbekannte Hostverbrauch bleibt null statt numerisch0.

Sämtliche Windows-förmigen Daten der Cloudtests sind synthetische Fixtures.
Der Windows-PowerShell-Code ist hier nicht ausgeführt und nicht mit einem
PowerShell-Parser geprüft worden. Diese Prüfung ist expliziter Teil des echten
Ryzen-Probes. Keine Cloudmessung wird als Zielhardwarebeleg ausgegeben.

## Entwicklungsbefunde und Grenzen

Beim ersten Aufruf des projektspezifischen Audithelfers fehlte dessen begleitende
requirements-audit.txt im isolierten Arbeitsverzeichnis. Die unveränderte Datei
wurde vom Basiscommit nachgeladen; der Helfer stellte pynauty2.8.8.1 bereit und
bestand seine Kanonisierungs-/Automorphismenkontrollen. python-sat1.9.dev15 und
six1.17.0 wurden gemäß den fixierten Runtime-Anforderungen installiert.

Der native Build aus den fixierten Quellen bestand; drat-trim meldete wie zuvor
eine Compilerwarnung zu getc_unlocked. Echte Kontroll-CNFs und Beweisprüfungen
bestanden. Die Endtests referenzieren die Binärhashes in BUILD.json.

Im Integrationsreview wurde die Ausgabe eines fehlenden Hostendbelegs verschärft:
Der äußere Prozess meldet nun Exit78 statt eines irreführenden CLI-Erfolgs.
Die entsprechende negative Integration ist Teil der vier finalen Tests.
Antwort-/Statusbefehle starten keinen Windows-Helfer, damit 0-Antworten nicht durch
zusätzliche Helferstarts verzögert werden. Bekannte ältere Betriebslücken bleiben
als solche erhalten; es gibt keine stille Ledgerreparatur.

Die sechs finalen Regressionsaufrufe sind in INVOCATIONS.json mit Exitcodes
und wait4-CPU protokolliert. Diese Zahlen sind Teilmessungen, keine vollständige
Abrechnung aller Entwicklungs-/Build-/Uploadarbeit. Die beiden neuen Testprogramme
besitzen geschlossene Ergebnisbelege, aber keine hier behauptete vollständige
Host-/Controller-Endabrechnung ihrer Testhülle.

## Verbleibende tatsächliche Grenze

1. Probe auf dem echten Ryzen unter WSL: Toolverfügbarkeit, PowerShell-Syntax,
   Dateiaustausch, sechs fortschreitende Hostmeldungen, sichtbare Cgroup-/Host-/
   Gastdaten, gültiger Windows-Endbeleg. Mögliche Interop-/Dateisystem-/
   Policy-/Cgroup-Unterschiede müssen anhand dieses Befunds behandelt werden.
2. Dort fixierte native Werkzeuge bauen; kleine echte SAT-/UNSAT-/Budget-/
   Wiederaufnahmekontrollen mit Hostanbindung abnehmen.
3. Erst danach Ressourcen und Startpaket für die beiden freien N1-Klassen
   festlegen. Die Gesamtsuche über220 beziehungsweise8105 ist nicht freigegeben.

Keine OS-Einstellungen ändern und keine laufenden C2-/anderen Nutzerprozesse
stoppen. GC-01/08/15/18/19/20/21/22 gelten am oben angegebenen Basiscommit.
