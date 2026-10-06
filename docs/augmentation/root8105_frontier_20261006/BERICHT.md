# ROOT8105: alle 17 geprüften Tiefe-13-Präfixe sind nicht ergänzbar

06.10.2026. Ausgangspunkt: 202b805ae17ff16745176bc5913936cb79744d4d.
Untersucht wurden ausschließlich die 17 gespeicherten Endpräfixe des Arms
Nachbarschaft zuerst plus Vorwärtsprüfung, aus 12 der 24 Pilot-Roots.

## Ergebnis und Konsequenz

**Für jedes der 17 festen Präfixe wurde eine offene Zeile gefunden, deren notwendige
Bedingungen unerfüllbar sind. Alle 17 Widerspruchsbelege wurden mit einem separaten
RUP-Prüfer bestätigt. Deshalb kann keines dieser festen Präfixe zu einem
srg(99,14,1,2) ergänzt werden.** Dies ist ein endlicher, rechnerisch zertifizierter
Teilausschluss; keiner der zwölf Roots als Ganzes ist ausgeschlossen.

Damit ändert sich die sachliche Fortsetzung: Eine andere nächste Zeile oder mehr
Abstiege unterhalb genau dieser Präfixe können ihre Ergänzbarkeit nicht retten.
Die bisherige Prüfung 17/17 PASS bleibt richtig für ihren angegebenen Umfang:
Grade, Rand-/Paarbedingungen der gebauten Zeilen, Kapazitätsintervalle und
abgeschlossene Sternrelaxation. Sie war ausdrücklich kein Ergänzbarkeitsnachweis.
Jetzt liegt die stärkere negative Aussage für diese 17 Objekte vor.

## Vollständige Frontiermessung

| Größe | Ergebnis |
| --- | ---: |
| Feste Präfixe | 17 |
| Offene Zeilen je Präfix | 71 |
| Vollständig untersuchte Präfix-Ziel-Paare | 1207 |
| Lokale Vorschläge insgesamt | 1432 |
| F-zulässige Vorschläge | 1429 |
| Nicht F-zulässige Vorschläge | 3 |
| Zielzeilen mit lokaler und F-Breite null | 601 |
| Zielzeilen mit positiver Breite | 606 |
| Nullzeilen pro Präfix | 29 bis 46 |
| Größte lokale Vorschlagsbreite | 11 |

Dies sind vollständig ausgezählte endliche Familien, keine Punktschätzungen oder
Stichproben. Die 1207 lokalen Breiten werden vom fixierten RowProposal exakt
berechnet. Alle 1432 Vorschläge wurden entpackt und geprüft; positive
F-Belegungen wurden direkt gegen die ursprünglichen Ganzzahlbedingungen geprüft.
Die drei Ablehnungen besitzen zusätzliche RUP-geprüfte UNSAT-Belege.
Der Zählalgorithmus selbst ist kein formal verifizierter Programmcode;
die Zertifizierung der 17 Teilausschlüsse hängt von seinen Nullzählungen nicht ab.

F bezeichnet hier präzise die historische Zielzeilenprojektion unter den
bereits gespeicherten notwendigen Propagationsfestlegungen. Die separat gefundenen
Sternzeugen aus der vorigen Prüfung wurden **nicht** als zusätzliche Festlegungen
verwendet. F-Zulässigkeit ist weiterhin keine volle SRG-Ergänzbarkeit.

Alle drei F-Ablehnungen liegen in prefix_r6682_w290, Zielzeile 7, bei den Rängen
1, 2 und 3. Für alle anderen Vorschläge fallen lokale Zulässigkeit und F-Mitgliedschaft
in dieser konkreten Untersuchung zusammen. Das begründet keine allgemeine
Gleichheit beider Modelle.

## Warum eine einzige Nullzeile das feste Präfix ausschließt

Sei t eine noch offene H-Zeile; x_v bezeichnet ihre Kante zum H-Vertex v.
Jede SRG-Ergänzung muss gleichzeitig erfüllen:

1. x_t=0 und x_u=A[u,t] für jede bereits vollständig gebaute Zeile u;
2. die 14 Randmargen: Summe der x_v über Labels mit Randpunkt c gleich 1,
   wenn c im Label von t oder dessen antipodalem Partnerlabel liegt, sonst 2;
3. für jede der 13 gebauten H-Zeilen u die Paarbedingung
   Summe der x_v über v in N_H(u) gleich 2-A[u,t]-|label(u) geschnitten label(t)|.

Die zweite Gruppe impliziert H-Grad 12, weil jedes H-Label genau zwei Randpunkte
enthält. Die dritte Gruppe folgt unmittelbar aus lambda=1 und mu=2 nach Abzug
der gemeinsamen Randnachbarn. Die unabhängig erzeugte CNF enthält nur diese
notwendigen Bedingungen. Sie benutzt weder RowProposal noch den historischen
Encoder, gespeicherte Propagationsfestlegungen oder Sternzeugen.

Für jedes Präfix ist eine solche CNF unerfüllbar. Damit existiert schon diese
eine erforderliche vollständige Zeile nicht; die Reihenfolge weiterer Zeilen
kann daran nichts ändern. Andere Zeilen können dennoch einzeln viele zulässige
Erweiterungen besitzen. Darin liegt kein Widerspruch zu den 1429 F-Mitgliedern.

## Belege, Prüfumfang und Kontrollen

FRONTIER_DATA.zip enthält die vollständigen Breiten, 1429 positiven F-Belegungen,
alle negativen Ränge, 17 unabhängige Zeilenausschluss-CNFs mit RUP-Belegen sowie
drei F-Ablehnungs-CNFs mit RUP-Belegen. SUMMARY.json nennt für jedes Präfix die
konkrete ausgeschlossene Zeile. FINAL_RECEIPT.json im Datenarchiv enthält die
vollständigen Ergebnisobjekte und ihre Hashverknüpfungen.

certify_dead.py erzeugt die unabhängigen Einzeilenmodelle. Der separate
rup_check.py importiert keinen SAT-Solver: Er bestätigt jede hinzugefügte Klausel
mittels Unit-Propagation unter ihrer Negation und verlangt eine so geprüfte leere
Klausel. Löschungen werden ignoriert; zuvor bewiesene Folgerungen dürfen erhalten
bleiben. RAT-Schritte ohne RUP-Eigenschaft werden nicht akzeptiert.
Die 17 Belege haben zwischen 34 und 1347 RUP-Additionen. Die Aussage vertraut der
mathematischen Übersetzung der angegebenen Gleichungen, dem Kardinalitätsencoder
und diesem veröffentlichten Prüfer; es wird keine Prüfung durch einen formalen
Theorembeweiser behauptet.

Zusätzlich bestehen 17 konkrete positive Zeilenkontrollen: je eine bereits direkt
geprüfte zulässige Zeile wird im unabhängigen Encoder vollständig festgesetzt und
als SAT bestätigt. Sechs Prüferkontrollen umfassen einen echten Unit-Widerspruch,
falsche leere Klausel bei SAT, nicht folgende Zwischenklausel, fehlende leere Klausel,
ignorierte Löschung und fehlerhafte Syntax. Bei den drei F-Ablehnungen meldet
Glucose den Widerspruch bereits beim Laden; ein zunächst leerer Solver-Proof genügte
unserem Checker zu Recht nicht. Die explizit ergänzte leere Klausel wurde danach
jeweils direkt durch RUP bestätigt. Das ist ein geprüftes Unit-Propagation-Zertifikat,
keine bloße Übernahme des Solverstatus. CONTROLS.json dokumentiert dies.

## Betriebsbefund und Sicherung

Zweimal stimmten ausgegebene Abschlussmeldungen nicht mit später gelesenen
Checkpointständen überein: zuerst fehlten acht Breiten- und vier F-Datensätze;
nach einer sequentiellen Fortsetzung fehlten nochmals 13 F-Datensätze. Die Ursache
ist unbekannt. Weder Parallelität noch ein bestimmtes Synchronisationssystem sind
als Ursache bewiesen. Ausschließlich fehlende Datensätze wurden nachgerechnet;
alle erhaltenen Resultate wurden übernommen. Die 40000er Kampagne und die
abgeschlossene Präfixrekonstruktion wurden nicht wiederholt.

Die letzte Fortsetzung erfolgte in einem privaten temporären Arbeitsverzeichnis.
Danach wurden alle 17 x 71 Breiten- und F-Einträge sowie 17 Ausschlussbelege
zusammen geprüft, in einem Abschlussbeleg gesichert und als geschlossenes
Datenarchiv übertragen. Alle Dateihashes und Archivbytes wurden verglichen.
CHECKPOINT_DISCREPANCY*.json bewahren den technischen Befund (GC-22).

Erhaltene Objektzeitmessungen: 194,949 CPU-s für Breiten, 160,805 CPU-s für
F-Prüfungen und 66,151 CPU-s für unabhängige Ausschlussmodelle samt RUP-Prüfung.
Das sind Cloud-Messwerte. Fehlende frühere Schlussbuchungen, zusätzliche Kontrollen,
Import-, Sicherungs- und Veröffentlichungsarbeit sind darin nicht vollständig
enthalten. Keine lückenlose Gesamtverbrauchsangabe oder Ryzen-Laufzeitprognose.
Es wurde kein Zeitbudgetabbruch oder Stichprobenlimit eingesetzt.

## Empfohlener nächster Schritt

**Früher erkennen, nicht diese 17 Präfixe tiefer durchsuchen.** Für jedes Präfix die
früheste bereits widersprüchliche Vorstufe entlang seines gespeicherten Pfades
bestimmen. Dafür werden die expliziten Zeilen nach ihrer gespeicherten Reihenfolge
hinzugenommen und notwendige Einzeilenbedingungen geprüft. Es werden keine neuen
Zufallspfade benötigt. Erstmals widersprüchliche Vorstufen sollen wieder konkrete
Belege erhalten; an der unmittelbar vorherigen Stufe muss die behauptete
Einzeilen-Erfüllbarkeit positiv geprüft werden.

Aus diesem Befund kann eine stärkere Vorwärtsprüfung entwickelt werden: Für noch
offene Zeilen nicht nur jede Summengleichung getrennt auf Kapazität prüfen, sondern
ihre Gleichungen gemeinsam. Welche Zeilen wann geprüft werden, muss nach Kosten
und frühestem Widerspruch gewählt werden. Ein vollständiger 71-Zeilen-Test nach
jedem Suchschritt ist noch nicht als wirtschaftlich belegt.

Diese nächste Phase ist noch nicht ausgeführt. Keine neue Großkampagne,
keine Aussage über alle 8105 Roots und keine Änderung der bisherigen
Baumgrößen-Punktschätzungen oder ihres Status INSUFFICIENT_INFORMATION.
