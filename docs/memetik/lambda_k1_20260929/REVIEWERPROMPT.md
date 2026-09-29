# Reviewerauftrag K1

Bitte prüfe die neue K1-Kampagne gegen den Reviewabgleich vom29.09.2026
(b9f215a4fb3a7824d71870743c38d1657b963d43), den ursprünglichen Review auf
reviews/20260929-lambda-repair-120 und die Vorgängerrohdaten.

Arbeite erneut mit den drei Perspektiven Optimierer, Hubschrauber und Maverick.
Trenne konkrete Codefehler, mathematische Widersprüche und Forschungshypothesen.
Prüfe insbesondere die gepaarten LP-/Radiuszellen, D/R-Masken, vollständige
Sternenumeration, Packinggültigkeit und693-Kanten-Gleichheitsfall. Benenne
welche Aussagen nur Solvermeldungen und welche unabhängig geprüft sind.

PLAN.md beschreibt ausdrücklich die Abweichungen von der ersten Skizze:
32 statt bis1000 Archivgründer in A, iterierte Suche statt Populations-P,
heuristische statt optimale Packingprojektion, kein unmöglicher SRG-Sterntest.
Vergleiche diese Entscheidungen mit den Vorschlägen aller sechs Perspektiven.

624CPUh wissenschaftliche Ziele,672CPUh harte Grenze,96h aktive Hostwalltime,
max12 Worker. Ein Timingfehler darf keine CPU verlieren; kleine erklärte Nachläufe
sind lokal. Prüfe insbesondere Pause/Restart, Receipts, globale und lokale Stopps.
Lehren GC-01 bis GC-14 und EXPERIMENT_RULES gehören zur verbindlichen Übergabe.

Zu jeder Kritik: reproduzierbarer kleinster Test, erwartetes Ergebnis, tatsächliches
Ergebnis und Tragweite. Kein vermeintlicher Ausschluss allein aus UNKNOWN oder
kleinem Pilot. Falls Verbesserungen vorgeschlagen werden, benenne primären
Endpunkt, angemessenen Vergleich und den erforderlichen zusätzlichen CPU-Aufwand.
