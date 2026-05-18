# ============================================================
# FIT5225 Assignment 1 - OCI Infrastructure as Code
# Creates:
#   - VCN
#   - Internet Gateway
#   - Route Table
#   - Security List
#   - Public Subnet
#   - 3 Ubuntu VMs: 1 master + 2 workers
# ============================================================

# Get availability domains from the selected compartment.
# This avoids hardcoding an availability domain value.
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_ocid
}

# Dynamically fetch the latest Canonical Ubuntu 22.04 image for the chosen shape.
# This avoids hardcoding an image OCID that may expire or differ by region.
data "oci_core_images" "ubuntu_2204" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape                    = var.instance_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

locals {
  # Prefix makes all created resources easy to identify in OCI.
  name_prefix = "fit5225-${var.student_id}"

  # Three required VMs for the assignment: one master and two workers.
  nodes = {
    master = {
      display_name = "master-${var.student_id}"
      hostname     = "mv1"
    }

    worker1 = {
      display_name = "worker1-${var.student_id}"
      hostname     = "wv1"
    }

    worker2 = {
      display_name = "worker2-${var.student_id}"
      hostname     = "wv2"
    }
  }
}

# -----------------------------
# Network
# -----------------------------

resource "oci_core_vcn" "fit5225_vcn" {
  compartment_id = var.compartment_ocid
  cidr_block     = var.vcn_cidr
  display_name   = "${local.name_prefix}-vcn"
  dns_label      = "fit5225vcn"
}

resource "oci_core_internet_gateway" "fit5225_igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fit5225_vcn.id
  display_name   = "${local.name_prefix}-internet-gateway"
  enabled        = true
}

resource "oci_core_route_table" "fit5225_route_table" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fit5225_vcn.id
  display_name   = "${local.name_prefix}-public-route-table"

  route_rules {
    # Route internet-bound traffic through the internet gateway.
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.fit5225_igw.id
  }
}

# Security list allows:
#   - SSH from internet
#   - NodePort 30080 from internet
#   - Kubernetes internal communication inside VCN
#   - Flannel VXLAN UDP 8472
resource "oci_core_security_list" "fit5225_security_list" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fit5225_vcn.id
  display_name   = "${local.name_prefix}-security-list"

  # SSH access for setup and interview demonstration.
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"

    tcp_options {
      min = 22
      max = 22
    }

    description = "Allow SSH"
  }

  # Public Kubernetes NodePort for the FastAPI service.
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"

    tcp_options {
      min = 30080
      max = 30080
    }

    description = "Allow Kubernetes NodePort 30080"
  }

  # Kubernetes API server from inside the VCN.
  ingress_security_rules {
    protocol = "6"
    source   = var.vcn_cidr

    tcp_options {
      min = 6443
      max = 6443
    }

    description = "Allow Kubernetes API server inside VCN"
  }

  # Kubelet API communication from inside the VCN.
  ingress_security_rules {
    protocol = "6"
    source   = var.vcn_cidr

    tcp_options {
      min = 10250
      max = 10250
    }

    description = "Allow kubelet communication inside VCN"
  }

  # Flannel VXLAN traffic used by the pod network.
  ingress_security_rules {
    protocol = "17"
    source   = var.vcn_cidr

    udp_options {
      min = 8472
      max = 8472
    }

    description = "Allow Flannel VXLAN"
  }

  # Allow all private node-to-node traffic inside the VCN.
  ingress_security_rules {
    protocol = "all"
    source   = var.vcn_cidr

    description = "Allow all internal VCN traffic"
  }

  # Allow outbound internet access so VMs can install packages and pull images.
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"

    description = "Allow all outbound traffic"
  }
}

resource "oci_core_subnet" "fit5225_public_subnet" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.fit5225_vcn.id
  cidr_block                 = var.public_subnet_cidr
  display_name               = "${local.name_prefix}-public-subnet"
  dns_label                  = "public"
  route_table_id             = oci_core_route_table.fit5225_route_table.id
  security_list_ids          = [oci_core_security_list.fit5225_security_list.id]
  prohibit_public_ip_on_vnic = false
}

# -----------------------------
# Compute instances
# -----------------------------

resource "oci_core_instance" "k8s_nodes" {
  for_each = local.nodes

  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = each.value.display_name
  shape               = var.instance_shape

  # Assignment requirement: each VM has 4 OCPUs and 8 GB RAM.
  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_gb
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.fit5225_public_subnet.id
    assign_public_ip = true
    hostname_label   = each.value.hostname
    display_name     = "${each.value.hostname}-vnic"
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_2204.images[0].id
  }

  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)

    # Minimal bootstrap. Kubernetes installation and kubeadm init/join can be
    # run manually during setup or interview preparation.
    user_data = base64encode(<<-EOF
      #!/bin/bash
      hostnamectl set-hostname ${each.value.hostname}
      apt-get update -y
    EOF
    )
  }
}

