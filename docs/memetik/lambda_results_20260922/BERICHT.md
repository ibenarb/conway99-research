# λ-Vergleich vom 21./22. September 2026: unabhängige Auswertung

**Ergebnis:** Pivot und vollständige Nachbarschaften überwinden das alte
W-Plateau robust in diesem Versuchsdesign. P ist die sinnvollste neue
Arbeitsreferenz. TC verbessert die gewählte Tabusuche gegenüber T, hat aber
keinen belegten allgemeinen Vorteil gegenüber P. Zielübergreifend gespeicherte
Rekorde liefern zusätzlichen, konkret nachprüfbaren Nutzen.

## 1. Was tatsächlich geprüft wurde

Originalarchiv `ryzen_lambda_compare_020_20260921.tar.gz`, SHA256:
`c9856a662d4b6438b1edc42f930a3b77c3d60dd2f15b7b167a0901893c32b382`.

- Archivhash und alle 1.825 Datei-Prüfsummen des Exportmanifests stimmen.
- Alle 46 eingefrorenen Quelldateien stimmen auch mit dem veröffentlichten
  Commit `b659cb8743dd6036d91dafb466b2d12cb21a29b0` überein.
- 192 vollständige Jobs: vier Verfahren × vier Ziele × zwölf gepaarte Seeds;
  gleiche Gründer, keine automatische Verlängerung und kein ungeklärter Active-Marker.
- Task-/Result-/Checkpoint-/SQLite-Hashes passen zu den CPU-Receipts. Jeder Job
  hat genau eine Sitzung; weder Wiederaufnahme noch Reserveübertrag in diesem Lauf.
- Neue, vom Suchcode unabhängige graph6-Dekodierung mit Mengen-Schnitten prüft
  1.536 verschiedene beschriftete Graphen aus Gründern, Ergebnissen und
  Checkpoints: n=99, Grad 14, CN=1 für jede Kante sowie sämtliche fünf Scores.
- Bestwertkurven, Messpunkte und alle veröffentlichten Paarvergleiche wurden
  aus den Rohresultaten erneut berechnet und stimmen.
- Alle 192 SQLite-Dateien bestehen `integrity_check`; ihre Klassen-/Endpunktzahlen
  stimmen mit den Resultaten. Insgesamt 1.490.795 Klassenzeilen über alle Jobs;
  das sind **nicht** ebenso viele global verschiedene Isomorphieklassen.

**Prüfgrenze:** Nicht sämtliche 1,49 Millionen Archivzeilen wurden erneut
mathematisch validiert; ebenso wenig wurden alle Kanonisierungszertifikate neu
berechnet oder sämtliche Suchpfade wiederholt. Die positive Aussage betrifft
alle oben bezeichneten berichteten Graphen und die vollständige Dateiintegrität.
Der später erwähnte identische TC-Endgraph ist sogar graph6-byteidentisch;
seine Gleichheit hängt nicht allein vom gespeicherten Zertifikat ab.

## 2. Primäres Ergebnis: aktives (W,L1) nach einer CPU-Stunde

| Verfahren | Median W | Kleinster W | Größter W | L1 beim besten (W,L1)-Endpunkt | Siege / Gleich / Niederlagen gegen B0 |
|---|---:|---:|---:|---:|---:|
| B0 | 2180 | 2180 | 2180 | 2398 | – |
| P | 2141 | **2130** | 2151 | 2452 | **12 / 0 / 0** |
| T | 2151,5 | 2132 | 2153 | 2518 | **12 / 0 / 0** |
| TC | 2141 | 2141 | 2141 | 2492 | **12 / 0 / 0** |

Die L1-Spalte gehört jeweils zum besten einzelnen W-Endpunkt, nicht zum
Median-W. Ein komponentenweiser Median der Scores wäre kein bestimmter Graph.
Die Rangordnung verwendet durchgehend W und erst bei Gleichstand L1.

Direkte Paarvergleiche nach 3600 Sekunden:

| Kontrast | Siege / Gleich / Niederlagen des zuerst genannten Verfahrens |
|---|---:|
| P gegen T | **11 / 0 / 1** |
| TC gegen T | **10 / 0 / 2** |
| TC gegen P | **6 / 0 / 6** |

Alle neuen Verfahren erfüllen die vorab definierte deskriptive Schwelle gegen
B0 (mindestens acht Siege, höchstens zwei Niederlagen). TC erfüllt zusätzlich
die Schwelle gegen T. Daraus folgt ein Nutzen des größeren Katalogs **innerhalb
dieser Tabuvariante**, nicht die generelle Überlegenheit von TC gegenüber P.
Die zwölf bekannten Gründerbestände mit neuen Seeds erlauben weder eine universelle
Aussage über alle Startfamilien noch einen Existenz-/Optimalitätsbeweis.

## 3. Die Zeit- und Mengenbeschränkungen waren entscheidend

| Verfahren | Median W bei 600 s | bei 1800 s | bei 3600 s |
|---|---:|---:|---:|
| B0 | 2180 | 2180 | 2180 |
| P | 2154 | 2150 | **2141** |
| T | 2153 | 2153 | 2151,5 |
| TC | **2141** | **2141** | 2141 |

Nach zehn Minuten schlägt T P in zehn Paaren bei zwei Gleichständen und keiner
Niederlage. Nach einer Stunde verliert T gegen P elf von zwölf Paaren. TC schlägt
P nach zehn Minuten zwölfmal, nach 30 Minuten elfmal, nach einer Stunde sechsmal.
**Ein bloßer Zehn-Minuten-Vergleich hätte hier die längerfristige Rangordnung
irreführend dargestellt.** Die Kritik an meinem zunächst zu kurzen Vorschlag
wird damit durch den tatsächlichen Verlauf gestützt.

P verbessert W in elf von zwölf Läufen noch zwischen 1800 und 3600 Sekunden.
Sein letzter aktiver W-Rekord liegt je nach Seed zwischen etwa 1681 und 3522
CPU-Sekunden. TC erreicht dagegen in allen zwölf W-Jobs denselben graph6-Graphen
(W,L1)=(2141,2492) nach etwa 19,3–19,8 Sekunden; danach folgt trotz eines Restarts
pro Job kein besserer aktiver Rekord. Das belegt frühe Konvergenz der Bestwerte,
aber weder identische ganze Trajektorien noch Unmöglichkeit eines späteren Entkommens.

P schließt im W-Ziel median 374,5 Episoden ab, B0 1044,5. Mehr Episoden allein sind
hier kein Qualitätsmaß. T schafft median 7467,5 Zugiterationen, TC 3546,5; der
größere Katalog kostet messbar Suchschritte innerhalb desselben CPU-Budgets.
Die abgeschlossenen W-Jobs von TC enthalten insgesamt 4564 akzeptierte Dreierzyklen.
B0 protokolliert sogar einen akzeptierten alten Rotationszug; seine frühere Leere
auf Diagnosefällen war also kein globaler Unmöglichkeitsbeweis.

## 4. Weitere Ziele und die Bedeutung des Archivs

- **L1:** B0 bleibt überall bei 2398. P erreicht überall 2392. T und TC erreichen
  bei jeweils einem Seed 2388, ansonsten 2392. T und TC sind im aktiven skalaren
  L1-Endziel in allen zwölf Paaren gleich. Kein robuster Vorteil ihres seltenen
  besseren Einzelrekords über die zwölf Seeds.
- **F:** Alle 48 F-Jobs bleiben bei 2836. Auch kein über andere Ziele beobachteter
  Archivrekord unterschreitet 2836. Das ist ein fortbestehendes Plateau dieser
  Verfahren und Starts, kein globaler Minimalitätsbeweis.
- **Linf:** Alle aktiven Endbesten haben Linf=2; Nmax und danach L1 unterscheiden.
  P schlägt B0, T und TC jeweils in allen zwölf Paaren. Median Nmax: P=238,
  T=259, TC=259, B0=262. Bestes aktives P-Ergebnis: (2,229,2478).

Die besten **beobachteten** Rekorde dürfen nicht mit dem aktiven Zielendpunkt
eines W-/Linf-Jobs vermischt werden:

| Herkunft | W | L1 | F | Linf | Nmax |
|---|---:|---:|---:|---:|---:|
| Bester aktiver W-Endpunkt, P/W | 2130 | 2452 | 3112 | 3 | 8 |
| Beobachteter W-Rekord, T/L1, Seedindex 4 | **2123** | 2442 | 3104 | 3 | 12 |
| Beobachteter Linf-Rekord, P/F, Seedindex 8 | 2241 | 2462 | 2904 | **2** | **221** |

Der W=2123-Kandidat steht im SQLite-Rekordprotokoll von `T--lambda-L1-04`
bei CPU=2250,520038 mit Rolle `OBSERVED`. Das Archiv hat damit einen W-Kandidaten
bewahrt, der besser ist als sämtliche aktiven W-Endpunkte. Daraus folgt noch
keine allgemeine Überlegenheit von Migration; es liefert aber einen konkreten
Ansatz, den ein rein aktives Zielarchiv übersehen hätte.

## 5. Kleine Nachdiagnose: konkrete Weiterverarbeitung der Archivrekorde

Nach Abschluss des Audits wurden die vollständigen Apex-/Pivot-/Dreierzyklus-
Nachbarschaften von sechs ausgewählten Rekorden ausgezählt. Keine neue Kampagne
und kein rückwirkendes Ändern der Endpunkte. `RECORD_CENSUS.json` enthält die
Kataloggrößen, Verbesserungszahlen, graph6-Kandidaten und expliziten Züge.
20 verschiedene Ausgangs-/Zeugengraphen wurden zusätzlich mit dem neuen
unabhängigen Decoder geprüft.

- W=2130 und der TC-Graph W=2141 sind lokale (W,L1)-Minima im gemeinsamen Katalog.
- Der **archivierte W=2123-Graph ist dort kein lokales W-Minimum**. Ein Pivot ergibt
  **(W,L1,F,Linf,Nmax)=(2121,2440,3100,3,11)**.
- Der archivierte Linf-Rekord (2,221,2462) besitzt einen Pivot zu
  **(Linf,Nmax,L1)=(2,218,2476)**, mit W=2258 und F=2912. Die Verbesserung von
  Nmax geht hier mit schlechterem W und L1 einher.
- Der ausgewählte L1=2388-Rekord ist lokal L1-minimal im gemeinsamen Katalog;
  HoG mit F=2836 bleibt dort lokal F-minimal.

W=2121 und Nmax=218 sind **erst nach dem Lauf erzeugte und verifizierte Ein-Schritt-
Zeugen**. Sie gehören nicht in die zwölf gepaarten Stunden-Endpunkte. Eine
vollständige weitere Abstiegssuche oder ein globaler Rekordanspruch wurde damit
nicht durchgeführt.

## 6. Kosten und Auffälligkeit der Zeitmessung

Gemessene Worker-CPU aus wait4: **191,735161443611 Stunden** Vergleich plus
75,475785 CPU-Sekunden Kontrollen. Pro Vergleichsjob 3595,022205–3595,056523 s;
die Differenz zu 3600 s entspricht der dokumentierten Abschlussreserve. Alle
Receipts und internen Kurven sind konsistent, ohne zusätzliche Budgetsitzung.

Die externe Walltime muss korrigiert dargestellt werden:

- UTC-Zeitstempel für die Vergleichsphase: 21.09. 15:51:57 bis 22.09. 02:56:47,
  also **11 h 04 min 50 s** (lokal 17:51:57 bis 04:56:47).
- `comparison_timing.json`: monotone Dauer **10 h 15 min 10,85 s**.
- Differenz: **49 min 39,15 s**. Die CPU/monotone-Dauer-Quote ist 18,70 und damit
  für 18 einthreadige Worker keine plausible reale Auslastungsangabe.

Die Abweichung zeigt sich über viele Statusintervalle; sie ist kein einzelner
klar lokalisierter Sprung. Ursache mit dem Paket nicht feststellbar. WSL-/Clock-
Verhalten ist eine mögliche Erklärung, aber hier keine bewiesene Diagnose.
Die frühere Budget-ETA war deshalb nur eingeschränkt belastbar. Insbesondere
wird aus der monotonen Dauer **kein** Beschleunigungsfaktor abgeleitet. Der
CPU-budgetierte Vergleich bleibt als Vergleich nach den gemessenen CPU-Uhren
nachvollziehbar; eine unabhängige Hardware-Zeitkalibrierung fehlt.

## 7. Konsequenzen und vorgeschlagene nächste Schritte

1. **P als neue Arbeitsreferenz verwenden**, B0 als historische Kontrolle
   behalten. P ist besonders für W und Linf begründet; es zeigt längere produktive
   Verläufe und schlägt T im primären Stundenvergleich klar.
2. **TC als gezielten Vergleich zum größeren Katalog behalten**, aber nicht
   pauschal zum Sieger erklären. Sein Vorteil gegen T ist bestätigt, sein frühes
   gleiches Bestplateau fordert bessere Restart-/Startdiversität als eigene
   Hypothese. Keine nachträgliche Parameterwahl auf denselben Bestätigungspaaren.
3. **Archivrekorde gezielt nach ihrem jeweiligen Ziel weiterverarbeiten.**
   Die geprüften Ein-Schritt-Verbesserungen liefern dafür konkrete Startpunkte.
   Eine Rekordfortsetzung wird separat von fairen Verfahrensvergleichen geführt.
   Gemeinsamer Austausch zwischen Zielen bleibt eine zu testende Änderung.
4. **Für die Langzeitfrage zunächst P und TC im W-Ziel länger vergleichen.**
   Sinnvoller konkreter Vorschlag: die zwölf W-Paare zustandserhaltend von einer
   auf vier CPU-Stunden erweitern, also 24 × 3 = **72 zusätzliche CPU-Stunden**.
   Das vorhandene `extend` erhöht allerdings alle 192 Jobs; es darf für diesen
   selektiven Vorschlag nicht unverändert aufgerufen werden. Vorher braucht es
   eine explizite Auswahl im Fortsetzungsmanifest und Prüfung der Zeitmessung.
5. F=2836 weiterhin als offene strategische Schwierigkeit behandeln. W- und
   Linf-Fortschritte ersetzen keinen F-Fortschritt; eine weitere unveränderte
   Gesamtverlängerung aller F-Jobs ist durch diesen Lauf nicht besonders gestützt.

Die 72-h-Fortsetzung ist hier ein neuer Vorschlag, **nicht gestartet oder zusätzlich
freigegeben**. Der abgeschlossene erste Vergleich und seine Originaldateien bleiben
unverändert. Es wurde weder auf Ryzen noch auf Office ein weiterer Lauf angestoßen.

## Reproduzierbare Dateien

- `SUMMARY.json`: Auditumfang, alle Paarzahlen, Seedwerte und Zeitkurven-Zusammenfassungen.
- `AUDIT.json.gz`: vollständiger rechnerischer Auditbericht einschließlich Paar-Scorelisten.
- `ENDPOINTS.json.gz`: alle 192 aktiven Endpunkte mit graph6, Seeds, CPU und Messpunktwerten.
- `RECEIPTS.json`: ursprüngliche 193 CPU-Receipts einschließlich Kontrolljob.
- `RECORD_CENSUS.json`: Nachdiagnose mit exakten Verbesserungstrades und Kandidaten.
- `experiments/memetik/lambda_audit_20260922/audit.py`: unabhängiger Prüfer; erwartet
  das unverändert entpackte Originalarchiv und ein separates Ausgabeverzeichnis.
- `experiments/memetik/lambda_audit_20260922/census.py`: reproduziert die kleine Nachdiagnose
  anhand der vom Prüfer erzeugten Dateien.

Das vollständige Originalarchiv bleibt über die obige SHA256 identifiziert;
die 287-MiB-Datei wird nicht als regulärer Git-Blob dupliziert. Sämtliche Aussagen
zu Archivinhalt und Ablauf sind von den ausdrücklich benannten Prüfgrenzen abhängig.
