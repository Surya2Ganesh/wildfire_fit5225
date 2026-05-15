data "oci_core_images" "ubuntu_images" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape                    = var.instance_shape

  sort_by    = "TIMECREATED"
  sort_order = "DESC"
}

locals {
  ssh_public_key = file(var.ssh_public_key_path)
}

resource "oci_core_instance" "master" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = var.master_name
  shape               = var.instance_shape
  state               = var.instance_state

  shape_config {
    ocpus         = var.ocpus
    memory_in_gbs = var.memory_in_gbs
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.fit5225_public_subnet.id
    assign_public_ip = true
    display_name     = "${var.master_name}-vnic"
    hostname_label   = "mv1"
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_images.images[0].id
  }

  metadata = {
    ssh_authorized_keys = local.ssh_public_key
  }
}

resource "oci_core_instance" "worker1" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = var.worker1_name
  shape               = var.instance_shape
  state               = var.instance_state

  shape_config {
    ocpus         = var.ocpus
    memory_in_gbs = var.memory_in_gbs
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.fit5225_public_subnet.id
    assign_public_ip = true
    display_name     = "${var.worker1_name}-vnic"
    hostname_label   = "wv1"
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_images.images[0].id
  }

  metadata = {
    ssh_authorized_keys = local.ssh_public_key
  }
}

resource "oci_core_instance" "worker2" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = var.worker2_name
  shape               = var.instance_shape
  state               = var.instance_state

  shape_config {
    ocpus         = var.ocpus
    memory_in_gbs = var.memory_in_gbs
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.fit5225_public_subnet.id
    assign_public_ip = true
    display_name     = "${var.worker2_name}-vnic"
    hostname_label   = "wv2"
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_images.images[0].id
  }

  metadata = {
    ssh_authorized_keys = local.ssh_public_key
  }
}