# Vorabplan: frühe R/LD-Diagnostik

Festgelegt nach Abschluss A, vor irgendeinem Ergebnis dieser Diagnose.
Basis:0e18d30faca11b62350e5ab95c6f8b6af28953c7; Regeln:84180ad8.
GC-08/16/17/19/20/22. Keine neuen Zufallspfade und kein Vollcensus.

Population: gespeicherte10000 Pfade von Zelle3, geschichtet nach24 festen Roots.
40 Pfade pro Root ohne Zurücklegen, Python Random(8105202610063000+root_id).
Auswahlreihenfolge in SELECTED_PATHS.json; Inklusionswahrscheinlichkeit40/n_r.
Erste4 je Root bilden eine vorab feste Kostenkalibrierung (4/n_r), bevor der
Rest gestartet wird. Beide Stufen sind keine Auflösung extrem seltener Ereignisse.
Datei stammt aus dem hashgeprüften originalen Abschlussbeleg5e7f8273...;
keine erneute Prüfung oder Berechnung der40000 abgeschlossenen Pfade.

Tiefe d bedeutet d vollständige H-Zeilen einschließlich Root. Nur d=2,3.
Rekonstruktion aus gespeichertem Matching, Vorschlagsrängen und dem fixierten
Sampler, mit Propagation nur bis zur jeweiligen Tiefe. Gespeicherte End-A werden
nicht gelesen. Rekonstruktion dient der Wiederherstellung, nicht neuer Suche.

Prädikat Q_d^R: jede zu Tiefe d offene Zeile hat eine Lösung von R.
Q_d^LD: jede solche Zeile hat eine Lösung von R+LD. Beide mit demselben
vorgegebenen Rootmatching M, soweit eine seiner Kanten die Zielzeile berührt.
Kein propagiertes A als Zusatzbedingung. M ist eine Klassenannahme und muss
auch vor vollständigem Ausbau der Rootnachbarschaft erhalten bleiben.
Eine negative Zielzeile genügt; UNSAT wird zertifiziert. Für positive Zustände
alle offenen Zeilen lösen und direkte Ganzzahlzeugen speichern. R und R+LD
getrennt. Falls ein R-Zeuge LD erfüllt, darf er direkt auch LD belegen.

Pruning bedeutet Tod sobald Q auf einer geprüften Vorstufe scheitert. Daher
J_2=Q_2 und J_3=Q_2 AND Q_3, jeweils getrennt für R und LD. Keine Bisektion.
Monotonie wird nicht vorausgesetzt, insbesondere weil ehemals offene Zielzeilen
später aus der Testmenge verschwinden können. Frühere tote Zustände bleiben
im definierten Pruningbaum tot.

Für die endliche gespeicherte Population pro Root: Mittel von W_d*J_d über
zufällig gezogene Pfade (Horvitz-Thompson mit gleichen Einschlusschancen,
vereinfacht zum Stichprobenmittel), dann gleiches Mittel über24 Roots.
W_d sind ursprüngliche inverse Pfadwahrscheinlichkeiten ohne neue Gewichtung.
Für d=3 bleibt das frühe J_2 enthalten. Quotient zu mittlerem W ist nur eine
Verhältnisschätzung, kein selbst erwartungstreuer Schätzer und keine Schranke.
Keine Aussage über8105 Roots. ESS, größter Gewichtsanteil und Prüfumfang melden.
119 alte Endpunkte werden nicht beigemischt.

Kalibrierumfang96 Pfade,192 Zustände, maximal31392 Einzelmodelle für zwei
Varianten und81/82 offene Zeilen. Die vollständige960er-Stufe ist zehnmal so
groß. Laufzeit/Peak-RAM/Dateivolumen zuerst messen, dann entscheiden. Keine
automatischen Zeitabbrüche; hier endliche vorab fixierte Aufgabenzahl, kein
Zeitbudget. Keine Nutzerprozesse ändern. Ergebnisse einzeln in privatem
Arbeitsverzeichnis, anschließend Hashreceipt und geschlossenes Archiv.

N1 danach: generischer Produktencoder; vollständiger3x3-Rook als positive
Kontrolle, freie Relaxation dieses Rooks, gestörte Zeugen als Negativtest des
Direktprüfers;17 ausgeschlossene feste Präfixe als Encoder-Negativkontrollen.
Externer DRAT-Prüfpfad vor Klassenausschlüssen. Noch kein Klassenpilot gestartet.
