# Abschlussabgleich der Cloud-Kalibrierung

Die Kalibrierung hat96 abgeschlossene Abstiege. Ihr terminaler Export meldet96
übernommene Ergebnisse und293,124005197CPU-s einschließlich Exportanteil. Das
Controller-Endlog meldet292,857922710CPU-s vor diesem Exportanteil. Diese beiden
Zahlen widersprechen sich nicht.

Die später gelesene SQLite-Datei enthält dagegen nur95 Ergebnisdatensätze und einen
offenen letzten Versuch. Zwei Worker-Ausgabedateien zeigen ebenfalls ältere
RUNNING-Stände, obwohl deren vollständige Ergebnisse schon in SQLite übernommen
sind. Die Ursache dieser nicht zusammenpassenden Persistenzstände ist ungeklärt;
ein Synchronisations-/Snapshot-Effekt der Cloud ist eine Vermutung, kein bewiesener
Code- oder WSL-Fehler. Während des Hintergrundlaufs wurden Statusabfragen aus
anderen Werkzeugaufrufen durchgeführt. Der Vorfall wird nicht durch Wiederholung
der mathematischen Abstiege verdeckt.

## Gesicherter Ergebnisstand

-95 vollständige, mit Digest gespeicherte Controllerergebnisse sind erhalten.
-Das fehlende96.Ergebnis liegt als vollständige Worker-Enddatei mit passender
  Input-, Run-, Root-, Modell- und Codeidentität vor.
-Alle96 Ergebnisse wurden gegen ihre Eingabespezifikationen geprüft. Der daraus
  in einer separaten In-Memory-Datenbank erzeugte statistische Export stimmt in
  sämtlichen Zellen, Vergleichsstatus und Gesamtstatus mit dem terminalen Export
  überein. Siehe TREE_VERIFIED_RESULTS.json und audit_review_followup.py.
-Die alte SQLite-Datei bleibt unverändert. Sie ist **kein freigegebener
  Wiederaufnahmestand**. Es wird kein erfundener Endzeitpunkt oder Einzel-wait4-Beleg
  ergänzt. Die293,124005197CPU-s sind ein berichteter Gesamtwert; der persistierte
  relationale Endledger ist nicht unabhängig geschlossen bestätigt.

Der Tiefe-2-Lauf ist hiervon zu unterscheiden: Seine25 Jobs und Konten sind
konsistent geschlossen; Endexport192,891001831CPU-s, vor Export192,476703754CPU-s.

## Änderung1.0.1

Die mathematischen Quellen und Ergebnisse bleiben1.0.0 zugeordnet. Die neue
Betriebsversion1.0.1 schreibt zusätzlich `final_receipt.json` als **ein** atomares
Dokument: sämtliche Resultate, Digests, Rootzustände, Versuche, Sitzungen,
Codeidentität und Zusammenfassung. Der Controller gibt dessen SHA256 aus.
Ein Regressionstest erhält den versiegelten Ergebnisstand trotz nachträglich
veraltetem/gelöschtem Live-Datenbankinhalt; eine manipulierte Ergebniszahl wird
abgewiesen. Das ergänzt die bisherigen Recoverykontrollen, ersetzt sie nicht.

Diese Änderung macht die Abschlussbelege weniger abhängig von voneinander
abweichenden Dateien. Sie beweist nicht, dass ein unbekannter Synchronisationsfehler
niemals auch die letzte atomare Datei verlieren kann. Auf Zielhardware bleiben
Vorabprüfung, lokales Laufverzeichnis und Prüfung des vollständigen Abschlussbelegs
Pflicht. Eine vollständige40k-Kampagne wurde in dieser Cloud noch nicht gestartet.
