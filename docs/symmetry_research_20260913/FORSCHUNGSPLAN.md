# Conway99: Forschungsplan für neue Symmetrieausschlüsse

Stand: 13. September 2026. Plan, kein neuer Ausschlussbeweis.
Ausgangsstand: Forschungscommit `56031005459c9eb6d352402704b7d4fa389058b0`.
Review und Abgleich: Reviewcommit `fbba251f1acbe49177a44ae47f77f66ab1b1de25`, Verzeichnis `docs/reviews/20260913_extern/`.

## Ziel und Neuheitsmaßstab

Ralph Beckmann legt ab jetzt den Schwerpunkt auf einen echten neuen mathematischen Beitrag mit dem Fernziel, nichttriviale Automorphismen eines SRG(99,14,1,2) auszuschließen. Bekannte Ergebnisse werden als ausdrücklich zitierte Voraussetzungen verwendet. Interne Nachimplementierung wird auf die für neue Beweise notwendige Vertrauensbasis begrenzt. Die vorhandene K66-Arbeit bleibt dokumentiertes Fundament; die übrigen, literaturseitig bereits ausgeschlossenen Fixdreieckfälle erhalten keine neue Produktionskampagne.

Ein vollständiges Involutionsmodell ist ein notwendiges Forschungswerkzeug, aber für sich kein nachgewiesener neuer mathematischer Beitrag. Auch ein neuer Encoder und schnellere Laufzeiten beweisen keine neue Einschränkung. Als Ziel zählen eine bisher nicht erfasste, exakt ausgeschlossene strukturelle Familie, eine nachweislich schärfere notwendige Bedingung oder der vollständige C2-Ausschluss. Neuheit muss jeweils an einer präzisen Aussage und ihren Voraussetzungen geprüft werden. Ein beliebiger ausgeschlossener SAT-Zweig ist noch kein substantieller mathematischer Beitrag.

## Literaturabgleich und Reichweite

Die Kombination der in Crnković–Maksimović, Abschnitt 7, referierten bzw. bewiesenen Einschränkungen mit Cesarz–Woldar, Korollar 3.13, lässt für die volle Automorphismengruppe nur 1, C2 und C3 zu. Der C3-Fall ist fixpunktfrei. Für den Involutionsfall wird der bekannte Satz über den eindeutigen Fixpunkt verwendet. Ein neuer C2-Ausschluss ließe somit nur 1 und C3 übrig; erst der zusätzliche C3-Ausschluss ergäbe Asymmetrie. Das wäre weiterhin kein Nichtexistenzbeweis des Graphen.

Primärquellen:

- [Crnković–Maksimović, insbesondere Sätze 7.1–7.3](https://cdm.ucalgary.ca/article/download/62323/54015/204856).
- [Cesarz–Woldar (2025), Einleitung und Korollar 3.13](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf).
- [Behbahani, Dissertation: Ausgangspunkt zum älteren rechnerischen Automorphismenausschluss](https://spectrum.library.concordia.ca/976720/1/NR63369.pdf).
- [Lou–Murin, strukturelle Vorarbeiten](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf).
- [Keramatipour (2026), SAT-Modellierungen und berichtete experimentelle Grenzen](https://arxiv.org/abs/2604.23037).

Ein zusätzlicher Überschneidungsbefund ist [Thakkar, arXiv:2608.11211v1, §§4–5](https://arxiv.org/html/2608.11211v1): Die 84-Knoten-Reduktion einschließlich gemischter Bedingungen und Modellierung vorgegebener Automorphismen werden dort beschrieben. Dies nimmt der Grundmodellierung den Neuheitsanspruch. Die dortige Darstellung des C7-Falls als offen widerspricht allerdings Satz 7.1 der oben genannten Literatur und wird nicht übernommen. Fremde Implementierungen und Laufzeitberichte sind hier nicht unabhängig reproduziert. Eine konkrete vollständige C2-Produktion bei 99 Knoten wird durch die gelesenen Passagen nicht belegt.

Vor strukturellen Neuheitsansprüchen außerdem die einschlägigen Originalnotizen im [externen Forschungsrepository YesterdaysLemon/conway-99-research](https://github.com/YesterdaysLemon/conway-99-research) abgleichen. Dessen Selbstbewertungen sind keine unabhängigen Beweisbestätigungen. Die heutige Suche ist begrenzt und belegt keine weltweite Priorität.

## Arbeitsprogramm

### A. Den tatsächlich offenen Zielraum festhalten

Aufwand: 1–2 konzentrierte Arbeitstage, überwiegend Quellen- und Spezifikationsarbeit.

Ergebnis: Tabelle mit jeder verwendeten Voraussetzung, Originalquelle, genauer Reichweite und bekannter Überlappung. Für jede neue Kandidatenaussage wird festgehalten, welche bisher zulässigen Objekte sie zusätzlich ausschließen würde. Vorhandenen nutzbaren Code auf Lizenz, Vollständigkeit und Anschlussfähigkeit prüfen; nur fehlende Teile implementieren. Kein umfassender Nachbau aller historischen Berechnungen.

Abschlusskriterium: präzise C2-Zielaussage und dokumentierter Unterschied zwischen bekanntem Modell, eigener Implementierung und gesuchter neuer Mathematik.

### B. Vollständiges C2-Referenzmodell mit Zertifikaten

Aufwand: etwa 3–5 weitere Arbeitstage; Kontrollrechnungen gewöhnlich Minuten bis Stunden. Schätzung für Entwicklung, keine gemessene Fertigstellungszeit.

Vom eindeutigen Fixpunkt aus sind seine 14 Nachbarn als sieben Kanten und die 84 Außenknoten als nichtgematchte Nachbarpaare festgelegt. R ist die 84×14-Inzidenzmatrix dieser Paare, K die 14×14-Matchingmatrix. Unbekannt ist die symmetrische binäre Außenmatrix M mit Nulldiagonale. Neben Involutionsinvarianz müssen gemeinsam gelten:

\[
M\mathbf1=12\mathbf1,\qquad
M^2+M=12I_{84}+2J_{84}-RR^T,\qquad
MR=2J_{84\times14}-R(K+I_{14}).
\]

Die letzte, gemischte Gleichung darf nicht stillschweigend entfallen. Mit den festen Blöcken müssen diese Bedingungen als äquivalent zur vollständigen SRG-Matrixgleichung nachgewiesen werden. Die im Reviewabgleich hergeleiteten 42 verbotenen Außenpartnerkanten und die daraus verbleibenden 1722 primären Kantenorbitvariablen sind Modellierungsdaten, keine Laufzeitprognose und kein Neuheitsnachweis.

Benötigt werden ein kleiner direkter Graphprüfer, eine dokumentierte Encoderkorrektheit, erschöpfende kleine Kontrollen und ein positiver Test am 9-Knoten-Rookgraphen mit passender Involution. Dieser Test muss dessen eigene Parameter verwenden. Jede WLOG-Reduktion erhält einen Vollständigkeitsbeweis. Die Ordnung 645120 der Rahmenumbenennungsgruppe ist kein pauschaler Suchraumgewinn; die vorgeschriebene Involution wirkt bereits trivial auf invariant belegten Variablen.

Abschlusskriterium: aus jeder SAT-Lösung lässt sich ein unmittelbar prüfbarer Graph gewinnen; aus einer vollständigen UNSAT-Kampagne lässt sich einschließlich Fallabdeckung ein prüfbarer C2-Ausschluss gewinnen. Kleine Tests allein ersetzen den allgemeinen Korrektheitsnachweis nicht.

### C. Zwei Wege innerhalb des C2-Falls vergleichen

1. **Direkte zertifizierte Suche.** Referenzmodell mit wenigen nachweislich korrekten zusätzlichen Konsequenzen. Vollständig protokollierte Fallzerlegung, SAT-Beweisausgaben und unabhängige Prüfung mit der vorhandenen verlässlichen Prüfkette. Ziel ist zunächst ein vollständig abgeschlossener, strukturell benannter Teilbereich, anschließend gegebenenfalls die Gesamtzerlegung.
2. **Strukturelle Verschärfung.** Die 42 Außenpaare liefern einen invarianten und einen antiinvarianten Matrixteil. Untersuchen, ob die gemeinsame ganzzahlige Realisierbarkeit, Paritätskopplung, Rang- oder Spektralbedingungen neue lokale Konfigurationen verbietet. Ein zulässiger Quotient genügt nicht: seine Kopplung an den zweiten Teil muss erhalten bleiben. Exakte Obstruktionen in kurze Lemmas oder prüfbare rationale bzw. ganzzahlige Zertifikate übersetzen.

Der zweite Weg ist eine Forschungsfrage, keine bereits bewiesene Verschärfung. Auch seine Standardwerkzeuge begründen allein keine Neuheit. Ein aus einem SAT-Widerspruch gewonnenes Muster muss für die gesamte benannte Familie gelten und gegenüber bekannten Folgen einen echten Zusatz liefern.

Pilotbudget: 24–48 Stunden Ryzen-Wandzeit nach Fertigstellung des Modells. Kleine und schwierigere Teilfälle vorher festlegen; höchstens wenige Encoder-/Zusatzbedingungenvarianten auf denselben Fällen vergleichen. Erfassen: geprüfte abgeschlossene Fälle, CPU-Zeit, Spitzen-RAM, Beweisgröße, Prüfzeit und offene Restfälle. Timeouts bleiben offen. Die Auswahl einiger leichter Fälle belegt keinen allgemeinen Durchsatz.

Entscheidung: Bei messbarem Fortschritt eine erste Kampagne mit 2–7 Tagen Wandzeit. Ohne abgeschlossene relevante Teilbereiche oder wirksame neue Obstruktion zunächst die Strukturarbeit verstärken. Nicht allein wegen bereits investierter Rechenzeit größere Budgets vergeben.

### D. C3 als vorbereitete zweite Route

Der projektseitig begründete fixpunktfreie Fall mit tau=6 bleibt das zweite notwendige Ausschlussziel. Die vorhandenen 26 zulässigen binären Gram-Typen und 101 noch offenen L-Typen sind Startkoordinaten. Ihr Produkt ist keine nachgewiesene Liste von 2626 tatsächlich möglichen Fällen.

Gesucht wird eine stärkere gemeinsame Realisierbarkeitsbedingung zwischen dem 6×6-Block X, seiner Inzidenz C und dem 27-Knoten-Restblock. Priorität erhalten exakte Integritäts-, gemeinsame-Nachbarn- und Zyklusbedingungen, die in der bisherigen Gram- oder schwachen LP-Prüfung fehlen. Dieselbe LP erneut auszuführen liefert keinen neuen Ansatz. Falls Quotienten überleben, folgt die vollständige Prüfung ihrer Hebbarkeit zum Graphen.

Erstes Ziel: einen ganzen bisher offenen L-Typ oder eine nicht schon ausgeschlossene strukturelle Familie zertifiziert beseitigen, alternativ eine nachweislich neue notwendige Bedingung. Der vollständige C3-Ausschluss bleibt ein größeres, unbefristetes Ziel.

Aktivierung: wenn der C2-Pilot strukturell stagniert oder C3 einen klareren überprüfbaren Ausschluss verspricht. Entwicklung grob 3–7 Arbeitstage plus eigener Pilot von 24–72 Stunden; diese Budgets werden nicht gleichzeitig mit voller C2-Produktion auf derselben Maschine verplant.

## Ryzen-Betrieb und realistische Zeitplanung

Ausgangspunkt ist der bekannte Ryzen 9 3900X mit 12 physischen Kernen und etwa 48 GiB verfügbarem RAM. Zunächst bis zu 10–11 einzelne Solverprozesse bei ausreichendem Speicher; tatsächlichen Durchsatz messen. 24 Threads werden nicht als 24 unabhängige Kerne budgetiert. Speicherintensive Zertifikatsprüfungen nötigenfalls separat laufen lassen. Vor Produktion RAM und freien Plattenplatz tatsächlich erheben; Archivierung und Prüfung gehören zum Rechenbudget.

Elf ausgelastete Kerne liefern idealisiert 264 Kernstunden pro Tag bzw. 1848 pro Woche. Das ist Kapazität, keine Prognose über die Lösbarkeit einer SAT-Instanz. Unterschiedliche Zweigschwierigkeit, Beweisspeicherung und Prüfung verringern den nutzbaren Durchsatz.

Für die erste Entscheidung über den Ansatz sind ungefähr 1–2 Wochen aus Entwicklung, Quellenabgleich und Pilot realistisch als Planungsrahmen. Ein erster neuer Teilbeitrag ist ein Ziel für die anschließenden Wochen, kein zugesagtes Ergebnis. Für den vollständigen C2- oder C3-Ausschluss gibt es derzeit keine belastbare Laufzeitschätzung; auch Monate zusätzlicher Berechnung garantieren ihn nicht.

## Evidenz und Erfolgskriterien

Jede Produktionskampagne fixiert Quellencommit, Modellversion, Parameter, Generator, CNF-Hashes, vollständige Fallabdeckung und Prüfwerkzeuge. SAT heißt erst nach direkter Graphprüfung Erfolg. UNSAT heißt erst nach korrekter Kodierung, gültigem Beweis und vollständiger beanspruchter Abdeckung Ausschluss. Solvermeldungen, Timeouts und numerische Vermutungen bleiben getrennt.

Ein neuer Satz nennt seine Literaturvoraussetzungen offen; deren vollständige interne Reproduktion wird nicht als Voraussetzung für jede neue Forschung verlangt. Reviewer erhalten den genauen Satz, Beweistext und reproduzierbare Artefakte. Reviews bleiben unverändert auf eigenen Zweigen, die eigenen Antworten separat.

Nächster konkreter Arbeitsschritt: den Abgleich A auf das C2-Modell und seine vorgeschlagenen Verstärkungen begrenzen und daraus die Spezifikation B ableiten. Dieser Commit startet noch keine neue Solverkampagne.
