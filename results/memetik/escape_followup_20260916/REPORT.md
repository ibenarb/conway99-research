# Escape-Fortsetzung und Symmetrieprüfung — 16. September 2026

## Git und Auftrag

Aktueller Git-Ausgangspunkt geprüft: `abc752d04bd0d72c3fd83fe8aaf4fe5ae3caa37e` auf memetik. Gegenüber dem im Übergabeprompt genannten `f6cb345` ist ausschließlich die Übergabedatei hinzugekommen. Arbeit in frischem Checkout; vorhandene fremde Arbeitskopien und Ryzen-Prozesse unverändert.

## Antwort: Sind alle Kandidaten symmetrisch?

Nein. Die 14 aufgenommenen KI-Kandidaten umfassen **acht asymmetrische und sechs symmetrische Graphen**, wobei symmetrisch hier mindestens einen nichtidentischen Automorphismus bezeichnet. Nicht gemeint ist die Symmetrie A=Aᵀ der Adjazenzmatrix: diese gilt bei allen ungerichteten Kandidaten.

| Kandidaten | Volle Automorphismengruppenordnung |
| --- | ---: |
| Gemini seed42; Claude B und C; Codex C01–C05 | 1 |
| Claude A | 14 |
| Codex C06, C07 | 66 |
| Codex C08, C09, C10 | 33 |

Bei den acht Escape-Gründern haben A_legacy, B_end_F, HoG57338, lambda_Linf2 und C02 Gruppenordnung 1; B_original Ordnung 2, C06 Ordnung 66 und C08 Ordnung 33. Insbesondere sind die Hindernisse bei A und HoG keine Folge einer nichttrivialen Automorphismengruppe.

Berechnet mit pynauty 2.8.8.1 auf den **ungefärbten vollständigen 99-Knoten-Graphen**. Vollständigkeit der Gruppe stützt sich auf nauty; jede ausgegebene Generatorpermutation wurde zusätzlich unmittelbar an sämtlichen Knotenpaaren geprüft. Quelle und Daten: `symmetry_audit.py`, `symmetry.json`. Keine neue Literaturbehauptung über Symmetrieausschlüsse exakter Conway-Graphen.

## C08: neutraler Ausgang und tatsächliche Vielfalt

Alle 66 direkten Apex-Trades sowie die leere Rotationsfamilie wurden im Folgelauf erfasst. Genau 33 direkte Nachbarn sind W-neutral. Die nauty-Klassifikation zeigt: **alle 33 sind untereinander isomorph**. Die Beschriftungsvielfalt ist daher keine Vielfalt verschiedener Graphstrukturen. Die Suchsteuerung verwendet diese Klassifikation nicht als Quotienten.

Ein geprüfter Pfad hat die Werte:

| Schritt | W | L1 | F | Linf | Nmax |
| --- | ---: | ---: | ---: | ---: | ---: |
| Start | 2673 | 3498 | 5412 | 3 | 132 |
| neutral | 2673 | 3504 | 5424 | 3 | 129 |
| verbessert | 2668 | 3504 | 5428 | 3 | 126 |

Weglänge zwei, W-Barriere null. Diese Länge ist minimal im implementierten Apex-/Rotationskatalog: die gesamte direkte Nachbarschaft enthält keine W-Verbesserung. **F und L1 verschlechtern sich dennoch.** Die Suche stoppte am ersten verbesserten Ausgang; die gesamte neutrale Komponente ist nicht geschlossen.

Der Endgraph besitzt Automorphismengruppenordnung **1**. Damit liegt ein konkret geprüfter Weg vom symmetrischen C08 zu einem asymmetrischen, W-besseren Graphen vor. Symmetrie des Gründers wird durch die Operatoren nicht zwangsläufig erhalten.

## Standardisierte Abstiege

Alle zwölf steilsten Abstiege endeten mit vollständig geprüften Nachbarschaften ohne strikt verbessernden Nachbarn im jeweiligen Ziel. Neutrale Nachbarn sind damit nicht ausgeschlossen. Auswahl deterministisch nach Zielwert, bei Gleichstand nach graph6. Vier getrennte Diagnoseziele, keine zusätzliche Populationsselektion.

| Aufgabe | Schritte | W | L1 | F | Linf | Nmax |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B_end_F__descent_F | 4 | 2287 | 3062 | 5218 | 8 | 1 |
| B_end_F__descent_L1 | 6 | 2280 | 3078 | 5292 | 8 | 1 |
| B_end_F__descent_Linf | 6 | 2280 | 3078 | 5292 | 8 | 1 |
| B_end_F__descent_W | 6 | 2214 | 3168 | 6052 | 8 | 6 |
| Codex_C02__descent_F | 5 | 2108 | 2486 | 3292 | 3 | 25 |
| Codex_C02__descent_L1 | 5 | 2065 | 2450 | 3292 | 4 | 2 |
| Codex_C02__descent_Linf | 7 | 2154 | 2572 | 3452 | 3 | 22 |
| Codex_C02__descent_W | 2 | 2031 | 2428 | 3298 | 4 | 2 |
| Codex_C08__neutral_W | 2 | 2668 | 3504 | 5428 | 3 | 126 |
| lambda_Linf2__descent_F | 8 | 2182 | 2398 | 2836 | 3 | 3 |
| lambda_Linf2__descent_L1 | 8 | 2182 | 2398 | 2836 | 3 | 3 |
| lambda_Linf2__descent_Linf | 2 | 2314 | 2616 | 3220 | 2 | 302 |
| lambda_Linf2__descent_W | 8 | 2182 | 2398 | 2836 | 3 | 3 |

Die C02-W-Folge verbessert W von 2074 über 2063 auf **2031**; der Endgraph hat L1=2428 und F=3298. Die verschiedenen Endpunktwerte sind keine gemeinsamen Bestwerte eines einzigen Graphen. Zwei C02-Abstiege erreichen F=3292, aber bei unterschiedlichen übrigen Werten und damit nichtisomorphen Endgraphen.

Alle 13 ausgegebenen Endgraph-Einträge sind asymmetrisch. Die W-, L1- und F-Abstiege des lambda_Linf2-Gründers enden bei Graphen, die zu **HoG57338 isomorph** sind. Dies belegt für diese drei deterministischen Abstiege Rückkehr zu einer bekannten Struktur; keine globale Aussage über Einzugsgebiete. Daten: `endpoint_symmetry.json`.

## B und HoG: begrenzte Breitensuche

Je Aufgabe 180 CPU-Sekunden; maximal 5000 gespeicherte Zustände, BFS-Tiefenschranke drei. Keine zusätzliche Fehlerbarriere auferlegt.

- **HoG57338/F:** Start und alle 46 Nachbarn vollständig expandiert. Kein F-besserer Endpunkt bis einschließlich Weglänge zwei. Von 1101 entdeckten Zuständen in Schicht zwei wurden 83 expandiert; insgesamt 2959 Zustände entdeckt, 130 expandiert. Ein vorhandener Verbesserungsweg im Katalog hätte mindestens Länge drei. Keine Existenzbehauptung eines solchen Wegs.
- **B_original/W:** Start und sechs seiner 277 Nachbarn expandiert; insgesamt 1855 Zustände entdeckt, sieben expandiert. Schicht zwei unvollständig. Daher weiterhin nur: keine direkte Verbesserung; eine Flucht der Länge zwei ist nicht ausgeschlossen.

Beide Aufgaben endeten CPU_BUDGET, nicht erschöpft. Aus diesen Zahlen folgt keine Empfehlung, beliebig lange ohne Ressourcenbegrenzung weiterzusuchen.

## A: Operatorerweiterung implementiert, lokale Flucht weiterhin offen

Drei Reparaturformulierungen sind ausführbar: vollständiges CP-SAT-Modell mit Kantendistanzschranke, unabhängiges sparse MILP mit minimaler Kantendistanz und CP-SAT in expliziten induzierten H-Fenstern. Es gelten ausschließlich der feste Ω-Rahmen und seine Marginalgleichungen; alle acht bekannten Zustände werden ausgeschlossen.

- CP-SAT: höchstens 64 Kantenänderungen/60 Sekunden sowie 256/120 Sekunden: jeweils UNKNOWN.
- Vollständiges Fenster ohne hilfreichen Start, 1008 Änderungen/60 Sekunden: UNKNOWN. 1008 ist hier die triviale maximale symmetrische Differenz zweier H-Graphen mit je 504 Kanten.
- MILP zur Minimierung der Kantendistanz, 120 Sekunden: kein zulässiger Zeuge innerhalb des Limits.
- Induzierte Fenster mit 24, 32, 40 und 48 Außenknoten: Solver meldet INFEASIBLE. Aussagen gelten nur für die gespeicherten konkreten Fenster; keine externen UNSAT-Zertifikate. Das 64-Knoten-Fenster endet nach 30 Sekunden UNKNOWN.
- Zusätzliche Produktfamilien 4x8, 4x10 und 4x12 sind am Start A ebenfalls leer. Keine Erweiterung dieser Aussage auf sämtliche denkbaren Produktgrößen.
- Warmstart mit dem bekannten C02: Solver gibt nur C02 unverändert zurück, bei 429 entfernten und 429 ergänzten H-Kanten. Das ist ein zulässiger Übergang aus der alten Komponente, aber **kein neu gefundener lokaler Reparaturmechanismus**, keine neue Struktur und kein Beleg für praktikable kleine Mutationen.

Der anspruchsvolle Teil des A-Auftrags bleibt somit offen. Die Rechnungen grenzen konkrete Versuche ein und liefern implementierte Modelle; sie lösen das lokale Reparaturproblem nicht. Kein alter Operatorlauf innerhalb der acht Zustände wurde wiederholt.

## Prüfung und Checkpoints

Der erste lokale Folgelauf dauerte etwa 445 Sekunden Wandzeit für 15 Aufgaben. Die 13 gespeicherten Pfade enthalten 82 Graphvorkommen und 69 Übergänge. Alle wurden mit separatem graph6-Decoder und Mengen gemeinsamer Nachbarn nachgerechnet, einschließlich beider Armverträge, Prüfsummen, Änderungen, Zielwerte und Barrieren: PASS.

Die Abschlussprüfung fand bei vier Aufgaben Diskrepanzen zwischen fertigem JSON und SQLite: die jeweils letzte Expansion fehlte im gespeicherten SQLite-Endstand. Ursache nicht abschließend festgestellt; betroffen war der WAL-Endstand. Das Original ist unverändert in `initial_0_2_0_run.zip` erhalten. Die vier betroffenen finalen Nachbarschaften wurden vollständig neu enumeriert (116, 114, 172 und 21 Trades); alle vier lokalen Minima bestätigt. Die korrigierten Checkpoints und die Nachprüfung sind getrennt archiviert. Daten: `checkpoint_reconciliation.json`, `witness_audit.json`.

Die Auslieferung **0.2.1** verwendet Rollback-Journal statt WAL. Vier gezielte Steuerungstests bestanden. Ein realer SIGHUP-/Prozessabbruch-/Wiederaufnahmetest mit SQLite-Integritätsprüfung bestand. Ein begrenzter Abschlusslauf aller 15 Aufgaben mit Version 0.2.1 bestand die Prüfung von Datenbankständen und gespeicherten Pfaden. Zeitbeendete Aufgaben dieses technischen Kurztests sind keine zusätzlichen mathematischen Negativbefunde.

## Fortsetzung auf Office

Geprüftes Paket: `releases/Conway99_Escape_Office_0.2.1.pyz`; Arbeitsprotokoll unter `experiments/memetik/escape_0_2/PROTOCOL.md`. Drei Worker, je 768 MiB Prozesslimit, Speicher-/Plattenkontrolle, atomare Checkpoints und zehnminütige Statusausgabe. Die Zipapp benötigt keine Zusatzpakete.

Für den nächsten produktiven Office-Lauf zunächst die beiden offenen B-/HoG-Pfadsuchen auswählen. Die zwölf abgeschlossenen Abstiege und der erste C08-Ausgang müssen nicht wiederholt werden. Eine vollständige neutrale C08-Komponentenaufnahme ist noch gesondert zu implementieren; derzeit stoppt dieser Suchmodus am ersten verbesserten Ausgang. Für A benötigen die separat bereitgestellten Reparaturscripte OR-Tools beziehungsweise SciPy; diese Abhängigkeiten wurden nicht auf einem Nutzerrechner installiert.

Kein Folgelauf auf Office oder Ryzen gestartet. Der spätere Populationspilot bleibt nachgeordnet. Seine Auswahl kann nun anhand verifizierter Endpunkte und tatsächlich beobachteter struktureller Wiederholungen vorbereitet werden.
