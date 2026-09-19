# Symmetrien: Reviewabgleich und Fortsetzungsplan

19. September 2026. Forschungsbasis b3d2f8dc4eb51be9c1db4fc2a35cb827a2b2501b.
Das externe Original wird unverändert im eigenen Reviewzweig archiviert.
Dieser Text ersetzt dessen Aussagen nicht, sondern bewertet sie getrennt.
Keine Produktionssolverläufe wurden für diesen Abgleich gestartet.

## Entscheidung

C2 bleibt das nächste Ausschlussziel. Die Restsymmetrie erhält höhere Priorität
als in unserem bisherigen Plan. Das war eine echte Auslassung unserer Planung.
Wir übernehmen jedoch weder die behaupteten Beschleunigungsfaktoren noch die
vorgeschlagene Primärfixierungsquote als Erfolgskriterium. Der nächste Versuch
vergleicht Symmetriebrechung und kurze Folgeklauseln getrennt und kombiniert.
Eine weitere unveränderte Langkampagne ist nicht vorgesehen.

Unter Übernahme der unten bezeichneten publizierten Resultate bleiben als volle
Automorphismengruppen 1, C2 und C3; C3 wirkt fixpunktfrei. Ein vollständiger
C2-Ausschluss ließe somit 1 oder C3. Anschließend ist C3 auszuschließen.
K66 ist ein eigener begrenzter Ordnung-3-Fall und kein Ersatz für diese gesamte
Kette; seine Archiv-/Zertifikatslage ist gesondert zu führen. Memetik ist hier
nicht Gegenstand.

## 1. Übereinstimmungen und eigene Nachrechnungen

Der Review bestätigt Rahmen, E1–E3, Matchingabdeckung und die vorsichtige
Interpretation der erfolglosen Laufbudgets. Das stärkt die Nachvollziehbarkeit,
ändert aber keinen offenen Fall in einen Ausschluss.

Mit `check_review.py` wurden hier neu berechnet:

- alle elf Stabilisatorordnungen von 12 bis 46080;
- ihre Bahnen auf den 1722 Primärbits: sämtliche elf Tabellenwerte stimmen;
- genau 28980 verschiedene nichttriviale Dreierklauseln, jeweils Länge 3.

Der Prüfer enumeriert die 46080 Rahmenumbenennungen, filtert diejenigen, die
L erhalten, erzeugt die Gruppe explizit und berechnet die induzierten Bitbahnen.
Die Rahmen-/Kantenabbildung wird aus unserem vorhandenen Encoder importiert:
Das ist eine neue Berechnung, aber kein vollständig unabhängiger Zweitencoder.
`checks.json` enthält die Ergebnisse. Ein erster Start scheiterte an fehlendem
SymPy; der fertige Prüfer verwendet stattdessen eine explizite Gruppenschließung
und benötigt keine solche Zusatzbibliothek.

Die vom Reviewer angegebenen UP-Stichproben (112/196, 35/35 usw.),
Primärfixierungszahlen und seine unabhängigen Reproduktionsprogramme wurden
nicht mitgeliefert. Diese Angaben bleiben externe Messberichte; die UP-Versuche
müssen vor Übernahme als eigene Benchmarkbasis reproduziert werden, insbesondere
auf dem tatsächlich eingesetzten Totalizer statt nur auf der Referenz-BDD-CNF.
Die F-Bedingung ist nach der E3-Partnerzeile und gcd-Normierung dieselbe
Gleichung, nicht bloß eine zusätzliche spektrale Konsequenz. Kein erneuter
F-Zusatzversuch.

## 2. Wesentliche Korrekturen am Review

| Reviewaussage | Bewertung und Konsequenz |
|---|---|
| Große Stabilisatoren liefern globale, exponentielle Reduktion bis 46080-fach | Gruppenwirkung ist vorhanden; Laufzeitgewinn folgt daraus nicht. Bitbahnen sind keine Belegungsbahnen. 11 Bitbahnen bedeuten keinesfalls 11 freie Bits. Bits derselben Bahn dürfen NICHT gleichgesetzt werden. |
| Stabilisator erhält 66 Einheitsklauseln elementweise | Er erhält deren Menge, kann einzelne Klauseln permutieren. Das genügt für semantische Symmetrie, nicht automatisch für eine syntaktische Permutation sämtlicher Hilfsvariablen. |
| Lex-Bedingungen für Erzeuger | Zulässige partielle Brechung bei einheitlicher Bitordnung: das globale lexikographische Minimum jeder Lösungsbahn erfüllt alle Vergleiche. Erzeugervergleiche garantieren weder genau einen Vertreter noch volle Brechung. Zufallsprüfungen ersetzen diesen Beweis nicht. |
| Fixierte Primärbits/1722 als einzige auswertbare Fortschrittsgröße | Nützliche Propagationsdiagnostik, keine Beweisnähe. UNSAT kann ohne vorherige Root-Fixierungen erscheinen; Symmetriebrechung kann Fixierungen nur durch Repräsentantenwahl erzeugen. Unter Annahmen fixierte Bits sind nicht globale Folgerungen. |
| Primärfixierungen alle 60 s abfragen kostet nichts | CaDiCaL hat eine API, aber der bestehende CLI-Prozess stellt keine solche Fernabfrage bereit. Instrumentierung benötigt einen sicheren Listener/Wrapper; Inprocessing und externe Variablenabbildung sind zu beachten. Keine beliebige gleichzeitige API-Abfrage während solve(). |
| Ein großer Stabilisator sollte monoton größere Fixierungsgewinne erzeugen | Keine solche Monotonie ist bewiesen. Die 25%-Schwelle und Konflikt-Faktor-2-Regel des vorgeschlagenen Piloten sind keine zuverlässigen Auswahlkriterien. |
| D-Spektrum ist umgekehrt äquivalent zur festen Matrixgleichung | Spektrum allein bestimmt den Nullraum nicht. Erst zusammen mit DV=0, VᵀV=12I und den Dimensionen identifiziert man den Nullraumprojektor VVᵀ/12. |
| Gleiche 1722 Primärbits schließen Encodergewinn aus | Falsch als allgemeines Argument. Äquivalente Darstellungen können verschieden propagieren. Ein neuer Q/D-Encoder ist aber ohne konkreten Wirkmechanismus vorerst nachrangig. |
| Cubing ist der einzige Zertifizierungspfad, jetzige Zertifizierung unmöglich | Nicht belegt. Speicherprojektion beruht auf angenommenen Bytes/Konflikt, nicht gemessener LRAT-Rate. Cubing ist eine sinnvolle Option; direkte, komprimierte oder gestreamte Prüfung sind ebenfalls grundsätzlich möglich. |
| Geprüfte Blattbeweise sofort löschen | Abgelehnt für die endgültige Belegkette. Nach unabhängiger Prüfung verlustfrei archivieren, Hash und Eingabezuordnung erhalten. Ein Prüflog ersetzt keinen erneut prüfbaren Beweis. |
| 11-vs-22-Worker-Test, je 20 min, kostet 1.5 CPU-h | Nominal 11 CPU-h, nämlich (11+22)·20/60. SMT-Zuwachs und Speicherbandbreitenlimit wurden nicht gemessen. |
| Ein zertifizierter Einzelfall sei kein publizierbares Teilergebnis | Ein exakt abgegrenzter Teilausschluss darf dokumentiert werden. Er ist lediglich kein vollständiger C2-Satz. |

Auch 100000 zufällige vollständige Primärbelegungen können einen Zweitencoder
nur schwach prüfen: fast alle verletzen bereits triviale Bedingungen.
Strukturierte gültige Kleinmodelle, gezielte negative Beispiele, partielle
Belegungen und ein generischer Encoderbeweis sind wichtiger. Eine CNF-Erweiterung
ist nicht allein deshalb polynomial prüfbar, weil sie Hilfsvariablen enthält;
das muss aus der jeweiligen Gatter-/Zählerstruktur begründet werden.

Eine Vorabreservierung im dünn belegten WSL-VHDX garantiert keinen entsprechenden
Windows-Speicher. Ressourcenplanung muss den realen Host messen, pro Job die
Ausgabe hart begrenzen und einen globalen Puffer vorhalten.

## 3. Nachgeholte Literaturprüfung

### C3: die ältere Projektbilanz bleibt bestehen

[Crnković–Maksimović 2020, §7, Sätze 7.1–7.3](https://cdm.ucalgary.ca/article/download/62323/54015/204856)
nennt ausdrücklich Fixpunktfreiheit für Ordnung 3, keine Untergruppe der Ordnung
6 oder 9 und nur Primteiler 2,3. Zusammen mit
[Cesarz–Woldar 2025, Korollar 3.13](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf)
folgt die obige Liste 1,C2,C3: im geraden Fall teilt die Ordnung 6, im ungeraden
Fall bleibt höchstens 3. Die publizierten Rechenausschlüsse wurden hier gelesen,
nicht unabhängig neu ausgeführt.

[Ishida, arXiv:2606.29183, PDF v2 vom 8. Juli 2026, §8.4](https://arxiv.org/pdf/2606.29183)
war eine tatsächliche Literaturlücke. Die Passage bestätigt a₁(t)=14 und nennt
bei C3 noch leere oder dreieckige Fixmenge. Das ist eine schwächere notwendige
Alternative, keine Behauptung der Realisierbarkeit beider Fälle und keine
Widerlegung von Satz 7.3. Kein Anlass, den C3-Dreiecksfall neu zu öffnen.
Der neue Spur-Rang-Satz wurde nicht vollständig auditiert und wird hier nicht
als zusätzliche unverzichtbare Voraussetzung verwendet. HTML v1 und PDF v2
haben unterschiedlichen Umfang; deshalb die Versionsangabe.

### Thakkar und Fixpunktsatz

[Thakkar, §§5–7 und Reproduzierbarkeitsangaben](https://arxiv.org/pdf/2608.11211)
ordnet den 48h-Lauf ausdrücklich C7 zu. Die Behauptung des Reviewers, dies sei
unabhängige C2-Langlaufevidenz, ist falsch. Ein C2-Ausschluss folgt aus dieser
Arbeit nicht. Ebenso ist ihre Einordnung von C7 als offen nicht mit der oben
zitierten Ausschlussliteratur abgeglichen.

[Makhnev–Minakova 2004](https://doi.org/10.1515/156939204872374): erneuter
Volltextabruf über den DOI scheiterte technisch. Der Originalbeweis bleibt
unauditiert. Wir unterscheiden „verwendeter veröffentlichter Satz“ von „intern
nachvollzogener Beweis“. Nicht jeden zitierten Satz neu zu beweisen macht einen
mathematischen Folgesatz nicht automatisch zu einer bloßen Vermutung. Für unser
Audit bleibt die Abhängigkeit ausdrücklich markiert; Beschaffung ist sinnvoll,
aber blockiert nicht jeden methodischen Pilot.

### Signed graphs: konkreter Ansatz statt bloßes Stichwort

[Anđelić–Koledin–Stanić 2020, Sätze 1–2](https://poincare.matf.bg.ac.rs/~zstanic/Papers/dmgt2.pdf)
behandelt reguläre vorzeichenbehaftete Graphen mit drei Eigenwerten und zeigt
Walk-Regularität. Die Klassifikationen betreffen zusätzliche Voraussetzungen
(z.B. Grad 3 oder höchstens zehn Knoten), also keinen direkten Ausschluss unseres
42-Knoten-Falles mit Grad 10.

Eigene Folgerung für unser D: Aus DV=0 und D²+D=12I−VVᵀ folgt
D³+D²−12D=0. Damit (D³)ᵢᵢ=−10 und (D⁴)ᵢᵢ=130.
An jedem Knoten ist die Differenz positiver und negativer signierter Dreiecke
also −5, global −70. Diese Bedingungen sind bereits Konsequenzen des exakten
Modells, könnten aber lokale Musterprüfungen verbessern. Kein neuer
Ausschlusssatz und kein Neuheitsanspruch. Beliebiges Switching von D ist bei
festgehaltenem V nicht automatisch zulässig.

## 4. Fortsetzungsplan mit Entscheidungspunkten

Zeitangaben sind Arbeits-/Pilotbudgets, keine Zusage einer Beweiszeit.

| Phase | Arbeit und Ergebnis | Budget und Fortsetzungskriterium |
|---|---|---|
| 0: Belegkette | Review archivieren, Literaturdifferenzen klären, kleine Zahlen nachrechnen | In diesem Abgleich erledigt; Original-Fixpunktbeweis und UP-Stichproben bleiben offen |
| 1: zulässige Brechung | Je Fall Erzeuger und Primärpermutationen exportieren; E1–E3 und Fallannahmen unter ihnen prüfen; partielle Lex-Ketten plus generischer Orbitminimum-Beweis | Etwa 0.5–1 Arbeitstag; keine Produktionssuche ohne bestandene Abdeckungskontrolle |
| 2: vier Varianten | Totalizer unverändert / +Lex / +Dreierklauseln / +beides; getrennte Hashes, Größe, UP-Basiswerte und gleiche vorab festgelegte Teilbelegungen | Etwa 0.5 Arbeitstag; Reviewer-UP zuerst auf beiden Encodern prüfen; keine flächendeckenden Viererklauseln |
| 3: kurzer Pilot | Typen 1+1+1+1+1+1, 2+2+2 und 6; vier Varianten, zwei Seeds, je 20 min | 24 Jobs, 8 nominelle CPU-h, mit elf Slots rund 1 h plus Auswertung; Reihenfolge gemischt, gleiche Parallelbelastung |
| 4: Teilproblem-Pilot | Falls Wurzeln sämtlich offen: identischer, vorab eingefrorener Satz primärer Cubes; beidseitiger Lookahead, vollständiges Splitprotokoll | Zunächst 1–2 h Suchbudget; bei nur trivialen Seitenblättern Splitwahl ändern, nicht automatisch vertiefen |
| 5: Zertifizierung | Ersten geeigneten Teilausschluss mit passender CNF und unabhängigem Prüfer nachfahren, Ressourcenverbrauch messen und Beweis archivieren | Eigener begrenzter Proof-Pilot; konkrete Dateigrenzen anhand gemessener Bytes/Schritt, genügend Hostreserve |
| 6: längere Kampagne | Beste belastbare Variante auf alle elf Fälle; Prüfkette und Coverage fortschreiben | Zunächst 4–8 h; längere Freigabe erst nach tatsächlicher Wirkung und Ressourcenprüfung |
| 7: Gesamtziel | Nach C2: fixpunktfreies C3-Modell; Literaturvoraussetzungen und vollständige Abdeckung separat prüfen | Keine Terminzusage; keine Gleichsetzung K66=C3 |

Messung: Root-Fixierungen auf Primärbits sind Zusatzdiagnostik. Wenn die sichere
CaDiCaL-Listenerintegration mehr als einen halben Arbeitstag beansprucht, zunächst
externe UP-Diagnostik verwenden; den Pilot nicht für eine vermeintliche
„Fortschrittsanzeige“ blockieren. Bisherige Einzelprozess-Logs liefern diese
Primärprojektion nicht.

Auswahlkriterien: echte Entscheidungen und Zeit/CPU bis zur Entscheidung auf
gleichen Aufgaben; für zensierte Läufe keine fiktiven Laufzeitverhältnisse.
Bei vollständigem Timeout ist das Ergebnis unentschieden, auch wenn mehr Bits
fixiert wurden. Auf festen Cubes Abschlussrate, CPU-Kosten, offene Frontier und
dominante Asttiefe gemeinsam messen; weder Bitquote noch Blattzahl ist ein
Prozentsatz des Beweisfortschritts. Zwei Seeds sind Screening, keine robuste
statistische Absicherung. Ein Vorteil muss auf zurückgehaltenen Aufgaben bzw.
einem weiteren Seed bestehen bleiben; sonst keine lange Eskalation.

Plan B bleibt verfügbar: zweite gekoppelte Nachbarschaft unter dem verbleibenden
Stabilisator. Symmetriebrechung und Fallzerlegung sind nicht austauschbar;
letztere kann unabhängig teilbare Aufgaben erzeugen. Auswahl nach tatsächlicher
Propagation/Teilproblemhärte, nicht allein nach Stabilisatorverlust.

Plan D wird als begrenzte Algebraarbeit geführt: lokale signierte Dreiecks- und
Walk-Muster katalogisieren und prüfen, ob sie eine neue kurze Obstruktion liefern.
Ohne solche Wirkung vorerst kein vollständiger neuer Encoder. Portfolio mit
anderem Solver/Seed bleibt eine spätere kontrollierte Option, kein kostenloser
Zusatz: Speicher und reale CPU-Zeit zählen.

## 5. Offene Beleganforderungen

Für einen endgültigen Satz: mathematische Reduktion, Encoderargument,
Symmetrieabdeckung einschließlich Lex-Brechung, vollständige Fall-/Cube-Abdeckung,
zugeordnete CNFs und archivierte unabhängig geprüfte UNSAT-Zertifikate.
Ein Proof nur für die symmetriegebrochene Formel genügt erst zusammen mit dem
separaten Vertretererhaltungsargument. Die jetzt angelegte Prüfdatei ist keine
Solverimplementierung; auf dem Ryzen wurde nichts gestartet oder verändert.
