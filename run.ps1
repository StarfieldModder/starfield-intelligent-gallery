# run.ps1 - launcher for the intro app
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# Activate the venv
& .\.venv\Scripts\Activate.ps1

# Ensure logs folder exists
if (-not (Test-Path -Path ".\logs")) {
    New-Item -ItemType Directory -Path ".\logs" | Out-Null
}

# Run the module with unbuffered output and tee to a dated log
$log = ".\logs\run_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss")
python -u -m intro.sig_main_intro 2>&1 | Tee-Object -FilePath $log
