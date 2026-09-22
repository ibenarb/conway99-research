# Conway99 λ: eigenständige Entscheidungsvorlage von Codex

22. September 2026 · Rückgabe zum gemeinsamen Auftrag · Version 1.0.0

**Empfehlung:** P als Arbeitsreferenz behalten. Nach technischer Zeit- und Wiederaufnahmekontrolle die zwölf vorhandenen W-Paare P/TC unverändert von einer auf vier kumulative CPU-Stunden fortsetzen. Daneben die besten bekannten Kandidaten in einer ausdrücklich getrennten P-Rekordspur nutzen. Dafür schlage ich **höchstens 100 neue CPU-Stunden** vor: 72 Fortsetzung + 24 Rekordspur + 2 Diagnose + 2 Infrastruktur. Nichts davon ist gestartet oder durch diesen Bericht freigegeben.

Die 72 Stunden sind auch nach eigener Prüfung vertretbar: P liefert noch späte Fortschritte; TC wurde mit nur einem Restart je Stundenjob bisher kaum unter seiner eigenen Restartregel beobachtet. Der Nachlauf beantwortet eine offene Horizontfrage. Er ist **keine neue, unbeeinflusste Bestätigung** und kein isolierter Operatorvergleich. Als sparsamere, wissenschaftlich anders ausgerichtete Alternative ist eine P-only-Fortsetzung für insgesamt höchstens **64 neue CPU-Stunden** genau benannt.

**Zwei neue Diagnoseergebnisse:** Der veröffentlichte W=2121-Zeuge ist bereits lokal minimal im vollständigen Apex-/Pivot-/Dreierzyklus-Katalog. Der Linf-Zeuge Nmax=218 besitzt dagegen noch einen verbesserten Pivot: **(W,L1,F,Linf,Nmax)=(2252,2468,2900,2,216)**. Außerdem erzeugt die eingefrorene TC-Steuerung mit den zwölf historischen Seeds zehn verschiedene 32-Zug-Folgen, aber denselben Bestgraphen. Ein ignorierter Zufallsseed erklärt die frühe TC-Konvergenz deshalb nicht.

## Quellen, Herkunft und Reichweite

Fest referenzierte Grundlage:

- [Gemeinsamer Auftrag, Commit 0a3b7b6](https://github.com/ibenarb/conway99-research/blob/0a3b7b6870f7892cbb229c5aee9fb04860e69fd1/docs/memetik/lambda_next_20260922/GEMEINSAMER_AUFTRAG.md).
- [Ergebnisdateien, Commit 84c46aa](https://github.com/ibenarb/conway99-research/tree/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_results_20260922): Bericht, SUMMARY, AUDIT, ENDPOINTS, RECEIPTS, RECORD_CENSUS und Veröffentlichungsmanifest.
- [Eingefrorener Suchcode, Commit b659cb8](https://github.com/ibenarb/conway99-research/tree/b659cb8743dd6036d91dafb466b2d12cb21a29b0/experiments/memetik/lambda_compare_0_2_0), einschließlich engine, kernel, archive, worker, queueing, run, Bootstrap, Konfiguration, Gründer, Kontrollcode und README.
- [Versuchsdesign und Kontrollberichte](https://github.com/ibenarb/conway99-research/tree/b659cb8743dd6036d91dafb466b2d12cb21a29b0/docs/memetik/lambda_compare_20260921); importierte Auswahl in `ryzen_compare_0_4_0/search.py`, Laufzeit-/Ressourcenfunktionen, `move_accel_0_1_0/fast_moves.py`, allgemeiner Zyklus in `lambda_strategy_0_1_0/strategy.py`, historische Operatoren und Graphkern.
- [Vorheriger Abgleich](https://github.com/ibenarb/conway99-research/blob/84c46aac2b39d718c44daee2a7b994c29930e6c5/docs/memetik/lambda_review_20260921/ABGLEICH.md) und [Originalreview, Commit 52ad622](https://github.com/ibenarb/conway99-research/blob/52ad622dfa5d04ba0a0d26dd39e4aa7fc6927ce7/docs/reviews/20260921_lambda/REVIEW_LAMBDA_Conway99_20260921.md).

In diesem Bericht bedeutet **eigen geprüft** eine hier ausgeführte Rechnung beziehungsweise eine hier gelesene Codebedingung. **Übernommen** bezeichnet historische Prüfungen aus diesen Quellen. **Hypothese** bezeichnet eine Erklärung, die daraus noch nicht folgt.

Eigen geprüft wurden die acht Dateien des Veröffentlichungsmanifests gegen ihre SHA256, alle 192 veröffentlichten aktiven Endgraphen und zusätzlich Gründer/Archivrekorde/Zeugen: insgesamt **69 verschiedene beschriftete veröffentlichte Graphen**, mit separatem graph6-Decoder und Mengen-Schnitten. Alle sind einfache 14-reguläre λ-Graphen; alle fünf Scores stimmen. Die 193 Receipt-Summen wurden arithmetisch geprüft, ebenso sämtliche **72 veröffentlichten Paarvergleichseinträge**. 858 Nachbarn der sechs veröffentlichten Census-Startgraphen wurden vollständig unabhängig auf Gültigkeit und Scores geprüft; auch die veröffentlichten Zeugen und ihre Inversen stimmen.

Die Katalogenumeration dafür stammt aus dem fest referenzierten Projektcode. Es ist keine zweite vollständige Implementierung der Zyklusenumeration. Für die zwei zusätzlichen Abstiegsdiagnosen wurden auch die Scores sämtlicher enumerierter Nachbarn unabhängig geprüft. Die Kanonisierungszertifikate wurden **nicht** neu berechnet; Aussagen über identische graph6-Dateien benötigen diese Zertifikate nicht.

**Nicht hier geprüft:** das 287-MiB-Originalarchiv, dessen 1.825 Inhaltsprüfsummen, alle historischen Checkpoints, SQLite-Dateien oder vollständigen Bestwertkurven. Der frühere Audit von 1.536 Graphen und 192 SQLite-Dateien bleibt ein übernommener Befund. Bei 600/1800 Sekunden enthält ENDPOINTS nur Scores und graph6-Hashes: ihre Paararithmetik wurde neu berechnet, die zugehörigen Zwischenzeitgraphen wurden mangels vollständiger graph6-Daten nicht neu dekodiert. Auch die tatsächliche Entstehungszeit des archivierten W=2123-Rekords wurde nicht erneut aus SQLite gelesen.

## A. Urteil und Prioritäten

### A1. Was der Stundenvergleich belegt

| Befund | Aussage und Alternativerklärung | Kleinste nötige Zusatzprüfung | Konsequenz |
|---|---|---|---|
| P/T/TC schlagen B0 im aktiven W-Ziel jeweils 12/12. Eigen nachgerechnet. | Vorteil dieser Pakete auf demselben bekannten Gründerbestand; P/B0 ändern zugleich Operatoren, Enumeration und Phasenregeln. | Für reine Operatorattribution wäre eine weitere Ablation nötig. Sie ist für die Wahl einer Arbeitsreferenz nicht erforderlich. | B0 historisch behalten; keine neue B0-Hauptrechnung. |
| P schlägt T 11/12; TC schlägt T 10/12. | P ist nach einer Stunde besser als T; der Zyklus hilft innerhalb dieser Tabusteuerung. Andere Horizonte können anders ausfallen. | Fortgesetzte vorhandene Pfade. | T zunächst nicht verlängern; P und TC erhalten. |
| TC/P: 6 Siege, 6 Niederlagen, keine Gleichstände; beide Median W=2141. | Kein belegter allgemeiner TC- oder P-Vorteil im Stunden-W-Endpunkt. | Zwölf Paare bei vier Stunden, dieselbe Zieldefinition. | TC nicht zum Sieger erklären; P als praktische Referenz, nicht als bewiesener W-Sieger über TC. |
| P verbessert W in 11/12 Fällen zwischen 1800 und 3600 Sekunden. Eigen aus Messpunkten bestätigt. | Längere Suche kann noch nützen; daraus folgt keine bestimmte Erfolgsrate nach Stunde vier. | 7200/10800/14400 als Beobachtungspunkte. | Ein längerer Horizont hat konkrete Evidenz. |
| TC: identischer Bestgraph, nur ein Restart je W-Job. | Gleicher bester Start, gemeinsame Anfangsdynamik, danach schwache Diversifikation oder strukturelles Becken. | Finiter Seed-/Steuerungstest plus Auswertung der Restart-Archive. | Kein pauschaler Fehlerverdacht; Restartwirkung separat beobachten. |
| Archiv W=2123 ist besser als alle aktiven W-Endpunkte; Pivot erreicht 2121. | Zielübergreifende Speicherung bewahrt nutzbare Kandidaten. Sie beweist noch keinen Migrationseffekt. | Nachoptimierung und getrennte Rekordspur. | Vorhandene Rekorde aktiv nutzen, Vergleichspopulationen unverändert lassen. |
| Alle F-Endpunkte 2836. | Plateau der getesteten Starts/Verfahren; mögliche Barrieren, ungünstige Auswahl oder fehlende Trades. | Zunächst geprüfte lokale Nachbarschaft; bei Bedarf gezielt neue F-Mechanik. | Keine unveränderte Verlängerung aller 48 F-Jobs. |
| UTC und monotone Dauer widersprechen sich. | Zeitbasis-/Erfassungsproblem; WSL als Ursache nicht bewiesen. | Mehrere Uhren, wait4 und unabhängige Windows-Hostmessung. | CPU-Endpunkte bleiben bedingt interpretierbar, ETA neu kalibrieren. |

Eigene Streuungsauswertung, aktive W-Jobs nach 3600 Budgetsekunden:

| Verfahren | Median W | Tukey-Hinges Q1/Q3 | Minimum/Maximum W | verschiedene beschriftete Bestgraphen |
|---|---:|---:|---:|---:|
| B0 | 2180 | 2180 / 2180 | 2180 / 2180 | 1 |
| P | 2141 | 2137,5 / 2145,5 | 2130 / 2151 | 11 |
| T | 2151,5 | 2145,5 / 2153 | 2132 / 2153 | 7 |
| TC | 2141 | 2141 / 2141 | 2141 / 2141 | 1 |

Q1/Q3 sind hier ausdrücklich die Mediane der unteren/oberen sechs geordneten W-Werte. Die vollständigen lexikographischen Paarwerte stehen in `W_PAIRS.tsv`. Für P−TC ist der Median der W-Differenzen 0 und der Mittelwert +1/6. Diese Zahlen widersprechen einer Behauptung, P habe TC nach einer Stunde bereits eindeutig geschlagen. Die praktische P-Präferenz beruht auf dem späten Verlauf, der Streuung und dem deutlichen Linf-Vorteil.

### A2. Eigene kleine Nachdiagnose

| Kategorie | W | L1 | F | Linf | Nmax | Status |
|---|---:|---:|---:|---:|---:|---|
| Historischer bester aktiver W-Endpunkt | 2130 | 2452 | 3112 | 3 | 8 | Stundenvergleich |
| Historischer beobachteter W-Rekord | 2123 | 2442 | 3104 | 3 | 12 | Archiv, kein aktiver W-Endpunkt |
| Bereits veröffentlichter Nachlauf-Zeuge | 2121 | 2440 | 3100 | 3 | 11 | Jetzt lokal minimal in A∪P∪C3; 136 Nachbarn |
| Bereits veröffentlichter Linf-Zeuge | 2258 | 2476 | 2912 | 2 | 218 | Nachlauf-Zeuge |
| **Hier erzeugter Linf-Zeuge** | **2252** | **2468** | **2900** | **2** | **216** | Ein weiterer Pivot; danach lokal minimal, 148 Nachbarn |

Der neue Pivot entfernt `{15,92}` und `{30,96}` und ergänzt `{15,30}` und `{92,96}`; Nummerierung 0–98. graph6 und vollständiger Schritt stehen in `POSTRUN_DESCENTS.json`. SHA256 des neuen graph6 ohne Zeilenumbruch:

`3180575be0efb2dd4a0a05add4b3e571208afc9ba5411dfe8b8611ad989738d7`.

W=2121 benötigt unmittelbar eine nichtmonotone Fortsetzung oder einen größeren Katalog. Eine weitere bloße strikte Nachoptimierung im geprüften Katalog kann dort nichts mehr bringen. Das ist eine lokale Aussage, keine Behauptung einer minimalen Fluchtbarriere.

### A3. Entscheidung zwischen konkurrierenden Wegen

1. **A – 72-h-Nachlauf: befürwortet, mit neuer äußerer Steuerung.** Alle zwölf Paare erhalten, keine Auswahl besonders günstiger Seeds. Vier Stunden sind ein vierfacher kumulativer Horizont, der mehrere zusätzliche TC-Restartgelegenheiten erwarten lässt; die Anzahl ist zu messen, nicht zu garantieren. Zwei Stunden wären nur die erste Zwischenmarke; acht Stunden würden bereits 168 zusätzliche Vergleichs-CPU-Stunden verlangen, ohne dass wir den Vierstundenverlauf kennen.
2. **B – Archivnutzung: sofort als getrennte Rekordspur.** Drei zielbezogene Starts, feste Herkunft, identische P-Regeln. Zunächst keine fortlaufende Migration und keine gemeinsame Populationskonkurrenz. Die neuen Starts dürfen keine „Verbesserung durch P“ am Zeitpunkt null vortäuschen.
3. **C – TC-Steuerung: diagnostizieren, nicht gleichzeitig tunen.** Die neue Präfixkontrolle zeigt reale Seedwirkung. Die Wirkung von Restarts, ihres Qualitätsbias und von 5–8 Zufallsschritten bleibt offen. Änderungen daran würden einen neuen Verfahrensvergleich erfordern.
4. **D – F, neue Familien, Crossover und Reparatur: zurückstellen.** Sie werden nicht durch W-/Linf-Fortschritt erledigt. Aber ein gleichzeitiger Umbau von Zielsteuerung, Operatoren, Gründern und Population würde die nächste Entscheidung unklar machen.

**Alternative P-only:** zwölf P/W-Jobs um je drei Stunden = 36 h; dieselbe Rekordspur 24 h; Diagnose 2 h; Infrastruktur 2 h: **64 h**. Das ist meine Alternative, wenn ausschließlich praktische Rekordchancen Vorrang vor der P/TC-Langzeitfrage erhalten. Sie verzichtet bewusst auf deren Aufklärung. Ich bevorzuge hier die 100-h-Option, weil TC nach einer Stunde in sechs Paaren noch besser ist und seine Restartmechanik erst einmal pro Seed zum Zuge kam. Ohne diese wissenschaftliche Frage wäre die zusätzliche TC-Ausgabe von 36 h nicht zwingend.

## B. Genaues Manifest und Budget

`PROPOSED_MANIFEST.json` ist die maschinenlesbare Spezifikation, `PROPOSED_JOBS.tsv` enthält alle 36 Suchjobs. `authorized_to_launch` ist **false**. Es gibt kein automatisches Anlaufen und keine automatische Verlängerung.

### B1. Zustandsfortsetzung: 24 bestehende Jobs

Auswahl ausschließlich `P--lambda-W-00` bis `P--lambda-W-11` und `TC--lambda-W-00` bis `TC--lambda-W-11`. Die Seeds werden aus den alten Tasks übernommen, der gespeicherte RNG-Zustand wird wiederhergestellt; die Zahlen werden **nicht** erneut zur Initialisierung benutzt.

| Index | gemeinsamer ursprünglicher Seed |
|---:|---:|
| 00 | 13066739246755516810 |
| 01 | 10736430408105228949 |
| 02 | 12075019074319984293 |
| 03 | 8784334872519884885 |
| 04 | 11492396544507892624 |
| 05 | 3836825322914055362 |
| 06 | 2475884772427737322 |
| 07 | 1063539887069556541 |
| 08 | 1539184063912749368 |
| 09 | 1423794378183781708 |
| 10 | 12677951989324453032 |
| 11 | 1879856566115949509 |

Pro Job: alter abgeschlossener Budgetendpunkt 3600 s, neuer kumulativer Endpunkt 14400 s, **10800 s neue Budgetfreigabe**. Tatsächlich früher gemessene CPU liegt je Job ungefähr bei 3595 s; die ungenutzte alte Abschlussreserve wird nicht nochmals verfügbar. Manifest bindet jeden alten Task, Resultat, Checkpoint und SQLite-Stand über den veröffentlichten Receipt.

Fortgesetzt werden vollständige Population/Kinder, Episode/Phase, Pfad, Tabu, Archiv, Zufallszustand und unvollständiger Nachbarschaftspräfix. Die 192 veröffentlichten Bestgraphen reichen hierfür allein nicht. Die tatsächlichen Zustände liegen im erhaltenen Ryzen-Lauf.

Messpunkte: 3600 unverändert; 7200, 10800 und 14400 kumulative Budgetsekunden. Die beiden Zwischenpunkte werden aus den vollständig gespeicherten Verbesserungskurven mit `record_cpu <= mark` rekonstruiert. Dafür ist keine Veränderung des eingefrorenen Task-Configs und kein künstlicher Neustart bei zwei/drei Stunden nötig. Adoptions- und Validierungszeit bleiben budgetwirksam.

### B2. Rekordspur: zwölf neue P-Jobs

| Ziel | Jobs × neue CPU-h | Startrekord | Population |
|---|---:|---|---|
| W, lexikographisch (W,L1) | 6 × 2 = 12 | (2121,2440) | 15 Originalgründer + dieser Rekord |
| Linf, lexikographisch (Linf,Nmax,L1) | 4 × 2 = 8 | (2,216,2468) | 15 Originalgründer + dieser Rekord |
| L1 | 2 × 2 = 4 | L1=2388, veröffentlichter beobachteter Graph | 15 Originalgründer + dieser Rekord |
| **Summe** | **24** | | |

Je Ziel wird genau der nach `(Zielschlüssel,state_sha256)` schlechteste Originalgründer ersetzt. Das sind für W `gen-lambda-08`, für Linf und L1 `claude_v01_c`. Das ist eine pragmatische neue Startbedingung, keine faire Ablation der Einspeisung. Die übrigen fünfzehn stehen in Originalreihenfolge, der neue Kandidat übernimmt den ersetzten Platz. Deduplizierung und unabhängige Vollprüfung erfolgen vor Start; keine Klone zum Auffüllen. Die Zielrekorde sind gegenüber allen Originalgründern strikt besser und deshalb mit keinem davon isomorph. Vor Start werden dennoch alle Zertifikate mit der gepinnten Version neu berechnet.

Neustart ohne historischen Checkpoint, neue Seeds exakt nach

`derive_seed(2026092201, ['lambda-record', target, i])`.

Alle resultierenden ganzen Zahlen stehen im Manifest. Sechs/vier/zwei Seeds sind eine Budgetverteilung für Rekordsuche; daraus wird kein robuster Methodenvergleich und keine Signifikanz abgeleitet. Zwei Stunden erlauben mehr als die bereits als irreführend erkannte Zehn-Minutenperspektive, ohne schon eine zweite mehrtägige Kampagne festzulegen. Messpunkte 600/1800/3600/7200, fünf Sekunden Abschlussreserve im Budget. Plateau beendet keinen Job vorzeitig. Zustände bleiben danach fortsetzbar.

Kein F-Job wird in dieser Stufe neu gestartet. F wird in allen Jobs weiterhin exakt beobachtet und ein F-Rekord gesichert. Das ersetzt keine aktive F-Suche; deren Wiedereinführung ist eine separate strategische Entscheidung.

### B3. Diagnose, Infrastruktur, Gesamtbetrag

| Kategorie | genaue Rechnung | neue CPU-h, höchstens |
|---|---|---:|
| Uhrenkontrolle, ein Worker | 1 × 180 s | 0,05 |
| Uhrenkontrolle, 18 Worker | 18 × 180 s | 0,90 |
| Kontroll-/Vorbereitungssuite | 900 s insgesamt | 0,25 |
| TC-Archiv-/Restartdiagnose | 12 × 240 s | 0,80 |
| **Diagnose insgesamt** | **7200 s** | **2** |
| P/TC-Fortsetzung | 24 × 10800 s | **72** |
| P-Rekordspur | 12 × 7200 s | **24** |
| Controller, Kopien/Hashes, Export, Windows-Hilfsprozesse und technische Reserve | separates Gesamtledger | **2** |
| **Gesamt** | **2 + 72 + 24 + 2** | **100** |

Die 192 h des alten freigegebenen Vergleichs und dessen tatsächliche 191,735161443611 h sind **keine** neuen Zeitguthaben. Die hier in der Codex-Umgebung durchgeführten kleinen Diagnosen sind ebenfalls gesondert dokumentiert; sie werden nicht als Ryzen-Suchzeit ausgegeben.

Diagnose- und Infrastrukturreserven sind Budgetzuteilungen, keine mathematischen Abbruchkriterien. Nicht verbrauchtes Budget wandert nicht stillschweigend in andere Suchjobs. Wenn eine technische Prüfung die vorgesehene Reserve überschreitet, wird der konkrete Mehrbedarf entschieden; Sucharchive werden deshalb weder gelöscht noch verkleinert. Controller reserviert vor neuen Starts genug Zeit zum sicheren Pausieren und Abschließen seiner eigenen Prozesse.

### B4. Worker und vorsichtige ETA

Maximal **18 einthreadige Worker insgesamt**, auch wenn Rekord- und Fortsetzungsjobs überlappen. Ursprüngliche Variantenreihenfolge wird paarweise abwechselnd P/TC beziehungsweise TC/P festgelegt, nicht nach Ergebnisqualität. Zunächst neun Paare (18 Jobs), danach die verbleibenden drei Paare; die zwölf zweistündigen Rekordjobs füllen dann freie Slots.

Die reine Kapazitätsuntergrenze für 96 Such-CPU-h ist 5 h 20 min. Bei drei zusätzlichen Stunden je Fortsetzungsjob und 18 Slots entstehen jedoch zwei Fortsetzungswellen: **ungefähr sechs Stunden schon im idealisierten Belegungsmodell**. Die Rekordjobs passen weitgehend in die zweite Welle. Vor Zeitkalibrierung vorsichtig **6–9 Stunden reale Laufzeit zuzüglich Einrichtung** einplanen, keine Garantie. Neue ETA erst aus Hostzeit und tatsächlich gemessener CPU-Fortschrittsrate; alle zehn Minuten aktualisieren, bei widersprüchlichen Uhren als unsicher ausweisen. Keine Lösung-ETA.

## C. Mathematische Regeln und technische Umsetzung

### C1. Unveränderliche Mathematik

Für ungeordnete Paare `u<v` gilt `r_uv = CN(u,v) + A_uv - 2`. Ziele unverändert:

- W: `(W,L1)` lexikographisch;
- L1: ausschließlich L1;
- F: ausschließlich F;
- Linf: `(Linf,Nmax,L1)` lexikographisch.

Eine L1-Verschlechterung darf einen strikt kleineren W nicht aufheben. Nmax wird nur nach Linf verglichen. Kein gewichteter Mischscore tritt an die Stelle dieser Ordnung.

Ein λ-Kandidat muss n=99, symmetrische 0/1-Adjazenz, Diagonale null, Grad 14 und `CN(u,v)=1` auf jeder Kante erfüllen. Dadurch zerfallen seine 693 Kanten in 231 Dreiecke; durch jeden Punkt gehen sieben. Linearität und Punktgrade einer Tripelfamilie genügen ohne Ausschluss zusätzlicher Dreiecke nicht.

Apex tauscht die Spitzen zweier disjunkter Dreiecke, Pivot ersetzt `{p,x,y},{p,u,v}` durch `{p,x,u},{p,y,v}`, C3 permutiert Spitzen dreier disjunkter Dreiecke zyklisch. Die Inverse entsteht durch Vertauschen gelöschter/ergänzter Kanten; bei C3 entspricht dies der Gegenrichtung auf den neuen Dreiecken. Der gültige λ-Eingang ist Voraussetzung der schnellen Bedingungen. Für Pivot ist wegen `G[N(p)] = 7K2` die Bedingung `CN(x,u)=CN(y,v)=1` exakt. Alle übernommenen Kandidaten durchlaufen trotzdem die unabhängige Vollprüfung.

Zusätzliche Plausibilitätskontrollen, hier an den geprüften Graphen bestätigt:

\[
\sum_{v\ne u}r_{uv}=0,\quad L_1\equiv0\pmod2,\quad
F=4C_4-8316\equiv0\pmod4.
\]

Für Linf=2 gilt ferner `L1=W+Nmax` und `F=W+3*Nmax=L1+2*Nmax`. Somit bedeutet kleineres Nmax bei größerem L1 keineswegs notwendig kleineres F. Der neue Linf-Rekord F=2900 bleibt über 2836. F=2836 entspricht 2788 Vierkreisen; eine Lösung hätte 2079. Das Plateau ist also keine bloße Rundungsfrage.

### C2. Selektive Fortsetzung ohne Änderung des alten Bundles

Neue äußere Steuerung unter beispielsweise `experiments/memetik/lambda_next_1_0_0/continue_selected.py`, `coordinator.py` und `evaluate.py`; diese Produktionsdateien sind **noch zu implementieren**. Der vorliegende Code ist Prüf-/Manifestcode, kein fertiger Kampagnencontroller.

Das vorhandene `extend --cpu-hours 4` ist unzulässig für diese Auswahl: Es würde alle 192 Jobs erweitern und **576** zusätzliche CPU-h freigeben. Auch direktes Verändern des alten `manifest.json` würde dessen Fingerprint brechen.

Präziser Ablauf des neuen äußeren Controllers:

```text
acquire read/continuation lock for old run; require no active or dirty jobs
verify old bundle/environment and the 24 source receipts against actual files
create a NEW continuation root; refuse an existing target
copy selected task/result/checkpoint/receipt/SQLite bytes into new root
copy frozen source bundle unchanged; verify every copied hash
never hard-link writable SQLite/checkpoint/result files
store source manifest/fingerprint/budget and all provenance hashes
write a separate selection manifest for exactly the 24 IDs
write new root budget: cumulative per-job ceiling 14400
for each selected job:
    assert copied task bytes and checkpoint task hash are unchanged
    base = max(old budget_cpu_seconds, old closed endpoint 3600)
    launch ORIGINAL frozen worker against copied task directory
    charge process startup, replay, validation, SQLite and closing CPU
    collect every session exclusively with wait4
    retain old published 3600 milestone exactly
read final curves; derive 7200/10800 marks; independently verify endpoints
```

Keine Hardlinks für veränderliche Daten, keine Reparatur alter Marker durch Löschen. SQLite nur aus sauber geschlossenem Stand kopieren; bei vorhandenem WAL eine konsistente Sicherung samt geordnetem Abschluss verlangen, nicht nur die Hauptdatei herauskopieren. Ursprung bleibt unverändert. Quellbundle und Such-Tasks bleiben byteidentisch; die selektive äußere Orchestrierung erhält eine neue Versionskennung und einen eigenen Fingerprint.

Der eingefrorene Worker liest das kumulative Budget aus seinem jeweiligen neuen Laufroot. Daher führt der neue gemeinsame Koordinator Fortsetzungsroot (14400) und Rekordroot (7200) mit einer globalen 18-Slot-Grenze, gemeinsamen Ressourcenkontrollen und gemeinsamer Erfolgsmeldung. Ein unveränderter Aufruf des alten `run.py`/`Queue.run` ist dafür nicht ausreichend: deren Manifest- und Vollständigkeitsannahmen gelten für 192 Jobs.

**Abrechnung:** `actual_total = previous_actual + wait4_current`; Budgetverbrauch schließt zusätzlich bereits geschlossene ungenutzte Reserven ein. Beim alten vollständigen Job wird `base=3600`, nicht 3595. Die neue Suchdeadline ist `14400−base−5`. Die CPU des Replay-Präfixes zählt vollständig; keine Garantie gleicher Trajektorie pro CPU-Zeit wie bei einer ununterbrochenen Vierstundensitzung. Beim sauberen Pausieren werden weitere Sitzungen demselben Ledger zugeschlagen. Ohne verlässlichen Receipt kein automatischer Neustart.

### C3. Gezielte Archivnutzung, keine laufende Migration

Die erste Umsetzung verwendet **eine eingefrorene Startbank**, nicht ein gemeinsam verändertes Sucharchiv:

```text
for target in [W, Linf, L1]:
    choose exact target record specified in PROPOSED_MANIFEST
    verify all lambda invariants and all scores independently
    compute pinned uncolored canonical certificate
    preserve source job, source role OBSERVED, source graph hash and postrun steps
    remove exactly the target-worst old founder; insert record at that position
    assert 16 different canonical classes and full validity
    start fresh P jobs with new prescribed seeds; initialize best from these starts
    send no further graphs between jobs
```

Empfänger: ausschließlich die sechs W-, vier Linf- und zwei L1-Rekordjobs. Zeitpunkt: einmal bei Vorbereitung/Initialisierung, vor der neuen CPU-Kurve. Herkunft wird als Provenienzliste geführt, nicht als erfundene neue Familie. Derselbe Graph kann mehrere Zielbedeutungen haben; seine Isomorphieklasse wird pro Archiv nur einmal gespeichert. Die Anzahl von Ereignissen/Empfängern ist keine Anzahl unabhängiger Entdeckungen. `ACTIVE`, `OBSERVED`, `POSTRUN_DIAGNOSTIC` und `IMPORTED_START` bleiben unterscheidbar.

Vorbereitung, Kanonisierung und Erstellung der Bank laufen im technischen Ledger; Überprüfung und Einsatz innerhalb jedes Workers zählen zu dessen CPU. Die alte Suchzeit bleibt nur Herkunftskosten, kein neues Suchguthaben. Ein schon eingepflanzter Startrekord wird bei t=0 ausgewiesen und nicht erneut als erzielter Suchrekord gezählt.

**Vergleich ohne Migration:** Die fortgesetzten P/TC-Jobs und alle vorgeschlagenen Rekordjobs haben Migration ausdrücklich ausgeschaltet. Man darf den Unterschied alte Starts/neue Startbank nicht als kausalen Migrationseffekt interpretieren. Ein solcher Effekt wäre nur mit gepaarten neuen Jobs auf derselben Bank, gleichem Budget und zusätzlich ein-/ausgeschalteter Einspeisung zu prüfen. Das ist jetzt nicht erforderlich; daher werden nicht gleichzeitig zwei neue Suchstrategien eingeführt. Wenn ein neuer Strategievergleich erforderlich wird, sind zwei Änderungen plus P als Referenz vorab zu spezifizieren, statt beliebig viele Varianten anzuhängen.

Für eine spätere kontrollierte Einspeisung ist die kleinste saubere Regel: pro Empfängerziel und festem Empfänger-CPU-Messpunkt höchstens den strikt besten, unabhängig geprüften und kanonisch noch nicht vorhandenen Kandidaten aus einer zuvor eingefrorenen Donorbank anbieten; Adoption nur an einer Episodengrenze, Elite erhalten, schlechtesten Nicht-Eliten ersetzen. Vergleichsarm bekommt denselben Prüf-/Auswahlcode ohne Einfügen. Donorbudget, Empfangsprüfung und durch Verzögerung betroffene Messpunkte separat protokollieren. Dynamische Donoren wären ein Island-Experiment: Vergleichseinheit wäre die gesamte kooperierende Seedgruppe, nicht jeder abhängige Worker. Diese spätere Änderung ist **nicht** Teil des 100-h-Manifests.

### C4. TC: tatsächliche Codewirkung und gezielte Diagnose

Der Code macht Folgendes:

1. `begin_path(False)` wählt den besten Gründer; kein zufälliger Anfangsgründer.
2. `catalogue(..., True)` enumeriert Apex, Pivot und allgemeines C3 deterministisch und dedupliziert Züge.
3. Zugtabu bezieht sich auf **Wiedereinfügen gelöschter Kanten**. Nach Schritt i erhalten entfernte Kanten Verfall `i+tenure+1`, tenure gleichverteilt 7–15. Verboten ist ein Kandidat, wenn eine ergänzte Kante noch tabu ist; strikte Verbesserung des aktiven Jobrekords erlaubt Aspiration.
4. Unter zulässigen Zügen wird nach Ziel minimiert; Gleichstände werden mit dem gespeicherten RNG zufällig entschieden. Die Zufallswahl wird auch bei Singleton-Listen aufgerufen. P verwendet im Abstieg dagegen die stabile Generatorreihenfolge.
5. Sind alle Züge tabu, wird der Iterationszähler zum nächsten Verfall vorgestellt. Das ist kein akzeptierter Suchschritt und erhöht den Stagnationszähler nicht.
6. Restart nach 2000 akzeptierten Schritten ohne aktiven Rekord; 25 % gleichverteilte Klasse, sonst bestes von acht Ziehungen mit Zurücklegen. Archiv enthält akzeptierte Zustände und beobachtete Rekorde, nicht sämtliche bewerteten Nachbarn. Anschließend 5–8 zufällige Schritte. In dieser expliziten Walk-Phase wird die Tabuzulässigkeit bei der Wahl nicht erzwungen; sie darf also unmittelbare Rückwege enthalten.
7. Kanonisch doppelte Einträge behalten durch `INSERT OR IGNORE` die zuerst gespeicherte beschriftete Darstellung. Zufällige Restarts randomisieren deshalb nicht automatisch die Beschriftung oder das Einzugsgebiet.

**Eigene Präfixkontrolle:** eingefrorenes `Engine`, ursprüngliche zwölf Seeds, genau 32 akzeptierte Schritte je Seed; ein Seed zusätzlich identisch wiederholt. Die ersten 14 Schritte stimmen über alle Seeds überein; danach ergeben sich zehn verschiedene vollständige Präfixe. Alle erreichen denselben (2141,2492)-Bestgraphen in Schritt 22. Jeder adoptierte Graph wurde unabhängig geprüft. SQLite, Kanonisierung, Zeitcallbacks und passive Rekordaufzeichnung waren im Diagnose-Observer ausgelassen. Vor dem ersten Restart beeinflussen sie die hier geprüfte Zug-/RNG-Entscheidung nicht. Das ist eine deterministische Steuerungskontrolle **ohne historische CPU-Zeitbehauptung**, keine Reproduktion der tatsächlichen Stundenpfade.

Der Stundenstand hat bei T 7406–7548 Iterationen und drei Restarts je Seed, bei TC 3523–3602 Iterationen und einen Restart. Der identische 2000-Schritte-Parameter führt somit bei dem langsameren Katalog zu deutlich weniger Restartgelegenheiten pro CPU-Budget. Das ist eine konkrete plausible Erklärung und kein Beweis, dass häufiger neu zu starten besser wäre.

**Kleinste noch offene Diagnose, 12 × 240 CPU-s:** je originalem TC/W-Job dessen unveränderten Endcheckpoint und SQLite-Kopie prüfen. Anzahl verschiedener akzeptierter Klassen, aktuelle Klasse, Tabu und Stagnation dokumentieren; 100 simulierte Restartziehungen aus genau diesem Archiv mit separatem Diagnoseseed durchführen. Verteilungen von Zielwerten, gewählten Klassen, Herkunft und Wiederholungen ausgeben. Für die ersten vier gezogenen Startklassen jeweils einen 5–8-Zug-Walk plus strikten Zielabstieg untersuchen, soweit das Gesamtbudget reicht; unvollständige Fälle als solche melden. Rückkehr zur bekannten TC-Bestklasse wird kanonisch geprüft. Diese künstlichen Restartproben werden niemals in den historischen Stundenlauf zurückgeschrieben.

Damit werden vier Erklärungen unterscheidbarer: (i) andere Klassen führen rasch zurück → Beckenhypothese; (ii) Archiv enthält Vielfalt, Wahl erreicht sie selten → Auswahlbias; (iii) Vielfalt wird gewählt, aber Walk kehrt zurück → Walklänge/-regel; (iv) wiederholter identischer Seed liefert andere Folge oder Tabu-/Restartzustand verletzt Regeln → Implementierungsproblem. Keine der ersten drei Beobachtungen beweist globale Unerreichbarkeit.

Bei einem Implementierungsproblem: Nachlauf vor Start anhalten, Fehler isolieren, neue Version und neues Vergleichsmanifest festlegen. Bei lediglich ungünstigen Parametern: alter Langzeitvergleich unverändert; neue Parameter nicht in dieselben zwölf Fortsetzungen einschleusen.

### C5. F, größere Trades und Familien

F bleibt strategisch offen. Der Prüfbestand zeigt ein lokales Minimum des HoG-F-Gründers in A∪P∪C3, keine globale F-Untergrenze. Der allgemeine Dreierzyklus ist **nicht** der vollständige Katalog sämtlicher Drei-Linien-Trades: Er verlangt drei disjunkte Dreiecke und eine bestimmte Spitzenpermutation. Gemeinsame Punkte und andere Neupartitionen fehlen weiterhin. Der alte Rotationsoperator war in einem historischen Job tatsächlich erfolgreich akzeptiert; „auf ausgewählten Graphen leer“ ist kein globaler Ausschluss.

Eine sinnvolle nächste Operatorhypothese, falls nötig, sind echte Drei-/Vier-Linien-Neupartitionen mit gemeinsamen Punkten. Exakte Spezifikation eines solchen späteren Kontrollprototyps:

```text
take a set Lout of k distinct existing triangle-lines, k=3 (later 4)
S = support; d[v] = number of removed lines through v
B = graph with all edges of Lout removed
enumerate distinct unordered triples of S
retain only triples with three different vertices and no pair already in B
enumerate unordered sets Lin of k triples with incidence multiplicities d
reject repeated pairs within Lin
form G' = B plus every pair in Lin
require full independent lambda validity, including all retained edges
exclude unchanged graph; deduplicate moves; score exact unordered pairs
emit (Lout,Lin) and its inverse (Lin,Lout)
```

Punktmultiplikitäten müssen exakt erhalten bleiben; mehrfach vorkommende Punkte dürfen nicht als disjunkte Kopien behandelt werden. Die Vollprüfung schützt auch gegen Berge-Dreiecke. Zunächst k=2 als Positivkontrolle für Apex und Pivot, inverse Trades und gezielte zusätzliche Dreiecke als Negativkontrolle. Ein beschränkt ausgewählter Linienblock ist kein vollständiger globaler k-Trade-Katalog. CPU-Abbruch ist `INCOMPLETE`, nie `LOCAL_MIN_EXACT`.

Diese Hypothese ist konkreter als pauschal mehr Population oder mehr neue Gründer. Crossover würde ebenfalls einen gültigen Trade beziehungsweise eine exakt überprüfte Rückkehr aus einem Reparaturmodus benötigen. Ein Reparaturmodus müsste ungültige Zwischenzustände separat halten und darf sie weder als λ-Rekord noch als Lösung zählen. Keine dieser Änderungen und keine Ω-Kampagne wird im nächsten Manifest aktiviert. Die bestehende Population 16 dient kontrollierbarer Fortsetzung; sie ist kein behauptetes Optimum. Ein größeres Archiv bleibt SQLite-basiert ohne künstlichen Klassen- oder Gesamtdateideckel.

### C6. Zeitdiagnose und Ressourcen

Die Differenz von 2979,1458815 s zwischen UTC und monotoner Gesamtdauer ist ein übernommener historischer Befund; die Quotientenrechnung aus den veröffentlichten Zahlen stimmt. Ihre Ursache ist weiterhin ungeklärt. `process_time` misst User-/System-CPU und schließt Schlafzeit aus; `wait4` liefert die Ressourcen des abgeholten Kindprozesses. Sie sind zwei Zugriffe auf verwandte Betriebssystemabrechnung, keine voneinander unabhängigen Hardwareuhren. [Python time](https://docs.python.org/3.12/library/time.html), [Python os.wait4](https://docs.python.org/3.12/library/os.html#os.wait4).

Der vorgeschlagene Test startet zuerst einen, dann 18 einthreadige eigene Rechenprozesse mit je 180 CPU-s Gesamtbudget. Aufzeichnung pro Sekunde und an gemeinsamen Barrieren:

- WSL: UTC/`time_ns`, `CLOCK_REALTIME`, `monotonic_ns`, soweit verfügbar `CLOCK_MONOTONIC_RAW` und `CLOCK_BOOTTIME`; Auflösung/Implementierung via `get_clock_info`.
- Jeder Worker: absolute Prozess-CPU (`process_time_ns`, `getrusage SELF`), Threadzahl und definierter Rechenzähler. Ein Abschnitt mit Warten muss CPU nahezu unverändert lassen.
- Controller: `/proc`-CPU während des Laufs, ausschließlich `wait4` beim Abholen; Start- und Abschlussoverhead mit erfassen.
- Unabhängiger **Windows-Hostprozess**: UTC und ein fortlaufender QPC-Zähler mittels `System.Diagnostics.Stopwatch`, mit Ping-/Pong-Zeitklammern zur WSL-Zuordnung. Dessen eigene CPU wird im Infrastrukturledger protokolliert. QPC ist für Intervalle, UTC für Kalenderzeit. [Microsoft-Dokumentation](https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps).

Der Hostprozess ist von der WSL-Uhrabfrage unabhängig, nicht zwingend von deren physischer Taktquelle. Er wird einmal gestartet und misst fortlaufend; einzelne PowerShell-Neustartzeiten werden nicht als vermeintliche Uhrendrift interpretiert. Optional vorhandene Suspend-/Resume-Ereignisse nur lesend korrelieren.

**Vorab technische Toleranzen:** abgeschlossene Worker-CPU gegen finalen absoluten Prozess-CPU-Wert höchstens max(0,1 s, 0,5 %) Differenz einschließlich gemessenem Nachlauf; kumulierte CPU höchstens Integral der aktiven Workerzahl über Hostzeit plus 1 % und gemessene Start-/Endklammern; monotone WSL-/Hostintervall-Abweichung bei durchgehend wachem Host höchstens max(0,5 s, 0,5 %) über den Test. Das sind Diagnosegrenzen, keine physikalischen Sätze. Überschreitungen führen zur Ursachenprüfung, nicht zu einer automatischen Korrekturmultiplikation.

**Budgetbasis:** weiterhin kumulative Worker-CPU plus explizit geschlossene Reserven. **ETA-Basis:** validierte Windows-Hostintervalle und beobachteter CPU-Durchsatz. Nur Realtime-UTC springt, monotone Hostzeit und CPU sind plausibel → UTC-Kalenderanzeige kennzeichnen, CPU-Fortsetzung möglich. WSL-monotonic weicht ab, CPU stimmt und Hostintervalle sind stabil → neue äußere ETA auf Hostzeit stützen; laufend parallel prüfen. Prozess-CPU/wait4 oder CPU/Hostrelation unplausibel → kein fairer CPU-Nachlauf, erst Messfehler klären. Ein kurzer bestandener Test erklärt die historische 49-Minuten-Abweichung noch nicht; deshalb laufen die Hostvergleiche auch im Nachlauf weiter.

Schutzregeln bleiben zunächst unverändert: 1 GiB Adressraum je Worker, 36 GiB gesamte eigene Prozessgruppe, 6 GiB MemAvailable-Reserve, 20 GiB Linux frei und 50 GiB frei auf dem **tatsächlichen** Windows-VHDX-Trägervolumen. Bei 18 Workern ist das individuelle Adressraumlimit stärker als die nominelle Gruppen-RAM-Grenze; Controller, Seitencache und andere Prozesse machen Gruppen-/Hostprüfung trotzdem nötig. Es gibt keinen Beleg für einen Bedarf an pauschal höheren Limits. Falls ein zulässiger kompletter Katalog den 1-GiB-Adressraum erschöpft, ist das ein technischer Fehlstatus mit gesichertem Zustand, kein Plateau- oder Nichtexistenzbefund.

Vor Kopieren/Start: realen Speicherbedarf der 24 Archivkopien und Bundle-Dateien messen, Linux- und physische Hostreserve **nach** dieser Allokation prüfen. Bei knapper Reserve keine Altarchive löschen. Ressourcenabfragen bisher etwa alle 15 s; diese Frequenz beibehalten und Kopierbedarf vorher prüfen. Erforderlichenfalls nur eigene Worker sauber pausieren. Die Gruppenprüfung muss sämtliche Fortsetzungs- und Rekordworker beider neuer Roots umfassen. Kein pauschaler 2-GiB-Laufdeckel, kein 600-s-Controllerstopp, keine Verdrängung nach 64 Klassen.

### C7. Konkret betroffene Dateien und Freigabekontrollen

| Bereich | vorhandene Bezugspunkte | neue Umsetzung / erforderliche Kontrolle |
|---|---|---|
| Auswahl/Kopien | `run.py`, `queueing.py`, `worker.py` aus 0.2.0 | Neuer äußerer Selektionscontroller; exakt 24 IDs, alte Tasks/Quellen unverändert; Hashbruch, falsches Ziel, fehlender Receipt und aktiver Quellprozess müssen abgewiesen werden. |
| Fortsetzung | `engine.py`, `worker.py` | Unterbrechung mitten im Katalog und vor Adoption: gleiche Folge/RNG bei Zählvergleich; tatsächlicher Replay-CPU-Verbrauch zählt. Alte 3600-Marke unverändert; keine Reservenrückgabe. |
| Rekordbank | `archive.py`, `search.py`, Gründerdatei | Neue Startdateien, 16 echte kanonische Klassen; falscher Score, doppelte Klasse und λ-Verletzung werden abgewiesen. Kein Import in alte Vergleichsjobs. |
| Tabu/Restarts | `engine.step_tabu`, `Archive.choose` | Entfernte Kante tabu, exakter Verfall, Aspiration nur bei striktem aktivem Rekord, alle-verboten ohne Adoption, Restart nach 2000 akzeptierten stagnanten Schritten; Walk-Ausnahme explizit prüfen. |
| Zeit/Ressourcen | `common.cpu`, `runtime.py`, `resources.py` | Neue Clockprobe und globaler Koordinator; absichtlicher Uhrensprung, fehlende Hostmessung und falsches VHDX-Volume werden erkannt. WSL-Test real auf Ryzen, kein Ersatzfixture als Hostnachweis. |
| Auswertung | alter `run.evaluate` | Neuer 24-Job-Auswerter plus getrennte 12-Job-Rekordauswertung, keine Erwartung von 192 neuen Ergebnissen. Manipulierter Messpunkt und unvollständiger Job dürfen nicht als regulärer Endpunkt eingehen. |
| Erfolgspfad | `Observer.solution`, `Queue.check` | Kleine echte srg(9,4,1,2)-Positivfixture mit Testparametern; n=9 und falsche Nullscores produktiv abweisen. Echter n=99-Nullresiduenzeuge zweifach dauerhaft sichern; global nur eigene Worker stoppen. |

Die alten Kontrollberichte sind positive historische Evidenz. Sie ersetzen die neuen Kontrollen des selektiven Controllers und der beiden parallel verwalteten Roots nicht. Vor Freigabe eines konkreten Starts müssen Manifest, Controllerfingerprint, Kontrollergebnisse und Hostdiagnose vorliegen.

## D. Vorab festgelegte Auswertung und Entscheidungen

### D1. Primärer Endpunkt

Vergleichseinheit ist das **Seedpaar**, nicht Gründer, archivierte Klasse, einzelner Zug oder Zwischenmesspunkt. Primärer Wert ist der aktive `(W,L1)`-Bestwert des W-Jobs bei 14400 kumulativen Budgetsekunden. Primärer Kontrast P gegen TC. Vollständige zwölf Paarwerte mit Vorzeichen der lexikographischen Differenz veröffentlichen; W-Differenzen separat mit Median, Bereich und fest definierter Streuung. Ein komponentenweiser Median ist kein existierender Graph.

Sekundär: 7200/10800, Verbesserung seit 3600 und seit 10800, Zeit bis Unterschreitung von W=2141, W=2130 und W=2121, Zahl kanonischer aktiver Bestklassen, Episoden/Restarts und tatsächliche CPU pro Fortschritt. Zeit bis Treffer ohne Treffer ist zensiert; nicht als Endzeitpunkt-Treffer behandeln. Beobachtete Nachbarrekorde, active best und künstliche Restart-/Abstiegsdiagnosen in getrennten Tabellen.

Alle zwölf Paare bleiben enthalten. Technisch fehlgeschlagene Jobs bleiben sichtbar und werden nach sauberer Diagnose zustandserhaltend vervollständigt; kein Entfernen ungünstiger Seeds und kein Neustart mit frischem Budget. Wegen nach Sichtung gewählten Horizonts, bekannten Starts und kleiner Seedzahl nur deskriptive Auswahlregeln, keine automatische Signifikanz oder allgemeine Überlegenheit.

### D2. Vorab Auswahlregeln

- **TC für weitere Hauptnutzung:** mindestens 8 Siege und höchstens 2 Niederlagen gegen P bei 14400. Der Effekt darf nicht allein als besserer Einzelrekord beschrieben werden. Schwelle ist eine praktische Auswahlregel, kein Signifikanztest.
- **P entsprechend stärker:** mindestens 8 Siege und höchstens 2 Niederlagen. Dann unverändertes P fortführen; kein Zwang, Migration, Crossover oder neue Familien einzubauen.
- **Keine klare Trennung:** P bleibt Arbeitsreferenz; TC bleibt dokumentierte Alternative. Seltene bessere TC-Rekorde werden gesichert, ohne die Paarbilanz umzudeuten.
- **Unveränderte weitere Verlängerung vorschlagen**, wenn mindestens 4/12 W-Jobs eines Verfahrens zwischen 10800 und 14400 noch lexikographisch verbessern; für die Fortführung genau dieser zwölf Jobs um weitere vier Stunden wäre ein neues Budget von 48 CPU-h nötig. Bei fortgesetztem P/TC-Paarvergleich wären es 96 zusätzliche CPU-h. Keine automatische Freigabe.
- **0–3 späte Verbesserungen:** kein voreiliger Unerreichbarkeitsbefund. Verbessert nur P weiter und TC bleibt bei derselben Klasse, unverändertes P bevorzugen und TC-Parameter als separate Hypothese bearbeiten. Bleiben beide still, gezielt Operator-/Archiv-/Beckendiagnose priorisieren; erneute lange unveränderte Kampagne braucht dann eine zusätzliche Begründung.
- **Methode verwerfen** heißt höchstens „in dieser Form für die nächste Kampagne nachrangig“, niemals „kann keine Lösung finden“. Echte Gültigkeits-/Budgetfehler führen unabhängig vom Score zur technischen Sperre und einer neuen Version.

Keine dieser Regeln beendet einen bereits freigegebenen Suchjob vor dem vereinbarten Messendpunkt wegen bloßer Stagnation. Ressourcengefahr, bestätigte Lösung und ausdrückliche Benutzerunterbrechung sind davon getrennt.

### D3. Rekordspur und F

Rekordspur meldet Verbesserungen ausschließlich gegenüber ihren eingepflanzten Startrekorden: W lexikographisch unter (2121,2440), Linf unter (2,216,2468), L1 unter 2388. Ergebnisse werden als aktive oder beobachtete Rekorde mit Herkunft und CPU getrennt gesichert. Sechs W-Jobs sind keine Konkurrenzschätzung gegen die zwölf alten W-Jobs, weil Startzustände und Historie verschieden sind.

Wenn mindestens zwei W-Rekordjobs in ihrer zweiten CPU-Stunde noch verbessern, kann eine weitere zweistündige Fortsetzung dieser sechs Jobs mit **12 neuen CPU-h** sinnvoll sein; auch das ist eine spätere Entscheidung. Ein einzelner neuer Rekord kann eigene Nachdiagnose rechtfertigen, aber keine behauptete robuste Methodenwirkung. Ein beobachtetes F<2836 wird sofort geprüft und archiviert und begründet eine neue F-spezifische Planung. Solange es fehlt, bleibt F=2836 ein empirisches Plateau, kein bewiesenes Optimum.

## E. Operative Reihenfolge, offene Risiken und Rückgabe

1. Diese Entscheidungsvorlage mit der unabhängig erstellten Reviewer-Rückgabe abgleichen; keine Vorab-Abstimmung erfolgte.
2. Nach Wahl des Budgets neuen äußeren Controller und Auswerter implementieren; alte Bundle-Dateien unberührt lassen. Die vorhandenen kleinen Prüfprogramme und das konkrete Manifest sind sofort verwendbare Spezifikationen.
3. Auf Ryzen ruhenden Originalstand, Fingerprints, Receipts, Datenträgerreserve und Python/pynauty prüfen; neue Verzeichnisse samt sicheren Kopien anlegen. Diagnosebudget durchführen, Ergebnisse vor Kampagnenstart vorlegen. Diese Planung erfordert dafür jetzt keinen Benutzerbefehl.
4. Erst nach Budgetfreigabe und bestandenen technischen Prüfungen die exakt ausgewählten Fortsetzungen sowie getrennte Rekordspur starten. Globale 18-Worker-Grenze, zehnminütige Statusmeldungen und eigene Ressourcenüberwachung.
5. Nach Abschluss neue Endpunkte, unveränderte alte Messpunkte, komplette Receipts, Kurven und getrennte Rekordlisten prüfen und veröffentlichen. Originalzustand und neue Zustände erhalten.

**Offene Daten:** Für die Planung fehlt nichts Entscheidendes. Für produktive Zustandsfortsetzung werden auf Ryzen die 24 vollständigen Task-/Checkpoint-/Result-/Receipt-/SQLite-Sätze, das Manifest/Fingerprint/Bundle und die alte Budgetdatei benötigt. Für die Archivdiagnose die zwölf TC/W-Archive. Für eine nachträgliche Erklärung der historischen Zeitabweichung wären `controller.log`, `comparison_timing.json` und passende Windows-/WSL-Zeit-/Suspendinformationen nötig. Keine erneute Uploadaufforderung ist nötig, solange diese Dateien lokal noch verfügbar sind. Ein bloßer ENDPOINTS-Download kann sie nicht ersetzen.

**Verbleibende Risiken:** Eine längere TC-Suche kann trotzdem im selben Becken bleiben; neue Startrekorde können P nur höhere Anfangsqualität geben, ohne neue Becken zu öffnen; SQLite-Abfragen mit `OFFSET` und Synchronisation können bei wachsenden Archiven teurer werden; der sichere Speicherbedarf des Kopierens ist noch auf Ryzen zu messen; ein kurzer Uhrenpass schließt seltene spätere WSL-Abweichungen nicht aus. Keines dieser Risiken begründet heimliche Änderungen am Vergleich.

### Was hier tatsächlich ausgeführt wurde

- Fest referenzierte Git-Dateien und Originalreview gelesen; benötigten Repository-Teil ausgecheckt. Die angeforderten Suchdateien und tatsächlichen Operator-/Auswahlabhängigkeiten im Code nachvollzogen; kein Kontakt mit dem anderen Bearbeiter.
- `analyse.py` ausgeführt: Veröffentlichungshashes, 193 Receipt-Rechnungen, 192 Endgraphen, 69 verschiedene veröffentlichte Graphen, 72 Paarvergleiche, 858 gültige Nachbarn samt inversen Zügen; danach die zwei strikten Abstiegsdiagnosen. Letzter Lauf ungefähr 11,1 lokale Prozess-CPU-s. Ein vorheriger Entwicklungsdurchlauf kostete ungefähr 8,3 s und fand denselben neuen Linf-Zeugen.
- `tc_prefix.py` ausgeführt: zwölf Seeds × 32 akzeptierte TC-Züge plus identische Wiederholung eines Seeds, insgesamt 416 überprüfte Adoptionen, ungefähr 189,6 lokale Prozess-CPU-s. Keine Zeittrajektorien- oder Restartreproduktion behauptet.
- `make_manifest.py` ausgeführt: exakte Jobauswahl, neue Rekordseeds, Zielstarter, bekannte Quelldateihashes und Budgetrechnung materialisiert. Kein Worker gestartet.
- Quellenstandprüfung der 46 im alten Bundle vorgesehenen Dateien gegen Commit b659cb8; Prüfergebnisse, Bericht, Manifest und kleine Programme als neue Projektdateien veröffentlicht.
- Offizielle Python-/Microsoft-Dokumentation für die Zeitdiagnose nachgesehen. Keine Uhrendiagnose auf Ryzen oder Windows ausgeführt.

Die vorhandenen Quellen, Endgraphen und Rechnungen reichen für diese Entscheidungsvorlage. Es wurde weder eine neue Ryzen-/Office-Kampagne gestartet noch ein vorhandener Lauf, ein altes Ergebnis oder ein fremder Prozess verändert.

### Dateien dieser Rückgabe

- `BERICHT.md`: dieser in sich geschlossene Bericht A–E.
- `OWN_CHECK.json`, `W_PAIRS.tsv`: eigene Datenprüfung und vollständige W-Paare.
- `POSTRUN_DESCENTS.json`: überprüfbare Graphen, Schritt und lokale Schlussdiagnosen.
- `TC_PREFIX.json`: sämtliche finiten Diagnosefolgen, Umfang und Grenzen.
- `PROPOSED_MANIFEST.json`, `PROPOSED_JOBS.tsv`: exakte, noch nicht gestartete Planung.
- `SOURCE_CHECK.json`, `DELIVERY_MANIFEST.json`: Quellenabgleich und Lieferdateihashes.
- `experiments/memetik/lambda_plan_codex_20260922/`: vollständige Programme `analyse.py`, `tc_prefix.py`, `make_manifest.py` und `validate_delivery.py`.
