# K66-Neustart: konsolidierter Stand

Massgeblich ist data/k66_restart_20260913/K66_NEUSTART_STATUS.json. Das Ergebnispaket enthaelt die lokalen Pruefberichte, Checker-Kontrollen und alle 125 neu erzeugten Profilbeweise samt Cake-Protokollen. PACKAGE_MANIFEST.json bindet seine Dateien durch Laenge und SHA256.

897 Hauptlaufblaetter: Baum, archivierte Cake-Protokolle und lokale Dateihashes geprueft; kein erneuter Produktionsbeweis-Replay. Weitere 28 vorhandene Beweise wurden erneut mit Cake geprueft: 15 globale Faelle sowie 12 Profilfaelle und die globale CNF fuer v4_09232. Alle 125 Profil-CNFs der sieben Hauptlaufwurzeln wurden neu zertifiziert: 100 per Unit-Propagation, 25 per CaDiCaL, jeweils Cake-geprueft.

Der konkrete historische lrat-check scheitert an Negativkontrollen. Das hashidentische Cake-Binary besteht alle fuenf Kontrollen. Dies ist kein vollstaendiger mathematischer K66-Abschluss: Modellnotwendigkeit, Encoder, Reduktionskette, 223 arithmetische Ausschluesse und Bahnenvollstaendigkeit bleiben zu auditieren.

Die beiden Original-ZIPs ersetzen die beschaedigten Git-Kopien. Aeltere abgeleitete Fassungen unter k66_completion_20260913, k66_main_completion_20260913 und k66_star125_20260913 sind als massgebliche Auswertung ersetzt; historische Dateien bleiben nachvollziehbar. Die grossen vorhandenen Produktionsbeweissammlungen sind nicht Bestandteil dieses Pakets.

TRANSFER_MANIFEST.json beschreibt die lokal vorbereiteten Bytes. Eine erfolgreiche Git-Sicherung ist erst nach Push und Rueckdownloadpruefung belegt. PENDING im Status bezeichnet den Zeitpunkt dieses Snapshots.
