# N1 Runtime 0.6.0: verpflichtender Start-Preflight

Basiscommit: 404007de5f1d957ee670c24877d4c9d1876389e8.
Abgegrenztes Paket vom 07.10.2026: Startprüfung implementieren, mit kleinen
Kontrollrechnungen und beiden vorhandenen Klasse-0-Eingaben prüfen und archivieren.
Keine neue N1-Klassensuche, kein Ryzen-Start, keine Migration alter Laufverzeichnisse.

## Neue Startgrenze

Jedes `run` und `resume` prüft den aktuellen Zustand vor einem nativen Versuch.
Identitäten, unveränderte Quellen, Eingaben, native Endkonten und Wiederanlaufzustand
werden erneut geprüft. Bereits bestehende Kontenlücken bleiben Startfehler.
Ein gespeicherter PASS-Bericht ist kein Starttoken. Ein frei ergänztes
`production_approved`-Feld erteilt keine Freigabe.

`init --profile control` ist der Standard für kleine Kontrollen: höchstens 8 MiB,
1000 Variablen und 20000 Klauseln, mit geprüfter DIMACS-Zählung und Literalgrenzen.
Eine beigefügte N1-Bindung muss eine m=2-Kontrollbindung sein. Die beiden echten
m=7-Klasseneingaben können dadurch nicht über das Kontrollprofil gestartet werden.
Diese Umfangsgrenze ist keine garantierte Laufzeitgrenze kleiner SAT-Probleme.

`init --profile n1-production --catalog CATALOG_RECEIPT.json` bereitet einen
prüfbaren Lauf vor; Initialisierung bedeutet ausdrücklich keine Startfreigabe.
Für Produktion sind die unveränderte Katalogquittung, exakte CNF-/Bindungshashes,
Root210 oder6682/Klasse0, vollständige Guardangaben und beobachtete CLI-Historie
Pflicht. Der Beleg vom Commit9a02918f46b2c7c5af2f36da3445233b7382c6b0 ist fixiert:
SHA256 bccafba36574c677c65d8f2e744310e2c85ce95cd2494c16a9ef667732f8e8e5.
Der Preflight wiederholt keine Katalogenumeration; er bindet die geprüften Bytes.

Produktionsstarts bleiben in0.6.0 grundsätzlich BLOCKED: Windows-Hostuhradapter,
Host-Endabrechnung, durchgängige Cgroup-Guardanbindung und Zielhardwareabnahme
fehlen. Dies sind fehlende ausführbare Fähigkeiten, keine per Manifest editierbaren
Freigabeschalter. Die Cloud ist zudem kein beobachtetes WSL-Zielsystem.
Eine spätere Freigabe braucht Implementierung und gesonderte Abnahme.

`python runtime.py preflight RUN` gibt einen aktuellen JSON-Bericht aus und startet
keinen Solver. Exit0 bedeutet erfolgreiche Berichterstellung; `allowed` und
`blockers` müssen ausgewertet werden. Die beobachtete CLI legt ihren eigenen
Abrechnungsbeleg im Geschwisterverzeichnis RUN.accounts ab. Die reine Inspektion
ändert keine wissenschaftlichen Run-Dateien. `run`/`resume` speichern einen neuen
Preflight-Beleg unter RUN/preflights und geben bei Sperre einen Fehlerstatus zurück;
sie verändern dabei keine vorhandenen Ergebnisse oder Versuchsgenerationen.
Frühere Identitäts-/Kontenfehler können schon vor dieser Berichtserstellung abbrechen.

## Sichtbare Umgebung

Der Preflight liest Cgroup-v2-Mitgliedschaft und Mountabbildung aus /proc,
berücksichtigt sichtbare Vorfahren sowie memory.max/current/high, cpu.max und
memory.events. Pfadüberschreitungen und fehlende Blattzähler werden abgewiesen.
Die engste sichtbare Grenze und der kleinste sichtbare Rest werden ausgewiesen.
Verdeckte Vorfahren sind ausdrücklich nicht verifiziert. Keine OS-/Cgroup-Grenze
wird verändert. cpu.max ist eine Durchsatzquote und kein Ablaufzeitlimit.
Die Momentaufnahme ersetzt keine kontinuierliche Überwachung; memory.high ist
keine zugesicherte harte Speichergrenze. Gastuhren bleiben von Hostuhren getrennt.
Referenz: https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html

## Abnahme und Reproduktion

78 bestandene Cloud-Kontrollen: 13 neue Preflight-, 18 Guard-, 9 Abrechnungs-,
16 Laufsteuerungs-, 11 Recovery- und 11 N1-Kontrollen. Beide echten Klasse-0-
Eingaben bestehen die Katalogbindung; run und resume bleiben vor Versuchserzeugung
gesperrt. Gefälschter PASS, Profilabstufung, falsche Bindung, veränderter Katalog,
fehlender Guard und fehlerhafte Cgroup-Fixtures sind erfasst. Native Sucharbeit
betrifft ausschließlich kleine Kontrollformeln; keine Suche in den beiden N1-Klassen.

AGENTS-Auditinterpreter und requirements-n1.txt verwenden. build.py baut die
unveränderten fixierten nativen Quellen. Alle sechs test_*.py erhalten --output
(neues Verzeichnis), --worker und --checker. test_preflight.py benötigt zusätzlich
das bestehende CLASSES.tar.xz unter docs/augmentation/root8105_n1_20261006 im
Repository. Das Quell-ZIP enthält sämtliche Versionsquellen, den unveränderten
Encoder sowie Katalogquittung und Bindungen; das große Eingabearchiv bleibt am
bestehenden Repositorypfad. Vollständige neue Kontrollbelege: EVIDENCE.tar.xz.

Regeln GC-01/03/04/08/15/18/19/20/22 am genannten Basiscommit. Keine neue
mathematische Aussage, keine ETA und keine neue Zielhardware-Ressourcenplanung.
Nächstes eigenständiges Paket: fehlende Host-/Cgroup-Anbindung implementieren und
isoliert prüfen; eine reale Zielhardwareabnahme bleibt ein gesonderter Schritt.

## Übernommener Vertrag aus0.5.0

Die folgende technische Beschreibung bleibt gültig, mit der zusätzlichen
verpflichtenden Profil-/Preflightgrenze von0.6.0. Ungeschützte Aufrufe sind nur im
beschränkten Kontrollprofil zulässig.

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

## Transport der Evidenz

Die GitHub-Schnittstelle nahm den vollständigen Archivblob nicht an. Daher liegt
dasselbe EVIDENCE.tar.xz bytegetreu in nummerierten Teilen vor. EVIDENCE_PARTS.json
enthält Reihenfolge, Teilhashes und Gesamthash. Zusammensetzen im Belegverzeichnis:

```sh
cat EVIDENCE.tar.xz.part* > EVIDENCE.tar.xz
```

Danach Gesamthash prüfen und mit `tar -xJf EVIDENCE.tar.xz` entpacken.
Dieser Transportwechsel verändert keine Testbelege oder Testresultate.
