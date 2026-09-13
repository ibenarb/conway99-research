# Abschlussbericht v4_09333 – 13. September 2026

Der lokale Nebenlauf meldet `MODULAR_REDUCED_ROOT_UNSAT_VERIFIED v4_09333`.
Der eingereichte Bericht stimmt hinsichtlich Ausgangs-CNF, Blatt- und Brückeninventar sowie Überdeckungsbeweis mit dem bisherigen strukturierten Plan überein.

## Nachweisumfang

| Gegenstand | Ergebnis des Berichtsabgleichs |
|---|---|
| Blätter | 3.076 eindeutige, exakt zum Plan passende IDs |
| Brücken | 112 eindeutige, exakt zum Plan passende IDs |
| Neue Blattprüfungen | 3.075; ein früher geprüftes Blatt wiederverwendet |
| Zusammensetzung | Bericht bestätigt exakte Übereinstimmung der Blockierungsklauseln mit dem Überdeckungseingang |
| Ausgangs-CNF SHA-256 | `8b2f5eeb923bc736d6af9d0ea96a9ed09251bdb3a433e3cbb33f3fb80446b7d9` |
| Überdeckungsbeweis SHA-256 | `3b71009ad1aa602e080235d8b54e9108cee845344f99d6ad4dd9e04326b6d7fd` |

Der mathematische Zusammensetzungsschritt lautet: Aus UNSAT(F ∧ S) folgt, dass F die Blockierungsklausel zu S impliziert. Wenn sämtliche zusätzlich verwendeten Klauseln auf diesem Weg abgesichert sind und die Überdeckungsinstanz UNSAT ist, ist auch F UNSAT. Hier ist F ausschließlich die ursprüngliche reduzierte CNF dieser Wurzel.

Der Bericht dokumentiert lokal LRAT/Cake-geprüfte Verpflichtungen mit einer Zusammensetzung durch Python. Er ist kein einzelner LRAT-Beweis für F. Die Beweisdateien und Checkerprotokolle wurden mit diesem Bericht nicht eingereicht und hier nicht erneut geprüft. Der beigefügte Audit prüft Inventar, ausgewählte Referenzhashes und die Form der übrigen Hashangaben; er bestätigt nicht unabhängig den Inhalt sämtlicher Beweisdateien oder die Klauselzusammensetzung.

## Konsequenzen

Die bisher offene strukturierte Zertifizierung von `v4_09333` ist laut lokalem Abschlussbericht erledigt. Der frühere Plan bleibt als historischer Plan unverändert; dieser Bericht aktualisiert seinen Ausführungsstand.

Das Ergebnis allein schließt weder alle K66-Wurzeln noch Symmetrie insgesamt aus. Vorgelagerte Reduktionen, die vollständige Profildomäne und andere Wurzeln werden dadurch nicht zusätzlich zertifiziert. Für einen umfassenderen Ausschluss müssen ihre jeweiligen Nachweispflichten separat geschlossen sein.

Ein weiterer Hauptlauf über exakt dieselbe CNF von `v4_09333` wäre für diesen modularen Nachweis redundant. Vor einer Änderung am Hauptlauf sind seine aktuelle Wurzelzuordnung, CNF-Identität und übrigen offenen Aufgaben zu prüfen. Dieser Dokumentationsschritt verändert keinen laufenden Prozess. Über den aktuellen Abschlussstand der anderen Hauptlaufwurzeln liegt hier keine neue Messung vor.

## Aufwand und Reproduktion

Die Summe der erfassten neuen Blattjobzeiten einschließlich Speicherung beträgt 8,013 Stunden; sie ist keine gemessene Gesamtlaufzeit. Der Median beträgt 8,37 Sekunden, das Maximum 25,79 Sekunden. Der Bericht verzeichnet zusammen 121,26 GiB unkomprimierte Blattbeweise. Daraus folgt keine Aussage über den gegenwärtigen freien Speicher oder die Größe komprimierter Archive.

Der unveränderte Originalbericht ist im privaten Austauschrepository archiviert: [ROOT_ERGEBNIS.json](https://github.com/ibenarb/conway99-review-exchange/blob/ad818cc6deadc54c174e4401f45eddb31e40b00a/runs/2026-09-13-v4_09333/ROOT_ERGEBNIS.json).

SHA-256 des Originalberichts: `d9bfda775d0a2d7962b870407ef60284cb46316a3a4a9bf6edd66e75ad9283d8`.

Aus dem Forschungsrepository mit lokal vorliegendem Originalbericht ausführen:

```bash
python3 src/k66_completion_20260913/audit_report.py /pfad/zu/ROOT_ERGEBNIS.json
```

Das Ergebnis steht in `results/k66_completion_20260913/audit.json`. Der öffentliche Audit ist ohne Zugriff auf den privaten Originalbericht nicht allein reproduzierbar; er ersetzt keinen Proof-Checker.
