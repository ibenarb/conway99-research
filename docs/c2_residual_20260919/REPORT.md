# C2-Restsymmetrie: Implementierung und Kleinkontrollen

Version 1.0.0, 19.09.2026. Ausgangscommit dd83aaef93dd0515e61513e3f2da2f3e29839c24.
Alle hier genannten Rechnungen wurden in der isolierten Arbeitsumgebung ausgeführt,
nicht auf Office oder Ryzen. Kein laufender Nutzerprozess wurde angesprochen.

## Ergebnis

Zulässige partielle Lex-Brechung ist implementiert. Alle elf Fallstabilisatoren
wurden enumeriert, ihre Erzeuger durch vollständige Gruppenschließung geprüft
und zusammen mit den Außen- und Primärpermutationen exportiert. Die 66
Fallannahmen werden von jedem Erzeuger als Menge erhalten. Der allgemeine
Vertretererhaltungsbeweis und die Gateherleitung stehen in THEOREM.md.

Die Ordnungen sind 46080,1536,288,256,64,48,20,384,32,72,12 in der dokumentierten
Typreihenfolge. Es werden keine Primärvariablen einer Bahn gleichgesetzt.

Kleinkontrollen: 2140 Lex-Projektionsprüfungen, 448 Bahnminimumprüfungen unter
S6 und 16 vollständige k=4-Variantenprüfungen bestanden. Ein separater C++-
Propagator wurde gegen einen anders aufgebauten Python-Propagator auf 400
kleinen Formel/Annahmen-Kombinationen geprüft (einschließlich Konflikten).

Für Typen 111111, 222 und 6 wurden jeweils vier Varianten erzeugt:
Totalizer, Totalizer+Lex, Totalizer+Dreierklauseln, Totalizer+beides.
Lex verwendet hier die volle Länge 1722, jedoch nur Erzeugervergleiche,
also weiterhin partielle Symmetriebrechung. Andere Präfixlängen sind möglich.
Die Basis hat den festgelegten SHA256
7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd;
die unveränderte Primärkarte
cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e.
Die 12 individuellen CNF-Hashes und Lex-Hilfsbereiche stehen in variants.json.
Große CNFs werden deterministisch rekonstruiert, nicht als Git-Binärlast archiviert.

## Strukturierte UP-Probe

Pro Fall fünf identische Aufgaben in allen vier Varianten, insgesamt 60:
leere Annahmen; beide Seiten des ersten durch Basis-UP nicht fixierten Bits;
zwei Kantenpaare der ersten Dreierklausel mit drei durch Basis-UP freien Bits.
Die Auswahl benutzt nur die Basis; cubes.json wurde vor den Variantenabfragen
festgeschrieben. Die beiden Bitseiten bilden einen vollständigen Einzelsplit;
die Dreierproben sind Diagnostik, keine vollständige Fallabdeckung.

| Typ | Root: Totalizer / Lex / Dreier / beides | Positiver Split: Totalizer | Positiver Split: Lex | Dreierzusatz |
|---|---|---|---|---|
| 111111 | 186 / 186 / 186 / 186 | 207 Primärbits, kein UP-Konflikt | UP-Konflikt | keine Änderung des konfliktfreien Primärabschlusses |
| 222 | 66 / 66 / 66 / 66 | 88 Primärbits, kein UP-Konflikt | UP-Konflikt | keine Änderung des konfliktfreien Primärabschlusses |
| 6 | 66 / 66 / 66 / 66 | 88 Primärbits, kein UP-Konflikt | 93 Primärbits, kein UP-Konflikt | keine Änderung des konfliktfreien Primärabschlusses |

Die negativen Splitseiten sowie die zwei Dreierproben zeigen in dieser kleinen
Probe keinen Variantenunterschied im Primärabschluss. Die gespeicherten Literale,
nicht nur deren Anzahl, wurden auf die erwartete Monotonie bei Klauselergänzung
geprüft. Bei Konflikt wird die aktuelle partielle Spur ausgegeben; ihre Länge
ist KEIN abgeschlossener Fixierungsvergleich und hängt von der Klauselreihenfolge ab.

Interpretation: Lex verändert bereits die Propagation unter Annahmen. Die beiden
UP-Konflikte nach Lex sind KEINE Ausschlüsse derselben beschrifteten Teilbelegung
in der ursprünglichen Formel: Der erhaltene Vertreter kann außerhalb des Cubes
liegen. Sie können ausschließlich als Schließung der Teilaufgabe der bereits
symmetriegebrochenen Formel verwendet werden. Kein gesamter Matchingfall ist
entschieden. Die 5 zusätzlichen Bits bei Typ 6 sind kein Beweisfortschritt.

Die Dreierprobe ist sehr klein und zeigt hier keinen zusätzlichen Primär-UP-
Gewinn auf dem Totalizer. Das widerlegt die extern berichteten BDD-Stichproben
nicht; deren genaue Auswahl und Code wurden nicht geliefert. Die historische
Reviewer-Stichprobe ist damit weiterhin nicht exakt reproduziert. Ein breiterer
BDD/Totalizer-Vergleich wird nicht als erledigt behauptet.

## Office-Fortsetzung

Vor Nutzerläufen eine lesende Ressourcenabfrage: tatsächliche CPU-Last,
MemAvailable, laufende Prozesse, Linux-Freiraum und Windows-Hostfreiraum.
Keine Ryzen-Pfade und keine Übernahme der elf Worker. Bei aktiver Memetik mit
knappen Ressourcen bleiben Solverläufe aus; zunächst nur kleine Kontrollen.

Nach Ressourcenprüfung zunächst höchstens EIN Scoutprozess, ohne Proof-Logging,
niedrige Priorität, identische Seeds/Budgets für alle Varianten. Der volle
Screeningentwurf umfasst 3 Typen x 4 Varianten x 2 Seeds x 20 Minuten = 8 CPU-h;
mit einem Prozess mindestens ungefähr 8 Stunden bei verfügbarer CPU, länger
unter Hintergrundlast. Nicht als sofortiger Office-Auftrag freigegeben oder
gestartet. Vorher ein kurzer technischer Pilot und Windows-/RAM-Schutz einrichten.
Keine unbeaufsichtigte Übernahme der älteren Ryzen-Controller.

Vergleich über Entscheidungen und CPU-Kosten gleicher Aufgaben. Reine Timeouts
bleiben zensiert; UP-Zahlen reichen nicht zur Auswahl einer Langkampagne.
Spätere Cubes müssen vor dem Vergleich festgelegt werden und auf der jeweils
vollständig begründeten Lex-Formel beide Splitseiten abdecken. Ein Scout erzeugt
keine Zertifikate; eine spätere Zertifizierung braucht einen eigenen Lauf und
archivierte unabhängig geprüfte Proofs samt vollständiger Abdeckung.

## Dateien und Reproduktion

- src/c2_residual_20260919: neue Implementierung, Kleinprüfer und UP-Diagnostik.
- results/c2_residual_20260919/certificates: elf explizite Gruppenzertifikate,
  Primärkarte und Dreierklauseln, jeweils mit Manifest.
- results/c2_residual_20260919/controls.json: ausgeführte Kleinkontrollen.
- results/c2_residual_20260919/variants.json: Hashes und Größen der zwölf CNFs.
- results/c2_residual_20260919/up: feste Teilbelegungen und vollständige UP-Ergebnisse.

Die einzelnen Einstiegspunkte sind im Paket-README dokumentiert. Es gibt keinen
installierenden oder startenden Hintergrunddienst. Alle Ausgabeverzeichnisse
für Export, CNF-Erzeugung und UP müssen neu sein; bestehende Kampagnen werden
nicht überschrieben. Die kleinen Programme benötigen Python 3 Standardbibliothek,
der UP-Motor zusätzlich einen C++17-Compiler. Kein SAT-Solver ist enthalten.
