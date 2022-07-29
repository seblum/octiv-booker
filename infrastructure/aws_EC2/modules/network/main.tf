
# resource "aws_vpc" "octivbooker-vpc" {
#   cidr_block           = var.cidr_vpc
#   enable_dns_hostnames = true
#   enable_dns_support   = true
# }

# resource "aws_subnet" "octivbooker-subnet" {
#   vpc_id     = aws_vpc.octivbooker-vpc.id
#   cidr_block = var.cidr_subnet
# }

# resource "aws_internet_gateway" "octivbooker-ig" {
#   vpc_id = aws_vpc.octivbooker-vpc.id
# }

# resource "aws_route_table" "octivbooker-rt" {
#   vpc_id = aws_vpc.octivbooker-vpc.id
#   route {
#     cidr_block = "0.0.0.0/0"
#     gateway_id = aws_internet_gateway.octivbooker-ig.id
#   }
# }

# resource "aws_route_table_association" "octivbooker-rta" {
#   subnet_id      = aws_subnet.octivbooker-subnet.id
#   route_table_id = aws_route_table.octivbooker-rt.id
# }


resource "aws_security_group" "octivbooker-sg" {
  name   = "octivbooker-sg"
  vpc_id = aws_vpc.octivbooker-vpc.id

  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    }
  ]
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 22
    }
  ]

  tags = {
    project = "octive-booker"
  }
}
