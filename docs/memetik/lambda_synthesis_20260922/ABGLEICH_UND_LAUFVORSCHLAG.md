# Conway99 λ – Abgleich Codex / Reviewer und Vorschlag für den nächsten Ryzen-Lauf

Stand: 22. September 2026 · Version 1.0.0 · Entscheidungsvorlage, kein Startauftrag.

**Empfehlung:** P bleibt Referenz. Als einzige neue Suchvariante wird **PC = P mit vollständigem Dreierzyklus** geprüft. Zwölf P/W-Zustände werden bis vier kumulative Budget-CPU-Stunden fortgesetzt; zwölf PC/W-Jobs starten mit den ursprünglichen Gründern und erhalten je vier Stunden. Drei unveränderte TC/W-Fortsetzungen klären den wichtigsten Dissens. Getrennte Rekordläufe nutzen sofort die besten geprüften Graphen. **117 Such-CPU-h + 4 Diagnose-/Infrastruktur-CPU-h = 121 neue CPU-h.**

**Neues eigenes Resultat:** Den Zwei-Zug-Zeugen des Reviewers W=2116 habe ich unabhängig auf Gültigkeit, Scores, explizite Züge und Inversen geprüft. Ein anschließender vollständiger strikter Abstieg ergibt über einen weiteren Pivot **(W,L1,F,Linf,Nmax)=(2114,2450,3148,3,13)**. Danach existiert kein strikt besserer (W,L1)-Nachbar im geprüften Apex-/Pivot-/Dreierzyklus-Katalog. Das ist ein neuer Nachlaufzeuge dieses λ-Prüfbestandes; kein nachträglich verbesserter Kampagnenendpunkt und keine globale Rekordbehauptung.

## 1. Quellen und Arbeitsstand

- [Eigene bereits ausgeführte Rückgabe zum gemeinsamen Auftrag](https://github.com/ibenarb/conway99-research/blob/c91fbdfc78c615412a9fa922995f0682a1013ec4/docs/memetik/lambda_plan_codex_20260922/BERICHT.md).
- [Revieweroriginal und unverändertes Prüf-ZIP](https://github.com/ibenarb/conway99-research/tree/07a82903e029b58d31f496a96e3464dc0798678c/docs/reviews/20260922_lambda), separater Zweig `reviews/20260922-lambda-next`.
- [Gemeinsamer Auftrag](https://github.com/ibenarb/conway99-research/blob/0a3b7b6870f7892cbb229c5aee9fb04860e69fd1/docs/memetik/lambda_next_20260922/GEMEINSAMER_AUFTRAG.md).
- Ergebnisdaten: `84c46aac2b39d718c44daee2a7b994c29930e6c5`; eingefrorene Suchquellen: `b659cb8743dd6036d91dafb466b2d12cb21a29b0`.

Mein eigener Auftrag war schon ausgeführt; deshalb habe ich ihn nicht nochmals als neue unabhängige Ausarbeitung ausgegeben. Die jetzigen Rechnungen sind ausdrücklich **nach Kenntnis des Reviews** entstanden. Reviewerbericht und inneres ZIP bleiben byteidentisch. Eigene Bewertungen und Ergebnisse stehen getrennt.

Der Original-Ryzen-Lauf und Office-Prozesse wurden nicht berührt. Das vollständige 287-MiB-Originalarchiv wurde in diesem Abgleich nicht geöffnet. Historische SQLite-Inhalte, Pfad-Histogramme und die Uhrenursache sind daher weiterhin nicht hier nachgeprüft.

## 2. Was beide Ausarbeitungen gemeinsam tragen

P ist die praktische Arbeitsreferenz: gegen T gewinnt es nach einer Budgetstunde 11 von 12 W-Paaren, und 11 P-Jobs verbesserten sich noch zwischen 1800 und 3600 Sekunden. Gegen TC ist die Endpunktbilanz 6:6. P wurde von mir also nicht zum bewiesenen allgemeinen Sieger über TC erklärt.

Die drei neuen Verfahren schlagen die alte B0-Referenz im W-Ziel jeweils 12:0. Das vergleicht Verfahrenspakete. Nur der bisherige TC/T-Kontrast isoliert den größeren Katalog innerhalb derselben Tabusteuerung. Ob dieser Katalog im langfristig besseren P-Rahmen nützt, bleibt offen.

Archivrekorde sind konkret nutzbar. Der W=2123-Graph wurde im Lauf beobachtet, aber nicht als aktiver W-Bestgraph erreicht; nachgelagerte Rechnungen liefern 2121, nun 2116 und 2114. Das belegt nutzbare gespeicherte Kandidaten, noch keinen allgemeinen Vorteil von Migration oder Kooperation.

F=2836 bleibt das beste F dieses Vergleichsbestandes. Unveränderte F-Verlängerungen und eine gleichzeitige Ω-Kampagne sind nicht vorgesehen. Alle Ziele bleiben mathematisch getrennt. Lösungserkennung und Sicherung von Nebenrekorden laufen in jedem Job weiter.

## 3. Neue Resultate und eigene Prüfungen

### 3.1 Die neue W-Kette

| Herkunft / Schritt | W | L1 | F | Linf | Nmax |
|---|---:|---:|---:|---:|---:|
| Bester aktiver W-Endpunkt des Stundenvergleichs | 2130 | 2452 | 3112 | 3 | 8 |
| Historisch beobachteter Archivrekord | 2123 | 2442 | 3104 | 3 | 12 |
| Bereits veröffentlichter Pivot-Zeuge | 2121 | 2440 | 3100 | 3 | 11 |
| Reviewer: erster, vorübergehend schlechterer Pivot | 2128 | 2454 | 3128 | 3 | 11 |
| Reviewer: anschließender Dreierzyklus | 2116 | 2452 | 3148 | 3 | 12 |
| **Hier: weiterer Pivot** | **2114** | **2450** | **3148** | **3** | **13** |

Die letzte Änderung, Nummerierung 0–98:
entferne `{3,66}, {33,72}`, ergänze `{3,33}, {66,72}`.
Alle Zwischenzustände sind einfache 14-reguläre λ-Graphen. Vollständige graph6-Daten, Scores, Schritte und die Schlussnachbarschaft mit 137 Zügen stehen in `WITNESS_CHECK.json`.

Die Passage 2121 → 2128 → 2116 zeigt einen gültigen Ausweg mit zwischenzeitlicher W-Erhöhung um sieben. Sie beweist **keine minimale Barrierenhöhe sieben** über alle Wege. Da der Ausgangsgraph in Tiefe eins lokal minimal und in Tiefe zwei verbesserbar ist, beträgt die kürzeste verbessernde Zugzahl dort zwei, relativ zu genau diesem Katalog. Zur kürzesten Entfernung von 2121 bis 2114 wird keine Aussage getroffen.

L1 und F verschlechtern sich gegenüber dem W=2121-Zeugen. Das ist bei dem unveränderten lexikographischen Primärziel (W,L1) zulässig: kleineres W entscheidet zuerst. Diese Kette ist kein gemeinsamer Fortschritt aller Normen.

Der separate Linf-Starter aus meiner ersten Ausarbeitung bleibt `(Linf,Nmax,L1)=(2,216,2468)`, vollständige Scores `(2252,2468,2900,2,216)`. Der L1-Starter hat L1=2388.

### 3.2 Reproduktionen

In dieser Sitzung ausgeführt:

- Eigenes, vom Reviewerdecoder und Projektscorer getrenntes Set-Nachbarschaftsprogramm prüft den Zwei-Zug-Zeugen, beide Inversen, 17 verschiedene graph6/Score-Einträge aus den Reviewer-JSONs sowie alle enumerierten Nachbarn beim anschließenden strikten W-Abstieg.
- Reviewerprogramm `check_all.py` erneut ausgeführt: **43 verschiedene veröffentlichte Graphen, 19 Zensus-Zeugen, null Abweichungen**.
- Reviewer-Brute-Force-Apex/Pivot-Zensus an allen sechs Zensusgraphen erneut ausgeführt: Zuganzahlen und Verbesserungszahlen stimmen vollständig. Dieser Teil besitzt tatsächlich eine zweite, projektcodefreie Enumeratorimplementierung.
- Reviewer-Tiefe-2-Programm erneut ausgeführt: 21.961 Folgen am F=2836-Gründer ohne F-Verbesserung; 18.892 am W=2121-Zeugen mit zwei verbesserten beschrifteten Endzuständen, bester W=2116; 19.630 am W=2130-Endpunkt ohne Verbesserung; 17.295 am TC-W=2141-Endpunkt ohne Verbesserung.
- Reviewer-Zeitrechnung erneut ausgeführt; Budget- und Belegungsrechnung des neuen Manifests ausgeführt.
- 46 lokale Quellen gegen die SHA256-Liste der früheren Prüfung zu b659cb8 erneut abgeglichen. Die vorherige Git-Commit-Zuordnung bleibt eine übernommene, fest referenzierte Quellenprüfung.

Der Tiefe-2-Zensus benutzt weiterhin den Projektkatalog und dessen inkrementellen Scorer. Seine Wiederholung ist keine unabhängige Implementierung des allgemeinen Dreierzyklus oder sämtlicher negativer Tiefe-2-Aussagen. Der positive W-Zeuge wurde davon unabhängig vollständig validiert. Die Reviewer-Tabusonden mit 250 Schritten und die vollständigen Stundenpfade wurden hier nicht erneut reproduziert; ihre Aussage bleibt modellbasierte Evidenz. Die gelieferten TC-Präfixdateien wurden auf die behauptete Zusammenführung bei Iteration 22 nachgerechnet.

Technische Grenzen: Im Standard-Python ist pynauty nicht installiert; hier wurden deshalb keine Kanonisierungszertifikate neu berechnet. Dies ist für die expliziten Graph-/Score-Prüfungen nicht nötig. Vor produktiven Starts werden alle Gründer auf Ryzen mit der gepinnten pynauty-Version erneut kanonisiert. Ein lokaler Git-Klonversuch scheiterte an fehlenden Objekten der vorhandenen Partial-Clone-Kopie; die unveränderten vorhandenen Quellen konnten verwendet werden, Veröffentlichung erfolgt über die GitHub-Schnittstelle. Daraus wird kein Defekt des öffentlichen Repositorys abgeleitet.

## 4. Abgleich: wo ich ändere und wo ich widerspreche

| Frage | Meine erste Ausarbeitung | Reviewer | Entscheidung dieses Abgleichs |
|---|---|---|---|
| Arbeitsreferenz | P | P | Zustimmung |
| Unverändertes TC verlängern? | Alle 12 W-Jobs, 36 zusätzliche CPU-h | Hauptsächlich verwerfen; optional 3 Jobs | Nur Seeds 00–02, 9 CPU-h, jetzt als klar begrenzter Diskriminator |
| Neuer Katalog in P | Zunächst zurückgestellt | PC mit Dreierzyklus | Übernehmen; einziger neuer Hauptarm |
| Elite-Tabu TE | Nicht vorgeschlagen | 12 × 4 CPU-h | Zurückstellen; konkrete Kontroll- und Interpretationsprobleme |
| Rekorde aktiv nutzen | Sofort getrennte Rekordspur | Erst nach Stufe 1 und Ernte | Sofort getrennt; eingefrorene Startbank, keine Verunreinigung des Hauptvergleichs |
| Rekordpopulation | 15 Originalgründer + Zielrekord | 16 beste Klassen aus Ernte | Zunächst 15+1 beibehalten; Gründerstrategie nicht gleichzeitig vollständig ändern |
| F und neue Familien | Separat, nachrangig | Separat, strategisch offen | Zustimmung mit genauer Reichweitenbegrenzung |
| Neue Suchkosten | 96 h, dazu 4 h Hilfsbudget | 132 h zunächst, später bis 33 h mehr | 117 h Suche + 4 h Hilfsbudget = 121 h |

**Warum ich PC nun bevorzuge:** Der neue Zwei-Zug-Weg ist ein konkreter Nutzenbeleg für den Dreierzyklus an einem relevanten Rekordkandidaten, und TC schlägt T in 10/12 Stundenpaaren. Beides macht die Übertragung in den P-Rahmen zum gezielten nächsten Experiment. Es beweist noch nicht, dass der größere Katalog pro CPU-Stunde besser ist: Er erhöht Enumerationskosten und verändert bei gleichverteilter Perturbation auch die Wahrscheinlichkeiten bisheriger Züge. Genau dieser Paketvergleich P/PC wird gemessen.

**Warum nur drei TC-Fortsetzungen:** Mein früheres Argument einer ungeklärten Langzeitwirkung bleibt logisch bestehen. Der Reviewer liefert aber zusätzliche konkrete Evidenz für einen gemeinsamen Anfangstrichter und lange Drift. 36 weitere TC-Stunden erscheinen deshalb derzeit schwächer begründet als 48 PC-Stunden. Die festen Seeds 00–02 sind keine Auswahl nach günstigen Ergebnissen. Drei Jobs erlauben eine praktische Gegenprobe, keine belastbare Häufigkeitsschätzung.

**Warum TE noch nicht:** Kürzere Stagnationsschwelle (200 statt 2000) und neue Elite-Auswahl sind zwei gleichzeitige Änderungen. Der Reviewer prüft damit ein Restartpaket, nicht einen isolierten Parameter. Sein vorgeschlagener Differentialtest ist außerdem fehlerhaft: Eliteanteil null wählt immer gleichverteilt aus dem Archiv, historisches TC dagegen zu 25 % gleichverteilt und sonst das Beste aus acht Ziehungen. Selbst bei reparierter Baseline bleibt ein 300-Schritte-Test ohne erzwungenen Restart unter der 2000er Schwelle für diese Änderung wirkungslos. Vor TE braucht es einen echten Legacy-Modus mit identischem RNG-Verbrauch und einen Test, der die Restartgrenze tatsächlich überschreitet. Eine zeitbegrenzte Positivprobe, die zufällig einen cycle3-Zug finden soll, ist ebenfalls kein robuster Korrektheitstest; dafür werden gezielte bekannte Zustände benutzt. Die Aussage „200 ist das Zehnfache von etwa 60 Schritten“ stimmt rechnerisch nicht; die erwartete Zahl von 15–18 Restarts je vier Stunden ist aus dem vorliegenden Durchsatz nicht hergeleitet.

**Vier fachliche Präzisierungen des Reviews:**

1. Gleicher Anfang und gleicher bester Endgraph beweisen keine statistische Abhängigkeit unabhängiger Zufallsströme. „Pseudoreplikate“ ist deshalb zu pauschal. Richtig ist: zwölf Wiederholungen derselben Gründerbedingung ergeben keinen Test über zwölf verschiedene Startfamilien. Die gelieferten 40-Schritt-TC-Sonden enthalten sogar zwölf verschiedene Gesamtfolgen.
2. HoG-Herkunft aller berichteten Endbesten ist ein Befund zu den erfolgreichen Abstammungslinien. Die Populationen besitzen trotzdem 16 verschiedene Gründer; daraus folgt nicht, dass überhaupt keine anderen Familien durchsucht wurden. Beschriftete Kantenabstände sind keine isomorphieinvariante Distanz und beweisen bei anderen Labels keine strukturelle Ferne.
3. Kein besserer Zustand in Tiefe zwei am HoG-F-Gründer bedeutet: Ein verbessernder Weg ab genau diesem Graphen benötigt mindestens drei Katalogzüge. Das ist keine untere Schranke für eine positive F-Barrierenhöhe und erklärt allein nicht die Ergebnislosigkeit langer Suchpfade.
4. Die 18-Slot-Zeituntergrenze ist unter den dokumentierten Annahmen sinnvoll. Sie identifiziert aber nicht, welche Uhr falsch ist; insbesondere folgt daraus nicht „genau eine Zeitbasis muss abweichen“. „Alle Arme werden gleich gemessen, also bleibt der Vergleich sicher fair“ setzt einen über Zeit/Last/Arme stabilen Messfehler voraus und ist nicht schon bewiesen.

## 5. Konkreter nächster Lauf

Zielrechner: **Ryzen RB-CUBE, Ubuntu unter WSL2, höchstens 18 einthreadige Worker insgesamt**.
Office und der Symmetriezweig bleiben außerhalb dieses Auftrags.

### 5.1 Jobs und Budget

| Gruppe | Anzahl und Laufzeit | Neue CPU-h |
|---|---|---:|
| Pext/W: ursprüngliche P-Seeds 00–11 fortsetzen | 12 × 3 zusätzliche h; kumulativ 1 → 4 h | 36 |
| PC/W: ursprüngliche 16 Gründer, dieselben gepaarten Seeds | 12 × 4 h, frischer Start | 48 |
| TCx/W: ursprüngliche TC-Seeds 00–02 fortsetzen | 3 × 3 zusätzliche h; kumulativ 1 → 4 h | 9 |
| R/W: drei P/PC-Paare ab W=2114, jeweils gleiche Population und Seed | 6 × 2 h | 12 |
| R/Linf: P ab (2,216,2468) | 4 × 2 h | 8 |
| R/L1: P ab L1=2388 | 2 × 2 h | 4 |
| Uhrenkontrolle ein Worker + 18 Worker | 19 × 180 CPU-s | 0,95 |
| Wiederaufnahme- und PC-Kontrollen | gesamt höchstens 3780 CPU-s | 1,05 |
| Schreibgeschützte OBSERVED-Ernte und gezielte Nachdiagnose | gesamt höchstens 3600 CPU-s | 1 |
| Controller, Hashes, Export, Host-Hilfsprozesse | eigenes Ledger | 1 |
| **Gesamt** | **39 Suchjobs, 117 Such-h + 4 Hilfs-h** | **121** |

Keine weiteren F-, B0-, T- oder TE-Jobs. Die alten 191,735 tatsächlich verbrauchten CPU-h werden nicht als neues Budget verbucht. Die fünf Sekunden Abschlussreserve bleiben je neuem Endpunkt im Budget; geschlossene alte Reserven werden nicht wieder freigegeben.

Die 4 h sind keine Garantie, jede beliebige Vollprüfung/Archivernte abschließen zu können. Ernte dedupliziert zunächst OBSERVED-Rekorde; beim Ende der Zuteilung werden exakte Abdeckung und Restmenge ausgewiesen. Ein unvollständiger Zensus ist INCOMPLETE, niemals ein Minimalitätsbeweis. Hilfsbudgetüberschreitung wird nicht verdeckt aus Suchjobs finanziert. Die vorhandenen Rekordstarter benötigen keine abgeschlossene Vollernte als Startvoraussetzung.

### 5.2 Genaue Starter und Seeds

`PROPOSED_MANIFEST.json` enthält alle 39 IDs, ganzen Seedzahlen, historische Receipts, neue Budgetanteile und die feste Queue; `PROPOSED_JOBS.tsv` ist die lesbare Jobliste.

- Pext und TCx verwenden die kopierten Originalzustände einschließlich RNG, Population/Pfad, Tabu, Archiv und unvollständiger Katalogpräfixe. Kein Neubeginn aus dem bloßen Bestgraphen. Die alten Seeds dienen nur der Zuordnung.
- PC verwendet die 16 Originalgründer byteidentisch; Seed i = `derive_seed(2026092104, ["lambda-compare", i])`.
- R/W verwendet drei neue, gepaarte P/PC-Seeds. Für alle Rekordziele gilt Seed i = `derive_seed(2026092202, ["lambda-record-synthesis", target, i])`.
- Rekordpopulation: Genau der nach (Zielschlüssel, state-SHA256) schlechteste Originalgründer wird durch den jeweiligen feststehenden Rekord ersetzt; die übrigen 15 und ihre Reihenfolge bleiben erhalten. Die exakten Graphen und Ersatzpositionen stehen in `RECORD_BANK.json`. W ersetzt Position 5, Linf und L1 Position 2, jeweils nullbasiert.
- Alle Rekordpopulationen werden vor Start erneut unabhängig geprüft und kanonisch dedupliziert. Ein neuer Rekord während der Ernte ändert die bereits festgelegte Bank nicht stillschweigend. Er wird separat gesichert und kann eine explizite neue Manifestversion begründen.

Es gibt keine Migration zwischen Haupt- und Rekordjobs, kein gemeinsam beschreibbares Sucharchiv und keine nachträgliche Vermischung ihrer Statistiken.

### 5.3 PC-Regel und erforderliche Umsetzung

PC übernimmt vollständig P-Elternwahl, Population 16, Familienregeln, Perturbationslängen/-gewichte und Abstieg. Einzige algorithmische Erweiterung: Vollständiger eindeutiger Katalog Apex ∪ Pivot ∪ cycle3 **sowohl bei Perturbation als auch bei Abstieg**. Perturbation wählt gleichverteilt einen Katalogzug, Abstieg den lexikographisch besten strikt besseren Nachbarn mit stabiler Generatorreihenfolge. Keine zusätzliche Tabusteuerung. Jede übernommene oder als Rekord gespeicherte Konfiguration wird vollständig unabhängig geprüft.

Erforderlich ist eine neue Versuchsversion mit neuer äußerer Steuerung und PC-Engine. Die eingefrorenen Originaldateien werden nicht editiert. Pext/TCx laufen aus einer unveränderten Bundlekopie; neue Jobs liegen separat. Der Koordinator kennt je Job Enginepfad, Budget und Datenwurzel. Das alte pauschale `extend` ist ungeeignet, weil es alle 192 Jobs erweitern würde.

PC muss an allen Variantendispatches als P-Episodenverfahren behandelt werden; Katalogfreigabe allein genügt nicht. Ein abgeschlossener Abstieg meldet `LOCAL_MIN_EXACT_APC`, nicht das irreführende alte AP-Label.

Vor produktivem Start erforderlich:
- Baseline-PC mit deaktiviertem cycle3 reproduziert P über eine feste Anzahl Episoden und inklusive RNG.
- Der bekannte Reviewer-Zyklus wird als Katalogmitglied positiv nachgewiesen; ein ungültiger injizierter Zug wird abgewiesen.
- Der neue W=2114-Zeuge und alle Startbanken bestehen den unabhängigen Prüfer.
- Unterbrechung/Wiederaufnahme mitten im Katalog reproduziert die Zugentscheidungen bei Zählvergleich; Replay-CPU wird zusätzlich innerhalb des Budgets gezählt.
- Alte Messpunkte 600/1800/3600 bleiben unverändert; manipulierte Task-, Receipt-, Resultat- und Checkpoint-Hashes werden abgewiesen.
- Alle Datenkopien sind konsistente SQLite-Snapshots. `immutable=1` nur bei nachgewiesen eingefrorenem, vollständig gecheckpointetem Stand ohne relevante WAL-Restdaten; ansonsten Backup einer konsistenten Nur-Lese-Verbindung.
- Der globale Erfolgspfad und Ressourcenwächter umfassen alle neuen Datenwurzeln und stoppen ausschließlich eigene Worker.

### 5.4 Zeitmessung und Betrieb

Die alte Untergrenze aus dem Reviewerprogramm lautet 39.545,244255 s für 192 nicht zwischen Slots migrierende Einzelsitzungen auf höchstens 18 Workerplätzen, jede mit mindestens 3595,022205 Prozess-CPU-s. Die UTC-Dauer 39.890 s liegt darüber; monotone 36.910,854118457 s darunter. Die reine Arbeitsmengen-Untergrenze ist 38.347,032289 s. Beide widersprechen der gemeldeten monotonen Dauer bei gesunder gemeinsamer Sekundenbasis.

Daraus folgt zunächst ein Erfassungs-/Zeitbasisproblem, keine kalibrierte Korrektur. Die historische faire CPU-Zurechnung ist plausible Evidenz, aber keine Freigabe, einen beliebigen Skalenfaktor vorauszusetzen.

Die Diagnose vergleicht laufend Gast-Realtime, monotone Uhren, Prozess-/Thread-CPU, abschließendes wait4 und einen **fortlaufenden Windows-Hostprozess mit monotonem Intervallzähler und UTC**. Ein Prozess, dann 18, jeweils 180 Prozess-CPU-s; aktive Workerzahl und Hostintervall gemeinsam protokollieren. Keine einzelne neue PowerShell-Startdauer als vermeintliche Drift auslegen.

Budget während eines Workers: eigene Prozess-CPU (getrusage); endgültige Abrechnung: wait4 plus explizite Reserven. wait4 steuert nicht allein die innere Suchschleife. ETA und Zehn-Minuten-Statusabstände: validierte monotone Hostintervalle.

Wenn nur Gast-monotonic abweicht, aber Prozess-CPU und Hostmessung konsistent sind, kann die ETA auf Hostintervalle umgestellt werden. Bei ungeklärter Prozess-CPU/Host-Inkonsistenz zuerst klären, kein stilles Durchstarten mit skalierten „CPU-Stunden“. Ein kurzer bestandener Test erklärt die alte Anomalie noch nicht; der Vergleich läuft während des gesamten Versuchs weiter.

Ressourcen bleiben: 1 GiB Adressraum je Worker, 36 GiB eigene Prozessgruppe, 6 GiB freier RAM, 20 GiB Linux-Platz und 50 GiB frei auf dem tatsächlichen Windows-VHDX-Trägervolumen. Kopierbedarf vorab messen. Keine Archive löschen, keine pauschalen 64-Klassen-, 2-GiB-Lauf- oder 600-s-Gesamtstopps. Kein vorzeitiger Stopp wegen bloßer Stagnation.

Die berechnete Queue erreicht im idealisierten Ein-CPU-Sekunde-pro-Slotsekunde-Modell **7 h** bei 92,86 % Auslastung. Sie verschränkt P/PC-Paare, lässt früh drei Rekordjobs freie Slots füllen und startet dann die TC-Probe. Das ist eine Belegungsrechnung, keine gemessene Ryzen-Laufzeit. Vorsichtig **7–10 h Suche, etwa 8–11 h einschließlich Diagnose und technischer Einrichtung** einplanen; die Implementierungsarbeit ist darin nicht garantiert. Neue ETA nach der Last-/Uhrenprobe. SMT-Einfluss, Hash-/SQLite-Kosten und die tatsächliche Arbeit pro CPU-Sekunde werden gemessen.

## 6. Auswertung und Entscheidung nach dem Lauf

Primärer Kontrast: **PC gegen Pext**, Einheit das zugeordnete Seedpaar, aktiver (W,L1)-Bestwert bei 14.400 kumulativen Budgetsekunden. Alle zwölf Paare bleiben in der Auswertung; keine Auswahl günstiger Seeds. Dies ist eine explorative Folgeuntersuchung mit wiederverwendeten Seeds und bekannten Gründern, keine neue unbeeinflusste Bestätigung.

Pext zahlt reale Wiederaufnahmekosten, PC beginnt neu. Replay-CPU, Katalog-/Episodendurchsatz und SMT-Last werden getrennt ausgewiesen. Der Vergleich bei 3600 s nutzt historische P-Messpunkte und frische PC-Messpunkte; ohne Replayasymmetrie, aber nicht gleichzeitig auf demselben Hostzustand gemessen. Keinen dieser Vorbehalte durch nachträgliche Bonuszeit ausgleichen.

Messpunkte: 600/1800/3600, dann 7200/10800/14400. Für fortgesetzte Jobs neue Zwischenpunkte aus den vollständigen Kurven mit `record_cpu <= mark` ableiten. Historische Endpunkte werden nicht nachträglich verändert. Rekordspur separat bei 600/1800/3600/7200.

Vorab praktische Auswahlregeln:
- PC gewinnt mindestens 8 Paare und verliert höchstens 2: PC für die nächste Hauptstufe bevorzugen.
- P gewinnt mindestens 8 und verliert höchstens 2: unverändertes P bevorzugen.
- Sonst bleibt P Referenz; bessere PC-Einzelrekorde werden gesichert, begründen aber keinen allgemeinen Methodensieg.
- TCx: mindestens 2/3 Jobs mit aktivem W<2141 schwächen die konkrete Prognose des Reviewers und begründen eine erneute Entscheidung zur restlichen TC-Fortsetzung. 0/3 rechtfertigt derzeitige Nachrangigkeit, keinen Ausschluss späteren TC-Erfolgs. L1-Verbesserung bei W=2141 zusätzlich separat berichten.
- Rekordspur beurteilt nur Verbesserungen gegenüber ihren jeweiligen Startrekorden. Drei W-Paare sind diagnostisch, kein robuster Methodenvergleich und kein Migrationstest.
- Mindestens 4/12 späte (W,L1)-Verbesserungen eines Hauptarms in (10800,14400] begründen einen Vorschlag für weitere vier Stunden je Job (+48 neue CPU-h je zwölf Jobs). Keine automatische Verlängerung. Weniger späte Verbesserungen beweisen keine Unerreichbarkeit; sie verschieben die Begründungslast zu Familien-/Trade-/Restartdiagnosen.
- F<2836 wird sofort unabhängig geprüft und gesichert und kann eine neue F-spezifische Stufe begründen. Ein echter Nullresiduenzeuge löst unabhängig vom aktiven Ziel die gemeinsame Sicherung und den kontrollierten Stopp eigener Worker aus.

Zu veröffentlichen: sämtliche Einzelwerte und Paarbilanzen, Median und Bereich, vollständige Bestwertkurven, aktive vs beobachtete Rekorde, Abstammungslinien, kanonische Diversität, Restarts, CPU-Abrechnung einschließlich Reserven, Wiederaufnahmekosten und technische Fehlstände. Aus zwölf Seeds wird nicht automatisch Signifikanz abgeleitet.

## 7. Operativer Stand

Dieser Abgleich liefert Bericht, geprüfte neue Graphen, genaues Manifest mit 39 Jobs, feste Startbanken und berechnete Queue. **Kein neuer Suchlauf wurde gestartet; der produktive neue Controller und die PC-Integration sind noch nicht implementiert.**

Der nächste konkrete Arbeitsschritt ist die Umsetzung genau dieses Manifests in einem neuen Paket, einschließlich der genannten Kontrollen. Danach erfolgen die Ryzen-Preflight-/Uhrenprüfung und die Budgetfreigabe vor dem tatsächlichen Kampagnenstart. Manueller Rechnerbetrieb weiterhin genau ein Bash-Einzeiler pro Rückmeldung. Für die jetzige Entscheidungsvorlage wird kein Befehl auf dem Office- oder Ryzen-Rechner benötigt.

Strategisch bleibt anschließend eine echte Frage nach anderen Gründerfamilien offen. Die jetzige Entscheidung priorisiert zunächst einen begründeten Katalogvergleich und die bereits greifbaren Rekorde; sie erklärt HoG weder zur einzigen aussichtsreichen Familie noch zur globalen Lösungsregion.

## Dateien

- `WITNESS_CHECK.json`: eigener Zeugencheck und neuer W=2114-Graph.
- `RECORD_BANK.json`: konkrete Starter W, Linf, L1 und Austauschpositionen.
- `PROPOSED_MANIFEST.json`, `PROPOSED_JOBS.tsv`: verbindlich spezifizierter Vorschlag, noch nicht freigegeben.
- `SCHEDULE.json`: idealisierte 18-Slot-Belegung.
- `REPRODUCTION.json` und `reproduced/`: tatsächlich erneut ausgeführte Reviewerprüfungen und deren Reichweite.
- `experiments/memetik/lambda_synthesis_20260922/check_review.py` und `make_manifest.py`: vollständige kleine Prüf- und Spezifikationsprogramme; kein Suchcontroller.
