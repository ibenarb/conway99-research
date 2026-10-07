# N1 Runtime 0.4.0: Endabrechnung der CLI-Prozesse

Basiscommit: 9a02918f46b2c7c5af2f36da3445233b7382c6b0.
Eigenes Versionsverzeichnis; 0.1–0.3 und frühere Läufe bleiben unverändert.
Cloud-Prototyp, keine Produktions-/Ryzen-Freigabe. Keine Root-8105-Suche.

## Messgrenze und Buchung

Jeder Aufruf von runtime.py startet jetzt einen äußeren Beobachter und einen
inneren Runtime-Prozess. Der Beobachter wartet mit wait4 auf das tatsächliche
Ende des inneren Prozesses. Damit sind auch Import, Inputprüfung, Initialisierung,
Nachprüfung, Recovery, Status und Nutzerantworten innerhalb dieses Prozesses
erfasst. Ein bereits abgeschlossenes Ergebnis wird weiter ohne neue Suche
wiederverwendet; die dabei anfallende Verwaltungsarbeit erhält ein neues Konto.

Die Linux-Endmessung umfasst den inneren Prozess und seine von ihm abgeholten
Kindprozesse. Die einzelnen Such-/Prüferbelege dienen der Aufteilung dieser Summe;
sie werden nicht ein zweites Mal hinzuaddiert. Benutzer- und System-CPU bleiben
getrennt im Endbeleg. Der Steuerungsanteil ist die inklusive Endmessung abzüglich
der Such-/Prüfersumme. Bei normalem Abschluss wird deren Vollständigkeit zusätzlich
mit RUSAGE_CHILDREN des inneren Prozesses abgeglichen. Der bekannte native Worker
und Checker erzeugen regulär keine unbeaufsichtigten Unterprozesse.

Der Abgleich erlaubt insgesamt 10 Mikrosekunden Rundungsdifferenz zwischen den
beiden Mikrosekundenauflösungen; die gemessene Differenz wird ausgewiesen und kein
Messwert verändert. Das ist weder ein Budgetaufschlag noch eine Stoppregel.
RSS bezeichnet das vom System gemeldete Maximum eines Kindes, nicht die Summe des
Speichers gleichzeitig lebender Prozesse.

Der Beobachter selbst protokolliert seine CPU bis zum letzten eigenen Messpunkt
als Untergrenze. Seine anschließende Beleg-/Berichtserstellung und sein Prozessende
sind nicht endabgerechnet. Der Bericht behauptet deshalb ausdrücklich
all_system_cpu_complete=false und host_cpu_s=null. Unverpackte Python-API-Aufrufe,
externes Build/Testprogramm, Windows-Hostdienste und sonstige Aufrufe außerhalb
dieser CLI gehören nicht zur exakten Messgrenze. Eine endliche Beobachterkette
liefert keine eigene externe Endmessung ihres äußersten Beobachters.

observed_commands_complete betrifft nur vollständig belegte, abgeschlossene
innere CLI-Prozesse einschließlich vollständiger Aufteilung. Ein innerer harter
Testcrash kann einen exakten äußeren Gesamtbeleg, aber keine vollständige
Aufteilung liefern: supervisor_cpu_s bleibt dann null. Der bekannte Gesamtwert
bleibt erhalten. Eine lebende/verwaiste Kindrechnung wird dadurch nicht nachträglich
als vollständig verbucht ausgegeben. history_includes_wrapped_init zeigt, ob auch
die Initialisierung über diese CLI erfolgt ist. Direkte init()-Aufrufe in älteren
Kontrolltests erfüllen diese Bedingung bewusst nicht.

## Dauerhafte Konten und Wiederaufnahme

Neben dem Runverzeichnis RUN liegt RUN.accounts. Beide müssen zusammen erhalten
und übertragen werden. Manifest, zufällige Sitzungskennungen, Prozessidentitäten,
Startabsicht, Heartbeats und Endbelege sind gespeichert. Dateihashes schützen die
Belege gegen unbeabsichtigte Änderung; das ist keine kryptographische Signatur
gegen einen Angreifer, der sämtliche Dateien ersetzen kann. Codehashes und die
Ledgerkennung sind für über CLI initialisierte Läufe im Runmanifest gebunden.

Neue Dateien werden atomar geschrieben und Datei-/Verzeichniseinträge mit fsync
gesichert. Registrieren und Lesen der Konten teilen eine Sperre, sodass eine
gleichzeitige Nutzerantwort keine halb angelegte Kontensitzung sichtbar macht.
Berichte sind abgeleitete Momentaufnahmen; unveränderte Einzelbelege sind
maßgeblich. Wiederholte Auswertung bucht nichts erneut. Während einer Abfrage ist
deren eigene aktuelle Sitzung ausdrücklich ausgenommen; nach Prozessende liegt
auch für diese Sitzung ein Endbeleg vor.

Geht der Beobachter zwischen wait4 und Belegsicherung verloren, ist CPU unbekannt,
nicht null. Ein neuer run/resume-Aufruf eines gebundenen Laufs wird vor der Suche
abgewiesen. Der aktuelle Ablehnungsaufruf selbst wird abgerechnet. Kein Erfinden
verlorener Endmessungen und kein automatischer Ersatz eines fehlenden Ledgers.
Ein Crash nach vollständigem Endbeleg benötigt keinen Berichts-Cache zur Rettung.
Die bisherigen Regeln gegen lebende verwaiste Worker, beschädigte maßgebliche
Transaktionen und verlorene native wait4-Endbelege bleiben erhalten.

Der Zustandswert accounting_complete und die bisherigen budget/cpu_completed-
Werte beziehen sich weiterhin ausdrücklich auf native_children_cpu_seconds.
Gesamt-CLI-Abrechnung steht im getrennten accounts-Bericht. Der bestehende
Nutzerbudgetvertrag wird nicht still auf eine andere Einheit umgestellt. Es gibt
keinen zusätzlichen Gesamtbudget-Autostopp. Eine künftige Gesamtbudgetsteuerung
benötigt einen getrennten, expliziten Vertrag samt Antworten und Wiederanlauf.

## Schnittstelle und Quellen

runtime.py behält init/run/resume/recover/status/reply bei und ergänzt accounts.
Aufrufe der CLI werden automatisch beobachtet. Das interne Sitzungskennzeichen
wird vom Starter gesetzt und mit der Elternprozessidentität abgeglichen.
Es ist kein vom Nutzer zu setzender Schalter. Alte Runverzeichnisse werden nicht
migriert. build.py baut die unverändert fixierten nativen Quellen;
requirements-n1.txt nennt die Python-Abhängigkeiten. Der unveränderte Encoder muss
weiter unter tools/memetik/root8105_n1/model.py liegen und ist im Quell-ZIP dabei.

Inputbindung, unabhängige N1-Zeugenprüfung und Beweisprüfung entsprechen 0.3.0.
Die zwei Klasse-0-Katalogbelege aus dem Basiscommit bleiben eigenständige Belege;
diese Runtime erzwingt ihre Prüfung noch nicht automatisch. Die neue Abrechnung
liefert keine neue mathematische Aussage und keine Leistungsprognose.

Maßgebliche Betriebssystemdokumentation:
https://man7.org/linux/man-pages/man2/getrusage.2.html
https://man7.org/linux/man-pages/man2/wait4.2.html
Hier nur Linux-Cloud geprüft; Windows/WSL-Zielhardware und Stromausfallverhalten
wurden nicht experimentell abgenommen.

## Abnahme und nächste Grenze

47 finale Kontrollen: 9 neue CLI-Abrechnung, 16 Laufsteuerung, 11 Recovery,
11 unabhängige N1-Kontrollen mit m=2. Reale CaDiCaL-/drat-trim-Prozesse für kleine
Kontrollformeln; keine m=7-Klassensuche. Gesteuerte Fehler verwenden ausdrücklich
aktivierte Testschalter; kein Zeitbudget wird als Abbruch eingesetzt.

Quellen, finale Ergebnisse und frühere Fehlversuche stehen unter
 docs/augmentation/root8105_n1_accounting_20261007.
Regeln: GC-01/04/08/15/18/19/20/22; Regeldateien am Basiscommit.
Alle bisherigen CPU-Lücken bleiben offen. Noch ausstehend: durchgängige
Gesamtbudgetsteuerung, Ressourcen-Notfallsteuerung, begrenzter Aufwand bei langen
Kontenhistorien, Windows-Hostuhr/-abrechnung und echte Zielhardwareabnahme.
Nächstes begrenztes Paket: Gesamtbudgetvertrag und Ressourcenüberwachung der
Runtime, zunächst ausschließlich synthetische Cloudkontrollen.
