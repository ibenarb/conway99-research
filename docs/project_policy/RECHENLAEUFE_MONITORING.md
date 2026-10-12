# Verbindliche Betriebsregeln für Forschungsrechenläufe

Vorgabe von Ralph vom 12.10.2026, 22:59 Uhr Europe/Berlin. Gilt projektweit für neue und überarbeitete Laufpakete. Diese Fassung verschärft die frühere Schwelle von einer Stunde auf 30 Minuten.

## Sichtbarer Heartbeat und Ereignisse

- Bei erwarteter Dauer über 30 Minuten von Beginn an spätestens alle 15 Minuten einen aussagekräftigen Heartbeat ausgeben. Bei unerwartet langen Läufen spätestens ab Minute 30; danach höchstens 15 Minuten Abstand. Häufigere sinnvolle Ausgaben sind zulässig.
- Die Ausgabe muss für Ralph direkt in einer mitgelieferten Liveansicht lesbar sein. Versteckte JSON-Dateien oder ein nur auf Nachfrage ausgeführter Statusbefehl allein erfüllen die Anforderung nicht. Ein abgekoppelter Controller braucht eine wieder anschließbare Liveansicht; ihr Schließen darf den Rechenlauf nicht beenden.
- Jeder Heartbeat nennt Zeitstempel, Phase, Gesamtwallzeit und CPU-Zeit, erledigte/offene/aktive Aufgaben, seit dem letzten Heartbeat erzielte Ergebnisse, relevante Änderungen der Such-/Prüfzähler, RAM-/Platten-/Proofverbrauch, Ressourcenpausen und Zeit seit dem letzten Ergebnis.
- Unverzüglich sichtbare Ereignisse: Aufgabenstart/-ende, Fund, SAT mit anschließender Belegungsprüfung, UNSAT zunächst unzertifiziert, Checkerstart/-erfolg/-fehler, tatsächliche neue Fallteilung mit Eltern-/Kindzuordnung, Phasenwechsel, Ressourcenpause/-fortsetzung, Fehler und Budget-/Verlängerungsanfrage.
- „Branch“ meint eine tatsächliche verwaltete Fallteilung oder relevante Suchphase. Milliarden interner SAT-Entscheidungen nicht einzeln ausgeben, sondern deren Zuwachs und Raten berichten. Keine nicht vorhandenen Branch-Ereignisse erfinden.
- Fortschritt, bloße Aktivität und mögliche Stagnation unterscheiden. Mehr Konflikte allein bedeuten weder Nähe zu UNSAT noch bewiesene Stagnation. Bei ausbleibenden Ergebnissen und veränderten Raten eine begründete Diagnose ausgeben, keine unbelegte Erfolgsaussicht.

## ETA

- Jeder Heartbeat enthält eine ETA-Angabe mit Bezug: aktuelle Phase, aktuelle Aufgabe oder freigegebene Stufe.
- Bei messbarem Restumfang aus Rate und verbleibender Arbeit eine Schätzung bzw. Spanne berechnen, mit Grundlage, Stichprobenumfang und Unsicherheit. Offene schwierige Fälle dürfen nicht aus der Prognose verschwinden.
- Bei SAT-Suche ohne belastbare Fortschrittsgröße keine erfundene Fund-/Abschlusszeit. Stattdessen ausdrücklich „Abschluss-ETA derzeit nicht belastbar“, den konkreten Grund und die Uhrzeit des nächsten Kontrollpunkts nennen. Ein Kontrollpunkt ist keine Abschluss-ETA.
- ETA-Veränderungen sichtbar machen. Unterschiedliche Phasen und Ressourcenengpässe berücksichtigen; keine Hochrechnung allein aus dem Median schnell gelöster Aufgaben.

## Laufzeit und Ressourcen

- Keine harten Zeitlimits für produktive Forschungsläufe. Zeitbudgets sind Melde- und Verlängerungspunkte; laufende Arbeit nicht still beenden. Explizite Antwort 0 darf den bezeichneten Job beenden, positive Sekunden verlängern. Fehlende Antwort ist kein Abbruchauftrag.
- Compute, RAM und Platte großzügig und nach gemessenem Nutzen einsetzen. Keine willkürlich knappen Limits, die aussichtsreiche Arbeit verhindern oder vernichten. Eine geringe Pilotparallelität dient der Kalibrierung, nicht als dauerhafte Ressourcensparvorgabe.
- Aussagekräftige Ressourcenüberwachung ist Pflicht: unter WSL Linux und physischen Windows-Host berücksichtigen; RAM, Swap/Speicherdruck, freie physische Platte, Proofwachstum, CPU-Nutzung und Telemetriefrische beobachten.
- Tatsächliche Gefährdung durch Ressourcenmangel rechtfertigt kontrolliertes Pausieren mit Erhalt des Zustands und klarer Meldung. Warn-/Pausegrenzen sachlich begründen; großzügige Ressourcenfreigabe hebt notwendige Reserven nicht auf.
- Keine vorhandenen fremden oder parallelen Forschungsprozesse verändern. Keine erfundene Wiederaufnahmefähigkeit nach Rechner-/WSL-Neustart.

## Abnahme vor Produktionsfreigabe

Mit kurzen kontrollierten Tests prüfen: periodische Ausgabe ohne Ergebnis, jedes unterstützte Ereignis, unbekannte sowie berechenbare ETA, Weiterlauf nach Zielzeit, Verlängerung und ausdrücklicher Abbruch, Ressourcenpause und Fortsetzung, Anschluss/Trennung der Liveansicht. Kontrolltests dürfen definierte Testgrenzen besitzen; diese dürfen nicht in Produktivjobs gelangen.

## Bestandsabgleich LOW Pilot 1.0.0

Bereits vorhanden: periodischer Status alle 600 Sekunden in Logdateien, strukturierte Jobzustände, Ressourcenwächter, weiche CPU-Zielzeiten mit Weiterlauf und ausdrücklicher Verlängerung/Beendigung, Prüfzertifikate.

Noch unzureichend: keine mitgelieferte automatische Liveansicht; keine durchgängige sofortige Ereignisausgabe; ETA stets unbekannt ohne differenzierte Herleitung; noch keine ausreichende zusammengefasste Aktivitäts-/Stagnationsdiagnose. Ressourcenbeobachtung bisher insbesondere freie RAM-/Plattenwerte und Prozessdaten, keine umfassende Swap-/Speicherdruckdiagnose.

Daher erfüllt 1.0.0 die neue Vorgabe nicht vollständig. Vor dem Start produktiver LOW-Pilotaufgaben ist die Monitoring-Ergänzung umzusetzen und zu prüfen. Bereits erlaubte Installation und Preflight können abgeschlossen werden; sie starten keine solchen Aufgaben.
