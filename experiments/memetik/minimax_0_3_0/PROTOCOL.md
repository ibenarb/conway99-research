# Office Minimax 0.3.0

Eigenständige Escape-Kampagne im Zweig memetik, kein Populationspilot.
Zielrechner: rb-PC, Ubuntu/WSL, ungefähr 4,8 GiB RAM und 8 GiB Swap.

## Forschungsziel

HoG57338: erster Graph mit F<2836; B_escape_W2082: erster Graph mit W<2082.
Die Suche priorisiert die minimale bekannte maximale Zielfehlerhöhe eines Wegs.
Relaxation: b(v) = min(b(v), max(b(u), Zielwert(v))).
Ein Zustand wird erst nach vollständiger Enumeration aller Familien endgültig
abgeschlossen. Neue günstigere Wege zu noch offenen Zuständen ersetzen Eltern
und Barrierenwert. Gleichstände: Zielfehlerwert und Einfüge-ID. Beschriftete
graph6-Identität; kein Isomorphiequotient und keine zusätzliche Symmetriebedingung.
Kein Tiefenlimit, keine Fehlerschranke, keine feste maximale Zustandszahl.

Wird ein besserer Graph als minimaler offener Eintrag entnommen, ist sein
Barrierenwert minimal unter allen Verbesserungswegen im Katalog. Die gespeicherte
Weglänge ist dabei NICHT notwendig minimal. Jeder Ergebnisweg wird vor Abschluss
unabhängig mengenbasiert geprüft und aus seinen Kantenänderungen rekonstruiert.
Ohne Fund bezeichnet frontier_peak die aktuelle untere Schranke für die
maximale Fehlerhöhe eines etwaigen Verbesserungswegs. Sie ist keine Erfolgsprognose.

Operatoren und Armverträge bleiben unverändert: Ω 4x4/4x6/6x6-Produkte,
λ Apex/Rotation. PH=2J−(C+I)P im festen Ω-Rahmen, λ=1 auf jeder Kante im λ-Arm.
W ist das ausdrücklich beauftragte B-Diagnoseziel, kein neuer Populationsarm.

## Startzustand und alte Checkpoints

Die geschlossenen Komponenten unter F<2928 (85 HoG-Zustände) und W<2094
(13 B-Zustände) werden samt vollständig materialisierter direkter Nachbarschaft
übernommen. Dazu wurden ihre bekannten inneren Nachbarschaften in der
Vorbereitung einmalig erneut erzeugt, um zuvor nicht gespeicherte Randübergänge
zu ergänzen. Die Familienzensen stimmen exakt mit den vorherigen Zertifikaten
überein. Alle Seed-Kennzahlen, einschließlich aller Randgraphen, wurden
unabhängig mit Mengen gemeinsamer Nachbarn nachgerechnet. Harte Bedingungen
werden bei der Erzeugung jedes Nachbarn geprüft.

HoG beginnt mit 2835 gespeicherten Zuständen, 85 abgeschlossenen Expansionen,
Frontierhöhe 2928. B beginnt mit 3269 Zuständen, 13 abgeschlossenen Expansionen,
Frontierhöhe 2094. Diese Zahlen sind nicht mit den großen BFS-Datenbankständen
gleichzusetzen: 0.3.0 verwendet eine eigene, korrekt initialisierte Minimax-Ablage.
Die vollständigen alten BFS-Checkpoints bleiben unverändert als Forschungsdaten
erhalten. Ihre Reihenfolge und Einzel-Elternpfade werden nicht als Minimax-Labels
übernommen. Die alte Breitensuche wird nicht erneut ausgeführt.

## Laufzeit und Ressourcen

Zwei Worker, einer je Ziel, gemeinsames absolutes Ende 34 Stunden nach Beginn
des Startbefehls (einschließlich kurzer Initialisierung). Ein früherer Fund oder
Komponentenabschluss beendet die jeweilige Aufgabe. Kein automatischer
Neustart mit neuem Budget. Wiederaufnahme nach Prozessabbruch behält dieselbe
Frist bei; Schlaf-/Ausfallzeit verlängert sie nicht. Ende wird kooperativ an
häufigen Prüfpunkten umgesetzt, anschließend folgen Transaktionsrollback und
Abschlussprotokoll; einige Sekunden Abschlusszeit sind möglich.

Je Worker 896 MiB Adressraumlimit, insgesamt grob unter 2,2 GiB zuzüglich
Linux-Dateicache. Keine Garantie für eine bestimmte Zustandszahl. SQLite wächst
auf Platte; Stopp bei weniger als 10 GiB freiem Platz auf Linux oder Windows
bzw. weniger als 512 MiB systemweit verfügbarem RAM. Keine willkürliche
Millionen-Zustandsgrenze. Bei Speichermangel endet die Aufgabe kontrolliert
unvollständig. Laufende Office-/Ryzen-Fremdprozesse werden nicht verändert.

Die erwartete produktive Wandzeit ist bis zu 34 Stunden. Mathematischer Fund,
Barrierenanstieg und erreichbare Zustandszahl sind nicht zuverlässig vorhersagbar.
Statusdateien spätestens alle zehn Sekunden pro Worker, Controller alle zwei
Sekunden; Konsolenbericht alle zehn Minuten. Restzeit ist Zeit bis zur gemeinsamen
Frist und wird nicht durch die Workerzahl geteilt.

## Betrieb

Nur Python-Standardbibliothek, Linux/WSL, Python 3.10 oder neuer. Kein pip auf Office.
Zipapp in einem dauerhaften Verzeichnis belassen. start legt ein neues Verzeichnis
unter ~/conway99_workspace/conway99_minimax_office_0.3.0/runs/ an und trennt den
Controller vom Terminal. status, resume und export verwenden den aktiven Lauf.
Gleichzeitiger zweiter Start bei unerledigter Kampagne wird verhindert; Controller
und Worker besitzen eigene Dateisperren. SIGHUP wird ignoriert. Terminalschließen
ist möglich; Windows/WSL müssen zum Rechnen aktiv bleiben.

SQLite DELETE-Journal, synchronous=FULL und atomare JSONs. Eine Expansion ist eine
Transaktion: Abbruch verwirft nur deren unvollständige Änderungen. Nach SIGKILL
stellt SQLite beim Öffnen das Journal wieder her. CPU-Zähler können bei hartem
Abbruch um die letzte Berichtsperiode abweichen; die absolute Endfrist bleibt exakt.
export wird nur bei gestoppter Kampagne und freien Prozesssperren zugelassen;
Ziel ist Windows-Downloads, ersatzweise das Kampagnenverzeichnis.

Status FINISHED bedeutet beide Aufgaben regulär beendet; WALLTIME_LIMIT ist
kein Unmöglichkeitsbeweis. STOPPED/ERROR/INTERRUPTED verlangen Prüfung; resume
setzt einen unterbrochenen Lauf fort und erweitert kein abgeschlossenes Budget.

## Gezielte Prüfung

- Minimax-Ergebnis gegen unabhängige Erreichbarkeit bei aufsteigenden Schwellen
  auf einem Testgraphen: längerer Barriere-2-Weg schlägt kürzeren Barriere-9-Weg.
- Absenken eines bestehenden offenen Wegwerts und Transaktionsrollback.
- Seed-Import: exakt 85/13 innere Zustände abgeschlossen; Startfrontier 2928/2094.
- SIGKILL während einer echten HoG-SQLite-Expansion: bitgenau dieselben logischen
  Knoten nach Journalwiederherstellung; Wiederaufnahme erzielt neuen Fortschritt.
- Anschließendes SIGTERM: konsistenter unterbrochener Status und exakte SQL-Zähler.
- Hintergrund-/Fristtest mit zwei echten Aufgaben und 36-Sekunden-Frist; siehe
  detached_test_report.json. Der Test hält nur die äußere Containerumgebung
  offen, während der start-Aufruf selbst beendet ist.

Tests sind gezielt auf die neue Suchordnung und Dauerhaftigkeit begrenzt.
Keine erneute Vollprüfung der abgeschlossenen Office-Breitensuchen.

## Reproduktion

build.py erzeugt die Zipapp deterministisch aus den hier enthaltenen Quellen
und beiden Seed-Dateien. manifest.json bindet deren Hashes an die Version.
Die Seed-Erzeugung build_seeds.py erwartet die im vorigen Analyseverzeichnis
abgelegten unkomprimierten Sublevelzertifikate und die Quellen von 0.2.2.
Die eingefrorenen Seeds sind vollständig enthalten; zur normalen Paketbildung
und zum Office-Betrieb müssen sie nicht neu erzeugt werden.
