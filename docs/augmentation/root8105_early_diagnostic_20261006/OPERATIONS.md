# Betriebsbefunde

Die96er-Kalibrierung wurde vollständig abgeschlossen und vor Erweiterung als
CALIBRATION_96.zip gesichert. Erste Vorbereitung des960er-Laufs scheiterte an
einem Klammerfehler in der neu eingefügten Zusammenfassung kompakter Zustände.
Syntaxfehler trat vor Rechnungsbeginn auf; korrigiert, keine Suchergebnisse verloren.

Der erste960er-Aufruf zeigte wachsende CPU-Kosten je Pfad. In python-sat1.9.dev15
reserviert CNF.append/extend zusätzlich IDs im globalen Formula-Pool.
IDPool.occupy sammelt und sortiert Intervalle; wiederholte unabhängige CNFs
vergrößern diesen nicht benötigten globalen Zustand. Eine Kontrollfolge von
3x200 Encodierungen hatte200/400/600 Intervalle. Nach Austausch des globalen
Pools blieb eine neue CNF in Variablenzahl und Klauselfolge identisch.
Alle eigentlichen Modelle verwenden eigene explizite IDPools.

Technische Unterbrechung des Cloud-Aufrufs, kein Zeitbudgetende. Direkter
SIGINT-Versuch über /proc-PID schlug mit ProcessLookupError fehl; danach
Unterbrechung über die Exec-Sitzung (Exit130).247 vollständige Pfaddateien
blieben erhalten. CPU-Probe vor Unterbrechung:264,8 CPU-s; dies ist KEIN
wait4-Endbeleg. Schlussverbrauch dieser Sitzung fehlt und wird nicht als null
behandelt. Der zuvor vollständig abgeschlossene96er-Aufruf bleibt separat.
Alle vollständigen Dateien wurden gehasht; nur der unvollständige Pfad wurde
bei Fortsetzung neu begonnen. Keine alten Audits oder Kampagnen wiederholt.

Korrektur: vor jedem unabhängigen Zielmodell Formula.attach_vpool(IDPool()).
Keine Änderung lokaler Variablenpools, Gleichungen, Klauseln oder SAT-Strategie.
Fortsetzung speichert kompakte Auswertungsdaten im RAM; vollständige Zeugen
stehen weiterhin in den Ergebnisdateien. Proben danach etwa0,4CPU-s je Pfad;
keine behauptete konstante Speicherbelegung oder Ryzen-Prognose.

CALIBRATION_SUMMARY und endgültiger Abschlussbeleg benennen verschiedene
Aufrufe. path_cpu_s summiert die übernommenen abgeschlossenen Pfadmessungen;
invocation_cpu_s misst nur den letzten Aufruf. Beide Größen sind keine
lückenlose Gesamtabrechnung einschließlich technischem Fehlversuch, Import,
Sicherung und Veröffentlichung. Vollständige Beweis-/Ergebnisintegrität bleibt
von dieser offen ausgewiesenen Betriebsabrechnungslücke getrennt.
