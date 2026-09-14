# Mistral v04: Ω-Backtracking

14. September 2026. Vollständige empfangene Markdown-Datei einschließlich Code byteidentisch in original.md. Code unverändert extrahiert in generator_received.py. Nur der mögliche Kopier-Escape bits[i\\:i+6] wurde in generator_normalized.py normalisiert. Wörtlicher Empfangscode hat einen SyntaxError, dessen Herkunft nicht Mistral zugeschrieben wird.

**Ergebnis: Kein Kandidat. Die Implementierung führt keine funktionsfähige Backtracking-Suche aus.**

## Tatsächliche Ausführung

Python 3.12 / NumPy im vorhandenen Runtime. Assertions aktiv. Maximal 15 Sekunden Prozessbudget je Test; beide Prozesse beendeten vorher.

| Parameter | Ergebnis |
| --- | --- |
| seed=42, max_steps=20 | NO_CANDIDATE_FOUND, Exitcode 1 |
| seed=42, max_steps=1000000 (empfohlener Standard) | RecursionError, Exitcode 1, keine reguläre NO_CANDIDATE_FOUND-Ausgabe |

Ein separater begrenzter instrumentierter Aufruf zählt 21 Prüfungen, alle ausschließlich für die Zelle (0,1). Die Beobachtung verändert keine Entscheidung: Wrapper protokolliert nur die Argumente der unveränderten Prüffunktion.

## 1. Endgleichungen sind keine korrekte Teilbelegungsprüfung

Alle Zielwerte von PH liegen bei 1 oder 2. Nach Setzen einer einzelnen Kante können die geprüften Zeilen nicht in allen 84 Spalten bereits diese positiven Werte besitzen. check_omega_conditions verlangt aber vollständige Gleichheit für jede dieser Spalten. Damit wird jede erste Kante abgelehnt.

Richtig wäre eine Prüfung auf noch mögliche Ergänzbarkeit, etwa für jede Gleichung:
bereits gesetzte Summe ≤ Ziel ≤ bereits gesetzte Summe + noch mögliche Beiträge.
Gradgrenzen entsprechend berücksichtigen. Solche Schranken sind notwendige lokale Bedingungen, nicht automatisch ein vollständiger Ergänzbarkeitsnachweis. Vollständige Gleichheit erst bei abgeschlossener Belegung verlangen.

## 2. Null und unentschieden sind nicht getrennt

Die Auswahl sucht immer die erste Null in H. Der Nullzweig speichert keine Entscheidung und rückt keinen Variablenindex weiter. Nach Ablehnung der ersten Kante wird daher wieder dieselbe Null gewählt. Das Budget zählt Wiederholungen statt untersuchter Zustände.

Auch das Abschlusskriterium ist falsch: Die Schleife erreicht ihren Abschluss nur, wenn keine Null mehr oberhalb der Diagonalen vorhanden ist. Ein 12-regulärer Graph auf 84 Knoten enthält aber 504 Kanten und 2982 Nichtkanten unter den 3486 möglichen Paaren. Legitime festgelegte Nullen bleiben also stets vorhanden.

Erforderlich wären explizite Zustände unentschieden/0/1 oder ein fortschreitender Entscheidungsindex; dazu Rücknahme und ein Zähler tatsächlich besuchter Suchknoten. Eine Erhöhung des Rekursionslimits behebt die logische Schleife nicht.

## 3. Angekündigte Optimierungen sind nicht implementiert

Keine MRV-Auswahl, keine Restkapazitätsprüfung, keine zufällige Auswahl trotz Seed-Parameter. max_steps ist eine Tiefengrenze, kein globales Suchbudget. Der Wert 1000000 überschreitet im beobachteten Lauf das Python-Rekursionslimit, bevor das eigene Limit erreicht wird.

## 4. graph6 teilweise korrigiert

Für n=99 stimmen Header ~?@b und Länge 813. Die tatsächlichen Schleifen behalten jedoch die zeilenweise Reihenfolge bei. Der Kommentar nennt eine andere, korrekte Reihenfolge.

Roundtrip-Test bei n=99 mit einziger Kante {0,3}: Standarddekodierung der erzeugten Zeichenfolge ergibt {1,2}. Damit wird die gelieferte Matrix nicht labelgetreu kodiert; das ist insbesondere für den Ω-Rahmen unzulässig. Der Test allein behauptet keine Nichtisomorphie dieser beiden Ein-Kanten-Graphen.

Richtige Reihenfolge: äußere Schleife j=1,…,n−1, innere Schleife i=0,…,j−1. Allgemeine n>62-Header außerhalb n=99 bleiben ebenfalls falsch. Die graph6-Funktion wird vom erfolglosen Generator nicht erreicht, wurde separat geprüft.

## 5. Faire Gesamtbewertung

Positiv: Frühere mathematische Gegenargumente werden akzeptiert, die ausgeschlossene zirkuläre λ-Familie aufgegeben, die Ω-Gleichungen korrekt als Constraints angesetzt und die fehlende Ausführung offengelegt. Die Summe der H-Grade ist 1008; die tabellarische Zahl 504 bezeichnet die Kantenanzahl, nicht die Gradsumme.

Die Behauptung eines mathematisch tragfähigen Suchalgorithmus trifft auf den gelieferten Code nicht zu. Mehr Rechenzeit hilft hier nicht. Ein zurückgegebenes NO_CANDIDATE_FOUND ist weder ein brauchbarer Suchbefund noch ein Unmöglichkeitsbeweis, wenn keine unterschiedlichen Belegungen untersucht werden.

Im Projekt sind bereits gültige Ω-Gründer bekannt. Es geht um zusätzliche Vielfalt, nicht darum, die bloße Erfüllbarkeit dieser Teilbedingungen erstmals festzustellen.

Nach diesem ausdrücklich letzten Korrekturversuch empfehlen wir keine weitere breite Überarbeitungsschleife mit Mistral. Der Constraint-Ansatz kann projektintern sauber implementiert werden, ist aber als solcher noch kein neuer Kandidat oder eigenständiger mathematischer Fortschritt.

## Reproduktion

python3 audit.py (NumPy erforderlich). Eigene Prüfung getrennt vom empfangenen Code. audit.json enthält Prozessausgaben, Zellbesuchsnachweis und Encoder-Roundtrip. Archiveintrag REJECTED_AS_SUBMITTED; null Kandidaten aufgenommen.
