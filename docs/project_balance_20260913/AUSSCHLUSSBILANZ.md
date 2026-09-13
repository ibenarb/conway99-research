# Conway99: Ausschlussbilanz vom 13. September 2026

Diese Bilanz trennt die externe mathematische Abdeckung von der internen Zertifikatsabdeckung. Feste Referenzen und Erläuterungen stehen in `ZWISCHENFAZIT.md` und `../../results/project_balance_20260913/source_manifest.json`. Die vollständigen Matrizen, Typen und Statusfelder stehen in `../../results/project_balance_20260913/exclusion_ledger.json`.

## Gesamtabdeckung

| Aufgabe | Status | Beweisgrundlage / offene Pflicht |
| --- | --- | --- |
| Primordnungen außer 2,3 | Extern ausgeschlossen | Literatur E1; kein vollständiger eigener Replay |
| Ordnung 3 mit Fixpunkten | Extern ausgeschlossen | E1; eigener Nachvollzug nur teilweise abgeschlossen |
| Freie Ordnung 3, τ=13,20 | Ausgeschlossen | Dreieckskongruenz |
| Freie Ordnung 3, τ=27 | Ausgeschlossen | Algebraischer τ=6-Schluss und reproduzierte f27-Kette |
| Freie Ordnung 3, τ=6 | Offen | 101 offene L-Typen; 26 überlebende notwendige T-Gerüste |
| Ordnung 2 mit einem Fixpunkt | Offen | Kanonische Wirkung; kein kompletter SRG-Ausschluss |
| Asymmetrischer Graph | Offen | Wird durch einen Symmetrieausschluss nicht erfasst |

## Freie C3-Wirkung: alle 103 L-Typen bei τ=6

H = historisches LRAT/Cake-Zertifikat, mit mathematischem Transfer; O = kein vollständiger Ausschluss in den geprüften Quellen. Die zwei H-Zeilen wurden in dieser Bilanz nicht erneut mit Produktionsproofs abgespielt.

| L-Zyklenlängen | Status |
| --- | --- |
| 27 | O |
| 24,3 | O |
| 22,5 | O |
| 21,6 | O |
| 21,3,3 | O |
| 20,7 | O |
| 19,8 | O |
| 19,5,3 | O |
| 18,9 | O |
| 18,6,3 | O |
| 18,3,3,3 | O |
| 17,10 | O |
| 17,7,3 | O |
| 17,5,5 | O |
| 16,11 | O |
| 16,8,3 | O |
| 16,6,5 | O |
| 16,5,3,3 | O |
| 15,12 | O |
| 15,9,3 | O |
| 15,7,5 | O |
| 15,6,6 | O |
| 15,6,3,3 | O |
| 15,3,3,3,3 | O |
| 14,13 | O |
| 14,10,3 | O |
| 14,8,5 | O |
| 14,7,6 | O |
| 14,7,3,3 | O |
| 14,5,5,3 | O |
| 13,11,3 | O |
| 13,9,5 | O |
| 13,8,6 | O |
| 13,8,3,3 | O |
| 13,7,7 | O |
| 13,6,5,3 | O |
| 13,5,3,3,3 | O |
| 12,12,3 | O |
| 12,10,5 | O |
| 12,9,6 | O |
| 12,9,3,3 | O |
| 12,8,7 | O |
| 12,7,5,3 | O |
| 12,6,6,3 | O |
| 12,6,3,3,3 | O |
| 12,5,5,5 | O |
| 12,3,3,3,3,3 | O |
| 11,11,5 | O |
| 11,10,6 | O |
| 11,10,3,3 | O |
| 11,9,7 | O |
| 11,8,8 | O |
| 11,8,5,3 | O |
| 11,7,6,3 | O |
| 11,7,3,3,3 | O |
| 11,6,5,5 | O |
| 11,5,5,3,3 | O |
| 10,10,7 | O |
| 10,9,8 | O |
| 10,9,5,3 | O |
| 10,8,6,3 | O |
| 10,8,3,3,3 | O |
| 10,7,7,3 | O |
| 10,7,5,5 | O |
| 10,6,6,5 | O |
| 10,6,5,3,3 | O |
| 10,5,3,3,3,3 | O |
| 9,9,9 | O |
| 9,9,6,3 | O |
| 9,9,3,3,3 | O |
| 9,8,7,3 | O |
| 9,8,5,5 | O |
| 9,7,6,5 | O |
| 9,7,5,3,3 | O |
| 9,6,6,6 | O |
| 9,6,6,3,3 | O |
| 9,6,3,3,3,3 | O |
| 9,5,5,5,3 | O |
| 9,3,3,3,3,3,3 | O |
| 8,8,8,3 | O |
| 8,8,6,5 | O |
| 8,8,5,3,3 | O |
| 8,7,7,5 | O |
| 8,7,6,6 | O |
| 8,7,6,3,3 | O |
| 8,7,3,3,3,3 | O |
| 8,6,5,5,3 | O |
| 8,5,5,3,3,3 | O |
| 7,7,7,6 | O |
| 7,7,7,3,3 | O |
| 7,7,5,5,3 | O |
| 7,6,6,5,3 | O |
| 7,6,5,3,3,3 | O |
| 7,5,5,5,5 | O |
| 7,5,3,3,3,3,3 | O |
| 6,6,6,6,3 | O |
| 6,6,6,3,3,3 | O |
| 6,6,5,5,5 | O |
| 6,6,3,3,3,3,3 | O |
| 6,5,5,5,3,3 | O |
| 6,3,3,3,3,3,3,3 | H |
| 5,5,5,3,3,3,3 | O |
| 3,3,3,3,3,3,3,3,3 | H |

## T-Gerüste: 156 → 69 → 44 → 26

| Stufe | Anzahl |
| --- | ---: |
| Negativer Gram-Eintrag | 87 |
| Negativer Hauptminor | 25 |
| Exaktes binäres Separationszeugnis | 18 |
| Binärer Gram-Zeuge; vollständiger Quotient offen | 26 |

Überlebende X-Indizes: 0, 1, 2, 5, 8, 13, 22, 24, 26, 27, 39, 40, 41, 46, 51, 52, 64, 65, 71, 72, 75, 95, 96, 98, 121, 122.

Alle 156 X-Matrizen samt Status stehen in der JSON-Bilanz. Diese Achse und die L-Achse sind nicht als zwei disjunkte Falllisten addierbar.

## Fixdreieck: alle 72 internen Strukturklassen

Für **jede** folgende Zeile gilt mit Literatur E1: mathematisch ausgeschlossen. Der Tabellenstatus beschreibt ausschließlich den eigenen Nachvollzug.

V3 = historisch als zertifiziert berichtet; Zuordnung aus dem dokumentierten Frontierklassifikator, keine Einzelproofprüfung hier. K66 = abgeschlossener eigener Audit. N = kein interner Abschlussnachweis in den geprüften Quellen.

| Strukturklasse | Interner Stand |
| --- | --- |
| k00_s0_t000 | N |
| k01_s0_t001 | N |
| k02_s0_t002 | V3 |
| k03_s0_t004 | N |
| k04_s0_t005 | N |
| k05_s0_t006 | N |
| k06_s0_t011 | N |
| k07_s0_t012 | V3 |
| k08_s0_t013 | N |
| k09_s0_t014 | N |
| k10_s0_t015 | N |
| k11_s0_t016 | N |
| k12_s0_t022 | V3 |
| k13_s0_t024 | V3 |
| k14_s0_t025 | V3 |
| k15_s0_t026 | V3 |
| k16_s0_t044 | N |
| k17_s0_t045 | N |
| k18_s0_t046 | N |
| k19_s0_t055 | N |
| k20_s0_t056 | N |
| k21_s0_t066 | N |
| k22_s0_t111 | N |
| k23_s0_t112 | V3 |
| k24_s0_t113 | N |
| k25_s0_t114 | N |
| k26_s0_t115 | N |
| k27_s0_t116 | N |
| k28_s0_t122 | V3 |
| k29_s0_t123 | V3 |
| k30_s0_t124 | V3 |
| k31_s0_t125 | V3 |
| k32_s0_t126 | V3 |
| k33_s0_t134 | N |
| k34_s0_t135 | N |
| k35_s0_t136 | N |
| k36_s0_t144 | N |
| k37_s0_t145 | N |
| k38_s0_t146 | N |
| k39_s0_t155 | N |
| k40_s0_t156 | N |
| k41_s0_t166 | N |
| k42_s0_t222 | V3 |
| k43_s0_t224 | V3 |
| k44_s0_t225 | V3 |
| k45_s0_t226 | V3 |
| k46_s0_t244 | V3 |
| k47_s0_t245 | V3 |
| k48_s0_t246 | V3 |
| k49_s0_t255 | V3 |
| k50_s0_t256 | V3 |
| k51_s0_t266 | V3 |
| k52_s0_t444 | N |
| k53_s0_t445 | N |
| k54_s0_t446 | N |
| k55_s0_t455 | N |
| k56_s0_t456 | N |
| k57_s0_t466 | N |
| k58_s0_t555 | N |
| k59_s0_t556 | N |
| k60_s0_t566 | N |
| k61_s0_t666 | N |
| k62_s1_t122 | V3 |
| k63_s1_t126 | V3 |
| k64_s1_t166 | V3 |
| k65_s1_t222 | V3 |
| k66_s1_t225 | K66 |
| k67_s1_t226 | V3 |
| k68_s1_t256 | N |
| k69_s1_t266 | V3 |
| k70_s1_t566 | N |
| k71_s1_t666 | V3 |

Ergebnis: 29 V3-Berichte + 1 K66-Abschluss + 42 N-Zeilen = 72. Eine spätere, nicht in den gesichteten Quellen gesicherte Rechnung wird damit nicht ausgeschlossen.

## Rechnerische Konsistenzprüfung

Die 103 L-Typen und 72 K-Bezeichnungen wurden auf Eindeutigkeit und die angegebenen Summen geprüft; die K-Bezeichnungen wurden aus den lokalen D8-Mustern rekonstruiert. Die 156 X-Statuszuordnungen wurden mit den 18 exakten Separationsausschlüssen und 26 Zeugen abgeglichen. Das ist eine Bilanzprüfung, keine neue SAT-/Proofrechnung.
