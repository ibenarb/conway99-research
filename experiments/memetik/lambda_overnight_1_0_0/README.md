# Lambda Overnight 1.0.0

Am 25.09.2026 freigegebener Übernachtlauf: acht neue unabhängige Seeds,
je 7 CPU-Stunden, zusammen maximal 56 Such-CPU-h plus 1 Hilfs-CPU-h.
Erwartete reale Laufzeit rund 7–8 Stunden bei freiem Ryzen wie im letzten Lauf.
CPU-Limits sind keine harte Wallclock-Frist: konkurrierende Last kann verlängern.
Die frühere Zwei-Stufen-Freigabe entfällt durch den Auftrag zum durchgehenden
Übernachtlauf. Nach vier Stunden nur Messpunkt, keine erfolgsabhängige Pause.
Keine automatische Budgetverlängerung nach sieben CPU-Stunden.

## Feste Ausgangsbanken

Quelle: ryzen_lambda_frontier_100_20260924_verified.tar.gz,
SHA256 682e335b7d5eb27f30bbedbd1d0a21c7fa100897cd44194e63f5b2836c1319ca.

| Bank | Quelljobs | Verfügbare Klassen | Gewählte Klassen | W-Spanne | Wiederholungen |
| --- | --- | ---: | ---: | --- | ---: |
| A, W2081 | F-W2096-1 und F-W2096-3 | 23 | 16 | 2081–2108 | 6 |
| B, W2092 | F-W2101-0 bis F-W2101-3 | 40 | 16 | 2092–2101 | 2 |

Vereinigung von Bestgraphen und Endpopulationen der jeweiligen Quelljobs;
Sortierung (W,L1,state), erste Repräsentanten je kanonischer Klasse, erste 16.
Keine Ergänzung aus älteren Archiven nötig. Alle 32 Klassen nachgerechnet,
keine Überschneidung zwischen den beiden Banken. Das bedeutet keine unabhängigen
Suchbecken. Vollständige Kandidaten und SHA256 der Quellresultate stehen in
FRONTIER_BANKS.json. Das Paket benötigt keine alten Laufverzeichnisse.
Neue Seeds: 2026092800–2026092805 für A, 2026092806–2026092807 für B.
Innerhalb jeder Bank identische Gründer, unterschiedliche RNG-Seeds, kein alter
RNG-Zustand übernommen. 6:2 dient der Suche, nicht einem kausalen Familienvergleich.

## Suche und Entscheidung

P unverändert: Apex-/Pivot-Perturbationen der Längen 2–4 / 5–12 / 13–32,
Gewichte 4:3:2, lokaler Abstieg nach (W,L1), bisherige 16er-Population und Selektion.
Kein PCesc, Crossover, neue Sprungmutation oder Migration.
Andere Normrekorde und Archive bleiben erhalten, ersetzen das W-Kriterium nicht.

Primärer Erfolg: mindestens zwei Jobs mit unabhängig verifiziertem best.W < 2081.
0 Treffer: PAUSE_W_FRONTIER; 1: SINGLE_SIGNAL_REVIEW_ONLY;
2 oder mehr: REPEATED_SIGNAL_REVIEW_ONLY. Entscheidung erst am Laufende.
Identische erfolgreiche Klassen werden separat von der Zahl erfolgreicher Jobs
gezählt. Ein negatives Ergebnis beweist keine Erschöpfung; Wiederholung keine
strukturelle Vielfalt. Eine exakte verifizierte Lösung stoppt die Kampagne und
wird doppelt gesichert. Technische Ressourcenprobleme führen zu Diagnose/Pause.

Messpunkte bei 1, 2, 4, 6 und 7 CPU-h je Job; Status alle 10 Minuten mit ETA.
Windows-Host-Monotonzeit bleibt maßgeblich, da WSL-Monotonzeit messbar driftet.
Reale CPU-Abrechnung per wait4; fünf Sekunden Schlussreserve zählen zum Budget.
Acht Suchworker, jeweils 1 GiB Adressraumlimit, bestehende Speicher-/Diskreserven.
Hilfsbudgets: Hostproben 540 CPU-s, Kontrollen 1260 CPU-s, Infrastruktur 1800 CPU-s.

## Bedienung

ZIP lambda_overnight_1_0_0.zip unter ~/conway99_workspace entpacken und start.py
mit ~/conway99_workspace/venvs/memetik/bin/python starten.
Reihenfolge prepare → check → launch; keine Überschreibung vorhandener Daten.
Run: ~/conway99_workspace/ryzen_lambda_overnight_100_20260925.
CLI run.py: status, pause, launch (Wiederaufnahme), evaluate, export.
Das Paket benötigt pynauty==2.8.8.1 in der vorhandenen Ryzen-Umgebung.
Die isolierte Cloud-Audit-Umgebung wird über tools/memetik/audit_python.py betreut;
sie verändert keine Ryzen-Fingerprints oder laufenden Umgebungen.

## Prüfung

TEST_RESULTS.json dokumentiert kurze echte Suchworker mit Pause/Wiederaufnahme,
Hash-Manipulationsnegativen, Lösungssicherung sowie den Acht-Job-Kampagnentest
mit den neuen Banken. Windows-Host und Ressourcen werden ausschließlich im
lokalen Test simuliert; echte Hostproben erfolgen auf dem Ryzen vor dem Start.
Suchworker und Operatorengine bleiben byteidentisch zum Frontier-Paket.
