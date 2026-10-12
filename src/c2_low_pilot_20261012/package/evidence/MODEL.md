# Kodierter notwendiger Übergang

F0 ist die unveränderte, durch SHA-256 gebundene Rahmenformel E1–E3.
L und N sind fest vorgegebene perfekte Matchings auf den zwölf Elementen W_a;
P(i)=i xor 1. Die 132 Units kodieren L intern und N über die t-Partner.
Eine zweite unzulässige Normalisierung wird nicht verwendet.

Für Z, die 60 übrigen Außenlabels, seien T die Partnerpermutation, R_Z die
Labelinzidenz und X die binäre Nachbarschaft von W_a nach Z. Kodiert werden:

- jede Zeile von X hat zehn Einsen, jede Spalte zwei;
- XX^T=9I+J-L (Diagonale bereits durch Zeilengrade);
- XTX^T=2J-P-N-LN-NL;
- XR_Z=2J-I-P-L-NP;
- X_(i,z)+X_(P(i),t(z))+R_Z(z,i)+R_Z(z,P(i)) <= 2.

Die letzten Ungleichungen folgen aus den Obergrenzen gemeinsamer Nachbarn
zwischen z und dem Anker i. Es gibt bereits den gemeinsamen Partneranker,
falls P(i) im Label von z liegt, sowie die zwei entsprechenden Nachbarn in W_a
und W_b. Bei Adjazenz von z und i beträgt die Obergrenze 1 statt 2.
Da ein Z-Label kein Partnerpaar enthält, wird bei Labelkontakt genau eine
binäre Verbotsklausel benötigt, sonst ist die Ungleichung automatisch erfüllt.

Die ersten vier Bedingungen sind Blöcke der Rahmenidentitäten. Jede gültige
Conway-99-C2-Lösung liefert deshalb eine Belegung dieser X-Formel.
Ein checkerbestätigtes UNSAT schließt die betreffende Matchingwurzel aus.
Umgekehrt wird keine hinreichende Erweiterbarkeit eines X-Modells behauptet.

Produktvariablen werden bidirektional als UND definiert. Exakte Summen nutzen
den unveränderten Referenzencoder bzw. dessen bereits auditierten gekürzten
Totalizer für Zielwerte bis 2; Mehrfachvorkommen werden als Gewichte berücksichtigt.
Die Ursprungsquellen liegen unverändert unter legacy.

Regel R: Für q != 0 wird (d+(q)>=3) ODER (d+(q)+d-(q)<=D(0)) kodiert.
Die Zählerausgänge sind vollständig äquivalente Schwellenvariablen. Eine
Disjunktion zweier solcher Literale ist keine bloße einseitige Implikationsheuristik.
MIN benutzt ausschließlich d+(q)>=d+(0). Beide Varianten werden nicht vermischt.
Die X-Relaxation enthält keine unbewiesene Projektion dieser globalen Regeln.

Gültigkeit der Wurzelüberdeckung, Fixpunktsatz und der bereits abgeschlossene
Hochgradzweig bleiben die dokumentierten mathematischen bzw. historischen
Voraussetzungen. Das Pilotpaket beweist keinen neuen allgemeinen C2-Ausschluss.
