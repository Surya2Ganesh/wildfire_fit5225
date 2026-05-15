variable "tenancy_ocid" {
  type = string
}

variable "user_ocid" {
  type = string
}

variable "fingerprint" {
  type = string
}

variable "private_key_path" {
  type = string
}

variable "region" {
  type    = string
  default = "ap-melbourne-1"
}

variable "compartment_ocid" {
  type = string
}

variable "availability_domain" {
  type = string
}

variable "ssh_public_key_path" {
  type = string
}

variable "vcn_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.0.0.0/24"
}

variable "vcn_name" {
  type    = string
  default = "fit5225-vcn-35415940"
}

variable "master_name" {
  type    = string
  default = "master-35415940"
}

variable "worker1_name" {
  type    = string
  default = "worker1-35415940"
}

variable "worker2_name" {
  type    = string
  default = "worker2-35415940"
}

variable "instance_shape" {
  type    = string
  default = "VM.Standard.E5.Flex"
}

variable "ocpus" {
  type    = number
  default = 4
}

variable "memory_in_gbs" {
  type    = number
  default = 8
}

variable "instance_state" {
  type    = string
  default = "RUNNING"
}