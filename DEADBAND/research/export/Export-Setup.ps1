# DEADBAND Export-Setup (Forschung V8.10, research/DATEN_EXPORT.md)
# Erster Doppelklick: Exportskripte ins GFT-Terminal legen und kompilieren.
# Nach dem Export: erneut doppelklicken -> Upload-Ordner mit ZIPs auf dem Desktop (Export, Berichte, Tester-Logs).
# Nur lesend gegenueber dem Konto. Die Altlast unter C:\Program Files\MetaTrader 5 wird nie angesprochen.
$ErrorActionPreference = 'Stop'

##CODE:gft##

$DATEN_MQ5 = ##DATEI:daten##
$KALENDER_MQ5 = ##DATEI:kalender##
$EA_MQ5 = ##DATEI:ea##

function Schreibe-Ascii([string]$pfad, [string]$text) {
    $t = $text -replace "`r?`n", "`r`n"
    [IO.File]::WriteAllText($pfad, $t, (New-Object System.Text.ASCIIEncoding))
}

function Kompiliere([string]$inst, [string]$datei) {
    $me = Join-Path $inst 'metaeditor64.exe'
    if (-not (Test-Path $me)) { throw "MetaEditor nicht gefunden: $me" }
    $log = [IO.Path]::ChangeExtension($datei, '.log')
    $ex5 = [IO.Path]::ChangeExtension($datei, '.ex5')
    if (Test-Path $log) { Remove-Item -LiteralPath $log -Force }
    $start = Get-Date
    $p = Start-Process -FilePath $me -ArgumentList @(('/compile:"' + $datei + '"'), ('/log:"' + $log + '"')) -Wait -PassThru
    $txt = ''
    if (Test-Path $log) { $txt = [IO.File]::ReadAllText($log) }
    $ok = (Test-Path $ex5) -and ((Get-Item -LiteralPath $ex5).LastWriteTime -ge $start.AddSeconds(-2))
    $zeile = ($txt -split "`r?`n" | Where-Object { $_ -match 'result|error|warning' } | Select-Object -Last 3) -join ' | '
    if ($ok) { Write-Host ("  OK   " + (Split-Path $datei -Leaf) + "  " + $zeile) }
    else { Write-Host ("  FEHLER " + (Split-Path $datei -Leaf) + "  " + $zeile) -ForegroundColor Red; Write-Host $txt }
    return $ok
}

try {
    Write-Host 'DEADBAND Export-Setup' -ForegroundColor Cyan
    $inst = Gft-Installation
    $daten = Gft-Datenordner $inst
    Write-Host "Datenordner: $daten"
    $exp = Join-Path $daten 'MQL5\Files\DEADBAND_Export'
    $berichte = 'C:\Trading\Berichte'
    if (-not (Test-Path $berichte)) { New-Item -ItemType Directory -Force -Path $berichte | Out-Null }

    $modus = '1'
    if (Test-Path (Join-Path $exp 'export_log.txt')) {
        Write-Host ''
        Write-Host 'Es liegt schon ein Export vor:'
        Write-Host '  [1] Skripte neu installieren und kompilieren'
        Write-Host '  [2] Upload-Ordner auf dem Desktop erstellen (ZIPs: Export, C:\Trading\Berichte, Tester-Logs)'
        $modus = Read-Host 'Auswahl (1/2)'
    }

    if ($modus -eq '2') {
        # Upload-Ordner: je CSV eine ZIP (GitHub-Weboberflaeche nimmt hoechstens 25 MB je Datei), Rest in rest.zip
        $stamp = Get-Date -Format 'yyyyMMdd_HHmm'
        $desk = [Environment]::GetFolderPath('Desktop')
        $up = Join-Path $desk ('DEADBAND_Upload_' + $stamp)
        New-Item -ItemType Directory -Force -Path $up | Out-Null
        $tmp = Join-Path $env:TEMP ('DEADBAND_Rest_' + $stamp)
        New-Item -ItemType Directory -Force -Path $tmp | Out-Null
        foreach ($f in @(Get-ChildItem -Path $exp -File)) {
            if ($f.Extension -eq '.csv' -and $f.Name -notlike 'kalender*') {
                Compress-Archive -LiteralPath $f.FullName -DestinationPath (Join-Path $up ($f.Name + '.zip')) -Force
            }
            else { Copy-Item -LiteralPath $f.FullName -Destination $tmp -Force }
        }
        $kl = Join-Path $tmp 'kompilier_logs'
        New-Item -ItemType Directory -Force -Path $kl | Out-Null
        foreach ($d in @((Join-Path $daten 'MQL5\Scripts\DEADBAND'), (Join-Path $daten 'MQL5\Experts\DEADBAND_Forschung'))) {
            if (Test-Path $d) { Copy-Item -Path (Join-Path $d '*.log') -Destination $kl -Force -ErrorAction SilentlyContinue }
        }
        if (@(Get-ChildItem -Path $berichte -File -ErrorAction SilentlyContinue).Count -gt 0) {
            Copy-Item -Path $berichte -Destination (Join-Path $tmp 'berichte') -Recurse -Force
        }
        # Tester-Logs der letzten 14 Tage (Tester-Ordner hat denselben Namen wie der Datenordner)
        $tst = Join-Path (Join-Path $env:APPDATA 'MetaQuotes\Tester') (Split-Path $daten -Leaf)
        if (Test-Path $tst) {
            $logs = @(Get-ChildItem -Path $tst -Recurse -Filter '*.log' -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-14) })
            if ($logs.Count -gt 0) {
                $ld = Join-Path $tmp 'tester_logs'
                New-Item -ItemType Directory -Force -Path $ld | Out-Null
                foreach ($l in $logs) { Copy-Item -LiteralPath $l.FullName -Destination (Join-Path $ld ($l.Directory.Parent.Name + '_' + $l.Name)) -Force }
            }
        }
        Compress-Archive -Path (Join-Path $tmp '*') -DestinationPath (Join-Path $up 'rest.zip') -Force
        Remove-Item -LiteralPath $tmp -Recurse -Force
        Write-Host ''
        $gross = $false
        foreach ($z in @(Get-ChildItem -Path $up -File)) {
            $mb = [math]::Round($z.Length / 1MB, 1)
            if ($z.Length -gt 24MB) { $gross = $true; Write-Host ("  {0}  {1} MB  ZU GROSS fuer GitHub (max. 25 MB)" -f $z.Name, $mb) -ForegroundColor Red }
            else { Write-Host ("  {0}  {1} MB" -f $z.Name, $mb) }
        }
        Write-Host ''
        Write-Host "Upload-Ordner fertig: $up" -ForegroundColor Green
        Write-Host 'Jetzt im Browser hochladen (Anleitung DATEN_EXPORT.md, Schritt 5): alle Dateien dieses Ordners.'
        if ($gross) { Write-Host 'Eine Datei ist groesser als 25 MB - bitte melden, dann teile ich sie.' -ForegroundColor Red }
        Start-Process explorer.exe -ArgumentList ('"' + $up + '"')
    }
    else {
        $ziel = Join-Path $daten 'MQL5\Scripts\DEADBAND'
        New-Item -ItemType Directory -Force -Path $ziel | Out-Null
        $f1 = Join-Path $ziel 'DEADBAND_Daten_Export.mq5'
        $f2 = Join-Path $ziel 'DEADBAND_Kalender_Export.mq5'
        Schreibe-Ascii $f1 $DATEN_MQ5
        Schreibe-Ascii $f2 $KALENDER_MQ5
        Write-Host "Skripte abgelegt in $ziel"
        Write-Host 'Kompilieren mit dem MetaEditor des GFT-Terminals:'
        $a = Kompiliere $inst $f1
        $b = Kompiliere $inst $f2
        # Referenz-EA fuer den Testerlauf: DEADBAND_V8.mq5 Build 8.10 unveraendert, eigener Ordner und Name
        # (der live laufende EA wird weder ersetzt noch neu geladen)
        $zielEa = Join-Path $daten 'MQL5\Experts\DEADBAND_Forschung'
        New-Item -ItemType Directory -Force -Path $zielEa | Out-Null
        $f3 = Join-Path $zielEa 'DEADBAND_V8_810_Referenz.mq5'
        Schreibe-Ascii $f3 $EA_MQ5
        Write-Host "Referenz-EA abgelegt in $zielEa"
        $c = Kompiliere $inst $f3
        if (-not $c) { Write-Host 'Der Referenz-EA (V8.10) kompiliert NICHT - bitte die Fehlerzeilen oben schicken (ZIP mit [2] enthaelt das Protokoll).' -ForegroundColor Red }
        Write-Host ''
        if ($a -and $b) {
            Write-Host 'Fertig. Weiter im Terminal (Anleitung research/DATEN_EXPORT.md):' -ForegroundColor Green
            Write-Host '  1. Extras > Optionen > Charts > Max. Balken im Chart = Unbegrenzt (falls noch nicht).'
            Write-Host '  2. Neuen Chart oeffnen (z. B. EURUSD, NICHT den Chart des EA).'
            Write-Host '  3. Navigator > Skripte > DEADBAND > DEADBAND_Daten_Export auf den Chart ziehen, OK. Warten bis zur Meldung.'
            Write-Host '  4. Danach DEADBAND_Kalender_Export ebenso.'
            Write-Host '  5. Referenzlauf im Strategietester mit Experts\DEADBAND_Forschung\DEADBAND_V8_810_Referenz (Einstellungen in DATEN_EXPORT.md),'
            Write-Host '     Bericht als HTML nach C:\Trading\Berichte speichern.'
            Write-Host '  6. Diese Datei erneut doppelklicken und [2] waehlen.'
        }
        else { Write-Host 'Kompilieren fehlgeschlagen - bitte das Protokoll oben schicken.' -ForegroundColor Red }
    }
}
catch {
    Write-Host ''
    Write-Host ('FEHLER: ' + $_.Exception.Message) -ForegroundColor Red
}
