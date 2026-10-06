# ROOT8105: Ergebnis der40000-Abstiege-Messung

06.10.2026. Run fb64e03e22304cb496455ceaa0af1c27, Quelle05fee711592baebc469ab7461376be3ca89046d0.

**Die neue Reihenfolge ist ein klarer Kandidat für die weitere Forschung. Eine
vollständige Erschöpfung ist durch diese Messung nicht gerechtfertigt.**
Das vorab festgelegte Freigabekriterium wird nicht erreicht; insbesondere fehlen
stabile Aussagen zur letzten Ebene. Die geschätzte kumulierte Baumgröße sinkt
stark, bleibt aber selbst im besten Arm astronomisch groß.

## Integrität und Umfang

Alle96 Aufträge (24 feste Roots × vier Arme), insgesamt40000 Abstiege, sind
vollständig vorhanden. Der atomare Abschlussbeleg stimmt mit der SQLite-Datei
überein: sämtliche Ergebnisse, Digests, Rootzustände, Versuche und Sitzung.
Alle Versuche sind geschlossen, ihre wait4-CPU summiert sich zum Worker-Gesamtwert.
Die Cloud-Abschlussabweichung der früheren96er Kalibrierung tritt hier nicht auf.

Der Audit reproduziert außerdem318789 gespeicherte Zufallsziehungen/Gewichtsschritte
anhand von Seed, Vorschlagsbreite und Rang. Positive Gewichte entsprechen den
Produkten der Vorschlagsbreiten, Nullfortsetzungen werden nicht als Ersatzziehungen
behandelt. Keine Suchrechnung, keine Censuszählung und kein SAT-Lauf wurde wiederholt.
Dies ist ein Integritäts- und Auswertungsaudit, noch keine unabhängige Überprüfung
vollständiger Graphpräfixe: Diese sind nur über Seeds/Ränge rekonstruierbar gespeichert.

## Vier Vergleichsarme

Jeder Arm verwendet dieselben24 Roots und denselben Wald von(a,M)-Repräsentanten.
F bedeutet hier das historische Verfahren unter der gemeinsamen Matchingvorbelegung.
Die Angaben zur Baumgröße sind Importance-Schätzungen, keine exakten Knotenzahlen.

| Reihenfolge | Vorwärtsprüfung | log10 mittlere kumulierte Knoten bis13 | Tiefe13 erreicht | Worker-CPUh |
|---|---|---:|---:|---:|
| numerisch | nein |37,04875|0/10000|10,408|
| numerisch | ja |35,31889|102/10000|7,229|
| Nachbarschaft zuerst | nein |31,03541|0/10000|1,385|
| Nachbarschaft zuerst | ja |29,56065|17/10000|2,107|

Die Punktverhältnisse betragen:

- Reihenfolgenwechsel ohne Vorwärtsprüfung: rund1,03Millionen weniger geschätzte Knoten.
- Vorwärtsprüfung bei numerischer Reihenfolge: Faktor53,7.
- Vorwärtsprüfung bei Nachbarschaft zuerst: Faktor29,8.
- Beide Änderungen gegenüber numerisch/F: Faktor30,8Millionen.

Auch rootweise zeigen alle24 Stichprobenmittel die gleiche Richtung; das letzte
Verhältnis liegt zwischen3,90 und140,0Millionen. Das ist ein breites empirisches
Signal innerhalb dieser Auswahl, kein Konfidenzintervall und keine Aussage über
alle8105 Roots. Die24 Roots sind keine designgerechte Zufallsstichprobe aus8105.

Die beobachteten CPU-Kosten dürfen nicht mit diesen Baumgrößenfaktoren verwechselt
werden. Nachbarschaft plus Vorwärtsprüfung kostet für dieselbe Zahl Abstiege etwa
20% der CPU von numerisch/F. Gegenüber Nachbarschaft ohne Vorwärtsprüfung kostet
sie etwa52% mehr pro Messkampagne, obwohl ihr geschätzter Suchbaum kleiner ist.
Die Kosten einer vollständigen Enumeration wurden nicht gemessen.

## Warum wir das Freigabekriterium nicht als erfüllt behandeln

Das vorab festgelegte Gate verlangt mindestens100 positive Endgewichte je Arm
und ausreichende effektive Stichprobengröße. Nur numerisch mit Vorwärtsprüfung
hat102 Endtreffer; der neue starke Arm hat17. Der gepaarte Gesamtvergleich bleibt
im Originalexport korrekt INSUFFICIENT_INFORMATION. Es wird kein fehlendes
Intervall nachträglich zu einer Freigabe umgedeutet.

Zudem müssen zwei verschiedene Größen getrennt werden:

| Größe | numerisch + Vorwärtsprüfung | Nachbarschaft + Vorwärtsprüfung |
|---|---:|---:|
| ESS der kumulierten Gewichte |2499,27|419,10|
| ESS allein der Gewichte auf Tiefe13 |32,65|2,55|
| größter Anteil am Gewicht auf Tiefe13 |10,35%|57,33%|

Das vorhandene95%-Bootstrapintervall [35,30598;35,33213] im numerischen starken Arm
bezieht sich auf **log10 der kumulierten Baumgröße**, nicht auf die letzte Ebene.
Die Bedingung von100 Endtreffern ist ein vorab gewähltes konservatives Gate, kein
mathematisch notwendiges Kriterium für jede kumulierte Schätzung. Künftige Designs
sollten kumulierten Aufwand und seltene Endpfade getrennt vorregistrieren. Das
ändert die jetzige vorregistrierte Entscheidung nicht rückwirkend.

Ein weiterer kleiner Auswertungsbefund: Die Tiefenprofile im Originalsummary
mitteln über alle10000 Abstiege, während die Hauptkennzahl erst innerhalb jeder
Root mittelt und dann die24 Roots gleich gewichtet. Wegen416/417 Abstiegen je Root
ist der Unterschied klein, aber systematisch. AUDIT_ANALYSIS.json enthält zusätzlich
korrekt gleich nach Roots gewichtete Tiefenprofile. Der Rohbericht bleibt unverändert.

Null Endtreffer in den F-Armen beweisen keine leere Ebene und keinen Rootausschluss.
Mehr Endtreffer im stärkeren Arm widersprechen nicht dessen engerem Suchraum:
Die zusätzliche Propagation ändert die Vorschlagsverteilung und vermeidet manche
frühen Sackgassen. Es werden keine identischen vollständigen Pfade verglichen.

## Was folgt für die Machbarkeit?

Im besten Arm beträgt die geschätzte mittlere kumulierte Baumgröße pro ausgewählter
Root immer noch etwa3,64×10^29, schon bis Tiefe13. Unter dieser Schätzung ist eine
zeilenweise vollständige Erschöpfung keine realistische nächste Kampagne.
Die Zahl ist keine zertifizierte untere Schranke; daher folgt daraus weder ein
Unmöglichkeitsbeweis noch ein globaler Ausschluss der Methode. Ein weiterer
Faktor100 würde die Größenordnung als Erschöpfungsstrategie nicht retten.

Die17 Endpfade des neuen starken Arms verteilen sich auf12 Roots. Sie sind gute
konkrete Ausgangspunkte für eine Fortsetzungsanalyse. Die102 numerischen Endpfade
verteilen sich aufalle24 Roots und bilden eine anders ausgewählte Vergleichsmenge.
Sie sind keine fertigen99-Graphen und bislang nicht separat rekonstruierte Zeugen.

## Empfohlener nächster Schritt

1. Die17 Matching-Endpfade aus ihren gespeicherten Rängen rekonstruieren und
   unabhängig an Grad-, Rand-, Paar- und Matchingbedingungen prüfen. Das ist eine
   neue Zeugenprüfung, keine Wiederholung der40000er Kampagne. Alle119 Endpfade
   bleiben in DEPTH13_PATHS.json erhalten; numerische Pfade bei Bedarf als Kontrolle.
2. Für die bestätigten17 Präfixe die Erweiterbarkeit jenseits der geschlossenen
   Wurzelnachbarschaft untersuchen: zunächst alle71 offenen Zeilen als mögliche
   nächste Zeile vergleichen. Lokale Vorschlagsbreite und echte F-Fortsetzbarkeit
   unterscheiden; fehlgeschlagene Stichproben sind kein UNSAT.
3. Aus diesem Frontierbefund eine dynamische Reihenfolge für Tiefe14 und höher
   ableiten. Erst danach einen neuen, klar definierten Vergleich starten. Harte
   Fälle einzelner(a,M)-Klassen gegebenenfalls mit zertifizierbaren SAT-Ausschlüssen
   behandeln. Die bisherigen Ergebnisse liefern selbst noch keinen solchen Ausschluss.

Eine bloße Wiederholung mit sehr viel mehr uniformen Abstiegen ist angesichts der
Endgewichts-ESS von2,55 nicht mein bevorzugter nächster Aufwand. Mehr Stichproben
würden die fehlende Analyse der tiefen Fortsetzbarkeit nicht ersetzen.

## Betrieb und Abrechnung

Sitzung laut UTC-Endbeleg:16:00:07,665 bis17:58:33,553 MESZ, also1h58min25,887s.
Windows-Stoppuhr und Host-UTC stimmen in den erhaltenen Statusproben eng überein;
die WSL-monotonic-Uhr läuft abweichend. Kein erfundener Korrekturfaktor wird benutzt.
Die ursprüngliche Planung von2–4h war eine grobe Hochrechnung, keine zugesicherte ETA.

Gemeldetes Gesamtkonto einschließlich Vorabprüfung und gemessenem Exportanteil:
76693,8290194CPU-s =21,30384CPUh. Davon76062,256315CPU-s Worker und
102,377598CPU-s Supervisor. CPU sind die aufgezeichneten Prozessmessungen, nicht
aus der abweichenden WSL-Walltime zurückgerechnete Werte.

Abrechnungsgrenze der Version1.0.1: Das Schreiben und erneute Einlesen des großen
final_receipt.json erfolgt nach der letzten Export-CPU-Buchung. Dieser letzte
Serialisierungs-/Prüfnachlauf ist nicht separat gemessen; die obige Zahl wird daher
nicht als sekundengenauer Gesamtverbrauch sämtlicher Programmteile ausgegeben.
Das ist eine Korrektur zur pauschalen Formulierung vollständiger Endabrechnung,
kein Verlust von Worker-Endbelegen. Vor einer neuen Betriebsversion ist der Nachlauf
separat zu erfassen; am abgeschlossenen Lauf wird nichts umgeschrieben.
