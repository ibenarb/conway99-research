# Lemma N, gemeinsame Matchingtypen und LOW

Stand 12.10.2026. Ergänzung zur Arbeitsfassung 0.5. Der allgemeine C2-Ausschluss bleibt offen.

## Ergebnis und Entscheidung

Lemma N ist korrekt und verbessert die normalisierte Fallaufteilung für LOW.
Die Gesamtzahl der geordneten Matchingpaarbahnen ist 3.580. Davon haben **3.412**
Ausgrad höchstens 2. Ein zusätzlicher notwendiger lokaler Test schließt **260**
dieser LOW-Bahnen aus; **3.152** bleiben als Kandidatentypen übrig.
Diese Kandidaten sind nicht als global realisierbar nachgewiesen.

Die vorhandene bedingte Ausschlusskette für Profil346 bleibt verwendbar.
Sie wird nicht erneut gerechnet. Für den weiteren rechnerischen LOW-Ausschluss
wären neue, auf LOW beschränkte Solver-/Zertifikatsläufe nötig, sofern kein weiterer
mathematischer Ausschluss gefunden wird. Vor einem großen Nutzerlauf sind die
Formelergänzung und ein kleiner LOW-Pilot zu prüfen. Aus den Fallzahlen folgt keine
verlässliche Laufzeit; insbesondere folgt daraus keine erneute 67-Stunden-Rechnung.
Die heutigen Prüfungen waren kleine endliche Aufzählungen, keine SAT-Läufe.

## 1. Beweis des Partnermatchings

Wir verwenden den bereits bewiesenen Rahmen mit Fixpunkt o, gepaarten Ankern
und Involution t. Für ein Ankerpaar a,b=t(a) sei W_a die Menge der zwölf
Außennachbarn von a und W_b=t(W_a). Der lokale Graph auf W_a ist das Matching L.
Das feste Matching P auf W_a vertauscht die Labels c und c*=t(c).

Für x in W_a sind x und b nicht benachbart. Von ihren genau zwei gemeinsamen
Nachbarn ist einer a. Da N(b)={o,a} vereinigt mit W_b und x nicht an o liegt,
hat x genau einen Nachbarn sigma(x) in W_b. Dasselbe Argument von W_b aus zeigt,
dass sigma eine Bijektion ist. Invarianz unter t liefert
sigma(t(sigma(x)))=t(x). Damit ist N(x)=t(sigma(x)) eine Involution auf W_a.
Sie hat keinen Fixpunkt, weil x und t(x) nicht benachbart sein können.
Also ist N ein perfektes Matching.

Für x=x_{a,c} gilt N(x)=x_{a,c*} genau dann, wenn x_{a,c} und x_{b,c}
benachbart sind. Dies ist die Pfeilbedingung q -> p für die Ankerpaare
q={c,c*}, p={a,b}. Deshalb ist der Eingrad von p gleich |N intersect P|;
er gehört wie der Ausgrad |L intersect P| zu {0,1,2,3,4,6}.
Insbesondere ist Eingrad 5 ausgeschlossen.

## 2. Zulässige gemeinsame Normalform

Nach Wahl eines Ankers mit minimalem Ausgrad darf der Stabilisator des
geordneten Ankerpaars, Aut(P)=C2 wreath S6, auf L und N gemeinsam wirken.
Er verändert weder die Minimumeigenschaft noch die zugrundeliegende Lösung.
Zuerst wird L auf einen Vertreter seines Partitionstyps gebracht, anschließend
N unter Stab(P,L) normalisiert. Eine zusätzliche unabhängige globale
Grad-/Profilnormalisierung wird dabei nicht vorausgesetzt.

Die Matchingdaten bestimmen sämtliche 66 Kantenentscheidungen innerhalb W_a
und weitere 66 unabhängige Entscheidungen zwischen W_a und W_b; Symmetrie und t
bestimmen ihre Gegenstücke. Das sind 132 unabhängige äußere Kantenbits anstelle
von 66 bei bloßer Festlegung von L. Die konkrete Übersetzung in die vorhandenen
B/C-Variablennummern ist vor einem Solverpaket noch gesondert zu prüfen.

## 3. Neuer notwendiger lokaler Kompatibilitätstest

L und N sind als perfekte Matchings **nicht beliebig kombinierbar**.
Für x=x_{a,c} und y=t(P(x))=x_{b,c} ist c ein gemeinsamer Ankernachbar.
Innerhalb W_a vereinigt mit W_b ist die Zahl weiterer gemeinsamer Nachbarn

    1[L(N(x))=P(x)] + 1[N(L(x))=P(x)].

Beide Summanden dürfen nicht zugleich 1 sein: Dann hätten x und y bereits
drei gemeinsame Nachbarn. Außerdem sind x und y in diesem Fall nicht benachbart:
N(x)=P(x) würde aus L(N(x))=P(x) einen Fixpunkt von L erzwingen.
Das widerspricht mu=2 und kann durch spätere Ergänzung des Graphen nicht behoben werden.

Ein konkretes verbotenes Teilmuster auf vier Elementen lautet

    P=(0 1)(2 3), L=(0 2)(1 3), N=(0 3)(1 2).

Auf den übrigen acht Elementen kann man für das Beispiel L=N=P setzen.
Die Bedingung ist invariant unter Aut(P). Sie ist notwendig, kein Nachweis der
Erweiterbarkeit überlebender Matchingpaare zu einem Graphen mit 99 Knoten.

## 4. Exakte Zählung

| Ausgrad am gewählten Anker | Paarbahnen | Lokal ausgeschlossen | Verbleibend |
|---:|---:|---:|---:|
| 0 | 1.930 | 155 | 1.775 |
| 1 | 1.029 | 73 | 956 |
| 2 | 453 | 32 | 421 |
| **LOW** | **3.412** | **260** | **3.152** |
| 3 | 106 | 7 | 99 |
| 4 | 51 | 5 | 46 |
| 6 | 11 | 0 | 11 |
| **Gesamt** | **3.580** | **272** | **3.308** |

Die hohen lokalen Typen zählen somit 168 vor bzw. 156 nach dem lokalen Test.
Das ist keine Aufforderung zu einer Wiederholung des abgeschlossenen Profil346-Zweigs.
Die Tabelle zählt lokale Bahnen; die Minimumgradbedingungen an den anderen sechs
Ankerpaaren sind noch nicht auf globale Lösbarkeit geprüft.

## 5. Ausgeführte Prüfungen

`enumerate_pairs.py` erzeugt alle 10.395 perfekten Matchings und alle 46.080
Elemente von Aut(P). Für jeden der elf L-Typen werden sämtliche Bahnen der
N-Matchings unter Stab(P,L) explizit gebildet. Pro L-Typ ist die Summe der
N-Bahngrößen 10.395. Die gewichtete Summe aller Paarbahnen ist
10.395^2 = 108.056.025.

Ein gesondertes Burnside-Verfahren zählt die invarianten Matchings anhand der
Zykellängen jeder Permutation: Gleich lange Zyklen können miteinander gepaart
werden; ein gerader Zykel kann außerdem intern durch seine Halbdrehung gepaart
werden. Diese Zählung stimmt für jeden L-Typ und für die gesamte Gruppe mit der
expliziten Bahnbildung überein. Sie verwendet nicht die bereits erzeugten Bahnen.

`check_induced_graph.py` baut unabhängig vom Kompositionstest für jeden der
3.580 Vertreter den festgelegten induzierten Graphen auf o, den 14 Ankern und
W_a vereinigt mit W_b, also 39 Knoten. Es prüft für jedes Knotenpaar die
Obergrenze gemeinsamer Nachbarn (1 für Kanten, 2 für Nichtkanten).
Genau dieselben 272 Vertreter scheitern. Alle anderen bestehen diese lokalen
Obergrenzen; daraus folgt kein globales Existenzresultat.

Reproduktion vom Repositorywurzelverzeichnis:

```sh
python src/c2_lemma_n_20261012/enumerate_pairs.py results/c2_lemma_n_20261012
python src/c2_lemma_n_20261012/check_induced_graph.py results/c2_lemma_n_20261012/pair_orbits.jsonl results/c2_lemma_n_20261012/induced_graph_check.json
```

Die vollständige Vertreterliste wird vom Skript erzeugt; ihr SHA-256 steht im
Manifest. Ergebniszusammenfassung und unabhängiger Kontrollbericht sind beigelegt.

## 6. Nächster sinnvoller Rechenschritt

Zuerst die 132 Kantenbits korrekt in F0 abbilden und die gemeinsame Normalisierung
mit einer kleinen bekannten Positivinstanz kontrollieren. Dann ein kleiner,
stratifizierter LOW-Pilot über alle acht L-Typen, einschließlich Grad 0 und 1,
mit klar begrenztem Ressourcenbudget und Erfassung von Solver- und Checkeraufwand.
Erst seine Ergebnisse rechtfertigen Größe und Organisation eines neuen lokalen
Produktionslaufs. Weitere mathematische Filter können die Kandidatenzahl vorher senken.

Anstoß war der privat archivierte Review vom 12.10.2026. Der vorliegende Text
enthält die eigene Prüfung, die korrigierte Gradaufteilung und den neuen
Kompatibilitätstest; der private Review wird hier nicht veröffentlicht.
