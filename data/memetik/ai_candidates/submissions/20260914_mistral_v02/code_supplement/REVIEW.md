# Korrektur und Ausführungsprüfung: Code-Nachtrag zu Mistral v02

14. September 2026.

## Korrektur unserer Zuschreibung

Ralph hat klargestellt: Die Mistral-Oberfläche zeigte die Codeblöcke, sie wurden beim Kopieren der Markdown-Antwort jedoch nicht mitgenommen. Er hat drei Generatoren und compute_metrics im Chat nachgereicht.

Unsere pauschale Zuschreibung, Mistral habe keinen Code geliefert, wird zurückgenommen. Richtig war nur: In der zunächst empfangenen Datei fehlte der Code. Eine Aussage über den vollständigen Inhalt der Mistral-Oberfläche war damit nicht gerechtfertigt. Der ursprüngliche Dateibefund bleibt historisch nachvollziehbar, ist aber keine Lieferbewertung der nun ergänzten Antwort.

## Methode

Die ausführbaren Anweisungen wurden ohne algorithmische Korrektur in generators_transcribed.py übertragen; Kommentare/Prosa wurden weggelassen und Importe zusammengeführt. Dies ist ausdrücklich keine byteidentische Originaldatei. Die Quelle ist die Code-Nachreichung im Chat. Manifest mit Dateihashes liegt bei.

Alle drei Funktionen tatsächlich aufgerufen, NumPy-Seed 42 für TriDecomp und vorgegebener Python-Seed 42 für RandFill. Assertions blieben aktiv. Nach deren Fehlschlag wurde die lokale Matrix über den Traceback ausgelesen, ohne die Suche zu verändern. Ihre Werte sind Zwischenstände vor dem Abbruch, keine erfolgreich zurückgegebenen Kandidaten.

Umgebung: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0.
Ein anfänglicher Importcheck zeigte: NetworkX fehlt. Alle drei Funktionen scheitern bereits vor dessen internem Import an ihren eigenen Assertions. Das fehlende Paket ist daher nicht die Ursache der gemeldeten Abbrüche. Die graph6-Ausgabe wurde nicht ausgeführt oder verifiziert.

## Ergebnisse

| Funktion | Tatsächlicher Ausgang | Gradverteilung | λ-Verletzungen auf Kanten |
| --- | --- | --- | ---: |
| generate_omega_conway | AssertionError bei Gradprüfung | 15 Knoten Grad 14, 84 Grad 4 | 0 von 273 |
| generate_tridecomp | AssertionError bei Gradprüfung | 99 Knoten Grad 2 | 0 von 99 |
| generate_randfill(seed=42) | AssertionError bei Gradprüfung | 91×14, 1×13, 5×12, 1×11, 1×10 | 684 von 684 |

### Ω

Der Code implementiert genau die bereits widerlegte Regel. H hat Grad 2 statt 12; die früher ermittelten 840 PH-Verletzungen bleiben bestehen. λ=1 auf den tatsächlich vorhandenen Kanten rettet den falschen Grad nicht.

### TriDecomp

Aus 33 disjunkten Dreiecken kann die Schleife keine erste Verbindung zwischen zwei Dreiecken einfügen: Ihre Endpunkte haben null gemeinsame Nachbarn, der Code verlangt genau einen. Innerhalb der Dreiecke fehlen keine Kanten. Somit bleibt die Ausgangsmatrix unverändert, unabhängig von der Shuffle-Reihenfolge.

Die bloße Dreieckspartition ist vollständig implementiert und benötigt kein vollständiges STS. Das Problem ist die nicht funktionierende Ergänzung. Auch deren Gradsteuerung wäre unzureichend: zwölf neue Kanten pro u berücksichtigen bereits von anderen Schleifendurchläufen hinzugefügte Kanten und den Zielgrad von v nicht korrekt.

### RandFill

Der Code akzeptiert nur Kanten zwischen Knoten ohne gemeinsamen Nachbarn. Das Einfügen der Kante erhöht die Zahl ihrer gemeinsamen Nachbarn nicht: Die Endpunkte werden dadurch nicht zu gemeinsamen Nachbarn ihrer selbst. Die Behauptung im Originalkommentar „+1“ ist falsch.

Aus dem leeren Graphen entsteht folglich ein dreiecksfreier Graph. Jede vorhandene Kante hat λ=0. Selbst bei zufällig vollständig erreichtem Grad 14 wäre dies kein zulässiger λ-Kandidat. Der zweite Durchlauf ergänzt nur Kanten, führt keinen Tausch aus und ist kein Backtracking.

Die im ersten Bericht aus der Prosainvariante abgeleitete Aussage „kein erster Schritt möglich“ trifft auf den tatsächlichen Code nicht zu: Er startet, verfolgt aber die falsche Bedingung. Diese Unterscheidung korrigiert die frühere Bewertung.

### compute_metrics

Die Funktion berechnet die vier vereinbarten Kennzahlen für die hier verwendeten ganzzahligen Matrizen korrekt. Für alle drei Zwischenstände stimmen ihre Ergebnisse mit einer unabhängigen Mengenrechnung aller ungeordneten Paare überein (audit.json). Das ist ein positiver geprüfter Befund; die Funktion selbst prüft keine Aufnahmebedingungen.

## Schlussfolgerung

Code wurde von Mistral bereitgestellt und ist nun prüfbar. Er wurde ehrlich als nicht ausgeführt bezeichnet. Seine eigenen Grad-Assertions verhindern bei allen drei Versuchen die Rückgabe eines unzulässigen Graphen. Die Generatoren sind dennoch mathematisch nicht erfolgreich; null Kandidaten aufgenommen.

Die faire Rückmeldung lautet: Übertragungsproblem behoben, Code vorhanden, Metrikfunktion bestätigt, drei Generatoren scheitern an konkret nachgewiesenen Konstruktionsfehlern. Aussagen über kostenlose Zugänge oder allgemeine Modellfähigkeiten folgen daraus nicht.

Reproduktion: python3 audit_execution.py im Nachtragsverzeichnis (NumPy und SciPy erforderlich).
