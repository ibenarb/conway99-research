Für das Update einer vorhandenen Installation: `python3 activate.py`, anschließend `python3 run_matching.py --seconds 28800`. Vorhandene CNFs und Solver werden wiederverwendet; activate.py sichert die bisherige setup.json und aktiviert nur nach bestandener echter Windows-Telemetrieprüfung.

# C2 Matching-Scout 1.0.1

Diese Vorbereitung ersetzt den empirischen Dreivariablenvergleich durch elf vollständig begründete lokale Matching-Orbitfälle. Die vollständige Herleitung steht in THEOREM.md. Neuheit gegenüber der Literatur und ein C2-Ausschluss werden nicht beansprucht.

Voraussetzung: die erfolgreich installierte Version c2_scout_v2 auf Debian unter rb_debian. `python3 prepare_matching.py` verwendet deren bereits gebauten CaDiCaL und die gepinnte Referenz-CNF. Quellcommit, Binärhash, Version, CNF-Hash und Variablenkarte werden abgeglichen. Es findet kein erneuter Solverbuild statt. Alle 10.395 Transportkontrollen laufen erneut. Vorbereitung erzeugt elf CNFs von insgesamt ungefähr 449 MiB; die übrigen vorhandenen Dateien bleiben erhalten.

`python3 run_matching.py` startet alle elf Fälle mit jeweils 1200 Sekunden Solver-Wallzeit, maximal elf gleichzeitig. Reine Suche dauert auf elf verfügbaren Kernen etwa 20 Minuten plus Anlauf/Abschluss. Standardwert für Windowsreserve ist 50 GiB, Linuxreserve 25 GiB, RAMreserve 4 GiB. Die unabhängige Windowsüberwachung wird vor dem Start aktiviert. Jeder Solver hat 4 GiB Adressraumlimit und 64 MiB Loglimit. Es gibt keine LRAT-/DRAT-Ausgabe. Die Speichergrenzen stammen aus Scout 2.0.0. Version 1.0.1 behebt Schwachstellen der Telemetrieaktualisierung und Fehlerprotokollierung; siehe FIX_20260916.md.

Das Programm kehrt nach bestätigter Controller-Bereitschaft zum Prompt zurück. Erst status.json zeigt die tatsächlich laufenden Jobs. Status wird laufend aktualisiert, driver.log erhält etwa alle zehn Minuten einen Eintrag. summary.json enthält Ergebnisse, Zeiten und den bekannten Umfang der Fälle. Eine STOP-Datei im aktuellen Laufverzeichnis beendet den Lauf kontrolliert. Pro Matching-Arbeitsverzeichnis ist nur ein Controller erlaubt.

Keine automatische Fortsetzung nach dem Scout. Ein expliziter späterer Start mit `--seconds 28800` würde acht Stunden PRO FALL erlauben. Dies startet die Suche neu, nicht aus einem Solvercheckpoint. Ein längerer Lauf soll erst anhand des Scouts beschlossen werden; es ist nicht belegt, dass längere Budgets allein einen offenen Fall lösen.

UNSAT_UNCERTIFIED ist eine unzertifizierte Solveraussage. Erst separat erzeugte und unabhängig geprüfte Zertifikate können einen Fall schließen. SAT wird als vollständiger Graph rekonstruiert und gegen alle Graphbedingungen und Fallannahmen geprüft. Zeitlimit bedeutet offen. Auch mehrere leichte Ausschlüsse belegen noch keine Beschleunigung der verbleibenden harten Fälle.

Die Fälle bilden eine vollständige Abdeckung bis auf zulässige Rahmenumbenennung. Sie haben unterschiedliche Orbitgrößen. Es wäre falsch, einen gelösten Fall als 1/11 der mathematischen Aufgabe zu zählen. Falls alle elf Solver UNSAT melden, bleibt die Zertifizierungsphase erforderlich.

`python3 check_matching.py` reproduziert die mathematischen Implementierungskontrollen. Optional prüft ein zweites Argument mit dem Solverpfad den Controller an elf winzigen UNSAT-Formeln; die Windows-Telemetrie ist dabei ausdrücklich simuliert. Die überarbeitete Windowsüberwachung wird vor Aktivierung mit activate.py auf dem Zielrechner geprüft und bei jedem Lauf neu gestartet.
