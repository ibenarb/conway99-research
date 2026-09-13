# C2-Referenzencoder 1.0.0

Status: implementiert, endliche Kodierungskontrollen bestanden, 99-Knoten-CNF erzeugt und reproduziert. Keine Produktionssuche, kein neues UNSAT-Zertifikat, kein Symmetrieausschluss.

## Dateien

- `src/c2_reference_20260913/c2_reference.py`: vollständiger deterministischer Encoder und direkter Graphprüfer; nur Python-Standardbibliothek.
- `src/c2_reference_20260913/test_reference.py`: unabhängiger kleiner DPLL-Prüfer, Projektions- und Dateikontrollen.
- `src/c2_reference_20260913/prepare.py`: führt Kontrollen, Erzeugung und Dateiprüfung aus; startet keinen Produktionssolver.
- [Allgemeines Korrektheitsargument](ENCODER_BEWEIS.md).
- `results/c2_reference_20260913/`: Kontrollberichte, Manifest und Erwartungshashes.
- `data/c2_reference_20260913/c2_reference_v1.zip`: flaches Vorbereitungspaket; die großen CNFs werden vor Ort erzeugt.

## Endgültige 99-Knoten-Instanz

| Größe | Wert |
|---|---:|
| Primäre Variablen | 1722 |
| Variablen einschließlich Hilfsvariablen | 570171 |
| Klauseln | 1990821 |
| Dateigröße einer CNF | 42747960 Bytes |
| Zusätzliche Matchingklauseln nach Normalisierung | 0 |

SHA256 beider CNFs: `f9d6011c5e6eb8a0fab971fa324d159e94b8bc4526b7b17dc31ee55aee1c25ba`.

Die Matchingbedingung ist nach Kürzen des Faktors 2 bereits eine E3-Gleichung. Beide Varianten sind byteidentisch. Der zuvor erwogene Matchingvergleich wird deshalb nicht als Ryzen-Kampagne gestartet.

## Vorbereitung auf dem Ryzen

Python 3 genügt; keine neuen Pakete, keine Installation eines Solvers. Das flache Paket enthält die drei Skripte nebeneinander. `prepare.py` erzeugt ein neues datiertes Verzeichnis unter `~/conway99_workspace/c2_reference_v1/`, prüft beide CNFs gegen feste Hashwerte und meldet `C2_REFERENCE_PREPARED`. Alternativ funktioniert derselbe Aufruf im Git-Checkout über den Pfad unter src.

`python3 src/c2_reference_20260913/prepare.py`

Erwarteter Zeitrahmen auf dem Ryzen: einige Sekunden bis wenige Minuten, konservativ bis drei Minuten für Erzeugung und vollständiges Lesen. Dieser Rahmen betrifft keine SAT-Suche. Beide Dateien zusammen benötigen rund 86 MB; bei Erzeugung kommen temporäre Daten hinzu. Das Vorbereitungsskript verlangt mindestens 256 MiB freien Plattenplatz. Vorhandene nichtleere Ergebnisverzeichnisse werden nicht überschrieben. Keine Änderung an laufenden Forschungsprozessen.

## Einzelne Funktionen

Die folgenden Aufrufe sind Dokumentation, kein Auftrag, mehrere Schritte ungeprüft nacheinander auf dem Ryzen auszuführen.

Erzeugung in ein neues oder leeres Verzeichnis: `python3 src/c2_reference_20260913/c2_reference.py --k 14 --out /tmp/c2_new_run`

Kleinfall: denselben Aufruf mit `--k 4` und einem anderen Ausgabeverzeichnis verwenden.

Prüfung einer SAT-Ausgabe: `python3 src/c2_reference_20260913/c2_reference.py --k 14 --model /path/to/solver.log --out /tmp/c2_checked_graph`

Die Ausgabe muss vollständige primäre Belegungen in DIMACS-v-Zeilen enthalten. Fehlende Bits werden nicht geraten. Ein bestandener Graphcheck ist ein direkt geprüfter Graph; er ist kein UNSAT-Zertifikat.

## Anschluss an den Forschungsplan

Nächster Schritt ist ein begrenzter Baseline-Pilot mit der vorhandenen verlässlichen CaDiCaL/Cake-Kette und real gemessenen Ressourcen. Seine ausführbare Steuerung ist in diesem Vorbereitungspaket noch nicht enthalten. Für längere Suche sind Status und ETA mindestens alle zehn Minuten, explizite Pilotbudgets, sichere Ergebnisablage und spätere Beweisprüfung vorzusehen. Eine Gesamtlaufzeit bis zum C2-Ausschluss ist weiterhin unbekannt.
