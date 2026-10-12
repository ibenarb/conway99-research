# Census und Verbindung zu den abgeschlossenen Profilausschlüssen

Stand 12.10.2026. Alle Ausschlusszahlen in der historischen Kette sind relativ
zum verwendeten C2-Modell und den jeweils angegebenen Einschränkungen.

## 1. Exakte Fallmenge und Filter

Der Profile346Pilot zählt gerichtete schleifenfreie Graphen $D$ auf sieben
Ankerpaaren mit 42 möglichen Pfeilen, modulo $S_7$, unter folgenden Bedingungen:

| Bedingung | Rolle | Für einen C2-Ausschluss zusätzlich erforderlich |
|---|---|---|
| Alle Ausgrade in {3,4,6} | Definition des Zweigs F346 | Die komplementären Fälle mit Grad 0, 1 oder 2 separat behandeln. |
| Mindestens ein Grad 3 | Entfernt den Zweig Profile46 | Bindung inzwischen neu geprüft; historische Checkerprüfungen übernommen, siehe Filteraudit. |
| Kein C4 im gegenseitigen Ankergraphen | Mathematisch begründeter Filter beansprucht | Bindung an F0 plus acht Units und 105 Transporte neu geprüft; historische Checkerprüfung übernommen. |
| Gradfolge absteigend sortiert | Umbenennung der sieben Anker | S7 erhält E1–E3 und alle vorangehenden Bedingungen. |
| Ein Vertreter je Bahn | Quotientierung | Vollständigkeit, Automorphismenordnungen und Isomorphiedublettenfreiheit sind neu geprüft; siehe CENSUS_VOLLSTAENDIGKEIT.md. |

Der lokale Census ist eine Menge notwendiger Pfeilkonfigurationen. Seine Vertreter
sind keine behaupteten SRG-Lösungen. Die Begriffe **Profile346** und **Rest234691**
sind nicht gleichbedeutend: Letzteres ist eine nach mehreren Ausschlüssen entstandene Restliste.

## 2. Originalcensus und neue Datenprüfung

Die auf Office wiedergefundene `representatives.tsv` hat 279.171.105 Bytes und SHA-256
`d003dd431ce506b0bbf936441b970cf80d99027e7d35219b26763312bffbb538`.
Sie wurde am 12.10.2026 vollständig gelesen. Die neue Prüfung bestätigte:

- 7.388.648 Datensätze mit unterschiedlichen 42-Bit-Codes;
- korrekte Gradfolgen, gegenseitige Kantenzahlen und Stratumzuordnungen für jeden Datensatz;
- die geforderten Grade und C4-Freiheit jedes gegenseitigen Ankergraphen;
- 28 Gradprofile einschließlich zehn leerer Profile und 37 nichtleere Strata;
- sämtliche Profil- und Stratumzahlen der begleitenden JSON-Dateien;
- die Summe 37.030.041.152 der Gewichte 5040/aut unter Verwendung der **gespeicherten** Automorphismenordnungen;
- byteidentische Begleitdateien gegenüber dem älteren Profile346Pilot-1.0.1-Ergebnisarchiv.

Dieser erste Upload-Audit berechnete die Automorphismenordnungen nicht neu, schloss isomorphe
Dubletten nicht neu aus und zählte die vollständige Suchmenge nicht erneut auf.
Die weiter unten beschriebenen zusätzlichen Prüfungen schließen diese Pflichten
für die gehashte Vertreterliste, ohne auf die Korrektheit des historischen
Kanonisierungsprogramms oder seiner Aufzählungsshards angewiesen zu sein.

Belege: [census_upload_audit.json](../../results/c2_completeness_20261012/census_upload_audit.json)
und [census_validation_output.txt](../../results/c2_completeness_20261012/census_validation_output.txt).
Die Überschrift der historischen README nennt noch 1.0.0; Pfade und Korrekturabschnitt
nennen 1.0.1. Die betreffende README ist byteidentisch mit dem früheren 1.0.1-Export.

### Zusätzlicher vollständiger Isomorphie- und Zählaudit

Eine neue Implementierung berechnete für sämtliche 7.388.648 Vertreter unabhängig
die Automorphismenordnung. Alle gespeicherten Werte stimmen. Kanonisierung unter
allen Permutationen innerhalb invariant geordneter Ausgrad-/Eingradklassen schloss
isomorphe Dubletten aus. Die Summe der neu berechneten Bahngrößen beträgt
37.030.041.152.

Ein zweites neues Programm zählt ohne Kanonisierung sämtliche beschrifteten
Pfeilgraphen der oben definierten Domäne. Es durchläuft alle Zeilenmasken für alle
28 Gradprofile und verwirft nur Präfixe, deren gegenseitiger Graph bereits einen
Vierzyklus enthält. Die Gesamtzahl ist ebenfalls 37.030.041.152; außerdem stimmen
die Zahlen für jedes einzelne Gradprofil mit den historischen Begleitdaten überein.

Zulässige, paarweise verschiedene Bahnen mit dieser Gesamtgröße füllen damit die
gesamte unabhängig gezählte Domäne aus. Dies schließt die Censusvollständigkeit
innerhalb seiner Bedingungen. Die Anwendung dieser Bedingungen auf SRG-Lösungen
bedarf der korrekt gebundenen Ausschlüsse P46 und C4. Die eigene Fortsetzung
[Filter- und Belegkette](../c2_filter_audit_20261012/FILTER_UND_BELEGKETTE.md) liefert
diese Bindung unter den dort ausdrücklich übernommenen historischen Checkerprüfungen.

Beweis und Reproduktionshinweise: [CENSUS_VOLLSTAENDIGKEIT.md](CENSUS_VOLLSTAENDIGKEIT.md).
Neue Berichte: [isomorphism_audit.json](../../results/c2_completeness_20261012/isomorphism_audit.json)
und [labelled_census_audit.json](../../results/c2_completeness_20261012/labelled_census_audit.json).

## 3. Historische Abdeckungskette

Die folgenden Zahlen wurden aus den Original-JSON-Belegen rekonstruiert. Die
Subtraktionskette wurde neu nachgerechnet. Ein rechnerisch passender Saldo ersetzt
keinen Mengenvergleich und keine Zertifikatsprüfung.

| Stufe | Zusätzlich abgedeckt | Verbleibend | Belegstatus dieses Arbeitsstands |
|---|---:|---:|---|
| Ausgangscensus | — | 7.388.648 | Struktur, Isomorphieklassen, Aut-Ordnungen und Vollständigkeit innerhalb der Censusbedingungen neu geprüft. |
| Generalize: sechs Musterausschlüsse | 4.686.633 | 2.702.015 | Original-Coverage-JSON; Beweise und Musterabdeckung übernommen. |
| One3: verbleibende Fälle mit genau einem Grad-3-Anker | 1.032 | 2.700.983 | Originalbelege: 48.252 Gesamtfälle, 47.220 vorher erfasst, 1.032 zertifiziert. |
| Generalize2: neue Muster und übernommene Pilotfälle | 2.466.285 | 234.698 | Original-Coverage-JSON; Vereinigungsabdeckung übernommen. |
| Two3: sieben verbleibende Fälle mit genau zwei Grad-3-Ankern | 7 | 234.691 | Originalbelege und Abschlussaudit vom 01.10.; kein neuer Checker-Replay. |
| seed_172_step_45 | 228.040 | 6.651 | Übernommener unabhängig DRAT-geprüfter Ausschluss. |
| A=seed_042_step_44 und B=seed_172_step_49, Vereinigung | 6.245 | 406 | Übernommene geprüfte Ausschlüsse und Coverage. |
| C=seed_172_step_47 | 188 | 218 | Übernommener geprüfter Ausschluss und Coverage. |
| Rest218, Trim/cake | 217 | 1 | Abschlussaudit: Metadaten, Formelrekonstruktion und Belegzuordnung. |
| p525910250893, direktes cake-Zertifikat | 1 | 0 | Direkter Checkerbeleg vom 11.10.2026; im Abschlussaudit ergänzt. |

Die separate Two3-Population umfasst 361.069 Fälle; 361.062 waren bereits durch
Muster erfasst. Ihre Differenz von sieben ist daher eine zusätzliche Abdeckung,
keine Addition der gesamten Two3-Population zur obigen Kette.

Der Rest218-Abschlussaudit ist unverändert unter
[rest218_abschlussaudit.json](../../results/c2_completeness_20261012/rest218_abschlussaudit.json)
abgelegt. Er prüfte Metadaten, alle 218 Formeln aus Basis plus 42 Units und deren
Belegzuordnung. Er führte nicht sämtliche Checker neu aus und las die externen
Beweisarchive nicht erneut. Die vorherigen Coverage-Stufen wurden übernommen.

## 4. Neu verifizierte Mengenverknüpfung

Eine neue vollständige Gegenprüfung bestätigte:

1. Die ursprüngliche Liste `remaining_234691.tsv` enthält 234.691 unterschiedliche Codes.
2. Jeder ihrer Datensätze steht **einschließlich aller Metadaten unverändert** im wiedergefundenen Census.
3. Alle 218 Datensätze der ursprünglichen Rest218-Liste stehen unverändert in `remaining_234691.tsv`.
4. Die drei Listen haben die historisch belegten SHA-256-Werte.

Die Zahl der Grad-3-Anker in der Rest234691-Liste verteilt sich wie folgt:

| Anzahl Grad-3-Anker | Datensätze |
|---:|---:|
| 3 | 826 |
| 4 | 13.935 |
| 5 | 64.772 |
| 6 | 104.941 |
| 7 | 50.217 |
| Summe | 234.691 |

Beleg: [reduction_checks.json](../../results/c2_completeness_20261012/reduction_checks.json).
Diese Teilmengenprüfung beweist noch nicht, dass jede Restliste **genau** das
Komplement der vorherigen Musterabdeckung ist. Dafür sind Muster, Transport und
Abdeckungsalgorithmus gesondert zu prüfen.

## 5. Offene Übergänge

- Unabhängiges Review der neu hergeleiteten Encoderadäquanz und C4-/Profile46-Filterbindung.
  Die Formel-, Transport-, Census- und Belegprüfungen dazu sind abgeschlossen; die
  historischen Beweischecker und 2.170 externen Profile46-Beweise wurden nicht erneut geprüft.
- Exakte Komplementbildung jeder historischen Coverage-Stufe, einschließlich Überschneidungen.
- Korrekte Bindung der weiteren historischen Formeln und Kerne an die jetzt
  hergeleitete Adäquanz von F0/F46/F346 und an die tatsächlich verwendeten Variablen.
- Durchgehende Bindung der früheren Zertifikate an die konkret transportierten Musteraussagen.
- Ausschluss oder anderweitige vollständige Behandlung der niedrigen Ankergrade 0, 1 und 2.

Ein erfolgreicher Abschluss der ersten vier Punkte würde den vollständigen
Profil346-Ausschluss tragen. Der letzte Punkt ist zusätzlich für den allgemeinen
C2-Satz erforderlich. Diese Punkte sind Prüfaufträge, keine festgestellten Fehler.
