terraform {
  #required_version = ">= 1.0.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "2.15.0"
    }
  }
  # cloud {
  #     organization = "octiv-booker"

  #     workspaces {
  #       name = "dev-booker"
  #     }
  #   }
}
