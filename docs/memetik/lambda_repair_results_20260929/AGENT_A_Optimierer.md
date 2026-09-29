# Perspektive A: der Optimierer

Stand: 29.09.2026. Unabhängige Analyse der vorhandenen λ-Reparatur, keine neue Suche und keine Implementierung. Grundlage: PLAN_V2, Modell/Worker 1.2.0, Ergebnisdateien des Nachtlaufs sowie Experimentregeln und GC-02/08/10/11.

## Urteil

Die bestehende Reparatur ist als Mechanismus funktionsfähig, aber noch kein leistungsfähiger Rekordoptimierer. Mehr Zeit in dieselben Fenster allein ist derzeit nachrangig. Die vorrangige technische Frage lautet: **Scheitern große Fenster an fehlender zulässiger Beweglichkeit oder daran, dass der Solver vorhandene Verbesserungen nicht findet?** Ein anderer Seed oder eine beliebige größere Population beantwortet diese Frage nicht.

Die Ausgangsbank hat bereits 24 paarweise nichtisomorphe Gründer. Ein Ausbau nur der Anzahl ersetzt keine zusätzliche Beweglichkeit. Auch die 88 lokalen Optimalitätsmeldungen schließen ausschließlich die jeweiligen eingefrorenen Fenster aus, nicht alle Fenster gleicher Größe oder die Gründer insgesamt.

## Zusätzliche Diagnose aus den Rohdaten

- Die 24er-Fenster sind vollständig erledigt: 43 Solver-Optimalitätsmeldungen, fünf durch Randpropagation starre Fenster. Diese konkrete Fensterbank braucht keine weitere Zeit.
- Von den 40er-Fenstern sind nach dem Nachtlauf noch drei offen; 45 meldeten Optimum. Zusätzliche Zeit brachte zwei weitere Abschlussmeldungen, aber keinen weiteren Kandidaten.
- Alle 48 60er-Fenster bleiben offen. Die nach zwei Stunden berichteten skalaren unteren Schranken, geteilt durch 50000, reichen etwa von 509,31 bis 860,67 (Median 699,63), während die bekannten Kandidaten W über 2000 haben. Dies ist ausdrücklich keine direkte ganzzahlige W-Schranke: L1 steckt ebenfalls in der Zielfunktion. Es zeigt dennoch die außerordentlich große verbleibende Optimierungslücke. Die Aussage „nahe am lokalen Optimum“ wäre unbegründet.
- Der einzige verbesserte Kandidat entsteht im 60er-Defektfenster des Gründers 2077_08 nach rund 78,50 Prozess-CPU-Sekunden; danach wird bis zum Zweistundenbudget keine weitere gespeicherte Verbesserung erreicht. Sein Modell enthält 120871 Variablen und 330732 Constraints; Aufbau dauert rund 10,42 CPU-Sekunden. Zumindest bei diesem Job dominiert nicht der Modellaufbau die Laufzeit.
- `worker.py` erlaubt objective <= incumbent und archiviert Verbesserungen. Daher beweist die unveränderte Bestliste nicht, dass es keine anderen zulässigen Graphen mit gleichem oder schlechterem Score gab. Für die Unterscheidung Starrheit/Suchschwierigkeit fehlt bisher eine gezielte Messung.

## Erste Wahl: ein gepaarter Beweglichkeits- und Verbesserungsversuch

Dies ist mein nächster vorgeschlagener Versuch; noch keine Startfreigabe oder Implementierung.

Alle 24 Gründer und die bestehenden zwei 60er-Fenster pro Gründer beibehalten. Für jedes der 48 Modelle zwei getrennte, gleich budgetierte Entscheidungsfragen stellen:

1. **Beweglichkeit:** Grad14 und λ=1 unverändert hart, genau denselben Rand fixieren, Gründerbelegung durch eine No-good-Bedingung ausschließen; keine Score-Obergrenze und kein Optimierungsziel. Gesucht wird irgendein anderer zulässiger Graph. Summe der vom Gründer abweichenden variablen Kanten >=1 genügt. Ein gelabelt anderer Graph kann zum Gründer isomorph sein; beide Ergebnisse getrennt berichten.
2. **Strikte Verbesserung:** gleiche harten Bedingungen und gleicher Rand, `(W,L1)` strikt kleiner als beim Gründer verlangen und nur Zulässigkeit suchen. Zunächst lexikographische Verbesserung als integer objective <= founder_objective-1. Zusätzlich W und L1 des Treffers berichten, damit reine L1-Verbesserung keinen W-Erfolg vortäuscht.

Mit einer vollen CPU-Stunde je Frage: 96 Aufgaben, 96 CPU-Stunden plus 12 Hilfsstunden. Zwölf parallele Einzelthreads ergeben rechnerisch acht Stunden reine volle Suchzeit; mit Aufbau, ungleichmäßigen Abschlüssen und Audit grob 9–12 Hoststunden, noch keine gemessene Prognose. Hartes Hostlimit 24 Stunden und die erprobten Nachlaufreserven beibehalten. Bei vertretbaren Ressourcen kann das vorab freigegebene Einzelbudget zwei Stunden betragen; man sollte aber nicht aufgrund erster Resultate nur erfolglose Zellen still verlängern.

**Diskriminierende Auswertung:**

- Viele schnelle bewegliche Zeugen, aber kaum Verbesserungen: Rand erlaubt Bewegung; reine Starrheit ist nicht die Hauptursache. Dann Bewegungskandidaten, Distanz und Fensterwahl untersuchen.
- Viele schnelle strikte Verbesserungen: Die bisherige Optimierungs-/Schrankenarbeit ist ein konkreter Ansatzpunkt. Entscheidungsorientierte Iteration mit Warmstarts bevorzugen.
- Beweglichkeit UNSAT und unabhängig zertifiziert: genau dieses Fenster ist vollständig starr. CP-SAT-INFEASIBLE allein bleibt eine unzertifizierte Solvermeldung.
- Beide Fragen überwiegend UNKNOWN: Solver/Modell bleibt der Engpass; keine Landschaftsschlussfolgerung. Erst dann Formulierungsvergleich priorisieren.

Die beiden Fragen sind logisch verschieden. Ihre Laufzeiten liefern einen praktischen Algorithmusvergleich, keine faire Schätzung einer einheitlichen Trefferwahrscheinlichkeit. Die bereits erfolgreiche 2077_08-Reparatur sowie die bekannte 2077→2076-Achtknotenreparatur dienen als positive Funktionskontrollen.

## Zweite Wahl: Fenster nach tatsächlicher Freiheit auswählen

Bisher wachsen beide Regeln entlang vorhandener Kanten; „defect“ priorisiert hohen Fehlergrad. Das muss nicht die Kantenmenge freigeben, die eine gute Reparatur benötigt. Eine neue Fensterbank sollte bei gleicher Größe und denselben Gründern drei Regeln vergleichen: bisherige Defektwahl, Zufallswahl als Kontrolle und Auswahl mit expliziter Berücksichtigung der Randrestriktionen.

Vorab viele deterministisch erzeugte Fenster durch dieselbe notwendige Randpropagation prüfen. Als Auswahlmerkmale dienen verbleibende freie Kanten, Verteilung freier Restgrade und Randzwang. **Freie Variablen sind nur ein Proxy**, kein Beweis beweglicher oder verbesserbarer Fenster; daher die Beweglichkeitsfrage einbeziehen. Auswahlkriterien vor Sichtung produktiver Suchergebnisse einfrieren.

Großzügige Bestätigungsbank: 24 Gründer × drei Regeln × zwei neue 60er-Fenster =144 Aufgaben mit je einer CPU-Stunde, insgesamt 156 CPU-h inklusive Hilfsbudget. Die alte, konkret optimale 24er-/40er-Bank nicht erneut rechnen. Größere Fenster (z.B.72) separat pilotieren, da mehr Freiheit und höhere Modellkosten gleichzeitig steigen und sonst der Vergleich unklar wird.

## Weitere technische Optionen, nachgeordnet

- Auf denselben eingefrorenen Aufgaben die skalare lexikographische Optimierung gegen zweistufige Suche vergleichen: zuerst W minimieren/verbessern, dann L1 bei festem W. Dies ändert die Suchführung, nicht die mathematische Priorität. Ein Vorteil ist unbewiesen und muss gepaart gemessen werden.
- Explizite Propagation der bereits mathematisch geprüften Randfolgen vor dem Modellbau kann Variablen/Produkte eliminieren. Presolve erledigt möglicherweise bereits viel davon; daher Variablen nach Presolve, Zeit bis zum ersten zulässigen Zeugen und Verbesserungen/CPU messen, nicht nur ursprüngliche Modellgröße.
- Warmstarts mit nachgewiesen beweglichen, diversifizierten Graphen einsetzen. Beste Kandidaten weiterhin unabhängig verifizieren. Keine automatisch aus der ersten Trefferbeobachtung nachoptimierte Kontrollgruppe.
- Den neuen W2127-Kandidaten unter frischen Fenstern weiter reparieren, aber als separaten, ausdrücklich adaptiven Mechanismustest. Das ist kein Ersatz für den Rekordarm mit W2076/2077.

## Entscheidungskriterien und Übertragbarkeit

Primär: neuer unabhängig geprüfter Rekord W<2076. Sekundär: Zahl verbesserter Gründer, Verteilung ΔW/ΔL1, neue kanonische Klassen, Zeit bis Treffer, bewegliche Fensterquote und offene Aufgaben. Erfolg des Betriebscontrollers getrennt von wissenschaftlichem Erfolg ausweisen.

GC-08 verhindert den Fehlschluss vom begrenzten Negativbefund auf die gesamte Methode. GC-10 verlangt getrennte Kennzeichnung von Versuch, logischer Frage und erfülltem Aufgabenbudget. GC-02 sichert lokale, vollständig verbuchte Nachlauftoleranz. GC-11 verlangt weiterhin Budgetprojektion statt scheinpräziser Fertigstellungsprognose.

**Priorisierung:** zunächst die bisher fehlende Unterscheidung Bewegung versus Verbesserung nachholen; bei nachgewiesener Beweglichkeit die Fensterwahl und Entscheidungsorientierung verbessern. Eine dritte unveränderte Zeitverdopplung würde diese Unklarheit voraussichtlich schlechter auflösen.
