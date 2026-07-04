@echo off
title Starfield Intelligent Gallery
cd /d "C:\SIG"
call "C:\SIG\.venv\Scripts\activate.bat"
"C:\SIG\.venv\Scripts\python.exe" "C:\SIG\sig_launcher.py"
exit