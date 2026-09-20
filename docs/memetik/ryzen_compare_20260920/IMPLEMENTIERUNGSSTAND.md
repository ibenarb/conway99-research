# Ryzen-Vergleich 0.4.0: ausführbare Vorbereitung

Fachlicher Vertrag: `docs/memetik/ryzen_plan_20260919/FORTSETZUNG_RYZEN.md`
und Plan V2. Unveränderter Eingangscommit:
`c54d4a1369f2f2b6f1289692c5001f49712a91a5`.

## Bestätigte Ausfallursache und Wiederaufbau

Am 20.09.2026 hat der Eigentümer die Ursache des früheren Ausfalls ausdrücklich
festgehalten: Ein Programmfehler ließ die physische Windows-Platte volllaufen,
während die virtuelle Ubuntu-Platte weiterhin freien Platz meldete. Der
16-GiB-Swap ist nicht die festgehaltene Ursache.

Ubuntu wurde nach der genehmigten Beendigung der Rettung neu installiert.
Aktuell: Ubuntu-24.04, Benutzer rb, Ryzen 9 3900X, 24 logische Prozessoren,
etwa 47 GiB RAM. Paket-/Graphbibliothekskontrolle und begrenzter Schreib-/Lesetest
sind laut Rückmeldung bestanden. Der Memetik-Checkout ist sauber auf obigem
Commit. Debian, Office und fremde Prozesse bleiben unberührt.

## Implementiert

`experiments/memetik/ryzen_compare_0_4_0/prepare.py` erstellt in einem neuen
Verzeichnis unter dem Linux-Workspace:

- ein unabhängig auf beide jeweiligen Verträge und fünf Scores geprüftes
  Gründerregister mit Quellhashes, exakten nauty-Zertifikaten, Abstammung und
  getrenntem Ω-Rahmen;
- ein Manifest mit 144 Aufträgen: zwölf gepaarte Seeds, zwei Arme, drei Ziele,
  zwei Varianten, je 3600 Worker-CPU-Sekunden, insgesamt 518400 Sekunden;
- einen lokalen Ressourcenbericht. Systempfade und Prozesslisten werden nicht
  automatisch veröffentlicht.

Der vorhandene Bestand liefert **17 verschiedene geeignete Ω-Klassen und
12 λ-Klassen**, ohne A als aktiven Bestand zu zählen. Enthalten sind der
geprüfte B-W2080-Endpunkt und C02-W2031/L1=2428/F=3298. A bleibt Kontrolle.
Claude-B zählt zur Z14-Abstammung von Claude-A, F03/F04 gemeinsam als
Z33-Lifts. HoG-Nachfahren sind keine neue Herkunftsfamilie. Fehlende historische
Kosten werden als unbekannt gespeichert, niemals als null.

Dies ist ein Reservoir, noch keine ausgewählte Vergleichspopulation. Vier
weitere verschiedene λ-Gründer für die nominellen 16 und getrennte
Trainings-/Übertragungsbestände sind noch bereitzustellen oder die ehrliche
kleinere Größe ist vor Bestätigung festzulegen. Kein Auffüllen durch Kopien.

Die neue Ω-Erzeugung speichert die statischen Träger und berechnet die
H-abhängigen Vorzeichenbedingungen mit Bitmasken neu je Zustand. Alte
Programme und Ergebnisse sind unverändert. Die zufällige Traversierungsordnung
ändert sich; behauptet wird derselbe zulässige Katalog, nicht dieselbe
Zufallsfolge und keine Gleichverteilung über Trades.

## Schutz vor Wiederholung des Plattenfehlers

Die aktuelle WSL-Registrierung bestimmt die tatsächliche VHDX. Über Windows
wird deren Trägervolumen abgefragt; ein fehlendes `/mnt/c` oder eine unbekannte
Messung gilt nicht als freier Platz. Reserven: **50 GiB auf dem physischen
Windows-Volume, 20 GiB im Linux-Ziel**, mindestens 6 GiB verfügbarer RAM.
Eine fehlgeschlagene Abfrage sperrt die Vorbereitung. Keine Mount-, Reparatur-,
Resize- oder Abschaltoperation.

Die Volume-Zuordnung nutzt das dokumentierte
[Get-Volume -FilePath](https://learn.microsoft.com/en-us/powershell/module/storage/get-volume).
Die Windows-Abfrage kann in der Entwicklungsumgebung nicht gegen den Ryzen
ausgeführt werden; genau dieser nächste lokale Prüfschritt ist noch offen.

## Gezielte Prüfung und verbleibende Implementierung

Sechs neue Kontrollen bestanden: Budget/Paarung, volle physische Platte trotz
virtuell freiem Platz, ausgefallene Hostabfrage, Aufnahme/Abstammung,
vollständiger 4×4-Abgleich an B vor und nach einem Trade und Vorzeichenmasken
gegen die alte Formel an C02. Keine erneute 6006-Graphen-Prüfung.

**Noch nicht startbereit:** A0/A1-Laufsteuerung, Training/Schwellenfreeze,
Checkpoint-/Wiederaufnahmebuchhaltung, laufende Ressourcenüberwachung,
12/18/24-Durchsatzmessung und Ergebnisexport/-auswertung. Die neue
Ressourcenfunktion muss im Controller wiederholt geprüft werden und einen
kontrollierten Stopp der eigenen Worker mit ausreichender Schreibreserve
auslösen; die einmalige Vorbereitung ersetzt dies nicht.

Das Auftragsmanifest trägt deshalb `launch_enabled: false`; die Vorbereitung
startet keine Vergleichsrechnung und keine 48-Stunden-Kampagne. Diese Datei
beschreibt den tatsächlichen Implementierungsstand, keine fertige Kampagne.
