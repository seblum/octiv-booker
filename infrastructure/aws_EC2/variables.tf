variable "region" {
  description = "AWS region to create resources in"
  type  = string
  default = "eu-central-1"
}


# variable "ami_name" {}
# variable "ami_id" {}
# variable "ami_key_pair_name" {}

# # access keys for terraform cloud 
# variable "aws_access_key_id" {
# type = string

# }

# variable "aws_secret_access_key" {
# type = string
# }

variable "octiv_password" {
  type = string
  description = "Octiv password to store as env in docker image"
  # read from env config, or github actions
  default = "value"
}
variable "octiv_username" {
  type = string
  description = "Octiv password to store as env in docker image"
  # read from env config, or github actions
  default = "value2"
}

variable "public_pem_key" {
  type = string
  description = "public pem key for ec2 instance"
  default = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCJDVYClz1eZtbBxsRnJt83BIlCWpmztkedF6bqyhr0A7xjRP50t66wk7hgSSGi2A/mrTyntS8s0ENpx9R6e84dgPWUmiNf4NjmyH+UUyrBozMuvXxH7ACwJVTtSHO6wT2TtCCc/Ea3mV1vHN3D6tA0raTU0cdglXitRVPUNVxbv7jf0Plj/1NCK4MSyZ9VHtnCV3WIf6DFp//gkZj/518ngD7yv1+hH4pncjJNhdXlDbaxS1fp0iTVwR+ZRH45vpyrHm1ykVopaO8YMgEDv8BOl3o1RXclucqEbXnG1xs98XWokKUrzmgKzUvUPbB5sbNGWoiFi8GlpcZ97ZdVz65N"
}