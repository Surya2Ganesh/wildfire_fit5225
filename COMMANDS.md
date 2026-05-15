# CloudEco — All Commands Reference
## FIT5225 Assignment 1 | Wildfire & Smoke Detection API

---

## START EVERYTHING (One Command)

```powershell
.\start_wildfire.ps1
```

**What this script does automatically (7 steps):**
1. Starts Docker Desktop (skips if already running)
2. Waits for Docker engine to become ready (polls every 5s, up to 5 min)
3. Navigates to the project folder
4. Activates the Python virtual environment (`venv\Scripts\Activate.ps1`)
5. Waits for the Kubernetes cluster to become ready (polls every 10s)
6. Runs `kubectl apply -f k8s/deployment.yaml` and `kubectl apply -f k8s/service.yaml`
7. Scales to 1 replica, waits 15 seconds, then opens `http://127.0.0.1:30080/docs`

> After the script finishes, the API is live at **http://127.0.0.1:30080**

---

## 1. DOCKER — Build & Manage Image

### Build the image (run once, or after code changes)
```
docker build -t wildfire-api:latest .
```

### Run container locally (without Kubernetes)
```
docker run -p 8000:8000 wildfire-api:latest
```

### Run container in background
```
docker run -d -p 8000:8000 --name wildfire wildfire-api:latest
```

### Check running containers
```
docker ps
```

### View container logs
```
docker logs wildfire
docker logs wildfire -f
```

### Stop and remove container
```
docker stop wildfire
docker rm wildfire
```

### List all Docker images
```
docker images
```

### Remove the image
```
docker rmi wildfire-api:latest
```

---

## 2. DOCKER — Load Image onto Kubernetes Nodes

### Save image to a tar file
```
docker save wildfire-api:latest -o wildfire-api.tar
```

### Copy and load onto each node
```
scp wildfire-api.tar ubuntu@<MASTER_IP>:~/
ssh ubuntu@<MASTER_IP> "docker load -i wildfire-api.tar"

scp wildfire-api.tar ubuntu@<WORKER1_IP>:~/
ssh ubuntu@<WORKER1_IP> "docker load -i wildfire-api.tar"

scp wildfire-api.tar ubuntu@<WORKER2_IP>:~/
ssh ubuntu@<WORKER2_IP> "docker load -i wildfire-api.tar"
```

---

## 3. KUBERNETES — Deploy the Application

### Apply both manifests at once
```
kubectl apply -f k8s/
```

### Or apply individually
```
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Check everything is running
```
kubectl get all
```

---

## 4. KUBERNETES — Check Status

### See pods (are they Running?)
```
kubectl get pods
```

### See pods + which node they are on
```
kubectl get pods -o wide
```

### See deployments
```
kubectl get deployments
```

### See services (find NodePort 30080)
```
kubectl get services
```

### See nodes (are they Ready?)
```
kubectl get nodes
```

---

## 5. KUBERNETES — Scaling (Benchmarking)

```
kubectl scale deployment wildfire-api --replicas=1
kubectl scale deployment wildfire-api --replicas=2
kubectl scale deployment wildfire-api --replicas=4
kubectl scale deployment wildfire-api --replicas=8
```

### Watch pods scale up in real time
```
kubectl get pods -w
```

---

## 6. KUBERNETES — Logs & Debugging

### View pod logs
```
kubectl logs <pod-name>
kubectl logs <pod-name> -f
```

### Describe a pod (shows events, probe results, errors)
```
kubectl describe pod <pod-name>
```

### Describe deployment or service
```
kubectl describe deployment wildfire-api
kubectl describe service wildfire-api-service
```

### View cluster events sorted by time
```
kubectl get events --sort-by='.lastTimestamp'
```

### CPU and memory usage
```
kubectl top pods
kubectl top nodes
```

---

## 7. KUBERNETES — Cleanup

```
kubectl delete -f k8s/
```

Or individually:
```
kubectl delete deployment wildfire-api
kubectl delete service wildfire-api-service
```

---

## 8. TEST THE API

### Health check
```
curl http://127.0.0.1:30080/
```

### Run the manual test script (sends one real image to /api/predict)
```
python scripts/test_request.py
```

### Open Swagger UI in browser
```
http://127.0.0.1:30080/docs
```

---

## 9. LOCUST — Load Testing

### Start Locust with web UI (then open browser at localhost:8089)
```
locust -f locust/locustfile.py --host http://127.0.0.1:30080
```

### Headless mode (no browser needed)
```
locust -f locust/locustfile.py --host http://127.0.0.1:30080 --headless --users 10 --spawn-rate 2 --run-time 60s
```

### Example benchmark runs used in the report
```
# 1 pod — ramp up users until breaking point
locust -f locust/locustfile.py --host http://127.0.0.1:30080

# Scale to 2 pods, then run again
kubectl scale deployment wildfire-api --replicas=2
locust -f locust/locustfile.py --host http://127.0.0.1:30080

# Scale to 4 pods, then run again
kubectl scale deployment wildfire-api --replicas=4
locust -f locust/locustfile.py --host http://127.0.0.1:30080

# Scale to 8 pods, then run again
kubectl scale deployment wildfire-api --replicas=8
locust -f locust/locustfile.py --host http://127.0.0.1:30080
```

---

## 10. TERRAFORM — OCI Infrastructure

```
cd teraform
```

### Initialise (first time only — downloads OCI provider)
```
terraform init
```

### Preview what will be created
```
terraform plan
```

### Create VMs + networking on OCI
```
terraform apply
```

### Get VM public IPs after creation
```
terraform output
```

### Start stopped VMs
```
.\start-vms.ps1
```

### Stop VMs (save OCI credits)
```
.\stop-vms.ps1
```

### Destroy all OCI resources
```
terraform destroy
```
```
.\destroy-all.ps1
```

---

## 11. GIT — Push Updates to GitHub

```
git add .
git commit -m "your message"
git push origin main
```

### Check what changed
```
git status
git log --oneline
```

---

## 12. FULL INTERVIEW DEMO SEQUENCE

```powershell
# 1 — Start everything
.\start_wildfire.ps1

# 2 — Confirm cluster is healthy
kubectl get nodes

# 3 — Confirm pods are running
kubectl get pods -o wide

# 4 — Confirm service is exposed
kubectl get services

# 5 — Hit the health endpoint
curl http://127.0.0.1:30080/

# 6 — Run a real inference request
python scripts/test_request.py

# 7 — Start load test (open http://localhost:8089)
locust -f locust/locustfile.py --host http://127.0.0.1:30080

# 8 — Scale pods while load test runs
kubectl scale deployment wildfire-api --replicas=4

# 9 — Watch new pods come up
kubectl get pods -w
```

---

## QUICK LOOKUP TABLE

| Task                          | Command                                                    |
|-------------------------------|------------------------------------------------------------|
| Start everything              | `.\start_wildfire.ps1`                                     |
| Build Docker image            | `docker build -t wildfire-api:latest .`                    |
| Deploy to Kubernetes          | `kubectl apply -f k8s/`                                    |
| Check pods                    | `kubectl get pods`                                         |
| Check services                | `kubectl get services`                                     |
| Scale to N pods               | `kubectl scale deployment wildfire-api --replicas=N`       |
| View pod logs                 | `kubectl logs <pod-name>`                                  |
| Debug a pod                   | `kubectl describe pod <pod-name>`                          |
| Test API manually             | `python scripts/test_request.py`                           |
| Open Swagger docs             | `http://127.0.0.1:30080/docs`                              |
| Start Locust load test        | `locust -f locust/locustfile.py --host http://...`         |
| Provision OCI VMs             | `cd teraform && terraform apply`                           |
| Destroy OCI VMs               | `cd teraform && terraform destroy`                         |
| Push code to GitHub           | `git add . && git commit -m "msg" && git push`             |

---

> **Port reference:** Container runs on `8000` internally → NodePort exposes it as `30080` externally
> **Resource limits:** Each pod = 1 vCPU + 2Gi RAM (defined in `k8s/deployment.yaml`)
> **Model:** `fire-models/fire_m.pt` — detects **Fire** and **Smoke**
