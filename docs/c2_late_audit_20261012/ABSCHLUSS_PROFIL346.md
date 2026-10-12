# Die späten Muster und der bedingte Abschluss des Profil346-Zweigs

Stand 12.10.2026, Arbeitsfassung 0.5. Kein allgemeiner C2-Ausschluss.

## 1. Neue Prüfung

Vier weitere Muster verbinden die inzwischen exakt rekonstruierte Rest234691-Liste
mit der bereits abgeschlossenen Rest218-Liste. Die Muster heißen hier D, A, B, C:

| Kürzel | Historische Kennung | Units | Historische Endprüfung |
|---|---|---:|---|
| D | seed_172_step_45 | 9 | drat-trim |
| A | seed_042_step_44 | 9 | cake_lpr auf gekürztem LRAT |
| B | seed_172_step_49 | 9 | cake_lpr auf gekürztem LRAT |
| C | seed_172_step_47 | 9 | cake_lpr auf gekürztem LRAT |

Jede Formel besteht aus derselben F346-Basis und den genau angegebenen neun
Unit-Klauseln. Alle vier Formelhashes wurden neu aus dieser Basis rekonstruiert.
Die Pfeilvariablen wurden aus den Labels und B/C-Einträgen der erzeugten
Variablenabbildung abgeleitet. Es gibt keine zusätzlich eingeführte
Matchingnormalform und keine globale Gradordnung in diesen Formeln.

Geprüft wurden die Gleichheit der Units mit den ursprünglichen Kandidaten,
Formelhashes, Kommandopfade, erfolgreiche Solver- und Checker-Rückgaben,
Loghashes und separat gespeicherte Operationsberichte. Für A/B/C ist die Kette
Solverausgabe → Trim-Eingabe → Trim-Ausgabe → cake-Eingabe einschließlich
Formelidentität und Proofhashes vollständig verbunden. Die Toolchain-Manifeste
stimmen mit den Zertifikaten überein. Beim D-Beleg passen Solver- und
Checkerpfade zur gleichen Formel und demselben historischen DRAT-Proof.

Die Originalzertifikate und finalen Checkerlogs sind als kompakte Quellen unter
[vendor/c2_late_audit_20261012](../../vendor/c2_late_audit_20261012) eingecheckt.
**Keine externen Proofdateien wurden erneut gelesen, kein Beweischecker ausgeführt.**
Die historischen UNSAT-Endurteile bleiben übernommene Voraussetzungen.

## 2. Exakte Mengenübergänge mit zwei Verfahren

Die Abdeckung wurde erneut auf zwei verschiedenen Wegen berechnet:

1. Historischer C++-Matcher mit injektiver Zuordnung der Musterknoten; sein
   Korrektheitsargument steht in [Muster und Komplemente](../c2_coverage_audit_20261012/MUSTER_UND_KOMPLEMENTE.md).
2. Unabhängiger Python-Algorithmus, der alle 5.040 Permutationen durchläuft und
   die erfüllenden Datensätze über Schnitt und Vereinigung von Bitmengen bestimmt.
   Er importiert weder Projektencoder noch C++-Matcher.

Beide Verfahren erzeugen die gleichen vollständigen Restdateien; diese sind
bytegleich mit den jeweiligen Originaldateien und ihren historischen Hashes.

| Schritt in historischer Abschlussreihenfolge | Zusätzlich entfernt | Rest |
|---|---:|---:|
| Ausgangsliste | — | 234.691 |
| D | 228.040 | 6.651 |
| B | 3.291 | 3.360 |
| A zusätzlich zu B | 2.954 | 406 |
| C zusätzlich zu A und B | 188 | 218 |

B wurde historisch vor A fertig. Deshalb bezeichnet `remaining_after_1.tsv`
den Rest nach B. Die anfänglich im neuen Audit angenommene Reihenfolge A vor B
führte zu einer fehlgeschlagenen Bytevergleichs-Assertion; die Quellen klärten
diese reine Reihenfolgefrage. Nach A allein bleiben 1.587 Fälle. Nach A und B
bleiben unabhängig von der Reihenfolge dieselben 406 Fälle.

Auf der 6.651-Fallmenge nach D sind A, B und C wie folgt überlappend:

| A | B | C | Bahnen |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 218 |
| 0 | 0 | 1 | 188 |
| 0 | 1 | 0 | 690 |
| 0 | 1 | 1 | 491 |
| 1 | 0 | 0 | 2.123 |
| 1 | 0 | 1 | 831 |
| 1 | 1 | 0 | 624 |
| 1 | 1 | 1 | 1.486 |

Hier bedeutet 1: mindestens eine S7-Kopie des Musters trifft. Insbesondere gilt
|A|=5.064, |B|=3.291, |A∩B|=2.110 und |A∪B|=6.245. Das erneute Zählen der
Vereinigung berücksichtigt daher die Überschneidungen explizit.

## 3. Anschluss an Rest218

Die neu erzeugte Restdatei hat SHA-256
`ade2b458fbf77a272fa058eee97e49daf34f0de24e9fb37403e8a17dd18d87f5`.
Sie stimmt bytegenau mit der ursprünglichen Rest218-Eingabe überein. Ihre 218
verschiedenen Codes sind exakt die 218 Codes des vorhandenen Abschlussaudits.
Für jeden Code wurde dessen Formel als F346 plus alle 42 positiven/negativen
Pfeil-Units neu gehasht; alle 218 Hashes stimmen mit dem Abschlussaudit überein.

Der ursprüngliche [Rest218-Abschlussaudit](../../results/c2_completeness_20261012/rest218_abschlussaudit.json)
bleibt unverändert. Er berichtet 217 Trim/cake-Abschlüsse und einen direkten
cake-Abschluss für p525910250893. Sein Befund einschließlich der ursprünglichen
Prüfgrenzen wird hier übernommen. Der neue Audit behauptet insbesondere keine
erneute Prüfung aller Rest218-Proofarchive oder ihrer Checkerprogramme.

Neue Berichte:
[late_audit.json](../../results/c2_late_audit_20261012/late_audit.json),
[independent_coverage.json](../../results/c2_late_audit_20261012/independent_coverage.json),
[input_manifest.json](../../results/c2_late_audit_20261012/input_manifest.json).

## 4. Zusammengesetzter Satz und Reichweite

**Satz H346, unter den historischen Zertifikatsvoraussetzungen.**
Unter der im Manuskript hergeleiteten Encoderadäquanz und Anerkennung der
gebundenen historischen UNSAT-Prüfungen einschließlich des Rest218-Abschlussaudits
besitzt das Rahmenmodell keine Lösung, deren sieben Ankergrade sämtlich in
{3,4,6} liegen.

**Beweis.** Angenommen, ein solches Rahmenmodell existiert. Der auf F0 geprüfte
C4-Ausschluss macht seinen gegenseitigen Pfeilgraphen C4-frei. Der vollständige
Profile46-Ausschluss erzwingt mindestens einen Ankergrad 3. Sein Pfeilgraph liegt
daher, bis auf S7-Umbenennung, im vollständig geprüften Profile346-Census.
Das Transportlemma überträgt jeden gebundenen partiellen Musterausschluss auf
jede seiner S7-Kopien. Die exakten Komplemente der Generalize-, One3-,
Generalize2- und Two3-Stufen lassen genau Rest234691 übrig. D, A, B und C lassen
hieraus genau Rest218 übrig. Der gebundene Abschlussaudit schließt jeden dieser
218 vollständigen Profile aus. Somit bleibt keine mögliche Censusbahn. ∎

Die Abhängigkeitsfolge ist zirkelfrei: C4 verwendet F0, Profile46 verwendet F46,
die weiteren Muster und vollständigen Profilfälle verwenden F346. Die
Notwendigkeit der F346-Einschränkung für *alle* C2-Graphen wird nirgends vorausgesetzt.

**Korollar LOW, unter denselben Voraussetzungen.** Jeder hypothetische
srg(99,14,1,2) mit Involution besitzt einen Anker mit Grad höchstens 2. Nach
Minimumankerwahl und zulässiger lokaler Matchingnormalisierung genügen noch
acht Typen: vier mit Grad 0, zwei mit Grad 1 und zwei mit Grad 2.

Das Korollar folgt aus L1–L7 und H346: Grad 5 ist lokal unmöglich, also würde
ein Minimumgrad von wenigstens 3 bereits F346 erzwingen. Ein weiterer
Ausschluss der acht niedrigen Typen ist in dieser Arbeit noch nicht bewiesen.
Der allgemeine C2-Satz bleibt deshalb offen.

## 5. Nächster mathematischer Arbeitsgegenstand

Die Abdeckung des hohen Gradbereichs ist jetzt unter den benannten historischen
Prüfergebnissen verbunden. Für den allgemeinen C2-Ausschluss benötigen wir eine
vollständige Behandlung der acht niedrigen Matchingtypen unter F0 und
Minimumankerbedingungen. Dazu dürfen keine Profile346-Klauseln übernommen werden.

Der laufende Reviewerauftrag bleibt unverändert; die Rechnungen dieses Audits
muss der Reviewer nicht wiederholen. Ein späteres Review sollte das
Transportargument, die logische Zusammensetzung und die verbleibenden niedrigen
Typen beurteilen. Vor einer endgültigen Veröffentlichung bleiben außerdem der
unabhängige mathematische Review und dauerhafte Bezugsstellen der externen
Census-/Proofdateien erforderlich.
