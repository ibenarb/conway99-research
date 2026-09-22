# Conway99 – gemeinsamer Planungsauftrag an Codex und Reviewer

Stand: 22. September 2026, nach Abschluss des 192-CPU-Stunden-λ-Vergleichs.
**Dieser Auftrag gilt wortgleich für beide Empfänger.** Zugriff auf frühere Chats wird nicht vorausgesetzt.

## Auftrag und Grenzen

Entwickle eigenständig eine **konkrete, begründete und ausführbare Fortsetzung des memetischen Zweiges**, mit Schwerpunkt λ, auf dem Ryzen. Liefere eine Entscheidungsvorlage, die nach Freigabe unmittelbar implementiert werden kann. Prüfe die bisherigen Schlussfolgerungen kritisch; weder Codex noch Reviewer sollen lediglich den anderen bestätigen. Der bisher vorgeschlagene 72-CPU-Stunden-Nachlauf ist eine zu prüfende Option, keine vorgegebene Antwort.

Lies die unten fest referenzierten Quellen und Daten vollständig soweit für Deine Aussagen erforderlich. Trenne **selbst nachgeprüfte Ergebnisse, übernommene Befunde und Hypothesen**. Erfinde keine Prüfung fehlender Rohdaten. Benenne abweichende Schlussfolgerungen und das kleinste sinnvolle Experiment, das sie unterscheiden könnte. Ein fehlender Bericht des jeweils anderen Bearbeiters ist kein Grund, die eigene Planung aufzuschieben.

Dieser Auftrag autorisiert die Analyse und Ausarbeitung, **keinen neuen länger laufenden Suchversuch**. Änderungen an einem vorhandenen Laufbundle, Löschen alter Ergebnisse oder Änderungen an Office-/fremden Prozessen sind ausgeschlossen. Neue Rechenbudgets müssen ausdrücklich beziffert und danach entschieden werden. Projektbezogene Dokumente, Prüfcode und Ergebnisse dürfen gemäß dauerhafter Git-Freigabe veröffentlicht werden; der Reviewer liefert seine Rückgabe als eigenes Dokument beziehungsweise eigenen Branch.

## 1. Problem und unveränderte Ziele

Gesucht ist ein srg(99,14,1,2). Die Memetik liefert Näherungskandidaten und möglicherweise eine Lösung, keinen Nichtexistenzbeweis. Vermenge diesen Auftrag nicht mit dem getrennten Involutions-/Symmetrieprojekt.

Für u≠v gilt r_uv = |N(u)∩N(v)| + A_uv − 2. Ungeordnete Paare werden einmal gezählt: W zählt r≠0, L1 summiert |r|, F summiert r², Linf=max|r| und Nmax zählt Paare beim Maximalbetrag. Primäres Ziel bleibt **lexikographisch (W,L1)**. Weitere aktive Ziele sind L1, F und lexikographisch (Linf,Nmax,L1). W hat ausdrücklich Vorrang vor seinem L1-Tie-Breaker; Verbesserungen verschiedener Ziele dürfen nicht miteinander verrechnet werden.

Im λ-Arm sind alle Kandidaten einfache 14-reguläre Graphen; jede Kante besitzt genau einen gemeinsamen Nachbarn. Jede Kante liegt damit in genau einem Dreieck, jeder Knoten in sieben Dreiecken. Ein linearer 3-uniformer, 7-regulärer Hypergraph ist nur dann geeignet, wenn sein 2-Sektionsgraph keine zusätzlichen Dreiecke enthält. Jeder neue Operator oder reparierte Kandidat braucht eine vollständige unabhängige Prüfung dieser Bedingungen.

## 2. Feste Quellen für beide Bearbeiter

Repository: `ibenarb/conway99-research`, Arbeitszweig `memetik`.
**Ergebnisstand:** `84c46aac2b39d718c44daee2a7b994c29930e6c5`.
**Eingefrorener Suchcode:** `b659cb8743dd6036d91dafb466b2d12cb21a29b0`.

Die Links sind commitfest; keine Annahme über später veränderte Branch-Inhalte:

- [Jüngster Ergebnisbericht einschließlich Prüfgrenzen und Empfehlungen](https://github.com/ibenarb/conway99-research/blob/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922/BERICHT.md)
- [SUMMARY.json – alle Paarzahlen, Seedwerte und Messpunktzusammenfassungen](https://github.com/ibenarb/conway99-research/blob/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922/SUMMARY.json)
- [AUDIT.json.gz – vollständiger Auditbericht mit Paar-Scorelisten, Rohdownload](https://raw.githubusercontent.com/ibenarb/conway99-research/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922/AUDIT.json.gz)
- [ENDPOINTS.json.gz – alle 192 aktiven Endgraphen mit Seeds, CPU und Messpunkten, Rohdownload](https://raw.githubusercontent.com/ibenarb/conway99-research/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922/ENDPOINTS.json.gz)
- [RECEIPTS.json – 193 CPU-Abrechnungen einschließlich Kontrolljob](https://github.com/ibenarb/conway99-research/blob/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922/RECEIPTS.json)
- [RECORD_CENSUS.json – Nachbarschaften, graph6-Rekorde und neue Ein-Schritt-Zeugen](https://github.com/ibenarb/conway99-research/blob/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922/RECORD_CENSUS.json)
- [PUBLICATION_MANIFEST.json – Hashes des veröffentlichten Prüfsatzes](https://github.com/ibenarb/conway99-research/blob/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922/PUBLICATION_MANIFEST.json)
- [Eigenständiger Auditcode und Code der Nachdiagnose](https://github.com/ibenarb/conway99-research/tree/84c46aac2b39d718c44daee2a7b994c29930e6c5/experiments/memetik/lambda_audit_20260922)
- [Eingefrorenes Versuchsdesign](https://github.com/ibenarb/conway99-research/blob/b659cb8743dd6036d91dafb466b2d12cb21a29b0/docs/memetik/lambda_compare_20260921/DESIGN.md)
- [Suchcode 0.2.0 samt README, Konfiguration und exakten Gründern](https://github.com/ibenarb/conway99-research/tree/b659cb8743dd6036d91dafb466b2d12cb21a29b0/experiments/memetik/lambda_compare_0_2_0)
- [Vorheriger Abgleich von Codex-Befunden und Reviewer-Vorschlag](https://github.com/ibenarb/conway99-research/blob/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_review_20260921/ABGLEICH.md)
- [Originalreview im separaten Archivbranch, fester Archivcommit](https://github.com/ibenarb/conway99-research/tree/52ad622dfa5d04ba0a0d26dd39e4aa7fc6927ce7/docs/reviews/20260921_lambda)

Lies insbesondere `engine.py`, `kernel.py`, `archive.py`, `worker.py`, `queueing.py`, `run.py`, die tatsächlich importierten Auswahl-/Operatorfunktionen und die Kontrollberichte. Der allgemeine Dreierzyklus stammt aus `lambda_strategy_0_1_0/strategy.py`; er ist nicht identisch mit der alten Rotation. Git enthält die erforderlichen Abhängigkeiten, nicht nur die neue Oberfläche.

**Datenverfügbarkeit:** Diese Git-Dateien reichen für einen überprüfbaren Endpunkt-/Paarvergleich und konkrete Planung. Sie enthalten nicht sämtliche SQLite-Archive, laufenden Suchzustände, vollständigen Ereignisprotokolle oder Original-Bestwertkurven. Das bereits vorhandene kompakte Review-ZIP enthält ebenfalls nicht das vollständige Laufarchiv. Der Prüfer `audit.py` benötigt dieses Originalarchiv; `census.py` benötigt zusätzlich die von `audit.py` erzeugten unkomprimierten `AUDIT.json` und `PAIRED_RESULTS.json` sowie die Repository-Abhängigkeiten.

Vollständiges Original: `ryzen_lambda_compare_020_20260921.tar.gz`, ca. 287 MiB, SHA256 `c9856a662d4b6438b1edc42f930a3b77c3d60dd2f15b7b167a0901893c32b382`. Es liegt beim Nutzer und wurde Codex hochgeladen, aber nicht als regulärer Git-Blob veröffentlicht. Für eine Behauptung, die nur daraus prüfbar ist, fordere gezielt dieses Archiv oder die konkret fehlenden Dateien an. Plane anhand der verfügbaren Daten weiter, ohne eine vollständige Rohdatenprüfung vorzutäuschen.

## 3. Letzter Versuch und Befunde

12 neue gepaarte Seeds × vier Ziele × B0/P/T/TC × 3600 Worker-CPU-s = 192 Jobs. 18 Worker, Population 16 bei B0/P; T/TC je ein Pfad mit Archiv. Identische 16 kanonisch verschiedene Gründer einschließlich früherer Endpunkte; neue Reviewer-Rekorde wurden nicht als Starter eingesetzt. Messpunkte 600/1800/3600 CPU-s derselben Trajektorie. Tatsächliche Vergleichs-CPU 191,735161443611 h, Kontrollen zusätzlich 75,475785 s.

| Verfahren | Eingefrorene Suchregel | Median W / bester aktiver W nach 3600 s |
|---|---|---:|
| B0 | Fast-A0, Apex/alte Rotation, Stichprobe 32, historische 45/75-s-Phasenlimits | 2180 / 2180 |
| P | Apex∪Pivot, gleichverteilte Perturbation, vollständiger strikter Abstieg, alte Populationsauswahl | 2141 / 2130 |
| T | Vollständiges Apex∪Pivot, gelöschte-Kanten-Tabu 7–15 Schritte, Aspiration, Archiv-Restarts | 2151,5 / 2132 |
| TC | Wie T, zusätzlich vollständiger allgemeiner Dreierzyklus | 2141 / 2141 |

Alle drei neuen Verfahren gewinnen gegen B0 im W-Ziel 12/12. P gegen T: 11/0/1; TC gegen T: 10/0/2; TC gegen P: 6/0/6 (Siege/Gleichstände/Niederlagen). B0 und P unterscheiden sich als Verfahrenspakete, nicht nur durch einen Operator. TC gegen T isoliert den größeren Katalog innerhalb derselben Pfadsteuerung bei gleichem CPU-Budget.

Die Rangordnung hängt vom Horizont ab: Nach 600 s gewinnt T gegen P 10/2/0 und TC gegen P 12/0/0; nach 3600 s gilt die obige Bilanz. P verbessert W in elf von zwölf Läufen noch zwischen 1800 und 3600 s. TC erreicht in allen zwölf W-Jobs nach ungefähr 20 CPU-s **denselben graph6-Bestgraphen** (2141,2492) und verbessert den aktiven Rekord danach nicht mehr. Gleicher Bestgraph beweist keine identischen ganzen Pfade.

Weitere Ziele: P erreicht L1=2392 in allen zwölf L1-Jobs; T und TC jeweils einmal 2388, sonst 2392. Alle 48 F-Jobs bleiben bei F=2836. Auch kein beobachteter Rekord aus anderen Zielen verbessert F. Im Linf-Ziel schlägt P alle drei anderen Verfahren in sämtlichen zwölf Paaren; bester aktiver P-Endpunkt (Linf,Nmax,L1)=(2,229,2478).

**Drei Ergebniskategorien strikt trennen:**

1. Aktiver W-Endpunkt des Stundenvergleichs: P mit (W,L1,F,Linf,Nmax)=(2130,2452,3112,3,8).
2. Während des Laufs nur beobachteter Archivrekord: T/L1, Seedindex 4, CPU=2250,520038, Rolle `OBSERVED`, mit (2123,2442,3104,3,12). Ein P/F-Job beobachtet außerdem (Linf,Nmax,L1)=(2,221,2462).
3. Erst nach dem Lauf erzeugte, unabhängig geprüfte Ein-Schritt-Zeugen: Pivot von W=2123 zu **(2121,2440,3100,3,11)**; Pivot vom beobachteten Linf-Rekord zu **(Linf,Nmax,L1)=(2,218,2476)**, W=2258, F=2912. Diese Zeugen sind keine nachträglich verbesserten Stunden-Endpunkte. Sie wurden noch nicht vollständig weiter abgestiegen.

W=2130 und der TC-Bestgraph W=2141 sind lokale (W,L1)-Minima im gemeinsamen Apex-/Pivot-/Dreierzyklus-Katalog. F=2836 ist am geprüften HoG-Start lokal minimal in diesem Katalog, nicht als global optimal bewiesen.

Prüfumfang von Codex: Originalhash, alle 1.825 Inhaltsprüfsummen, alle 192 Abrechnungen, Quellenabgleich, 1.536 verschiedene berichtete Graphen mit neuem Decoder und unabhängigen Mengen-Schnitten; SQLite-Integrität und Zeilenzahlen. Nicht alle 1.490.795 Archivzeilen wurden erneut mathematisch geprüft, nicht alle Kanonisierungszertifikate neu berechnet, keine vollständige Pfadreproduktion. Nutze dieses Audit als Evidenz mit benannter Herkunft, nicht als eigenen Prüfbericht.

## 4. Konkurrierende Fortsetzungen kritisch entscheiden

Bewerte mindestens die folgenden Optionen. Wähle danach ein priorisiertes Vorgehen; baue nicht alles gleichzeitig ein.

**A – Länger laufen lassen:** Prüfe, ob die ursprünglichen zwölf W-Paare P/TC zustandserhaltend von einer auf vier CPU-Stunden fortgesetzt werden sollten: 24 Jobs × drei zusätzliche Stunden = 72 zusätzliche CPU-Stunden. Stelle eine sinnvoll begründete Alternative gegenüber, falls vier Stunden, zwölf Seeds oder die Wahl dieser Verfahren nicht passen. Die Erweiterung ist ein nach Sichtung der ersten Ergebnisse gewählter Langzeittest, keine unberührte neue Bestätigung. CPU-Kosten von Wiederaufnahme und Präfix-Replay müssen zählen. Das vorhandene `extend` erweitert alle 192 Jobs; selektive Fortsetzung erfordert eine saubere neue Auswahl im Manifest. Unverändertes `extend --cpu-hours 4` würde **576**, nicht 72 zusätzliche Vergleichs-CPU-Stunden freigeben.

**B – Archivrekorde aktiv nutzen:** Untersuche zielweise Nachoptimierung, gezielte Einspeisung, Migration oder ein gemeinsames Archiv. Der W=2123→2121-Zeuge zeigt konkret, dass gespeicherte Nachbarn noch Fortschritt bieten. Er beweist keine allgemeine Überlegenheit von Kooperation. Definiere Empfänger, Auswahl, Zeitpunkt, Kanonisierung, Herkunft, Doppelzählung und CPU-Zurechnung. Trenne eine pragmatische Rekordfortsetzung mit den besten bekannten Kandidaten vom fairen Verfahrensvergleich auf gleichen Starts. Benenne einen Vergleich ohne Migration.

**C – TC-Konvergenz und Barrieren:** Prüfe Starts, Zufallsnutzung, Tie-Breaks, Attribut-Tabu, Aspiration und Restartauswahl im tatsächlichen Code. Restarts erfolgen nach 2000 akzeptierten Schritten ohne aktiven Rekord, danach 5–8 Zufallsschritte; Archivwahl 25 % gleichverteilt, sonst bestes von acht zufälligen Archivmitgliedern. Erklären diese Regeln die frühe gleiche Bestlösung plausibel? Unterscheide ein strukturelles Becken, unzureichende Diversifikation, ungeeignete Restartparameter und einen möglichen Implementierungsfehler. Leite eine gezielte Kontrolle ab, statt aus identischen Bestwerten direkt einen Fehler zu behaupten.

**D – F-Plateau und zusätzliche Familien/Operatoren:** Begründe, ob F eigene Barrierensteuerung, größere gültige Trades, andere Gründer oder einen getrennten Reparaturmodus braucht, oder zunächst nachrangig bleibt. Linf-Fortschritt und kleineres W widerlegen kein F-Plateau. Alte Rotation trat einmal als akzeptierter Zug auf; ihre frühere Leere ist kein globaler Ausschluss. Neue Familien, Crossover oder dauerhaft größere Populationen sind mögliche Alternativen, müssen aber den konkreten Befunden gegenüber begründet und separat kontrolliert werden. Ω kann als spätere Alternative diskutiert werden, eröffnet hier jedoch nicht stillschweigend eine zweite Kampagne.

## 5. Zeitmessung, Budgets und technische Pflichten

Die Zeitmessung ist offen: UTC-Zeitstempel ergeben 11 h 04 min 50 s, `comparison_timing.json` nur 10 h 15 min 10,85 s. Differenz 49 min 39,15 s; gemessene CPU/monotone-Dauer=18,70 trotz 18 einthreadiger Worker. Ursache unbekannt. Leite keine Beschleunigung daraus ab. Formuliere eine kleine Diagnose, die mindestens UTC/Realtime, monotone Uhr, Prozess-CPU, wait4 und eine unabhängige Hostzeit vergleicht; dokumentiere, welche Zeitbasis das Ergebnisbudget und welche die ETA steuert. Begründe, ob und unter welchen Befunden die Suchplanung fortgesetzt werden kann.

Die Nutzerpräferenz ist ausdrücklich: lokale Rechenzeit sinnvoll nutzen, keine künstlich kurzen Zeit- oder Mengendeckel ohne Begründung. Das ist keine Freigabe beliebiger neuer Kampagnen. Unterscheide wissenschaftlichen Messendpunkt, algorithmischen Parameter und echte Ressourcengefahr. Ein Plateau darf nicht als Beweis fehlender späterer Chancen dienen. Schlage begründete Beobachtungspunkte, zustandserhaltende Fortsetzung und klare Entscheidungsregeln vor. Begründe Seedzahl, Horizont und Archiv-/Populationsumfang; keine nachträgliche Änderung der primären Zielfunktion anhand günstiger Ergebnisse.

Erhalten bleiben die unabhängige Kandidatenprüfung, Lösungserkennung bei sämtlichen Residuen null, Sicherung des Zeugen, kontrollierter Stopp eigener Worker und faire CPU-Abrechnung. Die fünf Sekunden Abschlussreserve sind im Jobbudget enthalten; ungenutzte Reserve eines abgeschlossenen Endpunkts darf bei Verlängerung nicht rückwirkend neue Verbesserungen in alte Messpunkte eintragen. Veränderte Quellen oder Algorithmen sind eine neue Versuchsversion, keine unveränderte Fortsetzung.

Aktuelle Schutzregeln: 1 GiB Adressraum je Worker, 36 GiB Gruppen-RAM, 6 GiB freie RAM-Reserve, 20 GiB freier Linux-Platz, 50 GiB frei auf dem tatsächlich ermittelten Windows-VHDX-Trägervolumen. SQLite-Archiv ohne feste 64-Klassen-Verdrängung; keine pauschalen 2-GiB-Lauf- oder 600-CPU-s-Controllerstopps. Überprüfe die Eignung dieser Regeln, bevor Du Änderungen empfiehlst. Der frühere Ausfall war physischer Windows-Platzmangel trotz freier virtueller Linux-Platte.

## 6. Erwartete konkrete Rückgabe

A. **Urteil:** Was belegt der abgeschlossene Vergleich, was nicht? Kurze Tabelle mit Befund, Alternativerklärung, erforderlicher Zusatzprüfung und Konsequenz. Priorisiere eine Fortsetzung und begründe verworfene Alternativen.

B. **Genaues Versuchsmanifest:** Varianten, Startgraphen oder bestehende Job-IDs, Seeds, Wiederaufnahme versus Neustart, Ziele, Workerzahl, Laufhorizont, Messpunkte und getrennte CPU-Budgets für Diagnose, Verfahrensvergleich und Rekordfortsetzung. Gib Gesamtstunden als nachvollziehbare Rechnung an. Bereits verbrauchte CPU darf nicht als neu verfügbare Zeit erscheinen. Zwei bis höchstens drei neue Strategien plus begründete Referenz, sofern ein neuer Vergleich erforderlich ist.

C. **Mathematisch/algorithmisch präzise Regeln:** Pseudocode oder überprüfbarer Prototyp für jede Änderung; Gültigkeitsbedingungen, Inversen beziehungsweise Reparaturrückkehr, Auswahl-/Tabu-/Restart-/Migrationsregeln. Benenne konkret betroffene Dateien und positive wie negative Kontrollen. Eine bloße Liste möglicher Methoden reicht nicht.

D. **Vorab festgelegte Auswertung:** Primärer Endpunkt und Vergleichseinheit; Paarvergleich, Streuung, Zeitverlauf und Einzelrekorde getrennt. Beobachtete Nachbarn und aktive Endpunkte getrennt. Aus zwölf Seeds nicht automatisch Signifikanz ableiten. Definiere, unter welchen Ergebnissen verlängert, angepasst oder eine Methode verworfen wird. Behalte ausdrücklich die Möglichkeit bei, P ohne weitere Zusatzmechanismen fortzuführen.

E. **Umsetzung und Rückgabe:** Kurze operative Reihenfolge, erwartete Ressourcen und vorsichtige Budget-ETA, offene Risiken und fehlende Daten. Liefere einen in sich geschlossenen Bericht für den späteren Abgleich beider Vorschläge. Liste genau auf, was Du selbst ausgeführt hast. Keine erfundenen Zyklus-/BFS-/Tabutrajektorien und kein behaupteter Rohdatenzugriff allein aufgrund der Zusammenfassung.

## 7. Rechner und Bedienkontext

Ryzen RB-CUBE: Ryzen 9 3900X, 12 physische Kerne/24 logische CPUs, Ubuntu 24.04 unter WSL2, Benutzer `rb`, ungefähr 47 GiB RAM, 16 GiB Swap. Zuletzt 18 Worker. Repository `/home/rb/conway99_workspace/conway99-research`; Python `/home/rb/conway99_workspace/venvs/memetik/bin/python` (3.12.3, pynauty 2.8.8.1). Abgeschlossener Lauf `/home/rb/conway99_workspace/ryzen_lambda_compare_020_20260921`. Sein Zustand und die Archive bleiben für Fortsetzung erhalten; aktuell läuft diese Kampagne nicht mehr.

Manuelle Softwareanweisungen nur einzeln: **genau ein ausführbarer Bash-Einzeiler für Ryzen/Ubuntu/WSL pro Antwort, danach Rückmeldung abwarten**. Keine Office-Pfade und keine Beeinträchtigung anderer Projekte. Für diese Planungsaufgabe sind keine Nutzerbefehle erforderlich, solange die bereitgestellten Daten ausreichen.

**Beginne mit der eigenen Auswertung der Quellen und liefere anschließend A–E vollständig. Führe diesen Auftrag unabhängig aus; stimme Dich nicht vorab mit dem anderen Bearbeiter auf ein Ergebnis ab.**
