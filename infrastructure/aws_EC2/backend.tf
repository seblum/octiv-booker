terraform {
  required_version = "1.0.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "2.15.0"
    }
  }

  # Commented out until after bootstrap
  backend "s3" {
    bucket = "octivebookerterraform"
    key    = "terraform.tfstate"
    region = "eu-central-1"
    #dynamodb_table = "aws-locks"
    encrypt = true
  }

}
