output "aws_security_group" {
  value       = aws_security_group.octivbooker-sg.id
  description = "AWS security group of the given vpc network"
}

# output "aws_subnet" {
#   value       = aws_subnet.octivbooker-subnet.id
#   description = "AWS subnet of the given vpc network"
# }
