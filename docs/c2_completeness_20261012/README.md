# C2-Vollständigkeitsprüfung und Publikationsentwicklung

Stand **12.10.2026**, Arbeitsfassung **0.1**. Ausschließlich der C2-Symmetriezweig.
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

## Gesicherter Ausgangsstand und heutige Fortschritte

Die 234.691 angegebenen Profile sind unter ihren übernommenen Voraussetzungen
vollständig bedingt abgedeckt; Rest218 wurde durch 217 Trim-/cake-Belege und den
direkten cake-Beleg des letzten Profils geschlossen. Der frühere Abschlussaudit
ist im Ergebnisverzeichnis unverändert enthalten. Er war ein Metadaten- und
Formelrekonstruktionsaudit, keine erneute vollständige Beweisprüfung.

Am 12.10.2026 wurden zusätzlich ausgeführt:

- Originalsatz von Makhnev–Minakova zur Ein-Fixpunkt-Reduktion im Seitenscan verifiziert;
- vollständige Konsistenzprüfung der wiedergefundenen 7.388.648 Censusdatensätze;
- vollständige Einbettung aller 234.691 Restdatensätze in den Census und aller 218 Schlussdatensätze in die Restliste;
- vollständige lokale Enumeration der 10.395 Matchings mit Bestätigung aller elf Typen;
- neue Ausarbeitung der Kompatibilität von Minimumankerwahl und lokaler Matchingnormalform;
- arithmetischer Abgleich der historischen Abdeckungskette vom Census bis zur leeren Restliste.

Dabei wurden keine neuen Solverläufe und keine neuen Checker-Replays gestartet.
Ryzen- und Office-Prozesse wurden nicht angesprochen.

## Reproduzierbare kleine Prüfungen

Der Quellbaum [src/c2_completeness_20261012](../../src/c2_completeness_20261012) enthält:

- `check_reductions.py`: lokale Matchingenumeration, Gruppen-/Rahmenzahlen,
  historischer Zahlensaldo und optional die vollständige Listenverknüpfung.
- `validate_records.cpp`: unabhängiger Strukturprüfer aller Censusdatensätze,
  einschließlich C4-Freiheit und exakter Codedublettenprüfung.
- `audit_census.py`: Archiv-/Dateihashes, Abgleich mit historischen Begleitdateien
  und Vergleich der neu berechneten Profil-/Stratumzahlen.

Die tatsächlich ausgeführten Ergebnisse liegen unter
[results/c2_completeness_20261012](../../results/c2_completeness_20261012).
Die Grenzen jeder Prüfung stehen im jeweiligen Ergebnis. Insbesondere bedeutet
Codedublettenfreiheit nicht Isomorphiedublettenfreiheit; gespeicherte Aut-Ordnungen
wurden im Upload-Audit nicht unabhängig berechnet.

## Zwei Reviewphasen

Das frühe Review konzentriert sich auf die Beweisstruktur und die Reichweite des
Profil346-Zweigs. Ein erster konkreter Auftrag wird im privaten Review-Austausch
unter `reviews/2026-10-12-c2-vollstaendigkeit` mit festem Forschungscommit abgelegt.
Das Abschlussreview folgt erst nach Schließen der für die endgültige Satzfassung
notwendigen offenen Punkte. Eine Reviewerantwort liegt für diesen neuen Auftrag
noch nicht vor.

## Offener Kern

Profil346 fordert für alle sieben Anker Grade in {3,4,6}. Erst sein vollständig
begründeter Ausschluss reduziert einen hypothetischen C2-Fall auf einen Minimumanker
mit Grad 0, 1 oder 2. Hierzu gehören acht lokale Matchingtypen. Für diese Seite ist
bislang keine vollständige Ausschlusskette lokalisiert. Die Veröffentlichung darf
den allgemeinen C2-Satz erst beanspruchen, wenn auch dieser Übergang geschlossen ist.
