terraform {
  backend "s3" {
    bucket         = "thrivecart-prod-terraform-state-54321"
    key            = "serverless-health-check/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "thrivecart-terraform-state-lock"
  }
}
