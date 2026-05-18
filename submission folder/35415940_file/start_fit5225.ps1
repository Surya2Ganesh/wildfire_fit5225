# ============================================================
# FIT5225 Assignment 1 - Reliable Interview Startup Script
# Fixes path-with-spaces issues by launching separate .bat files.
# Opens:
#   1. VS Code
#   2. Docker Desktop
#   3. Browser health/docs/Locust
#   4. Locust terminal
#   5. Local test terminal
#   6. Master terminal: scale to 1 pod + watch pods
#   7. Worker 1 terminal
#   8. Worker 2 terminal
# ============================================================

$ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$DockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
$PythonExe = Join-Path $ProjectPath ".venv\Scripts\python.exe"

$PublicBaseUrl = "http://169.224.230.182:30080"

$KeyPath = "C:\Users\surya\OneDrive\Desktop\oraclekey\fit5225_oci_key"

$MasterIP = "169.224.230.182"
$Worker1IP = "161.33.93.53"
$Worker2IP = "152.69.179.232"

$SSHExe = "C:\Windows\System32\OpenSSH\ssh.exe"

$TempFolder = Join-Path $ProjectPath "startup-temp"

Write-Host "Starting FIT5225 interview environment..." -ForegroundColor Cyan

# ------------------------------------------------------------
# 1. Basic checks
# ------------------------------------------------------------

if (!(Test-Path $ProjectPath)) {
    Write-Host "Project folder not found:" -ForegroundColor Red
    Write-Host $ProjectPath
    exit 1
}

if (!(Test-Path $PythonExe)) {
    Write-Host "Venv Python not found:" -ForegroundColor Red
    Write-Host $PythonExe
    Write-Host "Create/activate venv first."
    exit 1
}

if (!(Test-Path $KeyPath)) {
    Write-Host "SSH key not found:" -ForegroundColor Red
    Write-Host $KeyPath
    exit 1
}

if (!(Test-Path $SSHExe)) {
    Write-Host "ssh.exe not found at:" -ForegroundColor Red
    Write-Host $SSHExe
    exit 1
}

if (!(Test-Path $TempFolder)) {
    New-Item -ItemType Directory -Path $TempFolder | Out-Null
}

# ------------------------------------------------------------
# 2. Open VS Code
# ------------------------------------------------------------

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$ProjectPath`"; code ."
)

# ------------------------------------------------------------
# 3. Start Docker Desktop
# ------------------------------------------------------------

if (Test-Path $DockerDesktopPath) {
    Start-Process "$DockerDesktopPath"
}

# ------------------------------------------------------------
# 4. Open browser tabs
# ------------------------------------------------------------

Start-Process "$PublicBaseUrl/health"
Start-Process "$PublicBaseUrl/docs"
Start-Process "http://localhost:8089"

# ------------------------------------------------------------
# 5. Create Locust launcher
# ------------------------------------------------------------

$LocustBat = "$TempFolder\start_locust.bat"

@"
@echo off
title FIT5225 - Locust Load Test
cd /d "$ProjectPath"
echo Starting Locust...
echo Host: $PublicBaseUrl
echo Open browser: http://localhost:8089
"$PythonExe" -m locust -f locust\locustfile.py --host $PublicBaseUrl
pause
"@ | Set-Content $LocustBat -Encoding ASCII

Start-Process "cmd.exe" -ArgumentList "/k `"$LocustBat`""

# ------------------------------------------------------------
# 6. Create local test terminal launcher
# ------------------------------------------------------------

$LocalTestBat = "$TempFolder\local_tests.bat"

@"
@echo off
title FIT5225 - Local Tests
cd /d "$ProjectPath"
echo Local test terminal ready.
echo.
echo Useful commands:
echo "$PythonExe" tests\test_predict.py
echo "$PythonExe" tests\test_annotate.py
echo curl.exe $PublicBaseUrl/health
echo.
cmd /k
"@ | Set-Content $LocalTestBat -Encoding ASCII

Start-Process "cmd.exe" -ArgumentList "/k `"$LocalTestBat`""

# ------------------------------------------------------------
# 7. Create master launcher
# This connects to master and runs Linux commands INSIDE Ubuntu:
#   kubectl scale ...
#   watch kubectl get pods ...
# ------------------------------------------------------------

$MasterBat = "$TempFolder\master_watch.bat"

@"
@echo off
title FIT5225 - Master Kubernetes Watch
cd /d "$ProjectPath"
echo Connecting to master VM...
echo This will scale wildfire-api to 1 pod and watch pod status.
echo.
"$SSHExe" -tt -i "$KeyPath" ubuntu@$MasterIP "kubectl scale deployment wildfire-api -n cloudeco --replicas=1; watch kubectl get pods -n cloudeco -o wide"
pause
"@ | Set-Content $MasterBat -Encoding ASCII

Start-Process "cmd.exe" -ArgumentList "/k `"$MasterBat`""

# ------------------------------------------------------------
# 8. Create worker 1 launcher
# ------------------------------------------------------------

$Worker1Bat = "$TempFolder\worker1.bat"

@"
@echo off
title FIT5225 - Worker 1
cd /d "$ProjectPath"
echo Connecting to worker 1...
"$SSHExe" -i "$KeyPath" ubuntu@$Worker1IP
pause
"@ | Set-Content $Worker1Bat -Encoding ASCII

Start-Process "cmd.exe" -ArgumentList "/k `"$Worker1Bat`""

# ------------------------------------------------------------
# 9. Create worker 2 launcher
# ------------------------------------------------------------

$Worker2Bat = "$TempFolder\worker2.bat"

@"
@echo off
title FIT5225 - Worker 2
cd /d "$ProjectPath"
echo Connecting to worker 2...
"$SSHExe" -i "$KeyPath" ubuntu@$Worker2IP
pause
"@ | Set-Content $Worker2Bat -Encoding ASCII

Start-Process "cmd.exe" -ArgumentList "/k `"$Worker2Bat`""

# ------------------------------------------------------------
# 10. Final instructions
# ------------------------------------------------------------

Write-Host ""
Write-Host "All startup windows opened." -ForegroundColor Green
Write-Host ""
Write-Host "Master terminal should automatically run:" -ForegroundColor Yellow
Write-Host "kubectl scale deployment wildfire-api -n cloudeco --replicas=1"
Write-Host "watch kubectl get pods -n cloudeco -o wide"
Write-Host ""
Write-Host "To stop watch in master terminal: CTRL + C" -ForegroundColor Yellow
Write-Host ""
Write-Host "Scaling demo commands after stopping watch:" -ForegroundColor Cyan
Write-Host "kubectl scale deployment wildfire-api -n cloudeco --replicas=2"
Write-Host "watch kubectl get pods -n cloudeco -o wide"
Write-Host ""
Write-Host "kubectl scale deployment wildfire-api -n cloudeco --replicas=4"
Write-Host "watch kubectl get pods -n cloudeco -o wide"
Write-Host ""
Write-Host "kubectl scale deployment wildfire-api -n cloudeco --replicas=6"
Write-Host "watch kubectl get pods -n cloudeco -o wide"
Write-Host ""
Write-Host "Public API: $PublicBaseUrl" -ForegroundColor Cyan
Write-Host "Locust UI: http://localhost:8089" -ForegroundColor Cyan
