# Escape-Versuch: erste ausführbare Stufe

Am 15. September 2026 vom Nutzer vor den nächsten Populationspiloten priorisiert. Office-PC: acht logische CPUs, 4340 MiB verfügbarer RAM, 953,4 GiB frei, kein erkannter laufender memetischer Prozess.

[Protokoll und Auswertungskriterien](../../experiments/memetik/escape_0_1/PROTOCOL.md), [Auslieferungsprüfung](../../experiments/memetik/escape_0_1/TEST_REPORT.md), [Quellcode](../../experiments/memetik/escape_0_1/runner.py).

Acht Gründer, 20 getrennte Familienaufgaben, drei Worker, je maximal 3600 CPU-Sekunden. Zunächst die bestehenden unmittelbaren Trade-Nachbarschaften vollständig oder mit eindeutigem Offenstatus untersuchen. Dies ist keine bereits implementierte mehrschrittige Fluchtsuche. Direkte Verbesserungen liefern bessere Ausgangspunkte für den anschließenden Abstieg; erst vollständig geprüfte lokale Endpunkte eignen sich für Aussagen über notwendige größere Weglängen. Neutrale Plateaukomponenten werden in Stufe 1 nicht vollständig erkundet.

Auslieferung: `releases/Conway99_Escape_Office_0.1.0.pyz`, SHA256 `be307de46a569853e9da294dfa944d2e66afd65181de0d5c89890473a8318efb`. Keine zusätzlichen Python-Pakete. Startmodus löst den Prozess vom Terminal und meldet den Statuspfad. Lauf auf dem Nutzerrechner zum Zeitpunkt dieses Commits vorbereitet, noch nicht bestätigt gestartet. Keine Ryzen-Prozesse verändert.
