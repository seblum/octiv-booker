

# variable "cidr_vpc" {
#   description = "CIDR block for VPC"
#   default     = "10.1.0.0/16"
# }

# variable "cidr_subnet" {
#   description = "CIDR block for subnet"
#   default     = "10.1.0.0/20"
# }

# resource "aws_vpc" "toydeploy-vpc" {
#   cidr_block           = var.cidr_vpc
#   enable_dns_hostnames = true
#   enable_dns_support   = true
# }

# resource "aws_subnet" "toydeploy-subnet" {
#   vpc_id     = aws_vpc.toydeploy-vpc.id
#   cidr_block = var.cidr_subnet
# }

# resource "aws_security_group" "toydeploy-sg" {
#   name   = "toydeploy-sg"
#   vpc_id = aws_vpc.toydeploy-vpc.id

#   ingress {
#     from_port = 22
#     to_port   = 22
#     protocol  = "tcp"
#     cidr_blocks = [
#       "0.0.0.0/0"
#     ]
#   }

#   # Terraform removes the default rule, so we re-add it.
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# # resource "aws_instance" "toydeploy" {
# #   ami                         = "ami-083f68207d3376798" # Ubuntu 18.04
# #   instance_type               = "t2.micro"
# #   security_groups             = ["${aws_security_group.toydeploy-sg.id}"]
# #   subnet_id                   = aws_subnet.toydeploy-subnet.id
# #   associate_public_ip_address = true
# #   key_name                    = "toydeploy"
# # }

# resource "aws_internet_gateway" "toydeploy-ig" {
#   vpc_id = aws_vpc.toydeploy-vpc.id
# }

# resource "aws_route_table" "toydeploy-rt" {
#   vpc_id = aws_vpc.toydeploy-vpc.id
#   route {
#     cidr_block = "0.0.0.0/0"
#     gateway_id = aws_internet_gateway.toydeploy-ig.id
#   }
# }

# resource "aws_route_table_association" "toydeploy-rta" {
#   subnet_id      = aws_subnet.toydeploy-subnet.id
#   route_table_id = aws_route_table.toydeploy-rt.id
# }
