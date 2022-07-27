output "ec2_global_ips" {
  value = ["${aws_instance.octivbooker-ec2.*.public_ip}"]
}

# ssh -i "octivebooker.pem"       ec2-user@ec3-70-23-178.eu-central-1.compute.amazonaws.com
# ssh -i "octivbooker-public.pem" ec2-user@ec2-3-66-213-246.eu-central-1.compute.amazonaws.com
