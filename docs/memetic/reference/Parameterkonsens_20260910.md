**Ich würde mit insgesamt 64 Kandidaten und acht Nachfahrenversuchen je Elter und Generation starten.** Diese Zahlen sind begründete Versuchswerte; ein Optimum kennen wir noch nicht. Die erste Konfiguration soll verschiedene Bewegungsgrößen ausreichend oft ausprobieren und Deine gewünschte Vielfalt erhalten.

Dabei unterscheiden wir drei Größen: **Populationsgröße**, **Anzahl der Nachfahrenversuche** und **Anzahl beziehungsweise Größe der Tausche innerhalb eines Versuchs**.

**Startpopulation: 64 Kandidaten, verteilt auf die beiden Suchräume**

| ParameterStartwertBegründung                  |                                           |                                                           |
| --------------------------------------------- | ----------------------------------------- | --------------------------------------------------------- |
| H84/Ω-Population                              | 32                                        | Strenger Rahmenansatz                                     |
| Wurzelfreie λ-Population                      | 32                                        | Vergleich mit anderen zulässigen Bewegungen               |
| Gleichzeitige Suchprozesse                    | 4, zunächst zwei je Arm                   | Passend zu Deinem Vierkerner                              |
| Herkunftsgruppen je Population                | Ziel: vier Gruppen mit je acht Kandidaten | Schutz verschiedener Konstruktionsansätze                 |
| HoG und seine unmittelbare Abstammungsfamilie | Höchstens vier Plätze insgesamt           | Als Kontrolle erhalten, ohne die Population zu dominieren |

Vier Kerne begrenzen die gleichzeitige Bearbeitung, kaum die speicherbare Population. 64 Adjazenzmatrizen benötigen bei einem Byte pro Eintrag zusammen nur rund 0,6 MB; zusätzliche Suchdaten kommen natürlich hinzu.

Als Herkunftsgruppen würde ich anstreben:

- **Randomisierte exakte Konstruktion:** harte Bedingungen lösen, mit wechselnden Zufallsentscheidungen und Hilfszielfunktionen.
- **Randomisierte Konstruktion mit Reparatur:** zunächst anders erzeugte Kandidaten anschließend vollständig zulässig machen.
- **Algebraische beziehungsweise symmetrische Konstruktionen:** mehrere Vorlagen, danach gegebenenfalls Symmetrie durch zulässige Bewegungen brechen.
- **Vorhandene Projektzustände und längere zulässige Ausflüge daraus.**

Das sind unterschiedliche Erzeugungswege, deren tatsächliche Ausbeute wir erst feststellen müssen. **Die 64 sind eine Zielgröße, kein bereits verfügbarer Bestand.** Fehlende Kandidaten werden nicht durch Umnummerierungen aufgefüllt.

Wenn genügend Starts verfügbar sind, würde ich innerhalb jeder Herkunftsgruppe vier Plätze nach Fehlerwert und vier nach struktureller Verschiedenheit besetzen. Alle müssen die harten Bedingungen erfüllen; etwas schlechtere, aber deutlich andere Starts bekommen ausdrücklich eine Chance.

**Nachfahren: acht Versuche je Elter**

Meine erste Aufteilung wäre:

| VersuchstypAnzahl je Elter                              |   |
| ------------------------------------------------------- | - |
| Kurze zufällige Störung plus Abstieg                    | 3 |
| Mittlere zufällige Störung plus Abstieg                 | 2 |
| Lange zufällige Störung plus Abstieg                    | 1 |
| Durch einen zweiten Elter gelenkte Störung plus Abstieg | 1 |
| Direkter Crossover-Versuch plus Abstieg                 | 1 |

Im λ-Arm würde der letzte Platz zunächst ebenfalls eine elterngerichtete Störung verwenden. Dort genügt die unten beschriebene lineare Crossover-Bedingung allein nicht, um λ zu erhalten.

Das ergibt **256 Versuche je Population, insgesamt 512 pro Generation**. Es entstehen höchstens 512 übernahmefähige Kinder; erfolglose Versuche sind keine Kinder.

Jeder Elter erhält zunächst sein vollständiges Versuchskontingent. Danach ersetzt ihn sein bester geeigneter Nachfahre:

- niedrigeres `F`: übernehmen, sofern kein Populationsduplikat;
- gleiches `F`: nur eine neue Struktur übernehmen, bei mehreren bevorzugt die mit größerem Abstand zur übrigen Population;
- kein geeigneter Nachfahre: Elter behalten.

So bleiben zunächst alle 64 Linien beziehungsweise ihre Nachfolger vertreten. Die globale Auswahl der besten 64 aus sämtlichen Kindern würde ich wegen ihrer verdrängenden Wirkung auf Startfamilien vermeiden.

**Länge und Größe der Transformationen**

Für die sechs rein zufälligen Störversuche würde ich die Anzahl `L` der **nacheinander ausgeführten zulässigen Tausche** so verteilen:

| KategorieVersuche je ElterVerteilung von `L` |   |                          |
| -------------------------------------------- | - | ------------------------ |
| Kurz                                         | 3 | Gleichverteilt auf 2–4   |
| Mittel                                       | 2 | Gleichverteilt auf 5–12  |
| Lang                                         | 1 | Gleichverteilt auf 13–32 |

Der Mittelwert beträgt damit etwa **8,08 Tausche je Störversuch**. Über die gesamte Population sind das im Erwartungswert 3104 Störzüge pro Generation, zuzüglich Abstieg und elterngerichteter Versuche.

Warum diese Mischung? Kurze Störungen erhalten viel vorhandene Struktur. Mittlere und lange Störungen untersuchen, ob wir andere Suchgebiete erreichen. Die kurzen Versuche beginnen bei zwei, weil anschließend noch der Abstieg folgt: Unser HoG-Befund betrifft die **gesamte Weglänge**, nicht allein die Länge der Störphase.

Die Größe eines einzelnen Tauschs würde ich gesondert gewichten:

| Suchraum und TauschBeteiligte KnotenEntfernte / ergänzte KantenStartgewicht |    |         |      |
| --------------------------------------------------------------------------- | -- | ------- | ---- |
| Ω: Produkt `4\times4`                                                       | 8  | 8 / 8   | 70 % |
| Ω: Produkt `4\times6`                                                       | 10 | 12 / 12 | 20 % |
| Ω: Produkt `6\times6`                                                       | 12 | 18 / 18 | 10 % |
| λ: Apex                                                                     | 6  | 4 / 4   | 90 % |
| λ: geprüfte Dreierrotation                                                  | 9  | 6 / 6   | 10 % |

Diese Gewichte gelten **unter den tatsächlich verfügbaren zulässigen Zugfamilien**. Fehlt eine Familie, werden die übrigen Gewichte entsprechend angepasst. Bei den bisher untersuchten Ω-Zuständen waren die größeren genannten Produktzüge nicht verfügbar; dort wäre die tatsächliche Verteilung zunächst entsprechend einseitig.

Eine lange Folge kann frühere Änderungen teilweise aufheben. Deshalb messen wir zusätzlich den **Nettoabstand zum Elter**; 20 Tausche bedeuten nicht automatisch eine große strukturelle Veränderung.

**Abstieg und Abbruchkriterien**

Je Nachfahrenversuch würde ich zunächst festlegen:

- höchstens **32 angenommene Abstiegszüge**;
- höchstens **256 bewertete Zugkandidaten im gesamten Versuch**;
- zusätzlich **30 CPU-Sekunden Gesamtbudget**, einschließlich Zugerzeugung beziehungsweise Crossover-Suche;
- unmittelbare Rücknahme sperren und die letzten **acht besuchten Zustände** gegen Wiederbesuch schützen;
- den besten zulässigen neuen Zwischenstand während des ganzen Versuchs sichern.

Ein ausgeschöpftes Budget beweist kein lokales Minimum. Es beendet lediglich diesen Versuch. Auch die Erzeugung eines zulässigen nächsten Zuges darf keine unbegrenzte Warteschleife werden.

Die ersten zehn Generationen würde ich mit diesen Parametern unverändert messen. Danach bekäme eine Linie bei fünf Generationen ohne strikte Verbesserung **zwei kurze, zwei mittlere und zwei lange Versuche**, wobei der lange Bereich auf **13–64** erweitert wird. Nach einer Verbesserung kehrt sie zur Anfangsverteilung zurück. Das ist eine einfache, überprüfbare Anpassung.

**Crossover: zwei Eltern nutzen, ohne Bedingungen zu verlieren**

Ich würde zwei Verfahren getrennt untersuchen.

Beim **direkten Crossover im Ω-Raum** seien `H_A,H_B` zwei Eltern im selben Rahmen und

```math
D=H_B-H_A.
```

Gesucht wird ein Kind

```math
H_C=H_A+\Delta, \qquad \Delta_{ij}\in\{0,D_{ij}\}, \qquad P\Delta=0,
```

mit symmetrischem `\Delta` und sämtlichen weiteren harten Bedingungen.

Anschaulich: Wo die Eltern übereinstimmen, bleibt das Kind unverändert. Wo sie sich unterscheiden, übernimmt es jeweils die Entscheidung eines Elternteils. **Welche Entscheidungen gemeinsam übernommen werden dürfen, bestimmen die Kopplungsbedingungen.**

Als gewünschte Übernahmeanteile vom zweiten Elter würde ich zufällig **25 %, 50 % oder 75 % der unterschiedlichen Positionen** wählen. Das sind Zielwerte, keine erzwungenen Gleichungen; die zulässigen Mischungen können andere Anteile verlangen. Beide vollständigen Eltern und ihre isomorphen Kopien werden als Crossover-Ergebnis ausgeschlossen.

Dieses Vorgehen ist an die Forschung zur beschränkten beziehungsweise optimalen Rekombination angelehnt; unser zeitbegrenzter Versuch würde zunächst zulässige Mischungen suchen und keine optimale Rekombination behaupten. [Eremeev und Kovalenko](https://arxiv.org/abs/1307.5519).

**Die Grenze ist konkret:** Ich habe gerade für unser vorhandenes Paar `H_-,H_+` alle `2^{16}=65\,536` Mischungen geprüft. Nur die beiden Eltern erfüllen die Kopplungsbedingungen. Dieses Paar besitzt keinen direkten Mischling.

Deshalb kommt als zweites Verfahren die **elterngerichtete Tauschfolge** hinzu:

- Einen zweiten, nichtisomorphen Elter aus möglichst anderer Herkunft wählen, innerhalb desselben Suchraums.
- Die Beschriftungen geeignet aufeinander ausrichten; im Ω-Arm nur mit erlaubten Rahmenumbenennungen.
- Vom ersten Elter aus **8–16 zulässige Tausche** ausführen.
- Je Schritt bis zu acht zulässige Zugmöglichkeiten betrachten. Mit **80 % Wahrscheinlichkeit** den Zug wählen, dessen Nachfolger dem zweiten Elter am nächsten liegt; mit **20 %** zufällig wählen.
- Danach lokal absteigen und den besten neuen Zustand gegen den ersten Elter vergleichen.

Dabei dürfen vorübergehend auch Kanten entstehen, die keiner der Eltern besitzt. **Es ist eine durch den zweiten Elter gelenkte Mutation.** Gerade diese zusätzliche Freiheit kann helfen, wenn die direkte Mischung blockiert ist; eine Erfolgsgarantie ergibt sich daraus nicht.

Für die erste Auswertung würde ich einen **24-Stunden-Pilot nach Starterzeugung und Kalibrierung** vorsehen, mit Statusbericht alle zehn Minuten. Entscheidend wären dann Verbesserungen je CPU-Stunde, neue gleich gute Strukturen und erhaltene Vielfalt. An diesen Messungen würde ich die Parameter ändern — insbesondere daran, welche Störlängen und welche Art der Elternkombination tatsächlich etwas beitragen.