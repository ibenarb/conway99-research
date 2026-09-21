# λ-Vergleich 0.2.0: B0, Pivot, Tabu und Dreierzyklus

Umsetzung des am 21.09.2026 freigegebenen nächsten Ryzen-Versuchs.
Vollständiges Design und Grenzen: `docs/memetik/lambda_compare_20260921/DESIGN.md`.
Die alten Pakete bleiben unverändert. Keine Office-Arbeit, keine Ω-Kampagne.

## Umfang

12 neue gepaarte Seeds × 4 Ziele × 4 Verfahren × 3600 Worker-CPU-Sekunden:
**192 Jobs, 192 CPU-Stunden Vergleichsbudget**, 18 Worker.
Kontrollen: höchstens eine zusätzliche Worker-CPU-Stunde, tatsächliche Zeit
separat ausgewiesen. Controller und Windows-Abfragen zusätzlich, ebenfalls
getrennt. Es gibt keine automatische Budgetverlängerung.

| Verfahren | Suchregel |
|---|---|
| B0 | Fast-A0-Referenz, alte Zugquelle, Stichprobe 32, 45/75-s-Phasengrenzen |
| P | Apex ∪ Pivot, gleichverteilte Perturbationszüge, vollständiger strikter Abstieg |
| T | Vollständiges Apex ∪ Pivot, Attribut-Tabu, Aspiration, Archiv-Restarts |
| TC | Wie T, zusätzlich vollständiger allgemeiner Dreierzyklus |

B0/P besitzen Population 16. T/TC führen je einen Suchpfad. Alle erhalten
dieselben 16 validierten Gründer einschließlich alter Endpunkte, ohne die neuen
Reviewer-Rekorde einzupflanzen. Aus dem Mengenparameter Population 16 wird keine
allgemeine Empfehlung für eine optimale Populationsgröße abgeleitet.

## Bedienung

Python ist auf Ryzen `/home/rb/conway99_workspace/venvs/memetik/bin/python`.
`run.py ACTION DIRECTORY` unterstützt:

- `preflight`: Umgebung, CPU-Affinität und tatsächliche Hostreserven prüfen.
- `prepare`: neues Verzeichnis mit unveränderlichem Quellbundle und Manifest
  anlegen; **startet nicht**.
- `launch`: Controller abgekoppelt starten; auch für saubere Wiederaufnahme.
- `run`: Controller im Vordergrund; Ctrl+C pausiert seine eigenen Vergleichsworker.
- `status`: gespeicherten Status anzeigen; Zeitstempel/Log prüfen, kein Live-Beweis.
- `evaluate`: vollständigen Endpunkt samt Receipts unabhängig nachprüfen.
- `extend --cpu-hours H`: neuen **kumulativen Stundenwert pro Job** vorbereiten,
  nachdem alle Jobs vollständig und geprüft sind. Beispiel H=2 bedeutet insgesamt
  384 Vergleichs-CPU-Stunden, also 192 zusätzliche; startet selbst nichts.
- `export`: komplettes ruhendes Laufverzeichnis mit Quellbundle, SQLite-Archiven,
  Ergebnissen und Inhaltsprüfsummen als benachbartes `.tar.gz` sichern.

Nach `prepare` laufen `launch`, `run`, `evaluate`, `extend` und `export` aus dem
gehashten Bundle; spätere Repository-Änderungen verändern diese Kampagne nicht.
Ein `git pull` erweitert also keine laufende Suche.

Je manueller Rückmeldung wird dem Nutzer nur **ein ausführbarer Bash-Einzeiler**
gegeben. Vor dem Start zuerst die Ryzen-Vorprüfung ansehen. Kein blindes Entfernen
von `active.json`, Receipts oder Locks bei Problemen. Ein Lock allein ist kein
laufender Prozess; der Kernel-Lock entscheidet, verbleibende Active-Marker weisen
auf ungeklärte CPU-Abrechnung hin.

`controller.log` enthält Verbesserungen nach 60 Sekunden stiller Anlaufphase,
vier Ziele um jeweils 25 Zeichen eingerückt. Variante/Seed/Ziel bleiben getrennt.
Alle zehn Minuten: Budgetstatus und aus gemessenem Durchsatz geschätzte Budget-ETA.
Ein `tail -f` bleibt nach dem Suchende aktiv; Ctrl+C beendet dann nur die Anzeige.

## Speicherung und Fortsetzung

Jeder Job hat ein SQLite-Archiv für alle akzeptierten, unabhängig validierten
Isomorphieklassen sowie alle beobachteten Rekorde in den vier Zielen. Das ist
**kein Archiv sämtlicher nur bewerteter Nachbarn**. Es gibt kein Klassenlimit 64,
keine zufällige Verdrängung und keinen pauschalen 2-GiB-Stopp. Archives sind lokal
pro Job; kein Austausch zwischen Verfahren, Seeds oder Zieljobs.

Checkpoint: Population, Kinder der laufenden Generation, Episode/Phase, aktueller
Pfad, Tabu-Verfall, Restartzähler, Zufallszustand, erzeugter Nachbarschaftspräfix,
Rekorde und Messpunkte. Eine unterbrochene Enumeration wird deterministisch bis
zum Präfix wiederholt; diese zusätzliche CPU-Zeit wird gezählt. Ein Zeitlimit wird
nicht als lokales Minimum bezeichnet. Für B0 kann bezahlte Wiederholungszeit die
45/75-s-Phasengrenze früher erreichen: Zustandsfortsetzung bedeutet keine Garantie
identischer gesamter zeitbegrenzter Trajektorien bei beliebig vielen Pausen.

Messpunkte 600/1800/3600 Sekunden gehören zu einer kontinuierlichen Trajektorie.
Die letzten fünf Budgetsekunden stehen der Finalisierung zur Verfügung. Bei einer
späteren Verlängerung verfällt ungenutzte Abschlussreserve des alten Endpunkts;
sie wird ausdrücklich als `closed_reserve_cpu_seconds` ausgewiesen und nicht als
gemessene CPU ausgegeben. `cpu_seconds` ist die Summe der echten wait4-Messungen,
`budget_cpu_seconds` addiert ausschließlich solche bereits geschlossenen Reserven.
Damit wandern nachträgliche Verbesserungen nicht in alte Messpunkte zurück.

Saubere Pausen ziehen echte CPU-Kosten ab; keine erneuten 3600 Sekunden pro Start.
Ein unkontrollierter Controller-/Workerabbruch erfordert Diagnose und ist nicht
stillschweigend fortsetzbar. Vor Verlängerung werden alte Task-, Result-, Receipt-
und Checkpointdateien separat gesichert. Das SQLite-Archiv wächst anschließend
weiter; seine alten Inhalte werden nicht gelöscht. Alte Archivdateien werden dabei
nicht vollständig dupliziert, ihr damaliger Hash steht im gesicherten Receipt.

## Kontrollen

`controls.py` prüft Apex gegen den alten Generator, Pivot gegen vollständige
Brute-Force-Prüfung, alle Scores/Inverse/λ-Invarianten auf 19 realen Zuständen,
Reviewer-Abstiege sowie deterministische Fortsetzung. `integration_tests.py`
prüft echte Workerprozesse, saubere Pause, Wiederaufnahme, Erweiterung und
fail-closed Receipts mit kleinen Testbudgets. Nur dessen Testklasse ersetzt die
Hostabfrage. Produktion hat keinen Schalter zum Abschalten der Hostwächter.

Die positive Erfolgsfall-Kontrolle benutzt den bekannten srg(9,4,1,2) mit expliziten
Testparametern sowie injizierten Testantworten für die Controller-Verkabelung.
Produktiv bleiben n=99 und Grad 14 fest. Ein Conway99-Erfolg wird dadurch weder
behauptet noch vorgetäuscht.
