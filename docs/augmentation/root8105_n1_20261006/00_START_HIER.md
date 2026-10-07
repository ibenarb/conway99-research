# N1 implementiert und kontrolliert; Klassenpilot vorbereitet

Modellvertrag: ../root8105_model_gap_20261006/MODELLVERTRAG.md.
Code: tools/memetik/root8105_n1/{model,controls,prepare_classes}.py.
Keine neue Klassen-SAT-Suche gestartet; keine Rootausschlüsse.

## Kontrollen

- Bekannter3x3-Rookgraph separat auf Grad und alle Codegrees geprüft, durch
  tatsächliche Randinzidenzen auf H-Labels abgebildet.
- Vollständig fixierter Rook und freie N1-Relaxation seiner Root: SAT mit
  direkter Ganzzahlprüfung. Freie Kontrolle enthält zwei Kantenvariablen und
  eine echte Produktvariable. Alle vier Kantenbelegungen wurden erschöpfend
  mit der direkten Modellprüfung verglichen: genau eine zulässig.
-17 alte feste ausgeschlossene Präfixe im NEUEN Encoder: UNSAT, jeder neue
  DRAT-Beleg extern geprüft. Das sind Encoderkontrollen, keine17 neuen Funde.
- Externer Prüfer weist falsche leere Klausel für erfüllbare Kontroll-CNF ab.

Externer Prüfer: marijnheule/drat-trim, Commit
2e3b2dc0ecf938addbd779d42877b6ed69d9a985; gcc -std=c99 -O2.
Build meldete die Warnung zu getc_unlocked; Kompilierung und Kontrollen bestanden.
Upstreamoption -O deaktiviert den automatischen Timeout und optimiert bis zum
intern begrenzten Fixpunkt. Kein eigenes Zeitbudget angesetzt, kein Abbruch.
Alle17 echten Negativkontrollen hatten Returncode0 und s VERIFIED.
Der Wrapper verlangt explizites VERIFIED und verbietet NOT VERIFIED; ein bloßer
Returncode gilt nicht als Zertifikat. Kein Beweisassistent beansprucht.

Messung der19 Modellkontrollen:3,701CPU-s Elternprozess und1,995CPU-s externe
Prüfer für die17 UNSAT-Fälle; kleine Zusatzkontrollen/Import separat. Peak des
Elternprozesses53364KiB. Diese sehr einfachen festen Kontrollen erlauben keine
Laufzeitprognose für freie99er-Klassen.

## Vorbereitete Klassen und Abdeckung

| Root | Zulässige Matchings | Verwendete Orbitklassen |
| --- | ---: | ---: |
| 210 | 328 | 28 |
| 6682 | 372 | 192 |

Root210 hat unter den24 Pilot-Roots die wenigsten Klassen; keine Behauptung,
dies sei das globale Minimum unter8105.6682 ist der diagnostische Kontrast.
Eine zweite vollständige Paarungsaufzählung vergleicht die zulässige Rohfamilie
mit der disjunkten Vereinigung der gespeicherten Orbits. Jeder verwendete
Generator wurde direkt auf Rand-Antipoden, H-Labelabbildung, fixierte Root und
Rootnachbarschaft geprüft. Die volle Automorphismengruppe wird für die
Vollständigkeit des konservativen Klassenüberdeckungsarguments nicht benötigt.
Vollständige Klassenlisten, Orbitmitglieder und Generatoren sind archiviert.

## Modellgröße, noch keine Härtemessung

Jeweils Klasse0 beider Roots aufgebaut, NICHT gelöst:

| Größe | Root210 | Root6682 |
| --- | ---: | ---: |
| Freie Kanten | 3337 | 3337 |
| Produktvariablen | 64326 | 64326 |
| Variablen einschließlich Hilfsvariablen | 295367 | 295389 |
| Klauseln | 674123 | 674153 |
| DIMACS-Bytes | 12155479 | 12158458 |
| CPU-s für Abdeckung, Aufbau und Schreiben | 1,700 | 1,446 |

Cloud-Prozesspeak167604KiB; kein gemessener Solverpeak für freie Klassen.
CNF-Größe ist kein Zertifikatsvolumen und sagt wenig über CDCL-Laufzeit aus.
CONTROLS.tar.xz und CLASSES.tar.xz enthalten geschlossene Belege, CNFs und Hashreceipts.

## Nächste Voraussetzung vor einem Produktionspilot

Auf dem vorgesehenen Ryzen zuerst begrenzte Hardware-/Solverkalibrierung für
beide bereits fixierten Klasse0-Instanzen vorbereiten: direkte SAT-Zeugen,
DRAT-Ausgabe, externer Prüfer, CPU-/RAM-/Plattenmessung und GC-19-konformer
Antwortkanal. Erst daraus Workerzahl, Solver- und Prüfreserve ableiten.220
Klassen sind die vollständige Fallliste beider ausgewählter Roots, noch keine
Startfreigabe für220 unkalibrierte Suchläufe. Ein fertig geprüfter GC-19-Runner
für diese neue N1-Kampagne ist noch offen; vorhandene Nutzerprozesse bleiben
unverändert. Keine belastbare ETA, kein größeres Zeitbudget erfunden.

SAT für N1 ist nur eine Relaxationslösung. UNSAT einer Klasse zählt nur nach
externem Beleg. Ein Rootausschluss erst nach zertifiziertem Abschluss sämtlicher
benötigter Klassen und bestandener Abdeckung. Keine neue Großkampagne.
