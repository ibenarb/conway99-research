# Abschlussprüfung für k66_s1_t225

Stand: Prüfer vorbereitet, vollständiger Ryzen-Lauf noch ausstehend. Dieses Dokument meldet noch keinen abgeschlossenen K66-Beweis.

## Ziel und vorhandene Beweiskette

Die mathematische Ableitung und Encoder-Reproduktion sind in `MATHEMATISCHER_AUDIT.md` und den Ergebnissen am Commit `a85aabc475116c6cb5fa39a10d281767ab6f7cf5` dokumentiert. Der neue Prüfer `src/k66_encoder_audit_20260913/close_k66.py` schließt die beiden noch offenen Prüfungen: die 223 arithmetischen Ausschlüsse und die vollständige Bahnenüberdeckung.

Die bereits geprüften 23 Restfälle beruhen auf 167 byteidentischen CNF-Reproduktionen, einschließlich 125 Profilen der sieben Hauptwurzeln. Die 28 zusätzlichen Cake-Replays sind mit den reproduzierten Eingaben verknüpft. Für die 897 Hauptblätter liegen geprüfte Dateiintegrität, vollständige binäre Überdeckung und archivierte Cake-Bestätigungen vor; diese 897 Beweise wurden im Audit nicht neu abgespielt. Diese Herkunft bleibt auch in der Abschlussaussage ausdrücklich erhalten.

## Vollständigkeit der endlichen Fallmenge

Die drei angehängten Vierergruppen besitzen jeweils die feste innere Paarung. Zwischen je zwei Gruppen liegt ein perfektes Matching. Damit werden sämtliche beschrifteten Möglichkeiten durch drei Permutationen aus S4, also 24³ = 13.824 Codes, erfasst. Der Prüfer wendet vor dieser Aufzählung keinen Zeilen-, Gram- oder Profilfilter an.

Die lokale Gruppe wird unmittelbar als die acht Permutationen bestimmt, welche die feste Paarung erhalten. Ihre Wirkung auf die 36 geordneten Paare von Zweiermengen ergibt sieben lokale Typen. Die geordneten Dreiertupel dieser Typen, Gruppenvertauschungen und die gemeinsame Vertauschung der beiden T-Positionen reproduzieren die kanonische Bezeichnung k66_s1_t225, ihre 96 rohen Gruppenmuster und die Zellen [0,5,5,8].

Für das feste K66-Gerüst werden alle 6·8³·2 = 6.144 entsprechenden Permutationen der 14 Positionen geprüft. Genau 64 sollen das Gerüst erhalten. Identität, Inversen, Abschluss und Kovarianz der rechten Seite der Gram-Gleichung werden ausdrücklich geprüft. Die Wirkung auf Crossmatchings wird direkt durch Umnummerieren der zwölf Kanten berechnet. Jede Wirkung muss eine Bijektion der 13.824 Codes sein.

Die gespeicherten Bahnen enthalten sämtliche Mitglieder, sind disjunkt und überdecken alle Codes. Bahnenlängen und Punktstabilisatoren sowie eine separate Fixpunktzählung nach Burnside müssen übereinstimmen und genau 246 Bahnen ergeben. Die Menge ihrer minimalen Codes muss exakt der disjunkten Vereinigung der 223 Ausschlüsse und 23 Restfälle im fest gepinnten Manifest entsprechen. Zusätzliche Symmetrien wären für diesen Vollständigkeitsbeweis nicht erforderlich: Schon die geprüfte Gruppe und ihre vollständige Partition genügen.

## Arithmetischer Widerspruch

Für jeden Vertreter wird H aus dem festen Gerüst und den drei Matchings neu aufgebaut. Der Prüfer berechnet unmittelbar

G = C_H − H² − H,

wobei (C_H)ᵢⱼ = 12δᵢⱼ + 6 − 3·[i,j liegen in derselben angehängten Vierergruppe]. Aus der bereits hergeleiteten Quotientengleichung folgt notwendig G = ZᵀZ. Daher muss jeder Hauptminor von G nichtnegativ sein.

Für jeden der 223 Ausschlüsse wird der im Manifest angegebene Hauptminor mit rationaler Gauß-Elimination und Zeilenpivotierung neu berechnet. Das Verfahren ist unabhängig vom historischen Bareiss-Verfahren. Der neue ganzzahlige Wert muss exakt dem gespeicherten Wert entsprechen und strikt negativ sein. Wegen der geprüften Kovarianz gilt der Widerspruch für die ganze jeweilige Bahn.

Für die 23 übrigen Vertreter werden die positive Semidefinitheit und der Rang exakt geprüft, einschließlich der Nullzeilenbedingung bei einem Nullpivot. Erwartet werden vier Matrizen vom Rang 11 und neunzehn vom Rang 12. Matching-Codes und sämtliche 254 kanonischen S/L-Einheitsbelegungen werden mit dem Manifest verglichen. Die lokalen Encoder-Ergebnisse werden in exakt dieselbe kompakte Fassung wie bei ihrer Veröffentlichung überführt. Deren SHA-256-Werte müssen den bereits gesicherten Werten entsprechen. Entfernt werden ausschließlich die damals ausgelassenen Felder rounds.before, rounds.after und cnfs.depends_on_earlier_removed; die lokalen Dateien bleiben unverändert.

## Abschlusskriterium und Ausführung

Erst wenn der Ryzen-Lauf `K66_ARITHMETIC_AND_ORBIT_COVERAGE_PASS` liefert und die sechs gespeicherten Ergebnisdateien überprüft sind, kann der Schluss zusammengesetzt werden: Jeder K66-Kandidat gehört einer der 246 Bahnen an; 223 sind durch negative Hauptminoren ausgeschlossen; die verbleibenden 23 sind durch die geprüften notwendigen Encoder-Bedingungen und die zugehörige UNSAT-Beweiskette ausgeschlossen. Daraus folgt die Nichtexistenz einer Realisierung des Falls k66_s1_t225 innerhalb der dokumentierten strukturellen Voraussetzungen. Das ist keine globale Nichtexistenzaussage für SRG(99,14,1,2).

Der Prüfer verwendet nur die Python-Standardbibliothek sowie gh/git für kleine, fest gepinnte Vorgängermetadaten und die Ergebnissicherung. Er startet keine SAT-Suche und öffnet keine Produktionsbeweisdateien. Originaldaten bleiben unverändert. Ergebnisse und wiederaufnehmbare Prüfpunkte entstehen unter `~/conway99_workspace/k66_completion_proof_v1_0_1`. `--publish` sichert sechs kompakte JSON-Dateien auf dem Forschungsbranch mit gewöhnlichem Commit/Push und vollständiger Rückdownloadprüfung. Die kleinen Kontrollen können separat mit `--controls-only` ausgeführt werden; sie ersetzen den vollständigen Lauf nicht.

## Korrektur 1.0.1

Der erste Ryzen-Lauf brach mit `pinned residual result bytes` ab. Version 1.0.0 verglich irrtümlich den Hash eines veröffentlichten kompakten Berichts mit der ausführlichen lokalen Datei. Version 1.0.1 prüft die oben beschriebene identische Veröffentlichungsprojektion. Die Hashbindung wird beibehalten. Die Projektion wurde gegen alle 23 gesicherten Berichte geprüft; zusätzliche Kontrollen bestätigen das Entfernen der ausgelassenen Felder ohne Eingabemutation. Ein eigenes Ausgabeverzeichnis verhindert die Vermischung von Prüfpunkten verschiedener Programmversionen. Der vollständige erfolgreiche Ryzen-Lauf steht weiterhin aus.
