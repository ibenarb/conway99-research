# ROOT8105 — Filterpilot abgeschlossen, 06.10.2026

**Ergebnis: In der vorab festgelegten Stichprobe verwerfen LD, CAP und LD+CAP
keinen der 4608 Zustände. Das ist kein allgemeiner Unwirksamkeitsnachweis.**
Die Auswahl lässt gerade eine für LD wesentliche Beziehungsklasse aus.
Ein separat konstruierter Zustand aus dieser Klasse wird von LD und CAP
korrekt verworfen. Der nächste Versuch sollte zuerst diese Auswahllücke schließen.

## Vollständiger, neuer Pilot

24 Roots, 72 Zielpaare und 4608 Ränge byteidentisch aus dem fertigen Audit
übernommen, Manifest SHA256 1411d0048ef189289d2f2388f6463052ea55ae2192dd5bc45468b303b1fa9d68.
Alle 72 Sampler aufgebaut, 72 Gesamtsummen stimmen mit ihren gespeicherten
Censuswerten überein; alle ausgewählten Ränge unranked, alle vier Varianten
an identischen Zuständen geprüft. Keine neue Vollzählung und keine Wiederholung
der 13455 fertigen Audit-Nachzählungen. Der Sampleraufbau benötigt seine
Rekursionsgewichte und ist separat gemessene neue Pilotarbeit.

Laufkennung: 92abc49a4139400d8a0a7780174a2fab.
Codehash: 8f1c9df83acf90c34577b78ef837f94026e1fd5f5cb1ae6a61ce0f9bf6ad5561.
Ausführung: hiesige Linux-/Cloudumgebung, vier Worker; **kein Ryzenlauf**.
Kalibrierung: drei Roots/9 Sampler/576 Zustände; anschließend übrige Aufgaben.
Alle drei Kalibrierungsreceipts, Ergebnisdigests und Versuchs-IDs wurden im
Folgelauf unverändert übernommen. 24 Samplejobs plus ein Kontrollauswahljob
sind abgeschlossen; ID0 bezeichnet diesen Kontrolljob, keinen zusätzlichen Root.

| Variante | Ausschlüsse | CPU-Sekunden für Filteraufrufe |
|---|---:|---:|
| F | 0 / 4608 | 0.182219 |
| F+LD | 0 / 4608 | 0.295190 |
| F+CAP | 0 / 4608 | 32.208226 |
| F+LD+CAP | 0 / 4608 | 33.150840 |

Jede der neun Schichten (drei Roottypen × drei Zielpositionen) umfasst 512
Zustände und zeigt ebenfalls null Ausschlüsse. Die Variantenaufrufe enthalten
jeweils die F-Grundprüfung; die Zahlen sind keine rein inkrementellen Filterkosten.
Sampleraufbau: 8.540871 CPU s;
Unranking: 0.500245 CPU s.
Maximales Worker-RSS: 54575104 Bytes
(52.05 MiB).

Worker-Endabrechnung: 77.041590 CPU s.
Supervisor: 2.490610 CPU s.
Initialisierung/Preflight/Exporte: 129.221583 CPU s,
darin Preflight 127.263793 CPU s.
Gesamt nach letztem Export: **208.753783 CPU s**.
Filter-/Samplerzeiten sind darin enthalten, nicht nochmals hinzuzurechnen.
Die beiden Rechensitzungen dauerten zusammen 35.241626
UTC-Sekunden; Preflight und Pause zwischen den Sitzungen gehören nicht zu dieser
Walltime. Keine Ryzen-Hochrechnung. Alle Sitzungen/Versuche geschlossen,
keine CPU-Untergrenzenmarkierung, keine offenen Budgetanfragen.

## Warum die Stichprobe LD nicht testen konnte

Für zwei gebaute Zeilen a,b sei e ihre Adjazenz und s die Größe des Schnitts
ihrer Zweierlabels. F verlangt genau 2−e−s gemeinsame H-Nachbarn.

| (e,s) | Vorhandene Ziele bei den 24 Roots | Ausgewählte Zielpaare |
|---|---:|---:|
| (0,0) | 1224 | 48 |
| (0,1) | 480 | 0 |
| (1,0) | 240 | 0 |
| (1,1) | 48 | 24 |

**Lemma für LD bei zwei gebauten Zeilen:** Eine durch LD verbotene, bereits
feststehende Kante zwischen Nachbarn einer gebauten Zeile muss die andere
gebaute Zeile berühren. Ihre Verletzung verlangt somit ein H-Dreieck a,b,w.
Für e=0 gibt es kein solches Dreieck. Für (e,s)=(1,1) erzwingt F
2−1−1=0 gemeinsame H-Nachbarn; ebenfalls kein solches Dreieck.
LD kann deshalb in den beiden ausgewählten Klassen bei F-gültigen Zuständen
überhaupt nicht ablehnen. Der Nullbefund für LD ist hier strukturell erklärt,
nicht bloß statistisch. Für CAP folgt aus diesem Lemma noch keine Redundanz.

Die ursprüngliche Auswahl nach Minimum/Median/Maximum der Breite war als
Kostenstichprobe brauchbar, als LD-Wirkungsprüfung aber unzureichend.
Dieser Planungsmangel wird nicht durch nachträgliches Ersetzen von Zuständen
verdeckt. Das Originalergebnis bleibt unverändert dokumentiert.

## Separater Gegencheck der fehlenden Klasse

Nach dem Nullbefund: kleinste ausgewählte Root-ID, dann lexikographisch erstes
geeignetes (Ziel, gemeinsamer Nachbar); Regel vor Solveraufruf gespeichert.
Bereits der erste Versuch liefert einen historischen F-SAT-Zustand:

- Root 1, Rootzeile `0x580000050a0520020040`.
- Ziel 29 mit Label (2,10), Zeile `0xa00040600442100080011`.
- Gemeinsamer H-Nachbar 32 mit Label (2,13).
- LD verweigert die feststehende Kante (29,32).
- CAP allein verweigert Zeile 32, Gleichung pair:29: mindestens 1 gemeinsame
  H-Nachbarschaft bei gefordertem Wert 0.

Direkter Grund: 29 und 32 sind benachbart und teilen sowohl H-Knoten0 als auch
Randknoten2 als Nachbarn. Das widerspricht lambda=1. Damit liegt ein tatsächlich
F-gültiger, aber nicht zu einem SRG fortsetzbarer Zustand vor.
Die unabhängig aufgebauten LD- und CAP-CNFs liefern beide
UNSAT_UNCERTIFIED; der elementare Widerspruch ist zusätzlich oben angegeben.
Der Zustand gehört **nicht** zu den 4608 vorab gezogenen Zuständen und wird
nicht nachträglich in deren Quoten eingerechnet. Diagnosearbeit separat:
ursprünglicher Diagnoseprozess 1.156224 CPU s;
CAP-Nachkontrolle im separaten Prozess gemessene Encoder-/Solverteile
0.009833 CPU s.
Diese Nachkontrolle hat keine vollständige Prozessendkonto-Messung und wird
nicht in das abgeschlossene Pilotkonto hineingerechnet.

## Kontrollen und Betrieb

Vollständige BVLS-Matrixprüfung; zwölf modellgerechte Präfixe bestehen LD/CAP;
zwölf SAT-Belegungsprüfungen (drei Tiefen, vier Varianten); zwei absichtliche
Prädikat-Negative. In der festen Stichprobe gibt es **keine** echten Ablehnungen;
folglich war die geplante deterministische SAT-Negativauswahl leer. Der rohe
Kontrolljob meldet PASS mit checks=[], was ausdrücklich keinen ausgeführten
Negativtest bezeichnet. Der separate Gegencheck oben schließt diese konkrete
Testlücke, ersetzt aber keinen Wirkungsquotenversuch in der fehlenden Klasse.

Betriebsregressionen bestanden: 21 Prozess-/Budget-/Uhrenfälle, sieben
Recovery-Prüfungen und neue Spiegel-/Anker-/Auswahltests. Dateispiegel nach
Antwort, COMPLETE, USER_BUDGET_ZERO und Neustart geprüft. Anker, Deltas,
Toleranz, Frische, konkrete Uhrenfehler gespeichert. Mathematische rc3-Quellen
byteidentisch; neue Steuerung separat. Windows-/WSL-Lasttest bleibt auf echter
Zielhardware offen. Kein laufender C2-Prozess verändert.

## Nächster Schritt, vorbereitet und noch nicht ausgeführt

Kein erneuter Lauf der fertigen 4608 Zustände und vorerst keine große Tiefenkampagne.
Zuerst nach Beziehungsklassen geschichteten Zusatzpilot durchführen: dieselben 24 Roots;
je ein zufällig gewähltes Ziel aus den fehlenden Klassen (0,1) und (1,0);
je 64 gleichverteilte Ränge ohne Zurücklegen. **48 zusätzliche Zielpaare,
3072 neue Zustände.** Seed 810520261008; Manifest
`supplement_manifest_PROPOSED.json`, SHA256
946fa4f19370e5df2871bfe11a78b4afc5de95f601e5345b8f6394b7fafb8ae0.
Alle Breiten stammen aus dem vorhandenen Census, keine neue Zählung für die
Auswahl. Das ist ein ausdrücklich nach dem ersten Pilot entworfener Folgetest,
keine Erweiterung der ursprünglichen Vorabregistrierung. Die Umsetzung als
neuer Lauf ist noch ausstehend.

Die Ergebnisse je Beziehungsklasse getrennt ausweisen. Erst danach beurteilen,
wo LD billig sinnvoll ist, ob LD-verengte CAP zusätzliche Zustände beseitigt
und wie ein Tiefe-2/3-Versuch dimensioniert werden sollte.

Regelbasis: 40c0050af19353fd9c9d1a203e58f5df07636229,
GC-01/02/08/10/11/15/16/18/19/20/21. Git-Push wurde durch automatische
Freigabeprüfung zurückgewiesen (Payload/Ziel als nicht ausreichend autorisiert
bewertet). Lokale Commits und vollständige Dateien werden bereitgestellt;
keine Veröffentlichung behauptet.
