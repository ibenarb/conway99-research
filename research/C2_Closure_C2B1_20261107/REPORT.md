# Vollständiger C2B1-Abschlussprüfer – geprüfter Forschungskandidat

7. November 2026. Implementiert und unabhängig begutachtet. Noch kein neuer vollständiger realer C2B1-Fallabschluss und keine Produktionsfreigabe.

## Aufgabe und Beweisaussage

Der vollständige Modus akzeptiert nur eine Belegsammlung, die jeden Rand des geprüften vollständigen Randpakets genau einmal abdeckt. Er verbindet die eingeschränkten C2B1-Einzelbelege mit dem globalen Minimalrandargument. Unbeschränkte C2S2-Belege dürfen ausdrücklich mitverwendet werden: Unlösbarkeit des ursprünglichen Randproblems impliziert Unlösbarkeit seiner eingeschränkten Teilmenge. Format, Status und konkrete Randmasken bleiben dabei erhalten.

Ein erfolgreiches vollständiges Audit würde die Unlösbarkeit des lokalen Matrixvertrags für genau den genannten Katalogfall belegen. Die bekannte Reduktion auf diesen notwendigen Vertrag und die vollständige Klassifikation der 62 Fälle werden nicht neu bewiesen. L62 und insbesondere C2 werden durch einen einzelnen Fall nicht abgeschlossen. Archivprüfung, Git-Dokumentation und unabhängige Freigabe bleiben vor einer globalen Zählung erforderlich.

## Was neu geprüft wird

1. Die Originalmatrizen D/G/K werden direkt aus den fest gepinnten Katalogdaten neu aufgebaut. Die reine Python-Rekonstruktion wurde für alle 62 Katalogeinträge gegen die vorhandene NumPy-Spezifikation verglichen.
2. Jede vollständige Zeilendomäne wird erneut durch die Komponentenaufzählung disjunkter Pfade und Zyklen erzeugt und mengenweise mit der Modelleingabe verglichen. Es wird ein vollständiger Enumerator erneut ausgeführt, nicht zwei.
3. Die Type-I-Randvoraussetzungen werden aus dem konkreten Modell geprüft. Daraus folgt die exakte Komplementbedingung für die Supports a∪P(a) und b∪P(b) in der 40-elementigen zulässigen Spaltenmenge. Eindeutige gültige geordnete Paare werden gegen eine unabhängig berechnete Gesamtzahl geprüft; kein Teilen durch zwei.
4. Jeder konkrete Transport, sämtliche verwendeten gekoppelten Aktionen, reine Zeilentausche, die Zusammensetzung g_col∘sigma_col, die Randminimalität und die S2-Erhaltung werden geprüft. Die Aktionsdatei muss genau diesen geprüften Abbildungen entsprechen.
5. Manifest und Einzelbelege sind an Fall, Randindex, konkrete Masken, Modell, Aktionsdateien und die genaue Einschränkungssemantik gebunden. Gleichheit in image>=a ist ausdrücklich erlaubt.
6. Jeder Beweis wird in einen privaten Snapshot übernommen und mit dem fest zugelassenen unabhängigen Prüfer frisch nachgespielt. Vorhandene PASS-Logs oder Controllerzähler ersetzen keine Prüfung. Header, Index, vollständiges EOF und jede native Quittung müssen passen.
7. Vor Abschluss werden die Eingaben und Originalbelege nochmals auf unveränderte Hashes geprüft. Manifesthash und Manifestverarbeitung stammen aus demselben Bytepuffer; gespeicherte Proofbytes werden einmal gelesen, gehasht, gesichert und aus genau diesen Bytes entpackt.

## Drei strikt getrennte Modi

- complete: sämtliche Originalränder erforderlich; erst nach vollständigem mathematischem Audit und vollständigem frischem Replay ist PASS mit case_proved_unsat=true möglich.
- subset: vollständiges mathematisches Modellaudit, aber nur angegebene Belege nachprüfen; Ergebnis immer NONCLOSING_SUBSET und case_proved_unsat=false.
- structure: vollständiges mathematisches Modellaudit ohne Belegabschluss; Ergebnis immer NONCLOSING_STRUCTURE.

Der Standard ist complete. Kein Modus verändert Ledger, Produktionscontroller oder T 20-Einstellungen.

## Reale Ausführung

Die endgültige Fassung wurde über run_closure.py am vollständigen Modell von Fall 20 geprüft:

- zwölf erneut vollständig geprüfte Zeilendomänen;
- 289536 geordnete gültige Randpaare;
- 36288 minimale Randvertreter;
- acht verwendete gekoppelte Gruppenaktionen;
- 17 frisch geprüfte reale Belege, davon ein ursprünglicher C2S2-Beleg und 16 eingeschränkte C2B1-Belege.

Ergebnis: NONCLOSING_SUBSET, case_proved_unsat=false; 36271 Randbelege fehlen in dieser Forschungssammlung. Der überwachte Lauf dauerte 32,61 Sekunden. Eine frühere begutachtete Fassung bestand denselben Test in 33,18 Sekunden; dies ist keine Geschwindigkeitsmessreihe.

Der vollständige Modus weist genau diese echte Sammlung sowohl direkt als auch über den überwachten Einstieg als INCOMPLETE zurück. Es wurde kein vollständiger realer Fall mit C2B1 als PASS abgeschlossen. Der positive vollständige Indexmengentest ist ausdrücklich nur ein synthetischer Test der Manifestfunktion, kein Ersatz für einen vollständigen realen Auditlauf.

## Fehlerkontrollen

23 Manifest-, Snapshot- und Vollständigkeitskontrollen bestanden. Dazu gehören falsche Fälle, Kontexte, Randmasken, Statuszuordnungen, Formate, Hashes, doppelte Indizes/Pfade, fehlende Ränder, Pfadausbruch und ein echter unvollständiger Abschlussaufruf.

Neun gezielte mathematische Fehler wurden vom echten Validator an der erwarteten Stelle abgewiesen: geänderte Matrix, verkürzte Domäne, falsche Aktionskomposition, ungültige S2-Permutation, ungültige alte Aktion, fehlende oder doppelte Coverage, falscher Transport und ein nichtminimaler Vertreter. Beim letzten Test wurden die Transporte korrekt mitangepasst; gerade deshalb musste erst die Minimalitätsprüfung scheitern. Nur innerhalb dieses Tests wurde die tatsächliche vollständige Komponentenaufzählung nach exakten Argumenten memoisiert; keine Domänen oder PASS-Ergebnisse wurden simuliert.

Fünf zusätzliche Kontrollen des Einstiegs bestanden: doppelte JSON-Schlüssel, bestehendes Ausgabeziel, belegte Forschungssperre, Ressourcenhalt und echte unvollständige Sammlung. Nur der Ressourcenmangel wurde simuliert; dabei durfte kein Prozess starten.

## Ressourcen und Vertrauensanker

run_closure.py ist der überwachte Einstieg aus dem begutachteten Quellensatz. Er hält die bestehende Forschungssperre, überwacht Host-/WSL-Speicher, freien Plattenplatz und Swap und beendet bei Fehlern die Prozessgruppe. Elternbindungen verhindern verwaiste Prüfer. Native Prüfschritte bleiben zeitlich und im Speicher begrenzt; der gesamte vollständige Audit hat kein kumulatives 180-Sekunden-CPU-Limit. Der Fortschrittswächter erhält auch während des abschließenden Hashabgleichs Meldungen über tatsächlich abgeschlossene Prüfungen. Die Priorität wird auf mindestens nice 15 gesetzt, nicht additiv zweimal erhöht.

Katalog und native Prüfer sind durch feste Hashes im Gate zugelassen. Die lokalen Auditorquellen sind zusätzlich gebunden. Voraussetzung bleibt ein von außen vertrauenswürdig bezogener, begutachteter Quellensatz: Selbstbindung ersetzt keinen externen Versionsanker. Nicht beliebige gleichnamige Programme aus einem ungeprüften Bundle starten. Die Veröffentlichung beziehungsweise das bytegeprüfte Archiv bindet den Quellensatz und die Referenzbelege.

## Noch offen vor Produktion

Der erste vollständige reale Abschlusslauf mit allen benötigten Belegen fehlt. Ebenso fehlen die Integration in den Produktionscontroller, neue unveränderliche Fallverträge und deren vollständige Wiederanlaufprüfung. Der neue Gate ist als Forschungskandidat geprüft; er wird nicht stillschweigend in einen laufenden oder bereits versiegelten Fall eingesetzt.

Quellen: closure_gate.py, mathematical_audit.py, row_domains_complete.py, run_closure.py, resource_sensor.py. Belege: CONTROLS_FINAL.json, MATH_MUTATIONS.json, LAUNCHER_CONTROLS.json, MATRIX_CROSSCHECK.json und final_guarded_subset/audit/FINAL_AUDIT.json.
