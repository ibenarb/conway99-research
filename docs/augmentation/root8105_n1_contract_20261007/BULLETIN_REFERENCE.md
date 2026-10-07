# Bulletin - generelle Anweisungen

Diese Anweisungen gelten für das gesamte Projekt Conway_99, alle Forschungszweige und alle zugehörigen Chats. Ihre Geltung ist nicht auf den Git-Zweig `memetik` beschränkt. Konkrete spätere Nutzeranweisungen gehen vor.

Stand: 07.10.2026. Die versionierte Git-Fassung bleibt als Referenz erhalten: https://github.com/ibenarb/conway99-research/blob/f379f5a39172a7559adde63159fed698e74e88e6/docs/CONWAY99_COLLABORATION.md . Nachfolgend ist deren Inhalt einschließlich der Regel zu abgegrenzten Bearbeitungsrunden übernommen und um die ausdrückliche Regel zu Timeouts, Datenerhalt und Fortsetzbarkeit vom 07.10.2026 ergänzt. Verweise auf Repository-Dateien beziehen sich auf `ibenarb/conway99-research`.

# Conway99: dauerhafte Zusammenarbeit und Git-Freigabe

Ralph Beckmann autorisiert seit 12. September 2026 generell Pushes projektbezogener Conway99-Commits. Für gewöhnliche Commits und Pushes ist keine erneute Einzelfreigabe erforderlich. Externe technische Zugriffsbeschränkungen bleiben zu beachten.

## Erneut ausdrücklich bestätigt am 21. September 2026

Ralph Beckmann: „Bitte merke für dieses Projekt, daß Du grundsätzlich auf GiT pushen und veröffentlichen darfst“.

Diese fortdauernde Freigabe umfasst projektbezogene Berichte, Quellcode, Prüfergebnisse, Daten und Archive sowie ihre Veröffentlichung im öffentlichen Repository `ibenarb/conway99-research`, insbesondere im Zweig `memetik`. Sie gilt auch für das bereits vorbereitete λ-Strategiepaket vom 21. September 2026. Gewöhnliche projektbezogene Veröffentlichungen benötigen keine erneute Einzelfreigabe. Die bestehenden Grenzen für destruktive Git-Aktionen, Zugriffsänderungen und vertrauliche fremde Unterlagen bleiben bestehen.

Reviewer- und Partneraustausch erfolgt grundsätzlich über Git. Eingerichtet ist das private Repository `ibenarb/conway99-review-exchange` mit eigenem Vorgangsverzeichnis und fixierten Commitreferenzen. Der erste vollständige Review-Vorgang ist unter Commit `72f791860921fa81b9fa4b50cc104ce0e4d68a5a` veröffentlicht. Startpunkt: https://github.com/ibenarb/conway99-review-exchange . Partnerzugänge werden über konkret benannte GitHub-Konten eingerichtet.

Ergebnisberichte und reproduzierbare Prüfungen werden im öffentlichen Forschungsrepository dokumentiert. Ungeprüfte private Partnerunterlagen werden nicht automatisch öffentlich gespiegelt. Rückgaben erfolgen über Partnerbranches und Pull Requests. Repository-Einladungen erfordern die konkrete Zuordnung eines GitHub-Kontos; ein privater Repository-Link allein genügt nicht.

Die allgemeine Freigabe ist keine pauschale Erlaubnis für Force-Pushes, Repository-Löschungen, beliebige neue Zugriffsfreigaben oder die Veröffentlichung vertraulicher Daten.

## Reviewarchivierung ab 13. September 2026

Auf ausdrückliche Anweisung von Ralph Beckmann wird jedes künftig eingehende Review in einem eigenen Git-Zweig archiviert, beispielsweise `reviews/YYYYMMDD-kurzbezeichnung`. Das erhaltene Original bleibt byteidentisch; Eingangsname, Länge, SHA256, geprüfte Forschungsreferenz und vorhandene beziehungsweise fehlende Begleitartefakte werden festgehalten. Eigene Bewertung, Korrekturen und Rechenergebnisse stehen in getrennten Dateien. Überarbeitete Rückgaben erhalten neue nachvollziehbare Versionen, keine stille Ersetzung des Originals.

Auf dem aktiven Forschungszweig wird ein fester Commitverweis im Reviewindex ergänzt. Die Archivierung eines fremden Befunds bedeutet keine automatische Übernahme als bewiesenes Projektergebnis. Aussagen über vom Reviewer ausgeführte Rechnungen bleiben von eigenen Reproduktionen getrennt. Bestehende Vertraulichkeits- und Zugangsregeln gelten weiter; private Reviews werden im geeigneten privaten Repository mit eigenem Zweig archiviert.

## Forschungsziel ab 13. September 2026

Ralph Beckmann priorisiert ausdrücklich neue mathematische Beiträge mit dem Fernziel des Symmetrieausschlusses. Bereits bekannte Ausschlüsse werden zitiert; ihre interne Nachimplementierung wird auf notwendige Kontrollen der neuen Beweiskette begrenzt. Ein neuer Encoder oder die Wiederholung eines bekannten Falles ist für sich kein neuer mathematischer Beitrag. Vor neuen Kampagnen sind die genaue Zielaussage und ihr Unterschied zu vorhandener Literatur zu dokumentieren. Der Forschungsplan steht unter `docs/symmetry_research_20260913/FORSCHUNGSPLAN.md`; C2 wird zunächst durch einen begrenzten Pilot bewertet, C3 bleibt die zweite offene Route. Eine Laufzeitgarantie für den Gesamtausschluss besteht nicht.

## Experimentpräferenzen und übergreifendes Lernen, 28.09.2026

Auf ausdrücklichen Wunsch von Ralph Beckmann gelten `docs/EXPERIMENT_RULES.md` und das Register `docs/operations/GLOBAL_CONCLUSIONS.md` als dauerhafte Arbeitsgrundlage. Toleranz gegenüber erklärbaren Betriebsabweichungen, großzügige Ressourcen und lokale Fehlerbehandlung sind Standard. Erfahrungen werden mit Evidenz, Regel und Regressionstest weitergegeben. Neue Projekt-/Reviewerübergaben verweisen auf einen fixierten Commit dieser Dateien.

## Keine harten Timeouts, Datenerhalt und Fortsetzbarkeit, 07.10.2026

Diese Regel gilt projektweit für neue und künftig überarbeitete Programme, einschließlich Controller, Worker, Solver und Prüfer. Sie übernimmt die Verlängerungsregel GC-19 und stellt Datenerhalt und Fortsetzbarkeit ausdrücklich klar.

- **Kein automatischer Zeitabbruch.** Das Erreichen eines Zeitbudgets darf weder einen harten Timeout noch einen automatischen Aufgabenabschluss auslösen. Auch untergeordnete Solverlimits, Betriebssystemlimits und Watchdogs dürfen diese Vorgabe nicht umgehen.
- **Verlängerung abfragen.** Bei Erreichen einer Zeitgrenze Lauf beziehungsweise Teilauftrag, Budgetart und tatsächlichen Verbrauch ausweisen und melden: `time limit reached. ETA HH:MM. Extend [seconds] ?`. ETA bezeichnet die geschätzte verbleibende Laufzeit in Stunden und Minuten; wenn nicht belastbar bestimmbar: `ETA unknown`.
- **Antwort 0: sofortiger kontrollierter Abbruch.** Die eigentliche Rechenarbeit des bezeichneten Laufs unverzüglich beenden und keine neuen Suchaufgaben dafür starten. Nur die zur verlustfreien Sicherung und vollständigen Abrechnung erforderliche Abwicklung ausführen. Kein destruktives Beenden vor der Sicherung. Unabhängige Läufe bleiben unberührt.
- **Antwort n > 0: Verlängerung um n Sekunden.** Eine positive ganze Zahl erhöht das bisherige Budget um genau n Sekunden derselben Budgetart (CPU- oder Walltime-Sekunden). Bereits während der Antwortzeit verbrauchte Sekunden bleiben angerechnet. Keine stillen Budgeterhöhungen; jede Verlängerung protokollieren und genau einmal verarbeiten.
- **Bis zur Antwort weiterrechnen.** Ohne Antwort, bei EOF oder ungültiger Eingabe unverändert weiterarbeiten, ohne Pause oder Drosselung allein wegen des Budgetendes. Tatsächlichen Verbrauch und Überschreitung vollständig verbuchen. Hintergrundprogramme benötigen einen dokumentierten dauerhaften Anfrage- und Antwortkanal. Regulärer Aufgabenabschluss erledigt eine noch offene Anfrage.
- **Kein Datenverlust durch Timeout oder Budgetentscheidung.** Ergebnisse, Suchfortschritt, offene Aufgaben, Zufallszustände soweit benötigt, Beweise beziehungsweise Beweisfragmente, Logs und Verbrauchskonten dauerhaft erhalten. Regelmäßige atomare Checkpoints und eine abschließende Sicherung vor kontrolliertem Beenden vorsehen. Vorhandene gültige Sicherungen niemals durch unvollständige Schreibvorgänge ersetzen.
- **Programme müssen fortsetzbar sein.** Wiederaufnahme aus einem geprüften Checkpoint ohne Verlust abgeschlossener Arbeit ermöglichen; offene oder unterbrochene Aufgaben eindeutig kennzeichnen. Fehlende Abschlussbelege oder abgebrochene Beweise dürfen nicht als vollständiges Ergebnis, UNSAT oder erschöpfte Suche gelten. Wiederanlauf erhält kumulative Verbrauchskonten und Provenienz. Kann ein Werkzeug seinen internen Zustand nicht speichern, müssen mindestens dauerhaft abgeschlossene Teilaufgaben erhalten bleiben und der Neustart des offenen Teilauftrags ausdrücklich dokumentiert werden; dies ist keine exakte Wiederaufnahme seines internen Suchzustands.
- **Vor Freigabe prüfen.** Budgetende, verzögerte Antwort, positive Verlängerung, 0-Abbruch, wiederholte Anfragen sowie Sicherung und Wiederaufnahme mit echten Prozessen testen. Ein Programm ohne nachgewiesenen sicheren Unterbrechungs- und Fortsetzungsweg ist für einen neuen Lauf nicht freizugeben.

Echte Ressourcen- oder Integritätsgefahr bleibt ein eigenständiger Grund für einen sicheren Stopp mit größtmöglichem Zustandserhalt; ein reines Zeitlimit darf nicht als Sicherheitsgrenze umetikettiert werden. Bereits laufende oder eingefrorene Programme werden durch diese Dokumentergänzung nicht automatisch verändert. Ein Antwort- oder Chatende ist ebenfalls kein Auftrag, laufende Programme abzubrechen.

## Begrenzte Bearbeitungsrunden und gesicherte Übergaben, 07.10.2026

Auf ausdrückliche Anweisung von Ralph Beckmann gilt für die Chat-Bearbeitung:

> Pro Bearbeitungsrunde genau ein abgegrenztes Arbeitspaket. Vor dessen Abschluss werden Ergebnisse, Prüfstatus und Fortsetzungsstand dauerhaft gesichert und die Sicherung überprüft. Danach endet die Antwort. Das nächste Paket beginnt erst mit „weiter“. Umfangreiche Rohdaten bleiben in Dateien; in den Chat kommen nur gezielte Auszüge und Zusammenfassungen.

Das Arbeitspaket wird zu Beginn benannt und so begrenzt, dass nicht mehrere größere Entwicklungsphasen zu einer einzigen Bearbeitungsrunde zusammengezogen werden. Der Abschluss nennt den gesicherten Stand (bei Git mit fixiertem Commit), erledigte und offene Prüfungen sowie den nächsten Schritt. Eine angekündigte Sicherung oder Fortschrittsmeldung gilt nicht als überprüfter Abschlussbeleg. Bei einer Unterbrechung zunächst vorhandene Sicherungen prüfen, bevor Rechnungen wiederholt werden.

Diese Regel ersetzt für die Chat-Bearbeitung ältere pauschale Aufforderungen, nach Paketabschluss automatisch entlang des Gesamtplans fortzufahren. Innerhalb des abgegrenzten Pakets sind keine zusätzlichen Bestätigungen für bereits autorisierte Teilschritte erforderlich. Das Ende einer Antwort ist kein Abbruchauftrag für laufende Rechenprozesse; insbesondere bleiben GC-19 und die Regeln für deren Überwachung und Abrechnung gültig.

Anlass: Im Chat „Memetik III“ wurden laut dem am 07.10.2026 vorgelegten Arbeitsverlauf mehrere Entwicklungs-, Diagnose-, Kontroll- und Veröffentlichungsphasen in einer Bearbeitung verbunden; anschließend wurde eine Volumengrenze gemeldet. Die konkrete technische Fehlerursache und der tatsächliche Kontextverbrauch sind nicht belegt. Die Regel begrenzt Arbeit zwischen überprüften Sicherungen; sie garantiert weder Fehlerfreiheit der Anwendung noch eine zuverlässige Vorwarnung vor deren Grenzen.
