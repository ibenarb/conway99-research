# Global conclusions: lernende Betriebs- und Forschungsregeln

Fortgeschrieben bis 04.10.2026 (Grundfassung 28.09.2026). Ziel: Fehlerklassen verhindern, nicht nur einzelne
Fehlerstellen reparieren. Nutzerpräferenzen stehen in ../EXPERIMENT_RULES.md.

**Aktueller Vorrang:** GC-19 und EXPERIMENT_RULES Version1.1 ersetzen frühere
Vorgaben, die allein bei ausgeschöpftem Zeitbudget einen automatischen
Abschluss/Stopp vorsahen. Historische Laufberichte und fixierte Pakete bleiben
als Belege unverändert.

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

## GC-14 — Ergebnisübergabe und dauerhafter Incumbent, 29.09.2026

Beim Zusammenbau von K1 lieferte ein neuer Katalog-Worker zunächst seinen besten
Graphen nur im Rückgabewert; der Controller bewertet und sichert dagegen best.json.
Vor Veröffentlichung durch Codeprüfung gefunden und behoben. Regel: Worker-API
muss sowohl die vollständige unabhängige Prüfung als auch das sofortige atomare
Speichern jeder Verbesserung festlegen. Eine erfolgreiche Funktionsrückgabe allein
belegt keine ausfallsichere Ergebnisübergabe. Regression: echter kurzer Suchlauf,
verbesserter Incumbent auf Platte, Pause/Neustart erhält ihn; gefälschter State wird
abgewiesen. K1-Integration prüft danach alle vier Familien samt Endabrechnung.
Belege: docs/memetik/lambda_k1_20260929/VALIDATION.json und zugehörige Kerneltests.
Status: im neuen K1-Paket umgesetzt; kein Befund über beschädigte ältere Läufe.

## GC-15 — Ungeordneter WSL-Neustart braucht getrennte Wiederanlaufkonten, 01.10.2026

K1 endete ohne Abschlussmeldung;336 Aufgaben/350 CPU-Receipts sind erhalten,
zwölf Worker-Endbelege sowie die Controller-/Hosthelfer-Endabrechnung fehlen.
Die aktuelle WSL-Instanz startete01.10.08:20:45; Ursache der vorigen Unterbrechung
unbekannt. Regel: RUNNING-Datei ist kein Lebenszeichen; offene Sitzungsmarker
nicht löschen und fehlende CPU nicht als Null buchen. Byteidentischen Vorgänger
sichern, neue Versuche mit neuen Konten kennzeichnen, abgeschlossene Aufgaben
übernehmen ohne sie erneut zu suchen. Bei gepaarten Vergleichen neue Vollversuche
mit originalen Hints; gerettete Zwischenstände separat halten. Alle30Hostsekunden
atomaren Heartbeat mit Boot-ID und live CPU schreiben; kein Ersatz für Endbelege.
Regression: Original unverändert, beschädigtes Archiv/Ledger abgewiesen,
bestehendes Ziel abgewiesen, korrekte336/12/172-Aufteilung und echte Kindprozesse
mit Pause/Wiederaufnahme. Belege: docs/memetik/lambda_k1_recovery_20261001.
Status: neuer Recovery-Abschnitt; Zielhardwarekontrollen vor Produktion.


## GC-16 — Begrenzte Enumeration ist keine erschöpfte Verzweigung, 01.10.2026

Der konstruktive Zeilenpilot 0.2.3 meldete bei Worker 1 nach 64
Zeile-16-Alternativen `ENUMERATED_SAMPLE_EXHAUSTED`, obwohl für jede
Zeile-17-Aufgabe lediglich das Limit von 4096 exakten Rohlösungen erreicht
worden war. Es lag weder ein exakter Widerspruch noch eine vollständige
Enumeration vor. Regel: Ein Lösungs-, Knoten- oder Zeitlimit markiert einen
Suchast ausschließlich als `LIMIT_UNRESOLVED`; es darf weder lokal noch
global als erschöpft behandelt werden. Wo billige notwendige
Fortsetzungsbedingungen bekannt sind, werden sie vor der Enumeration in das
Teilproblem eingebaut und anschließend unabhängig erneut geprüft. Begrenzte
Alternativen werden durch adaptive Erweiterung oder neue Suchreihenfolgen
ergänzt. Regression: absichtlich winziges Enumerationslimit muss
`LIMIT_UNRESOLVED` ergeben. Beleg:
`docs/memetik/row_constructive_20261001`.


## GC-17 — Starre Zeilenreihenfolge kann eine künstliche Tiefenbarriere erzeugen, 02.10.2026

Der konstruktive H-Zeilenpilot 0.2.4 erreichte in zwei unabhängigen Workern Tiefe 17.
Beide 17er waren gegen jede der jeweils 67 verbleibenden Zeilen exakt lokal maximal.
Die Frontierprofile zeigten jedoch bei Tiefe 16 noch jeweils drei exakt anschließbare
Zeilen. Für worker02 führte die starre nächste Vollzeile 32 in die Sackgasse, während
die dynamische Wahl 68 gefolgt von 90 eine gültige Tiefe-18-Partialkonstruktion
erzeugte. Damit war die beobachtete Tiefe-17-Barriere keine globale strukturelle
Grenze, sondern hing wesentlich von der Zeilenreihenfolge ab.

Regel: Bei konstruktiven Teilgraph-Suchen mit austauschbaren noch offenen Objekten
darf eine feste Objekt-/Zeilenreihenfolge nicht als neutral behandelt werden.
Rest-Erweiterbarkeit explizit messen und die Objektidentität selbst in die Suche
aufnehmen. Lokale Maximalität eines Zustands ist von globaler Maximaltiefe und von
Maximalität unter einer festen Reihenfolge zu unterscheiden.

Regression/Anwendung: Die WALK-Kampagne 0.3.0 durchsucht dynamische Zeilenidentitäten,
dedupliziert gespeicherte Basen und backtrackt zunächst über Schnitte 16 bis 8.
Belege: `docs/memetik/row_constructive_walk_20261002/PLAN.md` und
`experiments/memetik/row_constructive_0_2_0/probe_target_depth.py`.


## GC-18 — Supervisor-Arbeit muss mit wachsendem Dateibestand begrenzt bleiben, 04.10.2026

ROOT8105 1.0.1:251 Suchstunden abgeschlossen,19.3444 CPUh Nebenarbeit; globales
270h-Budget verhindert fünf Suchaufträge und alle Zertifikatsprüfungen. Alter
Controller prüfte rekursiv sämtliche Dateigrößen alle30Gastsekunden. Der genaue
Kostenanteil dieses Vorgangs ist unprofiliert; die blockierende Skalierung ist
im Code belegt. Gesamtüberschreitung1262.56CPU s einschließlich Abwicklung.
Regel: Größenprüfungen in beschränkte Abschnitte zerlegen, Alter/Fortschritt und
eigenen CPU-Aufwand melden; Supervisor- und Beweisreserven getrennt planen.
Phasenanzeige darf Ressourcenstopp nicht als ausgeführte Beweisphase ausgeben.
Regression:2040Einträge über121 begrenzte Aufrufe; Wachstum erkannt;
PermissionError bleibt sichtbar; echte Pause/Resume- und Beweisfortsetzung.
1.0.2 ist eine ausdrückliche Fortsetzung mit unveränderten mathematischen
Quellen und maximal286CPUh Gesamtrahmen, erst nach explizitem Startargument.
Belege:docs/memetik/root8105_recovery_20261004. Zielhardwareprüfung ausstehend.


## GC-19 — Zeitbudgetende erfordert eine Nutzerentscheidung, 04.10.2026

Explizite Nutzeranweisung: Kein Experiment allein wegen Erreichens eines
Zeitbudgets abbrechen. Prompt: `time limit reached. ETA HH:MM. Extend [seconds] ?`.
0 beendet kontrolliert; positive ganze Sekunden verlängern das betreffende
Budget. Klarstellung12:37:54MESZ: Bis zur Antwort unverändert weiterrechnen, auch bei
EOF oder ungültiger Eingabe. Keine Pause, Suspendierung oder Drosselung allein
wegen der offenen Anfrage. Verbrauch und Budgetüberschreitung weiter verbuchen.
Diese Weiterarbeit ist ausdrücklich autorisiert. Pro erreichtem Budget nur eine
offene Anfrage; regulärer Aufgabenabschluss erledigt sie. Positive Sekunden
werden auf das bisherige Budget aufgeschlagen, bereits verbrauchte Zeit bleibt
angerechnet; nötigenfalls erneut abfragen und weiterrechnen.
ETA ist verbleibende Walltime; bei unbestimmbarer Restlaufzeit `unknown`.
Budgetart und kumulative Reservierung offenlegen. Hintergrundläufe benötigen
einen dauerhaften Anfrage-/Antwortkanal mit einmaliger Verarbeitung.

Diese Vorgabe löst den früheren automatischen Budgetstopp ab. GC-02/05/10/11/15
bleiben hinsichtlich ehrlicher Abrechnung, Aufgabenabschluss, ETA und
Zustandserhalt gültig. Ressourcen-/Integritätssicherheit bleibt unabhängig.
Verbindliche Details: ../EXPERIMENT_RULES.md, Version1.1.

Akzeptanztests für künftige Implementierungen: positive Verlängerung erhält
Suchzustand;0 sichert und beendet; keine Antwort/EOF lässt die Berechnung weiterlaufen; ungültige Eingaben
ändern das nominelle Budget nicht; wiederholte und doppelt zugestellte Antworten erhöhen Budgets
nur einmal; Pause/Neustart erhält vollständige Abrechnung; Hintergrundlauf
kann über einen getrennten Kanal beantwortet werden.

Status: als Projektanweisung veröffentlicht, noch keine allgemeine technische
Implementierung. Der am04.10.2026 bereits laufende ROOT8105-Recovery1.0.2 bleibt
unverändert und besitzt diese interaktive Erweiterungsfunktion noch nicht.

## GC-20 — Positivkontrollen gelten nur für ihr geprüftes Modell, 04.10.2026

Der H-Faser-Handoff empfahl vollständige H-lineare Zeugen als garantiert
ergänzbare tiefe Präfixe. ROOT8105 verlangt jedoch schon in Geometry.verify
Paarbedingungen gebauter Zeilen und im Encoder zusätzliche Sternbedingungen.
XP=M allein garantiert diese Bedingungen nicht. Ein lineares H-Präfix ist
daher nur für das lineare Completion-Modell automatisch positiv, nicht für
den stärkeren Augmentation-Encoder. Auch das Scheitern eines konkreten
vollständigen Zeugen an Zusatzbedingungen beweist noch kein UNSAT des Präfixes.

Regel: Jede Positivkontrolle benennt die exakten Bedingungen, Labelabbildung
und eine unabhängig geprüfte erfüllende Belegung. Bei Modellverschärfung die
Garantie neu prüfen. UNKNOWN, ungültiger Kontrollinput und echter Widerspruch
sind verschiedene Befunde. Kleine vollständige SRG-Kontrollen ersetzen keine
Leistungsprognose für99Vertices.

Belege:docs/augmentation/root8105_review_20261004/ERGEBNISSE_UND_ABGLEICH.md,
Abschnitt7; Vergleich der drei H-Faser-Commits mit ROOT8105 core.py.
Regression geplant: getrennte L-/F-Kontrollen, erfüllende Belegungen prüfen,
absichtlich verletzte Paarbedingung erkennen, keine falsche SAT-Garantie.
Status: Modellunterschied durch Quellen-/Codeprüfung belegt; neue Kontrollen
noch nicht implementiert oder auf Zielhardware ausgeführt.

GC-18 Zielhardwareergänzung:Recovery1.0.2 schloss mit256Such- und512Proofjobs ab;
Gesamt276,262573CPUh. Diese Endbelege sind im obigen Reviewverzeichnis erhalten.
Das bestätigt den konkreten Recoveryabschluss, keine vollständige Profilierung
der alten Nebenarbeit und keine allgemeine Langzeitgarantie des Monitors.

## GC-15 Ergänzung — Recovery selbst prüfen, 05.10.2026

Beim ROOT8105-Census-Review wurde ein verwaister RUNNING-Root ohne offenen
Versuch reproduziert. rc1 verweigerte korrekt die Fortsetzung, verwies aber
auf reconcile-crash, das diesen Zustand nicht reparierte. Regel: einen normalen
Absturz mit zusammenhängenden Konten von einem inkohärenten Datenbestand
unterscheiden. Recovery prüft vor Schreibzugriffen Manifest, Code-/Modell-/Root-
Identitäten, Kontenverknüpfungen und endliche nichtnegative CPU-Werte. Ein
inkohärenter Bestand bleibt erhalten; bei diesem frühen Pilot ist ein neuer
Lauf mit neuer Kennung/Konten vorgesehen, keine stille Statusreparatur.

Regression in root8105_census_1_0_1rc2/recovery_test.py: Trockenlauf und Apply
weisen verwaiste Roots, falsche Identitäten und ungültige Konten unverändert
zurück; ungültige Worker-CPU wird nicht als Beleg akzeptiert. Dieselbe Version
prüft neben der Eltern-PID auch die Prozess-Startidentität. Echte Cloud-
Unterbrechungs-/Wiederanlaufbelege und Grenzen stehen in
docs/augmentation/root8105_census_rc2_20261005. Zielhardware separat abnehmen;
kein globaler WSL-Neustart während unabhängiger laufender C2-Prüfungen.
