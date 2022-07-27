
# Call the seed_module to build our ADO seed info
module "bootstrap" {
  source                      = "./modules/bootstrap"
  name_of_s3_bucket           = local.name_of_s3_bucket
  dynamo_db_table_name        = "aws-locks"
}

# /* Commented out until after bootstrap

module "network" {
  source                      = "./modules/network"
}

module "iam" {
  source                      = "./modules/iam"
}


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
    public_key = var.public_pem_key
}


resource "aws_instance" "octivbooker-ec2" {
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
    vpc_security_group_ids      = [aws_security_group.main.id]
    # subnet_id                   = "${aws_subnet.subnet-uno.id}"
    # security_groups             = ["${aws_security_group.toydeploy-sg.id}"]
    # subnet_id                   = aws_subnet.toydeploy-subnet.id

    iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

    tags = {
        project = "octive-booker"
    }

    key_name                = "${aws_key_pair.octivbooker-key.key_name}"
    monitoring              = true
    disable_api_termination = false
    ebs_optimized           = true
}


#*/

