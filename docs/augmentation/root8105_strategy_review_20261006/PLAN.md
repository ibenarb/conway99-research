# Angepasster Vorschlag: Modellklärung vor Klassen-SAT-Pilot

Stand 06.10.2026. Basis 0e693a355918816731d39e4ca8144b2f91234c5d.
Vorschlag, noch nicht implementiert oder gestartet. Keine Subagenten vorgesehen.
Regeln GC-08/16/17/19/20/22 gelten; fixe Budgets sind Entscheidungspunkte nach GC-19.

## Unmittelbares nächstes Arbeitspaket

1. **Zwei konkrete Modelldifferenzen aufklären.** Für r6682_w290, Ziele 13 und 15,
   eine explizite Lösung von R ohne LD/A gewinnen und direkt prüfen. Danach
   getrennt R+LD und R+LD+A untersuchen. Bei Leerheit einen Beleg sichern;
   verwendete Festlegungen und ihre notwendige Herleitung nachvollziehbar machen.
   Nicht nur eine verletzte Beispielbelegung zeigen: Diese allein beweist nicht,
   dass sämtliche R-Lösungen von den Zusatzbedingungen ausgeschlossen werden.
   Entscheidung: legitime Modellverschärfung oder konkreter Fehlerverdacht.
   Bei einem Fehler zuerst dessen Reichweite untersuchen; keine neuen
   Effizienzschlüsse auf eine fehlerverdächtige Vorschlagsverteilung stützen.
2. **Modellvertrag aufschreiben.** F_0, F_M, F_(M,A), R, R+LD, S, G und N1
   einschließlich fixer/variabler Kanten explizit definieren. N1 enthält
   Randmargen aller H-Zeilen und alle Codegrees mit mindestens einem Endpunkt
   in {a} vereinigt N_H(a), bei geteilten symmetrischen Kantenvariablen. Das
   vorgegebene Matching M bleibt Bestandteil der Klassenidentität. Vollständige
   SRG-Paarbedingungen zweier verbleibender Außenvertices fehlen weiterhin.
3. **Die geplante Diagnose vorab fixieren.** Aus den gespeicherten Abstiegen der
   starken Zelle 3 eine nach den 24 Roots geschichtete Zufallsauswahl mit bekannten
   Inklusionswahrscheinlichkeiten bestimmen. Zunächst ausschließlich Tiefe 2/3
   untersuchen. Stichprobenzahl, Prädikat und Auswertung vor Sichtung festlegen;
   ein Startwert wie 40 je Root ist eine Kalibrierung, kein Nachweis seltener Anteile.
   Die 119 Endpunkte sind getrennte Diagnose-/Kontrollmengen, keine Zusatzmasse
   im gleichen Schätzer. Die 102 numerischen Endpunkte separat behandeln.

Abnahme dieses Pakets: zwei Modelldifferenzen vollständig erklärt oder als Fehler
isoliert; eindeutiger Modellvertrag; veröffentlichter Diagnose- und N1-Kontrollplan.
Keine neuen 40000 Abstiege, kein Vollcensus, keine Wiederholung der alten Audits.

## Danach: zwei begrenzte Untersuchungen, sequentiell orchestriert

**B-früh:** Gewichtete Existenzprüfung offener Zeilen an frühen gespeicherten
Zuständen. R ohne LD und R+LD getrennt ausweisen; keine Übernahme späterer
Propagation aus Tiefe 13 in frühere Zustände. Pro Root linear gewichtet auswerten,
erst danach über Roots mitteln. Kennzahl und Kosten gemeinsam betrachten.
Wenn kein tragfähiges seltenes Ereignis erfasst wird, keinen winzigen lebenden
Restanteil behaupten. Tiefe 2/3 soll eine Entscheidung zur weiteren Diagnose
ermöglichen, keine globale Widerlegung des Zeilenparadigmas vortäuschen.
Eine spätere Bisektion über Tiefen benötigt ein nachgewiesen monotones Prädikat.

**A-vorbereiten:** N1 zunächst mit korrekter Produktkodierung implementieren und
gegen direkte Ganzzahlprüfungen testen. Positive Kontrolle: korrekt gelabeltes
srg(9,4,1,2)-Analogon; feste 17 ausgeschlossene Präfixe als negative Kontrollen.
Unabhängige Prüfung von SAT-Belegungen und externer DRAT/LRAT-Prüfweg vor Produktion.
Kontrollrechnungen sind neue Encoderprüfungen, keine neuen Forschungsbefunde.

Erst anschließend den eigentlichen Klassenpilot freigeben: vorab ausgewählte
Root mit kleiner Matchingorbitzahl plus Root 6682 als bewusst diagnostisch
gewählter Kontrast. Sämtliche Repräsentanten dieser Roots berücksichtigen.
Diese Auswahl ist keine repräsentative Kostenstichprobe über 8105 Roots.
Zuerst Modellgröße, Speicher und Zertifikatskosten auf Zielhardware kalibrieren;
daraus Gesamtbudget, Workerzahl und Prüfreserve bestimmen. Eine CPU-Stunde je
Instanz ist allenfalls ein Dialogpunkt, nicht automatisch ein Abbruch.
Bestehende C2-Prozesse nicht verändern.

SAT bedeutet nur N1-konsistente Klassenbelegung. Sie wird explizit gespeichert
und auf zusätzliche Bedingungen geprüft. UNSAT zählt nur mit bestandenem Beleg.
Ein Root gilt erst als ausgeschlossen, wenn vollständige Fallabdeckung und
zertifizierte UNSAT-Belege aller benötigten Matchingklassen vorliegen.
Überwiegend UNKNOWN motiviert zunächst eine begrenzte Untersuchung der
Zerlegung; nicht sofort eine große Cube-and-Conquer-Kampagne.

## Zurückgestellt

Die isolierte früheste tote Stufe nur der 17 Endpfade ist kein Hauptprojekt mehr.
Sie kann als Diagnose/Kontrolle in B zurückkehren. LP-/Farkas-Anatomie zunächst
an wenigen klar definierten R-Widersprüchen, später nur bei erkennbarem Nutzen.
Keine 601 LP-Tests ohne Trennung der zugrunde liegenden Modelle.
Keine Entfernung des F-Tests allein wegen null Ablehnungen im Hauptlauf.
Keine weiteren reinen Reihenfolge- oder schwachen Importance-Großkampagnen.

Vor dieser neuen Implementierungs-/Pilotphase einen neuen Chat mit dem gesicherten
Stand empfehlen. Das ist eine organisatorische Grenze, keine Behauptung über eine
zuverlässig bekannte verbleibende Kontextlänge.
