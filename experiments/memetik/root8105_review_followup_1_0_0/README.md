# ROOT8105 Review-Fortsetzung 1.0.0

Neue, eigenständige Version. `reference/` enthält den unveränderten historischen
Filterpiloten. Ausführbare Einstiegspunkte stehen im Hauptverzeichnis; die
Unterprogramme in `reference/` nicht als neue Kampagne starten.

## Enthalten

- `depth2.py`: Relationstabelle, exakte konditionierte Breiten, direkt eingeschränkter Sampler.
- `experiment.py`: eingefrorene3072 Zustände als Falsifikationstest; Vorhersagen je
  Ziel vor dessen Filteraufrufen atomar gespeichert, Formel vor dem gesamten Lauf fixiert.
- `matching.py`: perfekte Matchings allgemeiner Graphen und Stab(a)-Orbitzerlegung.
- `propagation.py`: notwendige Null-/Einsfolgerungen und Matchingprüfung.
- `row_sampler.py`: exakte uniforme notwendige Zeilenvorschläge, keine behauptete F-Projektionsbreite.
- `tree_probe.py`: SAT-Mitgliedschaft, inverse Vorschlagsgewichte, gespeicherte
  Abstiege und ausdrücklich bedingte statistische Auswertung.
- `tree_run.py`: vier Vergleichsarme auf identischem Matchingwald.

Die wissenschaftlichen Ergebnisse und Einschränkungen stehen im beigefügten Bericht.

## Reproduzierbare Befehle für Linux/WSL

Die abgeschlossene Tiefe-2-Prüfung nicht erneut ausführen, außer bei einer expliziten
Reproduktionsprüfung. Die Hauptmessung wird mit einer neuen Laufkennung initialisiert.
Nach Entpacken und Wechsel in dieses Verzeichnis:

```bash
python3 setup.py
.venv/bin/python tree_run.py init work/tree_main --workers 4 --draws-per-cell 10000 --depth 13
.venv/bin/python preflight.py work/tree_main
.venv/bin/python tree_run.py run work/tree_main --draws-per-cell 10000 --depth 13 --phase pilot
```

`setup.py` richtet ausschließlich die eigene `.venv` ein. Auf Zielhardware erst
Vorabprüfung und Ressourcenbefund ansehen.4 Worker sind ein konservativer Ausgangswert,
keine Vorgabe zum Beenden anderer Prozesse. Bei10k/13 entsprechen die Flags dem Default;
für andere Kalibrierungen bei **jedem** tree_run-Aufruf dieselben Werte angeben.
Das Programm prüft Run-, Code- und Modellidentität und verweigert Vermischungen.

Status/Export und kontrollierte Fortsetzung nach explizitem0:

```bash
.venv/bin/python tree_run.py status work/tree_main
.venv/bin/python tree_run.py export work/tree_main
.venv/bin/python tree_run.py resume-after-stop work/tree_main
.venv/bin/python tree_run.py run work/tree_main --phase pilot
```

Zeitbudgetende ist eine Abfrage, kein Stopp. Lauf-/Anfrage-IDs stehen in
`work/tree_main/time_request.json`; Antwort auch während Hintergrundbetrieb:

```bash
.venv/bin/python tree_run.py answer work/tree_main RUN_ID REQUEST_ID 14400
```

14400 bedeutet zusätzliche aggregierte CPU-Sekunden,0 kontrollierten Abbruch.
Bis zur Antwort wird weitergerechnet. Ein Ressourcen-/Integritätsproblem bleibt
unabhängig davon ein Stoppgrund. Nach hartem Rechnerausfall zuerst `inspect-crash`,
dann die dokumentierte Recovery; keine offenen Konten löschen und CPU-Lücken
nicht als null buchen. Abgeschlossene Rootjobs und gespeicherte Abstiege werden übernommen.

## Aussagegrenzen

96 Kalibrierungsabstiege erfüllen das10k-je-Zelle-Kriterium nicht. Selbst40000
Abstiege liefern nur bedingte Aussagen zu den24 ausgewählten Roots und Tiefe13.
Bootstrapintervalle sind keine zertifizierten Schranken. Diese Version startet
keine vollständige Erschöpfung aller8105 Roots.
