# Conway99 C2 Profile46Cert 1.0.0 — Office

Stand: 26.09.2026. Umsetzung des angenommenen ersten Fortsetzungsblocks.

## Ziel und Aussagegrenze

Zunächst den beigefügten Reviewer-Beweis gegen die byteidentische C4-Formel mit dem
gepinnten Office-Prüfer verifizieren. Danach die 2.170 vollständigen Pfeilbelegungen
von profile_46 einzeln mit CaDiCaL lösen, DRAT erzeugen und unabhängig prüfen.
Nur 2.170/2.170 geprüfte Zertifikate plus vollständige Fallabdeckung führen zu
PROFILE46_UNSAT_VERIFIED. Dies schließt unter der vereinbarten Prioritätsregel den
Resttyp d=4 aus. Es ist kein vollständiger C2-Ausschluss; d=0,1,2,3 bleiben offen.

Der Transfer des C4-Lemmas und die Reduktion auf S7-Bahnen sind explizite semantische
Metaschritte auf E1–E3. Eine Permutationsinvarianz der Totalizer-Hilfsvariablen wird
nicht behauptet. Die Vollständigkeit der ursprünglichen C2-Kodierung bleibt eine
Voraussetzung der mathematischen Schlussfolgerung.

## Vorbereitung und Start

Das ausführbare PYZ installiert unveränderliche Quellen in
~/conway99_workspace/Conway99_C2_Profile46Cert_1.0.0.

--prepare startet im Hintergrund nur die Vorbereitung: Originaldatei- und
Werkzeughashes, positive und negative Prüferkontrolle, SAT-/UNSAT-Solverkontrolle,
CPU-Abschaltkontrolle, Rahmengruppenprüfung, beschriftete Zählung,
unabhängige Bahnprüfung und C4-Beweisprüfung. Erwartet werden
FULLCERT_PREFLIGHT_PASS und FULLCERT_RESULT mit Status PREPARED.

--run startet bzw. setzt anschließend die Einzelzertifizierung im Hintergrund fort.
Es führt vorher dieselben Prüfungen aus, wobei gültige, hashgebundene Ergebnisse
wiederverwendet werden. Konkrete Startbefehle werden im Chat einzeln angegeben.

Voraussetzungen: Linux/WSL, Python 3, gcc und die vorhandene Installation
Conway99_C2_AnchorProfile_1.0.0 mit Basis, Variablenabbildung, profile_46 und drat-trim;
CaDiCaL unter ~/conway99_workspace/cadical_office_2.2.1/build/cadical.
Alle Originalformeln und Werkzeuge werden ausschließlich gelesen. Keine Downloads,
keine Paketinstallation, keine Änderungen an Memetik oder früheren Experimenten.
Der vollständige Reviewer-C4-Beweis ist im Paket enthalten.

## Fallabdeckung

count46.c stammt unverändert aus dem Reviewer-Prüfsatz; sein Algorithmus wurde geprüft.
Er zählt 10.690.440 beschriftete C4-freie Pfeilgraphen mit Ausgangsgraden in {4,6}:
10.448.730 ohne d=6 und 241.710 mit genau einer d=6-Klasse.
coverage.py prüft jeden gelieferten Vertreter und jede Pfeil-Unit gegen die ursprüngliche
Variablennummerierung. Eine vom Reviewer-C-Programm unabhängige Kanonisierung prüft
Nichtisomorphie und Automorphismenzahlen. Die Summe der Bahngrößen 5040/|Aut| stimmt
mit der beschrifteten Zählung überein. Das ergibt genau 2.170 Bahnen.

## Ausführung, Grenzen und Wiederaufnahme

- Insgesamt acht CPU-Stunden (28.800 s), kumulativ über Vorbereitung und Neustarts.
  Erfasst werden Controller-CPU, geerntete Kindprozess-CPU und laufende /proc-Samples.
  Bei einem harten Controllerabbruch wird zusätzlich eine konservative Reserve pro
  zuletzt aktivem Kind angerechnet. Kleine Überschreitungen durch Abtastung,
  Prozessbeendigung und abschließenden Export sind möglich.
- Höchstens drei gleichzeitig laufende Solver oder Prüfer, nice 10. Pro Solver
  höchstens 600 CPU-s, pro Würfel-Prüfer 1.800 CPU-s. Timeouts bleiben offen und
  werden nicht in einer automatischen Wiederholungsschleife erneut gestartet.
- Die ersten 40 Fälle bestehen aus den 20 langsamsten Reviewer-Fällen und 20
  reproduzierbar zufällig gezogenen übrigen Fällen. Danach geht der Lauf automatisch
  weiter, solange Budget und Ressourcen genügen. Die Pilotzeit ist keine unverzerrte
  Hochrechnung für den Gesamtlauf.
- FULLCERT_STATUS etwa alle zehn Minuten im controller.log, mit Fallzahlen,
  Restbudget, REALTIME, MONOTONIC und MONOTONIC_RAW. Angegeben wird eine Prognose
  zur Budgetausschöpfung, keine garantierte Fertigstellungszeit. Kein Faktor 1,10.
- Schutzgrenzen: mindestens 384 MiB verfügbares Linux-RAM, 25 GiB freier Linux-Speicher,
  unter WSL zusätzlich 35 GiB frei auf Windows C:. Ein weiterer Prozess startet nur
  bei mehr als 1 GiB verfügbarem RAM, außer wenn noch kein Prozess aktiv ist.
- Eine Dateisperre verhindert zwei Controller derselben Installation.
- Wiederaufnahme verwendet abgeschlossene Prüfergebnisse; unterbrochene Aufgaben
  werden mit verbleibendem Gesamtbudget neu begonnen. Solver-Lernzustände werden
  nicht fortgesetzt. Ein erschöpftes Gesamtbudget wird niemals automatisch erhöht.
- Unerwartetes SAT wird als 99-Knoten-Graph samt Involution unabhängig geprüft und
  beendet die Suche. Falsche Zertifikate oder Hashabweichungen stoppen den Lauf.

## Ergebnisdateien

work/round.json: Fallzustände und genaue Aussage.
work/preflight.json, coverage.json, c4_certificate.json: Beweisvoraussetzungen.
work/budget.json: kumulative CPU-Abrechnung.
work/certificates/cube_NNNN: Formelbeschreibung und geprüfter komprimierter DRAT-Beweis.
work/operations: vollständige Solver-/Prüferlogs, Startdaten und Ergebnisbelege.

Geprüfte Beweise werden verlustfrei komprimiert und per Dekompression und SHA256
kontrolliert. Erst nach dauerhaft gespeichertem Zertifikat wird die rohe Kopie entfernt.
Große Würfel-CNFs werden nach erfolgreicher Prüfung gelöscht; sie sind aus der gepinnten
profile_46-Formel und den 42 dokumentierten Units bytegenau wiederherstellbar.
Offene Beweise und CNFs bleiben erhalten.

C2_Profile46Cert_1.0.0_results.tar.gz ist ein kompakter Berichtsexport mit Quellen,
Metadaten und Logs. Er enthält ausdrücklich nicht alle großen Beweisdateien.
Diese verbleiben auf Office; ihre Hashes und Pfade stehen in round.json.

## Lokale Prüfung dieses Pakets

VALIDATION.json dokumentiert reproduzierte Formeln, Fallabdeckung und die Tests der
Laufsteuerung. Die Ablauf-Tests verwenden simulierte Werkzeuge und liefern keine
mathematischen UNSAT-Belege. Der echte gepinnte Office-Solver und Office-Prüfer stehen
in der Erstellungsumgebung nicht zur Verfügung; ihre Kontrollen und die echte Prüfung
des mitgelieferten C4-Beweises sind deshalb zwingender Teil von --prepare auf Office.

## Weitere Phasen

Die Untersuchung von profile_346 mit mindestens einer d=3-Klasse und der Pilot für
den pfeilarmen Bereich sind nicht Teil dieses Pakets. Sie folgen nach Auswertung dieses
Blocks. Der frühere breite Plan mit 54 Pfeiltests wird nicht gestartet.
