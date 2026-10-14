# DEADBAND Sidecar-Setup (research/PLAN.md 9.4, research/sidecar/BETRIEB.md)
# Doppelklick genuegt. Schritte: Python pruefen -> venv mit festen Paketversionen -> Sidecar nach C:\Trading\sidecar
# -> GFT-Terminal suchen (nie die Altlast C:\Program Files\MetaTrader 5) -> config.ini -> Aufgabe "DEADBAND Sidecar"
# -> Selbsttest -> optional Testalarm. Ausser der Aufgabe keine Registry-Eintraege. Der Sidecar sendet keine Orders.
$ErrorActionPreference = 'Stop'

##CODE:gft##

$SIDECAR_PY = ##DATEI:sidecar##
$KERN_PY = ##DATEI:kern##
$EA_PATCH = ##DATEI:ea##

$ZIEL = 'C:\Trading\sidecar'
$AUFGABE = 'DEADBAND Sidecar'
$MT5_PAKET = 'MetaTrader5==5.0.6180'

function Schreibe-Ascii([string]$pfad, [string]$text) {
    $t = $text -replace "`r?`n", "`r`n"
    [IO.File]::WriteAllText($pfad, $t, (New-Object System.Text.ASCIIEncoding))
}

function Kompiliere([string]$inst, [string]$datei) {
    $me = Join-Path $inst 'metaeditor64.exe'
    if (-not (Test-Path $me)) { Write-Host "  MetaEditor nicht gefunden: $me" -ForegroundColor Yellow; return $false }
    $log = [IO.Path]::ChangeExtension($datei, '.log')
    $ex5 = [IO.Path]::ChangeExtension($datei, '.ex5')
    if (Test-Path $log) { Remove-Item -LiteralPath $log -Force }
    $start = Get-Date
    Start-Process -FilePath $me -ArgumentList @(('/compile:"' + $datei + '"'), ('/log:"' + $log + '"')) -Wait | Out-Null
    $txt = ''
    if (Test-Path $log) { $txt = [IO.File]::ReadAllText($log) }
    $ok = (Test-Path $ex5) -and ((Get-Item -LiteralPath $ex5).LastWriteTime -ge $start.AddSeconds(-2))
    $zeile = ($txt -split "`r?`n" | Where-Object { $_ -match 'result|error|warning' } | Select-Object -Last 3) -join ' | '
    if ($ok) { Write-Host ("  OK   " + (Split-Path $datei -Leaf) + "  " + $zeile) }
    else { Write-Host ("  FEHLER " + (Split-Path $datei -Leaf) + "  " + $zeile) -ForegroundColor Red; Write-Host $txt }
    return $ok
}

function Finde-Python {
    # Kandidaten: Python-Launcher (py) und python.exe im PATH; der Store-Platzhalter (WindowsApps) zaehlt nicht
    $ErrorActionPreference = 'Continue'                 # Fehlermeldungen von py.exe/python.exe sind hier erwartet
    $kand = @()
    if (Get-Command py.exe -ErrorAction SilentlyContinue) {
        foreach ($v in @('-3.13-64', '-3.12-64', '-3.11-64', '-3.10-64', '-3.14-64', '-3-64')) {
            try {
                $p = & py.exe $v -c "import sys; print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0 -and $p) { $kand += ($p | Select-Object -First 1).Trim() }
            } catch { }
        }
    }
    foreach ($c in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)) {
        if ($c.Source -notmatch 'WindowsApps') { $kand += $c.Source }
    }
    foreach ($exe in ($kand | Select-Object -Unique)) {
        try {
            $info = & $exe -c "import sys, struct; print('%d %d %d' % (sys.version_info[0], sys.version_info[1], struct.calcsize('P') * 8))" 2>$null
            $t = ($info | Select-Object -First 1).Trim().Split(' ')
            if ([int]$t[0] -eq 3 -and [int]$t[1] -ge 10 -and [int]$t[2] -eq 64) {
                return [pscustomobject]@{ Exe = $exe; Minor = [int]$t[1] }
            }
            Write-Host "  uebergangen: $exe (Python $($t[0]).$($t[1]), $($t[2]) Bit)"
        } catch { }
    }
    return $null
}

function Lies-Ini([string]$pfad) {
    $w = @{}
    if (Test-Path $pfad) {
        foreach ($z in [IO.File]::ReadAllLines($pfad)) {
            if ($z -match '^\s*([A-Za-z_]+)\s*=\s*(.*)$') { $w[$matches[1]] = $matches[2].Trim() }
        }
    }
    return $w
}

try {
    Write-Host 'DEADBAND Sidecar-Setup' -ForegroundColor Cyan

    # 1) Python >= 3.10, 64 Bit
    $py = Finde-Python
    if (-not $py) {
        throw ("Kein Python >= 3.10 (64 Bit) gefunden. Ich installiere nichts ohne deine Freigabe.`r`n" +
               "So geht es: im Browser python.org > Downloads > Windows > 'Windows installer (64-bit)' fuer Python 3.12,`r`n" +
               "beim Installieren den Haken 'Add python.exe to PATH' setzen, danach diese Datei erneut doppelklicken.")
    }
    Write-Host "Python: $($py.Exe) (3.$($py.Minor), 64 Bit)"
    $numpy = if ($py.Minor -eq 10) { 'numpy==2.2.6' } else { 'numpy==2.3.5' }
    $inst = Gft-Installation                            # zuerst: ohne GFT-Terminal wird nichts installiert
    $daten = Gft-Datenordner $inst

    # 2) Ordner, laufenden Sidecar anhalten, Dateien ablegen
    New-Item -ItemType Directory -Force -Path $ZIEL | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $ZIEL 'logs') | Out-Null
    if (Get-ScheduledTask -TaskName $AUFGABE -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $AUFGABE -ErrorAction SilentlyContinue
        Write-Host 'Laufender Sidecar angehalten (wird am Ende neu gestartet).'
    }
    Schreibe-Ascii (Join-Path $ZIEL 'sidecar.py') $SIDECAR_PY
    Schreibe-Ascii (Join-Path $ZIEL 'sidecar_kern.py') $KERN_PY
    Write-Host "Sidecar-Dateien in $ZIEL"

    # 3) venv mit festen Versionen (E8); Ausgaben von python/pip auf stderr sind keine Abbruchgruende
    $ErrorActionPreference = 'Continue'
    $venv = Join-Path $ZIEL 'venv'
    $vpy = Join-Path $venv 'Scripts\python.exe'
    if (-not (Test-Path $vpy)) {
        Write-Host 'Lege venv an ...'
        & $py.Exe -m venv $venv
        if ($LASTEXITCODE -ne 0) { throw 'venv konnte nicht angelegt werden.' }
    }
    Write-Host "Installiere $MT5_PAKET und $numpy (nur fertige Pakete) ..."
    & $vpy -m pip install --disable-pip-version-check --only-binary=:all: $MT5_PAKET $numpy
    if ($LASTEXITCODE -ne 0) { throw 'Paketinstallation fehlgeschlagen (Internet? Proxy?). Ausgabe oben.' }
    $ErrorActionPreference = 'Stop'

    # 4) GFT-Terminal und config.ini (vorhandene Werte bleiben, Terminalpfad wird neu ermittelt)
    $portable = if ((Normpfad $daten) -eq (Normpfad $inst)) { '1' } else { '0' }
    $ini = Join-Path $ZIEL 'config.ini'
    $alt = Lies-Ini $ini
    $thema = $alt['ntfy_thema']
    if (-not $thema) {
        $b = New-Object byte[] 12
        [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b)
        $thema = 'deadband-' + (($b | ForEach-Object { $_.ToString('x2') }) -join '')
    }
    $werte = [ordered]@{
        terminal_pfad = (Join-Path $inst 'terminal64.exe'); portable = $portable; datenordner = $daten
        symbole = 'XAUUSD.x;NAS100.x'; max_datenalter_s = '180'; max_tickalter_s = '120'; takt_s = '60'
        alarm_sperre_min = '30'; ntfy_server = 'https://ntfy.sh'; ntfy_thema = $thema; log_ordner = (Join-Path $ZIEL 'logs')
        kalender_datei = (Join-Path $daten 'MQL5\Files\DEADBAND_Export\kalender_US.csv'); nachrichten_sperre = '0'
        sperre_vor_min = '15'; sperre_nach_min = '15'; kalender_warn_tage = '7'; anlauf_min = '15'
    }
    foreach ($k in @($werte.Keys)) {
        if ($k -in @('terminal_pfad', 'portable', 'datenordner')) { continue }
        if ($alt.ContainsKey($k) -and $alt[$k] -ne '') { $werte[$k] = $alt[$k] }
    }
    $zeilen = @('; DEADBAND Sidecar - erzeugt von Sidecar-Setup.cmd. Aenderungen bleiben bei erneutem Setup erhalten',
                '; (ausser terminal_pfad, portable, datenordner - die werden jedes Mal neu ermittelt).', '[sidecar]')
    foreach ($k in $werte.Keys) { $zeilen += ($k + ' = ' + $werte[$k]) }
    Schreibe-Ascii $ini (($zeilen -join "`r`n") + "`r`n")
    Write-Host "config.ini geschrieben (Terminal $inst, portabel $portable)"

    # 5) EA-Patch ablegen und kompilieren (separater EA, der laufende EA bleibt unberuehrt)
    $zielEa = Join-Path $daten 'MQL5\Experts\DEADBAND_Forschung'
    New-Item -ItemType Directory -Force -Path $zielEa | Out-Null
    $fea = Join-Path $zielEa 'DEADBAND_V8_Sidecar.mq5'
    Schreibe-Ascii $fea $EA_PATCH
    Write-Host "EA mit Sidecar-Lesen (Schalter aus = wie 8.10) abgelegt: $fea"
    $null = Kompiliere $inst $fea

    # 6) Aufgabe "DEADBAND Sidecar": beim Anmelden, 90 s Verzoegerung (nach "MT5 Autostart GFT"), interaktiv,
    #    Neustart bei Absturz 3 x je 1 min, keine Laufzeitgrenze
    $pyw = Join-Path $venv 'Scripts\pythonw.exe'
    $user = "$env:USERDOMAIN\$env:USERNAME"
    $akt = New-ScheduledTaskAction -Execute $pyw -Argument ('"' + (Join-Path $ZIEL 'sidecar.py') + '"') -WorkingDirectory $ZIEL
    $trig = New-ScheduledTaskTrigger -AtLogOn -User $user
    $trig.Delay = 'PT90S'
    $prin = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
    $set = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) `
        -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    Register-ScheduledTask -TaskName $AUFGABE -Action $akt -Trigger $trig -Principal $prin -Settings $set -Force | Out-Null
    Write-Host "Aufgabe '$AUFGABE' eingerichtet (beim Anmelden von $user, 90 s Verzoegerung)."

    # 7) Selbsttest
    $ErrorActionPreference = 'Continue'
    Write-Host ''
    Write-Host 'Selbsttest:' -ForegroundColor Cyan
    & $vpy (Join-Path $ZIEL 'sidecar.py') --selbsttest
    $selbst = ($LASTEXITCODE -eq 0)
    if ($selbst) { Write-Host 'Selbsttest bestanden.' -ForegroundColor Green }
    else { Write-Host 'Selbsttest NICHT bestanden - Ausgabe oben. Der EA handelt trotzdem unveraendert (fail-open).' -ForegroundColor Red }

    Write-Host ''
    Write-Host 'Alarme aufs Handy: App "ntfy" installieren, "+" > Thema abonnieren:' -ForegroundColor Cyan
    Write-Host "    $thema    (Server ntfy.sh)"
    Write-Host '  Das Thema ist das einzige "Passwort" des Kanals - nicht weitergeben.'
    $a = Read-Host 'Jetzt einen Testalarm senden? (j/n)'
    if ($a -match '^[jJyY]') { & $vpy (Join-Path $ZIEL 'sidecar.py') --testalarm }

    Start-ScheduledTask -TaskName $AUFGABE
    Write-Host ''
    Write-Host "Sidecar laeuft (Aufgabe '$AUFGABE'). Log: $ZIEL\logs\sidecar.log, Zustand: $daten\MQL5\Files\deadband_sidecar.txt" -ForegroundColor Green
    Write-Host 'Der EA liest den Sidecar erst, wenn du DEADBAND_Forschung\DEADBAND_V8_Sidecar mit SidecarLesen=true startest (BETRIEB.md).'
}
catch {
    Write-Host ''
    Write-Host ('FEHLER: ' + $_.Exception.Message) -ForegroundColor Red
}
