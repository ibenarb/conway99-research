# ROOT8105 – gesicherter Fortsetzungsstand: Präfixprüfung abgeschlossen

Zuerst BERICHT.md lesen, danach AGENTS.md, docs/EXPERIMENT_RULES.md,
docs/operations/GLOBAL_CONCLUSIONS.md und docs/CONWAY99_COLLABORATION.md.
Regelstand: d402d52f69d23b7f71ee7a77ff86db958f7e4e2b einschließlich GC-22.

Erledigt: Veröffentlichung der 40000er Auswertung; Rekonstruktion der exakt
17 Endpfade von cell=3; unabhängige direkte Graphbedingungen; gemeinsame
Sternrelaxation mit gespeicherten und direkt geprüften SAT-Belegungen;
Positivkontrolle und neun Negativkontrollen. Ergebnis 17/17 PASS.
Kein Nachweis einer Ergänzung zum vollständigen SRG, kein Rootausschluss.

Die 17 prefix_*.json enthalten explizite Nachbarschaftslisten, Labelabbildung,
Matchingklasse, gespeicherte Propagation und direkt prüfbare Sternbelegung.
RESULTS.json sichert ihre Hashwerte; CONTROLS.json dokumentiert Kontrollen.
Prüfprogramme: tools/memetik/root8105_prefix_audit im Repository.
In einem flachen Auslieferungs-ZIP sind dieselben Programme direkt beigelegt.

Abgeschlossene Audits und Rekonstruktionen nicht erneut ausführen, außer bei
konkreter Unstimmigkeit. Für neue memetische Prüfungen audit_python.py beachten.
Nächste noch nicht ausgeführte Phase: 17 x 71 offene Zielzeilen, lokale
Vorschlagsbreite getrennt von F-zulässiger Breite; siehe BERICHT.md.
Sternzeugen nicht als vorgeschriebene zukünftige Kanten behandeln.
Keine Subagenten ohne ausdrücklichen Auftrag. Veröffentlichung ist autorisiert.
Nach jedem Arbeitspaket dauerhaften Stand sichern. Vor längeren Phasen sinnvoll
Chatwechsel empfehlen, ohne Kenntnis einer zuverlässigen Restkontextanzeige zu behaupten.
