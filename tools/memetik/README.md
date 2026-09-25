# Verlässliche Python-Umgebung für Memetik-Audits

pynauty ist mit Version 2.8.8.1 in requirements-audit.txt festgelegt.
Die wiederholten Fehlstarts entstanden bei Prüfungen mit allgemeinem python3;
der zuletzt beobachtete Installationsort war /root/.local/lib/python3.12/site-packages.
Diese Benutzerinstallation ist nicht Teil des Projekts und kann nach einem
Wechsel/Reset der Ausführungsumgebung fehlen. Der genaue Cloud-Resetmechanismus
ist nicht nachgewiesen; eine dauerhafte Systeminstallation kann hier nicht garantiert werden.

Der Starthelfer richtet eine eigene venv ein, standardmäßig unter
<Elternverzeichnis-des-Repositories>/venvs/memetik-audit. Keine Aktivierung nötig.
Er ignoriert Benutzerpakete und prüft Version, Isomorphie-Invarianz eines
5-Zyklus, Unterscheidung vom 5-Pfad und Automorphismengruppenordnung 10.
Bei fehlender/falscher Abhängigkeit installiert er die festgelegte Version;
bei intakter Umgebung erfolgt kein pip-Aufruf. Scheitert Installation oder
Selbsttest, wird mit Fehler beendet, nicht ohne Isomorphieprüfung fortgefahren.

Vom Repository-Verzeichnis aus:

```bash
python3 tools/memetik/audit_python.py
```

Direkter Aufruf einer Prüfung mit demselben Interpreter:

```bash
python3 tools/memetik/audit_python.py -- audit_script.py
```

Auch Python-Optionen sind möglich: `-- -c 'import pynauty; print(pynauty.__version__)'`.
Ein anderer Ort kann mit --venv gewählt werden. Unvollständige bestehende
Umgebungen werden nicht automatisch gelöscht; einen frischen Ort wählen.

Die Einrichtung benötigt Python mit venv/pip und bei fehlendem Paket Zugriff
auf die Paketquelle. Bei komplettem Verlust des Workspaces lässt sie sich aus
den Git-Dateien erneut ausführen; ohne Paketquelle kann keine Installation
versprochen werden. Die Arbeitsanweisung in AGENTS.md verpflichtet kommende
Projektprüfungen zur Nutzung dieses Helfers statt zur improvisierten User-Installation.

Das ist keine Änderung laufender Forschungsumgebungen auf Ryzen/Office und
kein Ersatz für deren exakte Versions-/Fingerprint-Kontrollen. Historische
Umgebungsunterschiede müssen bei Audits weiterhin ausdrücklich benannt werden.
