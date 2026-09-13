# Analyse der Befunde

Stand: 13. September 2026. Die folgenden Deutungen sind von den [Befunden](BEFUNDE.md) getrennt.

## Suchleistung

Unveränderte Gesamtbestwerte verdecken Linienfortschritte. Der Linf=2-Zeuge belegt, dass die getrennte Minimax-Variante einen anderen relevanten Fehlerzustand erreicht. Er ist nach den drei übrigen Kennzahlen schlechter als HoG 57338. Eine allgemein bessere Nähe zur Lösung ist nicht bewiesen.

B ist entwicklungsfähig: Seine starken konzentrierten Fehler lassen sich abbauen. Dabei kann die Zahl falscher Paare wachsen. W, L1, F und Linf beschreiben verschiedene Eigenschaften; keine dieser Größen ist ein nachgewiesener Abstand in zulässigen Mutationen.

## Engpass

Das gemeinsame 30-CPU-Sekunden-Budget für Störung und Abstieg führte bei Ω zu stark verkürzten Ausflügen. Der ältere separate Kostenpilot lokalisiert die teure Mutationserzeugung; der volle Lauf bestätigt deren praktische Folgen. Eine bloß schnellere Scoreberechnung oder eine längere konfigurierte Störlänge genügt nicht.

Ein eigener Abstiegsrahmen hilft nur, wenn die Störung tatsächlich ausgeführt wurde. Ein wegen Ressourcen-/Versuchsbudget abgebrochener langer Ausflug darf nicht als erfolglos getesteter vollständiger langer Ausflug gezählt werden.

## Vielfalt

64 nichtisomorphe Starter aus zehn Gründern und 142 protokollierte Endklassen über drei Normvarianten sind keine 142 unabhängigen Einzugsgebiete. Dieselben Gründer können viele Nachfahren erzeugen. Umgekehrt beweist das Feststehen einer Linie weder ein lokales Minimum noch einen unüberwindbaren Suchbereich.

Neue Konstruktionsprinzipien bleiben deshalb sinnvoll. Eine größere Population allein kann bei gleichem Budget die Bearbeitung jeder Linie verkürzen. Die Zahl neuer KIs oder Zufallsseeds ersetzt keine Strukturprüfung.

## Rekombination und Flucht

Cross-over kann vorhandene andere Gründer reproduzieren. Ausrichtung und zusätzliche Reparaturmöglichkeiten sind getrennt von reiner Elternkantenmischung zu betrachten. Der aktuelle Befund rechtfertigt einen begrenzten Cross-over-Anteil und genaue Erfolgszählung, kein allgemeines Verbot.

Eine Folge mehrerer Mutationen, ein einzelner langer alternierender Kreis und ein gekoppelter Ω-Trade sind verschieden. Grade allein garantieren weder λ noch P-Margen. Für minimale Fluchtweiten ist eine separate vollständige kleine Nachbarschaftsuntersuchung nötig; der produktive Zufallsgenerator liefert keinen solchen Nachweis.
