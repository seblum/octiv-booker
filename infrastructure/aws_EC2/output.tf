output "ec2_global_ips" {
  value = ["${aws_instance.octivbooker-ec2.*.public_ip}"]
}
