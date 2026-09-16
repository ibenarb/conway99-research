# Escape-Zensus Office 2026-09-15: Befunde und Folgerungen

## Eingang und Prüfung

Originalpaket `92235c0c-77c1-452d-95dd-bebf5d4f3557.zip`, SHA256 `3e675a35beb32342b47cfbfba2d811d1bec861a8c702a45b0deac68f17204832`. ZIP-CRC geprüft, flache Dateistruktur. Ausgelieferte Version escape-0.1.0, Forschungsstand `9630f29c90a0295b1d08bc9caa9388e49df6acbf`. Das Original bleibt unverändert gespeichert; Rohdateien stehen unter `escape_office_result/`.

Alle 20 Aufgaben sind EXHAUSTED. Insgesamt 940 zulässige Trades, 71,835 summierte Worker-CPU-Sekunden. Der Endzeitstempel 18:24:29 UTC passt zum lokalen Verzeichnisstart 20:23:58 bei UTC+2; rund 32 Sekunden Wandzeit. Die frühere Größenordnung sieben Stunden bezeichnete ausgeschöpfte maximale Kontingente, keine gemessene Laufzeitprognose.

Die gesamte Enumeration wurde hier mit derselben ausgelieferten Zipapp wiederholt: alle Familienzählungen, besser/neutral/schlechter-Zählungen und gespeicherten Verbesserungszeugen stimmen exakt überein. Wiederholung derselben Generatoren belegt Reproduzierbarkeit, nicht deren Vollständigkeit gegenüber allen denkbaren armerhaltenden Trades. Die Aussage bleibt auf die implementierten Familien begrenzt.

Alle 28 kriteriumsbezogenen Verbesserungszeugnisse wurden zusätzlich aus Ausgangsgraph und gespeichertem Trade rekonstruiert. Harte Bedingungen, SHA256 und Metriken stimmen; die Fehlernormen wurden auch über Mengen gemeinsamer Nachbarn nachgerechnet. Diese 28 Einträge enthalten 18 verschiedene graph6-Dateihashes. Das ist keine Isomorphieklassenzahl. Prüfskript: `escape_verify_office.py`; Prüfdaten: `escape_office_audit.json`.

## Tatsächliche Nachbarschaften

| Gründer | 4x4 / Apex | 4x6 / Rotation | 6x6 | Gesamt |
| --- | ---: | ---: | ---: | ---: |
| A_legacy (Ω) | 3 | 0 | 0 | 3 |
| B_original (Ω) | 277 | 0 | 0 | 277 |
| B_end_F (Ω) | 90 | 33 | 0 | 123 |
| Codex_C02 (Ω) | 15 | 7 | 0 | 22 |
| HoG57338 (λ) | 46 | 0 | — | 46 |
| λ-Linf2-Zeuge | 40 | 0 | — | 40 |
| Codex_C06 (λ) | 363 | 0 | — | 363 |
| Codex_C08 (λ) | 66 | 0 | — | 66 |

Alle vier Ω-Starts haben keine anwendbaren 6x6-Trades, alle vier λ-Starts keine anwendbaren Rotationen. Daraus folgt keine globale Entbehrlichkeit dieser Familien: Nach einem Schritt können andere Trades gültig werden. Insbesondere bleibt die Operatorprüfung in Folgezuständen erforderlich.

B_original ist für W ein striktes lokales Minimum dieser Nachbarschaft, trotz 106 unmittelbar F-verbessernder Trades. HoG57338 ist für W, L1 und F strikt lokal minimal, Codex_C06 für W. Codex_C08 ist für L1 und F strikt lokal minimal; für W gibt es 33 neutrale Trades. Diese Zählungen beweisen keine verschiedenen neutralen Klassen.

B_end_F, der λ-Linf2-Zeuge und Codex_C02 lassen sich in allen vier Kriterien unmittelbar verbessern. Hier sind normabhängige Abstiege sinnvoll, bevor ein Escape von einem lokalen Endpunkt untersucht wird. Der historische Populationspilot hatte diese einfachen Verbesserungen teilweise nicht gefunden; seine Endpunkte waren keine nachgewiesenen lokalen Minima.

## Konkrete Verbesserungen von Codex_C02

| Graph | W | L1 | F | Linf | Nmax |
| --- | ---: | ---: | ---: | ---: | ---: |
| Gründer | 2074 | 2506 | 3472 | 4 | 6 |
| Bester W-Zeuge, 4x4 | 2063 | 2504 | 3490 | 4 | 5 |
| Bester F-Zeuge, 4x6 | 2083 | 2498 | 3406 | 4 | 3 |

W=2063 und F=3406 sind verschiedene Nachfahren; ihre Bestwerte dürfen nicht zu einem fiktiven Graphen zusammengezogen werden. Beide Zeugen liegen im Ω-Arm. Sie sind Kandidatenfortschritt gegenüber dem zuvor dokumentierten C02, kein weltweiter Rekordanspruch.

Bei HoG57338 und Codex_C08 betrifft die Linf-Verbesserung das lexikographische Tupel (Linf,Nmax,L1); Linf selbst bleibt jeweils 3. Beim alten λ-Linf2-Zeugen verschlechtern die gespeicherten W/L1/F-Verbesserungen Linf von 2 auf 3. Das unterstreicht die normabhängigen Zielkonflikte.

Ein gespeicherter Apex-Zeuge von Codex_C06 (Linf-Tupel) besitzt zwei Kanten innerhalb der ursprünglichen 33er-Farbklassen. Damit kann der Operator die feste ursprüngliche Dreiteilung tatsächlich verlassen. Dies beweist weder das Verlassen jeder möglichen Dreiteilung noch die Erreichbarkeit einer exakten Lösung.

## A_legacy: erste Barriere und zweite Schicht

A_legacy besitzt genau drei erste Trades. Ihre Änderungen sind:

| erster Trade | ΔW | ΔL1 | ΔF | ΔLinf | ΔNmax |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | +37 | +50 | +86 | +1 | −5 |
| 1 | +18 | +32 | +62 | 0 | 0 |
| 2 | +34 | +58 | +134 | 0 | +4 |

Jeder nichtleere zulässige Weg muss daher mit einer Verschlechterung beginnen. Für F mindestens von 3926 auf 3988. Das ist eine notwendige untere Schranke der zwischenzeitlichen Barriere; sie garantiert keine existierende Flucht.

Alle drei Nachbarn wurden danach über sämtliche drei Familien vollständig expandiert. Jeder besitzt wiederum genau drei 4x4-Trades und keine 4x6-/6x6-Trades. Keiner der neun Zwei-Schritt-Wege verbessert W, L1, F oder das Linf-Tupel gegenüber A_legacy. Ohne weiteren Befund hätte ein existierender Verbesserungsweg daher mindestens Länge drei. Die Untersuchung der gesamten erreichbaren Komponente wird nachfolgend separat dokumentiert.

## Konsequenz für weitere Läufe

Der Zensus liefert eine belastbare Ausgangslage für echte Escape-Experimente, ersetzt aber keine Untersuchung neutraler Komponenten und längerer Wege. Der nächste sinnvolle Vergleich ist B_original/W (zwingend zunächst schlechter), HoG57338/F (ebenso) und Codex_C08/W (neutrale erste Schritte möglich). Negative Aussagen gelten immer nur relativ zum konkret durchlaufenen Operatorensatz.

Für die bereits direkt verbesserbaren Starts sind zunächst standardisierte normabhängige Abstiege angebracht. Die Qualität und Komponentenzugehörigkeit ihrer Endpunkte müssen getrennt untersucht werden. Kein weiterer Office- oder Ryzen-Lauf wurde im Zuge dieses Audits gestartet.

## A_legacy: vollständige Komponentenuntersuchung

Die Anschlussuntersuchung ist abgeschlossen: genau **acht erreichbare beschriftete Graphen**, alle acht vollständig über 4x4, 4x6 und 6x6 expandiert. Jeder hat genau drei 4x4-Nachbarn; überall fehlen 4x6- und 6x6-Trades. Sämtliche erzeugten Kanten verbleiben in dieser Menge.

Die Übergangsstruktur ist der Würfel Q3: Die acht Graphen sind genau die acht XOR-Kombinationen der drei ersten Trades; jeder Übergang ändert eine dieser drei Koordinaten. Zwölf ungerichtete Übergangskanten. Dieses Zertifikat wurde durch Rekonstruktion aller Kanten überprüft. Die Würfelkoordinaten bezeichnen Zustände des Suchverfahrens, nicht Knoten des jeweiligen 99-Knoten-Graphen.

| Würfelkoordinate | W | L1 | F | Linf | Nmax |
| --- | ---: | ---: | ---: | ---: | ---: |
| 000 (A_legacy) | 2175 | 2718 | 3926 | 4 | 6 |
| 100 | 2212 | 2768 | 4012 | 5 | 1 |
| 010 | 2193 | 2750 | 3988 | 4 | 6 |
| 001 | 2209 | 2776 | 4060 | 4 | 10 |
| 110 | 2229 | 2806 | 4098 | 5 | 1 |
| 101 | 2242 | 2822 | 4138 | 5 | 1 |
| 011 | 2228 | 2808 | 4118 | 4 | 10 |
| 111 | 2260 | 2860 | 4220 | 5 | 1 |

**Folgerung:** A_legacy ist für W, L1, F und das lexikographische Linf-Tupel der eindeutig beste Zustand dieser erreichbaren Komponente. Mit diesen implementierten drei Familien gibt es keinen Verbesserungsweg irgendeiner Länge. Das stärkere Komponentenergebnis ersetzt die bloße Untergrenze „mindestens drei Schritte“. Die gefundene notwendige Anfangsverschlechterung ist kein hinreichender Fluchtmechanismus.

Die Aussage erfasst ausschließlich diese eingefrorenen Operatorfamilien im festgehaltenen Ω-Rahmen. Sie ist kein Ausschluss besserer Ω-Graphen und kein Conway-99-Ausschluss. Zusätzliche Trades, ein geeigneter Reparaturschritt oder andere zulässige Rekombinationen könnten die Komponente verlassen; das ist nicht untersucht.

Für A_legacy sollte deshalb keine längere Wanderung mit unverändertem Operatorensatz beauftragt werden. Hier benötigen wir eine konkrete Operatorerweiterung. Für B_original/W, HoG57338/F und Codex_C08/W bleibt die Untersuchung längerer Wege bzw. neutraler Komponenten sinnvoll.

Reproduktion: `escape_A_component.py`, begrenzt auf höchstens 64 entdeckte Zustände und 120 CPU-Sekunden je Expansion. Keine dieser Schranken wurde erreicht. Vollständige Daten in `escape_A_component_result.json`, Kanten-/Normprüfung mit `escape_verify_component.py`. Die vorausgehende Tiefen-zwei-Rechnung steht separat in `escape_A_depth2.py` und `escape_A_depth2_result.json`. Übernommene Kern-/Operatorversion samt benötigter Steuerungshilfen unter `escape_build/`; Ursprung ist die bereits ausgelieferte Version, ohne mathematische Änderung der Generatoren.
