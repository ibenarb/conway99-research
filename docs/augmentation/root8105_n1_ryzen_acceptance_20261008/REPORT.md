# Ryzen-Abnahme Runtime 0.7.2, 08.10.2026

Quellcommit: 432ce75ed58b1d1ae62fbb0afc8407ae6f0b7bc3.
Originalarchiv (316 Dateien) unverändert; SHA256
0a9293787b48cc5f739f42df573b37c3051fefa33516a8a94b7b28c779f04d4c.

Offlineprüfung: 208 versiegelte JSON-Belege erfolgreich gelesen; unveränderte
accounting.inventory-Funktion auf den gespeicherten Originalidentitäten:
SAT 3 Sitzungen, UNSAT 3, Budgetkontrolle 7; keine fehlenden Endkonten, keine
offenen Sitzungen, vollständige Partition der erfassten CPU-Untergrenze.
Alle drei Laufmanifeste binden die veröffentlichten 0.7.2-Quellen und die
im Ryzen-BUILD.json ausgewiesenen Binärhashes. Keine erneute Suchrechnung.
Die Binärdateien selbst sind nicht im Rückgabearchiv; kein eigener Neubau.

PLATFORM_PROBE: sechs verschiedene Hostsequenzen 0 bis 5, vollständiger
Hostabschluss ohne Fehler. TARGET_CONTROLS: kleine SAT-Kontrolle mit geprüftem
Modell, kleine UNSAT-Kontrolle mit Zertifikatsstatus, EOF/Weiterlauf,
Budgetverlängerung samt Duplikatbehandlung, explizite 0 und Wiederaufnahme.
Gespeicherte Endzustände: SAT_CNF_VERIFIED, UNSAT_CERTIFIED,
STOPPED_UNRESOLVED. Letzteres ist der erwartete Budgetkontrollabschluss.
Keine freie N1-Klasse gesucht. Keine Behauptung vollständigen physischen
Systemverbrauchs; all_system_cpu_complete bleibt false.

## Nächste begrenzte Aufgabe

Separates Kalibrierpaket ausschließlich Root210/Klasse0 und Root6682/Klasse0.
Vor Freigabe muss die bisher konstant gesperrte Zielhardwareabnahme durch eine
prüfbare Bindung an diese Belege ersetzt werden. Außerdem: Die sichtbaren
Cgroups melden memory.max=max. Das bestehende Produktionsgate verlangt eine
endliche sichtbare Speicherhülle und würde weiterhin blockieren. Tatsächliche
WSL-Speicherhülle erfassen und geeigneten Schutz begründen; nicht einfach den
Check abschalten oder eine unbegrenzte Cgroup als endliche Grenze behandeln.
Keine OS-Limitänderungen ohne gesonderte Grundlage, keine laufenden Prozesse
verändern. Noch kein Produktionsstart autorisiert durch einen PASS-Schalter.
Regeln GC-01/08/15/18/19/20/21/22 und EXPERIMENT_RULES gelten unverändert.
