# λ-Weglängenprofil 1.0.0 — Ryzen

Umsetzung des freigegebenen Plans V2, Commit ed3193cf07ae29c284153c56f928564e4e80a1d9.
Zwei fixierte Starts W2076/W2077; k=1,2,3,4,6,8,12,16,24,32; je300 Episoden,
insgesamt6000. Jede beginnt am Originalstart. Kein Populationsupdate. Uniforme
Apex/Pivot-Zugwahl und anschließend exakter P-Steilstabstieg mit dem bisherigen
Katalog-Tie-Break. SHA256-Seeds genau gemäß Plan. Keine Isomorphie-Deduplikation
der Beobachtungen; Klassenvielfalt wird separat ausgewiesen.

## Start und Grenzen

ZIP in ein neues Verzeichnis entpacken und `start.py` mit dem vorhandenen
Ryzen-Memetik-Python aufrufen. Erzeugt ausschließlich
`~/conway99_workspace/ryzen_lambda_profile_100_20260927` und verweigert Überschreiben.
Keine Paketinstallation, keine Änderung an alten Radius-/P-Läufen.

Vor dem Profil automatisch: unabhängige Eingabekontrollen, Replay des bekannten
Vier-Zug-Zeugen, positiver Mittelpunktabstieg und Vergleich zweier Episoden mit
Original-Engine einschließlich RNG. Danach je10 Episoden bei k8/k32 und beiden
Starts als Kalibrierung; diese zählen zu den300 Beobachtungen und Suchbudgets.

Jede der20 Zellen hat höchstens3600 verbuchte CPU-Sekunden; insgesamt20 CPU-h.
Hilfsarbeit maximal7200 Sekunden einschließlich Controller und Windows-Helfer;
Vorbereitung/Start reservieren konservativ je10 CPU-Sekunden. Keine Übertragung.
Eine Zelle mit ausgeschöpftem Budget bleibt INCOMPLETE; andere Zellen laufen weiter.
Pro Zelle nur ein Worker; nach bis zu10 Episoden Wechsel ans Ende der Warteschlange.

Bis zu12 Worker, bei Start konservativ auf gemessene freie Kapazität begrenzt,
Worker mit nice10. Bei0 freier Kapazität Pause. Keine fremden Prozesse werden
beendet oder umkonfiguriert. Die Kapazitätsschätzung garantiert keine vollständige
Lasttrennung bei später neu gestarteten Fremdprozessen. Vier Windows-Hoststunden
Gesamtgrenze über geordnete Sitzungen; angehaltene Zeit zwischen Sitzungen zählt
nicht als Rechenlaufzeit. 8GiB RSS/10GiB neue Ausgaben; Pause bei <6GiB verfügbarer
RAM oder <25GiB freiem Linux-/physischem VHDX-Datenträgerplatz.

Windows-Stopwatch und wait4 wie im geprüften Radiuspaket. Kein Linux-Zeitfallback
in Produktion. Alle10 Minuten Status mit abgeschlossenen Episoden, CPU, RSS und
vorsichtiger ETA; Meldungen stehen in controller.log und status.json. Die ETA
nutzt abgeschlossene Episoden, deren Laufzeiten je Länge stark variieren können.

## Wiederaufnahme und Integrität

CLI `run.py`: prepare, launch, status, pause, export; jeweils Laufverzeichnis
als zweites Argument. Für bestehende Läufe immer die eingefrorene Kopie unter
`program/experiments/memetik/lambda_profile_1_0_0/run.py` verwenden.
Eine geordnete Pause speichert nach einem vollständigen Zug. Unterbrochene
Katalogauswertung wird wiederholt; ihre CPU wird erneut und vollständig verbucht.
RNG wird erst bei tatsächlicher Zugwahl verändert. SQLite-Transaktion verknüpft
fertige Episode und nächsten Index atomar. Ein harter Controllerabbruch mit
offenen Reservationsdaten benötigt Diagnose, kein automatisches Budgetreset.

Unaufgelöste Sitzungen, geänderte Quellen, Tasks oder Checkpoints werden abgewiesen.
Ein fehlgeschlagener Worker stoppt die eigenen Prozesse zur Diagnose. Funde ändern
die Stichprobe nicht; nur eine unabhängig geprüfte vollständige SRG beendet früh.

## Ergebnisse und CPU-Interpretation

`RESULT.json`: Abschluss/Budgets; `PROFILE.json`: Zellenprofil;
`jobs/<cell>/episodes.jsonl`: alle fertigen Episoden mit vollständigen Traces;
`work.sqlite`: fertige Episoden und aktuelle zensierte Episode; Receipts liefern
Sitzungs-CPU, Task-/Resultat-/Checkpoint-Hashes. Sämtliche Endpunkte unabhängig
voll bewerten; verbessernde Pfade zusätzlich katalogtreu replayen.

`phase_cpu_seconds` misst Rechenzeit innerhalb Perturbation/Abstieg/Verifikation,
einschließlich wiederholter Katalogauswertung. Dateischreib-, Start- und weitere
Sitzungskosten sind in wait4 enthalten, nicht vollständig diesen Phasen zugeordnet.
Das Profil weist diesen Rest separat aus, einschließlich zensierter Arbeit. Deshalb
ist die ausgewiesene Rückkehr-Phasenzeit kein exakter Anteil der gesamten CPU.
Methodenvergleiche je CPU verwenden immer die vollständige wait4-Abrechnung.

R(k), E(k), Endpunktverteilungen und Blockerfolge sind je Start getrennt auszuwerten.
W<2076 ist globaler Rekord; ein lokaler Treffer kann auch nur L1 verbessern.
Andere Klassen mit W<=Start+2 sind kein bewiesenes Neutralplateau. Bei0 Treffern
gelten Wahrscheinlichkeitsgrenzen nur unter explizitem IID-Modell; unvollständige
Zellen werden nicht als0/300 ausgegeben. Kein automatischer Folgelauf.

## Cloud-Prüfung

`tests.py`: Original-Engine-Trace/RNG, positiver Kontrollpfad, Unterbrechung im
Katalog und nach Zugwahl, tatsächliche Worker mit wait4 und mehreren Sitzungen,
Taskmanipulation, Zellbudget-Isolation. Cloud-Scheduler-Tests verwenden ausdrücklich
eine FakeHost-Testuhr und beweisen nicht die Windows-Interop des Ryzen. Deren
vorhandener Helfer bleibt unverändert und wird beim Start real geprüft.
