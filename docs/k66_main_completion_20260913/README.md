# K66: Abschluss der sieben reduzierten Wurzeln

Stand: 13. September 2026. Das eingereichte Metadatenarchiv besteht die unabhängige Prüfung des gesamten binären Zerlegungswaldes und sämtlicher enthaltenen LRAT-/Cake-Prüfprotokolle. SHA256: `ae44c1274c5c3c646f964475e3c6a6057bb11525105144e2f41126ad54f0ebbb`.

| Wurzel | Zertifizierte Blätter | Verzweigungen | Frühere Entfernungen, Runden 1–3 |
|---|---:|---:|---|
| `v4_09316` | 7 | 6 | 28 + 0 + 0 |
| `v4_09317` | 11 | 10 | 34 + 1 + 0 |
| `v4_09322` | 175 | 174 | 10 + 0 + 0 |
| `v4_09323` | 236 | 235 | 12 + 0 + 0 |
| `v4_09331` | 3 | 2 | 24 + 0 + 0 |
| `v4_09332` | 236 | 235 | 10 + 0 + 0 |
| `v4_09333` | 229 | 228 | 6 + 0 + 0 |

Gesamt: 897 Blätter, 890 Verzweigungen, 1.787 Knoten. Jede Verzweigung ergänzt exakt entgegengesetzte Literale; alle Knoten werden genau einmal erreicht; es gibt keine offenen Endblätter. Sämtliche Checkerberichte melden Exitcode 0 und die positiven Marker, beide Checker-Fehlerprotokolle sind leer. Die aufgezeichneten Rohbeweishashes stimmen zwischen Solver- und Checker-Datensätzen überein.

## Nachweisgrenzen

Das Archiv enthält keine Blatt-CNFs oder LRAT-Beweisdateien. Hier wurden die Beweise nicht erneut ausgeführt und ihre Bytes nicht gegen die aufgezeichneten Hashes geprüft. Die Metadaten nennen rund 41,223 GiB gzip-Beweise bzw. 163,096 GiB Rohbeweise. Diese Dateien müssen auf dem Ryzen erhalten bleiben; die Git-Sicherung dieses Metadatenarchivs ersetzt keine Sicherung der Beweisdateien.

Der Hauptlauf schließt die sieben **reduzierten** CNFs gemäß den enthaltenen Prüfprotokollen ab. Der Nebenlauf für v4_09333 bezieht sich auf denselben dokumentierten Wurzelhash und ist zusätzliche Evidenz. Er erweitert den Geltungsbereich nicht.

## Konkret verbleibende Nachweispflichten

Die beigefügten älteren Rundenberichte nennen für diese sieben Wurzeln insgesamt **125 Neighbor-Star-Profilentfernungen**: 124 in Runde 1, eine in Runde 2 bei v4_09317, keine in Runde 3. Die vorhandene Deep7-star_history nennt danach null weitere Entfernungen und aktive Domänengrößen 634, 642, 654, 708, 608, 724, 741. Dies ist ein Inventar aus Berichten, noch keine unabhängige Identifikation und Zertifizierung sämtlicher 125 Einzelprofile.

1. Für jede Entfernung globale Profil-ID, Runde, konkrete Eingabedomäne, originale Star-CNF und deren Hash erfassen. Die hier vorhandenen Rundenberichte enthalten keine vollständige ID-Liste dieser 125 Fälle.
2. Für jede Star-CNF einen positiven LRAT- und Cake-Nachweis zu genau dieser Datei zuordnen bzw. fehlende Nachweise erzeugen. Das vorhandene Certify13-Manifest für v4_09232 betrifft eine andere Wurzel und ersetzt diese Nachweise nicht.
3. Die Abhängigkeiten der Runden prüfen: Eine Entfernung in Runde 2 darf auf bereits gerechtfertigten Entfernungen aus Runde 1 beruhen; zyklische Annahmen sind nicht zulässig.
4. Mathematische Notwendigkeit des Star-Modells einschließlich Multiplizitätsgrenzen, Eigenkopie-Abzug, zugelassenen Nachbarschaftsgewichten und Zellkapazitäten begründen; Encoder gegen diese Bedingungen prüfen.
5. Aus den verbleibenden Domänen die sieben reduzierten Wurzeln reproduzieren und ihre CNF-Hashes mit manifest.json abgleichen.
6. Für einen vollständigen K66-Ausschluss zusätzlich die vorgelagerte vollständige Falldomäne und die Zuordnung aller übrigen Fälle zu ihren jeweiligen Nachweisen zusammenführen. Der vorliegende Abschlussbericht allein leistet das nicht.

Konkreter Codebefund: `prior_removed_indices` im vorhandenen Deep7-Generator übernimmt jede Datei `star_round_{1,2,3}/<root>/profile_*.cnf` als frühere Entfernung, ohne dort Checkerberichte oder Zertifikate zu validieren. Die Zulässigkeit muss daher durch eine getrennte Zertifikatskette nachgewiesen werden. Daraus allein folgt kein Fehler einer konkreten Entfernung.

## Reproduktion

Vom Repository-Verzeichnis aus:

```bash
python3 src/k66_main_completion_20260913/audit.py data/k66_main_completion_20260913/k66_deep7_coarsecert_handoff_20260913_080728.zip
```

Erwarteter Status: `PASS_TREE_AND_CHECKER_LOG_AUDIT`. Der Prüfer verwendet nur die Python-Standardbibliothek. Nicht mit `python -O` starten, da er Assertions verwendet.

## Nächster Arbeitsschritt

Ein vollständiges Inventar der 125 Star-CNFs und vorhandenen Zertifikate vom Ryzen übernehmen. Anschließend gezielt fehlende Zertifikate schließen und die Domänenübergänge prüfen. Die sieben bereits abgeschlossenen reduzierten Wurzeln müssen dafür nicht erneut gelöst werden. Eine Laufzeitprognose für die fehlenden Zertifizierungen ist ohne Einzelinstanzen und vorhandene Protokolle noch nicht belastbar.
