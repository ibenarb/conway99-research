# Claude v01: Kandidatenprüfung und mathematische Einordnung

15. September 2026. Originalpaket CONWAY99_ClaudeOpus5.zip byteidentisch archiviert; SHA256 130c19eb128bea798dc1e8189461eb29e032b498ff3b6f26f511a56e2cb7f01c. Zehn flache ZIP-Mitglieder, CRC-Prüfung bestanden. Modellbezeichnung ist Selbstangabe, nicht extern verifiziert.

**Ergebnis: Drei gültige, paarweise nichtisomorphe Kandidaten aufgenommen: zwei Ω, einer λ.**

## 1. Unabhängige Abnahme

audit_independent.py dekodiert graph6 direkt und verwendet Mengenrechnung, weder Claudes Prüffunktionen noch dessen Encoder.
Geprüft: Header/Länge/Padding/LF, 99 Knoten mit Grad 14, vollständiger Ω-Rahmen für A/B, H-Grad 12 und alle 1176 PH-Gleichungen; für C alle 693 Kanten mit genau einem gemeinsamen Nachbarn. Alle Scores über 4851 Paare unabhängig nachgerechnet. JSON-Zwischenstände stimmen mit den Graphen überein; C enthält 231 paarweise kantenfremde Tripel mit Replikation 7.

| Kandidat | Arm | W | L1 | F | Linf | λ-verletzende Kanten |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Claude-A | Ω | 2338 | 3192 | 5180 | 4 | 406 |
| Claude-B | Ω | 2333 | 3070 | 4798 | 5 | 350 |
| Claude-C | λ | 2729 | 3596 | 5476 | 4 | 0 |

Alle gelieferten Werte und Nichtkantenhistogramme stimmen. Ihre Unterschiede beweisen paarweise Nichtisomorphie der drei Graphen. Die vorgegebene Z14-Translation erhält A und erhält B nicht. Keine vollständigen Automorphismengruppen berechnet.

H(A) und H(B) unterscheiden sich in 786 Kantenpositionen; bei jeweils 504 Kanten bleiben 111 gemeinsame Kanten. Diese Distanz ist für die gelieferte Nummerierung, nicht als minimaler Abstand über Isomorphismen ausgewiesen.

## 2. Reproduktion und Grenzen

Die Stufen final und cayley wurden mit dem unveränderten Generator in einem separaten Verzeichnis erneut ausgeführt. Alle drei graph6-Dateien, bewertung.json und cayley.json stimmen byteidentisch mit dem Paket überein.

Die längeren Suchstufen A, B und C wurden nicht erneut gestartet. Claudes Angaben zu 9055 Suchschritten, Seeds, Laufzeiten, 100 Reparaturrunden und 15 akzeptierten Schritten bleiben Anbieterangaben. Die tatsächlichen Ergebnisgraphen sind unabhängig bestätigt; das ist von einer vollständigen historischen Laufreproduktion getrennt.

Die lokale Behauptung, Zerstörungen an höchstens fünf Knoten würden identisch/eindeutig repariert, ist im Paket nicht durch Versuchstabellen, Seeds oder Suchprotokolle belegt. Der gelieferte Standardlauf verwendet k=12,16,20. Wir übernehmen daraus keinen Starrheits- oder Minimalitätsnachweis.

## 3. Bedeutung für den memetischen Piloten

A liefert eine funktionierende algebraische Konstruktion, allerdings innerhalb der bereits im Projekt vertretenen Z14-Symmetriefamilie. Eine weitere Z14-Lösung ist nicht allein deshalb ein neues Konstruktionsprinzip.

B ist ein Nachfahre von A, kein unabhängiger Gründer. Die große tatsächliche Veränderung, die gebrochene vorgegebene Translation und die besseren W/L1/F-Werte sind dennoch relevant. Linf wird von 4 auf 5 schlechter; der Lauf optimiert F, nicht alle Kriterien gleichzeitig.

Die Formulierung „destroy and repair im exakt zulässigen Bereich“ muss präzisiert werden: Beim Löschen und Reparieren werden Grad-/Margenbedingungen verletzt. Nur E=0-Endzustände werden übernommen. Die Suche nutzt damit auch unzulässige Zwischenzustände. Das ist zulässig als Kandidatenerzeugung, liefert aber keine Fluchtweglänge unter unseren durchgehend Ω-erhaltenden Mutationen.

C realisiert die kombinatorische Dreieckspackung tatsächlich. Im Code werden sowohl bereits vorhandene Paarverbindungen als auch gemeinsame Nachbarn ausgeschlossen; die erläuterte Bedingung muss zusammen mit dieser Paarfreiheit gelesen werden. So bleibt jedes vorhandene Dreieck eindeutig, und bei 231 Tripeln und maximal Grad 14 ist der Zielgrad erreicht.

Keiner dieser Kandidaten verbessert die bisherigen jeweiligen globalen Pilotbestwerte. Alle drei werden dennoch als gültige Strukturangebote aufgenommen. Isomorphie gegen das gesamte Projektarchiv und empirische Einzugsgebietstests bleiben offen. Nichtisomorphie untereinander genügt nicht für neue Plateaus.

Die im Bericht angedeutete Gefahr gesetzter Symmetrie ist von der Operationswahl abhängig: Ein Startgraph mit Symmetrie kann durch spätere Mutationen Symmetrie verlieren. Eine nur symmetrisch beschränkte Fortsetzung wäre eine andere Fragestellung. Literaturbehauptungen zu Automorphismenausschlüssen wurden in diesem Audit nicht neu geprüft.

## 4. Cayley-Ausschluss unabhängig bestätigt

Alle Gruppen der Ordnung 99 sind abelsch:
n11 teilt 9 und ist 1 modulo 11, also n11=1. n3 teilt 11 und ist 1 modulo 3, also n3=1. Beide Sylowgruppen sind normal; die Gruppe ist ihr direktes Produkt. Gruppen der Ordnung 9 sind abelsch. Es verbleiben Z99 und Z3×Z3×Z11.

Claudes Enumeration ist reproduziert: 1440 bzw. 1442 zulässige Basisblockbahnen, kein Treffer. Die Fixierung einer Ordnung-3-Untergruppe im zweiten Fall ist ohne Einschränkung möglich, weil GL(2,3) transitiv auf den vier solchen Untergruppen operiert; diese Begründung sollte zum Bericht ergänzt werden.

Zusätzlich verwenden wir eine unabhängige, kleinere Enumeration aus dem zuvor hergeleiteten Involutionsargument:
Für jede inverse-abgeschlossene Verbindungsmenge S und d∈S permutiert x↦d−x die gemeinsamen Nachbarn von 0 und d. Bei λ=1 ist der einzige Nachbar d/2, also S/2=S. Jede zulässige S ist deshalb eine Vereinigung vollständiger Verdopplungsbahnen.

- Z99: Bahngrößen 30,30,10,10,10,6,2; keine Vereinigung hat Größe 14.
- Z3×Z3×Z11: vier Bahnen der Größe 2 und neun der Größe 10. Größe 14 verlangt eine 10er-Bahn plus zwei 2er-Bahnen: 9·C(4,2)=54 Möglichkeiten.
- audit_cayley_independent.py prüft alle 54 Mengen direkt auf |S∩(d+S)|=1 für sämtliche d∈S. Keine besteht.

Damit ist die Aussage **kein Cayley-Graph über irgendeiner Gruppe der Ordnung 99 im λ-Suchraum** unabhängig abgesichert. Sie schließt nicht alle knotentransitiven Graphen und nicht alle algebraischen/Liftkonstruktionen aus. Keine Literatur-Neuheit behauptet.

## 5. Grenzen der Software

stage_final berechnet Prüfflags, bricht bei falschen Flags jedoch nicht generell ab. Für eine produktive Aufnahme deshalb unseren unabhängigen Validator verbindlich verwenden.
Die behauptete Unabhängigkeit von PYTHONHASHSEED ist nicht gleichbedeutend mit garantierter identischer Ausgabe über Python-Versionen; Integer-Set-Iteration wird weiterhin verwendet.
Die kurzzeitige Toleranz von +2 in F ist eine bewusste Zulassung schlechterer akzeptierter Ω-Endzustände, keine strikt monotone Optimierung.

## Schlussfolgerung

Das Paket liefert real verwertbare Graphen, eine funktionierende λ-Konstruktion und einen unabhängig bestätigten Cayley-Ausschluss. Für den neuen Piloten besonders nützlich: Dreieckspackung als Herkunft und destroy-and-repair als gesondert zu untersuchender Operator. Der behauptete Schwellenwert für lokale Flucht ist hingegen noch nicht belegt.

Alle Originaldateien werden bewahrt. Eigene Abnahme, Cayley-Prüfung und Bericht liegen getrennt daneben. Ein anfänglicher Startversuch unsererseits referenzierte ein noch nicht angelegtes Reproduktionsverzeichnis und wurde vor Codeausführung abgewiesen; nach Anlegen erfolgte die erfolgreiche Reproduktion.
