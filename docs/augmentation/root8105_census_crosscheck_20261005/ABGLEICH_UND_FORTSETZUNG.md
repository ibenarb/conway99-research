# ROOT8105: Reviewabgleich und konkrete Fortsetzung

Stand: 05.10.2026, Berlin. Gegenstand: Census 1.0.0, Commit
`948f252f798d8dc2cbf0044faa8d1e985c83fc04`, und eingereichter Kandidat 1.0.1-rc1.
Dies ist ein Arbeitsplan, keine Produktionsfreigabe und kein neuer Rechenlauf.

## Entscheidung

Mathematischen Kern und vorhandene Kontrollen weiterverwenden. 1.0.0 nicht auf
Ryzen starten. 1.0.1-rc1 als Reparaturbasis übernehmen, noch nicht als Release.
Zuerst begrenzte Betriebsabnahme, dann der bereits vorgesehene P0/P1-Zählzensus.
Keine automatische Tiefe-2/3-Kampagne, Vollbaum-Materialisierung oder Full-SAT-Suche.
Der laufende C2-Checker bleibt unverändert.

## Abgleich und Evidenz

| Punkt | Urteil | Konsequenz |
| --- | --- | --- |
| F-Kern, Rootdaten, Integergrenze | Kein Gegenbefund; Kern, historical_core, roots und beide Fixtures selbst byteidentisch zwischen 1.0.0 und rc1 geprüft | Keine mathematische Neuentwicklung erforderlich |
| RC-Fingerprint | Selbst vollständig gegen VALIDATION.json geprüft, stimmt | Eindeutige Basis e2662e92a757469e2b5bd18b0f427c4a6cf385822093985c3bb99cd5e6638dbf |
| Hosthelfer H1–H3 | Fehlerpfade des alten Codes plausibel und vom Reviewer reproduziert; rc1 enthält Abfang- und Beendigungslogik | Echte WSL-Abnahme bleibt offen |
| Crash/CPU H4, M1 | RC ergänzt Kontenabschluss mit Untergrenzen, getrennte Rettungsdaten und Elternprüfung | Fehlende Endbelege bleiben fehlend; Untergrenzen nie als exakten Gesamtverbrauch ausgeben |
| Unvollständige Zustände M2 | RC verhindert falschen Abschluss; Wiederanlaufhinweis noch unvollständig | Eigener reproduzierter Restbefund unten |
| Dateisystem M3 | RC prüft problematische Mounttypen | Live-DB auf lokalem Linux-Dateisystem, keine synchronisierte Arbeitsfläche; Sicherung konsistent erstellen |
| GC-19/CPU im Normalbetrieb | Reviewer bestätigt die grundsätzliche Logik und konkurrierende Antworten | Bewährte Logik erhalten, nur betroffene Fehlerpfade erneut prüfen |
| Unabhängige Mathematikkontrolle | Reviewer berichtet 2490 Vergleiche ohne Abweichung: 498 Kernel/Vertex und 1992 Vertex/Fixture | Starke zusätzliche Evidenz, hier nicht als eigene Neuberechnung ausgeben |

Meine frühere Darstellung wird präzisiert: 249/747 Fixture-Vergleiche sind
Regressionen innerhalb derselben algorithmischen Herkunftslinie. Unabhängige
Evidenz liefern SAT und die anders aufgebaute Vertex-Rekursion. Der erfolgreiche
isolierte 66-Root-Lauf mit anschließendem Neustart belegte keinen echten
Wiederanlauf mitten in einer Rootberechnung. Diese Prüfung berichtet nun der
Reviewer für einzelne Roots, noch nicht für elf Worker auf WSL.

Zum 66→64-Vorfall: Die vom Reviewer beschriebenen widersprüchlichen Seitenstände
sprechen stark für eine inkohärente Kopie/Synchronisation. Die genaue Ursache
ist nicht bewiesen. Ein positives SQLite integrity_check genügt nicht für
semantische Konsistenz. Die beschädigte DB bleibt Beleg, kein Produktionsstartpunkt.

## Eigener reproduzierter Restbefund

Mit unverändertem rc1 wurde eine frische synthetische Ein-Root-Testdatenbank
initialisiert und ausschließlich der Rootstatus auf RUNNING gesetzt, ohne
offenen Versuch. audit_start verweigert zu Recht den Start und empfiehlt
reconcile-crash. reconcile-crash --apply findet keine offenen Konten, ändert
nichts, und audit_start verweigert erneut den Start. Siehe OWN_CHECKS.json.

Das ist keine falsche Zählung und kein unsicheres Durchlassen. Es ist ein
irreführender Wiederherstellungsweg für einen inkonsistenten Zustand.
Vor Release: normale Absturzkonten von inkohärenten Datenbeständen unterscheiden.
Für letztere Original unverändert sichern, Diagnose ausgeben und einen neuen
Lauf mit neuer Kennung/Konten anlegen. Kein stilles RUNNING→PENDING ohne Beleg.
Für einen späteren Import abgeschlossener Ergebnisse wäre ein eigener geprüfter
Importer erforderlich; für diesen frühen Pilot ist sauberer Neustart einfacher.

Zusätzlicher Codeprüfauftrag: reconcile-crash muss vor jeder Mutation Identität,
Manifest/Fingerprint und Datenbankstruktur prüfen. Die normale audit_start-
Funktion lässt sich nicht unverändert verwenden, da offene Konten hier erwartet
werden. CPU-Felder der Rettungsbelege müssen endlich und nichtnegativ sein.
Diese Punkte sind Prüf-/Korrekturaufträge, keine hier reproduzierten Ausfälle.

## Konkrete Etappen und Abnahmekriterien

### A — Release-Kandidat abschließen

1. RC unverändert als Herkunft archivieren; Korrekturen in neuer Version.
2. Restbefund und vorgelagerte Recovery-Prüfungen bearbeiten. Vollständige
   Dateien und Bedienweg liefern; kein manueller Eingriff in Kontenmarker.
3. Relevante Betriebsregressionen ausführen; echter unterbrochener Kernel-Lauf
   mit Wiederaufnahme muss dieselben Counts wie die Referenz ergeben.
4. Elf Worker mit den festen 66 Kalibrierungsroots testen: 5478 Zielzählungen,
   keine offenen Konten, korrekte Abschlusszustände, vollständige Abrechnung.
   Cloud-Abnahme und Zielhardware-Abnahme getrennt kennzeichnen.

Ergebnis: eingefrorener neuer Kandidat, Prüfreceipts, Fingerprint und vollständiges
Paket. Erst danach die Zielhardware bedienen. Ein geändertes VALIDATION-Label
allein ist keine Freigabe.

### B — Ryzen/WSL-Abnahme, C2 geschützt

Separates wegwerfbares Testverzeichnis auf lokalem Linux-Dateisystem. Keine
Änderung der C2-Umgebung. Bedienanweisungen jeweils einzeln ausgeben.

- Reale PowerShell-Uhr mindestens drei Minuten unter de-DE beobachten: lesbare
  JSONs, Fortschritt, Driftmessung und Beendigung. Fehlend, defekt und hängend
  gezielt prüfen. Ohne brauchbare Hostuhr keine belastbare ETA behaupten.
- Elf Worker parallel zu C2: RAM beobachten, mindestens 2 GiB freie Reserve
  als Abnahmekriterium; bei Unterschreitung Workerzahl reduzieren und neu messen.
- Echte Teilrechnung per SIGTERM unterbrechen und wiederaufnehmen; separaten
  Testcontroller gezielt per SIGKILL beenden, Workerende nachweisen, Recovery
  durchführen und Resultate mit ununterbrochener Referenz vergleichen.
- Kein wsl --shutdown, solange C2 in der betroffenen Umgebung läuft. Ein
  vollständiger WSL-/Hostausfall bleibt bis zu einem sicheren separaten Test
  ausdrücklich ungeprüft; SIGKILL ist dafür kein vollständiger Ersatz.
- Hintergrundbetrieb und GC-19 mit 300 aggregierten CPU-Sekunden Meldeschwelle
  prüfen: ohne Antwort weiter, ungültige Eingabe weiter, positive Antwort genau
  einmal, erneute Schwelle, 0 kontrollierter Abschluss, offene Anfrage nach Resume.

Ergebnis: belastbarer Zielhardwarebericht. Keine Übernahme der Cloud-Schätzung
von etwa 23 CPUh als Ryzen-Prognose. Maßgeblich sind lokale Messungen.

### C — P0/P1-Zählzensus

Neue Produktionskennung und neue Konten. Unverändertes historisches F-Modell,
8105 Roots × 83 Zielzeilen = 672715 exakte Counts, keine Kindmaterialisierung.
66 Roots (22 je Typ) kalibrieren; ihre fertigen Counts im anschließenden
Gesamtzensus weiterverwenden. Ziel sind elf Worker, sofern B die Ressourcen bestätigt.

48 aggregierte CPUh bleiben die vereinbarte Meldeschwelle, kein automatischer
Abbruch. Vorabtests/Kontrollen getrennt ausweisen und dem Gesamtverbrauch
zurechnen; keine zweite versteckte 48h-Reserve. GC-19 gilt auch für Prüfarbeit.
Nach einem harten Crash bleibt der bekannte Gesamtverbrauch als Untergrenze
markiert; eine exakte Normalbetriebsabrechnung darf dadurch nicht vorgetäuscht werden.

Auswertung: Vollständigkeit aller Paare, Minima und Quantile der Breiten je
Root/Typ, Summe der jeweils minimalen ersten Verzweigung, Symmetrieklassen,
CPU/RAM/Nebenarbeit und offene Fehler. Diese Daten beschreiben Tiefe 1; daraus
folgt weder ein Gesamtbaumaufwand noch ein SRG-Nichtexistenzbeweis.

Unabhängige Nachzählung: vor Auswertung deterministisch nach Roottyp und
Breitenbereich geschichtete 13455 Paare festlegen (mindestens 2 Prozent).
Vertex-Rekursion verwenden, Herkunft der Fixture-Fälle kennzeichnen. CPU-Bedarf
aus lokalem Prüfdurchsatz bestimmen und offen verbuchen. Jede Abweichung sperrt
die wissenschaftliche Auswertung bis zur Klärung; Stichproben sind kein formales
Zertifikat für sämtliche übrigen Counts.

### D — Messbarer Filterpilot als anschließender Vorschlag

Erst nach C die konkrete Stichprobe fixieren: 24 Roots, acht je Typ, über
Breiten-/Stabilisatorgruppen verteilt; je Root bis zu drei unterschiedliche
Zielzeilen (schmal, Median, breit); je Ziel bis zu 64 eindeutige Ränge.
Bei weniger als 64 Kindern vollständig enumerieren, sonst gleichverteilt ohne
Zurücklegen ziehen. Maximal 4608 Zustände. Seeds und Auswahl vor Filterauswertung
festhalten. Keine Behauptung einer gleichverteilten Stichprobe aller Kinder.

Dieselben Zustände unter F, F+LD, F+CAP und F+LD+CAP prüfen, mit getrennten
Modellkennungen. Messen: Ausschlüsse, Überlappung, CPU pro Zustand sowie Kosten
je zusätzlichem Ausschluss. Positivkontrollen unverändert behalten. Eine vorab
fixierte Stichprobe abgelehnter Zustände unabhängig mit SAT prüfen; gültige
Fortsetzungen dürfen nie verworfen werden. Überlebende sind keine SAT-Zeugen.

Diese Stichprobe ermittelt Filterwirkung, keine exakten gefilterten
Verzweigungszahlen. Erst daraus einen begrenzten Tiefe-2/3-Versuch dimensionieren
und gesondert vorlegen. Filterentwicklung in separatem Paket, damit der laufende
Census-Fingerprint und Resume erhalten bleiben.

## Aktive Regeln und Status

Regelbasis im fixierten Commit 948f252f798d8dc2cbf0044faa8d1e985c83fc04:
AGENTS.md, docs/EXPERIMENT_RULES.md und docs/operations/GLOBAL_CONCLUSIONS.md.
Relevant: GC-01/07 (Uhren/Umgebung), GC-09/15 (Neustart/Konten), GC-10/11
(Abschluss/ETA), GC-16 (begrenzte Enumeration), GC-18 (Nebenarbeit), GC-19
(Budgetdialog), GC-20 (modellgerechte Kontrollen).

Heute selbst ausgeführt: Audit-Interpreterprüfung, Byte-/Fingerprintvergleich
und kleiner synthetischer Restfehlertest. Keine vollständige Wiederholung der
Reviewer-Testserie, kein neuer mathematischer Census, keine Ryzen-Aktion,
keine Produktionsfreigabe. Nächster Arbeitsblock: Etappe A.
