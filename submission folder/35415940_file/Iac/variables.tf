variable "tenancy_ocid" {
  description = "OCI tenancy OCID"
  type        = string
}

variable "user_ocid" {
  description = "OCI user OCID"
  type        = string
}

variable "fingerprint" {
  description = "API key fingerprint"
  type        = string
}

variable "private_key_path" {
  description = "Path to OCI API private key"
  type        = string
}

variable "region" {
  description = "OCI region"
  type        = string
  default     = "ap-melbourne-1"
}

variable "compartment_ocid" {
  description = "OCI compartment OCID where resources are created"
  type        = string
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key used for VM login"
  type        = string
}

variable "student_id" {
  description = "Student ID used for naming resources"
  type        = string
  default     = "35415940"
}

variable "vcn_cidr" {
  description = "CIDR block for the VCN"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.0.0/24"
}

variable "instance_shape" {
  description = "OCI flexible VM shape"
  type        = string
  default     = "VM.Standard.E5.Flex"
}

variable "instance_ocpus" {
  description = "OCPUs per VM"
  type        = number
  default     = 4
}

variable "instance_memory_gb" {
  description = "Memory in GB per VM"
  type        = number
  default     = 8
}

