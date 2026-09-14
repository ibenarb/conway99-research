# Prüfung der Mistral-/Vibe-Einreichung v01

Stand: 14. September 2026. Bezug: `original.md`, Prüfdaten in `audit.json`.
Ergebnis: **0 aufgenommene Kandidaten aus 6 eingereichten Datensätzen.**
Status **REJECTED_AS_SUBMITTED**. Kein allgemeiner Unmöglichkeitsbefund zu den vorgeschlagenen Suchrichtungen.

## Befunde

Das Original hat 18573 Bytes und SHA256 `fced622a4291180edbbbccc71f6ca479baacabc867cca490ecd4a8fac9897b94`.
Es endet nach der schließenden JSON-Klammer, ohne schließenden Markdown-Codezaun.
Generatoren G01–G06 und der geforderte separate Prüfer fehlen in der empfangenen Datei.
Ob die ursprüngliche Antwort länger war oder beim Kopieren abgeschnitten wurde, ist nicht festgestellt.

Der JSON-Inhalt ist mittels raw_decode ohne Änderung der Werte lesbar. Alle sechs graph6-Zeichenfolgen beginnen mit O: Der kurze graph6-Header kodiert damit 16 Knoten. Für 16 Knoten wären insgesamt 21 Zeichen erforderlich; geliefert werden 177, 172, 167, 167, 166 und 162 Zeichen. Die Angaben sind daher auch keine gültigen vollständigen graph6-Darstellungen von 16-Knoten-Graphen. Ein 99-Knoten-Graph benötigt gemäß vereinbarter Konvention den Header `~?@b` und 813 Zeichen ohne abschließendes LF.

Die gesetzten Flags order_99=true und regular_14=true sind nicht belegt; order_99 widerspricht den Daten unmittelbar. generated_unverified hebt diesen Widerspruch nicht auf. runtime=null entspricht nicht dem geforderten Objekt mit gegebenenfalls nullwertigen Komponenten. Scores und Prüfsummen fehlen. Der Text nennt sechs Kandidaten, zugleich zwei je Arm; tatsächlich enthält JSON drei je Arm. Keine Isomorphieprüfung wurde durchgeführt.

## Mathematische Analyse

| Familie | Befund |
| --- | --- |
| F01: elf K9-Blöcke | Jede innere Kante hat bereits sieben gemeinsame Nachbarn. Zusätzliche Außenkanten können diese Zahl nicht senken. Mindestens 396 Kanten verletzen λ=1. Die Konstruktion ist in dieser Form für λ ausgeschlossen. Die sechs äußeren Nachbarn sind zudem nicht konkret spezifiziert. |
| F02: J(14,2) plus acht universelle Knoten | Der Johnson-Grundgraph hat Grad 24. Nach Hinzufügen der acht universellen Knoten haben die alten Knoten Grad 32, die neuen bei wörtlicher Konstruktion Grad 98. Grad 14 wird verfehlt. |
| F03: Z99, D={1,…,7} | Die unabhängig aus diesem Rezept rekonstruierte Struktur ist einfach und 14-regulär. Jede ihrer 693 Kanten verletzt jedoch λ=1: gemeinsame Nachbarzahlen 6 bis 12, jeweils 99 Kanten. |
| F04: Z3 × Z33 | Konkrete Verbindungsmengen, vollständiger Generator und Nachweis des kanonischen Rahmens fehlen. Die Identitätspermutation allein belegt den Rahmen nicht. Keine ausreichende Definition für eine Reproduktion. |
| F05: Greedy | Keine ausführbare Regel für exakte Margen, Ergänzbarkeit oder Sackgassen. Teilbelegung und erfüllte Endgleichungen werden nicht sauber getrennt. Fehlende erzwungene Symmetrie beweist keine Asymmetrie. Die zusätzliche Nichtkantenbedingung ist eine unbegründete Einschränkung des gewünschten Ω-Suchraums. |
| F06: Zufall und Reparatur | Kein definierter Reparaturalgorithmus und kein exakter Ω-Zeuge. Ein approximativ erfüllter Ω-Vertrag reicht nicht. Das Konfigurationsmodell garantiert ohne zusätzliche Behandlung auch keine Einfachheit. |

Für F03 ergeben sich durch eigene direkte Mengenrechnung:
W=4752, L1=14058, F=66528, Linf=11.
Dies sind Werte des separat rekonstruierten Rezepts, **keine** Dekodierung oder Reparatur der eingereichten graph6-Zeichenfolge. Das Rezept wird nicht als zulässiger Gründer aufgenommen.

## Schlussfolgerung

Die Rückgabe ist derzeit eine Ideensammlung mit fehlerhaften Kandidatendaten, keine verwendbare Kandidatenlieferung. Die offene Angabe fehlender Ausführung ist angemessen; behauptete erfolgreiche Konstruktionen, gesetzte Wahrheitsflags und scheinbare Graphdaten sind dadurch nicht gerechtfertigt.

Die drei allgemeinen Suchrichtungen bleiben sinnvoll untersuchbar. Aus dieser Einreichung folgt jedoch weder ein neuer gültiger Gründer noch ein Vorteil der Vielfalt. F01 und F02 brauchen grundlegende Neukonstruktion; F03 braucht andere zulässige Parameter, deren Existenz hier nicht gezeigt wurde. F04–F06 brauchen konkrete Algorithmen.

Empfohlene Rückgabe an Mistral: Zunächst nur einen exakt definierten, prüfbaren Kandidaten oder einen vollständigen Generator liefern. Ohne Ausführung die Kandidatenliste leer lassen, statt Platzhalter-Graphdaten einzutragen. Zuerst F01/F02 korrigieren und das konkrete F03-Rezept als λ-Fehlversuch ausweisen. Danach gegebenenfalls das Portfolio erweitern. Falls ein Teil der Antwort fehlt, vollständige Datei nachreichen; das beseitigt die festgestellten mathematischen Fehler nicht automatisch.

## Reproduktion und Grenzen

Aufruf im Vorgangsverzeichnis: `python3 audit_submission.py original.md`.
Nur Python-Standardbibliothek erforderlich. Der Prüfer ist ein begrenztes Reproduktionsskript für diese Einreichung, kein allgemeiner Kandidatenvalidator. Er prüft die beobachteten Header/Längen, Metadaten und das F03-Rezept; die übrige mathematische Analyse steht oben. Es werden keine fremden Generatoren ausgeführt.

Ein optionaler Versuch, NetworkX in der Arbeitsumgebung zu importieren, scheiterte (Modul nicht installiert). Die berichteten Resultate wurden mit direkter Standardbibliotheksrechnung ermittelt; es wird keine NetworkX-Verifikation behauptet.

Die Einreichung wurde nur in der tatsächlich empfangenen Form beurteilt. Externe Literaturverweise und die selbst angegebene Modellversion wurden nicht verifiziert.
