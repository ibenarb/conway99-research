# ROOT8105 N1 Ryzen-Kalibrierung 0.8.0

Basis d28d8f88cd95119737a58089b963f8e5fbb94b96; Runtimevorgänger
432ce75ed58b1d1ae62fbb0afc8407ae6f0b7bc3 (0.7.2).
Ausschließlich Root210/Klasse0 und Root6682/Klasse0, nacheinander.
Keine automatische 220-/8105-Kampagne. SAT_N1 ist kein vollständiger SRG;
UNSAT einer Klasse ist kein Rootausschluss. Keine Laufzeitprognose möglich.

## Schutz und Freigabe

Die unveränderte Katalogprüfung begrenzt die Fälle und bindet CNF/Matching/Root.
Die neue Freigabeprüfung validiert das hashfixierte Ryzen-Abnahmearchiv, den
Zielrechner RB-CUBE unter WSL, die dort gebauten Binärdateien und die sieben
unveränderten Kern-/Plattformquellen. Der neue Gate-Quelltext selbst ist durch
den Preflight-Code gebunden; dieser wird im Laufmanifest fixiert. Kein frei
editierbares production_approved-Feld verleiht Startberechtigung. Alte Läufe
bleiben unverändert, keine Migration von 0.7.2-Laufverzeichnissen.

Änderungen: preflight.py ersetzt zwei bisher pauschale Sperren durch überprüfte
Abnahmebindung und aktuelle Speicherprüfung. runtime.py hält bei N1-Läufen eine
gemeinsame flock-Sperre über den gesamten Lauf. Mathematik, native Werkzeuge,
Budget-/Antwortmechanismus, Ressourcenmonitor und Endabrechnung unverändert.

## Begründete Speicherhülle statt erfundener Cgroup-Grenze

Ralph meldete MemTotal=49331856 KiB, MemAvailable=48648304 KiB, 16 GiB Swap;
.wslconfig nennt memory=48GB und swap=16GB. Sichtbare Cgroups sind unbegrenzt.
Der neue Gate verlangt aktuell endlichen Gast-RAM aus /proc/meminfo (höchstens
48 GiB), mindestens max_rss+Reserve in Gast und Windows-Host beim Start und
zusätzlich jede vorhandene endliche Cgroup-Grenze samt Headroom. Swap zählt
nicht als RAM. Die vorhandene fortlaufende Beobachtung von Host/Gastreserven,
RSS, Cgroup-Zählern und Platte bleibt aktiv. Keine Änderung an OS-Limits.

Je Fall: höchstens 24 GiB überwachte Prozess-RSS; mindestens 8 GiB frei in
Host und Gast, mindestens 100 GiB freie Platte. Ein einzelner N1-Lauf zur Zeit.
Dies ist kooperative Überwachung, keine neue harte Kernel-Prozessgrenze und
keine Garantie gegen abrupten OOM durch fremde Prozesse. Windows-/Linux-
Endkonten erfassen weiterhin nur die dokumentierte CPU-Untergrenze.

## Zeitbudgets und Bedienung

Je Fall 21600 native CPU-Sekunden (Suche und Prüfung zusammen), 28800 Sekunden
aggregierte verbuchte CPU-Untergrenze. Entscheidungspunkte, keine harten Stopps.
Keine Antwort: derselbe Lauf rechnet weiter. Positive Sekunden verlängern das
bezeichnete Konto; 0 beendet kontrolliert. Kein serialisierter CDCL-Zustand:
späterer Neustart einer offenen CNF beginnt einen neuen Suchversuch und erhält
vorhandene Belege. Antwortkanal: runtime.py reply ROOT --scope native|total
--request REQUEST_ID --seconds N --answer-id EINDEUTIGE_ALPHANUMERISCHE_ID.
Aktuelle Anfrage steht in state.json: request beziehungsweise guard.request.
Vor einer Antwort Kontotyp und ID ablesen; nicht anhand alter Meldungen raten.
Status/Endkonten: runtime.py status ROOT beziehungsweise accounts ROOT.

## Nächster Schritt: Vorbereitung, keine Suche

Mit der bestehenden ROOT8105_N1_python-Umgebung:
calibration.py prepare --output NEUES_VERZEICHNIS
Es werden die bestehenden Eingaben aus ROOT8105_N1_Kalibrierung_Eingaben_1.0
und Werkzeuge aus ROOT8105_N1_native_072 benutzt. Der Binder regeneriert jede
CNF unabhängig und vergleicht sie exakt. Anschließend aktuelle Preflights und
vollständige Vorbereitungskonten für beide Fälle. PREPARED.json wird versiegelt.
Alle Logs/Fehlschläge bleiben erhalten. Bei Fehlern nicht blind wiederholen.
Die neue reale Vorbereitung ist noch nicht ausgeführt. Nach Sichtung von
CALIBRATION_PREPARED wird zuerst nur r210_class000 mit runtime.py run gestartet;
r6682 folgt separat. Während langer Läufe Status etwa alle zehn Minuten prüfen;
ETA ohne repräsentative Suchdaten unknown.

## Validierung und Grenzen

22 gezielte Cloud-Tests für die neuen Gate-/Sperrbedingungen; keine N1-Suche.
Die echte Windows-/WSL-Abnahme des unveränderten Monitors stammt aus 0.7.2.
Die 104 früheren Cloudtests wurden nicht pauschal wiederholt. Die neue
Produktionsfreigabe muss vor der ersten Suche den realen Preflight bestehen.
GC-01/08/15/18/19/20/21/22 und EXPERIMENT_RULES gelten unverändert.
