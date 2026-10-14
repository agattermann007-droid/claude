# Gemeinsamer PowerShell-Baustein: GFT-Terminal und Datenordner finden.
# Regeln: die Altlast unter C:\Program Files\MetaTrader 5 wird nie ausgewaehlt.
# Vorrang: Datei C:\Trading\gft_terminal.txt (eine Zeile = Installationsordner des GFT-Terminals).
$ALTLAST = 'C:\Program Files\MetaTrader 5'

function Normpfad([string]$p) {
    if (-not $p) { return '' }
    try { $p = [IO.Path]::GetFullPath($p.Trim()) } catch { }
    return $p.TrimEnd('\').ToLowerInvariant()
}

function Lies-Origin([string]$datei) {
    $b = [IO.File]::ReadAllBytes($datei)
    if ($b.Length -ge 2 -and $b[0] -eq 0xFF -and $b[1] -eq 0xFE) { $t = [Text.Encoding]::Unicode.GetString($b, 2, $b.Length - 2) }
    elseif ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) { $t = [Text.Encoding]::UTF8.GetString($b, 3, $b.Length - 3) }
    else { $t = [Text.Encoding]::Default.GetString($b) }
    return ($t -split "`r?`n")[0].Trim([char]0, ' ')
}

function Origin-Liste {
    $root = Join-Path $env:APPDATA 'MetaQuotes\Terminal'
    $liste = @()
    if (-not (Test-Path $root)) { return $liste }
    foreach ($d in @(Get-ChildItem -Path $root -Directory -ErrorAction SilentlyContinue)) {
        $o = Join-Path $d.FullName 'origin.txt'
        if (-not (Test-Path $o)) { continue }
        $inst = Lies-Origin $o
        if ($inst) { $liste += [pscustomobject]@{ Inst = $inst; Daten = $d.FullName } }
    }
    return $liste
}

function Gft-Installation {
    $alt = Normpfad $ALTLAST
    $vorgabe = 'C:\Trading\gft_terminal.txt'
    if (Test-Path $vorgabe) {
        $inst = (Get-Content -LiteralPath $vorgabe -TotalCount 1).Trim()
        if ((Normpfad $inst) -eq $alt) { throw "In $vorgabe steht die Altlast-Installation - bitte den GFT-Ordner eintragen." }
        if (-not (Test-Path (Join-Path $inst 'terminal64.exe'))) { throw "In $vorgabe steht '$inst', dort gibt es keine terminal64.exe." }
        Write-Host "GFT-Terminal laut $vorgabe : $inst"
        return $inst
    }
    $kand = @()
    foreach ($pr in @(Get-Process -Name terminal64 -ErrorAction SilentlyContinue)) {
        $pf = $null
        try { $pf = $pr.Path } catch { }
        if (-not $pf) { continue }
        $dir = Split-Path $pf -Parent
        if ((Normpfad $dir) -eq $alt) { continue }
        if (-not ($kand | Where-Object { (Normpfad $_) -eq (Normpfad $dir) })) { $kand += $dir }
    }
    if ($kand.Count -eq 0) {
        foreach ($e in (Origin-Liste)) {
            if ((Normpfad $e.Inst) -eq $alt) { continue }
            if (-not (Test-Path (Join-Path $e.Inst 'terminal64.exe'))) { continue }
            if (-not ($kand | Where-Object { (Normpfad $_) -eq (Normpfad $e.Inst) })) { $kand += $e.Inst }
        }
    }
    if ($kand.Count -eq 0) { throw 'Kein GFT-Terminal gefunden (laeuft es?). Ausweg: Installationsordner in C:\Trading\gft_terminal.txt eintragen.' }
    if ($kand.Count -eq 1) { Write-Host "GFT-Terminal: $($kand[0])"; return $kand[0] }
    Write-Host 'Mehrere Terminals gefunden (die Altlast ist ausgeschlossen):'
    for ($i = 0; $i -lt $kand.Count; $i++) { Write-Host ("  [{0}] {1}" -f ($i + 1), $kand[$i]) }
    $w = Read-Host 'Nummer des GFT-Terminals'
    $n = 0
    if (-not [int]::TryParse($w, [ref]$n) -or $n -lt 1 -or $n -gt $kand.Count) { throw 'Ungueltige Auswahl.' }
    return $kand[$n - 1]
}

function Gft-Datenordner([string]$inst) {
    foreach ($e in (Origin-Liste)) {
        if ((Normpfad $e.Inst) -eq (Normpfad $inst)) { return $e.Daten }
    }
    if (Test-Path (Join-Path $inst 'MQL5')) { return $inst }      # portabler Betrieb
    throw "Datenordner zum Terminal $inst nicht gefunden."
}
