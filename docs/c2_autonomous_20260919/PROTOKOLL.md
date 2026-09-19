# C2 Office: autonomer Vergleich 1.1.0

19. September 2026. Forschungsbasis 40390caa48175fde4f708de71599bb0f391046a7.
Ziel: Entscheidungsergebnisse und CPU-Kosten derselben festgelegten Aufgaben
vergleichen. Technische Funktionsprüfung und Leistungsnachweis werden getrennt.
Keine UNSAT-Zertifizierung, kein behaupteter Involutionsausschluss.

## Vorab festgelegter Versuch

| Phase | Fälle | Varianten | Seeds | Aufgaben je Kombination | CPU-Budget je Aufgabe | Gesamt |
|---|---:|---:|---:|---:|---:|---:|
| Wurzeln | 3 | 4 | 2 | 1 | 600 s | 24 Aufgaben, 4 CPU-h |
| Cubes | 3 | 4 | 2 | 8 | 120 s | 192 Aufgaben, 6,4 CPU-h |

Fälle: 111111, 222, 6. Varianten: Totalizer, +Lex, +Dreierklauseln, +beides.
Seeds 0 und 1. Deterministische gemischte Reihenfolge mit Scheduling-Seed 20260919.
Die Cube-Phase folgt automatisch auf die Wurzelphase. Zwei Solver gleichzeitig,
soweit die RAM-Zulassung es erlaubt; Randzeiten einer Phase können einen Slot haben.
Die tatsächlich verfügbaren Ressourcen und gemessenen Zeiten bleiben im Bericht.

Nominal höchstens 10,4 CPU-h, also etwa 5,2 Stunden bei zwei verfügbaren CPUs,
zuzüglich Vorbereitung, Protokollierung und Export. Laufzeit ist keine Garantie:
Hintergrundlast und Speichergrenzen können verzögern oder zu einer Pause führen.
CPU-Überwachung alle 0,5 Sekunden; Kernel-Softlimit am Budget, Hardlimit zwei
Sekunden darüber für Abschluss/Abbruch. Diese kleine Abbruchreserve ist zusätzliche
reale Rechenzeit und wird durch wait4 mitgemessen.

## Gemeinsame Cube-Abdeckung

Die Auswahl wurde VOR jedem Versuch ausschließlich auf den drei gepinnten
Totalizer-CNFs berechnet, ohne Lex- oder Dreierklausel-Ergebnisse zu verwenden.
An jedem inneren Knoten wurden acht gleichmäßig über die noch freien Primärbits
verteilte Kandidaten beidseitig durch UP geprüft. Priorität: beide Seiten offen,
dann größeres Minimum der Fixierungen, dann kleinere Differenz, dann kleinere ID.
Insgesamt 113 UP-Abfragen pro Fall, 339 insgesamt. Dies ist eine Heuristik für
informative Teilprobleme, keine Garantie ausgewogener SAT-Suchschwierigkeit.

Für jeden Fall wird ein vollständiger binärer Baum der Tiefe 3 aufbewahrt, mit
beiden Vorzeichen an jedem Split. Der unabhängige Strukturcheck prüft den ganzen
Baum, die Pfade, frische Splitvariablen, acht Blätter und exakte Abdeckungsgewichte.
Das Gewicht bezieht sich allein auf vollständige beschriftete Bitbelegungen,
NICHT auf den Anteil tatsächlicher Graphlösungen oder einen Beweisfortschritt.

Alle acht Blätter bleiben bei jedem Fall unter Basis-UP offen. Damit besteht
diese Vorprobe nicht überwiegend aus sofort widersprüchlichen Blättern. Office
prüft die acht Blätter jedes Falls noch einmal gegen dieselbe Basis. Die komplette
Liste steht in results/c2_autonomous_20260919/cube_plan.json. Die Auswahl wird
nicht nach Kenntnis günstiger Variantenresultate verändert.

Für alle Varianten und Seeds sind diese Cubes identisch. Die Abdeckung ist
auch für die Lex-Formel vollständig. Einzelne Lex-Cubes können allein durch
Vertreterwahl leer werden; ihre schnelle Schließung ist deshalb nicht mit einem
entsprechend großen Fortschritt im ursprünglichen beschrifteten Problem identisch.
Berichtet werden die volle Abdeckung, die CPU-Kosten und die offenen Seiten des
ersten Splits. Ein verbleibender dominanter Ast wird sichtbar, aber aus acht
Blättern kann keine allgemeine Härteverteilung rekonstruiert werden.

## Ressourcen und Isolation

- Bestehender, per SHA256 geprüfter Office-Solver 2.2.1; kein Neubau.
- Bestehende Typ-6-CNFs werden per Hash geprüft und als unveränderte Dateien
  wiederverwendet. Die beiden fehlenden Fälle werden automatisch erzeugt.
- Standardbibliothek Python 3 plus vorhandenes g++; keine neuen Pythonpakete.
- Höchstens zwei Solver, nice=10, virtueller Adressraum je 1536 MiB, keine Core-Dumps.
- Kein solverinternes -t: CPU-Budget aus /proc, Kernelgrenze und eigene
  Wandzeit-Notgrenze von 4*CPU-Budget+30 Sekunden. Dadurch keine Abhängigkeit
  von der zuvor beobachteten SIGALRM-Behandlung der -t-Option.
- Mindestens 3 GiB MemAvailable für die Vorbereitung, 2,5 GiB zur Zulassung
  eines neuen Solvers. Während der Suche Stopp eigener Kinder bei unter 1 GiB.
- Mindestens 5 GiB Linux-Reserve vor Start/periodischer Messung, 2 GiB harte
  Laufreserve. Windows C: mindestens 20 GiB, tatsächlich über PowerShell gemessen.
  Windows-Probe hat einen Timeout; kein Ersatz durch virtuelle Linux-Werte.
- Neue andere erkennbare Python-/SAT-Prozesse führen zu einer Pause der eigenen
  Suche. Bereits laufende Memetik wird nicht beendet oder umkonfiguriert.
- Pro Solverlog hart 16 MiB; keine Proof-Dateien. Abgeleitete temporäre Cube-CNFs
  werden nach Ergebnisablage entfernt. Basis-CNFs, Logs und Resultate bleiben.
- Eigene Prozessgruppen; PR_SET_PDEATHSIG verhindert weiterlaufende Solverkinder
  beim plötzlichen Ende des Controllers. Ein Dateilock verhindert Doppelstarts.

Die konservative Erkennung anderer Forschungsprozesse kann auch einen harmlosen
Pythonprozess melden. Ein solcher Fall wird transparent angehalten, nicht durch
Beenden des fremden Prozesses gelöst. Die Experimentumgebung ist kein allgemeiner
Scheduler für konkurrierende Nutzerkampagnen.

## Wiederaufnahme und Ergebnisbehandlung

Ein neuer Aufruf desselben Starters prüft Paket, Solver, CNFs und Aufgabenplan.
Abgeschlossene Budgetaufgaben mit unverändertem Ergebnislog werden wiederverwendet,
auch wenn sie TIMEOUT/UNKNOWN sind. Sie sind mathematisch offen, aber ihr vereinbartes
Experimentbudget ist verbraucht. Eine unterbrochene Aufgabe startet dagegen als
neuer Versuch von vorne. Es gibt keine behaupteten internen Solvercheckpoints.
Alle Versuche behalten eigene Logs; unvollständig protokollierte CPU-Kosten werden
nicht erfunden. Erfasste CPU-Zeit aller Versuche wird gesondert ausgewiesen.

UNSAT ohne Proof bleibt UNSAT_UNCERTIFIED. SAT-Ausgaben werden unmittelbar am
rekonstruierten 99-Knoten-Graphen geprüft; ein bestandener Check beendet die weitere
Suche zur unabhängigen Inspektion. Technische Fehler und Ressourcenausfälle stoppen
die Kampagne, gelten nicht als mathematische Entscheidungen und sind keine Niederlage
einer Variante. Vorhandene Berichte oder finale Beweise werden nicht gelöscht.

Alle zehn Minuten Status und nominelle Restzeit, zusätzlich eine kurze Meldung je
Start/Ende. Abschluss oder kontrollierte Pause erzeugt summary.json, REPORT.md und
ein ZIP mit Code, festem Plan, Cube-Abdeckung, Ressourcenmessungen und allen Logs.
Die großen regenerierbaren CNFs werden nicht in das ZIP kopiert, ihre Hashes und
Encoder sind enthalten. Wenn möglich wird das ZIP mit Hashprüfung nach
C:/Users/rb/Downloads kopiert. Alle Dateien bleiben auch im WSL-Arbeitsordner.

## Auswertung und Grenzen

Bericht pro Phase/Fall/Variante, zusätzlich nach Seed. Ergebnisse umfassen
Entscheidungen, zensierte Aufgaben, reale CPU-Zeit, Spitzen-RSS und offene
Erstsplitseiten. Keine automatische Siegerwahl aus Konfliktzahlen oder Bitquoten.
Wenn alle Wurzeln offen bleiben, ist deren Laufzeitvergleich unentschieden.
Cube-Ergebnisse müssen im Zusammenhang der vollständigen Abdeckung bewertet werden;
eine höhere Rohzahl geschlossener Blätter allein genügt nicht. Zwei Seeds sind ein
Screening. Vor einer langen Kampagne bleibt Bestätigung auf weiteren Aufgaben oder
einem zurückgehaltenen Seed erforderlich. Kein automatischer Proof-/Langlauf.

## Ausgeführte Kontrollen

Die Struktur aller drei Cube-Bäume, beschädigte Gegenbeispiele, identische Aufgaben
über Varianten/Seeds und das Gesamtbudget wurden geprüft. Echte kleine Kindprozesse
prüften die Zwei-Prozess-CPU-Begrenzung und Unterbrechung. Ein kleiner künstlicher
Solver durchlief die gesamte Aufgabensteuerung; Wiederaufnahme erzeugte keine
doppelten Versuche. Manipulierte Ergebnislogs wurden zurückgewiesen. Cube-CNF-
Header, Klauselpräfix und angehängte Annahmen wurden unabhängig gelesen.

Dies waren hier ausgeführte Controller-/UP-Kontrollen, keine Conway99-SAT-Kampagne
auf Office. Der echte Versuch wird erst durch den Nutzerstart ausgeführt.
