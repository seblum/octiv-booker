
data "aws_caller_identity" "current" {}
data "aws_ecr_authorization_token" "token" {}

data "aws_vpc" "default" {
  default = true
}

data "template_file" "init" {
  template = file("instance.sh")

  vars = {
    ecr_url = "${aws_ecr_repository.ecr_repo.repository_url}:latest"
    region  = "${var.region}"
    awsid   = "${data.aws_caller_identity.current.account_id}"
  }
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-ebs"]
  }
}
