provider "aws" {
  region = var.region
  # access_key = var.aws_access_key_id
  # secret_key = var.aws_secret_access_key
  # profile = "seblum"
}

provider "docker" {
  registry_auth {
    address  = local.aws_ecr_url
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

