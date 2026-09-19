# Memetik: Ergebnisbilanz und Entscheidungsvorlage
Stand: 19.09.2026. Quellenstand: memetik, Commit 96db50629232709a79166200efa93adfd82fbbc3. Nur Memetik/Escape; keine Fortsetzung des Symmetrieausschlusses.

## Ziel und Vertrag
Gesucht wird srg(99,14,1,2). Für ungeordnete Paare gilt r_uv=(A²)_uv+A_uv−2. W zählt fehlerhafte Paare, L1 summiert Absolutwerte, F Quadrate. Die Linf-Selektion vergleicht (Linf,Nmax,L1) lexikographisch. Beide Arme verlangen einfache ungerichtete 14-reguläre Graphen auf 99 Knoten. Ω verlangt zusätzlich den kanonischen Rahmen und seine harten Gleichungen, insbesondere PH=2J−(C+I)P; λ verlangt genau einen gemeinsamen Nachbarn je Kante. Ω impliziert nicht global λ=1.

## Was erreicht wurde
| Untersuchung | Befund | Aussagegrenze |
|---|---|---|
| Populationspilot 0.2.0 | Budgetabschluss in Generation 10, 16.561 abgeschlossene Aufgaben | Endpunkte nicht durchweg lokale Minima; keine belastbare Überlegenheit einer Strategie |
| Kandidatenbestand | 14 zusätzliche KI-Kandidaten: acht Ω, sechs λ; acht asymmetrisch, sechs mit nichttrivialen Automorphismen | KI-Herkunft ist keine Konstruktionsfamilie; unterschiedliche Graphen müssen keine verschiedenen Einzugsgebiete liefern |
| Office-Zensus | Acht Gründer, 20 abgeschlossene Aufgaben, 940 zulässige Trades | Nur implementierter Katalog |
| A_legacy | Vollständig geschlossene Komponente aus acht beschrifteten Zuständen mit Q3-Übergangsstruktur; A eindeutig bestes Mitglied für alle untersuchten Ziele | Weitere Wege mit denselben Operatoren nutzlos; neue lokale Operatoren weiterhin offen |
| C08/W | Kürzester Verbesserungsweg 2673→2673→2668, Länge zwei, W-Barriere null | L1 und F werden schlechter; 33 direkte neutrale Nachbarn untereinander isomorph; gesamte neutrale Komponente offen |
| C02/W | 2074→2063→2031; Endpunkt (W,L1,F)=(2031,2428,3298) | Andere C02-Abstiege erreichen F=3292 bei anderen Graphen; kein kombinierter Bestwertvektor |
| Standardisierte Abstiege | Zwölf Endpunkte ohne strikt verbessernden Nachbarn im jeweiligen Ziel | Neutrale Nachbarn nicht ausgeschlossen; „lokal“ immer ziel- und katalogabhängig |
| B/W | Frühere Flucht 2110→2114→2102, danach bis 2082; neue Flucht 2082→2094→2094→2086→2090→2080 | Neue Fluchtbarriere genau 12 im Katalog; fünf Schritte sind nicht als kürzeste Länge bewiesen; 2080 noch nicht als lokales Minimum geprüft |
| HoG/F | BFS ohne Verbesserung bis Länge vier; Minimax endet mit 2.142.386 gespeicherten und 76.258 expandierten Zuständen | Keine Verbesserung; Komponente offen; Zeitlimit kein Unmöglichkeitsbeweis |

B=2080 hat den vollständig geprüften Vektor (W,L1,F,Linf,Nmax)=(2080,3360,8980,10,34). Es ist ein Fortschritt dieser Linie, kein neuer globaler W-Bestwert gegenüber C02=2031.

HoG startet bei F=2836. Die geschlossene Subniveaukomponente F<2928 mit 85 beschrifteten Graphen stützt die untere Barriere 92. Der neue Minimax-Checkpoint stützt ≥192 (Frontierhöhe 3028). Datenbankintegrität, alle gespeicherten Eltern-/Barrierenrekurrenzen und Census-Vollständigkeitsflags sowie 33 Graphstichproben wurden geprüft; eine vollständige unabhängige Nachbarschaftsreproduktion für ≥192 fehlt. Auch die ältere Subniveauprüfung ist keine von der Operatorimplementierung unabhängige formale Zertifizierung.

Die Symmetrieauswertung widerlegt die Vermutung, sämtliche Gründer seien symmetrisch: A und HoG sind asymmetrisch; C08 erreicht einen asymmetrischen Nachfahren. Drei deterministische Abstiege von lambda_Linf2 kehren zu HoG-isomorphen Endpunkten zurück. Dies ist konkrete Redundanz unter diesen Abstiegen, keine vollständige Einzugsgebietsklassifikation.

## Konsequenz
Die Suche trifft auf mindestens drei verschiedene Hindernisse: neutrale Plateaus mit Ausgang, echte Fehlerbarrieren und vom Katalog abgeschlossene Komponenten. Ein einziger strikter Abstieg behandelt sie nicht angemessen. Mehr Gründer helfen nur, wenn sie strukturell oder im Suchverhalten etwas beitragen. Asymmetrie allein schützt nicht vor Stagnation.

Empfehlung: vor dem Großversuch ein endliches Vorbereitungspaket aus Gründer-/Endpunktdeduplikation, kurzen randomisierten Abstiegen, gezielten Plateau-/Escape-Proben und einem kontrollierten Vergleich weniger Suchvarianten. Keine vollständige Kartierung aller Plateaus und keine unbefristete HoG-Fortsetzung als Startvoraussetzung. Populationsselektionen bleiben L1, F und das verfeinerte Linf-Tupel; W bleibt Diagnoseziel.

## Quellen und Sicherung
Alle Pfade relativ zum fixierten Quellencommit:
- docs/memetik/GRUENDERVERTRAG.md
- docs/memetik/UEBERGABE_ESCAPE_20260916.md
- results/memetik/escape_followup_20260916/REPORT.md (einschließlich Automorphismen und Endpunktisomorphien)
- results/memetik/landscape_20260917/REPORT.md
- results/memetik/minimax_20260919/REPORT.md und AUDIT.json
- experiments/memetik/minimax_0_3_0/ und releases/Conway99_Minimax_Office_0.3.0.pyz

Minimax-Original: Ergebnisse_Minimax_030_minimax_20260917_213047_385349.zip; 292828623 Bytes; SHA256 eb0b94a06ee2740d0439354146e6785f054e484816670464595ade4214444fe7. Hochgeladenes Original und Office-Checkpoint vorhanden beim Abschlussaudit; Original-ZIP/SQLite nicht in diesem Git-Stand veröffentlicht. Dieser Bericht verwendet die archivierten Prüfergebnisse, keine erneute vollständige Rohdatenprüfung.
