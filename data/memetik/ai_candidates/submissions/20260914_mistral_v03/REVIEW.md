# Mistral v03: Ausführung, Befunde und Korrektur

14. September 2026. Zwei Generatoren im Chat empfangen, Vollständigkeit vom Nutzer bestätigt. Keine eigenständige Originaldatei hochgeladen. Ausführbare Anweisungen transkribiert, Kommentare/Docstrings weggelassen, Kopier-Escape im Slice normalisiert und identischer Encoder gemeinsam verwendet; siehe manifest.json. Keine Änderung an Konstruktion, Abnahmebedingungen oder graph6-Algorithmus.

**Ergebnis: Beide Programme melden NO_CANDIDATE_FOUND und beenden mit Exitcode 1. Null aufgenommene Kandidaten.**

## λ: Sidon-Eigenschaft richtig, behauptete Schlussfolgerung falsch

D={1,2,4,8,16,32,64} besitzt modulo 99 tatsächlich 28 verschiedene Summen ungeordneter Paare einschließlich Wiederholungen. Die Sidon-Eigenschaft ist unter dieser Definition erfüllt. Unsere Prüfung widerspricht dieser Teilbehauptung nicht.

Der ungerichtete Graph verwendet aber S=D∪(-D), nicht nur D. Gemeinsame Nachbarn von 0 und d werden durch S∩(d+S) gezählt. Die Argumentation über positive Differenzen allein erfasst sie nicht.

Konkretes Gegenbeispiel: 0 und 1 sind benachbart, und beide haben 2 sowie 98 als Nachbarn. Damit ist λ auf dieser Kante 2 statt 1.
Vollständige Auswertung: 99 Kanten haben einen, 99 zwei, 495 drei gemeinsame Nachbarn. Also 594 von 693 Kanten unzulässig.

Grad 14, Einfachheit und Symmetrie sind für dieses konkrete D erfüllt. Allgemein folgt Grad 2|D| nur, wenn keine Nullschritte oder Kollisionen zwischen ±d vorkommen.

Die korrigierte Codeprüfung funktioniert: Der Generator meldet NO_CANDIDATE_FOUND. Die Prosa behauptet weiterhin fälschlich einen erfolgreichen Kandidaten.

## Eigene mathematische Folgerung: kein zirkulärer λ-Gründer auf Z99 vom Grad 14

Dies ist eine eigene Herleitung aus dem Prüfauftrag; es wird keine Literatur-Neuheit behauptet.

Sei S⊂Z99 ohne 0 mit S=-S die Verbindungsmenge eines einfachen ungerichteten zirkulären Graphen. Angenommen, jede Kante hat genau einen gemeinsamen Nachbarn.

Für jedes d∈S ist die Abbildung x↦d-x eine Involution auf der Menge gemeinsamer Nachbarn von 0 und d: Aus x∈S und x-d∈S folgen durch S=-S auch d-x∈S und -x∈S. Eine einelementige Menge muss unter dieser Involution aus einem Fixpunkt bestehen. Also 2x=d modulo 99 und d/2∈S.

Da Multiplikation mit 2 modulo 99 bijektiv ist, impliziert dies für das endliche S: S ist eine Vereinigung vollständiger Verdopplungsbahnen auf Z99 ohne 0.

Diese Bahnen haben die Größen 30,30,10,10,10,6,2. Repräsentanten: 1,5,3,9,15,11,33. Direkte Iteration in audit.py liefert alle 98 Nichtnullreste genau einmal.

Keine Auswahl dieser Bahnen hat insgesamt 14 Elemente:
- Eine 30er-Bahn ist zu groß.
- Ohne 10er-Bahn sind höchstens 6+2=8 erreichbar.
- Mit genau einer 10er-Bahn wären weitere 4 nötig, die aus 6 und 2 nicht entstehen.
- Zwei 10er-Bahnen sind bereits zu groß.

Widerspruch zu |S|=14. **Damit existiert kein einfacher ungerichteter 14-regulärer zirkulärer Graph auf Z99 mit λ=1 auf allen Kanten.**

Das schließt diese spezielle Gründerfamilie aus, nicht den gesamten λ-Suchraum, andere Gruppen oder allgemeine Block-/Liftkonstruktionen. Es ist nicht nötig, innerhalb dieser zirkulären Familie weitere Differenzenmengen zu suchen. Die Aussage setzt nicht μ=2 voraus.

## Ω: Johnson-Nachbarschaft weiterhin zu dicht

Für ein Außenpaar {a,b} entstehen 11 erlaubte andere Paare mit a und 11 mit b, insgesamt H-Grad 22 statt 12. Daher haben 15 Knoten des Gesamtgraphen Grad 14 und die 84 Außenknoten Grad 24.

Die eigene Gradprüfung bricht entsprechend ab und main meldet NO_CANDIDATE_FOUND. Zusätzlich ergibt unabhängige Nachrechnung 168 Verletzungen der 1176 PH-Gleichungen. Die 168 betroffenen Einträge sind jene mit a im Außenpaar: linker Wert 11 statt rechter Wert 1; diese Zählung erklärt die Abweichung direkt.

## Kopierfehler und graph6 getrennt behandeln

Die Chatübertragung enthält bits[i\\:i+6]. Wörtlich ist dies ungültiges Python. Für die Ausführung wurde ausschließlich dieser Backslash entfernt; keine mathematische Reparatur. Es wird nicht behauptet, der Fehler sei in Mistrals ursprünglichem Editor entstanden.

Unabhängig davon ist der Encoder sachlich falsch:
- Für n=99 erzeugt er OA statt des erforderlichen Headers ~?@b.
- Die Bitreihenfolge ist zeilenweise im oberen Dreieck; graph6 benötigt (0,1),(0,2),(1,2),(0,3),... .
- Resultierende Länge: 811 statt 813 Zeichen ohne LF.

Diese Encoderfehler verhindern die aktuelle Konstruktion nicht zusätzlich, weil beide Programme schon vor der Ausgabe ablehnen. Sie müssten aber vor einer erfolgreichen Kandidatenlieferung behoben werden.

## Bewertung

Fortschritt: tatsächliche Programmeinstiege und ehrliche Abbruchausgabe; die Kontrollen verhindern falsche Erfolgsmeldungen im Programm. Weiterhin nicht tragfähig: mathematische Erfolgsbehauptung zum λ-Rezept sowie Ω-Rezept mit falschem Grad. Kein Fehler wegen fehlenden Codes zugeschrieben.

Reproduktion: python3 audit.py (NumPy erforderlich). Der Audit startet beide transkribierten Programme separat mit aktiven Assertions, prüft D und die Verdopplungsbahnen und untersucht die Ω-Matrix nach dem abgefangenen Gradfehler. Zwei Main-Funktionen werden nicht versehentlich in einer Datei hintereinander ausgeführt.
