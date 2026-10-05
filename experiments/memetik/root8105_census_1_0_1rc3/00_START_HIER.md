# ROOT8105 Census 1.0.1-rc3

Status: Kandidat zur Ryzen-/WSL-Abnahme, noch keine Produktionsfreigabe.

Auftrag aus dem Reviewabgleich: Betriebsabsicherung abschließen, danach echte
Zielhardware-Abnahme vor P0/P1. Der mathematische F-Kern bleibt unverändert.

Zuerst PRUEFBERICHT.md und VALIDATION.json lesen, danach README.md.
Das Paket vollständig in ein neues Verzeichnis übernehmen, keine Einzeldateien
in bestehende Laufpakete kopieren. Eine eigene Python-Umgebung verwenden.
Historische DBs nicht mit diesem Kandidaten fortsetzen.

Nächster Nutzerschritt: ZIP im Windows-Ordner Downloads speichern und die
Bestätigung im Chat abwarten. Dort folgen WSL-Befehle einzeln. Kein automatischer
Produktionsstart. C2 unverändert laufen lassen; kein wsl --shutdown.

Offene Zielhardwareabnahme: reale Hostuhr/de-DE, Hintergrundbetrieb, elf Worker
neben C2 mit ausreichendem Speicher, gezielte Pause/Crash/Recovery und GC-19.
Der vollständige WSL-/Hostausfall ist bisher ungeprüft.

Projektgrundlage: f2fb0d98197d8d426b779819ae3158b3210df209 (memetik).
Revieworiginal: fd0e6a72e122be0a047f792dd6d9b0c4be49132b
Zweig reviews/20261005-root8105-census-crosscheck.
Aktive Regeln: project_rules/AGENTS.md, EXPERIMENT_RULES.md,
GLOBAL_CONCLUSIONS.md; insbesondere GC-01/07/09/10/11/15/16/18/19/20.

Freigegebene Richtung: P0/P1 mit 48 aggregierten CPUh als Meldeschwelle und
Weiterrechnung bis zur Antwort. Späterer Filtervergleich und tiefere Kampagnen
werden getrennt dimensioniert; dieser Kandidat startet sie nicht.

rc3 behebt die WSL-Testisolierung. Neuen Lauf anlegen; rc2 samt Logs erhalten.
Keinen Fingerprint in alten Konten ändern. Produktionscode und Mathematik
sind gegenüber rc2 unverändert. Siehe PRUEFBERICHT.md und GC-21.
