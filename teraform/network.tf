resource "oci_core_vcn" "fit5225_vcn" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = [var.vcn_cidr]
  display_name   = var.vcn_name
  dns_label      = "fit5225vcn"
}

resource "oci_core_internet_gateway" "fit5225_igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fit5225_vcn.id
  display_name   = "fit5225-igw-35415940"
  enabled        = true
}

resource "oci_core_route_table" "fit5225_public_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fit5225_vcn.id
  display_name   = "fit5225-public-rt-35415940"

  route_rules {
    network_entity_id = oci_core_internet_gateway.fit5225_igw.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

resource "oci_core_security_list" "fit5225_sec_list" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.fit5225_vcn.id
  display_name   = "fit5225-sec-list-35415940"

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"

    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "10.0.0.0/24"

    tcp_options {
      min = 6443
      max = 6443
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "10.0.0.0/24"

    tcp_options {
      min = 10250
      max = 10250
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "10.0.0.0/24"

    tcp_options {
      min = 30000
      max = 32767
    }
  }

  ingress_security_rules {
    protocol = "17"
    source   = "10.0.0.0/24"

    udp_options {
      min = 8472
      max = 8472
    }
  }

  ingress_security_rules {
    protocol = "all"
    source   = "10.0.0.0/24"
  }
}

resource "oci_core_subnet" "fit5225_public_subnet" {
  compartment_id            = var.compartment_ocid
  vcn_id                    = oci_core_vcn.fit5225_vcn.id
  cidr_block                = var.public_subnet_cidr
  display_name              = "public-subnet-fit5225-vcn-35415940"
  dns_label                 = "pubsubnet"
  route_table_id            = oci_core_route_table.fit5225_public_rt.id
  security_list_ids         = [oci_core_security_list.fit5225_sec_list.id]
  prohibit_public_ip_on_vnic = false
}