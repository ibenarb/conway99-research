# Befunde des abgeschlossenen Office-Piloten

Stand: 13. September 2026. Ausschließlich gemessene bzw. überprüfte Aussagen.

Quelle: [vollständige Auswertung](https://github.com/ibenarb/conway99-research/blob/ad09e3a2997809e9832f15845ce783856308d0e5/docs/memetik/OFFICE_PILOT_001_AUSWERTUNG_20260913.md), [Auditdaten](https://github.com/ibenarb/conway99-research/blob/ad09e3a2997809e9832f15845ce783856308d0e5/results/memetik/office_pilot_001_20260912/audit_summary.json). Roharchiv SHA256: 00116bcbea8fb5013338d0a53327254e4651ae594b24844be1841101e6b94dc3. Private Archivierung: conway99-review-exchange, Commit 1e447f7f35124cf7d9f33b46b2a8058bc47a2fde.

- Regulärer Abschluss nach 24 aktiven Pilotstunden; 16.561 Aufgaben einschließlich 96 Kalibrierungen; zehn vollständig selektierte Generationen.
- 2.219 verschiedene beschriftete Graph-/Arm-Zustände unabhängig auf harte Bedingungen und Scores geprüft. Alle CSV-Stichproben und zehn Generationen reproduziert. Kanonische Isomorphiezertifikate aus dem ursprünglichen Lauf übernommen, nicht erneut mit nauty berechnet.
- Kein neuer Gesamtbestwert in W, L1 oder F. λ: bestes F=2836; Ω: bestes F=3926.
- Neuer λ-Zeuge: Linf=2, W=2349, L1=2670, F=3312. Kein behaupteter Weltrekord oder Nachweis eines kürzeren Reparaturabstands.
- Sämtliche elf B-Linien verbessern ihr jeweiliges aktives Kriterium in jeder Normvariante. Beste Gruppenwerte Start→Endpopulation: L1 3512→3304; F 9364→5522; Linf 10→7. Diese Minima können verschiedene Graphen betreffen. Der ursprüngliche B allein hat F=9716.
- Je Norm bleiben acht A-, fünf H_minus- und fünf H_plus-Linien unverändert. Eine von drei H_Z14-Linien verbessert sich.
- Worker-CPU: Ω 55,50 Stunden, λ 7,60 Stunden. Die drei Normvarianten erhalten ungefähr gleich viel CPU; die beiden Arme nicht.
- Geführtes Ω: alle 1020 Versuche am CPU-Limit; 1009 erreichen weniger als acht Störzüge. Zufälliges Ω mit 13–32 geplanten Zügen: 656 von 977 erreichen nicht 13.
- Ω-Cross-over: 1020 Versuche, 30 übernahmefähige Rückgaben. Eine B-Rückgabe bei F=4980 entspricht laut kanonischem Laufzertifikat dem vorhandenen H_minus-Gründer. Rückgaben sind nicht gleichbedeutend mit neuen Populationsklassen.
- Ω und λ sind unterschiedliche Teilbedingungssysteme. B ist Ω-gültig, verletzt aber 460 λ-Kantenbedingungen.
