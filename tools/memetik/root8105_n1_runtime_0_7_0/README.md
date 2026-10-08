# ROOT8105 N1 Runtime 0.7.0 — Plattformanbindung zur Ryzen-Abnahme

Basis: 22b3da3fef6995158f7c3cf9602abb1df52533b2 (0.6.0 bleibt unverändert).
Status: Cloud-Kontrollen bestanden; echte Windows-/WSL-Abnahme ausstehend.
Kein N1-Suchstart, keine neue mathematische Aussage, kein Produktionsfreigabeschalter.

## Forschungsziel und nächste Entscheidung

Die nächste Forschungskalibrierung betrifft weiterhin ausschließlich Klasse 0
von Root 210 und Root 6682. Daraus sollen Such-/Prüfkosten, Speicher und
Beweiswachstum ermittelt werden. Erst danach folgt eine Entscheidung zum
220-Klassen-Pilot dieser beiden Roots. Dieser wäre keine repräsentative
Kostenschätzung für alle 8105 Roots. Die alte 40000er-Baummessung wird nicht wiederholt.

0.7.0 bereitet die Zielhardwareabnahme vor. Der wissenschaftliche Modellcode,
Katalog und die beiden CNFs bleiben unverändert. Alle N1-Produktionsstarts bleiben
hart durch das fehlende Zielhardware-Abnahmegate gesperrt. Ein frei ergänztes
Manifestfeld, ein alter PASS oder ein erfolgreicher Plattformtest hebt es nicht auf.

## Neue Komponenten

- `host_clock.ps1`: Ein Windows-Prozess sendet Stopwatch-Ticks/Frequenz, UTC,
  PID/Startidentität, CPU-Untergrenze und verfügbaren physischen Windows-Speicher.
  Sein besitzender Windows-Prozess hält das Prozesshandle bis nach WaitForExit
  und erfasst die tatsächliche End-CPU des Zeithelfers. Der Besitzer selbst
  liefert nur eine ausdrücklich so benannte CPU-Untergrenze.
- `platform_adapter.py`: Prüft Sitzungsidentität, Sequenz, Zeitfortschritt,
  Wertebereiche und Host-Abschluss. Der Linux-Außenbeobachter prüft fortlaufend
  Cgroup-v2-Mitgliedschaft, sichtbare Vorfahren, Speicherreserve, OOM-Zähler,
  Linux-MemAvailable, Plattenreserve und RSS der bekannten eigenen Prozesse.
- `target_acceptance.py`: Getrennte echte WSL-Stufen `probe` und `controls`.
  Keine N1-Klasse wird durch dieses Programm gestartet.

Init/run/resume/preflight nutzen den Windows-Adapter, wenn `init --platform-wsl`
festgelegt wurde. Die vier vorhandenen Guardwerte müssen explizit angegeben sein.
Status-, Antwort- und Kontenabfragen starten keinen zusätzlichen Windows-Helfer;
die vorhandene Linux-CLI-Abrechnung bleibt aktiv. Das vermeidet verzögerte
0-Antworten durch unnötige Windows-Starts. Die Adapterquellen werden im
unveränderlichen Laufmanifest per Hash gebunden. Keine Migration alter Läufe.

## Kontinuierliche Beobachtung und Fehler

Der äußere Beobachter arbeitet in der bestehenden Schleife mit 0,1 s Wartepause,
auch während Importen, Modellprüfung und abschließender Python-Arbeit im inneren
Prozess. Dies ist ein Solltakt, keine Echtzeitgarantie. Auslastung, Dateisystem und
Scheduling können Beobachtungen verzögern. Es werden die sichtbaren Cgroup-Vorfahren
und wenige sitzungsgebundene Dateien gelesen, keine wachsende Beweisdatei gehasht
und kein wachsender Ergebnisbaum rekursiv durchlaufen.

Neue OOM/oom_kill-Ereignisse, Zählerrücklauf, geänderte Mitgliedschaft, fehlende
Pflichtdaten oder unterschrittene Reserven werden dauerhaft verriegelt.
Bei einem aktiven Solver wird dessen STOP-Datei gesetzt; ein aktiver Prüfer wird
über ein identitätsgeprüftes Linux-pidfd beendet. Kein unbeteiligter Prozess wird
angefasst. Bereits gesicherte Ergebnisse und Beweise bleiben erhalten. Während
reiner Python-Arbeit wird der Fehler vermerkt, keine neue native Arbeit zugelassen
und auf reguläre Rückkehr gewartet. Kein asynchrones Töten des Python-Prozesses.
Eine Garantie gegen abruptes OOM oder externes Füllen des Datenträgers besteht nicht.

30 Gast-monotonic-Sekunden ohne beobachteten Hostfortschritt sind ausschließlich
ein Kommunikations-/Überwachungsfehler, kein Forschungsbudget. Dieselbe Frist gilt
für die Startbereitschaft des Helfers. Es erfolgt kein zeitabhängiger Kill. Beim
geordneten Ende wird STOP an den Helfer geschrieben und ohne Killfrist auf dessen
Rückkehr gewartet. Hängt die Windows-Seite, kann deshalb auch die Abwicklung warten.
Die Uhren werden nicht gegeneinander skaliert. Gastzeit dient nur dem lokalen
Lebenszeichenwächter, nicht einer behaupteten validierten Windows-Laufzeitmessung.

Cgroup `max` bleibt ausdrücklich unbegrenzt, nicht numerisch null. Nicht sichtbare
Vorfahren bleiben ungeprüft. Fehlende Speicherkontrollerdaten verhindern die Abnahme;
es werden keine OS-/Cgroup-Limits oder Windows-Einstellungen verändert. Eine
sichtbare unbegrenzte Cgroup kann im Plattformtest durch separate Host-/Gastreserven
beobachtet werden; das unveränderte zusätzliche Produktionsgate fordert weiterhin
eine begründete Speicherhülle. Zielhardwarebefunde können hier Anpassungen verlangen.

## Abrechnung und Fortsetzung

Windows-Zeithelfer-Endverbrauch und Windows-Besitzer-Untergrenze werden getrennt
zu den belegten Linux-Konten hinzugefügt. Linux-wait4 des inneren Prozesses enthält
seine nativen Kinder bereits; deren Zeiten werden nicht doppelt addiert.
Ein fehlender oder ungültiger Windows-Endbeleg ergibt `host=null`, eine offene
Abrechnungslücke und CLI-Exit 78. Der bestehende wissenschaftliche Status wird
nicht nachträglich gefälscht. Die nächste Fortsetzung verweigert ungeklärte Konten.
Der Plattformabschluss ist durch seinen Dateihash an den CLI-Endbeleg gebunden.

Weiterhin keine exakte Gesamtabrechnung sämtlicher physischer Hostarbeit:
Der letzte Nachlauf der äußeren Beobachter, Interop-Transport und fremde
Systemdienste sind nicht vollständig erfasst. `all_system_cpu_complete=false`.
Dies wird nicht durch eine erfundene Nullbuchung verdeckt. Das Gesamtbudget bleibt
ein Budget der aufgezeichneten CPU-Untergrenze. Alte Kontenlücken bleiben unverändert.

Budgetende erzeugt weiterhin genau eine offene Anfrage pro Konto. Ohne Antwort
läuft derselbe Solver weiter; positive Sekunden verlängern genau einmal;
0 veranlasst kontrollierte Beendigung. Eine später neu gestartete offene CNF
bekommt einen neuen Versuch; der interne CDCL-Zustand ist nicht serialisiert.
Vollständige Ergebnisse und versiegelte Beweise werden übernommen. Der Prüfer
setzt anhand seiner unveränderten Eingaben neu an, ohne erneute Suche.

## Abnahme auf Ryzen — nacheinander

1. `probe`: Voraussetzungen, PowerShell-Syntax auf dem echten Interpreter,
   sechs verschiedene Hostmeldungen, Cgroup/Host/Gast/Dateisystem und Helfer-Endkonto.
   Die kleinen Kontrollreserven sind 1 GiB Run-RSS, 128 MiB verfügbarer Host-/Gast-
   beziehungsweise endlicher Cgroup-Speicher, 512 MiB freier Datenträger.
   Das ist keine Ressourcenplanung für den späteren Forschungslauf.
2. Nach Bewertung dieses Befunds: `build.py` baut die unveränderten fixierten
   CaDiCaL- und drat-trim-Quellen in einem neuen Verzeichnis.
3. `controls`: echte kleine SAT/UNSAT-Kontrollen mit beiden nativen Werkzeugen,
   Windows-Endkonten, Ergebnisübernahme ohne Neusuche, Budgetende ohne Antwort,
   doppelte positive Antwort, explizite 0 und Wiederaufnahme mit getrennten Konten.
4. Ergebnisarchiv prüfen. Erst danach eigene Kalibrierungsfreigabe vorbereiten.

Ausgabeverzeichnisse müssen neu sein. Kontrollstart erfolgt mit abgetrennter
Prozesssitzung und geschlossener Standardeingabe; EOF hält ihn nicht an.
Bei einem Prüfungsfehler versucht das Abnahmeprogramm seine eigenen laufenden
Budgetkontrollen über den vorhandenen 0-Kanal kontrolliert zu schließen.
Keine Windows-/WSL-Neustarts, kein Eingriff in bestehende C2-Läufe.

## Belegte Cloud-Prüfungen

78 übernommene Regressionen gegen diese Version, 22 Plattformkontrollen und vier
Integrationskontrollen. Windows-Protokolldaten der Cloudtests sind ausdrücklich
synthetische Fixtures. Echte Linux-Prozesse belegen den STOP-/pidfd-/wait4-Pfad.
Ein CPU-beschäftigter innerer Prozess blockiert die äußere Überwachung nicht.
Es gibt keinen Testmodus-Schalter im Produktionsadapter; die Transportsimulation
ist ausschließlich im getrennten Testprogramm implementiert. PowerShell selbst
wurde in dieser Cloud nicht ausgeführt oder durch einen PowerShell-Parser geprüft.
Die WSL-Abnahme kann deshalb weiterhin Fehler aufdecken.

## Quellen und Regeln

GC-01/08/15/18/19/20/21/22 am Basiscommit; AGENTS.md,
docs/EXPERIMENT_RULES.md und docs/operations/GLOBAL_CONCLUSIONS.md.

- https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.totalprocessortime
- https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.waitforexit
- https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.stopwatch.gettimestamp
- https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
