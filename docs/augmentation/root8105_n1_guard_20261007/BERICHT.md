# N1 Runtime 0.5.0: Gesamtbudget und Ressourcenüberwachung

Basiscommit: 9d8e1dd2859c4c52749b8631fb90cf2f3c389327.
Abgegrenztes Arbeitspaket vom 07.10.2026; eigene Quellen, keine Migration älterer
Läufe. Cloud-Prototyp, keine Produktions-/Ryzen-Freigabe. Keine ROOT8105-Suche.
Die Modell-, Worker- und Beweisprüferquellen bleiben unverändert.

## Explizite Aktivierung

init behält --budget für native_children_cpu_seconds. Die neue Schutzschicht wird
nur mit allen vier zusätzlichen Angaben aktiviert:
--total-budget, --max-rss-bytes, --min-free-bytes, --min-available-bytes.
Der erste Wert bezeichnet positive endliche CPU-Sekunden, die drei übrigen
positive ganze Bytes. Es werden keine Zielhardwaregrenzen geraten. Unvollständige
Angaben werden abgewiesen. Ohne diese Angaben bleibt die ausdrücklich ungeschützte
alte Kontrollschnittstelle verfügbar; guard=null steht dann im Manifest.
Ein geschützter Lauf muss über die beobachtete CLI initialisiert werden.

## Zwei Budgetkonten

Das native Budget bleibt unverändert. Die neue Gesamtbudgeteinheit lautet
recorded_cli_aggregate_cpu_lower_bound_seconds. Sie umfasst die belegten inneren
CLI-Prozesse einschließlich ihrer abgeholten Kindprozesse, die dokumentierten
Beobachter-Untergrenzen und laufende Messungen. Such-/Prüferzeiten werden nicht
noch einmal zur bereits inklusiven Endmessung addiert. Bereits abgeschlossene
CLI-Aufrufe bleiben über Wiederaufnahme hinweg verbucht, auch Initialisierung,
Abfragen, Antworten und Recovery.

Die Messgrenzen von 0.4.0 bleiben bestehen: letzter Beobachternachlauf, ungemessene
Hostarbeit und Aufrufe außerhalb der CLI sind nicht vollständig endabgerechnet.
Das neue Budget ist deshalb keine exakte Obergrenze für die gesamte physische
Host-CPU. Die geprüfte Teilmenge und der Charakter als Untergrenze stehen im
Status. Vorherige Abrechnungslücken werden weder geschlossen noch als null behandelt.

Für laufende innere Prozesse werden eigene CPU und bereits abgeholte Kind-CPU
zuerst gelesen, danach die noch lesbare native Kindidentität. Ein inzwischen
abgeholtes Kind wird damit nicht zugleich als lebend und abgeschlossen addiert;
der Übergang kann kurzfristig unterzählen. PID, Startidentität, Boot und Namespace
werden geprüft. Bereits beobachtete Untergrenzen werden nicht zurückgesetzt.
Verschwindet ein äußerer Beobachter nach der ersten Dateiabfrage, wird der inzwischen
möglicherweise geschriebene Endbeleg nochmals geprüft, bevor eine Lücke gemeldet wird.

Ein erreichter Wert erzeugt genau eine offene Anfrage je Budgetkonto. Die Meldung
nennt Run-ID, Einheit, Verbrauch, Budget und Anfrage-ID, gefolgt von
`time limit reached. ETA unknown. Extend [seconds] ?`.
Die Anfrage liegt dauerhaft in der maßgeblichen Zustandsgeneration und im Log.
Status: RUNNING_AWAITING_TIME_EXTENSION, sofern kein echter Stopp ansteht.

reply akzeptiert --scope native oder --scope total; Standard bleibt native.
Anfrage-ID und Antwort-ID sind gebunden. 0 beendet den betroffenen Lauf kontrolliert,
n addiert genau n Sekunden zum bisherigen Budget des bezeichneten Kontos.
Eine native Verlängerung erhöht das Gesamtbudget nicht stillschweigend. Bei dessen
Erreichen wird separat gefragt, ohne einen zeitbedingten Stopp auszulösen.
Keine Antwort, EOF, ungültige/veraltete Antwort oder doppelte Zustellung pausiert
oder drosselt die Rechnung. Ist eine Verlängerung bereits verbraucht, folgt eine
neue Anfrage. Regulärer mathematischer Abschluss schließt offene Anfragen; kein
Warten auf eine dann gegenstandslose Entscheidung.

Annahme der Antwort, Budgetänderung und Antwortverlauf werden in derselben
Zustandsgeneration festgehalten. Nach einem Absturz werden Originalbudgets plus
bestätigte Antworten gegen beide gespeicherten Budgets geprüft. Eine ohne
passenden Antwortverlauf erhöhte Budgetzahl wird auch mit neu berechnetem
Dateiumschlag zurückgewiesen. Die Belege sind Integritätsschutz, keine Signatur
gegen einen Akteur mit vollständigem Schreibzugriff auf sämtliche Quellen/Belege.

## Ressourcen und kontrollierte Abwicklung

Die Schutzschicht liest freien, für den Benutzer verfügbaren Plattenplatz über
statvfs, MemAvailable des Linux-Gasts und den RSS-Summenwert des beobachteten
Laufs: äußerer Beobachter, innerer Supervisor und bekannter nativer Kindprozess.
RSS ist eine angenäherte, möglicherweise gemeinsam genutzte Seiten mehrfach
zählende Größe, kein exakter physischer Gesamtbedarf. Unbekannte/fehlerhafte
Pflichtmessungen werden nicht als gesunde Ressource ausgelegt.

DISK_RESERVE, MEMORY_AVAILABLE, RUN_RSS und MONITOR_ERROR sind getrennte Ursachen
mit Messwerten, Zeitpunkt und Runbezug. Sie betreffen nur diesen Lauf.
Suchworker erhalten das kooperative STOP-Signal über ihre Datei; der Checker
wird über den vorhandenen SIGTERM-Pfad beendet. Es gibt keine zeitabhängige
SIGKILL-Eskalation. Auf reguläres Prozessende und wait4-Endabrechnung wird gewartet.
Der Ressourcenstopp selbst beweist kein SAT/UNSAT; result_status bleibt getrennt.
Nicht entschiedene Aufgaben tragen operativ RESOURCE_STOPPED.

Vor dem Start wird 1 MiB mit posix_fallocate als eigene emergency.reserve angelegt
und synchronisiert. Bei Schutzstopp wird nur diese Reserve freigegeben, damit
Raum für Abwicklung verbleibt. Ergebnisse, Teilbeweise und Checkpoints werden
nicht zur Platzgewinnung gelöscht. Die Reserve ist keine Garantie gegen beliebig
schnelles externes Auffüllen, Gerätefehler oder verzögertes kooperatives Beenden.

Explizites resume prüft Ressourcen erneut und legt eine neue Reserve an. Solange
eine Gefahr besteht, wird kein neuer nativer Versuch angelegt. Die Ereignishistorie
bleibt erhalten. Ein gestoppter Checker setzt mit dem unveränderten versiegelten
Originalbeweis fort; die Suche wird nicht wiederholt. Ein unabhängiger laufender
Worker wird vom Schutzstopp dieses Runs nicht angehalten.

## Aufwand und Überwachungsfenster

Während nativer Wartephasen und vor dem Übergang zum Checker wird höchstens alle
0,25 Sekunden ein neuer Guard-Snapshot erzeugt. Es werden je Tick höchstens
32 neue Kontenverzeichnisse betrachtet, bis zu 32 bekannte aktive Konten aktualisiert
und der aktuelle Run gesondert gemessen. Geschlossene Konten werden innerhalb
einer Sitzung zwischengespeichert. Keine rekursive Bestandsgrößenmessung im Guard.
Letzter vollständiger Durchlauf, Anzahl bekannter Konten und Snapshotzeit werden
angezeigt. Änderungen an alten, bereits validierten Belegen werden nicht bei jedem
Tick vollständig erneut geprüft; die vorhandene End-/Wiederanlaufprüfung bleibt.

Die anfängliche Kontenaufnahme erfolgt vor einem neuen nativen Start. Nachlauf,
CLI-Endauswertung und bisherige Antwort-/Zustandshistorie sind damit noch nicht
vollständig auf konstanten Aufwand umgestellt. Bei sehr vielen Aufrufen kann die
Kontenerkennung verzögert sein; dies ist keine sofortige harte Kostenobergrenze.

Es gibt keine lückenlose asynchrone RAM-Überwachung während sämtlicher Python-
Import-, Modellaufbau- und Zeugenvalidierungsphasen. MemAvailable ist kein Beleg
für Windows- oder Containerreserve. Cgroup-Grenzen, Speicher-OOM-Vermeidung,
Windows-Hostuhr und reale WSL-Zielhardware sind noch nicht abgenommen. Diese
Grenzen sind Gründe gegen eine Produktionsfreigabe, keine versteckten Timeouts.

## Abnahme und Reproduktion

65 finale Kontrollen: 18 Guard, 9 Abrechnung, 16 Laufsteuerung, 11 Recovery,
11 unabhängige N1-Kontrollen. Die Guardfälle umfassen zwei offene Budgetkonten,
Weiterarbeit ohne Antwort, scope-getrennte/doppelte Verlängerungen, erneutes
Budgetende, 0-Abbruch, Wiederaufnahme, einen echten Prozessabbruch unmittelbar
nach Antwort-Commit, unerklärte Budgetänderung, drei Ressourcenstopps, fehlenden
Sensor, unabhängigen parallel laufenden Worker, Checkerfortsetzung, normalen
Abschluss trotz offener Anfrage und einen begrenzten Scan mit 257 Fixturekonten.
Ein deterministischer Regressionstest prüft den normalen Beobachter-Endübergang.
Fixturekonten sind ausdrücklich synthetische Zahlen, keine behauptete Rechenzeit.

Die Sensor-Gefahrentests benötigen gleichzeitig ALLOW_TEST_FAULTS im Run und
N1_TEST_RESOURCES in der Testumgebung. Sie erschöpfen keinen echten RAM und keine
Platte. Ein Abschlussfall verwendet die echten Linux-Sensoren. Reale native
Prozesse bearbeiten ausschließlich kleine Kontrollformeln beziehungsweise die
synthetische Pigeonhole-Formel; keine 99er-Klassensuche.

AGENTS-Auditinterpreter, requirements-n1.txt und build.py gelten wie zuvor.
Die fünf test_*.py erhalten --output (neues Verzeichnis), --worker und --checker.
Quell-ZIP enthält das gesamte neue Versionsverzeichnis und den unveränderten
Encoder am erwarteten relativen Pfad. Umfangreiche Evidenz liegt separat in Git.
Die m=2-Positivkontrolle und Katalogbelege von Root210/6682 werden nicht zu einer
neuen SRG-/Rootausschlussaussage erweitert. Katalogprüfung bleibt getrennt.

Regeln: GC-01/03/04/08/15/18/19/20/22 am oben genannten Basiscommit.
OS-Referenzen: https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html und
https://man7.org/linux/man-pages/man3/statvfs.3.html.

Nächstes begrenztes Paket: integrierter Start-Preflight mit verpflichtender
Katalog-/Guardprüfung und expliziter Prüfung der noch fehlenden Host-/Cgroup-
Voraussetzungen. Keine automatische Ausführung auf dem Ryzen.
