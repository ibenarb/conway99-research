# Office-Pilot 0.2.0: abgeschlossene Auswertung

Stand: 13. September 2026. Eingang: vollständiger pilot-001-Lauf vom 11.–12. September.
Archiv-SHA256: `00116bcbea8fb5013338d0a53327254e4651ae594b24844be1841101e6b94dc3`.

## Ergebnis

Kein neuer Bestwert in W, L1 oder Fehlerquadratsumme über den jeweiligen gesamten Arm. Ein neuer λ-Kandidat erreicht jedoch **Linf=2 statt 3**. Alle elf B-Linien verbessern ihr jeweils aktives Auswahlkriterium. Große Teile des übrigen Ω-Bestands bleiben unverändert. Der stärkste praktische Befund ist, dass viele geplante längere Ω-Ausflüge wegen der teuren Mutationserzeugung nicht ausgeführt werden konnten.

Es wurde keine Conway-Lösung gefunden. Aussagen über lokale Minima, Plateaus und Zusammenhang des Suchraums sind durch diesen heuristischen Lauf nicht bewiesen. Ein weltweiter Neuigkeitsanspruch für den Linf=2-Graphen wird nicht erhoben.

## Sicherung und Zugriff

Das vollständige Roharchiv und sein Einzeldateimanifest sind im bestehenden privaten Review-Repository gesichert:

[Privater Archivstand 1e447f7](https://github.com/ibenarb/conway99-review-exchange/tree/1e447f7f35124cf7d9f33b46b2a8058bc47a2fde/memetik/office_pilot_001_20260912).

Zweig: `memetik/office-pilot-001-20260912`. Das öffentliche Forschungsrepository enthält ausschließlich diesen Bericht, den Auswertungsprüfer, aggregierte Forschungsergebnisse und ausgewählte Graphen. Der Upload des gesamten Roharchivs ins öffentliche Repository wurde von der automatischen Freigabeprüfung wegen der enthaltenen Lauf-/Systemprotokolle abgelehnt. Die private Sicherung ist die ausgeführte Alternative; keine neuen Partnerfreigaben wurden eingerichtet.

## Validierung

Der neue Standardbibliothek-Prüfer `src/memetik/audit_office_pilot.py` wurde auf dem Archiv ausgeführt:

- Archivhash stimmt mit der auf Office erzeugten Prüfsumme überein; 169 reguläre Dateien sicher entpackt.
- Alle 22 im Herkunftsmanifest genannten Code-/Eingabedateien stimmen mit dem archivierten Forschungsstand überein.
- Alle drei Checkpoint-Prüfsummen stimmen; der neueste Checkpoint stimmt mit Population und Bestarchiv überein.
- 16.561 eindeutige Versuchseinträge; Kennungen und Seeds konsistent; letzter Batch mit Checkpoint abgeglichen.
- 2.219 verschiedene beschriftete Graph-/Arm-Kombinationen aus Starts, zurückgelieferten Kandidaten, Endpopulation und Archiv unabhängig geprüft: Einfachheit, Grad 14, jeweilige λ- oder Ω-Bedingungen, Fehlerhistogramm, W, L1, F, Linf, Nmax, Dreiecke, Vierecke und Defektgrade.
- Die Auswahl aller zehn vollständigen Generationen wurde unabhängig rekonstruiert. Sie reproduziert Endgraphen und Stagnationszähler.
- Sämtliche 5.256 CSV-Zeilen in 146 Stichproben stimmen mit den JSON-Berichten und den rekonstruierten Populationen überein.

Die Isomorphie-Zertifikate stammen aus dem ursprünglichen nauty-Lauf. In dieser Auswertung wurde nauty nicht erneut ausgeführt; die berichteten Klassenzahlen sind insofern Herkunftsdaten. Die harten Graphbedingungen und Scores wurden unabhängig nachgerechnet.

## Laufumfang

| Größe | Wert |
| --- | ---: |
| Aktives Pilotbudget | 24 Stunden |
| Kalibrierung davor | 487,6 Sekunden |
| Gemessene Worker-CPU, einschließlich Kalibrierung | 63,10 Stunden |
| Versuche insgesamt | 16.561 |
| Kalibrierungsversuche | 96 |
| Vollständig selektierte Generationen | 10 |
| Letzter, unvollständiger Batch | 1.105 / 1.536 |
| Zurückgelieferte Kandidaten | 5.669 |
| Davon strikt besser als der jeweilige Elter | 5.511 |
| Davon neutral und nach Laufzertifikat neuer als der Elter | 158 |
| Tatsächliche Elternersetzungen über zehn Generationen | 734 |

5.669 Rückgaben sind weder 5.669 verschiedene Graphen noch ebenso viele angenommene Populationserweiterungen. Der letzte Batch wurde nicht mehr selektiert; seine gültigen Rückgaben wurden dennoch ins Archiv aufgenommen. Abschlussgrund: `PILOT_BUDGET_COMPLETE`, kein gemeldeter Ressourcenabbruch.

## Drei Zielfunktionen: getrennte Ergebnisse

Die gleichen 64 Starts wurden in drei getrennten Varianten eingesetzt. Linf wird lexikographisch durch (Linf, Nmax, L1) verfeinert.

| Variante / Arm | Bester aktiver Wert Start → Ende | Strikt verbesserte Linien |
| --- | --- | ---: |
| L1 / λ | 2398 → 2398 | 30 / 32 |
| L2² / λ | 2836 → 2836 | 27 / 32 |
| Linf / λ | (3,3,2398) → **(2,321,2670)** | 32 / 32 |
| L1 / Ω | 2718 → 2718 | 12 / 32 |
| L2² / Ω | 3926 → 3926 | 12 / 32 |
| Linf / Ω | (3,56,2940) → (3,56,2940) | 12 / 32 |

Unveränderte Gesamtbestwerte bedeuten nicht unveränderte Populationen. Die mittlere Quadratsumme im L2-λ-Arm sinkt von 4105,5 auf 3717,5, im L2-Ω-Arm von 6405,0625 auf 5057,4375.

### Der Linf=2-Zeuge

Dateien: `lambda_Linf2_00.g6` und zugehörige JSON-Metadaten im Ergebnisverzeichnis.

| Kennzahl | HoG 57338 | Neuer Zeuge |
| --- | ---: | ---: |
| W | 2182 | 2349 |
| L1 | 2398 | 2670 |
| F=L2² | 2836 | 3312 |
| Linf | 3 | **2** |
| λ-Verletzungen | 0 | 0 |

Entstanden in `g000009-Linf-line-010-0`: drei Störzüge und zwei akzeptierte Abstiegsschritte, insgesamt fünf Apex-Züge laut Protokoll, 1,34 CPU-Sekunden. Das ist ein Weg vom damaligen Linienelter, nicht nachweislich ein Fünf-Zug-Weg vom ursprünglichen HoG-Gründer. Die geordneten Zwischenmatrizen stehen nicht im Protokoll; eine Minimalitätsbehauptung wird nicht abgeleitet.

Der Zeuge ist besser nach Linf und schlechter nach W, L1 und F. Er belegt einen konkreten Nutzen des getrennten Normarms für das erreichte Fehlerprofil. Er beweist keine schnellere Annäherung an die Lösung.

## B: deutliche Entwicklung, aber kein gemeinsamer Sieger aller Maße

Die Gruppe enthält B und zehn bereits vor dem Pilot erzeugte Nachfahren. Daher ist der Gruppenstartwert F=9364 und nicht der Wert 9716 des ursprünglichen B.

| B-Gruppe / aktive Zielfunktion | Bester Wert am Start | Bester Endpopulationswert |
| --- | ---: | ---: |
| L1 | 3512 | 3304 |
| L2² | 9364 | 5522 |
| Verfeinertes Linf | (10,30,3656) | (7,2,3324) |

In jeder Variante verbessern sich alle elf Linien strikt in ihrem aktiven Kriterium. Die W-Bestmarke 2110 wird nicht unterboten. Weniger starke Einzelfehler werden teilweise mit mehr falschen Paaren bezahlt.

Eine wichtige Falle der Abstammungsstatistik: Eine Rückgabe der B-L2-Linie erreicht F=4980. Ihr protokolliertes kanonisches Zertifikat entspricht aber dem bereits vorhandenen H_minus-Gründer. Sie entstand durch Cross-over in `g000006-L2-line-047-7`. Das ist keine neue Struktur und kein neuer Gründerrekord; die niedrigere Zahl darf nicht als neuer B-Erfolg ohne diese Einordnung beworben werden. Die beste regulär ausgewählte B-L2-Endpopulation liegt bei F=5522.

In jeder Norm bleiben alle acht A-Linien, fünf H_minus-Linien und fünf H_plus-Linien unverändert. Von den drei H_Z14-Linien verbessert sich jeweils eine. Diese Starrheit ist ein gezieltes Motiv für neue Operatoren, kein Beweis gleicher Plateaus.

## Engpass: geplante Ausflüge sind nicht tatsächlich ausgeführte Ausflüge

Ω verbraucht 55,50 CPU-Stunden, λ nur 7,60. Das sind rund 88 % beziehungsweise 12 %. Die Normvarianten selbst sind mit ungefähr 21 CPU-Stunden je Variante ähnlich ausgestattet; daraus folgt keine gleichmäßige Rechenzeitverteilung zwischen Ω und λ.

| Ω-Methode | Versuche | Vor Mindestzahl Störzüge beendet | CPU-Stunden |
| --- | ---: | ---: | ---: |
| Zufall, 2–4 | 3018 | 14 | 21,60 |
| Zufall, 5–12 | 2040 | 181 | 16,12 |
| Zufall, 13–32 | 977 | 656 | 8,09 |
| Zufall, 13–64 | 86 | 74 | 0,72 |
| Geführt, 8–16 | 1020 | 1009 | 8,50 |

Alle 1020 geführten Ω-Versuche enden am CPU-Limit. In 1017 wird kein Abstiegsschritt akzeptiert. Das kann je Versuch auch aus erfolgloser lokaler Suche entstehen; es wird nicht pauschal als „Abstieg nie begonnen“ ausgegeben. Viele Rückgaben stammen aus bereits während der kurzen Störphase gefundenen Verbesserungen.

Im λ-Arm erreichen dagegen alle protokollierten Störversuche mindestens die untere Grenze ihrer vorgesehenen Länge. Ein bloßer Vergleich der konfigurierten Längen würde deshalb unterschiedliche tatsächlich ausgeführte Experimente gleichsetzen.

Ω-Cross-over: 1020 Versuche, 971 mit Status NO_CROSSOVER_CHILD, 30 übernahmefähige Rückgaben. Dieser Status ist nicht gleichbedeutend mit einem allgemeinen Nichtexistenzbeweis für Kinder. Erfolgsfälle können außerdem bekannte andere Populationsgraphen reproduzieren. Das spricht für die bereits vorgeschlagene Ausrichtungs-/Rangdiagnostik, nicht für pauschales Abschalten.

## Konsequenzen für den nächsten Pilot

1. **Linf=2-Zeugen aufnehmen.** Eigenständiger Start und genauer lokaler Vergleich mit HoG, ohne ihn zum allgemeinen besseren Kandidaten zu erklären.
2. **Ω-Mutationserzeugung zuerst verbessern.** Wiederholte Trägerenumeration vermeiden, gültige Optionen wiederverwenden und ein gesondertes Abstiegsbudget vorsehen. Tatsächliche Störlänge sowie Grund einer Verkürzung ausweisen.
3. **B-Endgraphen übernehmen.** Die drei normabhängigen B-Nachfahren liegen als geprüfte Graphdateien vor. Ihre Herkunft zählt nicht als drei neue unabhängige Konstruktionsprinzipien.
4. **Neue Gründer weiterhin anstreben.** Der Lauf testete nahe Varianten vorhandener Gründer, nicht zehn zusätzliche unabhängige Prinzipien. Er widerlegt den Nutzen breiterer Starts nicht.
5. **Kleine exakte Fluchtuntersuchung getrennt führen.** Vollständige Nachbarschaftszählung darf nicht den begrenzten produktiven Zufallsgenerator verwenden. Dieser Pilot liefert keine Mindestzykluslänge.
6. **Vergleich fair gestalten.** Gleiches CPU-Budget je Arm und Variante sowie separate Messung tatsächlicher Zug-/Abstiegslängen; die bisherige Aufgabezahl allein genügt nicht. Bestehende Parameter zunächst als Baseline beibehalten.

Die Voraussetzung „letzten Office-Laufstand übernehmen“ aus dem Pilotentwurf ist damit erfüllt. Eine unveränderte Verlängerung dieses Piloten hat gegenüber der gezielten Ω-Verbesserung keine erste Priorität.
