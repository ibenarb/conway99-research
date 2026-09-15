# Qwen v01: Befunde, Analyse und Schlussfolgerung

Eingang 2026-09-15; Selbstbezeichnung Qwen3.7, selbst angegebenes Berichtsdatum 2026-09-16. Diese Angaben werden getrennt festgehalten, nicht extern verifiziert. Original samt CRLF-Zeilenenden unverändert in `original.txt`. Quellcodeblöcke und JSON sind mit LF-Zeilenenden separat extrahiert.

## Entscheidung

**Drei Datensätze eingereicht, null aufgenommen (`REJECTED_AS_SUBMITTED`).** Alle drei geben die jeweils erforderliche Arm-Bedingung selbst als `false` an. Zusätzlich sind die graph6-Kodierung und der Prüfer fehlerhaft. Die 14 bereits aufgenommenen KI-Kandidaten bleiben unverändert.

Positiv: Alle drei SHA256-Werte stimmen exakt mit den übermittelten Zeichenfolgen plus LF überein. Drei Generatoren und ein Prüfer sind vollständig als Codeblöcke vorhanden. Dies belegt Übertragungskonsistenz, keine mathematische Zulässigkeit.

## Tatsächlich ausgeführte Prüfungen

Die unabhängige Prüfung in `audit.py` benutzt nur die Python-Standardbibliothek. Sie prüft Header, Länge, SHA256, innere Konsistenz der gemeldeten Histogramme, zählt gemeinsame Nachbarn unabhängig über Mengen und ruft Qwens unveränderten Prüfer auf allen drei Einträgen auf. Kleine ausführbare Gegenbeispiele prüfen zusätzlich die defekte Initialisierung und Matrixmultiplikation. Alle Ergebnisse stehen in `audit.json` und `audit.log`.

Die Generatoren wurden nicht als unbeschränkte Suchläufe gestartet. Fehlende echte Zufallsseeds verhindern ohnehin eine zugesicherte Wiedererzeugung der eingereichten Graphen. Für die Ablehnung reichen die vorhandenen Daten und deterministischen Gegenbeispiele.

## Datenformat und diagnostische Rekonstruktion

Alle Strings beginnen mit `~??@b` und haben 814 Zeichen ohne LF. Standard-graph6 erwartet bei n=99 `~?@b` und insgesamt 813 Zeichen. Der Standard interpretiert die ersten vier gelieferten Zeichen als Ordnung 1, worauf unzulässige Nutzdaten folgen. Außerdem verwendet Qwen eine zeilenweise statt der standardmäßigen spaltenweisen Dreiecksreihenfolge. Der Encoder verschiebt den bereits linksbündig aufgebauten letzten Bitblock nochmals; das Padding ist ebenfalls fehlerhaft.

Um die beabsichtigten Graphen zu untersuchen, wurde zusätzlich Qwens eigener Decoder verwendet. **Diese diagnostische Interpretation ist keine Reparatur oder Aufnahme als graph6.** Auf den dadurch rekonstruierten Adjazenzmatrizen wurden sämtliche folgenden Zahlen unabhängig mit Nachbarmengen berechnet:

| ID | Kanten | Grade | W | L1 | F | Linf | Nmax | λ-fehlerhafte Kanten |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C01 | 952 | 14–29 | 3960 | 10230 | 35838 | 11 | 1 | 837 |
| C02 | 693 | alle 14 | 2772 | 4950 | 9306 | 2 | 2178 | 495 |
| C03 | 45 | 0–4 | 4848 | 9617 | 19155 | 2 | 4769 | 42 |

C03 hat 40 isolierte Knoten. Die Behauptung „nur 44 von 693 Kanten fehlerhaft“ wird durch die Daten nicht gestützt: Es gibt in dieser Interpretation lediglich 45 Kanten, von denen 42 λ verletzen. Der Wert Linf=2 ist bei einem sehr dünnen Graphen kein Qualitätsnachweis; selbst der leere Graph auf 99 Knoten hat Linf=2, aber verletzt sämtliche Nichtkantenbedingungen.

C02 wurde außerdem unabhängig unmittelbar aus der angegebenen Differenzenmenge {1,2,4,10,20,40,47} aufgebaut. Die dabei erhaltenen Kennzahlen stimmen mit der diagnostischen Rekonstruktion überein. Er ist 14-regulär, aber mit 495 λ-Verletzungen kein λ-Kandidat. Der zyklische 14-reguläre λ-Suchraum auf Z99 ist bereits ausgeschlossen; siehe den unmittelbar vorhergehenden Grok-Prüfbericht für den kurzen Spiegelungsbeweis.

## Der mitgelieferte Prüfer bestätigt die behauptete Selbstprüfung nicht

Tatsächliche Rückgaben von `verify_candidate` auf dem unveränderten JSON:

- C01: `FAIL: Regularität verletzt bei Knoten 15 (Grad: 24)`.
- C02: `PASS` — eine falsche Zulässigkeitsbestätigung.
- C03: `FAIL: Regularität verletzt bei Knoten 0 (Grad: 2)`.

Damit sind bereits die Angaben „drei selbst erfolgreich geprüft“ mit dem gelieferten Prüfer und den gelieferten Daten nicht reproduzierbar. Es wird nicht behauptet, dass keine andere Ausführung stattgefunden hat; dafür liegen keine Protokolle vor.

Der falsche PASS für C02 hat mehrere Ursachen:

1. Die Berechnung von A² summiert für Zwischenknoten k nur über j≥k und überschreibt symmetrische Einträge während der Berechnung. Das ist keine Matrixmultiplikation. Unser Drei-Knoten-Gegenbeispiel zeigt auch falsche Außerdiagonaleinträge.
2. Im λ-Arm verlangt der Prüfer λ=1 nicht zwingend. Er kontrolliert die Bedingung nur, wenn das eingereichte Flag bereits `true` ist. Mit `false` kann eine unzulässige Instanz passieren.
3. Im Ω-Arm prüft er lediglich die Länge der angegebenen Rahmenpermutation, weder deren Bijektivität noch den Rahmen oder PH=2J−(C+I)P.
4. Nmax zählt nur das positive maximale Residuum. Negative Residuen mit gleichem Betrag fehlen. Beim gemeldeten Histogramm von C03 müsste Nmax=4783 sein, nicht 0.
5. Die Histogrammprüfung kontrolliert nur die Größe des selbst berechneten Histogramms; sie vergleicht es nicht mit dem eingereichten Histogramm.

Unabhängige Plausibilitätsgrenzen hätten weitere Fehler sofort erkannt: Ein 14-regulärer Graph auf 99 Knoten hat genau 693 Kanten, also höchstens 693 λ-fehlerhafte Kanten. C01 meldet 833. Für einen einfachen 14-regulären Graphen gilt −2≤r_uv≤12; C01 meldet Linf=21. Außerdem gilt über ungeordnete Paare sum(r_uv)=99·14·13/2+693−2·4851=0. Die gemeldeten Histogramme von C01 und C03 haben stattdessen Residuen-Summen 8599 beziehungsweise −9621.

## Konstruktions- und Implementierungsfehler

**F01:** Ein zufälliges 12-reguläres H genügt nicht für Ω; PH muss exakt stimmen. Zusätzlich löscht das Programm bereits eingefügte H-Kanten nach einem fehlgeschlagenen Stub-Versuch nicht. Weitere Versuche häufen Kanten an, weshalb die Regularität verloren geht. Selbst nach hundert Fehlversuchen wird ein Ergebnis ohne Erfolgsprüfung ausgegeben. Ein nichtnull Ω-Residuum ist keine zulässige Baseline unseres Ω-Arms.

**F02:** Die Bewertung berücksichtigt nur die sieben positiven Generatoren S, obwohl der ungerichtete Cayley-Graph die Verbindungsmenge S∪(−S) benutzt. Der berechnete Suchwert misst daher nicht die behauptete λ-Bedingung. Der mathematische Ausschluss des zyklischen λ-Suchraums kommt unabhängig davon hinzu.

**F03:** Die vermeintliche Validitätsprüfung bildet ein Tupel, wertet dabei alle Seiteneffekte aus und nimmt anschließend dessen letztes Element `True`. Weder u!=v noch das Verbot vorhandener Kanten wirken als Schranken. Ein ausgeführtes Minimalbeispiel akzeptiert eine Selbstschleife als gültig. Mehrfachbelegungen kollabieren in der 0/1-Matrix; Schleifen werden vom Encoder weggelassen. Die anschließenden Swaps können die fehlerhafte Ausgangsregularität nicht herstellen. Der Annahmetest vergleicht zudem mit dem historischen Bestwert statt mit dem aktuellen Zustand; ein temperaturabhängiger Annealingplan fehlt.

**Reproduzierbarkeit:** Alle Generatoren benutzen `random`, ohne `random.seed(...)` zu setzen. Die angegebenen Seed-Bezeichnungen werden nicht eingelesen. Ebenso werden die in den Datensätzen angegebenen Kommandozeilenargumente nicht verarbeitet. Selbst eine Formatkorrektur ergäbe daher noch keine reproduzierbare Einreichung.

## Schlussfolgerung

Diese Antwort enthält tatsächlich Kandidatendaten, aber keinen zulässigen Gründer und keinen neuen geprüften Konstruktionsbeitrag. Am schwersten wiegt der Prüfaufbau: Generator und Prüfer teilen Formatannahmen, die Matrixmultiplikation ist falsch, und harte Bedingungen können durch falsche Eingabeflags umgangen werden. Passende Prüfsummen schützen vor Übertragungsfehlern, nicht vor diesen gemeinsamen Fehlern.

Ein kleiner maximaler Fehler oder eine kleine absolute Anzahl fehlerhafter Kanten ist erst nach Prüfung von Einfachheit, Ordnung und Regularität aussagekräftig. Unser bisheriger Ablauf — harte Bedingungen vor Bewertung und Isomorphie — verhindert genau diese Fehlaufnahme.

Keine längeren Läufe und keine Isomorphieanalyse der abgelehnten Daten nötig. Falls Qwen erneut beauftragt wird, sollte es zuerst einen einzigen harten zulässigen Graphen mit Standard-graph6 und unabhängig geprüftem Ergebnis liefern. Die Sammlung bleibt bei 14 akzeptierten Graphen; das Fluchtwegsexperiment kann mit diesem Bestand vorbereitet werden.
