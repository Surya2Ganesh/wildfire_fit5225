# -----------------------------
# Wildfire assignment startup script
# This script:
# 1. Starts Docker Desktop
# 2. Waits for Docker engine
# 3. Changes into the project folder
# 4. Activates the local Python virtual environment
# 5. Waits for the Kubernetes cluster
# 6. Applies deployment + service manifests
# 7. Shows status and opens the API docs
# -----------------------------

# Root of the project so every relative path below resolves correctly.
$projectPath = "C:\Users\surya\OneDrive\Desktop\wildfire-detection"

# Full path to Docker Desktop on this machine.
$dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

Write-Host "======================================="
Write-Host "Starting Wildfire Assignment Environment"
Write-Host "======================================="

# -----------------------------
# Step 1: Start Docker Desktop
# -----------------------------
Write-Host "`n[1/7] Starting Docker Desktop..."

# Start Docker Desktop only if it is not already running.
# This avoids opening duplicate windows/processes.
$dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerProcess) {
    Start-Process $dockerDesktopPath
    Write-Host "Docker Desktop launched."
} else {
    Write-Host "Docker Desktop is already running."
}

# -----------------------------
# Step 2: Wait for Docker engine
# -----------------------------
Write-Host "`n[2/7] Waiting for Docker engine to become ready..."

$dockerReady = $false
for ($i = 1; $i -le 60; $i++) {
    # "docker version" succeeds only when the Docker engine is reachable.
    # Redirecting output to $null keeps the console clean while polling.
    docker version *> $null
    if ($LASTEXITCODE -eq 0) {
        $dockerReady = $true
        break
    }

    Write-Host "Docker not ready yet... waiting 5 seconds"
    Start-Sleep -Seconds 5
}

if (-not $dockerReady) {
    Write-Host "Docker engine did not become ready in time."
    exit 1
}

Write-Host "Docker engine is ready."

# -----------------------------
# Step 3: Go to project folder
# -----------------------------
Write-Host "`n[3/7] Moving to project folder..."
Set-Location $projectPath
Write-Host "Current folder: $(Get-Location)"

# -----------------------------
# Step 4: Activate virtual environment
# -----------------------------
Write-Host "`n[4/7] Activating Python virtual environment..."

# Build the activation script path from the project root so it still works
# even if the script is started from another folder.
$venvActivate = Join-Path $projectPath "venv\Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    # Run the activation script so python/pip commands use the local venv.
    & $venvActivate
    Write-Host "Virtual environment activated."
} else {
    Write-Host "Virtual environment not found at: $venvActivate"
    exit 1
}

# -----------------------------
# Step 5: Wait for Kubernetes
# -----------------------------
Write-Host "`n[5/7] Waiting for Kubernetes cluster to become ready..."

$kubeReady = $false
for ($i = 1; $i -le 60; $i++) {
    # This probe succeeds once kubectl can talk to the Kubernetes control plane.
    kubectl get nodes *> $null
    if ($LASTEXITCODE -eq 0) {
        $kubeReady = $true
        break
    }

    Write-Host "Kubernetes not ready yet... waiting 10 seconds"
    Start-Sleep -Seconds 10
}

if (-not $kubeReady) {
    Write-Host "Kubernetes cluster did not become ready in time."
    Write-Host "Open Docker Desktop and make sure the cluster is running."
    exit 1
}

Write-Host "Kubernetes cluster is ready."

# Show node info
Write-Host "`nKubernetes nodes:"
kubectl get nodes

# -----------------------------
# Step 6: Apply deployment + service
# -----------------------------
Write-Host "`n[6/7] Applying Kubernetes files..."

# Create or update the Deployment object that runs the API container.
kubectl apply -f .\k8s\deployment.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to apply deployment.yaml"
    exit 1
}

# Create or update the Service object that exposes the API on a stable port.
kubectl apply -f .\k8s\service.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to apply service.yaml"
    exit 1
}

# Make sure exactly one API pod is running for this assignment setup.
Write-Host "`nScaling deployment to 1 replica..."
kubectl scale deployment wildfire-api --replicas=1

# Give Kubernetes a moment to pull the image and start the pod.
Write-Host "Waiting 15 seconds for pod startup..."
Start-Sleep -Seconds 15

# -----------------------------
# Step 7: Show status and open docs
# -----------------------------
Write-Host "`n[7/7] Checking pod and service status..."

Write-Host "`nPods:"
kubectl get pods

Write-Host "`nServices:"
kubectl get svc

# The service exposes NodePort 30080, so opening /docs reaches FastAPI Swagger UI.
Write-Host "`nOpening Swagger docs..."
Start-Process "http://127.0.0.1:30080/docs"

Write-Host "`n======================================="
Write-Host "Wildfire environment is ready"
Write-Host "======================================="
