# Umsetzung nach Freigabe, 26.09.2026

Ralph hat den dokumentierten Vorschlag am 26.09.2026 zur Umsetzung freigegeben.
Das [Laufpaket](../../../experiments/memetik/lambda_radius_1_0_0/README.md)
setzt die beiden festen Radiusfragen um. Es ersetzt keinen laufenden Suchprozess
und verändert keine bestehenden Ryzen-/Office-Umgebungen.

Vollständige untere Schichten bis Tiefe 3 sind Startgates für Tiefe 4.
Insgesamt höchstens 2 Hilfs-CPU-h plus 20 CPU-h je Arm; höchstens zwölf
Worker, feste Windows-Host-Walltimegrenze von acht Stunden. Kein Folgeabstieg.
Saubere Checkpoints, reservierte CPU-Allokationen und wait4-Receipts gelten
auch bei Unterbrechung. Ein technischer Crash wird nicht als negative
Radiusantwort oder als kostenloser Neustart gewertet.

Die lokalen mathematischen, Integrations-, Abbruch- und Paketkontrollen
sind in den vier JSON-Prüfberichten des Pakets dokumentiert. Die beiden
echten unteren Schichten wurden vollständig nachgerechnet; 582 zusätzliche
Kinder aus sechs Tiefe-2-Zuständen unabhängig validiert. Vollständige
Tiefe-3/4-Rechnung und Windows-Interop finden erst auf dem Ryzen statt.

Status beim Veröffentlichen: geprüftes Paket bereitgestellt, nicht auf
dem Ryzen gestartet; für den Start ist ein lokaler Befehl des Nutzers nötig.
