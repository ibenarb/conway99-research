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
| ENC | Jede mathematische Lösung erweitert sich auf eine erfüllende CNF-Belegung. | L4, Produkt- und Zählkodierungen, konkrete Generatoren | Für die gehashte Basis F0 und F46/F346 HERGELEITET; alle 4.746 Gleichungsaufrufe und Formelhashes NEU GEPRÜFT. Andere historische Kern-/Formelbindungen bleiben gesondert offen. Siehe ENCODER_ADAEQUANZ.md. |
| P46 | Alle Profile mit Graden ausschließlich 4 und 6 sind ausgeschlossen. | ENC, C4, 2.170 Fälle | Censusvollständigkeit, alle Formelhashes und Belegzuordnungen NEU GEPRÜFT; Schluss HERGELEITET unter den ÜBERNOMMENEN historischen Checkerprüfungen. Kein neuer Replay; 2.170 externe Beweise nicht neu gelesen. |
| C4 | Der gegenseitige Ankergraph des uneingeschränkten C2-Modells ist C4-frei. | ENC, F0 plus acht Units, historisches Zertifikat, L5 | Formelbindung an F0, alle 105 Transporte, Proofhashes und Checkerbeleg NEU GEPRÜFT; Schluss HERGELEITET unter der ÜBERNOMMENEN historischen Checkerprüfung. Kein neuer Replay. |
| CEN | Der Census enthält genau einen Vertreter jeder S7-Bahn schleifenfreier Pfeilgraphen mit Ausgraden in {3,4,6}, mindestens einem Grad 3 und C4-freiem gegenseitigem Graphen. | Strukturprüfung, unabhängige Isomorphieprüfung und vollständige beschriftete Zählung | NEU GEPRÜFT: 7.388.648 Bahnen, 37.030.041.152 beschriftete Graphen; Zählargument in CENSUS_VOLLSTAENDIGKEIT.md. Die mathematische Zulässigkeit der Filter gehört getrennt zu P46/C4. |
| LINK | Rest234691 ist eine unveränderte Teilmenge des Originalcensus; Rest218 eine unveränderte Teilmenge davon. | Drei gehashte Originaldateien | NEU GEPRÜFT vollständig; keine exakte Komplementbildung beansprucht. |
| COV | Historische Ausschlüsse lassen genau die jeweils angegebene Restmenge übrig. | ENC, L5, L9, konkrete Muster und Belege | Census bis Rest234691: exakte Komplemente, alle Muster-/Formelbindungen und 1.373 Belegdatensätze NEU GEPRÜFT; historische Checkerprüfungen ÜBERNOMMEN. Auch nachfolgende Übergänge bis Rest218 mit zwei Verfahren und vier Formel-/Checkerbindungen NEU GEPRÜFT; siehe späten Audit. |
| R218 | Alle 218 Schlussprofile sind unter F346 abgedeckt. | Gemeinsame Basis, 42 Units, frühere Checkerbelege | Abschlussaudit ÜBERNOMMEN: vollständige Metadaten-/Formelrekonstruktionsprüfung; keine Wiederholung aller Checker. |
| H346 | Kein Modell hat alle sieben Ankergrade in {3,4,6}. | ENC, P46, C4, CEN, COV, R218 | HERGELEITET unter den gebundenen historischen UNSAT-Prüfungen und dem übernommenen R218-Abschlussaudit; vollständige Mengenverknüpfung bis Rest218 NEU GEPRÜFT. Kein neuer Proof-Replay. |
| LOW | Die acht lokalen Typen eines Minimumankers mit d≤2 sind ausgeschlossen. | L7; uneingeschränkte Basis F0 | OFFEN; keine vollständige frühere Ausschlusskette gefunden. |
| C2 | Es gibt keinen solchen Graphen mit Involution. | L1–L8, H346, LOW | OFFEN. |

## Arbeitsfolge

1. **Frühes Strukturreview:** L1–L7, genaue Censusfilter und logische Reichweite von H346/LOW.
   Der Reviewer soll einen fehlenden Fall oder eine unzulässige Kombination aktiv suchen.
2. **Eigene Fortsetzung:** Nach der neuen Bindung von ENC für F0/F46/F346 und C4/P46
   sind auch die weiteren Coverage-Übergänge bis Rest218 gebunden. Schwerpunkt jetzt LOW.
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

## Fortschritt nach dem ersten Reviewauftrag

Der am Forschungscommit `7dbacd7eed56e2bf73b3aa5f2648f00e5484adfa` festgeschriebene
Reviewauftrag ist laut Ralph seit 12.10.2026, 14:43 Uhr in Arbeit. Seine Referenz
bleibt unverändert. Die eigene Fortsetzung zu ENC/C4/P46 steht unter
[Filter- und Belegkette](../c2_filter_audit_20261012/FILTER_UND_BELEGKETTE.md) und
[Encoderadäquanz](../c2_filter_audit_20261012/ENCODER_ADAEQUANZ.md). Sie beansprucht
noch keine Bestätigung durch diesen Reviewer.
