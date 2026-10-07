# N1: Unterbrechungs- und Fortsetzungsvertrag 1.0

Stand: 07.10.2026. Status: QUELLENGEPRUEFTER_ENTWURF; NICHT IMPLEMENTIERT; KEINE LAUFFREIGABE.
Basis: 55f978b28f6f4b4e8648e24a26c453d80ed0834f.
Umfang dieses Pakets: Vertrag, Quellennachweise, Abnahmekriterien. Keine Solverläufe.
Geltende Regeln: AGENTS.md, docs/EXPERIMENT_RULES.md und docs/operations/GLOBAL_CONCLUSIONS.md am Basiscommit; insbesondere GC-01/08/15/16/17/18/19/20/22/23. Die neuere Bulletin-Regel vom 07.10.2026 liegt byteidentisch als BULLETIN_REFERENCE.md bei und hat bei Abweichungen Vorrang.

## 1. Entscheidung und Grenzen

Geplant ist ein eigener kleiner nativer Worker gegen die CaDiCaL-2.2.1-Bibliothek, überwacht durch einen dauerhaften lokalen Supervisor. CaDiCaL-Quellcommit: 4198d817d0dcde5b1240eefbff70b555b7df2af9 (rel-2.2.1). Externer Prüfer: drat-trim 2e3b2dc0ecf938addbd779d42877b6ed69d9a985. Diese Wahl ist eine technische Vertragsentscheidung, keine Leistungsprognose und kein Ergebnisvergleich mit Glucose4.

| Situation | Erhalt / Fortsetzung |
| --- | --- |
| Budget erreicht, Antwort fehlt oder n > 0 | Derselbe lebende Solver rechnet weiter; kein Neustart, keine Unterbrechung. |
| Antwort 0 | Kooperative Beendigung der bezeichneten Suchaufgabe, Sicherung, Endabrechnung; offene Klasse bleibt ungelöst. |
| Spätere Fortsetzung nach beendetem Solver | Abgeschlossene Klassen übernehmen; offene CNF in neuem Versuch vom Original neu starten. |
| Prüfer unterbrochen | Geschlossene Original-CNF und vollständige Beweisdatei behalten; Prüfung in neuem Versuch von vorn beginnen. |
| Prozess-/Hostabsturz | Letzten gültigen dauerhaften Stand retten; fehlende Schlussabrechnung und möglichen ungesicherten Dateischwanz ausdrücklich ausweisen. |

Keine zugesagte Serialisierung des vollständigen CDCL-Zustands. Kein DIMACS-Export, keine Solverkopie und kein Teil-DRAT wird als solcher Checkpoint bezeichnet. Eine hypothetische Betriebssystem-Prozesssicherung ist nicht Teil dieses Vertrags. Ohne sie kann offene interne Sucharbeit beim Beenden nicht vollständig erhalten bleiben; dies ist die im Bulletin zugelassene, ausdrücklich ausgewiesene Neustartgrenze.

## 2. Konkrete Quellenbefunde

SOURCES.json fixiert gelesene Dateien mit SHA256; alle folgenden Links sind auf Commits fixiert.

- [CaDiCaL API](https://github.com/arminbiere/cadical/blob/4198d817d0dcde5b1240eefbff70b555b7df2af9/src/cadical.hpp): solve() unterscheidet 0/10/20; terminate() fordert eine asynchrone, nicht augenblicklich abgeschlossene Rückkehr an. Ein Terminator wird regelmäßig abgefragt. Hieraus folgt keine garantierte maximale Abbruchlatenz.
- copy() kopiert laut API keine vollständige interne Maschine, sondern insbesondere irredundante Klauseln und Units. write_dimacs() lässt redundante Klauseln und den Extension-Stack aus. Die gelesene öffentliche API liefert damit keinen vollständigen persistenten Suchcheckpoint; keine weitergehende Unmöglichkeitsaussage über andere Werkzeuge.
- Proof-Tracing muss vor Klauselimport und Suche eingeschaltet werden. flush_proof_trace() verspricht fflush-Semantik, keine fsync-Dauerhaftigkeit; close_proof_trace() sorgt für Flush.
- [CLI](https://github.com/arminbiere/cadical/blob/4198d817d0dcde5b1240eefbff70b555b7df2af9/src/cadical.cpp) und [Signale](https://github.com/arminbiere/cadical/blob/4198d817d0dcde5b1240eefbff70b555b7df2af9/src/signal.cpp): SIGINT/SIGTERM führen im CLI über Statistik/UNKNOWN und erneutes Auslösen des Signals; kein zugesicherter geordneter Proof-Abschluss. Daher kein Standard-CLI-Signal als normaler 0-Abbruch.
- [drat-trim](https://github.com/marijnheule/drat-trim/blob/2e3b2dc0ecf938addbd779d42877b6ed69d9a985/drat-trim.c): -O setzt optimize=1, wodurch der interne Timeouttest deaktiviert wird, aktiviert aber zusätzlich eine Optimierungsschleife. Diese hat iteration < 10000 als Begrenzung; das garantiert keine Laufzeit. VERIFIED kann bereits vor dieser Nacharbeit erscheinen. Ein Textfragment allein ist kein Prozessabschluss. -D würde den Eingangsbeweis löschen und ist verboten.
- Vorhandene N1-Kontrollen verwenden Glucose4 über PySAT und nachträgliches get_proof(). Das belegt weder den neuen CaDiCaL-Worker noch dauerhaftes Streaming. Bestehende Belege bleiben unverändert; spätere Integration benötigt eigene kleine Schnittstellenkontrollen, keine Wiederholung der 960er-Diagnose.

## 3. Prozess- und Abbruchvertrag

Ein dauerhafter Supervisor besitzt die nativen Kinder und bleibt zum wait4-Reaping verantwortlich. Eine kurzlebige Status-/Bedien-CLI besitzt keine Solver. Chatende, EOF und geschlossene Bedienkonsole beeinflussen sie nicht. Neuer Controllerstart darf weder blind doppelt starten noch fremde Prozesse signalisieren: Boot-ID, PID, Startzeit, Lauf-ID und exklusiven Besitz prüfen.

Der native Worker hat genau einen Solver-eigenen Thread. Der Kontrollpfad setzt für 0 ein threadsicheres Stopflag und fordert terminate() an; keine parallelen normalen Solver-API-Aufrufe. Nach solve()-Rückkehr schließt derselbe Besitzer den Beweis, sichert Dateien und Metadaten und beendet sich. Beim Einlesen muss der spätere Worker zwischen endlichen Importabschnitten das Stopflag prüfen; API-Terminierung allein deckt nicht alle Startphasen ab. Keine neuen Suchschritte nach beobachtetem Stopauftrag; verbleibende Abbruchlatenz messen und sichtbar machen.

Antwort 0 sperrt sofort neue Arbeit im bezeichneten Umfang. Kooperative Rückkehr kann verzögert sein: STOP_REQUESTED und Dauer anzeigen, nicht nach einer Frist automatisch SIGKILL senden. Kein künstlicher harter Nachlauf-Timeout. Bei nicht reagierendem Werkzeug bleiben Status, Dateien und Prozessidentität erhalten; sichere Abwicklung muss vor Produktionsfreigabe nachgewiesen sein. Echte akute Ressourcen-/Integritätsgefahr ist ein gesonderter, protokollierter Notfall, keine Umbenennung eines Zeitbudgets.

Beim externen Prüfer darf 0 dessen eigenen Prozess beenden, da seine versiegelten Eingaben unverändert bleiben; Ausgabe nur als Prüfversuch/Log erhalten. Kein fortsetzbarer interner Prüferzustand wird behauptet. Keine automatische Tötung unabhängiger Prüfer oder Suchläufe. Erfolgt 0 während einer Ergebnisübergabe, bleibt ein bereits vollständig gesichertes Resultat erhalten; weitere Validierung wird als ausstehend verbucht, nicht verworfen oder ungeprüft akzeptiert.

## 4. Budgets und dauerhafte Bedienung

Keine nativen Zeit-, Konflikt- oder Entscheidungslimits im Produktionssuchpfad, kein timeout-Kommando, kein zeitbasierter Kill-Watchdog, keine endlichen geerbten RLIMIT_CPU. Prüfer mit -O; dessen zusätzliche Optimierungsarbeit wird vollständig mitgezählt. Startprüfung dokumentiert effektive Limits und lehnt einen unvereinbaren Start ab. Kein bereits laufender Nutzerprozess wird verändert.

Jeder Budgetdatensatz enthält scope, kind (aggregierte CPU-Sekunden oder Walltime), original_budget, approved_budget und tatsächlichen kumulativen Verbrauch. Suche, Prüfung und Nebenarbeit haben getrennte Konten; Gesamtbudget summiert disjunkte Konten ohne Doppelzählung. Budgetprojektion ist keine Such-ETA.

Beim Erreichen: genau eine dauerhafte offene Anfrage pro Budgetgeneration. Anzeige mit Lauf, Teilauftrag, Budgetart, Verbrauch und Überschreitung, dann:
`time limit reached. ETA unknown. Extend [seconds] ?`
Eine belastbare Restzeit darf unknown ersetzen; Stunden:Minuten meint Restdauer.

Anfrage und Antwort tragen run_id, scope_id, request_id und generation. Separater Antwortbefehl akzeptiert nur 0 oder positive ganze Sekunden. Antworten werden dauerhaft atomar abgelegt; eine Transaktion verbucht Antwort-ID, Budgetänderung und Bestätigung genau einmal. Doppelte, fremde oder veraltete Antworten ändern nichts und werden nachvollziehbar quittiert. Neustart zwischen Buchung und Bestätigung darf keine doppelte Verlängerung verursachen.

n > 0 erhöht das bisherige genehmigte Budget, nicht den aktuellen Verbrauch, um n Sekunden derselben Art. Ist es schon wieder überschritten, neue Anfrage erstellen und weiterarbeiten. Fehlende/ungültige Antwort und EOF lassen Suche und reguläre Aufgabenplanung unverändert laufen. Kein verstecktes Pausieren, Drosseln oder Prioritätswechsel. Übergeordnete Budgets separat ausweisen und erforderlichenfalls ebenfalls abfragen; offene Gesamtanfrage verhindert keine genehmigte Weiterarbeit. Regulärer Abschluss erledigt die Anfrage; spätere Antwort startet nichts neu.

## 5. Artefakte, Proofs und Wiederanlauf

Vor Start unveränderlich fixieren: Original-CNF-SHA256, Modell-/Root-/Klassenidentität, Kantenabbildung, Matching/Abdeckung, Quellcommits, Binärhashes, Build-/Bibliotheksversionen, Optionen und Zufallsseed. Zwei vorgesehene Klasse-0-Inputs gehören zu Root 210 und 6682; keine automatische 220-Klassen-Kampagne.

Jeder Such- und Prüfversuch erhält ein neues Verzeichnis und neue attempt_id. Protokolle/Beweise früherer Versuche niemals überschreiben. Proof-Tracing vor Import aktivieren; DRAT-Format explizit fixieren (binary=1, lrat=0, frat=0, veripb=0) und später mit dem Prüfer testen. Direkt auf Datei streamen, nicht vollständigen Beweis im Controller-RAM sammeln. Ein laufender Beweis ist zunächst *.partial.

Regelmäßige atomare Metadaten-Checkpoints und fortlaufendes Ledger; geplantes Ausgangsintervall höchstens 30 Hostsekunden, auf Zielhardware zu prüfen. Daten zuerst schreiben/flush/fsync, dann temporäres Manifest fsync, atomarer rename und Verzeichnis-fsync. Hashen eines wachsenden Beweises nur als stabil identifizierter Präfix mit Länge; kein behaupteter endgültiger Gesamthash. Keine große rekursive Hashrunde im Überwachungstakt (GC-18). Datenträgerfehler dürfen gültige Vorgänger nicht ersetzen.

Während solve() kein unzulässiger paralleler flush_proof_trace()-Aufruf. Produktionsimplementierung muss Proof-Ausgabe ohne ungesicherten C-stdio-Puffer ermöglichen, etwa über ein vor trace_proof bereitgestelltes unbuffered FILE*, und aus dem Kontrollpfad sichere Datenträgersynchronisation vorsehen; genaue Kompatibilität und Kosten sind offene Abnahmepunkte. Nicht bestätigte Byteenden nach Absturz bleiben ungesichert. Periodische Synchronisation ist keine Garantie gegen Hardwareverlust; vollständiger interner Suchzustand ist ohnehin nicht persistiert.

Bei geordnetem Abschluss/0: Trace schließen, Daten synchronisieren, Hash und Bytezahl festhalten, Versuch versiegeln; erst danach terminales Receipt. Bei 0 bleibt der Teilbeweis als PARTIAL erhalten. Niemals Leerclause künstlich ergänzen, niemals an einen neuen Suchversuch anhängen. Neuer Versuch beginnt mit byteidentischer Original-CNF und neuer eigener Beweisdatei. Ausfuhr vereinfachter CNF oder Warmstart-Lemmas nicht Teil dieses Vertrags.

Nach Absturz: ausschließlich lesend Inventar und Receipts prüfen; endgültige Ergebnisse gegen Archiv/Hashes abgleichen (GC-22). Offene Versuche samt letzter Probe erhalten. Kein allein aus RUNNING abgeleiteter lebender Prozess. Bei noch lebendem Supervisor reconnect; bei verwaistem lebendem Solver kein zweiter Start und keine vorgetäuschte wait4-Adoption. Explizite Recoveryentscheidung erforderlich. Ein absichtlich neuer Gesamtversuch hat eigene Konten und einen Vorgängerverweis.

## 6. Ergebnis- und Abrechnungszustände

| Status | Zulässige Aussage |
| --- | --- |
| RUNNING / RUNNING_AWAITING_TIME_EXTENSION | Aufgabe offen; Solver lebt gemäß aktueller Identitätsprüfung. |
| STOP_REQUESTED / STOPPED_UNRESOLVED | Abbruch angefordert / gesichert beendet; kein SAT/UNSAT-Schluss. |
| SAT_UNVERIFIED | Kandidat erhalten; Prüfung ausstehend. |
| SAT_N1_VERIFIED | Vollständige Belegung gegen Original-CNF und dekodierten N1-Zeugen unabhängig geprüft; kein behaupteter srg(99)-Fund. |
| UNSAT_UNCERTIFIED | Solver meldet UNSAT, externer Abschlussbeleg fehlt. |
| UNSAT_CERTIFIED | Passende versiegelte CNF/Proof-Hashes, vollständig beendeter Prüfer mit Exit 0 und exakter Zeile s VERIFIED, keine Gegenanzeige wie NOT VERIFIED/TIMEOUT/DERIVATION oder Ausführungsfehler. |
| CRASHED_UNRESOLVED / ACCOUNTING_INCOMPLETE | Ergebnis beziehungsweise Endverbrauch ungeklärt; niemals als Null oder vollständiger Abschluss buchen. |

Mathematischer Status, Versuchslaufstatus und accounting_complete sind getrennte Felder. Ein bereits gültiger Beweis bleibt bei einer Abrechnungslücke gültig, der Betriebsabschluss bleibt unvollständig. Rootausschluss erst nach sämtlichen notwendigen zertifizierten Klassen und geprüfter Abdeckung. Solver-Exitcode oder leere Klausel allein genügt nicht.

Live-CPU pro identifiziertem Prozess aus /proc; Endwert aus wait4 mit user+system. Endwert ersetzt die Liveprobe desselben Prozesses und wird nicht zusätzlich dazu addiert. Worker, Prüfer, Supervisor und Hosthelfer disjunkt erfassen; keine gleichzeitig eingerechneten Eltern-Kinder-Summen. CPU während offener Anfragen und Abwicklung vollständig einbeziehen. Unbekannter Schlussverbrauch bleibt null im JSON-Sinn mit accounting_complete=false und letzter gemessener Untergrenze, niemals numerisch 0. Neue Versuche addieren sich zum kumulativen Verlauf; Abbruch verbraucht kein Budget rückwirkend.

Boot-ID, Gast-monotonic, UTC und echte Windows-Host-Stopwatch getrennt dokumentieren; keine Uhrkorrektur durch geratenen Faktor. Unterbrechungen zwischen Boot-Epochen nicht durch monotonic-Differenzen überbrücken. Bei fehlendem maßgeblichem Zeitbeleg lokal sicheren Zustand herstellen, Ursache ausweisen, unveränderte gesunde andere Läufe nicht pauschal stoppen. Die historische CPU-Lücke aus der 960er-Diagnose bleibt separat unverändert offen.

## 7. Abnahme vor jeder Startfreigabe (alles noch offen)

1. Echte kleine SAT-/UNSAT-Inputs mit neuem Worker, Streaming und externem Prüfer; falscher/abgeschnittener Proof und beschädigter SAT-Zeuge werden abgewiesen. Neues Backend separat von alten Glucose4-Kontrollen belegen.
2. Budgetende ohne Antwort, verspätetes n, erneute Überschreitung, EOF, ungültige Werte: gleiche Solverprozessidentität, fortschreitende Arbeit, unveränderte nominelle Budgets bis gültiger Antwort.
3. 0 während Import, Suche, Proof-Abschluss und Prüfung; Stoplatenz messen, sichere Dateien, keine neuen Suchjobs, tatsächliche End-CPU inklusive Abwicklung. Kein Kill nach Zeitablauf.
4. Doppelte/veraltete Antwort, konkurrierende Antworten, Absturz nach Buchung vor ACK: genau eine Wirkung, dauerhafte nachvollziehbare Quittung.
5. Controller-Neustart bei lebendem Supervisor: reconnect ohne doppelte Kinder; Supervisorverlust: keine automatische Adoption/Neusuche. Fremde PID und wiederverwendete PID zurückweisen.
6. Geordnete Fortsetzung übernimmt fertige Ergebnisse ohne Neusuche. Offene CNF erhält neue attempt_id, frischen Proof und kumulative Konten; kein exakter CDCL-Resume behauptet.
7. Simulierter Crash, unvollständiges Manifest, veraltete Live-DB, Dateikorruption und Schreibfehler: letzten gültigen Stand erhalten, fehlende Endkonten erkennen, keine falsche Zertifizierung.
8. Prüfer-VERIFIED vor regulärem Prozessende sowie falscher Exitcode: kein voreiliger Abschluss. Teilproofs niemals automatisch ergänzen/verketten.
9. CPU-Endwerte ersetzen Livewerte; verzögerte Reaping-/Flush-Phase und parallele Last mit disjunkten Konten prüfen. Testfehlersimulation von echten Systemwerkzeugen isolieren (GC-21).
10. Anschließend eigener Windows-/WSL-Zielhardwaretest für Uhren, fsync/rename, Kontrollkanal und Prozessbesitz. Kein WSL-Neustart bei unabhängigen laufenden Rechnungen. Cloudtest ersetzt diese Abnahme nicht.

Keine dieser Prüfungen wurde in diesem Vertragspaket ausgeführt. Keine Ressourcen-, Solver-RAM- oder Fertigstellungsprognose. Nächstes abgegrenztes Paket: nativen Worker und minimale Steuerung entsprechend diesem Vertrag implementieren und anhand kleiner echter Prozesse abnehmen; Zielhardware und Klasse-0-Kalibrierung bleiben danach getrennte Schritte.
