# FIT5225 Assignment 1 - CloudEco Wildfire Detection

Student ID: 35415940

This project implements the CloudEco REST API for wildfire and smoke detection using FastAPI, Ultralytics YOLO, Docker, Kubernetes, Locust, and OCI Terraform Infrastructure as Code.

## Public Deployment

Base URL:

```text
http://169.224.230.182:30080
```

Useful endpoints:

```text
GET  /health
POST /api/predict
POST /api/annotate
```

Quick health check:

```powershell
curl.exe http://169.224.230.182:30080/health
```

## API Payload

Both `/api/predict` and `/api/annotate` accept JSON in this format:

```json
{
  "uuid": "example-request-id",
  "image": "base64-encoded-image"
}
```

`/api/predict` returns detections, bounding boxes, confidence scores, and YOLO timing metrics.

`/api/annotate` returns a base64 JPEG image with YOLO bounding boxes and labels drawn onto it.

## Local Python Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
pip install -r requirements-test.txt
```

Run the FastAPI app locally:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Local API docs:

```text
http://localhost:8000/docs
```

## Docker

Build the Docker image:

```powershell
docker build -t wildfire-api:latest .
```

Run the Docker container:

```powershell
docker run --rm -p 8000:8000 wildfire-api:latest
```

Docker Hub image used by Kubernetes:

```text
suryaganesh2210/wildfire-api:latest
```

## Kubernetes

Apply the manifests:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check deployment status:

```bash
kubectl get nodes -o wide
kubectl get pods -n cloudeco -o wide
kubectl get svc -n cloudeco -o wide
```

Scale the deployment for benchmarking:

```bash
kubectl scale deployment wildfire-api -n cloudeco --replicas=1
kubectl scale deployment wildfire-api -n cloudeco --replicas=2
kubectl scale deployment wildfire-api -n cloudeco --replicas=4
kubectl scale deployment wildfire-api -n cloudeco --replicas=6
```

Benchmarks were run at 1, 2, 4, and 6 pods. Although the assignment suggested testing up to 8 pods, this deployment used a 2 GiB memory request per pod, and the available cluster memory was not sufficient to schedule 8 pods reliably. Six pods was the highest stable scheduled configuration.

## Locust Load Testing

Run Locust against the public deployment:

```powershell
.\.venv\Scripts\python.exe -m locust -f locust\locustfile.py --host http://169.224.230.182:30080
```

Open the Locust UI:

```text
http://localhost:8089
```

## Test Scripts

Run a prediction request:

```powershell
.\.venv\Scripts\python.exe tests\test_predict.py
```

Run an annotation request and save the returned image:

```powershell
.\.venv\Scripts\python.exe tests\test_annotate.py
```

The annotation output is saved to:

```text
tests/annotated_output.jpeg
```

## Infrastructure as Code

Terraform IaC is stored in:

```text
Iac/
```

It provisions the OCI network and three Ubuntu VMs required for the Kubernetes cluster:

- one VCN
- one public subnet
- internet gateway
- route table
- security list
- one master VM
- two worker VMs

Terraform validation:

```powershell
terraform -chdir=Iac init -backend=false
terraform -chdir=Iac validate
```

## Interview Startup Helper

The PowerShell helper script opens the local demo environment, test terminals, browser tabs, SSH sessions, and Locust:

```powershell
.\start_fit5225.ps1
```
