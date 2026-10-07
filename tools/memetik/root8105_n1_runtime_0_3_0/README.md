# N1-Runtime 0.3.0 – Inputbindung und unabhängige Zeugenprüfung

Basis: 88f762419e5668754f0ebe7c30141f106f3a051c.
Modellvertrag: docs/augmentation/root8105_model_gap_20261006/MODELLVERTRAG.md.
Laufvertrag: 34c51bd80e040bb705fdb68ae13b1074f9a3c8b5.
Eigenes Versionsverzeichnis; frühere Versionen unverändert.
Status: Cloud-Prototyp, KEINE PRODUKTIONS-/RYZEN-FREIGABE.

## Inputbindung

bind_n1.py erzeugt input.cnf und binding.json aus einem expliziten Taskdescriptor:
kind (control oder root-class), root_id, class_id, m, anchor, vollständige feste rows und matching. Es verwendet den unveränderten Encoder tools/memetik/root8105_n1/model.py, fixiert auf SHA256 3d041ddde9b01692fa18ed0c7d07fb8f8b0b16ddbd65c6c62c6305c0e6aa4d6a / öffentlichen Referenzcommit 55f978b28f6f4b4e8648e24a26c453d80ed0834f.

Die Bindung enthält Descriptor, CNF-Hash, Kantenvariablenabbildung und Encodermetadaten. init --binding prüft Struktur und Kantenabbildung unabhängig und regeneriert mit dem fixierten Encoder die gesamte CNF in einem separaten temporären Verzeichnis. Byteidentität und vollständige Bindungsdaten müssen stimmen. Ein bloß nach Änderung der CNF neu berechneter Hash genügt nicht.

Die vollständige binding.json wird unverändert in das neue Runverzeichnis übernommen, im Manifest gehasht und bei jedem run/resume/recover geprüft. Prüfer-/Binderquellen sind ebenfalls über Dateihashes fixiert. Es gibt keine automatische Migration früherer Runverzeichnisse. Ohne --binding bleibt die allgemeine CNF-Steuerung verfügbar und kann nur SAT_CNF_VERIFIED liefern.

root_id und class_id sind gebundene Bezeichnungen, aber noch kein geprüfter Nachweis der Zugehörigkeit zum historischen Katalog. catalog_identity_checked bleibt ausdrücklich false. Die Annahmen rows/matching sind exakt gebunden und mathematisch geprüft; der Abgleich zu den Root-210-/6682-Katalogdateien ist ein eigener noch offener Schritt. Keine Rootausschlüsse aus diesem Paket.

## Unabhängiger Prüfer

n1_check.py verwendet ausschließlich die Python-Standardbibliothek. Es importiert weder PySAT noch Encoderfunktionen und benutzt keine abschaltbaren assert-Prüfungen. Labels, feste Kanten und freie Kanten werden separat aus dem Descriptor hergeleitet. Der vollständige Solverbeleg muss jede CNF-Variable genau einmal belegen; die Kantenabbildung darf keine Vertauschungen, Lücken oder doppelten Variablen enthalten.

Nach bestandener vollständiger CNF-Prüfung wird die symmetrische H-Matrix rekonstruiert. Separat geprüft werden Form und Binärwerte, Schleifenfreiheit, Symmetrie, feste Zeilen, Grad, sämtliche Randmargen, das fixierte Matching und alle Paarbedingungen mit mindestens einem Endpunkt in U={anchor} vereinigt N_H(anchor). Paarbedingungen außerhalb dieses N1-Umfangs werden nicht behauptet. SRG_claim=false und root_exclusion=false sind Teil des Belegs.

SAT_N1_VERIFIED wird nur nach beiden Prüfungen gesetzt. N1_WITNESS.json enthält Matrix, Gleichungsumfang, Binding-/CNF-/Modellhashes. Auch Wiederverwendung und Recovery prüfen den N1-Zeugen erneut. Nach Absturz zwischen Solver-Endbeleg und Zeugenpersistierung kann Recovery den vollständig gespeicherten Solverbeleg unabhängig prüfen und die Matrix im Recoverybericht sichern, ohne die Suche neu zu starten. Ein fehlerhafter Kandidat wird nicht als SAT_N1_VERIFIED oder als UNSAT behandelt.

## Abnahme

11 N1-Tests, 16 Laufsteuerungs- und 11 Recoverytests bestanden (38 finale Prüfungen). Neue positive Kontrolle: freies N1-Modell der bekannten 3x3-Rookgeometrie, m=2. Die Sollmatrix wird aus tatsächlicher Rook-/Randadjazenz unabhängig abgeleitet. Alle vier Belegungen der zwei freien Kanten werden geprüft: genau eine ist zulässig.

Negative Kontrollen: beschädigte Matrix, bool statt Integerbit, falsche Kantenabbildung, doppelte Zeilen-/Matchingangaben, veränderte CNF trotz aktualisiertem Hash, fehlende Modellvariable und nachträglich veränderte Bindingdatei. Der eigenständige Prüfer läuft zusätzlich unter Python -O; eine explizite Fehlerauslösung prüft das Ausbleiben von Encoder-/PySAT-Imports. Der Testcrash nach search_receipt wird durch den bereits veröffentlichten expliziten Testmechanismus ausgelöst, nicht durch einen Zeitabbruch.

Umgebung: isolierte Audit-Pythonumgebung gemäß AGENTS.md; pynauty2.8.8.1 installiert und Helferkontrollen bestanden, python-sat1.9.dev15 und six1.17.0 ergänzt. Neuer unabhängiger Prüfer selbst ohne diese Bibliotheken. Nativer Worker und native Quellen byteidentisch zu 0.2.0. Keine Änderungen an Nutzerprozessen oder Zielhardware.

## Reproduktion und Grenzen

requirements-n1.txt fixiert die Python-Abhängigkeiten für Bindung/Tests. Der bestehende Audit-Helfer ist bei projektbezogenen Prüfungen weiterhin maßgeblich. build.py baut die fixierten nativen Abhängigkeiten. test_n1.py, test_runtime.py und test_recovery.py erhalten --output (neues Verzeichnis), --worker und --checker (absolute Pfade). Das Quell-ZIP enthält auch den unveränderten Encoder am erwarteten relativen Pfad.

m=7 ist im Prüfer vorgesehen, in diesem Paket aber nicht durch eine 99er-Klassensuche erprobt. Keine neue Encoderimplementierung, keine Wiederholung der 960er-Diagnose oder der 17 historischen Präfixkontrollen. Exakte Bindung ist kein allgemeiner formaler Korrektheitsbeweis des Encoders.

Weiter offen: Katalogabgleich der echten Klasse-0-Inputs, gesamte Supervisor-/Host-Endabrechnung, Hostuhr/Windows-WSL, Kampagnenbudgets, Ressourcen-Notfallsteuerung und skalierte Zustandssicherung. Die Sicherungsgrenzen von 0.2.0 gelten weiter; bei fehlender wait4-Abrechnung oder beschädigter maßgeblicher Transaktion kein automatischer Wiederanlauf.

Nächstes abgegrenztes Paket: die zwei bereits vorbereiteten Klasse-0-Instanzen von Root 210 und 6682 an den belegten Root-/Matchingkatalog binden und ihre Eingabeidentitäten prüfen; keine freie Klassensuche.
