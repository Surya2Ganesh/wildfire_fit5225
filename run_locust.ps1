$projectPath = "C:\Users\surya\OneDrive\Desktop\wildfire-detection"
Set-Location $projectPath

& "$projectPath\venv\Scripts\Activate.ps1"

Write-Host "Starting Locust load test..."
Write-Host "Once started, open browser at: http://localhost:8089"
Write-Host ""

locust -f locust\locustfile.py --host http://127.0.0.1:30080
