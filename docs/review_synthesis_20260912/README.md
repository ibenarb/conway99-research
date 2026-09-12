# Veröffentlichung und Reproduktion

Maßgeblich: [FINALES_RESUEMEE.md](FINALES_RESUEMEE.md). Der ältere Forschungsbericht bleibt als Detailbericht erhalten; seine vorläufige Schlusszahl 40 wird hier durch 26 ersetzt.

## Zertifikate ohne Zusatzinstallation

Aus dem Projektwurzelverzeichnis:

`python3 src/research_20260912/replay_tau6_exact.py`

`python3 src/review_synthesis_20260912/verify_review.py`

Der erste Prüfer validiert die ursprüngliche Abdeckung und 116 Ausschlüsse, der zweite die Reviewer-Separationszertifikate, 26 Profilzeugen und die Vereinigungsmenge. Zusammen ergeben sie 130 ausgeschlossene und 26 binär-Gram-mögliche Typen. Beide benötigen nur die Standardbibliothek. `verify_review.py` prüft Umnummerierungen explizit und setzt keine Übereinstimmung der Atlasindizes voraus.

## Zusätzliche Untersuchungen

Paketversionen: `docs/research_20260912/requirements.txt`. Keine produktiven Controller werden gestartet.

`python3 src/review_synthesis_20260912/check_lifts.py`

`python3 src/review_synthesis_20260912/check_alignment.py`

`python3 src/review_synthesis_20260912/check_remaining_lp.py`

Die beiden ersten Skripte prüfen die beschriebenen endlichen Kontrollen beziehungsweise das exakte Ausrichtungsgegenbeispiel. Der LP-Pilot löst 26 kleine Relaxationen mit höchstens zehn Sekunden Solverzeit pro Typ. Numerische Machbarkeit wird nur dann als exakt geführt, wenn die nachträgliche Bruchrekonstruktion alle Gleichungen exakt erfüllt. Er überschreibt ausschließlich seine eigene Ergebnisdatei.

K66 benötigt das im ursprünglichen Forschungsbericht referenzierte PromptA-Paket:

`python3 src/review_synthesis_20260912/check_k66_domain.py /PFAD/ZUM/ENTPACKTEN/PromptA`

Alle Ergebnisse stehen unter `results/review_synthesis_20260912`. Die Liste der 103 Zyklentypen stammt aus `o3_generic_core.all_types(6)`, gefiltert mit `4 not in part`. Die gespeicherte Kennzeichnung zweier bereits ausgeschlossener Zyklentypen übernimmt den historischen Zertifikatsstand; sie behauptet keinen erneuten Zertifikatslauf.

## Herkunft und verbleibende Reproduktionsgrenzen

Die beiden JSON-Dateien unter `data/review_synthesis_20260912` sind unveränderte Reviewer-Daten. Der Eingangshash und die Liste fehlender Dateien stehen in `reviewer_package.json`. Die zusätzlichen BvLS- und 120-Paar-Messungen des Reviewers sind damit nicht vollständig reproduzierbar und wurden nicht als verifizierte eigene Resultate veröffentlicht. Die vollständige ungeprüfte Reviewer-Erzählung wird nicht als Ergebnisquelle in diesen Git-Zweig kopiert.

Das Downloadpaket enthält die neuen Dateien, die notwendigen früheren Forschungsdateien und unveränderte Referenzdaten des Basiscommits. Sein Git-Bundle enthält beide Forschungscommits auf Basis `052611b67ee9d083634eaeb5a0de2f2960722fa2`. Große Original-CNFs und fremde Publikationsvolltexte werden nicht dupliziert.
