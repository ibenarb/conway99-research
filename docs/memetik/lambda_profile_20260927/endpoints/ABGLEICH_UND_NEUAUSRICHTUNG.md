# λ-Memetik: Reviewabgleich und strategische Entscheidung

27.09.2026. Eigene Bewertung, getrennt vom unveränderten Reviewertext.

Nachtrag: Nach Zustimmung des Nutzers und seinem Wunsch nach mehr
Startklassen und Ryzen-Ressourcen ersetzt
[Pilotplan V2](../../lambda_repair_pilot_20260927/PLAN_V2.md)
den unten dokumentierten Drei-CPU-Stunden-Vorschlag. Der ursprüngliche
Reviewabgleich bleibt nachvollziehbar erhalten.

## Entscheidung

**Die unveränderte Apex/Pivot-P-Linie pausieren. Den nächsten Versuch nicht
als weitere Landschaftsvermessung, sondern als begrenzte exakte gemeinsame
Reparatur mehrerer Kanten planen.** Kein großer Hauptlauf, keine automatische
Verlängerung. Der nachstehende Pilot ist ein Vorschlag, noch keine
Implementierung oder Startfreigabe.

Ich nehme meine vorherige Empfehlung zurück, den bloßen Strukturvergleich
von drei Minima zum nächsten Hauptschritt zu machen. Ein solcher Vergleich
kann eine präzise Reparaturaufgabe vorbereiten, rechtfertigt allein aber
weder neue Suchzeit noch eine neue Zielfunktion.

## Eingang und eigene Reproduktion

[Unverändertes Reviewarchiv](https://github.com/ibenarb/conway99-research/tree/79caad6434d3bdcca39d3ff7a17d653cdd55bf70/docs/reviews/20260927_lambda_profile),
Zweig `reviews/20260927-lambda-profile`.
Eingangsdatei `Pasted markdown(20260927-131016).md`, 12284 Bytes,
SHA256 `649d2744d36bc71ae8060afd536f91064cd7f75e83f6c11b59924f2719e1781a`.
Das darin angekündigte ZIP mit SHA256 `5f01eb2e…` wurde nicht mitgeliefert;
es wird weder als gelesen noch als archiviert ausgegeben.

Die Ergebnisse wurden stattdessen aus dem bereits vorliegenden vollständigen
Endarchiv eigenständig reproduziert. `reproduce.py` verwendet einen eigenen
graph6-Decoder und Bitmengen-Scorer ausschließlich aus der Python-Standardbibliothek.
Alle 885 verschiedenen nicht zurückgekehrten Endgraphen sowie die beiden
Starts stimmen in W/L1/F/Linf/Nmax und λ-Bedingungen. Die Klassenzuordnung
stammt aus dem vorher unabhängig mit pynauty nachgerechneten Endaudit;
der neue Standardbibliothek-Scorer behauptet keine eigene Kanonisierung.
Die komplette Tabelle steht in `REPRODUCED.json`.

Bestätigt sind die berichteten Mediane, Quartile bis Rundung, beschrifteten
Kantenaustauschzahlen und sechs beobachteten Nahklassen. Quartile verwenden
lineare Interpolation bei Index (N−1)p. Der höchste Anteil nicht
zurückgekehrter Episoden mit ΔW≤5 bei k≥8 ist 5/53=9,43 % in A/k12,
aus einer Klasse. Keine Zelle erreicht zehn solche Klassen.
Die zusätzliche Reviewerregel ist daher eindeutig verfehlt.
Der W2079/L1=2484-Nahpunkt ist der bereits gespeicherte beschriftete Vorfahr.

## Wo der Reviewer über die Daten hinausgeht

1. **Vorabregeln auseinanderhalten.** Unser freigegebener Plan forderte für
   das vollständige negative Profil eine vollständige Stichprobe; für
   unvollständige Zellen ausdrücklich kein globales negatives Urteil. Eine
   numerische Fünf-Minima-Regel stand in diesem freigegebenen Plan nicht.
   Die neue 10-%/zehn-Klassen-Regel wurde im Review vor seiner zusätzlichen
   Endpunktauswertung formuliert, aber nach Kenntnis des bisherigen
   Profilbefunds. Sie ist eine zusätzliche explorative Ressourcenregel,
   keine ursprüngliche konfirmatorische Erfolgsgrenze. Pausieren bleibt
   auch ohne diese Umdeutung sachlich vernünftig.
2. **315 fehlende Episoden sind nicht automatisch belanglos.** Ihre Ergebnisse
   sind unbekannt. Für A/k32 reichen mögliche volle Rückkehrquoten rein
   rechnerisch von 11/300=3,67 % bis 117/300=39,0 %, für B/k32 von 5,67 %
   bis 40,33 %. Diese Extrembereiche sind keine Prognose, zeigen aber die
   logische Lücke. Fehlende Versuche könnten einen seltenen Treffer enthalten.
   Das verpflichtet nicht zur Budgeterhöhung.
3. **Sechs beobachtete Klassen sind keine obere Schranke der Landschaft.**
   „Höchstens fünf Dellen um A“ gilt nur für die beobachteten Klassen bis
   ΔW≤10, nicht für alle erreichbaren Minima. Häufigkeiten nach zufälligem
   Kick und deterministischem Abstieg sind kein Zensus.
4. **Endpunktnähe beweist weder Trichter noch kleine Barrieren.** Auch eine
   erfüllte 10-%/zehn-Klassen-Regel hätte diese Geometrie nicht bewiesen.
   Nur für den konkreten Zweizugpfad zum neuen W2077/L1=2488-Minimum ist
   eine W-Erhöhung um höchstens drei ab A nachgewiesen. Metropolis,
   Tabu oder andere Akzeptanzen sind nicht logisch ausgeschlossen; es
   fehlt derzeit ein positiver Grund, ihnen weitere Laufzeit zu geben.
5. **Langer Kick ist kein geprüfter Neustart.** Bei k32 sind gegenüber dem
   Start im Median 47 bzw. 48 von 693 Kanten ersetzt. Das ist ein
   beschrifteter Abstand, nicht ein über Isomorphismen minimierter Abstand
   und kein Nachweis einer unabhängigen Gründerverteilung. Die adaptive
   O-Populationskampagne hatte eine andere Verteilung als dieser feste
   Root-Episodenversuch. Ihr Ertrag lässt sich nicht gleichsetzen.
6. **Kleine Zählpräzisierung.** Die Nahklasse A→2077/2488 wurde insgesamt
   17-mal beobachtet: einmal bei k2 und 16-mal bei k12–32. Bei A/k32 sind
   183 nicht zurückgekehrte Episoden 182 Klassen, bei B/k32 179 Episoden
   179 Klassen; die zusätzlichen jeweiligen Startklassen gehören nicht dazu.
7. **Theoriepriorität muss eigenständig begründet sein.** Aus P-Stagnation
   folgt kein Vorteil gerade von Genus-/Topologieansätzen. Für jeden
   solchen Ansatz wäre zunächst zu zeigen, dass seine Voraussetzungen
   für jeden Ziel-SRG gelten. Eine zusätzliche polyedrische Realisierbarkeit
   darf nicht stillschweigend vorausgesetzt werden. In diesem Auftrag
   werden keine anderen laufenden Projektzweige umgesteuert.

Die Pause der unveränderten P-Linie ist eine begründete Ressourcenentscheidung,
kein mathematischer Ausschluss der λ-Zustände oder aller heuristischen Verfahren.
Auch ein beliebiger neuer 3-/4-Switch allein wäre noch keine Wiederaufnahme-
begründung: Ein größerer Katalog muss einen messbaren Nutzen liefern; cycle3
hat bereits gezeigt, dass zusätzliche Fluchten allein nicht genügen.

## Wo wir tatsächlich stehen

Wir haben eine funktionierende, nachvollziehbare Such- und Prüfstrecke und
sehr stabile lokale Minima gefunden. W=2076 ist unser überprüfter λ-Rekord.
Das ist **eine bessere Erfüllung der Gleichungen**, aber kein kalibrierter
Abstand zu einem möglicherweise existierenden Zielgraphen. Die jüngste
Verbesserung 2081→2076 ist nicht die gesamte bisherige λ-Entwicklung.
Ein weiterer kleiner Rekord wäre ein lokaler Fortschritt, kein belegter
Beginn einer Konvergenz zu null.

Der Zielgraph muss gleichzeitig erfüllen:

    A = Aᵀ, Aii = 0, Aij ∈ {0,1}, A·1 = 14·1,
    A² + A = 12 I + 2 J.

Unsere λ-Kandidaten erfüllen bereits die Grad- und Kantenbedingungen.
Übrig sind die 4158 Nichtkantenbedingungen. Beim Rekord sind 2076 davon
falsch, also 49,92785 %. Jeder seiner 99 Knoten berührt 32 bis 52 falsche
Paare, Median 42; beim alternativen W2077-Start sind es 29 bis 56,
Median ebenfalls 42. Das ist keine kleine lokalisierte Restfehlerzone.
Die numerische Verteilung ist reproduziert, kein Beweis gegen lokale Reparatur.

Außerdem gilt bei Grad14 bereits Σ_{u<v} r_uv=0:
99·C(14,2)+693−2·C(99,2)=0. Fehlerüberschuss und Fehlerdefizit gleichen
sich global aus; eine lokale Verbesserung kann Fehler verschieben.
Bei A beträgt jede der beiden Residuenmassen 1244 (L1/2).
Daraus folgt nicht, dass eine lokale Reparatur unmöglich ist, wohl aber,
dass ihre gesamte Wirkung geprüft werden muss.

λ=1 organisiert sämtliche 693 Kanten in 231 eindeutige Dreiecke, sieben
an jedem Knoten. Jede exakte Lösung liegt im λ-Raum. **Nicht bewiesen ist,
dass unsere P-Züge jede relevante Region dieses Raums erreichen.** Die
mögliche Einschränkung liegt also im Zugkatalog und in der Suchdynamik,
nicht darin, dass λ=1 als Endbedingung zu streng wäre.

Die Befunde erklären einen Mechanismus der Stagnation: kurze Kicks kehren
fast immer zurück; lange Kicks erzeugen starke Verschlechterung (bei k32
ΔW der Störungsendpunkte im Median 411,5 für beide Starts), und der
Steilstabstieg beseitigt diese nur teilweise. Der Median der nicht
zurückgekehrten Endpunkte bleibt bei +154/+159. Größere Entfernung vom
Start und niedrigere Rückkehrrate sind daher keine geeigneten Erfolgsmaße.

## Welche Richtungen verdienen Priorität?

- **Weitere P-Laufzeit, Radius5, bloße Längen-/Populationsvergrößerung:**
  derzeit geringe Priorität; kein neuer mechanismischer Ansatz und kein
  überzeugender Nutzen aus den jüngsten Daten.
- **Wechsel zu F oder einer Mischkennzahl:** nur als neue Hypothese, nicht
  als vermeintlich besserer Lösungsabstand. W bleibt das direkte Zielmaß;
  F, L1 und Spektren liefern Diagnose, keine Fortschrittsgarantie.
- **Gezielte gemeinsame Änderung mehrerer Kanten:** plausibelster begrenzter
  nächster konstruktiver Test. Ein Solver kann zusammenhängende Änderungen
  wählen, deren einzelne Teilzüge unzulässig oder schlecht wären. Ob das
  hier hilft, ist offen und soll gerade gemessen werden.
- **Exakte globale Konstruktion beziehungsweise neue notwendige Bedingungen:**
  langfristig wesentlich. Dafür zählt eine gültige Konstruktion oder ein
  sauber begrenzter Ausschluss. Große unstrukturierte SAT-Modelle und
  zusätzliche geometrische Annahmen sind nicht schon durch ihre Form
  erfolgversprechender als lokale Suche.

Die Idee exakter Fensterreparatur ist nicht neu: Sie steht bereits in
`docs/memetic/reference/Conway99_Pong_Runde3_20260910.md`, Abschnitt3,
und wurde später gegenüber P zurückgestellt. Jetzt haben wir einen
konkreteren Grund, ihre Priorität zu erhöhen. SAT-gestützte lokale
Verbesserung wird auch in anderen kombinatorischen Problemen eingesetzt
(z.B. Schidler, SoCG2022, DOI 10.4230/LIPIcs.SoCG.2022.74). Das belegt das
Methodenprinzip, nicht dessen Erfolg für Conway99.

## Nächster Schritt: ein Reparaturpilot mit höchstens 3 CPU-Stunden

**Frage:** Kann eine exakte, gemeinsame Neuverdrahtung eines festen
Knotenfensters einen global besseren λ-Graphen erzeugen, den der bisherige
P-Steilstabstieg nicht findet? Primäres Ergebnis ist W<2076, nicht Vielfalt,
Flucht oder ein bloßer Wechsel des lokalen Minimums.

**Starts:** die beiden unveränderten Originalgraphen A=(2076,2488) und
B=(2077,2436). Keine Population, kein Crossover, keine adaptive Gründerwahl.
Der nahe Graph N=(2077,2488) dient ausschließlich als positive Kontrolle,
weil sein Zweizug-Rückweg zu A bekannt ist.

**Fenster:** 18 oder 24 Knoten, je Start und Größe zwei Verfahren mit je
zwei festen Wiederholungen; insgesamt 16 Aufgaben. Ein Verfahren beginnt
bei Knoten mit hoher Zahl inzidenter Fehlerpaare und wächst entlang
vorhandener Kanten; die Vergleichsfenster wachsen zufällig entlang
vorhandener Kanten. Beide bleiben zusammenhängend und gleich groß.
Vor dem Suchbeginn werden alle konkreten Knotenlisten aus einem festen
Seedmanifest erzeugt, dedupliziert, geprüft und veröffentlicht. Kein
Fenster wird nach seinen Solverergebnissen ausgewählt oder ausgetauscht.
Die genauen Tie-Breaks und Seeds gehören vor Ausführung in dieses Manifest;
der vorliegende Text ist noch kein ausführbares Versuchsmanifest.

**Reparaturmodell:** Nur Kanten mit beiden Endpunkten im Fenster dürfen sich
ändern. Alle anderen Kanten bleiben fest. Grad14 und λ=1 sind für den
vollständigen Endgraphen harte Bedingungen. Ziel ist lexikographisch
(W,L1), primär globales W. Das lässt sich z.B. als `50000·W+L1` kodieren,
da unter den harten Bedingungen L1≤12·4158=49896 gilt.
Auch alle gemeinsamen Nachbarzahlen für Fenster-Außen-Paare gehen in die
Nebenbedingungen und Zielfunktion ein; nur reine Außen-Außen-Paare bleiben
unverändert. Eine reine Bewertung interner Paare wäre falsch.
Es wird keine Folge zulässiger AP-Einzelzüge verlangt. Zulässigkeit wird
am vollständig reparierten Endgraphen unabhängig geprüft.

**Kontrollen vor Suchfreigabe:** unveränderter Start ist zulässige Belegung;
kleine Modelle stimmen mit vollständiger Enumeration überein; die bekannte
Rückreparatur N→A funktioniert bei einem Fenster, das den Träger der beiden
Züge enthält. Unabhängige Endprüfung sämtlicher globalen λ-/Grad-/Scorewerte.
Fehlschlag einer Kontrolle beendet die Vorbereitung ohne produktive Aufgaben.

**Budget:** 600 CPU-Sekunden je Aufgabe, insgesamt 9600 s=2 h40;
höchstens weitere1200 s=20 min für Kontrollen, Modellbau und Verifikation.
Maximal3 CPU-h insgesamt, keine Übertragung auf neue Aufgaben. Ryzen mit
höchstens12 freien Workern; zunächst Modellgrößen/RAM prüfen, höchstens
24 GiB Gruppen-RAM, Pause bei weniger als6 GiB freiem RAM. Geplante Walltime
unter einer Stunde bei freier Maschine, harte aktive Hostgrenze2h.
Windows-Host-Monotonzeit und wait4-Abrechnung, Status alle10min mit ETA.
Noch keine Solverinstallation und keine Änderung der bestehenden Umgebung.

**Erfolg und Entscheidungen:**

1. W<2076 mit unabhängig geprüftem Graphen: ein Mechanismusnachweis und
   neuer Rekord, noch kein Nachweis langfristiger Konvergenz. Erst danach
   eigener Bestätigungsplan mit neuen festen Fenstern und gleichem CPU-Budget
   für geeignete Vergleichsarme.
2. Nur lokaler Fortschritt bei B oder besseres L1 bei gleichem W: separat
   berichten; rechtfertigt nicht automatisch den Hauptlauf.
3. Kein globaler Treffer nach allen16 Aufgaben: konstruktive λ-Suche
   vorerst ruhen lassen; keine automatische Vergrößerung der Fenster,
   keine weitere Folge kleiner heuristischer Modifikationen.
4. Solverzeitende heißt UNKNOWN. Nur ein tatsächlich abgeschlossener
   exakter Ausschluss, bei SAT mit geprüftem Zertifikat, darf als
   Nichtverbesserbarkeit **dieses Fensters** gelten. Keine globale
   Nichtexistenzaussage und keine Gleichsetzung von Timeout mit UNSAT.

Dieser Pilot garantiert keinen Weg zu W=0. Er prüft mit engem Budget eine
wesentlich andere Art, die verbleibenden Gleichungen gemeinsam zu erfüllen.
Eine Garantie gibt es derzeit weder für diese Methode noch für die Existenz
des Zielgraphen. Das ist der Grund für die harte Entscheidungsgrenze.
