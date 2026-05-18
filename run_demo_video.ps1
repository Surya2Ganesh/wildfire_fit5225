$projectPath = "C:\Users\surya\OneDrive\Desktop\wildfire-detection"
Set-Location $projectPath
& "$projectPath\venv\Scripts\Activate.ps1"
python scripts/demo_video.py
