# Beweisabschluss: k66_s1_t225

Stand: 13. September 2026. Status: computergestützter Fallausschluss abgeschlossen, auf Grundlage der unten bezeichneten mathematischen Voraussetzungen und Cake-Evidenz.

## Satz und Geltungsbereich

Es gibt keinen stark regulären Graphen mit Parametern (99,14,1,2), dessen Ordnung-3-Automorphismus mit genau einem fixierten Dreieck das im Projekt definierte Quotientengerüst **k66_s1_t225** besitzt. Insbesondere besitzt dieses Gerüst keine Realisierung durch die notwendige symmetrische Orbitmatrix P.

Dabei bezeichnet K66 den Zweig mit drei angehängten Vierergruppen, zwei weiteren dreieckigen Orbits T und 18 gewöhnlichen Orbits U; die kanonischen lokalen Anschlussmuster sind (2,2,5), der T–T-Eintrag ist eins und die U-Zellen haben Größen (0,5,5,8). Der Satz betrifft diesen vollständig bezeichneten Strukturfall. Die Nichtexistenz von SRG(99,14,1,2) insgesamt folgt daraus nicht.

## Beweis

**1. Notwendige Gleichungen.** Aus der SRG-Identität A²+A=12I+2J folgt für die 32×32-Orbitmatrix nach Abzug der Beiträge der drei Fixpunkte

P²+P = 12I+6J−3 diag(J4,J4,J4,0_20).

Mit dem 14×14-Block H der angehängten Orbits und T, dem 18×14-Block Z und dem 18×18-Block B folgt insbesondere

G := C_H−H²−H = ZᵀZ,

BZ = 6J−Z(H+I),

B²+B+ZZᵀ = 12I+6J.

Die Herleitung sowie die notwendigen Profil-, Multiplizitäts-, Projektor-, Paar- und Star-Bedingungen stehen in `MATHEMATISCHER_AUDIT.md`, Abschnitte 3–8. Die dortige Herleitung verwendet die bezeichnete Orbitstruktur und keine Polytopeigenschaft.

**2. Vollständige endliche Überdeckung.** Zwischen jedem Paar der drei angehängten Vierergruppen liegt ein perfektes Matching. Alle drei Matchings werden ohne vorgelagerten Filter durch S4³ enumeriert: 24³ = 13.824 beschriftete Fälle. Der unabhängig bestimmte Stabilisator des festen Gerüsts besitzt Ordnung 64. Seine direkte Wirkung auf den zwölf Crossmatching-Kanten liefert eine disjunkte vollständige Partition in 246 Bahnen:

| Bahnlänge | Anzahl Bahnen | Beschriftete Fälle |
| --- | ---: | ---: |
| 32 | 60 | 1.920 |
| 64 | 186 | 11.904 |
| Gesamt | 246 | 13.824 |

Die vollständigen Mitgliederlisten sind gespeichert. Die separat bestimmte Fixpunktsumme ist 15.744; Burnside ergibt 15.744/64 = 246. Identität, Inversen, Gruppenabschluss, Bijektivität jeder Wirkung und Punktstabilisatorformel wurden geprüft. Die Wirkung erhält das feste Gerüst und C_H, folglich auch die notwendigen Gleichungen bis auf Umnummerierung.

**3. Ausschluss von 223 Bahnen.** Für jeden Vertreter wurde H unmittelbar aus den drei Matchings rekonstruiert und G exakt berechnet. In 223 Bahnen wurde ein Hauptminor von G mit strikt negativer Determinante nachgewiesen. Die Determinanten wurden durch rationale Gauß-Elimination neu berechnet und stimmen exakt mit den gespeicherten Zeugen überein. Weil jede Gram-Matrix ZᵀZ positiv semidefinit ist, widerspricht dies einer Realisierung. Die 223 Bahnen umfassen 12.672 beschriftete Fälle.

**4. Ausschluss der 23 verbleibenden Bahnen.** Die übrigen 23 Vertreter sind exakt die bereits geprüften Encoder-Fälle. Ihre Matching-Codes, alle 254 kanonischen S/L-Einheitsbelegungen und die gesicherten Encoder-Berichte wurden verknüpft. Die Gram-Ränge sind viermal elf und neunzehnmal zwölf.

Jede tatsächliche Realisierung liefert eine zulässige Belegung der auditierten notwendigen Profil-CNFs. Die BDD-Übersetzung dieser Bedingungen ist durch die allgemeine Induktion im Encoder-Audit gerechtfertigt; ihre konkreten Daten wurden mit beliebig genauer Ganzzahlarithmetik kontrolliert. Sämtliche 167 CNF-Vergleiche ergaben vollständige Bytegleichheit mit den gebundenen Beweiseingaben. Die Reduktionsrunden sind nichtzirkulär: Innerhalb einer Runde erfolgen Entfernungen simultan; spätere Runden verwenden nur zuvor gerechtfertigte Ausschlüsse.

Die 15 unreduzierten R2-Globalfälle und der reduzierte Globalfall v4_09232 sind durch die verknüpften Cake-Replays ausgeschlossen. Dazu gehören zwölf Star-Ausschlüsse für v4_09232. Bei den übrigen sieben Wurzeln rechtfertigen 125 Cake-geprüfte Profilbeweise die Reduktion; die reduzierte Suche besitzt eine vollständig geprüfte binäre Überdeckung durch 897 zertifizierte Hauptlaufblätter. Ihre Unerfüllbarkeit schließt die sieben Wurzel-CNFs aus. Somit sind alle 23 Restbahnen ausgeschlossen. Sie umfassen 1.152 beschriftete Fälle.

**5. Schluss.** Die 223 und 23 Vertreter sind disjunkt und ihre Vereinigung ist exakt die vollständige Repräsentantenmenge. Damit sind 12.672+1.152 = 13.824 beschriftete Fälle ausgeschlossen. Eine Realisierung von k66_s1_t225 würde zu einem dieser Fälle gehören und dort einen Widerspruch erzeugen. Der bezeichnete Strukturfall ist ausgeschlossen.

## Evidenz und tatsächlich ausgeführte Prüfungen

| Bestandteil | Evidenz |
| --- | --- |
| Hauptlauf mit 897 Blättern | Vollständige binäre Überdeckung, Dateiintegrität und archivierte Cake-Bestätigungen geprüft; kein neuer Replay dieser 897 Beweise im Neustart-/Abschlussaudit |
| 28 zusätzliche bestehende Beweise | Tatsächlich erneut mit Cake geprüft; sämtliche Eingaben mit der Encoder-Reproduktion verknüpft |
| 125 Profile der sieben Wurzeln | Neu erzeugte und Cake-geprüfte Profilbeweise im gesicherten Neustartstand |
| Encoder/Input-Reproduktion | 23 Fälle, 167 byteidentische Vergleiche, 945 kleine ergänzende Kontrollen; mathematische Übersetzungsbegründung dokumentiert |
| Arithmetik und Bahnen | Vollständiger Ryzen-Lauf `close_k66.py` 1.0.1: PASS in 2,108 Sekunden, ohne neue Solverläufe oder Beweis-Replays |
| Abschließende Artefaktprüfung | Alle sechs Git-Ergebnisdateien vollständig gelesen; Git-Blob-Identität, Partition, Summen, Zeugenabgleich, Programm-/Manifestbindung und Verknüpfung aller 23 veröffentlichten Encoder-Berichte geprüft |

Dies ist ein computergestützter Beweis mit der bezeichneten Checker- und Implementierungsgrundlage, kein vollständig in einem Beweisassistenten formalisiertes Theorem. Das historische fehlerhafte `lrat-check` trägt den positiven Schluss nicht. Für die 897 Hauptblätter wird ausdrücklich die archivierte Cake-Evidenz verwendet, kein nachträglich behaupteter unabhängiger Replay.

## Feste Nachweise

- Neustart und Zertifikatsgrundlage: `fba694b50357fdd795601a6b17c97036f06af101`.
- Eingesammelte Originalquellen: `0a54ce594f89b948c77200328f5de7379bae4806`.
- Encoder-Reproduktion: `b38d4cb755505a67c01bcf87aff0e2dbf1f79524`.
- Vollständige ergänzende Replay-Verknüpfung und Encoder-Audit: `a85aabc475116c6cb5fa39a10d281767ab6f7cf5`.
- Abschlussprüfer 1.0.1: `f1172b469c6e01dc926905f28bd844e695bee56e`; Programm-SHA256 `c7af2a075cc43c20555c00788c549bba09612b7fb0b7409b262f75429b4d449b`.
- Erfolgreiche Abschlussrechnung: `cba755a1810e15bff149e3a85cf9a59e4283502a`, Verzeichnis `results/k66_completion_proof_20260913`.
- Nachgelagerte Konsistenzprüfung: `results/k66_completion_proof_20260913/final_review.json`; enthält Längen, SHA256 und Git-Blob-IDs aller sechs gelesenen Abschlussdateien.

Die früheren Berichte mit noch offenen Abschlussbedingungen bleiben als historische Fassungen erhalten. Ihre offenen Punkte zu den 223 Minoren und 246 Bahnen sind durch den hier dokumentierten erfolgreichen Lauf erledigt. Version 1.0.0 des Abschlussprüfers hatte einen Serialisierungsvergleich zwischen vollständigen und kompakten Berichten verwechselt; Version 1.0.1 behebt dies unter Beibehaltung der festen Hashbindung. Das erfolgreiche Ergebnis stammt ausschließlich aus Version 1.0.1.
