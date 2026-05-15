# CloudEco — All Commands Reference
## FIT5225 Assignment 1 | Wildfire & Smoke Detection API

---

## 1. PROJECT SETUP (Local Machine)

### Navigate to project
```
cd C:\Users\surya\OneDrive\Desktop\wildfire-detection
```

### Install Python dependencies (local testing only)
```
pip install -r requirements_a1.txt
```

### Run API locally (without Docker)
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Test API is running (local)
```
curl http://localhost:8000/
```

---

## 2. DOCKER — Build & Run Container

### Build the Docker image
```
docker build -t wildfire-api:latest .
```

### Run the container locally
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
```
```
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

### Remove Docker image
```
docker rmi wildfire-api:latest
```

---

## 3. DOCKER — Load Image onto Kubernetes Nodes

### Save image to a tar file
```
docker save wildfire-api:latest -o wildfire-api.tar
```

### Copy and load onto master node
```
scp wildfire-api.tar ubuntu@<MASTER_IP>:~/
ssh ubuntu@<MASTER_IP> "docker load -i wildfire-api.tar"
```

### Copy and load onto worker1
```
scp wildfire-api.tar ubuntu@<WORKER1_IP>:~/
ssh ubuntu@<WORKER1_IP> "docker load -i wildfire-api.tar"
```

### Copy and load onto worker2
```
scp wildfire-api.tar ubuntu@<WORKER2_IP>:~/
ssh ubuntu@<WORKER2_IP> "docker load -i wildfire-api.tar"
```

---

## 4. KUBERNETES — Setup Cluster (Run on VMs via SSH)

### SSH into master node
```
ssh ubuntu@<MASTER_IP>
```

### SSH into worker nodes
```
ssh ubuntu@<WORKER1_IP>
ssh ubuntu@<WORKER2_IP>
```

### Install kubectl (on master)
```
sudo apt-get update
sudo apt-get install -y kubectl
```

### Check cluster is working
```
kubectl cluster-info
```

### Check all nodes are Ready
```
kubectl get nodes
```

---

## 5. KUBERNETES — Deploy the Application

### Apply deployment manifest
```
kubectl apply -f k8s/deployment.yaml
```

### Apply service manifest
```
kubectl apply -f k8s/service.yaml
```

### Apply both at once
```
kubectl apply -f k8s/
```

### Check pods are running
```
kubectl get pods
```

### Check pods with node placement
```
kubectl get pods -o wide
```

### Check deployments
```
kubectl get deployments
```

### Check services (find NodePort)
```
kubectl get services
```

### Check all resources at once
```
kubectl get all
```

---

## 6. KUBERNETES — Scaling (Benchmarking)

### Scale to 1 pod
```
kubectl scale deployment wildfire-api --replicas=1
```

### Scale to 2 pods
```
kubectl scale deployment wildfire-api --replicas=2
```

### Scale to 4 pods
```
kubectl scale deployment wildfire-api --replicas=4
```

### Scale to 8 pods
```
kubectl scale deployment wildfire-api --replicas=8
```

### Watch pods scale up in real time
```
kubectl get pods -w
```

---

## 7. KUBERNETES — Monitoring & Debugging

### View pod logs
```
kubectl logs <pod-name>
```

### Stream pod logs live
```
kubectl logs <pod-name> -f
```

### Describe a pod (see events, probes, errors)
```
kubectl describe pod <pod-name>
```

### Describe the deployment
```
kubectl describe deployment wildfire-api
```

### Describe the service
```
kubectl describe service wildfire-api-service
```

### View cluster events (sorted by time)
```
kubectl get events --sort-by='.lastTimestamp'
```

### Check CPU and memory usage per pod
```
kubectl top pods
```

### Check node resource usage
```
kubectl top nodes
```

### Get pod name (to copy for other commands)
```
kubectl get pods -o name
```

---

## 8. KUBERNETES — Delete / Cleanup

### Delete deployment
```
kubectl delete deployment wildfire-api
```

### Delete service
```
kubectl delete service wildfire-api-service
```

### Delete everything from k8s folder
```
kubectl delete -f k8s/
```

---

## 9. TEST THE API

### Test health endpoint (replace with your node IP)
```
curl http://<NODE_IP>:30080/
```

### Run the manual test script (1 request to /api/predict)
```
python scripts/test_request.py
```

### Test /api/predict with curl (example)
```
curl -X POST http://<NODE_IP>:30080/api/predict \
  -H "Content-Type: application/json" \
  -d "{\"uuid\":\"test-123\",\"image\":\"$(base64 demo-images/image0.jpeg | tr -d '\n')\"}"
```

### Open API docs in browser
```
http://<NODE_IP>:30080/docs
```

---

## 10. LOCUST — Load Testing

### Run Locust (opens web UI at localhost:8089)
```
locust -f locust/locustfile.py --host http://<NODE_IP>:30080
```

### Run Locust headless (no browser, auto-start)
```
locust -f locust/locustfile.py --host http://<NODE_IP>:30080 \
  --headless --users 10 --spawn-rate 2 --run-time 60s
```

### Run with 50 users, spawn 5 per second, run 2 minutes
```
locust -f locust/locustfile.py --host http://<NODE_IP>:30080 \
  --headless --users 50 --spawn-rate 5 --run-time 2m
```

### Open Locust web UI (after starting Locust)
```
http://localhost:8089
```

---

## 11. TERRAFORM (IaC) — OCI Infrastructure

### Navigate to terraform folder
```
cd teraform
```

### Initialise (download OCI provider plugin)
```
terraform init
```

### Preview what will be created
```
terraform plan
```

### Create all OCI resources (VMs, network, etc.)
```
terraform apply
```

### Create without confirmation prompt
```
terraform apply -auto-approve
```

### Get VM IP addresses after creation
```
terraform output
```

### Show current infrastructure state
```
terraform show
```

### Start stopped VMs
```
.\start-vms.ps1
```

### Stop VMs (save costs)
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

## 12. GIT — Version Control

### Check status
```
git status
```

### Add all changes
```
git add .
```

### Commit with message
```
git commit -m "your message here"
```

### Push to GitHub
```
git push origin main
```

### Pull latest from GitHub
```
git pull origin main
```

### Check commit history
```
git log --oneline
```

### Check remote URL
```
git remote -v
```

---

## 13. FULL START-TO-FINISH DEMO SEQUENCE

### Step 1 — Show cluster is healthy
```
kubectl get nodes
```

### Step 2 — Show pods are running
```
kubectl get pods -o wide
```

### Step 3 — Show service and port
```
kubectl get services
```

### Step 4 — Hit the health endpoint
```
curl http://<NODE_IP>:30080/
```

### Step 5 — Run a real inference test
```
python scripts/test_request.py
```

### Step 6 — Start load test
```
locust -f locust/locustfile.py --host http://<NODE_IP>:30080
```

### Step 7 — Scale pods during load test
```
kubectl scale deployment wildfire-api --replicas=4
```

### Step 8 — Watch new pods come up
```
kubectl get pods -w
```

---

## 14. QUICK COMMAND LOOKUP

| What you want to do              | Command                                              |
|----------------------------------|------------------------------------------------------|
| Build Docker image               | `docker build -t wildfire-api:latest .`              |
| Run container locally            | `docker run -p 8000:8000 wildfire-api:latest`        |
| Deploy to Kubernetes             | `kubectl apply -f k8s/`                              |
| Check pods                       | `kubectl get pods`                                   |
| Check services                   | `kubectl get services`                               |
| Scale to 4 pods                  | `kubectl scale deployment wildfire-api --replicas=4` |
| View pod logs                    | `kubectl logs <pod-name>`                            |
| Debug a pod                      | `kubectl describe pod <pod-name>`                    |
| Test API manually                | `python scripts/test_request.py`                     |
| Start Locust load test           | `locust -f locust/locustfile.py --host http://...`   |
| Provision OCI infrastructure     | `cd teraform && terraform apply`                     |
| Destroy OCI infrastructure       | `cd teraform && terraform destroy`                   |
| Push code to GitHub              | `git add . && git commit -m "msg" && git push`       |

---

## IMPORTANT NOTES

- Replace `<NODE_IP>` with the actual public IP of your master or any worker node
- Replace `<MASTER_IP>`, `<WORKER1_IP>`, `<WORKER2_IP>` with actual OCI VM public IPs (from `terraform output`)
- The API is always exposed on port **30080** (NodePort)
- The container runs on port **8000** internally
- Each pod is limited to **1 vCPU and 2Gi RAM** (set in k8s/deployment.yaml)
- `terraform.tfvars` is NOT committed to GitHub — it contains your OCI credentials
- Run all kubectl commands from your **local machine** (not inside the VM), with your kubeconfig set up
