# ROOT8105 – Prüfwerkzeuge und Ergebnisse des unabhängigen Reviews (Claude, 04.10.2026)

Ergänzung zum Review des Pakets `docs/augmentation/root8105_review_20261004` (Commit `ad92f04`).
Reine Prüf- und Messwerkzeuge, keine Produktionskampagne: Kein Skript hat ein Zeitbudget oder
bricht wegen Zeit ab; für einen Ryzen-Produktionslauf ist der GC-19-Controller vorzuschalten.
Gerechnet wurde in einer 1-Kern-Sandbox (keine Ryzen-Zeiten).

## Dateien

| Datei | Zweck |
|---|---|
| `width_dp.py` | Exakte Projektionsbreiten im ROOT8105-Zeilenmodell. Tiefe 1: reines Kanten-DP (`width_fast`). Beliebige Tiefe: `width_exact` = Summe über Adjazenzmuster der Zielzeile in die Sterne gebauter Nachbarn von [Sternsystem erfüllbar] × DP-Zählung. |
| `root_audit.py` | Unabhängiger Rootzensus über explizite Gruppe G_u (Ordnung 7680), ohne nauty. |
| `crosscheck_sat.py` | Abgleich `width_exact` gegen unveränderten Pilot-`core.encode` + erschöpfende Glucose-Enumeration. |
| `bvls_control.py` | Vollmodell-Positivkontrolle SRG(243,22,1,2) bei m=11 und Negativkontrolle (falsche Paarbedingung). |
| `census_level1.py` | Vorgeschlagene Phase P1: alle Roots × 83 Ziele, exakt, fortsetzbar, Multiprozess. |
| `probe_level2.py` | Prototyp Phase P2: Knuth-Probe auf Ebene 2 mit fester Regel R1. |
| `results/` | Ergebnisse der unten aufgeführten Läufe. |

Abhängigkeiten: Python ≥ 3.10, numpy, python-sat. Für `crosscheck_sat.py`, `bvls_control.py`,
`probe_level2.py` zusätzlich das Pilotverzeichnis `experiments/memetik/root8105_pilot_1_0_1`
(core.py, completion.py; pynauty wird bei Fehlen durch einen Stub ersetzt, encode nutzt es nicht).

## Modell (aus core.py rekonstruiert)

Randknoten 0..13, Matching a↔a+7, Labels = 84 nicht gematchte Paare. Zeile von Label t =
Labelmenge R ∌ t mit Gradprofil `margins(t)`. `core.encode(S,t)` verlangt: Margen von t,
Paarbedingung t–gebaut (|R ∩ N(s)| = 2 − e − |t∩s|) und für jede gebaute Zeile s die
Sterngleichungen ihrer offenen Nachbarn (Σ_{w∈N(s)} edge(v,w) = 1 − |s∩v|).

**Wichtige Lehre:** Die Sternsysteme verschiedener gebauter Zeilen sind über Labels gekoppelt, die
in zwei Nachbarschaften liegen. Ein DP mit nur einer Schnittbedingung je gebauter Zeile überzählte
in 2–9 % der Fälle, auch mit Restgradregeln je Stern. Beispiel m=4: (4,7) ist in N(u) gepaart, in
N((4,6)) isoliert, daher ist die Paarung (2,3)–(4,7) verboten. `width_exact` prüft deshalb für jedes
Adjazenzmuster das gesamte Sternsystem mit einem kleinen SAT-Aufruf.

## Ausgeführte Prüfungen und Ergebnisse

| Prüfung | Ergebnis |
|---|---|
| Rootzensus (`root_audit.py`) | PASS: 8105 paarweise inäquivalente Klassen, Stabilisatoren korrekt, Orbitsumme 56 011 010 = unabhängige DP-Zählung aller margengültigen u-Zeilen |
| Tiefe 1, m=4 / m=5 | 3×23 bzw. 3×39 Fälle, 0 Abweichungen |
| Tiefe 1, m=7, Root 1, Ziel (0,8) | SAT 173 365 = DP (zweimal unabhängig enumeriert) |
| `width_exact`, m=4 Tiefe 2/3, m=5 Tiefe 2/3/4 | 660 / 567 / 950 / 851 / 540 Fälle, 0 Abweichungen |
| `width_exact`, m=7 Tiefe 2 | 2 exakte Übereinstimmungen (22 311; 115 976); 2 SAT-zensiert nach 60 s, Untergrenzen konsistent |
| `width_exact`, m=6 und m=7 Tiefe ≥ 3 | **nicht geprüft** (Pflichtpunkt P0) |
| BvLS (`bvls_control.py`) | PASS: Golay-Code 729 Wörter, d=5; SRG-Identität; Pilot-`verify` aller 220 Zeilen und `verify_complete` = SRG_FOUND_VERIFIED; 33/33 Präfixe (Tiefe 1–219) mit Zeugenbelegung SAT; margen- und gradtreue Zeile mit falscher Paarzahl: `verify` → `common neighbors`, encode UNSAT |
| Ebene-1-Breiten der 128 Pilot-Roots, alle 83 Ziele | `results/widths128.jsonl`, Auswertung `results/widths128_summary.json` |
| Ebene-2-Probe Root 1 | `results/probe_level2_root1.jsonl` (wenige Stichproben, siehe Antworttext) |

`census_level1.py` ist auf Root 1 und 9 identisch mit `widths128.jsonl`. `crosscheck_sat.py` enthält
dieselbe Prüflogik wie die oben gezählten Läufe, wurde in dieser Paketform aber nur
syntaxgeprüft und nicht nochmals vollständig ausgeführt.

## Bekannte Grenzen

- Breiten gelten für die lokale Relaxation F des Piloten, nicht für stärkere Filter.
- `width_exact` setzt voraus, dass `core.encode` genau die oben genannten Gleichungen enthält.
  Bei Encoderänderung neu abgleichen (GC-20).
- Laufzeit `width_exact` auf Tiefe 2: in der Sandbox etwa 3–8 s je Ziel. Für P2 ist das
  Kandidatenmengen-Design vorab festzulegen; Kandidatenmessung gehört zu den Probenkosten.

`results/probe_level2_root1.jsonl` wurde mit dem Sandbox-Prototyp
`results/probe_level2_root1_generator.py` erzeugt (Root 1, t1=(0,8), Seed 4711, Kandidaten =
offene Ziele adjazent zu u oder t1), gleiche Regel wie `probe_level2.py`. Lauf nach 3 Stichproben
wegen Sandbox-Laufzeit beendet.
