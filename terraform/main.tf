terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "serverless_health_check" {
  source = "./modules/serverless-health-check"

  environment = var.environment
  aws_region  = var.aws_region
}
