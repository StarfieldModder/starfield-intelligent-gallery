# ================================================================
# create_sig_shortcut.ps1
# Starfield Intelligent Gallery — Desktop Shortcut Creator
#
# Run this ONCE from PowerShell:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\create_sig_shortcut.ps1
#
# What it does:
#   1. Creates "Starfield Intelligent Gallery.lnk" on your Desktop
#   2. Points it to pythonw.exe (no console window when SIG launches)
#   3. Sets the working directory to C:\SIG
#   4. Applies C:\SIG\Installer\sig.ico as the icon
#
# After running:
#   Right-click the Desktop shortcut → "Pin to taskbar"
# ================================================================

$AppName     = "Starfield Intelligent Gallery"
$SIGRoot     = "C:\SIG"
$PythonW     = "$SIGRoot\.venv\Scripts\pythonw.exe"
$Script      = "$SIGRoot\sig_launcher.py"
$IconPath    = "$SIGRoot\Installer\sig.ico"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$LinkPath    = "$DesktopPath\$AppName.lnk"

# ── Verify paths ──────────────────────────────────────────────────────────────
if (-not (Test-Path $PythonW)) {
    Write-Host "ERROR: pythonw.exe not found at $PythonW" -ForegroundColor Red
    Write-Host "       Make sure your .venv is set up inside C:\SIG\" -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path $Script)) {
    Write-Host "ERROR: sig_launcher.py not found at $Script" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $IconPath)) {
    Write-Host "WARNING: sig.ico not found at $IconPath" -ForegroundColor Yellow
    Write-Host "         Shortcut will be created without a custom icon." -ForegroundColor Yellow
    $IconPath = $PythonW   # fallback to python icon
}

# ── Create the shortcut ───────────────────────────────────────────────────────
$Shell    = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($LinkPath)

$Shortcut.TargetPath       = $PythonW
$Shortcut.Arguments        = "`"$Script`""
$Shortcut.WorkingDirectory = $SIGRoot
$Shortcut.IconLocation     = "$IconPath, 0"
$Shortcut.Description      = "Starfield Intelligent Gallery — Launch Pad"
$Shortcut.WindowStyle      = 1   # Normal window

$Shortcut.Save()

# ── Also create a Start Menu shortcut ────────────────────────────────────────
$StartMenu  = [Environment]::GetFolderPath("StartMenu")
$StartPrograms = "$StartMenu\Programs"
$StartLink  = "$StartPrograms\$AppName.lnk"

$Shortcut2 = $Shell.CreateShortcut($StartLink)
$Shortcut2.TargetPath       = $PythonW
$Shortcut2.Arguments        = "`"$Script`""
$Shortcut2.WorkingDirectory = $SIGRoot
$Shortcut2.IconLocation     = "$IconPath, 0"
$Shortcut2.Description      = "Starfield Intelligent Gallery — Launch Pad"
$Shortcut2.WindowStyle      = 1
$Shortcut2.Save()

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ✓ Desktop shortcut created:" -ForegroundColor Green
Write-Host "    $LinkPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ✓ Start Menu shortcut created:" -ForegroundColor Green
Write-Host "    $StartLink" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ──────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  TO PIN TO TASKBAR:" -ForegroundColor Yellow
Write-Host "    Right-click the Desktop shortcut" -ForegroundColor White
Write-Host "    → 'Pin to taskbar'" -ForegroundColor White
Write-Host "  ──────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""
