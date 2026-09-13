# Conway99: dauerhafte Zusammenarbeit und Git-Freigabe

Ralph Beckmann autorisiert seit 12. September 2026 generell Pushes projektbezogener Conway99-Commits. Für gewöhnliche Commits und Pushes ist keine erneute Einzelfreigabe erforderlich. Externe technische Zugriffsbeschränkungen bleiben zu beachten.

Reviewer- und Partneraustausch erfolgt grundsätzlich über Git. Eingerichtet ist das private Repository `ibenarb/conway99-review-exchange` mit eigenem Vorgangsverzeichnis und fixierten Commitreferenzen. Der erste vollständige Review-Vorgang ist unter Commit `72f791860921fa81b9fa4b50cc104ce0e4d68a5a` veröffentlicht. Startpunkt: https://github.com/ibenarb/conway99-review-exchange . Partnerzugänge werden über konkret benannte GitHub-Konten eingerichtet.

Ergebnisberichte und reproduzierbare Prüfungen werden im öffentlichen Forschungsrepository dokumentiert. Ungeprüfte private Partnerunterlagen werden nicht automatisch öffentlich gespiegelt. Rückgaben erfolgen über Partnerbranches und Pull Requests. Repository-Einladungen erfordern die konkrete Zuordnung eines GitHub-Kontos; ein privater Repository-Link allein genügt nicht.

Die allgemeine Freigabe ist keine pauschale Erlaubnis für Force-Pushes, Repository-Löschungen, beliebige neue Zugriffsfreigaben oder die Veröffentlichung vertraulicher Daten.

## Reviewarchivierung ab 13. September 2026

Auf ausdrückliche Anweisung von Ralph Beckmann wird jedes künftig eingehende Review in einem eigenen Git-Zweig archiviert, beispielsweise `reviews/YYYYMMDD-kurzbezeichnung`. Das erhaltene Original bleibt byteidentisch; Eingangsname, Länge, SHA256, geprüfte Forschungsreferenz und vorhandene beziehungsweise fehlende Begleitartefakte werden festgehalten. Eigene Bewertung, Korrekturen und Rechenergebnisse stehen in getrennten Dateien. Überarbeitete Rückgaben erhalten neue nachvollziehbare Versionen, keine stille Ersetzung des Originals.

Auf dem aktiven Forschungszweig wird ein fester Commitverweis im Reviewindex ergänzt. Die Archivierung eines fremden Befunds bedeutet keine automatische Übernahme als bewiesenes Projektergebnis. Aussagen über vom Reviewer ausgeführte Rechnungen bleiben von eigenen Reproduktionen getrennt. Bestehende Vertraulichkeits- und Zugangsregeln gelten weiter; private Reviews werden im geeigneten privaten Repository mit eigenem Zweig archiviert.

## Forschungsziel ab 13. September 2026

Ralph Beckmann priorisiert ausdrücklich neue mathematische Beiträge mit dem Fernziel des Symmetrieausschlusses. Bereits bekannte Ausschlüsse werden zitiert; ihre interne Nachimplementierung wird auf notwendige Kontrollen der neuen Beweiskette begrenzt. Ein neuer Encoder oder die Wiederholung eines bekannten Falles ist für sich kein neuer mathematischer Beitrag. Vor neuen Kampagnen sind die genaue Zielaussage und ihr Unterschied zu vorhandener Literatur zu dokumentieren. Der Forschungsplan steht unter `docs/symmetry_research_20260913/FORSCHUNGSPLAN.md`; C2 wird zunächst durch einen begrenzten Pilot bewertet, C3 bleibt die zweite offene Route. Eine Laufzeitgarantie für den Gesamtausschluss besteht nicht.
