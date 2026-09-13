# Forschungszweig memetik

Stand: 13. September 2026. Eigenständige memetische Forschung innerhalb Conway_99.

Aktiver Git-Zweig: `memetik`. Abgezweigt von `31c563f6ba460227c6ae4eebcd519257fcba5ad4` auf `research/algebra-memetic-20260912`. Dieser Stand enthält den Office-Piloten 0.2.0 und die nachfolgenden geprüften Forschungsergebnisse. Die gemeinsame Historie bleibt erhalten; die zukünftige Entwicklung ist getrennt.

## Einstieg

- [Bewertung und Pilotentwurf](docs/memetik/PILOTENTWURF_20260913.md)
- [Vertrag für neue Gründer](docs/memetik/GRUENDERVERTRAG.md)
- [Unabhängiger Gründerprüfer](src/memetik/audit_founders.py)
- [Frische Prüfergebnisse](results/memetik/founder_audit_20260913.json)

## Arbeitsaufteilung

| Bereich | Zuständigkeit |
| --- | --- |
| `memetik` | Neue Gründer, Mutation, Selektion, Rekombination, lokale Erreichbarkeit, Pilotenauswertung |
| `research/algebra-memetic-20260912` | Bisheriger Forschungszweig, aktuell Symmetrie- und Ausschlussarbeit |
| `memetic/office-v0.1.0-20260911`, `memetic/office-v0.2.0-multinorm-20260911` | Unveränderte historische Implementierungsstände |
| `reviews/YYYYMMDD-...` | Neue externe Reviews: unveränderte Eingänge und getrennte Bewertungen gemäß Projektregel |

Neue memetische Arbeiten liegen unter `src/memetik`, `docs/memetik`, `data/memetik`, `configs/memetik`, `results/memetik` und `manifests/memetik`, jeweils erst bei tatsächlichem Inhalt. Vorhandene v1/v2-Pfade bleiben wegen reproduzierbarer Importe und historischer Konfigurationen erhalten. Große Rohdaten bleiben in externen Laufverzeichnissen; ausgewählte Evidenz mit Manifest kommt in Git.

Gemeinsam genutzte geprüfte Änderungen werden gezielt mit festen Commitreferenzen übernommen. Keine pauschale Übertragung von Symmetrieannahmen in die memetische Suche. Ein Beweis gilt nur in seiner ausgewiesenen Domäne; eine heuristische Beobachtung wird nicht als Ausschluss geführt.

Diese Einrichtung ändert keine laufenden Prozesse und keinen Checkout auf den Rechnern des Nutzers. Der Pilot ist spezifiziert, noch nicht implementiert oder gestartet. Git ist die dauerhafte Referenz, nicht die Verfügbarkeit früherer Chatnachrichten.
