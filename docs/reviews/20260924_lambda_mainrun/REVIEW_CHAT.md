**Kurzfassung: In dieser Form rate ich davon ab.** Der Vorschlag ist sorgfältig formuliert und in vielen Details richtig. Er stützt sich aber nicht auf die Befunde, die er zu verwerten vorgibt: Die Zahlen aus V1 und V3 kommen im Text gar nicht vor. Wo er sich auf diese Prüfungen bezieht, widerspricht er dem, was sie zeigen.

Die 24 Bestgraphen des Pakets habe ich selbst nachgerechnet: alle λ-gültig, W, L1, Linf und Nmax stimmen. Receipts, Hashes und SQLite habe ich diesmal nicht erneut auditiert.

## Was die Vorprüfungen zeigen

**V1 (PCesc gegen P, 8 gepaarte Seeds, 3 600 CPU-s)** ist ein Nullergebnis.

- Nach (W, L1) steht es 5 : 3. Der Median der W-Differenzen ist −0,5, die Einzelpaare streuen von −20 bis +19. Median P 2141, PCesc 2138,5, also innerhalb der Jobstreuung.
- PCesc kostet wenig: Der cycle3-Katalog braucht nur rund 5 % der CPU, der Durchsatz liegt bei 374 statt 422 Episoden je Stunde.
- Entscheidend ist ein anderer Punkt: cycle3 findet an 10–17 % der exakten AP-Minima tatsächlich eine strikte Verbesserung, 42 bis 76 Fluchten je Job. **Die Fluchten finden also statt, die Endwerte werden trotzdem nicht besser.** Damit ist V1 der direkteste Test der Idee „besser aus lokalen Minima entkommen“, und er ist negativ.
- Nebenbei bestätigt P mit neuen Seeds bei 3 600 CPU-s genau den alten Median 2141. Die logarithmische Kurve steht.

**V3 (vier nicht-HoG-Linien × 2, je 7 200 CPU-s)** verfehlt das Kriterium.

- Kein Job kommt unter W = 2200. Der beste liegt bei 2222, der Median bei etwa 2250. HoG liegt bei gleicher CPU bei 2130, also rund 120 W besser.
- Die Kurven fallen steiler, etwa −25 W je Verdopplung gegenüber −10 bei HoG. Das erwartet man aber schlicht, weil sie weiter oben stehen.
- Die Unterschiede zwischen den Linien sind so groß wie die zwischen den beiden Wiederholungen derselben Linie (gen-lambda-13: 2238 gegen 2279). Die Bevorzugung von `gen-lambda-03` im Vorschlag stützt sich damit auf Rauschen.

**Neu aus den Histogrammen, und für den Vorschlag zentral:**

- Gewöhnliche Perturbationen klettern schon jetzt im Median **+91 W** über den Elternteil, zu 90 % bis +268, maximal +460.
- **64 % aller Episoden kehren exakt zum beschrifteten Elterngraphen zurück.**
- In der gemischten V1-Bank stellen die HoG-Linien nach 30 CPU-Minuten 97 % der Endpunkte und am Ende 100 % der Population.

## Warum der Vorschlag nicht trägt

**Er übergeht die vorab vereinbarten Konsequenzen.** Meine Bedingungen für einen Hauptlauf waren:

1. eine Maßnahme verbessert den Median bei 7 200 CPU-s um mehr als 18 W, oder
2. V3 erreicht W < 2200.

Beides ist nicht eingetreten. Für den negativen V3-Fall stand fest: Die Gründerbank wird auf HoG reduziert. Der Vorschlag gibt nicht-HoG-Familien stattdessen **9 von 18 Inseln, also die Hälfte des Budgets**. Das Paket-README hatte die Kriterien schon vor dem Lauf aufgeweicht („W<2200 ist ein positives Signal, keine notwendige Bedingung“). Genau dieses Vorgehen, einen offenen Ausgang nachträglich in eine siebenmal größere Investition umzudeuten, sollte die Vorabfestlegung verhindern.

**Die Barrierenausflüge begrenzen die Suche, statt sie zu erweitern.** Die Grenzen +42 / +105 / +210 bei W = 2100 liegen im Bereich dessen, was gewöhnliche Perturbationen ohnehin erreichen, die untere sogar darunter. Neu wäre nur die Länge, und was „gezielt“ bedeuten soll, ist nirgends definiert. Dafür 15 % des Budgets.

**Die Sprungmutation ist in der Praxis ein Neustart.** Ein AP-Zug ändert 4 oder 8 Kanten. Schon der kürzeste Sprung von 33 Zügen ändert damit bis zu 130–260 Kanten. Die gesamte 300-CPU-h-Trajektorie des HoG-Beckens hat sich nur 72–164 Kanten bewegt. Was ein Neustart kostet, zeigt V3: Nach 300 CPU-s standen die Jobs bei 2342–2401, erst nach zwei Stunden bei etwa 2250. Mit der geplanten 300-s-Obergrenze landen Sprungnachkommen also über 200 W hinter den Inseln, und acht geschützte Elternverwendungen schließen diese Lücke nicht. Der erwartete Ertrag der 86 CPU-h ist praktisch null. Die Literaturstütze für (k^{-1{,}5}) ist übrigens ein verwaister Verweis (`:chatgpt-content-reference{index="0"}`). Gemeint ist vermutlich die „fast GA“-Theorie für Bitstring-Sprungfunktionen, die sich auf diesen Zugraum kaum übertragen lässt.

**Crossover** verlangt eine Knotenzuordnung zwischen starren Graphen. Das ist teuer zu bauen, unerprobt und für höchstens 43 CPU-h. Ich würde es weglassen.

**Die Kontrollen reichen nicht, und es fehlen Ziel und Abbruchregel.**

- Drei Referenzinseln, je eine pro Familie, ohne Replikat: Die Jobstreuung liegt bei rund 9 W, die Replikatspreizung in V3 bei bis zu 41 W. Die Effekte, um die es geht, lassen sich damit nicht auflösen.
- Es gibt kein Erfolgskriterium und keine Abbruchregel. Die Auswertungen bei 8, 24 und 48 Stunden unterbrechen den Lauf ausdrücklich nicht.
- Es fehlt auch die ehrliche Erwartung: Die bestätigte Kurve extrapoliert für HoG-W-Inseln bei 48 CPU-h auf einen Median um **2090**. Das ist, was 864 CPU-h realistisch kaufen: vielleicht 10–20 W unter dem bestehenden Rekord 2102, keine Annäherung an eine Lösung.

**Übernehmen würde ich:** Isomorphie-Deduplikation, reine Inseln je Familie (falls man nicht-HoG überhaupt weiterführt), die Unterscheidung von Weglänge und Barrierenhöhe, die Abrechnung gescheiterter Versuche und das gemeinsame Mehrzielarchiv.

## Was ich stattdessen vorschlage

Zwei kleine Schritte mit vorab festen Kriterien, zusammen etwa 60 CPU-h, also rund vier Stunden auf dem Ryzen:

1. **V2 nachholen (12 CPU-h).** Frontier-Seeding ist die einzige Frage aus dem ursprünglichen Plan, die noch offen ist. Kriterium wie vereinbart: Erreicht ein Job W < 2102?
2. **Die acht V3-Jobs auf 8 CPU-h verlängern (+48 CPU-h).** Das prüft die These des Reviewee, die späten Z33-Verbesserungen seien ein Hebel, billig statt mit 432 CPU-h. Kriterium: Erreicht ein Job W < 2150? Das entspricht grob dem HoG-Niveau nach etwa einer Stunde.

Danach ergibt sich die Entscheidung von selbst:

- **V2 positiv:** ein schlanker HoG-Frontier-Lauf mit einem Operatorsatz (P oder PCesc, das ist egal), ohne Sprünge und Crossover, mit vorab festem Ziel und Abbruch nach einem Viertel.
- **V3-Fortsetzung positiv:** Erst dann sind Inseln für nicht-HoG-Familien gerechtfertigt.
- **Beides negativ:** Die λ-Memetik wird als sauber dokumentiertes Negativergebnis abgeschlossen. Nach über 450 CPU-h mit bestätigter logarithmischer Ertragskurve wäre das ein legitimer und verwertbarer Ausgang.
