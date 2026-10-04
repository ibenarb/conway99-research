# ROOT8105: Abschluss, Modellabgleich und Entscheidungsgrundlage

Stand: 04.10.2026. Status: Auswertung abgeschlossen; Fortsetzung nur vorgeschlagen, noch nicht beschlossen oder gestartet. Autor: Codex. Primäre Fragestellung: Wie breit wächst eine vollständige, zertifizierbare Augmentation, und ist sie auf Ralphs Ryzen handhabbar?

## 1. Quellen und Evidenzstufen

1. Nutzerexport `ROOT8105_Abschlussberichte.tar.gz`: unverändert in diesem Verzeichnis; die fünf enthaltenen Dateien byteidentisch unter `raw/`. Archivhash und nachgerechnete Kennzahlen in `DERIVED_METRICS.json`; Reproduktion mit `python3 audit_results.py` im Dokumentverzeichnis.
2. Ursprünglicher Pilot 1.0.1: Commit `7c664ebdbf94254179b74eaa523c5bc2150054f5`, insbesondere `experiments/memetik/root8105_pilot_1_0_1/{core,worker,proof,report,completion}.py`.
3. Recovery 1.0.2: Commit `036c108dd7176909cd7f9544d48a4daa1f8da1a2`. Mathematische Such-/Proofquellen blieben unverändert; fehlende Jobs und Proofphase wurden nachgeholt.
4. Experimentregeln: Commit `611be0b0bc14acf7e0dfd4dfe40db13b27487271`, `docs/EXPERIMENT_RULES.md` Version 1.1 und GC-19. Laufende/fixierte alte Pakete wurden durch diese spätere Regel nicht umgeschrieben.
5. Drei angeforderte, vollständig gelesene Commits des Parallelzweigs:
   - `efe29fd5aee3a79608f920e498a5279c6b7f4cc7`: `docs/memetik/H_FIBRE_INVESTIGATION_2026-10-04.md` (387 Zeilen).
   - `01e695903f6b6d1fa400e1e73ee16611cba7a500`: `results/memetik/H_FIBRE_INVESTIGATION_20261004.json` (71 Zeilen).
   - `34c3dbebf0d3748420e43abd3930f72df044e9b5`: `docs/augmentation/AUGMENTATION_PILOT_MEMETIK_HANDOFF_2026-10-04.md` (70 Zeilen).

Die drei Commits sind aufeinanderfolgende Dokumentationsschritte desselben Untersuchungspfads, keine drei unabhängigen Reproduktionen. Sie enthalten Berichte und Paket-Prüfsummen, aber nicht die zugehörigen vollständigen H-Zeugen, Move-Kataloge, Solverläufe und Prüfprogramme. Ihre mathematischen Resultate werden hier als dort berichtete Ergebnisse übernommen, nicht als in diesem Review neu bewiesen.

Der aktuelle Export enthält keine `closure.cnf`, DRAT-Dateien, Checkerlogs oder Einzel-`certificate.json`. Die 512 erfolgreichen Zertifizierungen sind durch konsistente Receipts und Berichtszähler dokumentiert, in dieser Auswertung aber nicht erneut mit dem Checker ausgeführt. `audit_results.py` prüft Konsistenz, keine Beweise. Der ursprüngliche Root-Audit (8105 Klassen, Orbit-Summe 56.011.010) gehört zum früher dokumentierten Fundament und wurde hier ebenfalls nicht wiederholt.

## 2. Vollständiger Pilotabschluss

128 ausgewählte Rootklassen, je ein ordered- und dynamic-Job; je 3600 CPU-Sekunden im historischen Versuch. 256 Suchjobs und 512 Proofjobs abgeschlossen, alle Prozess-Endcodes 0.

| Kennzahl | Ergebnis |
|---|---:|
| Suchstatus CPU_LIMIT_UNKNOWN | 256 |
| PROJECTED_COVERAGE_DRAT_VERIFIED | 512 |
| Maximale beobachtete Tiefe | 16 |
| Beobachtete Projektionszeilen | 1.447.471.813 |
| Reine Projektionsdaten | 33.748.941.099 Bytes |
| Mittlere Bytes je Projektionszeile | 23,3158 |
| Such-CPU | 256,006644 Stunden |
| Proof-CPU laut Jobbelegen | 0,857472 Stunden |
| Nebenarbeit laut Ledger | 19,398458 Stunden |
| Gesamtabrechnung | 276,262573 Stunden |
| Zertifizierte Root-Ausschlüsse | 0 |

Die Recovery ergänzte die fünf im ursprünglichen Lauf nicht gestarteten Suchjobs und alle Proofjobs. Die ursprüngliche Kampagne hatte bereits 19,3444 CPU-Stunden Nebenaufwand verbraucht. Der alte rekursive Dateiscan ist als skalierender Mechanismus im Code belegt; sein genauer Anteil wurde nicht profiliert. Die Recovery verwendete begrenzte Scanabschnitte und schloss auf Zielhardware ab. Das bestätigt diesen Lauf, keine universelle Langzeitgarantie.

Die Uhren des Windows-Hosts wurden nicht validiert. Daher hier keine präzise reale Laufzeit oder Speedup-Aussage aus Gastzeit. Die 276,26 Stunden sind verbuchte CPU-Zeit.

## 3. Gepaarter Strategievergleich

| Kennzahl | ordered | dynamic |
|---|---:|---:|
| Rootklassen | 128 | 128 |
| Median maximale Tiefe | 10 | 15 |
| Maximaltiefe 10 | 93 | 0 |
| Maximaltiefe 12 | 4 | 0 |
| Maximaltiefe 13 | 12 | 0 |
| Maximaltiefe 14 | 12 | 0 |
| Maximaltiefe 15 | 6 | 118 |
| Maximaltiefe 16 | 1 | 10 |
| Aufgezählte Zeilen | 784.169.116 | 663.302.697 |
| Projektionsversuche | 329.900 | 1.080.197 |
| Unvollständige Projektionsversuche | 11.426 | 8.441 |
| Neustarts | 1.333 | 640 |
| Anteil Tiefen 1–5 an Projektions-CPU | 85,32 % | 65,33 % |

Paarvergleich derselben Rootklasse: dynamic tiefer in 123 Fällen, gleich tief in 4, ordered tiefer in 1. Das ist ein deutlicher empirischer Vorteil für erreichte Tiefe bei diesem Budget und dieser Implementierung. Es beweist weder größere SRG-Fundwahrscheinlichkeit noch geringere Kosten einer vollständigen Suche.

`dynamic` ist keine bereits optimierte Minimum-Remaining-Values-Heuristik: Es wählt zufällig bis zu vier Vertreter von Bahnen offener Zeilen unter der aktuellen Zustandsgruppe. `ordered` nimmt die erste offene Zeile. Die Arme unterscheiden sich daher nicht nur durch eine Permutation derselben vollständigen Suche, sondern auch durch Zahl und Identität getesteter Zielzeilen und die entstehenden Stichproben.

## 4. Was wir über die Breite wirklich wissen

Tiefe in `growth_by_depth.csv` ist die Anzahl schon gebauter H-Zeilen vor der getesteten Erweiterung. Eine auf Tiefe d gefundene zusätzliche Zeile erzeugt einen Zustand der Tiefe d+1. Die CSV zählt Projektionsversuche, nicht verschiedene Elternzustände oder vollständige Schichtbreiten.

Auf Tiefe 1 sind sämtliche Versuche unvollständig:

| Arm | Versuche | Vollständig | Mittlere beobachtete Zeilen |
|---|---:|---:|---:|
| ordered | 1.461 | 0 | 65.126,31 |
| dynamic | 2.155 | 0 | 65.453,39 |

Viele Versuche erreichen das Limit 65.536, andere enden früher am Zeitbudget. Diese Zahlen sind Untergrenzen für die jeweiligen Projektionen; wiederholte Versuche können denselben Raum betreffen. Sie dürfen nicht addiert werden, um verschiedene Erweiterungen zu zählen.

Später verengen sich die besuchten Teilräume stark. Beispielsweise enthalten die 3.272 dynamic-Projektionsversuche auf Tiefe 15 insgesamt nur 10 Zeilen; auf Tiefe 16 liefern 40 Versuche null. Diese 40 Versuche sind weder 40 verschiedene Zustände noch 40 globale Ausschlüsse. Die Auswahl von Eltern, Reservoir mit 32 Zeilen und Beam mit 64 kanonischen Zuständen beschränkt die Aussage.

Die Duplikatzähler melden insgesamt nur 22 Treffer bei dynamic und null bei ordered. Gemessen wurde aber nur gegen den jeweils noch behaltenen Pool, nicht gegen alle jemals erzeugten Zustände. Daraus folgt keine geringe globale Isomorphiereduktion. Umgekehrt ist keine große bisher verborgene Symmetriereduktion zugesichert: Im Root-Audit hatten bereits 6.722 von 8.105 Rootklassen trivialen Stabilisator. Schichtdeduplizierung über verschiedene Baupfade und Symmetrie im Stabilisator eines einzelnen Elternzustands müssen getrennt gemessen werden.

## 5. Bedeutung der 512 Zertifikate

Für einen festen Teilzustand S, eine Zielzeile t und die verwendete notwendige CNF-Relaxation F(S,t) wurden alle gespeicherten Projektionszeilen durch Blockierklauseln ausgeschlossen. DRAT bestätigt die Unerfüllbarkeit der verbleibenden CNF. Aussage: Es gibt in dieser Relaxation keine weitere projizierte Zeile außerhalb der Liste.

Das zertifiziert nicht die globale Extendierbarkeit der gelisteten Zeilen, nicht die vollständige Schicht, nicht die Vollständigkeit des Beam und nicht den Root-Ausschluss. Ein nichtleeres vollständig ausgezähltes Teilproblem ist auch kein ausgeschlossener Suchast.

`worker.py` wählt pro Job die ersten zwei vollständig ausgezählten Projektionen als Proofkandidaten. Dies ist eine systematische Auswahl bereits abgeschlossener Fälle, keine Zufallsstichprobe und insbesondere keine repräsentative Probe der schweren zensierten frühen Projektionen. 0,86 Proof-CPU-Stunden sind deshalb ein erfolgreicher lokaler Funktionsnachweis, keine Prognose der Zertifizierungskosten der Hauptsuche. Auch der Berichtszähler `certified_projected_closures` muss in diesem Sinn gelesen werden.

## 6. Abgleich mit der memetischen H-Faser-Untersuchung

Laut den drei Commits:

- Der kleinste nichttriviale exakte H-Move verändert mindestens 8 H-Vertices und 16 undirektionale H-Kanten; diese Grenze ist scharf.
- Alle minimalen 8/16-Moves sind Omega-4x4-Moves.
- cand_A (W=2338): keine exakten Nachbarn in Distanzen 16–24.
- cand_B (W=2333): genau zwei Nachbarn bei Distanz 16, keine bei 17–24.
- Auch die geprüften Produktfamilien 4x8, 4x10, 4x12, 6x8 sind bei beiden leer. Das ist keine vollständige Prüfung aller größeren Distanzen.
- Root-Zeugen 1/2 haben 49/59 minimale Nachbarn und 4/3 Nachbarn der Familie 6x6.
- HealthyPrefix blieb in 14 EXTEND-Versuchen UNKNOWN. Ein CP-SAT-Kontrolltest löste nur zwei von drei garantiert H-linear erfüllbaren Fällen im damaligen Zeitfenster.
- H-FIBRE-NEAREST 0.7.0 hat in diesen fixierten Quellen noch kein Solverresultat. Keine Aussage über spätere, hier nicht vorliegende Ergebnisse.

Relevante Folgerung: Kleine exakte Moves allein sind keine belastbare universelle Navigationsstrategie; bekannte H-lineare Zeugen sind wertvolle Kontrastkontrollen für genau diese lineare Faser. Die Abstandszahl 16 zählt geänderte Kanten zwischen vollständigen Zuständen, die Pilot-Tiefe 16 zählt gebaute Zeilen. Die numerische Gleichheit hat keine nachgewiesene mathematische Bedeutung. Lokale H-Isolation liefert keinen zulässigen neuen Ausschlussfilter für ROOT8105.

## 7. Notwendige Präzisierung der empfohlenen Positivkontrollen

Der Handoff empfiehlt cand_A/B-Präfixe als garantiert completable Instanzen. Das gilt für H-lineare Completion, nicht ohne weitere Prüfung für den aktuellen ROOT8105-Encoder.

Notation: X ist die 84×84 H-Adjazenz, P die 84×14 Border-Inzidenz. Die memetische lineare Faser L fordert Symmetrie, Null-Diagonale, Binärität, Grad 12 und XP=M. Ein vollständiger solcher Zeuge garantiert, dass ein aus ihm entnommenes Präfix in L ergänzbar ist.

Ein voller SRG verlangt zusätzlich für verschiedene H-Vertices u,v:

    (X²)[u,v] = 2 - X[u,v] - |P_u ∩ P_v|.

Äquivalent für den gesamten H-Block: X² + PPᵀ = 12I - X + 2J.

Bereits `Geometry.verify(rows)` verlangt diese Gleichungen für Paare gebauter Zeilen. `encode(..., target=t)` verlangt zusätzlich die Paarbedingungen gebaut–Zielzeile sowie Sternbedingungen zwischen jeder gebauten Zeile und ihren noch offenen H-Nachbarn. Er verlangt jedoch nicht sämtliche Margen aller anderen offenen Zeilen. Das aktuelle lokale F(S,t) und die globale lineare Faser L sind deshalb nicht einfach dieselbe Relaxation. Die gemeinsame stärkere Relaxation `encode(..., target=None)` enthält alle offenen Margen und alle Paarbedingungen mit mindestens einer gebauten Zeile; auch sie erzwingt noch nicht sämtliche offen–offen-Paarbedingungen.

Folgen:

1. Ein L-Zeuge mit W>0 ist kein bekannter SRG-Zeuge und garantiert nicht die Gültigkeit beliebiger tiefer Präfixe unter `Geometry.verify`.
2. Ein Präfix kann lineare Completion besitzen, aber an den zusätzlichen Paar-/Sternbedingungen scheitern. Ein korrektes UNSAT dort wäre kein Fehler des Solvers.
3. Selbst wenn der vollständige mitgelieferte L-Zeuge eine zusätzliche Bedingung verletzt, beweist das allein nicht UNSAT für das Präfix: Eine andere Completion könnte die Bedingung erfüllen. Nur die behauptete Positivgarantie entfällt.
4. Ein echtes positives Kontrollobjekt für F(S,t) braucht eine überprüfte erfüllende Belegung genau dieses F. Ein SAT-Modell liefert eine lokale Positivkontrolle, keine Garantie beliebig weiterer Augmentation.
5. Vollständige SRG-Kontrollen können auf dem bekannten 9er-Rookgraphen die vollständige Kette testen. Sie ersetzen keine 99er-Leistungsprognose. Ein bekannter voller 99er-SRG als Kontrolle wäre bereits die Lösung unseres Existenzproblems.

Die vorgeschlagene planted-control-Idee wird deshalb präzisiert, nicht verworfen: getrennte Tests für L, tatsächliche lokale F-Instanzen und komplette kleine SRGs. Neue Kontrollen müssen ihre konkrete Ziel-CNF und Positivbelegung benennen.

## 8. Infrastruktur und Schlussfolgerung

Der beobachtete kleine RAM-Bedarf entstand bei begrenztem Beam und kleinen Reservoirs; er belegt keine Speicherverträglichkeit einer vollständigen Frontier. Größter gemeldeter Worker-RSS in der Wachstumsdatei: 100.400 KiB. Speicher für globale kanonische Schlüssel, SAT-Blockierklauseln und vollständige Schichten wurde damit nicht getestet.

Nur als Größenordnung einer Wiederholung desselben alten, auf eine Suchstunde pro Arm begrenzten Piloten: 8105×2 = 16.210 Such-CPU-Stunden, idealisiert 61,40 Tage mit elf Kernen ohne Nebenaufwand. Eine ungewichtete lineare Übertragung der mittleren Projektionsdaten ergäbe 2,137 TB. Das ist keine statistisch abgesicherte Hochrechnung des geschichteten Samples, keine vollständige Baumprognose und kein Budget für einen neuen GC-19-Lauf.

Die ursprüngliche Leitfrage ist teilweise beantwortet: Lokale Enumeration, kanonische Stichprobenprüfung und ausgewählte lokale DRAT-Zertifizierung funktionieren. Die Kosten einer vollständigen zertifizierbaren Schicht bleiben offen. Deshalb als nächster Erkenntnisschritt: Modellkalibrierung plus vollständige frühe Breitenmessung auf einer genügend breiten Rootauswahl. Ein flächiger 8105-Lauf, ein bloß größerer Beam oder ein teurer Completer an jedem Knoten werden durch die vorliegenden Daten noch nicht gerechtfertigt.

Konkreter Vorschlag: `FORTSETZUNGSPLAN.md`. Unabhängiger Auftrag: `REVIEWERPROMPT.md`. Entscheidung nach Eingang und Abgleich des Reviews.
