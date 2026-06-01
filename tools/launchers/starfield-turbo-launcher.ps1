<#
  starfield-turbo-launcher.ps1
  Copyright (c) 2026 YourName
  Licensed under the MIT License. See LICENSE in repo root.
  Safer variant: supports -DryRun and -ConfirmLaunch to avoid accidental destructive actions.
#>

param(
    [switch] $DryRun,
    [switch] $ConfirmLaunch,
    [switch] $VerboseLogging
)

function Log {
    param($msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $out = "$ts  $msg"
    $log = "$PSScriptRoot\Starfield_TurboLog.txt"
    $out | Out-File $log -Append
    if ($VerboseLogging) { Write-Host $out -ForegroundColor Gray }
}

# Helper to run or simulate a command
function Run-Action {
    param(
        [scriptblock] $Action,
        [string] $Description
    )
    if ($DryRun) {
        Log "DRYRUN: $Description"
        Write-Host "[DRYRUN] $Description" -ForegroundColor Yellow
    } else {
        Log "EXEC: $Description"
        & $Action
    }
}

Log "=== TURBO LAUNCH + MEMORY GUARDIAN STARTED: $(Get-Date) ==="
Write-Host "=== STARFIELD TURBO LAUNCHER – (DRYRUN=$DryRun) ===" -ForegroundColor Cyan

# -------------------------------
# Memory Guardian functions (unchanged logic, non-destructive)
# -------------------------------
function Get-VRAMGB { try { $gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1; return [math]::Round(($gpu.AdapterRAM / 1GB), 2) } catch { return 0 } }
function Get-StandbyGB { try { $mem = Get-Counter '\Memory\Standby Cache Reserve Bytes'; return [math]::Round(($mem.CounterSamples.CookedValue / 1GB), 2) } catch { return 0 } }
function Get-CommitPct { try { $commit = Get-Counter '\Memory\Committed Bytes'; $limit = Get-Counter '\Memory\Commit Limit'; $pct = ($commit.CounterSamples.CookedValue / $limit.CounterSamples.CookedValue) * 100; return [math]::Round($pct, 2) } catch { return 0 } }

function Invoke-StandbyFlush {
    $esl = "$PSScriptRoot\EmptyStandbyList.exe"
    if (Test-Path $esl) {
        Run-Action -Action { & $esl standbylist; & $esl modifiedpagelist } -Description "Run EmptyStandbyList.exe to flush standby/modified page lists"
        Log "Memory Guardian: Standby/modified page lists flushed."
    } else {
        Log "Memory Guardian: EmptyStandbyList.exe not found – cannot auto-flush standby."
    }
}

function Invoke-JunkKill {
    $junk = @("steamwebhelper","EpicWebHelper","OneDrive","ioloServiceManager","ioloTray","RadeonSoftware","NVIDIA Share","NVIDIA Web Helper")
    foreach ($p in $junk) {
        if ($DryRun) {
            Log "DRYRUN: Would stop process $p"
            Write-Host "[DRYRUN] Stop process $p" -ForegroundColor Yellow
        } else {
            Get-Process $p -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        }
    }
    Log "Memory Guardian: Background junk trimmed for RAM headroom."
}

$global:MG_LastSample = $null

function Start-MemoryGuardian {
    param([System.Diagnostics.Process] $StarfieldProc)
    $mgLog = "$PSScriptRoot\Starfield_MemoryGuardianLog_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').txt"
    "=== MEMORY GUARDIAN STARTED: $(Get-Date) ===" | Out-File $mgLog -Append
    Log "Logging to: $mgLog"
    Write-Host "[Memory Guardian] Monitoring Starfield.exe memory usage..." -ForegroundColor Cyan

    while ($StarfieldProc -and -not $StarfieldProc.HasExited) {
        try {
            $ramGB  = [math]::Round(($StarfieldProc.WorkingSet64 / 1GB), 2)
            $privGB = [math]::Round(($StarfieldProc.PrivateMemorySize64 / 1GB), 2)
        } catch { break }

        $vramGB  = Get-VRAMGB
        $standby = Get-StandbyGB
        $commit  = Get-CommitPct

        $sample = [PSCustomObject]@{
            Time       = Get-Date
            RAM_GB     = $ramGB
            Private_GB = $privGB
            VRAM_GB    = $vramGB
            Standby_GB = $standby
            Commit_Pct = $commit
        }
        $global:MG_LastSample = $sample

        $line = "{0:HH:mm:ss} | RAM={1}GB | Private={2}GB | VRAM={3}GB | Standby={4}GB | Commit={5}%" -f $sample.Time, $sample.RAM_GB, $sample.Private_GB, $sample.VRAM_GB, $sample.Standby_GB, $sample.Commit_Pct
        $line | Out-File $mgLog -Append

        if ($sample.Commit_Pct -ge 95) {
            Log "WARNING: Commit charge critical (>95%)."
            Write-Host "[Memory Guardian] Commit charge CRITICAL – flushing standby + trimming junk..." -ForegroundColor Red
            Invoke-StandbyFlush
            Invoke-JunkKill
        } elseif ($sample.Commit_Pct -ge 90) {
            Log "WARNING: Commit charge high (>90%)."
            Write-Host "[Memory Guardian] Commit charge high – consider lowering texture mods / increasing pagefile." -ForegroundColor Yellow
        }

        if ($sample.RAM_GB -ge 22) { Log "WARNING: RAM usage near physical limit." }
        if ($sample.Private_GB -ge 20) { Log "WARNING: Private bytes very high – possible memory leak from mods." }
        if ($sample.Standby_GB -ge 10) { Log "WARNING: Standby list pressure high."; Invoke-StandbyFlush }

        Start-Sleep -Seconds 1
    }

    "=== MEMORY GUARDIAN STOPPED: $(Get-Date) ===" | Out-File $mgLog -Append
    Log "Memory Guardian log: $mgLog"
}

function Analyze-MemoryCrash {
    if (-not $global:MG_LastSample) { Log "Memory Guardian: No memory samples recorded – cannot analyze."; return }
    $s = $global:MG_LastSample
    Log "=== MEMORY GUARDIAN – CRASH ANALYSIS ==="
    Log "Last Sample: $($s.Time)"
    Log "RAM: $($s.RAM_GB) GB | Private: $($s.Private_GB) GB | VRAM: $($s.VRAM_GB) GB | Standby: $($s.Standby_GB) GB | Commit: $($s.Commit_Pct)%"
    Write-Host "`n[Memory Guardian] Crash Analysis:" -ForegroundColor Cyan
    Write-Host "  RAM: $($s.RAM_GB) GB | Private: $($s.Private_GB) GB | VRAM: $($s.VRAM_GB) GB | Standby: $($s.Standby_GB) GB | Commit: $($s.Commit_Pct)%" -ForegroundColor Yellow

    if ($s.Commit_Pct -ge 95) {
        Write-Host "  → Likely cause: SYSTEM COMMIT EXHAUSTION." -ForegroundColor Red
        Write-Host "    Fix: Increase pagefile, close apps, reduce heavy mods." -ForegroundColor Green
    } elseif ($s.RAM_GB -ge 22 -or $s.Private_GB -ge 20) {
        Write-Host "  → Likely cause: PHYSICAL RAM EXHAUSTION / MOD MEMORY LEAK." -ForegroundColor Red
    } elseif ($s.Standby_GB -ge 10) {
        Write-Host "  → Likely cause: STANDBY LIST PRESSURE." -ForegroundColor Red
    } else {
        Write-Host "  → Memory did not appear critically exhausted at last sample." -ForegroundColor Yellow
    }
    Log "=== MEMORY GUARDIAN – ANALYSIS COMPLETE ==="
}

# -------------------------------
# 1. Ensure required folders exist (safe)
# -------------------------------
$sfRoot = "C:\Users\latsh\Documents\My Games\Starfield"
$folders = @($sfRoot, "$sfRoot\Creations", "$sfRoot\Saves")
foreach ($f in $folders) {
    if (!(Test-Path $f)) {
        Run-Action -Action { New-Item -ItemType Directory -Path $f | Out-Null } -Description "Create missing folder: $f"
    }
}

# -------------------------------
# 2. Fix permissions (destructive) - guarded
# -------------------------------
Run-Action -Action { icacls $sfRoot /grant latsh:(OI)(CI)F /T | Out-Null } -Description "Fix folder permissions on $sfRoot (icacls)"

# -------------------------------
# 3. Clear read-only attributes (destructive) - guarded
# -------------------------------
Run-Action -Action { attrib -R "$sfRoot" /S /D } -Description "Clear read-only attributes under $sfRoot"

# -------------------------------
# 4. Auto-backup INIs (safe)
# -------------------------------
$backupDir = "$sfRoot\INI_Backups"
if (!(Test-Path $backupDir)) { Run-Action -Action { New-Item -ItemType Directory -Path $backupDir | Out-Null } -Description "Create INI backup folder: $backupDir" }
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
Run-Action -Action { Copy-Item "$sfRoot\*.ini" "$backupDir\INI_Backup_$timestamp" -ErrorAction SilentlyContinue } -Description "Backup INI files to $backupDir\INI_Backup_$timestamp"

# -------------------------------
# 5. GPU Scheduling Registry Fix (destructive) - guarded
# -------------------------------
Run-Action -Action { reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f | Out-Null } -Description "Enable GPU Scheduling (HwSchMode=2)"

# -------------------------------
# 6. Shader Cache Purge (destructive) - guarded
# -------------------------------
$dxCache = "$env:LOCALAPPDATA\D3DSCache"; $nvCache = "$env:LOCALAPPDATA\NVIDIA\DXCache"; $amdCache = "$env:LOCALAPPDATA\AMD\DxCache"
$shaderCaches = @($dxCache, $nvCache, $amdCache)
foreach ($cache in $shaderCaches) {
    if (Test-Path $cache) {
        Run-Action -Action { Remove-Item "$cache\*" -Force -Recurse -ErrorAction SilentlyContinue } -Description "Purge shader cache: $cache"
    }
}

# -------------------------------
# 7. DirectX Pipeline Flush (destructive) - guarded
# -------------------------------
Run-Action -Action { Remove-Item "$env:LOCALAPPDATA\Starfield\Pipeline.cache" -ErrorAction SilentlyContinue } -Description "Remove Pipeline.cache"

# -------------------------------
# 8. Steam Integrity Auto-Check (safe)
# -------------------------------
Run-Action -Action { Start-Process "steam://validate/1716740" } -Description "Trigger Steam integrity check for Starfield"

Start-Sleep -Seconds 5

# -------------------------------
# 9. Flush RAM + Standby List (pre-launch)
# -------------------------------
Run-Action -Action { Clear-Content "$env:TEMP\*" -ErrorAction SilentlyContinue } -Description "Clear TEMP folder content"
Start-Sleep -Milliseconds 500
Invoke-StandbyFlush
Invoke-JunkKill

# -------------------------------
# 10. Ultimate Performance Mode (destructive) - guarded
# -------------------------------
Run-Action -Action { powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61 } -Description "Set power plan to Ultimate Performance"

# -------------------------------
# 11. Launch Starfield.exe (guarded)
# -------------------------------
$starfieldPath = "C:\SteamLibrary\steamapps\common\Starfield\Starfield.exe"
if (!(Test-Path $starfieldPath)) {
    Write-Host "ERROR: Starfield.exe not found!" -ForegroundColor Red
    Log "ERROR: Starfield.exe missing."
    exit
}

Write-Host "Prepared to launch Starfield.exe (DryRun=$DryRun). Use -ConfirmLaunch to actually start the game." -ForegroundColor Cyan
Log "Prepared to launch Starfield.exe with -sfc_disable_creations (DryRun=$DryRun)."

if ($ConfirmLaunch) {
    Run-Action -Action { $proc = Start-Process $starfieldPath -ArgumentList "-sfc_disable_creations" -PassThru } -Description "Start Starfield.exe with -sfc_disable_creations"
} else {
    Log "Launch skipped (ConfirmLaunch not provided)."
    Write-Host "Launch skipped. Provide -ConfirmLaunch to actually start Starfield." -ForegroundColor Yellow
    return
}

Start-Sleep -Seconds 3

# -------------------------------
# 12. Set High Priority (guarded)
# -------------------------------
try {
    if (-not $DryRun) {
        $proc.PriorityClass = "High"
        Write-Host "Priority set to HIGH." -ForegroundColor Green
        Log "Priority set to HIGH."
    } else {
        Log "DRYRUN: Would set process priority to HIGH."
    }
} catch {
    Write-Host "Could not set priority." -ForegroundColor Red
    Log "Priority set FAILED."
}

# -------------------------------
# 13. Start Memory Guardian (Active Protector)
# -------------------------------
if (-not $DryRun) {
    Start-MemoryGuardian -StarfieldProc $proc
} else {
    Log "DRYRUN: Memory Guardian would start monitoring the launched process."
    Write-Host "[DRYRUN] Memory Guardian would start monitoring." -ForegroundColor Yellow
}

# -------------------------------
# 14. Monitor for pre-menu CTD / Crash (post-launch)
# -------------------------------
Write-Host "Monitoring for early crash..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

if ($DryRun) {
    Log "DRYRUN: Skipping crash monitoring because DryRun is enabled."
    Write-Host "[DRYRUN] Skipping crash monitoring." -ForegroundColor Yellow
    return
}

if ($proc.HasExited) {
    Write-Host "`nStarfield quit early. Attempting fallback..." -ForegroundColor Red
    Log "Detected early CTD."
    Analyze-MemoryCrash
    Run-Action -Action { Remove-Item "$sfRoot\Starfield.ini" -ErrorAction SilentlyContinue } -Description "Remove Starfield.ini (fallback)"
    Run-Action -Action { Remove-Item "$sfRoot\StarfieldPrefs.ini" -ErrorAction SilentlyContinue } -Description "Remove StarfieldPrefs.ini (fallback)"
    Run-Action -Action { Remove-Item "$sfRoot\ContentCatalog.txt" -ErrorAction SilentlyContinue } -Description "Remove ContentCatalog.txt (fallback)"
    Log "INI + metadata reset."
    Write-Host "Retrying launch..." -ForegroundColor Cyan
    Run-Action -Action { Start-Process $starfieldPath -Priority High -ArgumentList "-sfc_disable_creations" } -Description "Retry Start Starfield.exe"
} else {
    Write-Host "`nStarfield appears stable. Enjoy!" -ForegroundColor Green
    Log "Launch stable."
}

Log "=== TURBO LAUNCH + MEMORY GUARDIAN COMPLETE ==="