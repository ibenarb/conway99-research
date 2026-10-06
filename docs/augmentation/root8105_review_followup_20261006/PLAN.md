# Angepasster Fortsetzungsplan v1

Regelbasis: `40c0050af19353fd9c9d1a203e58f5df07636229`, insbesondere GC-01/08/10/11/15/16/18/19/20/21; GC-22 wird mit dieser Fortsetzung ergänzt.
C2 und eingefrorene Vorläuferpakete bleiben unberührt.

1. **Abgeschlossen:** Reviewarchiv, Quellenabgleich und Tiefe-2-Beweis.
2. **Abgeschlossen:**3072 vorregistrierte Zustände als Falsifikationstest;
  48 exakte eingeschränkte Breiten; Matchingklassen der24 ausgewählten Roots.
3. **Implementiert:** vier Vergleichsarme mit gleicher Matchinggrundmenge:
   numerische Reihenfolge / Nachbarschaft zuerst × F / F mit Vorwärtsprüfung.
   Letztere nutzt Grad-, Rand- und Paargleichungen, LD-Nullen und allgemeine
   perfekte Matchings. Keine Annahme einer nichttrivialen Graphautomorphismusgruppe.
4. **Abgeschlossene Kalibrierung:** je ein vollständiger Abstieg pro Root und Zelle,
   also96 Abstiege bis höchstens13 gebauten Zeilen. Dies prüft Kosten und Pfade,
   erfüllt ausdrücklich nicht das Mindestmaß der statistischen Hauptmessung.
5. **Vorbereitete, noch nicht gestartete Hauptmessung:** mindestens10000 Abstiege pro
   Zelle, insgesamt40000, auf dieselben24 Roots nahezu gleich verteilt. Feste Seeds;
   keine adaptive Nachselektion erfolgreicher Wege. Jeder beendete Abstieg wird
   atomar mit Root-/Codeidentität gespeichert und bei Wiederaufnahme übernommen.
   Abbrüche, Solver-UNKNOWN und nicht abgeschlossene Abstiege sind keine Nullen.
6. **Auswertung:** Mittel der linearen Gewichte innerhalb jeder Root, dann Mittel
   der24 Rootmittel, erst danach log10. Kumulierte Knoten bis13 und Überleben je
   Tiefe getrennt. Bootstrap innerhalb der festen Roots, gepaarte Ziehungen beim
   Vergleich der Extremarme. Effektive Stichprobengröße, größter Gewichtsanteil
   und Zahl positiver Endgewichte berichten. Bei weniger als100 positiven
   Endgewichten oder ESS<100 keine belastbare Vergleichsfreigabe; diese Schwellen
   sind Diagnosegates, keine Garantie gegen schwere Ränder.
7. **Entscheidung:** Ein Wechsel zur neuen Konfiguration kommt in Betracht, wenn
   die obere Grenze des explorativen gepaarten95%-Verhältnisintervalls für
   neue/starke gegen alte/F-Konfiguration höchstens0,01 beträgt. Zusätzlich müssen
   die Varianzdiagnosen tragfähig sein. Weitere Zellen zeigen, welcher Faktor hilft.
   Ein intervallloser oder zensierter Lauf bleibt unentschieden.
8. **Globale Machbarkeit separat:** Rootdesign mit bekannten positiven
   Inklusionswahrscheinlichkeiten, weitere Tiefen und Kosten auf Zielhardware.
   Erst danach Gesamtbudgetentscheidung. Überschreitung um drei Größenordnungen
   kann eine strategische Umstellung motivieren, ist auf Basis von Tiefe13/24Roots
   aber noch keine belastbare Aussage. Dann zertifizierbare einzelne(a,M)-Klassen
   priorisieren; keine UNSAT-Behauptung aus einem Stichproben-Nullbefund.

## Betrieb

Das Paket nutzt den bereits getesteten Controller mit CPU-Endabrechnung, isolierten
Workerfehlern, Ressourcenüberwachung und GC-19-Verlängerungsdialog. Defaultschwelle:
14400 aggregierte CPU-Sekunden; dies ist eine Abfrageschwelle, kein Zeitabbruch.
Bis zur Antwort wird weitergerechnet. Hintergrundantwort:
`tree_run.py answer RUN RUN_ID REQUEST_ID SEKUNDEN` (mit denselben Planparametern).
0 beendet kontrolliert; positive Sekunden werden einmalig aufgeschlagen.

Die Cloud-Kontrollen ersetzen keine Windows-/WSL-Vorabprüfung. Vor einem Ryzenlauf
ist `preflight.py` im dortigen neuen Laufverzeichnis erforderlich. Workerzahl nach
RAM und Kalibrierung wählen; laufende C2-Rechnungen nicht beenden.

Vor Start: neue Betriebsversion1.0.1 verwenden. Die Kalibrierung1.0.0 nicht
aus ihrem widersprüchlichen SQLite-Endstand fortsetzen. Abschlussbeleg und
Zielhardware prüfen; GC-22/ABSCHLUSS_ABWEICHUNG.md beachten.
