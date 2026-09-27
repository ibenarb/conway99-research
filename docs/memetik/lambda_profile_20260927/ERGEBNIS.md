# λ-Profil vom 27.09.2026: geprüftes Ergebnis

## Ergebnis und Umfang

**5685 abgeschlossene Episoden, keine Verbesserung nach (W,L1), kein neuer
W-Rekord.** Auch die gespeicherten Zwischenbewertungen weisen keine
Verbesserung aus. 16 Zellen erreichten jeweils 300 Episoden. Vier Zellen
(k=24 und k=32 für beide Starts) endeten am nutzbaren Zellbudget;
315 geplante Episoden fehlen. Gesamtstatus `INCOMPLETE` ist somit korrekt.
Kein globales negatives Urteil aus unvollständigen Zellen.

Die Wiederaufnahme endete am 27.09.2026 um **12:32:10 MESZ**.
Kumulierte aktive Windows-Hostzeit: 4328,681715 s = 72 min 8,68 s;
davon Wiederaufnahme 1240,9133835 s = 20 min 40,91 s. Die Unterbrechung
zur Diagnose ist darin nicht enthalten. Suchzeit 10,202277 CPU-h,
insgesamt einschließlich Hilfsbudget/Reservierungen 10,233868 CPU-h.
Die Grenze einer Stunde pro Zelle galt ohne Budgetübertragung; das
ungenutzte Gesamtbudget erlaubte keine automatische Verlängerung.

## Rückkehrprofil

Rückkehr bezeichnet den exakt beschrifteten Startgraphen; isomorphe
Rückkehrzählungen stimmen hier damit überein. Verschiedene beobachtete
Endklassen sind kein Beweis unabhängiger Suchbecken.

| k | N ab W2076 | Rückkehr ab W2076 | N ab W2077 | Rückkehr ab W2077 |
|---|---:|---:|---:|---:|
| 1 | 300 | 100,00 % | 300 | 100,00 % |
| 2 | 300 | 99,00 % | 300 | 99,00 % |
| 3 | 300 | 99,00 % | 300 | 98,67 % |
| 4 | 300 | 98,67 % | 300 | 99,33 % |
| 6 | 300 | 97,67 % | 300 | 96,33 % |
| 8 | 300 | 95,00 % | 300 | 95,33 % |
| 12 | 300 | 82,33 % | 300 | 77,00 % |
| 16 | 300 | 64,33 % | 300 | 64,33 % |
| 24 | 245 | 33,47 % | 250 | 31,20 % |
| 32 | 194 | 5,67 % | 196 | 8,67 % |

Insgesamt 4586 Rückkehren von 5685 Episoden (80,67 %), aber diese gepoolte
Zahl ist von der hier gewählten Längenverteilung abhängig. Die gemessenen
CPU-Kosten steigen von rund 1,1 s pro fertiger Episode bei k=1 auf
18,3–18,5 s bei k=32. Die Kosten enthalten den verbuchten Workeraufwand,
bei unvollständigen Zellen auch Kosten der angefangenen letzten Episode.
Rückkehrquote ist ausdrücklich kein CPU-Verlustanteil.

**Interpretation:** Größere k verhindern in diesem Profil die Rückkehr
häufig, führen aber zu keinem besseren Endminimum. Eine reine Erhöhung
der Perturbationslänge ist damit bislang nicht als Verbesserung begründet.
Die Daten belegen weder Erschöpfung noch eine Erfolgswahrscheinlichkeit null.
Für die vollständig beobachteten Nullzellen wäre unter dem üblichen
IID-Modell die einseitige 95-%-Obergrenze je Zelle 0,9936 %; das ist keine
simultane Aussage. Budgetbedingt gestoppte Zellen können von einer festen
IID-Stichprobe abweichen und werden nicht als 0/300 behandelt.

## Ein konkret überprüfter naher Endpunkt

Es gibt genau eine andere beobachtete Endklasse mit
W ≤ W(Start)+2, erreicht nur ab W2076, insgesamt 17-mal:

- W=2077, L1=2488, F=3348, Linf=3, Nmax=19;
- state `e1edc9cb193240624c35e8a2fe0502f523349ec3b828ea31d6316c467a3ea72d`;
- Klasse `0b96da05e7ed675cd563d7fd6921af0d411e022bd69d2020d1c6a6bdfd2a6321`.

**Dieser Graph ist nicht die bekannte alternative W2077/L1=2436-Linie.**
Episode 183 bei k=2 erreicht ihn über
(2076,2488) → (2079,2492) → (2077,2488), ohne anschließenden Abstieg.
Beide Pivot-Züge wurden im eingefrorenen Katalog nachgespielt und ihre
Graphen unabhängig bewertet. Alle 97 Katalognachbarn des Endpunkts wurden
zusätzlich unabhängig nachgerechnet: keiner ist besser oder gleich nach
(W,L1). Damit ist hier ein anderes striktes lokales Minimum belegt,
kein Neutralplateau. Die maximale Erhöhung von W um drei gilt für diesen
konkreten Pfad; eine minimal notwendige Barriere wurde nicht berechnet.

## Prüfung und Grenzen

Eingangsarchiv `ryzen_lambda_profile_100_20260927_recovery_101_results.tar.gz`:
SHA256 `ccdb709a98ab0e5f32794807955026e1fe2819364de668f9eb3c37fe4854c2f3`.
Dieser Hash wurde hier berechnet; ein separat übermittelter Sollhash des
Endarchivs lag nicht vor. Der zuvor geprüfte Unterbrechungssnapshot hat
SHA256 `8a95e0a04416dd15acf620b7f54e5ea4389434ce0031fe2b266c700bd8b0d7fb`.

Geprüft: Original-Fingerprint, Quellmanifest, Wiederaufnahmequellen gegen
veröffentlichtes Paket 1.0.1, sämtliche Task-/Resultat-/Checkpoint-Receipts,
20 SQLite-Integritätsprüfungen, Episodenindizes und Seeds, JSONL/SQLite-
Übereinstimmung, Endprofil und CPU-Abrechnung. Alle **5099 alten Episoden
sind byteidentisch erhalten**. Keine offene Sitzung oder Workerreservierung.
Alle **887 verschiedenen Endgraphen und 887 Klassen** mit dem bestehenden
unabhängigen Score-/λ-Prüfer und pynauty 2.8.8.1 reproduziert.
Nicht jede komplette Suchtrajektorie oder jeder Steilstabstieg wurde in der
Cloud wiederholt. Die Nullzahl für Zwischenverbesserungen wurde aus allen
gespeicherten Pfadbewertungen überprüft, nicht durch erneute Bewertung aller
Zwischengraphen. Gezielter vollständiger Nachbarschaftstest nur für den
oben genannten nahen Endpunkt.

Die doppelte Controller-CPU-Abfrage ergibt kumuliert eine Differenz von
15 Mikrosekunden zwischen Sitzungsbelegen und Ledger (zuvor 6 Mikrosekunden);
dies wird mit 1-ms-Toleranz behandelt. Worker-CPU ist über wait4-Belege
nachvollzogen; keine Budgetüberschreitung.

Prüfcode und Ausgaben: `final/audit_final.py`, `final/AUDIT.json`,
`final/check_near.py`, `final/NEAR_CHECK.json`. Ausführen ausschließlich über
`tools/memetik/audit_python.py --`; Audit erhält Endlauf und ursprünglichen
Unterbrechungslauf als Argumente, Nahpunktprüfung nur den Endlauf.

## Folgerung für die Fortsetzung

Die vorab vorgesehene Trefferregel für einen neuen Längen-Bestätigungslauf
ist nicht erfüllt. Ein großer unveränderter P-Lauf, automatisches Radius 5
oder bloße Verlängerung der langen Zellen ist durch diese Daten nicht
begründet. Der Versuch ist als budgetbegrenztes Profil abgeschlossen.

Empfohlener nächster Schritt ist eine kleine strukturelle Auswertung der
**drei** jetzt klar unterschiedenen lokalen Minima: ursprüngliches W2076,
ursprüngliches W2077/L1=2436 und der oben nachgewiesene W2077/L1=2488-Nachbar.
Fragestellung: Welche Residuen und Katalogzüge unterscheiden das erreichbare,
aber schlechtere Nachbarminimum von den beiden bisherigen Starts? Erst eine
konkrete daraus abgeleitete Akzeptanz- oder Operatorhypothese rechtfertigt
einen neuen kontrollierten Suchplan. Das ist ein Vorschlag, kein gestarteter
Suchlauf und kein behaupteter Vorteil einer anderen Zielfunktion.
