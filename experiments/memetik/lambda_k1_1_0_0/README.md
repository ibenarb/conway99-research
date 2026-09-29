# Conway99 λ K1 1.0.0

Neue Kampagne, Referenz b9f215a4fb3a7824d71870743c38d1657b963d43.
520 Aufgaben, 624 CPU-Stunden Suchziele, bis12 Single-thread-Worker.
672 CPU-Stunden harte Kampagnengrenze einschließlich24 CPU-Stunden Aux
und expliziter Nachlaufreserven. Harte aktive Windows-Walltime96h.
Keine Garantie, dass alle Suchziele bis dahin ausgeschöpft werden.

A:32 Klassen×2 Katalogarme×45min CPU=48CPUh. Alle8 neuen Stern-Endpunkte
sind enthalten; aus dem alten25er Pool wird die schlechteste Klasse nach
(W,L1,state) ausgelassen. AP versus AP+vollständiger Sternkatalog, identische
iterierte Steilstabstiegs-/Perturbationspolitik. Keine Behauptung einer
Reproduktion der historischen Populationsmemetik P.
B:48 eingefrorene60er Fenster×2 Seeds×4 Varianten×1h=384CPUh.
LP0/LP2 gekreuzt mit freier Maske/festem Hammingball Radius16. Zentrum,
Hint, Ziel und Modell innerhalb jedes Vergleichs gleich, kein Rezentrieren.
C1:24 Elternpaare×D/zufällige Kontrollmaske×2h=96CPUh. Kontrollmaske hat
identische Anzahl vorhandener/fehlender variabler Kanten. Beide Eltern
liegen in D; optimierte Isomorphieausrichtung wird nicht behauptet.
C2:12 Gründer×Packing-Tabu/λ-Suche+Greedy-Projektion×4h=96CPUh.
Packings erfüllen CN(Kante)<=1, CN(Nichtkante)<=2 und zusätzlich Grad<=14.
693 Kanten würden das exakte Ziel ergeben. Greedy-Löschung liefert eine
obere Schranke für nötige Löschungen, kein zertifiziertes Minimum.

Sämtlicher Aufbau, Scoring, Projektion und Suchbetrieb zählen zur jeweiligen
Task-CPU. Zusatzkontrollen und Kalibrierung liegen auf Aux. Kein stiller
Budgettransfer. Arme werden vorab festgelegt interleaved gestartet.
Eine saubere Wiederaufnahme nach Nutzerpause erhält CPU und beste Graphen;
Solver-/Zufalls-/Tabuzustände werden neu gestartet. Entsprechende Vergleiche
müssen als unterbrochene Versuche markiert werden.

Status alle10min: datierte Momentaufnahme, echte Windows-Stopwatch, CPU via
/proc und wait4; Gastzeit nur Diagnostik. ETA ist Budgetprojektion/Schätzung,
keine Fertigstellungsgarantie. 30CPU-s Nachlauf pro Versuch,120 pro Aufgabe,
5s Mess-/Endabrechnungstoleranz; tatsächliche CPU vollständig verbucht.
Lokale Workerfehler isoliert; Integritäts-/Ressourcenprobleme stoppen global.
RAM24GiB Gruppe,6GiB Startreserve,2GiB kritische Reserve,25GiB Diskreserve.

Start ausschließlich mit vorhandenem venv lambda-repair-1.0.0, Python3.12.
Keine Installation, kein Umbau älterer Läufe. Frischer Ordner
ryzen_lambda_k1_100_20260929. Der Starter startet nach Hash-/Umgebungsprüfung
die Windows-Uhr-/Scheduler- und Mathematikkontrollen automatisch.

run.py: prepare/launch/status/pause/verify/export DIRECTORY.
CLI-Befehle nach Start stets aus dem eingefrorenen program-Verzeichnis.
Vor Export muss Lauf abgeschlossen/gestoppt sein; Export prüft alle Graphen,
Masken, Packings und CPU-Belege. Optimale Solverberichte sind unzertifiziert.

Relevante Lehren GC-01 bis GC-14 in docs/operations/GLOBAL_CONCLUSIONS.md.
Cloudprüfungen ersetzen nicht den eingebauten Windows-/WSL-Preflight.
