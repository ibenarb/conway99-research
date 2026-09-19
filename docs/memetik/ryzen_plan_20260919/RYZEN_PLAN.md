> Historischer Entwurf vor Eingang des tatsächlichen Reviews. Für die aktuelle Empfehlung gilt [Plan V2](RYZEN_PLAN_V2.md); siehe [Reviewabgleich](REVIEWABGLEICH.md).

# Memetik auf Ryzen: konkrete Fortsetzungsplanung
Stand 19.09.2026. Planungsauftrag, kein gestarteter Lauf. Basis memetik/958744f8b53ce66894a8b29e9bdfa033871574b0 sowie neu geprüfter Dateneingang; siehe EINGANG_UND_ABGLEICH.md.

## 1. Forschungsfrage und Gegenpositionen
Primärfrage: Verbessert eine größere strukturell gemischte Gründerbasis mit kontrollierten neutralen/schlechteren Ausflügen die Zielwerte und die Zahl neuer guter Endpunktklassen pro Rechenzeit?

Drei Gegenpositionen sind ernst zu nehmen:
1. Nur die besten F02/HoG-Nachfahren einsetzen: effizienter kurzfristiger Abstieg, aber hohe Gefahr wiederkehrender Endpunkte und blinder Flecken.
2. Alle Generatoren gleich gewichten: transparent, aber F03/F04 und G1/G2 sind verwandt; viele Namen würden verwandte Strukturen übergewichten. Schlechte teure Generatoren könnten Arbeit binden.
3. Möglichst viele Zufallsstarts statt langer Abstiege: schützt Breite, aber der alte Ω-Pilot zeigt, dass ohne genügend Abstieg und tatsächlich abgeschlossene Störungen bloß viele abgebrochene Versuche entstehen.

Vorschlag: gemischte Population mit begrenztem Qualitätsvorrang, explizitem Neuheitsanteil und gleichen CPU-Kontingenten je Arm/Ziel. Kein automatischer Sieg einer komplexeren Steuerung; einfacher Kontrolllauf bleibt Vergleich.

## 2. Ausgangspopulation: 128 Gründer, 384 Zielplätze
Ziel 64 gültige verschiedene Startgraphen je Arm. Dieselben 64 Graphen eines Arms starten jeweils in L1, F und (Linf,Nmax,L1). Das sind 128 Gründer und 384 aktive Plätze. Die Kopien zwischen Zielen sind absichtlich dieselben Starts, keine unabhängigen Stichproben.

### Ω: vorläufige Aufnahmequoten
| Herkunft/Erzeuger | Zielplätze |
|---|---:|
| Historischer Bestand und geprüfte Nachfahren, einschließlich A als Kontrolle, B- und C02-Zeugen | 12 |
| F02-Viererfaserkonstruktion, neue Seeds und Parameter | 20 |
| Freier Ω-CSP mit randomisierten Kosten, ohne F02-Faserzwang | 8 |
| G1: kantenweiser Aufbau nach Option 1 | 8 |
| G2: Randmatchings zuerst, dann Restergänzung | 8 |
| G4: kontrollierte λ-Überschussfehler, Ω hart | 4 |
| Explorationsreserve: G3 oder lokale K66/C2/C3-inspirierte Vorlagen mit freigegebenen Symmetrieannahmen | 4 |
| Summe | 64 |

Die zwölf Archivplätze werden nach Deduplikation vergeben; C02-Nachfahren bleiben in der Gesamtstatistik F02-Abstammung und zählen zur Familienobergrenze. A genau einmal, keine acht erstarrten Kopien. Alle bewährten Originale bleiben unabhängig von der aktiven Auswahl archiviert.

### λ: vorläufige Aufnahmequoten
| Herkunft/Erzeuger | Zielplätze |
|---|---:|
| HoG-Stämme und geprüfte Nachfahren einschließlich Linf=2-Zeuge | 12 |
| Unregelmäßige Dreieckspackung nach dem gültigen Claude-C-Prinzip, neue Seeds | 16 |
| Z33-Lifts: F03 vier, allgemeinere F04 zwölf | 16 |
| G3: Ω∩λ-Konstruktion, sofern sie tatsächlich zulässige neue Graphen erzeugt | 8 |
| Gezielte größere Zerstörung/Reparatur vorhandener λ-Strukturen | 8 |
| Weitere lokal vorstrukturierte, anschließend freigegebene Erzeugung | 4 |
| Summe | 64 |

Reparaturnachfahren sind keine neue unabhängige Familie; Abstammung explizit. F03/F04 werden gemeinsam als verwandte Liftgruppe gezählt. G3 ist eine unsichere Reserve, kein bereits vorhandener Generator mit garantierter Ausbeute. Ein Ω∩λ-Graph darf mit identischer Identität in beiden Armen geführt werden; dieser Überlapp wird berichtet.

### Aufnahme und Ausfallregel
Zunächst je Generator höchstens viermal die Zielquote an Kandidaten sammeln, mit global höchstens 32 Worker-CPU-Stunden für neue Konstruktion. Versuche, gültige Ausgaben, Isomorphieklassen, Kosten und Fehlschläge zählen. Bestehende Graphen nicht unnötig reproduzieren.
Aus jeder Quelle ungefähr die Hälfte nach zielübergreifender Rangqualität, die Hälfte nach struktureller Verschiedenheit wählen. Zielübergreifende Ränge dienen nur der gemeinsamen Startauswahl, nicht einer vierten Zielfunktion; vollständige Scorevektoren bleiben erhalten.
Ungefärbte Isomorphie zur Gründerzählung; in Ω unterschiedliche Rahmen separat registrieren, nicht als neue unabhängige Gründer zählen. Bei Arbeitszuständen später höchstens zwei belegbar verschiedene Rahmen derselben ungefärbten Klasse zulassen, falls sinnvoll; keine ungeprüfte Quotientensuche.
Kein Abstammungscluster soll anfangs mehr als 24 der 64 Plätze eines Arms beanspruchen, einzelne unmittelbare Elternlinie höchstens vier. Wenn ein Quotenblock ausfällt, zunächst an andere gültige unterrepräsentierte Quellen verteilen. Gelingt das nicht, tatsächliche Population kleiner beginnen (mindestens 32 je Arm angestrebt) statt Klone als Gründer auszugeben. Wenn selbst 32 nicht erreichbar sind, vorhandene Zahl offen nennen und Vergleichsgröße anpassen.

## 3. Kritische Prüfung von Option 1 und G1–G4
Sei c_uv die aktuelle Zahl gemeinsamer Nachbarn. G1 mit c_uv≤1 für vorhandene Kanten ist eine sinnvolle Begrenzung, aber nicht λ=1: manche Kanten können null gemeinsame Nachbarn haben. Nach jedem Kantenaufbau müssen alle betroffenen Bedingungen erneut geprüft werden, nicht nur die neu eingefügte Kante. Partielle Grade/Margen dürfen unter Soll liegen; vollständige Aufnahme erst nach Erfüllung aller harten Gleichungen. Rücknahme und Restkapazitätsprüfung sind notwendig.

Im Ω-Rahmen hat H genau 504 Kanten. Für jede der 14 Randpositionen erzwingen die entsprechenden Margen ein perfektes Matching auf zwölf Außenknoten. Insgesamt sind das 84 H-Kanten; 420 H-Kanten bleiben zwischen disjunkten Außenlabels. G2 ordnet diese bereits durch Ω verlangten Entscheidungen zuerst an: anderer Erzeugungsweg, nicht automatisch anderer zulässiger Raum.

G3 ergänzt den Rest durch 140 äußere Dreiecke; zusammen mit sieben Wurzeldreiecken und 84 Randdreiecken ergeben sich 231. Zusätzlich müssen unerwünschte Dreiecke ausgeschlossen und Grade/Margen vollständig erfüllt werden. Dann liegt der Graph in Ω∩λ. Diese Schnittmenge ist erheblich strenger als jeder Arm allein; Erzeugbarkeit nicht garantiert.

Bei G4 misst Bλ=Σ_{uv∈E}max(0,c_uv−1) nur Überschüsse. Kanten mit c_uv=0 werden nicht bestraft. Deshalb zusätzlich Zahl solcher Kanten und Σ|c_uv−1| protokollieren. Vier Startplätze aus zwei Budgetstufen, zunächst b=16 und b=64 als reine Versuchsparameter; zulässige Ergebnisse können sehr verschieden viele Fehlkanten haben. G4 soll keine Reparatursuche nach einer exakten Lösung voraussetzen.

Wichtige Grenze gegen Überverschärfung: Für jeden 14-regulären Graphen ist Σ_{u<v}c_uv=99·C(14,2)=9009. Auch 693·1+4158·2=9009. Würden wir im fertigen Graphen zugleich c_uv≤1 auf Kanten und c_uv≤2 auf Nichtkanten fordern, erzwingt die Summengleichheit überall Gleichheit: Das wäre bereits die exakte srg-Lösung. Nichtkantenfehler müssen bei der Gründererzeugung weich bleiben.

K66/C2/C3 dienen höchstens als lokale Strukturvorschläge. Keine ausgeschlossenen exakten Symmetriemodelle als erfüllt voraussetzen. Festgehaltene Zusatzbedingungen und anschließend freigegebene Bedingungen je Generator benennen. Keine neue Ausschlussrechnung.
F02-Matchings und Lift-Dreiteilung dürfen während der späteren Suche nicht als unbeabsichtigte Invarianten konserviert werden. Gezielte Operatorproben müssen dies prüfen; fehlt ein solcher Ausgang, Linie nur als markierte Kontrolllinie betreiben.

## 4. Selektion und Vielfalt
Sechs Inseln = zwei Arme × drei Ziele. In der kontrollierten Phase keine Migration; nach Auswahl einer Steuerung höchstens alle fünf abgeschlossenen Epochen zwei neue Vertreter pro Insel aus anderen Zielinseln desselben Arms, mit vollständiger Neubewertung nach dem Empfängerziel. Kein ungeprüfter Armwechsel.

Elternwahl: 80 % Dreierturnier nach aktivem Ziel, 20 % gleichmäßig über unterrepräsentierte Herkunftsgruppen und deren Mitglieder. Seedlisten vorab festlegen.
Überleben bei 64 Plätzen: acht geschützte beste verschiedene Zustände, 40 weitere nach Zielrang mit Familienobergrenze, 16 nach Neuheit und unterrepräsentierter Herkunft aus zulässigen Kindern/Archiv. Gruppen in den ersten fünf Epochen mit mindestens zwei Plätzen schützen, sofern passende verschiedene Zustände vorliegen; Eliterekorde in separatem unveränderlichem Bestarchiv bewahren. Danach Mindestvertretung anhand tatsächlicher Ausbeute lockern, Neuheitsanteil beibehalten. Bei kleinerer Population die Anteile proportional runden und Rest dem Qualitätsanteil geben.
Neuheit basiert zuerst auf exakter Endpunktisomorphie, dann auf Residuen-/Defektprofilen und Ω-Rahmenabstand; Profile sind kein Isomorphiebeweis. Abstammung und algorithmischer Endpunkt werden getrennt gezählt.

Bewusst schlechtere Ergebnisse dürfen nur in den 16 Explorationsplätzen verbleiben oder als temporärer Arbeitszustand dienen. Sie verdrängen nicht den Bestrekord. Neutral heißt beim Linf-Ziel Gleichheit des ganzen Tupels. W wird mitgemessen und archiviert, nicht zu einer vierten Insel.

## 5. Störungen, Verschlechterung und Zykluslängen
„Zyklus“ kann drei Dinge meinen: Träger eines Trades, Zahl akzeptierter Trades eines Ausflugs, oder Populationsepoche. Diese Größen werden getrennt protokolliert. Ein 6×6-Produkttrade ist keine Weglänge sechs. Alle regulären Trades erfüllen den Armvertrag; neue Reparaturen können intern unzulässig sein, aber nur gültige Endpunkte werden übernommen und solche Reparaturen nicht als durchgehend zulässiger Escape-Pfad ausgegeben.

Startverteilung der Kinderrezepte: 40 % kurze Ausflüge (2–4 akzeptierte Trades), 30 % mittlere (5–12), 20 % längere (13–32), 10 % frische Gründer oder validierte größere Reparatur. Ohne funktionierende Reparaturquelle werden diese zehn Prozent für Gründerreserve verwendet; leere Quelle nicht als Erfolgsversuch zählen. Längen 33–64 erst testen, wenn mindestens 80 % der längeren Versuche ihre Mindestlänge tatsächlich erreichen. Mehr Katalogbreite ist eine gesonderte Änderung.

Je Episode höchstens 45 CPU-Sekunden Störung und danach eigene 75 CPU-Sekunden Abstieg. Kein gemeinsames altes 256-Bewertungslimit, das den Abstieg vorab aufbraucht. Abstieg randomisierte erste Verbesserung mit bis zu 64 angenommenen Verbesserungsschritten; stichprobenbasierter Stillstand heißt STALLED_SAMPLED, nicht lokales Minimum. Vollständigen Census nur für ausgewählte Rekord-/Plateauzeugen.
Besuchsspeicher für die letzten 128 beschrifteten Arbeitszustände; zusätzlich Endpunktklassen gegen das Archiv. Im Abstieg bei Stillstand höchstens 32 neue neutrale Zustände innerhalb des verbleibenden Budgets erkunden. Das ist eine begrenzte Probe, keine vollständige Plateauaufnahme. Unvollendete lange Störung gesondert ausweisen; gültigen Teilfund speichern, aber nicht als vollständig ausgeführten Längenversuch zählen.

Für L1 und F: Verschlechterung relativ zum besten Wert am Beginn der Episode begrenzen, nicht relativ zum jeweils letzten schlechteren Zustand. Damit kein unbeabsichtigtes Hochschaukeln.
Kalibrierung aus positiven Einzeltrade-Änderungen nach Arm, Ziel und Herkunft: s=75-%-Quantil, wenn mindestens 32 Beobachtungen vorliegen, andernfalls gepoolter Arm/Ziel-Wert oder neue Kalibrierungsprobe. Stufen Δ=min(10 % des Ankerwerts, s), min(10 %,2s), min(10 %,4s). Obergrenze nach unten auf ganze Zielwerte runden. Wenn kein positives Budget entsteht, nur neutrale/senkende Züge oder neuer Gründer. Diese vorläufigen Stufen werden in der Screeningphase getestet und danach eingefroren; keine als optimal behaupteten Temperaturen.
Nicht jeder darunter liegende Zug ist gleich gut: zulässige Optionen zufällig mit Präferenz für kleinere Verschlechterung auswählen; tatsächlich benutzte Auswahlregel und Erzeugungsbias protokollieren. Keine unbeschränkte Minimax-Suche pro Individuum.

Linf erhält keine künstliche gewichtete Summe: normale Exploration hält Linf fest, lässt höchstens max(1,ceil(0,1·Nmax_Anker)) zusätzliche Maximalfehler und höchstens 5 % mehr L1 zu. Diese Explorationsgrenzen sind zusätzlich zur lexikographischen Populationsselektion definiert. In höchstens 10 % der Linf-Escape-Episoden darf Linf um eins steigen, für höchstens acht akzeptierte Trades; darunter liegende Komponenten werden dabei nicht als direkt mit ihren alten Nmax-Werten vergleichbare Fehlerzahlen interpretiert. Anschließend Abstieg/Abbruch, Bestarchiv unverändert. Nutzen dieses teuren Schritts separat prüfen.

Nach vier erfolglosen Bearbeitungen derselben Linie nächste Schwellenstufe; nach acht erfolglosen Bearbeitungen Linie für größere Mutation oder Austausch aus Gründerreserve vorschlagen. „Erfolg“ = strikt besserer aktiver Zielwert oder neue brauchbare Endpunktklasse, getrennt berichtet. Keine Garantie, dass diese Regeln HoG verlassen: die bekannten W-Barrieren lassen sich nicht auf F/L1/Linf übertragen.

Eine Epoche ist eine abgeschlossene Bearbeitung jedes aktiven Platzes, nicht eine feste Wandzeit. Bei 384 Episoden und 120 CPU-Sekunden maximal sind das 12,8 Worker-CPU-Stunden. 24 gleichmäßig ausgelastete Worker ergeben rechnerisch 32 Minuten ohne Overhead; SMT, Abbrüche, Validierung und Generatoren verhindern eine Laufzeitzusage. Durchsatz nur aus Messung berichten.

## 6. Crossover: abgetrennte Entscheidung
Nicht sofort 20 % der Kampagne reservieren. Gesonderter kleiner Vergleich von Reparatur-Crossover und Mutation mit denselben Eltern und demselben Gesamtbudget einschließlich Ausrichtung/Reparatur/Abstieg. Eigenständige Kinder, Rückkehr zu Eltern, bekannte andere Klassen und Verbesserung getrennt zählen. Erst nach Zusatznutzen bis zu 10 % der Kinderrezepte ersetzen; 20 % erst als weitere überprüfbare Variante. Ohne Erfolg bleibt Quote null. Keine Armvermischung.

## 7. Ryzen mit voller nutzbarer Kapazität
Bekannter Planungsstand Ryzen: 12 physische Kerne/24 logische Prozessoren, rund 47 GiB WSL-RAM. Vor Auslieferung tatsächliches CPU-Modell, CPU-Affinität, MemAvailable, freien Platz und laufende Jobs direkt prüfen; widersprüchliche ältere CPU-Namen nicht als Fakt übernehmen. Office bleibt unangetastet; keine dortige Last stoppen.

Kurzer Durchsatzvergleich 12/18/24 unabhängige Single-Thread-Worker auf demselben repräsentativen Aufgabenmix. Primär gültige abgeschlossene Episoden pro Wandzeit, sekundär CPU pro Ergebnis und RAM. 24 einsetzen, sofern Gesamtdurchsatz mindestens so gut wie mit weniger Workern ist; bei Gleichstand innerhalb Messstreuung Wiederholungsmessung statt Überinterpretation. Alle physischen Kerne nutzen, SMT nur soweit es Nutzen bringt. CPU-Auslastung allein ist kein wissenschaftlicher Ertrag. BLAS/Solver-Unterthreads begrenzen; kein 24×24-Overcommit.
Mit 24 Workern zunächst vier pro Insel, sonst zentrale Queue mit gleich hohen kumulierten Worker-CPU-Kontingenten für alle sechs Inseln. Freie Slots leihen, verbrauchte CPU verbuchen. Kosten von erfolglosen Reparaturen und Validierung der verursachenden Gruppe zurechnen; gemeinsame Infrastruktur gesondert ausweisen.

Planungsobergrenze aller Prozesse 36 GiB bei bestätigten rund 47 GiB RAM. Normale Aufgaben bis 1 GiB, höchstens zwei Reparaturjobs zugleich mit je 3 GiB; Controller/Caches mitrechnen. Bei MemAvailable unter 6 GiB keine neuen speicherintensiven Jobs starten. Ressourcenschutz rollt nur unvollständige Transaktionen zurück; bewahrt Checkpoints. Keine Millionen-Zustandsdatenbank je Individuum. Speichere Graphen, ausgewählte Pfadzeugen, Seeds, CPU-Zähler und kompakte Versuchszusammenfassungen.
Status alle zehn Minuten mit CPU je Insel, echten Zuglängen, Klassen-/Familienzahlen, Scorevektoren und Budget-ETA. Monotone Uhr für Sitzungsfristen; UTC nur zusätzlich protokollieren, da die früheren Uhrzähler voneinander abwichen. Wiederaufnahme mit verbleibendem Budget, keine stillschweigende Fristverlängerung.

## 8. Endlicher Ablauf und Entscheidung zur Skalierung
A. Technische Kalibrierung und Konstruktion: höchstens 16 CPU-Stunden für Durchsatz/gezielte Kontrollen, bis 32 CPU-Stunden Gründererzeugung. Testet nur geänderte Teile, keine Wiederholung aller bestandenen Tests. B ab 2080 dabei untersuchen; alte abgeschlossene Abstiege als Referenz verwenden.
B. Screening: zwei Varianten (einfache Störung+Abstieg gegen zusätzlichen neutralen Besuchsspeicher/Schwellensteuerung), drei unabhängige Seeds, sechs Arm/Ziel-Gruppen, je zwei CPU-Stunden =72 CPU-Stunden. In beiden Varianten derselbe Gründerbestand, dieselbe Populationsgröße und dieselbe Überlebensregel. Kleine Zahl bearbeiteter Epochen melden; drei Seeds sind keine definitive Signifikanzstudie.
C. Danach vorgeschlagen 48 Stunden Hauptkampagne mit ausgewählter Steuerung, Prüfung nach 24 Stunden. Bei 24 aktiven Single-Thread-Prozessen höchstens 1152 Worker-CPU-Stunden, keine 24-fache physische Rechenleistung versprochen. Bei unklarem Screeningbefund konservative Variante als Standard und adaptive Variante separat weiter vergleichen; nicht den besten Zufallsseed zum Beweis erklären.

Qualitäts- und Diversitätsänderung nicht kausal vermischen: ein besserer gemischter Start allein beweist noch keinen Diversitätsnutzen. Ein gezielter Familien-Ablationsvergleich bei gleicher Startqualität/Budget bleibt bei Bedarf ein Folgeexperiment. Als praktisches Suchziel dürfen wir dennoch die besseren geprüften Gründer verwenden.

Startbedingungen: vollständige Zulässigkeit der tatsächlichen Gründer, wirksame freie Operatoren oder klare Kennzeichnung eingeschränkter Linien, kein Score-/Checkpointfehler, ausreichender gemessener Episodendurchsatz. Keine vollständige A-/C08-/HoG-Kartierung erforderlich. Neue Kontrollen nur bei konkretem Risiko. Kein Großlauf wurde mit diesem Plan bereits gestartet.

## Quellen
Fixiert in memetik/958744f8b53ce66894a8b29e9bdfa033871574b0:
docs/memetik/OFFICE_PILOT_001_AUSWERTUNG_20260913.md; docs/memetik/pilot_0_3/{BEFUNDE,PILOT_0_3}.md; configs/memetic_v2/office-0.2.0.json; data/memetik/ai_candidates/submissions/20260915_{codex,claude}_v01/REVIEW.md; docs/memetik/review_grossversuch_20260919/; results/memetik/{escape_followup_20260916,landscape_20260917,minimax_20260919}/.
Zusätzlich Kontextauszüge Kandidatenkonstruktion 18.09.2026; kein vollständiger Chatabruf, keine nachträgliche Literaturprüfung/Neuheitsbehauptung.

