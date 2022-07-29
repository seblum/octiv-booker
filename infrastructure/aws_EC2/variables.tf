variable "region" {
  description = "AWS region to create resources in"
  type        = string
  default     = "eu-central-1"
}

variable "octiv_password" {
  type        = string
  description = "Octiv password to store as env in docker image"
  # read from env config, or github actions
}

variable "octiv_username" {
  type        = string
  description = "Octiv password to store as env in docker image"
  # read from env config, or github actions
}

variable "public_pem_key" {
  type        = string
  description = "public pem key for ec2 instance"
}
