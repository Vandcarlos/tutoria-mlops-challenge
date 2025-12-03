// variables.tf
// Public interface for the generic VPC module.

variable "project_name" {
  description = "Base project name (e.g. tutoria-mlops)"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g. dev, prod)"
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC (e.g. 10.0.0.0/16)"
  type        = string
}

variable "azs" {
  description = "List of availability zones to use (e.g. [\"us-east-1a\", \"us-east-1b\"])"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets (one per AZ)"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets (one per AZ)"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Whether to create NAT gateways for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "If true, a single NAT gateway is created in the first public subnet and shared across private subnets"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to VPC and related resources"
  type        = map(string)
  default     = {}
}
