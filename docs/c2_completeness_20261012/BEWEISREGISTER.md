# Beweisregister und Prüfprogramm

Stand 12.10.2026. **LITERATUR** bedeutet geprüft verorteter veröffentlichter Satz;
**HERGELEITET** bedeutet hier ausgearbeitetes Argument, noch ohne unabhängiges Review;
**NEU GEPRÜFT** bezeichnet exakt die ausgeführte endliche Prüfung;
**ÜBERNOMMEN** bezeichnet frühere Ergebnisse mit benannten Beleggrenzen;
**OFFEN** bezeichnet eine noch zu erfüllende Beweispflicht.

| ID | Präzise Aussage | Abhängigkeit | Status und nächster Prüfpunkt |
|---|---|---|---|
| L1 | Jede Involution hat genau einen Fixpunkt. | MM04, Satz 1, S. 96 | LITERATUR; Originalsatz im Scan geprüft. Kein neu beanspruchter Beweis der gesamten Literaturklassifikation. |
| L2–L3 | Jeder C2-Graph besitzt den beschriebenen 14-Anker-/84-Außenknoten-Rahmen; 42 Außenorbits, keine Außenpartnerkante. | L1, λ=1, μ=2 | HERGELEITET im Manuskript. Reviewer prüft alle Orbitfälle und die Labelbijektion. |
| L4 | E1–E3 sind notwendig und hinreichend für das vollständige Rahmenmodell. | L2–L3 | HERGELEITET; Blockrechnung und binäre Voraussetzungen explizit. |
| L5 | C2 wr S7 wirkt semantisch; auf Ankerpfeilen genügt S7. | L4 und Definition der Pfeile | HERGELEITET; keine syntaktische Hilfsvariablensymmetrie behauptet. |
| L6 | Genau elf lokale Matchingtypen; d zählt Eins-Teile und liegt in {0,1,2,3,4,6}. | λ=1 und zulässiger Stabilisator | HERGELEITET; alle 10.395 lokalen Matchings zusätzlich NEU GEPRÜFT. |
| L7 | Minimumanker und anschließende Matchingnormalform sind gemeinsam zulässig. | L5–L6 | HERGELEITET; weitere historische Normalisierungen nicht pauschal eingeschlossen. |
| ENC | Jede mathematische Lösung erweitert sich auf eine erfüllende CNF-Belegung. | L4, Produkt- und Zählkodierungen, konkrete Generatoren | Allgemeine historische Encoderbeweise verortet; vollständige Implementierungs-/Formelbindung OFFEN. |
| P46 | Alle Profile mit Graden ausschließlich 4 und 6 sind ausgeschlossen. | ENC, frühere 2.170 Fälle und gültige Vorfilter | ÜBERNOMMEN; Formeln, Coverage und ursprüngliche Zertifikate in die Gesamtkette binden. |
| C4 | Der verwendete gegenseitige Vierzyklus ist unter der benötigten Basis unmöglich. | ENC, konkrete Formel und Zertifikat, L5 | Beweisarchiv und Hashes lokalisiert; genaue Formelstärke und globaler Transport noch zu auditieren. |
| CEN | Der Census enthält genau einen Vertreter jeder S7-Bahn schleifenfreier Pfeilgraphen mit Ausgraden in {3,4,6}, mindestens einem Grad 3 und C4-freiem gegenseitigem Graphen. | Strukturprüfung, unabhängige Isomorphieprüfung und vollständige beschriftete Zählung | NEU GEPRÜFT: 7.388.648 Bahnen, 37.030.041.152 beschriftete Graphen; Zählargument in CENSUS_VOLLSTAENDIGKEIT.md. Die mathematische Zulässigkeit der Filter gehört getrennt zu P46/C4. |
| LINK | Rest234691 ist eine unveränderte Teilmenge des Originalcensus; Rest218 eine unveränderte Teilmenge davon. | Drei gehashte Originaldateien | NEU GEPRÜFT vollständig; keine exakte Komplementbildung beansprucht. |
| COV | Historische Ausschlüsse lassen genau die jeweils angegebene Restmenge übrig. | ENC, L5, L9, konkrete Muster und Belege | Zahlensaldo NEU GEPRÜFT; mengen- und zertifikatsbezogene Kette teilweise ÜBERNOMMEN, Gesamtaudit OFFEN. |
| R218 | Alle 218 Schlussprofile sind unter F346 abgedeckt. | Gemeinsame Basis, 42 Units, frühere Checkerbelege | Abschlussaudit ÜBERNOMMEN: vollständige Metadaten-/Formelrekonstruktionsprüfung; keine Wiederholung aller Checker. |
| H346 | Kein Modell hat alle sieben Ankergrade in {3,4,6}. | ENC, P46, C4, CEN, COV, R218 | BEDINGTES ZIEL; nicht allein aus Restzahl null ableiten. |
| LOW | Die acht lokalen Typen eines Minimumankers mit d≤2 sind ausgeschlossen. | L7; uneingeschränkte Basis F0 | OFFEN; keine vollständige frühere Ausschlusskette gefunden. |
| C2 | Es gibt keinen solchen Graphen mit Involution. | L1–L8, H346, LOW | OFFEN. |

## Arbeitsfolge

1. **Frühes Strukturreview:** L1–L7, genaue Censusfilter und logische Reichweite von H346/LOW.
   Der Reviewer soll einen fehlenden Fall oder eine unzulässige Kombination aktiv suchen.
2. **Eigene Fortsetzung:** ENC mit den konkreten Generatoren schließen und C4/P46 sowie
   die einzelnen Coverage-Übergänge an ihre Basen, Muster, Listen und Zertifikate binden.
   Vor erneuten Rechnungen zunächst vorhandene historische Belege auswerten.
3. **Niedrige Grade:** Nach vorhandenen Ausschlüssen suchen; andernfalls präzise neue
   Lemmas oder endliche Restaufgaben entwickeln. Kein neuer Solverlauf ohne konkrete
   mathematische Beweispflicht und dokumentierten Geltungsbereich.
4. **Abschlussreview:** Erst nach Schließen aller für den beanspruchten Satz notwendigen
   offenen Punkte das gesamte Manuskript und das reproduzierbare Belegpaket prüfen lassen.

Das erste Review ist unabhängig von der weiteren Eigenarbeit. Reviewerresultate
werden mit Ausgangscommit, Originaltext, reproduzierbaren Prüfungen und eigener
Gegenprüfung archiviert; die Beauftragung bedeutet keine Übernahme eines Ergebnisses.

## Veröffentlichung und Belegzugang

Der öffentliche Entwurf erhält versionierte Quellen und kompakte Prüfberichte auf Git.
Die großen Census- und Beweisdateien werden über ein separates Manifest adressiert.
Ein Library-Bezeichner oder lokaler Maschinenpfad ist **kein öffentlicher Downloadlink**.
Vor einem Publikationsrelease müssen dauerhafte Bezugsstellen auf GitHub oder dem
Projektwebserver eingerichtet und aus einer unabhängigen Umgebung geprüft sein.
Aktuell ist hierfür keine konkrete öffentliche Serveradresse belegt.

Ein Release benötigt außerdem: endgültige Satzfassung, vollständig geschlossene
Abhängigkeitsliste, Literaturverzeichnis, reproduzierbare Formelerzeugung, vollständige
Abdeckung, nachvollziehbare Checker-Provenienz und einen festgeschriebenen Releasecommit.
Die Unveränderlichkeit historischer Belege und der Originalbeweise ist beizubehalten.
