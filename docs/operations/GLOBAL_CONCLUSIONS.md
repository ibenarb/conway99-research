# Global conclusions: lernende Betriebs- und Forschungsregeln

Version 1.0, 28.09.2026. Ziel: Fehlerklassen verhindern, nicht nur einzelne
Fehlerstellen reparieren. Nutzerpräferenzen stehen in ../EXPERIMENT_RULES.md.

## Register

| ID | Belegter Anlass | Übergreifende Regel | Regression / Anwendung |
| --- | --- | --- | --- |
| GC-01 | λ-Vergleich 21./22.09.: Gast-monotonic und UTC differieren um 2979,15 s; Ursache im damaligen Bericht ausdrücklich ungeklärt. | Uhren und Intervalle getrennt protokollieren. Keine Throughput-/Speedup-Aussage aus unvalidierter Gastzeit. | Reale Hostuhr plus parallele interne CPU-/proc-/wait4-Messungen; Drift melden, nicht still skalieren. |
| GC-02 | Reparaturpilot 27.09.: +1,171611 s gegenüber Reservierung, +0,171611 s gegenüber Aufgabenstunde; vollständige CPU-Belege; globaler Stopp. | Betriebsabweichung von Abrechnungsverlust trennen. Lokales Budgetende darf gesunde Aufgaben nicht stoppen. | Absichtlich verzögerter Worker unter paralleler Last; lokale Warnung und vollständige Abrechnung, andere Worker arbeiten weiter. |
| GC-03 | Profil 27.09.: SQLite-Journal verschwand zwischen is_file und stat und beendete den Controller. | Überwachung muss mit regulären Zustandswechseln umgehen. Nur den konkret harmlosen Fehler behandeln. | FileNotFoundError beim temporären Journal simulieren; PermissionError bleibt sichtbar. Vorhandener Profil-Regressionstest. |
| GC-04 | Derselbe Profil-Audit: zwei CPU-Abfragen erzeugten 6 µs Differenz; 1 µs Prüftoleranz zu eng. | Gleiche Messung einmal erfassen und mehrfach verwenden; numerische Vergleichstoleranz von Betriebsbudget trennen. | Ein Zeit-Snapshot für Ledger und Receipt; veröffentlichte millisekundengroße Rundungstoleranz ohne Budgetverdeckung. |
| GC-05 | Profilbericht: lange k-Zellen erreichen Budget vor 300 Episoden; frühere Prognose war zu optimistisch. | Extremfälle und Modellaufbau in Kalibrierung aufnehmen; Budgetabschluss ist nicht Aufgaben-/Episodenabschluss. | Größe/Arm, Modellbau, Nachlauf, Durchsatz und offene Arbeit getrennt berichten. |
| GC-06 | Reparaturpilot-Status meldete am Phasenwechsel null Worker; status las nur diesen gespeicherten Bericht, während zwölf Worker liefen. | Status ist eine datierte Momentaufnahme, keine Prozessabfrage. Bedienung muss diesen Unterschied sichtbar machen. | Sofortiger Status nach erstem Startblock, Hostzeit im Bericht, dokumentierter Prozesscheck. |
| GC-07 | Reparatur 1.0.1: erster Cloud-Test sah eine gelöschte Sitzungsdatei erneut; Wiederholung in temporärem Verzeichnis bestand. Ursache nicht abschließend profiliert. | Umgebungseffekt nicht mit Produktionsfehler verwechseln; fehlgeschlagenen Test offenhalten und kontrolliert isoliert wiederholen. | Testdaten außerhalb synchronisierter Flächen, echte Zielhardware weiterhin separat prüfen. |
| GC-08 | λ-Radius/Profil: kein besserer Punkt in begrenztem Katalog/Budget; kleine Piloten und Herkunftslinien erlauben keine globale Landschaftsaussage. | Aussageumfang an tatsächlich geprüftem Raum und Budget binden. Rekord, Mechanismusnachweis und Konvergenz unterscheiden. | Im Bericht gelöste/offene Aufgaben und Zertifikatsstatus verpflichtend getrennt. |
| GC-09 | Aktueller Nutzerentscheid 28.09.: früher technischer Fehllauf soll nicht mit einer Wiederaufnahme vermischt werden. | Reparatur oder Neustart nach Restnutzen und Nachvollziehbarkeit entscheiden, nicht wegen versunkener Rechenkosten. | Fehllauf archiviert, neuer Lauf neue Kennung/Konten; gleicher wissenschaftlicher Input separat nachgewiesen. |

## Primärquellen im Repository

- GC-01: `docs/memetik/lambda_results_20260922/SUMMARY.json`
  und `docs/memetik/lambda_synthesis_20260922/ABGLEICH_UND_LAUFVORSCHLAG.md`.
- GC-03/04/05: `docs/memetik/lambda_profile_20260927/recovery/DIAGNOSE.md`
  und zugehörige `TEST_RESULTS.json`.
- GC-02/06/07/09: `docs/memetik/lambda_repair_restart_20260928/DIAGNOSE.md`
  und die dortigen Audit-/Testbelege; ausdrücklicher Nutzerentscheid im Chat
  „Memetik Neuer Pilotversuch“, 28.09.2026, 07:58–08:02 MESZ.
- GC-08: `docs/memetik/lambda_repair_pilot_20260927/PLAN_V2.md` und
  `FORTSETZUNG_RYZEN_LAMBDA_REPAIR_20260927.md` im selben Verzeichnis.

## Ältere Hinweise: noch keine hier erneut geprüften Primärbelege

Die Kontextsuche findet außerdem einen Windows-/WSL-Guardabbruch vom 17.09.,
einen als Fehler behandelten SIGALRM-Zeitstopp vom 19.09., gelöschte partielle
LRAT-Dateien bei einer älteren Recovery und die erneute Bearbeitung eines
bereits zertifizierten Typs Anfang September. Diese Hinweise begründen
weitere Prüfaufträge, aber die damaligen Rohbelege wurden für dieses Register
nicht erneut gelesen. Exakte Zahlen daraus werden hier nicht als neu
auditierte Tatsachen ausgegeben. Regeln: lokale Fehlerisolation, Artefakterhalt,
Fallregister vor Kampagnen und Trennung wissenschaftlicher/technischer Erfolge.

## Pflegeprozess

1. Vor einer Kampagne relevante GC-IDs und prüfbare Akzeptanzkriterien nennen.
2. Nach einem Vorfall zuerst Rohbelege sichern; Ursache und Vermutung trennen.
3. Kleinsten reproduzierbaren Fehlertest erstellen, dann Implementierung ändern.
4. Testresultat und Grenzen speichern; Zielhardwaretest separat kennzeichnen.
5. Eintrag hier aktualisieren und Regel in Starter/Template/AGENTS verankern.
6. Fortsetzungsprompt enthält fixierten Commit, aktive Regeln und offene Tests.

Nicht jeder Fehler rechtfertigt neue globale Komplexität. Nur wiederkehrende
oder folgenreiche Mechanismen werden zu allgemeinen Regeln. Veraltete Regeln
werden mit Begründung ersetzt, nicht kommentarlos weitergeschleppt.

## Ergänzung aus dem abgeschlossenen Reparaturpiloten, 28.09.2026 abends

- **GC-10 — Kalibrierung ist kein Aufgabenabschluss.** In1.1.0 wurden zwei Kalibrierungsversuche nach60 statt3600 CPU s als endgültig geschlossen markiert. Graph-/CPU-Audit bestand trotzdem. Regel: Versuch, Aufgabe und Planerfüllung separat prüfen.1.2.0 entfernt den unbedingten CPU_TARGET-Abschluss; Audit weist CPU_LIMIT_UNKNOWN mit>=5 Restsekunden zurück. Regression durchläuft kurze Kalibrierung, Hauptsuche und Pause/Resume mit echten Prozessen. Belege: docs/memetik/lambda_repair_night_20260928.
- **GC-11 — Budgetprojektion ist keine erwartete Fertigstellungszeit.**12–16h prognostiziert, tatsächlich5h03; viele Fenster früh beendet. Alte ETA zog laufende CPU nicht ab und berücksichtigte die letzte Aufgabenwelle unzureichend. Regel: aktive Arbeit abziehen, längste Restaufgabe berücksichtigen, frühzeitige Solverabschlüsse als unsichere Größe benennen.1.2.0 korrigiert Projektion; keine Garantie von Restlaufzeiten.
- **GC-02 Zielhardwarebeleg:**1.1.0 lief ohne globale Unterbrechung durch,52 dokumentierte weiche Zielwarnungen (inklusive2 absichtlicher Vorabtest-Verzögerungen), keine harten lokalen Budgetüberschreitungen. Dies bestätigt die Nachlauftoleranz, nicht vollständige Planerfüllung oder Langzeitstabilität aller Gastuhren.

## Zielhardware-Abschluss 1.2.0, 29.09.2026

GC-02/10: Vollständiger Neustart mit144 Aufgaben,51 verbuchten weichen Warnungen und ohne harte Überschreitungen abgeschlossen. Beide zuvor falsch geschlossenen Kalibrierungsaufgaben wurden weiterbearbeitet. GC-11: letzte Restzeitprojektion etwa11min17 gegenüber knapp10min tatsächlicher Restzeit. GC-08: doppeltes Budget erzeugte zwei weitere lokale Solveroptima, aber keine neue Graphklasse gegenüber1.1.0; alle48 großen Fenster bleiben UNKNOWN. Betriebserfolg und mathematischer Fortschritt getrennt bewerten. Belege: docs/memetik/lambda_repair_results_20260929.

## GC-12/13 — Review-Abgleich, 29.09.2026

**GC-12: Kontrollversuche brauchen erreichbare Störungen.** Der vorgeschlagene SRG-Rückkehrtest über gültige Sternzüge kann nicht starten: Fürλ=1 undμ≥2 existiert keine nichttriviale Sternneupaarung am exakten Zielgraphen. Vor Laufzeitplanung Erreichbarkeit, Invarianten und mindestens eine echte Störung prüfen. Nichtanwendbarkeit ist kein negatives Messergebnis. Einzelneλ-Defekte±1 bei festem Grad14 sind zudem durch Dreieckszählung ausgeschlossen. Beweis und9er-Rookkontrolle: docs/memetik/lambda_review_20260929.

**GC-13: Operatornamen ersetzen keinen Katalogvergleich.** FrühereC3-Züge auf neun Knoten aus drei disjunkten Dreiecken unterscheiden sich von Sterndreierzyklen mit gemeinsamem Zentrum. Ein negativer VergleichP/PC darf nicht still gegen den neuen Sternkatalog verwendet werden. Neue Operatoren durch gelöschte/ergänzte Kanten und Zulässigkeitsbedingungen identifizieren.
