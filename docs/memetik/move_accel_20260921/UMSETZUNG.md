# Beschleunigung der Änderungserzeugung nach dem Ryzen-Pilot

## Anlass und geprüfte Ausgangsdaten

Auftrag Ralph: Engpass konkret untersuchen, Optimierung implementieren und
begrenzt auf Ryzen prüfen. Keine 48-Stunden-Hauptkampagne automatisch starten.

Eingang `comparison_verified.tar.gz`, SHA256
`ada91cfa86f4d2ba44e26c6066197957668b211cfdea86d7637ad79bd0f64024`.
886 Archivdateien, davon 885 im Inhaltsmanifest; alle Inhaltsprüfsummen passen.
144 vollständige Vergleichsaufträge, tatsächlich 143.9219716878 Worker-CPU-Stunden.
Grad, Omega-Randbedingungen bzw. Lambda-Kantenbedingung und W/L1/F/Linf/Nmax
wurden aus Nachbarschaftsmengen unabhängig nachgerechnet. Die 50 verschiedenen
beschrifteten Gründer-/Endpunktgraphen bestehen diese Prüfungen. Endpunkt-
CPU-Quittungen: 3598.022065 bis 3598.111739 Sekunden; Bestkurven monoton,
Anfangswerte stimmen mit den jeweiligen Gründerbesten überein.

A1-Siege / Bindungen / A0-Siege in neun Paaren:

| Arm | W,L1 | L1 | F | Linf,Nmax,L1 |
|---|---|---|---|---|
| Omega | 3/4/2 | 4/4/1 | 0/5/4 | 1/7/1 |
| Lambda | 1/8/0 | 0/9/0 | 0/9/0 | 0/1/8 |

Die präregistrierte einseitige A1-Überlegenheitsprüfung liefert nach Holm keine
A1-Auswahl. Das ist kein universeller Nachweis der A0-Überlegenheit.
Alle 72 gespeicherten Omega-Laufbesten haben Herkunft F02, alle 72 Lambda-
Laufbesten HoG. Das schließt andere Familien nicht mathematisch aus.
91–93 % der erfassten Teilkosten betreffen die Erzeugung gültiger Änderungen.

## Was konkret geändert wurde

Neue, isolierte Implementierung `experiments/memetik/move_accel_0_1_0`.
Die Dateien der 0.4.1-Baseline bleiben unverändert.

- Omega: Nachbarschaften und Komplemente einmal je Strom vorberechnen.
  Bei einer rechten alternierenden Länge r werden r/2 positive und r/2
  negative Positionen benötigt. Kompatibilitätsmengen werden nur kleiner;
  unterschreitet eine Seite diese Grenze, ist der linke Vektor unmöglich.
  Deshalb früher Abbruch vor Dictionary- und Kantenlistenerzeugung.
- Apex: disjunkte Dreiecke und fehlende neue Kanten mit Bitmasken prüfen;
  sechs geänderte Nachbarschaften direkt durch XOR bestimmen. Sortierte
  Kantenlisten erst für Kandidaten aufbauen, die die neuen Dreieckszahlen
  erfüllen. Die vollständige bisherige Lambda-Prüfung bleibt erhalten.
- Rotation: Paar-Matchingtests je Zustand zwischenspeichern, unvereinbare
  Basen vor der dritten Schleife ausscheiden. Cache wird bei jedem neuen
  Strom verworfen; keine Wiederverwendung über einen geänderten Graphen.

Familiengewichte, vollständiger Katalog, Reihenfolge der gültigen Änderungen,
Deduplikation und RNG-Verbrauch bleiben gleich. Vollständige Ströme sind
identisch; bei CPU-gebundener Suche werden natürlich mehr Änderungen innerhalb
der Frist möglich. Somit sind zeitbegrenzte Suchtrajektorien nicht identisch.
Kein C++-Compiler, keine neue Python-Abhängigkeit erforderlich.

## Kontrollen und Grenzen der Geschwindigkeitsaussage

12 echte Graphzustände: ein Gründer jeder vorhandenen Herkunftsfamilie sowie
vier Pilot-Endpunkte. Zwei feste Seeds, insgesamt 62 vollständige
Familienvergleiche: Folgen und abschließende RNG-Zustände identisch. Alle
resultierenden Änderungen hart validiert, zusätzlich unabhängig geprüfte
Stichproben. Gemischte gewichtete MoveSource-Ströme ebenfalls verglichen.
Details in DIFFERENTIAL_CONTROLS.json.

Gemessene Median-Beschleunigung warmer vollständiger Ströme in der
Entwicklungsumgebung: 4x4 1.28x, 4x6 2.45x, 6x6 2.01x, Apex 3.71x,
Rotation 6.44x. Keine Ryzen-Werte, keine End-to-End-Prognose.
Die getesteten echten Zustände hatten keine 6x6-/Rotationsänderungen; dort
bedeutet die Beschleunigung schnellere Erkennung erschöpfter Ströme.
Zusätzliche positive Kernelfixtures prüfen echte Rotation am 9-Knoten-Rookgraph
und ein gepflanztes 6x6-Signrechteck samt geändertem Folgezustand. Das sind
Kontrollgraphen, keine neuen 99-Knoten-Gründer.

Ein verkürzter Integrationstest friert das Bundle ein, startet beide Backends
als echte Kindprozesse, prüft die Graphen und wait4-Quittungen und bestätigt,
dass abgeschlossene Jobs beim erneuten Aufruf nicht neu gestartet werden.
Bei dessen künstlichem 5-s-Limit waren inklusive Start/Abschluss etwa 0.03 s
Mehrverbrauch über vier Jobs zu sehen; dieser Test belegt nicht die
Produktions-CPU-Grenze. Im echten Benchmark gilt die unveränderte interne
2-s-Abschlussreserve bei 300 s, und die Auswertung verwirft jede Überschreitung.

Beim ersten Kontrolllauf war die Testzuordnung über das Zeichen x fehlerhaft
(apex enthält ebenfalls x). Die Zuordnung wurde auf explizite Familiennamen
korrigiert und die vollständigen Kontrollen danach erfolgreich wiederholt.

## Begrenzter Ryzen-Versuch

Referenz ist das unveränderte eingefrorene Bundle des abgeschlossenen Piloten,
nicht eine spätere Git-Version. Vorbereitung prüft dessen Datei-Fingerprints,
Python-/Paketstand und Manifesthash. Neue Optimierung und Referenz werden
zusammen in einem neuen eigenen Laufverzeichnis eingefroren.

1. Vorgeschaltete vollständige differentielle Kontrollen, bis 600 CPU-Sekunden.
   Jeder Fehler verhindert den Leistungsvergleich.
2. 2 Arme x 4 Ziele x 3 gepaarte neue Seeds x 2 Backends = 48 Jobs.
3. Je Job 300 Worker-CPU-Sekunden: zusammen höchstens 4 CPU-Stunden.
   Die Kontrollen sind getrennt budgetiert (höchstens 1/6 CPU-Stunde).
4. Beide Backends verwenden A0, dieselben originalen 16 Gründer je Arm,
   dieselben Operatorgewichte und Episodenlimits. Keine Gründerverbesserung
   gleichzeitig einschleusen. Reihenfolge Referenz/schnell alterniert.
5. 18 Worker, unveränderte Linux- und physische Windows-Speicherwächter,
   nur eigene Kindprozesse. Alte Pilotdaten, Office und fremde Prozesse
   werden nicht verändert. Kalibrierte Hardware wird weiter genutzt.
6. Verbesserungszeilen tragen zusätzlich reference/fast; fünf Minuten
   Anlaufphase, zehnminütiger Status. Aggregierte Baseline-Statusbestwerte
   mischen Backends; der Endbericht und die Ereigniskennzeichnungen trennen sie.
7. Prüfung der Endpunktgraphen, CPU-Belege und Kurven. Berichtet werden
   Episodenquotienten und gepaarte Zielwerte. Drei Seeds sind ein technischer
   Vorvergleich, kein ausreichend bestätigter wissenschaftlicher Siegerentscheid.

Erwartete Wandzeit etwa 15–25 Minuten, abhängig von Kontrollen und Auslastung;
keine Garantie. Nach Abschluss stoppt der Controller. Erst mit diesem Ergebnis
wird über Übernahme und konkrete Ausgestaltung der Hauptkampagne entschieden.
Keine Änderung der Laufzeit oder Erfolgsschwellen während des Versuchs.
