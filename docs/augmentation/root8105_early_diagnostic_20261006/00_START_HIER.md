# Frühe Diagnose abgeschlossen: 960 gespeicherte Pfade

Vorabplan und Auswahl veröffentlicht in cff611b49f33dda61e54174b3430b9db9401a3b4.
40 zufällig ohne Zurücklegen ausgewählte Pfade je24 Pilot-Root; Tiefe2/3.
M bleibt fest, spätere Propagation A wird nicht übernommen. Keine neuen Abstiege.

| Test | Tiefe2 | Tiefe3 |
| --- | ---: | ---: |
| R: positive Pfade | 960/960 | 958/960 |
| R+LD: positive Pfade | 960/960 | 958/960 |
| Gewichteter verbleibender Anteil, beide Tests | 100% | 99,9986629% |
| Geschätzte verbleibende Ebenenknoten je Pilot-Root | 9,34694e7 | 7,70040e12 |
| Gewichts-ESS der Stichprobe | 664,35 | 427,56 |
| Größter Gewichtsanteil | 0,2849% | 0,4689% |

Die letzten vier Zeilen sind Punktschätzungen/Diagnosekennzahlen, keine Schranken.
Rootgeschichtete Mittel und ursprüngliche Pfadgewichte; keine Hochrechnung auf8105.
Bei Tiefe3 ist der Test der Vorstufe explizit im Pruningprädikat enthalten.
Die119 alten Endpunkte wurden nicht beigemischt. Keine Bisektionsmonotonie behauptet.

Zwei konkrete frühe Präfixe scheitern: Root51/Pfad318 und Root210/Pfad21,
jeweils Tiefe3, offene Zielzeile32. Beide R-Widersprüche sowie ihre LD-Varianten
sind RUP-geprüft: vier Zertifikate, aber nur zwei verschiedene tote Präfixe.
Kein Rootausschluss. Die positiven Fälle besitzen insgesamt312756 gespeicherte,
direkt geprüfte Zeilenzeugen; darin sind wiederverwendete R-Zeugen für LD enthalten.
Die Zahl bezeichnet nicht312756 unabhängige Solveraufrufe.

## Fachliche Konsequenz

In dieser Stichprobe beschneidet der frühe gemeinsame Einzeilentest praktisch
keine gewichtete Masse. Ein Restanteil in der Nähe von10^-5 wird durch diese
Punktschätzung nicht gestützt; insbesondere lässt sich damit keine tragfähige
zeilenweise Erschöpfung begründen. Das unterstützt die strategische Priorität
für Klassen-SAT. Es widerlegt keine wesentlich anderen Zeilenverfahren und
beweist weder Härte noch Erfolg von N1. Kein zusätzlicher tiefer Diagnose- oder
Importance-Lauf wird aus diesem Ergebnis abgeleitet.

## Belege und Betrieb

EVIDENCE_960.zip: sämtliche ausgewählten Präfixe und Ganzzahlzeugen, vier
CNF/RUP-Belege, Zusammenfassung, RAW_RECEIPT und neuer Hashabschlussbeleg.
Die komprimierte Zeugenfassung lässt nur redundante bereits ausgewertete
Rand-/Paarsummen weg; alle ausgewählten Nachbarn und Bedingungen bleiben erhalten.
CALIBRATION_96.zip erhält die erste Stufe einschließlich ausgeführter Quelle.
OPERATIONS.md und POOL_CONTROL.json dokumentieren Fehler, Korrektur und Grenzen.

Letzter Fortsetzungsaufruf:295,757 CPU-s. Summe abgeschlossener Pfadmessungen
über alle Aufrufe:698,837 CPU-s. Spitzen-RAM letzter Aufruf:623792KiB.
Diese Größen sind keine lückenlose Gesamtverbrauchsangabe; die CPU-Schlussbuchung
des technisch unterbrochenen Aufrufs fehlt. Das ist ausdrücklich offengelegt,
keine Nullbuchung. Keine Zeitbudgeterhöhung oder automatischer Budgetabbruch.
Keine Zielhardwareprognose. Nutzerprozesse unverändert.

Nächster fachlicher Schritt: neuer N1-Encoder und Kontrollen, dokumentiert in
../root8105_n1_20261006. GC-08/16/17/19/20/22/23 beachten.
