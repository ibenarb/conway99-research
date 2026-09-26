# λ-Memetik: Reviewabgleich und Fortsetzungsvorschlag, 26.09.2026

**Empfehlung:** Den unveränderten stochastischen P-Lauf pausieren. Als nächste,
begrenzte Untersuchung eine deterministische Prüfung der beiden Rekordgraphen
bis Tiefe 4 vorbereiten, mit nachgeholter vollständiger Tiefe-3-Reproduktion.
Keine automatische Folgekampagne und kein endgültiger mathematischer
Erschöpfungsanspruch. Dieser Vorschlag ist noch nicht implementiert oder gestartet.

## Quellen und Trennung

[Byteidentisches Revieweroriginal, Prüfsatz und Eingangsidentität](https://github.com/ibenarb/conway99-research/tree/7a00a6a93227eb7eb09980355b4d3129975489fc/docs/reviews/20260926_lambda)
liegen ausschließlich im eigenen Archivzweig `reviews/20260926-lambda`.
Dieses Dokument ist die separate eigene Bewertung.

Verbindliches Datenpaket: `releases/memetik/Lambda_Review_20260926.zip` in
`c3197a2cad41d9b6e9f72ba9b90e63fb98a30b14`, SHA256
`85604ac1218a55f6601a76e589360611886e99ffd518ba571886629b2cba15d7`.
Der Hash wurde erneut bestätigt. `00_REVIEWERPROMPT.md`,
`01_DATENUEBERSICHT.md` und das neue Review wurden vollständig gelesen.
Die früheren Projektabgleiche vom 24.09. wurden zur Einordnung gelesen;
ihre ursprünglichen Rohprüfungen wurden nicht erneut ausgeführt.

## 1. Eigene Reproduktion

Alle Prüfungen liefen über `tools/memetik/audit_python.py` mit isoliertem
pynauty 2.8.8.1. Keine Ryzen- oder Office-Umgebung wurde verändert.

| Aussage | Eigener Prüfstand |
| --- | --- |
| Paketintegrität, λ-Zulässigkeit, fünf Scores, state-Hashes | PASS: 1465 unterschiedliche Graphen, 2318 Vorkommen, 126 Manifesteinträge |
| Reviewer-Endpunktanalyse, Abstandsmatrix, Raten und heuristische Zuordnung | Gesamtes `analysis_result.json` byteidentisch reproduziert; 22 Endpunkte, 12 verschiedene Graphen |
| Isomorphie über die Endpunkte hinaus | Alle 1465 Graphen kanonisiert; 1465 Klassen. Alle 1140 vorhandenen `class`-Vorkommen stimmen als vollständige SHA256 überein |
| Sieben (W,L1)-Minima bis Tiefe 2 | Vollständig reproduziert; alle Zähler identisch, abgesehen von Laufzeiten |
| Beschriftete Zugabstände 2081→2079 und 2079→2076 | Jeweils genau 4 im eingefrorenen Apex/Pivot-Katalog reproduziert |
| Beschrifteter Zugabstand 2096→2081 | Größer als 4 reproduziert |
| Minima bis Tiefe 3 bei 2076 und 2077 | Reviewerbefund, nicht erneut vollständig ausgeführt. Code und Endzähler geprüft, kein offensichtlicher Abdeckungsfehler gefunden |
| Große SQLite-Archive, vollständige Receipts und Host-Zeiten | In dieser Runde nicht neu geprüft; früherer Audit laut Übergabe |

Die Reviewer-Tiefe-3-Dateien melden vollständig 5222/5222 bzw. 4768/4768
Tiefe-2-Zustände und 526476 bzw. 459185 Kinder ohne Verbesserung. Die
Zustandslisten/Checkpoints liegen der Einreichung nicht bei. Diese Zahlen sind
keine von uns erneut ausgeführte vollständige Tiefe-3-Prüfung und kein formales
Beweiszertifikat. Gemeinsamer Operatorcode bleibt eine gemeinsame Fehlerquelle.

Der Zähler 125 in `05_CHECK_RESULT.json` ist gegenüber dem aktuellen Manifest
veraltet. Das Manifest hat 126 Einträge und enthält auch `05_CHECK_RESULT.json`.
Das ist mit einer Aufnahme des alten Prüfberichts nach dessen Erstellung
vereinbar; die genaue Erstellungsreihenfolge ist daraus allein nicht bewiesen.
Alle 126 aktuellen Hashes stimmen. Das fixierte Originalpaket bleibt unverändert;
der aktuelle Prüfbericht nennt korrekt 126.

## 2. Mathematische Einordnung

Für alle gültigen λ-Kandidaten gilt mit ungeordneten Paaren und Q als Anzahl
nichtorientierter Vierkreise exakt

\[
\sum_{uv\notin E}r_{uv}=0,\qquad L_1=2\sum r_{uv}^{+},\qquad F=4(Q-2079).
\]

Denn es gibt 693 Kanten und 4158 Nichtkanten; die Summe der gemeinsamen
Nachbarn auf Nichtkanten ist 8316. Ferner gilt
`sum_nonedge binom(CN,2) = 2Q`, da eine Kante nur einen gemeinsamen Nachbarn
hat und somit keine Vierkreisdiagonale sein kann. Mit
`CN² = 2*binom(CN,2)+CN` folgt die Identität unmittelbar.
Dies ist eine algebraische Umformulierung der Zielfunktion, kein zusätzlicher
unabhängiger Lösungsindikator. Sowohl W=0 als auch F=0 charakterisieren im
λ-Raum exakt die gesuchte SRG-Bedingung. Keiner dieser Werte gibt ohne weiteren
Nachweis den Abstand in zulässigen Zügen zur Lösungsmenge an.

| Eigenschaft | Rekord W2076 | Alternative W2077 |
| --- | ---: | ---: |
| W | 2076 | 2077 |
| L1 | 2488 | 2436 |
| F | 3352 | 3180 |
| Q | 2917 | 2874 |
| Q−2079 | 838 | 795 |
| Automorphismengruppenordnung | 1 | 1 |
| Knotenorbits | 99 | 99 |
| Kleinste/größte knotenweise L1-Last | 34 / 62 | 34 / 68 |

Residuenhistogramm auf den 4158 Nichtkanten:

| r | −2 | −1 | 0 | +1 | +2 | +3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| W2076 | 169 | 906 | 2082 | 778 | 203 | 20 |
| W2077 | 150 | 918 | 2081 | 813 | 183 | 13 |

Die W2077-Alternative hat insgesamt geringere quadratische und absolute Last,
aber eine höhere maximale knotenweise L1-Last. Beide sind asymmetrisch.
Dies belegt konkrete Unterschiede, keine allgemeine strukturelle Überlegenheit.
Die beschriftete Kantensymmetriedifferenz beträgt 128; das ist weder die minimale
Distanz über alle Umnummerierungen noch ein Nachweis getrennter Suchbecken.

Die empirische (W,F)-Paretofront **dieses Pakets** umfasst fünf Punkte:
`(2076,3352), (2077,3180), (2078,3172), (2097,3088), (2143,3084)`.
Zu jedem Punkt liegt hier genau ein Graph vor. Insbesondere ist W2077 nicht
einmal innerhalb dieses Pakets F-optimal. Der ältere F-Rekord 2836 ist nicht
Teil dieser Neuberechnung. Ein Wechsel zu F allein folgt aus dem Review nicht.

## 3. Zustimmung und notwendige Korrekturen

**Zustimmung:** Die neuen W-Rekorde sind echt. Beide Frontier-Linien bleiben
aufbewahrenswert. Das späte Budget brachte keinen kampagnenweiten W-Rekord;
ein großer unveränderter Hauptlauf ist weiterhin nicht begründet. Die gemessene
W-Schubrate 26/32=0,8125 (F), 13/32=0,40625 (O bis 4 h), 1/24≈0,04167
(O danach) ist reproduziert. Nenner sind nominale CPU-Budgets; Schübe werden
mit einer 60-Sekunden-Regel zusammengefasst. Das ist eine deskriptive Rate,
kein kontrollierter oder statistisch unabhängiger Methodenvergleich.

**Korrekturen:**

1. **„Bankerneuerung, nicht Laufzeit“ ist nicht kausal belegt.** Neue Banken,
   zusätzliche CPU-Zeit, neue Seeds und adaptive Auswahl ändern sich gemeinsam.
   D/V3 betrifft andere Startbedingungen. Ein kontrollierter Vergleich fehlt.
   Auch „nach 1–3 h eingefroren“ ist zu stark: mehrere letzte W-Ereignisse liegen
   später, eines bei 4,75 h. Bestwertplateau bedeutet zudem nicht Zustandsstillstand.
2. **„Keine neue Klasse nach vier Stunden“ stimmt so nicht.** Gegenüber sämtlichen
   bis 4 h gespeicherten O-Bestwertkurven erscheinen drei weitere Klassen:
   W2078/L1=2488 bei 4,751 h als Zwischenzustand, W2078/L1=2490 bei 6,167 h und
   W2084/L1=2458 bei 6,489 h. Der erneute W2076 ist dieselbe bekannte Klasse.
   Das sagt nicht, dass diese Klassen zuvor nirgendwo in einer Population oder
   SQLite-Datenbank vorhanden waren. Richtig bleibt: kein neuer globaler W-Rekord.
3. **Nächster Gründer ist keine rekonstruierte Abstammung.** Die Rechnungen zur
   beschrifteten Distanz stimmen, aber „stammt aus Gründer 8/2“ und „Vielfalt war
   entscheidend“ gehen darüber hinaus. Dafür fehlen Elternketten oder Replay.
4. **W und F liefern widersprechende Ordnungen.** Linie A verbessert W bei
   schlechterem F. „Entfernt sich algebraisch“ ist nur relativ zu F/Q korrekt;
   daraus folgt kein größerer Suchabstand. „W2077 strukturell besser“ ist zu ersetzen
   durch die konkret belegten Unterschiede. Der höhere Spitzenwert der Knotenlast
   illustriert gerade, dass „besser“ ein benanntes Kriterium benötigt.
5. **Kürzeste Distanz ist nicht die ausgeführte Trajektorie.** Die zwei
   Vier-Zug-Abstände zwischen fest beschrifteten Endpunkten sind bestätigt;
   damit ist nicht bewiesen, dass der Produktionslauf genau diese Wege oder
   Perturbationslänge 4 benutzt hat. Kürzere Perturbation plus längerer Abstieg
   und längere Perturbationen bleiben möglich.
6. **Ein lokales Nullergebnis schließt nur die geprüfte Umgebung aus.** Ein
   vollständiges negatives Tiefe-4-Ergebnis würde bedeuten: keine strikt
   (W,L1)-bessere Konfiguration in höchstens vier Apex/Pivot-Zügen von genau
   diesen Startgraphen. Falls eine bessere Konfiguration erreichbar ist, liegt
   ihr Abstand dann mindestens bei fünf. Es wäre keine Erschöpfung der Banken,
   der W-Frontier oder des λ-Suchraums. „Endgültig schließen“ wäre eine
   Ressourcenentscheidung, kein mathematischer Schluss.
7. **Eine Verbesserung bei W2077 ist nicht automatisch ein globaler Rekord.**
   Schon gleiches W mit kleinerem L1 zählt lokal als Verbesserung. Globaler
   W-Rekord erfordert W<2076. Auch die vorgeschlagene E3-Grenze W≤2071 ist eine
   frei gewählte Budgetregel, nicht aus den Daten abgeleitet.

Die ursprüngliche Vorabentscheidung für sieben Stunden und die unveränderte
Erfolgsschwelle werden ausdrücklich respektiert. Keine nachträgliche Bewertung
als Protokollverletzung. Vorprüfungen zu PCesc und Nicht-HoG behalten ihre
begrenzte Aussagekraft; kein allgemeiner Operator- oder Familienausschluss.

## 4. Konkreter Vorschlag: begrenzte lokale Diagnose, dann Neubewertung

**Fragestellung:** Sind die beiden fixierten Rekordgraphen tatsächlich bis Tiefe 3
lokale Minima, und liegt eine strikt (W,L1)-bessere Konfiguration in Abstand 4?
Das ist eine lokale mathematische Frage, kein Vergleich der Qualität von Banken.

| Bestandteil | Vorabfestlegung |
| --- | --- |
| Arm A | Einzelstart W2076, state `8169eba8e1f2bf78eb655d99b94844a1eb5056df828e8c610a3778d537a7d0fe` |
| Arm B | Einzelstart W2077/L1=2436, state `136bad89e063ba84bbc4201cfa5be21db6d511852602ad861a4d2c0e0ef8e49c` |
| Startpopulationen | Genau ein fixierter Graph je Arm; keine 16er-Bank, keine Neugründer |
| Kontrolle | Bekannte Vier-Zug-Verbindung W2079→W2076 als positiver Erreichbarkeitsfall; bekannte negative Tiefe-2-Fälle; Zeugen mit unabhängiger Vollbewertung prüfen |
| Operator | Unveränderter vollständiger Apex/Pivot-Katalog aus a4d4396; kein cycle3, kein Crossover, keine Migration |
| Zielfunktion | Strikte lexikographische Verbesserung von (W,L1) relativ zum jeweiligen Start; F, Linf, Nmax und Klassen zusätzlich erfassen |
| Suchraum | Alle beschrifteten Zustände bis Tiefe 4; keine ungeprüfte Isomorphie-Pruning-Regel, keine fitnessabhängige Auslassung |
| Hilfsbudget | Höchstens 2 CPU-h insgesamt: vollständige Tiefe-3-Reproduktion, Kontrollen und kurze Durchsatz-/Speichermessung |
| Tiefe-4-Budget | Höchstens 20 CPU-h pro Arm, insgesamt 40 CPU-h; keine Übertragung zwischen Armen oder automatische Verlängerung |
| Parallelität | Höchstens 12 Prozesse insgesamt, Arbeit innerhalb jedes Arms aufteilen; nur auf verfügbaren Ryzen-Ressourcen |
| Speicher/Disk | Geplanter Gesamtrahmen 8 GiB Audit-RAM und 10 GiB Ausgabedaten; kontrollierte Pause bei Überschreitung oder <6 GiB verfügbarem RAM bzw. <25 GiB freier Disk |
| Zeit | Planung etwa 4–6 h Walltime bei 12 freien physischen Kernen; harte zusätzliche Grenze 8 Host-Stunden; nach Kalibrierung keine unrealistische Vollständigkeit versprechen |
| Status | Alle zehn Minuten: abgeschlossene/gesamte Arbeitseinheiten, CPU-Verbrauch, RSS, Host-Walltime, vorsichtige ETA |

Die Reviewerangabe „40 CPU-h in 1–2 Stunden“ setzt nahezu perfekte Verteilung
auf 20–40 CPU-Äquivalente voraus. 24 logische Threads sind keine 24 gleich schnellen
physischen Kerne. Bei 12 Workern sind bereits 40/12=3,33 Stunden die ideale Untergrenze
für den vollständigen Verbrauch des Tiefe-4-Budgets, ohne Hilfsarbeit und Overhead.
Ohne gemessene Tiefe-3-Zustandszahl und Durchsatz ist auch die CPU-Schätzung vorläufig.
Die Aufteilung in Arbeitseinheiten muss echte interne Parallelisierung ermöglichen;
nur zwei ungeteilte Python-Jobs würden das Walltime-Ziel nicht erreichen.

**Erfolg und Beendigung, vorab getrennt:**

- Ein unabhängiger, replay-geprüfter Pfad mit strikt besserem (W,L1) beantwortet
  die Existenzfrage für diesen Arm positiv. Dieser Arm darf beim ersten Zeugen
  enden; damit wird keine vollständige Zählung aller Verbesserungen behauptet.
  Ein eventueller anschließender lokaler Abstieg ist in diesem Vorschlag nicht enthalten.
- W<2076 ist separat ein globaler W-Rekord; gleiches W mit kleinerem L1 oder
  W2077→2076 ohne Unterschreitung ist kein neuer globaler W-Rekord.
- Ein negatives Resultat heißt nur bei vollständiger, geprüft disjunkter
  Abdeckung `COMPLETE_NO_IMPROVEMENT_DEPTH4`. Bei Budget-/Speichergrenze heißt es
  `INCOMPLETE`, mit erhaltenen Checkpoints und genauer Abdeckung.
- Widersprüche in Katalog, Score, λ-Gültigkeit oder Abdeckung stoppen die eigenen
  Prüfprozesse. Auch Kontrollfehler oder unzureichendes Hilfsbudget verhindern
  den Start der Tiefe-4-Arme. Bestehende andere Prozesse bleiben unberührt.
- Danach Bericht und Pause des unveränderten P-Zweigs, bis eine neue begründete
  Entscheidung vorliegt. Keine automatische Rekordkampagne, kein endgültiger
  Ausschluss größerer Radien oder anderer Operatoren.

E3 (erneute 8×4-h-Zufallssuche mit zugleich geänderter Bankauswahl) wird jetzt
nicht empfohlen: Sie beantwortet weder den lokalen Radius noch den kausalen
Nutzen der Vielfalt sauber. Falls später genau Vielfalt untersucht werden soll,
braucht es gleiche Gründerpools, gleiche Budgets und gepaarte Replikate einer
unveränderten und einer diversifizierten Auswahl. Ein F-Arm oder Crossover wäre
jeweils eine weitere, gesondert zu begründende Methodenänderung.

## 5. Prüfartefakte und Grenzen

Im Unterverzeichnis `audit/`: Paketprüfbericht, reproduzierte Revieweranalyse,
Tiefe-2-/MITM-Ergebnisse, eigene vollständige Klassenprüfung, Paretofront,
Residuenhistogramme, Symmetriebefund und Quellhashes. `REPRODUKTION.md` beschreibt
den Ablauf. Keine großen Roharchive erneut angefordert. Kein neuer Suchlauf
programmiert oder gestartet. Die kleine strukturelle Auswertung ist nun erfolgt;
die volle Tiefe-3-Reproduktion und Tiefe 4 bleiben ausdrücklich Vorschläge.
