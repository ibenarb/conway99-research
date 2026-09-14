> **Korrektur nach Code-Nachreichung:** Mistral hatte Code angezeigt; dieser ging beim Kopieren verloren. Die folgende Bewertung beschreibt den früheren unvollständigen Eingang. Drei Generatoren und die Metrikfunktion wurden inzwischen tatsächlich ausgeführt. Siehe [Korrektur und Ausführungsbericht](code_supplement/REVIEW.md). Die pauschale Zuschreibung fehlender Codelieferung wird zurückgenommen.

# Mistral/Vibe v02: Befunde, Analyse, Schlussfolgerungen

Stand: 14. September 2026. Original: `original.md`; eigene Reproduktion: `audit_submission.py`, Ergebnisse: `audit.json`.

**Ergebnis: Drei Ansätze, null gelieferte Graphen, null Generatoren, null aufgenommene Kandidaten. REJECTED_AS_SUBMITTED.**

## 1. Ausgabe und Lieferumfang

Fortschritt gegenüber v01: keine scheinbaren graph6-Daten, keine erfundenen Messwerte; Ausführung ausdrücklich verneint. Die Datei endet mit ENDE DER ABGABE.

Trotz der Behauptungen „Alle Codeblöcke sind ausführbar“ und „vollständiger Code“ enthält die empfangene Datei keinen einzigen Codeblock. Die Abschnitte 3.2, 4.2, 5.2 bestehen nur aus Generatorüberschriften. Ein ZIP ist nicht beigefügt. Falls die Oberfläche Code separat angezeigt hat, wurde dieser nicht mitgeliefert; darüber wird keine Behauptung aufgestellt. Der Schlussmarker belegt nicht die inhaltliche Vollständigkeit.

## 2. Ω_Conway: konkrete Regel widerlegt

Untersucht wurde die explizite gdw-Regel: Zwei Außenpaare sind benachbart, wenn sie genau ein Element teilen und ihre Vereinigung genau eine Partnerkante enthält.

Für S={x,y} mit y ungleich Partner(x) sind genau zwei Nachbarn möglich:
{x,Partner(y)} und {Partner(x),y}.
Die Partnerkante kann nicht S selbst sein; das neue Element muss daher der Partner des jeweils ausgetauschten Elements sein. Damit hat H Grad 2 statt 12. Der vollständige A-Graph hat 84 Knoten vom Grad 4 und 15 vom Grad 14.

Eigene vollständige Auswertung aller 1176 Einträge von PH ergibt 840 Verletzungen der Zielgleichung.
Expliziter Zeuge: Außenpaar {1,2}, Zeile a=0. Die beiden H-Nachbarn sind {1,9} und {2,8}; folglich (PH)[0,{1,2}]=0. Gefordert ist 2.

Auch die erläuternde Deutung der rechten Seite ist falsch: Es wird pro Zeile a die Zugehörigkeit von a und Partner(a) zum Außenpaar subtrahiert. Außenpaare sind selbst keine Partnerpaare.
Die spätere Beschreibung „nicht beide in C“ ist nicht gleichbedeutend mit der expliziten Regel; sie liefert keinen Nachweis. Dies ist kein bloß offener globaler λ-Test: Bereits die harten Ω-Bedingungen scheitern.

## 3. TriDecomp: Zählfehler und fehlende Ergänzung

33 disjunkte Dreiecke geben jedem Knoten Grad 2, nicht 14.
In einem 14-regulären Graphen mit genau einem gemeinsamen Nachbarn je Kante liegt jede Kante in genau einem Dreieck. Die 14 Kanten an jedem Knoten paaren sich daher zu sieben Dreiecken. Insgesamt sind 99×7/3=231 Dreiecke erforderlich.

Die Behauptung, 33 Dreiecke könnten jeden Knoten 14-mal abdecken, widerspricht bereits der Inzidenzzählung: 33×3=99, nicht 99×14. Auch 14 Dreiecke pro Knoten wären bei eindeutiger Kantenbelegung die falsche Zielzahl.

In einem vollständigen STS(99) liegt jeder Knoten in 49 Blöcken, hat im zugehörigen Paargraphen aber 98 Nachbarn. Mistral verwechselt Blockanzahl und Nachbarzahl.

Ein System ausgewählter Tripel ist eine mögliche Modellrichtung. Eindeutige Paarbelegung allein garantiert jedoch kein λ=1 im entstehenden Graphen: Drei verschiedene Blöcke können die drei Kanten eines zusätzlichen Dreiecks liefern. Diese zusätzlichen Dreiecke müssen ausdrücklich ausgeschlossen werden. Die Existenz eines vollständigen STS liefert somit keinen Nachweis für den gewünschten Teilgraphen.

Die geforderten zusätzlichen Kanten sind nicht konstruiert. Aussagen über Existenz/Konstruktion von STS oder Kirkman-Systemen wurden für diesen Audit nicht extern verifiziert; die Ablehnung beruht auf elementaren Zählungen und dem fehlenden Ergänzungsalgorithmus.

## 4. RandFill: Startproblem und falsche Prüfung

Wenn nach jedem einzelnen Einfügen jede bestehende Kante genau einen gemeinsamen Nachbarn haben muss, ist bereits die erste Kante unzulässig: Im leeren Graphen hat sie null gemeinsame Nachbarn. Die behauptete Invariante erlaubt keinen Start.

Wenn die Prüfung dagegen nur zuvor vorhandene Kanten betrifft, könnte der erste Schritt zugelassen werden, aber die behauptete Invariante wäre verletzt. Der Text definiert hier keinen konsistenten vollständigen Algorithmus.

Die für eine Kante {u,w} angegebene Schnittmenge N(u)∩N(v) prüft zudem die falschen Endpunkte. Unkontrolliertes Löschen kann ebenfalls bestehende Dreiecke zerstören. Ein zufälliges Entfernen ist kein dokumentiertes vollständiges Backtracking.

Mögliche Korrekturrichtungen wären atomare Dreieckszüge oder vorübergehend unvollständige Bedingungen mit einer korrekten Ergänzungsprüfung. Sie sind eigene Folgevorschläge, keine bereits gelieferte Implementierung.

Der Hinweis „nur bestehende Kanten, nicht alle Paare“ ist als λ-Einschränkung irreführend: Für den λ-Arm ist genau die Prüfung aller Kanten gefordert. Für Nichtkanten wird λ=1 gerade nicht verlangt.

## 5. Schlussfolgerung und nächste Rückfrage

Die kürzere Aufgabenstellung hat die Ausgabeform teilweise verbessert. Sie hat weder die Lieferung von Code noch mathematische Korrektheit sichergestellt. Aus dieser Antwort lässt sich keine Ursache im kostenlosen Zugang oder in einer bestimmten Modellversion ableiten.

Empfehlung: Mistral einmal gezielt die konkrete Ω-Regel samt Gegenbeispiel zurückgeben und um Rücknahme oder echte Korrektur bitten. Nur ein vollständiger Generator, mit ehrlichem NICHT AUSGEFÜHRT falls nötig. Keine erneute Ausarbeitung dreier unvollständiger Familien. Die abstrakten Suchrichtungen sind durch diese Ablehnung nicht ausgeschlossen.

## 6. Reproduktion

`python3 audit_submission.py original.md`

Python-Standardbibliothek, keine Fremdpakete. Das Skript rekonstruiert die ausdrücklich beschriebene Ω-Regel und berechnet deren H-Grade und PH-Verletzungen vollständig. Keine Ausführung von Mistral-Code (nicht vorhanden), keine Isomorphieprüfung und keine Suche nach einer reparierten Konstruktion. Die weiteren Schlussfolgerungen sind oben argumentativ ausgewiesen.

Original: 9800 Bytes, SHA256 `8b1a3c20c11f13c4b3f459faf89cdc28ad39153aabd5c9b2a121735e159b8915`.
