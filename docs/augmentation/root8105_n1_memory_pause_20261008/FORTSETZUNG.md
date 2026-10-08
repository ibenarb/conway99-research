# Minimalübergabe Memetik VIII — 08.10.2026

## Auftrag und Grenzen

Nur ROOT8105/N1 auf RB-CUBE (Ryzen/WSL), C2 nicht verändern. Ralph hat den
Wiederholungstest autorisiert: Programm korrigieren; bei gleicher Fehlerart
Suchzustand erhalten und fortsetzen. Kein neuer Solverstart ist erfolgt.
Ein WSL-Einzeiler pro Nutzerantwort, Zeitstempel Europe/Berlin vor Antworten.
Große Quellen, Logs und Toolausgaben nicht in den Chat. Bereits bestandene
Mathematik-/Plattformprüfungen nicht wiederholen. Keine Subagents.

## Gesicherter Stand

0.8.0 ist veröffentlicht im Vorgängercommit3328ef661d374158d49719dfc07736e8d720ef39.
Root210 class0 startete am08.10. um12:12 und wurde wegen HOST_MEMORY_RESERVE
kontrolliert beendet. Kein mathematisches Ergebnis; CDCL-Zustand des alten
Prozesses verloren. Root6682 class0 ist nur vorbereitet, nicht starten.

Originalroot:
`/home/rb/conway99_workspace/ROOT8105_N1_Kalibrierung_20261008/r210_class000`
Originalaccounts: gleicher Pfad plus `.accounts`.
Native CPU11944.596729s; Gesamtuntergrenze12500.9748332s; Solver-Peak379940KiB.
Partialproof3635525064Bytes; kein Zertifikat. Diagnosearchiv im selben Gitordner,
SHA256b7c133be4e60d0bdb6481cecca74a0d4eb9cc668b2af7387ab666064bc106034.
49Dateien,37Seals und drei Endkonten samt referenzierter Hashes geprüft. Ursachen
des Windows-Speichereinbruchs unbekannt. Später Windows46.87GiB verfügbar.

## Bereits implementiert und geprüft — NICHT noch einmal entwickeln

`tools/memetik/root8105_n1_runtime_0_8_1/`:
- Unter8GiB Windows-Available: pidfd-SIGSTOP nur für eigenen validierten
  Solver/Checker. Derselbe Prozess setzt nach10 frischen Hostsekunden mit
  mindestens9GiB automatisch perSIGCONT fort. Messwerte und Übergänge gespeichert.
- Status PAUSED_HOST_MEMORY. Budgetende allein pausiert nie. Antwort0/fatale
  Plattformfehler wecken den pausierten Prozess für kontrollierte Beendigung.
- Exakt HOST_MEMORY_RESERVE mit intakten Host-/CLI-Endkonten wird gesondert
  klassifiziert. Alte Fehlerbelege bleiben erhalten; echte Lücken blockieren.
- Pause ist RAM-Erhalt, kein Crash-/Reboot-Checkpoint; sie gibt keinen RAM frei.
  Andere Ressourcen-/Integritätsstopps bleiben unverändert.
- 12Pauseprüfungen,8Endkontenprüfungen und22Versionsgateprüfungen bestanden.
  Echte Linux-Signale + gleicher Prozess/interner Zähler über2Pausezyklen;
  Druckmesswerte synthetisch. Neue WSL-Zielprüfung noch AUSSTEHEND.
- Native Binärdateien und mathematische Quellen unverändert; kein Cloud-N1-Lauf.

## Nächster Schritt

Das hier veröffentlichte ZIP auf Ryzen per festem Commit herunterladen, SHA prüfen,
neu entpacken. ZIP `ROOT8105_N1_Ryzen_Kalibrierung_0.8.1.zip` in diesem Gitordner:
SHA256f823d7468cea11104c813faa592118f436bc079443868cf2717635a14bf6bd72;
3081336Bytes,46Einträge. Topfolder ROOT8105_N1_Ryzen_Kalibrierung_0.8.1.

Interpreter `~/conway99_workspace/ROOT8105_N1_python/bin/python` ist vorhanden;
python-sat1.9.dev15/six1.17.0 bestätigt. Binaries in
`~/conway99_workspace/ROOT8105_N1_native_072/` bleiben unverändert, kein Build.

`retry.py --output ~/conway99_workspace/ROOT8105_N1_Kalibrierung_20261008_081_retry1`
mit dem obigen Interpreter aus dem neuen Runtimeordner ausführen. Es prüft
bytegenau die kleinen Originalbelege, auditiert alte CPU-Endkonten, führt nur
den neuen20erKontrollsatz auf WSL aus, initialisiert/preflightet ausschließlich
Root210 und schreibt PREDECESSOR.json. Kein Solverstart innerhalb retry.py.
Bei Fehler: Zielverzeichnisse erhalten und zugehöriges kleines Log auswerten;
nicht blind denselben Initialisierungsbefehl wiederholen.

Nur bei RETRY_READY danach `runtime.py run NEW_OUTPUT/r210_class000` detached
mit stdinDEVNULL und neuem exklusiv angelegtem Log starten. Mit dem neuen
`status.py ROOT` reale Prozessidentität und CPU prüfen; START_ANGEFORDERT ist
noch keine Laufbestätigung. Beide Aktionen können wie bisher in EINEM
WSL-Einzeiler verbunden werden, mit check=True vor Popen.

Neuer Test erhält6h native/8h aggregierte CPU-Entscheidungsbudgets; alte Verbräuche
bleiben getrennt verknüpft erhalten. Kein automatischer Zeitabbruch. Ohne Antwort
weiterarbeiten;0kontrollierter Stopp,positiveSekunden additiveVerlängerung.
MaxRSS24GiB,RAMreserve8GiB,Diskreserve100GiB. Unbekannte Ergebnis-ETA.

## Quellenbedarf

Zuerst dieses Dokument und README.md im neuen Runtimeordner lesen; weitere
Dateien nur gezielt. REPORT.md, VALIDATION.json, SOURCE_COMPARISON.json und
PREDECESSOR_ACCOUNT_AUDIT.json liegen hier. AGENTS.md und die verbindlichen
Experimentregeln gelten; neue Lehre GC-24 steht in GLOBAL_CONCLUSIONS.md.
Keine alten Chatverläufe oder großen Beweisdateien für den nächsten Schritt laden.
