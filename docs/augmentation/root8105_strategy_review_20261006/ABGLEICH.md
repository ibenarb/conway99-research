# Abgleich des Strategiereviews vom 06.10.2026

Geprüfter Forschungsstand: 0e693a355918816731d39e4ca8144b2f91234c5d.
Das Review ist eine Dokumenten-/Quelltextbegutachtung. Der Reviewer hat keine
Rechnungen ausgeführt und keine Zertifikate erneut geprüft. Dieser Abgleich
vergleicht Argumente, Quelltext und gespeicherte Befunde; keine neue Suchrechnung.

## Übernommen und präzisiert

1. **17 feste Präfixe ausgeschlossen, keine Roots ausgeschlossen.** Das Review
   bestätigt die Herleitung und beurteilt den RUP-Prüfer durch Quelltextlektüre
   als korrekt. Das ist fachliche Gegenprüfung, keine zweite Zertifikatsausführung.
   Strategisch sind die 17 Ausschlüsse primär ein zertifizierter Diagnosebefund,
   kein nennenswerter Abtrag eines gewaltigen Suchraums.
2. **601 ist eine Modellzahl.** Das Archiv enthält 19 unabhängige Einzeilentests:
   17 UNSAT, zwei SAT bei r6682_w290, Ziel 13 und 15. Das wurde direkt aus den
   gespeicherten attempts gelesen. Die 601 Nullen gehören zu RowProposal mit
   LD und gespeicherten Festlegungen A, nicht zur nackten Einzeilenrelaxation R.
   Die Kurzfassung wird entsprechend ergänzt. Diese Differenz beweist weder
   einen Fehler noch die Soundness der zusätzlichen Einschränkungen; sie ist
   ein gezielter Prüfauftrag. Eine Lösung des schwächeren Modells darf am stärkeren
   Modell scheitern. Werden alle Lösungen durch notwendige Zusatzbedingungen
   ausgeschlossen, ist die Nullbreite korrekt.
3. **Der F-Test verwarf im Hauptlauf nichts.** Die gespeicherten Abbruchkategorien
   bestätigen null F-Ablehnungen unter 40000 Abstiegen. Die Frontier hat dagegen
   drei belegte F-Ablehnungen. Empirische Redundanz im Hauptlauf rechtfertigt
   deshalb keine ersatzlose Entfernung aus einer exakten Suche.
4. **Numerisch ist strukturiert.** Unter lexikographischen Labels bilden die
   H-Zeilen 0 bis 11 L(0); numerisch wird diese Faser auf Tiefe 12 geschlossen.
   Damit ist der Vergleich strukturell N_H(a) gegen L(0), jeweils unter derselben
   Vorbelegung des Wurzelmatchings, jedoch ohne eigenes vorgegebenes L(0)-Matching.
5. **Die bisherige Auswahl ist zu eng für Strategieentscheidungen.** Die 17
   Endpfade sind Überlebende des alten Verfahrens. Ihre früheste tote Vorstufe
   wäre diagnostisch interessant, aber allein kein belastbares Designkriterium.
6. **Die Richtung ändern.** Keine neue schwach geprüfte Importance-Kampagne und
   keine Optimierung der Zeilenreihenfolge als Hauptziel. SAT-basierte Prüfungen
   ganzer (a,M)-Klassen werden die nächste strategische Hauptoption, deren
   tatsächliche Härte erst ein Pilot zeigen muss.
7. **Sprachkorrektur.** Im alten Bericht ist der Faktor 1,03 Millionen gemeint,
   nicht eine Differenz von 1,03 Millionen Knoten. Der aktuelle Text wird berichtigt.

## Wo das Review selbst Einschränkungen braucht

- Die Aussage, zeilenweise Suche sei grundsätzlich strukturell ausgereizt, geht
  weiter als die Daten. Für die untersuchten schwach beschneidenden Verfahren
  ist eine Vollenumeration nicht vertretbar. Ein wesentlich anderer Generator,
  stärkere Symmetriequotienten oder lernende Einschränkungen sind nicht widerlegt.
  Strategische Zurückstellung ist gerechtfertigt, ein Unmöglichkeitssatz nicht.
- Die bisherigen Kennzahlen schätzen Knoten bis Tiefe 13, keine CPU-Kosten ohne
  Kostenmodell. Dass kein F-Abstieg bestimmte tiefe Ebenen erreichte, macht sie
  nicht zu belastbaren Schätzungen des gesamten Widerlegungsbaums: seltene,
  ungezogene Äste können trotz geringer Wahrscheinlichkeit die Masse dominieren.
- Volle Überlebensrate an frühen Ebenen ist ein gutes Signal, aber kein Ersatz
  für eine Gewichts-/Varianzdiagnose. Ebenso folgt aus 17 toten Endpunkten keine
  belastbare Aussage über die gewichtete Gesamtpopulation. Die rund 16-Prozent-
  Binomialgrenze verlangt ein eigenes gemeinsames Bernoulli-Modell; bloße
  Root-Häufung beweist keine Abhängigkeit, macht dieses Modell aber nicht gültig.
- S enthält tatsächlich gemeinsam gekoppelte Sterne; Prop prüft lokale
  Kapazitäten und Matchingbedingungen. Das sind nicht schlicht identische Tests.
  Der wichtige Punkt des Reviews bleibt richtig: Ein gemeinsam erfüllter Stern
  ersetzt keine gemeinsame Prüfung sämtlicher Gleichungen einer offenen Zeile.
  Implikationsdiagramme müssen dieselben festen Kantenannahmen verwenden.
- N1 ist kein bloßer Aufruf des vorhandenen encode(rows, None): Dort sind rows
  konstante vollständige Bitmasken. Variable Nachbarzeilen erfordern einen neuen
  Encoder für Produkte von Kantenvariablen in Codegrees. Die grobe Variablenzahl
  allein belegt weder Speicherbedarf noch Lösbarkeit.
- Der gewichtete B-Schätzer benötigt einen genau fixierten beschnittenen Baum,
  unveränderte Vorschlagsgewichte und bekannte Auswahlwahrscheinlichkeiten.
  Alle 119 Endpunkte dürfen nicht ungewichtet in eine Stichprobe gemischt werden;
  die 102 numerischen Endpunkte gehören außerdem zu einem anderen Arm.
  R ohne LD, R mit LD und Loc mit A sind getrennte Tests. Bisektion verlangt
  zuvor die Monotonie genau des eingesetzten Prädikats.
- 40 Abstiege pro Root ergeben keine verlässliche Auflösung extrem seltener
  Anteile wie 10^-5. Die Schwellen 10^-3, 10^20, 10^12, 90 Prozent und 15/17 sind
  mögliche vorab gewählte Arbeitsentscheidungen, keine mathematischen oder
  statistisch garantierten Grenzen. Ein billiger früher Test kann grobe
  Erwartungen prüfen; er kann keinen winzigen Restanteil zuverlässig ausschließen.
- Aus der Länge eines RUP-Belegs allein folgt nicht, dass Unit-Propagation der
  Eingabeformel den Widerspruch nicht bereits erkennt. Diese Zusatzbehauptung
  benötigt einen eigenen Test und wird hier nicht übernommen.
- Farkas-Belege nur bei LP-Unzulässigkeit; numerische Solvermeldungen allein
  genügen nicht. Ein gemeinsames Muster müsste exakt rekonstruiert und geprüft
  werden. Hohe Trefferquote allein rechtfertigt keinen Standardfilter ohne
  Kosten-/Nutzenmessung.
- Feste automatische Zeitabbrüche widersprechen GC-19. Eine Stunde darf ein
  Entscheidungspunkt mit Weiterlauf und Verlängerungsdialog sein, kein stiller
  terminaler UNKNOWN-Abschluss. UNKNOWN bei ausdrücklich beendetem oder noch
  offenem Lauf bleibt zulässig. Betriebsaufwand darf vereinfacht werden,
  Integrität, unbekannte Verbrauchslücken und Zustandswahrheit bleiben verbindlich.

## Ergebnis

Die zentrale Kritik ist berechtigt: Wir sollten nicht ausgerechnet die 17
selektierten Endpfade zum alleinigen Entwurfsmaßstab machen. Neuer Vorschlag:
zuerst ein kleines Modellklärungs- und Auswahlpaket, danach eine repräsentativer
angelegte frühe Diagnose und ein kontrollierter N1-Pilot. Die konkrete Abfolge
steht in PLAN.md; keine dieser neuen Rechnungen wurde hier gestartet.
