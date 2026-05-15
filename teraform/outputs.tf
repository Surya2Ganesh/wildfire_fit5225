output "master_public_ip" {
  value = oci_core_instance.master.public_ip
}

output "worker1_public_ip" {
  value = oci_core_instance.worker1.public_ip
}

output "worker2_public_ip" {
  value = oci_core_instance.worker2.public_ip
}

output "master_private_ip" {
  value = oci_core_instance.master.private_ip
}

output "worker1_private_ip" {
  value = oci_core_instance.worker1.private_ip
}

output "worker2_private_ip" {
  value = oci_core_instance.worker2.private_ip
}