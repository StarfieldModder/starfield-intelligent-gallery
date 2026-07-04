@echo off
:: ================================================================
:: SIGLauncher.bat
:: Starfield Intelligent Gallery — Desktop Launch Script
:: Author   : Mark J. Latsha  (StarfieldModder / Games)
:: Co-Author: Microsoft Copilot (AI Engineering Collaborator)
:: Created  : Thursday, July 2, 2026
:: ================================================================
:: Deployed by the MSI installer to:
::   %LOCALAPPDATA%\StarfieldIntelligentGallery\SIGLauncher.bat
:: Always launches from C:\SIG where the Python source lives.
:: ================================================================

title Starfield Intelligent Gallery

:: Go to the SIG source root
cd /d "C:\SIG"

:: Activate the virtual environment
if exist "C:\SIG\.venv\Scripts\activate.bat" (
    call "C:\SIG\.venv\Scripts\activate.bat"
) else (
    echo WARNING: .venv not found at C:\SIG\.venv
    echo Using system Python instead.
)

:: Launch SIG
python "C:\SIG\sig_launcher.py"

:: Keep window open only if there was an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo SIG exited with error code %ERRORLEVEL%
    pause
)
