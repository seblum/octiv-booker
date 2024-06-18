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
    # rename in next run
    key    = "terraform.tfstate"
    region = "eu-central-1"
    #dynamodb_table = "aws-locks"
    encrypt = true
  }

}
