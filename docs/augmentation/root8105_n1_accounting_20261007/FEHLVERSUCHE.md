# Erhaltene Entwicklungsfehler

1. Beim ersten lokalen Syntaxcheck entstand durch eine Textersetzung `elf` statt
`elif`. Vor dem ersten Programmstart korrigiert. Kein Lauf und keine CPU-Aussage.
2. n1-accounting-runtime-01: Der UNSAT-Test lief durch; die nachgelagerte neue
Abrechnung wies 0,046269 s RUSAGE_CHILDREN gegen 0,046268 s Summe der beiden
wait4-Belege zurück. Eine Mikrosekunde Differenz überschritt wegen Gleitkommadarstellung
die zu knappe 1e-6-Bedingung. Alle Endbelege blieben erhalten. Abgleich jetzt mit
expliziten 10 Mikrosekunden Toleranz, Differenz unverändert im Bericht. Das alte
accounting.py wurde bytegenau rekonstruiert und gegen seinen damals gespeicherten
Quellhash geprüft; es liegt im Evidenzarchiv.
3. n1-accounting-final-1: Der Test für read-only-Recovery eines lebenden verwaisten
Workers verglich auch dessen parallel wachsende proof.partial. Die Assertion
scheiterte; der Test hinterließ den absichtlich gestarteten synthetischen Worker.
Dieser wurde über seine bekannte Laufidentität und STOP-Datei kooperativ beendet.
Der Vergleich schließt nun ausschließlich die vom laufenden Worker geschriebenen
Dateinamen aus; Konten und Steuerungsdateien müssen weiter unverändert bleiben.
Die alte Testquelle und sämtliche Fehllaufartefakte sind erhalten. Kein Beleg für
eine Schreibmutation durch Recovery und kein betroffener Nutzerprozess.

Zwischenabnahmen und abschließende Abnahme sind im Archiv getrennt. Die letzten
vier release-Verzeichnisse gehören zum veröffentlichten ausführbaren Code. Nach
der Abnahme wurden nur Dokumentation und Paketierung ergänzt. Die ergänzte
Verzeichnis-fsync-Sicherung wurde in der abschließenden Abnahme mit ausgeführt;
ein echter Stromausfalltest wird damit nicht behauptet.
