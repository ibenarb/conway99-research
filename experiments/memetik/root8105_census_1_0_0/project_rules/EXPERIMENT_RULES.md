# Verbindliche Arbeitsregeln für Rechenexperimente

Version 1.1, 04.10.2026. Änderung: Zeitbudgetende führt zur Verlängerungsabfrage.
Grundfassung vom 28.09.2026. Ralph Beckmann hat diese Grundausrichtung ausdrücklich
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
Verbrauch erfassen, Abweichung ausweisen und Verlängerungen ausdrücklich buchen.
Zeitbudgets sind künftig Entscheidungspunkte gemäß der folgenden Regel.
Konkrete Toleranzen werden vor dem Versuch veröffentlicht, nicht nach
Sichtung des Ergebnisses passend gemacht. Zeitlimits bleiben UNKNOWN.

Globale Stopps bei tatsächlicher Ressourcen-/Datensicherheitsgefahr,
ungültigen Ergebnissen, ungeklärter Abrechnung, unbrauchbarer maßgeblicher
Uhr. Ein ausgeschöpftes Zeitbudget allein ist kein Abbruchgrund. Lokale Workerfehler
isolieren; übrige unabhängige Aufgaben weiterführen, soweit ihre Integrität
und sichere Überwachung gesichert bleiben. Keine pauschale Fehlerunterdrückung.

## Zeitbudgetende: Verlängerung statt automatischem Abbruch

Ausdrückliche Nutzeranweisung vom 04.10.2026, 12:37 MESZ: Kein Experiment
wird allein wegen Erreichens seines Zeitbudgets abgebrochen. Das gilt für
Gesamtkampagnen sowie Such-, Worker-, Solver- und Prüfzeitbudgets. Ein solches
Limit darf insbesondere keinen terminalen Aufgabenabschluss oder ein UNSAT
vortäuschen. Stattdessen wird folgende interaktive Meldung ausgegeben:

```text
time limit reached. ETA HH:MM. Extend [seconds] ?
```

- `0`: ausdrücklicher kontrollierter Abbruch des in der Meldung bezeichneten
  Laufs beziehungsweise Teilauftrags; Ergebnisse und vollständige Abrechnung
  sichern. Ein Abbruch einer Teilaufgabe stoppt keine unabhängigen Aufgaben.
- Positive ganze Zahl: Budget um genau diese Anzahl Sekunden erhöhen und
  denselben Lauf weiterführen. Die Verlängerung wird auf das bisherige
  Budget aufgeschlagen; während der Antwortzeit verbrauchte Zeit bleibt
  vollständig angerechnet. Ist auch das verlängerte Budget bereits erreicht,
  eine neue Anfrage ausgeben und weiterlaufen. Sonst beim nächsten Budgetende
  erneut abfragen.
- Bis zur Beantwortung läuft das Programm unverändert weiter, einschließlich
  regulärer Aufgabenplanung. Keine Pause, Suspendierung oder Drosselung allein
  wegen der ausstehenden Antwort. Status `RUNNING_AWAITING_TIME_EXTENSION`.
  Auch EOF, geschlossene Konsole oder ungültige Eingaben bewirken keinen
  Abbruch. Der Nutzer hat diese Weiterarbeit während der Antwortzeit mit
  Klarstellung vom04.10.2026,12:37:54MESZ ausdrücklich autorisiert.
  Tatsächlichen Verbrauch und Überschreitung lückenlos weiterzählen, ohne
  das nominelle Budget stillschweigend zu ändern. Pro erreichtem Budget nur
  eine offene Anfrage halten, keine blockierende Eingabe im Rechenthread.
  Regulärer Aufgabenabschluss bleibt möglich; dann die offene Anfrage als
  erledigt kennzeichnen, statt auf eine überflüssige Antwort zu warten.

Vor der Promptzeile Lauf/Teilauftrag, verbrauchtes Budget und Zeiteinheit
anzeigen. `seconds` bezeichnet Sekunden derselben Budgetart wie das erreichte
Limit (CPU-Sekunden oder Walltime-Sekunden); bei aggregierten CPU-Budgets
nicht still in Sekunden je Worker umdeuten. ETA bezeichnet die geschätzte
verbleibende reale Laufzeit als Stunden:Minuten, nicht eine Uhrzeit. Stunden
können größer als23 sein. Ist keine belastbare Schätzung möglich, lautet das
Feld `ETA unknown`; keine erfundene Genauigkeit, insbesondere bei reiner
Existenzsuche ohne prognostizierbaren Abschluss. Eine vorhandene reine
Budgetprojektion ist zusätzlich ausdrücklich als solche zu kennzeichnen.

Eine genehmigte Teilbudgetverlängerung darf nicht unbemerkt an einem
übergeordneten Zeitlimit scheitern: nötige zusätzliche Gesamtreservierung vor
der Entscheidung mit ausweisen und verbuchen beziehungsweise dort ebenfalls
abfragen. Originalbudgets, jede Eingabe/Verlängerung, Zeitpunkt, Budgetart und
kumulativer tatsächlicher Verbrauch bleiben dauerhaft nachvollziehbar.

Hintergrundläufe ohne Eingabekanal (z.B. nohup mit /dev/null) müssen dieselbe
Anfrage sichtbar in Status/Log und dauerhaft in einer Anfragedatei ablegen.
Eine dokumentierte separate Antwortfunktion übernimmt `0` oder die positiven
Sekunden mit eindeutiger Lauf- und Anfrage-ID, einmaliger Verarbeitung und
Bestätigung. Ohne Antwort rechnet das Programm weiter. Die Eingabeabfrage
muss nebenläufig erfolgen, ohne Busy-Wait und ohne wiederholte Promptflut.
Ein bloß ins Log
geschriebener Prompt ohne Antwortmöglichkeit erfüllt diese Regel nicht.

Echte RAM-/Plattengefahr, Integritätsfehler und ungeklärte Abrechnung bleiben
unabhängige Gründe für einen sicheren Stopp. Ein als Sicherheitslimit
bezeichnetes reines Zeitlimit darf die Verlängerungsregel nicht umgehen.
Nativer Solver, Betriebssystemlimit und Watchdog müssen denselben Vertrag
einhalten: Das abgefragte Zeitbudget darf keinen untergeordneten automatischen
Zeitabbruch auslösen. Kann ein bestehendes Werkzeug während der ausstehenden
Antwort nicht weiterrechnen, ist dies vor dem Start zu lösen oder eine konkrete
abweichende Nutzeranweisung einzuholen; kein stiller Rückfall auf Abbruch.
Zusätzliche CPU-Zeit während der offenen Anfrage fällt unter die ausdrückliche
Weiterlaufanweisung und benötigt keine erneute Freigabe.

Diese Regel gilt für neue und künftig überarbeitete Programme. Bereits
laufende oder eingefrorene Pakete werden nicht automatisch verändert;
eine Regeländerung allein implementiert noch keine Eingabefunktion.

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
Vor Freigabe die Budgetabfrage einschließlich positiver Verlängerung,
explizitem0-Abbruch, wiederholtem Limit, ungültiger Eingabe, EOF und
Hintergrundantwort prüfen. Ununterbrochene Weiterarbeit während der offenen Anfrage, einmalige Verarbeitung einer
Antwort und vollständige kumulative Abrechnung nach Pause/Neustart belegen.
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
