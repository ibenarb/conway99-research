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

## Tatsächlicher Cloudbefund

Alle sechs Kontrollprogramme endeten mit Exit0. Die neue Gruppe bestand13,
die unveränderten Regressionen18/9/16/11/11 Kontrollen. Die beiden echten CNFs
wurden zur Identitätsprüfung initialisiert und exakt gegen den fixierten Encoder
regeneriert. Ihre Versuchsverzeichnisse blieben leer; es gab keinen Klassensuchlauf.

Die gemessene sichtbare Cgroup-Grenze betrug8589934592Bytes (8GiB), cpu.max
800000/100000. Dies beschreibt die sichtbare Containerhülle, nicht physischen
Windows-Hostspeicher oder eine Ryzen-Konfiguration. Kernel6.18.44, WSL=false;
Windows-Hostzeit und Host-Endkonto fehlen ausdrücklich. Die genauen dynamischen
Messwerte stehen in den erhaltenen Berichten. Keine Simulationsmessung wird als
physischer Hostbeleg ausgewiesen. Es gab keine zusätzliche Forschungsrechnung.

## Transport der Evidenz

Die GitHub-Schnittstelle nahm den vollständigen Archivblob nicht an. Daher liegt
dasselbe EVIDENCE.tar.xz bytegetreu in nummerierten Teilen vor. EVIDENCE_PARTS.json
enthält Reihenfolge, Teilhashes und Gesamthash. Zusammensetzen im Belegverzeichnis:

```sh
cat EVIDENCE.tar.xz.part* > EVIDENCE.tar.xz
```

Danach Gesamthash prüfen und mit `tar -xJf EVIDENCE.tar.xz` entpacken.
Dieser Transportwechsel verändert keine Testbelege oder Testresultate.
