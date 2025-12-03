// main.tf
// Creates the VPC, Internet Gateway and shared networking resources.
// Subnets and route tables are defined in subnets.tf and routes.tf.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    local.merged_tags,
    { Name = "${local.name_prefix}-vpc" }
  )
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = merge(
    local.merged_tags,
    { Name = "${local.name_prefix}-igw" }
  )
}
