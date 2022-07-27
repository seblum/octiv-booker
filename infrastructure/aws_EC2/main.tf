
# Call the seed_module to build our ADO seed info
module "bootstrap" {
  source                      = "./modules/bootstrap"
  name_of_s3_bucket           = local.name_of_s3_bucket
  dynamo_db_table_name        = "aws-locks"
}


# /* Commented out until after bootstrap


# create ECR repo
resource aws_ecr_repository ecr_repo {
    name = local.ecr_repository_name
}

## Build docker images and push to ECR
resource docker_registry_image docker_ecr_image {
    name = "${aws_ecr_repository.ecr_repo.repository_url}:latest"

    build {
        context = "../../slotBooker"
        dockerfile = "poetry.Dockerfile"
        build_args = {
          OCTIV_USERNAME=var.octiv_username
          OCTIV_PASSWORD=var.octiv_password
          }
    }

    depends_on = [var.octiv_username, var.octiv_password]

}



resource "aws_key_pair" "octivbooker-key"{
    key_name = "octivbooker-public"
    # used for terraform cloud
    public_key = var.public_pem_key
    # # used for local
    # public_key = "${file("../../octivbooker-public.pem")}"
}

resource "aws_iam_role" "ec2_role_hello_world" {
  name = "ec2_role_hello_world"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF

  tags = {
    project = "hello-world"
  }
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2_profile_hello_world"
  role = aws_iam_role.ec2_role_hello_world.name
}

resource "aws_iam_role_policy" "ec2_policy" {
  name = "ec2_policy"
  role = aws_iam_role.ec2_role_hello_world.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchImportUpstreamImage",
        "ecr:CreatePullThroughCacheRule"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}
 #  just the ECR repository instead of "*"



data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-ebs"]
  }
}

resource "aws_instance" "web" {
    ami           = data.aws_ami.amazon_linux_2.id
    instance_type = "t3.micro"

    root_block_device {
        volume_size = 8
    }

    user_data = data.template_file.init.rendered


    # depends_on = [
    #     module.ec2_sg,
    #     module.dev_ssh_sg
    # ]
    vpc_security_group_ids = [aws_security_group.main.id]
    #subnet_id = "${aws_subnet.subnet-uno.id}"
    # security_groups             = ["${aws_security_group.toydeploy-sg.id}"]
    # subnet_id                   = aws_subnet.toydeploy-subnet.id

    iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

    tags = {
        project = "octive-booker"
    }

    # aws ec2 create-key-pair --key-name octivebooker --output text > octivebooker.pem
    # run chmod 400 octivebooker.pem
    key_name                = "${aws_key_pair.octivbooker-key.key_name}"
    monitoring              = true
    disable_api_termination = false
    ebs_optimized           = true
}




resource "aws_security_group" "main" {
    #vpc_id = "${aws_vpc.test-env.id}"
    #name = "allow-all-sg"
    egress = [
        {
        cidr_blocks      = [ "0.0.0.0/0",]
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
    ingress                = [
        {
        cidr_blocks      = [ "0.0.0.0/0", ]
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
}

#*/