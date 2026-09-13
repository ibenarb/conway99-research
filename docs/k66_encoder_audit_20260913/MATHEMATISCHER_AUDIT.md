# K66: mathematischer Encoder- und Reduktionsaudit

Stand: 13. September 2026, nach bestandener Ryzen-Reproduktion.
Ergebniscommit: `b38d4cb755505a67c01bcf87aff0e2dbf1f79524`.
Geltungsbereich: ausschließlich `k66_s1_t225` innerhalb des Ordnung-3-Zweigs
mit fixiertem Dreieck. Kein globaler Ausschluss von srg(99,14,1,2).

## 1. Ergebnis und Beweisstatus

Die unten hergeleiteten Profil-, Projektor-, Paar- und Star-Bedingungen sind
notwendige Bedingungen des beschriebenen Quotientenmodells. Die untersuchten
CNF-Restriktionsfamilien setzen diese Bedingungen bei nichtnegativen ganzzahligen
Gewichten korrekt um. Die Multiplizitätsschranke zwei lässt sich kombinatorisch
beweisen; sie muss nicht aus einem fremden Kommentar übernommen werden.

Das ist ein mathematischer Schluss unter den ausdrücklich angegebenen
Quotientenannahmen. Die angeforderten 125 Star-CNFs und sieben Hauptlaufwurzeln sind jetzt
**vollständig byteidentisch reproduziert und an die gesicherten Eingabehashes
gebunden**. Alle 23 konkreten Profildomänen und Paarmasken stimmen mit der
unabhängigen Ganzzahlgegenrechnung überein. Bei den zusätzlich reproduzierten
zwölf Star-CNFs von v4_09232 fehlt im neuen Ergebnis noch die ausdrückliche
Verknüpfung mit den früheren Cake-Replay-Hashes; diese Restpflicht ist separat
aufgeführt. Es wird kein vollständiger K66-Fallabschluss behauptet.

| Gegenstand | Status dieser Fassung |
| --- | --- |
| Notwendigkeit der verwendeten Restriktionsfamilien im K66-Quotientenmodell | Mathematisch hergeleitet, Abschnitte 3–8 |
| Allgemeine BDD-Übersetzung für ihren tatsächlichen Eingabebereich | Mathematisch begründet; 945 kleine Projektionskontrollen rechnerisch bestanden |
| Preflight-Quelltext im ursprünglichen PYZ und Repository | SHA256-/Blob-Gleichheit anhand neuer Quellensammlung festgestellt |
| Acht zentrale Definitionen in Preflight und Deep7 | AST-Gleichheit rechnerisch festgestellt |
| Keine zusätzlichen Deep7-Entfernungen | In den neu eingesammelten Verlaufsdaten protokolliert |
| Beliebig genaue Gegenrechnung aller konkreten Profile und Paarmasken | Für alle 23 Fälle rechnerisch bestanden |
| 125 Star-CNFs und sieben Hauptlaufwurzeln erneut reproduziert | Vollständige Byte- und SHA256-Gleichheit; gesicherte Eingabehashes stimmen |
| Zusätzliche zwölf Star-CNFs und reduzierte Global-CNF für v4_09232 | Byteidentisch; ausdrückliche Verknüpfung der zwölf Profilhashes mit dem früheren Replay noch offen |
| 15 unreduzierte R2-Global-CNFs | Byteidentisch; Hashes stimmen mit separatem cert15_manifest überein |
| 223 arithmetische Ausschlüsse und Vollständigkeit der 246 Bahnen | Eigenständige offene Pflichten |

Es wird hier kein Produktionsbeweis erneut geprüft. Der gesicherte Neustartstand
umfasst 897 Hauptlaufblätter mit Integritäts- und archivierten Cake-Prüfungen,
28 tatsächlich erneut geprüfte vorhandene Beweise und 125 neu erzeugte,
Cake-geprüfte Profilbeweise. Diese Feststellungen werden als dokumentierter
Ausgangspunkt verwendet, nicht als Tätigkeit dieses Audits ausgegeben.

## 2. Quellen und Herkunft

Quellensammlung: Commit `0a54ce594f89b948c77200328f5de7379bae4806`,
`data/k66_encoder_audit_20260913/source_evidence/SOURCE_INDEX.json`.
Der Ryzen meldete 126 Nutzdateien plus Index, ohne Sammelfehler und mit
vollständigem Rückdownloadvergleich sämtlicher 127 Dateien.

| Funktion | Originalherkunft | Quelldatei im Evidenzordner |
| --- | --- | --- |
| Star-Preflight, Profilaufbau, Global-Encoder | `/mnt/c/Users/rb/Downloads/Conway99_K66_NeighborStar_Preflight_20260909.pyz!__main__.py` | `e88199345481ed6e.py` |
| Deep7-Star-Fortsetzung und Global-Encoder | `/mnt/c/Users/rb/Downloads/Conway99_K66_NeighborStar_Deep7_Autonomous_20260909.pyz!__main__.py` | `689553cc7f9df62e.py` |
| Unreduzierte Profile-Conflict-CNFs | `/mnt/c/Users/rb/Downloads/Conway99_K66_ProfileConflict_CNF_Scout_20260909_r2.pyz!__main__.py` | `ff29f19d0f5a564a.py` |
| Übergeordnetes lokales Manifest | K66-Lauf, `manifest.json` | `63a7807c55fb3a9c.json` |
| Deep7-Verlauf | Deep7-Lauf, `star_history.json` | `7b6e09c650d1ea37.json` |
| Deep7-Ergebnis | Deep7-Lauf, `summary.json` | `8d18d6cd5b24d750.json` |

SHA256 der drei Encoderquellen:

- Preflight: `e616de8e49bd678ac9425afb7bf6f067507827780c8746bfe0e184058b129088`.
- Deep7: `dad41b4b5114377cd2327774d2f6dcd1acc67090b8965faa08e641e149e78782`.
- R2: `914ff612545d0a005a4a147af05db521d68dcd3dd3e0ba73261461f94ac5d24e`.

Die Preflight-PYZ-Quelle stimmt mit
`src/k66_star125_20260913/original_preflight.py` überein. Ihr Git-Blob ist
`f76c01b1faaf1dede0c48c3753887095096be9e8`.

Preflight und Deep7 besitzen identische ASTs für `CNF`, `build_H`,
`encode_global`, `inverse_minor`, `make_profiles`, `prepare_case`, `require`
und `write_dimacs`. `build_star_cnf` verwendet andere lokale Bezeichner und
eine anders geschriebene, inhaltlich gleiche Gewichtsschleife. Der neue Prüfer
reproduziert die historischen Preflight-Star-CNFs direkt aus der Preflight-Quelle.
Für die Global-CNFs verwendet er zusätzlich die eigene Deep7-Quelle.

Die vorhandenen Downloads allein beweisen nicht, welches Paket damals gestartet
wurde. Die Kombination aus Quellpaket, lokalen Metadaten und vollständiger
Reproduktion der zertifizierten Eingaben soll diese verbleibende Provenienzlücke
für die mathematisch relevanten Dateien schließen.

## 3. Das zugrunde liegende Quotientenmodell

Sei ein srg(99,14,1,2) mit einem Automorphismus der Ordnung drei und genau einem
fixierten Dreieck gegeben. Die übrigen 96 Knoten bilden 32 Dreierorbits.
Im betrachteten Zweig heißen die zwölf an die Fixpunkte angeschlossenen Orbits
A0, A1, A2, je vier; T besteht aus zwei dreieckigen Orbits; U aus 18 gewöhnlichen,
unangeschlossenen Orbits. Die vorgelagerte Herleitung dieser Orbitklassifikation
ist in der Projektquelle `O3_fixed_triangle_internal_model.md` dokumentiert.

Die symmetrische 32×32-Orbitmatrix P zählt Nachbarn pro Knoten zwischen
Dreierorbits. Die SRG-Identität A²+A=12I+2J liefert nach Abzug der Beiträge
über die drei Fixpunkte

    P² + P = 12I + 6J - 3 diag(J4,J4,J4,0_20).

Der Term 3 entsteht, weil zwei Dreierorbits derselben Anschlussgruppe den
zugehörigen Fixpunkt gemeinsam haben: im Quotientenprodukt steht 1·3.
Zwischen unterschiedlichen Anschlussgruppen fehlt dieser Beitrag.

Die Fixpunkt-zu-Orbit-Gleichungen geben für jedes v in U

    sum_{a in Ar} P_av = 2  für r=0,1,2.

Die Diagonal- und Gradgleichungen ergeben für v in U genau zehn Einser und
zwei Zweier außerhalb der Diagonale; die Diagonale ist null. Für einen
Dreiecksorbit gibt es zwölf Einser, keine Zweier und Diagonale zwei.
Für einen angeschlossenen Orbit ergeben sich elf Einser und ein Zweier.
Alle nichtdiagonalen Einträge gehören damit zu {0,1,2}.

Innerhalb jeder Ar sowie zwischen je zwei Anschlussgruppen ist die gewichtete
Zeilensumme eins. Daher sind die dortigen Blöcke einfache Matchings. Im
K66-Manifest sind die inneren Matchings, die drei Crossmatchings und sämtliche
Anschlüsse an T fixiert.

Mit den ersten 14 Positionen A0∪A1∪A2∪T schreiben wir

$$
P=\begin{pmatrix}H&Z^\top\\ Z&B\end{pmatrix}.
$$

wobei Z 18×14 und B 18×18 ist. H ist vollständig durch den Manifestfall bestimmt.
B ist symmetrisch mit Diagonale null. Aus der Blockmultiplikation folgen exakt

    ZᵀZ = G := C_H - H² - H,
    BZ = 6J_(18,14) - Z(H+I),                              (S1)
    B² + B + ZZᵀ = 12I_18 + 6J_18.                        (S2)

Hier ist C_H=12I_14+6J_14-3diag(J4,J4,J4,0_2).
Das sind die tatsächlich benötigten Ausgangsgleichungen; eine Nummerierung in
Astra-Unterlagen ist für die Begründung nicht erforderlich.

## 4. Profile, Zellen und Multiplizitäten

Eine Zeile z von Z hat in jedem der drei Viererblöcke Summe zwei. Sie besteht
dort entweder aus zwei Einsern (sechs Möglichkeiten) oder einem Zweier
(vier Möglichkeiten). Sei ell die Zahl der Zweier in den ersten zwölf
Koordinaten. Wegen der insgesamt zwei Zweier pro U-Zeile gilt ell≤2.
Die letzten beiden Koordinaten sind Bits; ihre Summe sei q.

Damit gibt es 10³−4³=936 Zwölfkoordinatenprofile und mit den vier T-Bitpaaren
3744 globale Profil-IDs. Die Reihenfolge ist: die sechs lexikographischen
Zweier-Teilmengen, dann die vier Einzelpositionen mit Wert zwei, dreifaches
kartesisches Produkt ohne ell=3; anschließend die Zellen (1,1),(1,0),(0,1),(0,0).
Die globale ID ist `936*cell + index_within_936` und bleibt bei Filtern unverändert.
Ein lokaler Index bezeichnet dagegen die Position in der gefilterten Liste.

Es gelten

    ||z||² = 6 + 2ell + q,
    d_S(B,z) = 4 + 2ell - q,
    d_L(B,z) = 2 - ell.                                    (S3)

Die zweite und dritte Formel folgen durch Abzug der bereits in z enthaltenen
6−2ell+q Einser und ell Zweier von den zehn Einsern und zwei Zweiern der
vollständigen U-Zeile. (S1) zusammen mit (S3) rekonstruiert die im Star-Code
als Astra-(8)–(9) angesprochenen Gleichungsfamilien ihrem Inhalt nach.

Für K66 gelten s=P_T1,T2=1 und genau ein gemeinsamer Anschluss in A.
Jeder T-Orbit besitzt 12−6−s=5 Nachbarn in U. Die T-Paargleichung lautet

    common_U(T1,T2) = 6 - 5s - common_A(T1,T2) = 0.

Daher sind die Zellgrößen genau (0,5,5,8). Die Profile mit q=2 sind unmöglich.

**Multiplizität eins.** Für verschiedene u,v folgt aus (S2) wegen
(B²)_uv≥0

    z_u·z_v + B_uv ≤ 6.                                    (S4)

Identische Profile mit ell+q>0 hätten Skalarprodukt 6+2ell+q>6.
Sie können daher höchstens einmal auftreten.

**Multiplizität höchstens zwei.** Für ell=q=0 ist das Skalarprodukt identischer
Profile sechs. Drei solche Zeilen würden nach (S2) paarweise B_uv=0 und
(B²)_uv=0 erzwingen. Jede hat nach (S3) vier einfache und zwei doppelte
B-Nachbarn, also sechs verschiedene Nachbarn. Wegen (B²)_uv=0 und der
Nichtnegativität der B-Einträge sind diese drei Nachbarschaftsmengen paarweise
disjunkt. Sie müssten zusammen 18 Positionen belegen, könnten aber keinen der
drei identischen Profilträger enthalten. Es stehen nur 15 Positionen zur
Verfügung: Widerspruch. Somit ist die im Code verwendete Schranke zwei notwendig.

Wenn die Paarfilter auch für zwei verschiedene Träger desselben Profils keinen
B-Wert zulassen, darf diese Schranke weiter auf eins gesenkt werden.
Der Diagonaleintrag der Profil-Paarmaske meint hier zwei verschiedene Knoten
mit gleichem Profil, nicht B_uu.

## 5. Einzelprofilfilter und exakte Projektorherleitung

Aus G=ZᵀZ folgt G≥0. Für jeden vorhandenen Profilträger gilt komponentenweise
z_i z_j≤G_ij. Außerdem liegt z im Zeilenraum von G.

Wähle eine Menge I linear unabhängiger Spalten von Z und setze R=(G_II)⁻¹.
Für vorhandene Profilträger ist

    Π = Z_I R Z_Iᵀ

der orthogonale Projektor auf col(Z). Insbesondere 0≤Π_uu≤1.
Für z ist Π_uu=z_Iᵀ R z_I. Die im Code benutzte Bereichsprüfung

    z_Iᵀ R G_I,* = zᵀ

und die Leverageschranke z_Iᵀ R z_I≤1 sind deshalb notwendig.

Setze a=(1,1,1,1,0,…,0)ᵀ und

    M = -(H+I) + 3·1_14 aᵀ.

Weil Za=2·1_18, ist (S1) genau BZ=ZMᵀ. Der Raum col(Z) ist daher B-invariant.
Da B symmetrisch ist, ist auch sein orthogonales Komplement invariant.
Ferner liegt 1_18 in col(Z). Für E=I−Π gilt deshalb E1=0 und ZᵀE=0.
Die Einschränkung von (S2) auf im(E) liefert

    (B|im(E))² + B|im(E) = 12I.

Ihre Eigenwerte liegen folglich in {3,−4}. Mit K=BΠ=ΠB und C=B−K sind

    C + 4E ≥ 0,       3E − C ≥ 0.                          (P1)

Für zwei Profile z,w schreiben wir

    delta(z,w) = z_Iᵀ R w_I,
    eta(z,w)   = z_Iᵀ R (Mw)_I,
    lev(z)     = delta(z,z),
    beta(z)    = eta(z,z).

Bei tatsächlich vorhandenen Profilen sind dies Π_uv, K_uv, Π_uu und K_uu.
Da B_uu=0, liefern die Diagonalen von (P1)

    -3(1-lev(z)) ≤ beta(z) ≤ 4(1-lev(z)).                   (P2)

Die beiden nichtnegativen 2×2-Hauptminoren von (P1) ergeben für b=B_uv

    (b-eta(z,w)-4delta(z,w))²
        ≤ [4(1-lev(z))-beta(z)] [4(1-lev(w))-beta(w)],       (P3)

    (eta(z,w)-b-3delta(z,w))²
        ≤ [3(1-lev(z))+beta(z)] [3(1-lev(w))+beta(w)].       (P4)

Die Codegrößen `lev`, `beta`, `delta`, `eta` sind diese Größen multipliziert
mit dem gemeinsamen positiven Nenner `den`. Multiplikation von (P2) mit den
und von (P3)–(P4) mit den² liefert exakt die implementierten Ganzzahlvergleiche.
Vorzeichen und die Faktoren drei bzw. vier sind damit eigenständig hergeleitet.

## 6. Vollständige Einordnung der Paarfilter

Für jeden Kandidaten b∈{0,1,2} prüft `allowed`:

1. (S4), also z·w+b≤6.
2. Bei b=2 müssen beide Profile ell≤1 haben, weil sonst ihre zwei verfügbaren
   doppelten Nachbarn bereits vollständig in A liegen.
3. Die beiden Projektor-Minorbedingungen (P3) und (P4).
4. Einen Sonderfilter bei b=1, ell(z)=ell(w)=0, q(z)=q(w)=2 und disjunkten
   Anschlussprofilen.

Die ersten drei Bedingungen sind oben bewiesen. Der vierte Filter kann im
vorliegenden Fall nie greifen: q=2 wurde aufgrund der leeren Zelle vollständig
entfernt. Seine allgemeine Notwendigkeit wird hier weder benötigt noch behauptet.
Der unabhängige Prüfer lässt ihn gerade deshalb weg und verlangt ausdrücklich,
dass keine q=2-Profile verbleiben. Gleichheit der resultierenden Paarmasken
belegt dann zusätzlich seine Wirkungslosigkeit in allen 23 Restfällen.

Sind alle drei b-Werte verboten, können die beiden Profile nicht gemeinsam
vorkommen. Die globale CNF setzt hierfür eine Konfliktklausel. Sie verlangt
keine vollständige gegenseitig konsistente Realisierung der noch erlaubten
B-Einträge; dadurch entsteht eine zulässige Relaxation.

## 7. Star-Encoder: Variablen und Notwendigkeit

Fixiere einen tatsächlichen Träger u des Zentralprofils z. Für jeden aktiven
Profiltyp w stellt der Encoder `cap(w)` Kopien zur Verfügung, beim Zentraltyp
aber eine weniger. Das ist der notwendige Selbstabzug: u ist kein eigener
B-Nachbar. Der Profiltyp selbst bleibt in der aktiven Domäne.

Pro Kopie stehen je nach Paarmaske ein S-Bit für B_uv=1 und ein L-Bit für
B_uv=2 zur Verfügung. Wenn beide existieren, verbietet `¬S∨¬L` die doppelte
Benutzung derselben Kopie. Eine unbenutzte Kopie hat beide Bits null.
Jede tatsächliche Nachbarschaft lässt sich injektiv auf solche Kopien abbilden,
weil die Multiplizitätsschranken echte obere Schranken sind.

Die folgenden Gleichungen werden kodiert:

    sum S = 4 + 2ell(z) - q(z),
    sum L = 2 - ell(z),
    sum (S + 2L) w_k = 6 - [(H+I)z]_k,   k=0,…,13.

Die ersten beiden sind (S3), die nächsten vierzehn sind die Zeile von (S1).
Für jede T-Zelle kommt hinzu

    sum_{Kopien in Zelle c} (S+L) ≤ size(c) - 1_{z in c}.

Hier zählt S+L die Zahl verschiedener ausgewählter Nachbarn, nicht den
gewichteten Grad; die Disjunktheitsklausel macht diese Interpretation korrekt.
Auch dieser Selbstabzug ist notwendig, unabhängig vom Profil-Selbstabzug.

Nicht kodierte Nachbar-Nachbar-Verträglichkeiten schwächen das Modell.
Sie machen einen UNSAT-basierten Profilausschluss nicht unzulässig.
Die Kopien werden nicht durch eine zusätzliche Symmetriebrechung eingeschränkt.

## 8. Global-Encoder und BDD-Korrektheit

Für jeden Profiltyp steht ein Präsenzbit y zur Verfügung. Bei Kapazität zwei
kommt ein zweites Bit e mit `¬e∨y` hinzu. Die Multiplizität ist x=y+e, andernfalls
x=y. Genau die zulässigen Werte 0,1,2 bzw. 0,1 werden dargestellt.

Der Encoder verlangt alle 105 oberen Dreieckseinträge von

    sum_z x_z zzᵀ = G,

die vier Zellgleichungen

    sum_{z in c} x_z = size(c),

und für unverträgliche verschiedene Profiltypen `¬y_z∨¬y_w`.
Die Diagonalmaske wurde zuvor in die Kapazität umgesetzt. Diese Bedingungen
sind notwendig, aber keine vollständige Realisierung von B oder eines SRG.

Die BDD-Routine addiert wiederholte Gewichte desselben positiven Variablenbits,
zieht wahre Konstanten vom Ziel ab und ignoriert falsche Konstanten.
Für geordnete Bits x_i mit nichtnegativen Gewichten w_i bezeichnet ein
BDD-Zustand F(i,r) die Gleichung sum_{j≥i} w_j x_j=r. Negative Restziele und
Restziele über der Suffixsumme sind falsch; am Ende ist genau r=0 wahr.
Die Rekursion lautet

    F(i,r) ↔ [(x_i ∧ F(i+1,r-w_i)) ∨ (¬x_i ∧ F(i+1,r))].

Die vier Tseitin-Klauseln sind genau die beiden bedingten Äquivalenzen
`x_i ⇒ (v↔hi)` und `¬x_i ⇒ (v↔lo)`. Eine Einheitsklausel fordert den Wurzelzustand.
Induktion über die Tiefe beweist die Äquivalenz nach existenzieller Quantifizierung
der Hilfsvariablen. Wahrheitskonstanten werden mit Identitätsprüfungen behandelt,
damit das Python-Bool `True` nicht mit Variablennummer eins verwechselt wird.

`lo is hi` statt allgemeiner Gleichheit kann höchstens eine redundante
BDD-Zusammenfassung auslassen; die vier Definitionsklauseln bleiben korrekt.
Eine leere falsche Gleichung erzeugt eine leere Klausel, eine wahre keine.

`cardinality_leq` verwendet bei nichttrivialer Schranke L genau L zusätzliche
Einser-Slackbits und die Gleichung sum x + sum slack=L. Jede Summe von null
bis L lässt sich darstellen. Für negative L wird sofort die leere Klausel
erzeugt; bei höchstens L Eingabebits ist die Bedingung tautologisch.

Die Routine ist keine allgemeine Implementierung beliebiger vorzeichenbehafteter
Pseudo-Boolean-Gleichungen. Hier werden ausschließlich positive Variablenbits,
Bool-Konstanten, nichtnegative ganzzahlige Gewichte und ganzzahlige Ziele benutzt.
Der neue Prüfer kontrolliert diesen Eingabevertrag bei jedem tatsächlichen Aufruf.
Die Implementierung verwendet Python-Integer für BDD-Suffixsummen und Ziele;
dort tritt kein `int64`-Überlauf auf.

945 kleine erschöpfende Kontrollen über Primärbelegungen prüften alle drei
CNF-Klassen mit Nullgewichten, mehrfachen Variablen, Konstanten, leeren
Gleichungen, unerreichbaren/negativen Zielen und Zellkapazitäten. Diese Kontrollen
stützen die allgemeine Induktion; sie ersetzen sie nicht.

## 9. Reduktionskette und Profil 3520

| Wurzel | Anfang | Runde 1 entfernt | Runde 2 entfernt | Ende |
| --- | ---: | ---: | ---: | ---: |
| v4_09316 | 662 | 28 | 0 | 634 |
| v4_09317 | 677 | 34 | 1 | 642 |
| v4_09322 | 664 | 10 | 0 | 654 |
| v4_09323 | 720 | 12 | 0 | 708 |
| v4_09331 | 632 | 24 | 0 | 608 |
| v4_09332 | 734 | 10 | 0 | 724 |
| v4_09333 | 747 | 6 | 0 | 741 |
| Summe | 4836 | 124 | 1 | 4711 |

Die Zahlen sind aus den neu gesammelten Quellen und Metadaten rekonstruiert;
sie sind jetzt zusätzlich durch die vollständige lokale Reproduktion bestätigt. Der zusätzliche Fall
v4_09232 beginnt mit 350 Profilen, entfernt zwölf in Runde eins und endet mit 338.

Im Preflight wird `ACTIVE` während einer Runde nicht geändert. Erst nachdem
sämtliche Aufgaben beendet sind, werden die UNSAT-Profile gemeinsam entfernt.
Daher kann Runde eins keinerlei Ausschluss derselben Runde voraussetzen.
Induktiv ist jede spätere Entfernung gerechtfertigt, sobald ihre CNF notwendig
ist und ihre Unerfüllbarkeit mit den zuvor gerechtfertigten Domänen feststeht.
Die Dateien für erfüllbare oder nicht abgeschlossene Scouts werden gelöscht;
behalten werden nur die damaligen UNSAT-Kandidaten. Der neue Prüfer gleicht
exakte Dateimengen und Rundenzahlen ab.

Profil 3520 liegt in Zelle (0,0), mit Teilindex 712. Seine Zeile ist

    (0,2,0,0 | 1,0,0,1 | 0,0,2,0 | 0,0).

Es hat ell=2, q=0, also acht einfache und keine doppelten B-Nachbarn.
Die ID-Zuordnung und diese Werte wurden unabhängig durch kleine Enumeration
berechnet. Sein Ausschluss in Runde zwei von v4_09317 darf nur die 34
Entfernungen aus Runde eins desselben Falles voraussetzen. Der Prüfer speichert
diese konkrete Vorgängerliste, die Domäne vor und nach der Runde und den
Bytevergleich mit der zertifizierten Profil-CNF. Er behauptet nicht, dass alle
34 Vorgänger logisch unverzichtbar sind; es ist eine hinreichende Abhängigkeitsmenge.

Deep7 importiert die Preflight-Entfernungen aus den drei Rundenverzeichnissen.
Innerhalb einer Quick- oder Deep-Stufe sind Entfernungen simultan; zwischen
Quick und Deep wird die Domäne aktualisiert. Im vorliegenden protokollierten
Lauf gab es jedoch weder Quick- noch Deep-Entfernungen: 4637 schnelle SAT-Meldungen
und 74 zunächst offene, danach SAT-gemeldete Profile. Diese Meldungen sind hier
kein neuer SAT-Zeugencheck. Sie werden auch nicht als Beweis eines Ausschlusses
benötigt. Entscheidend ist, dass die endgültigen CNFs mit genau der durch die
125 zertifizierten Entfernungen begründeten Domäne reproduziert werden.

## 10. Neuer lokaler Reproduktionsprüfer

`src/k66_encoder_audit_20260913/reproduce.py` führt auf dem Ryzen aus:

- unabhängigen Profilaufbau, rationale PSD-/Rang-/Inverse-Prüfung und
  Berechnung der Filter sowie Paarmasken mit Python-Ganzzahlen;
- Vergleich mit den historischen NumPy-int64-Ergebnissen für alle 23 Fälle;
- explizite Absolutsummenschranken für die wesentlichen Matrixprodukte,
  Einzelprodukte, Summen und quadratischen Vergleiche;
- Reproduktion von 137 Star-CNFs, darunter den angeforderten 125, und von
  sieben Deep7-, acht Preflight- sowie 15 separaten R2-Global-CNFs;
- vollständigen Bytevergleich jeder erzeugten CNF, zusätzlich SHA256;
- Bindung der 125 Star-Eingaben an `k66_restart_audit_v1/inventory.json`,
  der sieben Wurzeln an das dort gebundene Hauptlaufmanifest, und der
  zusätzlichen Globalmodelle an ihre separat bezeichneten Manifesthashes;
- einzelne Ergebnisdateien, fallweise Wiederaufnahme und Status/ETA alle
  zehn Minuten; standardmäßig vier parallele Fälle;
- regulären Commit der kompakten JSON-Ergebnisse und geprüften Rückdownload.

Die neuen CNFs bleiben ausschließlich auf dem Ryzen. Es werden keine Solver
oder Produktionschecker aufgerufen. Abweichende Dateien werden aufbewahrt;
ein Byteunterschied führt zu FAIL und wird nicht automatisch als harmlose
Serialisierung oder Äquivalenz ausgegeben. Diese Unterscheidung wäre dann
anhand der konkreten Abweichung gesondert vorzunehmen.

Der historische Inversenhelfer überspringt einen Nullpivot, ohne die restliche
Schur-Zeile auf null zu prüfen. Als allgemeiner PSD-Test ist das unzureichend.
Es ist hier kein nachgewiesener Fehl-Ausschluss: Der neue unabhängige Prüfer
kontrolliert diese Zeile, die positive Pivotfolge sowie die vollständige
Rangrekonstruktion. Außerdem werden die konkreten Einzelprofil- und Paarmasken
gegen die unbeschränkte Ganzzahlarithmetik verglichen. Alle 23 Fälle bestanden;
der allgemeine Schwachpunkt des historischen Nullpivot-Tests hat in diesen
konkreten Eingaben keinen abweichenden Befund verursacht.

Entwicklungsprüfung ohne Produktionsdaten: Die 945 BDD-Kontrollen bestanden.
Kleine definite und singulär-PSD-Matrizen bestanden den Inversenprüfer;
zwei indefinite Gegenkontrollen wurden abgelehnt. Der Bytevergleich erkannte
sowohl identische als auch gezielt veränderte kleine CNFs.

## 11. Bestätigte Reproduktionsergebnisse

Die 23 einzelnen Ergebnisdateien und der Gesamtbericht wurden am festen
Ergebniscommit vollständig gelesen und auf konsistente Auditidentität,
PASS-Status, Bytegleichheit und gespeicherte Hashverknüpfungen geprüft.

| Vergleichsgruppe | Anzahl | Ergebnis |
| --- | ---: | --- |
| Star-CNFs der sieben Hauptlaufwurzeln | 125 | Byteidentisch, einschließlich Bindung an Neustart-Inventar |
| Zusätzliche Star-CNFs von v4_09232 | 12 | Byteidentisch; Replay-Hashverknüpfung noch zu ergänzen |
| Deep7-Global-CNFs | 7 | Byteidentisch, einschließlich Bindung an Hauptlaufmanifest |
| Preflight-Global-CNFs | 8 | Byteidentisch; sieben stimmen außerdem mit Deep7 überein |
| Separate R2-Global-CNFs | 15 | Byteidentisch; Hashbindung an cert15_manifest |
| Summe der Vergleiche | 167 | Alle bestanden |

Die 167 Vergleiche umfassen 160 verschiedene SHA256-Werte: Die sieben
Preflight-/Deep7-Globalmodelle sind erwartungsgemäß paarweise gleich.
Die genaue Ganzzahlgegenrechnung bestätigt vier Gram-Matrizen vom Rang elf
und 19 vom Rang zwölf. Der größte protokollierte Absolutwert bzw.
Absolutsummen-Bound ist 143046661868010000 (`v4_09332`, `second_square`).
Er liegt mehr als Faktor 64 unter 9223372036854775807, der int64-Obergrenze.
Damit sind die überprüften konkreten Rechenschritte und Masken abgesichert;
dies ist keine allgemeine Zusicherung für andere Parameter oder Encoder.

Profil 3520 wurde mit 1152 Variablen, 4200 Klauseln und 59175 Bytes
reproduziert. SHA256:
`b002e7887ebbff1813dbf60c52db1d1aae142f9bded0c9c03f8c5f504482ac23`.
Der Vergleich erfolgte vor seiner Entfernung und nach genau diesen
34 Entfernungen aus Runde eins:

    1395, 1875, 1984, 1991, 1994, 2001, 2004, 2011, 2014, 2021,
    2084, 2091, 2094, 2101, 2104, 2114, 2135, 2136, 2184, 2191,
    2194, 2204, 2214, 2284, 2291, 2294, 2304, 2314, 2495, 2519,
    2871, 3037, 3156, 3411.

Dies belegt die nichtzirkuläre, rundenweise Reproduktion. Es ist keine
Behauptung über eine minimale logische Abhängigkeitsmenge.

Der eigentliche Prüflauf benötigte laut Gesamtbericht 21 Sekunden; die
vorherige Schätzung 5–20 Minuten war deutlich zu konservativ. Der anschließende
Git-Upload und vollständige Rückdownloadvergleich wurden vom lokalen Programm
als bestanden gemeldet. Kein Produktionsbeweis wurde erneut geprüft.

## 12. Verbleibende Abschlussbedingungen

**Unmittelbar erforderlich:** die kompakten früheren Replay-Berichte
`v4_09232_cake_replay.json` und `remaining15_cake_replay.json` aus dem
Neustartverzeichnis heranziehen. Die zwölf zusätzlichen Star-Eingaben besitzen
im neuen Ergebnis `certificate_input_sha256: null`; ihre Bytegleichheit ist
bewiesen, die ausdrückliche Verbindung zum damaligen Replay fehlt in dieser
Ergebnisfassung. Auch die bereits manifestgebundenen Zusatz-Globalhashes sollen
den tatsächlich erneut geprüften Eingaben direkt zugeordnet werden. Dafür
sind nur Berichtsdaten erforderlich, kein weiterer Solver- oder Checker-Lauf.

**Danach eigenständig erforderlich:** die 223 arithmetischen Ausschlusszeugen
mit vollständiger Matrixzuordnung nachprüfen und die 246 Bahnen einschließlich
Stabilisatorwirkung, Repräsentanten, Disjunktheit und Überdeckung der 13.824
beschrifteten Crossmatchings unabhängig nachweisen. Eine bloße disjunkte Liste
223+23 erfüllt diese Pflicht nicht.

**Gesondert zu bilanzieren:** Für v4_09232 und die 15 R2-Fälle müssen die
reproduzierten Eingabehashes mit den bereits tatsächlich ausgeführten
Cake-Replays verbunden bleiben. Ein Hash aus einer Scout-Zusammenfassung
allein ist keine neue Checkerbestätigung. Für die 897 Hauptlaufbeweise bleibt
der bekannte Status „archivierte Cake-Bestätigung und Integrität geprüft,
kein Neustart-Replay“. Ein zusätzlicher Replay ist eine mögliche Verstärkung
des Vertrauensniveaus, nicht ein hier bereits erfüllter Prüfschritt.

Ein vollständiger Abschluss dieses Falls würde nur `k66_s1_t225` ausschließen.
Die übrigen strukturellen Fälle des fixierten-Dreieck-Zweigs, die anderen
Automorphismustypen und die allgemeine Conway-99-Frage sind davon getrennt.
