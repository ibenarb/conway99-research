# Prüfsatz zum Review „nächster Schritt nach der λ-Radiusprüfung“

Stand 27.09.2026. Erstellt in einer Anthropic-Cloud-Sandbox (ein Kern, Python 3.12,
pynauty 2.8.8.1, networkx 3.6.1), **nicht auf dem Ryzen**. Kein Suchlauf programmiert
oder gestartet; alle Rechnungen sind kleine Prüfungen im Sinne des Reviewauftrags.
Eingaben und gepinnte Commits: `QUELLEN.json`. Gelesener Auftrag: `REVIEWPROMPT_gelesen.md`
(Commit 9ffa817).

## Ergebnisse

| Skript | Prüft | Ergebnis |
| --- | --- | --- |
| `indep_scores.py` | Drei STARTS-Graphen mit eigenem networkx-Scorer, ohne Projektcode | W/L1/F/Linf/Nmax und state-Hashes stimmen; λ auf jeder Kante; sum_nonedge r = 0; F = 4(Q−2079), Q = 2917/2874/2911 |
| `layers12.py` | Schichten 1/2 mit eingefrorenem Katalog; Kontrollpfad W2079→W2076 | 99/5222 bzw. 95/4768; keine Verbesserung; Meet-in-the-middle-Distanz genau 4 |
| `twoswitch_completeness.py` | Alle λ-erhaltenden 2-Switches per Brute-Force gegen Pivot-Katalog | 56 bzw. 60, Differenz 0 in beide Richtungen |
| `cycle3_census.py` | Ausgeschlossene cycle3-Züge an der Wurzel | 43 bzw. 35, keiner verbessert auf Tiefe 1 |
| `episode_histograms.py` | Rückkehrquote der P-Episoden aus den F/O-Resultatdateien des flachen Pakets | F 76,9 %, O 79,2 % der Episoden enden exakt im Elternzustand |
| `depth3_resume.py` | Vollständige Tiefe-3-Nachzählung beider Arme, Checkpoints, Stichprobe mit unabhängigem Scorer | siehe unten |

Tiefe 3, beide Arme vollständig:

| Arm | Eltern | Kinder | Neue verschiedene Tiefe-3-Zustände | Verbessernd | Stichprobe | CPU-s |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| W2076 | 5222 | 526476 | 195508 | 0 | 400/0 Abweichungen | 1262 |
| W2077 | 4768 | 459185 | 169048 | 0 | 400/0 Abweichungen | 1218 |

Alle Zahlen stimmen exakt mit `DEPTH3_VERIFIED.json` und den Merge-Zählungen des
Ryzen-Laufs überein. Beste (W,L1) je exakter Tiefe 1/2/3:
W2076: (2078,2488) / (2077,2488) / (2082,2498);
W2077: (2080,2436) / (2083,2452) / (2085,2450).

## Grenzen

- Tiefe 4 (36,28 Mio. Übergänge) und die SQLite-Zustandsmengen wurden **nicht** neu berechnet.
  Die Tiefe-4-Abdeckung ist über die unabhängig bestätigte Tiefe-3-Zustandszahl und die
  lückenlose Job-ID-Partition des Rückgabearchivs gestützt, nicht vollständig reproduziert.
- Tiefe 3 nutzt den eingefrorenen Katalog- und Scorercode; unabhängig sind nur die
  Stichprobenbewertung und die Zählung. Gemeinsamer Operatorcode bleibt eine gemeinsame Fehlerquelle.
- Verschiedene Zustände werden über blake2b-128-Digests gezählt (Kollisionen als vernachlässigbar angenommen).
- Vollständigkeit von Apex ∪ Pivot für 3-/4-Switches ist nicht geprüft.
- Die Arm-2077-Rechnung wurde nach einer Sandbox-Pause am Checkpoint fortgesetzt;
  `depth3_2077.log` zeigt beide Sitzungen. CPU-Angaben sind Sandbox-Werte.
- `depth3_2076.log` enthält nur die abschließende, ununterbrochene Sitzung; ein früherer,
  durch Sandbox-Pause abgebrochener Versuch ohne Checkpoint ist nicht enthalten.

## Reproduktion

Voraussetzung: Commit 8ec085c unter `/home/claude/src` entpackt (Pfade in den Skripten anpassen),
Rückgabearchiv und flaches Paket entpackt. Dann `python3 <skript>.py`; die Tiefe-3-Zählung mit
`python3 depth3_resume.py 2076` bzw. `2077` (je ≈ 20 CPU-Minuten). `SHA256SUMS` listet alle Dateien.
