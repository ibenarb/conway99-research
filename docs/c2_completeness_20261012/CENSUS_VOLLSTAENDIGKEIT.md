# Vollständigkeit des Profile346-Census in seiner definierten Domäne

Stand 12.10.2026. **Neu ausgeführter endlicher Rechennachweis mit mathematischem
Zählargument; kein allgemeiner C2-Ausschluss.**

## 1. Aussage und Eingabe

Sei $\mathcal D$ die Menge aller gerichteten schleifenfreien Graphen auf
$\{0,\ldots,6\}$ mit folgenden Eigenschaften:

1. Jeder Ausgrad gehört zu $\{3,4,6\}$.
2. Mindestens ein Ausgrad ist 3.
3. Der ungerichtete gegenseitige Graph mit Kanten $ij$ genau dann, wenn beide
   Pfeile $i\to j$ und $j\to i$ vorkommen, enthält keinen Vierzyklus.

Ein Vierzyklus ist hier nicht notwendig induziert. $S_7$ wirkt durch Umbenennung.

**Satz CEN.** Die Datei `representatives.tsv` mit 279.171.105 Bytes und SHA-256
`d003dd431ce506b0bbf936441b970cf80d99027e7d35219b26763312bffbb538`
enthält genau einen Vertreter jeder $S_7$-Bahn in $\mathcal D$.
Es gilt

$$|\mathcal D|=37\,030\,041\,152,\qquad |\mathcal D/S_7|=7\,388\,648.$$

Der Nachweis verbindet die folgenden drei tatsächlich ausgeführten Prüfungen.
Die Programme sind neue Implementierungen, keine Wiederverwendung des historischen
Kanonisierers oder seiner Aufzählungsshards. Sie wurden vom selben Bearbeiter
ausgeführt; ein externer Reviewer hat diesen Stand noch nicht geprüft.

## 2. Zulässigkeit der vorliegenden Vertreter

Der Strukturprüfer `validate_records.cpp` liest alle 42-Bit-Codes, rekonstruiert
ihre gerichteten Graphen und bestätigt die drei Bedingungen von $\mathcal D$.
Außerdem prüft er die gespeicherten Gradfolgen, gegenseitigen Kantenzahlen und Strata.
Der ausgeführte Upload-Audit bindet diese Prüfung an den obigen Dateihash.
Damit liegt jede gespeicherte Bahn vollständig in $\mathcal D$, da die Bedingungen
unter Umbenennung invariant sind.

Belege: [census_upload_audit.json](../../results/c2_completeness_20261012/census_upload_audit.json),
[census_validation_output.txt](../../results/c2_completeness_20261012/census_validation_output.txt).

## 3. Isomorphieklassen und Automorphismenordnungen

Der neue Prüfer `audit_isomorphism.cpp` verwendet für jeden Knoten die Farbe
$(d^+(v),d^-(v))$. Jede Graphisomorphie erhält diese Farbe. Er ordnet die Farbklassen
lexikographisch und durchläuft alle Permutationen innerhalb dieser Klassen.
Für jede solche Knotenordnung kodiert er die vollständige $7\times7$-Adjazenzmatrix
als 49-Bit-Zahl; ihr Minimum ist der Vergleichscode.

**Korrektheit des Vergleichs.** Isomorphe Graphen besitzen dieselben Farbklassen
und dieselbe Menge farbgeordnet beschrifteter Adjazenzmatrizen. Ihr Minimum ist
daher gleich. Umgekehrt beschreibt ein gleicher Vergleichscode eine konkrete
Umbenennung zwischen den beiden Graphen. Der Vergleichscode ist somit ein
vollständiges Isomorphieinvariant.

**Korrektheit der Automorphismenzahl.** Fixiert man eine Ordnung, die das Minimum
erreicht, so entsprechen die anderen Ordnungen mit derselben Matrix bijektiv
den Automorphismen des Graphen. Jeder Automorphismus erhält die Farben und wird
deshalb im durchlaufenen Permutationsraum erfasst. Die Anzahl der Treffer des
Minimums ist genau $|\operatorname{Aut}(D)|$.

Der Prüfer bestätigt für alle Datensätze die Übereinstimmung mit der gespeicherten
Automorphismenordnung. Anschließend sortiert er alle Vergleichscodes; es gibt
keinen gleichen Nachbarn und damit keine isomorphen Dubletten. Nach dem
Bahn-Stabilisator-Satz ist die Größe der Vereinigung der gespeicherten Bahnen

$$S=\sum_{D\text{ in der Datei}}\frac{7!}{|\operatorname{Aut}(D)|}
=37\,030\,041\,152.$$

Tatsächlich geprüft wurden 58.737.762 Knotenordnungen, höchstens 5.040 pro Datensatz.
Die Eingabedatei wurde vor und nach dem Lauf gehasht. Fünf Kontrollgraphen mit
bekannten Automorphismenordnungen sowie negative Kontrollen für eine falsche
Ordnung und für zwei verschiedene, aber isomorphe Codes wurden ebenfalls geprüft.

Beleg: [isomorphism_audit.json](../../results/c2_completeness_20261012/isomorphism_audit.json)
und zugehöriges [Laufprotokoll](../../results/c2_completeness_20261012/isomorphism_audit.log).

## 4. Unabhängige vollständige Zählung der beschrifteten Domäne

Das zweite neue Programm `count_labelled.cpp` verwendet keine Kanonisierung und
liest keine Vertreterdatei. Es zählt zunächst für jede nichtsteigende Gradfolge
$d_0\ge\cdots\ge d_6$ mit Einträgen in $\{6,4,3\}$ und mindestens einer 3 alle
Graphen mit genau dieser fest zugeordneten Ausgradfolge. Es gibt 28 solche Folgen.

Für Zeile $v$ der gerichteten Adjazenzmatrix durchläuft das Programm jede
7-Bit-Maske mit genau $d_v$ Einsen und einer Null an Position $v$. Somit wird
jede mögliche Matrix einmal erzeugt, sofern sie nicht durch die folgende sichere
Präfixprüfung verworfen wird.

Nach Wahl der Zeilen $0,\ldots,v-1$ ist der gegenseitige Graph auf diesen Knoten
bereits vollständig bestimmt. Bei Wahl von Zeile $v$ entsteht seine Menge alter
gegenseitiger Nachbarn

$$S_v=\{u<v:(u\to v)\text{ und }(v\to u)\}.$$

Wenn der alte Graph keinen Vierzyklus enthält, entsteht genau dann ein neuer
Vierzyklus, wenn zwei verschiedene Knoten $u,w\in S_v$ einen gemeinsamen alten
gegenseitigen Nachbarn $z$ haben. Der Zyklus lautet $v,u,z,w,v$.
Alle vier Knoten sind verschieden: $v$ ist neu, $u\ne w$, und Schleifenfreiheit
schließt $z=u$ und $z=w$ aus. Umgekehrt besitzt jeder neue Vierzyklus durch $v$
diese Form. Genau diesen Test implementiert die Präfixprüfung.

Ein bereits entstandener Vierzyklus kann durch spätere Zeilen nicht entfernt
werden. Deshalb verwirft die Prüfung ausschließlich unzulässige Zweige. Bei der
letzten Zeile ist die gesamte gegenseitige Adjazenz bestimmt. Die Zahl
$N(d_0,\ldots,d_6)$ der akzeptierten Blätter ist somit die vollständige Zahl für
die fest zugeordnete Gradfolge.

Seien $m_3,m_4,m_6$ ihre Gradmultiplizitäten. Es gibt
$7!/(m_3!m_4!m_6!)$ verschiedene Zuordnungen dieser Grade zu den sieben beschrifteten
Knoten. Die jeweiligen Graphmengen sind disjunkt und durch Umbenennung gleich groß.
Daher ist die Gesamtzahl

$$T=\sum_d N(d)\frac{7!}{m_3!m_4!m_6!}=37\,030\,041\,152.$$

Alle 28 Einzelzahlen stehen im Bericht; zehn sind null. Ein separater Python-Code
prüfte die Rekursion zuvor für vier Knoten gegen alle $2^{12}=4.096$ gerichteten
Graphen, mit einer direkten Prüfung der drei möglichen Vierzyklen. Die Zahlen
stimmen für jede der 35 Gradfolgen; insgesamt sind 4.050 Graphen zulässig.

Die historischen erwarteten Zahlen werden vorab eingelesen und ausschließlich
**nach** der Aufzählung zum Vergleich verwendet; sie bestimmen weder die
Zweigauswahl noch den C4-Test. Alle 28 Gradprofilzahlen stimmen zusätzlich mit ihnen
überein. Entscheidend für den Vollständigkeitsbeweis ist der Vergleich $S=T$.

Beleg: [labelled_census_audit.json](../../results/c2_completeness_20261012/labelled_census_audit.json)
und zugehöriges [Laufprotokoll](../../results/c2_completeness_20261012/labelled_census_audit.log).

## 5. Schluss des Vollständigkeitsarguments

Nach Abschnitt 2 ist die Vereinigung der gespeicherten Bahnen eine Teilmenge von
$\mathcal D$. Nach Abschnitt 3 sind diese Bahnen paarweise disjunkt und haben
zusammen $S$ Elemente. Nach Abschnitt 4 hat die gesamte Menge $\mathcal D$ genau
$T$ Elemente. Wegen $S=T$ fehlt kein Element und damit keine Bahn. Zusammen mit
der Isomorphiedublettenfreiheit folgt Satz CEN.

Dieser Nachweis benötigt keine erneute historische Kanonisierung und keine
Vertrauensannahme, dass jeder ursprüngliche Enumerationsteil tatsächlich gelaufen
sei. Er benötigt die Korrektheit der hier dokumentierten neuen Prüfprogramme,
ihrer Ausführung und der Bindung an die gehashte Eingabe. Eine formal in einem
Beweisassistenten verifizierte Implementierung wird nicht behauptet.

## 6. Reproduzierbarkeit und Aussagegrenzen

Quellprogramme und Python-Runner liegen unter
[src/c2_completeness_20261012](../../src/c2_completeness_20261012).
Die Runner kompilieren die C++-Dateien mit `g++`; Version, Optionen, Quellhashes,
Runnerhashes und Ergebniszeiten stehen in den jeweiligen JSON-Berichten.
Python muss mit aktiven Assertions ausgeführt werden, also ohne `-O` oder
`PYTHONOPTIMIZE`. Benötigte Argumente sind über `--help` dokumentiert.

Die Isomorphieprüfung benötigt die gehashte Vertreterdatei. Die beschriftete Zählung
benötigt zum anschließenden Abgleich die mitgelieferte `expected_census.json` und
den neu erzeugten Isomorphiebericht. Die Rohzählung selbst benötigt beide nicht.
Ein öffentlich überprüfter Downloadlink für die große Vertreterdatei fehlt noch;
ihre vorhandenen Bezugsstellen stehen im
[Artefaktmanifest](../../results/c2_completeness_20261012/artifact_manifest.json).

**Nicht bewiesen durch Satz CEN:** die Zulässigkeit des C4-Filters für SRG-Lösungen,
der frühere Profile46-Ausschluss, Encoderadäquanz, sämtliche historischen
Coverage-Komplemente, die UNSAT-Zertifikate oder der Ausschluss der Ankergrade
0, 1 und 2. Diese Pflichten bleiben im [Beweisregister](BEWEISREGISTER.md) getrennt.
Es wurde für diesen Nachweis kein SAT-Solver und kein UNSAT-Beweischecker gestartet.
