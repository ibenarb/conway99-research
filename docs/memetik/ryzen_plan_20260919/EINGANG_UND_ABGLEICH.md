# Eingangsprüfung und Abgleich — 19.09.2026
## Was tatsächlich vorliegt
Das übergebene files (9).zip enthält genau zwei gzip-komprimierte JSON-Dateien: B_escape_W2082__bfs_W_boundary.json.gz und HoG57338__bfs_F_boundary.json.gz. Kein Reviewertext und kein neuer Reviewerprompt sind enthalten. Der vorhandene eigene Reviewerauftrag wurde erneut gelesen: docs/memetik/review_grossversuch_20260919/REVIEWERPROMPT.md, fixiert in Commit 958744f8b53ce66894a8b29e9bdfa033871574b0. Er ist ein Prüfauftrag, kein externes Urteil. Aussagen über Zustimmung/Widerspruch eines Reviewers sind daher derzeit nicht möglich. Bitte externen Review nachreichen, sofern dieser gemeint war.

Original byteidentisch auf eigenem Eingangszweig reviews/20260919-memetik-boundary-input, Commit 0ccc3c771aabd3582eac886036f8c2600159e2d4, unter reviews/20260919-memetik-boundary-input/original.zip. SHA256 19c53531d49f8c6cc82c2fb9524f441a5ef8fc7053b3ece34f83d27f276245f3, 208884 Bytes. Die branch-Anlage gelang über create_branch; ein vorausgehender update_ref-Versuch auf die noch nicht vorhandene Referenz wurde von GitHub mit 422 abgewiesen.

## Eigene neue Nachrechnung
Mit dem unabhängigen mengenbasierten Graphprüfer aus results/memetik/minimax_20260919/verify_results.py wurden alle gelieferten Randgraphen geprüft:
| Datensatz | Verschiedene beschriftete Randgraphen | Verschiedene angegebene Eltern | Kleinster Randwert |
|---|---:|---:|---:|
| B ab W=2082 | 3256 | 13 | W=2094 |
| HoG ab F=2836 | 2750 | 85 | F=2928 |

Einfachheit, Grad 14, Ω-Gleichungen bzw. λ-Bedingung und alle fünf Kennzahlen stimmen für sämtliche 6006 Randgraphen. Auch alle 98 verschiedenen angegebenen Eltern bestehen die Armprüfung und liegen im jeweiligen strikten Subniveau. Keine doppelten graph6-Einträge innerhalb eines Datensatzes. Die Dateien selbst melden frühere Stichproben von 42 bzw. 53 Randgraphen; das ist von unserer jetzigen vollständigen Kennzahlenprüfung zu unterscheiden.

Nicht neu geprüft wurden vollständige Erzeugung des Randes und Zugehörigkeit jeder Eltern-Kind-Beziehung zum Operatorkatalog. Diese Prüfung liefert deshalb keinen eigenständigen neuen Vollständigkeitsbeweis. Die Randminima sind konsistent mit den alten katalogbezogenen Untergrenzen B≥12 und HoG≥92. Die Dateien enthalten nicht den Endcheckpoint zur späteren HoG-Schranke ≥192 und bestätigen diese nicht unabhängig.

## Abgleich mit früheren Experimenten
- Der Office-Pilot lieferte einen λ-Linf=2-Zeugen und verbesserte alle elf B-Linien im jeweiligen Ziel, aber keine neuen Gesamtbestwerte in W/L1/F.
- Ω verbrauchte 55,50 von 63,10 Worker-CPU-Stunden; 1009 von 1020 geführten Ω-Versuchen verfehlten die Mindeststörlänge. Vollere CPU-Auslastung ersetzt keine effiziente Bewegungserzeugung.
- Crossover: 30 übernahmefähige Rückgaben bei 1020 Ω-Versuchen, darunter bekannte Strukturen. Das ist kein Beleg für 30 neue Klassen. Eine feste 20-%-Quote ist nicht gerechtfertigt.
- F02-Gründer C01–C05 bilden eine gemeinsame Konstruktionsfamilie. F03 ist ein Spezialfall von F04; zwei KI-Namen oder Generatorlabels garantieren keine Unabhängigkeit.
- Die dreiteilige λ-Liftvorlage selbst kann keine exakte Lösung enthalten. Deshalb muss die freie Suche nachweislich die feste Dreiteilung verlassen können. Symmetrieverlust allein belegt das noch nicht.
- A-Katalogkomponente geschlossen; C08 neutraler Ausgang; B echte Barriere; HoG ohne gefundenen Ausgang. Keine einheitliche Plateau-Erklärung.
- Die von mir zuvor empfohlenen 32→64 Plätze werden jetzt präzisiert: Ziel 64 verschiedene Gründer je Arm, in drei Zielinseln kopiert. Gleichverteilung über alle Generatornamen wäre wegen Qualitätsunterschieden und Verwandtschaft nicht sinnvoll.

## Rekonstruktion Kandidatenkonstruktion
Kontextsuche zum Chat vom 18.09.2026 ergab Option 1 und G1–G4: Kantenaufbau mit höchstens einem gemeinsamen Nachbarn für vorhandene Kanten; Randmatchings; äußere Dreiecke; begrenztes λ-Überschussbudget. Spätere K66-Anregung: lokale Anschlussmuster als Vorlagen, globale Ausschlussannahmen freigeben. Abruf liefert Ausschnitte, keinen vollständigen Chat oder neue getestete Generatoren. Diese Herkunft wird nicht mit implementierten Resultaten verwechselt. Eine widersprüchliche Suchzusammenfassung setzte Option 1 mit unserer Strategie B gleich; das ist nicht übernommen: Konstruktionsoption und Suchsteuerung sind verschiedene Dinge.

## Selbstkorrektur und Priorität
Der frühere Voruntersuchungsplan war als Rahmen sinnvoll, aber für den Ryzen noch zu unbestimmt. Jetzt werden Ausgangsquoten, Auswahl, Fluchtschwellen, tatsächliche Zuglängen und CPU-Zuteilung explizit festgelegt. Es sind überprüfbare Startparameter, keine ermittelten Optima. Exakte lange Minimax-Suchen werden nicht je Individuum vervielfacht. Der beigefügte RYZEN_PLAN.md ist eine eigene, vorläufige Planung ohne externen Review-Konsens.

