# ROOT8105 Modelllücke: Paket A abgeschlossen

Basis und Regeln: 84180ad8bffe6905b8384e4acf889879b85a3fa9.
Arbeitsbranch: work/root8105-review-followup-20261006.
Keine neuen Abstiege; keine Wiederholung der alten Frontier; keine Rootausschlüsse.

| Ziel in r6682_w290 | R | R+LD | R+LD+A |
| --- | --- | --- | --- |
| 13 | SAT, direkter Zeuge geprüft | SAT, direkter Zeuge geprüft | RUP-verifiziert UNSAT |
| 15 | SAT, direkter Zeuge geprüft | SAT, direkter Zeuge geprüft | RUP-verifiziert UNSAT |

Die notwendige zusätzliche Propagation A erklärt beide Nullbreiten. LD allein
reicht hier nicht. Das ist eine gezielte Klärung, kein allgemeiner
Vollständigkeitsbeweis des historischen RowProposal-Programms.
Alle 1127 gespeicherten A-Einträge wurden unabhängig aus den vollständigen
Präfixzeilen, LD-Nullen und Sättigung notwendiger Grad-, Rand- und Paargleichungen
hergeleitet. Keine gespeicherten A-Werte und keine Sternzeugen dienten als Prämissen.
Das ursprüngliche Wurzelmatching ist bereits durch die 13 vollständigen Zeilen
festgelegt; diese Prüfung benötigt somit keine zusätzlichen Matchingannahmen.

Die beiden LD-Regeln sind getrennt implementiert und mit Ursprüngen versehen:
1. Für gebauten Mittelpunkt u und Nachbar v mit gemeinsamem Randlabel ist
   der H-Codegree null: 2-1-1=0. Alle Summanden sind daher null.
2. Zwei H-Nachbarn eines gebauten Mittelpunktes mit gemeinsamem Randlabel
   können nicht benachbart sein: Sie haben bereits zwei gemeinsame Nachbarn,
   während eine Kante lambda=1 verlangen würde.

R+LD bezeichnet hier die auf die Zielzeile projizierten Nullen beider Regeln.
R+LD+A übernimmt nur die A-Einträge, die diese Zielzeile berühren. Andere offene
Zeilen werden dabei nicht gleichzeitig gelöst. Ihre notwendigen Gleichungen
begründen jedoch die vorgelagerte Herleitung von A.

Ein R-Zeuge für Ziel13 verletzt A[13,74]=0; für Ziel15 verletzt der gespeicherte
Zeuge A[15,25]=A[15,38]=0. Entscheidend sind nicht diese Beispiele, sondern die
beiden separat geprüften UNSAT-Zertifikate für sämtliche R+LD+A-Lösungen.

EVIDENCE.zip enthält vier vollständige SAT-Belegungen, direkte Prüfergebnisse,
sechs CNFs, zwei RUP-Belege, die Herleitung aller Festlegungen und FINAL_RECEIPT
mit Einzeldateihashes. SUMMARY.json enthält den Abschlussbeleg auch außerhalb
des Archivs. Zertifikate: 1018 bzw. 749 geprüfte RUP-Additionen einschließlich
explizitem abschließendem Leerclause-Test. Kein Beweisassistent verwendet.

Messung: insgesamt 19,179 CPU-Sekunden für die gezielte Cloud-Prüfung inklusive
A-Herleitung und Zertifikatsprüfer. Keine Ryzen-Prognose. Kein Zeitbudgetabbruch.
Positivkontrollen: vier direkt geprüfte Zeugen; jeweils ein absichtlich um eine
Kante beschädigter Zeuge wurde abgewiesen. Die bereits veröffentlichten
RUP-Prüferkontrollen wurden nicht wiederholt.

Reproduktion: tools/memetik/root8105_model_gap/check_gap.py mit --repo und einem
neuen --output-Verzeichnis ausführen. Zuvor audit_python.py verwenden.
Umgebung: Python3.12, pynauty2.8.8.1, python-sat1.9.dev15, numpy2.5.3.
Der erste neue Audit-Interpreter enthielt noch kein pynauty; der Helfer richtete
es ein. SAT fehlte auch im alten Interpreter. Abhängigkeiten wurden ausschließlich
im neuen isolierten Cloud-Interpreter ergänzt. Keine Nutzerprozesse verändert.

Nächste Voraussetzungen: Modellvertrag und vorab festgelegte frühe Diagnose;
danach kontrollierter N1-Encoder. GC-08/16/17/19/20/22 beachten.
