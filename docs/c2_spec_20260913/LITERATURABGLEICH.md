# Begrenzter C2-Literaturabgleich, 13. September 2026

Zweck: Literaturvoraussetzungen und Überschneidungen für die neue C2-Modellspezifikation bestimmen. Kein vollständiges Literaturreview, keine Wiederholung historischer Ausschlussrechnungen, kein Prioritätsnachweis.

| Gegenstand | Befund und genaue Quelle | Konsequenz |
|---|---|---|
| Eindeutiger Fixpunkt einer Involution | Makhnev–Minakova (2004), DOI 10.1515/156939204872374. Im Autoren-Vortrag unten, Theorem 1 auf PDF-Seite 16, ausdrücklich angegeben; vorausgehende Folien behandeln Fixpunktkonfigurationen. Verlags-PDF-Abruf in dieser Sitzung mit technischem Fehler gescheitert. | Als zitierte Voraussetzung übernehmen; keine Behauptung eines erneuten Audits des Originalbeweises. |
| Gruppenbeschränkungen | Crnković–Maksimović §7, Sätze 7.1–7.3, zusammen mit Cesarz–Woldar (2025), Korollar 3.13. | Volle Gruppe nur 1, C2 oder C3; C3 fixpunktfrei. Ein C2-Erfolg ist noch kein vollständiger Symmetrieausschluss. |
| Rahmen 1+14+84 | Standardfolgen von lambda=1 und mu=2; explizit Thakkar §4. | Keine Neuheit beanspruchen. |
| Gemischte Nachbarbedingungen | Thakkar §4 formuliert auch die inneren/äußeren Paarbedingungen. | Unsere vollständige E2 ist keine neu entdeckte notwendige Bedingung. |
| Vorgegebene Automorphismen | Thakkar §5 beschreibt Orbitmodelle und einen positiven C2-Kleintest. In den gelesenen Passagen kein vollständiger C2-Ausschluss bei 99 Knoten. | Modellprinzip zitieren; fremde Implementierung weder als geprüft noch als unmittelbar übernommen ausgeben. |
| Thakkars C7-Einordnung | §5 nennt den C7-Fall offen. Dies widerspricht dem in Crnković–Maksimović Satz 7.1 festgehaltenen Behbahani–Lam-Ergebnis. | Kein C7-Arbeitspaket eröffnen; technische Beschreibung und Literaturbilanz getrennt beurteilen. |
| Lou–Murin | §6 behandelt Primordnungen und Orbitmatrizen. Kein vollständiger Involutionsausschluss in den geprüften Passagen gefunden. | Strukturelle Vorarbeit; kein Beleg für Neuheit unseres C2-Modells. |
| SAT allgemein | Keramatipour, arXiv:2604.23037; SAT-Formulierungen und experimentelle Schwierigkeiten. | SAT allein ist keine neue Forschungsidee; negative Laufzeitberichte sind keine mathematische Unmöglichkeit. |
| Externe Notiz „sign-involution“ | YesterdaysLemon, verification/wave31-literature-audit/audit.md, insbesondere §6: diagonale Vorzeichenoperation auf 231 Dreiecken. | Anderes Objekt als unsere Knotenpermutation der Ordnung 2. Die Notiz liefert weder die C2-Modellspezifikation noch einen C2-Ausschluss. Nur diese konkrete Überschneidung geprüft, nicht das gesamte Repository. |
| 42-Paar-Modell, Doppelmatching und Spektrum D | In SPEZIFIKATION.md aus den vollständigen Gleichungen bewiesen. Die begrenzte Suche fand keinen identischen Satz. | Status: hergeleitete Konsequenzen, Neuheit ungeklärt; kein neuer Ausschluss. |

## Primärquellen und untersuchte Fundstellen

1. [Makhnev, Symmetric graphs and their automorphisms, PDF-Seiten 13–16](https://www.math.uni-bielefeld.de/~baumeist/sommerschule/makhnev.pdf).
2. [Makhnev–Minakova, Originalpublikation, DOI](https://doi.org/10.1515/156939204872374). Volltextabruf hier fehlgeschlagen.
3. [Crnković–Maksimović, §7](https://cdm.ucalgary.ca/article/download/62323/54015/204856).
4. [Cesarz–Woldar, veröffentlichte Fassung 2025](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf).
5. [Lou–Murin, MIT PRIMES, §6](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf).
6. [Thakkar, arXiv:2608.11211v1, §§4–5](https://arxiv.org/html/2608.11211v1).
7. [Keramatipour, arXiv:2604.23037](https://arxiv.org/abs/2604.23037).
8. [Externe Wave31-Originalnotiz, §6](https://github.com/YesterdaysLemon/conway-99-research/blob/main/verification/wave31-literature-audit/audit.md). Abgerufen am 13. September 2026; keine Übernahme des Fremdcodes.

Die Arbeit am Grundmodell ist durch diese Überschneidungen als notwendige Implementierungsarbeit eingeordnet. Eigenständiger Code für die kleine Kontrollrechnung wurde neu geschrieben; fremde Algorithmen wurden nicht als eigene Erfindungen ausgegeben. Die beschriebene Literatur wurde nicht insgesamt rechnerisch reproduziert.

## Suchumfang und Grenzen

Zusätzlich zu den konkreten Quellen wurden unter anderem folgende Ausdrücke gesucht: Makhnev Minakova 99 14 1 2 involution fixed vertex; Conway involution 42 10; Conway involution signed graph; Conway involution perfect matching; Conway involution 10-regular; 99,14,1,2 involution quotient; sowie gezielt die Wave31-Notiz. Viele Treffer betreffen die sporadischen Conway-Gruppen und sind für diese Frage irrelevant. Ein fehlender Suchtreffer beweist keine Originalität. Kostenpflichtige Datenbanken, unveröffentlichte Manuskripte und sämtliche nichtenglischen Quellen sind nicht vollständig erfasst.

## Forschungsentscheidung

Der angekündigte erste Schritt ist abgeschlossen: C2-Scope und direkte Modellgleichungen sind festgelegt; die vollständige Plus/Minus-Darstellung samt Kopplung liegt vor. Als nächste Implementierung dient ein deterministischer zertifikatsfähiger Referenzencoder. Der erste Vergleich soll den praktischen Nutzen des bewiesenen Doppelmatchings gegenüber derselben Baseline ohne explizite redundante Matchingbedingungen messen. Es wird keine neue Ausschlussaussage aus bloßer Modellverkleinerung oder Pilot-Timeouts abgeleitet.

## Ergänzung 19. September 2026 nach externem C2-Review

Der [Abgleich und Fortsetzungsplan](../symmetries_plan_20260919/ABGLEICH_UND_PLAN.md) enthält die nachgeholten Quellenprüfungen. Die ursprüngliche Notiz bleibt als datierter Stand erhalten.

- Crnković–Maksimović, Sätze 7.1–7.3, wurden im Volltext geprüft: C3 ist fixpunktfrei; Gruppen der Ordnung 6 und 9 sind ausgeschlossen. Zusammen mit Cesarz–Woldar Kor. 3.13 bleibt die bisherige Liste 1,C2,C3 bestehen, unter Verwendung der publizierten Ausschlüsse.
- Ishida, arXiv:2606.29183 PDF v2 (8. Juli 2026), §8.4 ergänzt den Quellenbestand. Die schwächere C3-Alternative einschließlich K3 widerlegt den stärkeren Satz 7.3 nicht. Sein neuer allgemeiner Beweis wurde hier nicht vollständig auditiert.
- Thakkars 48h-Experiment gehört laut §5 zu C7, nicht C2. Es ist keine unabhängige 48h-C2-Benchmarkbestätigung.
- Anđelić–Koledin–Stanić, DOI 10.7151/dmgt.2279, eröffnet eine konkrete Literaturspur zu regulären signed graphs mit drei Eigenwerten; bislang kein auf unseren Fall anwendbarer Ausschlusssatz.
- Makhnev–Minakova: Originalbeweis weiterhin nicht intern auditiert; erneuter DOI-Abruf technisch gescheitert. Veröffentlichtes Literaturresultat und eigene Reproduktion bleiben getrennt.
