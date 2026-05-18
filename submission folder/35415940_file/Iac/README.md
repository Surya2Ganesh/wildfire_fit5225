# CloudEco Terraform IaC

This folder contains the Terraform Infrastructure as Code for the FIT5225 Assignment 1 CloudEco deployment on Oracle Cloud Infrastructure.

It creates:

- one VCN
- one public subnet
- one internet gateway
- one public route table
- one security list for SSH, Kubernetes internal traffic, Flannel, and NodePort `30080`
- three Ubuntu 22.04 VMs: one master and two workers

The Terraform dynamically fetches:

- the first availability domain in the selected compartment
- the latest Canonical Ubuntu 22.04 image for the selected OCI shape

## Usage

Copy the example variables file:

```powershell
Copy-Item .\terraform.tfvars.example .\terraform.tfvars
```

Edit `terraform.tfvars` with your real OCI values, then run:

```powershell
terraform init
terraform plan
terraform apply
```

After provisioning, use the output public IP addresses to SSH into the VMs and configure Kubernetes with `kubeadm`. Then deploy the application from the project root:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods -n cloudeco -o wide
kubectl get svc -n cloudeco
```

The deployed API health endpoint is exposed through NodePort `30080`:

```text
http://<master-public-ip>:30080/health
```

