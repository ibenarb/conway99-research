# Gemini v01: Befunde, Analyse und Aufnahme

14. September 2026.

**Ergebnis: Ein tatsächlich erzeugter und unabhängig geprüfter Ω-Kandidat. Aufnahme als gültiger Graph, strukturelle Neuheit und Eignung für den nächsten Piloten noch offen.**

## 1. Modell und tatsächliche Ausführung

Der bereitgestellte Generator bildet die vereinbarten Ω-Bedingungen korrekt ab:
3486 Boolesche Kantenvariablen für H, gemeinsame Variable für beide Richtungen, Nulldiagonale durch Konstante; 84 Gradgleichungen und 1176 PH-Gleichungen. Keine zusätzliche λ-Bedingung, keine weitere Symmetrieannahme.

Die Solver-Modelvalidierung liefert keine Fehler. Mit Seed 42, einem Worker und 45 Sekunden Obergrenze wurde nach etwa 2,47 Sekunden eine Lösung gefunden. Modell und mathematische Bedingungen wurden nicht verändert. Originaleinstellungen: 3600 Sekunden und keine explizite Workerzahl.

Solverstatus OPTIMAL bedeutet hier die erfolgreiche Lösung des reinen Erfüllbarkeitsmodells, **keine Optimierung von W, L1, F oder Linf**. Es gibt keine Zielfunktion.

Getestete Umgebung: Python 3.12.14, OR-Tools 9.15.6755, NumPy 2.5.3, NetworkX 3.6.1. Pakete wurden in einem separaten Scratch-Ziel installiert, da OR-Tools und NetworkX zuvor fehlten. Ein erster Startversuch scheiterte an einem von uns falsch angegebenen lokalen Dateipfad, bevor Code ausgeführt wurde; nach Korrektur lief der dokumentierte Probelauf erfolgreich.

## 2. Unabhängige Abnahme der exportierten Datei

validate_candidate.py verwendet weder CP-SAT noch Generatorhilfsfunktionen noch NetworkX. graph6 wird direkt dekodiert und anschließend mittels Mengenrechnung geprüft:
- 99 Knoten, einfach, symmetrisch, jeder Grad 14;
- vollständiger kanonischer Wurzel-/Nachbar-/Außenrahmen;
- H-Grad 12 und alle 1176 PH-Gleichungen;
- sämtliche 4851 ungeordneten Paare für die Fehlerwerte;
- graph6-Header, Länge, Padding und genau ein abschließendes LF.

Ergebnis PASS. Unabhängige Werte stimmen mit der Generatorausgabe überein:

| Kennzahl | Wert |
| --- | ---: |
| W | 3107 |
| L1 | 5310 |
| F=L2² | 11504 |
| Linf | 8 |
| Nmax | 3 |
| λ-verletzende Kanten | 420 |

Die 420 λ-Verletzungen sind im Ω-Arm zulässig. Sie disqualifizieren den Graphen für den separaten λ-Arm.

kandidat_42.g6: 814 Bytes einschließlich LF.
SHA256: 5dbfad84a90aa1622f51c171c0b72857ad8721173b74f23ed21473616c91dffb.

## 3. Einordnung

Dies ist eine funktionierende Umsetzung des bekannten linearen Ω-Vertrags und eine reale Kandidatenerzeugung. Die erstmalige Erfüllbarkeit dieses Suchraums wird damit nicht behauptet: Im Projekt liegen bereits Ω-Gründer vor.

Der erste erzeugte Graph verbessert die bisherigen Bestwerte nicht. Das ist kein Ablehnungsgrund für ein Diversitätsexperiment. Aber aus einer anderen Erzeugungsmethode oder einem anderen Seed folgt weder Nichtisomorphie noch ein anderes Einzugsgebiet.

Kein Isomorphietest gegen das vollständige Projektarchiv durchgeführt. Auch keine Behauptung, die Strukturfamilie sei neu. Aufnahme ins validierte Archiv; Auswahl für den Pilot und Gründerneuheit bleiben gesonderte Entscheidungen.

## 4. Verbleibende Schwächen und notwendige Erweiterungen

- Im Original fehlt die unabhängige Nachprüfung vor Export. Diese wurde hier extern durchgeführt und sollte vor jeder dauerhaften Aufnahme automatisiert werden.
- INFEASIBLE, UNKNOWN und MODEL_INVALID werden in derselben Textmeldung zusammengefasst. Für belastbare Laufberichte getrennt ausweisen. Ein Zeitlimit ist kein Unmöglichkeitsbeweis.
- Workerzahl ist nicht begrenzt. Auf dem Office-Rechner ausdrücklich budgetieren. Seed allein garantiert bei automatischer paralleler Suche keine identische Ausgabe.
- Wiederholung desselben Seeds überschreibt den Dateinamen. Für die Sammlung Laufkennung und Dateihash verwenden.
- Verschiedene Seeds garantieren keine Vielfalt. Zunächst kanonisch deduplizieren und Herkunft/Fehlerprofile untersuchen; Ausschluss bereits gefundener Lösungen oder diverse Suchziele wären spätere Erweiterungen, nicht Bestandteil dieses Tests.
- Die Aussage „quadratische Bedingungen sprengen Standard-CP-Solver“ ist unbegründet pauschal. Ihre Modellierung und Kosten hängen vom konkreten Verfahren ab.
- Fehlerwerte werden exakt berechnet, nicht heuristisch geschätzt.
- T hat hier nur Werte 1 und 2. Summiert man PH=T über die 14 Zeilen, folgt 2·Grad_H=24. Die gesonderten Gradgleichungen sind daher mathematisch redundant, aber korrekt und als Solverhilfe zulässig.
- Die behauptete Mindestversion Python 3.8 wurde nicht getestet; reproduzierbar belegt ist die oben genannte Umgebung.

## 5. Reproduktion und Provenienz

Im Vorgangsverzeichnis: python3 probe.py; anschließend python3 validate_candidate.py.
Abhängigkeiten des Probelaufs oben, der unabhängige Validator benötigt nur Python-Standardbibliothek.

SOURCE.md dokumentiert den Eingang im Chat. generator.py enthält den bereitgestellten Code. probe.py dokumentiert die begrenzten Ressourcenparameter. probe.json und probe_console.log enthalten Solver- und Programmresultate. validation.json enthält eigene Abnahme und Scores.

Die Datei stammt aus unserer tatsächlichen Ausführung des Gemini-Generators. Gemini selbst hatte korrekt keine Ausführung behauptet.
