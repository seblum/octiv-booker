variable "region" {
  description = "AWS region to create resources in"
  type  = string
  default = "eu-central-1"
}


# variable "ami_name" {}
# variable "ami_id" {}
# variable "ami_key_pair_name" {}

# variable "aws_access_key_id" {
# type = string
# }

# variable "aws_secret_access_key" {
# type = string
# }

variable "octiv_password" {
  type = string
  default = "value"
}
variable "octiv_username" {
  type = string
  # read from env config, or github actions
  default = "value2"
}
