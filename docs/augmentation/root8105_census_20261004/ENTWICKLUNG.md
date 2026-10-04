# Entwicklungsprüfung und abgefangene Fehler

Diese Datei trennt vorläufige Tests von der finalen Paketprüfung.

1. Erste mathematische Kontrollrunde:152 SAT/DP/Vertex-Fälle und81 exhaustive
   Rangbijektionen bestanden. Danach scheiterte das Einlesen einer Reviewer-
   Fixture am Feldnamen: die Originaldatei verwendet `w`, nicht `widths`.
   Leser korrigiert; keine produktiven Counts betroffen.
2. Erster echter Resume-Test scheiterte an `/proc/<os.getpid()>`: Der
   Cloud-Supervisor verwendet virtuelle PIDs, `/proc` reale PIDs. `/proc/self`
   behob den Selbstzugriff, reichte aber nicht für Child-CPU-Zähler.
3. Bei manueller Sichtung der Zeitreihe fiel ein unmöglicher Rückgang der
   laufenden Gesamt-CPU auf (etwa37→7s). Ursache: Ein virtueller Child-PID
   traf einen fremden `/proc`-Prozess. Die endgültige Implementierung liest
   die vom Kind über `/proc/self` gemeldete reale Prozessnummer und Start-ID;
   Controller bestätigt beide. Ohne sichere Zuordnung wird kein fremder
   Livewert übernommen. Abschließendes `wait4` bleibt unabhängig davon.
   Vorläufige Betriebspässe vor dieser Korrektur sind kein finaler Beleg.
4. Der Abhängigkeitscheck des integrierten Preflight schlug korrekt fehl:
   nach einem Downgrade waren in der Cloud alte und neue dist-info-Verzeichnisse
   gleichzeitig sichtbar. Kein Produktionsstart. Frische Audit-Umgebung mit
   exakt gepinnten Versionen statt Vertrauen in die mehrdeutige Installation.

Endgültige Prüfergebnisse werden separat unter VALIDATION.json und in den
referenzierten Rohberichten gespeichert. Cloudkontrollen ersetzen keine
Ryzen-/Windows-/WSL-Kalibrierung. Der Windows-Stopwatch-Zweig muss auf dem
Ryzen geprüft werden; ohne verlässlichen Hostvergleich bleibt seine ETA unknown.

5. Erster integrierter66-Root-Lauf im synchronisierten Cloud-Workspace:
   Abschlusslog und JSON-Export meldeten66 Roots; bei anschließendem erneutem
   Datenbankzugriff waren64 Resultate und eine offene Sitzung sichtbar.
   Der Wiederanlauf verweigerte erwartungsgemäß die Fortsetzung. Ursache
   nicht abschließend bewiesen; konkurrierende Workspace-Snapshots bzw.
   SQLite-WAL-Synchronisation sind eine Arbeitshypothese. Rohzustand/Logs
   im Entwicklungsarchiv. Der vollständige Ablauf wird im isolierten/tmp
   und in einer einzigen Prozesskette wiederholt. Ein etwaiger PASS dieser
   Wiederholung validiert diesen Ablauf, nicht beliebige synchronisierte
   Dateisysteme. Produktiver Lauf unter WSL im Linux-Dateisystem.
