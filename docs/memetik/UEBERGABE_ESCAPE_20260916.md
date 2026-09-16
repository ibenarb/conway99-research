# Übergabeprompt – Conway99 / Memetik / Escape
Stand: 16. September 2026

Bitte setze unsere Untersuchung zu srg(99,14,1,2) im bestehenden Forschungszweig fort. Arbeite auf Deutsch, mathematisch sorgfältig und ergebnisorientiert. Diese Datei ist zugleich die Zusammenfassung des abgeschlossenen Chats. Die referenzierten Rohdaten und Prüfungen sind bereits archiviert; beginne nicht erneut mit der KI-Kandidatensammlung oder der Wiederholung aller alten Tests.

## Projekt und verbindliche Quellen

Repository: https://github.com/ibenarb/conway99-research
Forschungszweig: memetik.
Gesicherter Ergebnisstand vor dieser Übergabe: f6cb34592f096704ba2e938510ded28e7ecb1aa0. Prüfe den aktuellen Branchstand und bewahre spätere Änderungen.

Lies zunächst AGENTS.md und docs/CONWAY99_COLLABORATION.md, danach:
1. results/memetik/escape_census_20260915/escape_office_REPORT.md
2. docs/memetik/ESCAPE_CENSUS_20260915_BEFUNDE.md
3. experiments/memetik/escape_0_1/PROTOCOL.md und die dortigen Operatoren/Gründer.
4. data/memetik/ai_candidates/INDEX.md und registry.json bei Bedarf.
5. docs/memetik/GRUENDERVERTRAG.md für die harten Aufnahmebedingungen.

Die Dateien unter docs/memetik/pilot_0_3/ dokumentieren einen früheren Plan. Sie sind kein Nachweis eines bereits durchgeführten Piloten 0.3 und müssen im Licht der neueren Escape-Befunde gelesen werden.

## Bisherige Ergebnisse und Archiv

Der Office-Populationspilot 0.2.0 endete regulär mit PILOT_BUDGET_COMPLETE, Generation 10 und 16.561 abgeschlossenen Aufgaben. Seine Endpunkte waren nicht durchweg lokale Minima. Der gesonderte Escape-Versuch soll deshalb vor dem nächsten Populationspiloten klären, was die verwendeten Mutationen tatsächlich erreichen können.

Aus der externen KI-Kampagne wurden insgesamt 14 Graphen aufgenommen: zehn Codex, drei Claude und ein lokal erzeugter Gemini-Kandidat; acht Ω und sechs λ. Originalabgaben, Prüfberichte, Graphen und Herkunft stehen unter data/memetik/ai_candidates/. Verschiedene Graphen oder KI-Namen bedeuten noch keine unabhängigen Konstruktionsprinzipien oder Suchkomponenten. Mistral, Grok und Qwen lieferten in den geprüften Abgaben keine aufgenommenen Kandidaten. DeepSeek wurde vom Nutzer als erfolglos berichtet.

Der Office-Escape-Zensus escape-0.1.0 ist vollständig beendet:
- Acht Gründer, 20 Aufgaben über die jeweiligen Operatorfamilien.
- Alle 20 Aufgaben erschöpft; keine unvollständige Aufgabe.
- 940 zulässige Trades; etwa 32 Sekunden Wandzeit und 71,835 summierte Worker-CPU-Sekunden.
- Alle gespeicherten Verbesserungszeugen wurden rekonstruiert und ihre harten Bedingungen und Metriken geprüft. 28 kriteriumsbezogene Zeugen enthalten 18 unterschiedliche graph6-Hashes, keine nachgewiesenen 18 Isomorphieklassen.
- Die Wiederholung mit denselben Generatoren bestätigt Reproduzierbarkeit, nicht Vollständigkeit gegenüber beliebigen denkbaren Mutationen.

Vollständiges Archiv: results/memetik/escape_census_20260915/
Darin original.zip, Rohresultate unter escape_office_result/, Audit, Prüfskripte und eingefrorene Implementierung unter escape_build/.
SHA256 von original.zip: 3e675a35beb32342b47cfbfba2d811d1bec861a8c702a45b0deac68f17204832.

## Definitionen und Geltungsgrenzen

Für jedes ungeordnete Paar u<v gilt r_uv=(A²)_uv+A_uv−2.
W zählt r≠0; L1 summiert |r|; F summiert r².
Die verfeinerte Linf-Selektion minimiert lexikographisch (Linf,Nmax,L1), wobei Nmax alle Paare mit maximalem Absolutfehler zählt. Eine Verbesserung dieses Tupels muss Linf selbst nicht senken.

Harte Bedingungen: einfacher ungerichteter 14-regulärer Graph auf 99 Knoten; zusätzlich der jeweilige Armvertrag.
Ω: kanonischer Wurzelrahmen mit Matching C, Inzidenz P und PH=2J−(C+I)P.
λ: genau ein gemeinsamer Nachbar auf jeder Kante.
Ω allein garantiert nicht global λ=1.

Untersuchte Mutationen:
- Ω: implementierte 4x4-, 4x6- und 6x6-Produkttrades.
- λ: implementierte Apex- und Rotationstrades.
Alle Negativaussagen beziehen sich auf diesen Katalog und seine konkrete Implementierung. Tradegröße, Anzahl aufeinanderfolgender Schritte, Fehlerbarriere und Zusammenhangskomponente sind unterschiedliche Größen. Ein gefundener Weg liefert eine obere Schranke seiner minimalen Länge; Minimalität erfordert den vollständigen Ausschluss kürzerer Wege im definierten Suchraum. Unvollständige Suche ist kein Unmöglichkeitsbeweis.

## Wesentliche mathematische Befunde

**A_legacy:** Die gesamte erreichbare Komponente ist bereits untersucht: acht beschriftete Graphen, zwölf ungerichtete Übergänge, Übergangsstruktur Q3. Jeder Zustand besitzt genau drei 4x4-Nachbarn und keinen 4x6- oder 6x6-Nachbarn. Alle Übergänge bleiben innerhalb der acht Zustände.
A_legacy mit (W,L1,F,Linf,Nmax)=(2175,2718,3926,4,6) ist für alle vier Ziele eindeutig bester Zustand dieser Komponente.
Folglich gibt es unter diesen Operatoren keinen Verbesserungsweg irgendeiner Länge. Das ersetzt die frühere schwächere Aussage „mindestens drei Schritte“. Keine Aussage über alle Ω-Graphen oder die Existenz von srg(99,14,1,2)!
Zertifikat: escape_A_component_result.json; Erzeugung und unabhängige Kanten-/Normprüfung im selben Archiv. Acht beschriftete Zustände sind keine behaupteten acht Isomorphieklassen.

**B_original/W:** 277 direkte Nachbarn, alle W-schlechter, keiner W-neutral. Gleichzeitig existieren 106 unmittelbar F-verbessernde Trades. Lokalität ist normabhängig.

**HoG57338/F:** 46 direkte Nachbarn, alle F-schlechter; ebenso für W und L1. Zwei verbessern das Linf-Tupel, ohne Linf selbst zu senken.

**Codex_C08/W:** 66 direkte Nachbarn, darunter 33 W-neutrale und kein W-verbessernder. Die neutrale Komponente ist noch nicht vollständig untersucht. Für L1 und F ist der Start strikt lokal minimal.

**B_end_F, lambda_Linf2 und Codex_C02:** In allen vier Zielen unmittelbar verbesserbar. Zunächst normabhängige Abstiege durchführen, bevor diese als Escape-Ausgangspunkte bezeichnet werden.

Konkreter Ω-Fortschritt bei Codex_C02:
- Start: W=2074, L1=2506, F=3472.
- Bester gespeicherter W-Nachbar: W=2063, L1=2504, F=3490.
- Bester gespeicherter F-Nachbar: W=2083, L1=2498, F=3406.
Das sind unterschiedliche Graphen, kein gemeinsam erreichter Bestwertvektor.

Ein Apex-Nachfolger von Codex_C06 verlässt nachweislich die ursprüngliche feste Dreiteilung durch zwei innere Kanten. Das beweist weder das Verlassen jeder möglichen Dreiteilung noch die Erreichbarkeit einer exakten Lösung.

## Nächster Arbeitsauftrag

Setze das eigenständige Escape-Experiment vor dem nächsten Populationspiloten fort:

1. **A: Operatorerweiterung.** Keine weiteren Wanderungen innerhalb der abgeschlossenen Acht-Zustände-Komponente. Entwickle und prüfe einen erweiterten armerhaltenden Eingriff, der tatsächlich einen Zustand außerhalb dieser Komponente erreicht. Ein begrenztes exaktes Reparaturproblem mit SAT/CP-SAT oder größere, nicht auf die bisherige Produktform beschränkte Trades sind mögliche Ansätze. Schließe die acht bekannten Zustände explizit aus. Erfinde keine zusätzlichen Symmetrie- oder Schablonenbedingungen. Ein negatives Ergebnis eines begrenzten Fensters gilt nur für dieses Fenster.
2. **B_original/W und HoG57338/F:** Untersuche Wege zunehmender Länge mit zugelassenen zwischenzeitlichen Verschlechterungen. Ziel zunächst: ein Endgraph mit strikt besserem Zielwert als der Start. Dokumentiere Weglänge und maximale zwischenzeitliche Verschlechterung getrennt. Beanspruche Minimalität nur bei vollständiger Abdeckung aller kürzeren Wege.
3. **Codex_C08/W:** Untersuche zuerst die neutral erreichbare Komponente und ihre verbessernden Ausgänge. Ermittle, ob die 33 neutralen ersten Trades strukturelle Vielfalt liefern; verwechsle Zählungen beschrifteter Zustände nicht mit Isomorphieklassen.
4. **Direkt verbesserbare Gründer:** Führe standardisierte normabhängige Abstiege zu überprüften lokalen Endpunkten durch. Bewahre Herkunft, Zeugen und Zielkonflikte. Das ergänzt die Escape-Untersuchung und bereitet später den Populationspiloten vor.

Prüfe Operatoren nach jedem Schritt erneut: Eine am Start fehlende Familie kann später anwendbar werden. Nutze sichere Deduplikation; Isomorphiequotienten dürfen nur eingesetzt werden, wenn sie die relevanten Arm-/Rahmenbedingungen und die Vollständigkeit erhalten.

Beginne mit einem knappen Arbeitsplan und einer begründeten Reihenfolge nach erwarteter Aussagekraft und Aufwand. Entwickle dann die konkrete Fortsetzung einschließlich sinnvoller Ressourcenlimits, Checkpoints, expliziter Vollständigkeitsstatus und reproduzierbarer Zeugen. Überprüfe nur die konkret neuen Risiken; wiederhole nicht pauschal alle alten Tests.

## Ausführung und Zusammenarbeit

Office-Zielrechner rb-PC: acht logische CPUs, knapp 5 GiB RAM, circa 4,3 GiB zuvor verfügbar, 8 GiB Swap. Für den nächsten Lauf zunächst drei Worker mit Speicherkontrolle einplanen. Alle längeren Läufe müssen ein geschlossenes Terminal überleben und ihren Zustand atomar sichern.

Bestehende Office-Installation:
 /home/rb/conway99_workspace/conway99_escape_office_0.1.0/
Abgeschlossener Lauf:
 runs/census_20260915_202358
Release im Repository:
 releases/Conway99_Escape_Office_0.1.0.pyz

Es wurde im Zuge des Audits noch kein Folgelauf auf Office oder Ryzen gestartet. Die parallel laufende Ryzen-Symmetrie-/C2-Forschung nicht verändern oder stoppen.

Bereite Änderungen und ein geprüftes Folgepaket konkret vor. Gib mir bei manuellen Installations-/Startschritten jeweils nur einen Bash-Befehl ohne Zeilenfortsetzungen und warte danach auf meine Rückmeldung. Keine erneute allgemeine Rechner-Einrichtung, sofern kein konkretes Hindernis vorliegt.

Dokumentiere neue Befunde, Analyse, Schlussfolgerungen, Codeversionen und Zeugen auf memetik. Normale Git-Sicherungen sind bereits autorisiert; kein Force-Push und keine Löschung fremder Arbeit. Halte Originalabgaben unverändert und eigene Bewertungen getrennt.

Der spätere Populationspilot bleibt nachgeordnet. Seine Grundpopulation soll strukturell breit sein; ihre Breite muss gemessen werden. Der frühere Plan sah die drei Selektionen L1, F und das verfeinerte Linf-Tupel vor, W als zusätzliche Mess-/Archivgröße. Weitere Selektionsarme nicht stillschweigend hinzufügen. Die neuen Escape-Befunde sollen zuerst die Mutationsauswahl und die erreichbare Vielfalt begründen.
