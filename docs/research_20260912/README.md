# Reproduktion und Review

Startpunkt ist [BERICHT.md](BERICHT.md). Alle neuen Skripte liegen in `src/research_20260912`, Ergebnisse in `results/research_20260912`. Sie sind Forschungswerkzeuge und starten keinen Produktionscontroller. Befehle aus dem Projektwurzelverzeichnis ausführen. Ein Ergebnislauf überschreibt seine eigene Ergebnis-JSON; für einen bytegenauen Vergleich vorher eine Kopie behalten. Zeitbegrenzte Solverläufe können auf anderer Hardware andere offene Fälle oder Zeugen liefern. Maßgeblich für den berichteten Ausschluss sind die gespeicherten exakten Zertifikate.

## Sofortige exakte Prüfung ohne Installation

`python3 src/research_20260912/replay_tau6_exact.py`

Erwartet: `PASS_STDLIB_EXACT_116_EXCLUSIONS`, 156 Klassen, 32768 beschriftete Graphen, 116 ausgeschlossen, 40 verbleibend. Dieses Skript benutzt weder Optimierer noch Gleitkommazahlen. Es rekonstruiert die vier Dualprüfungen unabhängig vom MILP-Builder. Der mathematische Übergang vom Quotienten zum notwendigen Modell bleibt im Bericht zu prüfen.

## Weitere Umgebung

Python 3.12 wurde verwendet. Die beim Abschluss erfassten Paketversionen stehen in `requirements.txt` und `results/research_20260912/environment.json`. Frühere Kontrollen liefen teilweise vor Erweiterung des lokalen Paketverzeichnisses; die Datei ist kein Beleg für eine während der gesamten Sitzung unveränderte Umgebung. Leistungszahlen sind keine Hardwareprognose.

`python3 -m venv .venv-research`

`.venv-research/bin/python -m pip install -r docs/research_20260912/requirements.txt`

Danach jeweils `.venv-research/bin/python` anstelle von `python3` verwenden.

## Exakte Algebra und Bewertungsprüfung

`python3 src/research_20260912/f3_lift.py`

`python3 src/research_20260912/audit_omega.py`

`python3 src/research_20260912/benchmark_memetic.py`

`python3 src/research_20260912/profile_search_cost.py`

`python3 src/research_20260912/crossover_audit.py`

Die letzten drei sind begrenzte lokale Experimente. Bewertungs- und Kostenpilot benötigen zusammen typischerweise Minuten, abhängig vom Rechner; dies ist keine Zusage einer festen Laufzeit. Der Rangtest beweist nur die Unmöglichkeit des konkreten ausgerichteten Mischraums.

Ein vorhandener exakter 33×33-Quotient kann als JSON-Liste von Zeilen an `f3_lift.py --quotient-json PFAD` übergeben werden. Ungültige Quotienten werden abgewiesen. Ohne Argument werden ausschließlich Kontrollen ausgeführt, keine Conway-Lösung gesucht.

## τ=6-Scout neu erzeugen

`python3 src/research_20260912/tau6_aggregate.py`

`python3 src/research_20260912/tau6_verify.py`

Diese beiden Skripte verwenden numerische Optimierer zur Zeugenfindung; ihre abschließenden Zertifikatsprüfungen sind exakt. Ein erneuter Scout kann andere Zeugentypen ergeben. `replay_tau6_exact.py` ist bewusst der Prüfer der mitgelieferten 116-Ausschluss-Instanz und verlangt genau deren Ergebniszahl; bei einem neuen besseren Scout muss die neue Anspruchszahl separat überprüft und dokumentiert werden.

## Veröffentlichte Tabelle

Die vollständige fremde Publikation wird nicht erneut verteilt. Der Downloadhelfer lädt die Originaleingaben und verlangt ihre im Manifest gespeicherten Hashes. Bei geänderter Quelle bricht er ab; nicht den Hash ungeprüft anpassen.

`python3 src/research_20260912/fetch_paper_inputs.py`

`python3 src/research_20260912/audit_reimbayev.py`

Erwartet: 208 Gleichungen in allen Darstellungen gleich, Summendefizit 94034160. Es wird keine reparierte Einzelgleichung behauptet.

## f27, externe Beweise

Das fixierte Repository und ein gebautes `drat-trim` werden separat benötigt; große Beweise werden nicht dupliziert. Repository klonen und auf `e8f4d629cdf03b4bb14ebed01e4ebe7e8dbf3f8b` auschecken. Anschließend:

`python3 src/research_20260912/replay_f27.py /PFAD/ZU/f27 /PFAD/ZU/drat-trim`

Der Wrapper regeneriert zusätzlich die sechs Ausgangs-Gram-CNFs bytegenau, bevor er den vollständigen frischen Upstream-Audit aufruft. Der vorhandene Auditlog steht unter `data/research_20260912/f27-audit.log`. Diese Reproduktion ist kein LRAT/Cake-Abschluss der Graph-zu-Modell-Kette.

## K66, originale Eingaben

Benötigt wird das entpackte `Conway99_PromptA_Audit_20260912.zip`. Der SHA-256 steht in `data/research_20260912/input_manifest.json`. Das Paket enthält die großen Original-CNFs und wird hier nicht dupliziert.

`python3 src/research_20260912/k66_plans.py /PFAD/ZUM/ENTPACKTEN/PromptA`

Dies erzeugt die vier Pläne und Abdeckungsdateien neu und prüft Original-CNF-Hashes, Profilidentitäten und geordnete RUP-Hinweise. Keine Blatt- oder Brückenbeweise werden dadurch erzeugt. Der Prüfer in diesem Skript ist ein Python-Prüfer, kein frischer Cake-Lauf.

Für den gesonderten erneuten Durchlauf der originalen gekoppelten Bäume verwendet man die im PromptA-Paket enthaltenen `verify_coupled_roots.py` beziehungsweise `verify_coupled_pilot.py` mit den dort dokumentierten Argumenten. Die Berichtszahlen sind in diesem Forschungslauf nachgeprüft worden.

## Paketinhalt und Herkunft

Das Reviewarchiv enthält die neuen Forschungsdateien sowie die benötigten unveränderten `src/memetic_v2/core.py`, `operators.py` und Referenzdaten vom angegebenen Basiscommit. Es enthält keinen Office-Controller und keine vollständige Kopie des Projekts. Ein Dateimanifest im Archiv sichert die enthaltenen Bytes. Eigene Änderungen sind im separaten Forschungszweig dokumentiert. Für die gesamte Originalhistorie ist das Git-Repository maßgeblich.
