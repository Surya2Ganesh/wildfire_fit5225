output "vcn_id" {
  description = "Created VCN OCID"
  value       = oci_core_vcn.fit5225_vcn.id
}

output "public_subnet_id" {
  description = "Created public subnet OCID"
  value       = oci_core_subnet.fit5225_public_subnet.id
}

output "node_public_ips" {
  description = "Public IPs for Kubernetes nodes"
  value = {
    for name, instance in oci_core_instance.k8s_nodes :
    name => instance.public_ip
  }
}

output "node_private_ips" {
  description = "Private IPs for Kubernetes nodes"
  value = {
    for name, instance in oci_core_instance.k8s_nodes :
    name => instance.private_ip
  }
}

output "application_url" {
  description = "Public NodePort health URL after Kubernetes deployment"
  value       = "http://${oci_core_instance.k8s_nodes["master"].public_ip}:30080/health"
}

