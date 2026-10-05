# Augmentation-Pilot ↔ Memetik H-Faser Handoff — 2026-10-04

## Pilotabschluss

Der ROOT-8105 / Augmentation-Pilot ist als `PILOT_COMPLETE` abgeschlossen:

- 256 Suchjobs, sämtlich `CPU_LIMIT_UNKNOWN`;
- 512 Proofjobs, sämtlich `PROJECTED_COVERAGE_DRAT_VERIFIED`;
- 276.26 CPU-hours;
- maximale beobachtete Tiefe 16;
- 1,447,471,813 beobachtete Rows;
- 33,748,941,099 Projektionsbytes;
- 512 zertifizierte projected closures;
- 0 zertifizierte Root-Ausschlüsse.

Wichtig: sampled parents, Beam-Truncation und zensierte Widths erlauben **keine** Aussage „Tiefe 16 ist eine Barriere“ und **keine** Root-Erschöpfung.

## Neuer memetischer Befund, der für die Fortsetzung relevant ist

Der parallel untersuchte exakte H-Raum ist lokal deutlich starrer als der bisherige Operator-Katalog vermuten ließ:

- kleinster exakter H-Move: 8 Vertices / 16 Kanten;
- alle minimalen 8/16-Moves sind exakt die bekannten Omega-4x4-Moves;
- cand_A: 0 exakte H-Nachbarn in jeder vollständig geprüften Distanz 16–24;
- cand_B: genau 2 Nachbarn bei Distanz 16, 0 bei 17–24;
- erweiterte Produktfamilien 4x8, 4x10, 4x12, 6x8 liefern auf cand_A und cand_B ebenfalls 0 Moves.

Ausführlicher Stand:
`docs/memetik/H_FIBRE_INVESTIGATION_2026-10-04.md`

Maschinenlesbare Zusammenfassung:
`results/memetik/H_FIBRE_INVESTIGATION_20261004.json`

### Update 2026-10-05: globaler Nearest-H-Lauf

H-FIBRE-NEAREST 0.7.0 liefert zusätzlich:

- cand_A: verifizierter anderer H-Zustand bei Distanz 184; zertifizierte Untergrenze 25, also derzeit **25 ≤ d_min ≤ 184**;
- cand_B jenseits der beiden bekannten 16er-Nachbarn: verifizierter Zustand bei Distanz 28; Untergrenze 25, also **25 ≤ d_min^(>16) ≤ 28**.

Für cand_B sind damit nur noch die Shells 25, 26 und 27 offen. Dieser sehr enge Abstand ist für Augmentation besonders interessant: lokale exakte Moves fehlen bis 24, aber ein global anderer Zustand existiert bereits bei 28. Das ist ein guter Test dafür, ob eine konstruktive Präfixsuche solche kurzen, aber nicht durch den alten lokalen Move-Katalog sichtbaren Übergänge erschließen kann.

## Empfohlene Nutzung im nächsten Augmentation-Schritt

### 1. Planted positive controls

Verwende Präfixe aus vollständigen H-Zeugen als garantiert completable Instanzen.

Besonders wertvoll:

- **cand_A** als lokal stark isolierter Stressfall;
- **cand_B** als fast-isolierter Stressfall;
- root witness 1/2 als deutlich beweglichere Kontrollen.

Teste z.B. fest gepflanzte Präfixtiefen 16, 24, 32 und darüber. Wenn der Augmentation-/Completion-Stack auf einem aus einem vollständigen H-Zeugen entnommenen Präfix nicht robust weiterkommt, ist das ein Such-/Oracleproblem und kein Existenzproblem.

### 2. Tiefe 16 nicht überinterpretieren

Die Pilotbeobachtung max_depth=16 und die H-Faser-Isolation sind kompatibel, aber logisch verschieden. Aus keinem der beiden Befunde folgt eine globale konstruktive Barriere.

### 3. Nicht nur kleine exakte H-Nachbarschaften augmentieren

Die memetische Untersuchung spricht dagegen, die nächste Generation ausschließlich als lokale Folge exakter H-Moves zu planen. Sinnvolle Alternativen für den Augmentation-Zweig sind:

- größere globale Rekonstruktion;
- zeitweilige H-Defekte mit späterer Reparatur;
- canonical augmentation auf Präfixebene mit einem Completer, der nicht an eine lokale exakte H-Nachbarschaft gebunden ist.

### 4. Nächste Kalibrierung vor Großlauf

Vor einem weiteren sehr großen ROOT-8105-Lauf sollte eine kleine planted-control-Matrix messen:

- Erreichbarkeit pro gepflanzter Tiefe;
- Completion-Walltime;
- UNKNOWN-Rate;
- Einfluss von Row-Order / Branching;
- ob bekannte vollständige H-Zeugen systematisch wiedergefunden werden.

Das liefert eine sauberere Diagnose als ein weiterer großer sampled Pilot ohne garantierte Positivfälle.
