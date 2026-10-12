# C2-Vollständigkeitsprüfung und Publikationsentwicklung

Stand **12.10.2026**, Arbeitsfassung **0.4**. Ausschließlich der C2-Symmetriezweig.
Der allgemeine C2-Ausschluss ist **offen**.

## Einstieg

1. [Manuskript](MANUSKRIPT.md): Fixpunktsatz, vollständiger Rahmen, Matrixmodell,
   semantische Symmetrien, lokale Matchingtypen und bedingte Reduktion auf niedrige Grade.
2. [Beweisregister](BEWEISREGISTER.md): genaue Aussagen, Abhängigkeiten, Belegstatus und offene Pflichten.
3. [Census und Coverage](CENSUS_UND_COVERAGE.md): exakte Fallmenge, historische Ausschlusskette und neue Mengenverknüpfung.
4. [Artefaktmanifest](../../results/c2_completeness_20261012/artifact_manifest.json): Hashes,
   Bezugsstellen und ausdrücklich noch fehlende öffentliche Downloadadressen.
5. [Herkunft der Quellkopien](../../results/c2_completeness_20261012/source_provenance.json):
   unveränderte ausgewählte Originaldateien aus den tatsächlich verwendeten Paketen.
6. [Vollständigkeitsnachweis des Census](CENSUS_VOLLSTAENDIGKEIT.md): unabhängige
   Isomorphieprüfung, Automorphismenordnungen und vollständige beschriftete Zählung.
7. [C4/Profile46 und Belegkette](../c2_filter_audit_20261012/FILTER_UND_BELEGKETTE.md) sowie
   [Encoderadäquanz](../c2_filter_audit_20261012/ENCODER_ADAEQUANZ.md): eigene Fortsetzung nach dem ersten Reviewauftrag.

## Gesicherter Ausgangsstand und heutige Fortschritte

Die 234.691 angegebenen Profile sind unter ihren übernommenen Voraussetzungen
vollständig bedingt abgedeckt; Rest218 wurde durch 217 Trim-/cake-Belege und den
direkten cake-Beleg des letzten Profils geschlossen. Der frühere Abschlussaudit
ist im Ergebnisverzeichnis unverändert enthalten. Er war ein Metadaten- und
Formelrekonstruktionsaudit, keine erneute vollständige Beweisprüfung.

Am 12.10.2026 wurden zusätzlich ausgeführt:

- Originalsatz von Makhnev–Minakova zur Ein-Fixpunkt-Reduktion im Seitenscan verifiziert;
- vollständige Konsistenzprüfung der wiedergefundenen 7.388.648 Censusdatensätze;
- unabhängige Neuberechnung aller Automorphismenordnungen und Ausschluss isomorpher Dubletten;
- unabhängige vollständige Zählung von 37.030.041.152 beschrifteten Graphen;
  Übereinstimmung mit der neu berechneten Bahngrößensumme und damit Vollständigkeit
  des Census innerhalb seiner definierten Bedingungen;
- vollständige Einbettung aller 234.691 Restdatensätze in den Census und aller 218 Schlussdatensätze in die Restliste;
- vollständige lokale Enumeration der 10.395 Matchings mit Bestätigung aller elf Typen;
- neue Ausarbeitung der Kompatibilität von Minimumankerwahl und lokaler Matchingnormalform;
- arithmetischer Abgleich der historischen Abdeckungskette vom Census bis zur leeren Restliste;
- neue Bindung sämtlicher 4.746 Gleichungsaufrufe an die konkrete Basiskodierung;
- neue Rekonstruktion von F0, C4, F46 und F346; 105 vollständige C4-Transporte;
- neuer vollständiger Censusaudit für die 2.170 Profile46-Bahnen und Rekonstruktion
  sämtlicher Formelhashes mit Prüfung aller zugehörigen Solver-/Checkerbelege.

Dabei wurden keine neuen Solverläufe und keine neuen Checker-Replays gestartet.
Ryzen- und Office-Prozesse wurden nicht angesprochen.

## Reproduzierbare Prüfungen

Der Quellbaum [src/c2_completeness_20261012](../../src/c2_completeness_20261012) enthält:

- `check_reductions.py`: lokale Matchingenumeration, Gruppen-/Rahmenzahlen,
  historischer Zahlensaldo und optional die vollständige Listenverknüpfung.
- `validate_records.cpp`: unabhängiger Strukturprüfer aller Censusdatensätze,
  einschließlich C4-Freiheit und exakter Codedublettenprüfung.
- `audit_census.py`: Archiv-/Dateihashes, Abgleich mit historischen Begleitdateien
  und Vergleich der neu berechneten Profil-/Stratumzahlen.
- `audit_isomorphism.cpp` und `run_isomorphism_audit.py`: vollständige unabhängige
  Isomorphieprüfung und Neuberechnung sämtlicher Automorphismenordnungen.
- `count_labelled.cpp` und `run_labelled_census.py`: vollständige beschriftete
  Aufzählung ohne Kanonisierung und Abgleich mit der unabhängig bestimmten Bahngrößensumme.

Die tatsächlich ausgeführten Ergebnisse liegen unter
[results/c2_completeness_20261012](../../results/c2_completeness_20261012).
Die Grenzen jeder Prüfung stehen im jeweiligen Ergebnis. Der unveränderte frühere
Upload-Audit prüfte nur Datensatzkonsistenz; die späteren Isomorphie- und Zählaudits
schließen die dort noch offenen Censuspflichten. Unabhängig bedeutet hier:
neue Implementierungen ohne Verwendung des historischen Kanonisierers oder seiner
Aufzählungsshards, nicht bereits eine Prüfung durch eine andere Person.

## Zwei Reviewphasen

Das frühe Review konzentriert sich auf die Beweisstruktur und die Reichweite des
Profil346-Zweigs. Der erste konkrete Auftrag liegt im privaten Review-Austausch
unter `reviews/2026-10-12-c2-vollstaendigkeit` mit Forschungscommit
`7dbacd7eed56e2bf73b3aa5f2648f00e5484adfa`. Ralph hat am 12.10.2026 um 14:43 Uhr
mitgeteilt, dass er versandt wurde und in Arbeit ist.
Das Abschlussreview folgt erst nach Schließen der für die endgültige Satzfassung
notwendigen offenen Punkte. Eine Reviewerantwort liegt für diesen neuen Auftrag
noch nicht vor.

## Offener Kern

Profil346 fordert für alle sieben Anker Grade in {3,4,6}. Erst sein vollständig
begründeter Ausschluss reduziert einen hypothetischen C2-Fall auf einen Minimumanker
mit Grad 0, 1 oder 2. Hierzu gehören acht lokale Matchingtypen. Für diese Seite ist
bislang keine vollständige Ausschlusskette lokalisiert. Die Veröffentlichung darf
den allgemeinen C2-Satz erst beanspruchen, wenn auch dieser Übergang geschlossen ist.

## Eigene Fortsetzung: exakte Abdeckung bis Rest234691

Die [Muster- und Komplementprüfung](../c2_coverage_audit_20261012/MUSTER_UND_KOMPLEMENTE.md)
reproduziert jetzt alle Restlisten vom vollständigen Census bis zu genau
234.691 Fällen bytegenau. Alle verwendeten Muster sind an ihre Formeln und
historischen Checkerbelege gebunden; 1.373 Belegdatensätze wurden geprüft.
Es gab keinen neuen Proof-Replay. Die nachfolgenden Übergänge bis Rest218
und die niedrigen Ankergrade bleiben getrennte Aufgaben.
