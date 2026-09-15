# Auslieferungsprüfung Escape 0.1.0

Alle acht Gründer und beide übernommenen Module stimmen mit den festgehaltenen Git-Blob-IDs überein. Harte Bedingungen und vollständige Eingangsmetriken unabhängig über Nachbarmengen bestätigt.

Während der Implementierung wurden zwei Laufsteuerungsfehler gefunden und behoben: JSON-Histogrammschlüssel beim Vergleich vereinheitlicht; beim Fortschrittsbericht die Aufgabennamen statt Future-Objekte verwendet. Ein erster abgetrennter Sandbox-Prozess wurde beim Ende seines Werkzeugaufrufs abgeräumt; dies war kein erfolgreicher Starttest. Anschließend wurde der Start mit Bereitschaftsmeldung und innerhalb eines weiterlaufenden Testprozesses vollständig geprüft.

Endgültiger Logiktest als Zipapp: drei Worker, 0,1 CPU-Sekunden je Familie, 20 Aufgaben, CENSUS_FINISHED, vier erschöpfte und 16 offene Aufgaben. 24 gespeicherte kriteriumsbezogene Verbesserungszeugen aus Ursprungsgraph und Trade rekonstruiert; sämtliche harten Bedingungen, Prüfsummen, vollständigen Scores und strikten Verbesserungen bestätigt. Die Zahl 24 zählt Kriterienzeugnisse und muss nicht 24 verschiedene Graphen bedeuten. Testlauf und Zeugen unter tests/short_run im Git-Verzeichnis dieser Version.

Der Kurzlauf dient der Funktionsprüfung, nicht der Nachbarschaftsvollständigkeit oder Durchsatzprognose. Bereits gefundene Ein-Schritt-Verbesserungen zeigen, dass einige Starts, darunter Codex-C02, noch keine lokalen Minima sind. Es werden keine mehrschrittigen Fluchtlängen behauptet.
