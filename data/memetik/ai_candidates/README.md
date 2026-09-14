# KI-Einreichungen und Kandidaten für den memetischen Zweig

Hier werden Antworten, eingereichte Graphdaten und unabhängige Bewertungen nachvollziehbar gesammelt.
Archivierung bedeutet keine Aufnahme in eine Startpopulation.

## Ablage

| Pfad | Zweck |
| --- | --- |
| `INDEX.md` | Lesbarer Eingangskatalog mit festen Archivcommits und Aufnahmeentscheidungen |
| `registry.json` | Maschinenlesbare Liste der Einreichungen und angenommenen Kandidaten |
| `submissions/YYYYMMDD_anbieter_vNN/original.md` | Unveränderte empfangene Antwort, einschließlich ursprünglicher Zeilenenden |
| `submissions/.../manifest.json` | Eingangsname, SHA256, Dateigröße, Anbieter-/Modellangabe, Forschungsreferenz und fehlende Bestandteile |
| `submissions/.../submitted_candidates.json` | Extrahierte Einreichungsdaten; keine stillen Korrekturen, kein Zulässigkeitsnachweis |
| `submissions/.../REVIEW.md` | Eigene Befunde, Analyse, Schlussfolgerungen und Grenzen |
| `submissions/.../audit.json` | Maschinenlesbare Ergebnisse eigener Prüfungen |
| `submissions/.../audit_submission.py` | Reproduktion der jeweiligen Prüfung, mit ausdrücklich benanntem Umfang |
| `accepted/lambda/`, `accepted/omega/` | Ausschließlich unabhängig geprüfte Graphen und ihre Abnahmemetadaten |

Die accepted-Unterverzeichnisse werden mit der ersten Aufnahme angelegt. Bis dahin erläutert `accepted/README.md` den Vertrag; es gibt keine Platzhaltergraphen.

## Vorgang und Versionierung

1. Jede Einreichung erhält einen eigenen Ordner und Archivzweig `reviews/YYYYMMDD-anbieter-candidates-vNN`.
2. Original bytes erhalten, Hash und Begleitartefakte erfassen. Eine Folgeantwort wird v02 usw., keine stille Überschreibung.
3. Eingereichte Daten extrahieren und getrennt prüfen. Behauptete Ergebnisse von tatsächlich nachgerechneten Ergebnissen unterscheiden.
4. Archivcommit in diesem Index und im Projekt-Reviewindex festhalten. Der Vorgang bleibt auch auf `memetik` zugänglich.
5. Nur nach unabhängiger Zulässigkeits-/Scoreprüfung Graphdaten in accepted aufnehmen. Isomorphie- und Neuheitsstatus separat berichten.

Einreichungsstatus: RECEIVED, UNDER_REVIEW, REJECTED_AS_SUBMITTED, PARTIALLY_ACCEPTED, ACCEPTED.
Einzelprüfungen: PASS, FAIL, UNVERIFIED, jeweils mit Umfang. Eine Ablehnung der vorliegenden Daten ist kein Unmöglichkeitsbeweis für eine Familie.

## Kandidatenidentität und Bytekonvention

Globale Eingangskennung: `<submission_id>/<candidate_id>`.
Familienkennungen gelten zunächst innerhalb einer Einreichung; verschiedene Namen verschiedener KIs beweisen keine verschiedenen Konstruktionsprinzipien.

graph6 ohne optionalen Header, genau ein abschließendes LF in der .g6-Datei. SHA256 über diese Dateibytes.
Dateihash identifiziert Bytes, nicht Isomorphieklassen. Ω-Rahmenpermutation zusätzlich speichern.

Die drei derzeit im Gespräch vorgeschlagenen Selektionsvarianten sind (W,L1), (F,W) und (Linf,Nmax,L1,W), jeweils lexikographisch. Ältere Pilotentwürfe führen noch L1 als eigene Variante; eine Implementierungsumstellung ist hiermit nicht behauptet.

## Aktueller Stand

Mistral/Vibe v01: sechs eingereichte Datensätze, null aufgenommene Kandidaten.
Alle sechs graph6-Angaben sind ungültig. Details im [Prüfbericht](submissions/20260914_mistral_v01/REVIEW.md).
