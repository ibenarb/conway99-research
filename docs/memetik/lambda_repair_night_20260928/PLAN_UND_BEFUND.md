# Lambda repair 1.2.0: korrigierter Nachtlauf

Ralph genehmigt am 28.09.2026 um 22:06 MESZ eine vollständige längere Wiederholung.

## Befund 1.1.0
Archiv SHA256 63fd94806b2235d6182178c0b066c1274fcf268a17f9cae951d65d3ef2ed5c8f.
Quellen-/Graph-/Score-/Fixkanten-/CPU-Audit in isolierter Auditumgebung reproduziert: PASS_WITH_RECORDED_LOCAL_DEVIATIONS. Kein Beleg vollständiger Planerfüllung.
Walltime 18163.4379649 Sekunden, Abschluss 28.09.2026 13:30 MESZ.
Nach Export 51.9984391442 verbuchte CPU-Stunden einschließlich CLI-Reserven; reine gemeldete Kampagnenabrechnung vorher 51.9484391442 Stunden.
24 Gründer sind paarweise nicht isomorph (pynauty 2.8.8.1). Zusammen mit einem neuen Kandidaten 25 Klassen.
Einziger verbesserter Job 2077_08_s60_defect: W 2139 -> 2127, L1 2516 -> 2498; globaler Bestwert bleibt W2076. IDs mit 2076/2077 bezeichnen Herkunft, nicht zwingend aktuellen W-Wert.
24er: 43 OPTIMAL_UNCERTIFIED, 5 RIGID_BOUNDARY_VERIFIED.
40er: 43 OPTIMAL_UNCERTIFIED, 5 CPU_LIMIT_UNKNOWN.
60er: 48 CPU_LIMIT_UNKNOWN. Keine CP-SAT-Ausschlusszertifikate.

Receipts16/17: 2076_01_s40_defect (60.173183 CPU s) und 2076_01_s60_defect (60.322118 CPU s) nach Kalibrierung durch CPU_TARGET vorzeitig endgültig geschlossen. Ursache: collect() setzte bei Ende eines Versuchs done unabhängig vom verbleibenden Aufgabenbudget. 144/144 war damit keine vollständige Planerfüllung. Der vorherige Audit testete diese Pflicht nicht.

## Neuer Versuch
Gleiche 24 Gründer, 144 Aufgaben, Fenster, Regeln, Seeds, Modell und verifizierende Mathematik. Jede Aufgabe 7200 CPU s einschließlich Aufbau, Kalibrierung und früherer Versuche; frische Konten und keine übernommenen Ergebnisse. Vergleich ist kein exakter deterministischer Laufzeit-Präfixvergleich: OS-Zeitlimits und Neustarts können Suchpfade ändern.
12 Worker, bis 300 gesamte CPU-Stunden inklusive 12 Hilfsstunden, 24 Hoststunden Sicherheitsgrenze. RAM-/Diskgrenzen unverändert. Reserven20 CPU s je Versuch /60 je Aufgabe, vollständig verbucht; globales Budget unverändert bindend.
Erwartung aus 1.1.0 etwa9–12 Hoststunden, falls frühe Abschlüsse ähnlich bleiben. Kein Versprechen: bei stärkerer Ausschöpfung bis zur24h-Grenze möglich.
Erfolgskriterien getrennt: besserer Rekord W<2076; weitere verbesserte Gründer/neue Klassen; mehr gelöste Fenster und informative Schranken. Keine Behauptung einer starken Erfolgsaussicht aus einem Treffer.

## Korrektur und Kontrollen
CPU_TARGET allein beendet nur den Versuch; CPU_LIMIT_UNKNOWN erst bei weniger als5 verbleibenden CPU-Sekunden. Standardversuch erhält gesamtes Restbudget statt implizitem3600s-Limit. Audit prüft Budgetabschluss unabhängig.
Integration verwendet echte CP-SAT-Prozesse, kurze Kalibrierung, Weiterlauf, Pause/Resume, wait4, Integrität und Quellenkorruption. Zielhardware-Scheduler-Preflight beim Start weiterhin verpflichtend; Cloud-FakeHost ist kein Windows-Test.
ETA zieht aktive CPU ab und berücksichtigt längsten verbleibenden Job und reduzierte Slotzahl. Es bleibt eine Budgetprojektion; frühe mathematische Abschlüsse werden nicht vorhergesagt.

## Übergreifende Lehren
GC-02 bestätigt: erklärbare lokale Nachläufe tolerieren und verbuchen.
GC-08: ein begrenzter Treffer ist Mechanismusbeleg, keine Prognose eines Rekorddurchbruchs.
GC-10: Versuchsende, Aufgabenende und Planerfüllung separat modellieren/auditieren.
GC-11: Budgetobergrenze nicht als erwartete Walltime verkaufen; aktive Arbeit und Schlussphase in Projektion berücksichtigen.
