# ROOT8105 — Abschlussprüfung des Ryzen-Zensus, 06.10.2026

## Ergebnis und Aussageumfang

Der vollständige Export enthält **8105 Roots × 83 Zielzeilen = 672715 Zählwerte**.
Die aus den Einzelwerten erneut berechnete Summe der kleinsten Breite je Root ist
**4.846.403.679**. Datenbank, Worker-Ausgaben und Export stimmen vollständig überein.
**13455 von 13455 unabhängig nachgezählten Paaren stimmen exakt überein; keine Abweichung.**
Die Einzelheiten stehen in `independent_summary.json`.

Für Roots als Ebene 1 gilt im historischen F-Modell:

`B2 = sum_r min_{t=1..83} W_F(r,t) = 4.846.403.679`.

Dabei wird je Root genau eine Zielzeile gewählt, bei Gleichstand die kleinste
Labelnummer. Gezählt werden die damit erzeugbaren gelabelten Kinder, vor den
zusätzlichen LD/CAP-Filtern und vor einer weiteren Isomorphiereduktion. Weder
Fortsetzbarkeit zu einem vollständigen SRG noch eine Gesamtbaumgröße folgt daraus.
Die Konvention „Roots = Ebene 0“ nennt dieselbe Rechnung einen Erweiterungsschritt.
Kein Root hat eine Nullbreite: F allein schließt hier keinen Root aus.

| Roottyp | Roots | Kleinste Root-Minimalbreite | Median der Root-Minimalbreiten | Größte Root-Minimalbreite | Beitrag zu B2 |
|---|---:|---:|---:|---:|---:|
| 0 | 7418 | 515304 | 648108 | 689767 | 4706649635 |
| 1 | 630 | 199108 | 206129 | 212670 | 129792039 |
| 2 | 57 | 172657 | 174549 | 179820 | 9962005 |

Quantile sind sortierte Ordnungsstatistiken mit Index floor(p·(n−1)). Weitere
Breitenstatistiken stehen in `integrity.json`; keine interpolierten Zählwerte.
Typ 0 trägt rund 97,1 Prozent dieser Rohbreite. Für die nächste Methodenprüfung
werden die seltenen Typen dennoch bewusst überrepräsentiert.

## Herkunft und Vollständigkeitsprüfung

Eingang: `ROOT8105_Census_1.0.1rc3_results_20261006.tar.gz`, SHA256
`84751007d21c17f234cbc11a19b32a85c50a2ae29791ea959111a6a54ba5908d`.
24344 Archiveinträge, 135080211 unkomprimierte Bytes. Das Archiv wurde mit sicherer
Pfadbehandlung separat entpackt. Die Originaldatenbank wurde ausschließlich lesend
geöffnet; keine Produktionsprozesse oder Konten wurden verändert.

Lauf: `53167b04133d421fa22e8191e218d3bf`.
Modell: `F-historical-core-1.0.1-depth1`.
Quellreferenz und Regelbasis: Commit
`44439c8cac8259257f80842a567c07e4a7f8e00d`,
`experiments/memetik/root8105_census_1_0_1rc3`.
Codehash: `34fbec2d77648323ac559d928ead5076679a7ad1c7eafbbdd3b2dbd778d0fce1`.
Rootdatei: `c525d03be144a7493c3239340c6263dcb8a29b5521e5d3b152ce43afe90cac41`.

Ausgeführt: SQLite integrity_check und rc3 audit_start; vollständiger Fingerprint-
und Manifestvergleich; feste Rootidentitäten samt Orbit/Stabilisator-Kontrolle;
8105 Ergebnisdigests; Zuordnung zu 8105 abgeschlossenen Versuchen; Abgleich jedes
Versuchsinputs und -outputs; vollständige Zielmenge 1..83; nichtnegative ganzzahlige
Counts; Exportgleichheit, alle Minima und alle Argmin-Mengen. Drei Sitzungen sind
geschlossen, kein Versuch offen, kein ERROR-Root, keine CPU-Untergrenzenmarkierung.
`certified:false` im Export bleibt korrekt: dies sind keine formalen Zählzertifikate.

## Unabhängige Nachzählung

Vor der Nachzählung wurden **13455 unterschiedliche Root/Ziel-Paare** fixiert,
also mindestens 2 Prozent. Seed: `810520261006`. Drei Roottypen × zehn nach Breite
sortierte Rangsegmente ergeben 30 Schichten. Gleichstände: Root-ID, Ziel-ID.
Proportionale Zuteilung mit größtem Rest; Ziehen ohne Zurücklegen je Schicht.
Auf Typ 0/1/2 entfallen 12314/1050/91 Paare. Die Auswahl hängt von den gemeldeten
Breiten ab, nicht vom späteren Nachzählergebnis.

SHA256 des vorab gespeicherten `sample_manifest.json`:
`ad64b7301aef8ed830d28ea73ae690db8e02ac6db2d0a35a173bd3cc1c342d1c`.

Nachzählung durch `VertexSampler` mit Python-Ganzzahlen und Vertex-Rekursion,
in acht lokalen Prüfprozessen. Der Zensus verwendete die anders aufgebaute
NumPy-Kanten-DP. **Die Zählalgorithmen sind unabhängig, Geometrie und
Constraint-Aufbereitung werden geteilt.** Dies ist keine vollständig unabhängige
Modellimplementierung und kein Beweis für sämtliche nicht nachgezählten Paare.
Frühere Fixture-Vergleiche bleiben Regressionen derselben DP-Herkunftslinie;
Fixture-Überschneidungen werden separat in `fixture_overlap.json` ausgewiesen.

Gemessene neue Nachzählung: 2735.967331 Aufgaben-CPU-Sekunden
(0.759991 CPUh), 344.408 lokale Walltime-Sekunden.
212 ausgewählte Paare überschneiden sich mit den 128 Fixture-Roots; auch diese
wurden neu mit Vertex-Rekursion gezählt.

Einzelergebnisse einschließlich Soll/Ist und gemessener CPU pro Prüfaufgabe stehen
in `independent.jsonl.gz`. Die dort summierte Prüf-CPU zählt die Nachzählaufgaben;
Prozessstarts und Poolverwaltung sind darin nicht vollständig enthalten. Diese
neue Cloud-Prüfarbeit wird nicht nachträglich in die unveränderte Ryzen-Abrechnung
hineingeschrieben. Keine erneute vollständige Zensusrechnung wurde gestartet.

## CPU, Laufzeit und Budget

| Konto | Verbuchte CPU-Sekunden |
|---|---:|
| Worker, wait4-Endabrechnungen | 430996,334146 |
| Sitzungen einschließlich Hosthelfer | 4497,326171300853 |
| Initialisierung, Vorabprüfung und Exporte | 138,1883487 |
| Gesamt nach letztem Export | 435631,8486660008 |

Das sind **121,008847 aggregierte CPU-Stunden**, nicht reale Laufzeit.
In den Sitzungskonten stecken 1288,78125 Sekunden Windows-Hosthelfer,
0,024199 Sekunden sonstige Linux-Kinder und 3208,520722 Sekunden Supervisor.
Diese Positionen nicht erneut zur Gesamtsumme addieren. Ebenso sind CPU-Zeiten
je Ziel deskriptiv und keine zusätzlich zu wait4 zu addierenden Konten.
Der letzte Export erhöht die CENSUS_END-Summe um 1,6707848 Sekunden.
Die Ledger-Arithmetik und geschlossenen Endbelege stimmen; die historischen
CPU-Messungen wurden hier nicht nachträglich physikalisch neu gemessen.

Hauptsitzung: 40230,493051 Sekunden nach UTC, also **11 h 10 min 30 s**;
Windows-Stopwatch am letzten Helferstand: 40228,757255 Sekunden. Die Messgrenzen
unterscheiden sich durch Start/Abwicklung. Abschluss am 06.10.2026 um
01:48:28,330 Europe/Berlin. Kalibrierung: weitere 345,778698 Sekunden;
leerer erneuter Kalibrierungsaufruf: 0,537153 Sekunden. Die Pause zwischen den
Sitzungen ist keine Rechenlaufzeit.

Die ursprüngliche Meldeschwelle blieb 172800 Sekunden = 48 CPUh. Genau eine
Anfrage wurde erzeugt, keine Antwort verbucht, kein Budget erhöht. Die weitere
Rechnung bis zum regulären Abschluss entspricht GC-19. Überschreitung:
73,008847 CPUh. Datenbank-Anfrage: `CLOSED_COMPLETE`.

## Zwei Betriebsbefunde

1. **Veraltete Anfragedatei.** `time_request.json` steht noch auf `OPEN`.
   `close_requests` aktualisiert nur die Datenbank. Mit unverändertem rc3 in einer
   wegwerfbaren synthetischen Datenbank reproduziert: DB `CLOSED_COMPLETE`, Datei
   `OPEN`. Dies ist ein Konsistenzfehler der Anzeige, kein offenes Rechenkonto.
   Vor dem nächsten Paket atomaren Dateiabgleich beim Abschluss und beim Neustart
   ergänzen; Regression muss beide Darstellungen nach COMPLETE und USER_BUDGET_ZERO
   prüfen. Das eingefrorene Ergebnisarchiv wird nicht rückwirkend repariert.
2. **WSL-Uhrenvergleich nicht freigegeben.** Alle 62 gespeicherten Statusmeldungen
   zeigen clock_ok=false; 61 enthalten eine Hostmessung, die erste noch keine.
   Die gespeicherten Hoststände sind aktuell (Abstand zur Status-UTC −0,533 bis
   +3,374 Sekunden). Die Änderung der Host-UTC stimmt mit der Änderung der
   Windows-Stopwatch bis auf maximal 0,001078 Sekunden überein. Keine gespeicherten
   Helferwarnungen oder Hostlogfehler. Nach Anlauf scheitert somit der
   Host/WSL-Vergleich, nicht das Vorhandensein einer Hostuhr.

Die für den Vergleich benutzten Monotonic-Anker und Differenzen wurden nicht
mitgespeichert. Ein exakter Driftverlauf oder eine genaue Betriebssystemursache
lässt sich damit nicht rekonstruieren. Der mediane Statusabstand von 652,49 UTC-
Sekunden bei nominell 600 Gastsekunden ist zusätzliche Evidenz, kein exakter
Driftmesswert: Schleifenarbeit kann den Abstand ebenfalls vergrößern.
`ETA unknown` war folgerichtig. Kein erfundener CPU-Skalierungsfaktor.
Für Folgeläufe beide Anker, Deltas, Abweichung, Frische und konkreten Fehlergrund
speichern und eine mehrminütige Lastprüfung vorsehen. Der kurze Preflight-PASS
belegte Lesbarkeit und Beendigung, keine langfristige Uhrengenauigkeit.

Die kleinste gespeicherte freie RAM-Menge lag bei 48347914240 Bytes; diese
Statusstichprobe belegt keinen sekundengenauen Minimalwert des gesamten Laufs.

## Konkrete Fortsetzung: Filterpilot, noch nicht gestartet

Der nächste sinnvolle Schritt ist ein begrenzter Vergleich der Zusatzfilter;
4,846 Milliarden Rohkinder rechtfertigen keine direkte Vollmaterialisierung.
`filter_pilot_manifest.json` fixiert bereits die vollständige Auswahl:

- 24 Roots, acht je Typ; je Typ acht Rangblöcke nach Root-Minimalbreite.
  Abwechselnde Präferenz für trivialen/nichttrivialen Stabilisator, soweit im
  jeweiligen Block vorhanden; sonst Auswahl aus dem ganzen Block.
- Je Root drei unterschiedliche Zielzeilen: schmalste, Medianrang, breiteste,
  sortiert nach (Breite, Label). Je Ziel 64 gleichverteilte Ränge ohne Zurücklegen.
- Insgesamt 72 Root/Ziel-Kombinationen und **4608 Zustände**. Seed `810520261007`.
  SHA256: `1411d0048ef189289d2f2388f6463052ea55ae2192dd5bc45468b303b1fa9d68`.
- Dieselben Zustände unter F, F+LD, F+CAP und F+LD+CAP prüfen. Je Variante
  Ausschlüsse, Überschneidungen, Ablehnungsgrund und CPU ausweisen. Unranking
  separat messen. Ergebnisse je Typ und Zielrang berichten; die bewusst
  geschichtete Auswahl ist keine gleichverteilte Stichprobe aller Rohkinder.
- Vor Ausführung SAT-Kontrolle festlegen: pro Typ und Ablehnungsgrund bis zu acht
  Fälle deterministisch nach (Root, Ziel, Rang) wählen; unabhängig kodierte
  notwendige Bedingungen prüfen. UNKNOWN bleibt UNKNOWN. Bereits bewährte
  modellgerechte Positivkontrollen müssen ebenfalls bestehen.

Ein Folgelauf erhält ein separates Paket und eigene Konten; rc3 bleibt fixiert.
Zunächst alle 72 Sampler aufbauen und Gesamtkosten einschließlich Unranking
messen. Für den Pilot eine großzügige Meldeschwelle von vier aggregierten CPUh
mit GC-19-Antwortkanal vorsehen, einschließlich SAT-Kontrollen und Nebenarbeit;
keine Walltime-Garantie daraus ableiten. Die Laufzeitprognose erst nach einem
kurzen End-to-End-Durchsatztest desselben neuen Pakets auf Zielhardware nennen.

Abnahme: keine unbegründete Ablehnung der Positivkontrollen, keine Abweichung der
unabhängigen Kontrollfälle, geschlossene Konten und berichtete Filterkosten.
Erst danach einen Tiefe-2/3-Versuch dimensionieren. Überlebende sind keine
SAT-Zeugen; gemessene Ausschlussquoten sind keine exakten gefilterten Breiten.
Ein entsprechender Filterlauf wurde in diesem Audit **nicht** gestartet.
Aktive Regeln: GC-01/08/10/11/15/16/18/19/20/21.

## Reproduktion

`audit.py SOURCE RUN OUTPUT` mit der geprüften Audit-Pythonumgebung ausführen.
SOURCE ist das unveränderte rc3-Quellverzeichnis am oben genannten Commit;
RUN das entpackte Originalverzeichnis. Das Skript öffnet RUN nur lesend, erzeugt
aber eine neue unabhängige Nachzählung und schreibt OUTPUT. Danach
`analyze.py SOURCE RUN OUTPUT` für Uhrenauswertung, Anzeigeregression und den
unverändert als Vorschlag markierten Filterplan ausführen. Vorher entsprechend
AGENTS.md den Interpreter über `tools/memetik/audit_python.py` prüfen.
Alle SHA256-Zuordnungen stehen im begleitenden Dateiverzeichnis.
