# K66: Encoder- und Reduktionsaudit

Aktueller Bericht: `MATHEMATISCHER_AUDIT.md`. Die neue Ryzen-Reproduktion
bestand für alle 23 Fälle mit 167 byteidentischen CNF-Vergleichen; Ergebniscommit
`b38d4cb755505a67c01bcf87aff0e2dbf1f79524`. Die angeforderten 125 Star-CNFs
und sieben Hauptlaufwurzeln sind an die gesicherten Eingabehashes gebunden.
Noch offen sind die ausdrücklichen Zusatz-Replay-Verknüpfungen sowie die
eigenständigen 223 arithmetischen Ausschlüsse und die Bahnenvollständigkeit.

Die nachfolgende Quellenbeschaffungsnotiz dokumentiert den früheren
Arbeitsstand vor der inzwischen bestandenen Reproduktion.

Stand: 13. September 2026. Dies ist eine Arbeitsnotiz zur Quellenbeschaffung,
kein abgeschlossener mathematischer Audit und keine neue Zertifizierung.

## Maßgeblicher Ausgangspunkt

Repository `ibenarb/conway99-research`, Branch
`research/algebra-memetic-20260912`, Neustart-Commit
`fba694b50357fdd795601a6b17c97036f06af101`.

Der Neustart hat nach dem übergebenen, gesicherten Bericht die Integrität
und archivierten Cake-Bestätigungen der 897 Hauptlaufblätter geprüft.
Ein Produktionschecker-Replay dieser 897 Beweise wurde dort nicht ausgeführt.
28 weitere vorhandene Beweise wurden mit Cake erneut geprüft und
125 Profil-CNFs neu zertifiziert und mit Cake geprüft. Diese Angaben sind
hier übernommener gesicherter Projektstand, keine in diesem Audit wiederholten Prüfungen.

## Bisherige Quellenzuordnung

| Gegenstand | Quelle / Befund | Erkenntnisstatus |
| --- | --- | --- |
| Star-Encoder | `src/k66_star125_20260913/original_preflight.py`, Funktion `build_star_cnf` | Quelltext am Neustart-Commit gelesen; tatsächliche Verwendung noch zu belegen |
| Global-Encoder | Dieselbe Datei, Funktion `encode_global` | Quelltext gelesen; tatsächliche Verwendung noch zu belegen |
| Profilaufbau und Filter | Dieselbe Datei, `make_profiles`, `prepare_case`, `main` | Identifiziert; mathematische Notwendigkeit und exakte Arithmetik noch zu auditieren |
| Rundenablauf dieser Fassung | `ACTIVE` wird erst nach Abschluss aller Aufgaben einer Runde aktualisiert | Simultaner Rundenablauf im gelesenen Code festgestellt; Übertragung auf Produktionslauf offen |
| Älterer Rekonstruktionsprüfer | `src/k66_star125_20260913/reconstruct.py` | Gelesen; historische Ergebnisse ausdrücklich nicht als neue Beweisquelle übernommen |
| Lokale Quotientenreferenz | `reference/src/reconciliation/o3_fixed_triangle_certify.py` im K66-Lauf | Vom Nutzer ausgegebene SHA256 stimmt mit Manifestangabe überein |
| Lokale V3-Referenz | `reference/src/reconciliation/o3_fixed_triangle_structural_v3.py` | Vom Nutzer ausgegebene SHA256 stimmt mit Manifestangabe überein |
| Produktionsquellen Star/Global | Bisherige lokale Suche fand keine entsprechende Python-Datei im K66-Lauf | Pfad und Paketzuordnung offen |
| Zusätzliche Deep7-Stufen | `round_1_quick`, `round_1_deep`, `star_history.json`, `summary.json` | Existenz durch Nutzer-Inventar belegt; Bedeutung und Abhängigkeiten offen |

Lokale Referenzhashes:

- `o3_fixed_triangle_certify.py`: `c6dc278d22480dd1eddb9fa236c6e839dccf224b74260f2c5f2a132ee3f8ddce`
- `o3_fixed_triangle_structural_v3.py`: `c86731245027ef256a4b684361811f8c43479d54a6773b01bf9c3c065baaf251`

Die Ausgangsdatei `original_preflight.py` besitzt den Git-Blob-Hash
`f76c01b1faaf1dede0c48c3753887095096be9e8`.
Die Benennung als "original" belegt für sich keine historische Originalität.

## Begrenzter lokaler Sammler

`src/k66_encoder_audit_20260913/collect_sources.py` sammelt auf dem Ryzen:

- einschlägige Python-Quellen im Workspace und in den Downloads;
- Python-Mitglieder kleiner, passend benannter ZIP-/PYZ-Programmpakete;
- JSON-Metadaten aus dem K66-Lauf, dem Star-Preflight, Deep7 und dem R2-Global-Scout;
- Pfade und Größen der Star-/Global-CNFs, ohne ihre Inhalte zu lesen;
- die vorhandene mathematische Referenzdokumentation.

Jeder übernommene Text bleibt byteidentisch. Ein Index bindet seinen
ursprünglichen Pfad bzw. Paketmitgliedsnamen, Länge, SHA256 und Git-Blob-Hash.
Dateien werden einzeln gesichert. Bei Wiederholung darf ein bereits erfasster
Ursprung nicht unbemerkt andere Bytes erhalten. Es werden keine Solver gestartet.

Grenzen: 512 KiB je Text, 8 MiB gesammelte Texte, maximal 32 MiB je geöffnetem
Quellpaket; maximale Suchtiefe neun im Workspace und eins in Downloads.
Unter anderem Beweis-, Job-, Abhängigkeits- und Git-Verzeichnisse werden bei
der Quellensuche übersprungen. Übersprungene Größen und Lesefehler werden
protokolliert; die Sammlung behauptet keine unbegrenzte Vollständigkeit.

Mit `--publish` erstellt das Programm aus dem vorhandenen separaten
Backup-Repository ein weiteres isoliertes Worktree. Es schreibt nur unter
`data/k66_encoder_audit_20260913/source_evidence`, erzeugt einen regulären
Commit und pusht ohne Force auf den freigegebenen Branch. Die
Originaleingaben und das gewöhnliche Forschungs-Worktree bleiben unberührt.
Jede übertragene Datei wird danach mit GitHubs Blob-Hash und Länge sowie
vollständigem Rohdaten-Rückdownload byteweise und per SHA256 verglichen.
Die lokale Quittung lautet
`k66_encoder_source_audit_v1/GIT_SOURCE_RECEIPT.json`.

Vorläufige Laufzeitschätzung: etwa 1–5 Minuten, bei vielen alten
Programmpaketen oder langsamen GitHub-Zugriffen länger. Die reine Sammlung
benötigt keinen Suchlauf; ihre Dauer hängt von Zahl und Lage der Dateien ab.
Längere Sammlung meldet nach jeweils zehn Minuten Status; während der
noch nicht abgeschlossenen Verzeichnissuche ist keine belastbare ETA bekannt.

Entwicklungsprüfung: Ein kleines künstliches ZIP prüfte, dass nur die
vorgesehenen Python-Quellen übernommen, CNF-/Beweisinhalte ausgeschlossen,
Bytes erhalten und wiederholte Checkpoints konsistent verarbeitet werden.
Die Git-Blob-Berechnung wurde an dem bekannten leeren Blob kontrolliert.
Ein echter Ryzen-Lauf und der Git-Veröffentlichungsweg stehen noch aus.

## Offene Pflichten und nächster Schritt

1. Lokale Quellpakete, Imports, Produktionsparameter und Rundendaten zuordnen.
2. Profiluniversum, IDs, Multiplizitäten, Paarfilter und Zellkapazitäten aus
   dem Quotientenmodell herleiten; die als Astra-(8)–(9) bezeichneten
   Gleichungen eigenständig ableiten.
3. CNF-Übersetzung einschließlich Konstanten, Randfällen und Hilfsvariablen
   prüfen; Ganzzahlarithmetik und Überlaufschranken vollständig beurteilen.
4. Gesamte Reduktionskette inklusive Deep7 rekonstruieren; insbesondere
   Rundenzugehörigkeit und vorausgesetzte Entfernungen für Profil 3520
   in `v4_09317` ohne Zirkelschluss belegen.
5. Auf dem Ryzen alle 125 Star-CNFs und sieben reduzierten Global-CNFs in
   einem frischen Auditverzeichnis erneut erzeugen und vollständig vergleichen.
6. Die Modelle von `v4_09232` und den 15 weiteren Restfällen gesondert zuordnen.
7. Die 223 arithmetischen Ausschlüsse und Bahnenvollständigkeit bleiben
   eigenständige Pflichten; der Fallabschluss wäre kein globaler SRG-Ausschluss.

Nächster erforderlicher Schritt: den begrenzten Sammler auf dem Ryzen
laufen lassen und anschließend seinen indexierten Quellenbestand aus Git
lesen. Erst daraus wird der ausführbare Rekonstruktionsaudit aufgebaut.
