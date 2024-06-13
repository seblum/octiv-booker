terraform {
  required_version = ">= 1.0.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "2.20.0"
    }
  }

  backend "s3" {
    bucket = "octivebookerterraform"
    key    = "lambda_terraform.tfstate"
    region = "eu-central-1"
    encrypt = true
  }

}
