module "vpc" {
  source = "../../modules/vpc"

  project_name   = "tutoria-mlops"
  environment    = "prod"
  vpc_cidr_block = "10.0.0.0/16"

  azs = [
    "us-east-1a",
    "us-east-1b",
  ]

  public_subnet_cidrs = [
    "10.0.0.0/24",
    "10.0.1.0/24",
  ]

  private_subnet_cidrs = [
    "10.0.10.0/24",
    "10.0.11.0/24",
  ]

  enable_nat_gateway  = true
  single_nat_gateway  = true

  tags = {
    Owner = "vand"
  }
}
