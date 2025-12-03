terraform {
  backend "s3" {
    bucket         = "tfstate-vandcarlos-tutoria-mlops-challenge"
    key            = "envs/prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-ml-locks"
    encrypt        = true
  }
}
