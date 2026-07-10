Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
}
"@

function Get-WindowHandle {
    param([string]$Title)

    $windows = Get-Process | Where-Object { $_.MainWindowTitle -like "*$Title*" }
    if ($windows) {
        return $windows[0].MainWindowHandle
    }
    return [IntPtr]::Zero
}

function Lock-Window {
    param(
        [string]$Title,
        [int]$X,
        [int]$Y,
        [int]$Width,
        [int]$Height
    )

    $hWnd = Get-WindowHandle -Title $Title

    if ($hWnd -ne [IntPtr]::Zero) {
        [Win32]::MoveWindow($hWnd, $X, $Y, $Width, $Height, $true)
    }
}

# Load saved layout
$layoutFile = "$env:APPDATA\WindowLayout.json"

if (Test-Path $layoutFile) {
    $layout = Get-Content $layoutFile | ConvertFrom-Json
} else {
    $layout = @{
        LeftTitle  = "Visual Studio Code"
        RightTitle = "Copilot"
        LeftX      = 0
        LeftY      = 0
        LeftWidth  = 960
        LeftHeight = 1080
        RightX     = 960
        RightY     = 0
        RightWidth = 960
        RightHeight= 1080
    }
    $layout | ConvertTo-Json | Set-Content $layoutFile
}

Write-Host "Window Manager running. Press CTRL+C to stop."

while ($true) {
    Lock-Window -Title $layout.LeftTitle `
                -X $layout.LeftX -Y $layout.LeftY `
                -Width $layout.LeftWidth -Height $layout.LeftHeight

    Lock-Window -Title $layout.RightTitle `
                -X $layout.RightX -Y $layout.RightY `
                -Width $layout.RightWidth -Height $layout.RightHeight

    Start-Sleep -Seconds 2
}
