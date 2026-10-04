# ROOT8105: Abgleich des Reviewer-Prüfpakets und revidierte Fortsetzung

04.10.2026. Ausgangsstand: ad92f0406c9f2e28eef59a326ecfbe76597ebcf0. Empfehlung, kein neuer Produktionslauf. Der frühere 480-CPUh-Vorschlag wird nicht unverändert empfohlen.

## Eingang und Aussageumfang

Originalarchiv: [efcf4a1f068d86f4216ccbfdf501bd8955972c80](https://github.com/ibenarb/conway99-research/tree/efcf4a1f068d86f4216ccbfdf501bd8955972c80/docs/reviews/20261004_root8105), Zweig `reviews/20261004-root8105-claude`. Eingang `files (17).zip`, byteidentisch als `files_17.zip` archiviert; äußeres ZIP enthält `README_review_tools.md` und `root8105_claude_review_tools.zip`. Inneres Paket: sechs Prüf-/Messprogramme, ein DP-Modul, Ergebnisdateien und Hashmanifest. Alle angegebenen SHA256 stimmen; äußere und innere README sind bytegleich.

**Ein separater strategischer Reviewtext fehlt.** Die README verweist auf einen „Antworttext“, der nicht im ZIP liegt. Auch die vollständige Kinderliste `root1_t1_children.json` des Beispielgenerators und Rohlogs der zahlreichen berichteten SAT-Crosschecks fehlen. Der folgende Abgleich betrifft die tatsächlich gelieferten Werkzeuge, Resultate und dokumentierten Vorschläge P0/P1/P2; keine Rekonstruktion einer nicht vorliegenden Reviewermeinung.

## 1. Wesentlicher Fortschritt: zählen statt alle Zeilen erzeugen

Der Reviewer formuliert eine exakte Zählung der projizierten Zeilen des historischen F(S,t). Auf Tiefe 1 genügt eine Kanten-DP auf den 14 Bordervertices. Eine H-Zeile wird als Auswahl nicht gematchter Borderpaare mit festgelegten kleinen Graden aufgefasst. Die DP zählt diese Auswahlen, ohne jede Zeile als SAT-Modell auszugeben oder auf Platte zu speichern.

Für S={u} ist das zusätzliche Sternsystem besonders einfach: Die zwei H-Nachbarn mit einem gemeinsamen Bordervertex zu u müssen im H-Anteil des Sterns isoliert sein. Die übrigen 2m-4 Nachbarn müssen paarweise gematcht werden. Ist die Zielzeile selbst Nachbar von u, müssen ihre gewählten Anschlüsse in dieses Muster passen; danach existiert die restliche Paarung im verbleibenden vollständigen Variablenraum. Ist die Zielzeile kein Nachbar, beeinflusst sie dieses Sternsystem nicht. Diese Reduktion rechtfertigt die Zählbedingungen von `width_fast` für gültige Rootzeilen. Es wird die Zahl der Zielzeilen gezählt, nicht die Zahl aller möglichen Stern-/SAT-Hilfsbelegungen.

Bei mehreren gebauten Zeilen sind die Sterne gekoppelt. Die allgemeine Funktion `width_exact` summiert über die relevanten Ziel-Adjazenzmuster: DP-Zahl der Zeilen zum Muster, multipliziert mit 0 oder 1 je nach Erfüllbarkeit des gesamten gekoppelten Sternsystems. Ein isolierter Test je Stern würde nicht genügen. Diese logische Zerlegung ist durch den Code nachvollziehbar; eine allgemeine formale Verifikation der Implementierung ist damit noch nicht erledigt.

**Änderung meiner Priorität:** Eine vollständige frühe Breitenmessung muss nicht mit der Materialisierung einer vollständigen Frontier beginnen. Der kostengünstige Zensus aller 8105 Roots wird jetzt vorgezogen. Meine vorher vorgeschlagene 32-Root-Aufzählung wäre für diese erste Frage unnötig teuer.

## 2. Ergebnisse und eigene Nachprüfung

Der Reviewer liefert für die 128 bisherigen Roots alle 83 Zielbreiten, insgesamt 10.624 Werte. Sie sind laut seiner DP exakte rohe Projektionsbreiten, keine Isomorphieklassen und keine SRG-Completion-Zahlen.

| Beispiel | ordered-Ziel | kleinstes Ziel | Verhältnis |
|---|---:|---:|---:|
| Root 1 | 15.525.813 | 173.365 | 89,56 |

Über alle 128 Roots beträgt der Median der individuellen Quotienten ordered/min rund 26,17; das Verhältnis der Summen rund 30,65. Letzteres ist keine populationsgewichtete Aussage. In 116 der 128 Fälle liegt ein Minimum bei den als isoliert bezeichneten u-Nachbarn. Es gibt zwölf Ausnahmen; deshalb keine universelle Regel „nimm immer einen isolierten Nachbarn“ einführen, solange alle 83 Breiten günstig exakt verfügbar sind.

Die Merkmalsklassen des Reviews zählen, wie viele der beiden isolierten u-Nachbarn einen Partner-Bordervertex 7 oder 8 enthalten:

| Typ | Rootpopulation | Pilotstichprobe | Bereich der kleinsten Breiten im Sample |
|---|---:|---:|---:|
| 0 | 7418 | 94 | 515.304–682.915 |
| 1 | 630 | 14 | 199.108–212.190 |
| 2 | 57 | 20 | 173.365–179.820 |

Die Populationstypzahlen habe ich aus `roots.tsv` selbst nachgerechnet. Typ2 mit Root1 umfasst nur 0,703 % der Population, aber 15,625 % des bisherigen Samples. Root1 ist daher ein besonders ungeeigneter alleiniger Kostenmaßstab für alle Roots. Auch innerhalb der Typen ist das bisherige Sample nicht automatisch eine einfache Zufallsstichprobe.

Die aus typgewichteten Samplemitteln berechnete Summe minimaler erster Breiten ist 4.675.782.997,287, gerundet 4.675.782.997. Die Rechnung stimmt. Sie bleibt eine Schätzung; erst P1 ersetzt sie durch den exakten Zensus. Selbst diese Summe würde rohe Zustände unter rootweiser bester Zielwahl zählen, keine globalen Isomorphieklassen.

Eigene Ausführung in isolierter Cloud-Auditumgebung, keine Ryzen-Messung:

- Rootzensus mit expliziter Gruppe der Ordnung7680: alle8105 Klassen, Stabilisatoren und Orbit-Summe56.011.010 reproduziert; ca.22,9s in dieser Umgebung.
- Sämtliche83 Breiten für Roots1,64,751,3675 mit geliefertem DP neu gerechnet:332/332 identisch. Auswahl umfasst alle drei Typen und einen Fall, in dem isolierte Nachbarn nicht das Minimum liefern.
- Zwei eigene Python-Zählungen durch Vertex-Elimination mit beliebig großen Ganzzahlen, ohne NumPy/SAT:173.365 für Root1/(0,8),204.768 für Root64/(0,8). Beide stimmen überein. Gemeinsame mathematische Reduktion, aber anderer Zählalgorithmus.
- Die drei gelieferten Tiefe2-Minima am angegebenen Ziel (1,7) nachgerechnet:22.410,22.403,22.399. Das prüft diese Ziele, nicht erneut alle22 Kandidaten pro Probe.
- Zusätzliche kleine und m7-Tiefe3-Crosschecks gegen unveränderte vollständige Glucose-Aufzählung stehen mit Zuständen/Zielen in `check_review.jsonl`. Jeder als MATCH gemeldete Fall wurde vollständig ausgezählt; keine zensierten Fälle als Übereinstimmung gezählt. Die m6-Fälle dieses Audits sind Nullfälle und ersetzen keine breite Positivabdeckung.
- Die größeren Kontrollgraph-/Präfixtests sind unter Abschnitt4 erläutert.

Nicht erneut ausgeführt: sämtliche10.624 DP-Werte, die im README berichteten Tausende früherer SAT-Crosschecks, die komplette m7-Tiefe1-SAT-Aufzählung des Reviewers und die volle Untersuchung aller höheren Tiefen. Eigenes Audit ist eine verstärkte Stichprobe plus Code-/Modellprüfung, kein pauschaler Beweis aller Eingaben.

Das NumPy-DP nutzt int64. Für m=7 ist die Anzahl aller während dieser Grad-DP ausgewählten Kantenmengen höchstens Summe(C(84,k),k=0..12)=134.744.793.483.572 <2^63. Daher ist dort kein Zählüberlauf zu erwarten. Diese Schranke ist nicht ohne neue Prüfung auf m=11 oder beliebige Modelle übertragbar. Dort wird in der BvLS-Kontrolle keine solche Breiten-DP ausgeführt.

## 3. Was die drei Proben der zweiten Erweiterung sagen

Root1, erste Zielzeile (0,8), erste Breite173.365. Die drei Stichproben liefern unter Regel R1 für die zweite Zielwahl minimale Breiten22.410,22.403,22.399. Der entsprechende Schätzwert

    173365 × (22410 + 22403 + 22399) / 3 = 3.884.069.460

betrifft die Zahl beschrifteter Tiefe3-Knoten im definierten R1-Suchbaum. Er ist keine exakte Schichtgröße, keine Zahl kanonischer Zustände und keine SRG-Anzahl. Die drei eng beieinanderliegenden Zahlen beweisen keine geringe Varianz über die gesamte erste Schicht.

Der Erwartungswert ist unter echten gleichverteilten Kindern aus der vollständigen ersten Projektion und fest definierter R1-Regel korrekt: W1 × Mittelwert(W2). Ein Minimum über eine fest definierte Kandidatenmenge ist dabei legitim; ein unbekanntes Minimum über alle Ziele darf daraus nicht behauptet werden. Die Regel prüft hier nur offene Ziele adjazent zu u oder zur ersten neuen Zeile. Für wechselnde Regeln oder kanonische Quotienten muss das Schätzproblem neu definiert werden.

Die zugrunde liegende vollständige Kinderliste fehlt im Eingang. `rng.choice` im Generator ist als uniform implementiert, aber die Vollständigkeit/Einzigartigkeit seiner externen Eingabeliste wurde hier nicht nachgeprüft. Zeitabhängiges Stoppen einer Probe kann ferner die letzte, teure Beobachtung zensieren. Für die Produktion vorab feste Stichprobenindizes planen und begonnene teure Proben zu Ende führen beziehungsweise als offen melden.

Selbst unter günstiger Zielwahl können die nächsten Schichten also sehr groß bleiben. Das ist ein starkes Argument für probabilistische Kostenmessung und gegen sofortiges Speichern ganzer Folgeschichten, aber noch keine globale Unmachbarkeitsaussage.

## 4. Größere vollständige Positivkontrolle

Der mitgelieferte Berlekamp–van-Lint–Seidel-Graph hat Parameter SRG(243,22,1,2). Die Konstruktion aus dem ternären Golay-Code wurde hier ausgeführt und geprüft:729 Codewörter, Minimaldistanz5; volle SRG-Matrixidentität; alle220 H-Zeilen bestehen Geometry.verify bei m=11 und den unabhängigen vollständigen Graphchecker.

Alle33 Präfixkontrollen über Tiefen1..219 sind SAT, und die absichtlich falsche gemeinsame-Nachbarn-Zahl wird sowohl vom Zeilenchecker als auch von der CNF zurückgewiesen. Die eigene Ergebniszusammenfassung stimmt mit der gelieferten überein.

Damit war meine vorherige Konzentration auf den kleinen 9er-Rookgraphen zu eng. Der größere echte SRG ist eine wesentlich stärkere strukturelle Kontrolle desselben parametrisierten Encoders. Die Präzisierung zu cand_A/B bleibt dennoch richtig: H-linear ist nicht automatisch SRG-kompatibel.

**Wichtige Grenze:** In den33 Tests werden sämtliche Kantenvariablen auf den bekannten Zeugen fixiert. Das prüft Encoderkompatibilität, nicht die Fähigkeit des Solvers, eine freie Completion selbst zu finden. Kanonisierung, Workerplanung und DRAT-Kette sind durch diese Kontrolle ebenfalls nicht automatisch getestet. Zudem ist m=11 nicht m=7; daraus folgt keine 99er-Laufzeitprognose oder Lösung.

## 5. Technischer Befund: Prüfsatz, noch kein Produktionsautopilot

Die Reviewerdateien bleiben unverändert archiviert. Vor einer produktiven Übernahme erforderlich:

- `census_level1.py` ignoriert fehlerhafte JSON-Zeilen und hängt an dieselbe Datei an. Ein abgerissener letzter Datensatz ohne Newline kann so mit dem nächsten Record verkleben; falsche fertige IDs werden nicht gegen Quell-/Codehash und Inhalt validiert. Ergebnisübernahme muss Schema, genau83 Breiten, ID, Root, Hashes und vollständige Datensatzgrenzen prüfen.
- `probe_level2.py` startet Seed und Sampleindex bei jedem Aufruf neu, öffnet aber im Append-Modus. Ein Restart kann dieselben Proben doppelt zählen. RNG-/Indexzustand dauerhaft führen oder Zufall deterministisch aus Root/Probe/Seed ableiten; genau-einmalige Übernahme.
- `crosscheck_sat.py` besitzt entgegen der pauschalen README-Aussage „kein Skript hat ein Zeitbudget“ einen optionalen `cpu_cap`; der m7-Pfad nutzt600s. Als historischer Review-Crosscheck markiert er Zensierung immerhin korrekt, darf aber nicht unverändert als GC-19-Produktionspfad verwendet werden.
- `width_exact` setzt gültige Teilzustände voraus und ruft selbst nicht den vollständigen Zustandschecker auf. Diese Vorbedingung vor jedem produktiven Aufruf prüfen. Überlappende forced/forbidden-Sets und ungültige Ziele müssen in allen verwendeten Zählroutinen ausdrücklich behandelt werden.
- Mehrdimensionale Flags und Zielmuster können die tiefere DP stark vergrößern. Sie ist nicht allein durch ihren Namen für beliebige Tiefen effizient. Zählerüberlauf, RAM und direkte/symbolische Kosten getrennt prüfen.
- Vor Sampling eine exakte Uniformitätskonstruktion belegen; SAT-Ausgabereihenfolge plus abgeschnittenes Reservoir genügt nicht. Eine bloße statistische Gleichverteilungskontrolle beweist Uniformität ebenfalls nicht.
- GC-19-Dialog, Weiterarbeit bis Antwort, persistenter Hintergrundkanal, vollständige CPU-Endbelege, begrenzte Überwachung und sichere Wiederaufnahme fehlen als integrierter Produktionsvertrag.

## 6. Revidierte Fortsetzungsempfehlung

### P0: Korrektheit und Betrieb vor dem Lauf

Reviewcode als Referenz erhalten; produktive Umsetzung separat versionieren. Reduktion F↔Zählmodell schriftlich fixieren. BvLS und Rook als exakte Kontrollen, m7-spezifische SAT/DP-Prüfungen auf verschiedenen Tiefen, insbesondere zusätzliche nichtleere m6-/m7-Fälle, gekoppelte Sterne und Grenzfälle aufnehmen. Ein DP-Zählwert ist nicht von selbst ein DRAT-Zertifikat.

Wenn später DP-Zahlen über mathematische Vollständigkeit entscheiden sollen, brauchen wir entweder eine unabhängig prüfbare Zählspur oder einen ausreichend unabhängigen verifizierten Zähler und eine explizite Beweisverbindung zum Encoder. Für reine Forschungs-/Ressourcenmessung kann die derzeitige doppelte Zählung mit Crosschecks genügen, solange sie nicht als zertifizierter Root-Ausschluss ausgegeben wird.

Produktionskontrollen: GC-19 sowie Crash mitten im Record, falsche/duplizierte IDs, RNG-Resume, Code-/Roothashänderung, RAM-/Disk-Grenzen. Keine laufenden Nutzerprozesse verändern. Offenstehende Modell-/Betriebsprüfungen nicht als erledigt markieren.

### P1: exakter Breitenzensus aller8105 Roots

Alle8105×83=672.715 Breiten berechnen. Speichern: Root-ID/-hash, alle83 Ganzzahlen, Minima/Argmin, Stabilisator, Typmerkmal, CPU/RSS und Codehash. Keine Kinderlisten und keine vollständigen Frontiers nötig. Alle83 Ziele verhindern die falsche Verallgemeinerung aus den116/128 isolierten Minima.

Bis elf Single-Thread-Worker, reale RAM-/Plattenverfügbarkeit vorher messen; C2-Checker bleibt unangetastet. Die vier eigenen Cloud-Tests benötigten ungefähr6–7CPU-Sekunden pro Root, der Reviewer schätzt etwa10. Das spricht für einen überschaubaren Zensus, ergibt aber noch keine Ryzen-ETA. Vorab eine gemischte24-Root-Messung auf dem Ryzen unter paralleler Last; Ergebnisse behalten, nicht doppelt zählen.

Vorschlag für P0+P1:48CPUh als großzügige Meldeschwelle, keine automatische Beendigung. Reiner Zensus dürfte nach den Cloud-Raten deutlich darunter liegen; keine Garantie. Format und Datenmenge nach einem Block messen. Nicht den früheren 480CPUh-Plan durch dieselbe Arbeit unter neuem Namen fortsetzen.

### P2: kontrollierte Kostenproben statt vollständiger Folgeschichten

Erst nach P1 und Kontrolle des Samplers:32 zufällig innerhalb veröffentlichter Typstrata gezogene Roots, vorgeschlagen24 vom dominanten Typ0 und je4 von Typ1/2. Root1 als zusätzliche feste Diagnose, falls nicht gezogen; seine Diagnose nicht ungekennzeichnet in populationsgewichtete Schätzer mischen.

Je Root64 vorab bestimmte uniforme Kinder der ersten, unter allen83 Zielen kleinsten Projektion. Einheitliche Tie-Break-Regel. Uniformität bevorzugt durch geprüftes DP-Rang-/Unrangverfahren ohne volle Materialisierung; bis zu dessen Verifikation nur aus nachweislich vollständiger eindeutiger Enumeration. Noch keine Behauptung, dass dieses Sampling im gelieferten DP bereits implementiert ist.

Für jedes Kind die festgelegte R1-Kandidatenmenge vollständig vermessen, dabei Auswahlkosten verbuchen. Ergänzend auf vorab bestimmten Diagnosefällen alle offenen Ziele prüfen, um die Beschränkung der R1-Kandidatenmenge zu bewerten. Stratumweise Schätzwerte, Varianz und offene teure Proben melden; keine ungewichtete Hochrechnung. Stichproben sind Kostendiagnose, kein Ausschlussbeweis.

Vorschlag:128CPUh als erste Meldeschwelle inklusive Auswahl/Enumeration, Checks und Nebenarbeit. Nach Ryzen-Messung präzisieren. Bei Erreichen weiterrechnen und Verlängerungsdialog stellen; die Zahl ist kein Abbruchlimit oder Fertigstellungsversprechen. Noch keine Zeitfreigabe/Implementierungsanweisung aus diesem Analyseauftrag ableiten.

### Entscheidung danach

- Zeigt P1 starke Reduktion durch exakte Zielwahl, diese als vollständigkeitserhaltende Reihenfolgeoption auswerten.
- Bleiben nächste Breiten groß, gezielt stärkere notwendige Bedingungen F_all oder direkte Residual-SAT/Cube-Zerlegung auf denselben Teilzuständen vergleichen. Lokale Breite allein misst nicht die gesamte Sucharbeit.
- Vollständige kanonische Schichten erst materialisieren, wenn ihre Größe und Deduplizierungskosten vertretbar gemessen sind.
- H-Faser-Memetik/Nearest-H bleibt ein separater Erkenntnispfad; kleine-Move-Isolation ist kein Augmentation-Pruningkriterium. P1 muss nicht darauf warten.

## 7. Fazit des Abgleichs

Die grundsätzlichen Warnungen meines ersten Berichts bleiben gültig: kein Rootausschluss, keine Tiefenbarriere16, keine Übertragung H-linearer Positivgarantien, keine repräsentative Proofkostenmessung aus512 ausgewählten Closures. Die Fortsetzungsmethode ändert sich jedoch wesentlich: günstiger vollständiger Zensus vor teurer Enumeration, exakte Zielwahl statt nur zufälliger dynamischer Wahl, größere echte SRG-Kontrolle und klar definierte Baumproben statt früher Materialisierung ganzer Folgeschichten.

Der separate Reviewer-Antworttext kann zusätzliche Argumente oder Empfehlungen enthalten. Er sollte vor einer abschließenden Gesamtentscheidung noch nachgereicht werden. Die aus dem vorliegenden Prüfsatz gewonnenen Ergebnisse sind davon unabhängig dokumentiert.
