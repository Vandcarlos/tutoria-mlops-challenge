// locals.tf
// Naming helpers and base tags for the VPC resources.

locals {
  name_prefix = "${var.project_name}-${var.environment}"

  base_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Component   = "vpc"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
