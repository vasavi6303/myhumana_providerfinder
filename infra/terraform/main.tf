terraform {
  required_version = ">= 1.2"

  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}
provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "providerfinder" {
  name = "providerfinder"
  image_scanning_configuration { scan_on_push = true }
}

output "ecr_repo_url" {
  value = aws_ecr_repository.providerfinder.repository_url
}
