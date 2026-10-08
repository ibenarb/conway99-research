# ROOT8105 N1 Runtime 0.7.2 — Windows/WSL-Dateiaustausch

Basis: 630894857bce5e69be43d12635f4b8ef08284174 (0.7.1).
Nur host_clock.ps1 ist funktional verändert; sämtliche Python-/C++-Quellen
und mathematischen Eingaben bleiben bytegleich. Prozessbezogenes Bypass bleibt.

## Befund auf Ryzen, 08.10.2026

probe 0.7.1: eine Meldung mit sequence=0; anschließend Unterprozess-Exitcode1,
kein sampler-final.json. Der Besitzer lieferte den Fehler-Endbeleg; Produktion
blieb gesperrt. host.log war leer. Direkte kleine Tests durch Ralph auf demselben
WSL-Dateisystem: File.Replace mit $null scheiterte mit ungültiger Pfadform;
mit [NullString]::Value scheiterte es mit 'The request is not supported'.
MoveFileExW(source,target,1) bestand einschließlich Inhaltskontrolle und Prüfung,
dass die Quelldatei nach erfolgreicher Ersetzung nicht mehr existiert.

## Begrenzte Korrektur

Write-Atomic schreibt und flusht weiterhin eine vollständige eindeutige temporäre
Datei im Zielverzeichnis. Veröffentlichung erfolgt nun mit MoveFileExW und nur
MOVEFILE_REPLACE_EXISTING (1): kein vorheriges Löschen, kein Kopierfallback,
kein Wiederholungs-/Fehlerunterdrückungspfad. Ein fehlgeschlagener Aufruf wirft den
Win32-Fehler; die temporäre Datei bleibt als Diagnose erhalten. Keine behauptete
Garantie gegen Stromausfall oder alle denkbaren Dateisystem-/Lastzustände.

Der Besitzer liest stderr seines Unterprozesses asynchron, damit eine volle Pipe
nicht blockiert, und speichert es nach Prozessende als sampler-stderr.log.
CPU-Endkonto und Exitcode werden wie zuvor aus demselben gehaltenen Prozesshandle
ermittelt. Ein Fehler beim Schreiben wird nicht ignoriert.

## Abnahmestand und nächster Schritt

Der direkte Windows-Primitivtest stammt vom Nutzer auf Ryzen. Der vollständige
korrigierte Helfer wurde in der Cloud nicht mit Windows-PowerShell ausgeführt.
Keine erneute Durchführung der 104 alten Kontrollen; diese sind Vorgängerevidenz.
Zuerst nur target_acceptance.py probe mit neuem Ausgabeverzeichnis unter WSL.
Erwartet: sechs fortschreitende Hostmeldungen und gültige Endkonten. Produktion
bleibt gesperrt. Alte probe-Verzeichnisse und Diagnosebelege unverändert lassen.
Keine zusätzliche Windows-Kopie, keine dauerhafte Richtlinienänderung und keine
Änderung laufender C2-Prozesse. Regeln GC-01/08/15/18/19/20/21/22 gelten weiter.
