# Ryzen-Vergleich 0.4.1: ausführbare Vorbereitung

Fachlicher Vertrag: `docs/memetik/ryzen_plan_20260919/FORTSETZUNG_RYZEN.md`
und Plan V2. Unveränderter Eingangscommit:
`c54d4a1369f2f2b6f1289692c5001f49712a91a5`.

## Bestätigte Ausfallursache und Wiederaufbau

Am 20.09.2026 hat der Eigentümer die Ursache des früheren Ausfalls ausdrücklich
festgehalten: Ein Programmfehler ließ die physische Windows-Platte volllaufen,
während die virtuelle Ubuntu-Platte weiterhin freien Platz meldete. Der
16-GiB-Swap ist nicht die festgehaltene Ursache.

Ubuntu wurde nach der genehmigten Beendigung der Rettung neu installiert.
Aktuell: Ubuntu-24.04, Benutzer rb, Ryzen 9 3900X, 24 logische Prozessoren,
etwa 47 GiB RAM. Paket-/Graphbibliothekskontrolle und begrenzter Schreib-/Lesetest
sind laut Rückmeldung bestanden. Der Memetik-Checkout ist sauber auf obigem
Commit. Debian, Office und fremde Prozesse bleiben unberührt.

## Implementiert

`experiments/memetik/ryzen_compare_0_4_0/prepare.py` erstellt in einem neuen
Verzeichnis unter dem Linux-Workspace:

- ein unabhängig auf beide jeweiligen Verträge und fünf Scores geprüftes
  Gründerregister mit Quellhashes, exakten nauty-Zertifikaten, Abstammung und
  getrenntem Ω-Rahmen;
- ein Manifest mit 144 Aufträgen: neun gepaarte Seeds, zwei Arme, vier Ziele,
  zwei Varianten, je 3600 Worker-CPU-Sekunden, insgesamt 518400 Sekunden;
- einen lokalen Ressourcenbericht. Systempfade und Prozesslisten werden nicht
  automatisch veröffentlicht.

Der vorhandene Bestand liefert **17 verschiedene geeignete Ω-Klassen und
12 λ-Klassen**, ohne A als aktiven Bestand zu zählen. Enthalten sind der
geprüfte B-W2080-Endpunkt und C02-W2031/L1=2428/F=3298. A bleibt Kontrolle.
Claude-B zählt zur Z14-Abstammung von Claude-A, F03/F04 gemeinsam als
Z33-Lifts. HoG-Nachfahren sind keine neue Herkunftsfamilie. Fehlende historische
Kosten werden als unbekannt gespeichert, niemals als null.

Dies ist ein Reservoir, noch keine ausgewählte Vergleichspopulation. Vier
weitere verschiedene λ-Gründer für die nominellen 16 und getrennte
Trainings-/Übertragungsbestände sind noch bereitzustellen oder die ehrliche
kleinere Größe ist vor Bestätigung festzulegen. Kein Auffüllen durch Kopien.

Die neue Ω-Erzeugung speichert die statischen Träger und berechnet die
H-abhängigen Vorzeichenbedingungen mit Bitmasken neu je Zustand. Alte
Programme und Ergebnisse sind unverändert. Die zufällige Traversierungsordnung
ändert sich; behauptet wird derselbe zulässige Katalog, nicht dieselbe
Zufallsfolge und keine Gleichverteilung über Trades.

## Schutz vor Wiederholung des Plattenfehlers

Die aktuelle WSL-Registrierung bestimmt die tatsächliche VHDX. Über Windows
wird deren Trägervolumen abgefragt; ein fehlendes `/mnt/c` oder eine unbekannte
Messung gilt nicht als freier Platz. Reserven: **50 GiB auf dem physischen
Windows-Volume, 20 GiB im Linux-Ziel**, mindestens 6 GiB verfügbarer RAM.
Eine fehlgeschlagene Abfrage sperrt die Vorbereitung. Keine Mount-, Reparatur-,
Resize- oder Abschaltoperation.

Die Volume-Zuordnung nutzt das dokumentierte
[Get-Volume -FilePath](https://learn.microsoft.com/en-us/powershell/module/storage/get-volume).
Die Windows-Abfrage kann in der Entwicklungsumgebung nicht gegen den Ryzen
ausgeführt werden; genau dieser nächste lokale Prüfschritt ist noch offen.

## Vergleichsläufer implementiert (zweite Auslieferung, 20.09.2026)

`campaign.py`, `worker.py`, `search.py`, `runtime.py`, `generate.py` und
`evaluate.py` ergänzen die Vorbereitung. Die echte Ryzen-Rückmeldung bestätigt
24 CPUs in der Affinität, C als VHDX-Träger, 641,22 GiB dort frei und
953,45 GiB frei im Linux-Dateisystem. Vorbereitungspfad:
`/home/rb/conway99_workspace/ryzen_compare_prepare_cjgeeuwh`.

A0/A1 haben identische Anfangsstörung, Gründer, Populationsgröße und Selektion.
A1 ergänzt 128 beschriftete Besuchszustände je Arbeitslinie/Ziel, höchstens
32 neue neutrale Schritte und Escape-Grenzen relativ zum festen Episodenanker.
Strikte Verbesserungen dürfen die Verschlechterungsschranken umgehen.
Linf vergleicht das vollständige Tupel. Linf+1 ist in dieser ersten Variante
ausgeschaltet; Crossover und Migration ebenfalls. Die nicht qualifizierte
10-%-Frisch-/Reparaturquote wird offen proportional auf 4:3:2 umverteilt.
Störung und Abstieg erhalten eigene Obergrenzen von 45 bzw. 75 CPU-Sekunden.

Bei 16 Plätzen bleiben zwei Elitezustände, zehn weitere Qualitätsplätze und
vier Explorationsplätze. In den ersten fünf Epochen bleibt jede ausgewählte
Herkunftsgruppe vertreten. Elternwahl: 80 % Dreierturnier, 20 % aus den aktuell
am schwächsten besetzten Herkunftsgruppen. A1 wechselt nach vier erfolglosen
Linienbearbeitungen die Schwellenstufe und erzwingt ab acht längere Ausflüge.
Stichprobenstillstand heißt STALLED_SAMPLED, niemals lokales Minimum.

### Ausführbare Kalibrierung, getrennt vom Vergleich

1. Fester Batch: acht neue F02-Seeds und 24 F04-Seeds, maximal je 60 CPU-Sekunden.
   Die adaptierten Generatoren vermeiden zusätzliche NetworkX-Abhängigkeiten.
   Jeder Rückgabekandidat wird unabhängig geprüft und exakt dedupliziert.
2. B-W2080 erhält einen auf 900 CPU-Sekunden begrenzten W-Abstieg/Zensus.
   Ein Minimalitätsstatus wird nur nach vollständiger Enumeration aller drei
   Katalogfamilien am endgültigen Zustand ausgegeben.
3. Fester Trainingsbestand: Ω B_original und Codex-C01, λ HoG57177 und
   Codex-C07. Diese vier Graphen sind aus der Bestätigung ausgeschlossen.
   Je Arm wird zusätzlich ein neu erzeugter Gründer als Übertragungsprobe
   zurückgehalten. Auswahl und Trennung werden vor dem Training gespeichert.
4. Schwellen: nächster Rang des 75-%-Quantils positiver Einzeltradeänderungen,
   wenigstens 32 Beobachtungen je Arm/Ziel aus dem Trainingspool; sonst Stopp.
   Übertragungsproben führen nicht zu nachträglichem Nachstellen der Schwellen.
5. 12/18/24 Worker: jeweils dieselben 32 gepaarten Trainingsaufträge mit bis
   zu 130 Worker-CPU-Sekunden, die mehrere echte Episoden ausführen. Auswahl
   nach gültigen abgeschlossenen Episoden pro Wandzeit, zusätzlich tatsächliche
   Längen und Zielkosten. Kurze λ-Jobs werden damit nicht nur einmal gestartet,
   während der restliche Benchmark allein Ω misst.
6. Danach unveränderliches `confirmation.json`: 144 Aufträge und 518400
   CPU-Sekunden. Der Controller endet mit READY_FOR_CONFIRMATION. Er startet
   den Vergleich ausdrücklich nicht automatisch.

Die oberen Worker-CPU-Kontingente dieser Kalibrierung summieren sich auf
18340 Sekunden = 5,0944 Stunden (einschließlich der Generatorgrenzen).
Das liegt unter den beschlossenen separaten Rahmenbudgets. Tatsächlich
verbrauchte CPU wird über alle eigenen Worker einschließlich Fehlversuchen
gezählt; ungenutzte Kontingente sind keine verbrauchte Rechenzeit.

Im verkürzten Entwicklungstest ließen sich 16 verschiedene Gründer je Arm
zusammenstellen. Die λ-Auswahl umfasste fünf HoG-Abstammungen, eine
Tripelpackung und zehn Lifts: offen erkennbare Herkunftsverengung, keine zehn
neuen Familien. Ob der echte Ryzen-Lauf dieselbe Auswahl liefert, bleibt
seiner Prüfung vorbehalten. Feste F02-Faser-/Z33-Partitionsbedingungen werden
explizit geprüft; Automorphismenverlust ersetzt diese Prüfung nicht.
Beobachtete Ausgänge betreffen die ursprünglichen Labels, keinen Ausschluss
aller möglicherweise anders nummerierten Lift-/Faserdarstellungen.

### CPU, Wiederaufnahme und Datenhaltung

Jeder Bestätigungslauf erhält höchstens 3600 Worker-CPU-Sekunden. Zwei Sekunden
liegen als identisches Abschlussreservat innerhalb dieses Kontingents;
abschließende Prüfung/Checkpoint/Prozessende dürfen nicht zusätzlich als
kostenfreie Arbeit behandelt werden. Die letzte gültige Bestmarke wird bis
zum Budgetende konstant fortgeschrieben. Tatsächlicher Verbrauch und
ungenutzte Reserve werden getrennt berichtet; keine Übertragung der Reserve
auf andere Läufe. Überschreitet eine CPU-Quittung das Kontingent, sperrt die
Auswertung eine reguläre Vergleichsentscheidung.

Der Controller erfasst mit wait4 die gesamte Benutzer-/System-CPU des eigenen
beendeten Prozesses, einschließlich nativer Solverthreads. Worker erzeugen
keine weiteren Prozesse. Auch Start-/Prüf-/Checkpointkosten zählen.
Controller-CPU wird separat protokolliert. CPU der Windows-Abfrage gehört
zur Infrastruktur, nicht zu einem Arm.

Atomare, gehashte Checkpoints speichern Population, RNG, Besuchsspeicher,
Stagnation, Bestkurven und Kosten. Geordnete Pause/Wiederaufnahme übernimmt
die bereits verbrauchte CPU aus der Controllerquittung. Nach abruptem
Controllerverlust wird kein unsicheres Restbudget geschätzt: eine offene
Quittung oder unvollständige Zeitmessung verlangt Diagnose. Worker erkennen
den Verlust ihres Elternprozesses und beenden sich kooperativ. Dies ist
keine Garantie verlustfreier Fortsetzung nach Stromausfall.

Die Software wird je Lauf als geprüftes Codebündel eingefroren. Ein späteres
Git-Pull verändert laufende Worker nicht. Eine Wiederaufnahme verwendet
weiter dieses Bündel und prüft Python-/Bibliotheksversionen.

Windows-Trägerplatz wird während des Betriebs spätestens beim nächsten
15-Sekunden-Prüftermin erneut abgefragt (Abfragetimeout 20 Sekunden), RAM
zusätzlich zwischen Queue-Abfragen. Unter einer Reserve werden keine neuen
Jobs gestartet und nur die eigenen Worker zum Speichern/Beenden aufgefordert.
Normale Prozesse erhalten 1 GiB Adressraum; die ganze Gruppe bleibt zusätzlich
unter 36 GiB RSS. Es gibt keine schweren Reparaturjobs. Status alle zehn
Minuten enthält CPU, ETA für die aktuelle Phase und im Vergleich Bestwerte,
Klassen je Lauf und die Verteilung tatsächlich erreichter Störlängen.

### Auswertung und Export

Primär: bester aktiver Zielwert je vollständigem Laufseed. Einseitiger exakter
Vorzeichentest, Bindungen ausgeschlossen und sichtbar, Holm über acht Tests,
Gesamtalpha 0,05. Zusätzlich vorab festgelegt: mindestens 0,5 % medianer
relativer Gewinn zur Empfehlung von A1. Bei Linf wird der relative Gewinn an
der ersten unterschiedlichen Tupelkomponente berechnet; der primäre Test
bleibt unmittelbar lexikographisch, ohne gewichtete Skalarersatzfunktion.
Fehlende/fehlerhafte Läufe werden nicht stillschweigend ausgelassen.

Der Export enthält vollständige Bestkurven, Endgraphen, Konfiguration,
CPU-Quittungen, Herkunft, Kosten und Längenstatistik. Alle Endgraphen werden
unabhängig nachgeprüft; anschließend wird das erzeugte Archiv wieder gelesen
und mit dem Einzeldatei-Hashmanifest verglichen. Systemberichte und Konsolenlogs
werden nicht automatisch veröffentlicht. Eine 48-Stunden-Hauptkampagne wird
von keinem dieser Befehle gestartet oder freigegeben.

### Prüfstatus

- Sechs bisherige gezielte Kontrollen bestanden.
- Neue Kontrollen: bytegleiche F02/C02- und F04/C08-Reproduktion; Auswahl ohne
  Klone/Trainingsgraphen; Anker-/Linf-Schranken; exakte Sign-/Holm-Rechnung;
  echter Worker mit Pause/Wiederaufnahme und gemeinsamem CPU-Kontingent;
  synthetischer Exporttest einschließlich Ablehnung eines fehlenden Laufpaars.
- Echter Zwei-Prozess-Queue-Test: CPU-Quittungen erfasst, erneuter Aufruf führt
  abgeschlossene Aufgaben nicht erneut aus.
- Verkürzter Gesamtworkflow mit maximal vier Prozessen in der Entwicklungsumgebung
  bis zum 144-Aufträge-Manifest bestanden. Dessen Durchsatz ist **kein Ryzen-
  Benchmark** und wird nicht für die Workerwahl auf dem Ryzen verwendet.
- Separater Codebündeltest bestätigt identische Dateihashes und importierbare
  eingefrorene Abhängigkeiten.

Der nächste lokale Schritt ist die reale Kalibrierung. Der 144-Stunden-
Vergleich ist implementiert, aber noch nicht auf dem Ryzen gestartet.


## Revision 0.4.1: vier Ziele und ereignisbasierter Fortschritt

Am 20.09.2026 vom Nutzer beauftragt: zusätzlich W mit nachrangigem L1,
lexikografisch. Neun gepaarte Seeds je Arm/Ziel, unverändert 144 × 3600
Worker-CPU-Sekunden. Alle vier Ziele verwenden denselben Gründerbestand je Arm;
die Auswahl enthält nun auch einen W/L1-Qualitätsanker. Keine Migration.
W/L1 gilt für Elternwahl, Abstieg, Neutralität, Überlebensauswahl, Bestkurve und
Endpunkttest. Bei A1 wird eine eigene positive W-Änderungsschwelle trainiert
(gepoolt mindestens 32 Beobachtungen, 75-%-Quantil). Nicht verbessernde W-Schritte
bleiben am festen Episodenanker auf höchstens +10 % W und +10 % L1 begrenzt.
Strikte lexikografische Verbesserung bleibt zulässig. Der praktische Effekt
verwendet bei W-Gleichstand die relative L1-Änderung; Holm umfasst acht Tests.
Mit neun Paaren ist die Entscheidung konservativ: neun Siege ohne Niederlage
haben p=1/512, bei acht gleich kleinen p-Werten Holm p=1/64; acht Siege und eine
Niederlage allein reichen bei achtfacher Korrektur nicht (10/512 × 8 = 5/32).

Jeder neue unabhängig geprüfte aktive Bestwert wird mit Worker-CPU-Zeit,
Wanduhrzeit, Zielwert und Wanduhrabstand zum vorherigen Bestwert dieses Laufs
in improvements.jsonl gespeichert. Der Controller zeigt nach fünf Minuten
stiller Bestwert-Anlaufphase alle neuen Ereignisse, Polling alle zwei Sekunden.
Die Ziele stehen bei Einrückung 0/25/50/75 Zeichen; Arm, Variante und Replikat
stehen in jeder Zeile. Der erste Abstand läuft ab Initialisierung der Population;
Pausen zählen zum Wanduhrabstand. Die CPU-Zeit bleibt separat sichtbar.
Die zehnminütigen Status-/Ressourcenmeldungen bleiben erhalten. Nach Resume
beginnt die Konsolen-Anlaufphase erneut; alte Ereignisse werden nicht wiederholt.
Plateauabstände verschiedener Replikate dürfen nicht zusammengerechnet werden.

13 gezielte Kontrollen bestanden, einschließlich W/L1-Reihenfolge,
W-Ausweichgrenzen, Holm für acht Tests, synthetischer 144-Läufe-Auswertung,
Zeileneinrückung, stiller Phase, unvollständigen Logzeilen und CPU-Wiederaufnahme.
Der vollständige verkürzte Workflow weiter oben bezieht sich auf 0.4.0;
dieser ist kein gemessener Ryzen-Durchsatz der Revision.

Walltime: 144/n Stunden ist die Idealrechnung für n kontinuierlich ausgelastete
Worker (24: 6 h; 18: 8 h; 12: 12 h), keine Garantie. Vorbereitung separat:
18340 CPU-Sekunden an oberen Taskkontingenten, darunter ein serieller Zensus
bis 900 CPU-Sekunden. Vor Ryzen-Messung grob 0,5–1 h dafür einplanen und für
Vorbereitung plus Vergleich insgesamt etwa 7–14 h. Auswahl 12/18/24 erfolgt
nach gemessenem Episodendurchsatz. Keine Ableitung einer 48-h-Hauptkampagne.

Bereits eingefrorene 0.4.0-Bundles bleiben unverändert; Git-Pull migriert keine
laufende Kalibrierung. Revision benötigt ein neues Vorbereitungsverzeichnis;
alte und neue Vergleichsresultate dürfen nicht gemischt werden.
