## Vorschlag nach dem λ-Profil

### Einordnung

Das Profil erfüllt die vorab festgelegte Regel für den **negativen Ausgang**:

- keine einzige (W,L1)-Verbesserung in 5685 Episoden,
- keine Zwischenverbesserung,
- die Rückkehr lässt sich durch längere Perturbation fast vollständig verhindern, ohne dass dadurch bessere Endpunkte entstehen.

Das **Plateaukriterium** (mindestens fünf verschiedene Endminima mit W ≤ W(Start)+2) ist nicht erfüllt. Es gibt genau eine solche Klasse, und die gibt es nur ab W2076. Nach der Vorabregel folgt daraus: **Pause der λ-P-Linie mit unverändertem Operator und unveränderter Akzeptanz.** Dem stimme ich zu, ebenso der Folgerung im ERGEBNIS, dass Radius 5, verlängerte lange Zellen oder ein großer P-Lauf nicht begründet sind.

Die vier unvollständigen Zellen ändern daran nichts. Sie liegen gerade dort, wo die Rückkehr bereits fast verschwunden ist (5,7 % bzw. 8,7 % bei k=32). Die fehlenden 315 Episoden würden die Rückkehrquote kaum verschieben. Zur Verbesserungsrate sagen sie ebenfalls wenig.

**Eigene Gegenprüfung des neuen Minimums [N]:** Der Endpunkt W2077/L1=2488 (state `e1edc9cb…`) ist in meiner unabhängigen Schichtenzählung um W2076 genau der eine Zustand in exakter Tiefe 2 mit W2077. Außer ihm gibt es in Radius 2 nur noch einen Zustand mit W ≤ 2078, nämlich (2078, 2488) in Tiefe 1. Der Weg über (2079, 2492) passt ebenfalls zu meiner Tiefe-1-Liste. Der Befund ist damit aus zwei unabhängigen Rechnungen gestützt. Zusätzlich zeigen die 17 Beobachtungen bei k=12 bis 32: Auch nach langen Perturbationen fällt ein Teil der Abstiege in genau diese Delle zurück **[H]**.

### Was ich vorschlage

**1. Eine rechenfreie Abschlussauswertung der vorhandenen Endpunkte, mit vorab festgelegter Entscheidungsregel.**

Im Ergebnis fehlt die Qualitätsverteilung der nicht zurückgekehrten Endpunkte. Bei k=32 sind es 183 bzw. 180 verschiedene Klassen, aber wie hoch deren W liegt, steht nirgends. Genau davon hängt die letzte offene Methodenfrage ab. Die Daten liegen im Abschlussarchiv vor; es muss nichts neu gesucht werden. Je Zelle würde ich auswerten:

- Min, Median und Quartile von W der nicht zurückgekehrten Endpunkte,
- Anzahl der Episoden und der Klassen mit W ≤ W(Start)+5 bzw. +10,
- beschrifteter Kantenabstand jedes Endpunkts zum Start.

Vorab festgelegte Regel:

| BefundFolge                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bei mindestens einer Länge k ≥ 8 liegen ≥ 10 % der nicht zurückgekehrten Endpunkte bei W ≤ W(Start)+5, und darunter sind ≥ 10 verschiedene Klassen | Es gibt einen Trichter aus vielen nahen Minima mit kleinen Barrieren; die W2076↔W2077/2488-Barriere ist ≤ 3. Die einzige dann noch begründete Operatorhypothese ist eine **Kette über lokale Minima mit Akzeptanz leicht schlechterer Minima** (z. B. Schwelle ΔW ≤ 3). Sie wäre als eigener, separat freizugebender Pilot zu planen: gleiche Starts, festes Budget ≤ 10 CPU-h. |
| Sonst                                                                                                                                              | Die nahen Minima sind vereinzelt. Lange Perturbationen wirken dann praktisch wie Neustarts, und deren Ertrag kennen wir aus der O-Kampagne. **Endgültige Pause** der λ-P-Linie.                                                                                                                                                                                                 |

**2. Den Strukturvergleich der drei Minima aus dem ERGEBNIS nur als beschreibenden Anhang.**

Er ist billig und für die Dokumentation sinnvoll. Mit drei Graphen erzeugt er aber fast zwangsläufig nachträglich formulierte Hypothesen. Deshalb sollte er nicht das Tor zu einem neuen Suchplan sein. Die Endpunktverteilung aus Punkt 1 stützt sich auf 5685 Episoden und auf eine Regel, die vor der Auswertung feststeht.

**3. Strategisch.**

Die gesamte λ-Kampagne hat W von 2081 auf 2076 gesenkt. Der Abstand zu W=0 bleibt riesig, und ein kleineres W ist kein Beleg dafür, dass man sich einem srg(99,14,1,2) nähert. Ich würde die λ-Linie nach Punkt 1 als dokumentierten Landschaftsbefund abschließen und die Ryzen-Zeit den theoretischen Linien geben, etwa den Genus- und Topologieschranken im Repository. Das ist eine Ressourcenabwägung, kein mathematisches Urteil. Die Wiederaufnahmebedingungen aus meinem letzten Review gelten unverändert.

### Nächster Schritt

Die Endpunkt-Scores sind nicht auf Git: `AUDIT.json` enthält nur die Nahklasse. Lade bitte das Abschlussarchiv hier hoch, also `ryzen_lambda_profile_100_20260927_recovery_101_results.tar.gz` mit SHA256 `ccdb709a…`. Ist es zu groß, genügen die JSONL-Dateien der 20 Zellen. Ich prüfe dann den Hash, rechne die Auswertung aus Punkt 1 mit dem unabhängigen Scorer und wende die obige Regel an.

ryzen_lambda_profile_100_20260927_recovery_101_results.tar.gz

GZ

Hat einen Befehl ausgeführt

Hash stimmt (`ccdb709a…`). Ich sehe mir das Episodenformat an.

2 Befehle ausgeführt

Die Regel ist eindeutig nicht erfüllt. Ich schlüssele noch die wenigen nahen Klassen auf, damit klar ist, woraus die Anteile ≤ W+5 bestehen.

3 Befehle ausgeführt, dateien geteilt

## Endpunktauswertung des λ-Profils

**Ergebnis:** Die vorab festgelegte Trichterregel ist in keiner Zelle erfüllt. Nach unserer eigenen Regel folgt daraus: **endgültige Pause der λ-P-Linie.**

Der Archivhash `ccdb709a…` stimmt mit dem ERGEBNIS überein. Es wurde nichts neu gesucht. Alle 885 verschiedenen nicht zurückgekehrten Endgraphen habe ich mit dem unabhängigen Scorer ohne Projektcode neu bewertet; es gab 0 Abweichungen. Zusammen mit den beiden Startgraphen ergibt das die 887 Klassen aus dem Audit.

### Anwendung der Regel

Die Regel verlangte: In einer Zelle mit k ≥ 8 haben mindestens 10 % der nicht zurückgekehrten Endpunkte W ≤ W(Start)+5, **und** darunter sind mindestens 10 verschiedene Klassen.

| ZelleNicht zurückgekehrtΔW Median (Q1–Q3)Anteil ≤ +5Klassen ≤ +5Kanten ersetzt, Median |     |               |       |   |     |
| -------------------------------------------------------------------------------------- | --- | ------------- | ----- | - | --- |
| 2076, k=8                                                                              | 15  | 25 (22–38)    | 0 %   | 0 | 8   |
| 2076, k=12                                                                             | 53  | 31 (17–44)    | 9,4 % | 1 | 8   |
| 2076, k=16                                                                             | 107 | 46 (27–73)    | 8,4 % | 2 | 12  |
| 2076, k=24                                                                             | 163 | 90 (51–135)   | 1,8 % | 2 | 23  |
| 2076, k=32                                                                             | 183 | 154 (103–204) | 0,5 % | 1 | 47  |
| 2077, k=8                                                                              | 14  | 18 (18–32)    | 0 %   | 0 | 8,5 |
| 2077, k=12                                                                             | 69  | 34 (18–58)    | 0 %   | 0 | 10  |
| 2077, k=16                                                                             | 107 | 50 (26–76)    | 0 %   | 0 | 13  |
| 2077, k=24                                                                             | 172 | 88 (46–139)   | 0 %   | 0 | 23  |
| 2077, k=32                                                                             | 179 | 159 (114–210) | 0 %   | 0 | 48  |

Der höchste Anteil liegt bei 9,4 %, und er besteht aus einer einzigen Klasse. Beide Bedingungen sind also verfehlt, bei W2077 besonders deutlich.

### Die nahen Minima

Innerhalb von W+10 gibt es über beide Arme nur **sechs** verschiedene Klassen:

| ArmW / L1BeobachtetBemerkung |             |     |                                                                                                  |
| ---------------------------- | ----------- | --- | ------------------------------------------------------------------------------------------------ |
| 2076                         | 2077 / 2488 | 17× | das bekannte Nachbarminimum in Tiefe 2                                                           |
| 2076                         | 2079 / 2484 | 2×  | **exakt der beschriftete Zustand des alten W2079-Rekords** (state `7acadd04…`), also der Vorfahr |
| 2076                         | 2082 / 2476 | 8×  |                                                                                                  |
| 2076                         | 2083 / 2478 | 5×  |                                                                                                  |
| 2076                         | 2086 / 2480 | 1×  |                                                                                                  |
| 2077                         | 2085 / 2460 | 15× | einziges nahes Minimum dieses Arms                                                               |

### Deutung [H]

Um W2076 liegt eine kleine Gruppe von höchstens fünf festen Dellen, darunter der eigene Vorfahr. Um W2077 liegt praktisch nur eine. Die Abstiege finden immer wieder dieselben wenigen Minima, keinen breiten Trichter mit vielen Varianten.

Lange Perturbationen führen dagegen weit weg und nach oben:

- Bei k=32 treibt die Perturbation W im Median um gut 410 hoch.
- Der Abstieg holt davon nur einen Teil zurück; der Median der Endpunkte liegt bei +154, im Abstand von 47 ersetzten Kanten.
- Fast jede Episode endet in einer eigenen Klasse (182 von 183).

Solche Episoden wirken wie Neustarts, und deren Ertrag kennen wir aus der O-Kampagne. Eine Kette mit Akzeptanz schlechterer Minima (ΔW ≤ 3) hätte hier nur die Wahl zwischen wenigen, meist schlechteren Nachbarn. Dass so eine Kette einen besseren Punkt als W2076 findet, lässt sich aus diesen Daten nicht begründen.

### Vorschlag

1. **λ-P-Linie abschließen**, und zwar gemäß der vorab festgelegten Regel als Ressourcenentscheidung, nicht als mathematisches Urteil. Die Abschlussseite dokumentiert drei Befunde: 
   - Radius 4 ist exakt geprüft, zu Tiefe 3 liegt eine unabhängige Nachzählung vor.
   - Das Rückkehrprofil zeigt: längere Perturbation verhindert die Rückkehr, bringt aber keine Verbesserung.
   - Die Endpunktverteilung zeigt wenige feste nahe Dellen und keinen Trichter.
    Der Strukturvergleich der Minima kann als beschreibender Anhang dazu. Mit dem Vorfahren W2079 sind es jetzt vier Graphen, eine Suche sollte er nicht auslösen.
2. **Wiederaufnahme** nur unter einer dieser Bedingungen: 
   - ein neuer Operator, der λ erhält und nachweislich andere Nachbarschaften erschließt, zum Beispiel ein geprüfter Katalog aus 3- und 4-Switches;
   - ein Gründer mit W < 2076 aus einer anderen Linie.
3. **Ryzen-Zeit** in die theoretischen Linien geben.

Im ZIP liegen das Auswertungsskript, die Ergebnisse je Zelle, die Liste der nahen Klassen und `SHA256SUMS`. SHA256 des ZIPs: `5f01eb2efaf68ede30175b4f2e5e937229b994cf20d1c326f14ca5821c2d6f63`.

**Nächster Schritt:** Lege die Auswertung auf Git neben das ERGEBNIS, zum Beispiel unter `docs/memetik/lambda_profile_20260927/endpoints/`. Wenn du willst, formuliere ich danach die Abschlussseite der λ-P-Linie.