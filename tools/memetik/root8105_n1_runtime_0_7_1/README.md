# ROOT8105 N1 Runtime 0.7.1 — prozessbezogener PowerShell-Start

Einzige funktionale Änderung gegenüber 0.7.0: Der Windows-Besitzer wird wie in
ROOT8105 Census rc3 und Review-Followup 1.0.1 mit `-ExecutionPolicy Bypass`
gestartet. Das gilt nur für diesen PowerShell-Prozess; keine dauerhafte Änderung
an CurrentUser/LocalMachine und keine Änderung einer Gruppenrichtlinie.
Nutzerfreigabe: 08.10.2026, Memetik VII, Rückkehr zum bisherigen Startverfahren.

Anlass: Der erste echte Ryzen-probe von 0.7.0 bestand den Syntaxcheck, scheiterte
aber vor dem Heartbeat: unsigniertes host_clock.ps1 über den UNC-Pfad
\\wsl.localhost\Ubuntu-24.04 unter RemoteSigned. MachinePolicy/UserPolicy/Process
waren Undefined, CurrentUser/LocalMachine RemoteSigned. Der Fehllauf bleibt
unverändert in ROOT8105_N1_probe_20261008_01 erhalten.

Zuerst ausschließlich `target_acceptance.py probe --output NEUES_VERZEICHNIS`
unter Ryzen-WSL ausführen. Standardbibliothek genügt. Keine Windows-Kopie nötig.
Produktion bleibt gesperrt. Vor weiteren Schritten den Zielhardwarebefund prüfen.

Cloud-Nachprüfung: gezielter Aufruftest mit simuliertem Prozessstart, keine echte
Windows-Ausführung. Die 104 Kontrollen von 0.7.0 sind Vorgängerevidenz und wurden
nicht wiederholt; sie sind keine vollständige Abnahme von 0.7.1.
Alle anderen Laufzeit-, Mathematik-, Budget-, Ressourcen- und Abrechnungsquellen
sind bytegleich zu 0.7.0. Dessen ausführliche Beschreibung gilt mit obiger Änderung.
Regeln: GC-01/08/15/18/19/20/21/22, AGENTS.md, EXPERIMENT_RULES.md.
