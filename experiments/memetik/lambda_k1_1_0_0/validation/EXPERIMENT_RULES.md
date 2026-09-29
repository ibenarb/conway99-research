# Verbindliche Arbeitsregeln für Rechenexperimente

Version 1.0, 28.09.2026. Ralph Beckmann hat diese Grundausrichtung ausdrücklich
als dauerhafte Präferenz auch für zukünftige Experimente bestätigt.
Sie gilt vorbehaltlich konkreter abweichender Vorgaben je Versuch.

## Ressourcen und Toleranz

Lokale Rechenzeit ist vergleichsweise günstig; wiederholte Chat-Schleifen,
vermeidbarer Stillstand und verlorene Nachtläufe sind teuer. Startpopulationen,
Suchbudgets und Kontrollen ausreichend breit und großzügig bemessen.
Vorhandene Hardware nach gemessenem Durchsatz und Speicherbedarf nutzen.
Keine künstlich kurzen Prüfzeitlimits oder Abbrüche nur wegen Stagnation.

Suchziel, Beendigungsreserve und harte Sicherheitsgrenze getrennt definieren.
Kleine, vollständig erklärbare und verbuchte Zeitüberschreitungen sind ein
lokales Betriebsereignis, kein automatischer Grund für Kampagnenabbruch.
Toleranz bedeutet keine unprotokollierte Budgeterhöhung: tatsächlichen
Verbrauch erfassen, Abweichung ausweisen, Gesamtbudget weiter einhalten.
Konkrete Toleranzen werden vor dem Versuch veröffentlicht, nicht nach
Sichtung des Ergebnisses passend gemacht. Zeitlimits bleiben UNKNOWN.

Globale Stopps bei tatsächlicher Ressourcen-/Datensicherheitsgefahr,
ungültigen Ergebnissen, ungeklärter Abrechnung, unbrauchbarer maßgeblicher
Uhr oder ausgeschöpftem freigegebenem Gesamtbudget. Lokale Workerfehler
isolieren; übrige unabhängige Aufgaben weiterführen, soweit ihre Integrität
und sichere Überwachung gesichert bleiben. Keine pauschale Fehlerunterdrückung.

## Uhren und Abrechnung

Windows-Host-Stopwatch, Gastuhren, interne CPU-Messung und wait4-Endabrechnung
namentlich unterscheiden. Zeitdifferenzen nur zwischen vergleichbaren
Intervallen und Einheiten bewerten. Gastdrift nicht durch einen erfundenen
Skalierungsfaktor korrigieren. `wait4` enthält Nachlauf nach der letzten
Worker-Messung; diese Differenz allein beweist keine Uhrendrift.
Abschaltanforderung, Solver-Rückkehr, internen Endstand und Endabrechnung
protokollieren. Ungeklärte Verbrauchslücken nicht als Null interpretieren.

## Vorabtests und Prognosen

Produktionspfad auf Zielhardware testen, einschließlich paralleler Last,
Budgetende, verzögertem Worker-Ende und lokalem Fehler. Cloud-/FakeHost-Tests
als solche ausweisen; sie ersetzen keinen echten Windows-/WSL-Test.
Tests müssen relevante Fehler auslösen, nicht nur den Normalstart bestätigen.
ETA aus repräsentativen Messungen auf derselben Maschine ableiten; mindestens
Budgetprojektion und gemessene Schätzung unterscheiden. Sehr kurze Messungen,
andere Hardware und unvalidierte Uhren ergeben keine belastbare Prognose.

## Nachvollziehbarkeit und Lernen

Fehlläufe samt Logs, Receipts, Checkpoints, Quellen und Fehlerursache erhalten.
Bei frühem technischen Abbruch kann ein sauberer vollständiger Neustart
sinnvoller sein als Migration. Die Entscheidung begründen. Beim Neustart
neue Laufkennung und neue Konten, keine Vermischung mit dem Fehllauf.
Bei Fortsetzung dagegen sämtliche alten Verbräuche und Ergebnisse erhalten.

Vor Planung `docs/operations/GLOBAL_CONCLUSIONS.md` lesen und die relevanten
Regel-IDs im Versuchsmanifest/Plan benennen. Nach Fehlern oder Fehleinschätzungen
einen Eintrag ergänzen: Beobachtung, Evidenz, Ursache/Unsicherheit, Regel,
Regressionstest, Anwendungsbereich und Status. Bloße Vorsätze gelten nicht
als umgesetzte Fehlerbehebung. Regeln bei Gegenbelegen revidieren.
Jeder Fortsetzungsprompt und Reviewerauftrag nennt den aktuellen fixierten
Commit dieser Regeln und die noch offenen technischen Prüfungen.

Mathematische Evidenz bleibt unabhängig von Betriebstoleranz streng:
Solvermeldungen, unabhängig geprüfte Kandidaten und zertifizierte Beweise
trennen. Kleine/abgebrochene Piloten nicht als Erschöpfung einer Methode
interpretieren. Fehlender Vorteil ist kein Gleichwertigkeitsbeweis.
Vor neuen Suchläufen bereits entschiedene Fälle und Literatur abgleichen.

## Projektübergreifende Weitergabe

Diese Datei ist die verbindliche Projektfassung. Die portable Fassung
`Globale_Lehren_Rechenexperimente.md` ist für Übergaben an andere Projekte
vorgesehen. Eine gespeicherte Datei garantiert nicht, dass jeder neue Chat
sie automatisch liest: in neuen Projekten ausdrücklich als Arbeitsgrundlage
mitgeben oder in deren Projektanweisungen verlinken. Keine automatische
Änderung laufender/fixierter Experimente aufgrund neuer Regeln.
