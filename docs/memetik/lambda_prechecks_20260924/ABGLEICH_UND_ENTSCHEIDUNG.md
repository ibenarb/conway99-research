# Reviewabgleich und freigegebene Umsetzung, 24. September 2026

Ausgang: Folgelauf im Commit 7f146a20bd80364cef66492632bb0e7478b89122.
Revieweroriginal und Eingangs-ZIP byteidentisch im separaten Archivzweig
[reviews/20260923-lambda-followup](https://github.com/ibenarb/conway99-research/tree/c7215b3d16c99169381cac3175506bd6480748d2/docs/reviews/20260923_lambda_followup).
Der Nutzer hat die nachfolgende 34-CPU-h-Etappe ausdrücklich zur Umsetzung freigegeben.

## Übernommene Befunde

Die unabhängigen Reviewer-Skripte check_scores.py und analyse_run.py wurden
nochmals auf dem publizierten ZIP ausgeführt: 9827 Scoreeinträge, 1496 verschiedene
beschriftete Graphen, keine λ-/Scoreabweichung. W=2102 und L1=2380 bestätigt.
Durchsatz P 406,6 gegen PC 197 Episoden/CPU-h bestätigt. Die nauty-Auswertung des
Reviews wurde zum Zeitpunkt des inhaltlichen Abgleichs mangels installiertem
pynauty nicht erneut ausgeführt und wird als Reviewerbefund gekennzeichnet.
Für die jetzige Implementierung ist pynauty 2.8.8.1 installiert; die neuen
Startbanken werden damit unabhängig auf 16 verschiedene Klassen geprüft.

## Korrekturen der Interpretation

- Linf-Jobs haben 57998 Züge adoptiert, aber keinen neuen Bestwert erreicht.
  Erfolgloser Bestwertverlauf ist nicht Stillstand. Ein AP-Minimum schließt
  Verbesserung durch Perturbation nicht aus.
- Die vier gezählten Startgraphen sind curves[0], also anfängliche Bestwerte.
  Methodenjobs hatten 16 Gründer (5 HoG, 10 Z33_lift, 1 triangle_packing).
- HoG-Abstammung, Starrheit und Kantendistanzen beweisen kein einziges Becken;
  ein negatives Budgetexperiment beweist keine Erschöpfung eines Beckens.
- Der Vierpunkt-Logarithmusfit von einer bis vier Stunden beschreibt abnehmenden
  Ertrag, rechtfertigt aber keine gesicherte 53000-Stunden-Prognose oder einen
  mathematischen Ausschluss späterer Sprünge.
- PC-Kosten sind belegt; ausschließlich Kosten als Ursache ist nicht belegt,
  weil der zusätzliche Operator auch die Suchtrajektorien verändert.
- endpoint_Linf2_N262 ist laut task.json HoG-abstämmig und fällt als Nicht-HoG-
  Gründer aus. Alle vier V3-Ursprünge des neuen Plans sind geprüft.
- PC--W-03 und PC--W-10 haben identische Bestgraphen. Die Aussage über 24
  paarweise nichtisomorphe Methodenendpunkte ist deshalb falsch. Die 1496
  zuvor deduplizierten Graphen widersprechen diesem Duplikatbefund nicht.
- Vier Siege aus acht sind kein Überlegenheitsnachweis: unter acht unabhängigen
  fairen Bernoulli-Versuchen ist P(X>=4)=163/256=0,63671875.

## Entscheidung

Kein unmittelbarer Hauptlauf. V1 (cycle3 nur am exakten AP-Minimum) und V3
(getrennte Nicht-HoG-Linien) werden umgesetzt. V2-Rekordfortsetzung bleibt aus.
Neu gerechnete gepaarte Kontrollen statt historischem Pext-Vergleich. Keine
universelle Verwerfung von cycle3 oder Konstruktionsfamilien aus negativem Screen.
Details, Entscheidungen und Budgets stehen in der experimentellen
[README](../../../experiments/memetik/lambda_prechecks_1_0_0/README.md).

V3 benötigt aufgrund der eingefrorenen Auswahl 16 reale Gründer pro Population.
Daher wird pro Herkunftslinie eine kleine feste AP-Walk-Bank ohne Fitnessauswahl
gebildet: ursprünglicher Gründer plus 15 neue Isomorphieklassen. Beide Replikate
verwenden dieselbe Bank. Die 60 aufgezeichneten Übergänge werden replay-geprüft.
Dieser konkrete Aufbau misst die Umgebung der jeweiligen Herkunftslinie;
keine HoG-Zumischung, keine Migration, kein Anspruch unabhängiger Becken.

Die Kampagne ist vorbereitet, aber noch nicht auf dem Ryzen gestartet. Die
Windows-/WSL-Produktionsgates sind dort zwingend und nicht durch lokale
Containerprüfungen ersetzt.
