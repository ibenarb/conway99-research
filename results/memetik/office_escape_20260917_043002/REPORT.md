# Office Escape 0.2.2 – Abschluss und Audit, 17.09.2026

## Eingang und Sicherung

Original: Ergebnisse_Escape_022_continue_20260917_043002_073517.zip.
89.706.888 Bytes; SHA256 `18723e6b853bdeeb522cef271ebdd451805c7af755aa5ea7c827d314fbf9b440`.
Pruefsumme stimmt mit der Office-Ausgabe ueberein. ZIP-CRC aller zehn Eintraege bestanden.
Original unveraendert lokal als original.zip archiviert und als hochgeladenes
Artefakt dauerhaft verfuegbar. Dieser Git-Bericht und die kleinen Begleitdateien
enthalten NICHT die SQLite-Rohdaten. Das Original-ZIP ist noch nicht auf Git veroeffentlicht.
Die Version 0.2.2 und fruehere Pruefungen liegen im noch nicht gepushten lokalen
Commit 6fee6d9420e4bb682bed304b4c44aab0e6fd889b.

## Ergebnis und Aussagegrenzen

| Aufgabe | Status | Zustaende | Expandiert | Vollstaendig bewertete Weglaenge |
|---|---|---:|---:|---:|
| HoG57338/F | DEPTH_LIMIT | 264378 | 19585 | 4 |
| B ab W=2082 | CPU_BUDGET | 369992 | 2955 | 2 |

Kein gespeicherter HoG-Zustand hat F<2836; kein gespeicherter B-Zustand W<2082.
HoG: alle Tiefen 0–3 expandiert, 244793 Zustaende in Tiefe 4 bewertet.
B: alle Tiefen 0–1 expandiert; 2685 von 34597 Zustaenden der Tiefe 2 expandiert.
335125 Zustaende in Tiefe 3 entdeckt; diese Schicht ist unvollstaendig.
Damit hat ein etwaiger Verbesserungsweg im implementierten Katalog bei HoG
mindestens fuenf, bei B mindestens drei Schritte. Keine Existenzbehauptung.
Keine Gesamtkomponente geschlossen; beschriftete Zustaende sind keine Isomorphieklassen.
Die frueher gepruefte notwendige HoG-Barriere >=88 ist eine gesonderte Aussage;
sie wurde in dieser Sitzung nicht neu enumeriert.

## Tatsaechlich ausgefuehrte Pruefung

- Ausgelieferte Zipapp: Manifest und enthaltene Quellen stimmen ueberein.
- Beide SQLite-Dateien: integrity_check=ok; Endresultat in SQL, Aufgaben-JSON
  und summary.json identisch; Konfiguration und Gruenderidentitaet stimmen.
- Alle Schichtenzahlen, Eltern-IDs/Tiefen und die expandierte BFS-Praefixmenge geprueft.
- Jeder gespeicherte Zensus eines expandierten Zustands meldet saemtliche
  erwarteten Operatorfamilien vollstaendig.
- Alle 99995 importierten HoG-Zustaende, ihre Eltern/Wege/Metriken und die
  6258 bereits abgeschlossenen Expansionen sind erhalten. Alte Datenbank per Hash identifiziert.
- Je Aufgabe 32 deterministisch ausgewaehlte Zustands-IDs: unabhaengige
  mengenbasierte Arm- und Scorepruefung sowie Rekonstruktion des Elternuebergangs;
  Eltern ebenfalls unabhaengig geprueft. Alles PASS.

Keine unabhaengige Neuberechnung aller 634370 Graphen und keine vollstaendige
Wiederholung aller Nachbarschaften. Vollstaendigkeitsaussagen beruhen auf
gepruefter Suchlogik und konsistenten gespeicherten Zensen, nicht auf einem
externen formalen Beweiszertifikat. Stichprobe ist kein Ersatz fuer Vollpruefung.
Reproduktion: audit.py mit --run-dir (entpacktes neues ZIP), --old-run
(entpackter Original-Office-Lauf 0.2.1), --verifier-dir (dieses Verzeichnis),
--output (neue Ausgabedatei). Originaldatenbanken werden nur lesend geoeffnet.

## Betriebsbefunde

Die Felder discovered_committed/expanded_committed enthalten beim Abschluss
noch Werte des letzten Zehnsekundenberichts. discovered/expanded und depth_counts
werden zum Abschluss direkt aus SQL neu gelesen und sind hier bestaetigt.
Kein Datenverlust. Anzeige sollte in einer kuenftigen Version angeglichen werden.
Die Restbudgetanzeige teilt weiterhin durch konfigurierte Workerzahl zwei,
auch wenn nur noch ein Worker aktiv ist. Sie unterschaetzt dann die Restdauer.
Keine nachtraegliche Aenderung der verwendeten Zipapp oder der Originaldaten.
CPU_BUDGET ist ein Ressourcenende, kein Unmoeglichkeitsbeweis.

## Naechste Forschungsentscheidung

Keine Wiederholung der abgeschlossenen Schichten. B koennte mit neuem Budget
ab vorhandener Frontier fortgesetzt werden, benoetigt aber eine explizite,
getestete Checkpointkopie mit neuer Konfiguration; resume erweitert das Budget nicht.
HoG benoetigt fuer weitere Breitensuche ein hoeheres Tiefenlimit und ebenfalls
explizite Migration. Ein blosser erneuter Start von 0.2.2 setzt nicht hier fort.
Zunaechst bevorzugt: die gespeicherten Zustaende auf niedrigere Fehlerbarrieren
und strukturelle Wiederholungen auswerten, bevor Tiefe 5 pauschal expandiert wird.
A-Operatorerweiterung und C08-Neutralkomponente bleiben eigenstaendige offene
Aufgaben. Noch kein neuer produktiver Lauf vorbereitet oder gestartet.
