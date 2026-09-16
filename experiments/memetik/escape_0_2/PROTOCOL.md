# Escape-Fortsetzung 0.2.1

Basis: memetik `abc752d04bd0d72c3fd83fe8aaf4fe5ae3caa37e`. Kern und bisherige Generatoren bleiben byteidentisch zu Escape 0.1.0. Neu sind Suchsteuerung, Reparaturmodelle, Symmetrieanalyse und Ergebnisprüfer. Kein Populationspilot und keine Änderung der Ryzen-Prozesse.

## Reihenfolge und Definitionen

1. Vollständige ungerichtete Automorphismengruppen der 14 angenommenen KI-Kandidaten und acht Escape-Gründer; keine Farben. nauty-Vollständigkeit, zusätzliche direkte Kontrolle aller ausgegebenen Generatorpermutationen. Keine Isomorphiequotienten in der Pfadsuche.
2. A: alle H-Kanten als Boolesche Variablen, Ω-Randbedingungen, expliziter Ausschluss der acht bisherigen Zustände. CP-SAT mit begrenzter Kantendistanz; alternativ MILP mit Kantendistanz als Ziel. Separater CP-SAT-Ansatz fixiert alle Kanten außerhalb eines ausdrücklich gespeicherten induzierten Fensters. Keine zusätzlichen Symmetrien oder Konstruktionsschablonen. UNKNOWN und zeitbeendete Rechnungen liefern keinen Ausschluss. INFEASIBLE gilt ausschließlich für das konkrete Modell und ist hier nicht extern proof-zertifiziert. Ein bekannter Graph als Hint wird als solcher ausgewiesen.
3. C08/W: Breitensuche durch W-neutrale Zustände, Ende beim ersten strikt verbesserten Ausgang. Keine Behauptung einer geschlossenen neutralen Gesamtkomponente bei gefundenem Ausgang. Die erste gefundene Weglänge ist minimal unter neutralen Präfixen. Eine globale Minimalitätsaussage bei Länge zwei folgt zusätzlich aus der vollständig erfolglosen direkten Nachbarschaft.
4. HoG57338/F und B_original/W: echte Breitensuche ohne Schranke für zwischenzeitliche Zielfehler. Jede Schicht wird vor der nächsten expandiert. Minimale gefundene Weglänge gilt nur im implementierten Katalog. Die Barriere ist die höchste Zielfehlerzunahme gegenüber dem Start auf genau diesem Zeugen; keine Behauptung minimaler Barriere.
5. C02, B_end_F und lambda_Linf2: jeweils deterministischer steilster Abstieg für L1, F, Linf-Tupel sowie W als Diagnose. Gleichstand nach graph6 sortiert. Jeder Schritt benötigt vollständige Enumeration aller Familien. Ein strikt lokales Minimum wird **nicht** behauptet: LOCAL_MINIMUM_VERIFIED bedeutet kein strikt verbessernder Nachbar; neutrale Nachbarn können bestehen. W fügt keinen Populationsselektionsarm hinzu.

Familien werden in jedem Zustand neu erzeugt. Ω: 4x4/4x6/6x6, λ: Apex/Rotation. Identität ist der ganze graph6-String mit UNIQUE-Constraint, nicht ein Hash allein. Unterschiedliche Beschriftungen bleiben getrennt. Keine symmetriebedingte Beschränkung der Mutationen.

## Ressourcen und Betrieb

Office-Zipapp erfordert nur Python 3.10+ unter Linux, kein pip. Standard: drei Prozesse, je 768 MiB Adressraum, 3600 CPU-Sekunden je Aufgabe, 50.000 Zustände je Breitensuche, maximale BFS-Weglänge vier, maximal 1000 Abstiegsschritte. Insgesamt 15 Aufgaben: höchstens 15 CPU-Stunden, idealisiert fünf Stunden bei drei voll ausgelasteten Prozessen; keine garantierte Wandzeit oder Lösungs-ETA. Frühe Erschöpfung endet sofort. Unter 512 MiB systemweit verfügbarem RAM oder 10 GiB freiem Datenträger wird die betroffene Aufgabe kontrolliert unvollständig beendet.

`start` trennt eine neue Prozesssitzung ab und leitet Ein-/Ausgabe in den Laufordner. SIGHUP wird ignoriert; Ausschalten von WSL/Windows kann Prozesse dennoch beenden. Status alle zehn Sekunden, Konsolenausgabe spätestens alle zehn Minuten einschließlich restlichem CPU-Kontingent. Ein Laufverzeichnis ist durch flock gegen parallele Controller geschützt.

Atomare JSON-Dateien mit fsync. Jede vollständig abgeschlossene Expansion wird als eigene SQLite-Transaktion gesichert. Version 0.2.1 verwendet DELETE/Rollback-Journal statt WAL: abgeschlossene Daten stehen in einer Datenbankdatei. Bei Abbruch wird nur die laufende Expansion erneut berechnet. CPU-Verbrauch zwischen letztem Zehnsekundenstatus und hartem Abbruch ist höchstens näherungsweise erhalten. Wiederaufnahme verlangt identische Konfiguration, Version und Quellenmanifest. Abgeschlossene Budgetaufgaben werden nicht automatisch mit neuer Zeit neu gestartet; für größere Budgets einen neuen Lauf anlegen. Laufende Datenbanken nicht ungeprüft kopieren.

## Ergebnisstatus

- IMPROVEMENT_FOUND: geprüfter Pfad, Länge und Barriere; keine Komponentenerschöpfung.
- LOCAL_MINIMUM_VERIFIED: alle Familien am Abstieg-Endpunkt erschöpft, kein strikt besserer Nachbar.
- COMPONENT_EXHAUSTED: alle im betreffenden Suchmodus zugelassenen Zustände expandiert. Bei neutralem Modus betrifft dies ausschließlich die neutrale Komponente.
- DEPTH_LIMIT: alle Wege bis zur angegebenen Länge bewertet, kein verbessernder Endpunkt; keine globale Unmöglichkeit.
- CPU_BUDGET, STATE_LIMIT, DESCENT_STEP_LIMIT, DISK_FLOOR, SYSTEM_MEMORY_FLOOR, MEMORY_LIMIT: unvollständig. Bereits vollständig expandierte Schichten werden gesondert angegeben.
- ERROR / WORKER_ERROR: technischer Fehler, kein Negativbefund.

Bei Linf wird (Linf,Nmax,L1) lexikographisch verglichen; komponentenweise Änderungen werden getrennt gespeichert. Ein numerischer skalarer Barrierenwert wird für dieses Tupel nicht erfunden.

## Optionale Analysewerkzeuge

`symmetry_audit.py` und `neutral_diversity.py` benötigen pynauty. `repair.py` und `repair_window.py` benötigen OR-Tools; `repair_milp.py` SciPy. Diese Werkzeuge sind separat im Git-Quellverzeichnis und werden nicht heimlich auf Office installiert. Gemessene Laufversionen stehen in den Ergebnissen. Die Office-Zipapp führt ausschließlich Pfadsuchen und Abstiege aus.

Alle neuen Pfade werden zusätzlich mit `verify_results.py` geprüft: eigener graph6-Decoder, Mengendarstellung, harte Arm-Bedingungen, sämtliche Zielwerte, Kantenübergänge und Barrieren. Steuerungstests betreffen nur neue Risiken: Schicht-/Barrierenrechnung, neutrale Beschränkung, unvollständige Expansion und echte Prozessunterbrechung mit Wiederaufnahme.
