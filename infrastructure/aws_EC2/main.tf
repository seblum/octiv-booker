
# Initially used to setup S3 and DynamoDB as backend.
# module "bootstrap" {
#   source                      = "./modules/bootstrap"
#   name_of_s3_bucket           = local.name_of_s3_bucket
#   dynamo_db_table_name        = "aws-locks"
# }


module "network" {
  source = "./modules/network"
}

module "iam" {
  source = "./modules/iam"
}


# create ECR repo
resource "aws_ecr_repository" "ecr_repo" {
  name = local.ecr_repository_name
  tags = {
    project = "octive-booker"
  }
}

## Build docker images and push to ECR
resource "docker_registry_image" "docker_ecr_image" {
  #name = "${aws_ecr_repository.ecr_repo.repository_url}:latest"
  name = "${local.ecr_repository_name}:${local.ecr_image_tag}"
  build {
    context    = "../../slotBooker"
    dockerfile = "poetry.Dockerfile"
    build_args = {
      OCTIV_USERNAME = var.octiv_username
      OCTIV_PASSWORD = var.octiv_password
    }
  }
  depends_on = [var.octiv_username, var.octiv_password]
}

resource "aws_key_pair" "octivbooker-key" {
  key_name   = "octivbooker-public"
  public_key = var.public_pem_key
  # tags = {
  #     project = "octive-booker"
  # }
}


resource "aws_instance" "octivbooker-ec2" {
  ami                     = data.aws_ami.amazon_linux_2.id
  instance_type           = "t3.micro"
  iam_instance_profile    = module.iam.aws_iam_instance_profile
  user_data               = data.template_file.init.rendered
  vpc_security_group_ids  = [module.network.aws_security_group]
  subnet_id               = module.network.aws_subnet
  key_name                = aws_key_pair.octivbooker-key.key_name
  monitoring              = true
  disable_api_termination = false
  ebs_optimized           = true
  root_block_device {
    volume_size = 8
  }
  tags = {
    project = "octive-booker"
  }
}
